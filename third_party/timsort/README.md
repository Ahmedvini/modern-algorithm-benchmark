# cpp-TimSort provenance

Canonical upstream: https://github.com/timsort/cpp-TimSort (formerly gfx/cpp-TimSort).
Pinned commit: `99b612d9826e8387a30008f2b21be206181ad890`, from branch `2.x.y`.
This branch supports C++11 and therefore this project's C++17 build; upstream's
current 3.x branch requires C++20. The older branch is not actively maintained.
The header's version macros are 2.1.0, but this commit is not the v2.1.0 tag.

License: MIT. The complete standalone LICENSE and the header's license/copyright
notices for Fuji, Goro (gfx), Morwenn and Igor Kushnir are preserved. Include
these notices when distributing copies or substantial portions of the software.

Both upstream files are unchanged. SHA-256:

| File | Hash |
| --- | --- |
| include/gfx/timsort.hpp | a5cf0f0f61d92a62cf14528d1969a236db587b95678b088b5e38833d9865e9c9 |
| LICENSE | 210f3341e9e04dc3004f416ae0e28dc7e8eaa84528c5966661186a1b512f34c3 |

UPSTREAM.json records revision-qualified download URLs, hashes and retrieval
time. Vendoring verified identical bytes from a detached Git checkout, git show
at the pinned revision, and the revision-qualified raw GitHub downloads.
Builds require no network access or additional library.

The local adapter lives in src/algorithms/timsort.cpp and calls gfx::timsort on
the project's vector of signed int32 keys. No upstream source changes, comparator
instrumentation, or diagnostic macro overrides were added. The private CMake
include directory keeps the dependency out of the public header interface.
