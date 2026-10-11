## Post-cloud validation — first CUB correctness slice, hardware validation pending

Inspected AGENTS.md, README/roadmap/audit/protocols, CMake/CUDA isolation, existing
CPU and parallel sorter interfaces/registries/implementations, differential tests,
preflight and runner conventions, Phase7/blocked-gate records and new cloud archive.
Git status/branches/log each exit128: no Git metadata, branches/commits/uncommitted
status unavailable; no Git initialization/commit/push. Anonymous temporary-file
write verified access. Source before: 127 files including .gitignore,
backup under build/cub_sort_review_20261009T220322089788Z; all 8,709 earlier results/evidence files
hashed before edits. No existing user source was discarded.

Initial root-level cloud archive lookup failed (ls2, sha256sum1, tar2), resolved by
file search to results/evidence/cloud_validation_evidence.tar.gz before extraction.
Archive SHA256 matches 48b3e78360e7c0c1721c21a3879bc975b902f5b3603fa25a0c92230c695c0810.
Listed members first; safely extracted to new results/raw/cub_sort_validation_20261009T220322089788Z/cloud_evidence. Preflight marker
hashes and four reported source hashes match the starting code. Historical Colab
report: Tesla T4, compute7.5, driver580.82.07, nvcc13.0.88, runtime/driver API13000,
CMake3.31.10, host GNU13.3.0, device0 checked kernel success. Actual preflight
configure/build/runtime return0; retained LastTest logs have23 CPU passes/0 failures
(OpenMP OFF) and1 CUDA-runtime pass/0 failures. The CUDA log's24/24 ordinal is a
filtered test index, not24 GPU tests. External full command transcript/exit statuses
for the cloud CPU build/CTest are not in the archive; LastTest.log and the CPU cache
support successful tests/Release configuration, not invented missing commands.
This proves historical readiness, not new CUB sorting or a currently connected GPU.
cloud_evidence_review.json records precisely that scope. Prior extracted cloud
evidence and original archive are unchanged.

Baseline fresh Release configure/build/CTest: exit0/0/0,25/25 groups,27.49s.
No baseline correctness defect found. CUDA_SORT_PROTOCOL_v1.md was saved/hash-frozen
before implementation. Separate cub_radix_sort_v1 adapter: signed-int32 full-width
CUB SortKeys, per-call device input/output/scratch and host output, checked API/
launch/sync/copy/cleanup, caller host mutation only after successful cleanup. Empty/
singleton require an available device then no-op; no CPU fallback. Length/byte
bounds checked; no abs/signed overflow. Existing Sorter shape reused in a separate
GPU registry; CPU six-entry registry/std_sort and all timing implementations stay
unchanged. No performance timing or CUB comparison metric implemented.

Dependency reference: NVIDIA CCCL v3.0.0, resolved commit
 e944297b0b51a8e9c0f1b30425370c31c1c0e0a0. Revision-qualified SortKeys/version/license
bytes verified against reviewed tag downloads. CUB is BSD-3-Clause, unchanged
aggregate LICENSE/attribution/provenance retained in third_party/cub. Toolkit
headers used without network fetching or upstream modification. Sorting opt-in
MAB_ENABLE_CUDA_SORT=OFF by default requires CUDA ON/toolkit>=13.0; readiness-only
CUDA path/minimum remains unchanged. CUB_VERSION300000 and two reviewed header
hashes are enforced. Actual installed cloud CUB identity is absent from the old
archive: a mismatch is an explicit dependency-review blocker, not a hidden bypass.
Cloud runner records transitive cub/thrust/cuda header hashes when configure passes.

GPU-only test source includes475 expected inputs/1900 output checks through public,
registry, interleaved/repeated calls, extrema/mixed signs/duplicates/sorted/random/
all generator distributions and lengths0..65537 including non-power-of-two and
boundary neighbors. These counts are **planned, not executed GPU results**. Default
CPU suites do not register GPU sorting. The cloud runner demands actual direct
sort-test success and a genuinely selected/passed CTest; skip77, empty selection,
malformed/incomplete output, failed subprocess, source changes or unavailable
preflight prevent COMPLETE. Exclusive paths, manifests/command diagnostics and
FAILED/INTERRUPTED markers preserve incomplete attempts. No resume/overwrite.

