# Exact retained validation commands and exit statuses

Local CLI exit0 is not proof of remote success: inspect the inner records.
Initial status printed not found despite0; original validation CLI0/runner1.
The stalled client child exit-15 maps to outer recorder shell241.
Read-only source inspections are described in FINAL_AUDIT.md.

## local: attach_existing

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
/home/ahmedelsheikh/.local/share/uv/tools/google-colab-cli/bin/python results/raw/cub_correctness_colab_20261009T223853955936Z/attach_existing_session.py
```

exit: 0; record: commands/attach_existing.json

## local: check_private_state

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
/home/ahmedelsheikh/.local/share/uv/tools/google-colab-cli/bin/python results/raw/cub_correctness_colab_20261009T223853955936Z/check_private_state.py
```

exit: 0; record: commands/check_private_state.json

## local: cli_version

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab version
```

exit: 0; record: commands/cli_version.json

## local: cpu_environment

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
python3 scripts/capture_environment.py --build-dir build/cub_correctness_colab_20261009T223853955936Z/cpu-release --output results/raw/cub_correctness_colab_20261009T223853955936Z/cpu_environment.json
```

exit: 0; record: commands/cpu_environment.json

## local: cpu_final_release_build

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
cmake --build build/cub_correctness_colab_20261009T223853955936Z/cpu-release --parallel 2
```

exit: 0; record: commands/cpu_final_release_build.json

## local: cpu_final_release_configure

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
cmake -S . -B build/cub_correctness_colab_20261009T223853955936Z/cpu-release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CUDA_SORT=OFF
```

exit: 0; record: commands/cpu_final_release_configure.json

## local: cpu_final_release_ctest

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
ctest --test-dir build/cub_correctness_colab_20261009T223853955936Z/cpu-release --output-on-failure -V
```

exit: 0; record: commands/cpu_final_release_ctest.json

## local: cpu_release_build

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
cmake --build build/cub_correctness_colab_20261009T223853955936Z/cpu-release --parallel 2
```

exit: 0; record: commands/cpu_release_build.json

## local: cpu_release_configure

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
cmake -S . -B build/cub_correctness_colab_20261009T223853955936Z/cpu-release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CUDA_SORT=OFF
```

exit: 0; record: commands/cpu_release_configure.json

## local: cpu_release_ctest

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
ctest --test-dir build/cub_correctness_colab_20261009T223853955936Z/cpu-release --output-on-failure -V
```

exit: 0; record: commands/cpu_release_ctest.json

## local: cpu_sanitize_build

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
cmake --build build/cub_correctness_colab_20261009T223853955936Z/cpu-sanitize --parallel 2
```

exit: 0; record: commands/cpu_sanitize_build.json

## local: cpu_sanitize_configure

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
cmake -S . -B build/cub_correctness_colab_20261009T223853955936Z/cpu-sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CUDA_SORT=OFF
```

exit: 0; record: commands/cpu_sanitize_configure.json

## local: cpu_sanitize_ctest

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/cub_correctness_colab_20261009T223853955936Z/cpu-sanitize --output-on-failure -V
```

exit: 0; record: commands/cpu_sanitize_ctest.json

## local: diagnose_connection

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
/home/ahmedelsheikh/.local/share/uv/tools/google-colab-cli/bin/python results/raw/cub_correctness_colab_20261009T223853955936Z/diagnose_connection.py
```

exit: 0; record: commands/diagnose_connection.json

## local: download_colab_evidence

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
timeout --signal=TERM 180 colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/reconnect.json download /content/mab_cub_20261009T223853955936Z_retry1/colab_evidence.tar.gz results/raw/cub_correctness_colab_20261009T223853955936Z/colab_evidence.tar.gz --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal
```

exit: 0; record: commands/download_colab_evidence.json

## local: final_review

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
python3 results/raw/cub_correctness_colab_20261009T223853955936Z/final_review.py
```

exit: 0; record: commands/final_review.json

## local: git_status

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
git status --short
```

exit: 128; record: commands/git_status.json

## local: handoff_after_pin

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
python3 tests/test_cuda_sort_handoff.py
```

exit: 0; record: commands/handoff_after_pin.json

