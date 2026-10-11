#!/usr/bin/env python3
"""INERT fixtures only: all real subprocess entry points are blocked in setUp.

No binary is created or executed. The two runner callbacks below only return
literal JSON/text. Even the CLI's subprocess path is replaced by a Python fake.
"""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import non_timing_tests as selector
import ctest_build_guard as guard
from ctest_fixture import write_fixture

EXPECTED = ['baselines','cli','comparisons','cpu_gpu_comparison_framework',
    'cuda_benchmark_analysis','cuda_preflight','cuda_sort_handoff','datasets',
    'environment_manifest','memory','memory_unsupported','mergesort','metrics_cli',
    'pdqsort','quicksort','radixsort','searching','structures','timsort']


class BuildGuardTests(unittest.TestCase):
    def setUp(self):
        self.stack = contextlib.ExitStack(); self.addCleanup(self.stack.close)
        for entry in ['run','Popen','call','check_call','check_output']:
            self.stack.enter_context(mock.patch('subprocess.'+entry,
                side_effect=AssertionError('real subprocess forbidden')))
        self.stack.enter_context(mock.patch('os.system', side_effect=AssertionError('shell forbidden')))
        self.stack.enter_context(mock.patch.dict(os.environ, {}, clear=True))
        self.temp = self.stack.enter_context(tempfile.TemporaryDirectory())
        self.build = Path(self.temp)/'build'; self.output = Path(self.temp)/'evidence'; self.output.mkdir()
        self.discovery = write_fixture(self.build)
        self.file = self.build/'CTestTestfile.cmake'
        self.original = self.file.read_text(); self.calls = []

    def fake(self, name, argv, timeout):
        self.calls.append((name, argv))
        if name.endswith('_discovery'):
            return dict(stdout=json.dumps(self.discovery), exit_code=0)
        return dict(stdout='100% tests passed, 0 tests failed out of 19\n', exit_code=0)

    def assert_rejected_before_discovery(self):
        with self.assertRaises((ValueError, OSError)):
            selector.selected_ctest(self.fake, self.output, 'inert', self.build)
        self.assertEqual(self.calls, [])

    def test_clean_reviewed_fixture_preserves_exact_19_plan(self):
        plan = selector.select_tests(self.discovery, self.build)
        self.assertEqual(plan['selected'], EXPECTED)
        self.assertNotIn('parallel_mergesort', plan['selected'])
        self.assertNotIn('comparison_engine', plan['selected'])
        self.assertFalse(plan['tests_executed']); self.assertEqual(self.calls, [])

    def test_clean_fixture_runner_callbacks_are_only_python_fakes(self):
        selector.selected_ctest(self.fake, self.output, 'inert', self.build)
        self.assertEqual([x[0] for x in self.calls], ['inert_discovery','inert'])
        self.assertEqual(json.loads((self.output/'inert_selection.json').read_text())['selected'], EXPECTED)

    def test_custom_pre_and_post_hooks_and_ctest_variant_fail_before_discovery(self):
        for filename in ['CTestCustom.cmake','CTestCustom.ctest','CTestConfig.cmake']:
            for value in ['', '# inert\n', 'set(CTEST_CUSTOM_PRE_TEST "/never/executed")\n',
                          'set(CTEST_CUSTOM_POST_TEST "/never/executed")\n']:
                with self.subTest(filename=filename, value=value):
                    p=self.build/filename; p.write_text(value)
                    self.assert_rejected_before_discovery(); p.unlink()

    def test_unreviewed_include_rejected_without_reading_or_running_included_code(self):
        included=self.build/'inert.cmake';included.write_text('# inert included metadata\n')
        self.file.write_text(self.original+'include("'+str(included)+'")\n')
        self.assert_rejected_before_discovery()

    def test_exact_prior_review_inert_hook_fixture_is_rejected_before_discovery(self):
        previous=ROOT/'results/raw/cpu_gpu_repair_review_20261010T185659333607Z/UNEXECUTED_MATCHING_CTEST_METADATA'
        for name in ['CTestTestfile.cmake','CTestCustom.cmake','unreviewed.cmake']:
            (self.build/name).write_text((previous/name).read_text().replace(str(previous),str(self.build)))
        self.assert_rejected_before_discovery()

    def test_subdirs_nested_unreviewed_file_fails_closed(self):
        nested=self.build/'nested';nested.mkdir()
        (nested/'CTestTestfile.cmake').write_text('include("inert.cmake")\n')
        (nested/'inert.cmake').write_text('# inert, never interpreted\n')
        self.file.write_text(self.original+'subdirs("nested")\n')
        self.assert_rejected_before_discovery()

    def test_unreferenced_nested_metadata_and_hooks_also_rejected(self):
        nested=self.build/'nested';nested.mkdir()
        for filename in ['CTestTestfile.cmake','CTestCustom.cmake','DartConfiguration.tcl']:
            with self.subTest(filename=filename):
                p=nested/filename;p.write_text('# inert\n');self.assert_rejected_before_discovery();p.unlink()

    def test_modified_previously_reviewed_command_rejected(self):
        self.file.write_text(self.original.replace('/test_datasets"','/test_parallel_mergesort"'))
        self.assert_rejected_before_discovery()

    def test_modified_reviewed_properties_and_backtrace_rejected(self):
        for text in [self.original.replace('PROPERTIES ', 'PROPERTIES FIXTURES_REQUIRED "timing" ',1),
                     self.original.replace(';86;add_test;', ';999;add_test;',1),
                     self.original.replace('PROPERTIES ', 'PROPERTIES DEPENDS "parallel_mergesort" ',1)]:
            with self.subTest(text=text[:100]):
                self.file.write_text(text); self.assert_rejected_before_discovery()

    def test_unreadable_file_rejected_even_under_privileged_test_user(self):
        original=Path.read_bytes
        def unreadable(path):
            if path==self.file:raise PermissionError('inert unreadable fixture')
            return original(path)
        with mock.patch.object(Path,'read_bytes',unreadable):
            self.assert_rejected_before_discovery()

    def test_missing_file_and_directory_rejected(self):
        self.file.unlink();self.assert_rejected_before_discovery()
        with self.assertRaises(ValueError):selector.pre_discovery_gate(self.build/'absent')

    def test_malformed_ambiguous_and_control_flow_are_rejected(self):
        for line in ['include("unterminated)', 'execute_process(COMMAND "/never/executed")',
                     'if(TRUE)', 'subdirs(../outside)', 'add_test(datasets "${VARIABLE}")',
                     'add_test(datasets "$<TARGET_FILE:timing>")',
                     'add_test(datasets "escaped\\value")', 'add_test(datasets "a""b")',
                     '#[[\nunknown_command()\n]]', 'add_test(datasets "a")\x00']:
            with self.subTest(line=line):
                self.file.write_text(self.original+line+'\n');self.assert_rejected_before_discovery()
        self.file.write_bytes(b'\xff')
        self.assert_rejected_before_discovery()

    def test_duplicates_and_missing_declarations_rejected(self):
        for text in [self.original+self.original.splitlines()[0]+'\n',
                     '\n'.join(self.original.splitlines()[2:])]:
            with self.subTest(text=text[:100]):
                self.file.write_text(text);self.assert_rejected_before_discovery()

    def test_symlinked_metadata_and_build_rejected(self):
        real=self.build/'inert.txt';self.file.rename(real);self.file.symlink_to(real)
        self.assert_rejected_before_discovery()
        alias=Path(self.temp)/'alias';alias.symlink_to(self.build, target_is_directory=True)
        with self.assertRaises(ValueError):selector.pre_discovery_gate(alias)

    def test_ctest_environment_override_and_unreviewed_wrapper_rejected(self):
        with mock.patch.dict(os.environ, {'CTEST_TEST_ARGS':'--unreviewed'}):
            self.assert_rejected_before_discovery()
        with self.assertRaisesRegex(ValueError,'wrapper'):
            selector.selected_ctest(self.fake,self.output,'inert',self.build,prefix=['unreviewed-wrapper'])
        self.assertEqual(self.calls, [])

    def test_metadata_modified_during_fake_discovery_never_reaches_execution(self):
        def discovery(name, argv, timeout):
            result=self.fake(name,argv,timeout)
            self.file.write_text(self.original+'# modified reviewed file bytes\n')
            return result
        with self.assertRaisesRegex(ValueError,'changed during discovery'):
            selector.selected_ctest(discovery,self.output,'inert',self.build)
        self.assertEqual([n for n,_ in self.calls], ['inert_discovery'])

    def test_hook_added_during_fake_discovery_never_reaches_execution(self):
        def discovery(name, argv, timeout):
            result=self.fake(name,argv,timeout);(self.build/'CTestCustom.cmake').write_text('# inert\n');return result
        with self.assertRaisesRegex(ValueError,'hook/configuration'):
            selector.selected_ctest(discovery,self.output,'inert',self.build)
        self.assertEqual([n for n,_ in self.calls], ['inert_discovery'])

    def test_final_boundary_rechecks_build_metadata(self):
        original=selector.dump_new
        def save(path, plan):
            original(path,plan);self.file.write_text(self.original+'# changed after saving plan\n')
        with mock.patch.object(selector,'dump_new',side_effect=save), self.assertRaisesRegex(ValueError,'before execution'):
            selector.selected_ctest(self.fake,self.output,'inert',self.build)
        self.assertEqual([n for n,_ in self.calls], ['inert_discovery'])

    def test_source_manifest_mismatch_rejected_before_discovery(self):
        with mock.patch.object(selector,'source_manifest',return_value={}):self.assert_rejected_before_discovery()

    def test_cli_default_and_retained_json_reject_hooks_before_subprocess(self):
        (self.build/'CTestCustom.cmake').write_text('# inert hook\n')
        retained=Path(self.temp)/'discovery.json';retained.write_text(json.dumps(self.discovery))
        for extra in [[], ['--discovery-json', str(retained)]]:
            with self.subTest(extra=extra),mock.patch.object(sys,'argv',['selector','--build-dir',str(self.build)]+extra),\
                 contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(selector.main(),1)
        self.assertEqual(self.calls, [])

    def test_cli_clean_retained_json_never_invokes_subprocess(self):
        retained=Path(self.temp)/'discovery.json';retained.write_text(json.dumps(self.discovery))
        with mock.patch.object(sys,'argv',['selector','--build-dir',str(self.build),'--discovery-json',str(retained)]),\
             contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(selector.main(),0)
        self.assertEqual(json.loads(stdout.getvalue())['selected'],EXPECTED)

    def test_cli_clean_default_uses_only_explicit_fake_discovery(self):
        fake=mock.Mock(return_value=type('Result',(),{'stdout':json.dumps(self.discovery)})())
        with mock.patch.object(sys,'argv',['selector','--build-dir',str(self.build)]),\
             mock.patch.object(selector.subprocess,'run',fake),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(selector.main(),0)
        fake.assert_called_once();self.assertIn('-N',fake.call_args.args[0])

    def test_gpu_metadata_fixture_still_requires_opt_in_never_selects_diagnostics(self):
        discovered=write_fixture(self.build,gpu=True)
        plan=selector.select_tests(discovered,self.build)
        self.assertEqual(plan['selected'],EXPECTED)
        plan=selector.select_tests(discovered,self.build,allow_gpu=True)
        self.assertEqual(plan['selected_count'],21)
        self.assertNotIn('cuda_benchmark_gpu_framework',plan['selected'])

    def test_reviewed_cuda_backtrace_matches_retained_generator_stack_shape(self):
        policy=selector.load_manifest()['build_metadata']['test_properties']
        include_line=next(i+1 for i,line in enumerate((ROOT/'CMakeLists.txt').read_text().splitlines())
                          if 'include(cmake/cuda.cmake)' in line)
        for name in ['cuda_runtime_smoke','cuda_sorting','cuda_benchmark_gpu_framework']:
            number=next(i+1 for i,line in enumerate((ROOT/'cmake/cuda.cmake').read_text().splitlines())
                        if 'add_test(NAME '+name+' ' in line)
            expected=f'@source/cmake/cuda.cmake;{number};add_test;@source/cmake/cuda.cmake;0;;@source/CMakeLists.txt;{include_line};include;@source/CMakeLists.txt;0;'
            self.assertEqual(policy[name]['_BACKTRACE_TRIPLES'],expected)

    def test_reviewed_bracket_quoted_generator_format(self):
        import re
        self.file.write_text(re.sub(r'"([^"\n]*)"',r'[=[\1]=]',self.original))
        self.assertEqual(selector.select_tests(self.discovery,self.build)['selected'],EXPECTED)

    def test_dart_unknown_commands_duplicate_and_malformed_records_rejected(self):
        dart=self.build/'DartConfiguration.tcl'
        for value in ['CTEST_CUSTOM_PRE_TEST: /never/executed\n', 'garbage', 'TimeOut: 1\nTimeOut: 2\n']:
            with self.subTest(value=value):dart.write_text(value);self.assert_rejected_before_discovery()

    def test_reviewed_dart_metadata_and_modified_command(self):
        policy=selector.load_manifest()['build_metadata'];values=policy['dart_defaults']
        text=''.join(k+': '+v.replace('@source',str(ROOT)).replace('@build',str(self.build))+'\n' for k,v in values.items())
        dart=self.build/'DartConfiguration.tcl';dart.write_text(text)
        self.assertEqual(selector.select_tests(self.discovery,self.build)['selected'],EXPECTED)
        dart.write_text(text.replace('MakeCommand: ', 'MakeCommand: /unreviewed-command '))
        self.assert_rejected_before_discovery()

    def test_discovery_command_properties_and_registry_identity_must_match_guard(self):
        for mutation in ['command','working_directory','duplicate_property','registry']:
            with self.subTest(mutation=mutation):
                data=copy.deepcopy(self.discovery);test=next(t for t in data['tests'] if t['name']=='datasets')
                if mutation=='command':test['command']=['/never/executed']
                if mutation=='working_directory':test['properties'][0]['value']='/unreviewed'
                if mutation=='duplicate_property':test['properties']*=2
                if mutation=='registry':data['tests'].pop()
                with self.assertRaises(ValueError):selector.select_tests(data,self.build)


if __name__ == '__main__':
    unittest.main()
