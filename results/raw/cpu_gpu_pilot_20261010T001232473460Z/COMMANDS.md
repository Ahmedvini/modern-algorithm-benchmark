# Commands and actual exit statuses

Full stdout/stderr, timestamps and wall durations are retained in the linked JSON files. Local CLI exit status is not a substitute for the remote Python result; v1 returned CLI0 with actual validation1, v2 ended SIGTERM/-15 with remote final outcome unverified, and final v3 has independently verified inner/outer0. Expected synthetic test failures are assertions, not failed suites.

## commands/check_remote_destinations.json

```sh
timeout --signal=TERM 120 colab exec --session cpu-gpu-pilot --file results/raw/cpu_gpu_pilot_20261010T001232473460Z/check_remote_destinations.py --timeout 90
```

Exit: 1; status: recorded; wall seconds: 1.7992970180002885. [commands/check_remote_destinations.json](commands/check_remote_destinations.json).

## commands/collect_remote_v1.json

```sh
timeout --signal=TERM 90 colab exec --session cpu-gpu-pilot-reconnect --file results/raw/cpu_gpu_pilot_20261010T001232473460Z/collect_remote_v1.py --timeout 60
```

Exit: 0; status: recorded; wall seconds: 2.9831454889999804. [commands/collect_remote_v1.json](commands/collect_remote_v1.json).

## commands/cpu_release_build.json

```sh
cmake --build build/cpu_gpu_pilot_20261010T001232473460Z/release --parallel 2
```

Exit: 0; status: recorded; wall seconds: 17.44224035699972. [commands/cpu_release_build.json](commands/cpu_release_build.json).

## commands/cpu_release_configure.json

```sh
cmake -S . -B build/cpu_gpu_pilot_20261010T001232473460Z/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CPU_GPU_COMPARISON=OFF -DMAB_ENABLE_OPENMP=ON
```

Exit: 0; status: recorded; wall seconds: 0.6105884190001234. [commands/cpu_release_configure.json](commands/cpu_release_configure.json).

## commands/cpu_release_ctest.json

```sh
ctest --test-dir build/cpu_gpu_pilot_20261010T001232473460Z/release --output-on-failure -V
```

Exit: 0; status: recorded; wall seconds: 33.171438307000244. [commands/cpu_release_ctest.json](commands/cpu_release_ctest.json).

## commands/cpu_sanitize_build.json

```sh
cmake --build build/cpu_gpu_pilot_20261010T001232473460Z/sanitize --parallel 2
```

Exit: 0; status: recorded; wall seconds: 21.408500737000395. [commands/cpu_sanitize_build.json](commands/cpu_sanitize_build.json).

## commands/cpu_sanitize_configure.json

```sh
cmake -S . -B build/cpu_gpu_pilot_20261010T001232473460Z/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CPU_GPU_COMPARISON=OFF -DMAB_ENABLE_OPENMP=ON
```

Exit: 0; status: recorded; wall seconds: 0.5552993780001998. [commands/cpu_sanitize_configure.json](commands/cpu_sanitize_configure.json).

## commands/cpu_sanitize_ctest.json

```sh
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/cpu_gpu_pilot_20261010T001232473460Z/sanitize --output-on-failure -V
```

Exit: 0; status: recorded; wall seconds: 134.90418023099937. [commands/cpu_sanitize_ctest.json](commands/cpu_sanitize_ctest.json).

