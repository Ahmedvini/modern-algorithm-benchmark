# Implemented algorithms

## std_sort

This adapter calls the installed C++ standard library's std::sort, ascending over
signed int32 keys. It is not relabeled as PDQSort, Timsort or project QuickSort.
Compiler/library details belong to each environment manifest.

## quick_sort: bounded project QuickSort

The public interface is `mab::quick_sort(Values&)`; the registry name and CLI
selection are `quick_sort` and `--sort quick_sort`. Sorting is in place and not
stable. Empty/singleton inputs need no partitioning.

The pivot is the median of the first, middle and last keys of the current
half-open range, copied before rearrangement. Three-way partitioning separates
keys less than, equal to and greater than the pivot. The equal group is skipped,
making all-equal input finish in one partition. No key arithmetic is used.

The initial budget is twice floor(log2(N)), calculated with integer shifts.
Each partition consumes one level for both child paths. A nontrivial range with
exhausted budget is sorted using std::make_heap followed by std::sort_heap.
This bounds worst-case sorting work to O(N log N). Only the smaller strict
partition is recursively processed; the larger is processed iteratively.
The stack is O(log N), with no allocated auxiliary array. This is an asymptotic
space description, not a measured peak-memory result.

Internal observer templates in algorithms/detail/quicksort_impl.hpp let tests
count actual partitions, fallback calls and stack depth, and inject budgets of
zero/one. The production instantiation uses an empty observer and no mutable
counters, runtime callback selection or comparison instrumentation. Its normal
entry point always uses the calculated budget. Observer tests must not be used
as performance timing runs.

Fresh Release and Debug ASan/UBSan runs both passed 3,718 dedicated differential
input cases through the production and observed paths. The asserted fallback
counts were: zero-budget whole-range 1; one-budget subrange 1; balanced children
2; sentinel-bounded subrange 1; normal-budget adversarial inputs 618 in total.
Both runs also checked the smaller-partition stack bound. These are correctness
coverage counts, not timing or performance measurements.

Correctness tests compare the full output against std::sort, including exhaustive
small arrays, integer extrema, all distributions, multiple seeds/sizes, sorted,
reverse, organ-pipe, sawtooth and alternating-low/high inputs. They explicitly
require fallback calls after forced exhaustion and under the production budget
on adversarial data. The implementation has no third-party source dependencies.

## pdq_sort: official upstream PDQSort

