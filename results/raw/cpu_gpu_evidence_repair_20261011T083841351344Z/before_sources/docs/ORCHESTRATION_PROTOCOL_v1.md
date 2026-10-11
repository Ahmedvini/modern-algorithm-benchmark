# Phase 5 orchestration and visualization: experiment_pipeline_v1

Frozen before the new orchestration implementation and any study execution.
This supplements sort_timing_v1, search_batch_v1 and structures_batch_v1 without
altering their engines, schemas, protocols or the frozen 1M sorting study.

## Scope and fixed presets

Three serial benchmark families: sorting (std_sort, quick_sort, pdq_sort, tim_sort,
merge_sort, radix_sort); array search (linear_search, binary_search,
exponential_search); structures (skip_list, btree_m10/m16/m32/m64). Algorithms run
in existing registry order with existing cyclic trial ordering. Sorting defaults
stay unchanged. No comparison instrumentation, RSS, CUDA or 100M workloads.

Smoke: sizes 0,64,1000; source distributions uniform,duplicate_heavy; dataset
seeds 1729,42; query seed 2718; structure seed 1729; Q=64 queries per available
category; one warmup/five measured repetitions; duplicate cardinality16; swaps
floor(N/100); planning limit1024MiB. Twelve configurations per family, 36 total.
All nine original query policies are requested, including explicit unavailable
ones. This is infrastructure validation, not a full performance study.

Full study: sizes 1000,10000,100000,1000000; all five original benchmark
source distributions uniform,sorted,reverse_sorted,duplicate_heavy,nearly_sorted;
dataset seeds1729,42,2718; query seed2718; structure seed1729; Q=1000; W1/R5;
cardinality16; default swaps;1024MiB. Sixty configurations per family,180 total.
Measured-row upper bounds: sorting1800, search8100, structures15000 (includes
1500 builds); total24900. Warmup upper bounds:360+1620+3000=4980. Actual lookup
counts depend on query availability; unavailable policies are not missing trials.
The full study extends the Phase 4 development scope under this new document.
It runs only after fresh suites, smoke/regeneration/integrity and resource review.

Configuration JSON schema1 records protocol, preset label, sizes, distributions,
dataset/query seeds, structure seed, Q, W/R, cardinality, optional swaps, memory
budget, selected algorithm lists and validation_only. Strict known fields,
unsigned integers, unique nonempty bounded lists, fixed protocol identities.
Custom matrices are labeled custom; changes cannot be called the frozen full
preset. Maximum N=1M, 256 configurations per family,100000 total row upper bound.
Debug/sanitizer validation is labeled separately and never pooled with performance.

## Execution, paths and failures

run_experiments.py accepts explicit raw/processed/figure roots and a required safe
run ID. Each root must already exist; exclusively create root/run_id, reject
existing paths including symlinks. Raw/processed/figure paths must not overlap.
Atomic mkdir arbitrates concurrent identical IDs; no overwrite/resume flag.
Retries always use a new ID, preserve failed output and reference its old ID in
the audit. Safe resumption is intentionally unsupported. Different-ID concurrent
runs are not scheduled by the tool; users must avoid benchmark contention.

Dry run validates configuration, emits stable JSON with its SHA256 fingerprint,
exact runner argv, every planned child argv/output location, row upper bounds and
resource estimates, without launching benchmark processes or creating outputs.
Stable configuration hash uses sorted compact UTF8 JSON; timing/environment
snapshots, paths and invocation are separately recorded rather than hashed into
workload identity. Actual execution verifies the binaries' registry lists.

Invoke existing family runners with the current Python interpreter, serially.
Retain command argv, UTC start/end, wall duration (includes setup; not algorithm
time), return code/stdout/stderr. Fail fast on nonzero, preserve children/raw.
SIGINT/SIGTERM terminate the active process group on Linux and record interrupted
execution where writes remain possible. SIGKILL/power/disk failure may leave only
a planned or started command: missing completion is authoritative. Unstarted
families and missing bundles are visible. An interruption is a command outcome,
not an invented timed observation; missing trials retain interruption context.

Write the plan before running, COLLECTED only after strict validation of every
child/configuration/observation, and final COMPLETE only after derived summary,
plots and report validate. Failure/INTERRUPTED markers never coexist with a valid
COMPLETE. The final manifest hashes raw and derived artifacts. A standalone
analysis may validate collected raw before final COMPLETE; it checks family
completion and the collection marker. Partial analysis requires explicit
--allow-incomplete, retains diagnostics and exits1; malformed data always reject.

## Timing and shared workload identity

Keep existing steady_clock nanosecond timing exactly. Sorting restores copies
outside timing and validates full vectors. Search preprocessing/query generation
are outside batch timing. Structure construction and lookup stay separate; first
sorted-rank payload preparation and invariant/answer checks remain outside timers.
Destruction is outside structure timers. All families receive equivalent seeded
source data; search/structures use identical prepared input and query identities.
Uniform/sorted/reverse/nearly-sorted can share sorted multisets and are not
independent lookup datasets. Source distribution is still retained separately.
No end-to-end metric or direct individual-query duration/max is inferred.

