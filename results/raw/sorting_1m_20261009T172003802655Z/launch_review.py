import hashlib,json,os
from pathlib import Path
raw=Path(__file__).resolve().parent
before=json.loads((raw/'before_execution.json').read_text());paths=json.loads((raw/'paths.json').read_text())
assert not os.path.lexists(paths['matrix'])
assert before['mem_bytes']['MemAvailable']>=256*1024**2 and before['disk_bytes']['free']>=128*1024**2
for name,value in before['cgroup_ancestors'].items():
    if name.endswith('/memory.max') and value!='max':assert int(value)-int(before['cgroup_ancestors'][name.replace('memory.max','memory.current')])>=256*1024**2
for name,digest in json.loads((raw/'execution_inputs_sha256.json').read_text()).items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
print('Pre-execution gate passed: output absent, RAM/disk/cgroup headroom adequate, frozen inputs and protocol unchanged.')
