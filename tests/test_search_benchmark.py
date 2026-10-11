import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

EXECUTABLE = str(Path(sys.argv.pop(1)).resolve())
COUNTS = str(Path(sys.argv.pop(1)).resolve())
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import analyze_search_results as analysis


class SearchBenchmarkTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def cli(self, output, *args):
        return subprocess.run([EXECUTABLE, "--output", str(output), "--validation-only", *args],
                              capture_output=True, text=True)

    def bundle(self, name="run", *args):
        path = self.root/name
        result = self.cli(path, "--size", "31", "--search", "all", "--queries", "8",
                          "--repetitions", "2", "--warmups", "1", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return path

    def test_schema_escaping_identity_availability(self):
        identity = 'search, "quoted"\nnext'
        path = self.bundle("schema", "--run-id", identity)
        meta = json.loads((path/"run.json").read_text())
        self.assertEqual(meta["run_id"], identity)
        self.assertEqual(meta["input_order"], "ascending")
        self.assertEqual(meta["algorithms"], ["linear_search", "binary_search", "exponential_search"])
        with (path/"trials.csv").open(newline="") as f:
            reader = csv.DictReader(f)
            self.assertEqual(reader.fieldnames, analysis.FIELDS)
            rows = list(reader)
        self.assertEqual(len(rows), 8*3*3)
        self.assertEqual({r["run_id"] for r in rows}, {identity})
        for category in analysis.CATEGORIES[:-1]:
            chosen = [r for r in rows if r["query_category"] == category]
            self.assertEqual(len({r["query_hash_fnv1a64"] for r in chosen}), 1)
        parsed = analysis.analyze(path)
        self.assertTrue(parsed["complete"])
        self.assertEqual(len(parsed["groups"]), 24)
        self.assertTrue(all(g["successful_trials"] == 2 and g["failed_trials"] == 0 for g in parsed["groups"]))
        self.assertEqual([e["category"] for e in parsed["availability"] if not e["available"]], ["miss_empty"])

    def test_reproducible_distributions_and_seeds(self):
        for d, distribution in enumerate(["uniform", "sorted", "reverse_sorted", "nearly_sorted", "duplicate_heavy"]):
            for size in [0, 1, 33]:
                args = ("--size", str(size), "--distribution", distribution, "--seed", "18446744073709551615",
                        "--query-seed", "18446744073709551615")
                a, b = self.bundle(f"a{d}_{size}", *args), self.bundle(f"b{d}_{size}", *args)
                self.assertEqual((a/"queries.csv").read_bytes(), (b/"queries.csv").read_bytes())
                self.assertEqual(json.loads((a/"run.json").read_text())["input_hash_fnv1a64"],
                                 json.loads((b/"run.json").read_text())["input_hash_fnv1a64"])
                self.assertTrue(analysis.analyze(a)["complete"])
        prepared = [json.loads((self.root/f"a{d}_33/run.json").read_text())["input_hash_fnv1a64"] for d in range(4)]
        self.assertEqual(len(set(prepared)), 1)

    def test_duplicates_and_explicit_unavailable(self):
        path = self.bundle("equal", "--distribution", "duplicate_heavy", "--distinct", "1")
        data = analysis.rows(path/"queries.csv", analysis.QUERY_FIELDS)
        last = [r for r in data if r["query_category"] == "hit_last"]
        self.assertTrue(all(r["target"] == "0" and r["selected_position"] == "30" and r["expected_position"] == "0" for r in last))
        self.assertFalse(next(e for e in analysis.analyze(path)["availability"] if e["category"] == "miss_between")["available"])
        empty = self.bundle("no_gap", "--size", "1", "--categories", "miss_between")
        parsed = analysis.analyze(empty)
        self.assertTrue(parsed["complete"])
        self.assertEqual(parsed["groups"], [])
        self.assertTrue(parsed["availability"][0]["reason"])

    def test_invalid_configuration(self):
        invalid = [("--size", "-1"), ("--size", "+1"), ("--size", str(2**64)),
                   ("--queries", "0"), ("--queries", "3"), ("--queries", "100002"),
                   ("--query-seed", "-1"), ("--query-seed", str(2**64)), ("--seed", "bad"),
                   ("--repetitions", "0"), ("--repetitions", "10001"), ("--warmups", "1001"),
                   ("--search", "bad"), ("--search", "binary_search,binary_search"), ("--search", "binary_search,"),
                   ("--categories", "bad"), ("--categories", "hit_first,hit_first"), ("--categories", ""),
                   ("--distribution", "bad"), ("--distinct", "0"), ("--distinct", str(2**32+1)),
                   ("--memory-limit-mib", "0"), ("--memory-limit-mib", "1", "--queries", "100000"),
                   ("--size", "100000000"), ("--swaps", "10000001"), ("--size",), ("--bad",)]
        for i, args in enumerate(invalid):
            path = self.root/f"bad{i}"
            result = self.cli(path, *args)
            self.assertEqual(result.returncode, 1, args)
            self.assertTrue(result.stderr.startswith("error:"), result.stderr)
            self.assertFalse(path.exists())

    def test_output_safety(self):
        path = self.bundle()
        before = {p.name: p.read_bytes() for p in path.iterdir()}
        self.assertEqual(self.cli(path).returncode, 1)
        self.assertEqual(before, {p.name: p.read_bytes() for p in path.iterdir()})
        ordinary = self.root/"file"
        ordinary.write_text("preserve")
        self.assertEqual(self.cli(ordinary).returncode, 1)
        self.assertEqual(ordinary.read_text(), "preserve")
        self.assertEqual(self.cli(self.root/"missing/child").returncode, 1)
        link = self.root/"link"
        try:
            link.symlink_to(path, target_is_directory=True)
        except OSError:
            return
        self.assertEqual(self.cli(link).returncode, 1)
        self.assertEqual(before, {p.name: p.read_bytes() for p in path.iterdir()})

    def test_statistics_synthetic_and_regeneration(self):
        path = self.bundle("synthetic", "--search", "linear_search", "--categories", "hit_first",
                           "--repetitions", "3", "--warmups", "0")
        data = analysis.rows(path/"trials.csv", analysis.FIELDS)
        for row, value in zip(data, [10, 20, 30]):
            row["elapsed_ns"] = str(value)
        # Only this temporary fixture is synthetic; no retained study data changes.
        with (path/"trials.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=analysis.FIELDS)
            writer.writeheader()
            writer.writerows(data)
        group = analysis.analyze(path)["groups"][0]
        for name, value in [("median", 20), ("mean", 20), ("stdev", 10), ("min", 10), ("max", 30)]:
            self.assertEqual(group[name+"_batch_ns"], value)
            self.assertEqual(group[name+"_normalized_ns_per_query"], value/8)
        before = {p.name: p.read_bytes() for p in path.iterdir()}
        outputs = [self.root/"summary1.json", self.root/"summary2.json"]
        for output in outputs:
            command = [sys.executable, str(ROOT/"scripts/analyze_search_results.py"), str(path), "--output", str(output)]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
        self.assertEqual(outputs[0].read_bytes(), outputs[1].read_bytes())
        self.assertEqual(before, {p.name: p.read_bytes() for p in path.iterdir()})
        self.assertEqual(analysis.summarize_samples([10, 20, 10000])["max_ns"], 10000)
        self.assertIsNone(analysis.summarize_samples([10])["stdev_ns"])

    def test_partial_failure_and_missing(self):
        path = self.bundle()
        (path/"COMPLETE.json").unlink()
        with self.assertRaises(ValueError):
            analysis.analyze(path)
        data = analysis.rows(path/"trials.csv", analysis.FIELDS)
        data[-1].update(status="error", correctness="failed", error='wrong, "answer"\nquery')
        with (path/"trials.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=analysis.FIELDS)
            writer.writeheader()
            writer.writerows(data)
        parsed = analysis.analyze(path, True)
        self.assertFalse(parsed["complete"])
        self.assertEqual(sum(g["failed_trials"] for g in parsed["groups"]), 1)
        result = subprocess.run([sys.executable, str(ROOT/"scripts/analyze_search_results.py"), str(path),
                                 "--output", str(self.root/"partial.json"), "--allow-incomplete"], capture_output=True)
        self.assertEqual(result.returncode, 1)
        with (path/"trials.csv").open("w", newline="") as f:
            csv.writer(f).writerow(analysis.FIELDS)
        empty = analysis.analyze(path, True)
        self.assertEqual(sum(g["missing_measured_trials"] for g in empty["groups"]), 48)

    def test_tampering_rejected(self):
        for i, field in enumerate(["query_id", "target", "selected_position", "expected_position", "expected_hit"]):
            path = self.bundle(f"tamper{i}")
            data = analysis.rows(path/"queries.csv", analysis.QUERY_FIELDS)
            data[0][field] = "99999" if field != "expected_hit" else "false"
            with (path/"queries.csv").open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=analysis.QUERY_FIELDS)
                writer.writeheader()
                writer.writerows(data)
            with self.assertRaises(ValueError):
                analysis.analyze(path)
        path = self.bundle("bad_csv")
        text = (path/"trials.csv").read_text()
        (path/"trials.csv").write_text(text.replace("elapsed_ns", "unknown_schema", 1))
        with self.assertRaises(ValueError):
            analysis.analyze(path)

    def test_separate_counts_and_exact_small_input(self):
        path = self.root/"counts"
        result = subprocess.run([COUNTS, "--output", str(path), "--search", "all", "--size", "5",
                                 "--distribution", "duplicate_heavy", "--distinct", "1", "--queries", "4",
                                 "--categories", "hit_first"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        meta = json.loads((path/"run.json").read_text())
        self.assertEqual(meta["protocol"], "search_counts_v1")
        self.assertNotIn("preprocessing_sort_ns", meta)
        self.assertFalse((path/"trials.csv").exists())
        with (path/"counts.csv").open(newline="") as f:
            data = list(csv.DictReader(f))
        self.assertEqual(len(data), 12)
        for row in data:
            self.assertEqual(int(row["key_comparisons"]), {"linear_search": 1, "binary_search": 4, "exponential_search": 2}[row["algorithm"]])
            self.assertEqual(row["actual_position"], "0")
            self.assertEqual(row["correctness"], "passed")
        self.assertEqual(subprocess.run([COUNTS, "--output", str(path), "--warmups", "1"], capture_output=True).returncode, 1)
        with self.assertRaises(ValueError):
            analysis.analyze(path)

    def test_defaults_help_and_build_guard(self):
        self.assertEqual(subprocess.run([EXECUTABLE, "--list-searches"], capture_output=True, text=True).stdout.splitlines(),
                         ["linear_search", "binary_search", "exponential_search"])
        self.assertEqual(subprocess.run([EXECUTABLE, "--help"], capture_output=True).returncode, 0)
        path = self.root/"default"
        self.assertEqual(self.cli(path, "--size", "0").returncode, 0)
        self.assertEqual(json.loads((path/"run.json").read_text())["algorithms"], ["linear_search"])
        meta = json.loads((path/"run.json").read_text())
        performance = self.root/"guard"
        result = subprocess.run([EXECUTABLE, "--output", str(performance), "--size", "0", "--queries", "2"], capture_output=True)
        self.assertEqual(result.returncode, 0 if meta["build_type"] == "Release" and not meta["sanitizers"] else 1)

    def test_matrix_completion_validation_and_safety(self):
        path = self.root/"matrix"
        command = [sys.executable, str(ROOT/"scripts/run_search_matrix.py"), "--binary", EXECUTABLE,
                   "--output", str(path), "--sizes", "0,1,33", "--queries", "4", "--repetitions", "1",
                   "--warmups", "0", "--validation-only"]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((path/"COMPLETE.json").read_text())["runs"], 6)
        summary = analysis.analyze(path)
        self.assertTrue(summary["complete"])
        self.assertEqual({e["category"] for e in summary["availability"] if e["available"]}, set(analysis.CATEGORIES))
        before = {str(p.relative_to(path)): p.read_bytes() for p in path.rglob("*") if p.is_file()}
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
        self.assertEqual(before, {str(p.relative_to(path)): p.read_bytes() for p in path.rglob("*") if p.is_file()})
        for i, args in enumerate([("--sizes", "0,0"), ("--seeds", "-1"), ("--query-seeds", str(2**64)),
                                  ("--searches", "bad"), ("--categories", "bad"), ("--queries", "3"),
                                  ("--sizes", "999999999"), ("--queries", "100000", "--memory-limit-mib", "1")]):
            output = self.root/f"matrix_bad{i}"
            bad = [sys.executable, str(ROOT/"scripts/run_search_matrix.py"), "--binary", EXECUTABLE, "--output", str(output), *args]
            self.assertNotEqual(subprocess.run(bad, capture_output=True).returncode, 0)
            self.assertFalse(output.exists())

    def test_matrix_records_failed_child(self):
        if sys.platform == "win32":
            self.skipTest("executable script fixture is POSIX")
        fake = self.root/"child"
        fake.write_text('#!/usr/bin/env python3\nimport sys\nif "--list-searches" in sys.argv:\n print("linear_search\\nbinary_search\\nexponential_search")\nelse:\n sys.exit(9)\n')
        fake.chmod(0o700)
        shutil.copyfile(Path(EXECUTABLE).parent/"CMakeCache.txt", self.root/"CMakeCache.txt")
        path = self.root/"failed_matrix"
        result = subprocess.run([sys.executable, str(ROOT/"scripts/run_search_matrix.py"), "--binary", str(fake),
                                 "--output", str(path), "--sizes", "0", "--distributions", "uniform"], capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads((path/"run_000000_command.json").read_text())["exit_code"], 9)
        self.assertTrue((path/"FAILED.json").exists())
        self.assertFalse((path/"COMPLETE.json").exists())
        parsed = analysis.analyze(path, True)
        self.assertFalse(parsed["complete"])
        self.assertEqual(len(parsed["missing_runs"]), 1)


if __name__ == "__main__":
    unittest.main()
