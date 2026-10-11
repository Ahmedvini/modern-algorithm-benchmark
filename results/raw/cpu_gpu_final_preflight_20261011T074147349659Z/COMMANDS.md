# Preflight commands and exit statuses

Repository cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark. Review only plus one offline documented eligibility gate and Colab metadata attempt. No CTest, tests, build/configuration, GPU workload, warmup, measured trial, pilot, performance sweep or study ran.

Initial unwrapped inspection command (exit0):
```sh
pwd
cat AGENTS.md
ls results/raw/bounded_resume_20261011T024034091796Z
cat results/raw/bounded_resume_20261011T024034091796Z/FINAL_AUDIT.md
```

Initial read-only identity baseline was executed with `python3 -B -` from repository root: SHA256 every prior sealed190 member and current project/build/frozen/protected maps; exclusive timestamped directory creation, BEFORE.json and record.py, then subprocess `git status --short --branch`. Shell/Python exit0; Git child128 (no Git metadata). Full resulting maps are in BEFORE.json. No Git mutation.

## cli_auth_help.json

- Exit: 0
- Purpose: CLI help only; no authentication credentials supplied or session creation
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- UTC: 2026-10-11T07:44:43.953540+00:00
- Exact output: [cli_auth_help.json](cli_auth_help.json)

```sh
colab --help
```

## corrected_review_parser_assembly.json

- Exit: 0
- Purpose: Create additive evidence-only parser revision; preserve failed parser and logs
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- UTC: 2026-10-11T07:46:52.864321+00:00
- Exact output: [corrected_review_parser_assembly.json](corrected_review_parser_assembly.json)

```sh
python3 -B -c 'from pathlib import Path;p=Path("results/raw/cpu_gpu_final_preflight_20261011T074147349659Z");s=(p/"verify_review.py").read_text();old="r\x27\\d+/21 Test #\\d+: ([a-z_]+)\\s+\\.\\.\\.\\s+Passed\x27";new="r\x27\\d+/21 Test\\s+#\\d+: ([a-z_]+)\\s+\\.{3,}\\s+Passed\x27";assert old in s;f=(p/"verify_review_v2.py").open("x");f.write(s.replace(old,new));f.close();print("Preserved v1; v2 accepts literal CTest alignment and dotted padding, same21-name/count requirement.")'
```

## documented_source_eligibility.json

- Exit: 1
- Purpose: Offline documented verify_source_extension gate only; no subprocess/test/workload APIs
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- UTC: 2026-10-11T07:42:45.755046+00:00
- Exact output: [documented_source_eligibility.json](documented_source_eligibility.json)

```sh
python3 -B -c 'import sys; sys.path.insert(0,"scripts"); from cpu_gpu_protocol import load_protocol,verify_source_extension; print(verify_source_extension(load_protocol()))'
```

## eligibility_paths_inspection.json

- Exit: 0
- Purpose: Read-only launch/analyzer provenance and policy control-flow inspection
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- UTC: 2026-10-11T07:43:35.903689+00:00
- Exact output: [eligibility_paths_inspection.json](eligibility_paths_inspection.json)

```sh
python3 -B -c 'from pathlib import Path; spans={"scripts/run_cpu_gpu_pilot.py":(1,155),"scripts/cpu_gpu_provenance.py":(1,260),"scripts/analyze_cpu_gpu.py":(1,130),"scripts/ctest_build_guard.py":(110,215)};[(print("FILE",p),print("\n".join(str(i)+":"+s for i,s in enumerate(Path(p).read_text().splitlines(),1) if a<=i<=b))) for p,(a,b) in spans.items()]'
```

## evidence_locations.json

- Exit: 0
- Purpose: Read-only evidence/doc inventory; no workloads
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- UTC: 2026-10-11T07:44:09.301403+00:00
- Exact output: [evidence_locations.json](evidence_locations.json)

