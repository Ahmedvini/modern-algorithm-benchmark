# Phase 7 CUDA readiness protocol v1

Scope: non-destructive environment discovery and a reproducible future execution
path. This extends the roadmap with a preflight/guide milestone; CUDA sorting,
benchmark timing and acceleration results remain **not implemented/not run**.
Existing CPU interfaces, defaults, protocols and experiment bytes are preserved.

## Discovery and evidence

`python3 scripts/cuda_preflight.py --output NEW_DIRECTORY` exclusively creates
report.json, SUMMARY.txt and COMPLETE.json. No overwrite or resume. Record UTC,
OS/kernel/architecture/CPU, Python, source hashes, executable discovery, bounded
command diagnostics/return codes, NVIDIA display/compute PCI evidence (Linux),
driver evidence, toolkit/header/library paths, CMake version and CUDA-language
property availability. Missing commands/files are explicit. Discovery is scoped
to this process/container; no claim about hidden host hardware. Never install
packages, change permissions, drivers, environment variables or system settings.

Use only an explicit allowlist of CUDA/path environment variables. Do not dump
the environment, credentials or the entire PATH. Record resolved tools and CUDA
path entries; redact credentials in URLs and values of secret-named environment
variables from command diagnostics. Capture selected CMake cache fields, never
publish the whole cache. Temporary configure/build files are deleted after use;
retained reports include commands and diagnostics. Review reports before sharing.
Each command has a configurable finite timeout (default60s, range1..300).

When a discovered NVIDIA nvcc answers --version successfully and CMake>=3.18 is
available, configure this project's optional target in a fresh temporary build:
MAB_ENABLE_CUDA=ON, MAB_ENABLE_OPENMP=OFF, MAB_ENABLE_SANITIZERS=OFF,
BUILD_TESTING=OFF, Release, explicit CMAKE_CUDA_COMPILER. Build only
cuda_runtime_probe, then run it. Otherwise record each skipped step/reason; do
not attempt CUDA-enabled configuration without a working candidate compiler.
CMake property documentation is evidence of CMake's CUDA language feature, not
of an installed working compiler or device. Failures never imply CPU failure.

## Readiness classification

Capability fields retain all overlapping evidence; classification precedence is:

1. **operational**: project configure/build succeeds and the runtime probe's
   strict JSON reports enumeration and the checked kernel success (exit0).
2. **gpu_driver_unavailable**: NVIDIA GPU evidence exists, but neither successful
   nvidia-smi enumeration nor runtime enumeration establishes a usable driver.
   Missing driver evidence is unverified, not a diagnosis of a broken driver.
3. **driver_toolkit_unavailable**: driver/device enumeration works but no working
   NVIDIA nvcc is discoverable. Headers/libraries alone are not a full toolchain.
4. **toolkit_no_usable_device**: project CUDA target builds, but enumeration or
   the checked device0 runtime probe fails. Separate runtime stage/exit/diagnostic
   distinguishes no device, unavailable driver and kernel/allocation failures.
5. **toolchain_unverified**: nvcc answers, but CMake/build is missing, unsupported,
   skipped or fails; device usability is not inferred from nvcc --version.
6. **no_nvidia_gpu_detected**: no GPU evidence in available visibility probes and
   no working nvcc. This is absence of detection, not proof about host hardware.
7. **detection_unavailable**: visibility probes are unavailable/inconclusive and
   no stronger evidence establishes a category.

Runtime enumeration overrides absent management tooling. Contradictory evidence
is retained. All5 required hardware/toolkit scenarios have independent mocked
fixtures; extra unverified states avoid misleading readiness claims.

Exit0 means verified operational CUDA. Exit2 with a completed report means CUDA
unavailable/unverified, not CPU-project failure. Exit1 means a reporting/IO/internal
error; argparse usage errors exit2 without a completed report. Interrupted runs
exit130 and leave an explicit incomplete marker. COMPLETE means discovery finished,
**not** that CUDA is operational. No benchmark measurements in this schema.

## Build and runtime isolation

MAB_ENABLE_CUDA defaults OFF. CPU minimum CMake3.16/C++17 is unchanged. CUDA ON
requires CMake>=3.18, a NVIDIA CUDA toolkit>=11.0 with C++17 support and a compatible
host compiler; actual version/architecture compatibility must be checked. CUDA
language and FindCUDAToolkit run only inside the ON branch. The tiny target is
independent of mab_core and CPU sanitizer flags; CUDA+MAB_ENABLE_SANITIZERS is
explicitly rejected, use separate CPU sanitizer/CUDA build directories.
No GPU algorithms or sorting-registry entries are added. Existing OpenMP option
and default remain unchanged. CUDA_RUNTIME_LIBRARY is Shared (CUDA::cudart).

Runtime probe enumerates visible devices and records name, compute capability and
memory for each. It tests **device0 only**: allocate one int, launch a one-thread
kernel writing1729, check launch/synchronize, copy back, compare and free. No timing
or sorting is measured; CUDA context creation may itself use runtime memory.
Probe exit77 means enumeration unavailable/no devices (CTest skip), exit1 means
post-enumeration failure (CTest fail), exit0 means checked success. A failure
cannot become a successful preflight. Other devices' execution is unverified.

## Validation and completion

Before marking this scoped milestone complete: mocked classification/diagnostic/
timeout/output/privacy tests; actual CUDA-OFF default/explicit CMake option tests;
fresh full CPU Release and ASan/UBSan CTest (leaks disabled only for documented
ptrace recurrence); actual local preflight; hash verification of all previous
raw/processed/figures and frozen protocols. Review commands/warnings and retain
new unique evidence. GPU-target compilation/execution and Colab steps remain
explicitly unverified if prerequisites are unavailable. No expensive experiment.

The cloud guide must use an immutable source revision or verified archive,
separate CPU/CUDA builds, preflight evidence, explicit GPU allocation checks and
persistent output export. No unverified repository URL/revision is invented.
Future GPU sorting requires a new implementation/protocol: pin CUB/CCCL/license,
full CPU differential correctness, synchronized transfer/kernel/end-to-end metrics
and resource gates before experiments. No100M or CUDA performance study here.
