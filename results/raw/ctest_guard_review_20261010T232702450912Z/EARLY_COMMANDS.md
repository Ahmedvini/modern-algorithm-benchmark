# Early/unwrapped terminal commands

Each shell below returned exit0, as observed in terminal tool output. Multiline
shell statements were not separately instrumented. Some output was truncated;
no reconstructed stdout is represented as a raw subprocess log. Commands were
read-only except exclusive creation of this review directory and START_SNAPSHOT.

```sh
pwd
cat AGENTS.md
ls -la results/raw/ctest_hook_repair_20261010T223851377458Z
cat results/raw/ctest_hook_repair_20261010T223851377458Z/FINAL_AUDIT.md
cat results/raw/ctest_hook_repair_20261010T223851377458Z/COMMANDS.md
```

```sh
cat results/raw/cpu_gpu_repair_review_20261010T185659333607Z/FINAL_AUDIT.md
cat results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/FINAL_AUDIT.md
cat results/raw/ctest_hook_repair_20261010T223851377458Z/FINAL_INTEGRITY.json
```

Bootstrap executable command was `python3 -B -`, exit0. Its stdin was not retained
verbatim as an artifact before context compaction. The hashing/write body below
documents the operations; it is not offered as a byte-exact stdin transcript:

```python
import datetime,hashlib,json
from pathlib import Path
root=Path.cwd()
base=root/'results/raw'/('ctest_guard_review_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
base.mkdir()
def mapping(paths):return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
 for p in sorted(set(paths)) if p.is_file()}
results=mapping((root/'results').rglob('*'))
project=mapping([root/'AGENTS.md',root/'README.md',root/'CMakeLists.txt']+
[p for name in ['scripts','tests','docs','include','src','cmake','third_party']
for p in (root/name).rglob('*') if '__pycache__' not in p.parts])
build=mapping([p for p in (root/'build').rglob('*') if p.name in
['CTestTestfile.cmake','DartConfiguration.tcl','CTestCustom.cmake','CTestCustom.ctest']])
with (base/'START_SNAPSHOT.json').open('x') as f:
 json.dump(dict(prior_results_sha256=results,prior_result_count=len(results),
 project_sha256=project,build_metadata_sha256=build),f,indent=2,sort_keys=True);f.write('\n')
print(base)
```

The trailing diagnostic print labels are not reconstructed. The authoritative
exact hash maps/counts are START_SNAPSHOT.json. The bootstrap created the directory
named by this report exclusively; no pre-existing path was reused. All subsequent
review programs are retained in full and all wrapped child argv/output are logged.

Additional read-only inspection, exit0:

```sh
pwd
ls -la results/raw/ctest_guard_review_20261010T232702450912Z
cat results/raw/ctest_guard_review_20261010T232702450912Z/record.py
```

All other shell commands are recorded by record.py under commands/*.json.
apply_patch was used only to add new evidence programs/documents in this directory
(record.py, verify_evidence.py, static_review.py, FINAL_AUDIT.md,
EARLY_COMMANDS.md and seal_review.py). Tool edits have no shell exit code and
returned successful tool results except the evidence-document correction described
in TOOL_FAILURE.md. No project source, test, documentation, build,
manifest or old evidence file was edited.