Local affected CUDA configure: exit1, CUDA compiler NOTFOUND (no nvcc); sorter
compilation and execution **not run**. Fresh local preflight exit2 remains
gpu_driver_unavailable. No driver/package/system changes and no live Colab endpoint
available to this agent. A versioned handoff guide and new source archive are
provided for user-run GPU validation, not represented as a tested cloud sorter.

Final reviewed fresh Release configure/build/CTest exit0/0/0:26/26 groups,
27.97s. Debug ASan/UBSan configure/build/CTest exit0/0/0:
26/26,82.91s, leaks enabled. No ptrace limitation or
detect_leaks=0 retry. Eleven new host tooling methods pass standalone and in both
final suites: schema/count validation, skip/empty CTest rejection, unavailable/
timeout/interruption diagnostics, output/symlink collisions, redaction, invalid
CLI and CUDA-SORT-with-CUDA-OFF rejection. These are host/synthetic record tests,
not mocked evidence of actual GPU sorting. Existing CPU sort/search/structure/
OpenMP tests remain passing; all22 preflight methods pass. Earlier intermediate
26/26 runs precede the final CTest-result-validator test and are retained separately.
CPU environment capture exit0. Captured CPU configure/build output has no compiler
warnings; new GPU compiler warnings cannot be reviewed before a CUDA build.

Exact argv/cwd/timestamps/exit/stdout/stderr: results/raw/cub_sort_validation_20261009T220322089788Z/COMMANDS.md,
commands_index.json and commands/*.json. Nonzero commands are the explained Git
metadata errors128, unavailable CUDA configure1 and readiness2; initial misplaced
archive lookup is recorded in initial_lookup_diagnostics.json. No failed check is
silently treated as successful. Local full suites:26 passed/0 failed/0 skipped each.
New GPU sorting test:0 executed,1 group unexecuted (not registered in CPU-OFF tests).
Historical cloud runtime smoke:1 passed; historical cloud CPU:23 passed.

Files added: include/algorithms/cuda_sorting.hpp, src/cuda/cub_sort.cu,
tests/test_cuda_sorting.cpp, scripts/validate_cuda_sort.py,
tests/test_cuda_sort_handoff.py, docs/CUDA_SORT_PROTOCOL_v1.md,
docs/CUDA_SORT_VALIDATION_GUIDE_v1.md, third_party/cub/README.md/LICENSE/UPSTREAM.json.
Modified: CMakeLists.txt, cmake/cuda.cmake, README.md and docs/ROADMAP.md/AUDIT.md/
ALGORITHMS.md/BENCHMARKING.md/EXPERIMENT_PROTOCOL.md. Existing CPU algorithms/tests,
vendors/licenses and old versioned protocols/studies/results stay unchanged.
Final manifests/change patch/integrity audit retained under results/raw/cub_sort_validation_20261009T220322089788Z.

Current phase: original roadmap Phase7 CUDA, requested post-cloud GPU continuation;
original Phase8 learned-index/AlphaDev remains pending. Runtime readiness validated
historically; first sorter source/build/tests/docs delivered but GPU compilation/
correctness **pending**. GPU timing/smoke/full study **not started**. No acceleration,
GPU benchmark measurements, significance or100M claim. The repository is ready
for cloud correctness handoff, not for the next research phase or timing study.

Exact next step: use the new cub_sort_source.tar.gz (source_bundle.json has its hash)
and docs/CUDA_SORT_VALIDATION_GUIDE_v1.md on an allocated supported cloud GPU.
After source verification, run:
```sh
python3 scripts/validate_cuda_sort.py --output results/raw/NEW_CUB_CORRECTNESS
```
Retain/persist COMPLETE or failed-attempt evidence and return the archive/hash for
review. Only observed build/475-case/1900-check success permits the separate GPU
timing contract/engine. If installed CUB mismatches the pin, retain actual hashes
and review that version explicitly before changing the frozen design.

New cloud source archive identity:
```json
{
  "archive": "results/raw/cub_sort_validation_20261009T220322089788Z/cub_sort_source.tar.gz",
  "sha256": "4907bd41d9443e457e01edb7fed5ba2bd0e035cdf2b2c5affb85795620bf8f8c",
  "bytes": 286683,
  "source_files": 137,
  "members": 138,
  "all_member_hashes_verified": true,
  "includes_historical_results": false
}
```
