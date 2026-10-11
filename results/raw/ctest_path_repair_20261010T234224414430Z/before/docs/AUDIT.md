# Initial repository audit

## Inventory before changes

The only existing file was `AGENTS.md`, read in full. README.md,
docs/ROADMAP.md, docs/EXPERIMENT_PROTOCOL.md, CMakeLists.txt, source, tests,
scripts, third-party implementations, and result artifacts were absent.
There is no `.git` directory: `git status --short` failed with "not a git
repository". Version-control history and a diff against an original commit
therefore cannot be recorded. No existing algorithm defects could be assessed.

The first attempted command,
`cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release`, failed because no
CMakeLists.txt existed. No pre-existing tests were available to execute.

## Phase 0 changes and validation

Added a portable C++17 CMake library, an explicitly named std::sort baseline,
CTest integration, checks active in Release builds, and Python environment
capture. No custom algorithm has been added at this phase.

Release configure/build succeeded with GNU C++ 13.3.0 and CMake 3.28.3.
`ctest --test-dir build/release --output-on-failure -V` passed 2/2 tests:

- C++: 310 full-vector comparisons against std::stable_sort, including empty,
  singleton, sorted, reverse, duplicates, negative and int32 boundary inputs.
- Python: three tests for manifest JSON round-trip, overwrite rejection,
  unavailable-tool recording, and invalid CMake-cache rejection.

`results/raw/baseline_environment_phase0.json` records the actual compiler,
flags, OS, CPU probe, memory snapshot, exact capture invocation and CMake cache.
The script creates files exclusively and refuses to overwrite raw output.
The recorded workload is null because this was not a performance experiment.

## Remaining work

All required custom sorters, searches, search structures, performance metrics,
CSV analysis, OpenMP, CUDA, learned index, research report and scale experiments
remain pending. No GPU or 100M run was attempted. Installed toolchains are
sufficient to continue the CPU correctness phase; missing Git metadata does
not block building or testing.

Next smallest step: deterministic dataset generation with regression fixtures
and cross-distribution differential sort tests, then bounded project QuickSort
after the correctness core is ready.

## Phase 1 continuation — 2026-10-09

The earlier read-only sessions did not modify files or rebuild tests. Their
direct executable checks and syntax-only proposed test were historical evidence,
not execution of the new regressions. The initial four-test Release/sanitizer
logs have been copied exclusively to a new results/raw/validation_* directory
before CTest reuses its build-directory logs.

This continuation verified workspace write access by creating an anonymous
temporary file in the repository, writing, reading and automatically deleting
it. No permission changes were made. `pwd`, `git status --short`, and
`rg --files --hidden -g '!.git/**' -g '!build/**' -g '!**/__pycache__/**'` were
executed; Git still reports "not a git repository".

Before freezing fixtures, the current generator was compiled with:

```sh
c++ -std=c++17 -Wall -Wextra -Wpedantic -Iinclude build/fixture_check/probe.cpp src/datasets/generator.cpp -o build/fixture_check/probe
```

The probe returned 15 vectors (five seeds, zero/one/five swaps). An independent
inline Python MT19937-64 initialization/twist/tempering calculation matched all
15 complete vectors. The generator implementation and its v1 contract were not
changed. Exact one-swap vectors now test the first/last self-swaps, endpoint and
interior pairs and another size; a five-swap vector catches incorrect requested
swap counts. Empty/singleton inputs are checked with size_t's maximum swap count.
CLI tests now check the complete schema, repeated options, malformed values,
full domain cardinality and a vector length error before allocation.

Fresh commands executed, each with exit status 0:

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

Both full CTest suites passed 4/4 groups. The newly changed C++ dataset test was
compiled, linked and executed in both builds. Results in each configuration:

- baselines: 3,590 full-vector differential sort cases and 98,508 linear-oracle
  search checks passed.
- datasets: 220 distribution/size/seed cases, five exact one-swap fixtures with
  zero-swap baselines, one five-swap fixture, maximum-request empty/singleton
  checks, and all existing fixtures/configuration tests passed.
- environment_manifest: all three Python tests passed.
- cli: all six Python tests passed, including the new schema, repeats and
  oversized-vector checks.

Leak detection was enabled in this fresh sanitizer run. The historical ptrace
limitation did not recur; no detect_leaks=0 retry was needed. There were no build
or test failures in Phase 1. Per-command output and exit status are preserved in
results/raw/validation_20261009T150941468271Z/phase1_*.json, labeled as correctness
validation rather than benchmark results. With saved documentation and these
passing suites, Phase 1 is complete before QuickSort implementation begins.

## Bounded QuickSort continuation

After Phase 1 passed, added project QuickSort with copied median-of-three pivots,
three-way half-open partitioning, a 2*floor(log2(N)) budget and make_heap/sort_heap
fallback on exhausted subranges. Only the smaller strict partition recurses.
The production observer has no counters; internal templates expose explicit
budget/observer hooks for correctness tests. No existing sorting registry was
present, so a two-entry registry was added and used by `--sort` selection and the
existing differential tests. std_sort remains the default.

Fresh commands executed, each with exit status 0:

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

The initial QuickSort Release build emitted a range-loop-copy warning in its
test. It was fixed by binding the loop element by const reference. After that
fix and additional sibling-budget/sentinel checks, Release build and full CTest
were repeated with the same commands above; the final build had no warnings.
Sanitizer validation ran on that final code.

Both final full suites passed 5/5 groups:

| CTest group | Actual coverage/result in each configuration |
| --- | --- |
| baselines | 3,590 input cases, with both registry entries checked against full output; 98,508 linear-oracle search checks |
| environment_manifest | Three Python tests passed |
| datasets | 220 distribution/size/seed cases checked for both sorters; exact swap and existing fixtures passed |
| cli | Seven Python tests passed, including QuickSort selection across all distributions |
| quicksort | 3,718 input cases checked through public and observed paths; fallback/stack checks passed |

The dedicated QuickSort cases include 14 explicit edges, 3,280 exhaustive small
arrays, 400 seeded distribution/size cases, and 24 adversarial/all-equal cases.
Heapsort was actually called and asserted: zero budget yielded one whole-range
fallback; one budget yielded one subrange fallback; balanced children yielded
two; a sentinel-bounded range yielded one; normal-budget adversarial tests
yielded 618 fallback calls. Full reference equality passed in every case.

ASan/UBSan and LeakSanitizer were enabled; the historical ptrace limitation did
not recur. There were no fresh build/test failures, apart from the unchanged
Git-status failure described above. Raw per-command records are in
results/raw/validation_20261009T150941468271Z/quicksort_*.json; final environment
manifests include the actual compiler/flags and expanded source list.

Phase 1 is complete; this QuickSort portion of Phase 2 is implemented/tested/
documented. Phase 2 as a whole remains in progress. No benchmark measurement,
CUDA, OpenMP, learned-index or 100-million-element execution was attempted.
Next smallest implementation step: integrate upstream PDQSort with pinned source,
license/attribution and full differential tests. Timsort and metric collection
remain pending after that.

## PDQSort integration — 2026-10-09

The source, sorting registry, CLI, CMake and tests were inspected before edits.
The QuickSort implementation and test bytes matched the prior validated SHA-256
manifest. An anonymous temporary-file write/read/delete check confirmed access.
Git metadata is still absent in the project directory. Earlier mutable CTest
logs were copied exclusively into a new raw validation directory before reuse;
they are historical evidence, separate from the fresh runs below.

### Verified upstream provenance

- Repository: https://github.com/orlp/pdqsort (Orson Peters' official C++ source).
- Exact revision: b1ef26a55cdb60d236a5cb199c4234c704f46726.
- License: Zlib; original license.txt and pdqsort.h notices retained in full.
- Local upstream modifications: none. The project adapter is separate.
- Verification: clean clone, committed Git blobs and revision-qualified HTTPS
  downloads of both files were byte-identical. UPSTREAM.json records URLs,
  revision, author, retrieval time and SHA-256 hashes. third_party/pdqsort/README.md
  provides attribution, local-modification status and checkout instructions.

Retrieval/identity commands executed successfully:

```sh
git clone https://github.com/orlp/pdqsort.git build/pdqsort-upstream
git -C build/pdqsort-upstream remote get-url origin
git -C build/pdqsort-upstream rev-parse HEAD
git -C build/pdqsort-upstream status --short
git -C build/pdqsort-upstream log -1 --format=fuller
```

An inline `python3 -B -` verification script read each committed blob via
`git -C build/pdqsort-upstream show b1ef26a55cdb60d236a5cb199c4234c704f46726:pdqsort.h`
and the corresponding license.txt command, fetched both revision-qualified raw
HTTPS URLs recorded in UPSTREAM.json, compared the three byte sequences, checked
the retained notices, calculated SHA-256 and exclusively wrote the vendor files.
It exited 0. No retrieval/access dependency blocked integration.

### Integration and fresh validation

Added mab::pdq_sort(Values&) as a direct ::pdqsort(begin,end) adapter, the pdq_sort
registry entry and CLI choice. The default std_sort, JSON schema and existing
algorithms remain unchanged. With signed int32/std::less under C++17 the pinned
upstream code automatically selects its branchless partition specialization.
The original header is compiled with normal project warnings enabled, not a
warning-suppressed system include. CMake uses vendored files without downloads.

Exact fresh build/test commands, each exit 0:

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

Both full suites passed 6/6 groups; builds emitted no compiler warnings:

| CTest group | Actual result in each configuration |
| --- | --- |
| baselines | 3,590 input cases, now checking all three registry entries; 98,508 search checks passed |
| environment_manifest | Three Python tests passed |
| datasets | 220 distribution/size/seed cases for all three sorters; all swap/validation fixtures passed |
| cli | Nine Python tests passed; PDQSort exercised on all distributions and sizes 0,1,24,128,1000; invalid names rejected |
| quicksort | Existing 3,718 cases passed unchanged; normal-budget adversarial fallback count remained 618 |
| pdqsort | 4,027 dedicated cases passed through both public and registry paths |

PDQSort's dedicated cases comprise 15 explicit boundary/negative/extreme inputs,
3,280 exhaustive small arrays, 600 cases across four distributions/five seeds/
30 sizes, and 132 adversarial/all-equal patterns. Each checks full equality to
std::sort, including multiset preservation. No upstream implementation hook or
instrumentation was added, and PDQSort internal fallback coverage is not claimed.

LeakSanitizer stayed enabled; the historical ptrace limitation did not recur.
No leak-disabled retry was run. Validation evidence is preserved separately from
prior results under results/raw/pdqsort_validation_20261009T152406222351Z,
including per-command exit status/stdout, historical/final logs, source hashes,
upstream provenance and final compiler/flags/environment manifests.

The only inspection failure was project Git status (missing Git metadata).
No retrieval/build/test failures occurred. Validation covers the current GNU
toolchain/Linux environment; other toolchains/platforms were not executed.
The PDQSort integration is complete; Phase 2 overall is not complete. Genuine
Timsort, extra sorters and comparison/memory/timing CSV metrics remain pending.
Next step: integrate a genuine, pinned upstream Timsort with license/attribution
and the same correctness validation. No benchmarking, CUDA or 100M run occurred.

## Timsort integration — 2026-10-09

### Workspace and baseline

Before editing, pwd, file inventory, AGENTS.md, README, protocol, this audit,
roadmap, algorithm documentation, CMake, sorting registry, CLI and tests were
reviewed. An anonymous temporary-file write/read/delete check passed. Project
Git metadata is absent: git status --short exited 128 with "not a git repository".
No permissions or access controls were changed. Existing sources were backed up
under build/timsort_review for comparison; earlier CTest logs were copied with
exclusive creation into the new evidence directory. Historical logs are not
used as proof that the new integration passes.

Before integrating Timsort, these commands each exited 0:

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
```

The existing suite passed 6/6 groups: 3,590 sorting inputs, 98,508 search checks,
220 dataset combinations plus fixtures, three environment tests, nine CLI
methods, 3,718 QuickSort cases (618 normal-budget adversarial fallbacks) and
4,027 PDQSort cases. No baseline defect or compiler warning was found.

### Source selection, license and verification

Canonical repository: https://github.com/timsort/cpp-TimSort, formerly gfx/cpp-TimSort.
Selected exact commit: 99b612d9826e8387a30008f2b21be206181ad890 on the C++11-compatible
2.x.y branch. Current upstream 3.x requires C++20; upstream states that older
branches are not actively maintained. This choice preserves the project's
C++17 interface. Header macros say 2.1.0, but this commit is distinct from the
v2.1.0 tag; the commit identity is the dependency pin.

Commands executed successfully (exit 0):

```sh
git clone https://github.com/timsort/cpp-TimSort.git build/timsort-upstream
git -C build/timsort-upstream checkout --detach 99b612d9826e8387a30008f2b21be206181ad890
```

Revision and committed contents were verified using rev-parse HEAD and git show
at the selected commit. An inline python3 verification/vendoring script fetched
the revision-qualified raw HTTPS URLs recorded in UPSTREAM.json, asserted that
download bytes, Git blobs and checkout files were identical, computed SHA-256,
and exclusively created the vendor files. It exited 0. The standalone LICENSE
and complete header license/attribution were reviewed and retained unchanged.

| Vendored file | SHA-256 |
| --- | --- |
| third_party/timsort/include/gfx/timsort.hpp | a5cf0f0f61d92a62cf14528d1969a236db587b95678b088b5e38833d9865e9c9 |
| third_party/timsort/LICENSE | 210f3341e9e04dc3004f416ae0e28dc7e8eaa84528c5966661186a1b512f34c3 |

License: MIT. Copyright notices for Fuji, Goro/gfx, Morwenn and Igor Kushnir
remain in the header; the standalone license retains the original author notice.
Local upstream modifications: none. The local adapter is separate and calls
gfx::timsort(begin,end); no diagnostics or comparison counters were added.
No build-time network access, Catch2 or other upstream development dependencies
are required. The vendored include is private and uses normal warning flags.

Browser attempts to open an alternative repository (tvanslyke/timsort) and the
selected revision's tree URL returned tool fetch errors. Canonical repository,
commit and license pages were accessible, and Git/raw-HTTPS retrieval succeeded;
these browser failures did not block or substitute for provenance verification.
An exploratory rg command with no matches exited 1; this was a search result,
not a failed build or test.

### Saved changes and review

- include/algorithms/timsort.hpp and src/algorithms/timsort.cpp: public int32
  adapter to genuine upstream Timsort, including empty/singleton ranges.
- include/algorithms/sorting.hpp and src/algorithms/sorting.cpp: fourth registry
  entry tim_sort; std_sort remains first and the default.
- src/main.cpp: help advertises --sort tim_sort; existing registry dispatch,
  unknown-name errors and eleven-field JSON schema are preserved.
- CMakeLists.txt: new adapter, private vendor include and timsort CTest group.
- tests/test_timsort.cpp: deterministic full-vector differential checks through
  public and registry paths, including natural-run/merge-oriented patterns.
- tests/test_cli.py: Timsort selections, help/repeated options, and invalid names;
  all earlier methods are retained.
- third_party/timsort: unchanged header and LICENSE, plus local README.md and
  UPSTREAM.json with provenance/hashes and adapter details.
- README.md, docs/ALGORITHMS.md, docs/ROADMAP.md and this audit: source identities,
  interface, actual validation and remaining milestones.

Review compared files against the initial backup because project Git metadata
is unavailable. Existing QuickSort, PDQSort, generator, baseline/dataset tests,
and dedicated QuickSort/PDQSort tests are byte-for-byte unchanged. PDQSort's
original recorded source/license hashes also still match.

Source review covered early exits, half-open ranges, minrun rounding, partial
tails, forward/backward merge cursors, galloping offsets, run-length arithmetic,
and the deeper merge-stack invariant. Sort keys are compared/moved without key
arithmetic. No demonstrated defect required patching upstream. The current
compiler uses a C++17 default dialect; CMake requires at least C++17 and disables
extensions. Actual compile commands/manifests include the private include path,
Release -O3 -DNDEBUG, -Wall -Wextra -Wpedantic, and sanitizer flags where enabled.

An explicit strict-C++17 syntax check also exited 0 without warnings (this check
is separate from the compiled/executed full suites):

```sh
c++ -std=c++17 -Wall -Wextra -Wpedantic -Iinclude -Ithird_party/timsort/include -fsyntax-only src/algorithms/timsort.cpp
```

### Fresh integration validation

After source/test changes, all six commands below exited 0:

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

Both full suites passed 7/7 CTest groups; no compiler warnings were emitted.

| CTest group | Actual result in both configurations |
| --- | --- |
| baselines | 3,590 full-vector inputs across all four registry sorters; 98,508 linear-oracle search checks passed |
| environment_manifest | Three Python tests passed |
| datasets | 220 distribution/size/seed combinations across all four sorters, exact swap and other fixtures passed |
| cli | Ten Python methods passed, including 36 Timsort distribution/size selections and invalid algorithm names |
| quicksort | Existing 3,718 cases and all fallback checks passed; normal-budget adversarial fallback total 618 |
| pdqsort | Existing 4,027 full-vector cases passed through public/registry paths |
| timsort | 4,149 inputs passed through both public and registry paths against std::sort |

Timsort's dedicated count comprises 15 explicit edges, 3,280 exhaustive small
arrays, 600 distribution/seed/size combinations, 132 general patterns, 24 varied
run layouts and 98 unequal/overlapping two-run patterns. Largest dedicated input
size is 10,000. Tests target natural runs, short tails and merge behavior without
claiming specific internal branch coverage. Tests remain active in Release.
Stability of decorated records is outside the public signed-int32 API.

ASan/UBSan and LeakSanitizer passed with leak detection enabled. The previously
reported ptrace limitation did not recur; no leak-disabled retry was executed.
No fresh configure/build/test failures or unresolved correctness errors occurred.
Validation covers this GNU/Linux environment; Windows, macOS and other toolchains
were not run. The unmaintained older upstream branch is a documented dependency
limitation, not a hidden upgrade to C++20.

Evidence is exclusively saved under
results/raw/timsort_validation_20261009T153302249194Z: per-command output/exit status,
separate historical logs, final CTest logs, provenance/source review, and these
environment snapshots (both commands exited 0):

```sh
python3 scripts/capture_environment.py --build-dir build/release --output results/raw/timsort_validation_20261009T153302249194Z/release_environment.json
python3 scripts/capture_environment.py --build-dir build/sanitize --output results/raw/timsort_validation_20261009T153302249194Z/sanitize_environment.json
```

The final source-preservation/provenance review command exited 0 and exclusively
saved the existing-file diff, final source hashes, provenance and CTest log copies:

```sh
python3 results/raw/timsort_validation_20261009T153302249194Z/review_sources.py
```

Timsort integration is complete with saved code/tests/documentation and passing
fresh full suites. Phase 2 overall remains in progress: additional Merge/Radix
baselines, separate comparison counting, memory reporting and repeatable timing
CSV infrastructure are unfinished. Next milestone: separate comparison-count
instrumentation and documented memory reporting, before performance experiments.
No benchmark measurements, CUDA execution or 100-million-element runs occurred.

## Comparison instrumentation and memory reporting — 2026-10-09

### Inspection and baseline

Read AGENTS.md, README, roadmap, audit, algorithm/protocol documentation, CMake,
sorting interfaces/registry/adapters, QuickSort internals, upstream comparator
interfaces and existing tests before editing. No timing/output infrastructure
existed beyond the correctness JSON CLI and raw validation records. pwd confirmed
the project location; an anonymous temporary write/read/delete check succeeded.
git status --short exited 128 because project Git metadata remains absent.
No access controls were changed. Sources/docs/tests/vendors were backed up under
build/metrics_review; prior CTest logs were exclusively copied as historical
evidence before the build directories were reused. Vendor provenance hashes
matched their pinned revisions before edits.

The following baseline commands each exited 0 before feature changes:

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
```

