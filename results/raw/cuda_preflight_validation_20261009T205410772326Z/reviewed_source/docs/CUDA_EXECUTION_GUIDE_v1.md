# CUDA preflight and Colab/cloud guide v1

This guide prepares future GPU work. **No CUDA sorter or GPU timing exists yet.**
The local validation machine has an NVIDIA PCI device, but no discoverable nvcc,
nvidia-smi or working CUDA driver evidence. CUDA target compilation, kernel
execution and the Colab workflow have **not been validated on a GPU**. Mocked
readiness results are tests, never hardware evidence. The existing CPU studies
remain frozen. Follow [the readiness contract](CUDA_PREFLIGHT_PROTOCOL_v1.md).

## 1. Allocate and verify an environment

In Google Colab select Runtime → Change runtime type → an available GPU hardware
accelerator, then connect. A selection is not evidence a GPU was allocated;
[Colab does not guarantee particular resources](https://research.google.com/colaboratory/faq.html).
Equivalent cloud environments need an NVIDIA GPU instance and provider-supported
CUDA image. Do not upgrade or replace hosted drivers from this guide.

Run discovery in a notebook `%%bash` cell (or ordinary cloud shell):

```sh
uname -a
python3 --version
cmake --version
command -v nvidia-smi || true
command -v nvcc || true
nvidia-smi --query-gpu=index,name,driver_version --format=csv,noheader,nounits
nvcc --version
```

Each command's status matters. Missing nvidia-smi/nvcc is expected on a CPU-only
runtime. `nvcc --version` is not a kernel test. nvidia-smi's displayed CUDA version
is the driver's supported CUDA level, not proof the toolkit is installed; see
[NVIDIA's compatibility explanation](https://docs.nvidia.com/datacenter/tesla/drivers/cuda-toolkit-driver-and-architecture-matrix.html).
Do not assume a GPU model, compute capability, toolkit version or free memory.

## 2. Obtain an identified project snapshot

Use one of these source paths. No canonical remote/revision can be inferred from
the local directory: its Git metadata is absent. Supply a trusted URL and immutable
commit yourself, or use the retained audited source archive.

Git checkout (requires network and a real published revision; **not locally tested**):

```sh
export MAB_SOURCE_URL='REPLACE_WITH_VERIFIED_REPOSITORY_URL'
export MAB_SOURCE_REV='REPLACE_WITH_FULL_IMMUTABLE_COMMIT'
git clone "$MAB_SOURCE_URL" modern-algorithm-benchmark
cd modern-algorithm-benchmark
git checkout --detach "$MAB_SOURCE_REV"
git rev-parse HEAD
git status --short
```

Archive alternative: upload `phase7_source.tar.gz` and its independently retained
SHA256 value to `/content` (or a cloud work directory). Do not use an unknown
archive. The Phase7 final audit records its hash. Before extracting:

```sh
export MAB_ARCHIVE_SHA256='REPLACE_WITH_RETAINED_AUDIT_HASH'
python3 - <<'PY'
import hashlib, os
from pathlib import Path
assert hashlib.sha256(Path('phase7_source.tar.gz').read_bytes()).hexdigest() == os.environ['MAB_ARCHIVE_SHA256']
PY
test ! -e modern-algorithm-benchmark || exit 1
tar -xzf phase7_source.tar.gz
cd modern-algorithm-benchmark
python3 - <<'PY'
import hashlib, json
from pathlib import Path
manifest = json.loads(Path('SOURCE_SHA256.json').read_text())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p, h in manifest.items())
print('Verified', len(manifest), 'source files')
PY
```

The generated archive contains source/docs/tests/vendors and a manifest, not old
experiment data. Its export/integrity commands are locally validated; uploading
and executing it in Colab is untested. Retain the archive/hash with future results.

## 3. Prepare CPU dependencies and fallback

Create empty output parents in a source-only checkout/archive:

```sh
mkdir -p results/raw results/processed results/figures
```

Preflight itself uses Python's standard library. Full CPU tests also require CMake,
a compatible C++17 host compiler, Python3 and Matplotlib/NumPy. The local validated
stack is Python3.12.3, Matplotlib3.11.0, NumPy1.26.4, CMake3.28.3, GCC13.3.0.
Cloud images vary; confirm compatibility before installing into a dedicated venv.
These dependency-setup commands are for the cloud, **not executed locally here**:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install 'matplotlib==3.11.0' 'numpy==1.26.4'
```

If a toolchain/venv package is missing, select a supported provider image or arrange
user-approved environment setup; preflight never installs anything. Do not use
privileged driver installation as a workaround. All following commands assume
repository cwd and the same activated venv. In separate notebook `%%bash` cells,
repeat `cd` and activation; shell variables/cwd do not persist between cells.

CPU fallback (validated project options, no CUDA compiler discovery):

```sh
cmake -S . -B build/cloud_cpu -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=OFF
cmake --build build/cloud_cpu --parallel 2
ctest --test-dir build/cloud_cpu --output-on-failure -V
```

OpenMP is optional; enable it explicitly when the image has a supported runtime.
CPU fallback never means GPU work succeeded. These commands/options were checked
locally; the cloud environment and its test outcomes remain unverified.

## 4. Save readiness evidence

Choose a previously nonexistent run directory. In a Python notebook cell:

```python
import datetime, pathlib, subprocess
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
run = pathlib.Path('results/raw') / ('cloud_cuda_preflight_' + stamp)
r = subprocess.run(['.venv/bin/python', 'scripts/cuda_preflight.py',
                    '--output', str(run), '--timeout-seconds', '180'], text=True)
print('preflight exit:', r.returncode, 'evidence:', run)
assert r.returncode in (0, 2), 'reporting failed; inspect diagnostics'
```

Exit0 requires actual checked device0 execution; exit2 means unavailable/unverified
CUDA and a valid completed discovery report. Read report.json and SUMMARY.txt before
continuing. COMPLETE.json means **discovery complete**, not GPU operational.
Exit1 is a reporting error; exit130 is interruption. Every attempted command has
its argv/status/stdout/stderr; skipped configure/build/runtime has a reason.
The script does not print the entire environment or PATH and redacts known secret
values/URL credentials. Review diagnostics before sharing; local paths remain.
No CUDA-enabled configuration is attempted without a working candidate nvcc and
CMake>=3.18. It uses a temporary project build and deletes that scratch directory.

## 5. Optional persistent CUDA build and smoke

**GPU/toolkit-dependent commands below have not run locally.** Proceed only after
an operational preflight. Use a separate build; MAB_ENABLE_CUDA is OFF by default.
CUDA ON requires CMake>=3.18, NVIDIA toolkit>=11.0/C++17, and a compatible host
compiler. [CMake CheckLanguage](https://cmake.org/cmake/help/v3.28/module/CheckLanguage.html)
and [FindCUDAToolkit](https://cmake.org/cmake/help/v3.28/module/FindCUDAToolkit.html)
validate compiler/toolkit independently from device execution.

```sh
cmake -S . -B build/cloud_cuda -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_OPENMP=OFF -DMAB_ENABLE_SANITIZERS=OFF
cmake --build build/cloud_cuda --target cuda_runtime_probe --parallel 2
build/cloud_cuda/cuda_runtime_probe
ctest --test-dir build/cloud_cuda --output-on-failure -V -R '^cuda_runtime_smoke$'
```

The probe enumerates devices, records runtime/driver API versions, and tests only
device0 using a tiny kernel plus synchronized copy-back/reference check. Version
integers follow the [CUDA runtime API](https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART____VERSION.html).
Probe exit77/CTest skip means unavailable enumeration or no devices; it is never a
GPU pass. Post-enumeration allocation/launch/synchronization/copy/verification failure
exits1 and fails CTest. Exit0 checks one kernel, not sorting or CUDA acceleration.
If architecture selection is needed, set CMAKE_CUDA_ARCHITECTURES using the actual
GPU compute capability and toolkit-supported targets; no architecture is guessed.
Use separate CPU ASan/UBSan and CUDA builds; combining options is explicitly rejected.

Capture CPU build metadata separately (validated existing CLI):

```sh
python3 scripts/capture_environment.py --build-dir build/cloud_cpu --output results/raw/NEW_CLOUD_CPU_ENVIRONMENT.json
```

This older CPU tool deliberately says GPU not probed; use cuda_preflight/report.json
for GPU capabilities. Retain both records and identify which build produced each.
Do not mix future GPU timing rows into the current CPU schemas/plots.

## 6. Persist before runtime shutdown

Colab/cloud workspace files are ephemeral. Save the source archive/hash, preflight
report/summary/marker, exact build commands and stdout/stderr, CPU environment,
compile_commands.json and relevant build logs outside the VM. No experiment is
complete if its evidence is lost. Use fresh destinations; never overwrite studies.

Colab example (**requires Colab authorization; not locally executed**):

```python
from google.colab import drive
from pathlib import Path
import shutil
# Mount your own persistent storage; review the notebook before authorizing it.
drive.mount('/content/drive')
destination = Path('/content/drive/MyDrive/mab_evidence') / run.name
assert not destination.exists()
destination.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(run, destination)
assert (run / 'report.json').read_bytes() == (destination / 'report.json').read_bytes()
```

Also export build/environment/source evidence to exclusive sibling paths. An
alternative is downloading an evidence archive or an authenticated cloud-storage
upload configured by the user. Never embed credentials in commands/notebooks.

## Troubleshooting and next GPU milestone

- No device detected: confirm allocation/runtime type, account quota and provider
  visibility. A CPU fallback remains valid; do not report GPU results.
- GPU PCI evidence but driver unverified: missing tools/module/library is evidence
  of unavailable readiness, not proof physical hardware is broken. Use a supported
  provider GPU image or administrator-managed environment; no driver changes here.
- Driver works, nvcc absent: runtime-only images can expose a GPU without a compiler.
  Select a development image; do not infer toolkit from nvidia-smi's CUDA banner.
- nvcc works, configure/build fails: inspect recorded host-compiler/toolkit/architecture
  diagnostics; consult the installed toolkit's compatibility documentation. A compiler
  version string is not a successful target build.
- Build works, enumeration/kernel fails: preserve diagnostics and visibility variables;
  driver/toolkit/device compatibility, allocation or image architecture can matter.
  Never suppress a failed kernel as a successful smoke test.
- Colab resource interruption: export partial evidence, use a new run identifier after
  reconnecting, and never pool partial attempts into a completed study.

Next GPU work: validate this guide/probe on an actually allocated device, then
separately pin/license CUB/CCCL, implement signed-int32 sorting/full CPU differential
checks, and freeze synchronized H2D/algorithm/D2H/end-to-end semantics with allocation
scope before experiments. No100M, GPU sorting timing or performance claims here.
