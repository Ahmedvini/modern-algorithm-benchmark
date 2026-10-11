# Reviewed-source transfer and isolated T4 build/validation

**Status: READY for this isolated build and narrow correctness scope only.** No study authorization, performance trials or full prerequisite eligibility is implied.

## Authorization and source audit

The user's request explicitly authorized both reviewed-source transfer and an isolated build with narrowly scoped validation. Read AGENTS.md, README, roadmap, experiment protocol, latest T4 audit, frozen comparison identities, CMake/CUDA configuration, direct test sources/helpers, reviewed source policy, prerequisite runner and comparison CLI control flow before execution. The broader prerequisite runner was deliberately not used: it would execute additional probes/builds/tests outside this minimum scope. Historical guides describe older pins/status; the actual reviewed source/CMake CUB3.0.1 requirements were authoritative.

`git status --short` returned128: no Git repository metadata. No repository was initialized. Exact revision is the153-file SOURCE_IDENTITY.json content manifest, SHA256 `7ce8297b76037af65d6d2dbbf3e2ccf5ec4684849090ee554a6d9552fcd50bda`. Its144 implementation/test/script/dependency entries match the reviewed non-timing source policy; nine additional reviewed project/protocol/identity documents match the prior preserved project baseline. Frozen protocol/matrix/resource hashes and the independently pinned freeze/CMake review identities were verified. CUB3.0.1/300001, CCCL commit f19d875da0d8bfb2e38c109b2b40522b8abbbbc3 is unchanged.

Only that allowlisted bundle was transferred. No result directories, credentials, dotfiles, caches, build artifacts, unrelated data or unreviewed working-tree differences were included. Archive SHA256: `953319b89a78d1e21498c4324570ec301bfb574eae4530a353db9c648b61b400`. The remote archive independently matched; all154 member paths (153source files plus generated identity manifest) were inspected as regular relative files with no traversal/duplicates before extraction. All153 contents matched before/after extraction and again after validation. Extraction used the verified-absent unique directory `/content/mab_isolated_20261011T010417197263Z/source`; no remote project was overwritten.

## Fresh isolated build

Session alias cpu-gpu-validation, ID gpu-t4-s-kkb-usw4b0-21qggbdn9iask. Fresh management diagnostics observed Tesla T4, UUID GPU-c51b969a-fbb1-a810-8346-93e2f6fc1849, driver580.82.07, GPU15360MiB total/14913MiB free; nvcc13.0.88; CMake3.31.10; G++13.3.0. These snapshots do not reserve resources. Remote ENVIRONMENT.json retains CPU/RAM/disk and whitelisted environment observations without secrets.

Build directory: `/content/mab_isolated_20261011T010417197263Z/build-release` (new, separate from source/history). Release, C++17/CUDA17, host/CUDA release flags -O3 -DNDEBUG, CUDA architecture75, OpenMPON, CUDA/CUDA_SORT/comparisonON, sanitizersOFF, BUILD_TESTINGON. Configuring only registers tests; no CTest discovery or test scheduling occurred. Built exactly requested targets cpu_gpu_comparison, comparison_input, test_cuda_sorting, test_mergesort and their dependency closure, using two build jobs. Production prepared-timing libraries are linked because the worker requires them; linking is not executing diagnostic samples.

Configure and build exited0. Actual configured OpenMP metadata: version 4.5, flags -fopenmp; requested threads were not a workload in this task. Binary paths/hashes/sizes, compile_commands.json, CMakeCache.txt and generated metadata are retained in remote_evidence/validation/. The built cpu_gpu_comparison successfully emitted --describe metadata (exit0) identifying cpu_gpu_comparison_driver_v1, Release, no sanitizers, CUB300001. --describe returns before any sorting/trial/resource-query path. No normal comparison invocation or --resources was made.

Warnings: 341 retained warning diagnostics. Every recorded warning is "style of line directive is a GCC extension", from nvcc-generated host translation units under the existing -Wpedantic flag. See remote_evidence/validation/build.stderr.txt and RESULT.json for every diagnostic. No flags/source were changed or warnings suppressed; build and correctness succeeded despite this toolchain warning.

## Narrow correctness outcomes

| Direct validation | Observed result | Exit |
|---|---|---|
| test_mergesort | 4015 differential inputs through public/registry/repeated paths; stable-merge fixture passed |0|
| test_cuda_sorting |475 inputs,1900 complete-vector output checks; cub_radix_sort public/registry/repeated/interleaved paths; status ok|0|
| cpu_gpu_comparison --describe | Build/implementation metadata only; no sorting/timing |0|

GPU test protocol cuda_sort_correctness_v2 reports runtime API 13000, driver API 13000, device0, compute capability7.5, CUB300001. This establishes actual production CUB sorting on the current T4; it is not merely hardware visibility or a version command. Empty/singleton, boundaries, duplicates, negative/extreme values, deterministic distributions and tile-adjacent/non-power-of-two sizes up to65537 are in the unchanged existing correctness test. No CPU fallback was substituted.

Two correctness executables passed; zero failed/skipped among those two. The metadata-only command also passed. No broader CPU regression suite, sanitizer suite, OpenMP actual-team/race tests, prepared timing smoke, resource workspace queries, pilot or study ran. Those remain unexecuted in this isolated run rather than claimed fresh passes. No performance metrics, benchmark CSV, warm-up batches or measured trials were generated. The comparison worker's full numerical/trial path remains unexercised here by design.

## Evidence and preservation

Downloaded remote archive SHA256 `764d00c2200ae835c4fd91a8d7dfa1b839edb7362412e70af63712afdd9af412` matches the remote value. All33 sealed remote evidence files were independently rehashed, with complete membership matching. Configure/build/test stdout/stderr, attempt/exit records, source identities, environment, binary hashes, failure/warning information and plan are under remote_evidence/validation/. Exact local/remote commands and statuses: COMMANDS.md, individual JSON records and EARLY_COMMANDS.json.

All11696 pre-existing result files,177 project files,65 local build-metadata files preserved by before/after membership and SHA256 comparison. Rechecked26 protected anchors with the existing independently pinned CMake exception,80 production/header/dependency files,144 reviewed source entries and3 frozen members; zero missing/changed/unexpected entries. Local source/tests/protocols/build metadata and all historical evidence remained untouched. All local additions are confined to this new evidence directory. Remote writes are confined to the new upload, isolated source/build/validation directory and its new archive. No commit, push, deletion or destructive cleanup occurred. The session/source/build are left in place.

No build or correctness failure occurred. The Git128 diagnostic is retained as missing metadata, not concealed or mislabeled a passing Git check. Hash manifests provide local retained integrity evidence, not external signed attestation or proof against arbitrary transient modifications.

## Remaining gates and next action

Stop after isolated validation. Review this audit and retained evidence, then separately authorize any additional prerequisite/resource validation or study execution. This run did not produce a study-eligible PREREQUISITES.json, establish fresh workspace allocations at the full matrix sizes, validate actual two-worker teams, repeat sanitizers/full regression suites, or measure performance. Availability/compilation/correctness does not authorize or prove the frozen full study. No performance ranking is claimed.