All seven previous groups passed: 3,590 sorting inputs, 98,508 search checks,
220 dataset combinations and fixtures, three environment tests, ten CLI methods,
3,718 QuickSort inputs with all fallback assertions (normal-budget total 618),
4,027 PDQSort inputs and 4,149 Timsort inputs. No baseline defect was demonstrated.

### Design and saved changes

The separate mab_metrics library and sort_metrics executable contain instrumented
adapters and process-memory reporting. algorithm_benchmark still links only
mab_core; its source, CLI, eleven-field JSON and registry are unchanged. std_sort
remains default in both executables. No timer or performance matrix was added.

key_less_than_v1 counts each executed signed-int32 less-than predicate once,
including false/equal results, pivot selection and heap/merge work. It excludes
swaps, assignments, iterator/bookkeeping tests, generation and verification.
Every sort initializes its own uint64 counter; comparator copies share only that
call's local state. Overflow throws before wrapping. All four current algorithms
support the same counting unit; counts are not machine instructions or timing.

QuickSort's internal template was parameterized by a comparator, defaulting to
std::less<Key>. The shared pivot/partition/budget policy is preserved and the
comparator reaches recursive children and both heap calls. Existing public
adapters and observer tests are unchanged. Normal execution has no counter.
PDQSort counting explicitly uses its public branchless comparator entry point
because ordinary custom-comparator dispatch would silently select another policy.
Timsort/std::sort use comparator interfaces without source modifications. Timsort
audit comparisons are excluded; enabling that macro rejects the counted build.
Checked-library configurations need separate review; current flags do not enable
those modes. Upstream/library exact counts are not hardcoded across platforms.

Linux memory uses getrusage(RUSAGE_SELF).ru_maxrss in KiB, checked conversion to
bytes. It is a process-lifetime peak, sampled after counted sorting and before
validation vectors. It can include generation, input/output, runtime, allocator,
instrumentation, sanitizer and execution-history effects; it does not isolate
algorithm workspace. Unsupported platforms return unsupported/null, never zero.
Measurement errors report errno/null in a partial record and exit 1. No algorithm
temporary-buffer allocation measurement or theoretical-to-measured substitution
was implemented. METRICS.md cites the Linux API documentation and defines scope,
units, sample point and all 15 top-level/seven nested JSON fields.

Files changed/added:

- CMakeLists.txt: separate metrics library/executable and four new CTest groups.
- include/algorithms/detail/quicksort_impl.hpp: shared comparator forwarding,
  preserving default operation and observer seam.
- include/benchmark/comparisons.hpp, detail/counting_less.hpp,
  src/benchmark/comparisons.cpp: counted registry and run-local predicates.
- include/benchmark/memory.hpp, src/benchmark/memory.cpp, memory_json.cpp:
  platform-specific peak RSS, unsupported/error status and validated formatting.
- src/benchmark/metrics_main.cpp: separate metric CLI, configuration/provenance
  fields, normal/reference agreement and explicit partial memory-failure records.
- tests/test_comparisons.cpp: exact project counts, comparator copy/isolation/
  overflow, repeated/interleaved runs, differential data and heap forwarding.
- tests/test_memory.cpp: synthetic format/error fixtures plus real and separately
  compiled unsupported probes; no actual kernel failure is induced.
- tests/test_metrics_cli.py: seven schema/configuration/error/repetition methods.
- README.md, docs/ALGORITHMS.md, docs/EXPERIMENT_PROTOCOL.md, docs/METRICS.md,
  docs/ROADMAP.md and this audit: definitions, methodology, limits and real status.

### Fresh build and test results

Each of the following commands exited 0:

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

Full Release and Debug ASan/UBSan suites both passed 11/11 groups. Neither build
emitted compiler warnings. Leak detection was enabled and the historical ptrace
failure did not recur; no leak-disabled retry was executed.

| CTest group | Actual result in each configuration |
| --- | --- |
| baselines | 3,590 full-vector sorting inputs and 98,508 search checks passed |
| environment_manifest | Three Python tests passed |
| datasets | 220 combinations plus all existing swap/validation fixtures passed |
| cli | Ten existing Python methods passed unchanged |
| quicksort | 3,718 existing inputs and all fallback assertions passed; adversarial fallback total still 618 |
| pdqsort | 4,027 existing public/registry cases passed |
| timsort | 4,149 existing public/registry cases passed |
| comparisons | 1,404 inputs across all four sorters, repeated/interleaved reset, six exact QuickSort fixtures, comparator copy/isolation/overflow and counted heap fallback passed |
| memory | Supported/zero/error/unsupported synthetic JSON fixtures, four inconsistent reports and repeated real Linux probes passed |
| memory_unsupported | Same fixture tests and repeated probes compiled through the actual unsupported implementation branch passed |
| metrics_cli | Seven Python methods passed; 80 sorter/distribution/size configurations repeated twice, defaults, exact equal-key QuickSort fixture, invalid inputs/help/bounds/repeated options |

Comparison inputs comprise 11 explicit edges, 1,093 exhaustive arrays of lengths
0..6 over {-1,0,1}, 252 four-distribution/three-seed/21-size combinations and
48 patterns. Largest new counted input size is 4,096. For each input every sorter
is checked against production and std::sort, repeated, followed by an empty run,
interleaved with other sorters and repeated again. The forced zero-budget heap
test compares counting against an independent local comparator over the same
STL heap calls. This asserts forwarding, not a portable fixed STL count.

Memory format values (including 4096 bytes and errno 22) are synthetic fixtures,
not measured RSS. Real probes assert unit/high-water properties without assuming
a fixed value. The unsupported branch is tested on Linux through a test-only
compile definition; this is not Windows/macOS execution. Actual getrusage syscall
failure is not induced; error-object formatting is tested with a fixture.

A separate metric smoke command also exited 0:

```sh
build/release/sort_metrics --sort quick_sort --size 2 --distribution duplicate_heavy --distinct 1
```

It reported seven actual key comparisons and a Linux process RSS sample. The raw
sample is preserved as returned, without interpreting the process high-water
mark as two-element sorting workspace or a comparative memory experiment.

### Evidence, failures and remaining work

New evidence was exclusively created under
results/raw/metrics_validation_20261009T154659316368Z. Historical logs are distinct
from fresh per-command records. Source/provenance review, final logs and manifests
are preserved separately; prior raw evidence was not overwritten. Environment
capture commands both exited 0:

```sh
python3 scripts/capture_environment.py --build-dir build/release --output results/raw/metrics_validation_20261009T154659316368Z/release_environment.json
python3 scripts/capture_environment.py --build-dir build/sanitize --output results/raw/metrics_validation_20261009T154659316368Z/sanitize_environment.json
```

The project Git-status failure (128) was expected because metadata is absent.
One documentation apply_patch was rejected for a mismatched protocol-file
context before any changes were applied; a follow-up inspection exited 2 because
METRICS.md was not yet created. The corrected patch was applied successfully.
There were no configure/build/test/sanitizer failures or suppressed diagnostics.

Existing production registry, CLI, dataset implementation, algorithm adapters and
all earlier test files were preserved byte-for-byte. All vendor files, licenses,
attribution and provenance are unchanged. The QuickSort internal comparator seam
is the only changed production implementation file and all prior observer/fallback
tests still pass. Normal executable linkage excludes the metrics library.

Validation covers the current GNU/Linux environment. Process RSS is not algorithm
isolation and cannot be reset; sanitizer RSS is not a production-memory baseline.
Other memory platforms and temporary-buffer allocation metrics remain unsupported.
The older Timsort branch maintenance limitation is unchanged. No performance
benchmarking, CUDA workload or 100-million-element input was executed.

This comparison/memory milestone is complete with saved code, tests, definitions
and passing fresh suites. Phase 2 overall remains in progress. Next milestone:
implement repeatable Release timing/CSV infrastructure with identical inputs,
repetitions, environment provenance and checks outside timing. Optional Merge/Radix
baselines and measured experiment collection remain pending.

## Reproducible sorting benchmark engine — 2026-10-09

### Inspection and baseline

Read AGENTS.md, roadmap, audit, README, protocol, algorithm documentation, CMake,
registry, dataset generator, metrics interfaces and existing tests before edits.
pwd confirmed the project directory. A temporary write/read/delete check passed;
git status --short exited 128 because project Git metadata is still absent.
Existing sources/tests/docs/vendors/scripts were copied to build/benchmark_review,
and earlier CTest logs were exclusively saved as historical evidence. Upstream
source/license hashes matched their provenance records. No algorithms or generator
behavior needed baseline repair.

