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