## Unified representation and strict validation

observations.jsonl contains every raw warmup/measured row, with source CSV path,
zero-based row index, raw row preserved verbatim and the following normalized
fields. Required: family (plan), protocol/run_id/algorithm/distribution/size/seed,
input hash, phase/trial/order, ns unit, elapsed integer or null, status/correctness/
error, compiler ID/version, build_type, sanitizers, platform/architecture/run_kind
(from CSV checked against run.json). operation=sort or lookup is derived from
family; structures operation comes from CSV. Dataset generator and cardinality/
swaps come from run.json when not in CSV. Query category/seed/hash/batch size/
hit/miss counts are required for lookup; null for construction/sorting. Structure
seed/insertion hash are required only for structures; otherwise null. Source
manifest SHA256 and flags come from retained sidecars/run.json; optional fields
remain null when absent. Environment/queries are traceable by bundle paths.
Unknown metadata is never guessed. Keys/targets/expected ranks remain in queryCSV.

Use existing family validators plus stricter common validation: matrix child
commands/return codes/configuration coverage, family protocol, exact registered
algorithms, build/run kind, source manifest, matching expected parameters, unique
trial identities, finite nonnegative uint64 ns, fail-fast semantics and fingerprints.
Reject traversal/symlink bundles, duplicate JSON keys, NaN/Infinity, malformed or
mismatched metadata, extra configurations and invalid completion markers. Count
failed/missing warmups/measured rows separately. If a bundle was never produced,
report missing configuration and known build/sort trial counts plus lookup-count
bounds (availability unknown), not a fabricated exact lookup total.

## Statistics, plots and report

Per dataset/algorithm/operation/category summarize successful measured ns only:
count,median,mean,sample SD(n-1),min,max. Retain all observations/outliers and
warmups. Failed/interrupted/missing totals remain visible; null SD for<2 successes,
null statistics for0. Lookup additionally divides statistics by batch size and
labels them normalized batch-average ns/query, never individual latency.

Cross-dataset groups fix family,operation,algorithm,N,source distribution,query
policy/query seed/structure seed,batch size,parameters,build/platform/source identity.
First summarize repetitions per declared dataset. Collapse identical ordered
input fingerprints (insertion fingerprint for structures) into one unit using
median of their per-dataset medians; then equal-weight distinct-dataset medians.
Retain declared-seed counts and distinct-input counts. Different distributions
remain separate even if prepared hashes coincide; never count them as independent
replicates. Report median/mean/sample SD/min/max of dataset medians. No confidence
interval/significance test or universal ranking; one session is not independent
session replication. Seed/query repetitions are not independent datasets.

plot_results.py revalidates raw and computes summaries; it never trusts arbitrary
manually entered numbers. Matplotlib Agg, bundled DejaVu Sans, fixed style/SVG
hash salt, explicit stable PDF metadata, SVG+PDF output. Separate figures for
family/operation/distribution/query policy: central median of dataset medians with
min/max dataset-median error bars over size, and per-dataset trial min/max spread.
Linear y axes start at0; input-size symlog axis explicitly labels its scale and
linear region at N<=1. Units ms for sorting/build; ns/query for normalized lookup.
Titles/manifest record distinct datasets, declared seeds, R, filters, source raw
hashes, transformations, sizes, metric semantics, dependencies and output hashes.
No unsupported count/memory figure: manifest/report identify missing evidence.
Completeness table/figure retain successes/failures/missing/interrupted commands.
Reports include protocol/environment/workloads/audit/all-family results/spread,
limits, reproduction and deferred work. Summary/report/figure bytes must regenerate
on the same plotting stack; dependency versions/fonts/backend are recorded.
Cross-platform/font/version byte identity is not promised.

## Resource and runtime gates

One child configuration/structure resident at a time. Planning workspace upper
bound max(16*N,16*N+128*Q*9,512*N+128*Q*9), excluding runtime/allocator/analysis
memory. Not measured memory/hard RSS cap. Dataset/input/source copies and plot
processing also use memory. Require available RAM >=max(512MiB,2*workspace), and
free disk>=max(128MiB,2*disk allowance); use accessible cgroup headroom too.
Disk allowance:2MiB per configuration +4096 bytes per row upper bound +256 bytes
per planned query +512KiB per potential figure pair +32MiB report/analysis reserve.
These are planning allowances, not measurements. Dry run reports them explicitly.

Estimate full wall runtime after validated smoke: derive per-family observed
wall/timed costs; scale N*log2(N+1) for sorting/structures and N*Q for linear-search
dominant array batches, sum full configurations and use a documented safety factor.
Include setup/validation, not just timed intervals. Record model and assumptions;
it is a forecast with shared-machine uncertainty, not a promised runtime. Record
available OS/kernel/CPU/RAM/compiler/CMake/flags/executable+tool+source hashes,
limits, cgroups, affinity/governor/load; no thermal/frequency/load control claim.
If finite limits/headroom or runtime estimates make full execution unreasonable,
retain the validated pipeline/smoke and explicit full plan/deferred rationale.
Never reduce the matrix and label it full. No inputs above1M in this milestone.