Before adding features, these commands each exited 0 and all 11 existing CTest
groups passed freshly:

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
```

### Architecture and protocol

Added mab_timing and sort_benchmark, linked only to production mab_core. Neither
comparison counters nor process-memory probes enter primary timing. Existing
algorithm_benchmark, sort_metrics, registries, algorithms and dataset generator
are unchanged. std_sort remains the single-run default; the matrix selects all
four existing algorithms. The benchmark-only sorted distribution reuses
nearly_sorted generation with zero swaps, preserving generator-v1 compatibility.

sort_timing_v1 is fully specified in docs/BENCHMARKING.md. One warmup and five
measured repetitions are default per algorithm/configuration. Immutable original
input is copied into preallocated working storage before each call. Only the
normal sort call is bracketed by steady_clock timestamps, converted to integer
nanoseconds. Generation, copies, reference sorting, full-vector validation,
metadata and CSV output are outside timing. Sort-owned allocation is included.
Algorithm order rotates by seed offset and trial, recorded explicitly.

The raw 28-field CSV includes identity/configuration, ordered input fingerprint,
phase/trial/order, timing/unit, correctness/status/error and compiler/build/platform
fields. Sidecars record argv, clock period, planning limits, source SHA-256,
upstream provenance, CMake cache and available compile commands. Matrix metadata
adds OS/CPU/RAM/tool probes, exact child commands/exit statuses and executable hash.
Unavailable platform/Git information is not invented. CMake-configured flags are
labeled as settings; effective options are in compile_commands.json.

Exclusive directory creation prevents overwrites. Raw data is flushed per row;
COMPLETE.json is written only after all planned observations pass and files close.
Failures retain rows/diagnostics and no completion marker. Analysis validates raw
schema, metadata, schedule, totals, statuses and markers. It rejects incomplete
runs by default. Explicit partial summaries remain complete=false and exit 1,
with failed/missing counts. Warmups are retained separately; all successful
measured observations, including outliers, enter statistics.

Separate summary JSON reports successful/failed/missing trials, warmups, median,
mean, sample standard deviation (n-1), minimum and maximum, grouped by run and
algorithm. Fewer than two successes yields null standard deviation; zero successes
yields null statistics. Synthetic fixtures are labeled tests and are not results.

Input planning uses 4*N*sizeof(int32), bounded before allocation by a configurable
256 MiB default. This is not measured memory or a hard process RSS limit. Matrix
configuration/row/list limits are checked before constructing its Cartesian
product. CPU affinity/frequency, machine background load and cache state are not
controlled; timing units do not imply clock accuracy. No ranking is claimed.

### Files added or changed

- include/benchmark/timing.hpp and src/benchmark/timing.cpp: protocol/configuration,
  generator reuse, ordered fingerprint, cyclic trials, normal sorting timing,
  reference validation and failure rows.
- include/benchmark/output.hpp and src/benchmark/output.cpp: CSV/JSON escaping.
- src/benchmark/timing_main.cpp: dedicated CLI and exclusive raw bundles/markers.
- cmake/benchmark_metadata.cmake and CMakeLists.txt: separate targets, configured
  compiler/build metadata, source hashes/provenance and two new CTest groups.
- scripts/run_matrix.py: bounded serial matrix with environment/command evidence.
- scripts/analyze_results.py: strict raw validation and separate JSON statistics.
- tests/test_timing.cpp: reproducibility, distribution construction, equivalent
  original input, schedule, full validation, exceptions, bounds and escaping.
- tests/test_benchmark.py: CLI/schema/escaping/bounds/safety, synthetic statistics,
  partial/tampered data, matrix completion/failure and build-mode policy.
- README.md, docs/BENCHMARKING.md, docs/EXPERIMENT_PROTOCOL.md,
  docs/ALGORITHMS.md, docs/ROADMAP.md and this audit: methodology and actual status.

### Fresh validation

Initial Release configure/build/full tests exited 0 and passed 13/13 groups
(nine Python framework methods at that point). Review corrected a test command
that duplicated --output and could pass for the wrong invalid-argument reason,
bounded matrix-product construction before allocation, tightened uint64 CSV
validation and added source provenance plus synthetic CSV/child-failure checks.
No required build/test command failed; reviewed tests now contain 11 methods.

Fresh reviewed build commands, each exit 0:

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

Both full suites passed 13/13 groups. After the final Python numeric-parser
tightening, the Release CTest command and sanitizer CTest command above were
repeated; both exited 0 and again passed 13/13. No compiler warnings were emitted.
ASan/UBSan and LeakSanitizer passed with leak detection enabled; the historical
ptrace limitation did not recur and no leak-disabled retry was run.

| CTest group | Actual result in each final configuration |
| --- | --- |
| baselines | 3,590 sorting input cases and 98,508 linear-oracle search checks passed |
| environment_manifest | Three Python methods passed |
| datasets | 220 distribution/size/seed combinations and all existing fixtures passed |
| cli | Ten existing methods passed |
| quicksort | 3,718 existing inputs and fallback assertions passed; normal-budget fallback total 618 |
| pdqsort | 4,027 existing public/registry inputs passed |
| timsort | 4,149 existing public/registry inputs passed |
| comparisons | 1,404 inputs across four counted sorters plus exact/reset/isolation/overflow/fallback checks passed |
| memory, memory_unsupported | Existing format/error/real/unsupported checks passed |
| metrics_cli | Seven existing methods passed |
| timing | 72 reproducible distribution/seed/size inputs, 864 validated registry calls including warmups, sorted alias, input restoration/order, errors, bounds and escaping passed |
| benchmark_framework | 11 Python methods covering actual CSV/statistics/matrix/safety/failure behavior passed |

The timing unit cases use sizes 0,1,2,31,64,257 and seeds 0,1729,UINT64_MAX on the
four original distributions; sorted aliases are checked against corresponding
uniform samples. Faulty and throwing test sorters assert fail-fast behavior and
recorded correctness/exception distinctions. The Python child-failure stub exits
9 intentionally; the matrix records it and exits 1 as asserted by the passing
test. These expected negative tests are not failed validation commands or
benchmark measurements. Synthetic [10,20,30] ns CSV samples verify median/mean=20,
sample deviation=10, min=10/max=30; they never enter retained experiment output.

### Actual Release smoke matrix and analysis

The documented protocol was saved before running the smoke matrix. Commands
executed, each exit 0:

```sh
python3 scripts/run_matrix.py --binary build/release/sort_benchmark --output results/raw/benchmark_validation_20261009T160450529409Z/smoke_matrix --sizes 1000,10000 --seeds 1729 --repetitions 5 --warmups 1
python3 scripts/analyze_results.py results/raw/benchmark_validation_20261009T160450529409Z/smoke_matrix --output results/processed/benchmark_smoke_20261009T160450529409Z.json
```

results/processed was created if absent before analysis. Actual outcome: ten
completed size/distribution/seed configurations, 200 successful measured trials,
40 successful warmups and zero failed rows. The separate summary contains 40
algorithm/run groups, five measured observations per group, all outliers retained.
Largest measured size is 10,000. Raw measured durations are retained verbatim
and summaries are derived from those rows; no timings or speedups are invented
or presented as a general performance leaderboard. The larger 1M command in
documentation is instructions only and was not executed.

### Evidence and limitations

All new command records and historical/final CTest logs are under
results/raw/benchmark_validation_20261009T160450529409Z. Raw smoke bundles and
completion records are inside smoke_matrix; the derived summary is exclusively
saved under results/processed. Earlier evidence/results were not overwritten.
These environment-capture commands also exited 0:

```sh
python3 scripts/capture_environment.py --build-dir build/release --output results/raw/benchmark_validation_20261009T160450529409Z/release_environment.json
python3 scripts/capture_environment.py --build-dir build/sanitize --output results/raw/benchmark_validation_20261009T160450529409Z/sanitize_environment.json
```

The project Git-status inspection exited 128 due to absent metadata. No required
configure/build/test/smoke/analysis command failed. Test-only negative exits are
intentional assertions, not hidden failures. Review verifies unchanged original
CLI/registry/algorithms/generator/metrics/tests/vendors, effective timing linkage,
source hashes and exact regeneration of the smoke summary.

Validated on GNU/Linux only. Other OS/toolchains, full large-scale matrices,
controlled CPU/cache environments, timer-overhead calibration, allocation-level
memory tracking and plotting are not validated here. Runtime provenance artifacts
must remain accessible at the configured build path. No CUDA, 100M, or larger-than-
10K performance experiment ran; no cross-algorithm speed claim is made.

This reproducible timing/CSV/statistics milestone is complete. Phase 2 remains
open for optional Merge/Radix baselines and larger controlled sorting studies.
Next implementation milestone: add those CPU baselines with differential tests,
then Phase 3 deterministic hit/miss query generation and search benchmarking.

## Merge Sort and signed Radix Sort — 2026-10-09

### Inspection and fresh baseline

Read AGENTS.md, README, roadmap, audit, ALGORITHMS.md, BENCHMARKING.md,
EXPERIMENT_PROTOCOL.md, METRICS.md, CMake, registry/adapters, dataset/timing/metrics
interfaces, memory reporting, matrix runner and test conventions before edits.
pwd confirmed the existing workspace. An anonymous temporary-file write/read/delete
check passed. git status --short exited 128 because Git metadata is absent.
Existing files were backed up with SHA-256 inventory under
build/extra_baselines_review_20261009T165551911968Z. New evidence was exclusively
created under results/raw/extra_baselines_validation_20261009T165551911968Z;
historical CTest logs were copied before reuse and are not fresh test proof.

The pre-change Release configure, build and full CTest commands below each
exited 0; all 13 existing groups passed. No baseline defect needed repair.

### Implementations and integration

Added stable bottom-up project Merge Sort with adjacent run widths 1,2,4,...,
one N-key allocation per nontrivial call and alternating source/destination.
Clamped size_t lengths and guarded doubling avoid overflowing boundary arithmetic.
One right < left predicate selects each merge key, choosing left on equality;
tails use no predicates. A shared comparator template defaults to std::less in
production and uses run-local CountingLess only in mab_metrics. Exact small
fixtures and existing reset/interleaving tests verify counted behavior.

Added genuine stable LSD radix-256 sorting: four eight-bit passes, one N-key
allocation per nontrivial call, 256 size_t bucket offsets, stable forward scatter.
uint32(key) XOR 0x80000000 maps signed order monotonically into unsigned order.
No abs, signed shifts, overflowing key arithmetic, comparison sorting or fallback
is used. Original Key values are scattered, avoiding implementation-dependent
out-of-range conversion back to signed. Compile-time width checks enforce int32.
Both return without allocation for N < 2; no global/shared mutable state exists.
Theoretical auxiliary space is O(N) for Merge Sort and O(N+256) for Radix Sort,
not measured allocation. Sort-owned allocation remains inside normal timing.

Registered merge_sort and radix_sort after the four unchanged existing entries.
Correctness CLI help advertises both; default std_sort and JSON/CSV schemas remain
unchanged. sort_benchmark and the unchanged matrix runner discover all six names
through the existing registry, using identical generator input and normal adapters.
Normal timing still links only mab_timing/mab_core, without comparison counters.
Five sorters support key_less_than_v1. Radix Sort explicitly rejects comparison
counting as unsupported (stderr, exit 1, no metric JSON), rather than fabricating
zero. The RSS implementation and its process-level limitations are unchanged;
the unsupported radix metric request does not collect a separate RSS record.

### Files added and changed

Added:
- include/algorithms/mergesort.hpp, radixsort.hpp and detail/mergesort_impl.hpp:
  public int32 interfaces and shared stable merge strategy.
- src/algorithms/mergesort.cpp, radixsort.cpp: production implementations.
- tests/test_mergesort.cpp, test_radixsort.cpp, test_integer_sorts.hpp: dedicated
  full-vector differential/repetition/edge/digit tests and stable merge fixture.

Changed:
- CMakeLists.txt: two production sources and dedicated mergesort/radixsort groups.
- include/algorithms/sorting.hpp, src/algorithms/sorting.cpp: six-entry registry.
- include/benchmark/comparisons.hpp, src/benchmark/comparisons.cpp: fifth counted
  adapter and explicit radix unsupported diagnostic.
- src/main.cpp, src/benchmark/metrics_main.cpp: help describes available sorters
  and unsupported radix counting, preserving parsing/output behavior.
- tests/test_comparisons.cpp: eleven exact merge counts, five-adapter coverage,
  explicit radix exclusion; all previous checks retained.
- tests/test_cli.py, test_metrics_cli.py, test_benchmark.py: baseline selections,
  metric identity/unsupported handling, six-name discovery/equivalent fingerprints,
  subsets, schema/statistics and automatic matrix integration.
- README.md, ALGORITHMS.md, BENCHMARKING.md, METRICS.md, ROADMAP.md and this audit:
  algorithm details, conventions, current coverage, commands/outcomes/limitations.

Existing QuickSort/PDQSort/Timsort/std_sort implementations, generator, timing
engine, memory code, Python matrix/analysis, upstream source/licenses/provenance,
and all unrelated tests are unchanged. Source review records hashes and a patch;
Git metadata is not assumed or recreated.

### Fresh validation and exact commands

Each command exited 0. The first three were also executed before changes,
giving the 13/13 baseline; after integration they give 15/15.

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

Both full suites passed 15/15 CTest groups. Neither build emitted compiler warnings.
ASan/UBSan and LeakSanitizer passed with leak detection enabled; the historical
ptrace limitation did not recur. No leak-disabled retry was performed.

| Group | Fresh result in each configuration |
| --- | --- |
| baselines | 3,590 sorting inputs across six registry entries; 98,508 linear-oracle search checks passed |
| environment_manifest | Three Python methods passed |
| datasets | 220 combinations across six sorters plus unchanged swap/configuration fixtures passed |
| cli | Eleven methods passed; 72 new baseline distribution/size selections plus repeats/help/invalid aliases |
| quicksort | 3,718 unchanged cases and fallback/stack assertions passed; normal-budget fallback total 618 |
| pdqsort | 4,027 unchanged public/registry cases passed |
| timsort | 4,149 unchanged public/registry cases passed |
| mergesort | 4,015 differential inputs through public/registry/repeated paths; stable merge fixture passed |
| radixsort | 4,015 differential inputs through public/registry/repeated paths passed |
| comparisons | 1,404 inputs across five adapters; six exact QuickSort and eleven exact Merge Sort fixtures; isolation/reset/overflow/heap forwarding and radix exclusion passed |
| memory, memory_unsupported | Existing real/unsupported/synthetic format/error checks passed |
| metrics_cli | Nine methods passed, including 100 sorter/distribution/size configurations repeated twice, exact merge count and unsupported radix handling |
| timing | 72 reproducible inputs, 1,296 validated registry calls, sorted alias/restoration/order/failure/escaping checks passed |
| benchmark_framework | Twelve methods passed, including all-six-name CSV/matrix coverage, new subsets and identical input fingerprints |

Each new sorter's 4,015 inputs comprise 15 explicit edges, 3,280 exhaustive
arrays of length 0..7 over {-1,0,1}, 600 four-distribution/five-seed/30-size
combinations, 108 patterns and 12 digit sweeps. Largest correctness input is
10,000. Every case compares with std::sort through public and registry paths,
interleaves a different-sized call, repeats original input and re-sorts its result.
Merge stability is tested through the internal comparator with distinguishable
int32 equal-group keys, without claiming a public generic-record interface.

Exact Merge Sort fixtures are empty/singleton (0), two keys in either/equal order
(1), [1,2,3] (3), [3,2,1] (2), [1,1,1] (3), ascending/descending four keys (4),
and [1,3,2,4] (5). Counts were manually checked from bottom-up merge decisions;
they exclude tails and all reference validation. No fixed standard-library or
upstream count was invented. Synthetic timing/failed-child fixtures stay in
temporary tests; intentional test exits 1/9 are asserted negative paths.

### Actual six-sorter smoke and summary regeneration

Executed commands, each exit 0:

```sh
python3 scripts/run_matrix.py --binary build/release/sort_benchmark --output /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/extra_baselines_validation_20261009T165551911968Z/smoke_matrix --sizes 1000,10000 --seeds 1729 --repetitions 5 --warmups 1
python3 scripts/analyze_results.py /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/extra_baselines_validation_20261009T165551911968Z/smoke_matrix --output results/processed/extra_baselines_smoke_20261009T165551911968Z.json
```

All six sorters, all five benchmark distributions, seed 1729, sizes 1K/10K,
one warmup/five measured repetitions produced ten completed configurations:
300 successful measured trials, 60 successful warmups and zero failed rows.
The separate JSON summary has 60 groups with five measured successes per group,
all outliers retained. Review regenerates that entire summary exactly from raw
CSV and checks raw bytes unchanged during analysis, source manifests/current
source equality and executable/environment hash. No ranking is asserted.

Environment capture retries below each exited 0:

```sh
python3 scripts/capture_environment.py --build-dir build/release --output /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/extra_baselines_validation_20261009T165551911968Z/release_environment_verified.json
python3 scripts/capture_environment.py --build-dir build/sanitize --output /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/extra_baselines_validation_20261009T165551911968Z/sanitize_environment_verified.json
```

Initial environment-capture wrappers failed with exit 1: their command-record
names release_environment.json/sanitize_environment.json collided with the newly
created snapshot paths. Exclusive creation raised FileExistsError and preserved
the snapshots. Those child exit statuses were not saved, so they are not inferred.
The original snapshots and explicit recorder_failure.json notes remain alongside
successful retries with distinct *_command.json and *_verified.json names.
The source-review wrapper repeated the same filename collision with source_review.json
and exited 1 after review artifacts were written. Its unsaved child status is not
inferred. A separate read-only final verification checks those artifacts, current
sources, exact summary regeneration and raw immutability with a recorded exit 0.
These three wrapper failures were validation-recorder errors, not failed
build/test/benchmark commands or ignored sanitizer diagnostics. Git status's
exit 128 is the other inspection failure. No raw artifact was overwritten.

Per-command JSON records (run_command.py captures exact argv/stdout/stderr/exit),
historical/final CTest logs, source review, inventory/patch and raw smoke results
are preserved in the new evidence directory. No earlier raw evidence was
overwritten. Source review is executed as:

```sh
python3 results/raw/extra_baselines_validation_20261009T165551911968Z/review_sources.py
python3 build/extra_baselines_final_review.py
```

### Status and limitations

Both baselines are implemented, tested and documented. GNU/Linux is the validated
platform; other OS/toolchains were not executed. Memory complexity remains
theoretical, RSS remains process-wide, and allocation-specific instrumentation
is pending. Input limits use a planning estimate, not a hard RSS cap. CPU/cache
controls and timer calibration remain absent, so the small smoke is not evidence
of performance superiority. No CUDA, 100M or greater-than-10K performance run
was performed. The older upstream Timsort maintenance limitation is unchanged.

The Merge/Radix milestone is complete. Phase 2's larger controlled sorting studies
remain unfinished. Next step: define a controlled 1M study configuration and
collect repeated Release trials with saved environment/raw data; Phase 3 query
generation/search benchmarking follows the sorting experiments.

## Controlled one-million-element sorting study — 2026-10-09

Study `sorting_1m_20261009T172003802655Z` is complete under frozen v1 protocol
[protocol](studies/sorting_1m_20261009T172003802655Z_v1.md). No algorithms, timing/metrics implementation,
CLI, runner, analyzer, test, CMake or vendor file changed. Workspace write access
passed an anonymous temporary-file write/read/delete probe. Git metadata remains
absent: the environment probe git status --short exited 128; no Git revision is
invented. The current source, tools, build inputs and executable are SHA-256
manifested. Existing raw artifacts were inspected and hashed before new output.

### Frozen configuration, semantics and resource review

Six production sorters in registry order: std_sort, quick_sort, pdq_sort,
tim_sort, merge_sort, radix_sort. N=1,000,000 signed int32 keys; distributions
uniform, sorted, reverse_sorted, duplicate_heavy and nearly_sorted; seeds
1729,42,2718. One warm-up and five measured repetitions per algorithm/dataset.
Duplicate domain 16 ([-8,7]); nearly-sorted request exactly 10,000 index-pair
swaps, including allowed self/repeated pairs. Sorted uses the corresponding
uniform sample ordered ascending with zero swaps. Other inactive parameters
remain in the CSV as documented. mt19937_64_v1 is unchanged.

Expected and observed: 15 size/seed/distribution configurations, 90 algorithm/
dataset groups, 450 measured trials and 90 warm-ups, 540 total rows. Configurations
run serially in size/seed/distribution order; algorithm order uses the unchanged
seed_offset_cyclic_v1 rotation. Raw rows retain trial and execution indices;
five rounds do not fully balance six positions and no random shuffle occurred.
Each normal production call starts with the same restored original vector.
steady_clock times only sorting in integer ns, including sort-owned allocation/
deallocation. Generation, copying, reference sorting, full-output validation and
CSV I/O remain outside timing. Primary timing links mab_timing/mab_core, never
mab_metrics; no comparison-count experiment or process-RSS study was run.

Preflight MemTotal 16,475,164,672 bytes; MemAvailable 4,340,154,368 bytes;
free disk 134,457,196,544 bytes. Immediately before execution, available RAM
4,411,662,336 bytes and disk 134,454,919,168 bytes. The engine estimates
4*N*sizeof(int32) = 16,000,000 bytes (15.26 MiB), with unchanged planning limit
256 MiB. This excludes runtime/allocator overhead and bucket offsets and is
not measured memory or a hard RSS cap. Gates require >=256 MiB available RAM,
>=128 MiB free disk and equivalent finite-cgroup headroom if such a cap exists.
Accessible cgroup ancestors report memory.max=max and exposed cpu.max=max 100000;
address-space/data/RSS/file-size/CPU-time limits are unlimited, stack soft limit
8 MiB. Both preflight and immediate launch gates passed with matrix path absent.
No resource-driven protocol revision was necessary.

### Environment and limitations of control

Pop!_OS 24.04 LTS, Linux 6.18.7-76061807-generic, x86_64; Intel Core i5-11400H,
six physical cores and 12 logical CPUs, allowed affinity 0..11. GNU C++ 13.3.0,
CMake 3.28.3, Python 3.12.3, Release, sanitizers OFF; configured -O3 -DNDEBUG,
-Wall -Wextra -Wpedantic, C++17. Exact compile commands, cache, link command,
libstdc++ linkage, source/upstream provenance, CLI help/tool hashes are retained.
CLI/Python tools have no --version option; hashes and runtime versions identify
them instead. Benchmark executable SHA-256:
`98ae6eea14525a27241936abf4b493650a428bf6f0afcc1a94042dcfad087c7f`.

CPU policy observed before/after: intel_pstate powersave, balance_performance,
800000..4500000 kHz. No affinity, governor, priority or frequency change was made.
Preflight 1/5/15-minute load averages: 1.518/1.018/1.062; immediately before:
1.314/1.164/1.104; after: 1.286/1.176/1.109. Per-policy current-frequency,
pressure, cgroup and process-name/load snapshots are retained. A shared desktop
was used; background activity, CPU frequency, thermal and cache state were not
controlled. Thermal state was not measured. Copies touch input memory; this is
a warmed-input protocol. Timer overhead was not calibrated or subtracted.
These observations support descriptive findings for this session, not a universal
ranking, statistical significance or hardware-controlled population claim.

### Exact commands and fresh outcomes

All commands below exited 0. The full Release suite passed 15/15 CTest groups.
The build refreshed existing artifacts without source changes and emitted no
compiler warnings. The full suite includes 3,590 shared sort inputs/98,508 search
checks, 220 dataset combinations, QuickSort 3,718/PDQSort 4,027/Timsort 4,149 inputs,
4,015 inputs per new baseline, 1,404 comparison inputs across five adapters,
72 timing inputs/1,296 validated registry calls, and all CLI/memory/framework tests.
These tests are validation rather than study timings. No fresh sanitizer build
or suite was run for this documentation/experiment-only milestone; the preceding
15/15 ASan/UBSan result with leak detection enabled is historical evidence.

```sh
python3 results/raw/sorting_1m_20261009T172003802655Z/preflight_capture.py after_execution.json  # exit 0
python3 results/raw/sorting_1m_20261009T172003802655Z/analyze_study.py --self-test  # exit 0
python3 results/raw/sorting_1m_20261009T172003802655Z/preflight_capture.py before_execution.json  # exit 0
python3 results/raw/sorting_1m_20261009T172003802655Z/analyze_study.py --study /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/sorting_1m_20261009T172003802655Z  # exit 0
python3 results/raw/sorting_1m_20261009T172003802655Z/launch_review.py  # exit 0
python3 scripts/analyze_results.py /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/sorting_1m_20261009T172003802655Z/matrix --output /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/processed/sorting_1m_20261009T172003802655Z/per_seed.json  # exit 0
python3 results/raw/sorting_1m_20261009T172003802655Z/preflight_capture.py  # exit 0
cmake --build build/release --parallel 2  # exit 0
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF  # exit 0
ctest --test-dir build/release --output-on-failure -V  # exit 0
python3 scripts/run_matrix.py --binary build/release/sort_benchmark --output /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/sorting_1m_20261009T172003802655Z/matrix --sizes 1000000 --seeds 1729,42,2718 --distributions uniform,sorted,reverse_sorted,duplicate_heavy,nearly_sorted --sorts std_sort,quick_sort,pdq_sort,tim_sort,merge_sort,radix_sort --repetitions 5 --warmups 1 --memory-limit-mib 256 --distinct 16 --swaps 10000  # exit 0
python3 results/raw/sorting_1m_20261009T172003802655Z/verify_study.py  # exit 0
```

Every benchmark child command is retained separately in matrix/*_command.json;
all 15 child exit codes are 0. Existing environment-capture subprocess probes
also retain their exact commands/statuses; Git 128 is the expected metadata-
absence inspection failure. There were no failed build, test, matrix, analysis,
regeneration or verification commands, and no retries or omitted configurations.

Matrix execution UTC: 2026-10-09T17:26:15.005269+00:00 through
2026-10-09T17:26:30.239307+00:00. The wrapper's 15.234 s elapsed time includes
setup/process/validation/output and is not algorithm sort time.

### Results and analysis units

All 450 measured trials and 90 warm-ups passed full-vector std::sort-reference
correctness; zero failed/missing trials. The parser validates the 28-field
sort_timing_v1 schema, units, metadata, cyclic order, row identities/totals and
completion markers. All 15 required configurations and 90 algorithm/dataset
combinations are present. All six algorithms share each configuration's input
fingerprint, and configured source manifests match the current source files.

The established analyzer emits 90 per-seed groups with five successes and zero
failures each, median/mean/sample SD/min/max in ns. Warm-ups are retained and
excluded from statistics. Cross-seed analysis computes descriptive median/mean/
sample SD/min/max of three equal-weight per-seed medians, giving 30 groups.
It does not pool 15 trials as independent datasets. Every raw observation,
including outliers, is retained; no clipping, winsorization or significance test.
Full per-seed and cross-seed tables (ms = ns/1,000,000) are saved under
results/processed/sorting_1m_20261009T172003802655Z/RESULTS.md with unrounded CSV/JSON alongside.
The study-specific analysis code and its synthetic-only known-statistic/group-
validation tests are retained in the new raw evidence directory; engine/runner/
established analyzer remain unchanged.

### Verification and immutable evidence

New raw location: results/raw/sorting_1m_20261009T172003802655Z; matrix contains 15 exclusively created
bundles and COMPLETE markers. protocol.json/PROTOCOL_v1.md match the frozen
project protocol, SHA-256
`5a684928f809f8aa373c9275697676e061595a31617bf03ea6f952f4d3a11b9b`.
preflight.json, before_execution.json, after_execution.json, repository/source/
executable manifests, exact command records and verification.json are retained.
Processed location: results/processed/sorting_1m_20261009T172003802655Z; per_seed.json/csv,
cross_seed.json/csv and RESULTS.md are derived files. FINAL_AUDIT.md is saved
separately under the new raw study path after review.

Verification regenerated all five processed files byte-for-byte in a temporary
new location. All 138 matrix files match their pre-analysis hashes; all 334
previous raw files match their pre-study hashes; frozen protocol and execution
inputs are unchanged. Raw datasets/results and earlier audit evidence were not
overwritten. No observed deviation from the frozen protocol or required matrix.
No comparison or memory results are estimated from timing; RSS remains a process-
wide lifetime measure available through a separate path, not isolated workspace.

### Status and next experiment

The requested 1M study milestone is complete. Phase 2's required sorting
implementations/metrics/repeatable timing and first 1M study are validated.
Optional allocation-specific metrics, additional sorting experiments and plots
remain future work. No dataset larger than 1M, CUDA, GPU or 100M workload was run.
Recommended next experiment: a separately frozen 1M replication across independent
sessions and more held-out seeds, with documented CPU affinity/power policy and
counterbalanced configuration order where practical; retain session/dataset units
rather than treating repeated trials as independent data. No such replication
has run. Next implementation phase is Phase 3 deterministic hit/miss queries
and search benchmarking; 10M/100M scaling remains deferred.

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

## Phase 4 ordered structures — 2026-10-09

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


## Phase 5 — audited orchestration, visualization and completed CPU study (2026-10-09)

Workspace was writable: the safe temporary-file check succeeded and was removed.
AGENTS.md was read completely; README, roadmap, audit, algorithm/benchmark/metrics
references and both family protocols were inspected before implementation. Git
metadata is absent (`git status --short`: exit 128); none was created. The existing
Release baseline was freshly configured, built and passed 21/21 CTest groups.
Historical LastTest logs were copied separately; they are not fresh test evidence.

The new evidence root is
`results/raw/orchestration_validation_20261009T191000587965Z/`. Starting-state,
repository-before and prior-results manifests record 99 original project files
and 867 earlier result artifacts. Original files were backed up for a reviewable
patch. All 867 artifacts and all protected original files remain unchanged,
including the frozen 1M sorting study, search/structures protocols, vendored code,
algorithms, existing tests and existing Python family tools. No original C++
implementation or timing behavior changed. std_sort remains the default.

Before implementation, the new versioned protocol was saved and frozen as
`docs/ORCHESTRATION_PROTOCOL_v1.md`, with a retained copy PROTOCOL_v1.md and SHA256
`5bf13d60312d4958be93eb17dfe56c0be221964cf2960dec5988849d524d0d73`.
Earlier protocols were preserved. The protocol defines smoke and full presets,
serial execution, exact family outputs, query-category availability, resource
planning, missing/failure/interruption handling, aggregation and plotting.

### Implemented changes and metric definitions

Seven new files: the orchestration protocol; scripts/experiment_model.py,
run_experiments.py, analyze_experiment.py, plot_results.py, assess_experiment.py;
and tests/test_experiments.py. Eight existing files changed: CMakeLists.txt adds
one experiment_pipeline CTest group; README and docs/ROADMAP, AUDIT, ALGORITHMS,
BENCHMARKING, EXPERIMENT_PROTOCOL and METRICS describe verified behavior.
file_changes.json, changes.patch and final_source_manifest.json retain the exact
file inventory and review without Git.

The serial top-level runner invokes the unchanged sorting, array-search and
structure runners. Deterministic dry runs print exact parent/child commands,
configuration hashes, output paths and bounded resource estimates. Explicit run
IDs and exclusive directory creation prevent overwrites and collisions. Resume
is deliberately unsupported: existing paths fail fast. Child stdout/stderr,
return codes, timestamps and interruption diagnostics are retained; failed or
interrupted runs never receive successful completion markers. Process groups
are terminated on interruption. Collection and final completion markers require
strict validation, including configuration, raw schema, duplicate trial identity,
positive/nonnegative finite timing as appropriate, family protocol, build and
fingerprint consistency, expected coverage and derived-file hashes. A partial
analysis requires an explicit flag, reports omissions and exits unsuccessfully.

observations.jsonl preserves every raw observation and its file/row provenance;
unavailable metadata remains null rather than invented. Warmups and measured
rows remain distinct. Sorting and construction times are elapsed batch ns;
lookup plots show normalized batch-average ns/query, never directly measured
individual latency. Generation, copying, queries and correctness checks retain
the existing outside-timing semantics. Primary runs contain no comparison
instrumentation. No process RSS or isolated allocation value was collected in
these timing studies. Comparison/memory figures explicitly report absent matching
evidence instead of estimating measurements.

Per-dataset groups retain successful/failed/missing counts, median, mean, sample
standard deviation (ddof=1), minimum and maximum. Warmups are excluded from timing
statistics. Cross-dataset summaries first summarize repeated timings within each
dataset, collapse identical ordered-input fingerprints, then equally weight
medians of distinct inputs; repetitions do not inflate dataset sample size.
All outliers remain. Query policies, workload parameters, build/source identity
and construction versus lookup stay separate. No confidence interval or
statistical-significance claim is made.

Matplotlib Agg produces SVG/PDF figures with deterministic metadata, fixed font
and styling, zero-based linear y axes, explicitly labeled symlog size axes,
central medians, dataset-median min/max spread and separate trial variability.
Each plot manifest records source hashes, filters, transforms, points, units,
plotting stack and output hashes. Reports consolidate environment, protocol,
coverage, results, variability, limitations and regeneration instructions.
Byte identity is verified on this plotting stack, not guaranteed across versions.

### Actual failures, fixes and final validation

The initial standalone pipeline suite exited 1: 18/19 methods passed; the parent
SIGTERM test timed out. Raising InterruptedError in the signal handler allowed
Python I/O retry; it now raises KeyboardInterrupt and terminates the child process
group. Test cleanup also fixed ResourceWarnings from that failure. The initial
failure log and result remain retained. Subsequent review separated natural
SIGINT/SIGTERM interruption from other fatal child signals such as SIGABRT, and
validated exact return-code types plus interrupted parents whose child exited 0.
These handling fixes affect failure paths, not successful benchmark timings.
The exact Python execution tools used for all three studies are retained under
execution_tools/ with hashes matching each study environment. Final code includes
the handling fixes and passes the expanded 23-method suite. No study failed.

Exact final commands, each exit 0:

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
python3 tests/test_experiments.py build/release
```