## local: kernel_status

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
/home/ahmedelsheikh/.local/share/uv/tools/google-colab-cli/bin/python results/raw/cub_correctness_colab_20261009T223853955936Z/kernel_status.py
```

exit: 0; record: commands/kernel_status.json

## local: remote_dependency_inspect

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/sessions.json exec --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal --file results/raw/cub_correctness_colab_20261009T223853955936Z/remote_dependency_inspect.py --timeout 90
```

exit: 0; record: commands/remote_dependency_inspect.json

## local: remote_extract

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/sessions.json exec --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal --file results/raw/cub_correctness_colab_20261009T223853955936Z/remote_extract.py --timeout 120
```

exit: 0; record: commands/remote_extract.json

## local: remote_inspect

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/sessions.json exec --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal --file results/raw/cub_correctness_colab_20261009T223853955936Z/remote_inspect.py --timeout 90
```

exit: 0; record: commands/remote_inspect.json

## local: remote_list_root

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/sessions.json ls content --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal
```

exit: 0; record: commands/remote_list_root.json

## local: remote_package

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
timeout --signal=TERM 240 colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/reconnect.json exec --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal --file results/raw/cub_correctness_colab_20261009T223853955936Z/remote_package.py --timeout 180
```

exit: 0; record: commands/remote_package.json

## local: remote_progress_reconnected

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
timeout --signal=TERM 120 colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/reconnect.json exec --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal --file results/raw/cub_correctness_colab_20261009T223853955936Z/remote_progress.py --timeout 30
```

exit: 0; record: commands/remote_progress_reconnected.json

## local: remote_retry_extract

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/sessions.json exec --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal --file results/raw/cub_correctness_colab_20261009T223853955936Z/remote_retry_extract.py --timeout 120
```

exit: 0; record: commands/remote_retry_extract.json

## local: remote_retry_inspect

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/sessions.json exec --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal --file results/raw/cub_correctness_colab_20261009T223853955936Z/remote_retry_inspect.py --timeout 90
```

exit: 0; record: commands/remote_retry_inspect.json

## local: remote_retry_parent_listing

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/sessions.json ls content/mab_cub_20261009T223853955936Z_retry1 --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal
```

exit: 0; record: commands/remote_retry_parent_listing.json

## local: remote_retry_progress

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/sessions.json ls /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark/results/raw/NEW_CUB_CORRECTNESS --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal
```

exit: 1; record: commands/remote_retry_progress.json

## local: remote_retry_validation

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/sessions.json exec --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal --file results/raw/cub_correctness_colab_20261009T223853955936Z/remote_retry_validate.py --timeout 2500
```

exit: -15; record: commands/remote_retry_validation.json

## local: remote_retry_validation_reconnected

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
timeout --signal=TERM 2600 colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/reconnect.json exec --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal --file results/raw/cub_correctness_colab_20261009T223853955936Z/remote_retry_validate.py --timeout 2500
```

exit: 0; record: commands/remote_retry_validation_reconnected.json

## local: remote_validation

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/sessions.json exec --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal --file results/raw/cub_correctness_colab_20261009T223853955936Z/remote_validate.py --timeout 2500
```

exit: 0; record: commands/remote_validation.json

## local: review_upstream_v3_0_1

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
python3 results/raw/cub_correctness_colab_20261009T223853955936Z/review_upstream.py
```

exit: 0; record: commands/review_upstream_v3_0_1.json

## local: sessions

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab sessions
```

exit: 0; record: commands/sessions.json

## local: status

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab status --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal
```

exit: 0; record: commands/status.json

## local: status_attached

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/sessions.json status --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal
```

exit: 0; record: commands/status_attached.json

## local: upload_retry

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/sessions.json upload results/raw/cub_correctness_colab_20261009T223853955936Z/cub_sort_source_v3.tar.gz /content/cub_sort_source_v3_20261009T223853955936Z.tar.gz --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal
```

exit: 0; record: commands/upload_retry.json

## local: upload_v2

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
colab --config build/cub_correctness_colab_20261009T223853955936Z/private_cli/sessions.json upload results/raw/cub_sort_final_review_20261009T222209607981Z/cub_sort_source_v2.tar.gz /content/cub_sort_source_v2.tar.gz --session gpu-t4-s-kkb-ass1b1-aq78qx2sgfal
```

exit: 0; record: commands/upload_v2.json

