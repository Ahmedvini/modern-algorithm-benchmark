# Commands and observed exit statuses

Initial read-only inspection used pwd, rg, cat/sed and Python hash/manifest checks. The initial hash/seal snapshot completed with exit0; its verified inputs are in freeze_verified.json and source_before.json. No Git metadata is present (recorded git status128).

- Local `colab --help` — exit 0; log `commands/colab_help.json`.
- Local `colab sessions` — exit 0; log `commands/colab_sessions.json`.
- Local `colab new --session cub-workspace-65537-20261010T110457Z --gpu T4` — exit 0; log `commands/create_fresh_t4.json`.
- Local `colab download /content/cub_workspace_65537_20261010T110457531249Z/workspace_evidence.tar.gz /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/cub_workspace_65537_20261010T110457531249Z/workspace_evidence.tar.gz --session cub-workspace-65537-20261010T110457Z` — exit 0; log `commands/download_resource_evidence.json`.
- Local `colab status --session cub-workspace-65537-20261010T110457Z` — exit 0; log `commands/fresh_session_status.json`.
- Local `git status --short` — exit 128; log `commands/git_status.json`.
- Local `python3 /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/cub_workspace_65537_20261010T110457531249Z/verify_download.py` — exit 0; log `commands/independent_verification.json`.
- Local `colab exec --session cub-workspace-65537-20261010T110457Z --file /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/cub_workspace_65537_20261010T110457531249Z/inspect_fresh_session.py --timeout 120` — exit 0; log `commands/inspect_fresh_session.json`.
- Local `colab download /content/cub_workspace_65537_20261010T110457531249Z/evidence/configure.json /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/cub_workspace_65537_20261010T110457531249Z/progress_configure.json --session cub-workspace-65537-20261010T110457Z` — exit 0; log `commands/progress_configure.json`.
- Local `colab exec --session cub-workspace-65537-20261010T110457Z --file /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/cub_workspace_65537_20261010T110457531249Z/remote_resource_check.py --timeout 900` — exit 0; log `commands/remote_resource_validation.json`.
- Local `colab upload results/raw/cpu_gpu_pilot_20261010T001232473460Z/cpu_gpu_pilot_source_v2.tar.gz /content/cub_workspace_source_65537.tar.gz --session cub-workspace-65537-20261010T110457Z` — exit 0; log `commands/upload_verified_source.json`.
- Remote `cmake --build /content/cub_workspace_65537_20261010T110457531249Z/modern-algorithm-benchmark/build/resource_fresh --target cpu_gpu_comparison --parallel 2` — exit 0; full stdout/stderr `downloaded/evidence/build.json`.
- Remote `cmake -S . -B /content/cub_workspace_65537_20261010T110457531249Z/modern-algorithm-benchmark/build/resource_fresh -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DMAB_ENABLE_SANITIZERS=OFF -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_CUDA_SORT=ON -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_CPU_GPU_COMPARISON=ON -DCMAKE_CUDA_ARCHITECTURES=75 -DCMAKE_CXX_FLAGS= '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG' -DCMAKE_CUDA_FLAGS= '-DCMAKE_CUDA_FLAGS_RELEASE=-O3 -DNDEBUG'` — exit 0; full stdout/stderr `downloaded/evidence/configure.json`.
- Remote `/content/cub_workspace_65537_20261010T110457531249Z/modern-algorithm-benchmark/build/resource_fresh/cpu_gpu_comparison --describe` — exit 0; full stdout/stderr `downloaded/evidence/describe.json`.
- Remote `nvidia-smi --query-gpu=name,uuid,driver_version,memory.total,memory.free,temperature.gpu,clocks.sm,clocks.mem,power.limit --format=csv,noheader,nounits` — exit 0; full stdout/stderr `downloaded/evidence/gpu_after.json`.
- Remote `nvidia-smi` — exit 0; full stdout/stderr `downloaded/evidence/gpu_initial.json`.
- Remote `nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader,nounits` — exit 0; full stdout/stderr `downloaded/evidence/gpu_processes_initial.json`.
- Remote `/content/cub_workspace_65537_20261010T110457531249Z/modern-algorithm-benchmark/build/resource_fresh/cpu_gpu_comparison --resources 65537` — exit 0; full stdout/stderr `downloaded/evidence/resources_65537.json`.

Evidence-only generation: `python3 /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/cub_workspace_65537_20261010T110457531249Z/write_audit.py`; final sealing: `python3 /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/cub_workspace_65537_20261010T110457531249Z/seal_integrity.py`. Their actual exits are reported by the invoking command and final manifest, rather than pre-assumed here.