## commands/download_remote_v1.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_evidence_v1.tar.gz results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_evidence_v1.tar.gz --session cpu-gpu-pilot-reconnect
```

Exit: 0; status: recorded; wall seconds: 1.4037578130000838. [commands/download_remote_v1.json](commands/download_remote_v1.json).

## commands/download_remote_v3.json

```sh
timeout --signal=TERM 180 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_evidence_v3.tar.gz results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_evidence_v3.tar.gz --session cpu-gpu-pilot-reconnect-v3
```

Exit: 0; status: recorded; wall seconds: 3.5098403680003685. [commands/download_remote_v3.json](commands/download_remote_v3.json).

## commands/generate_report.json

```sh
python3 results/raw/cpu_gpu_pilot_20261010T001232473460Z/write_report.py
```

Exit: 1; status: recorded; wall seconds: 0.09131124200030172. [commands/generate_report.json](commands/generate_report.json).

## commands/generate_report_v2.json

```sh
python3 results/raw/cpu_gpu_pilot_20261010T001232473460Z/write_report_v2.py
```

Exit: 1; status: recorded; wall seconds: 0.08448712700010219. [commands/generate_report_v2.json](commands/generate_report_v2.json).

## commands/generate_report_v3.json

```sh
python3 results/raw/cpu_gpu_pilot_20261010T001232473460Z/write_report_v3.py
```

Exit: 0; status: recorded; wall seconds: 0.026764259999254136. [commands/generate_report_v3.json](commands/generate_report_v3.json).

## commands/generate_reviewed_report.json

```sh
python3 results/raw/cpu_gpu_pilot_20261010T001232473460Z/write_report_v4.py results/processed/cpu_gpu_pilot_20261010T001232473460Z/reviewed
```

Exit: 0; status: recorded; wall seconds: 0.024675715001649223. [commands/generate_reviewed_report.json](commands/generate_reviewed_report.json).

## commands/git_status_final.json

```sh
git status --short
```

Exit: 128; status: recorded; wall seconds: 0.0011645289996522479. [commands/git_status_final.json](commands/git_status_final.json).

## commands/independent_verify.json

```sh
python3 results/raw/cpu_gpu_pilot_20261010T001232473460Z/independent_verify.py
```

Exit: 0; status: recorded; wall seconds: 0.05809474400120962. [commands/independent_verify.json](commands/independent_verify.json).

## commands/inspect_remote.json

```sh
timeout --signal=TERM 150 colab exec --session cpu-gpu-pilot --file results/raw/cpu_gpu_pilot_20261010T001232473460Z/inspect_remote.py --timeout 120
```

Exit: 0; status: recorded; wall seconds: 3.6120867259996885. [commands/inspect_remote.json](commands/inspect_remote.json).

## commands/local_analyze_v3.json

```sh
python3 scripts/analyze_cpu_gpu.py results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3 --output results/processed/cpu_gpu_pilot_20261010T001232473460Z/summary.json
```

Exit: 0; status: recorded; wall seconds: 0.08033892799903697. [commands/local_analyze_v3.json](commands/local_analyze_v3.json).

## commands/local_environment.json

```sh
python3 scripts/capture_environment.py --build-dir build/cpu_gpu_pilot_20261010T001232473460Z/release --output results/raw/cpu_gpu_pilot_20261010T001232473460Z/local_environment.json
```

Exit: 0; status: recorded; wall seconds: 0.046224784000514774. [commands/local_environment.json](commands/local_environment.json).

## commands/local_regenerate_v3.json

```sh
python3 scripts/analyze_cpu_gpu.py results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3 --output results/processed/cpu_gpu_pilot_20261010T001232473460Z/summary_regenerated.json
```

Exit: 0; status: recorded; wall seconds: 0.07584244799909357. [commands/local_regenerate_v3.json](commands/local_regenerate_v3.json).

## commands/local_release_final_ctest.json

```sh
ctest --test-dir build/cpu_gpu_pilot_20261010T001232473460Z/release --output-on-failure -V
```

Exit: 0; status: recorded; wall seconds: 33.452122522000536. [commands/local_release_final_ctest.json](commands/local_release_final_ctest.json).

## commands/local_sanitize_final_ctest.json

```sh
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/cpu_gpu_pilot_20261010T001232473460Z/sanitize --output-on-failure -V
```

Exit: 0; status: recorded; wall seconds: 136.66907917800017. [commands/local_sanitize_final_ctest.json](commands/local_sanitize_final_ctest.json).

## commands/narrow_build.json

```sh
cmake --build build/cpu_gpu_pilot_20261010T001232473460Z/release --target test_comparison comparison_input --parallel 2
```

Exit: 0; status: recorded; wall seconds: 5.047965804999876. [commands/narrow_build.json](commands/narrow_build.json).

## commands/narrow_ctest.json

```sh
ctest --test-dir build/cpu_gpu_pilot_20261010T001232473460Z/release --output-on-failure -V -R '^(comparison_engine|cpu_gpu_comparison_framework)$'
```

Exit: 0; status: recorded; wall seconds: 1.7786616099992898. [commands/narrow_ctest.json](commands/narrow_ctest.json).

## commands/python_clean_checkout_regression.json

```sh
python3 tests/test_cpu_gpu_comparison.py build/cpu_gpu_pilot_20261010T001232473460Z/release/comparison_input
```

Exit: 0; status: recorded; wall seconds: 0.8255044879997513. [commands/python_clean_checkout_regression.json](commands/python_clean_checkout_regression.json).

## commands/python_final_framework.json

```sh
python3 tests/test_cpu_gpu_comparison.py build/cpu_gpu_pilot_20261010T001232473460Z/release/comparison_input
```

Exit: 0; status: recorded; wall seconds: 0.9134848789999523. [commands/python_final_framework.json](commands/python_final_framework.json).

## commands/python_framework.json

```sh
python3 tests/test_cpu_gpu_comparison.py build/cpu_gpu_pilot_20261010T001232473460Z/release/comparison_input
```

Exit: 0; status: recorded; wall seconds: 0.8160875749999832. [commands/python_framework.json](commands/python_framework.json).

## commands/reconnect_destinations.json

```sh
timeout --signal=TERM 120 colab exec --session cpu-gpu-pilot-reconnect --file results/raw/cpu_gpu_pilot_20261010T001232473460Z/check_remote_destinations.py --timeout 90
```

Exit: 0; status: recorded; wall seconds: 2.4847710260000895. [commands/reconnect_destinations.json](commands/reconnect_destinations.json).

## commands/reconnect_destinations_v2.json

```sh
timeout --signal=TERM 90 colab exec --session cpu-gpu-pilot-reconnect --file results/raw/cpu_gpu_pilot_20261010T001232473460Z/check_remote_destinations_v2.py --timeout 60
```

Exit: 0; status: recorded; wall seconds: 2.984197365. [commands/reconnect_destinations_v2.json](commands/reconnect_destinations_v2.json).

## commands/reconnect_destinations_v3.json

```sh
timeout --signal=TERM 90 colab exec --session cpu-gpu-pilot-reconnect-v3 --file results/raw/cpu_gpu_pilot_20261010T001232473460Z/check_remote_destinations_v3.py --timeout 60
```

Exit: 0; status: recorded; wall seconds: 3.4478417809996245. [commands/reconnect_destinations_v3.json](commands/reconnect_destinations_v3.json).

## commands/reconnect_environment.json

```sh
timeout --signal=TERM 120 colab exec --session cpu-gpu-pilot-reconnect --file results/raw/cpu_gpu_pilot_20261010T001232473460Z/inspect_remote.py --timeout 90
```

Exit: 0; status: recorded; wall seconds: 4.452826921999986. [commands/reconnect_environment.json](commands/reconnect_environment.json).

## commands/reconnect_environment_v3.json

```sh
timeout --signal=TERM 90 colab exec --session cpu-gpu-pilot-reconnect-v3 --file results/raw/cpu_gpu_pilot_20261010T001232473460Z/inspect_remote.py --timeout 60
```

Exit: 0; status: recorded; wall seconds: 3.1628039170000193. [commands/reconnect_environment_v3.json](commands/reconnect_environment_v3.json).

## commands/reconnect_status.json

```sh
timeout --signal=TERM 90 colab status --session cpu-gpu-pilot-reconnect
```

Exit: 0; status: recorded; wall seconds: 1.4460278060005294. [commands/reconnect_status.json](commands/reconnect_status.json).

## commands/reconnect_t4.json

```sh
timeout --signal=TERM 180 colab new --session cpu-gpu-pilot-reconnect --gpu T4
```

Exit: 0; status: recorded; wall seconds: 4.381622105999668. [commands/reconnect_t4.json](commands/reconnect_t4.json).

## commands/reconnect_t4_v3.json

```sh
timeout --signal=TERM 180 colab new --session cpu-gpu-pilot-reconnect-v3 --gpu T4
```

Exit: 0; status: recorded; wall seconds: 4.313447458000155. [commands/reconnect_t4_v3.json](commands/reconnect_t4_v3.json).

## commands/reconnect_upload_v1.json

```sh
timeout --signal=TERM 180 colab upload results/raw/cpu_gpu_pilot_20261010T001232473460Z/cpu_gpu_pilot_source_v1.tar.gz /content/cpu_gpu_pilot_20261010T001232473460Z_source_v1.tar.gz --session cpu-gpu-pilot-reconnect
```

Exit: 0; status: recorded; wall seconds: 2.3051057960001344. [commands/reconnect_upload_v1.json](commands/reconnect_upload_v1.json).

## commands/reconnect_upload_v2.json

```sh
timeout --signal=TERM 180 colab upload results/raw/cpu_gpu_pilot_20261010T001232473460Z/cpu_gpu_pilot_source_v2.tar.gz /content/cpu_gpu_pilot_20261010T001232473460Z_source_v2.tar.gz --session cpu-gpu-pilot-reconnect
```

Exit: 0; status: recorded; wall seconds: 2.3946080269997765. [commands/reconnect_upload_v2.json](commands/reconnect_upload_v2.json).

## commands/reconnect_upload_v3.json

```sh
timeout --signal=TERM 180 colab upload results/raw/cpu_gpu_pilot_20261010T001232473460Z/cpu_gpu_pilot_source_v2.tar.gz /content/cpu_gpu_pilot_20261010T001232473460Z_source_v2.tar.gz --session cpu-gpu-pilot-reconnect-v3
```

Exit: 0; status: recorded; wall seconds: 2.2765043519993924. [commands/reconnect_upload_v3.json](commands/reconnect_upload_v3.json).

## commands/remote_cpu_quota_precheck.json

```sh
timeout --signal=TERM 90 colab download /sys/fs/cgroup/cpu.max results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_cpu_max_precheck.txt --session cpu-gpu-pilot-reconnect-v3
```

Exit: 0; status: recorded; wall seconds: 1.414702086998659. [commands/remote_cpu_quota_precheck.json](commands/remote_cpu_quota_precheck.json).

## commands/remote_progress_1.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v1/launch_stdout.log results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_progress_1.log --session cpu-gpu-pilot-reconnect
```