Final Release: 22/22 CTest groups, 19.32 seconds. Final Debug ASan/UBSan: 22/22,
54.94 seconds. Independent Python: 23/23 methods. Leak detection remained enabled;
the historical ptrace limitation did not recur, so no leak-disabled retry ran.
No final compiler warnings. All 21 preexisting groups passed unchanged, including
6,635 structure cases / 1,239,680 insertion attempts / 3,218,705 map-oracle lookups /
75,665 invariant checks; 3,704 search inputs / 309,996 oracle checks; existing
sorting, metrics, CLI, timing and Python framework tests. New tests cover stable
configuration/dry-run identity, malformed/duplicate records, incompatible protocols,
missing trials, failed and interrupted subprocesses, atomic directory collisions,
hand-checkable hierarchical statistics, resource estimates, exact plot points,
manifest provenance and byte-identical summary/report/figure regeneration.
Synthetic fixture timings are test data, never presented as benchmark measurements.

COMMANDS.md and commands_index.json in the new evidence root retain every recorded
configure/build/test, dry-run, smoke/calibration/full launch, runtime assessment
and independent verification command with actual exit codes and diagnostics.
The initial unwrapped failure and Git inspection failure are separately identified.
Family experiment.json and *_command.json files retain exact benchmark commands.

### Executed smoke, calibration and unchanged full preset

Smoke command (exit 0), preceded by the identical command plus --dry-run (exit 0):

```sh
python3 scripts/run_experiments.py --preset smoke --run-id phase5_smoke_20261009T191000587965Z
```

Smoke: N=0/64/1000, uniform/duplicate_heavy, dataset seeds 1729/42,
query seed 2718, structure seed 1729, Q64, one warmup and five repetitions.
All 36 configurations completed: sorting 360 measured/72 warmup;
search 975/195; structures 1,925/385. Total 3,260 measured successes and 652
warmups, zero failed/missing/interrupted trials. Its 652 per-dataset and 330
cross-dataset groups, report and 81 SVG/PDF figure pairs regenerated exactly.
Unavailable categories were explicitly recorded, not fabricated as missing trials.
verification.json retains raw immutability and prior-artifact verification.

The tiny smoke's overhead-inclusive full forecast was 22,955.803 seconds,
exceeding the 3,600-second runtime gate. A separately labeled, frozen 100K uniform
calibration used all algorithms/structures, seed 1729, Q1000, zero warmups and one
measured repetition. It did not replace or reduce the full protocol. Its exact
launch used --config with calibration_config.json and the distinct run ID
phase5_calibration_20261009T191000587965Z; exit 0. CALIBRATION_PROTOCOL_v1.md and
calibration_runtime_assessment.json retain the prelaunch contract and result.
The refined forecast was 2,745.658 seconds with a factor-four allowance; memory,
disk and runtime planning gates passed. Forecasts are estimates, not timings.
FULL_STUDY_LAUNCH_v1.md and full_launch_plan.json were saved before execution.

Full command (exit 0), preceded by identical --dry-run (exit 0):

```sh
python3 scripts/run_experiments.py --preset full --run-id phase5_full_20261009T191000587965Z
```

The frozen full preset ran N=1K/10K/100K/1M; uniform, sorted, reverse_sorted,
duplicate_heavy and nearly_sorted; seeds 1729/42/2718; query seed 2718;
structure seed 1729; Q1000; W1/R5; cardinality16; default nearly-sorted swaps;
1024 MiB per-process budget. All six sorting algorithms, three array searchers,
Skip List and B-Tree orders 10/16/32/64 ran serially. 180 configurations completed.
Before query availability checks, protocol upper bounds were 24,900 measured and
4,980 warmup rows. Exact actual availability produced:

| Family | Successful measured | Successful warmups | Failed / missing |
|---|---:|---:|---:|
| Sorting | 1,800 | 360 | 0 / 0 |
| Array search | 7,020 | 1,404 | 0 / 0 |
| Structures | 13,200 | 2,640 | 0 / 0 |
| Total | 22,020 | 4,404 | 0 / 0 |

Structure measured rows comprise 1,500 builds and 11,700 lookup batches.
No interrupted configuration. 144 category/configuration pairs were explicitly
unavailable (72 each search/structures: empty-only policy on nonempty input and
unrepresentable between-value gaps in duplicate-heavy inputs). This is expected
protocol availability, not omitted execution. Every retained row passed correctness.
The report has 4,404 per-dataset and 1,468 cross-dataset groups and 177 SVG/PDF
figure pairs. Overhead-inclusive family wall times were sorting 16.222 seconds,
search 158.112 seconds and structures 215.411 seconds; analysis 97.930 seconds.
These include setup/process/validation/I/O and are not algorithm timing statistics.

Raw, processed and figure roots respectively are:
`results/raw/phase5_full_20261009T191000587965Z/`,
`results/processed/phase5_full_20261009T191000587965Z/`,
`results/figures/phase5_full_20261009T191000587965Z/`.
REPORT.md, summary.json, observations.jsonl and plot_manifest.json are data-driven.
Independent verify_full.py exited 0: all processed bytes and 177 figure pairs
regenerated byte-for-byte in fresh temporary directories; all 1,764 full raw files
remained unchanged. full_verification.json retains this proof. All 867 earlier
artifacts and 671 smoke/calibration artifacts also remained unchanged. Final
read-only validation checks current code against retained summaries/manifests.

