import csv
import json
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest

BINARY = str(Path(sys.argv.pop(1)).resolve())
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import analyze_structure_results as analysis
from analyze_results import summarize_samples


class StructureFrameworkTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root = Path(temp.name)

    def cli(self, path, *args):
        return subprocess.run([BINARY, '--output', str(path), '--validation-only', *args], capture_output=True, text=True)

    def bundle(self, name='run', *args):
        path = self.root/name
        result = self.cli(path, '--size', '31', '--queries', '8', '--structure', 'all', '--repetitions', '2', '--warmups', '1', *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return path

    def rewrite_rows(self, path, rows):
        with (path/'trials.csv').open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=analysis.FIELDS);writer.writeheader();writer.writerows(rows)

    def test_schema_escaping_and_counts(self):
        path = self.bundle('schema', '--run-id', 'structure, "quote"\nline')
        rows = analysis.rows(path/'trials.csv', analysis.FIELDS)
        self.assertEqual(len(rows), 135)
        self.assertEqual({r['run_id'] for r in rows}, {'structure, "quote"\nline'})
        summary = analysis.analyze(path)
        self.assertTrue(summary['complete']);self.assertEqual(len(summary['groups']), 45)
        for group in summary['groups']:
            self.assertEqual((group['successful_trials'], group['failed_trials'], group['missing_measured_trials']), (2, 0, 0))
            self.assertEqual('median_normalized_ns_per_query' in group, group['operation'] == 'lookup')
        self.assertEqual(sum(r['operation'] == 'build' for r in rows), 15)
        self.assertEqual(len({r['insertion_hash_fnv1a64'] for r in rows}), 1)

    def test_reproducibility_source_order_and_duplicates(self):
        prepared = []
        for i, dist in enumerate(('uniform', 'sorted', 'reverse_sorted', 'nearly_sorted', 'duplicate_heavy')):
            args = ('--distribution', dist, '--seed', '18446744073709551615', '--query-seed', '42', '--structure-seed', '42')
            a = self.bundle(f'a{i}', *args);b = self.bundle(f'b{i}', *args)
            self.assertEqual((a/'queries.csv').read_bytes(), (b/'queries.csv').read_bytes())
            ma, mb = (json.loads((p/'run.json').read_text()) for p in (a,b))
            self.assertEqual(ma['insertion_hash_fnv1a64'], mb['insertion_hash_fnv1a64'])
            self.assertTrue(analysis.analyze(a)['complete']);prepared.append(ma['input_hash_fnv1a64'])
        self.assertEqual(len(set(prepared[:4])), 1)
        equal = self.bundle('equal', '--distribution', 'duplicate_heavy', '--distinct', '1')
        queries = analysis.rows(equal/'queries.csv', analysis.QUERY_FIELDS)
        self.assertTrue(all(q['expected_position'] == '0' for q in queries if q['expected_hit'] == 'true'))
        self.assertEqual(json.loads((equal/'run.json').read_text())['unique_keys'], 1)
        empty = self.bundle('empty', '--size', '0')
        self.assertEqual(len(analysis.analyze(empty)['groups']), 10)
        singleton = self.bundle('singleton', '--size', '1', '--categories', 'miss_between')
        summary = analysis.analyze(singleton)
        self.assertEqual(len(summary['groups']), 5)  # construction still measured
        self.assertTrue(summary['availability'][0]['reason'])

    def test_registry_defaults_help_and_build_guard(self):
        result = subprocess.run([BINARY, '--list-structures'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0);self.assertEqual(result.stdout.splitlines(), list(analysis.ALGORITHMS))
        result = subprocess.run([BINARY, '--help', '--bad'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0);self.assertIn('--structure-seed', result.stdout)
        path = self.root/'default';self.assertEqual(self.cli(path, '--size', '0', '--queries', '2').returncode, 0)
        self.assertEqual(json.loads((path/'run.json').read_text())['algorithms'], ['skip_list'])
        real = self.root/'guard'
        result = subprocess.run([BINARY, '--output', str(real), '--size', '0', '--queries', '2'], capture_output=True, text=True)
        if json.loads((path/'run.json').read_text())['build_type'] == 'Release':
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertEqual(result.returncode, 1);self.assertFalse(real.exists())

    def test_invalid_arguments(self):
        invalid = [('--size','-1'),('--size','+1'),('--size',str(2**64)),('--seed','bad'),('--structure-seed','-1'),
                   ('--structure-seed',str(2**64)),('--query-seed','+1'),('--queries','0'),('--queries','3'),
                   ('--queries','100002'),('--repetitions','0'),('--repetitions','10001'),('--warmups','1001'),
                   ('--structure','bad'),('--structure','skip_list,skip_list'),('--structure','skip_list,'),
                   ('--categories','bad'),('--categories','hit_first,hit_first'),('--distribution','bad'),
                   ('--distinct','0'),('--distinct',str(2**32+1)),('--size','100000000'),('--memory-limit-mib','0'),
                   ('--size','10000','--memory-limit-mib','1','--queries','2'),('--swaps','10000001'),('--size',),('--bad',)]
        for i, args in enumerate(invalid):
            path = self.root/f'invalid{i}';result = self.cli(path, *args)
            self.assertEqual(result.returncode, 1, args);self.assertTrue(result.stderr.startswith('error:'));self.assertFalse(path.exists())

    def test_output_safety(self):
        path = self.bundle();before = {p.name:p.read_bytes() for p in path.iterdir()}
        self.assertEqual(self.cli(path).returncode, 1);self.assertEqual(before, {p.name:p.read_bytes() for p in path.iterdir()})
        f = self.root/'file';f.write_text('preserve');self.assertEqual(self.cli(f).returncode, 1);self.assertEqual(f.read_text(), 'preserve')
        self.assertEqual(self.cli(self.root/'absent/child').returncode, 1)
        link = self.root/'link';link.symlink_to(path, target_is_directory=True)
        self.assertEqual(self.cli(link).returncode, 1);self.assertEqual(before, {p.name:p.read_bytes() for p in path.iterdir()})

    def test_known_statistics(self):
        path = self.bundle('synthetic', '--structure', 'skip_list', '--categories', 'hit_first', '--warmups', '0', '--repetitions', '3')
        rows = analysis.rows(path/'trials.csv', analysis.FIELDS)
        for i, row in enumerate(rows):
            row['elapsed_ns'] = str((i//2+1)*10)
        self.rewrite_rows(path, rows)
        for group in analysis.analyze(path)['groups']:
            self.assertEqual([group[k+'_ns'] for k in ('median','mean','stdev','min','max')], [20,20,10,10,30])
        self.assertIsNone(summarize_samples([10])['stdev_ns'])

    def test_failed_and_missing_records(self):
        path = self.bundle('partial', '--warmups', '0')
        data = analysis.rows(path/'trials.csv', analysis.FIELDS);self.rewrite_rows(path, data[:-1]);(path/'COMPLETE.json').unlink()
        with self.assertRaises(ValueError): analysis.analyze(path)
        summary = analysis.analyze(path, True)
        self.assertFalse(summary['complete']);self.assertEqual(sum(g['missing_measured_trials'] for g in summary['groups']), 1)
        data[-1].update(status='error', correctness='not_checked', elapsed_ns='', error='synthetic failure')
        self.rewrite_rows(path, data);(path/'FAILED.json').write_text('{"complete":false}')
        summary = analysis.analyze(path, True);self.assertEqual(sum(g['failed_trials'] for g in summary['groups']), 1)
        out = self.root/'partial.json'
        result = subprocess.run([sys.executable, str(ROOT/'scripts/analyze_structure_results.py'), str(path), '--output', str(out), '--allow-incomplete'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1);self.assertTrue(out.exists())

    def test_malformed_records_and_queries(self):
        for i, (field, value) in enumerate([('operation','wrong'),('elapsed_unit','ms'),('execution_order','99'),('elapsed_ns','-1'),('input_hash_fnv1a64','0')]):
            path = self.bundle(f'bad{i}');rows = analysis.rows(path/'trials.csv', analysis.FIELDS);rows[0][field] = value;self.rewrite_rows(path, rows)
            with self.assertRaises(ValueError): analysis.analyze(path, True)
        path = self.bundle('query');query = analysis.rows(path/'queries.csv', analysis.QUERY_FIELDS);query[0]['target'] = str(2**31)
        with (path/'queries.csv').open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=analysis.QUERY_FIELDS);writer.writeheader();writer.writerows(query)
        with self.assertRaises(ValueError): analysis.analyze(path)
        path = self.bundle('schema');(path/'trials.csv').write_text('wrong,columns\n')
        with self.assertRaises(ValueError): analysis.analyze(path)

    def test_summary_regeneration_and_exclusive_output(self):
        path = self.bundle();before = {p.name:p.read_bytes() for p in path.iterdir()}
        a, b = self.root/'a.json', self.root/'b.json'
        for out in (a,b):
            result = subprocess.run([sys.executable, str(ROOT/'scripts/analyze_structure_results.py'), str(path), '--output', str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(a.read_bytes(), b.read_bytes());self.assertEqual(before, {p.name:p.read_bytes() for p in path.iterdir()})
        result = subprocess.run([sys.executable, str(ROOT/'scripts/analyze_structure_results.py'), str(path), '--output', str(a)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1);self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_matrix_completion_missing_and_child_failure(self):
        path = self.root/'matrix'
        command = [sys.executable, str(ROOT/'scripts/run_structure_matrix.py'), '--binary', BINARY, '--output', str(path), '--sizes', '0,64', '--distributions', 'uniform', '--queries', '8', '--repetitions', '2', '--warmups', '1', '--validation-only']
        result = subprocess.run(command, capture_output=True, text=True);self.assertEqual(result.returncode, 0, result.stderr)
        summary = analysis.analyze(path);self.assertTrue(summary['complete']);self.assertEqual(len(summary['groups']), 55)
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
        (path/'COMPLETE.json').unlink();(path/'run_000001/run.json').unlink()
        partial = analysis.analyze(path, True);self.assertFalse(partial['complete']);self.assertEqual(len(partial['missing_runs']), 1)
        stub = self.root/'stub';stub.write_text('#!/usr/bin/env python3\nimport sys\nif "--list-structures" in sys.argv: print("skip_list")\nelse: sys.exit(9)\n');stub.chmod(0o700)
        shutil.copyfile(Path(BINARY).parent/'CMakeCache.txt', self.root/'CMakeCache.txt')
        failed = self.root/'failed'
        result = subprocess.run([sys.executable, str(ROOT/'scripts/run_structure_matrix.py'), '--binary', str(stub), '--output', str(failed), '--sizes', '0', '--queries', '8'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads((failed/'run_000000_command.json').read_text())['exit_code'], 9)
        self.assertTrue((failed/'FAILED.json').exists());self.assertFalse((failed/'COMPLETE.json').exists())
        self.assertEqual(len(analysis.analyze(failed, True)['missing_runs']), 2)

    def test_matrix_invalid_configuration(self):
        for i, args in enumerate([('--sizes','0,0'),('--seeds','-1'),('--query-seeds',str(2**64)),
                                 ('--structure-seed','bad'),('--structures','bad'),('--categories','bad'),
                                 ('--queries','3'),('--size','33'),('--sizes','999999999'),
                                 ('--queries','100000','--memory-limit-mib','1')]):
            output = self.root/f'matrix_bad{i}'
            command = [sys.executable, str(ROOT/'scripts/run_structure_matrix.py'), '--binary', BINARY, '--output', str(output), *args]
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
