# CUB prepared GPU timing smoke report

Protocol: `cuda_sort_timing_v1`. This is an infrastructure smoke, not a comparative performance study.

Tesla T4 / compute7.5; driver580.82.07; CUDA nvcc/toolkit13.0.88 and runtime API13000; GCC13.3.0; CMake3.31.10. Release `-O3 -DNDEBUG`, CUDA architecture75. CUB3.0.1, CCCL commit f19d875da0d8bfb2e38c109b2b40522b8abbbbc3, BSD-3-Clause. Exact dependency/build/source/binary hashes and command records are retained in the raw bundle.

Smallest: N1025, uniform, seed1729, W1/R5. Matrix: N0,1,1025,65537; uniform, sorted, reverse_sorted, duplicate_heavy, nearly_sorted, signed_edges; seeds1729,42; W1/R5. All48 configurations completed,240 measured and48 warmups; including smallest,245 measured and49 warmups. Zero failures/missing. Every output equalled std::sort outside timing. Empty/singleton GPU phases deliberately zero; signed_edges ignores seed. Warmups are retained and excluded from summaries.

A separate validation-only framework exercised60 size/workload configurations,120 measured/60 warmup rows. These are test diagnostics, excluded from the performance summaries. The unchanged production adapter also passed475 inputs/1900 output checks directly and again through1/1 CTest.

Four metrics: H2D/device-sort/D2H use CUDA-event intervals on a private nonblocking stream; end-to-end uses host steady_clock through checked completion. Reused pinned/device/workspace buffers; excludes allocation/context setup, staging, output-vector copy, oracle/verification, event queries and I/O. Includes enqueue/dispatch/check/wait. Device interval can include dispatch gaps; it is not isolated kernel active time. See docs/CUDA_TIMING_PROTOCOL_v1.md for exact boundaries.

## Example: N65537 uniform, seed1729

Five measured trials. Values below convert raw ns to microseconds by dividing1000. Sample SD uses ddof1. This single cell supports no general speedup or ranking.

| Metric | Median us | Mean us | Sample SD us | Min us | Max us |
| --- | ---: | ---: | ---: | ---: | ---: |
| h2d_ns | 28.896 | 29.165 | 1.117 | 28.032 | 31.040 |
| device_sort_ns | 63.904 | 63.392 | 1.420 | 61.312 | 64.704 |
| d2h_ns | 27.680 | 27.430 | 2.204 | 24.736 | 30.368 |
| end_to_end_ns | 128.136 | 127.790 | 1.684 | 125.231 | 129.542 |

## All matrix cells

Each cell retains five measured observations. Units ns. No pooling across seeds or metrics; no outlier removal.

