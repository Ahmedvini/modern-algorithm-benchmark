# Vendored PDQSort

Original author: Orson Peters. This is the official C++ implementation from
[orlp/pdqsort](https://github.com/orlp/pdqsort), pinned to commit
[`b1ef26a55cdb60d236a5cb199c4234c704f46726`](https://github.com/orlp/pdqsort/commit/b1ef26a55cdb60d236a5cb199c4234c704f46726).
Upstream commit message: "Updated license year." (2021-03-14).

License: **Zlib**. The complete original license is preserved in license.txt,
and the original copyright/license notice remains in pdqsort.h. The origin must
not be misrepresented, altered source must be marked, and the notice retained.

Local modifications to upstream files: **none**. pdqsort.h and license.txt are
byte-for-byte copies of Git blobs at the recorded commit, independently matched
against revision-qualified raw.githubusercontent.com downloads over HTTPS.
UPSTREAM.json records source URLs, revision, retrieval time and SHA-256 hashes:

| File | SHA-256 |
| --- | --- |
| pdqsort.h | 1916aff237fc7ecc638dec6397662334552a1b6f823fa65011a8dfe831237fc0 |
| license.txt | 323fc18e35fcf058d69d684022ef844f206cb8fefb2bac1298fa1767e0b9ae38 |

The project-specific adapter lives in src/algorithms/pdqsort.cpp and calls
`::pdqsort(values.begin(), values.end())` for signed int32 vectors. It is separate
from the original code. The upstream overload uses std::less<Key>; with C++17
arithmetic keys this automatically selects branchless partitioning. No custom
comparator, upstream patch or forced pdqsort_branchless entry point is used.

The build reads these vendored files locally; it does not download dependencies.
To reproduce the source checkout in a separate directory:

```sh
git clone https://github.com/orlp/pdqsort.git pdqsort-upstream
git -C pdqsort-upstream checkout --detach b1ef26a55cdb60d236a5cb199c4234c704f46726
```

Compare the two files against this checkout and UPSTREAM.json before changing
the pin. Record any future modifications explicitly and retain upstream notices.
