# Controlled CPU/GPU six-dataset pilot

Pilot accepted; full 1,200-measurement study was not run. Frozen cpu_gpu_comparison_v1: N=1,025 and 1,000,000; uniform/duplicate-heavy/fixed signed edges; seed 1729; five modes; W1/R5. Exactly 150 measured + 30 warm-up calls passed full std::sort oracle equality, with zero failed/interrupted/missing/duplicate records.

Tesla T4 CC 7.5, driver 580.82.07, runtime API 13000, CUDA/nvcc 13.0.88, GCC 13.3.0, CMake 3.31.10; CUB 3.0.1/CCCL f19d875da0d8bfb2e38c109b2b40522b8abbbbc3. C++17/CUDA17 Release -O3 -DNDEBUG, architecture 75; OpenMP 4.5/libgomp. Linux 6.6.122+, Xeon@2GHz, two logical CPUs on one physical SMT core. Requested OpenMP 2, actual 1 below 32768 and 2 above; OMP policy follows the freeze. cpu.max=max 100000; memory.max=max. Frequency/governor/thermal/background exclusivity not controlled. Snapshot load 1.741/1.631/0.936.

Primary measurements use steady_clock around unchanged host-vector APIs, including internal allocation/free and production GPU transfers/workspace/synchronization. Restoring input, generation, prior device drain, validation and I/O are excluded. Prepared H2D/device/D2H CUDA-event metrics and steady_clock prepared E2E exclude allocation/setup/staging/final vector copy and remain diagnostics. Prepared measurements never supply CPU ratio denominators.

## Primary host-vector API medians

All table values are microseconds, converted from retained ns by division by 1000. Each cell summarizes five measured calls on one input; one warm-up excluded. These are descriptive pilot observations, not rankings or significance.

| N | Distribution | std_sort | merge_sort | OpenMP 2 | Production CUB |
| --- | --- | ---: | ---: | ---: | ---: |
| 1025 | duplicate_heavy | 24.698 | 41.598 | 49.368 | 75.793 |
| 1025 | signed_edges | 14.907 | 15.172 | 22.263 | 67.166 |
| 1025 | uniform | 41.368 | 55.705 | 59.862 | 64.105 |
| 1000000 | duplicate_heavy | 31831.862 | 50374.917 | 46867.424 | 3154.675 |
| 1000000 | signed_edges | 20261.968 | 24478.621 | 32218.138 | 3107.064 |
| 1000000 | uniform | 78558.687 | 104438.312 | 74786.327 | 3338.940 |

## Prepared diagnostics medians

| N | Distribution | H2D us | Device sort us | D2H us | Prepared E2E us |
| --- | --- | ---: | ---: | ---: | ---: |
| 1025 | duplicate_heavy | 5.824 | 33.344 | 9.600 | 57.297 |
| 1025 | signed_edges | 6.176 | 28.320 | 5.312 | 48.090 |
| 1025 | uniform | 5.920 | 21.888 | 4.032 | 39.941 |
| 1000000 | duplicate_heavy | 342.720 | 381.600 | 314.336 | 1054.405 |
| 1000000 | signed_edges | 343.904 | 279.136 | 317.888 | 959.410 |
| 1000000 | uniform | 343.552 | 492.576 | 315.840 | 1168.889 |

## Variability and resources

[statistics.csv](statistics.csv) and [summary.json](summary.json) retain per-input median, mean, sample SD (ddof1), min/max, counts and identities in ns, plus equal-weight distinct-input summaries and permitted paired ratios. All outliers remain. There is only one seed/input per pilot workload, so cross-dataset SD is unavailable; repeated timings are not independent datasets. No CI/significance claim.

At N=1025 both workspace queries/diagnostic requests are 1 byte. At N=1M both are 4,178,687 bytes. Combined device payload calculations are 16,402 and 24,357,374 bytes, respectively; known host payload calculations 24,600 and 24,000,000 bytes. These are payload formulas from queried sizes, not measured physical GPU allocation. Production allocations are not instrumented. RSS includes process/context/runtime, all modes and allocator history; values are explicitly process-lifetime, not structure/algorithm/GPU memory. See [resources_observed.csv](resources_observed.csv). Frozen planning files are unchanged.

Pilot runner wall time 7.360 s; all fresh prerequisites/validation/analysis took 541.073 s. An 8x dataset-count-only main-study proxy is about 59 s plus fresh prerequisites, not a measured prediction: unseen distributions/N=65537, cold state and cloud variance require a reviewed allowance and fresh workspace check. No planning cap is raised here.

## Validation and reproducibility

Fresh local CPU Release 29/29 and ASan/UBSan 29/29; cloud CPU Release 29/29, ASan/UBSan 29/29 and GPU-enabled Release 32/32 pass. Leak detection enabled. New framework 22 methods pass; engine 60 inputs/3600 checks. Actual CUDA correctness 475 inputs/1900 checks passed directly and in CTest. Host-only CUDA analysis deliberately skips two GPU methods; separate GPU framework 14/14 methods pass. CUDA build produced 341 nvcc-generated GCC line-directive extension warnings; no other category, no suppression or CUB pin change. CPU builds have zero warnings. CPU sanitizers do not cover device code; Compute Sanitizer was not run.

The first remote attempt failed on missing build/ parent and was fixed with a regression; an expired subsequent session has unverified final outcome and is excluded. Final v3 reran every prerequisite and has complete downloaded evidence. CLI exit0 alone was not accepted for Python exceptions.

Raw source/checksum/command/build/environment/query/trial evidence: [validation audit](../../raw/cpu_gpu_pilot_20261010T001232473460Z/FINAL_AUDIT.md), [raw pilot](../../raw/cpu_gpu_pilot_20261010T001232473460Z/remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/), [independent verification](../../raw/cpu_gpu_pilot_20261010T001232473460Z/INDEPENDENT_VERIFICATION.json). The archive SHA256 and all 174 members were verified; all 118 raw-manifest files remain unchanged.

Cloud summaries and two independently regenerated local summaries are byte-identical, SHA256 07e69e2e0c8853f93d3f3da895337b5e4b72e5e2dd0ff0577db3cbd1f7053a22. Independent retained-row calculations verified 48 metric groups and 18 host-call ratios.

Regenerate to a new filename:

```sh
python3 scripts/analyze_cpu_gpu.py results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3 --output results/processed/NEW_PILOT_SUMMARY.json
```

Next: review pilot quality/resource observations and authorize a separate full frozen comparison study if acceptable. Query N=65537 in its fresh environment, retain all confounders and distinguish primary/diagnostic scopes. No full study, 100M run, performance superiority or phase-wide research completion is claimed.