Exit: 0; status: recorded; wall seconds: 1.3209818320001432. [commands/remote_progress_1.json](commands/remote_progress_1.json).

## commands/remote_progress_v2_1.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v2/launch_stdout.log results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_progress_v2_1.log --session cpu-gpu-pilot-reconnect
```

Exit: 0; status: recorded; wall seconds: 1.446630052000728. [commands/remote_progress_v2_1.json](commands/remote_progress_v2_1.json).

## commands/remote_progress_v2_2.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v2/launch_stdout.log results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_progress_v2_2.log --session cpu-gpu-pilot-reconnect
```

Exit: 0; status: recorded; wall seconds: 1.00447431900011. [commands/remote_progress_v2_2.json](commands/remote_progress_v2_2.json).

## commands/remote_progress_v2_3.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v2/launch_stdout.log results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_progress_v2_3.log --session cpu-gpu-pilot-reconnect
```

Exit: 0; status: recorded; wall seconds: 1.4175917620004839. [commands/remote_progress_v2_3.json](commands/remote_progress_v2_3.json).

## commands/remote_progress_v2_4.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v2/launch_stdout.log results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_progress_v2_4.log --session cpu-gpu-pilot-reconnect
```

Exit: 0; status: recorded; wall seconds: 1.4644518360000802. [commands/remote_progress_v2_4.json](commands/remote_progress_v2_4.json).

