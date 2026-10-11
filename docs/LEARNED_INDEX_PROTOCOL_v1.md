# Learned rank index protocol v1

This additive phase does not alter any frozen CPU/GPU or historical study.
The implementation owns an ascending signed-int32 vector. Construction rejects
unsorted input. Lookup returns the first equal index or nullopt, matching the
existing binary-search contract. No inserts, updates or deletion are supported.
Copies and moves use ordinary vector ownership semantics.

The model is a single endpoint affine rank predictor, fixed before evaluation:
map the minimum key to rank0 and maximum to rank N-1, clamp predictions to the
stored range, and use a fixed radius32 correction window. Differences use signed
64-bit arithmetic. Floating predictions are clamped before integer conversion.
Empty/singleton/all-equal inputs have defined predictions. A bounded lower-bound
search is accepted only when its left boundary proves no earlier equal key and
its right boundary proves no omitted answer; otherwise binary-search the full
vector. A separate diagnostic call reports key comparisons, prediction distance
to the true lower-bound position and fallback, never during primary timing.

Construction owns one N-key vector, O(N) validation/copy and O(N) total storage;
model metadata is constant space. Queries are worst-case O(log N), not guaranteed
O(1). An endpoint model may predict poorly on skewed or duplicate-heavy data.
Logical capacity bytes and object sizeof are reported separately from process
peak RSS, which includes all process/runtime/allocator storage and never resets.

Use the existing deterministic generator, sorting and make_search_batches helper.
Both binary search and the learned index receive the identical 1000-query
mixed_50 batch (exactly500 hits/500 misses), with query seed2718. Datasets use
four existing distributions, sizes1000/10000/100000/1000000 and held-out dataset
seeds42/2718/314159. Seed1729 is development-only and not in the evaluation matrix.
The radius and model are not tuned on evaluation datasets. Training/build uses
only each indexed vector; held-out refers to dataset/configuration evaluation,
not pretending the indexed keys were unseen by construction.

Five measured repetitions and one warm-up; cyclic algorithm order. Time each
complete query batch with steady_clock nanoseconds. Query generation, sorting,
input copies, diagnostics, output validation and serialization are outside query
timing. Report batch latency and batch latency/1000 as normalized average, never
direct individual-query duration or maximum per-query latency. Record build time
separately per repetition including index copy/validation; model destruction is
outside that interval. Raw records retain correctness/failure and run identity.

Summarize repetitions within each dataset first (median, mean, sample SD, min,
max); cross-seed summaries equally weight distinct dataset medians. Retain every
outlier, publish no significance or universal ranking claims. Binary-search
comparisons and learned diagnostics are separate untimed observations. The
existing frozen 1M sorting and CPU/GPU protocols remain unchanged.
