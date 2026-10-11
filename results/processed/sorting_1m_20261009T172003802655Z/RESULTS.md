# 1M sorting study: descriptive results

Study: `sorting_1m_20261009T172003802655Z`.

15 configurations completed: 450 measured trials and 90 warm-ups, all passed; no failed or missing trials. Six sorters, N=1,000,000, five distributions, seeds 1729/42/2718.

## Cross-seed results

Each row describes three dataset medians (five trials per seed). All rows have 15 successful trials, zero failed trials and three datasets. The standard deviation below is sample SD across three seed medians; min/max are the smallest/largest seed median, not the extremes of all 15 trials. Milliseconds = nanoseconds / 1,000,000; tables round to three decimals, JSON/CSV retain precision. No outliers removed and no significance test performed.

| Algorithm | Distribution | Median of medians (ms) | Mean of medians (ms) | Sample SD (ms) | Min median (ms) | Max median (ms) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| std_sort | uniform | 57.699 | 58.703 | 2.587 | 56.768 | 61.642 |
| std_sort | sorted | 8.740 | 8.716 | 0.064 | 8.643 | 8.763 |
| std_sort | reverse_sorted | 5.978 | 6.067 | 0.277 | 5.844 | 6.377 |
| std_sort | duplicate_heavy | 20.182 | 20.366 | 1.427 | 19.039 | 21.876 |
| std_sort | nearly_sorted | 10.407 | 10.542 | 0.357 | 10.272 | 10.946 |
| quick_sort | uniform | 83.771 | 86.526 | 5.076 | 83.424 | 92.384 |
| quick_sort | sorted | 74.459 | 75.527 | 1.869 | 74.436 | 77.685 |
| quick_sort | reverse_sorted | 72.090 | 72.520 | 3.892 | 68.861 | 76.610 |
| quick_sort | duplicate_heavy | 14.574 | 14.664 | 0.463 | 14.253 | 15.165 |
| quick_sort | nearly_sorted | 31.783 | 32.222 | 0.909 | 31.615 | 33.267 |
| pdq_sort | uniform | 24.457 | 25.080 | 1.477 | 24.016 | 26.767 |
| pdq_sort | sorted | 0.764 | 0.751 | 0.029 | 0.718 | 0.771 |
| pdq_sort | reverse_sorted | 1.558 | 1.523 | 0.084 | 1.427 | 1.584 |
| pdq_sort | duplicate_heavy | 4.248 | 4.383 | 0.267 | 4.211 | 4.691 |
| pdq_sort | nearly_sorted | 8.627 | 8.612 | 0.203 | 8.402 | 8.806 |
| tim_sort | uniform | 82.326 | 82.662 | 1.593 | 81.263 | 84.396 |
| tim_sort | sorted | 0.396 | 0.402 | 0.012 | 0.395 | 0.416 |
| tim_sort | reverse_sorted | 2.057 | 2.021 | 0.236 | 1.769 | 2.237 |
| tim_sort | duplicate_heavy | 40.939 | 40.833 | 1.598 | 39.185 | 42.375 |
| tim_sort | nearly_sorted | 7.693 | 7.773 | 0.269 | 7.554 | 8.073 |
| merge_sort | uniform | 75.129 | 77.611 | 4.958 | 74.384 | 83.319 |
| merge_sort | sorted | 10.942 | 10.773 | 0.316 | 10.408 | 10.969 |
| merge_sort | reverse_sorted | 10.903 | 10.442 | 1.088 | 9.199 | 11.224 |
| merge_sort | duplicate_heavy | 36.602 | 37.704 | 5.070 | 33.276 | 43.235 |
| merge_sort | nearly_sorted | 15.330 | 15.183 | 1.546 | 13.569 | 16.649 |
| radix_sort | uniform | 7.268 | 7.475 | 0.481 | 7.132 | 8.025 |
| radix_sort | sorted | 8.311 | 8.125 | 0.551 | 7.505 | 8.559 |
| radix_sort | reverse_sorted | 7.721 | 8.078 | 1.019 | 7.286 | 9.228 |
| radix_sort | duplicate_heavy | 13.286 | 13.135 | 0.373 | 12.710 | 13.410 |
| radix_sort | nearly_sorted | 8.388 | 8.195 | 0.696 | 7.423 | 8.775 |

## Results by dataset seed

All 90 rows below describe five repeated timings of one dataset, with successful/failed counts explicit. SD is sample SD across repetitions, and min/max retain every successful observation.

