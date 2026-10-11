from pathlib import Path
import sys,json,shutil,datetime
root=Path.cwd();sys.path.insert(0,str(root/'scripts'))
from experiment_model import load_json,save_json,sha256,tree_hashes
from run_parallel_matrix import make_plan,preset
from run_experiments import resource_snapshot,check_resources
p=load_json(root/'build/phase6_paths.json');e=root/p['evidence'];name=p['full_retry']
for stem in ['corrected_release_configure','corrected_release_build','corrected_release_ctest','corrected_sanitize_configure','corrected_sanitize_build','corrected_sanitize_ctest','corrected_parallel_python','retry_smoke_verification']:
 assert load_json(e/'commands'/(stem+'.json'))['exit_code']==0,stem
forecast=load_json(e/'retry_full_forecast.json');assert forecast['runtime_gate_passed']
plan=make_plan(preset('full'),root/'build/release/parallel_sort_benchmark',root/'results/raw'/name,root/'results/processed'/name,root/'results/figures'/name)
for key in ['raw_path','processed_path','figure_path']:assert not Path(plan[key]).exists()
snapshot=resource_snapshot(root/'results/raw');check_resources(snapshot,plan['resources']);assert len(snapshot['affinity'])>=8
source=load_json(root/'build/release/generated/Release/source_hashes.json')
assert all(sha256(root/f['path'])==f['sha256'] for f in source['files'])
assert all(sha256(root/f)==h for f,h in load_json(e/'prior_artifacts_sha256.json').items())
assert sha256(root/'docs/OPENMP_PROTOCOL_v1.md')==load_json(e/'protocol.json')['sha256']
save_json(e/'retry_full_launch_plan.json',plan);save_json(e/'retry_full_launch_resources.json',snapshot)
tools=e/'retry_execution_tools';tools.mkdir();hashes={}
for f in (root/'scripts').glob('*.py'):shutil.copyfile(f,tools/f.name);hashes[f.name]=sha256(f)
save_json(tools/'sha256.json',hashes)
smoke={}
for directory in ['raw','processed','figures']:
 for f in (root/'results'/directory/p['smoke_retry']).rglob('*'):
  if f.is_file():smoke[f.relative_to(root).as_posix()]=sha256(f)
save_json(e/'smoke_retry_before_full.json',smoke)
command='python3 scripts/run_parallel_matrix.py --preset full --output results/raw/'+name+' --processed results/processed/'+name+' --figures results/figures/'+name
text='''# OpenMP scaling study v2 — frozen retry launch

Attempt1 retained FAILED after all180 children completed1800 measured/360 warmups:
the analyzer incorrectly required floor(N/100) swaps for sorted input, whose existing
contract records0. Corrected analyzer plus all-five-distribution regression passed
fresh suites before retry. The timing engine, binary, workload and trial counts are
unchanged; no retry in place or pooling with attempt1. Original launch v1 remains
immutable. This document clarifies swap metadata and freezes new output paths.

Saved before the retry; no previous protocol or result changes. This extends
OPENMP_PROTOCOL_v1.md (parallel_sort_timing_v1) with the unchanged full preset.

180 configurations: N32768/100000/1000000, uniform/sorted/reverse_sorted/
duplicate_heavy/nearly_sorted, seeds1729/42/2718, threads1/2/4/8. Two sorters:
sequential merge_sort and parallel_merge_sort. W1/R5, cardinality16, swaps=0 for sorted and floor(N/100) otherwise,
256MiB array planning budget. Expected1800 measured and360 warmup rows.
OMP_DYNAMIC=FALSE,OMP_THREAD_LIMIT=8,OMP_MAX_ACTIVE_LEVELS=1,OMP_WAIT_POLICY=PASSIVE.
Actual team must equal request above threshold; team size is not a busy-worker count.

Shared timing engine; identical restored inputs; generation/copying/full reference
validation excluded. Allocation/team creation/task execution/joins/deallocation
included. No counting/RSS. Primary ratio uses same-cell sequential median; separate
parallel-request1 ratio. Per-dataset medians and ratios precede equal-weight distinct
input aggregation. Keep all outliers and sample SD/min/max; no significance claim.
Fixed size/seed/distribution/thread order and cyclic algorithm order, odd R imbalance,
serial parent merges, warmed copies and uncontrolled shared-machine frequency/cache/
thermal/background state remain confounders. No affinity/governor change; thermal
state unmeasured. ThreadSanitizer startup fails in this environment, including a
non-OpenMP probe; ordinary stress/ASan/UBSan are not a race-freedom proof.

Prelaunch gates: final reviewed Release24/24 and ASan/UBSan24/24, leak detection
on; Python13/13; smoke32 configurations,320 measured/64 warmup successes, zero
failed/missing trials; exact derived regeneration; prior3796 artifact hashes match.
Smoke overhead-inclusive child wall forecast, scaled by Nlog2(N+2) and fourfold
allowance, is '''+str(forecast['forecast_seconds'])+''' seconds, below1800s budget;
plotting separate. This is a forecast, not measured full duration. Resource estimates
and actual available resources below are planning values, not measured algorithm RSS.

Exact command:
```sh
'''+command+'''
```

Configuration/source identity and resource evidence:
```json
'''+json.dumps(dict(frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),configuration_sha256=plan['configuration_sha256'],implementation_protocol_sha256=load_json(e/'protocol.json')['sha256'],binary_sha256=sha256(root/'build/release/parallel_sort_benchmark'),resources=plan['resources'],snapshot=snapshot),indent=2,sort_keys=True)+'''
```

Results are complete only if every configuration/trial/actual-team/correctness
check passes and summaries/plots/report regenerate from immutable raw data.
Failures/interruption are retained, never completion; no retries in-place.
No CUDA, learned index, AlphaDev or100M work. Maximum study size1M.
'''
protocol=root/'docs/studies'/(name+'_v2.md')
with protocol.open('x') as f:f.write(text)
with (e/'RETRY_FULL_STUDY_LAUNCH_v2.md').open('x') as f:f.write(text)
save_json(e/'retry_full_protocol.json',dict(path=protocol.relative_to(root).as_posix(),sha256=sha256(protocol)))
print(json.dumps(dict(configurations=len(plan['cases']),measured=1800,warmups=360,forecast_seconds=forecast['forecast_seconds'],resources=plan['resources'],available_memory=snapshot['available_memory_bytes'],disk_free=snapshot['disk_free_bytes'],protocol=str(protocol)),indent=2))
