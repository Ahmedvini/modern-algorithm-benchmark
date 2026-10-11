import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    "environment", Path(__file__).resolve().parents[1] / "scripts/capture_environment.py")
environment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(environment)


class EnvironmentTests(unittest.TestCase):
    def test_manifest_round_trip_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "raw" / "manifest.json"
            original = {"schema_version": 1, "status": "not run", "command": "a\nb"}
            environment.write_manifest(output, original)
            saved_bytes = output.read_bytes()
            self.assertEqual(json.loads(saved_bytes), original)
            with self.assertRaises(FileExistsError):
                environment.write_manifest(output, {"changed": True})
            self.assertEqual(output.read_bytes(), saved_bytes)

    def test_unavailable_probe_is_explicit(self):
        result = environment.probe(["mab_nonexistent_executable_1729"])
        self.assertIsNone(result["returncode"])
        self.assertIn("error", result)

    def test_invalid_build_cache_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            build_dir = Path(directory)
            (build_dir / "CMakeCache.txt").write_text("CMAKE_BUILD_TYPE:STRING=Release\n")
            with self.assertRaisesRegex(ValueError, "compiler"):
                environment.capture(build_dir, "test")


if __name__ == "__main__":
    unittest.main()
