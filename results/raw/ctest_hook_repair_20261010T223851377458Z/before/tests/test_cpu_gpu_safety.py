#!/usr/bin/env python3
"""Offline provenance and selection regressions. No sorting timing or GPU calls."""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import cpu_gpu_provenance as provenance
import non_timing_tests as selector
from cpu_gpu_protocol import load_protocol, verify_source_extension


def discovery(build, gpu=False):
    manifest = selector.load_manifest()
    names = manifest['cpu_build_tests'] + (manifest['cuda_additional_tests'] if gpu else [])
    return dict(kind='ctestInfo', version=dict(major=1, minor=0), tests=[dict(
        name=n, command=selector.expected_command(manifest['tests'][n]['command'], build), properties=[])
        for n in names])


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.model = load_protocol()
        self.source = verify_source_extension(self.model)

    def test_valid_current_source_matches_independent_frozen_anchors(self):
        provenance.validate_retained_source(self.source, self.model)
        expected = provenance.trusted_source_anchors(self.model)
        self.assertEqual(expected['src/cuda/cub_sort.cu'],
                         self.model['source_at_freeze_sha256']['src/cuda/cub_sort.cu'])

    def test_changed_adapter_claim_rejected_independent_of_other_consistent_maps(self):
        altered = copy.deepcopy(self.source)
        altered['current_source_sha256']['src/cuda/cub_sort.cu'] = '0'*64
        self.assertEqual(altered['current_source_sha256'], copy.deepcopy(altered['current_source_sha256']))
        with self.assertRaisesRegex(ValueError, 'retained protected source.*src/cuda/cub_sort.cu'):
            provenance.validate_retained_source(altered, self.model)

    def test_legacy_code_only_maps_still_verify_documentation_independently(self):
        path=ROOT/'docs/CUDA_TIMING_PROTOCOL_v1.md'
        self.assertNotIn(str(path.relative_to(ROOT)),self.source['current_source_sha256'])
        original=provenance.sha
        with mock.patch.object(provenance,'sha',side_effect=lambda p: '0'*64 if p==path else original(p)),\
             self.assertRaisesRegex(ValueError,'trusted documentation anchor'):
            provenance.validate_retained_source(self.source,self.model)

    def test_pin_and_cmake_claims_rejected(self):
        for path in ['third_party/cub/UPSTREAM.json', 'CMakeLists.txt', 'src/cuda/cub_timing.cu']:
            with self.subTest(path=path):
                altered = copy.deepcopy(self.source); altered['current_source_sha256'][path] = '0'*64
                with self.assertRaisesRegex(ValueError, 'retained protected source'):
                    provenance.validate_retained_source(altered, self.model)

    def test_missing_or_malformed_model_anchor_fails_closed(self):
        for value in [None, {}, [], {'src/cuda/cub_sort.cu': 'not-a-digest'}]:
            with self.subTest(value=value):
                model = copy.deepcopy(self.model); model['source_at_freeze_sha256'] = value
                with self.assertRaises(ValueError): provenance.trusted_source_anchors(model)
        model = copy.deepcopy(self.model); model['source_at_freeze_sha256'].pop('src/cuda/cub_sort.cu')
        with self.assertRaises(ValueError): provenance.trusted_source_anchors(model)

    def test_mutating_model_and_retained_maps_together_does_not_redefine_trust(self):
        model = copy.deepcopy(self.model); source = copy.deepcopy(self.source)
        model['source_at_freeze_sha256']['src/cuda/cub_sort.cu'] = '0'*64
        source['current_source_sha256']['src/cuda/cub_sort.cu'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'model differs from trusted'):
            provenance.validate_retained_source(source, model)

    def test_trusted_freeze_missing_changed_or_malformed(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'freeze.json'
            for text in [None, '{}', '{', '{"files_sha256":{},"files_sha256":{}}']:
                with self.subTest(text=text), mock.patch.object(provenance, 'FREEZE', path):
                    if text is not None: path.write_text(text)
                    with self.assertRaisesRegex(ValueError, 'trusted freeze identity'): provenance.trusted_source_anchors(self.model)

    def test_cmake_exception_root_cannot_be_redefined(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'review.json'; path.write_text('{}')
            with mock.patch.object(provenance, 'CMAKE_REVIEW', path), self.assertRaisesRegex(ValueError, 'trusted CMake review'):
                provenance.trusted_source_anchors(self.model)
        altered = copy.deepcopy(self.source); altered['cmake_review_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'CMake exception'): provenance.validate_retained_source(altered, self.model)

    def test_retained_map_malformed_missing_and_ambiguous_paths(self):
        for path, digest in [('src/cuda/cub_sort.cu', None), ('src/cuda/cub_sort.cu', 'xyz'),
                             ('src/./cuda/cub_sort.cu', '0'*64), ('../cub_sort.cu', '0'*64)]:
            with self.subTest(path=path, digest=digest):
                altered = copy.deepcopy(self.source); altered['current_source_sha256'][path] = digest
                with self.assertRaises(ValueError): provenance.validate_retained_source(altered, self.model)
        altered = copy.deepcopy(self.source); altered['current_source_sha256'].pop('src/cuda/cub_sort.cu')
        with self.assertRaises(ValueError): provenance.validate_retained_source(altered, self.model)

    def test_duplicate_json_fields_and_nonfinite_data_are_rejected(self):
        for text in ['{"a":"x","a":"y"}', '{"a":NaN}', '{"a":Infinity}']:
            with self.subTest(text=text), self.assertRaises(ValueError): provenance.strict_json(text)

    def test_exact_previously_accepted_full_matrix_reproducer(self):
        source = ROOT/'tests/fixtures/cpu_gpu_provenance_reproducer.py'
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                         '1588c1ce06ded80b91d9806673b883effb7c98b0ace8d1eadb5c04688072142c')
        with tempfile.TemporaryDirectory() as d:
            # The exact script uses its own directory for output; never run the archived copy.
            path = Path(d)/'reproducer.py'; path.write_bytes(source.read_bytes())
            result = subprocess.run([sys.executable, '-B', str(path)], cwd=ROOT,
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((Path(d)/'FULL_ANALYSIS_PROBE.json').read_text())
            self.assertTrue(report['baseline_accepted']); self.assertTrue(report['protected_source_change_rejected'])
            self.assertEqual(report['synthetic_measured_records'], 1200)
            self.assertEqual(report['synthetic_warmup_records'], 240)
            self.assertEqual((report['sorting_calls'], report['actual_gpu_calls']), (0, 0))


class SelectorTests(unittest.TestCase):
    def setUp(self):
        self.build = ROOT/'build/UNEXECUTED_SAFETY_FIXTURE'
        self.discovered = discovery(self.build)

    def test_exact_cpu_list_excludes_all_timing_tests_and_known_32768_case(self):
        with mock.patch.object(selector.subprocess, 'run', side_effect=AssertionError('must not execute')):
            plan = selector.select_tests(self.discovered, self.build)
        self.assertEqual(plan['selected_count'], 19)
        expected = {'structures','searching','baselines','environment_manifest','cuda_preflight',
            'cuda_benchmark_analysis','cuda_sort_handoff','datasets','cli','quicksort','pdqsort','timsort',
            'mergesort','radixsort','comparisons','memory','memory_unsupported','metrics_cli','cpu_gpu_comparison_framework'}
        self.assertEqual(set(plan['selected']), expected)
        expression = plan['ctest_argv'][-1]
        for name in ['parallel_mergesort','timing','comparison_engine','benchmark_framework','parallel_framework',
                     'experiment_pipeline','search_timing','search_framework','structure_timing','structure_framework']:
            self.assertNotIn(name, plan['selected']); self.assertIsNone(re.fullmatch(expression, name))
        self.assertFalse(plan['tests_executed']); self.assertFalse(plan['full_protocol_prerequisites'])

    def test_gpu_correctness_requires_explicit_opt_in_and_never_includes_gpu_benchmark(self):
        data = discovery(self.build, gpu=True)
        cpu = selector.select_tests(data, self.build)
        self.assertEqual(cpu['selected_count'], 19)
        selected = selector.select_tests(data, self.build, allow_gpu=True)
        self.assertEqual(selected['selected_count'], 21)
        self.assertTrue({'cuda_runtime_smoke','cuda_sorting'} <= set(selected['selected']))
        self.assertNotIn('cuda_benchmark_gpu_framework', selected['selected'])
        with self.assertRaises(ValueError): selector.select_tests(self.discovered, self.build, allow_gpu=True)

    def test_unknown_missing_duplicate_and_malformed_discovery_fail_closed(self):
        for change in ['unknown','missing','duplicate','invalid']:
            data = copy.deepcopy(self.discovered)
            if change=='unknown': data['tests'].append(dict(name='new_correctness_test', command=['unknown']))
            if change=='missing': data['tests'].pop()
            if change=='duplicate': data['tests'].append(copy.deepcopy(data['tests'][0]))
            if change=='invalid': data['version'] = {'major':2,'minor':0}
            with self.subTest(change=change), self.assertRaises(ValueError): selector.select_tests(data, self.build)

    def test_safe_name_cannot_mask_timing_command_or_arguments(self):
        for command in [[str(self.build/'test_parallel_mergesort')],
                        [sys.executable,str(ROOT/'tests/test_cuda_benchmark.py'),str(self.build/'cuda_sort_benchmark')],
                        [str(self.build/'test_datasets'),'--unreviewed']]:
            data = copy.deepcopy(self.discovered)
            next(t for t in data['tests'] if t['name']=='datasets')['command'] = command
            with self.subTest(command=command), self.assertRaises(ValueError): selector.select_tests(data, self.build)

    def test_fixture_dependencies_environment_and_missing_commands_rejected(self):
        for property_name in ['FIXTURES_REQUIRED','FIXTURES_SETUP','DEPENDS','ENVIRONMENT','ENVIRONMENT_MODIFICATION']:
            data = copy.deepcopy(self.discovered)
            next(t for t in data['tests'] if t['name']=='datasets')['properties'] = [dict(name=property_name,value='timing')]
            with self.subTest(property_name=property_name), self.assertRaises(ValueError): selector.select_tests(data,self.build)
        data = copy.deepcopy(self.discovered); next(t for t in data['tests'] if t['name']=='datasets').pop('command')
        with self.assertRaises(ValueError): selector.select_tests(data,self.build)

    def test_source_snapshot_change_requires_reclassification(self):
        with tempfile.TemporaryDirectory() as d:
            manifest = selector.load_manifest(); manifest['reviewed_source_sha256']['tests/test_parallel_mergesort.cpp'] = '0'*64
            path = Path(d)/'manifest.json'; path.write_text(json.dumps(manifest))
            with mock.patch.object(selector,'MANIFEST',path), self.assertRaisesRegex(ValueError,'source snapshot changed'):
                selector.select_tests(self.discovered,self.build)

    def test_even_a_relabelled_known_timing_entry_point_is_forbidden(self):
        manifest = selector.load_manifest(); manifest['tests']['parallel_mergesort']['classification'] = 'cpu_correctness'
        with mock.patch.object(selector,'load_manifest',return_value=manifest), self.assertRaisesRegex(ValueError,'timing entry point'):
            selector.select_tests(self.discovered,self.build)

    def test_unclassified_manifest_entry_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            manifest = selector.load_manifest(); manifest['tests']['datasets']['classification'] = 'unknown'
            path = Path(d)/'manifest.json'; path.write_text(json.dumps(manifest))
            with mock.patch.object(selector,'MANIFEST',path), self.assertRaisesRegex(ValueError,'unclassified'):
                selector.select_tests(self.discovered,self.build)

    def test_selection_is_saved_before_execution_callback(self):
        calls=[]
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)
            def call(name,argv,timeout):
                calls.append((name,argv))
                if name.endswith('_discovery'):
                    self.assertIn('-N',argv); self.assertIn('--show-only=json-v1',argv)
                    return dict(stdout=json.dumps(self.discovered))
                self.assertTrue((output/'fixture_selection.json').exists())
                self.assertIn('-R',argv); self.assertIsNone(re.fullmatch(argv[-1],'parallel_mergesort'))
                return dict(stdout='100% tests passed, 0 tests failed out of 19\n')
            selector.selected_ctest(call,output,'fixture',self.build)
        self.assertEqual([name for name,_ in calls],['fixture_discovery','fixture'])

    def test_bad_discovery_never_reaches_execution_callback(self):
        calls=[]; data=copy.deepcopy(self.discovered);data['tests'].append(dict(name='unclassified'))
        def call(name,argv,timeout): calls.append(name);return dict(stdout=json.dumps(data))
        with tempfile.TemporaryDirectory() as d, self.assertRaises(ValueError):
            selector.selected_ctest(call,Path(d),'fixture',self.build)
        self.assertEqual(calls,['fixture_discovery'])

    def test_non_timing_prerequisites_cannot_authorize_a_study(self):
        from run_cpu_gpu_pilot import validate_prerequisites
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'PREREQUISITES.json'
            path.write_text(json.dumps(dict(protocol='cpu_gpu_comparison_v1',complete=True,
                validation_scope='non_timing_correctness_v1',study_eligible=False)))
            with self.assertRaisesRegex(ValueError,'non-timing subset'):
                validate_prerequisites(path,Path('never'),Path('never'),load_protocol())


if __name__ == '__main__':
    unittest.main()