## commands/remote_progress_v2_after_continue.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v2/launch_stdout.log results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_progress_v2_after_continue.log --session cpu-gpu-pilot-reconnect
```

Exit: 1; status: recorded; wall seconds: 0.43811227200058056. [commands/remote_progress_v2_after_continue.json](commands/remote_progress_v2_after_continue.json).

## commands/remote_progress_v3_1.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v3/launch_stdout.log results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_progress_v3_1.log --session cpu-gpu-pilot-reconnect-v3
```

Exit: 0; status: recorded; wall seconds: 0.9203132299999197. [commands/remote_progress_v3_1.json](commands/remote_progress_v3_1.json).

## commands/remote_progress_v3_2.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v3/launch_stdout.log results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_progress_v3_2.log --session cpu-gpu-pilot-reconnect-v3
```

Exit: 0; status: recorded; wall seconds: 1.3373231730001862. [commands/remote_progress_v3_2.json](commands/remote_progress_v3_2.json).

## commands/remote_progress_v3_3.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v3/launch_stdout.log results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_progress_v3_3.log --session cpu-gpu-pilot-reconnect-v3
```

Exit: 0; status: recorded; wall seconds: 0.8752918080008385. [commands/remote_progress_v3_3.json](commands/remote_progress_v3_3.json).

## commands/remote_progress_v3_4.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v3/launch_stdout.log results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_progress_v3_4.log --session cpu-gpu-pilot-reconnect-v3
```

Exit: 0; status: recorded; wall seconds: 1.4856841019991407. [commands/remote_progress_v3_4.json](commands/remote_progress_v3_4.json).

## commands/remote_progress_v3_5.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v3/launch_stdout.log results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_progress_v3_5.log --session cpu-gpu-pilot-reconnect-v3
```

Exit: 0; status: recorded; wall seconds: 2.7221448450000025. [commands/remote_progress_v3_5.json](commands/remote_progress_v3_5.json).

## commands/remote_progress_v3_6.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v3/launch_stdout.log results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_progress_v3_6.log --session cpu-gpu-pilot-reconnect-v3
```

Exit: 0; status: recorded; wall seconds: 0.8914285480004764. [commands/remote_progress_v3_6.json](commands/remote_progress_v3_6.json).

## commands/remote_progress_v3_7.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v3/launch_stdout.log results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_progress_v3_7.log --session cpu-gpu-pilot-reconnect-v3
```

Exit: 0; status: recorded; wall seconds: 1.0133831989987812. [commands/remote_progress_v3_7.json](commands/remote_progress_v3_7.json).

