# Commands and observed statuses

No CTest discovery/tests, configure/build, CUDA API/kernel, benchmark, warm-up, measured trial or full study was executed.
The remote programs use metadata/file reads and management/version commands only. Full command bodies are retained in the two diagnostic .py files.

Local capture wrapper for each record below: `python3 -B results/raw/colab_t4_diagnostics_20261011T005409276199Z/record.py NAME SCOPE CHILD_ARGV...`.
Each JSON record contains exact child argv, cwd, stdout/stderr and status. Capture timestamps are collection timestamps (the helper assigns started_utc after completion).

## cli_exec_help.json

```text
colab exec --help
```
Exit: 0. Scope: CLI metadata/session inventory only.

## cli_new_help.json

```text
colab new --help
```
Exit: 0. Scope: CLI metadata/session inventory only.

## cli_sessions.json

```text
colab sessions
```
Exit: 0. Scope: CLI metadata/session inventory only.

## cli_usage_docs.json

```text
colab readme
```
Exit: 0. Scope: CLI metadata/session inventory only.

## cli_version.json

```text
colab version
```
Exit: 0. Scope: CLI metadata/session inventory only.

## create_t4.json

```text
colab new --session cpu-gpu-validation --gpu T4
```
Exit: 0. Scope: Explicitly authorized T4 session provisioning only; no workload script.

## remote_diagnostic_run.json

```text
colab exec --session cpu-gpu-validation --file /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/colab_t4_diagnostics_20261011T005409276199Z/remote_diagnostics.py --timeout 120
```
Exit: 0. Scope: Remote management/version/file diagnostics only; no CUDA APIs or project executable.

## runtime_files_run.json

```text
colab exec --session cpu-gpu-validation --file /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/colab_t4_diagnostics_20261011T005409276199Z/runtime_files_diagnostic.py --timeout 60
```
Exit: 0. Scope: Read-only remote library filenames and header versions; no loading/API execution.

## session_status.json

```text
colab status --session cpu-gpu-validation
```
Exit: 0. Scope: Session state diagnostic only.

## session_status_final.json

```text
colab status --session cpu-gpu-validation
```
Exit: 0. Scope: Session metadata only; no workload or CUDA execution.

## sessions_after_create.json

```text
colab sessions
```
Exit: 0. Scope: Session state diagnostic only.

## verification_json_format_correction.json

```text
python3 -B -c 'import json;from pathlib import Path
e=Path('"'"'results/raw/colab_t4_diagnostics_20261011T005409276199Z'"'"');raw=(e/'"'"'VERIFIED_BEFORE.json'"'"').read_text();data=json.loads((e/'"'"'verify_before.json'"'"').read_text());clean=json.loads(data['"'"'stdout'"'"'])
with (e/'"'"'VERIFIED_BEFORE_V2.json'"'"').open('"'"'x'"'"') as f: print(json.dumps(clean,indent=2),file=f)
print('"'"'Retained initial file with literal backslash-n footer; corrected evidence JSON from retained verification stdout, no checks rerun or weakened.'"'"')
'
```
Exit: 0. Scope: Own evidence formatting only; original retained.

## verify_before.json

```text
python3 -B -c 'import json,hashlib;from pathlib import Path
r=Path.cwd();e=r/'"'"'results/raw/colab_t4_diagnostics_20261011T005409276199Z'"'"'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
seal=json.loads((r/'"'"'results/raw/cpu_gpu_readiness_20261011T004018152238Z/FINAL_INTEGRITY.json'"'"').read_text())
freeze=r/'"'"'docs/studies/cpu_gpu_comparison_v1.freeze.json'"'"'
assert sha(freeze)=='"'"'518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6'"'"'
maps={'"'"'readiness_evidence'"'"':seal['"'"'evidence_sha256'"'"'],'"'"'frozen_members'"'"':json.loads(freeze.read_text())['"'"'files_sha256'"'"'],'"'"'reviewed_source'"'"':json.loads((r/'"'"'docs/NON_TIMING_TEST_SELECTION_v1.json'"'"').read_text())['"'"'reviewed_source_sha256'"'"']}
report={}
for name,m in maps.items():
 changed=[p for p,h in m.items() if not(r/p).is_file() or sha(r/p)!=h];report[name]={'"'"'files'"'"':len(m),'"'"'differences'"'"':changed};assert not changed,name
assert sha(r/'"'"'src/cuda/cub_sort.cu'"'"')==seal['"'"'production_adapter_sha256'"'"']
assert sha(r/'"'"'third_party/cub/UPSTREAM.json'"'"')==seal['"'"'cub_pin_sha256'"'"']
with (e/'"'"'VERIFIED_BEFORE.json'"'"').open('"'"'x'"'"') as f:json.dump(report,f,indent=2);f.write('"'"'\n'"'"')
print(json.dumps(report,indent=2))'
```
Exit: 0. Scope: Static integrity only.

## Remote inner commands (all exit 0)

- `uname -a`: 0 (version, OS, NVML management or linker-cache metadata).
- `python3 --version`: 0 (version, OS, NVML management or linker-cache metadata).
- `cmake --version`: 0 (version, OS, NVML management or linker-cache metadata).
- `g++ --version`: 0 (version, OS, NVML management or linker-cache metadata).
- `nvcc --version`: 0 (version, OS, NVML management or linker-cache metadata).
- `nvidia-smi`: 0 (version, OS, NVML management or linker-cache metadata).
- `nvidia-smi --query-gpu=name,uuid,driver_version,memory.total,memory.free,temperature.gpu,clocks.sm,clocks.mem,power.limit --format=csv,noheader,nounits`: 0 (version, OS, NVML management or linker-cache metadata).
- `nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader,nounits`: 0 (version, OS, NVML management or linker-cache metadata).
- `ldconfig -p`: 0 (version, OS, NVML management or linker-cache metadata).

## Evidence authoring and direct reads

The initial `pwd`, `cat AGENTS.md`, and cat of the readiness FINAL_AUDIT.md, COMMANDS.md, FINAL_INTEGRITY.json and docs/CUDA_EXECUTION_GUIDE_v1.md completed with shell exit 0.
The exclusive baseline creation used `python3 -B -` (exit 0); its complete shell program is retained in EARLY_COMMANDS.json. Only this evidence directory was created.
Subsequent `pwd` / `ls` of this evidence directory, stdlib Python JSON/key/output inspections, and cat of the prior readiness audit, local CUB pin and record.py all completed with exit 0. No project code was imported.
Source authoring used apply_patch for record.py, both diagnostic programs and this finalizer; all additions are inside this new evidence directory.
Finalization command: `python3 -B results/raw/colab_t4_diagnostics_20261011T005409276199Z/finalize_evidence.py` (exit 0 when FINAL_INTEGRITY.json exists; assertions precede the seal). It parses retained logs, hashes files and writes new evidence only.
Polling write_stdin waited on those same diagnostic/status commands; it did not launch any extra workload.

Retained evidence-format issue: VERIFIED_BEFORE.json had a literal trailing backslash-n and was not strict JSON. The correction command preserved it and created VERIFIED_BEFORE_V2.json; all hash checks passed. No environment or validation failure was suppressed.
