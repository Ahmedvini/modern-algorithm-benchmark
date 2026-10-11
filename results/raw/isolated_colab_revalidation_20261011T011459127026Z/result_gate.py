import json
from collections import Counter
from pathlib import Path
e=Path(__file__).resolve().parent
log=json.loads((e/'isolated_build_validation.json').read_text());assert log['exit_code']==0
text=log['stdout'];assert text.count('ISOLATED_VALIDATION_BEGIN')==text.count('ISOLATED_VALIDATION_END')==1
remote=json.loads(text.split('ISOLATED_VALIDATION_BEGIN')[1].split('ISOLATED_VALIDATION_END')[0])
result=remote['result'];assert result['validation_passed'] and remote['validation_passed']
assert [r['name'] for r in result['records']]==['configure','build','cpu_correctness','gpu_correctness','comparison_describe']
assert all(r['exit_code']==0 for r in result['records'])
assert (result['cuda_correctness']['cases'],result['cuda_correctness']['output_checks'])==(475,1900)
assert result['ctest_invocations']==result['timing_trials']==result['benchmarks']==0
assert remote['evidence_archive']=='/content/mab_isolated_20261011T011459127026Z/validation_evidence.tar.gz'
assert not (e/'downloaded_validation.tar.gz').exists()
with (e/'REMOTE_RESULT_CHECKED.json').open('x') as f:json.dump(remote,f,indent=2);f.write('\n')
print(json.dumps({k:remote[k] for k in ['validation_passed','evidence_archive','archive_sha256']},indent=2))
print('GPU:',result['cuda_correctness']);print('CPU:',result['cpu_correctness'])
print('Warnings:',dict(Counter(w['text'].split('warning:',1)[-1] for w in result['warnings'])))
