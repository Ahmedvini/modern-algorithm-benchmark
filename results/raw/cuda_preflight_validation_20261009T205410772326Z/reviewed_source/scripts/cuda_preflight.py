#!/usr/bin/env python3
"""Non-destructive CUDA readiness. Exit 0 ready, 2 unavailable, 1 report error."""
import argparse
import csv
import ctypes.util
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
ENV_NAMES=('CUDA_VISIBLE_DEVICES','NVIDIA_VISIBLE_DEVICES','CUDACXX','CUDAHOSTCXX',
           'CUDAToolkit_ROOT','CUDA_HOME','CUDA_PATH','LD_LIBRARY_PATH')


def scrub(text,environ):
    text=str(text)
    for name,value in environ.items():
        if re.search(r'TOKEN|PASSWORD|SECRET|CREDENTIAL|API_KEY|PRIVATE_KEY',name,re.I) and len(value)>=4:
            text=text.replace(value,'<redacted>')
    text=re.sub(r'([A-Za-z][A-Za-z0-9+.-]*://)[^/\s@]+@',r'\1<redacted>@',text)
    return re.sub(r'(?i)([?&](?:token|password|secret|api_key)=)[^&\s]+',r'\1<redacted>',text)


def command(argv,timeout=60):
    result=dict(command=list(argv),returncode=None,stdout='',stderr='',status='unavailable')
    try:
        r=subprocess.run(argv,capture_output=True,text=True,errors='replace',timeout=timeout,check=False)
        result.update(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,status='completed')
    except subprocess.TimeoutExpired as error:
        def decoded(value):return value.decode(errors='replace') if isinstance(value,bytes) else value or ''
        result.update(status='timeout',stdout=decoded(error.stdout),stderr=decoded(error.stderr),error='command timeout')
    except OSError as error:result['error']=str(error)
    return result


def read_optional(path):
    try:return dict(path=str(path),available=True,text=Path(path).read_text(encoding='utf-8',errors='replace'))
    except OSError as error:return dict(path=str(path),available=False,error=str(error))


