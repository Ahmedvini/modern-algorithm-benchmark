# Phase 4 contracts and development protocol: structures_batch_v1

This document is frozen before structure implementation. It supplements, and
does not change, search_batch_v1 or the frozen 1M sorting study. No large
structure experiment is authorized by this development protocol.

## Ordered map contract

Keys are mab::Key (signed int32); payloads are size_t values, returned by value
as optional<size_t>. insert(key,value) returns true for a newly stored key;
duplicate insertion returns false and preserves the first inserted payload.
size() counts unique keys. find(key) returns that payload or nullopt, including
on empty structures. Zero and SIZE_MAX are valid payloads. There is no sentinel
key: INT32_MIN/MAX are ordinary keys ordered with signed < and ==.

There is no update, erase, clear, iterator or concurrency API in this milestone.
Changing a duplicate payload is unsupported, rather than an implicit update.
Copy and move construction/assignment are explicitly disabled. Instances own
their nodes with RAII; forward links are nonowning and results never expose node
lifetimes. Destruction releases all storage. Callers must synchronize mutation;
concurrent const lookup is possible only when no thread mutates the instance.
Invalid construction parameters throw invalid_argument. Allocation/size overflow
throws; the structure retains its existing key/value contents and invariants,
although a B-tree may have split nodes before an insertion allocation fails.
Failed allocations are not fault-injected by the initial tests.

## Skip List

Public SkipList(seed=1729) uses at most 32 levels, numbered 0..31, promotion
probability 1/2. For each new unique key draw a fresh mt19937_64 word per attempted
promotion, promote when bit zero is one, stop on zero or level 31. Duplicate
insertion consumes no engine outputs. Seed-to-level behavior is specified for
successful insertion sequences; failed allocation may advance the engine.
Head has 32 forward links; each node has level+1 links. Unique_ptr ownership is
held in a vector independent of forward chains, avoiding recursive destruction.

Level zero contains every unique key exactly once in strictly ascending order.
Every higher chain is ordered and exactly the subsequence of level-zero nodes
whose heights cover that level. Links are null or point to an owned node with
sufficient height; cycles, unreachable ownership, wrong size and invalid heights
fail validate(). Tests inspect a reproducible structural fingerprint and require
multiple levels for a fixed seeded large fixture.

Expected insertion/lookup O(log U), expected link storage O(U), with U unique
keys and independent promotions while the level cap is adequate. Worst-case
lookup/insertion O(U+32); hard storage bound O(32U). The fixed cap limits the
asymptotic expectation at arbitrarily large U. Destruction is iterative O(U).

## B-tree convention

Public BTree(order=16) is a classic B-tree with even maximum child count M in
[4,64], minimum degree t=M/2. Registry configurations are btree_m10, btree_m16,
btree_m32, btree_m64; these are orders, not minimum degrees. Each node reserves
M-1 key/payload entries and M child slots. Nonroot nodes have t-1..M-1 keys;
nonempty root has 1..M-1 keys. Leaves have no children; internal nodes have
key_count+1 children. Empty tree has no root. Keys are strictly ordered, child
ranges lie strictly between separators, and all leaves have equal depth.

Top-down insertion splits a full child before descending: entry t-1 moves to
the parent, t-1 entries remain left and t-1 move right; internal children split
t/t. A full root gets a new root. Duplicate lookup precedes mutation, preserving
payload and shape. Node allocation/reservation precedes each split mutation.
validate() checks all capacities, ranges, counts, leaf depths and total size.
Diagnostic split count/height evidence is outside lookup timing.

With fixed M, insertion/lookup O(log U) node visits, O(M log_M(U+1)) key work
using linear scans per node; worst auxiliary lookup O(1), insertion stack O(log_M
(U+1)), owned storage O(U). This is a B-tree, not a binary search tree. No deletion.

## Oracles and implementation gates

Differential tests use std::map::emplace first-insertion semantics. Include empty,
singleton, extrema, zero/SIZE_MAX payloads, repeated keys, ascending/descending/
shuffled/duplicate-heavy/random seeded sequences and repeated lookups. Validate
after every insertion in small cases and periodically in larger cases; force
multiple Skip List levels and multiple root/nonroot B-tree splits. Verify disabled
copy/move at compile time. Release and ASan/UBSan full suites must pass before
benchmark integration/smoke. Preserve all existing tests and sources.

