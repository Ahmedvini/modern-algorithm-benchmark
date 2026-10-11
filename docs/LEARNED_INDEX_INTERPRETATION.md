# Interpreting the learned-rank evaluation

The version1 study contains48 declared configurations. Search preprocessing sorts
every dataset ascending. For a fixed size and seed, uniform, nearly_sorted and
reverse_sorted therefore become the same sorted uniform sample: the latter two
are permutations of that sample. Their recorded input/query fingerprints preserve
this identity. They are separate workload labels, not three independent key
distributions. Do not pool these labels to inflate the number of datasets.
Duplicate-heavy inputs provide the second sorted-key shape in this study.

Cross-seed summaries remain within each size/distribution group and equally weight
three input datasets. The final report additionally counts distinct content
fingerprints across declared configurations. No cross-distribution significance
test or confidence interval is claimed. Evaluation seeds are held out from
performance tuning, not forbidden from oracle correctness tests. The radius32
was specified before measurements and was not selected using evaluation timings.

The index owns an int32 vector. Its constant-size object contains the vector's
control metadata; model endpoints are read from the stored first/last keys.
`owned_capacity_bytes` reports vector capacity×4; `object_bytes` reports sizeof
the containing object. Neither includes allocator metadata. Process RSS includes
all input/index/query/runtime storage and is a different measurement.

`diagnose()` counts every executed key less-than predicate in endpoint prediction,
local correction, boundary certification, full fallback and equality determination.
It excludes index arithmetic, size checks, floating operations and bookkeeping.
The ordinary `find()` instantiates the same lookup with an ordinary comparator;
there is no global state or mandatory mutable counter. Exact small fixtures are
checked separately; larger counts depend on the concrete lookup strategy.

The endpoint model is deliberately limited: it is not a recursive/neural learned
index, and the indexed keys are used when fitting its endpoints. Build cost,
owned storage, fallback frequency and rank correction distance must accompany
latency rather than presenting only a favorable query result.
