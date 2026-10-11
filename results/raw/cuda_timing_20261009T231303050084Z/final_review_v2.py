import hashlib,json,difflib
from pathlib import Path
p=json.loads(Path('build/cuda_timing_paths.json').read_text());e=Path(p['evidence']);before=json.loads((e/'source_before.json').read_text());b=Path(p['backup'])/'before'
current={}
for base in ['include','src','tests','scripts','cmake','docs','third_party']:
 for f in sorted(Path(base).rglob('*')):
  if f.is_file() and '__pycache__' not in f.parts:current[str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
for name in ['CMakeLists.txt','README.md','AGENTS.md','.gitignore']:current[name]=hashlib.sha256(Path(name).read_bytes()).hexdigest()
added=sorted(set(current)-set(before));modified=sorted(k for k in before if k in current and current[k]!=before[k]);deleted=sorted(set(before)-set(current));assert not deleted,deleted
allowed={'CMakeLists.txt','cmake/cuda.cmake','README.md','docs/AUDIT.md','docs/ROADMAP.md','docs/ALGORITHMS.md','docs/BENCHMARKING.md','docs/EXPERIMENT_PROTOCOL.md','docs/METRICS.md'}
assert set(modified)<=allowed,set(modified)-allowed
assert Path('cmake/cuda.cmake').read_text().split('    # Benchmark-only prepared execution')[0]==(b/'cmake/cuda.cmake').read_text().split('    if(BUILD_TESTING)\n        add_executable(test_cuda_sorting')[0]
protected={k:v for k,v in before.items() if k not in allowed};assert all(current[k]==v for k,v in protected.items())
remote=json.loads((e/'downloaded/remote_source_manifest.json').read_text())
code=[k for k in remote if not k.startswith('docs/') and k!='README.md']
assert all(hashlib.sha256(Path(k).read_bytes()).hexdigest()==remote[k] for k in code)
assert hashlib.sha256(Path('docs/CUDA_TIMING_PROTOCOL_v1.md').read_bytes()).hexdigest()==remote['docs/CUDA_TIMING_PROTOCOL_v1.md']
artifacts=json.loads((e/'prior_artifacts_sha256.json').read_text())
assert all(Path(k).is_file() and hashlib.sha256(Path(k).read_bytes()).hexdigest()==v for k,v in artifacts.items())
changes=dict(added=added,modified=modified,deleted=deleted,protected_starting_sources=len(protected),protected_sources_unchanged=True,
             final_code_matches_gpu_tested_bundle=True,gpu_tested_files_checked=len(code),timing_protocol_unchanged_after_execution=True,
             prior_artifacts_verified=len(artifacts),prior_artifacts_changed=0)
with (e/'changes.json').open('x') as f:json.dump(changes,f,indent=2);f.write('\n')
with (e/'source_after.json').open('x') as f:json.dump(current,f,indent=2,sort_keys=True);f.write('\n')
purpose={'CMakeLists.txt':'Register always-host CUDA analysis tests; preserve CPU targets/defaults.',
'cmake/cuda.cmake':'Opt-in prepared CUDA library/CLI/GPU framework and generated CUDA build metadata; pin unchanged.',
'include/benchmark/cuda_timing.hpp':'Benchmark-only RAII prepared-session API with four measurements.',
'src/cuda/cub_timing.cu':'Checked same-stream event/transfer/CUB/synchronization execution; reusable pinned/device buffers.',
'src/benchmark/cuda_main.cpp':'Release-only CLI, dataset restoration/oracle checks, CSV/metadata and safe bundles.',
'scripts/analyze_cuda_results.py':'Strict schema/completeness checks and per-dataset four-metric statistics.',
'scripts/run_cuda_matrix.py':'Exclusive serial deterministic matrix with exact command/failure/interruption evidence.',
'scripts/validate_cuda_timing.py':'Real-GPU correctness -> smallest smoke -> framework -> matrix -> summary/hash verification.',
'docs/CUDA_TIMING_PROTOCOL_v1.md':'Versioned timing/allocation/workload/output/analysis contract frozen before execution.',
' tests/test_cuda_benchmark.py'.strip():'12 host fixture methods and2 actual GPU CLI/integration methods; correctness, statistics, failures and safety.'}
lines=['# Files changed','', 'No Git metadata. Changes are compared to source_before.json and the private local before-copy; no existing source file was deleted. CPU implementations, production CUDA adapter, CUB dependency metadata/license and frozen protocols remain byte-identical.','', '| File | Status | Purpose |','| --- | --- | --- |']
for name in added+modified:lines.append('| `'+name+'` | '+('added' if name in added else 'modified')+' | '+purpose.get(name,'Document actual implementation, validation evidence, commands, limits and milestone status.')+' |')
lines.extend(['','New evidence/derived outputs: '+str(e)+' and results/processed/'+p['runid']+'. Builds and credential-bearing CLI config stay under '+p['backup']+'; credentials are excluded from evidence. Source bundle fixes the tested snapshot; only documentation changed after GPU execution.','', 'Final protected source check: '+str(len(protected))+' starting files unchanged; '+str(len(code))+' tested non-document files match remote source. New timing protocol also matches. All'+str(len(artifacts))+' earlier result files remain unchanged.'])
with (e/'CHANGES.md').open('x') as f:f.write('\n'.join(lines)+'\n')
patch=[]
for name in modified+added:
 old=(b/name).read_text().splitlines(True) if (b/name).exists() else []
 patch.extend(difflib.unified_diff(old,Path(name).read_text().splitlines(True),fromfile='a/'+name if old else '/dev/null',tofile='b/'+name))
with (e/'source_changes.patch').open('x') as f:f.writelines(patch)
print(json.dumps(changes,indent=2))
