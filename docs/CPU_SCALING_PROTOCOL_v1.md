# CPU scale extension v1

This is a separate experiment, not a revision of any frozen CPU/GPU study.
Use the unchanged Release sort_benchmark and run_matrix.py. First validate the
current source with guarded Release and ASan/UBSan correctness selections.

Stage A: N=10000000; uniform, sorted, reverse_sorted, duplicate_heavy and nearly_sorted;
seeds1729/42/2718; all six sequential sorters; one warm-up and five measured
repetitions. Expected15 datasets,90 algorithm/configurations,450 measured trials
and90 warm-ups. Run configurations sequentially. No comparison instrumentation.

Stage B, only after A is complete and correct: N=100000000, same five distributions,
seed1729, all six sequential sorters, one warm-up and five measured repetitions.
Expected5 datasets,30 algorithm/configurations,150 measured trials and30 warm-ups.
One seed means no cross-dataset uncertainty estimate in each workload group.
These are scale-feasibility observations, not a representative universal ranking.

Input generation, restoration, oracle construction, full-result verification and
CSV serialization remain outside sort timing. Measure steady_clock nanoseconds,
preserve every observation, use the existing seed-offset cyclic sorter order,
and retain failed/incomplete configurations. Use the existing strict analyzer.
Record environment, actual build/compiler/link commands, executable/source hashes,
dataset fingerprints and command return codes. RSS collected for an entire child
process is a lifetime peak including input, oracle, working copy, temporary buffers,
runtime and allocator; it does not isolate any one algorithm in a combined child.

The existing engine budget is16N bytes for four int32 array allowances, including
auxiliary workspace. Stage A requires160000000 bytes and uses a512MiB policy cap.
Stage B requires1600000000 bytes and uses a2048MiB policy cap. These are calculated
payload estimates, not measured physical allocations. One100M int32 vector is
400000000 bytes. Before each stage require MemAvailable at least3GiB above the
calculated payload, and disk free at least2GiB. Check cgroup headroom if limited.
Stop on any resource/correctness failure rather than changing sizes or algorithms.
Do not rely on swap to justify insufficient RAM. Background load, frequency,
temperature and cache state are observed/confounded, not controlled. Run no other
project benchmark or compilation concurrently with these timed studies.

Analyze repeated trials within each dataset; retain mean, median, sample SD and
min/max. Stage A cross-seed summaries equally weight dataset medians. Stage B
reports within-dataset variability only. No outlier removal, significance test,
or GPU comparison is part of this protocol. A process interruption leaves the
stage incomplete; never silently merge incompatible attempts.
