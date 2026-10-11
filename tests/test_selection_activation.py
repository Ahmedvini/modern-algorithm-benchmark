"""Inert source-review activation checks; never invokes discovery or tests."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import non_timing_tests as selector


class ActivationTests(unittest.TestCase):
    def setUp(self):
        self.manifest = selector.load_manifest()
        self.forbid = patch('subprocess.run', side_effect=AssertionError('discovery forbidden'))
        self.forbid.start(); self.addCleanup(self.forbid.stop)

    def test_approved_names_and_scope_unchanged(self):
        base = json.loads((selector.ROOT / 'docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())
        for key in ['tests', 'cpu_build_tests', 'cuda_additional_tests', 'build_metadata']:
            self.assertEqual(self.manifest[key], base[key])
        self.assertEqual(sum(e['classification'] == 'cpu_correctness' and not e.get('diagnostic_only') for e in base['tests'].values()), 19)
        self.assertFalse(self.manifest['full_study_eligible'])

    def test_add_remove_and_changed_source_rejected(self):
        for kind in ['add', 'remove', 'change']:
            source = dict(self.manifest['reviewed_source_sha256'])
            key = next(iter(source))
            if kind == 'add': source['scripts/unreviewed.py'] = 'a' * 64
            elif kind == 'remove': source.pop(key)
            else: source[key] = 'a' * 64
            with self.subTest(kind=kind), patch.object(selector, 'source_manifest', return_value=source):
                with self.assertRaisesRegex(ValueError, 'source snapshot changed'): selector.load_manifest()

    def test_manifest_cannot_change_approved_command_or_selection(self):
        original = selector.strict_json
        for key in ['tests', 'cpu_build_tests', 'cuda_additional_tests', 'build_metadata']:
            changed = copy.deepcopy(self.manifest); changed[key] = {} if isinstance(changed[key], dict) else []
            def parse(text):
                value = original(text)
                return changed if value.get('schema_version') == 5 else value
            with self.subTest(key=key), patch.object(selector, 'strict_json', side_effect=parse):
                with self.assertRaisesRegex(ValueError, 'changed approved selection'): selector.load_manifest()


if __name__ == '__main__': unittest.main()
