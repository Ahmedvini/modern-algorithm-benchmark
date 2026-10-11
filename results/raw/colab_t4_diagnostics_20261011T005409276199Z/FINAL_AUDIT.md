# Colab T4 setup and diagnostic validation

**Status: BLOCKED.** T4 session creation and non-benchmark environment diagnostics succeeded. The project source and comparison executable are absent in the inspected remote workspace. No build or study was authorized or launched.

## Session and method

Read AGENTS.md, the latest readiness audit/commands/integrity, and the historical cloud guide before setup. Installed CLI 0.7.4 syntax was confirmed using `colab new --help`, `colab exec --help` and `colab readme`. Initial `colab sessions` found no active session; `colab new --session cpu-gpu-validation --gpu T4` exited 0 and reported READY. Status and server inventory independently identify session `gpu-t4-s-kkb-usw4b0-21qggbdn9iask`, alias `cpu-gpu-validation`, T4 Standard GPU IDLE. Final status is retained in session_status_final.json. No authentication or account interaction was required; no credentials were read/requested or printed. CLI output capture redacts URLs and credential-shaped fields.

Only two read-only Python diagnostics were sent via `colab exec --file`. No project archive was uploaded, source extracted, package installed, driver modified, or runtime library loaded. CLI exit statuses, complete JSON markers and all nine inner command exit statuses were checked. Exact commands/logs are in [COMMANDS.md](COMMANDS.md), remote_diagnostic_run.json and runtime_files_run.json. The historical v1 guide's old implementation-status statements were not treated as current evidence.

## Fresh observations

Observed 2026-10-11T00:56:31.902174+00:00; these are snapshots, not future reservations.

| Item | Observed |
|---|---|
| OS / architecture | Linux 6.6.122+, x86_64, glibc 2.39 |
| GPU | Tesla T4, GPU-c51b969a-fbb1-a810-8346-93e2f6fc1849 |
| Driver | 580.82.07; /proc driver metadata and /dev/nvidiactl, /dev/nvidia0 present |
| GPU memory | 15,360 MiB total; 14,913 MiB free in explicit NVML query |
| nvcc | CUDA toolkit 13.0, compiler V13.0.88 |
| Runtime files | libcudart.so.13.0.96; runtime/driver header macros 13000 |
| CMake / G++ | 3.31.10 / Ubuntu GCC 13.3.0 |
| Python | 3.13.15 |
| Package metadata | NumPy 2.1.3; Matplotlib 3.10.0; pip 24.1.2 |
| CPU | 2 logical CPUs; affinity [0,1] |
| RAM | 13,605,822,464 bytes total; 12,546,945,024 bytes MemAvailable |
| /content disk | 75,467,313,152 bytes free; 120,942,624,768 bytes total |
| cgroup | cpu.max=max 100000; memory.max=max; memory.current=2,792,468,480 bytes |
| Load | 0.0791 / 0.1196 / 0.1074 |

No running compute process was listed at observation. GPU 37 C, P8, SM 300 MHz, memory 405 MHz, power limit 70 W; frequency, temperature, background activity and scheduling were not controlled. The whitelisted CUDA/OMP settings were unset. No setting was changed. RAM/disk availability exceeds the frozen 1 GiB observation thresholds; this does not validate allocations, actual two-worker OpenMP teams, resource limits at future execution or study readiness.

The nvidia-smi CUDA banner is driver compatibility metadata. Runtime library/header presence is not a successful CUDA runtime call or kernel execution. No compute capability query or CUDA execution probe ran. Package presence/version metadata is not compatibility testing; Python differs from earlier cloud records. No required dependency was repaired automatically.

## Source identity and blockers

Bounded inspection scope: /content, depth<=8, pruned Drive/results/private and dependency directories; no files outside scope assumed absent. No project root (CMakeLists.txt plus scripts/cpu_gpu_protocol.py) or cpu_gpu_comparison executable was found there. This does not prove absence at all remote paths. Remote frozen project-input hashes cannot be checked without those files. The source/executable are missing prerequisites; no existing build was declared ready.

Installed CUB version and DeviceRadixSort headers match the local reviewed CUB 3.0.1 / 300001 hashes exactly; see DIAGNOSTIC_ASSESSMENT.json. Toolkit path aliases are not separate independent installations. This verifies the two reviewed headers, not the full transitive CCCL tree or linked implementation. Local production adapter, CUB pin, freeze identity and three frozen members remain unchanged.

Explicitly unexecuted: all tests and CTest discovery, configure/build, actual OpenMP-team checks, CUDA runtime/kernel/correctness workloads, CUB workspace queries/allocations, benchmarks, warm-ups, measured trials, pilot/full study and 100M runs. Zero such executions were initiated. The session remains available as last observed; ephemeral-session lifetime is not guaranteed. No PREREQUISITES.json eligible for study launch was generated.

## Preservation and evidence

Direct before/after membership and SHA-256 comparison: all 11,668 pre-existing result files, 177 project files, 65 build-metadata files unchanged, no missing/modified/unexpected old-area files. Rechecked 26 protected anchors with the existing pinned CMake review exception, 80 production/header/dependency files, 144 reviewed source entries, and three frozen members. No differences. See BEFORE.json, PRESERVATION.json and FINAL_INTEGRITY.json. Every addition is confined to this uniquely named evidence directory. Historical evidence was not regenerated or overwritten.

An evidence-only formatting defect in VERIFIED_BEFORE.json (literal trailing backslash-n) is retained; VERIFIED_BEFORE_V2.json is the valid correction and has the same successful hash-check results. The correction command is preserved. Capture helper timestamps are collection timestamps despite the started_utc field name. Hash preservation is a local comparison, not external attestation or proof against arbitrary transient changes.

## Next permitted action

Stop here. Separately authorize transfer of the reviewed source and a fresh isolated build/validation on this T4, if desired. This task authorizes no build, test, CUDA workload or study execution. Source availability, executable identity and actual execution prerequisites must be established in that later scope; resource availability alone never authorizes the study.