## commands/remote_progress_v3_8.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v3/launch_stdout.log results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_progress_v3_8.log --session cpu-gpu-pilot-reconnect-v3
```

Exit: 0; status: recorded; wall seconds: 1.3406315310003265. [commands/remote_progress_v3_8.json](commands/remote_progress_v3_8.json).

## commands/remote_sanitize_progress_v3.json

```sh
timeout --signal=TERM 90 colab download /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/cpu-sanitize/Testing/Temporary/LastTest.log.tmp results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_sanitize_progress_v3.log --session cpu-gpu-pilot-reconnect-v3
```

Exit: 0; status: recorded; wall seconds: 1.4109238669989281. [commands/remote_sanitize_progress_v3.json](commands/remote_sanitize_progress_v3.json).

## commands/remote_validate_v1.json

```sh
timeout --signal=TERM 2900 colab exec --session cpu-gpu-pilot-reconnect --file results/raw/cpu_gpu_pilot_20261010T001232473460Z/extract_and_validate_v1.py --timeout 2800
```

Exit: 0; status: recorded; wall seconds: 2.250757266999244. [commands/remote_validate_v1.json](commands/remote_validate_v1.json).

## commands/remote_validate_v2.json

```sh
timeout --signal=TERM 2900 colab exec --session cpu-gpu-pilot-reconnect --file results/raw/cpu_gpu_pilot_20261010T001232473460Z/extract_and_validate_v2.py --timeout 2800
```

Exit: -15; status: recorded; wall seconds: 2112.8499313089997. [commands/remote_validate_v2.json](commands/remote_validate_v2.json).

## commands/remote_validate_v3.json

```sh
timeout --signal=TERM 2900 colab exec --session cpu-gpu-pilot-reconnect-v3 --file results/raw/cpu_gpu_pilot_20261010T001232473460Z/extract_and_validate_v3.py --timeout 2800
```

Exit: 0; status: recorded; wall seconds: 548.2864265899998. [commands/remote_validate_v3.json](commands/remote_validate_v3.json).

## commands/session_status.json

```sh
timeout --signal=TERM 90 colab --config build/cuda_timing_20261009T231303050084Z/private_cli/sessions.json status --session mab-t4-20261009T231303050084Z
```

Exit: 0; status: recorded; wall seconds: 0.8451842900003612. [commands/session_status.json](commands/session_status.json).

## commands/sessions_after_loss.json

```sh
timeout --signal=TERM 90 colab sessions
```

Exit: 0; status: recorded; wall seconds: 1.0820561870004894. [commands/sessions_after_loss.json](commands/sessions_after_loss.json).

## commands/sessions_before_reconnect.json

```sh
timeout --signal=TERM 90 colab sessions
```

Exit: 0; status: recorded; wall seconds: 1.5010445509997226. [commands/sessions_before_reconnect.json](commands/sessions_before_reconnect.json).

## commands/sessions_continue.json

```sh
timeout --signal=TERM 90 colab sessions
```

Exit: 0; status: recorded; wall seconds: 1.133529634000297. [commands/sessions_continue.json](commands/sessions_continue.json).

## commands/sessions_latest.json

```sh
timeout --signal=TERM 90 colab sessions
```

Exit: 0; status: recorded; wall seconds: 0.8268451470003129. [commands/sessions_latest.json](commands/sessions_latest.json).

## commands/sessions_recheck.json

```sh
timeout --signal=TERM 90 colab sessions
```

Exit: 0; status: recorded; wall seconds: 1.4115228029995706. [commands/sessions_recheck.json](commands/sessions_recheck.json).

## commands/upload_source_v1.json

```sh
timeout --signal=TERM 180 colab upload results/raw/cpu_gpu_pilot_20261010T001232473460Z/cpu_gpu_pilot_source_v1.tar.gz /content/cpu_gpu_pilot_20261010T001232473460Z_source_v1.tar.gz --session cpu-gpu-pilot
```

Exit: 1; status: recorded; wall seconds: 0.46265591800056427. [commands/upload_source_v1.json](commands/upload_source_v1.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_0.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/cpu_gpu_comparison --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_165d412fee938b9aadbd61e577c0b0e75795d20746eaac1ecea1a4ab5111899d/measurements --input /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_165d412fee938b9aadbd61e577c0b0e75795d20746eaac1ecea1a4ab5111899d/input.bin --size 1000000 --seed 1729 --distribution signed_edges --swaps 0 --distinct 16 --dataset-id 165d412fee938b9aadbd61e577c0b0e75795d20746eaac1ecea1a4ab5111899d --base-order gpu_cub_prepared,gpu_cub_adapter,cpu_std_sort,cpu_parallel_merge_sort_t2,cpu_merge_sort --global-offset 0 --input-sha256 e0538418dd0cea5beb705a6e9a37c507b075fd490383f8122a151d4fbf2ef33f --input-fnv 9241023644615169733 --matrix-sha256 29f9f2765e466a88fc3a7b6e590b1c38dd1ebe5f4f003a37e02aabc9b7074833 --build-id 55da4400147799a7ec0864f025c6488bc48e83ed6dc80e015fa02d3e3aabe99b --environment-id 0542625c6b4de2446c2b16b4ecdc5cb774f46cac03a221da3394d65b636d954f --run-id pilot_v3
```