```sh
python3 -B -c 'from pathlib import Path; import json; paths=["README.md","docs/ROADMAP.md","docs/EXPERIMENT_PROTOCOL.md","docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md","docs/studies/cpu_gpu_comparison_v1.matrix.json","docs/studies/cpu_gpu_comparison_v1.resources.csv","docs/studies/cpu_gpu_comparison_v1.freeze.json","docs/CPU_GPU_VALIDATION_POLICY_v2.json","results/raw/bounded_resume_20261011T024034091796Z/COMMANDS.md","results/raw/bounded_resume_20261011T024034091796Z/FINAL_INTEGRITY.json"];[(print(p,"read",len(Path(p).read_bytes()),"bytes")) for p in paths]; print("RELEVANT REPORTS"); roots=["cpu_gpu_pilot_20261010T001232473460Z","cub_workspace_65537_20261010T110457531249Z","ctest_path_independent_review_20261011T000547578754Z","isolated_colab_revalidation_20261011T011459127026Z","cpu_gpu_prelaunch_review_20261011T012430643251Z"];[(print(str(p)),print(p.read_text())) for root in roots for p in [Path("results/raw")/root/"FINAL_AUDIT.md"] if p.is_file()]; print("PILOT FILES");[(print(str(p))) for p in sorted(Path("results/raw/cpu_gpu_pilot_20261010T001232473460Z").glob("*"))]; print("MATRIX META"); m=json.loads(Path("docs/studies/cpu_gpu_comparison_v1.matrix.json").read_text());print(json.dumps({k:v for k,v in m.items() if k not in ["pilot","study","source_at_freeze_sha256"]},indent=2)); print("RESOURCES");print(Path("docs/studies/cpu_gpu_comparison_v1.resources.csv").read_text())'
```

## git_identity.json

- Exit: 128
- Purpose: Read-only repository identity
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- UTC: not recorded in leaf
- Exact output: [git_identity.json](git_identity.json)

```sh
git status --short --branch
```

## offline_independent_verification.json

- Exit: 1
- Purpose: Offline log parsing, frozen-anchor checks, sealed evidence hashes and classifier checks; no tests/workloads
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- UTC: 2026-10-11T07:46:28.551718+00:00
- Exact output: [offline_independent_verification.json](offline_independent_verification.json)

```sh
python3 -B results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/verify_review.py
```

## offline_independent_verification_v2.json

- Exit: 0
- Purpose: Offline evidence log/hash/provenance verification only; no tests/workloads
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- UTC: 2026-10-11T07:46:52.951280+00:00
- Exact output: [offline_independent_verification_v2.json](offline_independent_verification_v2.json)

```sh
python3 -B results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/verify_review_v2.py
```

## retained_manifest_inventory.json

- Exit: 0
- Purpose: Read-only structured evidence schemas and source identity inventory
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- UTC: 2026-10-11T07:45:10.168336+00:00
- Exact output: [retained_manifest_inventory.json](retained_manifest_inventory.json)

```sh
python3 -B -c 'from pathlib import Path; import json; roots=["results/raw/cpu_gpu_pilot_20261010T001232473460Z","results/raw/cub_workspace_65537_20261010T110457531249Z","results/raw/ctest_path_independent_review_20261011T000547578754Z","results/raw/isolated_colab_revalidation_20261011T011459127026Z","results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z"];[(print(root),print([(k,len(v) if isinstance(v,(dict,list)) else str(v)[:100]) for k,v in json.loads((Path(root)/"FINAL_INTEGRITY.json").read_text()).items()])) for root in roots if (Path(root)/"FINAL_INTEGRITY.json").is_file()];p=Path("results/raw/bounded_resume_20261011T024034091796Z/downloaded/evidence"); print("LATEST BUILD",(p/"BUILD_COMPLETE.json").read_text()); print("RAW PILOT BUILDS");[(print(str(q)),print(q.read_text()[:3500])) for q in Path(roots[0]).rglob("build.json")];print("DOC RUNNER REFERENCES");[(print(str(q),str(i)+":"+line)) for q in [Path("docs/BENCHMARKING.md"),Path("docs/AUDIT.md"),Path("README.md"),Path("docs/ROADMAP.md")] for i,line in enumerate(q.read_text().splitlines(),1) if any(t in line for t in ["run_cpu_gpu_study.py","--execute-study","PREREQUISITES.json","full-study prerequisites"])]'
```

## review_parser_diagnostics.json

- Exit: 0
- Purpose: Read retained test-summary lines only after offline parser assertion; no test execution
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- UTC: 2026-10-11T07:46:36.231611+00:00
- Exact output: [review_parser_diagnostics.json](review_parser_diagnostics.json)

