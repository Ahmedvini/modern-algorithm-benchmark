# Search Phase 3 final audit

## Phase 3 array search and batch benchmarking — 2026-10-09

### Inspection and baseline

Read AGENTS.md fully; inspected README, ROADMAP, AUDIT, BENCHMARKING,
EXPERIMENT_PROTOCOL, METRICS, ALGORITHMS, CMake, source/test interfaces, generator,
timing/output utilities and Python runner/analysis. Only the unchanged
std_lower_bound_search reference existed; the roadmap required independent linear,
binary and exponential adapters. No project search registry or query benchmark
existed. Anonymous temporary-file write/read/delete passed. Git metadata remains
absent (environment git status --short probe exit 128). Source backup and SHA-256
inventory are retained under /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/search_review_20261009T173830593675Z; all earlier results were hashed
before writing under /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/search_validation_20261009T173830593675Z. Historical test logs were copied separately.

Fresh pre-change Release configure/build/full CTest each exited 0; 15/15 groups
passed, with no correctness defect requiring repair. The versioned
SEARCH_PROTOCOL_v1.md and an identical evidence copy/hash were saved before engine
implementation. The final protocol hash still matches that pre-implementation
record. No sorting implementation/CLI/default/generator/vendor/test/tool changed.

### Implementation and contracts

Three project public/registry adapters: linear_search accepts any order; binary
and exponential require ascending input, documented without an O(N) per-call
check. Every result is first equal index or nullopt. Exponential expansion clamps
before doubling and binary refinement uses first+(last-first)/2. Empty inputs,
duplicates, negative values, extrema and size boundaries pass independent
std::find differential checks. Existing std_lower_bound is the reference in the
engine, never relabeled as the project implementation. ALGORITHMS.md documents
best/average/worst time models and O(1) per-lookup auxiliary space.

New search libraries/CLIs are separate from preserved sorting targets. Shared
project templates instantiate normal less/equality or checked run-local counters.
search_counts measures one executed key < or == predicate (key_predicate_v1);
index/bookkeeping/reference operations are excluded. This is distinct from
sorting's less-only convention. No global/shared counter or mandatory normal
instrumentation. Timing link/nm review confirms counted code absent.

search_benchmark reuses existing dataset/timing validation, fingerprints and CSV/
JSON escaping. It generates and sorts once outside lookup timing. The separate
preprocessing_sort_ns observation covers only final std::sort, not generation's
transforms; no index is built. Prepared data are immutable and all algorithms
receive the same category query lists. Source distributions can share sorted
multisets, explicitly documented. Query RNG streams are seeded separately by fixed
category identities, so selecting subsets does not change another category.

Nine policies: fixed first/middle/last hits, random-position hits, representable
below/interior/above misses, mixed_50 alternating random hits/misses and miss_empty.
Fixed/rand policies intentionally can overlap values; expected first-match index
and selected source rank remain explicit. Unavailable policies retain reasons
in run.json and summary availability, never invented observations. Mixed batches
have exact 50% hit/miss ratio; aggregate ratio varies with policy availability.
All 3,008 smoke query records contain 1,728 hits and 1,280 misses before repetition.

steady_clock times batch loops/normal dispatch/preallocated answer stores, in ns.
Every answer is validated outside timing on warm-ups and measured calls. Generation,
preprocessing, query/reference creation, buffer allocation, metadata/I/O and counts
are excluded. All warm-ups precede measured rounds; algorithms rotate cyclically
by dataset seed/trial within category. Batch-average ns/query is normalized, not
individual-query time; max batch/normalized average is not max individual latency.
No timer calibration, cache flushing, CPU affinity/frequency/thermal/load control.
The planning estimate 16*N+128*batch_size*9 is not measured memory/hard RSS limit.
Review reserved gap capacity to N, avoiding geometric growth exceeding its budget,
and made missing-position hashing explicitly uint64 on narrower size_t platforms.
Only GNU/Linux was executed; no 32-bit/Windows/macOS execution is claimed.

The dedicated analyzer validates all 32 trial fields, six query fields, metadata,
query hashes/positions/hit counts, cyclic ordering and completion/row totals.
Per-run/algorithm/category summaries report success/failure/missing/warm-up counts,
median/mean/sample SD (n-1)/min/max batch time and normalized average. Warm-ups and
all raw outliers are retained; seeds/categories are not pooled. Incomplete analysis
requires --allow-incomplete and exits 1; malformed data remain errors. Exclusive
output ownership protects old paths; partial/failed runs cannot imply completion.

### Files added/changed

Added project files:
- docs/SEARCH_PROTOCOL_v1.md
- include/algorithms/detail/search_impl.hpp
- include/algorithms/searching.hpp
- include/benchmark/search_comparisons.hpp
- include/benchmark/search_timing.hpp
- scripts/analyze_search_results.py
- scripts/run_search_matrix.py
- src/algorithms/searching.cpp
- src/benchmark/search_comparisons.cpp
- src/benchmark/search_main.cpp
- src/benchmark/search_timing.cpp
- tests/test_search_benchmark.py
- tests/test_search_timing.cpp
- tests/test_searching.cpp

Changed: CMakeLists.txt (independent search targets and three CTest groups), README
and docs/ALGORITHMS.md, BENCHMARKING.md, EXPERIMENT_PROTOCOL.md, METRICS.md, ROADMAP.md
and AUDIT.md (interfaces/contracts/protocol/commands/results/limitations/status).
All original algorithms/generator/CLIs/tests/Python sorting tools and upstream
source/licenses/provenance are preserved byte-for-byte.

### Actual commands and validation

