# Phase 4 final audit — 2026-10-09


### Starting state, access and contracts

Read AGENTS.md completely and inspected README, ROADMAP, this audit, ALGORITHMS,
BENCHMARKING, EXPERIMENT_PROTOCOL, METRICS, SEARCH_PROTOCOL_v1, CMake, array-search
interfaces/registry/templates, dataset/query/timing/output code, Python tools and
CTest conventions. pwd confirmed the existing repository; anonymous temporary-file
write/read/delete passed. git status --short exits 128 (no Git metadata); no Git
repository was initialized. Phase 3's three array searches and 18-test suite were
present, and no owned search structures existed. Baseline Release configure/build/
full CTest each exited 0, passing 18/18 with no baseline defect or warning.

New evidence: results/raw/structures_validation_20261009T181402878134Z. Before edits,
696 earlier raw/processed artifacts were SHA-256 inventoried, and all project
sources/tests/tools/docs/vendors backed up in build/structures_review_20261009T181402878134Z.
Historical build-directory test logs were copied separately. The frozen 1M sorting
study and Phase 3 search protocol/results are protected, with all old artifacts.
STRUCTURES_PROTOCOL_v1.md was saved and copied/hashed into PROTOCOL_v1.md/protocol.json
before data-structure implementation; it also freezes the development benchmark
contract before engine implementation.

OrderedIndex maps signed-int32 keys to size_t payloads, using first insertion on
duplicates, optional copied lookup results and unique-key size. No update/deletion,
copy/move or mutable shared state. SkipList owns nodes independently with unique_ptr,
nonowning forward links, 32 levels and explicitly seeded low-bit MT19937-64 promotion
at probability 1/2. BTree uses even maximum-child order M and minimum degree M/2,
preallocated node capacities and top-down median splits. Separate factory names
skip_list,btree_m10,btree_m16,btree_m32,btree_m64 preserve existing registries/APIs.

### Correctness gate and integration

The std::map::emplace oracle follows the documented first-payload contract. Tests
cover empty/singleton/extrema, exhaustive small arrays, seeded distributions,
ascending/descending/shuffled/duplicate-heavy insertions, repeated keys/lookups,
zero/SIZE_MAX payloads, size, invariant traversals, seed isolation and disabled
copy/move. Public fixtures insert 10,000 keys to demonstrate multiple levels and
root/nonroot splits. No allocation-failure injection or concurrent mutation test
is claimed. Ownership review checks exception-safe node reservation before split
mutation and iterative Skip List destruction. B-tree destruction depth is balanced.

Before benchmark integration, fresh full Release and ASan/UBSan suites passed
19/19 groups, leak detection enabled. New results in both: 6,635 structure/input
cases, 1,239,680 differential insertion attempts, 3,218,705 map-oracle lookups,
75,665 invariant validations. Separate public diagnostic fixtures observed 14
Skip List levels and 14,875 splits across orders 4/10/16/32/64; these are actual
coverage evidence, not comparison counts or timings.

The new engine reuses the existing generator, exact Phase 3 query plans, timing
clock/output helpers, configured source/compiler metadata and Python statistics.
Original insertion order is retained; first sorted ranks are precomputed outside
timing so duplicate payloads match array-search answers independently of order.
Each round builds a fresh structure, validates all contents/invariants, and then
looks up each eligible batch. Construction and lookup rows remain separate;
constructor/RNG setup/allocation/inserts belong to build timing, destruction does
not. All answers and full payload/invariant checks are outside timers. Normalized
batch averages are not individual latency. No counters/RSS/isolation measurements.
Planning guard 512*N+128*queries*9 is not measured memory or a hard RSS limit.

### Failures and corrections retained

The first structure build succeeded but emitted a misleading-indentation warning
and an optional-comparison maybe-uninitialized warning in the test oracle. Separate
statements and direct presence/payload checks corrected both; no warning suppression.
Reviewed subsequent builds have no warnings.

The first full engine Release CTest (reviewed_release_ctest) exited 8: 20/21 groups
passed, structure_framework failed because argparse accepted --size as an
abbreviation of --sizes. Both new Python tools now disable option abbreviations.
The corrected full Release suite and fresh full sanitizer suite passed 21/21;
no sanitizer failure, ptrace limitation or leak-disabled retry occurred. Intentional
negative fixtures assert CLI/tool exits 1/2 and a child stub's exit 9; these are
passing test assertions, not retained smoke-study failures. Git status exit 128
is the expected missing-metadata inspection failure. No failed check is omitted.

### Files added/changed

Added: docs/STRUCTURES_PROTOCOL_v1.md; include/structures/ordered_index.hpp,
skip_list.hpp,btree.hpp; src/structures/skip_list.cpp,btree.cpp,registry.cpp;
include/benchmark/structure_timing.hpp; src/benchmark/structure_timing.cpp,
structure_main.cpp; scripts/run_structure_matrix.py,analyze_structure_results.py;
tests/test_structures.cpp,test_structure_timing.cpp,test_structure_benchmark.py.
Changed: CMakeLists.txt (independent structure libraries/executable, three tests),
README and docs/ALGORITHMS.md,BENCHMARKING.md,EXPERIMENT_PROTOCOL.md,METRICS.md,
ROADMAP.md,AUDIT.md. Existing sources, tests, Python tools, vendor notices/licenses,
array-search/sort APIs/CLIs and std_sort default are intended to remain byte-identical;
final manifests/patch and integrity checks below establish the actual preservation.

### Final fresh validation and exact commands