def discover(environ,which=shutil.which):
    gpu=[];errors=[];pci=Path('/sys/bus/pci/devices');visible=False
    if sys.platform.startswith('linux'):
        try:
            for device in pci.iterdir():
                try:
                    if (device/'vendor').read_text().strip()=='0x10de' and int((device/'class').read_text().strip(),16)>>16==3:
                        gpu.append(dict(pci_address=device.name,vendor='0x10de',device=(device/'device').read_text().strip(),device_class=(device/'class').read_text().strip(),
                                        kernel_driver=(device/'driver').resolve().name if (device/'driver').is_symlink() else None))
                except (OSError,ValueError) as error:errors.append(str(error))
            visible=not errors
        except OSError as error:errors.append(str(error))
    roots=[]
    for key in ['CUDAToolkit_ROOT','CUDA_HOME','CUDA_PATH']:
        if environ.get(key):roots.append(Path(environ[key]))
    roots.extend([Path('/usr/local/cuda'),Path('/opt/cuda')])
    roots.extend(sorted(Path('/usr/local').glob('cuda-*')))
    path_nvcc=which('nvcc');candidates=[]
    if environ.get('CUDACXX'):candidates.append(environ['CUDACXX'])
    if path_nvcc:candidates.append(path_nvcc)
    for directory in roots:candidates.extend([str(directory/'bin/nvcc'),str(directory/'bin/nvcc.exe')])
    nvcc=next((which(s) or str(Path(s).resolve()) for s in candidates if which(s) or Path(s).is_file()),None)
    if nvcc:roots.insert(0,Path(nvcc).resolve().parent.parent)
    files={}
    for directory in roots:
        for pattern in ['version.json','version.txt','include/cuda_runtime.h','lib64/libcudart.so*','lib/x64/cudart.lib','targets/*/lib/libcudart.so*']:
            for f in directory.glob(pattern):
                if f.is_file():
                    entry=dict(kind='version' if f.name.startswith('version.') else 'header' if f.suffix=='.h' else 'runtime_library',sha256=None)
                    if entry['kind']=='version':
                        try:entry['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
                        except OSError as error:entry['error']=str(error)
                    files[str(f.resolve())]=entry
    return dict(pci_scan_available=visible,pci_gpus=gpu,pci_errors=errors,driver_file=read_optional('/proc/driver/nvidia/version'),
                nvidia_module_visible=Path('/sys/module/nvidia').is_dir(),device_nodes={str(f):f.exists() for f in [Path('/dev/nvidiactl'),Path('/dev/nvidia0')]},
                tools=dict(nvidia_smi=which('nvidia-smi'),nvcc=nvcc,cmake=which('cmake'),lspci=which('lspci')),
                toolkit_files=files,driver_library=ctypes.util.find_library('cuda'),runtime_library=ctypes.util.find_library('cudart'))


def gpu_rows(record):
    if record.get('returncode')!=0:return []
    rows=[]
    for row in csv.reader(io.StringIO(record['stdout'])):
        if len(row)==3 and all(s.strip() for s in row):rows.append(dict(index=row[0].strip(),model=row[1].strip(),driver_version=row[2].strip()))
    return rows


def runtime_json(record):
    try:
        value=json.loads(record.get('stdout',''))
        if not isinstance(value,dict) or value.get('schema_version')!=1 or value.get('record_kind')!='cuda_runtime_probe':return None
        if type(value.get('device_count')) is not int or value['device_count']<0:return None
        if value.get('status') not in ['ok','error','unavailable']:return None
        if value['status']=='ok' and (record.get('returncode')!=0 or value['device_count']<1 or value.get('stage')!='complete' or value.get('kernel_result')!=1729 or type(value.get('tested_device')) is not int or value['tested_device']!=0 or value.get('cuda_error_code')!=0 or not isinstance(value.get('devices'),list) or len(value['devices'])!=value['device_count']):return None
        return value
    except (ValueError,TypeError):return None


def classify(discovery,probes):
    smi=gpu_rows(probes.get('nvidia_smi',{}));runtime=runtime_json(probes.get('runtime',{}))
    count=runtime['device_count'] if runtime else None
    driver=bool(smi) or bool(count and runtime.get('stage')!='enumerate')
    pci=bool(discovery['pci_gpus']);lspci=probes.get('lspci',{})
    pci=pci or (lspci.get('returncode')==0 and bool(re.search(r'VGA|3D controller|Display controller',lspci.get('stdout',''),re.I)))
    gpu=pci or bool(smi) or bool(count)
    nvcc=probes.get('nvcc',{}).get('returncode')==0
    built=probes.get('configure',{}).get('returncode')==0 and probes.get('build',{}).get('returncode')==0
    usable=built and runtime is not None and runtime['status']=='ok' and probes['runtime']['returncode']==0
    if usable:state='operational'
    elif gpu and not driver:state='gpu_driver_unavailable'
    elif driver and not nvcc:state='driver_toolkit_unavailable'
    elif built:state='toolkit_no_usable_device'
    elif nvcc:state='toolchain_unverified'
    elif discovery['pci_scan_available'] or lspci.get('returncode')==0 or probes.get('nvidia_smi',{}).get('returncode')==0:state='no_nvidia_gpu_detected'
    else:state='detection_unavailable'
    return dict(state=state,gpu_detected=gpu,driver_operational_evidence=driver,nvcc_answers=nvcc,
                project_cuda_target_built=built,device0_kernel_verified=usable,
                runtime_device_count=count,management_devices=smi,
                scope='Visible to this process/container; absence of detection does not prove host GPU absence.')


def collect(timeout=60,runner=command,environ=None,discovery=None,which=shutil.which):
    environ=dict(os.environ if environ is None else environ)
    found=discover(environ,which) if discovery is None else discovery
    probes={}
    def run(name,argv):
        probes[name]=runner(argv,timeout);return probes[name]
    run('nvidia_smi',[found['tools']['nvidia_smi'] or 'nvidia-smi','--query-gpu=index,name,driver_version','--format=csv,noheader,nounits'])
    run('lspci',[found['tools']['lspci'] or 'lspci','-nn','-d','10de:'])
    run('nvcc',[found['tools']['nvcc'] or 'nvcc','--version'])
    cmake=found['tools']['cmake'] or 'cmake';version=run('cmake',[cmake,'--version'])
    run('cmake_cuda_property',[cmake,'--help-property','CUDA_STANDARD'])
    match=re.search(r'cmake version (\d+)\.(\d+)',version['stdout'])
    cmake_ok=version['returncode']==0 and match is not None and tuple(map(int,match.groups()))>=(3,18)
    cache={};runtime=None
    if probes['nvcc']['returncode']==0 and found['tools']['nvcc'] and cmake_ok:
        with tempfile.TemporaryDirectory(prefix='mab_cuda_preflight_') as temporary:
            build=Path(temporary)/'build'
            cfg=run('configure',[cmake,'-S',str(ROOT),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DBUILD_TESTING=OFF',
                '-DMAB_ENABLE_CUDA=ON','-DMAB_ENABLE_OPENMP=OFF','-DMAB_ENABLE_SANITIZERS=OFF','-DCMAKE_CUDA_COMPILER='+found['tools']['nvcc']])
            if cfg['returncode']==0:
                b=run('build',[cmake,'--build',str(build),'--target','cuda_runtime_probe','--config','Release','--parallel','2'])
                if b['returncode']==0:
                    binary=next((f for f in [build/'cuda_runtime_probe',build/'Release/cuda_runtime_probe',build/'Release/cuda_runtime_probe.exe',build/'cuda_runtime_probe.exe'] if f.is_file()),build/'cuda_runtime_probe')
                    run('runtime',[str(binary)]);runtime=runtime_json(probes['runtime'])
            allowed={'CMAKE_CUDA_COMPILER','CMAKE_CUDA_HOST_COMPILER','CMAKE_CUDA_ARCHITECTURES','CMAKE_CUDA_FLAGS','CMAKE_BUILD_TYPE','CUDAToolkit_NVCC_EXECUTABLE','CUDAToolkit_INCLUDE_DIR','CUDA_cudart_LIBRARY'}
            text=read_optional(build/'CMakeCache.txt')
            for line in text.get('text','').splitlines():
                if ':' in line and '=' in line and line.split(':',1)[0] in allowed:
                    key,value=line.split('=',1);cache[key.split(':',1)[0]]=value
    for step in ['configure','build','runtime']:
        if step not in probes:probes[step]=dict(status='skipped',returncode=None,stdout='',stderr='',reason='Requires successful previous step, working NVIDIA nvcc and CMake>=3.18.')
    report=dict(schema_version=1,protocol='cuda_preflight_v1',record_kind='cuda_readiness',captured_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        platform=dict(os=platform.system(),release=platform.release(),kernel=platform.version(),architecture=platform.machine(),cpu=platform.processor() or None,logical_cpu_count=os.cpu_count(),python=sys.version),
        environment={name:environ.get(name) for name in ENV_NAMES},
        cuda_path_entries=[s for s in environ.get('PATH','').split(os.pathsep) if re.search(r'cuda|nvidia',s,re.I)],
        discovery=found,probes=probes,cmake_selected_cache=cache,runtime_probe=runtime,
        classification=classify(found,probes),timeout_seconds=timeout,
        source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['CMakeLists.txt','cmake/cuda.cmake','src/cuda/runtime_probe.cu','scripts/cuda_preflight.py']},
        limitations=['No installation/system changes; no sorting/performance experiment.','Only device0 kernel execution is checked; other enumerated devices untested.','Toolkit/Colab GPU path unvalidated unless operational evidence is present.'])
    # Scrub before any report/summary output, including diagnostics and allowlisted paths.
    def sanitized(value):
        if isinstance(value,str):return scrub(value,environ)
        if isinstance(value,list):return [sanitized(v) for v in value]
        if isinstance(value,dict):
            return {(scrub(k,environ) if '/' in k or '\\' in k else k):sanitized(v) for k,v in value.items()}
        return value
    return sanitized(report)


