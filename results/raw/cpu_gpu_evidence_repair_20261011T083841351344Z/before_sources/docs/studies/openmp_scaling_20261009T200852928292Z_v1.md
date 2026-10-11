# OpenMP scaling study v1 — frozen launch

Saved before execution; no previous protocol or result changes. This extends
OPENMP_PROTOCOL_v1.md (parallel_sort_timing_v1) with the unchanged full preset.

180 configurations: N32768/100000/1000000, uniform/sorted/reverse_sorted/
duplicate_heavy/nearly_sorted, seeds1729/42/2718, threads1/2/4/8. Two sorters:
sequential merge_sort and parallel_merge_sort. W1/R5, cardinality16, swaps=floor(N/100),
256MiB array planning budget. Expected1800 measured and360 warmup rows.
OMP_DYNAMIC=FALSE,OMP_THREAD_LIMIT=8,OMP_MAX_ACTIVE_LEVELS=1,OMP_WAIT_POLICY=PASSIVE.
Actual team must equal request above threshold; team size is not a busy-worker count.

Shared timing engine; identical restored inputs; generation/copying/full reference
validation excluded. Allocation/team creation/task execution/joins/deallocation
included. No counting/RSS. Primary ratio uses same-cell sequential median; separate
parallel-request1 ratio. Per-dataset medians and ratios precede equal-weight distinct
input aggregation. Keep all outliers and sample SD/min/max; no significance claim.
Fixed size/seed/distribution/thread order and cyclic algorithm order, odd R imbalance,
serial parent merges, warmed copies and uncontrolled shared-machine frequency/cache/
thermal/background state remain confounders. No affinity/governor change; thermal
state unmeasured. ThreadSanitizer startup fails in this environment, including a
non-OpenMP probe; ordinary stress/ASan/UBSan are not a race-freedom proof.

Prelaunch gates: final reviewed Release24/24 and ASan/UBSan24/24, leak detection
on; Python12/12; smoke32 configurations,320 measured/64 warmup successes, zero
failed/missing trials; exact derived regeneration; prior3796 artifact hashes match.
Smoke overhead-inclusive child wall forecast, scaled by Nlog2(N+2) and fourfold
allowance, is 184.14736184079177 seconds, below1800s budget;
plotting separate. This is a forecast, not measured full duration. Resource estimates
and actual available resources below are planning values, not measured algorithm RSS.

Exact command:
```sh
python3 scripts/run_parallel_matrix.py --preset full --output results/raw/openmp_scaling_20261009T200852928292Z --processed results/processed/openmp_scaling_20261009T200852928292Z --figures results/figures/openmp_scaling_20261009T200852928292Z
```

Configuration/source identity and resource evidence:
```json
{
  "binary_sha256": "b5a990e58a51e453976980a0c6701dd21d1fae8447db922a48d9416199176a9d",
  "configuration_sha256": "bfd68b6f9e1dcac7338c0464d79803f71954c6b7188e486cf2534affca3b97d7",
  "frozen_utc": "2026-10-09T20:32:16.777201+00:00",
  "implementation_protocol_sha256": "83a7bdf942e941fe69a6b6e0cf1795edaeb96e82e7c80975a67a587b2477e7ac",
  "resources": {
    "disk_bytes_allowance": 419889152,
    "required_available_memory_bytes": 536870912,
    "required_free_disk_bytes": 839778304,
    "workspace_bytes_estimate": 150217728
  },
  "snapshot": {
    "affinity": [
      0,
      1,
      2,
      3,
      4,
      5,
      6,
      7,
      8,
      9,
      10,
      11
    ],
    "available_memory_bytes": 6587469824,
    "cgroups": [
      {
        "headroom_bytes": null,
        "memory_current": 1872969728,
        "memory_max": "max",
        "path": "/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/app.slice/cosmic-files-applet.scope"
      },
      {
        "headroom_bytes": null,
        "memory_current": 8327446528,
        "memory_max": "max",
        "path": "/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/app.slice"
      },
      {
        "headroom_bytes": null,
        "memory_current": 8383234048,
        "memory_max": "max",
        "path": "/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service"
      },
      {
        "headroom_bytes": null,
        "memory_current": 8739078144,
        "memory_max": "max",
        "path": "/sys/fs/cgroup/user.slice/user-1000.slice"
      },
      {
        "headroom_bytes": null,
        "memory_current": 8762683392,
        "memory_max": "max",
        "path": "/sys/fs/cgroup/user.slice"
      }
    ],
    "controls": "No affinity/frequency/cache/thermal/background changes; shared machine.",
    "disk_free_bytes": 134517039104,
    "frequency_policy": {
      "/sys/devices/system/cpu/cpufreq/policy0/scaling_governor": "performance",
      "/sys/devices/system/cpu/cpufreq/policy1/scaling_governor": "performance",
      "/sys/devices/system/cpu/cpufreq/policy10/scaling_governor": "performance",
      "/sys/devices/system/cpu/cpufreq/policy11/scaling_governor": "performance",
      "/sys/devices/system/cpu/cpufreq/policy2/scaling_governor": "performance",
      "/sys/devices/system/cpu/cpufreq/policy3/scaling_governor": "performance",
      "/sys/devices/system/cpu/cpufreq/policy4/scaling_governor": "performance",
      "/sys/devices/system/cpu/cpufreq/policy5/scaling_governor": "performance",
      "/sys/devices/system/cpu/cpufreq/policy6/scaling_governor": "performance",
      "/sys/devices/system/cpu/cpufreq/policy7/scaling_governor": "performance",
      "/sys/devices/system/cpu/cpufreq/policy8/scaling_governor": "performance",
      "/sys/devices/system/cpu/cpufreq/policy9/scaling_governor": "performance"
    },
    "load_average": [
      1.6728515625,
      1.61572265625,
      1.5625
    ],
    "logical_cpu_count": 12,
    "platform": "linux",
    "resource_limits": {
      "AS": [
        -1,
        -1
      ],
      "CPU": [
        -1,
        -1
      ],
      "DATA": [
        -1,
        -1
      ],
      "FSIZE": [
        -1,
        -1
      ],
      "STACK": [
        8388608,
        -1
      ]
    },
    "total_memory_bytes": 16475164672
  }
}
```

Results are complete only if every configuration/trial/actual-team/correctness
check passes and summaries/plots/report regenerate from immutable raw data.
Failures/interruption are retained, never completion; no retries in-place.
No CUDA, learned index, AlphaDev or100M work. Maximum study size1M.
