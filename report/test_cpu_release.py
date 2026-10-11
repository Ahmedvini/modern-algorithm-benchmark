"""CPU release reporting regressions; no native execution or timing trials."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import generate
from verify_cpu import seed_statistics, json_value


class CPUReleaseTests(unittest.TestCase):
    def setUp(self):
        for name in ['subprocess.run','subprocess.Popen','os.system']:
            p=patch(name,side_effect=AssertionError('no workload execution'))
            p.start();self.addCleanup(p.stop)

    def rows(self):
        return [dict(seed=s,median_ns=m,min_ns=1,successful_trials=5,failed_trials=0,
                     missing_measured_trials=0,run_complete=True) for s,m in [(1,10),(2,20),(3,60)]]

    def test_median_is_not_minimum_or_mean(self):
        value=seed_statistics(self.rows(),[1,2,3])
        self.assertEqual(value['median_of_seed_medians_ns'],20)
        self.assertEqual(value['min_seed_median_ns'],10)
        self.assertEqual(value['mean_of_seed_medians_ns'],30)
        self.assertEqual(value['max_seed_median_ns'],60)

    def test_json_tuple_normalization_preserves_numeric_values(self):
        self.assertEqual(json_value({'build_identity':('GNU','13.3.0'), 'median':20}),
                         {'build_identity':['GNU','13.3.0'], 'median':20})

    def test_sample_standard_deviation(self):
        self.assertAlmostEqual(seed_statistics(self.rows(),[1,2,3])['sample_stdev_of_seed_medians_ns'],26.457513110645905)

    def test_missing_seed_rejected(self):
        with self.assertRaisesRegex(ValueError,'seed coverage'):seed_statistics(self.rows()[:-1],[1,2,3])

    def test_duplicate_seed_rejected(self):
        rows=self.rows();rows[2]['seed']=2
        with self.assertRaisesRegex(ValueError,'seed coverage'):seed_statistics(rows,[1,2,3])

    def test_failed_missing_or_incomplete_dataset_rejected(self):
        for field,value in [('failed_trials',1),('missing_measured_trials',1),('run_complete',False),('successful_trials',4)]:
            rows=self.rows();rows[0][field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'failed/incomplete'):seed_statistics(rows,[1,2,3])

    def test_inputs_are_cpu_only(self):
        paths=generate.input_paths(Path('/evidence'),Path('/learned'),Path('/metrics'))
        self.assertEqual(set(paths),{'sort1m','cpu','openmp','learned','metrics','scale10','scale100'})
        self.assertTrue(all(not any(word in str(p) for word in ['cuda','gpu','cub']) for p in paths.values()))

    def test_existing_output_preserved_before_any_input_work(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);marker=root/'retained';marker.write_text('immutable')
            with patch.object(generate,'verify',side_effect=AssertionError('must reject before analysis')):
                with self.assertRaises(FileExistsError):generate.generate(root,root,root,root)
            self.assertEqual(marker.read_text(),'immutable')


if __name__=='__main__':unittest.main()
