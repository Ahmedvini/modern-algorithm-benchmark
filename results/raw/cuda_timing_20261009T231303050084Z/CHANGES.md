# Files changed

No Git metadata. Changes are compared to source_before.json and the private local before-copy; no existing source file was deleted. CPU implementations, production CUDA adapter, CUB dependency metadata/license and frozen protocols remain byte-identical.

| File | Status | Purpose |
| --- | --- | --- |
| `docs/CUDA_TIMING_PROTOCOL_v1.md` | added | Versioned timing/allocation/workload/output/analysis contract frozen before execution. |
| `include/benchmark/cuda_timing.hpp` | added | Benchmark-only RAII prepared-session API with four measurements. |
| `scripts/analyze_cuda_results.py` | added | Strict schema/completeness checks and per-dataset four-metric statistics. |
| `scripts/run_cuda_matrix.py` | added | Exclusive serial deterministic matrix with exact command/failure/interruption evidence. |
| `scripts/validate_cuda_timing.py` | added | Real-GPU correctness -> smallest smoke -> framework -> matrix -> summary/hash verification. |
| `src/benchmark/cuda_main.cpp` | added | Release-only CLI, dataset restoration/oracle checks, CSV/metadata and safe bundles. |
| `src/cuda/cub_timing.cu` | added | Checked same-stream event/transfer/CUB/synchronization execution; reusable pinned/device buffers. |
| `tests/test_cuda_benchmark.py` | added | 12 host fixture methods and2 actual GPU CLI/integration methods; correctness, statistics, failures and safety. |
| `CMakeLists.txt` | modified | Register always-host CUDA analysis tests; preserve CPU targets/defaults. |
| `README.md` | modified | Document actual implementation, validation evidence, commands, limits and milestone status. |
| `cmake/cuda.cmake` | modified | Opt-in prepared CUDA library/CLI/GPU framework and generated CUDA build metadata; pin unchanged. |
| `docs/ALGORITHMS.md` | modified | Document actual implementation, validation evidence, commands, limits and milestone status. |
| `docs/AUDIT.md` | modified | Document actual implementation, validation evidence, commands, limits and milestone status. |
| `docs/BENCHMARKING.md` | modified | Document actual implementation, validation evidence, commands, limits and milestone status. |
| `docs/EXPERIMENT_PROTOCOL.md` | modified | Document actual implementation, validation evidence, commands, limits and milestone status. |
| `docs/METRICS.md` | modified | Document actual implementation, validation evidence, commands, limits and milestone status. |
| `docs/ROADMAP.md` | modified | Document actual implementation, validation evidence, commands, limits and milestone status. |

New evidence/derived outputs: results/raw/cuda_timing_20261009T231303050084Z and results/processed/cuda_timing_20261009T231303050084Z. Builds and credential-bearing CLI config stay under build/cuda_timing_20261009T231303050084Z; credentials are excluded from evidence. Source bundle fixes the tested snapshot; only documentation changed after GPU execution.

Final protected source check: 131 starting files unchanged; 125 tested non-document files match remote source. New timing protocol also matches. All9568 earlier result files remain unchanged.
