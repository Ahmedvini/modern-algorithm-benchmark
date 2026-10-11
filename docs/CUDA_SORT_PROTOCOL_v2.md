# CUDA sorting correctness contract v2

This revision supersedes the dependency pin and result protocol identity in
[v1](CUDA_SORT_PROTOCOL_v1.md); v1 and its source bundles remain immutable history.
The first v2-bundle validation on Colab stopped at configure: installed
`cub/version.cuh` was CUB 3.0.1, not the initial 3.0.0 pin. No sorter ran in that
attempt. Evidence and the independent upstream review are under
`results/raw/cub_correctness_colab_20261009T223853955936Z/`.

## Reviewed dependency change

Use the CUDA toolkit's installed CUB 3.0.1, reviewed against canonical
[NVIDIA CCCL commit f19d875da0d8bfb2e38c109b2b40522b8abbbbc3](https://github.com/NVIDIA/cccl/tree/f19d875da0d8bfb2e38c109b2b40522b8abbbbc3)
(release v3.0.1). The installed version header matches this immutable revision;
its only difference from the previously reviewed version header is
`CUB_VERSION 300000` becoming `300001`. The SortKeys header hash is unchanged.
The aggregate license is byte-identical; CUB remains BSD-3-Clause. Upstream headers
and licenses are not edited. No dependencies are downloaded during configure.

| Revision-qualified file | SHA-256 |
| --- | --- |
| cub/cub/version.cuh | 316819d3be158deebcf40e96dde6d8d08e7910e9740a69b111677d0c5a21c124 |
| cub/cub/device/device_radix_sort.cuh | 7190cd469e955b2bd08dacb6e4a06a4600ee9d6547747a8148750bb6a97d29be |
| LICENSE | 01b767dcd7d36f42efb608076741cf83f154a995e198028cb698aadc3a43b63b |

Configure still rejects mismatching header hashes; compilation requires
`CUB_VERSION == 300001`. This is a reviewed pin update, not an unchecked version
range. Full installed cub/thrust/cuda tree hashes are recorded per validation;
two matching reference headers do not prove the entire installation equals an
upstream release. CUDA toolkit >=13.0, CMake >=3.18, C++17/nvcc, explicit CUDA and
CUDA-SORT opt-ins, and CPU-only defaults remain as defined in v1.

## Unchanged algorithm and validation contract

The public adapter remains `cub_radix_sort_v1`: full-domain signed int32 ascending
sort using CUB `DeviceRadixSort::SortKeys` over all 32 bits. Per-call RAII buffers,
checked CUDA operations, current-device/stream0 use, allocation and exception
semantics, and no CPU fallback are unchanged. Equal-key stability remains
unobservable in the keys-only API. Input above INT_MAX is unsupported.

The result identity is now `cuda_sort_correctness_v2`, schema 1, CUB version
300001. The unchanged 475 input fixtures and four full-vector comparisons per
fixture require 1,900 checks per execution. Run directly and again through CTest;
report these as two executions of the same cases, not 950 distinct inputs.
All v1 edge, random, signed-boundary, non-power-of-two, repeated-call and registry
checks remain required. Missing hardware/exit77 is not a pass. The runner rejects
old/incompatible protocol versions and CUB identities.

Use an exclusive fresh checkout/output for retry; preserve the failed original
attempt, source archives and diagnostics. A fresh operational kernel preflight,
successful sorter build, direct test, non-skipped CTest and unchanged source
manifest are required for COMPLETE. This document freezes requirements before
the retry; observed results belong in the audit, not an assumed completion here.

No GPU timing, comparison instrumentation or performance experiment is added.
After observed correctness success, the next milestone is a separate synchronized
H2D/device/D2H/host end-to-end timing protocol and engine. No100M experiment.
