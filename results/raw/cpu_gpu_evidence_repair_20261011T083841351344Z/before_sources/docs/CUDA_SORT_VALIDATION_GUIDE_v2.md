# CUB correctness validation on Colab v2

The retained cloud runtime archive proves Tesla T4 readiness on its recorded date.
It does not prove this new sorter compiles or works, nor that the current session
still has a GPU. Local validation cannot run CUDA. This guide has not yet been run
on the new sorter in Colab. No benchmark timing is collected.

Use the new `cub_sort_source_v2.tar.gz` and its independent SHA256 from the current
local final audit, not the old Phase 7 archive (which lacks the sorter). Upload it
to a connected GPU runtime and run from the upload directory. The output directory
and extracted source must not already exist:

```sh
# Set this to the new archive hash retained in the local audit:
export MAB_CUB_ARCHIVE_SHA256='REPLACE_WITH_NEW_CUB_SOURCE_ARCHIVE_HASH'
python3 - <<'PY'
import hashlib, os
from pathlib import Path
assert hashlib.sha256(Path('cub_sort_source_v2.tar.gz').read_bytes()).hexdigest()==os.environ['MAB_CUB_ARCHIVE_SHA256']
PY
test ! -e modern-algorithm-benchmark || exit 1
tar -xzf cub_sort_source_v2.tar.gz
cd modern-algorithm-benchmark
python3 - <<'PY'
import hashlib,json
from pathlib import Path
manifest=json.loads(Path('SOURCE_SHA256.json').read_text())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in manifest.items())
print('Verified',len(manifest),'source files')
PY
mkdir -p results/raw results/processed results/figures
python3 - <<'PY'
import datetime, subprocess, sys
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
output='results/raw/cub_correctness_'+stamp
r=subprocess.run([sys.executable,'scripts/validate_cuda_sort.py','--output',output])
print('exit:',r.returncode,'evidence:',output)
assert r.returncode==0,'Not validated: preserve FAILED/INTERRUPTED and command diagnostics'
PY
```

An existing source checkout must not be overwritten: use a new empty upload/work
location. Use the existing Python environment; this narrow target does not need
Matplotlib. If a host compiler/CMake/toolkit is missing, use a supported development
image; do not replace hosted drivers. Existing readiness guide describes CPU-only
fallback and persistence, unchanged.

The runner records a fresh operational preflight, derives architecture from actual
device0, and executes the equivalent commands below with unique absolute paths:

```sh
cmake -S . -B NEW_BUILD -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_CUDA_SORT=ON -DMAB_ENABLE_OPENMP=OFF -DMAB_ENABLE_SANITIZERS=OFF -DBUILD_TESTING=ON -DCMAKE_CUDA_ARCHITECTURES=75
cmake --build NEW_BUILD --target test_cuda_sorting --parallel 2
NEW_BUILD/test_cuda_sorting
ctest --test-dir NEW_BUILD --output-on-failure -V -R '^cuda_sorting$'
```

`75` above applies only to an actually observed T4/7.5. The automated runner uses
the current preflight, never a guessed architecture. Direct tests require 475
complete input cases and 1900 full-vector output checks. These are expected counts,
not observed GPU passes yet. Empty/singleton cases require a usable device but skip
sorting. Missing device returns77 (CTest skip), which the runner rejects as an
incomplete correctness validation. No CPU fallback for requested GPU sorting.

Initial dependency pin: CUB 3.0.0, two revision-verified header hashes from
third_party/cub/UPSTREAM.json. The old cloud archive did not capture CUB identity.
If the installed toolkit differs, configure fails with actual hashes. Preserve
those diagnostics and report the mismatch for deliberate version review; do not
edit hashes or pretend the test passed. No dependency downloads during configure.

A successful run contains source_sha256.json, preflight/report.json, exact command
records, build/CMakeCache.txt, build/compile_commands.json, dependency_sha256.json,
sorting.json, ctest.json and COMPLETE.json. Failed/interrupted runs retain their
own marker; no overwrite/resume. COMPLETE means new correctness validation, not
GPU timing or a full study. Keep the build/cache and all diagnostics with the run.

Before the ephemeral runtime ends, archive the entire run to a new destination
outside the source tree, hash it, and persist/download it using your own Drive or
cloud storage. Follow section6 of CUDA_EXECUTION_GUIDE_v1.md; authorization/mounting
is a separate user operation. Return the archive/hash for local evidence review.
The local agent cannot infer a live Colab connection from historical artifacts.

Only after observing sorter build and differential-test success should a separate
GPU timing protocol/engine be implemented. No100M and no performance claims here.

Revision2 handoff includes the dangling-symlink output safety fix and its regression. Use the v2 source bundle; the first candidate archive/guide remain retained history. GPU sorting build/tests remain pending.