| N | Workload | Seed | Metric | Successful | Failed | Missing | Median ns | Mean ns | Sample SD ns | Min ns | Max ns |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | uniform | 1729 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | uniform | 1729 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | uniform | 1729 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | uniform | 1729 | end_to_end_ns | 5 | 0 | 0 | 55.000 | 55.400 | 5.320 | 50.000 | 63.000 |
| 0 | uniform | 42 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | uniform | 42 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | uniform | 42 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | uniform | 42 | end_to_end_ns | 5 | 0 | 0 | 51.000 | 50.400 | 1.517 | 48.000 | 52.000 |
| 0 | sorted | 1729 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | sorted | 1729 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | sorted | 1729 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | sorted | 1729 | end_to_end_ns | 5 | 0 | 0 | 42.000 | 42.400 | 1.517 | 41.000 | 45.000 |
| 0 | sorted | 42 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | sorted | 42 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | sorted | 42 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | sorted | 42 | end_to_end_ns | 5 | 0 | 0 | 37.000 | 38.600 | 3.435 | 36.000 | 44.000 |
| 0 | reverse_sorted | 1729 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | reverse_sorted | 1729 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | reverse_sorted | 1729 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | reverse_sorted | 1729 | end_to_end_ns | 5 | 0 | 0 | 45.000 | 45.400 | 1.673 | 44.000 | 48.000 |
| 0 | reverse_sorted | 42 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | reverse_sorted | 42 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | reverse_sorted | 42 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | reverse_sorted | 42 | end_to_end_ns | 5 | 0 | 0 | 24.000 | 27.400 | 8.735 | 23.000 | 43.000 |
| 0 | duplicate_heavy | 1729 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | duplicate_heavy | 1729 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | duplicate_heavy | 1729 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | duplicate_heavy | 1729 | end_to_end_ns | 5 | 0 | 0 | 39.000 | 41.600 | 4.336 | 39.000 | 49.000 |
| 0 | duplicate_heavy | 42 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | duplicate_heavy | 42 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | duplicate_heavy | 42 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | duplicate_heavy | 42 | end_to_end_ns | 5 | 0 | 0 | 42.000 | 40.400 | 4.930 | 32.000 | 45.000 |
| 0 | nearly_sorted | 1729 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | nearly_sorted | 1729 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | nearly_sorted | 1729 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | nearly_sorted | 1729 | end_to_end_ns | 5 | 0 | 0 | 37.000 | 37.800 | 3.564 | 35.000 | 44.000 |
| 0 | nearly_sorted | 42 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | nearly_sorted | 42 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | nearly_sorted | 42 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | nearly_sorted | 42 | end_to_end_ns | 5 | 0 | 0 | 37.000 | 38.600 | 4.722 | 36.000 | 47.000 |
| 0 | signed_edges | 1729 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | signed_edges | 1729 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | signed_edges | 1729 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | signed_edges | 1729 | end_to_end_ns | 5 | 0 | 0 | 36.000 | 37.600 | 4.159 | 35.000 | 45.000 |
| 0 | signed_edges | 42 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | signed_edges | 42 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | signed_edges | 42 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0 | signed_edges | 42 | end_to_end_ns | 5 | 0 | 0 | 43.000 | 44.800 | 4.087 | 42.000 | 52.000 |
| 1 | uniform | 1729 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | uniform | 1729 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | uniform | 1729 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | uniform | 1729 | end_to_end_ns | 5 | 0 | 0 | 38.000 | 39.200 | 3.834 | 37.000 | 46.000 |
| 1 | uniform | 42 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | uniform | 42 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | uniform | 42 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | uniform | 42 | end_to_end_ns | 5 | 0 | 0 | 37.000 | 38.400 | 4.278 | 36.000 | 46.000 |
| 1 | sorted | 1729 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | sorted | 1729 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | sorted | 1729 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | sorted | 1729 | end_to_end_ns | 5 | 0 | 0 | 39.000 | 40.800 | 4.087 | 38.000 | 48.000 |
| 1 | sorted | 42 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | sorted | 42 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | sorted | 42 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | sorted | 42 | end_to_end_ns | 5 | 0 | 0 | 37.000 | 41.200 | 9.391 | 37.000 | 58.000 |
| 1 | reverse_sorted | 1729 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | reverse_sorted | 1729 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | reverse_sorted | 1729 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | reverse_sorted | 1729 | end_to_end_ns | 5 | 0 | 0 | 37.000 | 39.000 | 3.937 | 37.000 | 46.000 |
| 1 | reverse_sorted | 42 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | reverse_sorted | 42 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | reverse_sorted | 42 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | reverse_sorted | 42 | end_to_end_ns | 5 | 0 | 0 | 36.000 | 37.800 | 7.155 | 31.000 | 50.000 |
| 1 | duplicate_heavy | 1729 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | duplicate_heavy | 1729 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | duplicate_heavy | 1729 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | duplicate_heavy | 1729 | end_to_end_ns | 5 | 0 | 0 | 47.000 | 48.200 | 2.775 | 46.000 | 53.000 |
| 1 | duplicate_heavy | 42 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | duplicate_heavy | 42 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | duplicate_heavy | 42 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | duplicate_heavy | 42 | end_to_end_ns | 5 | 0 | 0 | 39.000 | 40.800 | 4.087 | 38.000 | 48.000 |
| 1 | nearly_sorted | 1729 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | nearly_sorted | 1729 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | nearly_sorted | 1729 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | nearly_sorted | 1729 | end_to_end_ns | 5 | 0 | 0 | 47.000 | 47.400 | 2.881 | 45.000 | 52.000 |
| 1 | nearly_sorted | 42 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | nearly_sorted | 42 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | nearly_sorted | 42 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | nearly_sorted | 42 | end_to_end_ns | 5 | 0 | 0 | 42.000 | 43.000 | 3.391 | 41.000 | 49.000 |
| 1 | signed_edges | 1729 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | signed_edges | 1729 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | signed_edges | 1729 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | signed_edges | 1729 | end_to_end_ns | 5 | 0 | 0 | 48.000 | 48.400 | 0.548 | 48.000 | 49.000 |
| 1 | signed_edges | 42 | h2d_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | signed_edges | 42 | device_sort_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | signed_edges | 42 | d2h_ns | 5 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1 | signed_edges | 42 | end_to_end_ns | 5 | 0 | 0 | 42.000 | 44.200 | 8.526 | 38.000 | 59.000 |
| 1025 | uniform | 1729 | h2d_ns | 5 | 0 | 0 | 5024.000 | 5715.200 | 1497.621 | 4736.000 | 8352.000 |
| 1025 | uniform | 1729 | device_sort_ns | 5 | 0 | 0 | 20256.000 | 21990.400 | 3704.157 | 19487.999 | 28320.000 |
| 1025 | uniform | 1729 | d2h_ns | 5 | 0 | 0 | 4096.000 | 6131.200 | 3536.007 | 3424.000 | 11232.000 |
| 1025 | uniform | 1729 | end_to_end_ns | 5 | 0 | 0 | 41039.000 | 40454.400 | 5384.622 | 35001.000 | 48185.000 |
| 1025 | uniform | 42 | h2d_ns | 5 | 0 | 0 | 4960.000 | 5587.200 | 1513.603 | 4768.000 | 8288.000 |
| 1025 | uniform | 42 | device_sort_ns | 5 | 0 | 0 | 20479.999 | 20364.800 | 716.471 | 19584.000 | 21407.999 |
| 1025 | uniform | 42 | d2h_ns | 5 | 0 | 0 | 4064.000 | 3878.400 | 433.715 | 3392.000 | 4384.000 |
| 1025 | uniform | 42 | end_to_end_ns | 5 | 0 | 0 | 35343.000 | 36482.800 | 2357.447 | 34890.000 | 40594.000 |
| 1025 | sorted | 1729 | h2d_ns | 5 | 0 | 0 | 4992.000 | 5516.800 | 1319.122 | 4832.000 | 7872.000 |
| 1025 | sorted | 1729 | device_sort_ns | 5 | 0 | 0 | 21407.999 | 23507.200 | 4065.045 | 20160.001 | 28767.999 |
| 1025 | sorted | 1729 | d2h_ns | 5 | 0 | 0 | 4384.000 | 5907.200 | 2503.026 | 3648.000 | 9184.000 |
| 1025 | sorted | 1729 | end_to_end_ns | 5 | 0 | 0 | 40425.000 | 41437.600 | 6102.781 | 35296.000 | 47946.000 |
| 1025 | sorted | 42 | h2d_ns | 5 | 0 | 0 | 5056.000 | 5747.200 | 1653.753 | 4928.000 | 8704.000 |
| 1025 | sorted | 42 | device_sort_ns | 5 | 0 | 0 | 20992.000 | 24102.400 | 5386.437 | 19648.001 | 31872.001 |
| 1025 | sorted | 42 | d2h_ns | 5 | 0 | 0 | 4320.000 | 5139.200 | 2275.108 | 3744.000 | 9184.000 |
| 1025 | sorted | 42 | end_to_end_ns | 5 | 0 | 0 | 40456.000 | 41602.600 | 6131.785 | 35220.000 | 48305.000 |
| 1025 | reverse_sorted | 1729 | h2d_ns | 5 | 0 | 0 | 4960.000 | 5324.800 | 1125.381 | 4544.000 | 7264.000 |
| 1025 | reverse_sorted | 1729 | device_sort_ns | 5 | 0 | 0 | 20544.000 | 23987.200 | 7807.232 | 20384.001 | 37951.998 |
| 1025 | reverse_sorted | 1729 | d2h_ns | 5 | 0 | 0 | 3584.000 | 4044.800 | 1176.756 | 2912.000 | 5824.000 |
| 1025 | reverse_sorted | 1729 | end_to_end_ns | 5 | 0 | 0 | 35444.000 | 39947.200 | 10924.634 | 33966.000 | 59419.000 |
| 1025 | reverse_sorted | 42 | h2d_ns | 5 | 0 | 0 | 4928.000 | 5548.800 | 1356.438 | 4864.000 | 7968.000 |
| 1025 | reverse_sorted | 42 | device_sort_ns | 5 | 0 | 0 | 21215.999 | 23033.600 | 3405.212 | 20160.001 | 26880.000 |
| 1025 | reverse_sorted | 42 | d2h_ns | 5 | 0 | 0 | 9184.000 | 7392.000 | 3502.575 | 3264.000 | 11232.000 |
| 1025 | reverse_sorted | 42 | end_to_end_ns | 5 | 0 | 0 | 43195.000 | 42540.000 | 5241.713 | 34844.000 | 47496.000 |
| 1025 | duplicate_heavy | 1729 | h2d_ns | 5 | 0 | 0 | 4992.000 | 5574.400 | 1358.475 | 4832.000 | 8000.000 |
| 1025 | duplicate_heavy | 1729 | device_sort_ns | 5 | 0 | 0 | 20416.001 | 20505.600 | 718.897 | 19711.999 | 21632.001 |
| 1025 | duplicate_heavy | 1729 | d2h_ns | 5 | 0 | 0 | 4128.000 | 6796.800 | 3698.569 | 4064.000 | 10912.000 |
| 1025 | duplicate_heavy | 1729 | end_to_end_ns | 5 | 0 | 0 | 40968.000 | 39509.400 | 3604.346 | 35304.000 | 42788.000 |
| 1025 | duplicate_heavy | 42 | h2d_ns | 5 | 0 | 0 | 4992.000 | 5939.200 | 1804.187 | 4800.000 | 9088.000 |
| 1025 | duplicate_heavy | 42 | device_sort_ns | 5 | 0 | 0 | 19967.999 | 21171.200 | 2722.879 | 19711.999 | 26016.001 |
| 1025 | duplicate_heavy | 42 | d2h_ns | 5 | 0 | 0 | 5344.000 | 5868.800 | 3248.165 | 3232.000 | 11232.000 |
| 1025 | duplicate_heavy | 42 | end_to_end_ns | 5 | 0 | 0 | 37502.000 | 39846.000 | 6182.957 | 34545.000 | 49364.000 |
| 1025 | nearly_sorted | 1729 | h2d_ns | 5 | 0 | 0 | 5088.000 | 6009.600 | 1753.793 | 5024.000 | 9088.000 |
| 1025 | nearly_sorted | 1729 | device_sort_ns | 5 | 0 | 0 | 20320.000 | 21369.600 | 2361.223 | 19840.000 | 25504.000 |
| 1025 | nearly_sorted | 1729 | d2h_ns | 5 | 0 | 0 | 5088.000 | 4825.600 | 1382.570 | 3072.000 | 6784.000 |
| 1025 | nearly_sorted | 1729 | end_to_end_ns | 5 | 0 | 0 | 36745.000 | 39154.000 | 5954.400 | 34925.000 | 49376.000 |
| 1025 | nearly_sorted | 42 | h2d_ns | 5 | 0 | 0 | 5024.000 | 5824.000 | 1897.333 | 4896.000 | 9216.000 |
| 1025 | nearly_sorted | 42 | device_sort_ns | 5 | 0 | 0 | 20384.001 | 20473.600 | 261.344 | 20223.999 | 20768.000 |
| 1025 | nearly_sorted | 42 | d2h_ns | 5 | 0 | 0 | 4128.000 | 5465.600 | 3047.435 | 3232.000 | 10784.000 |
| 1025 | nearly_sorted | 42 | end_to_end_ns | 5 | 0 | 0 | 36554.000 | 38426.400 | 3336.899 | 35376.000 | 42469.000 |
| 1025 | signed_edges | 1729 | h2d_ns | 5 | 0 | 0 | 5152.000 | 7475.200 | 3536.297 | 5024.000 | 12928.000 |
| 1025 | signed_edges | 1729 | device_sort_ns | 5 | 0 | 0 | 21088.000 | 22547.200 | 3013.153 | 20000.000 | 27392.000 |
| 1025 | signed_edges | 1729 | d2h_ns | 5 | 0 | 0 | 5120.000 | 5920.000 | 2429.578 | 3424.000 | 8608.000 |
| 1025 | signed_edges | 1729 | end_to_end_ns | 5 | 0 | 0 | 42663.000 | 42522.600 | 7057.668 | 35340.000 | 51487.000 |
| 1025 | signed_edges | 42 | h2d_ns | 5 | 0 | 0 | 4864.000 | 5555.200 | 1511.403 | 4800.000 | 8256.000 |
| 1025 | signed_edges | 42 | device_sort_ns | 5 | 0 | 0 | 20064.000 | 20249.600 | 912.533 | 19296.000 | 21695.999 |
| 1025 | signed_edges | 42 | d2h_ns | 5 | 0 | 0 | 4096.000 | 5382.400 | 3284.282 | 3392.000 | 11232.000 |
| 1025 | signed_edges | 42 | end_to_end_ns | 5 | 0 | 0 | 35621.000 | 37736.400 | 3651.540 | 34578.000 | 42311.000 |
| 65537 | uniform | 1729 | h2d_ns | 5 | 0 | 0 | 28896.000 | 29164.800 | 1117.162 | 28031.999 | 31040.000 |
| 65537 | uniform | 1729 | device_sort_ns | 5 | 0 | 0 | 63904.002 | 63392.001 | 1419.949 | 61312.001 | 64704.001 |
| 65537 | uniform | 1729 | d2h_ns | 5 | 0 | 0 | 27680.000 | 27430.400 | 2204.101 | 24736.000 | 30368.000 |
| 65537 | uniform | 1729 | end_to_end_ns | 5 | 0 | 0 | 128136.000 | 127790.200 | 1683.554 | 125231.000 | 129542.000 |
| 65537 | uniform | 42 | h2d_ns | 5 | 0 | 0 | 28511.999 | 29299.200 | 2012.009 | 27456.000 | 32159.999 |
| 65537 | uniform | 42 | device_sort_ns | 5 | 0 | 0 | 62592.000 | 62630.400 | 538.514 | 61919.998 | 63327.998 |
| 65537 | uniform | 42 | d2h_ns | 5 | 0 | 0 | 26079.999 | 26316.800 | 1973.209 | 23488.000 | 28640.000 |
| 65537 | uniform | 42 | end_to_end_ns | 5 | 0 | 0 | 125910.000 | 126210.000 | 3707.376 | 122726.000 | 131905.000 |
| 65537 | sorted | 1729 | h2d_ns | 5 | 0 | 0 | 31392.001 | 33779.201 | 5464.209 | 31168.001 | 43552.000 |
| 65537 | sorted | 1729 | device_sort_ns | 5 | 0 | 0 | 63552.000 | 63321.602 | 2037.650 | 60160.000 | 65760.002 |
| 65537 | sorted | 1729 | d2h_ns | 5 | 0 | 0 | 25696.000 | 27091.200 | 2430.168 | 25056.001 | 30880.000 |
| 65537 | sorted | 1729 | end_to_end_ns | 5 | 0 | 0 | 132491.000 | 134345.000 | 6220.179 | 130311.000 | 145303.000 |
| 65537 | sorted | 42 | h2d_ns | 5 | 0 | 0 | 28096.000 | 28870.400 | 2317.008 | 27360.000 | 32928.001 |
| 65537 | sorted | 42 | device_sort_ns | 5 | 0 | 0 | 62368.002 | 62220.801 | 516.778 | 61344.001 | 62720.001 |
| 65537 | sorted | 42 | d2h_ns | 5 | 0 | 0 | 27968.001 | 27462.400 | 1486.433 | 25312.001 | 29184.001 |
| 65537 | sorted | 42 | end_to_end_ns | 5 | 0 | 0 | 125828.000 | 126000.800 | 3705.666 | 122513.000 | 131496.000 |
| 65537 | reverse_sorted | 1729 | h2d_ns | 5 | 0 | 0 | 27680.000 | 28262.400 | 1379.233 | 27232.001 | 30592.000 |
| 65537 | reverse_sorted | 1729 | device_sort_ns | 5 | 0 | 0 | 61983.999 | 61759.999 | 416.000 | 61152.000 | 62112.000 |
| 65537 | reverse_sorted | 1729 | d2h_ns | 5 | 0 | 0 | 28991.999 | 28198.400 | 3480.168 | 23615.999 | 32448.001 |
| 65537 | reverse_sorted | 1729 | end_to_end_ns | 5 | 0 | 0 | 124555.000 | 125275.000 | 2802.372 | 121942.000 | 129233.000 |
| 65537 | reverse_sorted | 42 | h2d_ns | 5 | 0 | 0 | 27519.999 | 28147.200 | 1220.539 | 27071.999 | 30015.999 |
| 65537 | reverse_sorted | 42 | device_sort_ns | 5 | 0 | 0 | 61951.999 | 61964.800 | 865.362 | 60736.001 | 62944.002 |
| 65537 | reverse_sorted | 42 | d2h_ns | 5 | 0 | 0 | 26079.999 | 26579.200 | 920.966 | 25952.000 | 28096.000 |
| 65537 | reverse_sorted | 42 | end_to_end_ns | 5 | 0 | 0 | 123568.000 | 124544.200 | 1984.013 | 123157.000 | 127990.000 |
| 65537 | duplicate_heavy | 1729 | h2d_ns | 5 | 0 | 0 | 31968.001 | 32051.200 | 696.909 | 31168.001 | 33119.999 |
| 65537 | duplicate_heavy | 1729 | device_sort_ns | 5 | 0 | 0 | 61184.000 | 61222.400 | 867.961 | 60384.002 | 62463.999 |
| 65537 | duplicate_heavy | 1729 | d2h_ns | 5 | 0 | 0 | 26688.000 | 26438.400 | 1334.519 | 24736.000 | 28287.999 |
| 65537 | duplicate_heavy | 1729 | end_to_end_ns | 5 | 0 | 0 | 129951.000 | 130028.400 | 1564.822 | 127818.000 | 132077.000 |
| 65537 | duplicate_heavy | 42 | h2d_ns | 5 | 0 | 0 | 28864.000 | 29043.200 | 1468.971 | 27616.000 | 30912.001 |
| 65537 | duplicate_heavy | 42 | device_sort_ns | 5 | 0 | 0 | 59712.000 | 59296.000 | 856.560 | 57888.001 | 60031.999 |
| 65537 | duplicate_heavy | 42 | d2h_ns | 5 | 0 | 0 | 28192.000 | 28409.600 | 508.689 | 27904.000 | 29088.000 |
| 65537 | duplicate_heavy | 42 | end_to_end_ns | 5 | 0 | 0 | 123692.000 | 124349.600 | 2016.488 | 122507.000 | 126566.000 |
| 65537 | nearly_sorted | 1729 | h2d_ns | 5 | 0 | 0 | 28480.001 | 28902.400 | 1096.765 | 28096.000 | 30816.000 |
| 65537 | nearly_sorted | 1729 | device_sort_ns | 5 | 0 | 0 | 61567.999 | 61728.001 | 776.618 | 60800.001 | 62848.002 |
| 65537 | nearly_sorted | 1729 | d2h_ns | 5 | 0 | 0 | 25855.999 | 28070.400 | 5373.876 | 23712.000 | 37344.001 |
| 65537 | nearly_sorted | 1729 | end_to_end_ns | 5 | 0 | 0 | 123987.000 | 125935.400 | 5872.729 | 122086.000 | 136267.000 |
| 65537 | nearly_sorted | 42 | h2d_ns | 5 | 0 | 0 | 29568.000 | 29689.600 | 814.084 | 28991.999 | 31040.000 |
| 65537 | nearly_sorted | 42 | device_sort_ns | 5 | 0 | 0 | 62399.998 | 62220.801 | 724.996 | 61152.000 | 62912.002 |
| 65537 | nearly_sorted | 42 | d2h_ns | 5 | 0 | 0 | 25728.000 | 27296.000 | 3705.028 | 25440.000 | 33920.001 |
| 65537 | nearly_sorted | 42 | end_to_end_ns | 5 | 0 | 0 | 124581.000 | 127366.800 | 6390.397 | 123664.000 | 138741.000 |
| 65537 | signed_edges | 1729 | h2d_ns | 5 | 0 | 0 | 31136.001 | 31200.000 | 615.532 | 30400.001 | 32127.999 |
| 65537 | signed_edges | 1729 | device_sort_ns | 5 | 0 | 0 | 62144.000 | 62745.601 | 3434.481 | 59360.001 | 68512.000 |
| 65537 | signed_edges | 1729 | d2h_ns | 5 | 0 | 0 | 26112.000 | 26496.000 | 3472.995 | 23072.001 | 32224.000 |
| 65537 | signed_edges | 1729 | end_to_end_ns | 5 | 0 | 0 | 128837.000 | 129760.800 | 5452.551 | 122715.000 | 136513.000 |
| 65537 | signed_edges | 42 | h2d_ns | 5 | 0 | 0 | 27456.000 | 28153.600 | 1317.142 | 27327.999 | 30432.001 |
| 65537 | signed_edges | 42 | device_sort_ns | 5 | 0 | 0 | 59967.998 | 60652.799 | 1405.380 | 59455.998 | 62208.001 |
| 65537 | signed_edges | 42 | d2h_ns | 5 | 0 | 0 | 26144.000 | 26470.400 | 3158.969 | 23072.001 | 29792.000 |
| 65537 | signed_edges | 42 | end_to_end_ns | 5 | 0 | 0 | 123981.000 | 122951.000 | 2352.516 | 118868.000 | 124713.000 |