## Benchmark workload and timing

Reuse mt19937_64_v1 datasets, sorted alias, query planner, category definitions,
query fingerprints, availability and hit/miss semantics from SEARCH_PROTOCOL_v1.
Retain original insertion order and its fingerprint. Sort a reference copy and
prepare each input key's first sorted rank outside timing. Thus duplicate
payloads agree independently of source insertion order. All structures receive
the identical entry sequence and exact query batches, and return first sorted
rank/absence. Skip List seed is separately recorded (default 1729).

Development matrix: N=0,1,64,1000, uniform/duplicate_heavy, dataset seed 1729,
query seed 2718, structure seed 1729; all five registry entries, all nine policies,
64 queries per eligible category, one warmup and five measured repetitions.
No larger experiment is executed. Future studies need a new frozen protocol.

For each warmup/measured round rotate structure order by (dataset_seed mod A +
trial mod A) mod A. For each structure create a fresh instance and insert every
entry inside a construction timer. Constructor, RNG initialization and node
allocation are included; destruction is excluded. Validate invariants, size and
every stored payload outside timing. Then measure each available query batch on
that instance with steady_clock, normal virtual dispatch, loop and preallocated
answer stores included. Validate every answer outside timing. Query generation,
reference sorting/ranks, allocation of answer buffers, I/O and instrumentation
are excluded. All warmup rounds precede measurements. Keep construction and lookup
rows/groups separate; no end-to-end metric is inferred. Nanoseconds are units,
not guaranteed resolution. Batch ns/query is normalized average, never an
individual-query duration or maximum. No comparison counters are collected.

Planning guard: 512*N + 128*batch_size*9 bytes <= memory_limit_mib*2^20,
plus the inherited search configuration limits. One structure is resident at a
time. The bound is a conservative development estimate, not measured allocation
or a hard RSS cap; runtime/allocator overhead is excluded. RSS is not collected.
Theoretical storage must not be labeled measured structure memory. No CPU/cache/
frequency/thermal/background controls, outlier removal or significance claim.

## Output, analysis and failures

New structure_benchmark CLI and run_structure_matrix.py/analyze_structure_results.py
use exclusively new directories/files. Defaults mirror search_benchmark except
--structure defaults skip_list, --structure-seed 1729, and --list-structures.
--structure accepts unique registry names or all. Existing CLIs are untouched.
Performance requires Release without sanitizers; --validation-only labels tests.
Sidecars retain exact argv, original/sorted input hashes, query metadata, seeds,
compiler/build/platform/clock, source hashes, CMake cache/compile commands and
available environment. queries.csv retains the unchanged six-column query schema.

trials.csv fields (schema 1, protocol structures_batch_v1):

```text
schema_version,protocol,run_id,run_kind,algorithm,distribution,size,seed,insertion_hash_fnv1a64,input_hash_fnv1a64,structure_seed,query_seed,operation,query_category,query_hash_fnv1a64,batch_size,hit_queries,miss_queries,phase,trial_index,execution_order,elapsed_ns,elapsed_unit,status,correctness,error,repetitions,warmups,compiler_id,compiler_version,build_type,sanitizers,platform,architecture
```

Construction rows have operation=build and empty category/hash/query counts;
lookup rows have operation=lookup and exact batch identity. A failed call emits
error/not_checked with blank time; failed validation emits error/failed with
time retained. Fail fast, retain partial rows and FAILED/absent COMPLETE; COMPLETE
is written only after all planned rows validate and streams close. Missing trials
are never successes. Matrix records child argv/stdout/stderr/exit statuses.

Analysis validates schema, metadata, queries/fingerprints, row schedule, counts,
statuses and completion markers. Default refuses incomplete data; explicit
--allow-incomplete reports missing/failed groups and exits 1. Groups remain
separate by run/structure/operation/category; report successes/failures/missing,
warmups, median/mean/sample SD(n-1)/min/max ns, plus normalized lookup averages.
No outliers are discarded; SD null below two successes, all statistics null
without successes. Summaries must regenerate byte-for-byte; raw/protocol/earlier
artifacts are hash-verified unchanged after analysis. No large experiment until
correctness, full suites and smoke pipeline pass.