Source: Orson Peters' [orlp/pdqsort](https://github.com/orlp/pdqsort), exact commit
[`b1ef26a55cdb60d236a5cb199c4234c704f46726`](https://github.com/orlp/pdqsort/commit/b1ef26a55cdb60d236a5cb199c4234c704f46726).
License: [Zlib](https://github.com/orlp/pdqsort/blob/b1ef26a55cdb60d236a5cb199c4234c704f46726/license.txt),
with the full license and header notice preserved in third_party/pdqsort.
Local modifications to upstream code/license: none. Source URLs and SHA-256
hashes are recorded in third_party/pdqsort/UPSTREAM.json.

The public interface is `mab::pdq_sort(Values&)`; the registry/CLI name is
`pdq_sort`. The adapter calls the original `::pdqsort(begin,end)` over signed
int32 keys, ascending and unstable. Its default std::less<Key> comparator and
arithmetic key type automatically select the upstream branchless partition path
under C++17. No relabeled std::sort or locally reconstructed PDQSort is used.

The pinned implementation contains insertion sorting for small ranges,
median-of-three/ninther pivots, equal-key handling, pattern breaking after
unbalanced partitions and a heapsort fallback after too many bad partitions.
These are verified source properties, not measured speed or memory claims.
Dedicated full-vector tests exercise the public adapter and registry against
std::sort, including threshold-adjacent sizes and partition-adversarial patterns.
The existing shared dataset/baseline tests also cover the new registry entry.
Fresh integration validation passed 6/6 full CTest groups in both Release and
Debug ASan/UBSan, with leak detection enabled. Dedicated PDQSort coverage is
4,027 full-vector cases through the public function and registry: 15 explicit
edges, 3,280 exhaustive small arrays, 600 distribution/seed/size cases and 132
sorted/reverse/equal/organ-pipe/sawtooth/alternating/extreme/rotated/run patterns.
Threshold-adjacent sizes include 23/24/25, 63/64/65 and 127/128/129. These tests
do not claim internal PDQSort fallback coverage or measured performance.

## tim_sort: upstream cpp-TimSort

Source: [timsort/cpp-TimSort](https://github.com/timsort/cpp-TimSort), formerly
gfx/cpp-TimSort, pinned to
[`99b612d9826e8387a30008f2b21be206181ad890`](https://github.com/timsort/cpp-TimSort/commit/99b612d9826e8387a30008f2b21be206181ad890).
The selected 2.x.y branch supports C++11 and this project's C++17 configuration;
current upstream 3.x requires C++20. Upstream describes the older branches as
not actively maintained. Header version macros say 2.1.0, but the exact commit
is distinct from the v2.1.0 tag. License: MIT, preserved in the standalone LICENSE
and complete header notice (Fuji, Goro/gfx, Morwenn and Igor Kushnir).
See third_party/timsort/README.md and UPSTREAM.json for URLs and SHA-256 hashes.

The public function `mab::tim_sort(Values&)` calls `gfx::timsort(begin,end)` on
vector<int32_t>. The registry and CLI name is `tim_sort`; ascending std::less
comparison is the upstream default. The adapter introduces no custom comparator,
diagnostic macro overrides or algorithm changes. Upstream source and license
bytes match the pinned Git objects and revision-qualified raw downloads.

This is genuine stable Timsort, ported from Python/OpenJDK: it detects natural
ascending/strictly descending runs, reverses descending runs, extends short runs
with binary insertion sorting, and merges a pending-run stack using collapse
invariants and galloping searches. MIN_MERGE is 32; minrun rounding shifts while
N >= 64. The merge-collapse policy includes the deeper pending-run invariant.
The merge workspace and pending-run stack are std::vector storage managed by
RAII. Worst-case auxiliary space is O(N); this is an algorithm description,
not a measured memory result. Allocation exceptions propagate through the
adapter into the CLI's existing exception handling.

Source review covered the N < 2 early return, half-open ranges, partial final
runs, merge cursor updates (including backward merging), run-length sums and
signed iterator offsets used by galloping. Keys are only compared/moved, so no
signed key arithmetic is introduced by the sorter. No defect requiring local
source modification was demonstrated. Validation applies to the project's
int32 vector interface and tested sizes, not every generic upstream instantiation
or extreme allocation size. Equal int32 keys have no distinguishable payload;
these tests verify full value sequences, not decorated-record stability.

Release and Debug ASan/UBSan both passed 4,149 dedicated differential inputs
against std::sort through the public adapter and registry: 15 explicit edges,
3,280 exhaustive arrays of lengths 0..7 over {-2,0,2}, 600 distribution/seed/size
combinations, 132 general patterns, 24 varied natural-run patterns and 98
unequal/overlapping two-run patterns. Cases include cutoff-adjacent lengths,
short tails, negative values, extrema, descending duplicates, long winner blocks,
and many short runs. These inputs target run/merge behavior without asserting
specific internal branch coverage. Shared baseline/dataset tests also use the
registry entry. Ten CLI methods include 36 Timsort distribution/size selections,
repeated sorting options, help and invalid names. Full suites passed 7/7 groups
each, with leak detection enabled and no compiler warnings.

## std_lower_bound

The reference search adapter requires ascending sorted input and returns the
first matching index or nullopt. Lookup uses O(log N) comparisons and O(1)
auxiliary space; it constructs no index. Sorting preprocessing is separate.
Tests use an independent linear std::find oracle. The project linear, binary and
exponential algorithms remain pending.

Advanced search structures remain pending. No measured algorithm-performance
claims are made here.

## merge_sort: stable project Merge Sort

The public interface is mab::merge_sort(Values&); registry/CLI name merge_sort.
This is conventional bottom-up merging of adjacent half-open runs with widths
1,2,4,... . Each call of size N >= 2 allocates one N-key vector once, then
alternates source/destination arrays. An odd number of passes requires a final
copy into the caller's existing vector storage. Empty/singleton inputs return
without allocating. Allocation failures propagate through existing CLI handling.

While both runs contain keys, one predicate right < left selects the next key;
ties select the left run, making merges stable. Unconsumed tails are copied with
no key predicates. There is no pre-merge ordered-run shortcut. Boundaries use
size_t and clamp run lengths against remaining size before addition; width
doubles only when width < N-width. No signed key/index arithmetic or recursion
is used. Work is O(N log N), auxiliary space O(N) plus constant bookkeeping.
These are theoretical bounds; allocation, initialization, passes and any final
copy are all included in the normal sorting call's timing.

The shared internal template defaults to std::less<Key> in production and uses
CountingLess only in mab_metrics. Counted identity project_merge_sort_counting_less
follows key_less_than_v1; no production counter overhead is mandatory. Small
manually checked fixtures test exact counts, and the existing repeated/interleaved
counter-isolation tests include this adapter. The internal stable merge policy
is also tested with distinguishable int32 keys in equal-comparator groups.
Public ascending-int32 tests check values; they do not imply a generic API.

## radix_sort: stable project signed LSD Radix Sort

The public interface is mab::radix_sort(Values&); registry/CLI name radix_sort.
The implementation uses radix 256 and four eight-bit digit passes, least
significant first. Every nontrivial call allocates one N-key vector once, uses
a stack array of 256 size_t bucket counts/offsets, and alternates source and
destination. Four passes place the final result in the caller's original vector.
Empty/singleton calls return without allocating. There is no adaptive pass
skipping, key comparison, std::sort delegation or comparison-sort fallback.

For key x, the digit word is uint32(x) XOR 0x80000000. Signed-to-unsigned conversion
is defined modulo 2^32: negative keys become words in [2^31,2^32), nonnegative
keys in [0,2^31). Flipping bit 31 maps each case to x+2^31 in mathematical
arithmetic, a strictly increasing mapping into [0,2^32). All implementation
shifts/masks are unsigned; static assertions require 31 signed value bits and
32 unsigned value bits. It uses neither abs(INT32_MIN) nor signed shifts/overflow,
representation aliasing or an out-of-range unsigned-to-signed conversion.

Each digit pass builds frequencies and exclusive prefixes, then scatters original
signed Key values in forward order. Stable scatter is required so subsequent
passes preserve lower-digit order. Prefix/offset sums are bounded by vector size;
the full sorted sequence is compared with std::sort. Complexity is O(4*(N+256))
work and O(N+256) auxiliary storage, theoretical rather than measured workspace.
Memory allocation belongs to normal timing. No trustworthy comparison complexity
metric exists for this noncomparison algorithm: radix_sort is deliberately absent
from counted_sorters, and sort_metrics rejects it explicitly as unsupported.

Dedicated tests for both project baselines cover exhaustive small arrays, all
generator distributions, reproducible seeds, digit and merge-width boundaries,
sorted/reverse/all-equal/run/organ-pipe patterns, negative/positive/mixed signs,
integer extrema and repeated differently sized calls through public/registry
paths. Tests target these inputs without claiming radix internal branch coverage.

Fresh Release and Debug ASan/UBSan each pass 4,015 dedicated cases per sorter:
15 explicit edges, 3,280 exhaustive arrays, 600 distribution/seed/size combinations,
108 patterns and 12 digit sweeps. Each case uses the public adapter, registry,
interleaved different-size call, repeated input and already sorted result. Full
suites pass 15/15 groups; counts/commands and six-sorter smoke evidence are in
AUDIT.md. These are correctness results, not comparative speed conclusions.

## Separate metric adapters

Five comparison sorters have counted adapters in mab_metrics. Radix Sort's
comparison metric is explicitly unsupported. Each executed signed-int32
less-than predicate counts once, including false/equal and pivot/heap/merge work.
Counters are run-local, reset per call, and throw on uint64 overflow. Normal
adapters do not update counters; the normal executable does not link mab_metrics.

QuickSort's shared internal template now accepts a comparator, defaulting to
std::less<Key>; policy, boundaries, budget and observers are preserved. The
counted comparator reaches both heap calls. PDQSort uses upstream's explicit
branchless entry point, preserving the normal int32/default-comparator policy.
Timsort/std::sort use comparator APIs directly. Vendored files are unchanged.
Counts depend on implementation and are not timing proxies. Exact cross-platform
counts are not asserted for upstream/standard-library algorithms.

Linux peak RSS is a process-lifetime high-water mark including input, runtime,
allocator and instrumentation overhead. It does not measure algorithm-specific
allocations. Other platforms return unsupported/null. See [METRICS.md](METRICS.md)
for definitions, sampling point, schema, inclusion rules and validation limits.

## Production timing adapters

sort_benchmark calls the unchanged normal sorting registry from mab_core, with
no link to mab_metrics and no counting comparators. The same immutable generator
input is restored for each trial, including the benchmark-only sorted alias of
nearly_sorted with zero swaps. Full equality to std::sort is checked outside the
steady-clock interval. Sort-owned allocation is included; dataset/copy/reference/
CSV setup is excluded. [BENCHMARKING.md](BENCHMARKING.md) defines warmups, cyclic
order, repetition/timing units, metadata, failure records and separate statistics.
Small smoke measurements validate the engine; no performance ranking is asserted.
