# Phase 5 full-study launch review v1

The unchanged full preset of ORCHESTRATION_PROTOCOL_v1.md is frozen and recorded
in full_launch_plan.json before execution. 180 configurations: six sorters,
three array searches and all five ordered-index configurations; N=1K/10K/100K/1M,
five distributions, seeds1729/42/2718, query seed2718,structure seed1729,Q1000,W1/R5,
cardinality16,default swaps,Release/sanitizersOFF,1024MiB planning allowance.
Measured upper bound24900, warmup upper4980. Actual query availability remains
explicit; no omitted/unavailable policy becomes an invented measurement.

Prerequisites: final 22/22 Release+ASan/UBSan,21 new Python tests,36-configuration
smoke with complete raw/derived-byte regeneration and 867-artifact integrity,
100K custom calibration correct, runtime/resource assessment gates passed.
Calibration forecast2745.6575762072134seconds (factor4), below3600seconds family
budget; this is a forecast, not a measured full duration. Plotting cost is separate.
The shared machine's frequency/cache/thermal/background conditions remain
uncontrolled. New exclusive phase5_full ID; prior studies and pilot outputs hashed
before launch. No parameter reduction, CUDA,100M or instrumentation is authorized.