Commands below all exited 0; per-command JSON retains exact argv/stdout/stderr/UTC
interval/status. Baseline commands precede integration. Initial new algorithm
checks passed; the first engine build emitted five misleading-indentation sites
for both CLI compilations. Those sites were corrected before the first full suites;
subsequent builds emit no compiler warnings. CMake GLOB mismatch messages during
new-source discovery are regeneration notices, not build/test failures.

```sh
cmake --build build/release --parallel 2  # exit 0
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF  # exit 0
ctest --test-dir build/release --output-on-failure -V  # exit 0
build/release/search_counts --output results/raw/search_validation_20261009T173830593675Z/counts_smoke --search all --size 64 --queries 16 --seed 1729 --query-seed 2718 --distribution uniform  # exit 0
cmake --build build/release --parallel 2  # exit 0
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF  # exit 0
ctest --test-dir build/release --output-on-failure -V  # exit 0
python3 scripts/capture_environment.py --build-dir build/release --output results/raw/search_validation_20261009T173830593675Z/release_environment.json  # exit 0
cmake --build build/release --parallel 2  # exit 0
ctest --test-dir build/release --output-on-failure -V  # exit 0
cmake --build build/sanitize --parallel 2  # exit 0
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V  # exit 0
cmake --build build/sanitize --parallel 2  # exit 0
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON  # exit 0
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V  # exit 0
python3 scripts/capture_environment.py --build-dir build/sanitize --output results/raw/search_validation_20261009T173830593675Z/sanitize_environment.json  # exit 0
cmake --build build/release --parallel 2  # exit 0
ctest --test-dir build/release --output-on-failure -V -R '^searching$'  # exit 0
cmake --build build/release --parallel 2  # exit 0
cmake --build build/release --parallel 2  # exit 0
ctest --test-dir build/release --output-on-failure -V -R '^search'  # exit 0
python3 scripts/analyze_search_results.py results/raw/search_validation_20261009T173830593675Z/smoke_matrix --output results/processed/search_smoke_20261009T173830593675Z.json  # exit 0
python3 scripts/run_search_matrix.py --binary build/release/search_benchmark --output results/raw/search_validation_20261009T173830593675Z/smoke_matrix --sizes 0,1,64,1000 --seeds 1729 --query-seeds 2718 --distributions uniform,duplicate_heavy --searches all --categories all --queries 64 --repetitions 5 --warmups 1  # exit 0
python3 results/raw/search_validation_20261009T173830593675Z/verify.py  # exit 0
```

Full Release and ASan/UBSan suites initially passed 18/18 groups. After the final
gap-capacity/parser review, both builds and full suites were repeated and again
passed 18/18. Leak detection was enabled throughout; the historical ptrace issue
did not recur and no leak-disabled rerun was performed. No configure/build/test/
smoke/analysis/verification command failed. Intentional negative tests retain/assert
CLI exits 1, Python argparse exits 2 and failed-child fixture exit 9; they are
temporary validation fixtures, not failed study runs.

New results in each final suite:
- searching: 3,704 input cases and 309,996 public/registry/counted oracle checks;
  exact small counts, first duplicates, unsorted linear and reset/isolation passed.
- search_timing: 72 reproducible configuration cases and 4,266 validated batches;
  categories, mixed ratio, subset RNG independence, duplicate rank, int64 gaps,
  extrema/precondition/stale-answer/exception/wrong-result checks passed.
- search_framework: 12 methods; schemas/escaping, all distributions/seeds, availability,
  invalid arguments/path safety, actual counts CLI, build guard, synthetic statistics,
  partial/tampered data, exclusive summary/regeneration and matrix failure passed.
All 15 preserved sorting/metrics/environment groups also pass, including their
3,590 sorting inputs/98,508 search-reference checks, 220 dataset cases, existing
Quick/PDQ/Tim/Merge/Radix differential suites and 1,296 sorting timing calls.

### Retained smoke and reproducibility

Release matrix: sizes 0,1,64,1000; uniform/duplicate_heavy; dataset seed 1729,
query seed 2718, all three algorithms/all nine policies, 64 queries per available
category, one warm-up/five repetitions. Eight completed configurations; all nine
policies occur where applicable. There are 47 available and 25 explicitly
unavailable category/configuration pairs, 141 summary groups, 705 successful
measured batches and 141 successful warm-ups (846 rows), zero failed/missing trials.
Every row validates all 64 answers: 54,144 total timed query answers, including
warm-ups. A separate 64-key/16-query/all-searchers count smoke produced 384 correct
per-query records without latency; it is not part of timing observations.

Raw bundles: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/search_validation_20261009T173830593675Z/smoke_matrix and counts_smoke.
Processed summary: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/processed/search_smoke_20261009T173830593675Z.json.
verification.json confirms byte-for-byte regeneration to a new temporary file,
raw smoke hashes unchanged, configured source/binary manifests current, normal
timing link free of metrics, and all 534 earlier raw/processed artifact hashes
unchanged. The frozen 1M sorting protocol and all its outputs remain unchanged;
the new search protocol also matches its original saved hash. Environment
manifests and historical/final logs are retained separately. Smoke timings are
actual retained validation observations; no superiority/significance claim.

### Status, limitations and exact next step

Phase 3's array-search/batch-benchmark milestone is complete. Direct individual-
query latency/maxima await timer calibration; large search experiments, search
RSS/allocations, structures and plots have not run. No CUDA or 100M workload;
negative excessive-size arguments were rejected before allocation. Next roadmap
implementation: Phase 4 Skip List, then B-Tree/M-way structures, with first-duplicate
semantics, separate build costs and differential validation. A 1M search study
requires its own frozen protocol/resource review before execution; it is not a
result of this smoke milestone.
