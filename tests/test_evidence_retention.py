"""Inert graph preservation tests; no CTest, compiler, GPU or timer calls."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from cpu_gpu_evidence_io import digest
from cpu_gpu_retention import retain_evidence


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.target = self.root / 'retained'
        for name in ['subprocess.run', 'subprocess.Popen', 'os.system']:
            guard = patch(name, side_effect=AssertionError('workload forbidden'))
            guard.start()
            self.addCleanup(guard.stop)

    def put(self, name, value):
        raw = value if isinstance(value, bytes) else json.dumps(value).encode()
        p = self.source / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
        return dict(file=name, sha256=digest(raw))

    def test_nested_evidence_remains_self_contained(self):
        child = self.put('nested/command.json', {'stdout': 'observed fixture only'})
        parent = self.put('record.json', {'command': child})
        manifest = retain_evidence({'records': [parent, child]}, self.source, self.target)
        self.assertEqual(set(manifest), {'record.json', 'nested/command.json'})
        self.assertEqual((self.target / child['file']).read_bytes(), (self.source / child['file']).read_bytes())
        self.assertEqual(json.loads((self.target / 'RETAINED_SHA256.json').read_text()), manifest)

    def test_stale_nested_reference_rejected_before_writing(self):
        child = self.put('child.json', {})
        parent = self.put('parent.json', {'child': child})
        self.put('child.json', {'changed': True})
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            retain_evidence(parent, self.source, self.target)
        self.assertFalse(self.target.exists())

    def test_malformed_reference_or_json_fails_closed(self):
        for raw in [b'{', b'{"duplicate":1,"duplicate":2}']:
            ref = self.put('broken.json', raw)
            with self.assertRaises(ValueError):
                retain_evidence(ref, self.source, self.target)
        ref = self.put('valid.json', {})
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            retain_evidence(dict(ref, ignored=True), self.source, self.target)
        self.assertFalse(self.target.exists())

    def test_unsafe_path_and_alias_rejected(self):
        ref = self.put('valid.json', {})
        (self.source / 'alias.json').symlink_to('valid.json')
        for name in ['../valid.json', './valid.json', 'alias.json']:
            with self.assertRaises((ValueError, OSError)):
                retain_evidence(dict(ref, file=name), self.source, self.target)
        self.assertFalse(self.target.exists())

    def test_existing_output_never_merged_or_overwritten(self):
        ref = self.put('valid.json', {})
        self.target.mkdir()
        sentinel = self.target / 'keep'
        sentinel.write_text('historical')
        with self.assertRaises(FileExistsError):
            retain_evidence(ref, self.source, self.target)
        self.assertEqual(sentinel.read_text(), 'historical')

    def test_conflicting_reference_cannot_change_snapshot(self):
        ref = self.put('valid.json', {})
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            retain_evidence([ref, dict(ref, sha256='0' * 64)], self.source, self.target)
        self.assertFalse(self.target.exists())


if __name__ == '__main__':
    unittest.main()
