# Local correctness source review v5

The user's standing autonomous authorization explicitly permits reviewed
selection activation. `NON_TIMING_TEST_SELECTION_v5.json` records the current
source membership and hashes while copying the v3 tests, commands, classifications,
properties and build metadata policy **exactly**. No default test is added or
removed: the default19 remain unchanged. Two previously reviewed untimed diagnostics
require explicit opt-in. Historical v3 and the inactive v4 candidate are preserved.

The selector verifies v3 against its existing pinned digest before accepting v5,
requires exact classification/command/property equality to v3, and requires an
exact current source map. Its static CTest hook/include/subdirectory gate,
canonical build-path retention and metadata rechecks are unchanged. Unknown or
modified source still fails before discovery. The separate learned-index build
does not use this root registry; its one correctness executable is invoked directly.

This is a **local correctness review**, not an independently signed study approval.
`full_study_eligible` is false. The full evidence validator is unchanged and still
requires an independently protected trust root, approved study source/selection,
actual GPU build provenance and identity-matched records. No trust root is invented,
no historical evidence is relabeled, and no study guard is bypassed.

The activation exposed an old regression that assumed v3 was always the active
default. Its initial failure is retained. The corrected regression explicitly
loads immutable v3 and proves it still rejects the changed tree; inactive v4 is
still rejected. New activation regressions reject changed selection membership,
commands, source additions, removals and hashes. Guard/path tests remain inert.

Current local results: Release21/21 and Debug ASan/UBSan21/21 correctness groups,
leak detection enabled. The new learned index separately passed153 datasets,
45201 oracle queries and exact small comparison assertions in both configurations.
See the current audit for exact commands, retained outputs and initial snapshots.

The following helper performs static validation before discovery, retains the
exact approved plan and rechecks metadata before execution. Use a new evidence
destination and the explicit helper from the retained run:

```sh
python3 -B results/raw/autonomous_completion_20261011T095554571762Z/guarded_validate.py release
```

That retained helper uses exclusive evidence filenames; do not rerun it into the
existing directory. Copy the reviewed helper to a new evidence directory and
adjust the isolated build paths for a future validation. A plain broad CTest run
includes timing-bearing framework tests and is not a correctness-only substitute.

## Separate learned-index build

The additive standalone target compiles the existing generator/search/timing
sources and the new index without changing root CMake or the frozen adapters:

```sh
cmake -S cmake/learned_index_standalone -B build/learned_release -DCMAKE_BUILD_TYPE=Release
cmake --build build/learned_release --parallel 2
build/learned_release/test_learned_index
cmake -S cmake/learned_index_standalone -B build/learned_sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
cmake --build build/learned_sanitize --target test_learned_index --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 build/learned_sanitize/test_learned_index
```

These examples use new build paths; the actual validated paths are
`build/autonomous_learned_release` and `build/autonomous_learned_sanitize`.
The native correctness executable contains no benchmark timing loops.
Explicit Release study execution is separate:

```sh
python3 -B scripts/learned_study.py run --binary build/learned_release/learned_index_benchmark --output NEW_RAW_DIRECTORY
python3 -B scripts/learned_study.py analyze --raw NEW_RAW_DIRECTORY --output NEW_PROCESSED_DIRECTORY
```

The fixed matrix is `docs/studies/learned_rank_v1.matrix.json`; the runner refuses
existing output directories. These learned timings are not frozen CPU/GPU study
eligibility evidence.
