import json
from pathlib import Path
import subprocess
import sys
import unittest


EXECUTABLE = str(Path(sys.argv.pop(1)).resolve())


class MetricsCliTests(unittest.TestCase):
    def run_cli(self, *arguments):
        return subprocess.run([EXECUTABLE, *arguments], capture_output=True, text=True)

    def record(self, *arguments):
        result = self.run_cli(*arguments)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        value = json.loads(result.stdout)
        self.assertEqual(set(value), {
            "schema_version", "mode", "status", "sort_algorithm", "instrumented_implementation",
            "comparison_convention", "key_comparisons", "dataset_generator", "size", "seed",
            "distribution", "nearly_sorted_swaps", "duplicate_cardinality", "memory_sample_point",
            "process_memory"})
        self.assertEqual(value["schema_version"], 1)
        self.assertEqual(value["mode"], "sort_metrics")
        self.assertEqual(value["status"], "ok")
        self.assertEqual(value["comparison_convention"], "key_less_than_v1")
        self.assertEqual(value["dataset_generator"], "mt19937_64_v1")
        self.assertEqual(value["memory_sample_point"], "after_instrumented_sort_before_validation")
        self.assertIs(type(value["key_comparisons"]), int)
        self.assertGreaterEqual(value["key_comparisons"], 0)
        memory = value["process_memory"]
        self.assertEqual(set(memory), {"status", "metric", "scope", "unit", "method", "value", "error_code"})
        self.assertEqual(memory["metric"], "peak_rss")
        self.assertEqual(memory["scope"], "process_lifetime")
        self.assertEqual(memory["unit"], "bytes")
        self.assertIsNone(memory["error_code"])
        if sys.platform.startswith("linux"):
            self.assertEqual(memory["status"], "ok")
            self.assertEqual(memory["method"], "getrusage_ru_maxrss")
            self.assertIs(type(memory["value"]), int)
            self.assertGreaterEqual(memory["value"], 0)
            self.assertEqual(memory["value"] % 1024, 0)
        else:
            self.assertEqual(memory["status"], "unsupported")
            self.assertEqual(memory["method"], "none")
            self.assertIsNone(memory["value"])
        return value

    def test_default(self):
        value = self.record()
        self.assertEqual(value["sort_algorithm"], "std_sort")
        self.assertEqual(value["instrumented_implementation"], "std_sort_counting_less")
        for field, expected in {"size": 1000, "seed": 1729, "distribution": "uniform",
                                "nearly_sorted_swaps": 10, "duplicate_cardinality": 16}.items():
            self.assertEqual(value[field], expected)

    def test_all_sorters_distributions_and_repeated_counts(self):
        identities = {"std_sort": "std_sort_counting_less",
                      "quick_sort": "project_quick_sort_counting_less",
                      "pdq_sort": "upstream_pdqsort_branchless_counting_less",
                      "tim_sort": "upstream_gfx_timsort_counting_less",
                      "merge_sort": "project_merge_sort_counting_less"}
        for sorter, identity in identities.items():
            for distribution in ("uniform", "nearly_sorted", "reverse_sorted", "duplicate_heavy"):
                for size in (0, 1, 2, 33, 257):
                    with self.subTest(sorter=sorter, distribution=distribution, size=size):
                        args = ("--sort", sorter, "--distribution", distribution, "--size", str(size),
                                "--seed", "42", "--swaps", "3", "--distinct", "7")
                        first = self.record(*args)
                        self.assertEqual(first["key_comparisons"], self.record(*args)["key_comparisons"])
                        self.assertEqual(first["sort_algorithm"], sorter)
                        self.assertEqual(first["instrumented_implementation"], identity)
                        for field, expected in {"size": size, "seed": 42, "distribution": distribution,
                                                "nearly_sorted_swaps": 3, "duplicate_cardinality": 7}.items():
                            self.assertEqual(first[field], expected)
                        if size < 2:
                            self.assertEqual(first["key_comparisons"], 0)

    def test_manual_quicksort_equal_fixture(self):
        value = self.record("--sort", "quick_sort", "--size", "2",
                            "--distribution", "duplicate_heavy", "--distinct", "1")
        self.assertEqual(value["key_comparisons"], 7)

    def test_invalid_arguments(self):
        for args in [("--sort", "unknown"), ("--sort", "timsort"), ("--sort",),
                     ("--unknown",), ("--size",), ("--size", "-1"), ("--size", "+1"),
                     ("--size", ""), ("--size", "1x"), ("--seed", "18446744073709551616"),
                     ("--seed", " 1"), ("--swaps", "-1"), ("--distribution", "bad"),
                     ("--distinct", "0"), ("--distinct", "4294967297")]:
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertTrue(result.stderr.startswith("error: "), result.stderr)

    def test_merge_equal_fixture(self):
        value = self.record("--sort", "merge_sort", "--size", "4",
                            "--distribution", "duplicate_heavy", "--distinct", "1")
        self.assertEqual(value["key_comparisons"], 4)

    def test_radix_comparisons_unsupported(self):
        result = self.run_cli("--sort", "radix_sort", "--size", "0")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr,
                         "error: comparison counting unsupported for sorter: radix_sort (no key comparisons)\n")

    def test_repeated_options(self):
        value = self.record("--sort", "tim_sort", "--sort", "std_sort", "--size", "4", "--size", "0",
                            "--seed", "1", "--seed", "0", "--distribution", "nearly_sorted",
                            "--swaps", "9", "--swaps", "2", "--distinct", "1", "--distinct", "7")
        for field, expected in {"sort_algorithm": "std_sort", "size": 0, "seed": 0,
                                "nearly_sorted_swaps": 2, "duplicate_cardinality": 7}.items():
            self.assertEqual(value[field], expected)
        self.assertEqual(self.run_cli("--size", "bad", "--size", "0").returncode, 1)

    def test_unsigned_bounds_and_oversized_vector(self):
        value = self.record("--size", "8", "--seed", "18446744073709551615",
                            "--distribution", "duplicate_heavy", "--distinct", "4294967296")
        self.assertEqual(value["seed"], 2**64 - 1)
        self.assertEqual(value["duplicate_cardinality"], 2**32)
        result = self.run_cli("--size", str(sys.maxsize))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr.startswith("error: "))

    def test_help(self):
        result = self.run_cli("--help", "--unknown")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertIn("no timing", result.stdout)
        for sorter in ("std_sort", "quick_sort", "pdq_sort", "tim_sort", "merge_sort"):
            self.assertIn(sorter, result.stdout)
        self.assertIn("radix_sort comparison counting is unsupported", result.stdout)


if __name__ == "__main__":
    unittest.main()