## Reproducibility and limitations

Original and regenerated cloud summaries are byte-identical. Two independent local regenerations are byte-identical; local/cloud groups and every statistic agree. Absolute source provenance paths correctly differ after transfer. All196 cell/metric statistic groups were independently recalculated from CSV with Python statistics;980 measured metric values were checked. Raw warmups/outliers remain retained.

This report was generated from processed/matrix.json, not entered timing values. All48 configurations, including trivial/duplicate seed data, remain visible. Seeds for signed_edges do not create distinct datasets, and repetitions are not independent datasets. No confidence interval or significance claim.

CPU Release27/27 and Debug ASan/UBSan27/27 passed, leak detection enabled. Each host CUDA-analysis run passes12 methods and skips2 hardware methods; the real GPU framework passes all14. CPU sanitizers do not instrument CUDA device code; Compute Sanitizer was not run.

Known compiler warning:100 generated line-directive warnings building production correctness,161 building the prepared timing translation unit. All are nvcc/GCC extension diagnostics under the existing -Wpedantic setting; no other warning category, no suppression or dependency-pin workaround. No source/CUB compatibility fix was needed.

Colab frequency, thermal state and background contention were not controlled. Post-run probes are separately labelled and do not describe conditions during timing. CUDA event API float-ms precision/resolution limits small measurements; ns columns do not imply ns resolution. Context/allocator overhead is outside the prepared timing contract. The old session had expired; one replacement T4 session was created and verified.

Next: freeze a modest controlled GPU/CPU comparison protocol at <=1M, clearly matching prepared GPU transfer-inclusive versus CPU sort-only boundaries and optionally adding separately labelled allocation-inclusive GPU latency. Estimate resources first; no100M, full GPU study, speedup, or universal ranking follows from this smoke.