Exit: 0; status: completed; wall seconds: 0.8742749330000379. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_0.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_0.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_1.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/cpu_gpu_comparison --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_b8f5b14f2927387857f936d8bd1282d5aa1a26e8a7e8fa9a803b04ed851b7d08/measurements --input /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_b8f5b14f2927387857f936d8bd1282d5aa1a26e8a7e8fa9a803b04ed851b7d08/input.bin --size 1000000 --seed 1729 --distribution uniform --swaps 0 --distinct 16 --dataset-id b8f5b14f2927387857f936d8bd1282d5aa1a26e8a7e8fa9a803b04ed851b7d08 --base-order gpu_cub_prepared,cpu_parallel_merge_sort_t2,cpu_std_sort,cpu_merge_sort,gpu_cub_adapter --global-offset 30 --input-sha256 d0603029325b5f050a95f721aef45f6470780199a2c146bf68f89357606498a1 --input-fnv 12963997089183458962 --matrix-sha256 29f9f2765e466a88fc3a7b6e590b1c38dd1ebe5f4f003a37e02aabc9b7074833 --build-id 55da4400147799a7ec0864f025c6488bc48e83ed6dc80e015fa02d3e3aabe99b --environment-id 0542625c6b4de2446c2b16b4ecdc5cb774f46cac03a221da3394d65b636d954f --run-id pilot_v3
```

Exit: 0; status: completed; wall seconds: 2.081436531999998. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_1.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_1.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_2.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/cpu_gpu_comparison --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_ad820393316a1cfd77454babc2d838a2a5c9ba1eab2227961528a552bb54e407/measurements --input /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_ad820393316a1cfd77454babc2d838a2a5c9ba1eab2227961528a552bb54e407/input.bin --size 1000000 --seed 1729 --distribution duplicate_heavy --swaps 0 --distinct 16 --dataset-id ad820393316a1cfd77454babc2d838a2a5c9ba1eab2227961528a552bb54e407 --base-order cpu_std_sort,cpu_merge_sort,gpu_cub_prepared,cpu_parallel_merge_sort_t2,gpu_cub_adapter --global-offset 60 --input-sha256 e8bae355bcbc3652e8f8ea51996a7a0bcc8c24b989071a26217fafb145ba274f --input-fnv 5009479449751836040 --matrix-sha256 29f9f2765e466a88fc3a7b6e590b1c38dd1ebe5f4f003a37e02aabc9b7074833 --build-id 55da4400147799a7ec0864f025c6488bc48e83ed6dc80e015fa02d3e3aabe99b --environment-id 0542625c6b4de2446c2b16b4ecdc5cb774f46cac03a221da3394d65b636d954f --run-id pilot_v3
```

Exit: 0; status: completed; wall seconds: 1.3152327430000241. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_2.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_2.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_3.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/cpu_gpu_comparison --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_e41da1be1f203ac1b4c73b1ff47ddf1966dbf79e5f18af77bfa149e6ecdc3f1e/measurements --input /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_e41da1be1f203ac1b4c73b1ff47ddf1966dbf79e5f18af77bfa149e6ecdc3f1e/input.bin --size 1025 --seed 1729 --distribution duplicate_heavy --swaps 0 --distinct 16 --dataset-id e41da1be1f203ac1b4c73b1ff47ddf1966dbf79e5f18af77bfa149e6ecdc3f1e --base-order gpu_cub_adapter,gpu_cub_prepared,cpu_merge_sort,cpu_std_sort,cpu_parallel_merge_sort_t2 --global-offset 90 --input-sha256 d891ca277ccf8a0ef5ccb118a945be27702526430f0f60faf586b46e052deed1 --input-fnv 6761271111269900403 --matrix-sha256 29f9f2765e466a88fc3a7b6e590b1c38dd1ebe5f4f003a37e02aabc9b7074833 --build-id 55da4400147799a7ec0864f025c6488bc48e83ed6dc80e015fa02d3e3aabe99b --environment-id 0542625c6b4de2446c2b16b4ecdc5cb774f46cac03a221da3394d65b636d954f --run-id pilot_v3
```

Exit: 0; status: completed; wall seconds: 0.37427838700000393. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_3.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_3.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_4.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/cpu_gpu_comparison --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_57fda37acfcd314cd59b4b3ad79220abed2f976d3bb2b24f37ac2ec16d8e1e5b/measurements --input /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_57fda37acfcd314cd59b4b3ad79220abed2f976d3bb2b24f37ac2ec16d8e1e5b/input.bin --size 1025 --seed 1729 --distribution signed_edges --swaps 0 --distinct 16 --dataset-id 57fda37acfcd314cd59b4b3ad79220abed2f976d3bb2b24f37ac2ec16d8e1e5b --base-order gpu_cub_prepared,cpu_merge_sort,gpu_cub_adapter,cpu_parallel_merge_sort_t2,cpu_std_sort --global-offset 120 --input-sha256 0c4c94af1a5af0c44bd2ff788ebc819b0203da70d8542162b1d82de6c15d51ed --input-fnv 4643278884434036853 --matrix-sha256 29f9f2765e466a88fc3a7b6e590b1c38dd1ebe5f4f003a37e02aabc9b7074833 --build-id 55da4400147799a7ec0864f025c6488bc48e83ed6dc80e015fa02d3e3aabe99b --environment-id 0542625c6b4de2446c2b16b4ecdc5cb774f46cac03a221da3394d65b636d954f --run-id pilot_v3
```

