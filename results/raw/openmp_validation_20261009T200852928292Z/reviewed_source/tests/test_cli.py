import json
from pathlib import Path
import subprocess
import sys
import unittest


EXECUTABLE = str(Path(sys.argv.pop(1)).resolve())


class CliTests(unittest.TestCase):
    def run_cli(self, *arguments):
        return subprocess.run([EXECUTABLE, *arguments], capture_output=True, text=True)

    def test_default_and_reproducible_configuration(self):
        first = self.run_cli()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, self.run_cli().stdout)
        record = json.loads(first.stdout)
        self.assertEqual(record, {
            "schema_version": 1, "mode": "correctness", "status": "ok",
            "sort_algorithm": "std_sort", "search_algorithm": "std_lower_bound",
            "dataset_generator": "mt19937_64_v1", "size": 1000, "seed": 1729,
            "distribution": "uniform", "nearly_sorted_swaps": 10,
            "duplicate_cardinality": 16})

    def test_distributions_and_parameters(self):
        for distribution in ("uniform", "nearly_sorted", "reverse_sorted", "duplicate_heavy"):
            for size in (0, 1, 257):
                with self.subTest(distribution=distribution, size=size):
                    result = self.run_cli("--size", str(size), "--seed", "18446744073709551615",
                                          "--distribution", distribution, "--swaps", "3", "--distinct", "7")
                    self.assertEqual(result.returncode, 0, result.stderr)
                    record = json.loads(result.stdout)
                    self.assertEqual(record["size"], size)
                    self.assertEqual(record["seed"], 2**64 - 1)
                    self.assertEqual(record["distribution"], distribution)
                    self.assertEqual(record["nearly_sorted_swaps"], 3)
                    self.assertEqual(record["duplicate_cardinality"], 7)

    def test_invalid_arguments(self):
        cases = [("--unknown",), ("--size",), ("--size", "-1"), ("--size", "1x"),
                 ("--size", ""), ("--size", "1.5"), ("--seed", "18446744073709551616"),
                 ("--distribution", "pdqsort"), ("--distinct", "0"),
                 ("--distinct", "4294967297"), ("--swaps", "-2"),
                 ("--seed", "+1"), ("--seed", " 1"), ("--seed", "1 "),
                 ("--seed", "1e3"), ("--seed", "0x10"),
                 ("--swaps", "18446744073709551616"), ("--sort",), ("--sort", "pdqsort")]
        for arguments in cases:
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertTrue(result.stderr.startswith("error: "), result.stderr)

    def test_repeated_options_use_last_value(self):
        result = self.run_cli("--size", "12", "--size", "17", "--seed", "1", "--seed", "0",
                              "--distribution", "uniform", "--distribution", "duplicate_heavy",
                              "--swaps", "100", "--swaps", "2", "--distinct", "3", "--distinct", "4")
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        for name, value in {"size": 17, "seed": 0, "distribution": "duplicate_heavy",
                            "nearly_sorted_swaps": 2, "duplicate_cardinality": 4}.items():
            self.assertEqual(record[name], value)
        # A malformed value fails when parsed, even if a later value is valid.
        self.assertEqual(self.run_cli("--size", "bad", "--size", "0").returncode, 1)

    def test_full_cardinality_and_oversized_vector(self):
        result = self.run_cli("--size", "8", "--distinct", "4294967296",
                              "--distribution", "duplicate_heavy")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["duplicate_cardinality"], 2**32)
        # Exceeds vector<int32_t>::max_size(), so it fails before allocation.
        result = self.run_cli("--size", str(sys.maxsize))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr.startswith("error: "), result.stderr)

    def test_help(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Correctness-only", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_quicksort_selection(self):
        for distribution in ("uniform", "nearly_sorted", "reverse_sorted", "duplicate_heavy"):
            with self.subTest(distribution=distribution):
                result = self.run_cli("--sort", "quick_sort", "--distribution", distribution,
                                      "--size", "1000")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["sort_algorithm"], "quick_sort")
        result = self.run_cli("--sort", "quick_sort", "--sort", "std_sort", "--size", "0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["sort_algorithm"], "std_sort")

    def test_pdqsort_selection(self):
        for distribution in ("uniform", "nearly_sorted", "reverse_sorted", "duplicate_heavy"):
            for size in (0, 1, 24, 128, 1000):
                with self.subTest(distribution=distribution, size=size):
                    result = self.run_cli("--sort", "pdq_sort", "--distribution", distribution,
                                          "--size", str(size), "--seed", "42")
                    self.assertEqual(result.returncode, 0, result.stderr)
                    record = json.loads(result.stdout)
                    self.assertEqual(record["sort_algorithm"], "pdq_sort")
                    self.assertEqual(record["status"], "ok")
                    self.assertEqual(record["size"], size)
        result = self.run_cli("--sort", "pdq_sort", "--sort", "std_sort", "--size", "0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["sort_algorithm"], "std_sort")
        self.assertIn("pdq_sort", self.run_cli("--help").stdout)

    def test_project_integer_baselines_selection(self):
        for name in ("merge_sort", "radix_sort"):
            for distribution in ("uniform", "nearly_sorted", "reverse_sorted", "duplicate_heavy"):
                for size in (0, 1, 2, 31, 32, 33, 255, 256, 1000):
                    with self.subTest(sorter=name, distribution=distribution, size=size):
                        result = self.run_cli("--sort", name, "--distribution", distribution,
                                              "--size", str(size), "--seed", "42")
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(json.loads(result.stdout)["sort_algorithm"], name)
            result = self.run_cli("--sort", name, "--sort", "std_sort", "--size", "0")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["sort_algorithm"], "std_sort")
            self.assertIn(name, self.run_cli("--help").stdout)
        for name in ("mergesort", "radixsort", "merge_sort_typo", "radix_sort_typo"):
            self.assertEqual(self.run_cli("--sort", name).returncode, 1)

    def test_invalid_sorter_names(self):
        for name in ("", "pdqsort", "PDQSort", "pdq_sort_typo", "timsort", "TimSort", "tim_sort_typo"):
            with self.subTest(name=name):
                result = self.run_cli("--sort", name)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertTrue(result.stderr.startswith("error: unknown sorter:"), result.stderr)

    def test_timsort_selection(self):
        for distribution in ("uniform", "nearly_sorted", "reverse_sorted", "duplicate_heavy"):
            for size in (0, 1, 2, 31, 32, 33, 64, 65, 1000):
                with self.subTest(distribution=distribution, size=size):
                    result = self.run_cli("--sort", "tim_sort", "--distribution", distribution,
                                          "--size", str(size), "--seed", "42")
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
                    record = json.loads(result.stdout)
                    self.assertEqual(record["sort_algorithm"], "tim_sort")
                    self.assertEqual(record["status"], "ok")
                    self.assertEqual(record["size"], size)
        result = self.run_cli("--sort", "tim_sort", "--sort", "std_sort", "--size", "0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["sort_algorithm"], "std_sort")
        self.assertIn("tim_sort", self.run_cli("--help").stdout)


if __name__ == "__main__":
    unittest.main()
