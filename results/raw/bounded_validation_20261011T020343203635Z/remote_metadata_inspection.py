from pathlib import Path
import hashlib,json,sys
root=Path('/content/mab_bounded_20261011T020343203635Z');source=root/'source';e=root/'evidence'
policy=json.loads((source/'docs/NON_TIMING_TEST_SELECTION_v2.json').read_text())['build_metadata']['dart_defaults']
reports={}
for name in ['cpu-release','cpu-sanitize','gpu-release']:
    b=root/name
    raw=(b/'DartConfiguration.tcl').read_text()
    values={line.split(': ',1)[0]:line.split(': ',1)[1] for line in raw.splitlines() if line.strip() and not line.lstrip().startswith('#')}
    reports[name]=dict(extra_keys=sorted(set(values)-set(policy)),missing_keys=sorted(set(policy)-set(values)),
                       differing_values={k:dict(expected=policy[k],actual=v) for k,v in values.items()
                                         if k in policy and v!=policy[k].replace('@source',str(source)).replace('@build',str(b))},
                       dart_sha256=hashlib.sha256(raw.encode()).hexdigest())
    dest=e/('metadata_'+name);dest.mkdir()
    for f in ['DartConfiguration.tcl','CTestTestfile.cmake','CMakeCache.txt','compile_commands.json']:
        (dest/f).write_bytes((b/f).read_bytes())
    generated=dest/'generated';generated.mkdir()
    for p in (b/'generated').rglob('*'):
        if p.is_file():
            d=generated/p.relative_to(b/'generated');d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(p.read_bytes())
with (e/'DART_GUARD_BLOCKER.json').open('x') as f:json.dump(reports,f,indent=2);f.write('\n')
print(json.dumps(reports,indent=2))
print('READ_ONLY_METADATA_INSPECTION_COMPLETE; NO CTEST EXECUTED')