### Environment, limits and completion

Recorded full-launch environment: Linux 6.18.7-76061807-generic x86_64;
Intel Core i5-11400H, 12 logical CPUs; RAM 16,475,164,672 bytes,
available 3,908,259,840 bytes; disk free 134,313,807,872 bytes.
GNU C++13.3.0, CMake3.28.3, Python3.12.3, Release -O3 -DNDEBUG;
Matplotlib3.11.0, NumPy1.26.4, Agg/DejaVu Sans. Actual compile commands,
source/executable/tool/font hashes and environment/resource snapshots are retained.
Exposed cgroup memory.max=max; affinity CPUs0..11; governors powersave;
load average 1.1245/1.4868/1.4043. These are observations, not controls. No frequency,
cache, affinity, thermal or background-load control was imposed; thermal state
was not measured. Results describe this shared-machine session. No statistical
significance, universal ranking or independent-session replication is claimed.

This milestone delivers both the validated end-to-end pipeline and completed full
CPU timing study. Final review evidence is FINAL_AUDIT.md and final_review.json;
all intended changes are saved and no required test/integrity check remains open.
Limitations: no resume, Linux-specific orchestrator resource/signal policy, byte
identity tied to plotting stack, unavailable comparison/memory study figures,
uncalibrated individual-query latency and uncontrolled shared-session confounders.
No CUDA or 100M experiment was attempted. Exact next implementation milestone:
Phase 6 OpenMP parallel sorting, thread-count controls and differential validation,
then a separately frozen scaling/speedup/efficiency experiment.

Final review command initially exited 1 because the review helper reconstructed
the report from a JSON-loaded plot manifest whose sorted PDF/SVG keys differ from
the SVG/PDF insertion order used by figure generation. This was a verification
helper error, not a raw-data or production-regeneration failure. The helper now
restores the generator's explicit format order before comparing report bytes;
final_review_initial.py and commands/final_review.json retain the failure. The
corrected final_review_corrected command and final_review.json retain its result.

A second helper invocation exited 1 after the substantive data/report/hash checks
passed: it used the full verification field name when reading the smoke evidence
(the smoke field is all_derived_regenerated_byte_identical). This schema-reference
error was corrected; final_review_second.py and final_review_corrected command
record preserve it. final_review_complete is the final corrected invocation.
Neither helper failure modified an experiment or required a production-code change.

## Phase 6 — OpenMP implementation and completed scaling study (2026-10-09)

Workspace writable; no Git metadata (git status128), no repository initialized.
Inspected AGENTS.md completely, README, roadmap/audit/algorithm/benchmark/protocol/
metrics docs, existing core/registry/CLI/CMake/tests and Phase5 tooling before edits.
Baseline fresh Release configure/build/CTest exited0,22/22 groups passed17.54s.
The starting106 project-file hashes/backups and3,796 previous artifact hashes are
retained in `results/raw/openmp_validation_20261009T200852928292Z/repository_before.json`, `prior_artifacts_sha256.json`
and `build/openmp_review_20261009T200852928292Z`. All earlier raw/processed/figures and historical protocols,
including frozen1M sorting and Phase5 full study, remain unchanged.

Contract `results/raw/openmp_validation_20261009T200852928292Z/PROTOCOL_v1.md` and docs/OPENMP_PROTOCOL_v1.md were frozen
before implementation. Stable signed-int32 parallel Merge Sort uses one N-key
buffer allocated before mutation, task splits above16384, taskwait before parent
merge/copyback and a final team barrier. Requests1..64, serial for request1 or
N<32768; invalid or nested requests reject before mutation. Parent merges are
serial; O(NlogN) work/O(N) keys plus runtime/task/stack overhead. Task bodies
cannot throw/allocate; OpenMP runtime failure is runtime-defined. No fault-injection
claim. Empty/singleton safe, no arithmetic transformation of keys.

Separate configurable registry/executable preserves the old6-entry registry,
std_sort default and sequential merge_sort. The old timing loop is factored into
one shared template; copy/reference validation remain outside steady_clock ns.
Allocation, team creation, tasks/joins and deallocation are timed. New32-column
parallel_sort_timing_v1 appends version/request/actual-team/region fields; original
sort_timing_v1 CSV remains28 columns. Requested team is not busy-worker count.
Normal timing has no test observer/counting/RSS. Benchmark metadata retains
source/executable/tool/library hashes, compile commands, OpenMP flags/runtime paths
and environment. No guessed libgomp version.

Files added: include/algorithms/parallel_mergesort.hpp,
include/algorithms/detail/parallel_mergesort_impl.hpp,
src/algorithms/parallel_mergesort.cpp, include/benchmark/detail/timing_impl.hpp,
include/benchmark/parallel_timing.hpp, src/benchmark/parallel_timing.cpp,
src/benchmark/parallel_main.cpp, scripts/run_parallel_matrix.py,
scripts/analyze_parallel_results.py, tests/test_parallel_mergesort.cpp,
tests/test_parallel_benchmark.py, docs/OPENMP_PROTOCOL_v1.md and both frozen
OpenMP study launch documents in docs/studies/. Existing changes: CMakeLists.txt,
include/benchmark/timing.hpp, src/benchmark/timing.cpp, README.md and docs/
ALGORITHMS.md, BENCHMARKING.md, EXPERIMENT_PROTOCOL.md, METRICS.md, ROADMAP.md,
AUDIT.md. No vendor, generator, old algorithm/registry or old test/Python file
changes. Full final inventory and review patch are retained with this audit.

Final commands (all exit0, stdout/stderr/argv/status retained in commands/):
```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF -DMAB_ENABLE_OPENMP=ON
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON -DMAB_ENABLE_OPENMP=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
python3 tests/test_parallel_benchmark.py build/release/parallel_sort_benchmark
```
Final corrected Release24/24 passed30.09s, ASan/UBSan24/24 passed84.51s;
13 parallel Python tests passed standalone and within each suite, including all
five distributions/zero sorted swaps. Existing Phase5 Python23 methods still pass.
No compiler warnings in fresh build logs. Leak detection enabled; no ptrace failure
or leak-disabled retry occurred. Earlier reviewed suites24/24 also passed before
the metadata correction; they are retained separately, not the final evidence.
C++ parallel tests:523 inputs,4,184 public/registry output checks at1/2/4/8threads,
ten concurrent131073-element calls; eight observed tasks and65,549 merges in
stable projected-key fixture, bounds/threshold/serialized-nesting and6 timing rows.
Exact equality to std::sort/sequential results verifies order and permutation;
stability uses projected-key identity. OpenMP-enabled team probe1:1,2:2,4:4,8:8.
OpenMP-OFF configure/build sort_benchmark/list-sorts all exited0 and retained
originalsix names; no full OFF CTest is claimed.

Concurrency limitation: TSan compilation succeeded, but both the parallel test
and independent std::thread probe exited66 before tests with `FATAL:
ThreadSanitizer: unexpected memory mapping`. This is an environment startup
failure, not evidence of an OpenMP-specific conflict or race-free execution.
Valgrind unavailable. No access-control/ASLR workaround attempted. Disjoint ranges,
barriers, atomic internal observers, concurrent-call stress and ASan/UBSan are
complementary validation, not a race-detector pass. Exact commands/diagnostics:
commands/tsan_compile.json, tsan_run.json, tsan_standalone_compile.json,
tsan_standalone_run.json.

Failures retained: initial recorder setup exited1 because commands/ did not yet
exist; its baseline child was never launched (initial_recorder_failure.json).
Initial Python fixtures emitted unclosed-file ResourceWarnings, corrected with
StringIO before final tests; no final warning. First full study command exited1:
`matrix/bundle configuration differs`. All180 child processes actually exited0
with1,800 correct measured/360 warmup rows, but analyzer incorrectly required
floor(N/100) swaps for already-sorted input, which correctly records0. This was
an analysis defect; corrected without changing datasets/timing code. The original
attempt `openmp_scaling_20261009T200852928292Z` remains FAILED, no COMPLETE or derived-success claim.
Its1,806 files are hash-protected, diagnosis in failed_attempt_diagnosis.json.
An all-five-distribution regression and fresh Release/sanitizer suites preceded
exclusive new smoke/full retry paths. No attempt pooling, overwrite or resume.
Exploratory read of nonexistent case_0004/run.json exited1 (actual name run_000004);
it did not affect execution or evidence.

Corrected smoke commands (all exit0):
```sh
python3 scripts/run_parallel_matrix.py --preset smoke --output results/raw/openmp_smoke_20261009T200852928292Z_retry1 --processed results/processed/openmp_smoke_20261009T200852928292Z_retry1 --figures results/figures/openmp_smoke_20261009T200852928292Z_retry1 --dry-run
python3 scripts/run_parallel_matrix.py --preset smoke --output results/raw/openmp_smoke_20261009T200852928292Z_retry1 --processed results/processed/openmp_smoke_20261009T200852928292Z_retry1 --figures results/figures/openmp_smoke_20261009T200852928292Z_retry1
python3 -B results/raw/openmp_validation_20261009T200852928292Z/verify_run.py smoke
```
Smoke32 configurations,N0/32767/32768/65537,uniform/duplicate_heavy,seed1729,
threads1/2/4/8,W1/R5:320 measured and64 warmup successes, zero failed/missing.
Eight figure pairs/report/summary bytes regenerated; all329 raw files unchanged.
All-distribution N100 validation additionally passes within the13-method suite.

Full retry launch frozen before execution at
`docs/studies/openmp_scaling_20261009T200852928292Z_retry1_v2.md` and RETRY_FULL_STUDY_LAUNCH_v2.md.
Original v1 remains immutable; v2 clarifies sorted swaps0 and records retry reason,
new paths, hashes/resources. No matrix change. Corrected smoke forecast199.616s
child wall (Nlog2(N+2) ratio×4), below1800s budget, plotting separate. Memory estimate
150,217,728 bytes, required available536,870,912 bytes; disk allowance419,889,152,
required free839,778,304. Actual prelaunch availableRAM6,755,241,984 and disk free
134,562,123,776 bytes. These are planning/snapshot values, not isolated memory.

Full commands (all exit0):
```sh
python3 scripts/run_parallel_matrix.py --preset full --output results/raw/openmp_scaling_20261009T200852928292Z_retry1 --processed results/processed/openmp_scaling_20261009T200852928292Z_retry1 --figures results/figures/openmp_scaling_20261009T200852928292Z_retry1 --dry-run
python3 scripts/run_parallel_matrix.py --preset full --output results/raw/openmp_scaling_20261009T200852928292Z_retry1 --processed results/processed/openmp_scaling_20261009T200852928292Z_retry1 --figures results/figures/openmp_scaling_20261009T200852928292Z_retry1
python3 -B results/raw/openmp_validation_20261009T200852928292Z/verify_run.py full
```
Full180 configurations:N32768/100000/1000000,5distributions,3seeds1729/42/2718,
threads1/2/4/8,two sorters,W1/R5,card16,sorted swaps0/defaultfloor(N/100)otherwise,
256MiB array budget. All1,800 measured/360warmup trials passed, failed/missing0;
all180 child commands and analysis exited0. Pipeline wall33.123s includes analysis.
Each input fingerprint agrees across thread configurations. Observed parallel
teams2/4/8 equal requests; request1 executes serial. Timing remains uninstrumented.
360 per-dataset algorithm groups,180 dataset ratios,60 cross-dataset groups;
20SVG/PDF figure pairs, report/summary/observations regenerated byte-for-byte.
All1,809 raw files unchanged through regeneration, all3,796 previous artifacts,
original smoke, failed attempt and frozen protocols unchanged.

Descriptive N1M,p8 results: median of three dataset-specific ratios, formed from
within-dataset five-trial medians. Efficiency divides primary ratio by actual8;
min/max is across dataset ratios, not a confidence interval. No significance claim.

| Distribution | Sequential-baseline speedup | Min–max | Efficiency | Separate parallel1 speedup |
|---|---:|---|---:|---:|
| duplicate_heavy | 3.568831 | 3.468465–3.826871 | 0.446104 | 3.893432 |
| nearly_sorted | 3.079466 | 2.492053–3.328528 | 0.384933 | 3.777703 |
| reverse_sorted | 2.603176 | 2.111693–2.929176 | 0.325397 | 4.384512 |
| sorted | 2.501757 | 2.457263–2.671667 | 0.312720 | 3.594457 |
| uniform | 3.045514 | 3.042874–3.512856 | 0.380689 | 3.355280 |

Environment: Linux6.18.7-76061807-generic x86_64/glibc2.39, Intel i5-11400H,
6physical/12logical CPUs, affinity0..11; totalRAM16,475,164,672bytes; GNU13.3.0,
CMake3.28.3,Python3.12.3,Matplotlib3.11.0. Release-O3-DNDEBUG for both algorithms,
parallel translation units additionally-fopenmp; CMake OpenMP4.5/_OPENMP201511,
actual libgomp linkage/hashes retained. Exposed cgroup memory.max=max; governors
performance at retry preflight, load3.3564/2.5723/1.9731. These are observations,
not controls; no affinity/frequency/cache/thermal/background changes imposed.
Thermal state not measured;12logical CPUs are not12physical cores.
OMP_DYNAMIC=FALSE,THREAD_LIMIT=8,MAX_ACTIVE_LEVELS=1,WAIT_POLICY=PASSIVE recorded.

Raw `results/raw/openmp_scaling_20261009T200852928292Z_retry1`, processed `results/processed/openmp_scaling_20261009T200852928292Z_retry1` and figures
`results/figures/openmp_scaling_20261009T200852928292Z_retry1` retain matrix, environments/source/compile/runtime
identities, every row/outlier, statistics, report and machine-readable plot manifest.
`results/raw/openmp_validation_20261009T200852928292Z/full_retry_verification.json` supports completion/regeneration;
smoke_retry_verification.json supports smoke. execution_tools and retry_execution_tools
archive exact pre/post-correction Python tools. COMMANDS.md/commands/ retain exact
argv, exit status, stdout/stderr, including prior failures. final_review.json,
FINAL_AUDIT.md, file_changes.json, source_after.json and changes.patch support
saved-file/integrity review. Regenerate into NEW paths with analyze_parallel_results.py;
raw files are immutable, no retries/resumption in-place.

Phase6 delivers validated OpenMP implementation **and completed scaling study**.
Limitations: TSan unavailable as above; serial parent merges and different serial
merge strategies between sequential baseline and parallel-request1; team count
not busy-worker count; one shared session with fixed matrix order/odd-R cyclic
imbalance and uncontrolled frequency/cache/thermal/load. Ratios aggregate datasets,
not independent repetitions. No isolated RSS, comparison-count experiment,
independent-session replication, statistical significance or linear/universal
scaling claim. No CUDA, learned-index/AlphaDev or100M experiment was attempted.
Next roadmap milestone: Phase7 CUDA device/runtime preflight and reproducible CUB
Colab/cloud guide with separate transfer/kernel/end-to-end semantics; do not claim
GPU results until actual verified execution. Other deferred research remains listed
in ROADMAP.md.

## Phase 7 — CUDA readiness and reproducible cloud guide

This completes the **requested preflight/guide milestone**, not the original
roadmap's CUDA sorting/timing experiment. No CUDA sorting/searching algorithm,
acceleration result, GPU performance measurement or100M experiment was added/run.
Workspace writable via anonymous temporary-file check; Git status128/no metadata,
no Git initialization. Read AGENTS.md, current roadmap/audit/README/CMake/timing
architecture, Phase6 protocol/report/final audit/integrity records before edits.
Phase6 reviewed source120/120 hashes matched starting state. Initial source120
files and8,447 raw/processed/figure artifacts were hashed/backed up before editing.
`results/raw/cuda_preflight_validation_20261009T205410772326Z/source_before.json`, prior_artifacts_sha256.json, inspection.json
and `build/cuda_review_20261009T205410772326Z` retain this baseline. Baseline Release configure/build/CTest
exited0 with24/24 groups passed30.14s. No prior correctness defect was observed.

Contract docs/CUDA_PREFLIGHT_PROTOCOL_v1.md was frozen before implementation,
with copy PROTOCOL_v1.md/hash protocol.json retained. scripts/cuda_preflight.py
uses standard-library discovery, Linux NVIDIA display/compute PCI and kernel-driver
binding/module/device/version evidence, lspci and nvidia-smi management queries,
resolved nvcc/toolkit/header/library paths, OS/kernel/architecture/CPU/Python,
CMake version/CUDA_STANDARD availability, relevant allowlisted environment paths
and source hashes. No full environment/PATH/cache dump. Secret-named environment
values, URL credentials and sensitive query values are redacted from retained
strings/path keys. Selected CMake cache fields only; scratch builds are deleted.
Commands have timeout/default60s and explicit return code/stdout/stderr/status.
Missing tools/files and skipped steps are explicit, not successful probes.

