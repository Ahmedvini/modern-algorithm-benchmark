import csv
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

EXECUTABLE = str(Path(sys.argv.pop(1)).resolve())
ROOT = Path(__file__).resolve().parents[1]
SORTERS = {"std_sort", "quick_sort", "pdq_sort", "tim_sort", "merge_sort", "radix_sort"}
spec = importlib.util.spec_from_file_location("analysis", ROOT / "scripts/analyze_results.py")
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def run_cli(self, output, *args):
        return subprocess.run([EXECUTABLE, "--output", str(output), "--validation-only", *args],
                              capture_output=True, text=True)

    def bundle(self, name="run", *args):
        directory = self.root / name
        result = self.run_cli(directory, "--size", "31", "--sort", "all", "--repetitions", "2", "--warmups", "1", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return directory

    def test_schema_equivalent_input_and_escaping(self):
        run_id = 'trial, "quoted"\nnext'
        directory = self.bundle("run", "--run-id", run_id)
        metadata = json.loads((directory / "run.json").read_text())
        self.assertEqual(metadata["run_id"], run_id)
        self.assertEqual(metadata["run_kind"], "validation")
        self.assertTrue(metadata["compiler_id"])
        self.assertEqual(set(metadata["algorithms"]), SORTERS)
        self.assertEqual(len(metadata["algorithms"]), len(SORTERS))
        with (directory / "trials.csv").open(newline="") as stream:
            reader = csv.DictReader(stream)
            self.assertEqual(reader.fieldnames, analysis.FIELDS)
            rows = list(reader)
        self.assertEqual(len(rows), 3 * len(SORTERS))
        self.assertEqual({row["algorithm"] for row in rows}, SORTERS)
        self.assertEqual({row["run_id"] for row in rows}, {run_id})
        self.assertEqual(len({row["input_hash_fnv1a64"] for row in rows}), 1)
        self.assertTrue(all(row["correctness"] == "passed" and int(row["elapsed_ns"]) >= 0 for row in rows))
        self.assertTrue((directory / "COMPLETE.json").exists())
        result = analysis.analyze(directory)
        self.assertTrue(result["complete"])
        self.assertEqual([group["successful_trials"] for group in result["groups"]], [2] * len(SORTERS))
        self.assertEqual([group["warmup_rows"] for group in result["groups"]], [1] * len(SORTERS))

    def test_all_distributions_reproducible_and_boundaries(self):
        for index, distribution in enumerate(("uniform", "sorted", "reverse_sorted", "duplicate_heavy", "nearly_sorted")):
            for size in (0, 1, 33):
                with self.subTest(distribution=distribution, size=size):
                    params = ("--size", str(size), "--distribution", distribution, "--seed", "18446744073709551615")
                    first = self.bundle(f"first{index}_{size}", *params)
                    second = self.bundle(f"second{index}_{size}", *params)
                    a = json.loads((first / "run.json").read_text())
                    b = json.loads((second / "run.json").read_text())
                    self.assertEqual(a["input_hash_fnv1a64"], b["input_hash_fnv1a64"])
                    self.assertEqual(a["distribution"], distribution)
                    self.assertEqual(a["nearly_sorted_swaps"], 0 if distribution == "sorted" else size // 100)

    def test_invalid_configuration_before_output_creation(self):
        for index, args in enumerate([
                ("--size", "-1"), ("--size", "+1"), ("--size", "18446744073709551616"),
                ("--size", "999999999", "--memory-limit-mib", "1"), ("--repetitions", "0"),
                ("--repetitions", "10001"), ("--repetitions", "-1"), ("--warmups", "1001"),
                ("--seed", "18446744073709551616"), ("--seed", "bad"), ("--sort", "unknown"),
                ("--sort", "std_sort,std_sort"), ("--sort", "std_sort,"), ("--distribution", "bad"),
                ("--distinct", "0"), ("--distinct", "4294967297"), ("--memory-limit-mib", "0"),
                ("--swaps", "10000001"), ("--unknown",), ("--size",)]):
            path = self.root / f"invalid{index}"
            result = self.run_cli(path, *args)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertTrue(result.stderr.startswith("error: "))
            self.assertFalse(path.exists())

    def test_output_safety(self):
        path = self.bundle()
        before = {file.name: file.read_bytes() for file in path.iterdir()}
        self.assertEqual(self.run_cli(path).returncode, 1)
        self.assertEqual(before, {file.name: file.read_bytes() for file in path.iterdir()})
        existing_file = self.root / "file"
        existing_file.write_text("preserve")
        self.assertEqual(self.run_cli(existing_file).returncode, 1)
        self.assertEqual(existing_file.read_text(), "preserve")
        self.assertEqual(self.run_cli(self.root / "missing" / "child").returncode, 1)
        link = self.root / "link"
        try:
            link.symlink_to(path, target_is_directory=True)
        except OSError:
            return  # Symlink support may require privileges on Windows.
        self.assertEqual(self.run_cli(link).returncode, 1)
        self.assertEqual(before, {file.name: file.read_bytes() for file in path.iterdir()})

    def test_statistics_synthetic_and_outliers_retained(self):
        self.assertEqual(analysis.summarize_samples([10, 20, 30]), {
            "successful_trials": 3, "median_ns": 20, "mean_ns": 20, "stdev_ns": 10.0, "min_ns": 10, "max_ns": 30})
        self.assertEqual(analysis.summarize_samples([10, 20])["median_ns"], 15)
        self.assertIsNone(analysis.summarize_samples([10])["stdev_ns"])
        self.assertIsNone(analysis.summarize_samples([])["mean_ns"])
        self.assertEqual(analysis.summarize_samples([10, 20, 30, 10000])["max_ns"], 10000)
        for malformed in ("-1", "+1", "nan", "1.5", "", str(2**64)):
            with self.assertRaises(ValueError):
                analysis.integer(malformed)

    def test_statistics_through_synthetic_csv(self):
        path = self.bundle("synthetic", "--sort", "std_sort", "--repetitions", "3", "--warmups", "0")
        with (path / "trials.csv").open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        for row, synthetic in zip(rows, [10, 20, 30]):
            row["elapsed_ns"] = str(synthetic)
        # Deliberately replace observations only in this synthetic temporary test fixture.
        with (path / "trials.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=analysis.FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        group = analysis.analyze(path)["groups"][0]
        for name, expected in {"successful_trials": 3, "median_ns": 20, "mean_ns": 20,
                               "stdev_ns": 10, "min_ns": 10, "max_ns": 30}.items():
            self.assertEqual(group[name], expected)

    def test_analysis_fail_closed_and_partial_counts(self):
        path = self.bundle()
        (path / "COMPLETE.json").unlink()
        with self.assertRaises(ValueError):
            analysis.analyze(path)
        self.assertFalse(analysis.analyze(path, allow_incomplete=True)["complete"])
        with (path / "trials.csv").open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        rows[-1].update(status="error", correctness="failed", error='bad, "output"\nfailed')
        with (path / "trials.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=analysis.FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        partial = analysis.analyze(path, allow_incomplete=True)
        self.assertEqual(sum(group["failed_trials"] for group in partial["groups"]), 1)
        summary = self.root / "partial.json"
        result = subprocess.run([sys.executable, str(ROOT / "scripts/analyze_results.py"), str(path),
                                 "--output", str(summary), "--allow-incomplete"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(summary.read_text())["complete"])

    def test_analysis_rejects_schema_tampering_and_protects_output(self):
        path = self.bundle()
        summary = self.root / "summary.json"
        command = [sys.executable, str(ROOT / "scripts/analyze_results.py"), str(path), "--output", str(summary)]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        before = summary.read_bytes()
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
        self.assertEqual(summary.read_bytes(), before)
        raw = (path / "trials.csv").read_text()
        (path / "trials.csv").write_text(raw.replace("elapsed_ns", "bad_schema", 1))
        with self.assertRaises(ValueError):
            analysis.analyze(path)

    def test_default_help_and_build_policy(self):
        self.assertEqual(subprocess.run([EXECUTABLE, "--help"], capture_output=True).returncode, 0)
        path = self.root / "default"
        result = self.run_cli(path, "--size", "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads((path / "run.json").read_text())
        self.assertEqual(metadata["algorithms"], ["std_sort"])
        self.assertEqual(metadata["repetitions"], 5)
        self.assertEqual(metadata["warmups"], 1)
        other = self.root / "policy"
        result = subprocess.run([EXECUTABLE, "--output", str(other), "--size", "0"], capture_output=True)
        self.assertEqual(result.returncode, 0 if metadata["build_type"] == "Release" and not metadata["sanitizers"] else 1)

    def test_small_matrix_and_validation_failures(self):
        path = self.root / "matrix"
        command = [sys.executable, str(ROOT / "scripts/run_matrix.py"), "--binary", EXECUTABLE,
                   "--output", str(path), "--sizes", "0,16", "--seeds", "0", "--repetitions", "1",
                   "--warmups", "0", "--validation-only"]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = analysis.analyze(path)
        self.assertTrue(summary["complete"])
        self.assertEqual(len(summary["groups"]), 10 * len(SORTERS))
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
        for args in [("--sizes", "-1"), ("--sizes", "1,1"), ("--repetitions", "0"),
                     ("--seeds", "bad"), ("--sorts", "unknown"), ("--distributions", "bad")]:
            invalid = self.root / "invalid_matrix"
            result = subprocess.run(command[:4] + ["--output", str(invalid), *args], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(invalid.exists())

    def test_new_baseline_subsets_and_registry_discovery(self):
        listed = subprocess.run([EXECUTABLE, "--list-sorts"], capture_output=True, text=True)
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertEqual(set(listed.stdout.splitlines()), SORTERS)
        fingerprints = []
        for name in ("std_sort", "merge_sort", "radix_sort", "merge_sort,radix_sort"):
            path = self.bundle(name.replace(",", "_"), "--sort", name, "--size", "257", "--seed", "42")
            with (path / "trials.csv").open(newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual({row["algorithm"] for row in rows}, set(name.split(",")))
            fingerprints.extend(row["input_hash_fnv1a64"] for row in rows)
            self.assertTrue(analysis.analyze(path)["complete"])
        self.assertEqual(len(set(fingerprints)), 1)
        for alias in ("mergesort", "radixsort", "merge_sort_typo", "radix_sort_typo"):
            path = self.root / alias
            self.assertEqual(self.run_cli(path, "--sort", alias).returncode, 1)
            self.assertFalse(path.exists())

    @unittest.skipIf(os.name == "nt", "test subprocess stub uses POSIX executable scripts")
    def test_matrix_failure_remains_explicit(self):
        fake_build = self.root / "fakebuild"
        fake_build.mkdir()
        actual_cache = next(parent / "CMakeCache.txt" for parent in Path(EXECUTABLE).parents
                            if (parent / "CMakeCache.txt").exists())
        (fake_build / "CMakeCache.txt").write_bytes(actual_cache.read_bytes())
        binary = fake_build / "injected_failure"
        binary.write_text('#!/usr/bin/env python3\nimport sys\n'
                          'if "--list-sorts" in sys.argv:\n    print("std_sort")\n'
                          'else:\n    sys.stderr.write("injected child failure\\n")\n    sys.exit(9)\n')
        binary.chmod(0o700)
        output = self.root / "failed_matrix"
        command = [sys.executable, str(ROOT / "scripts/run_matrix.py"), "--binary", str(binary),
                   "--output", str(output), "--sizes", "1", "--distributions", "uniform", "--validation-only"]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse((output / "COMPLETE.json").exists())
        self.assertTrue((output / "FAILED.json").exists())
        self.assertEqual(json.loads((output / "run_000000_command.json").read_text())["exit_code"], 9)
        with self.assertRaises(ValueError):
            analysis.analyze(output)
        partial = analysis.analyze(output, allow_incomplete=True)
        self.assertFalse(partial["complete"])
        self.assertEqual(len(partial["missing_runs"]), 1)


if __name__ == "__main__":
    unittest.main()
