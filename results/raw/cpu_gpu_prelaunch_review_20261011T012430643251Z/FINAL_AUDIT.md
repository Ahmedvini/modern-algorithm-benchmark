# Final pre-launch independent evidence review

**Verdict: NO-GO for launch readiness.** The warning investigation found no demonstrated sorting defect. The isolated build/correctness milestone passed, but the fresh, study-eligible prerequisite and resource/team evidence required by the current runner is not established. This review neither authorizes nor executes additional validation or the study.

## 1. Warning origin and interpretation

Independently parsed the complete retained `remote_evidence/validation/build.stderr.txt` under `results/raw/isolated_colab_revalidation_20261011T011459127026Z/`: exactly **341** warnings, all `style of line directive is a GCC extension`; no `error:`/`fatal error` diagnostics. All other configure/build/correctness/describe stdout/stderr logs have zero warning/error diagnostics. Build exit status was 0.

| Originating CUDA translation unit | Log lines | Warnings |
|---|---:|---:|
| src/cuda/comparison_resources.cu | 1–232 | 80 |
| src/cuda/cub_sort.cu | 233–520 | 100 |
| src/cuda/cub_timing.cu | 521–993 | 161 |

The three blocks begin at nvcc-generated `/tmp/tmpxft_*_*.cudafe1.cpp:1:3`. Their diagnostic excerpts explicitly show GNU-style markers, e.g. `# 1 "/content/.../source/src/cuda/comparison_resources.cu"` (log lines 1–3). Each block also ends with warnings in generated `.cudafe1.stub.c`. Reported positions in original `.cu`/header files are mapped source positions, not 341 independently defective C++ statements. The three original CUDA sources contain no explicit numeric/`#line` directives. Retained compile_commands.json records nvcc13.0.88 compiling C++17/architecture75 with `-Xcompiler=-Wall,-Wextra,-Wpedantic`; the retained host compiler is GCC13.3.0. The flags originate at CMakeLists.txt:207 and cmake/cuda.cmake:48,56.

**Assessment:** expected pedantic diagnostics for nvcc-generated GNU line markers in this observed toolchain configuration, rather than an observed CUB API incompatibility, compilation failure or sort-correctness error. No suppression or source/flag modification is recommended by this review. Exact diagnostic tokens and compilation flags are verified; attribution to the compiler's generated-marker/host-pedantic interaction is supported by these excerpts. Complete temporary generated files were not retained, so their full contents and every compiler-internal transformation cannot independently be inspected. Successful tests do not prove absence of arbitrary toolchain defects. WARNING_DIAGNOSTICS.json retains every diagnostic with its original log line; INDEPENDENT_FINDINGS.json retains compile commands and mapped locations.

## 2. Actual validation coverage and remaining gates

Reviewed RESULT.json, PLAN.json, attempt/command records, stdout/stderr, CMakeCache.txt, generated build metadata and the unchanged test/CLI source. Exactly five remote commands are recorded, all exit0: configure, targeted build, direct `test_mergesort`, direct `test_cuda_sorting`, and `cpu_gpu_comparison --describe`. These were historical commands inspected here, not re-executed.

- Sequential Merge Sort: **4,015 differential inputs** through public/registry/repeated paths plus stable-merge fixture.
- Production CUB: **475 inputs / 1,900 output checks**, status ok, cuda_sort_correctness_v2, CUB300001, runtime/driver APIs13000, device0/CC7.5. tests/test_cuda_sorting.cpp:19–38 verifies public, registry, interleaved and repeated calls against full-vector CPU results. Size coverage ends at65,537 (lines64–65), not1M. No CPU fallback was substituted.
- `--describe` is metadata only: src/benchmark/cpu_gpu_main.cpp:86 returns before resources, input loading, prepared sessions and trials. Linking prepared timing code establishes build compatibility, not execution or timing validation.

