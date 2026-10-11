"""Review evidence only: capture commands without invoking any benchmark implicitly."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

base = Path(__file__).resolve().parent
name, *argv = sys.argv[1:]
record = dict(argv=argv, cwd=os.getcwd(), started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
child = subprocess.run(argv, capture_output=True, text=True)
record.update(exit_code=child.returncode, stdout=child.stdout, stderr=child.stderr,
              ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
with (base / 'commands' / (name + '.json')).open('x') as stream:
    json.dump(record, stream, indent=2, sort_keys=True)
    stream.write('\n')
print(json.dumps(dict(command=name, exit_code=child.returncode)))
print(child.stdout)
print(child.stderr, file=sys.stderr)
raise SystemExit(child.returncode)