Exit: 0; status: completed; wall seconds: 0.29545849500004806. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_4.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_4.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_5.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/cpu_gpu_comparison --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_c68abdcccf294f4f71f56dde5eeb40d61957c8e8dfa4810813fabfe463e840e0/measurements --input /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_c68abdcccf294f4f71f56dde5eeb40d61957c8e8dfa4810813fabfe463e840e0/input.bin --size 1025 --seed 1729 --distribution uniform --swaps 0 --distinct 16 --dataset-id c68abdcccf294f4f71f56dde5eeb40d61957c8e8dfa4810813fabfe463e840e0 --base-order gpu_cub_prepared,cpu_std_sort,cpu_merge_sort,cpu_parallel_merge_sort_t2,gpu_cub_adapter --global-offset 150 --input-sha256 b5377bd58aaa7b2a14d0700de0d250c83d197b69dba19d16a09cc9f73de82549 --input-fnv 16235787445208220162 --matrix-sha256 29f9f2765e466a88fc3a7b6e590b1c38dd1ebe5f4f003a37e02aabc9b7074833 --build-id 55da4400147799a7ec0864f025c6488bc48e83ed6dc80e015fa02d3e3aabe99b --environment-id 0542625c6b4de2446c2b16b4ecdc5cb774f46cac03a221da3394d65b636d954f --run-id pilot_v3
```

Exit: 0; status: completed; wall seconds: 0.26664204399992286. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_5.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/dataset_5.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/describe.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/cpu_gpu_comparison --describe
```

Exit: 0; status: completed; wall seconds: 0.004481288999954813. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/describe.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/describe.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_0.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/comparison_input --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_165d412fee938b9aadbd61e577c0b0e75795d20746eaac1ecea1a4ab5111899d --size 1000000 --seed 1729 --distribution signed_edges --swaps 0 --distinct 16
```

Exit: 0; status: completed; wall seconds: 0.06961072500007504. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_0.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_0.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_1.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/comparison_input --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_b8f5b14f2927387857f936d8bd1282d5aa1a26e8a7e8fa9a803b04ed851b7d08 --size 1000000 --seed 1729 --distribution uniform --swaps 0 --distinct 16
```

Exit: 0; status: completed; wall seconds: 0.045041566999998395. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_1.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_1.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_2.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/comparison_input --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_ad820393316a1cfd77454babc2d838a2a5c9ba1eab2227961528a552bb54e407 --size 1000000 --seed 1729 --distribution duplicate_heavy --swaps 0 --distinct 16
```

Exit: 0; status: completed; wall seconds: 0.06332637699995303. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_2.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_2.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_3.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/comparison_input --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_e41da1be1f203ac1b4c73b1ff47ddf1966dbf79e5f18af77bfa149e6ecdc3f1e --size 1025 --seed 1729 --distribution duplicate_heavy --swaps 0 --distinct 16
```

Exit: 0; status: completed; wall seconds: 0.0020274040000458626. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_3.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_3.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_4.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/comparison_input --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_57fda37acfcd314cd59b4b3ad79220abed2f976d3bb2b24f37ac2ec16d8e1e5b --size 1025 --seed 1729 --distribution signed_edges --swaps 0 --distinct 16
```

Exit: 0; status: completed; wall seconds: 0.0020270630000140955. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_4.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_4.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_5.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/comparison_input --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3/data_c68abdcccf294f4f71f56dde5eeb40d61957c8e8dfa4810813fabfe463e840e0 --size 1025 --seed 1729 --distribution uniform --swaps 0 --distinct 16
```

Exit: 0; status: completed; wall seconds: 0.0020252929999742264. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_5.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/input_5.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/resources_1000000.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/cpu_gpu_comparison --resources 1000000
```

Exit: 0; status: completed; wall seconds: 0.37845295499994336. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/resources_1000000.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/resources_1000000.json).

## remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/resources_1025.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/cpu_gpu_comparison --resources 1025
```

Exit: 0; status: completed; wall seconds: 0.42502490399999715. [remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/resources_1025.json](remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/commands/resources_1025.json).

## remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/analyze.json

```sh
/usr/bin/python3 /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/scripts/analyze_cpu_gpu.py /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3 --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/processed/pilot_v3/summary.json
```

Exit: 0; status: completed; wall seconds: 0.17295378200003597. [remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/analyze.json](remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/analyze.json).

## remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_release_build.json

```sh
cmake --build /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/cpu-release --parallel 2
```

Exit: 0; status: completed; wall seconds: 46.359732485999984. [remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_release_build.json](remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_release_build.json).

## remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_release_configure.json

```sh
cmake -S /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark -DCMAKE_CXX_FLAGS= '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG' -DMAB_ENABLE_OPENMP=ON -DBUILD_TESTING=ON -B /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/cpu-release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CPU_GPU_COMPARISON=OFF
```

Exit: 0; status: completed; wall seconds: 1.5616830029999846. [remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_release_configure.json](remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_release_configure.json).

## remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_release_ctest.json

```sh
ctest --test-dir /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/cpu-release --output-on-failure -V
```

Exit: 0; status: completed; wall seconds: 46.90958754999997. [remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_release_ctest.json](remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_release_ctest.json).

## remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_sanitize_build.json

```sh
cmake --build /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/cpu-sanitize --parallel 2
```

Exit: 0; status: completed; wall seconds: 48.66275223800005. [remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_sanitize_build.json](remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_sanitize_build.json).

## remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_sanitize_configure.json

```sh
cmake -S /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark -DCMAKE_CXX_FLAGS= '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG' -DMAB_ENABLE_OPENMP=ON -DBUILD_TESTING=ON -B /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/cpu-sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CPU_GPU_COMPARISON=OFF -DMAB_ENABLE_SANITIZERS=ON
```

Exit: 0; status: completed; wall seconds: 1.1082459759999779. [remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_sanitize_configure.json](remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_sanitize_configure.json).

## remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_sanitize_ctest.json

```sh
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/cpu-sanitize --output-on-failure -V
```

Exit: 0; status: completed; wall seconds: 231.78011473000004. [remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_sanitize_ctest.json](remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cpu_sanitize_ctest.json).

## remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cuda_build.json

```sh
cmake --build /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release --parallel 2
```

Exit: 0; status: completed; wall seconds: 79.32545715699996. [remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cuda_build.json](remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cuda_build.json).

## remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cuda_configure.json

```sh
cmake -S /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark -DCMAKE_CXX_FLAGS= '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG' -DMAB_ENABLE_OPENMP=ON -DBUILD_TESTING=ON -B /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_CUDA_SORT=ON -DMAB_ENABLE_CPU_GPU_COMPARISON=ON -DMAB_ENABLE_SANITIZERS=OFF -DCMAKE_CUDA_ARCHITECTURES=75 -DCMAKE_CUDA_FLAGS= '-DCMAKE_CUDA_FLAGS_RELEASE=-O3 -DNDEBUG'
```

Exit: 0; status: completed; wall seconds: 7.9622537740000325. [remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cuda_configure.json](remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cuda_configure.json).

## remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cuda_correctness.json

```sh
/content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/test_cuda_sorting
```

Exit: 0; status: completed; wall seconds: 1.0931762000000163. [remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cuda_correctness.json](remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cuda_correctness.json).

## remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cuda_ctest.json

```sh
ctest --test-dir /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release --output-on-failure -V
```

Exit: 0; status: completed; wall seconds: 60.37553225800002. [remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cuda_ctest.json](remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/cuda_ctest.json).

## remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/pilot.json

```sh
/usr/bin/python3 /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/scripts/run_cpu_gpu_pilot.py --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3 --executable /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/cpu_gpu_comparison --input-tool /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/build/validation_v3/gpu-release/comparison_input --prerequisites /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/validation_v3/PREREQUISITES.json
```

Exit: 0; status: completed; wall seconds: 7.360124724000002. [remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/pilot.json](remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/pilot.json).

## remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/preflight.json

```sh
/usr/bin/python3 /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/scripts/cuda_preflight.py --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/validation_v3/preflight --timeout-seconds 180
```

Exit: 0; status: completed; wall seconds: 7.579227378000041. [remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/preflight.json](remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/preflight.json).

## remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/regenerate.json

```sh
/usr/bin/python3 /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/scripts/analyze_cpu_gpu.py /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/raw/pilot_v3 --output /content/cpu_gpu_pilot_20261010T001232473460Z_v3/modern-algorithm-benchmark/results/processed/pilot_v3/summary_regenerated.json
```

Exit: 0; status: completed; wall seconds: 0.17302373600000465. [remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/regenerate.json](remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/commands/regenerate.json).

The final integrity check is `python3 results/raw/cpu_gpu_pilot_20261010T001232473460Z/final_integrity.py`; its result is saved in FINAL_INTEGRITY.json. Read-only inspection also used pwd, rg, cat/sed/tail, colab --help/new --help/download --help/version and process inspection. A discovery-only colab start --help returned2 (command does not exist); correct new syntax was used. Mistyped read-only source paths returned missing-file diagnostics and were corrected. One documentation apply_patch attempt was rejected as an invalid hunk before any file changed. Two evidence report-generator syntax failures are retained above and corrected by v3/v4; raw measurements were unaffected.

Final integrity review: initial `python3 results/raw/cpu_gpu_pilot_20261010T001232473460Z/final_integrity.py` exit1, incorrect post-integration diff baseline; corrected `python3 results/raw/cpu_gpu_pilot_20261010T001232473460Z/final_integrity_v2.py` uses the verified frozen CMake archive. Its result/exit are in FINAL_INTEGRITY.json; no source/data change.
