## Phase 7 — CUDA readiness and reproducible cloud guide

This completes the **requested preflight/guide milestone**, not the original
roadmap's CUDA sorting/timing experiment. No CUDA sorting/searching algorithm,
acceleration result, GPU performance measurement or100M experiment was added/run.
Workspace writable via anonymous temporary-file check; Git status128/no metadata,
no Git initialization. Read AGENTS.md, current roadmap/audit/README/CMake/timing
architecture, Phase6 protocol/report/final audit/integrity records before edits.
Phase6 reviewed source120/120 hashes matched starting state. Initial source120
files and8,447 raw/processed/figure artifacts were hashed/backed up before editing.
`results/raw/cuda_preflight_validation_20261009T205410772326Z/source_before.json`, prior_artifacts_sha256.json, inspection.json
and `build/cuda_review_20261009T205410772326Z` retain this baseline. Baseline Release configure/build/CTest
exited0 with24/24 groups passed30.14s. No prior correctness defect was observed.

Contract docs/CUDA_PREFLIGHT_PROTOCOL_v1.md was frozen before implementation,
with copy PROTOCOL_v1.md/hash protocol.json retained. scripts/cuda_preflight.py
uses standard-library discovery, Linux NVIDIA display/compute PCI and kernel-driver
binding/module/device/version evidence, lspci and nvidia-smi management queries,
resolved nvcc/toolkit/header/library paths, OS/kernel/architecture/CPU/Python,
CMake version/CUDA_STANDARD availability, relevant allowlisted environment paths
and source hashes. No full environment/PATH/cache dump. Secret-named environment
values, URL credentials and sensitive query values are redacted from retained
strings/path keys. Selected CMake cache fields only; scratch builds are deleted.
Commands have timeout/default60s and explicit return code/stdout/stderr/status.
Missing tools/files and skipped steps are explicit, not successful probes.

Only when a candidate NVIDIA nvcc answers and CMake>=3.18 exists does preflight
configure the actual project with CUDA ON, OpenMP/sanitizers/testing OFF, Release
and explicit compiler, build cuda_runtime_probe, and attempt enumeration/device0
kernel/copyback validation. Driver/toolkit/device capabilities are separate, not
inferred from nvcc version. Seven states include the five required scenarios plus
toolchain_unverified/detection_unavailable. Operational requires strict runtime
JSON+successful configure/build/checked kernel. COMPLETE.json means discovery
finished, not CUDA working. Exit0 operational, exit2 unavailable/unverified report,
exit1 reporting/IO/internal error,130 interrupted (incomplete marker); argparse
usage errors exit2 without discovery completion. Atomic directory ownership rejects
existing output before any probe and preserves previous/concurrent-run evidence.

CMake MAB_ENABLE_CUDA defaults OFF; no CUDA discovery/language/toolkit dependency
in the CPU path. New cmake/cuda.cmake requires CMake>=3.18 and NVIDIA toolkit>=11.0
with C++17/compatible host compiler on explicit opt-in. Existing CPU CMake3.16/
C++17 minimum, algorithms/default/registries/timing and OpenMP policy unchanged.
New src/cuda/runtime_probe.cu links only CUDA::cudart, independently of CPU
sanitizer flags; combining CUDA and CPU sanitizers explicitly rejects. Enumerate
visible device properties/API versions; test only device0 with one-int write1729,
launch/synchronization/copy-back/reference/free checks. No timing or sorting.
Probe exit77 on enumeration unavailable/no device maps to optional CTest skip;
post-enumeration failure exits1/CTest fail. This source is **not compiled or run
locally** because no toolkit is available; no CUDA test pass/skip is claimed for
CPU-OFF builds, where that test is not registered.

Files added: scripts/cuda_preflight.py, tests/test_cuda_preflight.py,
cmake/cuda.cmake, src/cuda/runtime_probe.cu, docs/CUDA_PREFLIGHT_PROTOCOL_v1.md,
docs/CUDA_EXECUTION_GUIDE_v1.md. Modified: CMakeLists.txt, README.md,
docs/ROADMAP.md, docs/AUDIT.md. Existing algorithms, interfaces, dataset generation,
benchmark/Python implementation/tests, third-party licenses/sources and historical
protocols/results remain unchanged. Detailed inventory/review patch/source manifest
are retained in file_changes.json/changes.patch/source_after.json.

Final commands below all exited0, with exact argv/stdout/stderr/times/status
retained in commands/reviewed_*.json and COMMANDS.md:
```sh
python3 tests/test_cuda_preflight.py
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=OFF
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```
Final reviewed Release25/25 passed27.09s, ASan/UBSan25/25 passed78.64s.
All22 preflight/build-isolation methods passed standalone and in both final suites;
13 OpenMP framework and23 existing orchestration Python methods still pass.
Existing sorting/search/structure/OpenMP differential/invariant tests remain
registered/passing. No fresh configure/build/test failures or compiler warnings.
Leak detection enabled; ptrace limitation did not recur, no detect_leaks=0 retry.
The first25/25 Release/sanitizer runs also passed before final privacy/path-driver
review; they are intermediate evidence, not substituted for final reviewed suites.

