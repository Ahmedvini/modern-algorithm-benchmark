from pathlib import Path
import datetime,hashlib,json,os,subprocess,tarfile
root=Path('/content/mab_bounded_resume_20261011T024034091796Z');s=root/'source';e=root/'evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=json.loads((root/'source_manifest.json').read_text())
assert all(sha(s/p)==h for p,h in files.items())
builds=json.loads((e/'BUILD_COMPLETE.json').read_text())
for name,b in builds['builds'].items():
    assert all(sha(Path(b)/p)==h for p,h in builds['identities'][name].items())
assert (e/'BOUNDED_COMPLETE.json').is_file() and json.loads((e/'BOUNDED_COMPLETE.json').read_text())['complete'] is True
for name,b in builds['builds'].items():
    dest=e/('metadata_'+name);dest.mkdir()
    base=Path(b)
    for rel in ['CMakeCache.txt','CTestTestfile.cmake','DartConfiguration.tcl','compile_commands.json']:
        target=dest/rel
        with target.open('xb') as out:out.write((base/rel).read_bytes())
    for f in sorted((base/'generated').rglob('*')):
        if f.is_file():
            target=dest/f.relative_to(base);target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as out:out.write(f.read_bytes())
gpu=Path(builds['builds']['gpu-release'])
cache=(gpu/'CMakeCache.txt').read_text()
include=Path(next(x.split('=',1)[1] for x in cache.splitlines() if x.startswith('MAB_CUB_INCLUDE_DIR:PATH=')))
dependencies={str(p):sha(p) for p in [include/'cub/version.cuh',include/'cub/device/device_radix_sort.cuh']}
for line in cache.splitlines():
    if line.startswith(('OpenMP_gomp_LIBRARY:','OpenMP_pthread_LIBRARY:')):
        p=Path(line.split('=',1)[1])
        if p.is_file():dependencies[str(p.resolve())]=sha(p.resolve())
with (e/'DEPENDENCY_SNAPSHOT.json').open('x') as f:json.dump(dependencies,f,indent=2);f.write('\n')
links={n:(gpu/'CMakeFiles'/n/'link.txt').read_text() for n in
       ['cpu_gpu_comparison.dir','test_parallel_workers.dir','test_cuda_prepared_correctness.dir']}
assert all('libmab_parallel.a' in links[n] for n in ['cpu_gpu_comparison.dir','test_parallel_workers.dir'])
with (e/'LINK_BINDINGS.json').open('x') as f:json.dump(dict(commands=links,shared_parallel_library_sha256=sha(gpu/'libmab_parallel.a')),f,indent=2);f.write('\n')
argv=['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total,memory.free,temperature.gpu,clocks.sm,clocks.mem','--format=csv']
p=subprocess.run(argv,capture_output=True,text=True,timeout=30)
with (e/'FINAL_GPU_SNAPSHOT.json').open('x') as f:json.dump(dict(argv=argv,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr,observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),f,indent=2);f.write('\n')
assert p.returncode==0 and 'GPU-5d327ac4-2d0a-4a11-6bd7-97474ba6359c' in p.stdout and 'Tesla T4' in p.stdout
manifest={str(p.relative_to(e)):sha(p) for p in sorted(e.rglob('*')) if p.is_file()}
with (e/'REMOTE_INTEGRITY.json').open('x') as f:json.dump(manifest,f,indent=2,sort_keys=True);f.write('\n')
archive=root/'validation_evidence.tar.gz';assert not archive.exists()
with tarfile.open(archive,'x:gz') as t:
    for p in sorted(e.rglob('*')):
        if p.is_file():t.add(p,arcname=str(p.relative_to(root)),recursive=False)
print(json.dumps(dict(archive=str(archive),sha256=sha(archive),members=len(manifest)+1,
                     source_files_verified=len(files),build_identities_verified=True,all_validation_complete=True,
                     full_study_authorized=False),indent=2))
print('REMOTE_EVIDENCE_SEALED')