def summary(report):
    c=report['classification'];lines=['CUDA readiness: '+c['state'],
        'Device0 kernel verified: '+str(c['device0_kernel_verified']),
        'NVIDIA nvcc answers: '+str(c['nvcc_answers']),
        'Project CUDA target built: '+str(c['project_cuda_target_built']),
        'CPU project: unaffected by unavailable CUDA; use MAB_ENABLE_CUDA=OFF.',c['scope']]
    for name,r in report['probes'].items():lines.append(f"{name}: {r['status']}; exit={r['returncode']}"+(('; '+r['reason']) if 'reason' in r else ''))
    for gpu in c['management_devices']:lines.append('NVIDIA GPU: '+gpu['model']+'; driver='+gpu['driver_version'])
    if not c['management_devices']:
        for line in report['probes']['lspci']['stdout'].splitlines():
            if re.search(r'VGA|3D controller|Display controller',line,re.I):lines.append('PCI GPU evidence: '+line)
    lines.extend(report['limitations']);return '\n'.join(lines)+'\n'


def execute(output,timeout=60,collector=collect):
    output=Path(output)
    # Atomic ownership protects earlier evidence and concurrent invocations.
    output.mkdir(exist_ok=False)
    try:
        report=collector(timeout=timeout)
        text=json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n'
        with (output/'report.json').open('x',encoding='utf-8') as f:f.write(text)
        human=summary(report)
        with (output/'SUMMARY.txt').open('x',encoding='utf-8') as f:f.write(human)
        marker=dict(schema_version=1,discovery_complete=True,cuda_operational=report['classification']['device0_kernel_verified'],
                    files_sha256={name:hashlib.sha256((output/name).read_bytes()).hexdigest() for name in ['report.json','SUMMARY.txt']})
        with (output/'COMPLETE.json').open('x') as f:json.dump(marker,f,indent=2);f.write('\n')
        print(human,end='');return 0 if marker['cuda_operational'] else 2
    except (Exception,KeyboardInterrupt) as error:
        with (output/'INCOMPLETE.json').open('x') as f:json.dump(dict(complete=False,error='interrupted' if isinstance(error,KeyboardInterrupt) else type(error).__name__),f)
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('--output',required=True,type=Path);parser.add_argument('--timeout-seconds',default=60,type=int)
    args=parser.parse_args()
    if not 1<=args.timeout_seconds<=300:parser.error('timeout must be in [1,300] seconds')
    try:return execute(args.output,args.timeout_seconds)
    except KeyboardInterrupt:print('CUDA preflight interrupted; incomplete evidence retained.',file=sys.stderr);return 130
    except Exception as error:
        print('CUDA preflight reporting error: '+scrub(str(error),dict(os.environ)),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
