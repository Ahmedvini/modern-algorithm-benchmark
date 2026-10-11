## Cloud GPU follow-up — Gate 1 blocked (user-requested Phase 8)

This follows the GPU milestone; it does not replace original roadmap Phase 8
learned-index/AlphaDev. Inspected AGENTS.md, roadmap/audit/README, cloud guide,
experiment protocol, CMake and Phase 7 final audit/source manifest/archive.
Workspace writable via anonymous temporary-file write; no Git metadata or Git
initialization. All 126 starting source hashes matched the Phase 7 manifest.
Before new evidence, all 8,656 raw/processed/figure files were hashed.

**Gate 1 did not pass.** No cloud GPU execution tool or remote runtime endpoint
is connected/provided. Available shell is local Linux. Colab/Kaggle/SSH markers
and gcloud/aws/jupyter were absent. SSH client presence is not remote access;
marker/tool absence alone cannot prove no remote GPU exists. No credentials,
SSH configuration or provider accounts were inspected. No cloud allocation,
remote execution, installation, driver/system change or paid provisioning was
attempted. inspection.json records access scope without secret values.

Archive verification exited 0: SHA256
f20581a4cb9b74ee8967485c259999f797fac0bbd44309ca1552aaaa2418c9f5,
127 members and 126 matching source files. Extracted into a new build-only path;
original archive unchanged. The archived preflight ran **locally**, exited 2,
classified gpu_driver_unavailable. Observed Linux 6.18.7-76061807-generic/x86_64,
CMake 3.28.3 and host GNU 13.3.0. PCI shows GA107M / GeForce RTX 3050 Ti Mobile
at 0000:01:00.0, with no bound driver/module/device nodes/version file, nvidia-smi,
nvcc, discoverable libcuda/libcudart or toolkit files. Runtime device count,
compute capability and driver/runtime/toolkit versions remain unknown. CMake
CUDA_STANDARD help success does not establish compiler support. CUDA configure,
build, enumeration/kernel checks were skipped, not passed. This is unavailable
readiness, not a CPU failure or diagnosis of broken hardware.

Archived CPU fallback configure/build/registry exited 0/0/0, CUDA/OpenMP/testing
OFF, all six original sorters listed. Testing OFF means no fallback CTest claim.
Fresh current Release configure/build/CTest and Debug ASan/UBSan configure/build/
CTest exited 0/0/0 each. Release **25/25** groups passed in 28.61s;
ASan/UBSan **25/25** in 83.81s. Leak detection remained enabled;
no ptrace limitation or detect_leaks=0 retry. All 22 readiness/build-isolation
methods passed per suite, including real default/explicit CUDA-OFF and mocked
states; mocks are not GPU evidence. Existing sorting/search/structure/OpenMP
checks passed unchanged. Captured configure/build output has no compiler warnings.
These are fresh invocations using existing CPU build directories; archive fallback
used a new build directory. CPU environment capture exited 0; its older 'GPU not
probed' field is distinct from the fresh preflight.

Twelve validation command records: archive verification 0; local preflight 2
(expected unavailable); fallback configure/build/registry 0/0/0; Release configure/
build/CTest 0/0/0; sanitizer configure/build/CTest 0/0/0; environment capture 0.
Exact argv/cwd/status/timestamps/stdout/stderr: commands/*.json, commands_index.json
and COMMANDS.md under results/raw/gpu_cloud_gate1_20261009T211734154323Z.
One editing-helper generation command exited 1 with a nested Python quoting
SyntaxError before executing/writing files; corrected with a literal heredoc.
editing_diagnostic.json records the failure. No failed validation command was
silently ignored. No CUDA-ON attempt, GPU correctness test or GPU timing trial ran.

Modified only README.md and docs/ROADMAP.md (blocked status/next action),
docs/ALGORITHMS.md (no CUB), docs/BENCHMARKING.md (no GPU schema/results),
docs/EXPERIMENT_PROTOCOL.md (environment gate), docs/AUDIT.md (this evidence).
No algorithms, CMake, scripts/tests, vendors/licenses or versioned protocols
changed. All 120 other original source files and all 8,656 earlier result
artifacts remain byte-identical, including frozen sorting/Phase 5/6 studies,
failed attempts and Phase 7 evidence/archive. Source manifests, changes.patch
and final_review.json retain integrity/review results. The old cloud guide and
readiness protocol remain unchanged. No new GPU sorting contract was created.

Completion statuses: cloud validation **blocked/not passed**; CUB implementation/
correctness **not started/not run**; GPU smoke **not run**; full GPU study **not
run**. Gates 2–4 are deferred per the user. Requested Phase 8 GPU task is incomplete.
BLOCKED.json records a gate outcome, never completed-study status. No acceleration
or100M execution claimed. Evidence: results/raw/gpu_cloud_gate1_20261009T211734154323Z/FINAL_AUDIT.md,
local_preflight/report.json, archive_verification.json, cpu_environment.json,
COMMANDS.md, final_review.json, prior_artifacts_sha256.json and source manifests.

Exact next action: allocate/connect an NVIDIA cloud development runtime, transfer
and verify the retained Phase 7 source archive, then follow
[CUDA_EXECUTION_GUIDE_v1.md](../../../docs/CUDA_EXECUTION_GUIDE_v1.md). From verified source run:
```sh
python3 scripts/cuda_preflight.py --output results/raw/NEW_CLOUD_PREFLIGHT
```
Require exit 0/operational, actual model/compute capability, driver/runtime/toolkit/
compiler metadata, enumeration and checked kernel. Retain exact cloud commands
and CPU fallback evidence outside ephemeral storage. Only then define Gate 2's
new GPU sorting contract, pin/license CUB, and implement signed-int32 differential
checks with separate synchronized transfer/device/end-to-end metrics. Cloud guide
execution remains unvalidated here because no cloud runtime was available.
