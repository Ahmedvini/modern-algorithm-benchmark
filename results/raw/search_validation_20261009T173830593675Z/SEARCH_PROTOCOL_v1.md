# Search experiment protocol: search_batch_v1

Version 1, defined before implementing the search engine/matrix. Sorting protocols,
algorithms, CLIs and retained studies are unchanged. This is an initial validation
protocol, not a performance leaderboard or a frozen large-scale search study.

## Data and answers

Use mt19937_64_v1 signed int32 datasets with recorded source distribution, size,
seed, swaps and duplicate cardinality. Generate using the existing infrastructure,
then sort ascending with std::sort once outside lookup timing. Uniform, reverse
and nearly-sorted generation with the same seed have the same sorted multiset;
their prepared fingerprints can therefore coincide. All searchers receive that
same immutable prepared vector and exactly the same query batches. No lookup
sorts or checks sortedness internally. The engine validates ascending order once
before timing. Linear search also supports arbitrary order through its public API.

All algorithms return optional<size_t>: the first matching index, or nullopt for
absence. Expected answers use the existing std_lower_bound_search outside timing;
tests independently use std::find. Duplicate target position and selected source
position can differ: the expected index is always the first occurrence.

## Query generator: mt19937_64_queries_v1

Defaults: query seed 2718, batch size 1000, one warm-up and five measured rounds.
Batch size must be even and in [2,100000]. Each category has its own fresh
mt19937_64(query_seed XOR (0x9e3779b97f4a7c15 * (category_index+1))), with uint64
wraparound. Indices/categories are the fixed order in the following table.
Unbiased bounded sampling uses unsigned (0-bound)%bound rejection before modulo.
Changing selected categories does not change another category's queries.

| Index/category | Exact definition | Availability |
| --- | --- | --- |
| 0 hit_first | Repeat the key at selected position 0 | Nonempty data |
| 1 hit_middle | Repeat the key at selected position floor(N/2) | Nonempty data |
| 2 hit_last | Repeat the key at selected position N-1 | Nonempty data |
| 3 hit_random | Independently sample a position uniformly in [0,N) | Nonempty data |
| 4 miss_below | Repeat minimum-1, computed in int64 | Nonempty and minimum > INT32_MIN |
| 5 miss_between | Uniformly select an adjacent gap with difference >1; use left+floor(gap/2) in int64 | At least one such gap |
| 6 miss_above | Repeat maximum+1, computed in int64 | Nonempty and maximum < INT32_MAX |
| 7 mixed_50 | Alternate random-position hit then miss; choose uniformly among available below/between/above miss policies, then apply that policy | Nonempty and at least one miss policy available |
| 8 miss_empty | Low uint32 engine output minus 2^31 in int64; always absent | Empty data only |

Every available category contains exactly batch_size queries. Query IDs are
zero-based within category; queries.csv records target, selected source position,
expected position and hit status. Fixed-position batches intentionally repeat a
target. Hit policies can intentionally select equal values/positions, particularly
for singleton/duplicate-heavy inputs; labels describe selection policies rather
than disjoint key sets. The three miss policies are disjoint numeric regions.
mixed_50 is exactly 50% hits/misses; hit-only categories are 100% hits and miss-only
categories 0%. The overall default ratio depends on category availability and is
reported from actual batch counts, not assumed to be 50%. Unavailable categories
have no fabricated trials: run.json retains the reason and analysis lists them.

## Timing and ordering

Use steady_clock, integer nanoseconds, Release with sanitizers OFF. Debug/sanitizer
tests require --validation-only and label observations validation. One row times
one complete batch: loop, function dispatch and stores into a preallocated answer
buffer are included. Generation, sorting preprocessing, query construction,
allocation, reference checks, comparison counts and output I/O are excluded.
Validate every answer after each batch, including warm-ups; failures stop the run.
Store results and consume them in validation to prevent dead-code elimination.