```sh
python3 -B -c 'from pathlib import Path; import json,re;p=Path("results/raw/bounded_resume_20261011T024034091796Z/downloaded/evidence/validation_commands/cpu_release_ctest.json");t=json.loads(p.read_text())["stdout"];print("\n".join(repr(x) for x in t.splitlines() if "/21 Test" in x));print(re.findall(r"\d+/21 Test #\d+: ([a-z_]+)\s+\.\.\.\s+Passed",t))'
```

## session_inventory.json

- Exit: 1
- Purpose: Colab session metadata only; no new session or workloads
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- UTC: 2026-10-11T07:42:45.904774+00:00
- Exact output: [session_inventory.json](session_inventory.json)

```sh
colab sessions
```

## source_safety_inspection.json

- Exit: 0
- Purpose: Read-only source and retained diff inspection; no execution
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- UTC: 2026-10-11T07:43:18.510325+00:00
- Exact output: [source_safety_inspection.json](source_safety_inspection.json)

```sh
python3 -B -c 'from pathlib import Path; paths=["scripts/non_timing_tests.py","scripts/ctest_build_guard.py","tests/test_ctest_dart_compatibility.py","scripts/cpu_gpu_validation_policy.py","scripts/run_cpu_gpu_pilot.py"]; [(print("FILE",p),print(Path(p).read_text())) for p in paths]; d=Path("results/raw/bounded_resume_20261011T024034091796Z/final_diffs");[(print("DIFF",p),print(p.read_text())) for p in sorted(d.rglob("*.diff"))]'
```

## targeted_line_review.json

- Exit: 0
- Purpose: Static source lines for correctness isolation, build pin, policy and launch guards
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- UTC: 2026-10-11T07:44:44.555470+00:00
- Exact output: [targeted_line_review.json](targeted_line_review.json)

```sh
python3 -B -c 'from pathlib import Path; files={"tests/test_cuda_prepared_correctness.cpp": ["execute_untimed","std::sort","for (std::size_t","return 77"],"src/cuda/cub_timing.cu":["void CudaTimingSession::execute_untimed","CudaTimingSession::sample","sort_keys","copy_"],"tests/test_parallel_workers.cpp":["find_parallel_sorter","parallel_merge_sort","actual_team_size","32768","for (std::size_t"],"tests/test_ctest_dart_compatibility.py":["def test_","subprocess","discovery","os.system"],"scripts/cpu_gpu_validation_policy.py":["def ","study_eligible","bounded_validation_ready","launch_review_candidate"],"docs/CPU_GPU_VALIDATION_POLICY_v2.md":["Every assessment","current compatible","cannot use","timing workloads"],"scripts/run_cpu_gpu_study.py":["execute-study","run(args"],"cmake/cuda.cmake":["CUB","SHA256"]};[(print("FILE",p),print("\n".join(str(i)+":"+s for i,s in enumerate(Path(p).read_text().splitlines(),1) if any(x in s for x in terms)))) for p,terms in files.items()]'
```

## Evidence-only final consolidation

Executed from repository root; no subprocess/test/timing/GPU API:
```sh
python3 -B results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/finalize_review.py
```

Completion is established by FINAL_INTEGRITY.json and terminal marker FINAL_PREFLIGHT_REVIEW_SEALED; exit0 on successful completion. Source/evidence additions used apply_patch only inside this new review directory.

The initial offline parser exited1 because it expected a single space after Test and exactly3 dotted alignment characters. review_parser_diagnostics.json retains actual literal CTest lines. Additive verify_review_v2.py accepts whitespace/dotted padding while still requiring the exact21 names/count; it exited0. Both parser versions and failure output retained. No tests were rerun.

colab sessions exited1, requested local interactive authorization, and aborted. The authorization URL was redacted; no code/token supplied, requested from the user, or stored. CLI help exit0 does not establish session readiness.

Not executed: run_cpu_gpu_study.py, validate_cpu_gpu_pilot.py, selector CLI/discovery, tests, builds, GPU resource/worker/correctness commands. --dry-run would return before eligibility validation and was not used as evidence of launch readiness.
