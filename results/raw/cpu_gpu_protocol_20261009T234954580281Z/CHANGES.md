# Changes for the CPU/GPU protocol deliverable

New frozen project documentation/assets:

* `docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md`: full design, scopes, matrix, deterministic
  order, statistical policy, resource/runtime assumptions and acceptance checklist.
* `docs/studies/cpu_gpu_comparison_v1.matrix.json`: explicit pilot/study recipes and
  orders, expected counts, source/CUB identity, schema specification and launch gates.
* `docs/studies/cpu_gpu_comparison_v1.resources.csv`: per-size calculated host/device
  payloads, historical prepared workspace where known, current unknowns and policy caps.
* `docs/studies/cpu_gpu_comparison_v1.freeze.json`: exact three-asset SHA-256 freeze,
  frozen-for-review status and execution_authorized=false.

Updated existing documentation:

* `README.md`: new protocol links, pending driver and matched-scope explanation.
* `docs/ROADMAP.md`: CUDA status-row update and next implementation milestone.
* `docs/BENCHMARKING.md`: planned scope/matrix/resource summary, no executable claim.
* `docs/AUDIT.md`: evidence, actual validation, skipped/unexecuted checks and limits.

New uniquely named planning evidence directory:
`results/raw/cpu_gpu_protocol_20261009T234954580281Z/`.
It retains starting snapshots/hashes, generation/freeze/static-validation helpers,
all validation command records, local planning metadata, editor diagnostics and
final audit/integrity. These helpers do not implement or execute benchmark timing.
Working backups/intermediate generated assets remain under
`build/cpu_gpu_protocol_20261009T234954580281Z/`; no prior evidence was overwritten.

No production algorithm, interface, CMake, benchmark CLI, analyzer, test source,
vendored file, dependency pin or historical experiment artifact was modified.
No commit/push or study execution was performed.
