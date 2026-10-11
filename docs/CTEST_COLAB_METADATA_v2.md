# Reviewed CMake 3.31 Colab metadata alternative

This additive review binds `NON_TIMING_TEST_SELECTION_v3.json` to the current
source snapshot. Earlier selection/policy documents remain immutable. The exact
default19 CPU names and opt-in21 CPU groups are unchanged. No production sorter,
frozen experiment, eligibility rule, timing interface or test registration changes.

The shared guard's `flat_literal_ctest_v2` profile accepts the old literal Dart
keyset or that keyset plus both `TLSVerify` and `TLSVersion`, each exactly empty.
`MemoryCheckCommand` is either the original `MEMORYCHECK_COMMAND-NOTFOUND` or
exactly `/usr/local/cuda/bin/compute-sanitizer`; no other path/arguments allowed.
All other values retain the old checks. Unknown profiles/settings and single or
nonempty TLS fields fail closed. Hook/include/subdirectory/symlink/command/property
checks and guarded absolute path/boundary rechecks remain unchanged.

CMake's installed `Modules/CTest.cmake` discovers compute-sanitizer; its CTest
manual defines `MemoryCheckCommand` for the MemCheck dashboard step. The shared
selector constructs only ordinary `-N --show-only=json-v1` discovery and fixed
ordinary `-R` test commands, never `-T`, `-D`, `-S` or dashboard/MemCheck actions.
The metadata alternative therefore does not authorize or invoke that tool.
This review does not generalize to arbitrary CTest invocations.

`tests/test_ctest_dart_compatibility.py` uses inert temporary metadata and blocks
all external subprocess/shell entry points. It checks the actual selector path,
both approved layouts, unknown/ambiguous settings, altered commands/options,
legacy/unknown profiles, hooks/includes, and metadata mutation during fake
discovery. Existing guard/path regression tests remain required before real
discovery. A valid static plan must be retained before test execution.

The CPU selection contains configure-only temporary checks of CUDA-OFF options;
these are not benchmark execution. Host-only CUDA analysis intentionally skips
two Python GPU timing integration methods. Report these method skips separately
from CTest group skips. The default legacy pilot validator must not be used for
this bounded task; use the shared guarded selector from an isolated bounded runner.

This extension closes only metadata compatibility. Passing correctness still
does not establish performance framework coverage or authorize any measurements.