Tests cover five readiness scenarios, extra unknown/toolchain states, nvcc version
not implying kernel readiness, failed kernels, management CSV escaping, malformed
runtime JSON, missing commands/files, subprocess exit/timeout diagnostics, disabled
compiler gating, mocked build pipeline failure boundaries, redaction/path-key
redaction/numeric JSON preservation, consecutive-run isolation, output collision,
interrupted/report-error markers and invalid CLI timeout. A real CMake option test
configures both default/explicit CUDA OFF with deliberately unavailable CUDACXX/
CUDAToolkit_ROOT, verifying no CUDA compiler cache/check. No mocked fixture is
represented as actual GPU capability. Additional CPU fallback commands (all0):
```sh
cmake -S . -B build/cuda_cpu_fallback -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=OFF -DBUILD_TESTING=OFF
cmake --build build/cuda_cpu_fallback --target sort_benchmark --parallel 2
build/cuda_cpu_fallback/sort_benchmark --list-sorts
```
The original6 sorter names were returned. This fallback has testing OFF; no full
fallback CTest pass is claimed. Full fresh suites above keep existing OpenMP ON.
CPU environment capture exited0:
```sh
python3 scripts/capture_environment.py --build-dir build/release --output results/raw/cuda_preflight_validation_20261009T205410772326Z/cpu_environment.json
```
The unchanged older CPU tool says GPU not probed; GPU evidence is the new report.

Actual local preflight (exit2, expected unavailable readiness):
```sh
python3 scripts/cuda_preflight.py --output results/raw/cuda_preflight_20261009T205410772326Z_reviewed
```
Earlier discovery at `results/raw/cuda_preflight_20261009T205410772326Z` also exited2, retained unchanged; final
report includes additional human model/driver-path/redaction review. report.json,
SUMMARY.txt, COMPLETE.json and source hashes are retained in each exclusive path.
Observed Linux6.18.7-76061807-generic/x86_64, CMake3.28.3. PCI0000:01:00.0,
NVIDIA10de:25a0/class030000; lspci exit0 identifies GA107M [GeForce RTX3050Ti Mobile].
No bound kernel driver, visible nvidia module, /dev/nvidia0 or /dev/nvidiactl;
/proc/driver/nvidia/version missing. nvidia-smi and nvcc missing (returncode=null,
status unavailable), no discovered CUDA driver/runtime libraries or toolkit files.
Driver/runtime/toolkit versions unknown, not invented. CMake version and
CUDA_STANDARD-help commands exit0, documenting language feature availability,
**not** an available CUDA compiler. Configure/build/runtime are explicitly skipped;
CUDA ON configuration was never attempted. Classification gpu_driver_unavailable
means CUDA driver unavailable/unverified from current evidence, not a diagnosis
that hardware is broken. No software installation or system/permission change.

The guide covers allocated GPU verification, source URL/revision supplied by user
(no invented remote), alternatively audited source archive+hash verification,
cloud-only dependency setup, CPU fallback, isolated CUDA smoke/CTest semantics,
metadata/visibility, troubleshooting and persistent Drive/cloud export. It uses
current project options. Colab/cloud execution, remote clone, dependency installs,
Drive mounting/upload and CUDA-enabled commands have **not run locally or in Colab**.
A source-only archive and126-file manifest are retained as phase7_source.tar.gz/
source_after.json, archive hash in source_bundle.json and final audit appendix;
local extraction/integrity/relocated CUDA-OFF configure are checked separately.
No earlier experiment results are included in the source archive or overwritten.

Primary documentation consulted for compatibility/guide facts: CMake3.28
CheckLanguage, FindCUDAToolkit and CUDA_STANDARD; NVIDIA CUDA11 NVCC C++17,
CUDA runtime device/version APIs and driver/toolkit compatibility; official Colab
FAQ. Links are in the guide. These are documentation checks, not cloud experiments.

Integrity: all8,447 starting result files remain unchanged, including Phase6 smoke,
failed attempt/full retry, reports/figures/validation snapshots, earlier1M sorting
and Phase5 studies. All original frozen protocols remain byte-identical. All116
unmodified starting project files are protected; only the4 listed originals change.
Final reviewed source126 files, new readiness protocol and retained initial local
preflight are hash-verified. final_review.json and FINAL_AUDIT.md support completion,
commands_index.json/COMMANDS.md retain exact command statuses, reviewed_source
contains the saved source snapshot and changes.patch makes edits reviewable without
Git. Archive relocation evidence is source_bundle_validation.json.

Requested Phase7 preflight/guide milestone complete with **unavailable local CUDA**.
Limitations: GPU CMake branch and .cu compilation/execution are unverified; no CUDA
compiler/runtime version/device execution, sorting or performance evidence. GPU
readiness mocks are not hardware tests. Linux discovery is primary; other platforms
are best-effort/unvalidated. The tiny kernel checks device0 only, not all devices.
No privileged install/driver change, inferred acceleration or100M attempt.
Original Phase7 GPU sorter/timing objectives remain pending. Exact next GPU step:
allocate a supported cloud GPU, verify the source archive, run this guide/preflight
and isolated runtime smoke, then separately pin/license CUB and implement signed
sorting/differential checks plus synchronized H2D/algorithm/D2H/end-to-end metrics
under a new frozen protocol. Phase8/9/10 and deferred CPU research remain listed.

Source archive identity (local extraction/manifest/relocation check passed):
```json
{
  "archive": "results/raw/cuda_preflight_validation_20261009T205410772326Z/phase7_source.tar.gz",
  "archive_members": 127,
  "byte_identical_repack": true,
  "bytes": 253980,
  "extracted_source_hashes_match": true,
  "relocated_cuda_off_configure_exit": 0,
  "sha256": "f20581a4cb9b74ee8967485c259999f797fac0bbd44309ca1552aaaa2418c9f5",
  "source_files": 126
}
```
