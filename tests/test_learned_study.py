"""Synthetic analysis regressions: never launches a benchmark or subprocess."""
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import learned_study as study


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cell = dict(id='fixture', size=1000, seed=42, distribution='uniform')
        self.forbid = patch('subprocess.run', side_effect=AssertionError('workload forbidden'))
        self.forbid.start(); self.addCleanup(self.forbid.stop)
        self.encode('COMPLETE.json', dict(complete=True, rows=18, diagnostic_queries=1000))
        self.encode('run.json', dict(schema_version=1, protocol='learned_rank_v1', size=1000, seed=42, distribution='uniform',
            query_seed=2718, queries=1000, hits=500, misses=500, warmups=1, repetitions=5, radius=32,
            build_type='Release', clock='steady_clock', input_fingerprint='123', query_fingerprint='456'))
        self.encode('memory.json', dict(owned_capacity_bytes=4000, object_bytes=24))
        self.rows = []
        for phase, rounds in [('warmup', 1), ('measure', 5)]:
            for trial in range(rounds):
                self.rows.append(['learned_rank', 'build', phase, trial, 0, (trial + 1)*1000, 0, 'passed'])
                for order in range(2):
                    algorithm = study.ALGORITHMS[(trial + order) % 2]
                    self.rows.append([algorithm, 'lookup_batch', phase, trial, order, (trial + 1)*100, 1000, 'passed'])
        self.save_rows()
        with (self.root / 'diagnostics.csv').open('w', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['query_id', 'target', 'expected_position', 'actual_position', 'predicted_position', 'lower_bound_position',
                'correction_distance', 'fallback', 'learned_comparisons', 'binary_comparisons'])
            for q in range(1000): writer.writerow([q, q, q if q % 2 == 0 else '', q if q % 2 == 0 else '', q, q, 0, 'false', 4, 10])

    def encode(self, name, data): (self.root / name).write_text(json.dumps(data))
    def save_rows(self):
        with (self.root / 'trials.csv').open('w', newline='') as stream:
            writer = csv.writer(stream); writer.writerow(study.FIELDS); writer.writerows(self.rows)
    def test_valid_statistics(self):
        result = study.validate_cell(self.root, self.cell)
        lookup = next(t for t in result['timings'] if t['algorithm'] == 'binary_search')
        self.assertEqual(lookup['median'], 300); self.assertEqual(lookup['mean'], 300)
        self.assertAlmostEqual(lookup['sample_sd'], 158.113883008419)
        self.assertEqual((lookup['minimum'], lookup['maximum'], lookup['n']), (100, 500, 5))
    def test_missing(self):
        self.rows.pop(); self.save_rows()
        with self.assertRaisesRegex(ValueError, 'missing trials'): study.validate_cell(self.root, self.cell)
    def test_duplicate(self):
        self.rows[-1] = self.rows[-2]; self.save_rows()
        with self.assertRaisesRegex(ValueError, 'duplicate'): study.validate_cell(self.root, self.cell)
    def test_failed(self):
        self.rows[-1][-1] = 'failed'; self.save_rows()
        with self.assertRaisesRegex(ValueError, 'failed/unknown'): study.validate_cell(self.root, self.cell)
    def test_wrong_identity(self):
        with self.assertRaisesRegex(ValueError, 'configuration mismatch'): study.validate_cell(self.root, dict(self.cell, seed=43))
    def test_invalid_time(self):
        self.rows[-1][5] = '-1'; self.save_rows()
        with self.assertRaisesRegex(ValueError, 'numeric'): study.validate_cell(self.root, self.cell)
    def test_wrong_order(self):
        self.rows[-1][4] = 7; self.save_rows()
        with self.assertRaisesRegex(ValueError, 'order'): study.validate_cell(self.root, self.cell)
    def test_interrupted(self):
        self.encode('FAILED.json', dict(error='interrupted'))
        with self.assertRaisesRegex(ValueError, 'failed configuration'): study.validate_cell(self.root, self.cell)
    def test_hit_ratio(self):
        text = (self.root / 'diagnostics.csv').read_text().replace('0,0,0,0,0,0,0,false', '0,0,,,0,0,0,false')
        (self.root / 'diagnostics.csv').write_text(text)
        with self.assertRaisesRegex(ValueError, 'ratio'): study.validate_cell(self.root, self.cell)


if __name__ == '__main__': unittest.main()