## local: verify_download

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
python3 results/raw/cub_correctness_colab_20261009T223853955936Z/verify_download.py
```

exit: 0; record: commands/verify_download.json

## local: verify_frozen_integrity

cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

```sh
python3 results/raw/cub_correctness_colab_20261009T223853955936Z/verify_integrity.py
```

exit: 0; record: commands/verify_frozen_integrity.json

## attempt1: configure

cwd: /content/mab_cub_20261009T223853955936Z/modern-algorithm-benchmark

```sh
cmake -S /content/mab_cub_20261009T223853955936Z/modern-algorithm-benchmark -B /content/mab_cub_20261009T223853955936Z/modern-algorithm-benchmark/results/raw/NEW_CUB_CORRECTNESS/build -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_CUDA_SORT=ON -DMAB_ENABLE_OPENMP=OFF -DMAB_ENABLE_SANITIZERS=OFF -DBUILD_TESTING=ON -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc -DCMAKE_CUDA_ARCHITECTURES=75
```

exit: 1; record: downloaded/attempt1/NEW_CUB_CORRECTNESS/configure.json

## attempt1: preflight

cwd: /content/mab_cub_20261009T223853955936Z/modern-algorithm-benchmark

```sh
/usr/bin/python3 /content/mab_cub_20261009T223853955936Z/modern-algorithm-benchmark/scripts/cuda_preflight.py --output /content/mab_cub_20261009T223853955936Z/modern-algorithm-benchmark/results/raw/NEW_CUB_CORRECTNESS/preflight --timeout-seconds 180
```

exit: 0; record: downloaded/attempt1/NEW_CUB_CORRECTNESS/preflight.json

## attempt1: runner

cwd: /content/mab_cub_20261009T223853955936Z/modern-algorithm-benchmark

```sh
python3 scripts/validate_cuda_sort.py --output results/raw/NEW_CUB_CORRECTNESS
```

exit: 1; record: downloaded/attempt1/runner.json

## attempt1/preflight: build

cwd: recorded in preflight/context; not inferred

```sh
/usr/local/bin/cmake --build /tmp/mab_cuda_preflight_khqr8ook/build --target cuda_runtime_probe --config Release --parallel 2
```

exit: 0; record: downloaded/attempt1/NEW_CUB_CORRECTNESS/preflight/report.json

## attempt1/preflight: cmake

cwd: recorded in preflight/context; not inferred

```sh
/usr/local/bin/cmake --version
```

exit: 0; record: downloaded/attempt1/NEW_CUB_CORRECTNESS/preflight/report.json

## attempt1/preflight: cmake_cuda_property

cwd: recorded in preflight/context; not inferred

```sh
/usr/local/bin/cmake --help-property CUDA_STANDARD
```

exit: 0; record: downloaded/attempt1/NEW_CUB_CORRECTNESS/preflight/report.json

## attempt1/preflight: configure

cwd: recorded in preflight/context; not inferred

```sh
/usr/local/bin/cmake -S /content/mab_cub_20261009T223853955936Z/modern-algorithm-benchmark -B /tmp/mab_cuda_preflight_khqr8ook/build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_OPENMP=OFF -DMAB_ENABLE_SANITIZERS=OFF -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc
```

exit: 0; record: downloaded/attempt1/NEW_CUB_CORRECTNESS/preflight/report.json

## attempt1/preflight: lspci

cwd: recorded in preflight/context; not inferred

```sh
lspci -nn -d 10de:
```

exit: None; record: downloaded/attempt1/NEW_CUB_CORRECTNESS/preflight/report.json

## attempt1/preflight: nvcc

cwd: recorded in preflight/context; not inferred

```sh
/usr/local/cuda/bin/nvcc --version
```

exit: 0; record: downloaded/attempt1/NEW_CUB_CORRECTNESS/preflight/report.json

## attempt1/preflight: nvidia_smi

cwd: recorded in preflight/context; not inferred

```sh
/opt/bin/nvidia-smi --query-gpu=index,name,driver_version --format=csv,noheader,nounits
```

exit: 0; record: downloaded/attempt1/NEW_CUB_CORRECTNESS/preflight/report.json

## attempt1/preflight: runtime

cwd: recorded in preflight/context; not inferred

```sh
/tmp/mab_cuda_preflight_khqr8ook/build/cuda_runtime_probe
```

exit: 0; record: downloaded/attempt1/NEW_CUB_CORRECTNESS/preflight/report.json

## retry1: build

cwd: /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark

```sh
cmake --build /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark/results/raw/NEW_CUB_CORRECTNESS/build --target test_cuda_sorting --parallel 2
```

exit: 0; record: downloaded/retry1/NEW_CUB_CORRECTNESS/build.json

## retry1: configure

cwd: /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark

```sh
cmake -S /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark -B /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark/results/raw/NEW_CUB_CORRECTNESS/build -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_CUDA_SORT=ON -DMAB_ENABLE_OPENMP=OFF -DMAB_ENABLE_SANITIZERS=OFF -DBUILD_TESTING=ON -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc -DCMAKE_CUDA_ARCHITECTURES=75
```

exit: 0; record: downloaded/retry1/NEW_CUB_CORRECTNESS/configure.json

## retry1: ctest

cwd: /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark

```sh
ctest --test-dir /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark/results/raw/NEW_CUB_CORRECTNESS/build --output-on-failure -V -R '^cuda_sorting$'
```

exit: 0; record: downloaded/retry1/NEW_CUB_CORRECTNESS/ctest.json

## retry1: preflight

cwd: /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark

```sh
/usr/bin/python3 /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark/scripts/cuda_preflight.py --output /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark/results/raw/NEW_CUB_CORRECTNESS/preflight --timeout-seconds 180
```

exit: 0; record: downloaded/retry1/NEW_CUB_CORRECTNESS/preflight.json

## retry1: sorting

cwd: /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark

```sh
/content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark/results/raw/NEW_CUB_CORRECTNESS/build/test_cuda_sorting
```

exit: 0; record: downloaded/retry1/NEW_CUB_CORRECTNESS/sorting.json

## retry1: runner

cwd: /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark

```sh
python3 scripts/validate_cuda_sort.py --output results/raw/NEW_CUB_CORRECTNESS
```

exit: 0; record: downloaded/retry1/runner.json

## retry1/preflight: build

cwd: recorded in preflight/context; not inferred

```sh
/usr/local/bin/cmake --build /tmp/mab_cuda_preflight_a69xi_u8/build --target cuda_runtime_probe --config Release --parallel 2
```

exit: 0; record: downloaded/retry1/NEW_CUB_CORRECTNESS/preflight/report.json

## retry1/preflight: cmake

cwd: recorded in preflight/context; not inferred

```sh
/usr/local/bin/cmake --version
```

exit: 0; record: downloaded/retry1/NEW_CUB_CORRECTNESS/preflight/report.json

## retry1/preflight: cmake_cuda_property

cwd: recorded in preflight/context; not inferred

```sh
/usr/local/bin/cmake --help-property CUDA_STANDARD
```

exit: 0; record: downloaded/retry1/NEW_CUB_CORRECTNESS/preflight/report.json

## retry1/preflight: configure

cwd: recorded in preflight/context; not inferred

```sh
/usr/local/bin/cmake -S /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark -B /tmp/mab_cuda_preflight_a69xi_u8/build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_OPENMP=OFF -DMAB_ENABLE_SANITIZERS=OFF -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc
```

exit: 0; record: downloaded/retry1/NEW_CUB_CORRECTNESS/preflight/report.json

## retry1/preflight: lspci

cwd: recorded in preflight/context; not inferred

```sh
lspci -nn -d 10de:
```

exit: None; record: downloaded/retry1/NEW_CUB_CORRECTNESS/preflight/report.json

## retry1/preflight: nvcc

cwd: recorded in preflight/context; not inferred

```sh
/usr/local/cuda/bin/nvcc --version
```

exit: 0; record: downloaded/retry1/NEW_CUB_CORRECTNESS/preflight/report.json

## retry1/preflight: nvidia_smi

cwd: recorded in preflight/context; not inferred

```sh
/opt/bin/nvidia-smi --query-gpu=index,name,driver_version --format=csv,noheader,nounits
```

exit: 0; record: downloaded/retry1/NEW_CUB_CORRECTNESS/preflight/report.json

## retry1/preflight: runtime

cwd: recorded in preflight/context; not inferred

```sh
/tmp/mab_cuda_preflight_a69xi_u8/build/cuda_runtime_probe
```

exit: 0; record: downloaded/retry1/NEW_CUB_CORRECTNESS/preflight/report.json