All warm-up rounds precede measured rounds. For each round, visit selected
categories in fixed registry order; for each category rotate the selected
algorithm list by (dataset_seed%algorithm_count + trial_index%algorithm_count)
%algorithm_count. Indices restart for measured rounds. The raw execution_order is
the zero-based algorithm position within the category/round. No randomization,
frequency control, affinity, cache flushing, exclusive load or thermal control.
Repeated targets and warm-ups can warm caches; this is not a cold-cache protocol.

elapsed_ns/batch_size is normalized batch-average latency, not directly measured
individual-query latency. Maximum batch time and maximum normalized batch average
are not maximum per-query latency or a theoretical bound. Timer overhead is not
subtracted; no individual-query maxima are reported without future calibration.

## Resource limits, raw output and metadata

Development matrix: sizes 0,1,64,1000; source distributions uniform and
duplicate_heavy, dataset seed 1729, query seed 2718; 64 queries per available
category, one warm-up/five repetitions, all three required algorithms. A larger
explicit baseline may use N=1M, 1000 queries per category and multiple seeds;
it is not a default test and is not executed in this milestone. Linear batch
work is O(N*batch_size); check runtime as well as memory before larger studies.

Use existing dataset/timing validation plus a conservative planning guard:
16*N + 128*batch_size*9 bytes <= memory_limit_mib*2^20 (default 256 MiB).
This allows input/gap workspace/query metadata/answers, not a hard RSS cap or
measured allocation. Lists/configurations/total planned rows are bounded by the
runner (1000 list entries/configurations, 1M total timing rows). Configurations
execute serially, size/seed/query-seed/distribution order, with a new process each.

Exclusively create a new output directory; refuse existing paths and symlinks.
run.json stores schema/protocol, invocation/run identity, input/query fingerprints,
parameters, algorithms, category availability/counts, expected trial totals,
clock period, compiler/build/platform, CMake flags and source SHA-256 manifest.
Copy compile commands, CMake cache and vendored provenance. A matrix environment
manifest records available OS/kernel/CPU/RAM/tool metadata, executable hash and
source/tool hashes. Unknown metadata is absent/null, never invented.

trials.csv schema version 1 has these ordered fields:

```text
schema_version,protocol,run_id,run_kind,algorithm,distribution,size,seed,input_hash_fnv1a64,query_seed,query_generator,query_category,query_hash_fnv1a64,batch_size,hit_queries,miss_queries,phase,trial_index,execution_order,elapsed_ns,elapsed_unit,status,correctness,error,repetitions,warmups,compiler_id,compiler_version,build_type,sanitizers,platform,architecture
```

queries.csv fields: query_category,query_id,target,selected_position,
expected_position,expected_hit. Empty positions mean absence/not applicable;
expected_hit is true/false. Fingerprints use FNV-1a64 low-byte-first encoding:
dataset as sort_timing_v1; query list as uint32 target then uint64 selected and
expected positions (UINT64_MAX for null). They identify inputs, not correctness
proofs. The parser validates the manifest, categories, query hashes/counts, row
sequence, schema and completion markers before summarizing. CSV uses existing
escaping (quote comma/quote/CR/LF, double quotes). Exceptions have blank elapsed
time, status error and a diagnostic; wrong answers retain elapsed time and failed
correctness. COMPLETE only follows all planned successes and successful writes.
FAILED/absent completion retains partial output; default analysis refuses it.
Explicit --allow-incomplete reports failed/missing trials and still exits 1.

## Analysis and separate comparisons

Group by run/algorithm/category; never silently pool seeds or categories. Retain
every observation/outlier and all warm-up rows. Report successful/failed/missing
trials, median/mean/sample SD (n-1)/min/max batch ns and normalized average ns per
query. SD is null with fewer than two successes, all statistics null with none.
No significance tests or universal performance claims. Raw observations stay
immutable; summaries use a separate exclusively created processed path.

Separate counted adapters measure each executed signed key < or == predicate
(key_predicate_v1), excluding index/bookkeeping/reference operations. They share
project templates with counter-free production adapters and run-local checked
uint64 counters; no global state. This search predicate convention differs from
sorting's less-than-only convention. A separate search_counts executable exports
per-query answers/counts, without collecting time or running inside primary timing.
Process RSS and algorithm allocation measurement are not added for search here.
