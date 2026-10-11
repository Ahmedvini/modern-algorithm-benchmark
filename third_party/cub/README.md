# CUB dependency reference

Canonical upstream: https://github.com/NVIDIA/cccl . API reference release:
[v3.0.1](https://github.com/NVIDIA/cccl/tree/f19d875da0d8bfb2e38c109b2b40522b8abbbbc3), CUB_VERSION=300001.
CUB license: BSD 3-Clause, copyright NVIDIA Corporation and Duane Merrill.
LICENSE is the unchanged aggregate upstream license file, also covering CCCL's
other components. No algorithm/header is vendored or modified here; CUDA builds
use toolkit headers. Do not infer installed CUB identity from toolkit version.

Reviewed raw files at https://raw.githubusercontent.com/NVIDIA/cccl/f19d875da0d8bfb2e38c109b2b40522b8abbbbc3/:

| Path | SHA256 |
| --- | --- |
| cub/cub/device/device_radix_sort.cuh | 7190cd469e955b2bd08dacb6e4a06a4600ee9d6547747a8148750bb6a97d29be |
| cub/cub/version.cuh | 316819d3be158deebcf40e96dde6d8d08e7910e9740a69b111677d0c5a21c124 |
| LICENSE | 01b767dcd7d36f42efb608076741cf83f154a995e198028cb698aadc3a43b63b |

Configure checks the two installed CUB headers against these hashes. Cloud
validation additionally records the dependency tree hashes, compiled CUB_VERSION
and CUDA versions. Installation-specific transitive files remain part of the
recorded toolkit environment; actual sorter validation is recorded in the latest audit.
The adapter and tests are project code; preserve this license with redistributed
CUB-containing binaries. See docs/CUDA_SORT_PROTOCOL_v2.md.

Release tag resolved to commit f19d875da0d8bfb2e38c109b2b40522b8abbbbc3.
Revision-qualified downloads match all three reference hashes; see UPSTREAM.json.
The initial v3.0.0 reference and its hashes remain in previous_reference there.
Colab CUDA13.0.88 supplies v3.0.1: the first configure correctly rejected the old
pin. Independent upstream review found only the version macro changed in that
header; SortKeys and LICENSE hashes are unchanged. No upstream file was modified.
