# CUDA sorting correctness contract v1

Status: source implementation and cloud validation handoff; GPU compilation and
sorting validation are pending. Historical Colab runtime evidence is sufficient
to begin implementation, not proof the new sorter works. No timing experiment is
authorized by this correctness slice. Original roadmap CUDA milestone remains open.

## Dependency and build isolation

NVIDIA CUB DeviceRadixSort::SortKeys, reviewed against CCCL v3.0.0:
https://github.com/NVIDIA/cccl/tree/v3.0.0/cub . CUB is BSD-3-Clause; the complete
upstream aggregate LICENSE is retained in third_party/cub/LICENSE, with attribution
and reference hashes. No upstream algorithm is copied/modified in project source.
Use the CUDA toolkit's installed headers, not a network fetch during CMake.
This initial adapter pins CUB_VERSION=300000 (3.0.0), and the reviewed SortKeys and
version header SHA256 values at configure time. Other toolkit/CUB combinations
must fail explicitly until separately reviewed; do not bypass the checks. The cloud
archive records CUDA 13.0.88, but does not record CUB headers: compatibility with
this exact pin still requires a cloud build. Transitive toolkit headers are recorded
in the cloud run's dependency manifest, not asserted to match an unobserved revision.

MAB_ENABLE_CUDA remains OFF by default. MAB_ENABLE_CUDA_SORT is a separate OFF
opt-in requiring CUDA ON. Readiness-only CUDA builds retain their existing toolkit
minimum and probe behavior. Sorting requires CUDA toolkit >=13.0, CMake>=3.18,
C++17/nvcc and a compatible host compiler. No CUDA dependency or GPU test is added
to CPU-only builds. Separate GPU registry uses the existing Sorter function-pointer
shape; CPU registry/defaults/timing schemas stay unchanged.

## Public contract and ownership

mab::cub_radix_sort(Values&) sorts signed int32 keys ascending, preserving the full
multiset including INT32_MIN/MAX, negatives and duplicates. Operates on the current
CUDA device in the calling host thread (default device0); no automatic CPU fallback.
Every call checks device properties, even empty/singleton calls, which then do no
sorting work. Inputs larger than INT_MAX or whose byte count cannot fit size_t are
rejected before allocation. No shared mutable buffers, caches or counters.

For nontrivial input, allocate an independent host output, two N-key device buffers,
and CUB-requested device temporary storage per call. Submit H2D, full-bit-range
[0,32) CUB SortKeys, stream0 synchronization, and D2H. Check all API/launch/sync/
copy results. Checked cleanup on success precedes swapping host output into the
caller. Thus a reported exception leaves the original host vector unchanged.
RAII cleanup during unwinding cannot throw; secondary cudaFree errors are printed
to stderr rather than hiding the primary exception. No device reset or global
runtime policy changes. Concurrent host callers are not a performance contract;
stream0 scheduling/runtime allocator behavior can serialize work.

CUB handles signed ordering by its documented sign-bit transform; the adapter does
not use abs, signed overflow, truncated bits or a comparison-sort fallback. Upstream
SortKeys is stable; equal-key stability is not observable in this keys-only API and
no key/payload stability test is claimed. Expected device workspace O(N) plus CUB
scratch; host output O(N). These are theoretical/allocated shapes, not measured RSS.

## Correctness and evidence

GPU-only cuda_sorting CTest compares full vectors with std::sort through public,
GPU-registry and repeated-call paths. Cases include empty/singleton/two keys,
negative/positive/mixed/extreme values, duplicates/all equal, sorted/reverse,
seeded generator distributions, non-power-of-two and boundary-adjacent sizes through
65537. No specific CUB tile size or internal branch coverage is inferred. Missing
runtime/device at test startup returns77/CTest skip; failures after availability
returns1. A skip is never a GPU pass. JSON output records case/output-check totals,
algorithm/version, actual CUB/runtime API versions and current device identity.

scripts/validate_cuda_sort.py requires a new output directory and captures exact
argv/cwd/exit/stdout/stderr. A fresh operational preflight must pass before configure,
then build the sorter/test and run the test directly plus targeted CTest. Direct
exit77 fails the validation handoff, even if CTest would consider it a skip. Capture
CMake/compile commands and installed cub/thrust/cuda header hashes/licenses.
Exclusive build/output locations, source manifest and terminal COMPLETE/FAILED/
INTERRUPTED markers preserve incomplete runs. COMPLETE requires actual successful
sorter output, not only runtime smoke. No live Colab connection is assumed.

## Deferred benchmark contract

No GPU performance numbers or primary timing rows in this milestone. After observed
GPU correctness success, freeze a separate benchmark version defining datasets,
seeds, warmups/repetitions, memory planning and reuse, CUDA-event H2D/device/D2H
measurements and host steady_clock end-to-end boundaries (including allocation
scope). Compare equivalent CPU data and retain dataset-level repetitions/outliers;
keep kernel-only versus CPU end-to-end comparisons explicitly distinct. No100M.
