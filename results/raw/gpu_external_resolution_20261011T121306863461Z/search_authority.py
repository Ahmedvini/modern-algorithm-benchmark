"""Search authorized home/configuration filenames, without reading credentials."""
import json
import os
from pathlib import Path

E = Path(__file__).resolve().parent
home = Path.home()
excluded = {'.cache', '.local', '.git', 'node_modules', '__pycache__', 'build',
            '.venv', 'venv', '.ssh', '.gnupg', '.pki', '.mozilla', '.google',
            '.colab-cli', 'colab-cli', 'google-chrome', 'chromium',
            'site-packages', 'Trash', 'sessions', 'history'}
found = []
errors = []
count = 0
directories = 0
def error(exc):
    errors.append({'path': str(exc.filename), 'error': type(exc).__name__})
for folder, dirs, names in os.walk(home, topdown=True, followlinks=False, onerror=error):
    dirs[:] = sorted(d for d in dirs if d not in excluded and not (Path(folder)/d).is_symlink())
    directories += 1
    for name in names:
        count += 1
        low = name.lower()
        if name == 'CPU_GPU_EVIDENCE_REVIEW_v1.json' or ('cpu_gpu' in low and any(s in low for s in ['approval', 'trust', 'review'])):
            p = Path(folder)/name
            item = {'file': str(p), 'symlink': p.is_symlink()}
            if name == 'CPU_GPU_EVIDENCE_REVIEW_v1.json' and not p.is_symlink():
                try:
                    value = json.loads(p.read_text())
                    item['schema_version'] = value.get('schema_version')
                    item['policy'] = value.get('policy')
                    item['approved'] = value.get('approved')
                except (ValueError, OSError, UnicodeError, AttributeError) as exc:
                    item['parse_error'] = type(exc).__name__
            found.append(item)
environment_names = sorted(n for n in os.environ if ('CPU_GPU' in n or 'MAB_' in n) and any(w in n for w in ['APPROVAL', 'TRUST', 'POLICY', 'REVIEW']))
result = {'scope':str(home), 'directories_inspected':directories, 'filenames_inspected':count,
          'excluded_directory_names': sorted(excluded), 'followed_symlinks':False,
          'credential_contents_read':False, 'candidates':found, 'errors':errors,
          'relevant_environment_variable_names':environment_names,
          'limitation':'Filename search includes accessible user project/config directories; excludes caches, package stores, credentials, browser profiles and private conversation/session logs. Exclusions are not claimed verified.'}
with (E/'USER_CONFIGURATION_SEARCH.json').open('x') as f:json.dump(result,f,indent=2,sort_keys=True)
print(json.dumps(result,indent=2))