| Algorithm | Distribution | Seed | Successful | Failed | Median (ms) | Mean (ms) | Sample SD (ms) | Min (ms) | Max (ms) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| std_sort | uniform | 1729 | 5 | 0 | 56.768 | 58.215 | 2.367 | 56.545 | 61.981 |
| quick_sort | uniform | 1729 | 5 | 0 | 83.424 | 83.546 | 0.963 | 82.706 | 85.030 |
| pdq_sort | uniform | 1729 | 5 | 0 | 24.016 | 24.099 | 0.237 | 23.798 | 24.355 |
| tim_sort | uniform | 1729 | 5 | 0 | 82.326 | 82.952 | 2.967 | 78.920 | 86.487 |
| merge_sort | uniform | 1729 | 5 | 0 | 75.129 | 77.201 | 3.887 | 74.669 | 83.867 |
| radix_sort | uniform | 1729 | 5 | 0 | 7.132 | 7.343 | 0.721 | 6.864 | 8.613 |
| std_sort | sorted | 1729 | 5 | 0 | 8.643 | 8.596 | 0.431 | 7.994 | 9.094 |
| quick_sort | sorted | 1729 | 5 | 0 | 74.459 | 73.819 | 1.876 | 71.343 | 76.132 |
| pdq_sort | sorted | 1729 | 5 | 0 | 0.718 | 0.716 | 0.029 | 0.678 | 0.757 |
| tim_sort | sorted | 1729 | 5 | 0 | 0.396 | 0.401 | 0.029 | 0.365 | 0.439 |
| merge_sort | sorted | 1729 | 5 | 0 | 10.408 | 10.411 | 0.704 | 9.617 | 11.207 |
| radix_sort | sorted | 1729 | 5 | 0 | 7.505 | 7.572 | 0.479 | 7.045 | 8.077 |
| std_sort | reverse_sorted | 1729 | 5 | 0 | 5.978 | 6.029 | 0.150 | 5.887 | 6.278 |
| quick_sort | reverse_sorted | 1729 | 5 | 0 | 72.090 | 73.309 | 3.440 | 70.594 | 78.922 |
| pdq_sort | reverse_sorted | 1729 | 5 | 0 | 1.558 | 1.587 | 0.160 | 1.391 | 1.810 |
| tim_sort | reverse_sorted | 1729 | 5 | 0 | 2.237 | 2.268 | 0.451 | 1.892 | 3.004 |
| merge_sort | reverse_sorted | 1729 | 5 | 0 | 10.903 | 11.085 | 0.971 | 10.384 | 12.750 |
| radix_sort | reverse_sorted | 1729 | 5 | 0 | 7.721 | 7.697 | 0.240 | 7.400 | 8.016 |
| std_sort | duplicate_heavy | 1729 | 5 | 0 | 19.039 | 19.759 | 1.236 | 18.831 | 21.642 |
| quick_sort | duplicate_heavy | 1729 | 5 | 0 | 14.574 | 14.915 | 0.770 | 14.082 | 15.881 |
| pdq_sort | duplicate_heavy | 1729 | 5 | 0 | 4.691 | 4.798 | 0.282 | 4.574 | 5.279 |
| tim_sort | duplicate_heavy | 1729 | 5 | 0 | 39.185 | 39.175 | 0.678 | 38.127 | 39.883 |
| merge_sort | duplicate_heavy | 1729 | 5 | 0 | 33.276 | 33.469 | 0.777 | 32.631 | 34.685 |
| radix_sort | duplicate_heavy | 1729 | 5 | 0 | 12.710 | 13.063 | 1.044 | 12.219 | 14.821 |
| std_sort | nearly_sorted | 1729 | 5 | 0 | 10.272 | 10.756 | 1.370 | 9.828 | 13.141 |
| quick_sort | nearly_sorted | 1729 | 5 | 0 | 31.615 | 32.529 | 1.932 | 31.308 | 35.939 |
| pdq_sort | nearly_sorted | 1729 | 5 | 0 | 8.402 | 8.436 | 0.361 | 8.079 | 9.008 |
| tim_sort | nearly_sorted | 1729 | 5 | 0 | 7.554 | 7.466 | 0.248 | 7.195 | 7.743 |
| merge_sort | nearly_sorted | 1729 | 5 | 0 | 13.569 | 14.010 | 0.857 | 13.444 | 15.476 |
| radix_sort | nearly_sorted | 1729 | 5 | 0 | 7.423 | 7.656 | 0.558 | 7.154 | 8.329 |
| std_sort | uniform | 42 | 5 | 0 | 61.642 | 60.587 | 3.198 | 55.450 | 63.902 |
| quick_sort | uniform | 42 | 5 | 0 | 92.384 | 92.884 | 9.306 | 80.364 | 106.599 |
| pdq_sort | uniform | 42 | 5 | 0 | 26.767 | 28.100 | 6.060 | 23.037 | 38.585 |
| tim_sort | uniform | 42 | 5 | 0 | 84.396 | 83.893 | 5.521 | 77.894 | 89.589 |
| merge_sort | uniform | 42 | 5 | 0 | 83.319 | 84.657 | 4.357 | 80.879 | 91.878 |
| radix_sort | uniform | 42 | 5 | 0 | 8.025 | 7.985 | 0.391 | 7.357 | 8.401 |
| std_sort | sorted | 42 | 5 | 0 | 8.763 | 8.752 | 0.384 | 8.262 | 9.232 |
| quick_sort | sorted | 42 | 5 | 0 | 74.436 | 74.411 | 0.745 | 73.491 | 75.182 |
| pdq_sort | sorted | 42 | 5 | 0 | 0.764 | 0.808 | 0.086 | 0.732 | 0.944 |
| tim_sort | sorted | 42 | 5 | 0 | 0.395 | 0.394 | 0.004 | 0.389 | 0.399 |
| merge_sort | sorted | 42 | 5 | 0 | 10.969 | 11.004 | 0.505 | 10.453 | 11.776 |
| radix_sort | sorted | 42 | 5 | 0 | 8.311 | 8.374 | 0.387 | 7.839 | 8.839 |
| std_sort | reverse_sorted | 42 | 5 | 0 | 6.377 | 6.886 | 1.264 | 6.009 | 9.063 |
| quick_sort | reverse_sorted | 42 | 5 | 0 | 76.610 | 77.446 | 5.045 | 73.246 | 85.972 |
| pdq_sort | reverse_sorted | 42 | 5 | 0 | 1.584 | 1.655 | 0.105 | 1.577 | 1.793 |
| tim_sort | reverse_sorted | 42 | 5 | 0 | 2.057 | 2.109 | 0.237 | 1.881 | 2.372 |
| merge_sort | reverse_sorted | 42 | 5 | 0 | 11.224 | 12.429 | 1.933 | 11.102 | 15.575 |
| radix_sort | reverse_sorted | 42 | 5 | 0 | 9.228 | 8.710 | 1.240 | 7.412 | 10.212 |
| std_sort | duplicate_heavy | 42 | 5 | 0 | 21.876 | 21.674 | 0.676 | 20.489 | 22.132 |
| quick_sort | duplicate_heavy | 42 | 5 | 0 | 14.253 | 13.936 | 0.881 | 12.372 | 14.452 |
| pdq_sort | duplicate_heavy | 42 | 5 | 0 | 4.211 | 4.091 | 0.264 | 3.636 | 4.282 |
| tim_sort | duplicate_heavy | 42 | 5 | 0 | 40.939 | 40.693 | 1.887 | 37.499 | 42.180 |
| merge_sort | duplicate_heavy | 42 | 5 | 0 | 36.602 | 36.924 | 1.438 | 35.175 | 39.015 |
| radix_sort | duplicate_heavy | 42 | 5 | 0 | 13.410 | 13.370 | 0.243 | 12.996 | 13.621 |
| std_sort | nearly_sorted | 42 | 5 | 0 | 10.946 | 10.961 | 0.402 | 10.482 | 11.410 |
| quick_sort | nearly_sorted | 42 | 5 | 0 | 33.267 | 33.043 | 0.626 | 31.987 | 33.579 |
| pdq_sort | nearly_sorted | 42 | 5 | 0 | 8.806 | 8.825 | 0.185 | 8.559 | 9.012 |
| tim_sort | nearly_sorted | 42 | 5 | 0 | 8.073 | 8.198 | 0.378 | 7.744 | 8.723 |
| merge_sort | nearly_sorted | 42 | 5 | 0 | 16.649 | 16.574 | 0.816 | 15.267 | 17.324 |
| radix_sort | nearly_sorted | 42 | 5 | 0 | 8.775 | 8.822 | 0.615 | 8.145 | 9.462 |
| std_sort | uniform | 2718 | 5 | 0 | 57.699 | 58.434 | 1.840 | 56.391 | 60.622 |
| quick_sort | uniform | 2718 | 5 | 0 | 83.771 | 84.184 | 2.665 | 80.477 | 87.675 |
| pdq_sort | uniform | 2718 | 5 | 0 | 24.457 | 24.409 | 0.925 | 23.282 | 25.575 |
| tim_sort | uniform | 2718 | 5 | 0 | 81.263 | 81.083 | 1.982 | 78.314 | 82.981 |
| merge_sort | uniform | 2718 | 5 | 0 | 74.384 | 76.590 | 3.381 | 74.006 | 81.113 |
| radix_sort | uniform | 2718 | 5 | 0 | 7.268 | 7.326 | 0.448 | 6.931 | 8.041 |
| std_sort | sorted | 2718 | 5 | 0 | 8.740 | 9.371 | 1.705 | 8.079 | 12.351 |
| quick_sort | sorted | 2718 | 5 | 0 | 77.685 | 76.506 | 4.278 | 71.470 | 80.615 |
| pdq_sort | sorted | 2718 | 5 | 0 | 0.771 | 0.766 | 0.041 | 0.709 | 0.817 |
| tim_sort | sorted | 2718 | 5 | 0 | 0.416 | 0.420 | 0.055 | 0.373 | 0.508 |
| merge_sort | sorted | 2718 | 5 | 0 | 10.942 | 12.036 | 2.364 | 10.332 | 16.053 |
| radix_sort | sorted | 2718 | 5 | 0 | 8.559 | 8.884 | 2.023 | 7.199 | 12.342 |
| std_sort | reverse_sorted | 2718 | 5 | 0 | 5.844 | 5.939 | 0.225 | 5.752 | 6.324 |
| quick_sort | reverse_sorted | 2718 | 5 | 0 | 68.861 | 69.311 | 1.163 | 68.649 | 71.377 |
| pdq_sort | reverse_sorted | 2718 | 5 | 0 | 1.427 | 1.401 | 0.060 | 1.330 | 1.459 |
| tim_sort | reverse_sorted | 2718 | 5 | 0 | 1.769 | 1.809 | 0.110 | 1.709 | 1.973 |
| merge_sort | reverse_sorted | 2718 | 5 | 0 | 9.199 | 9.461 | 0.497 | 9.098 | 10.290 |
| radix_sort | reverse_sorted | 2718 | 5 | 0 | 7.286 | 7.381 | 0.220 | 7.224 | 7.766 |
| std_sort | duplicate_heavy | 2718 | 5 | 0 | 20.182 | 22.768 | 4.331 | 18.782 | 28.008 |
| quick_sort | duplicate_heavy | 2718 | 5 | 0 | 15.165 | 15.755 | 2.168 | 14.067 | 19.375 |
| pdq_sort | duplicate_heavy | 2718 | 5 | 0 | 4.248 | 4.726 | 1.135 | 3.721 | 6.565 |
| tim_sort | duplicate_heavy | 2718 | 5 | 0 | 42.375 | 46.312 | 8.320 | 37.791 | 57.005 |
| merge_sort | duplicate_heavy | 2718 | 5 | 0 | 43.235 | 41.405 | 6.991 | 32.751 | 49.739 |
| radix_sort | duplicate_heavy | 2718 | 5 | 0 | 13.286 | 13.733 | 1.797 | 11.869 | 16.520 |
| std_sort | nearly_sorted | 2718 | 5 | 0 | 10.407 | 10.421 | 0.459 | 9.913 | 11.094 |
| quick_sort | nearly_sorted | 2718 | 5 | 0 | 31.783 | 31.851 | 0.588 | 31.257 | 32.809 |
| pdq_sort | nearly_sorted | 2718 | 5 | 0 | 8.627 | 8.641 | 0.030 | 8.616 | 8.678 |
| tim_sort | nearly_sorted | 2718 | 5 | 0 | 7.693 | 7.771 | 0.356 | 7.329 | 8.291 |
| merge_sort | nearly_sorted | 2718 | 5 | 0 | 15.330 | 15.483 | 0.751 | 14.438 | 16.272 |
| radix_sort | nearly_sorted | 2718 | 5 | 0 | 8.388 | 8.333 | 0.373 | 7.765 | 8.729 |

## Interpretation and limitations

These are descriptive observations on one shared Pop!_OS machine, GNU 13.3.0, Release -O3 -DNDEBUG, dynamically managed powersave frequency policy. Seeds vary data, while repeated timings reuse that data; trials are not independent datasets. Algorithm effects can depend on distribution, ordering, implementation, compiler and hardware. No universal ranking or statistical significance is asserted.

CPU affinity, frequency, thermal state, cache state and background activity were not controlled. Input copying warms memory; algorithm-owned allocation is timed. No timer-overhead subtraction. No measured RSS or comparison-count study was run alongside these primary timings. The 16 MB array/workspace estimate is planning only, not measured algorithm memory.

The immutable v1 protocol and environment snapshots are retained under the raw study directory. Per-seed statistics reuse scripts/analyze_results.py; the retained analyze_study.py verifies all groups and produces this table plus equal-weight cross-seed statistics. No sizes above 1M, CUDA or GPU workload was run.
