# CPU/GPU provenance and non-timing selection repair v1

This implementation note changes validation tooling only. Frozen protocol,
matrix, resource CSV, freeze, CMake review, production adapters and CUB3.0.1 stay
unchanged. No prerequisite run, timing trial or GPU execution is authorized here.

## Independent source identity

`scripts/cpu_gpu_provenance.py` pins the accepted freeze SHA256
`518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6`
and the existing CMake review SHA256
`b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a`.
Those identities already occur in accepted evidence. It verifies the three
frozen assets, then reads expected source digests from that verified matrix.
It never obtains expected adapter identity from retained run metadata. The
only exception is the exact additive CMake change in the pinned existing review.
Duplicate JSON keys, invalid digests/paths, absent roots and contradictory
anchors are rejected. Legacy source manifests exclude documentation; frozen
documentation is checked directly and optional retained claims must agree.

Both pilot and study performance analysis enforce these anchors. The regression
fixture `tests/fixtures/cpu_gpu_provenance_reproducer.py` is byte-identical to the
previous review's reproducer. Tests copy it to a disposable directory, accept its
unchanged synthetic baseline, then reject its mutually rehashed adapter mutation.
Its 1200 measured/240 warm-up records are synthetic, not experimental evidence.

## Reviewed non-timing selection

No safety labels exist in the current CTest definitions. Instead,
`docs/NON_TIMING_TEST_SELECTION_v1.json` records every CPU/CUDA test's reviewed
classification, exact command template and a digest snapshot of all engine,
test, script and dependency source files. A source change requires explicit
review and snapshot renewal before selection. This is a repository safety policy,
not a sandbox or proof about a substituted executable. A future execution must
still establish correspondence between its fresh binaries and reviewed sources.

`scripts/non_timing_tests.py` only discovers/plans; its CLI never executes tests:

```sh
python3 -B scripts/non_timing_tests.py --build-dir build/EXISTING_RELEASE
# Or avoid CTest entirely when reviewing previously captured discovery:
python3 -B scripts/non_timing_tests.py --build-dir build/EXISTING_RELEASE \
  --discovery-json /path/to/ctest-discovery.json --output /path/to/NEW-plan.json
```

CPU selection is exactly 19 groups: baselines, cli, comparisons,
cpu_gpu_comparison_framework, cuda_benchmark_analysis, cuda_preflight,
cuda_sort_handoff, datasets, environment_manifest, memory, memory_unsupported,
mergesort, metrics_cli, pdqsort, quicksort, radixsort, searching, structures,
timsort. `cuda_benchmark_analysis` has no executable argument and skips its two
GPU timing methods. Mock-based CUDA preflight/handoff tests execute no GPU work.
The comparison framework uses synthetic records, subprocess doubles and small
untimed input generation. Other selected groups check correctness, invariants,
comparison counts, serialization or process memory, without timing engines.

All ten CPU timing groups are excluded, including `parallel_mergesort` (embedded
N32768/W1/R2 timing). CUDA builds add two correctness tests only with explicit
`--allow-gpu-correctness`; `cuda_benchmark_gpu_framework` is always excluded.
Unknown/missing/duplicate tests, unreviewed commands/arguments/source, fixture
dependencies, environment overrides and other unreviewed CTest properties fail
closed. Known timing entrypoints cannot be admitted by merely changing their
classification. Execution via the shared helper saves selection before calling
CTest, serializes it and checks exact coverage/no skips. This repair only tests
that execution helper with doubles.

`validate_cpu_gpu_pilot.py --prerequisites-only` uses this helper and labels its
result `validation_scope=non_timing_correctness_v1`, `study_eligible=false`.
The study runner and analyzer reject that subset as full-study prerequisites.
The unchanged full frozen gate includes timing-framework coverage and remains
outstanding. Non-flag legacy pilot validation retains its original scope.

## Validation evidence

See [the repair audit](../results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/FINAL_AUDIT.md)
for exact discovery, synthetic/static commands, failed attempt, final test counts,
selection, preservation hashes and limitations. No selected CTest suite or fresh
prerequisite validation was executed. Full-study launch remains **NO-GO**.
