"""Record explicitly reviewed, non-workload repair commands, never CTest."""
import datetime
import json
from pathlib import Path
import subprocess
import sys

base = Path(__file__).resolve().parent
name, safety, *argv = sys.argv[1:]
assert argv and not any(Path(a).name in {'ctest', 'colab', 'nvcc'} for a in argv)
result = subprocess.run(argv, text=True, capture_output=True, check=False)
record = dict(argv=argv, cwd=str(Path.cwd()), exit_code=result.returncode,
              safety=safety, stdout=result.stdout, stderr=result.stderr,
              utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(base/'commands').mkdir(exist_ok=True)
with (base/'commands'/(name+'.json')).open('x') as stream:
    json.dump(record, stream, indent=2, sort_keys=True); stream.write('\n')
print(result.stdout, end=''); print(result.stderr, end='', file=sys.stderr)
raise SystemExit(result.returncode)