Only when a candidate NVIDIA nvcc answers and CMake>=3.18 exists does preflight
configure the actual project with CUDA ON, OpenMP/sanitizers/testing OFF, Release
and explicit compiler, build cuda_runtime_probe, and attempt enumeration/device0
kernel/copyback validation. Driver/toolkit/device capabilities are separate, not
inferred from nvcc version. Seven states include the five required scenarios plus
toolchain_unverified/detection_unavailable. Operational requires strict runtime
JSON+successful configure/build/checked kernel. COMPLETE.json means discovery
finished, not CUDA working. Exit0 operational, exit2 unavailable/unverified report,
exit1 reporting/IO/internal error,130 interrupted (incomplete marker); argparse
usage errors exit2 without discovery completion. Atomic directory ownership rejects
existing output before any probe and preserves previous/concurrent-run evidence.

CMake MAB_ENABLE_CUDA defaults OFF; no CUDA discovery/language/toolkit dependency
in the CPU path. New cmake/cuda.cmake requires CMake>=3.18 and NVIDIA toolkit>=11.0
with C++17/compatible host compiler on explicit opt-in. Existing CPU CMake3.16/
C++17 minimum, algorithms/default/registries/timing and OpenMP policy unchanged.
New src/cuda/runtime_probe.cu links only CUDA::cudart, independently of CPU
sanitizer flags; combining CUDA and CPU sanitizers explicitly rejects. Enumerate
visible device properties/API versions; test only device0 with one-int write1729,
launch/synchronization/copy-back/reference/free checks. No timing or sorting.
Probe exit77 on enumeration unavailable/no device maps to optional CTest skip;
post-enumeration failure exits1/CTest fail. This source is **not compiled or run
locally** because no toolkit is available; no CUDA test pass/skip is claimed for
CPU-OFF builds, where that test is not registered.

Files added: scripts/cuda_preflight.py, tests/test_cuda_preflight.py,
cmake/cuda.cmake, src/cuda/runtime_probe.cu, docs/CUDA_PREFLIGHT_PROTOCOL_v1.md,
docs/CUDA_EXECUTION_GUIDE_v1.md. Modified: CMakeLists.txt, README.md,
docs/ROADMAP.md, docs/AUDIT.md. Existing algorithms, interfaces, dataset generation,
benchmark/Python implementation/tests, third-party licenses/sources and historical
protocols/results remain unchanged. Detailed inventory/review patch/source manifest
are retained in file_changes.json/changes.patch/source_after.json.

Final commands below all exited0, with exact argv/stdout/stderr/times/status
retained in commands/reviewed_*.json and COMMANDS.md:
```sh
python3 tests/test_cuda_preflight.py
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=OFF
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```
Final reviewed Release25/25 passed27.09s, ASan/UBSan25/25 passed78.64s.
All22 preflight/build-isolation methods passed standalone and in both final suites;
13 OpenMP framework and23 existing orchestration Python methods still pass.
Existing sorting/search/structure/OpenMP differential/invariant tests remain
registered/passing. No fresh configure/build/test failures or compiler warnings.
Leak detection enabled; ptrace limitation did not recur, no detect_leaks=0 retry.
The first25/25 Release/sanitizer runs also passed before final privacy/path-driver
review; they are intermediate evidence, not substituted for final reviewed suites.

Tests cover five readiness scenarios, extra unknown/toolchain states, nvcc version
not implying kernel readiness, failed kernels, management CSV escaping, malformed
runtime JSON, missing commands/files, subprocess exit/timeout diagnostics, disabled
compiler gating, mocked build pipeline failure boundaries, redaction/path-key
redaction/numeric JSON preservation, consecutive-run isolation, output collision,
interrupted/report-error markers and invalid CLI timeout. A real CMake option test
configures both default/explicit CUDA OFF with deliberately unavailable CUDACXX/
CUDAToolkit_ROOT, verifying no CUDA compiler cache/check. No mocked fixture is
represented as actual GPU capability. Additional CPU fallback commands (all0):
```sh
cmake -S . -B build/cuda_cpu_fallback -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=OFF -DBUILD_TESTING=OFF
cmake --build build/cuda_cpu_fallback --target sort_benchmark --parallel 2
build/cuda_cpu_fallback/sort_benchmark --list-sorts
```
The original6 sorter names were returned. This fallback has testing OFF; no full
fallback CTest pass is claimed. Full fresh suites above keep existing OpenMP ON.
CPU environment capture exited0:
```sh
python3 scripts/capture_environment.py --build-dir build/release --output results/raw/cuda_preflight_validation_20261009T205410772326Z/cpu_environment.json
```
The unchanged older CPU tool says GPU not probed; GPU evidence is the new report.

Actual local preflight (exit2, expected unavailable readiness):
```sh
python3 scripts/cuda_preflight.py --output results/raw/cuda_preflight_20261009T205410772326Z_reviewed
```
Earlier discovery at `results/raw/cuda_preflight_20261009T205410772326Z` also exited2, retained unchanged; final
report includes additional human model/driver-path/redaction review. report.json,
SUMMARY.txt, COMPLETE.json and source hashes are retained in each exclusive path.
Observed Linux6.18.7-76061807-generic/x86_64, CMake3.28.3. PCI0000:01:00.0,
NVIDIA10de:25a0/class030000; lspci exit0 identifies GA107M [GeForce RTX3050Ti Mobile].
No bound kernel driver, visible nvidia module, /dev/nvidia0 or /dev/nvidiactl;
/proc/driver/nvidia/version missing. nvidia-smi and nvcc missing (returncode=null,
status unavailable), no discovered CUDA driver/runtime libraries or toolkit files.
Driver/runtime/toolkit versions unknown, not invented. CMake version and
CUDA_STANDARD-help commands exit0, documenting language feature availability,
**not** an available CUDA compiler. Configure/build/runtime are explicitly skipped;
CUDA ON configuration was never attempted. Classification gpu_driver_unavailable
means CUDA driver unavailable/unverified from current evidence, not a diagnosis
that hardware is broken. No software installation or system/permission change.

The guide covers allocated GPU verification, source URL/revision supplied by user
(no invented remote), alternatively audited source archive+hash verification,
cloud-only dependency setup, CPU fallback, isolated CUDA smoke/CTest semantics,
metadata/visibility, troubleshooting and persistent Drive/cloud export. It uses
current project options. Colab/cloud execution, remote clone, dependency installs,
Drive mounting/upload and CUDA-enabled commands have **not run locally or in Colab**.
A source-only archive and126-file manifest are retained as phase7_source.tar.gz/
source_after.json, archive hash in source_bundle.json and final audit appendix;
local extraction/integrity/relocated CUDA-OFF configure are checked separately.
No earlier experiment results are included in the source archive or overwritten.

Primary documentation consulted for compatibility/guide facts: CMake3.28
CheckLanguage, FindCUDAToolkit and CUDA_STANDARD; NVIDIA CUDA11 NVCC C++17,
CUDA runtime device/version APIs and driver/toolkit compatibility; official Colab
FAQ. Links are in the guide. These are documentation checks, not cloud experiments.

Integrity: all8,447 starting result files remain unchanged, including Phase6 smoke,
failed attempt/full retry, reports/figures/validation snapshots, earlier1M sorting
and Phase5 studies. All original frozen protocols remain byte-identical. All116
unmodified starting project files are protected; only the4 listed originals change.
Final reviewed source126 files, new readiness protocol and retained initial local
preflight are hash-verified. final_review.json and FINAL_AUDIT.md support completion,
commands_index.json/COMMANDS.md retain exact command statuses, reviewed_source
contains the saved source snapshot and changes.patch makes edits reviewable without
Git. Archive relocation evidence is source_bundle_validation.json.

Requested Phase7 preflight/guide milestone complete with **unavailable local CUDA**.
Limitations: GPU CMake branch and .cu compilation/execution are unverified; no CUDA
compiler/runtime version/device execution, sorting or performance evidence. GPU
readiness mocks are not hardware tests. Linux discovery is primary; other platforms
are best-effort/unvalidated. The tiny kernel checks device0 only, not all devices.
No privileged install/driver change, inferred acceleration or100M attempt.
Original Phase7 GPU sorter/timing objectives remain pending. Exact next GPU step:
allocate a supported cloud GPU, verify the source archive, run this guide/preflight
and isolated runtime smoke, then separately pin/license CUB and implement signed
sorting/differential checks plus synchronized H2D/algorithm/D2H/end-to-end metrics
under a new frozen protocol. Phase8/9/10 and deferred CPU research remain listed.

## Cloud GPU follow-up — Gate 1 blocked (user-requested Phase 8)

This follows the GPU milestone; it does not replace original roadmap Phase 8
learned-index/AlphaDev. Inspected AGENTS.md, roadmap/audit/README, cloud guide,
experiment protocol, CMake and Phase 7 final audit/source manifest/archive.
Workspace writable via anonymous temporary-file write; no Git metadata or Git
initialization. All 126 starting source hashes matched the Phase 7 manifest.
Before new evidence, all 8,656 raw/processed/figure files were hashed.

**Gate 1 did not pass.** No cloud GPU execution tool or remote runtime endpoint
is connected/provided. Available shell is local Linux. Colab/Kaggle/SSH markers
and gcloud/aws/jupyter were absent. SSH client presence is not remote access;
marker/tool absence alone cannot prove no remote GPU exists. No credentials,
SSH configuration or provider accounts were inspected. No cloud allocation,
remote execution, installation, driver/system change or paid provisioning was
attempted. inspection.json records access scope without secret values.

Archive verification exited 0: SHA256
f20581a4cb9b74ee8967485c259999f797fac0bbd44309ca1552aaaa2418c9f5,
127 members and 126 matching source files. Extracted into a new build-only path;
original archive unchanged. The archived preflight ran **locally**, exited 2,
classified gpu_driver_unavailable. Observed Linux 6.18.7-76061807-generic/x86_64,
CMake 3.28.3 and host GNU 13.3.0. PCI shows GA107M / GeForce RTX 3050 Ti Mobile
at 0000:01:00.0, with no bound driver/module/device nodes/version file, nvidia-smi,
nvcc, discoverable libcuda/libcudart or toolkit files. Runtime device count,
compute capability and driver/runtime/toolkit versions remain unknown. CMake
CUDA_STANDARD help success does not establish compiler support. CUDA configure,
build, enumeration/kernel checks were skipped, not passed. This is unavailable
readiness, not a CPU failure or diagnosis of broken hardware.

Archived CPU fallback configure/build/registry exited 0/0/0, CUDA/OpenMP/testing
OFF, all six original sorters listed. Testing OFF means no fallback CTest claim.
Fresh current Release configure/build/CTest and Debug ASan/UBSan configure/build/
CTest exited 0/0/0 each. Release **25/25** groups passed in 28.61s;
ASan/UBSan **25/25** in 83.81s. Leak detection remained enabled;
no ptrace limitation or detect_leaks=0 retry. All 22 readiness/build-isolation
methods passed per suite, including real default/explicit CUDA-OFF and mocked
states; mocks are not GPU evidence. Existing sorting/search/structure/OpenMP
checks passed unchanged. Captured configure/build output has no compiler warnings.
These are fresh invocations using existing CPU build directories; archive fallback
used a new build directory. CPU environment capture exited 0; its older 'GPU not
probed' field is distinct from the fresh preflight.

