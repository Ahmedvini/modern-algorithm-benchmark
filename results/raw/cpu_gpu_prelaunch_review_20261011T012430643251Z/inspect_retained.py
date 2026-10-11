import collections,hashlib,json,re
from pathlib import Path
R=Path.cwd(); E=Path(__file__).resolve().parent
OLD=R/'results/raw/isolated_colab_revalidation_20261011T011459127026Z'
V=OLD/'remote_evidence/validation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def verify(mapping,root):
    bad=[k for k,v in mapping.items() if not (root/k).is_file() or sha(root/k)!=v]
    assert not bad,bad
    return len(mapping)
out={}
seal=load(OLD/'FINAL_INTEGRITY.json')['evidence_sha256']
out['isolated_seal_verified']=verify(seal,OLD)
assert set(seal)=={str(p.relative_to(OLD)) for p in OLD.rglob('*') if p.is_file() and p.name!='FINAL_INTEGRITY.json'}
remote=load(V/'EVIDENCE_SHA256.json');out['remote_seal_verified']=verify(remote,V)
assert set(remote)=={str(p.relative_to(V)) for p in V.rglob('*') if p.is_file() and p.name!='EVIDENCE_SHA256.json'}
source=load(OLD/'SOURCE_IDENTITY.json')['files_sha256']
out['transferred_source_matches_local']=verify(source,R)
assert (V/'SOURCE_AFTER.json').read_bytes()==(OLD/'SOURCE_IDENTITY.json').read_bytes()
freeze=load(R/'docs/studies/cpu_gpu_comparison_v1.freeze.json')
out['freeze_members_verified']=verify(freeze['files_sha256'],R)
out['freeze_hashes']=freeze['files_sha256']
matrix=load(R/'docs/studies/cpu_gpu_comparison_v1.matrix.json')
anchors=matrix['source_at_freeze_sha256']
out['anchors_exact_matches']=sum((R/k).is_file() and sha(R/k)==v for k,v in anchors.items())
out['anchor_differences']={k:{'frozen':v,'current':sha(R/k)} for k,v in anchors.items() if sha(R/k)!=v}
out['driver_review']=load(R/'docs/CPU_GPU_DRIVER_REVIEW_v1.json')
out['cub_pin']=load(R/'third_party/cub/UPSTREAM.json')
out['production_adapter_sha256']=sha(R/'src/cuda/cub_sort.cu')
before=load(E/'BEFORE.json')
out['project_files_verified']=verify(before['project_sha256'],R)
out['build_metadata_verified']=verify(before['build_metadata_sha256'],R)
lines=(V/'build.stderr.txt').read_text().splitlines()
warnings=[{'log_line':i+1,'diagnostic':line,'context':lines[i+1:i+3]} for i,line in enumerate(lines) if 'warning:' in line]
out['warning_count']=len(warnings)
out['warning_categories']=dict(collections.Counter(x['diagnostic'].split('warning:',1)[1].strip() for x in warnings))
out['warning_locations']=dict(collections.Counter(re.sub(r':\d+:\d+: warning:.*','',x['diagnostic']) for x in warnings))
out['generated_marker_blocks']=[x for x in warnings if '.cudafe1.' in x['diagnostic']]
out['error_lines']=[{'line':i+1,'text':s} for i,s in enumerate(lines) if re.search(r'\berror:|fatal error',s)]
out['cuda_compile_commands']=[x for x in load(V/'compile_commands.json') if x['file'].endswith('.cu')]
out['source_line_directives']={}
for f in ['src/cuda/comparison_resources.cu','src/cuda/cub_sort.cu','src/cuda/cub_timing.cu']:
    out['source_line_directives'][f]=[{'line':i+1,'text':s} for i,s in enumerate((R/f).read_text().splitlines()) if re.match(r'\s*#\s*(?:line\b|\d)',s)]
result=load(V/'RESULT.json')
out['executed_records']=result['records']
out['coverage']={k:result[k] for k in ['cpu_correctness','cuda_correctness','study_eligible','validation_passed','ctest_invocations','benchmarks','timing_trials']}
env=load(V/'ENVIRONMENT.json')
blocks=env['cpuinfo'].strip().split('\n\n')
out['environment']={k:env[k] for k in ['affinity','cpu_count','disk','environment','platform','python']}
out['cpu_topology']=[{k:v.strip() for line in b.splitlines() if ':' in line for k,v in [line.split(':',1)] if k.strip() in ['processor','model name','cpu MHz','physical id','siblings','core id','cpu cores']} for b in blocks]
out['meminfo_bytes']={m.group(1):int(m.group(2))*1024 for s in env['meminfo'].splitlines() if (m:=re.match(r'(MemTotal|MemAvailable|SwapTotal):\s+(\d+) kB',s))}
out['frozen_resources']=matrix['resources']
out['frozen_launch_gates']=matrix['launch_gates']
out['frozen_openmp_policy']=matrix['openmp_policy']
out['matrix_counts']={k:matrix[k] for k in ['warmups','repetitions','study','pilot']}
with (E/'INDEPENDENT_FINDINGS.json').open('x') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
with (E/'WARNING_DIAGNOSTICS.json').open('x') as f:json.dump(warnings,f,indent=2);f.write('\n')
print(json.dumps({k:out[k] for k in ['isolated_seal_verified','remote_seal_verified','transferred_source_matches_local','freeze_members_verified','anchors_exact_matches','anchor_differences','project_files_verified','build_metadata_verified','warning_count','warning_categories','generated_marker_blocks','error_lines','coverage','environment','cpu_topology','meminfo_bytes']},indent=2))
