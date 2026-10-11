# Project files changed

No source file removed. Evidence/build additions are confined to this new run.

- README.md: Observed correctness status, evidence and next GPU timing step.
- cmake/cuda.cmake: Exact reviewed CUB3.0.1 header pin; default isolation unchanged.
- docs/ALGORITHMS.md: Current validation status/results/limitations with retained evidence links.
- docs/AUDIT.md: Current validation status/results/limitations with retained evidence links.
- docs/BENCHMARKING.md: Current validation status/results/limitations with retained evidence links.
- docs/CUDA_SORT_PROTOCOL_v2.md: Frozen dependency-contract extension before retry.
- docs/CUDA_SORT_VALIDATION_GUIDE_v3.md: Updated reproducible cloud/CLI handoff.
- docs/EXPERIMENT_PROTOCOL.md: Current validation status/results/limitations with retained evidence links.
- docs/ROADMAP.md: Current validation status/results/limitations with retained evidence links.
- scripts/validate_cuda_sort.py: v2 protocol and reviewed dependency identity.
- src/cuda/cub_sort.cu: Compile-time CUB version assertion only; algorithm unchanged.
- tests/test_cuda_sort_handoff.py: Accepted3.0.1 identity; reject old/unreviewed versions and old protocol.
- tests/test_cuda_sorting.cpp: Result protocol label only; all475 fixtures unchanged.
- third_party/cub/README.md: Reviewed source, license and pin update rationale.
- third_party/cub/UPSTREAM.json: Pinned3.0.1 commit/URLs/hashes; retain previous reference.