Twelve validation command records: archive verification 0; local preflight 2
(expected unavailable); fallback configure/build/registry 0/0/0; Release configure/
build/CTest 0/0/0; sanitizer configure/build/CTest 0/0/0; environment capture 0.
Exact argv/cwd/status/timestamps/stdout/stderr: commands/*.json, commands_index.json
and COMMANDS.md under results/raw/gpu_cloud_gate1_20261009T211734154323Z.
One editing-helper generation command exited 1 with a nested Python quoting
SyntaxError before executing/writing files; corrected with a literal heredoc.
editing_diagnostic.json records the failure. No failed validation command was
silently ignored. No CUDA-ON attempt, GPU correctness test or GPU timing trial ran.

Modified only README.md and docs/ROADMAP.md (blocked status/next action),
docs/ALGORITHMS.md (no CUB), docs/BENCHMARKING.md (no GPU schema/results),
docs/EXPERIMENT_PROTOCOL.md (environment gate), docs/AUDIT.md (this evidence).
No algorithms, CMake, scripts/tests, vendors/licenses or versioned protocols
changed. All 120 other original source files and all 8,656 earlier result
artifacts remain byte-identical, including frozen sorting/Phase 5/6 studies,
failed attempts and Phase 7 evidence/archive. Source manifests, changes.patch
and final_review.json retain integrity/review results. The old cloud guide and
readiness protocol remain unchanged. No new GPU sorting contract was created.

Completion statuses: cloud validation **blocked/not passed**; CUB implementation/
correctness **not started/not run**; GPU smoke **not run**; full GPU study **not
run**. Gates 2–4 are deferred per the user. Requested Phase 8 GPU task is incomplete.
BLOCKED.json records a gate outcome, never completed-study status. No acceleration
or100M execution claimed. Evidence: results/raw/gpu_cloud_gate1_20261009T211734154323Z/FINAL_AUDIT.md,
local_preflight/report.json, archive_verification.json, cpu_environment.json,
COMMANDS.md, final_review.json, prior_artifacts_sha256.json and source manifests.

Exact next action: allocate/connect an NVIDIA cloud development runtime, transfer
and verify the retained Phase 7 source archive, then follow
[CUDA_EXECUTION_GUIDE_v1.md](CUDA_EXECUTION_GUIDE_v1.md). From verified source run:
```sh
python3 scripts/cuda_preflight.py --output results/raw/NEW_CLOUD_PREFLIGHT
```
Require exit 0/operational, actual model/compute capability, driver/runtime/toolkit/
compiler metadata, enumeration and checked kernel. Retain exact cloud commands
and CPU fallback evidence outside ephemeral storage. Only then define Gate 2's
new GPU sorting contract, pin/license CUB, and implement signed-int32 differential
checks with separate synchronized transfer/device/end-to-end metrics. Cloud guide
execution remains unvalidated here because no cloud runtime was available.

## Post-cloud validation — first CUB correctness slice, hardware validation pending

Inspected AGENTS.md, README/roadmap/audit/protocols, CMake/CUDA isolation, existing
CPU and parallel sorter interfaces/registries/implementations, differential tests,
preflight and runner conventions, Phase7/blocked-gate records and new cloud archive.
Git status/branches/log each exit128: no Git metadata, branches/commits/uncommitted
status unavailable; no Git initialization/commit/push. Anonymous temporary-file
write verified access. Source before: 127 files including .gitignore,
backup under build/cub_sort_review_20261009T220322089788Z; all 8,709 earlier results/evidence files
hashed before edits. No existing user source was discarded.

Initial root-level cloud archive lookup failed (ls2, sha256sum1, tar2), resolved by
file search to results/evidence/cloud_validation_evidence.tar.gz before extraction.
Archive SHA256 matches 48b3e78360e7c0c1721c21a3879bc975b902f5b3603fa25a0c92230c695c0810.
Listed members first; safely extracted to new results/raw/cub_sort_validation_20261009T220322089788Z/cloud_evidence. Preflight marker
hashes and four reported source hashes match the starting code. Historical Colab
report: Tesla T4, compute7.5, driver580.82.07, nvcc13.0.88, runtime/driver API13000,
CMake3.31.10, host GNU13.3.0, device0 checked kernel success. Actual preflight
configure/build/runtime return0; retained LastTest logs have23 CPU passes/0 failures
(OpenMP OFF) and1 CUDA-runtime pass/0 failures. The CUDA log's24/24 ordinal is a
filtered test index, not24 GPU tests. External full command transcript/exit statuses
for the cloud CPU build/CTest are not in the archive; LastTest.log and the CPU cache
support successful tests/Release configuration, not invented missing commands.
This proves historical readiness, not new CUB sorting or a currently connected GPU.
cloud_evidence_review.json records precisely that scope. Prior extracted cloud
evidence and original archive are unchanged.

Baseline fresh Release configure/build/CTest: exit0/0/0,25/25 groups,27.49s.
No baseline correctness defect found. CUDA_SORT_PROTOCOL_v1.md was saved/hash-frozen
before implementation. Separate cub_radix_sort_v1 adapter: signed-int32 full-width
CUB SortKeys, per-call device input/output/scratch and host output, checked API/
launch/sync/copy/cleanup, caller host mutation only after successful cleanup. Empty/
singleton require an available device then no-op; no CPU fallback. Length/byte
bounds checked; no abs/signed overflow. Existing Sorter shape reused in a separate
GPU registry; CPU six-entry registry/std_sort and all timing implementations stay
unchanged. No performance timing or CUB comparison metric implemented.

Dependency reference: NVIDIA CCCL v3.0.0, resolved commit
 e944297b0b51a8e9c0f1b30425370c31c1c0e0a0. Revision-qualified SortKeys/version/license
bytes verified against reviewed tag downloads. CUB is BSD-3-Clause, unchanged
aggregate LICENSE/attribution/provenance retained in third_party/cub. Toolkit
headers used without network fetching or upstream modification. Sorting opt-in
MAB_ENABLE_CUDA_SORT=OFF by default requires CUDA ON/toolkit>=13.0; readiness-only
CUDA path/minimum remains unchanged. CUB_VERSION300000 and two reviewed header
hashes are enforced. Actual installed cloud CUB identity is absent from the old
archive: a mismatch is an explicit dependency-review blocker, not a hidden bypass.
Cloud runner records transitive cub/thrust/cuda header hashes when configure passes.

GPU-only test source includes475 expected inputs/1900 output checks through public,
registry, interleaved/repeated calls, extrema/mixed signs/duplicates/sorted/random/
all generator distributions and lengths0..65537 including non-power-of-two and
boundary neighbors. These counts are **planned, not executed GPU results**. Default
CPU suites do not register GPU sorting. The cloud runner demands actual direct
sort-test success and a genuinely selected/passed CTest; skip77, empty selection,
malformed/incomplete output, failed subprocess, source changes or unavailable
preflight prevent COMPLETE. Exclusive paths, manifests/command diagnostics and
FAILED/INTERRUPTED markers preserve incomplete attempts. No resume/overwrite.

Local affected CUDA configure: exit1, CUDA compiler NOTFOUND (no nvcc); sorter
compilation and execution **not run**. Fresh local preflight exit2 remains
gpu_driver_unavailable. No driver/package/system changes and no live Colab endpoint
available to this agent. A versioned handoff guide and new source archive are
provided for user-run GPU validation, not represented as a tested cloud sorter.

Final reviewed fresh Release configure/build/CTest exit0/0/0:26/26 groups,
27.97s. Debug ASan/UBSan configure/build/CTest exit0/0/0:
26/26,82.91s, leaks enabled. No ptrace limitation or
detect_leaks=0 retry. Eleven new host tooling methods pass standalone and in both
final suites: schema/count validation, skip/empty CTest rejection, unavailable/
timeout/interruption diagnostics, output/symlink collisions, redaction, invalid
CLI and CUDA-SORT-with-CUDA-OFF rejection. These are host/synthetic record tests,
not mocked evidence of actual GPU sorting. Existing CPU sort/search/structure/
OpenMP tests remain passing; all22 preflight methods pass. Earlier intermediate
26/26 runs precede the final CTest-result-validator test and are retained separately.
CPU environment capture exit0. Captured CPU configure/build output has no compiler
warnings; new GPU compiler warnings cannot be reviewed before a CUDA build.

Exact argv/cwd/timestamps/exit/stdout/stderr: results/raw/cub_sort_validation_20261009T220322089788Z/COMMANDS.md,
commands_index.json and commands/*.json. Nonzero commands are the explained Git
metadata errors128, unavailable CUDA configure1 and readiness2; initial misplaced
archive lookup is recorded in initial_lookup_diagnostics.json. No failed check is
silently treated as successful. Local full suites:26 passed/0 failed/0 skipped each.
New GPU sorting test:0 executed,1 group unexecuted (not registered in CPU-OFF tests).
Historical cloud runtime smoke:1 passed; historical cloud CPU:23 passed.

Files added: include/algorithms/cuda_sorting.hpp, src/cuda/cub_sort.cu,
tests/test_cuda_sorting.cpp, scripts/validate_cuda_sort.py,
tests/test_cuda_sort_handoff.py, docs/CUDA_SORT_PROTOCOL_v1.md,
docs/CUDA_SORT_VALIDATION_GUIDE_v1.md, third_party/cub/README.md/LICENSE/UPSTREAM.json.
Modified: CMakeLists.txt, cmake/cuda.cmake, README.md and docs/ROADMAP.md/AUDIT.md/
ALGORITHMS.md/BENCHMARKING.md/EXPERIMENT_PROTOCOL.md. Existing CPU algorithms/tests,
vendors/licenses and old versioned protocols/studies/results stay unchanged.
Final manifests/change patch/integrity audit retained under results/raw/cub_sort_validation_20261009T220322089788Z.

Current phase: original roadmap Phase7 CUDA, requested post-cloud GPU continuation;
original Phase8 learned-index/AlphaDev remains pending. Runtime readiness validated
historically; first sorter source/build/tests/docs delivered but GPU compilation/
correctness **pending**. GPU timing/smoke/full study **not started**. No acceleration,
GPU benchmark measurements, significance or100M claim. The repository is ready
for cloud correctness handoff, not for the next research phase or timing study.

Exact next step: use the new cub_sort_source.tar.gz (source_bundle.json has its hash)
and docs/CUDA_SORT_VALIDATION_GUIDE_v1.md on an allocated supported cloud GPU.
After source verification, run:
```sh
python3 scripts/validate_cuda_sort.py --output results/raw/NEW_CUB_CORRECTNESS
```
Retain/persist COMPLETE or failed-attempt evidence and return the archive/hash for
review. Only observed build/475-case/1900-check success permits the separate GPU
timing contract/engine. If installed CUB mismatches the pin, retain actual hashes
and review that version explicitly before changing the frozen design.

## CUB handoff final review revision2 — GPU correctness still pending

Final output-safety review found that resolving the requested path before mkdir
could follow a dangling symlink. Corrected to preserve the final path component
with Path.absolute(), so exclusive mkdir rejects existing and dangling symlinks.
New regression verifies no subprocess or target creation. Twelve host handoff
methods now pass. This is a host runner fix, not a CUDA algorithm change.
The initial source bundle/audit and all earlier validation evidence remain intact.
Use CUDA_SORT_VALIDATION_GUIDE_v2.md and cub_sort_source_v2.tar.gz for the corrected
handoff; v1 is retained history. Frozen CUDA_SORT_PROTOCOL_v1.md is unchanged.

Fresh narrow tests and Release configure/build/CTest all exited0:26/26 groups,
28.88s. Fresh Debug ASan/UBSan configure/build/CTest exited0:
26/26 groups,80.80s, leak detection enabled, no ptrace retry.
Zero failed/skipped CPU groups;12 host methods pass standalone and in each suite.
GPU sorting remains uncompiled/unexecuted:1 GPU test group unexecuted,475 expected
inputs/1900 expected output checks, not passes. Earlier local CUDA configure1
(no compiler), preflight2(unavailable), Git128(no metadata) and historical T4
runtime/cloud-CPU evidence remain exactly as recorded in the initial audit.

The first candidate bundle's137 files were also independently extracted/hash
verified, relocated CUDA/CUDA-SORT/OpenMP/testing OFF configure/build/registry
returned0/0/0 and six CPU sorters; that fallback had testing OFF. Correction changes
only host handoff/script/test/docs; CUDA adapter/CMake are unchanged. The corrected
bundle is separately source-hash verified and preserves every original result.
All 8,709 pre-task artifacts and all 8,798 pre-correction artifacts
(including first candidate archive and its relocation evidence) remain unchanged.
Current source differences/patch/manifest and final_review.json are retained here.

Evidence: results/raw/cub_sort_final_review_20261009T222209607981Z/COMMANDS.md, commands/*.json and FINAL_AUDIT.md.
Initial audit/evidence: results/raw/cub_sort_validation_20261009T220322089788Z/FINAL_AUDIT.md and COMMANDS.md.
No CUDA implementation validation, GPU smoke, full study, timing values or100M run
is claimed. No system configuration, driver change, commit or push. Current
roadmap CUDA work is incomplete; ready for corrected cloud handoff only.

Next: transfer the corrected v2 archive using source_bundle.json's SHA256, verify
its source manifest, follow docs/CUDA_SORT_VALIDATION_GUIDE_v2.md and run:
```sh
python3 scripts/validate_cuda_sort.py --output results/raw/NEW_CUB_CORRECTNESS
```
Preserve/return full success/failure evidence. Actual installed CUB must match the
reviewed version/header pin or be deliberately reviewed before any pin update.
Only observed GPU sorting success permits the separate timing milestone.

## Actual Colab CUB sorter validation — correctness passed

The existing Tesla T4 session compiled/executed cub_radix_sort_v1. Direct test
passed475 inputs/1900 checks; targeted CTest repeated the suite and passed1/1,
zero failures/skips. Fresh configure/build/test/CTest and runner exited0. Original
v2 archive SHA256 matched locally/remotely; first configure exited1 on installed
CUB3.0.1 versus the initial3.0.0 pin. Failed attempt retained. Independent official
CCCL commit f19d875da0d8bfb2e38c109b2b40522b8abbbbc3 review verified installed
headers and unchanged license; exact pin/result identity updated under frozen
CUDA_SORT_PROTOCOL_v2.md, original protocol/bundles unchanged. No algorithm or
fixture replacement. A separate CLI prelude connection stall was interrupted
locally (child-15), then recovered on the same session; no new GPU/reset.

Hardware Tesla T4/7.5, driver580.82.07, nvcc13.0.88/runtime API13000, GCC13.3.0,
CMake3.31.10. Both fresh preflights verified device0 kernel. Build emitted100
nvcc-generated GCC line-directive warnings under host -Wpedantic; all retained,
none suppressed. Fresh final CPU Release26/26,28.36s and ASan/UBSan26/26,80.21s
passed (configure/build/CTest all0), leaks enabled, no ptrace retry.12 host handoff
methods and22 preflight methods pass; CPU sanitizers do not validate device memory.

Downloaded archive fda8f0107e04975068a5db5217d5996984c4a6e92a2b267f5910acd8308a7a4b
contains611 hash-verified files and1688 dependency hashes. All8,825 previous result
artifacts and16 protected source/protocol/license files match starting hashes.
No Git metadata (status128), commits, pushes, driver/package changes or new GPU.
Exact commands/statuses, failure/connection diagnostics, source patches/manifests
and integrity evidence: results/raw/cub_correctness_colab_20261009T223853955936Z/COMMANDS.md
and FINAL_AUDIT.md. Successful raw records: downloaded/retry1/NEW_CUB_CORRECTNESS/
{COMPLETE,sorting,ctest,build}.json beneath that directory; failed original:
downloaded/attempt1/NEW_CUB_CORRECTNESS/{FAILED,configure}.json.

Correctness milestone complete; full CUDA phase remains open. Next freeze/implement
separate H2D/device/D2H/host end-to-end timing and validate a small GPU benchmark
smoke. No performance measurement/study, speedup or100M claim.


## Separate CUB GPU timing milestone — validated 2026-10-09 UTC

Protocol CUDA_TIMING_PROTOCOL_v1.md was saved before implementation/execution.
Separate prepared timing library/executable leaves production adapter, reviewed
CUB3.0.1 pin, all vendors, CPU algorithms and defaults unchanged. CUDA-event
H2D/device-sort/D2H and host steady_clock end-to-end are separately labelled;
allocations/setup, staging, output-vector copy and correctness checks are excluded.
End-to-end includes enqueue/dispatch/check/wait/transfers/sort. Details, exact
commands/statuses and files changed: [FINAL_AUDIT](../results/raw/cuda_timing_20261009T231303050084Z/FINAL_AUDIT.md),
[COMMANDS](../results/raw/cuda_timing_20261009T231303050084Z/COMMANDS.md), [CHANGES](../results/raw/cuda_timing_20261009T231303050084Z/CHANGES.md).

Fresh exclusive CPU Release configure/build/CTest passed27/27 groups; fresh Debug
ASan/UBSan configure/build/CTest passed27/27, ASAN_OPTIONS/LSAN_OPTIONS unset and
UBSAN_OPTIONS=halt_on_error=1, leak detection enabled. No CPU compiler warnings.
The new analysis group passes12 host methods and explicitly skips2 GPU methods.
No CTest group was skipped. The previous Colab session was expired; one replacement
T4 was created, with driver580.82.07, nvcc/toolkit13.0.88, runtime13000, compute7.5,
GCC13.3.0, CMake3.31.10. Actual checked kernel/preflight passed. Correctness rerun
passed475 inputs/1900 outputs directly and again through1/1 CTest. New benchmark
compiled and executed; actual GPU framework passed14/14 methods,1/1 targetedCTest,
including60 validation-only size/workload configurations. No CPU substitution.

Smallest primary smoke:1025/uniform/1729,W1/R5,5 measured/1 warmup. Matrix:
N0/1/1025/65537,six distributions,two seeds,W1/R5,48 complete configurations,
240 measured/48 warmups. Overall245 measured/49 warmups, zero failed/missing;
all outputs equal std::sort outside timers. Raw four-field schema/nonnegative
values and all196 metric-statistic groups independently verified. Cloud summaries
regenerate byte-for-byte; two local regenerations match byte-for-byte, with all
local/cloud statistics identical (absolute source paths correctly relocate).

New evidence: [results/raw/cuda_timing_20261009T231303050084Z](../results/raw/cuda_timing_20261009T231303050084Z); downloaded raw at `downloaded/raw`, processed
summaries/report at [results/processed/cuda_timing_20261009T231303050084Z](../results/processed/cuda_timing_20261009T231303050084Z).
Source bundle SHA256 fa7c1d2fc131ba832a5c357498a6c1523c3eeeea99d6c7c4478df30d04ab0f73
matched locally/remotely; retrieved archive SHA256
236b32018d74ac5be6252df130038eadcbc95169509107bd6d3e7ea323290c41 matched;
1115 packaged files verified. All9568 prior result files match starting hashes.
Exact pin, production adapter and frozen protocols are protected by source review.
No Git metadata exists (`git status`128); no Git initialization/commit/push.

GPU warnings:100 production and161 prepared translation-unit generated GCC
line-directive extension diagnostics under existing -Wpedantic; no other warning
category, suppression, CUB incompatibility or pin change. Fixture exit9/timeouts/
collisions are intentional tested failures; no actual benchmark/build failure.
CPU sanitizers do not instrument device code; Compute Sanitizer was not run.
Clock/thermal/background control unverified; post-run probes are labelled after
measurements. API float-ms precision limits small event intervals. No GPU speedup,
full GPU study, allocation-inclusive adapter measurement or100M run is claimed.
The smoke performance infrastructure milestone passes; next freeze a <=1M
controlled GPU/CPU study with explicit matching timing scopes/resource estimates.

## Controlled CPU/GPU protocol freeze — no experiment executed

Evidence: [results/raw/cpu_gpu_protocol_20261009T234954580281Z/FINAL_AUDIT.md](../results/raw/cpu_gpu_protocol_20261009T234954580281Z/FINAL_AUDIT.md).
Read the requested previous final audit, changes, final command records, processed
report, integrity files and timing protocol; inspected CPU/GPU adapter/timer/registry,
dataset and analysis code. No Git metadata exists (`git status --short` exit128);
workspace is writable. No implementation or vendored source changed.

Saved [protocol](CPU_GPU_COMPARISON_PROTOCOL_v1.md),
[matrix](studies/cpu_gpu_comparison_v1.matrix.json),
[resource estimates](studies/cpu_gpu_comparison_v1.resources.csv) and
[freeze manifest](studies/cpu_gpu_comparison_v1.freeze.json). Main plan: 48 datasets,
1200 measured + 240 warm-up calls; pilot: six datasets, 150 + 30. Neither ran.
Primary ratios require allocation-inclusive host-vector API calls on the same
cloud machine. Prepared four-metric measurements remain explicitly incompatible
with that CPU scope. Comparison driver, paired analyzer and workspace-query helper
remain unimplemented. CUB3.0.1 pin/adapter and old protocols are unchanged.

Fresh targeted CTest using unchanged existing Release binaries passed 3/3 groups
(`datasets`, `timing`, `cuda_benchmark_analysis`), exit0: 220 distribution/size/seed
cases plus frozen swap/other fixtures; 72 timing inputs/1296 validated trials;
14 Python methods ran, 12 passed and two GPU methods explicitly skipped. No fresh
build, full-suite sanitizer run or GPU execution was performed for these planning
changes. Previous 27/27 Release/ASan-UBSan evidence and Tesla T4 smoke results were
verified as historical only. The 14 new host-only protocol validation methods all
passed, including byte-for-byte regeneration and rejection fixtures.

All 10755 prior result files and the sealed 1186-file previous GPU-smoke manifest
were verified before changes; final integrity evidence verifies them again plus
protected source/protocol/license files. Two initial README patch attempts failed
context matching without modifying files; corrected append succeeded. No build,
test or experimental failure occurred in this task. Exact validation commands,
exit statuses and editor diagnostics are retained in the new evidence directory.

Resource numbers are calculated payloads/policy caps; N1M and adapter CUB workspace
sizes remain unmeasured. Runtime estimates use a different-host CPU proxy and
explicit unmeasured GPU allowances, not performance observations. Current Colab
availability was not queried. Next: review freeze, implement/test missing tooling,
fresh environment/workspace/correctness checks, then authorize the pilot. No full
comparative GPU study, 100M workload, ranking or phase-wide completion is claimed.


## Controlled CPU/GPU driver and frozen pilot — final v3 accepted

Evidence: [FINAL_AUDIT.md](../results/raw/cpu_gpu_pilot_20261010T001232473460Z/FINAL_AUDIT.md),
[exact commands/exit statuses](../results/raw/cpu_gpu_pilot_20261010T001232473460Z/COMMANDS.md),
[raw pilot](../results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/),
[processed report](../results/processed/cpu_gpu_pilot_20261010T001232473460Z/REPORT.md).
No Git metadata (`git status --short`128), workspace writable. Inspected requested
frozen protocol/matrix/resources/freeze and previous audit, CUB pin/adapter,
prepared timer, datasets, CPU/OpenMP adapters, CMake and tests before editing.
All three frozen hashes match; freeze manifest and production anchors remain
unchanged. Only additive reviewed CMake integration changes a protected anchor.

Added isolated host comparison/input library, CUDA workspace diagnostic and worker,
pilot-only prerequisite validator/runner, independent paired analyzer, two CTest
groups and implementation guide. Existing algorithms/registries/defaults, CUDA
pin and timing families remain unchanged. Host API timing includes per-call
allocation/free and production transfers/synchronization; prepared four metrics
remain diagnostic-only. Attempts and samples flush independently; output collisions,
failed subprocesses and incomplete records never become successful completion.

Fresh local configure/build/full CTest: Release29/29 and ASan/UBSan29/29, exit0;
final reruns33.45s/136.67s. Leak detection enabled; no ptrace limitation reproduced.
Cloud final fresh CPU Release29/29, ASan/UBSan29/29 and GPU Release32/32 all exit0.
New comparison engine60 inputs/3600 trial checks and Python22 methods pass.
Existing host-only CUDA analysis skips two GPU methods explicitly; separate GPU
framework14/14 methods actually pass. CUB direct test and CTest each pass475 inputs/
1900 output checks. CPU builds zero warnings. CUDA build341 warnings, exclusively
nvcc-generated GCC line-directive extensions under existing -Wpedantic; retained,
reviewed and unsuppressed. No CUB incompatibility/pin change or other warning type.

Actual final environment: Tesla T4 compute7.5, driver580.82.07, runtime API13000,
CUDA/nvcc13.0.88, GCC13.3.0, CMake3.31.10, OpenMP4.5/libgomp, Linux6.6.122+.
Release C++17/CUDA17 -O3 -DNDEBUG, architecture75; no sanitizer instrumentation in
primary timing. Two logical CPUs share one physical SMT core; cpu.max=max100000,
memory.max=max. Known headroom checks passed. Frequency/thermal/cache/background
exclusivity are not controlled. Actual OpenMP workers1 below32768 and2 above.

Exact pilot: N1025/1M x uniform/duplicate_heavy/signed_edges, seed1729, five modes,
W1/R5 and frozen deterministic order. All150 measured and30 warm-ups passed full
oracle equality; failed/interrupted/missing/duplicate counts0. Primary144 total rows
(120 measured/24 warm-ups), prepared36 (30/6), with four metrics per prepared call.
Both workspace queries/isolated successful cudaMalloc request sizes are1 byte at
N1025 and4,178,687 bytes at N1M. Production allocations remain uninstrumented;
combined device payload formulas16,402/24,357,374 bytes and host24,600/24,000,000
bytes are calculations, not measured physical allocations. Linux process peak RSS
111,529,984..133,550,080 bytes includes context/runtime/all modes, not isolated GPU
or algorithm memory. Frozen resource CSV was not modified.

Two cloud and two local summaries match byte-for-byte, SHA256
07e69e2e0c8853f93d3f3da895337b5e4b72e5e2dd0ff0577db3cbd1f7053a22.
Independent retained-row formulas match48 metric groups and18 allowed host-call
ratios; all118 raw-manifest files match. Downloaded archive SHA256
 eafcccf97c9f2077d01e8d819bb377161f5c6e8d6402072d242861ffe518285a,
174 members verified. Executed source v2 SHA256
 a923e54fb4d8323496c2e49342775d481b12af6b84bbafb4f2611614cb777510
matches locally/remote; current code matches GPU-tested source exactly. All10,791
previous result artifacts and protected source/protocol/pin hashes match final
integrity verification. No previous result was overwritten or regenerated.

Failures preserved: first visible session disappeared404/401 before successful
upload; replacement authorized. Remote v1 stopped before preflight because build/
parent was absent; fixed narrowly and covered by a clean-checkout regression.
Corrected v2 reached sanitizer compilation but expired before final evidence
retrieval; final/pilot outcome unknown, excluded. Owned hung CLI command terminated
(SIGTERM/-15), no user data removed. Final v3 repeated all prerequisites in new paths
and passed. Colab CLI can return0 despite a Python exception, so remote result/
completion records were independently checked. Two evidence-only report-generator
syntax errors and one invalid documentation patch were corrected; diagnostics
retained, no raw timing or production code changed by those failures.

This milestone delivers validated driver/analyzer and an accepted pilot, not the
full1200-measurement study. Pilot wall7.360s; fresh remote validation541.073s.
An8x count-only main-run proxy is about59s plus fresh prerequisites, not a measured
forecast; N65537/distributions/current conditions still need review and fresh
workspace sizing. Exact next step: review pilot/resource evidence, then separately
authorize main execution. Single seed, shared/cloud frequency/thermal/load, float-ms
event precision and non-isolated RSS limit interpretation; no CI/significance or
universal performance ranking. CPU sanitizers do not cover device code; Compute
Sanitizer was not run. No full study,100M run, commit, push or driver installation.

Final integrity helper initially compared the additive CMake diff with a post-integration archive and rejected that wrong baseline (exit1). Corrected v2 uses the historical pre-comparison archive and requires its exact frozen CMake SHA256. No source/data change was needed; the failed review is retained in INTEGRITY_REVIEW_ATTEMPT1.json.

## Fresh-environment N=65537 workspace/resource validation

Evidence: [FINAL_AUDIT.md](../results/raw/cub_workspace_65537_20261010T110457531249Z/FINAL_AUDIT.md),
[commands](../results/raw/cub_workspace_65537_20261010T110457531249Z/COMMANDS.md),
[independent verification](../results/raw/cub_workspace_65537_20261010T110457531249Z/INDEPENDENT_VERIFICATION.json).
All frozen hashes, accepted pilot seal and protected source identities verified.
No Git metadata (status128). New Colab session created after sessions reported none;
actual Tesla T4 compute7.5, driver580.82.07, CUDA runtime/driver API13000,
nvcc13.0.88, GCC13.3.0, CMake3.31.10, OpenMP4.5/libgomp, Linux6.6.122+.
Fresh Release configure/build of existing cpu_gpu_comparison diagnostic passed0;
no production code/interface/pin change. CUDA retained341 known generated
GCC line-directive extension warnings; no other warning category. All1688 installed
CCCL file hashes match the accepted pilot, as do local/remote source archive hashes.

Only --resources65537 ran: both signed-int32 full32-bit SortKeys workspace queries
return279295 bytes and both diagnostic allocations/checked cleanup succeed0.
Free device memory before buffers15527116800 bytes; combined payload formula
1607182 bytes, known host payload1572888 bytes. Host MemAvailable12532940800 bytes,
disk75447238656 bytes; CPU/memory cgroup maxima unlimited, affinity2 logical CPUs
on one physical SMT core. Frozen workspace/combined/half-free/host/disk gates pass.
Requested bytes do not measure allocator physical footprint; diagnostic uses one
key-buffer pair while the combined formula budgets two concurrent pairs.
Production allocation semantics and frozen estimates are unchanged.

Downloaded archive/inner result/completion marker/resource formulas independently
verified; CLI exit0 alone was not accepted. No new performance or correctness
trials, CTest or sanitizer suite: unchanged-code milestone requested queries only;
accepted pilot's suites remain historical. All11165 prior result files and136
current source files unchanged; final evidence manifest records exact hashes.

Resource gate GO; full-study launch NO-GO now pending separate authorization,
reviewed/tested full-matrix tooling and fresh prerequisites/all-size gates.
Pilot variability includes small uniform prepared D2H sampleCV65.34%, small
signed-edge sequential merge32.82%,1M uniform prepared device sort17.00%; all
five-trial samples retained, no independent-session uncertainty or significance
claim. Cloud frequency/cache/thermal/background exclusivity remain uncontrolled.
No pilot rerun,full1200-measurement study,100M run,commit,push or cleanup.

## Full frozen CPU/GPU orchestration and analysis tooling

Evidence: [FINAL_AUDIT.md](../results/raw/cpu_gpu_full_tooling_20261010T121208603276Z/FINAL_AUDIT.md),
[commands/statuses](../results/raw/cpu_gpu_full_tooling_20261010T121208603276Z/COMMANDS.md),
[downloaded GPU verification](../results/raw/cpu_gpu_full_tooling_20261010T121208603276Z/INDEPENDENT_GPU_VERIFICATION.json).
Read instructions/current tooling/frozen inputs/accepted pilot/latest resource audit;
verified frozen hashes and both earlier seals before editing. Git status128 confirms
absent metadata; no initialization/commit/push. All11228 prior result files preserved.

Added isolated run_cpu_gpu_study.py, shared matrix-part orchestration, strict full
analysis, prerequisite-only validation, synthetic tests and tooling documentation.
48 datasets/five modes/W1/R5/1200 measured+240 warm-ups are taken from the exact
frozen matrix; three-size resource and frozen60s-dataset/1800s-study gates remain.
All command/attempt/failure evidence and planned identities are retained; no resume
or overwrite. Prepared diagnostics remain separate and never ratio denominators.
Incomplete studies cannot provide paired/cross-input summaries. Production/CUB/
CMake/frozen assets are unchanged. The public CLI rejects synthetic results.

Fresh CPU Release configure/build and selected correctness/metrics/synthetic CTest
passed19/19; fresh Debug ASan/UBSan configure/build/selection19/19, leak detection
enabled, no ptrace failure. Final current framework50/50 methods pass with Release
and sanitizer input binaries. An earlier45/48-method selection preceded the final
two prerequisite-only tests; retained logs distinguish these runs. Full29-group
CPU suites were not run because their timing/framework paths violate this task's
exclusion. Initial standalone run collected41 methods with one explicit missing-input-tool skip
and two unclosed-file ResourceWarnings; final supplied-tool runs50/50 have no skips
or ResourceWarnings. CPU compiler warnings0.

Deviation: initial20-group selection included parallel_mergesort, whose end of
correctness test invokes six timing rows atN32768: two algorithms, W1/R2, four
measured calls and two warm-ups. This was overlooked, disclosed and excluded from
all subsequent runs; durations were not serialized or used as study observations.
The original log remains. No benchmark executable, pilot/full comparison or GPU
timing workload was launched. No claim of zero CPU timing calls is made.

Colab initially had no active session; reconnected fresh T4 session
cpu-gpu-full-tooling-20261010T121208Z. Fresh GPU Release configure/build and explicit
non-timing allowlist passed21/21 groups;50 framework methods,475 actual CUB input
cases/1900 output checks and actual runtime kernel passed. Eleven timing-related
groups were excluded. Host-only CUDA analysis deliberately skips its two GPU
timing methods, including on the GPU VM; no GPU timing framework coverage claimed.
Source archive local/remote hash matches; current source matches GPU-tested source.
Driver580.82.07/runtime13000/nvcc13.0.88, GCC13.3.0,CMake3.31.10,OpenMP4.5/libgomp,
Linux6.6.122+, TeslaT4 compute7.5. All1688 CCCL file hashes match accepted pilot;
CUB3.0.1 commit unchanged. CUDA compiler retains341 known generated GCC line-
directive extension warnings; no other category/suppression/incompatibility.
CPU sanitizer checks do not cover device code; Compute Sanitizer was not run.

Independent download SHA256/15 inner hashes, completion/exit records, source,
GPU correctness and dependency identity verified. Accepted pilot summary SHA256
07e69e2e0c8853f93d3f3da895337b5e4b72e5e2dd0ff0577db3cbd1f7053a22
regenerates unchanged. Full dry-run plans48 command pairs without output/workload;
complete synthetic1440-record fixtures validate counts/statistics/regeneration,
failure/interruption/missing/duplicate/identity/scope/resource/thread cases and
production-only ratios. Synthetic completion console messages are explicitly
labelled mocks and are not measurements. No real full study/pilot/100M experiment.

Tooling is validated under these recorded tests and limitations; study launch
remains **NO-GO** until review, separate authorization and fresh complete study
prerequisites/resource gates. The prerequisite-only full-suite command was tested
with mocks, not executed here; it includes timing-framework tests and needs later
authorization. Shared-cloud load/SMT/thermal/frequency/cache controls remain
uncontrolled. Next: review tooling/deviation, then authorize fresh prerequisites
and the unchanged study separately. No frozen protocol change is proposed.

## Provenance and non-timing selection repair

Evidence: [FINAL_AUDIT.md](../results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/FINAL_AUDIT.md),
[commands and safety classifications](../results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/COMMANDS.md),
[final selection](../results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/SELECTED_TESTS_FINAL.json),
[synthetic original reproducer](../results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/FULL_ANALYSIS_PROBE.json).

Read the latest independent review before edits and checked its retained seals.
The analyzer previously compared mutually consistent mutable source claims;
it now derives expected adapter/pin/code identities from an independently pinned
freeze and its verified matrix, with only the existing pinned CMake exception.
The exact previously accepted 1440-record synthetic reproducer now rejects the
changed production-adapter digest, while its baseline remains accepted.

Prerequisite-only selection previously included timing-bearing CTest groups.
A reviewed source/command manifest now selects 19 CPU correctness groups, excludes
all ten timing groups including parallel_mergesort, and rejects unknown commands,
sources, tests and fixture/dependency/environment scheduling. Its CUDA correctness
opt-in selects 21 groups, never the GPU benchmark framework. No selected CTest
suite, prerequisite validator or GPU work executed during this repair.
Correctness-only prerequisite manifests cannot satisfy the frozen full-study gate.

Final focused methods22/22 and existing synthetic framework50/50 pass, no skips.
The initial focused attempt ran21 methods with three failures/one error because
legacy code-only source maps omit frozen documentation; the repair checks that
document directly without weakening code anchors. That failed attempt is retained.
Accepted pilot summary regenerates byte-for-byte, with no measurements launched.
No fresh build, Release/ASan suite, GPU suite, pilot or full study is claimed here.
Git status128 confirms absent metadata; no repository initialization occurred.

All11345 pre-existing result files, four frozen assets, production source,
protected anchors, CMake review and CUB3.0.1 pin are preserved; exact comparisons
and final evidence hashes are retained. Full-study launch remains **NO-GO**,
pending independent repair review and separately authorized fresh prerequisites,
resources and study execution. This repair stops at the audit.

## CTest build-hook guard repair (inert validation only)

The independent review found that CTest discovery preceded validation and that
directory hooks/includes were outside the JSON selector. The repair adds a
static flat-registry guard shared by the CLI, retained-discovery selection and
the prerequisite helper. It rejects hooks/includes/subdirectories and unreviewed
commands/properties before discovery, with fingerprint rechecks before execution.
No frozen source, production adapter, CUB pin or historical artifact changed.

Evidence: [repair audit](../results/raw/ctest_hook_repair_20261010T223851377458Z/FINAL_AUDIT.md),
[commands](../results/raw/ctest_hook_repair_20261010T223851377458Z/COMMANDS.md),
[inert rejection proof](../results/raw/ctest_hook_repair_20261010T223851377458Z/REJECTION_PROOF.json),
[guard contract](CTEST_BUILD_GUARD_v1.md).

Final focused Python validation passes 28 new guard methods and 11 existing
selector methods (39/39, no skips). Real subprocess launch was blocked in the
tests; fake discovery/execution callbacks returned literal fixture data. The
previous review's exact inert hook fixture is rejected with zero callback calls.
The first 26-method run had one error from rejecting a normal P4Command Dart key;
its log and source snapshot remain retained. Static review also corrected the
CUDA backtrace stack policy using retained generated metadata, then retested it.
An initial policy-derivation assertion exposed the existing python3 symlink;
canonical path comparison fixed it without weakening argument matching. A
documentation patch context mismatch made no changes and was corrected.

Direct before/after checks verify all 11,448 prior result files (11,345 historical,
46 earlier repair and 57 independent-review files), 26 protected anchors, four
frozen assets including the pinned freeze, 80 production/header/dependency files
and 21 existing build-metadata files. No differences occurred in those sets.
The separate final integrity manifest records new evidence counts and intended
source/document changes. The selector source policy was explicitly renewed;
frozen protocol and production provenance were not changed.

No actual CTest discovery/test, native suite, prerequisite/resource validation,
benchmark, pilot or GPU work ran. No fresh build, Release or ASan/UBSan run is
claimed. The new grammar intentionally rejects unsupported generated layouts;
boundary checks require an exclusively owned, quiescent tree and trusted tools.
Study launch remains **NO-GO** pending a separate independent review. This task
stops at the repair audit and does not authorize subsequent fresh validation.