All commands below ran from the repository root. Each exited 0. Each configure
and build succeeded, and neither final build emitted compiler warnings.

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

Final Release passed 21/21 groups (4.24 seconds); final ASan/UBSan passed 21/21
(37.56 seconds). Leak detection was enabled; the historical ptrace limitation did
not recur. There was no leak-disabled retry. All 18 existing groups passed without
changing their sources/tests. New groups in both builds:

| Test | Actual result |
| --- | --- |
| structures | 6,635 inputs; 1,239,680 insertion attempts; 3,218,705 map-oracle lookups; 75,665 invariant validations; separate diagnostic fixtures observed 14 levels and 14,875 splits |
| structure_timing | 72 reproducible workloads and 8,190 validated build/lookup rows; failures, rank/query tampering, extrema and resource checks passed |
| structure_framework | 11 Python methods covering schema/escaping, reproducibility, safety, failed/missing records, malformed records/matrices, strict arguments and statistics/regeneration |

The commands/ directory retains every recorded configure/build/test invocation,
stdout/stderr, exact argv, cwd, timestamps and exit status, including intermediate
checks and the corrected exit-8 CTest failure. COMMANDS.md is the complete command
index; final Release/sanitizer LastTest.log copies are fresh evidence, while the
historical copies are explicitly named separately. An initial final-documentation
patch failed because its context did not match and applied no changes; a corrected
patch succeeded. No validation failure was suppressed.

### Retained development smoke and analysis

Preflight verified prior hashes, an absent output path and resources. Linux
6.18.7 with 12 logical CPUs, available memory 4,255,592 kB and free disk
134,350,553,088 bytes were recorded at that check. Maximum planning allowance for
N=1000/Q=64 was 585,728 bytes, not measured memory. Address-space limit was
unlimited; background load was recorded, and no affinity/frequency/cache/thermal
control was claimed. Environment manifests retain actual compiler, CMake, OS,
RAM, limits, tool hashes and executable hashes; unavailable fields are not invented.

```sh
python3 scripts/capture_environment.py --build-dir build/release --output results/raw/structures_validation_20261009T181402878134Z/release_environment.json
python3 scripts/capture_environment.py --build-dir build/sanitize --output results/raw/structures_validation_20261009T181402878134Z/sanitize_environment.json
python3 scripts/run_structure_matrix.py --binary build/release/structure_benchmark --output results/raw/structures_validation_20261009T181402878134Z/smoke_matrix --sizes 0,1,64,1000 --seeds 1729 --query-seeds 2718 --structure-seed 1729 --distributions uniform,duplicate_heavy --structures all --categories all --queries 64 --repetitions 5 --warmups 1 --memory-limit-mib 256 --distinct 16
python3 scripts/analyze_structure_results.py results/raw/structures_validation_20261009T181402878134Z/smoke_matrix --output results/processed/structures_smoke_20261009T181402878134Z.json
python3 results/raw/structures_validation_20261009T181402878134Z/verify.py
```

Each command exited 0; the recorder wrapper also exited 0. All eight configurations
completed with all five registry entries. Actual counts: 200 measured build
successes, 1,175 measured lookup successes, 275 warmups, 1,650 total rows; zero
failed or missing trials/warmups. All 275 groups retain separate construction and
lookup/category statistics: median/mean/sample standard deviation/min/max in ns,
with normalized lookup ns/query. No pooling of incompatible categories or removal
of outliers. 47 eligible category/configuration pairs produced 3,008 query records;
25 unavailable pairs retain reasons and no invented timings. All 90,240 lookup
answers including warmups passed validation.

The processed summary is results/processed/structures_smoke_20261009T181402878134Z.json.
verify.py reran the analyzer into an exclusive temporary path, exit 0, and compared
summary bytes successfully. All 83 smoke files matched the pre-analysis SHA-256
checkpoint. Query CSV bytes and reference-input hashes match retained Phase 3
smoke inputs, demonstrating identical logical workloads; original insertion order
is also recorded. These small timings validate the pipeline, not superiority.

### Integrity, final review and milestone status

verification.json confirms all 696 earlier raw/processed artifacts unchanged,
including the frozen 1M sorting study, all existing implementations/tests/tools/
vendors outside the eight intended project-file edits unchanged (76 protected
files), and the old sort_benchmark executable byte-identical. Source hashes match
the final Release build; timing links contain no counting libraries. The pre-code
structures protocol and retained copy both retain SHA-256
c2b414fb1322dbbcc56cff65adeae4c2a8da5743de26c6ecd26905d70bd0a61f.

FINAL_AUDIT.md, file_changes.json, changes.patch, final_source_manifest.json and
final_review.json under the new evidence directory retain the final review and
actual added/changed files without needing Git. Earlier artifacts were neither
modified nor regenerated. This Phase 4 insertion/lookup milestone is complete.
No large structure study, CUDA, 100M experiment, structure comparison counts,
measured structure memory or direct individual-query maximum is claimed. No
allocation-failure injection or concurrent mutation support. Update/deletion and
copy/move remain deliberately unsupported by the frozen contract. Larger studies
need a separate frozen protocol/resource review; uncontrolled shared-machine
smoke timings cannot support statistical significance or a universal ranking.

Exact next roadmap milestone: Phase 5 full experiment orchestration and
reproducible plots with variability, using retained raw data and separate derived
paths. Larger search/structure experiments remain unrun.

Evidence is in this directory. See COMMANDS.md/commands_index.json, verification.json, final_review.json, file_changes.json, final_source_manifest.json and changes.patch.