Two correctness executables passed, zero failed or skipped among those two. Unexecuted in this isolated run: broader CPU Release regression, ASan/UBSan, OpenMP actual-team/race validation, prepared GPU framework tests, comparison numerical/trial path, standalone all-size workspace/resource checks, pilot/study and performance measurements. A separate device memory checker/Compute Sanitizer run is not established; CPU ASan/UBSan cannot validate device memory or establish race freedom. Historical pilot and GPU timing evidence remains useful but is not a fresh pass on these new binaries.

**Concrete launch blocker:** no study-eligible PREREQUISITES.json bound to the fresh worker is retained. RESULT.json explicitly sets study_eligible=false. scripts/run_cpu_gpu_pilot.py:107–123 requires full_protocol_v1, matching current source/binary identities and completed CPU Release, CPU sanitizer, CUDA suite, CUDA correctness and preflight command records. scripts/analyze_cpu_gpu.py:88–103 enforces the same distinction. The only retained uppercase PREREQUISITES.json found under results/raw is the accepted pilot's validation_v3 artifact; its worker digest is `df88672d04b64427523bbd4e0a7b1271c3113315bf645cdff4e490ad875c611c`, whereas the fresh BINARIES.json records `62a2290576b0618e1a8e9fb3faeed8aa5a0d2784ba655ba8102314be0a21571a`. It cannot be reused as fresh matching prerequisite evidence.

Do not solve this by relabeling the narrow run. The existing prerequisite-only path explicitly produces non_timing_correctness_v1/study_eligible=false (scripts/validate_cpu_gpu_pilot.py:89–98). The alternative broader path invokes GPU timing-framework tests and then the pilot (lines85–87,99–105); it is not an appropriate command to run under this review authorization. A separately authorized validation plan must reconcile and satisfy these gates without accidentally launching a pilot/study.

## 3. Frozen identities and preservation

Independently rehashed all three freeze members; exact approved hashes match:

- Protocol: `7738d21ff0ea611c04a557418182ab562769b568c7dc0b898ca5d50280e21c70`.
- Matrix: `29f9f2765e466a88fc3a7b6e590b1c38dd1ebe5f4f003a37e02aabc9b7074833`.
- Resource CSV: `324a67c9668d258366f738348ad853cbadd65ce4edd6f34b3ec16f4baaafeaab`.
- Freeze manifest: `518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6`.

All26 protected anchors match the effective approved policy:25 exact original matches plus the already approved additive CMake exception in docs/CPU_GPU_DRIVER_REVIEW_v1.json (its independently retained digest also checked). This is not a claim that original/current CMake hashes are identical. Production adapter digest remains `b6d7f37c7494587fc6e4a676c00c166dc322d31cce96710811e3a4cb9cd8b9cb`; CUB UPSTREAM.json digest remains `477b1ee70b0a9113c9f98b263c19a31d05ccee54f45ce8476aec4cc98965ced1`, release3.0.1/300001, commit f19d875da0d8bfb2e38c109b2b40522b8abbbbc3. Successful reviewed CMake configuration checked the pinned installed version/SortKeys headers; this narrow run did not archive a new complete installed CCCL-tree manifest.

Independently verified the isolated audit's75 sealed members with exact membership, all33 downloaded sealed files, all153 transferred source entries against local files, and byte identity of retained pre/post remote source manifests. These are retained hash/record checks, not new remote observations or an external signed attestation.

Before/after preservation: **11,833 historical result files**,177 project files,65 local build-metadata files,80 production/header/dependency files and144 reviewed source entries all match SHA256 baselines; zero missing, changed or unexpected historical result files. Only this new review evidence directory was added. Prior initial source-verifier failure and correction remain preserved; no attempt was hidden or rerun. See BEFORE.json and PRESERVATION.json.

## 4. Environment and resource review

Retained T4 validation: session cpu-gpu-validation, GPU UUID GPU-c51b969a-fbb1-a810-8346-93e2f6fc1849, CC7.5, driver580.82.07, nvcc/toolkit13.0.88, runtime API13000, GCC13.3.0, CMake3.31.10, Linux6.6.122+, Python3.13.15, Release -O3 -DNDEBUG, OpenMP4.5. The completed production correctness test establishes actual GPU use then; no current remote availability check was made here.

