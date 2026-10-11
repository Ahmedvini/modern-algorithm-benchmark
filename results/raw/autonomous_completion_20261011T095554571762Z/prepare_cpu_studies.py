import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'scripts'))
from cpu_gpu_protocol import source_manifest, load_protocol
E = Path(__file__).resolve().parent
def write(path, value):
    with path.open('x') as stream: json.dump(value, stream, indent=2, sort_keys=True); stream.write('\n')
model = load_protocol()
base_path=ROOT/'docs/NON_TIMING_TEST_SELECTION_v3.json'
base=json.loads(base_path.read_text()); current=source_manifest()
old=base['reviewed_source_sha256']
delta=dict(added=sorted(set(current)-set(old)),removed=sorted(set(old)-set(current)),
           modified=sorted(p for p in set(old)&set(current) if old[p]!=current[p]))
selection=dict(base,schema_version=5,policy='non_timing_correctness_v5',scope='local_correctness_only',
               full_study_eligible=False,base_manifest_sha256=hashlib.sha256(base_path.read_bytes()).hexdigest(),
               reviewed_source_sha256=current,source_delta=delta,
               authorization='User standing autonomous authorization; local source review only; no independent study approval fabricated')
write(ROOT/'docs/NON_TIMING_TEST_SELECTION_v5.json',selection)
write(E/'SELECTION_REVIEW.json',dict(default_tests=sorted(n for n,e in base['tests'].items() if e['classification']=='cpu_correctness' and not e.get('diagnostic_only')),
    commands_properties_classifications_unchanged=True,source_delta=delta,current_source_sha256=current,
    basis='Static review of registrations and guarded paths; new learned tests execute separately; full-study anchor remains uninstalled'))
matrix=dict(schema_version=1,protocol='learned_rank_v1',sizes=[1000,10000,100000,1000000],seeds=[42,2718,314159],
    development_seed=1729,warmups=1,repetitions=5,queries=1000,hit_queries=500,query_seed=2718,radius=32,
    cells=[dict(id=f'n{n}_{d}_s{s}',size=n,distribution=d,seed=s) for n in [1000,10000,100000,1000000]
           for d in ['uniform','nearly_sorted','reverse_sorted','duplicate_heavy'] for s in [42,2718,314159]])
write(ROOT/'docs/studies/learned_rank_v1.matrix.json',matrix)
write(E/'LEARNED_FREEZE.json',dict(files_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
      [ROOT/'docs/LEARNED_INDEX_PROTOCOL_v1.md',ROOT/'docs/studies/learned_rank_v1.matrix.json']},expected_measured_lookup_batches=480,
      expected_measured_builds=240,expected_warmup_lookup_batches=96,expected_warmup_builds=48))
print('Frozen CPU/GPU matrix verified:',len(model['study']['cells']),'datasets')
print('v5 local correctness snapshot:',len(current),'files; exact default19 preserved; full study NOT eligible')
print(json.dumps(delta,indent=2))
