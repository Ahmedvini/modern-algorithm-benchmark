# Commands, observed statuses and safety classification

Only static inspections, explicit local source-hash renewal and focused inert Python methods ran. No actual CTest, native selection, configure/build, prerequisite/resource probe, timing trial, benchmark or GPU command ran.

Recorder prefix: `python3 -B results/raw/ctest_path_repair_20261010T234224414430Z/record.py NAME SAFETY CHILD_ARGV...`. Every commands/*.json contains exact child argv/cwd, complete stdout/stderr and actual exit code.

Early shell inspections and tool edits: EARLY_COMMANDS.md.

## Exclusive evidence bootstrap

```sh
python3 -B -c 'import datetime,hashlib,json,sys;from pathlib import Path
r=Path.cwd();b=r/"results/raw"/("ctest_path_repair_"+datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"));b.mkdir()
def hashes(paths):return {str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths)) if p.is_file()}
prior=hashes(p for p in (r/"results").rglob("*") if b not in p.parents)
project=hashes([r/"AGENTS.md",r/"README.md",r/"CMakeLists.txt"]+[p for n in ["scripts","tests","docs","include","src","cmake","third_party"] for p in (r/n).rglob("*") if "__pycache__" not in p.parts])
metadata=hashes(p for p in (r/"build").rglob("*") if p.name in ["CTestTestfile.cmake","CTestCustom.cmake","CTestCustom.ctest","CTestConfig.cmake","DartConfiguration.tcl"])
d=dict(command_argv=sys.orig_argv,cwd=str(r),prior_results_sha256=prior,project_sha256=project,build_metadata_sha256=metadata,git_metadata_present=(r/".git").exists())
with (b/"BEFORE.json").open("x") as f:json.dump(d,f,indent=2,sort_keys=True);f.write("\n")
for p in ["scripts/non_timing_tests.py","tests/test_ctest_build_guard.py","docs/NON_TIMING_TEST_SELECTION_v1.json","docs/CTEST_BUILD_GUARD_v1.md","README.md","docs/ROADMAP.md","docs/AUDIT.md"]:
 out=b/"before"/p;out.parent.mkdir(parents=True,exist_ok=True)
 with out.open("xb") as f:f.write((r/p).read_bytes())
print(b);print("prior results",len(prior),"project",len(project),"build metadata",len(metadata),"Git metadata",d["git_metadata_present"])'
```

Exit0, observed in terminal. Only file hashes, seven original-file copies and exclusive evidence creation. Exact program retained in BEFORE.json.


## all_inert_selector_regressions

```sh
python3 -B results/raw/ctest_path_repair_20261010T234224414430Z/run_inert_tests.py all
```

Exit 0; safety: 36 guard plus 11 existing selector methods; process launch blocked and callbacks fake; no native tests. Full output: `commands/all_inert_selector_regressions.json`.


## audit_append_context

```sh
tail -n 28 README.md docs/AUDIT.md
```

Exit 0; safety: read-only documentation tails. Full output: `commands/audit_append_context.json`.


## final_file_review

```sh
python3 -B results/raw/ctest_path_repair_20261010T234224414430Z/review_changes.py
```

Exit 0; safety: AST/diffs only; preserve reviewed source bytes; no project execution. Full output: `commands/final_file_review.json`.


## final_source_and_docs_review

```sh
cat scripts/non_timing_tests.py docs/CTEST_BUILD_GUARD_v1.md
```

Exit 0; safety: read-only final source/documentation inspection; no execution. Full output: `commands/final_source_and_docs_review.json`.


## inert_regressions_after_repair

```sh
python3 -B results/raw/ctest_path_repair_20261010T234224414430Z/run_inert_tests.py new
```

Exit 0; safety: 8 inert methods only; all real subprocess launch blocked; no CTest or GPU. Full output: `commands/inert_regressions_after_repair.json`.


## inert_reproducer_before_fix

```sh
python3 -B results/raw/ctest_path_repair_20261010T234224414430Z/run_inert_tests.py new
```

Exit 1; safety: 8 inert regression methods; all actual process launch blocked; expected defect reproduction only. Full output: `commands/inert_reproducer_before_fix.json`.


## inspect_inert_wrapper

```sh
cat results/raw/ctest_path_repair_20261010T234224414430Z/run_inert_tests.py
```

Exit 0; safety: source text only; fake-only test runner inspection. Full output: `commands/inspect_inert_wrapper.json`.


## inspected_test_infrastructure

```sh
cat tests/test_ctest_build_guard.py tests/ctest_fixture.py results/raw/ctest_hook_repair_20261010T223851377458Z/run_existing_inert_selection_tests.py scripts/cpu_gpu_protocol.py scripts/cpu_gpu_provenance.py
```

Exit 0; safety: source text only; no tests or subprocess workloads. Full output: `commands/inspected_test_infrastructure.json`.


## preservation_after

```sh
python3 -B results/raw/ctest_path_repair_20261010T234224414430Z/verify_preservation.py AFTER_VERIFIED
```

Exit 0; safety: file hashes and exact source-policy/selection comparisons only. Full output: `commands/preservation_after.json`.


## preservation_before

```sh
python3 -B results/raw/ctest_path_repair_20261010T234224414430Z/verify_preservation.py BEFORE_VERIFIED
```

Exit 0; safety: file hashes/JSON only; no project execution. Full output: `commands/preservation_before.json`.


## review_new_regression_source

```sh
sed -n 48,210p tests/test_ctest_build_guard.py
```

Exit 0; safety: static source read before executing only inert tests. Full output: `commands/review_new_regression_source.json`.


## save_pre_fix_reproducer

```sh
python3 -B -c 'from pathlib import Path;b=Path("results/raw/ctest_path_repair_20261010T234224414430Z");
for name in ["scripts/non_timing_tests.py","tests/test_ctest_build_guard.py","docs/NON_TIMING_TEST_SELECTION_v1.json"]:
 p=b/"reproducer_before_fix"/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("xb") as f:f.write(Path(name).read_bytes())'
```

Exit 0; safety: copy current candidate bytes to new evidence only; no workloads. Full output: `commands/save_pre_fix_reproducer.json`.


## source_policy_after_repair

```sh
python3 -B results/raw/ctest_path_repair_20261010T234224414430Z/renew_source_policy.py SOURCE_REVIEW_REPAIR
```

Exit 0; safety: explicit renewal of two inspected source hashes; all policy classifications/commands unchanged. Full output: `commands/source_policy_after_repair.json`.


## source_policy_for_reproducer

```sh
python3 -B results/raw/ctest_path_repair_20261010T234224414430Z/renew_source_policy.py SOURCE_REVIEW_REPRODUCER
```

Exit 0; safety: explicit repair-time source hash renewal only; no discovery or tests. Full output: `commands/source_policy_for_reproducer.json`.


## Final integrity seal

```sh
python3 -B results/raw/ctest_path_repair_20261010T234224414430Z/seal_repair.py
```

Exit0 on successful completion, unwrapped terminal command; file hashes/retained-log checks/new evidence writes only.