ENVIRONMENT.json reports affinity[0,1],2 logical CPUs on **one physical/core ID** with2 siblings, Xeon CPU@2.00GHz; RAM13,605,822,464 bytes, MemAvailable12,524,589,056 bytes, no swap, disk free75,442,806,784 bytes. Management diagnostics retained with the validation audit report15,360MiB GPU total/14,913MiB free. Earlier same-session diagnostic evidence reports uncapped cpu.max and memory.max, but the isolated ENVIRONMENT.json has no fresh cgroup headroom record. All numbers are snapshots, not reservations or guarantees at launch; management free memory is not a replacement for fresh CUDA cudaMemGetInfo gates.

Frozen resource limits remain unchanged:1GiB host headroom under both MemAvailable/applicable cgroup limits and1GiB disk;64MiB per workspace; combined device payload<=256MiB and<=half fresh runtime free memory. Calculated payloads (not observed allocations):

| N | Known host24N bytes | Device planning16N+two64MiB allowances bytes |
|---:|---:|---:|
|1,025|24,600|134,234,128|
|65,537|1,572,888|135,266,320|
|1,000,000|24,000,000|150,217,728|

Runtime/context/staging/allocator/tasks overhead is additional. Historical N65,537 sizing passed on a different T4 session with279,295 bytes per workspace; historical pilot recorded1M workspaces4,178,687 bytes each. These support feasibility, not current measurements or an upper bound. Fresh prepared/default-stream queries and diagnostic allocation checks at all three sizes remain required; production correctness's internal allocations do not report those values. The runner does this before trial execution at scripts/run_cpu_gpu_pilot.py:175–180; it was not run here.

The two-logical-CPU allocation satisfies the nominal frozen two-thread policy, subject to actual quota/affinity and team checks. It cannot support a claim about two physical cores or broader4/8-core scaling. Actual two-worker execution above32,768 remains unverified in this isolated run. OMP policy values were unset during narrow validation; the study runner explicitly applies the frozen policy before its environment snapshot (lines158–174), so unset values alone are not a protocol incompatibility.

Cloud CPU/GPU sharing, SMT contention, scheduling, frequency, thermals/cache state and background interference remain uncontrolled. Prior pilot variability and its single-seed workload subset do not establish stable full-study performance, significance or a universal winner. Frozen full matrix remains48 datasets/five modes,1 warm-up and5 measured calls per configuration:240 warm-ups/1,200 measured calls. Primary host-vector API timings must remain separate from prepared H2D/device/D2H/end-to-end diagnostics; prepared device time cannot serve as the primary CPU speedup denominator.

## 5. Scope assessment and next permitted action

The isolated FINAL_AUDIT.md accurately limits READY at lines3,33,45; its two direct correctness results and metadata claim are supported. It does not overstate full regression, sanitizer, prepared timing or study coverage. Historical documentation contains earlier-stage pending-tooling statements; current full-matrix tooling exists, so those historical statements are not treated as current blockers.

This review executed **zero** tests, CTest discovery, builds/configures, prerequisites/resource probes, GPU commands, warm-ups, measured calls or benchmarks. All inspection/hash commands exited0; no source, flag, protocol, historical artifact or build metadata was modified. Exact commands/statuses are in COMMANDS.md and per-command JSON. Warnings were not suppressed.

Next permitted action: present the remaining fresh prerequisite/resource/team validation scope for a **separate explicit authorization decision**. Do not launch the existing broad validator blindly: it also runs timing-bearing checks and a pilot. Do not change frozen eligibility requirements to make the narrow evidence pass. A new authorization must state which additional validation is permitted and how a fresh study-eligible bundle will be produced. This NO-GO is a readiness finding, not study authorization; stop here.
