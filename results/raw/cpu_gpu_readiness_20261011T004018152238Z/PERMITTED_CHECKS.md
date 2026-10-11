# Authorized diagnostic plan, established before diagnostics

Source: user authorization for non-benchmark prerequisite/resource diagnostics
only; CPU_GPU_COMPARISON_PROTOCOL_v1.md:247-281,
run_cpu_gpu_pilot.py:51-92, capture_environment.py, cloud guide and previous
cub_workspace_65537_20261010T110457531249Z/COMMANDS.md.

Permitted command families:

1. Read/list/hash existing files; standard-library JSON parsing and source/build
   manifest comparison. Do not import or invoke project runners/guards/analyzers.
2. `cmake --version`, `python3 --version`, `gcc --version`, `g++ --version`,
   `nvcc --version` (if present); `g++ -print-file-name=libgomp.so` to locate the
   runtime without compiling; `ldconfig -p` to read library cache; `lscpu`.
3. Standard-library reads of the existing capture procedure's /proc/meminfo,
   /proc/loadavg, resource/cgroup limits and governor files; affinity, platform,
   CPU count, output-filesystem disk usage. Only relevant environment settings,
   never credential/configuration dumps.
4. Read /proc/driver/nvidia/version, /sys NVIDIA PCI metadata, device-node
   presence; if installed, `nvidia-smi` and the exact GPU detail/compute-app
   queries already used by run_cpu_gpu_pilot.snapshot. These are management
   diagnostics, not CUDA device execution.
5. `colab --help`, `colab --version`, `colab sessions`, and `colab status --session
   NAME` only for an existing returned session. No session creation/reconnect,
   software installation, upload, or remote build. Only if an existing session is
   accessible and the CLI scope is confirmed: `colab exec --session NAME --file
   OWN_DIAGNOSTIC_SCRIPT --timeout 120`, using only the already specified version,
   nvidia-smi, platform and resource reads. Any remote diagnostic must retain its
   own inner statuses and complete output; CLI exit0 alone is insufficient.
6. Existing artifact files/caches/build flags inspected as text/file hashes only.
   No project executable is launched, including --describe/--resources/--help.

All shell/program commands receive a retained exact argv/status record. Missing
tools are recorded as absent; they are not installed or treated as passed checks.
This plan grants no authority to execute the study or repair the environment.

Explicitly skipped: validate_cpu_gpu_pilot.py (even --prerequisites-only),
cuda_preflight.py, all CMake configure/build commands, all CTest commands,
test binaries, production/prepared sorting calls, CUDA kernel probes,
cudaMemGetInfo/CUB workspace/allocation diagnostics and runtime team tests.
Their implementations include operations forbidden in this authorization.

If a diagnostic command's semantics cannot be established by static inspection or
CLI help, stop that proposed command and report the scope ambiguity.
