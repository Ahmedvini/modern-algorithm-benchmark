# Review commands and observed exit statuses

These are new review commands, not a rerun of historical builds or measurements. Full argv/stdout/stderr/timestamps are in commands/*.json.

- `python3 -B results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/inspect_bundle.py` — exit 0; `commands/bundle_review.json`.
- `env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/probe_full_analysis.py` — exit 1; `commands/full_analysis_probe.json`.
- `git status --short` — exit 128; `commands/git_status.json`.
- `python3 -B results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/verify_retained.py` — exit 0; `commands/integrity.json`.
- `env PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/analyze_cpu_gpu.py results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3 --output results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/PILOT_REANALYSIS.json` — exit 0; `commands/pilot_reanalysis.json`.
- `env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/check_plan_and_compatibility.py` — exit 0; `commands/plan_and_compatibility.json`.
- `python3 -B results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/review_selection.py` — exit 0; `commands/selection_review.json`.
- `env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/probe_source_validation.py` — exit 1; `commands/source_validation_probe.json`.
- `env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/probe_source_validation_v2.py` — exit 1; `commands/source_validation_probe_v2.json`.
- `env PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_cpu_gpu_comparison.py build/cpu_gpu_full_tooling_20261010T121208603276Z/release/comparison_input` — exit 0; `commands/synthetic_framework.json`.

Dry-run child invocations are also recorded exactly in PLAN_AND_COMPATIBILITY.json (two identical commands, both exit0); they launched no worker and created no study directory.

Before the recorder was created, read-only pwd/cat/sed/rg/Python inspections read AGENTS, protocol, evidence and implementation files. An initial git status reported128. The repository-wide result snapshot command used Python SHA-256 and created START_SNAPSHOT.json, exit0. Evidence-only apply_patch/new-version creation commands created the scripts retained here; no project source was edited.

Final command: `python3 -B /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/finalize_review.py`. Its successful completion and preservation checks are recorded in FINAL_INTEGRITY.json; this command creates that manifest last.

The recorded six-row historical CTest command is reproduced in SELECTION_REVIEW.json and the original milestone COMMANDS.md. It was inspected, not executed in this review. Fresh Release/sanitizer/GPU builds, CTest, Colab commands, prerequisites-only validation, pilot, study and all timing trials were NOT executed.
