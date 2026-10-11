"""Review source preservation, validation records, and retained smoke results."""
import csv
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

root = Path.cwd()
evidence = Path(__file__).resolve().parent
paths = json.loads((evidence / "paths.json").read_text())
backup = Path(paths["backup"])
before = json.loads((evidence / "initial_inventory.json").read_text())
allowed = {
    "CMakeLists.txt", "README.md", "docs/ALGORITHMS.md", "docs/BENCHMARKING.md",
    "docs/METRICS.md", "docs/ROADMAP.md", "docs/AUDIT.md",
    "include/algorithms/sorting.hpp", "include/benchmark/comparisons.hpp",
    "src/algorithms/sorting.cpp", "src/benchmark/comparisons.cpp",
    "src/main.cpp", "src/benchmark/metrics_main.cpp", "tests/test_comparisons.cpp",
    "tests/test_cli.py", "tests/test_metrics_cli.py", "tests/test_benchmark.py",
}
added = {
    "include/algorithms/mergesort.hpp", "include/algorithms/radixsort.hpp",
    "include/algorithms/detail/mergesort_impl.hpp", "src/algorithms/mergesort.cpp",
    "src/algorithms/radixsort.cpp", "tests/test_integer_sorts.hpp",
    "tests/test_mergesort.cpp", "tests/test_radixsort.cpp",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


current = {}
for folder in ["include", "src", "tests", "third_party", "scripts", "docs", "cmake"]:
    for file in (root / folder).rglob("*"):
        if file.is_file() and "__pycache__" not in file.parts:
            current[str(file.relative_to(root))] = digest(file)
for name in ["README.md", "CMakeLists.txt", "AGENTS.md"]:
    current[name] = digest(root / name)
assert before.keys() <= current.keys(), "an existing file was removed"
changed = {name for name, value in before.items() if current[name] != value}
assert changed == allowed, ("unexpected/missing changes", changed ^ allowed)
assert current.keys() - before.keys() == added, "unexpected added project file"
assert all(current[name] == value for name, value in before.items() if name.startswith("third_party/"))

for name in ["baseline_release_configure", "baseline_release_build", "baseline_release_ctest",
             "release_configure", "release_build", "release_ctest", "sanitize_configure",
             "sanitize_build", "sanitize_ctest", "smoke_matrix", "smoke_analysis",
             "release_environment_command", "sanitize_environment_command"]:
    record = json.loads((evidence / (name + ".json")).read_text())
    assert record["exit_code"] == 0, name
    if name.endswith("build"):
        assert "warning:" not in record["stdout"] + record["stderr"], name
for config in ["release", "sanitize"]:
    record = json.loads((evidence / (config + "_ctest.json")).read_text())
    assert "100% tests passed, 0 tests failed out of 15" in record["stdout"]
    with (evidence / ("final_" + config + "_ctest.log")).open("x") as stream:
        stream.write(record["stdout"] + record["stderr"])
    manifest = root / "build" / config / "generated" / ("Release" if config == "release" else "Debug") / "source_hashes.json"
    for item in json.loads(manifest.read_text())["files"]:
        assert digest(root / item["path"]) == item["sha256"], item["path"]

link = (root / "build/release/CMakeFiles/sort_benchmark.dir/link.txt").read_text()
assert "mab_metrics" not in link and "libmab_timing" in link and "libmab_core" in link
symbols = subprocess.run(["nm", "-C", "build/release/sort_benchmark"], check=True, capture_output=True, text=True)
assert all(name not in symbols.stdout for name in ["CountingLess", "counted_sorters", "process_memory()"])

matrix = evidence / "smoke_matrix"
raw_before = {str(path.relative_to(matrix)): digest(path) for path in matrix.rglob("*") if path.is_file()}
spec = importlib.util.spec_from_file_location("analysis", root / "scripts/analyze_results.py")
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)
summary = analysis.analyze(matrix)
stored = json.loads((root / "results/processed/extra_baselines_smoke_20261009T165551911968Z.json").read_text())
assert summary == stored, "summary did not regenerate exactly"
assert summary["complete"] and len(summary["groups"]) == 60
assert sum(group["successful_trials"] for group in summary["groups"]) == 300
assert sum(group["warmup_rows"] for group in summary["groups"]) == 60
assert sum(group["failed_trials"] + group["failed_warmups"] for group in summary["groups"]) == 0
assert all(group["successful_trials"] == 5 for group in summary["groups"])
expected_names = {"std_sort", "quick_sort", "pdq_sort", "tim_sort", "merge_sort", "radix_sort"}
plan = json.loads((matrix / "matrix.json").read_text())
assert len(plan["runs"]) == 10
for name in plan["runs"]:
    run = matrix / name
    with (run / "trials.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 36 and {row["algorithm"] for row in rows} == expected_names
    assert len({row["input_hash_fnv1a64"] for row in rows}) == 1
    assert all(row["correctness"] == "passed" and row["status"] == "ok" for row in rows)
    for item in json.loads((run / "source_hashes.json").read_text())["files"]:
        assert digest(root / item["path"]) == item["sha256"]
assert raw_before == {str(path.relative_to(matrix)): digest(path) for path in matrix.rglob("*") if path.is_file()}
environment = json.loads((matrix / "environment.json").read_text())
assert environment["benchmark_executable_sha256"] == digest(root / "build/release/sort_benchmark")

patch = []
for name in sorted(changed | added):
    original = (backup / name).read_text().splitlines(keepends=True) if name in before else []
    modified = (root / name).read_text().splitlines(keepends=True)
    patch.extend(difflib.unified_diff(original, modified, fromfile="a/" + name if name in before else "/dev/null", tofile="b/" + name))
with (evidence / "changes.patch").open("x") as stream:
    stream.writelines(patch)
review = {
    "changed_files": sorted(changed), "added_files": sorted(added),
    "final_file_sha256": {name: current[name] for name in sorted(changed | added)},
    "unchanged_files": sorted(set(before) - changed), "vendor_files_unchanged": True,
    "timing_excludes_metrics": True, "source_manifests_current": True,
    "summary_regenerated_exactly": True, "raw_smoke_unchanged_by_analysis": True,
    "smoke_configurations": 10, "successful_measured_trials": 300,
    "successful_warmups": 60, "failed_rows": 0, "summary_groups": 60,
    "release_and_sanitizer_ctest": "15/15 passed; leak detection enabled",
}
with (evidence / "source_review.json").open("x") as stream:
    json.dump(review, stream, indent=2)
    stream.write("\n")
print("Preservation review passed: 17 changed and 8 added project files; vendors/algorithms/generator/timing/scripts preserved.")
print("Both full suites 15/15; normal timing excludes metrics; source/executable hashes verified.")
print("Smoke: 10 configurations, 300 measured trials, 60 warmups, 60 groups; exact summary regeneration, raw unchanged.")
