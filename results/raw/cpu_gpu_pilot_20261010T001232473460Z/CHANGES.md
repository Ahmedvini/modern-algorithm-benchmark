# Controlled CPU/GPU pilot implementation changes

Existing source changes: additive CMake integration only. Production sorters, CUB pin, existing timing code, tests and frozen study assets are unchanged. No Git metadata is present.

- CMakeLists.txt: host-testable comparison library/input helper, explicit OFF-by-default CUDA comparison option, and two CTest groups. Exact additive diff: CMAKE_ADDITIONS.diff.
- docs/CPU_GPU_COMPARISON_DRIVER_v1.md
- docs/CPU_GPU_DRIVER_REVIEW_v1.json
- include/benchmark/comparison.hpp
- include/benchmark/cuda_comparison.hpp
- scripts/analyze_cpu_gpu.py
- scripts/cpu_gpu_protocol.py
- scripts/run_cpu_gpu_pilot.py
- scripts/validate_cpu_gpu_pilot.py
- src/benchmark/comparison.cpp
- src/benchmark/comparison_input_main.cpp
- src/benchmark/cpu_gpu_main.cpp
- src/cuda/comparison_resources.cu
- tests/test_comparison.cpp
- tests/test_cpu_gpu_comparison.py

The new driver separates allocation-inclusive host-vector API calls from the unchanged prepared-buffer diagnostics. The pilot-only runner gates execution on fresh hardware/build/correctness evidence, flushes attempts/samples, rejects output collisions and stops on failures. The analyzer validates frozen identities/order/counts, finite metrics, actual threads, resource caps and full completeness before producing paired host-call ratios. Synthetic tests are explicitly rejected as performance evidence.

Workspace diagnostics query the unchanged CUB API parameters separately and record successful cudaMalloc request sizes. They do not instrument production allocations or measure allocator-rounded memory. No frozen resource estimate is modified.

Actual validation outcomes are recorded separately in FINAL_AUDIT.md after execution.

Remote clean-source attempt v1 stopped before preflight: the validator required an absent build/ parent. The focused v2 fix creates the shared build parent while preserving exclusive per-run build paths. A new test verifies this clean-checkout case. Original v1 source and failure archive remain retained; v2 has a separate source hash and destination.

Session recovery history: the first visible session returned 404/401 before upload; a replacement was authorized. Corrected source v2 was uploaded and reached successful remote CPU sanitizer compilation, but that session later expired before final evidence retrieval. Its final/pilot outcome is explicitly unverified. A new session/destination v3 reruns all prerequisites from the same v2 source, with automatic evidence packaging. No prior attempt is reused as a passing prerequisite.

Final existing documentation changes: README.md documents the opt-in pilot command and actual status; docs/ROADMAP.md advances only driver/pilot and retains full-study/research pending; docs/AUDIT.md records observed tests/evidence/failures; docs/BENCHMARKING.md documents separated scopes/resources and final pilot outcome. No other existing source/test/vendor file changed. New evidence helpers and generated reports are distinct from production source.
