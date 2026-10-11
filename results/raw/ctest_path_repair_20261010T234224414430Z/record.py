"""Evidence recorder. Only inspected reads and focused inert Python commands."""
import datetime
import json
from pathlib import Path
import subprocess
import sys

base = Path(__file__).resolve().parent
name, safety, *argv = sys.argv[1:]
assert argv and argv[0] in ['cat', 'sed', 'rg', 'nl', 'tail', 'python3']
assert not any(Path(a).name in ['ctest', 'cmake', 'nvcc', 'colab'] for a in argv)
(base/'commands').mkdir(exist_ok=True)
result = subprocess.run(argv, capture_output=True, text=True, check=False)
record = dict(argv=argv, cwd=str(Path.cwd()), utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              exit_code=result.returncode, safety=safety, stdout=result.stdout, stderr=result.stderr)
with (base/'commands'/(name+'.json')).open('x') as f:
    json.dump(record, f, indent=2, sort_keys=True); f.write('\n')
print(result.stdout, end=''); print(result.stderr, end='', file=sys.stderr)
raise SystemExit(result.returncode)
