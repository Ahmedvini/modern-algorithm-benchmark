"""Inert metadata fixtures only; every external execution entry point is blocked."""
import contextlib
import copy
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
from ctest_fixture import write_fixture


class DartCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.stack = contextlib.ExitStack(); self.addCleanup(self.stack.close)
        for name in ['run', 'Popen', 'call', 'check_call', 'check_output']:
            self.stack.enter_context(mock.patch('subprocess.'+name,
                side_effect=AssertionError('external execution forbidden')))
        self.stack.enter_context(mock.patch('os.system', side_effect=AssertionError('shell forbidden')))
        self.stack.enter_context(mock.patch.dict(os.environ, {}, clear=True))
        self.temp = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.build = self.temp/'build'
        self.discovery = write_fixture(self.build)
        self.manifest = selector.load_manifest()
        self.defaults = copy.deepcopy(self.manifest['build_metadata']['dart_defaults'])
        self.output = self.temp/'evidence'; self.output.mkdir()

    def dart(self, values):
        def expand(value):
            return value.replace('@source', str(ROOT.resolve())).replace('@build', str(self.build))
        (self.build/'DartConfiguration.tcl').write_text(
            '\n'.join(k+': '+expand(v) for k,v in values.items())+'\n')

    def colab(self):
        return dict(self.defaults, TLSVerify='', TLSVersion='',
                    MemoryCheckCommand='/usr/local/cuda/bin/compute-sanitizer')

    def rejected(self, values):
        self.dart(values)
        callback = mock.Mock(side_effect=AssertionError('discovery forbidden'))
        with self.assertRaises(ValueError):
            selector.selected_ctest(callback, self.output, 'rejected', self.build)
        callback.assert_not_called()

    def test_both_reviewed_layouts_preserve_19_and_21(self):
        for values in [self.defaults, self.colab()]:
            with self.subTest(values=values):
                self.dart(values)
                base = selector.select_tests(self.discovery, self.build)
                self.assertEqual(base['selected_count'], 19)
                self.assertNotIn('parallel_mergesort', base['selected'])
                extended = selector.select_tests(self.discovery, self.build, allow_diagnostics=True)
                self.assertEqual(set(extended['selected'])-set(base['selected']),
                                 {'parallel_workers_correctness', 'validation_policy'})
                self.assertEqual(extended['selected_count'], 21)
                self.assertFalse(any(a in extended['ctest_argv'] for a in ['-T', '-D', '-S', '--test-action']))

    def test_single_tls_field_rejected(self):
        for key in ['TLSVerify', 'TLSVersion']:
            with self.subTest(key=key): self.rejected(dict(self.defaults, **{key:''}))

    def test_nonempty_tls_rejected(self):
        for key in ['TLSVerify', 'TLSVersion']:
            for value in ['1', 'OFF', '1.2', ' ', '${VALUE}', ';']:
                with self.subTest(key=key,value=value):
                    values=self.colab();values[key]=value;self.rejected(values)

    def test_unreviewed_memorycheck_commands_rejected(self):
        for value in ['/tmp/compute-sanitizer', '/usr/local/cuda/bin/compute-sanitizer --tool memcheck',
                      '/usr/local/cuda/bin/compute-sanitizer;never', 'compute-sanitizer', '', '${COMMAND}']:
            with self.subTest(value=value):
                values=self.colab();values['MemoryCheckCommand']=value;self.rejected(values)

    def test_changed_memorycheck_options_and_type_rejected(self):
        for key in ['MemoryCheckCommandOptions', 'MemoryCheckType']:
            with self.subTest(key=key):
                values=self.colab();values[key]='unreviewed';self.rejected(values)

    def test_unknown_missing_duplicate_malformed_settings_rejected(self):
        values=self.colab();values['UnreviewedSetting']='';self.rejected(values)
        values=self.colab();del values['MemoryCheckCommand'];self.rejected(values)
        for line in ['TLSVerify: \n', 'malformed\n', 'TLSVersion: \x00\n']:
            self.dart(self.colab())
            with (self.build/'DartConfiguration.tcl').open('a') as out: out.write(line)
            callback=mock.Mock(side_effect=AssertionError('discovery forbidden'))
            with self.assertRaises(ValueError):
                selector.selected_ctest(callback,self.output,'malformed',self.build)
            callback.assert_not_called()

    def test_modified_dart_during_discovery_rejected_before_execution(self):
        self.dart(self.colab()); calls=[]
        def callback(name,argv,timeout):
            calls.append(name)
            self.assertTrue(name.endswith('_discovery'))
            self.dart(self.defaults)
            return dict(stdout=json.dumps(self.discovery),exit_code=0)
        with self.assertRaisesRegex(ValueError,'metadata changed during discovery'):
            selector.selected_ctest(callback,self.output,'changed',self.build)
        self.assertEqual(calls,['changed_discovery'])

    def test_hooks_and_includes_remain_rejected_in_colab_layout(self):
        self.dart(self.colab())
        for filename in ['CTestCustom.cmake','CTestConfig.cmake']:
            path=self.build/filename;path.write_text('# inert\n')
            callback=mock.Mock(side_effect=AssertionError('discovery forbidden'))
            with self.assertRaises(ValueError):selector.selected_ctest(callback,self.output,'hook',self.build)
            callback.assert_not_called();path.unlink()
        path=self.build/'CTestTestfile.cmake'
        with path.open('a') as out:out.write('include("never.cmake")\n')
        callback=mock.Mock(side_effect=AssertionError('discovery forbidden'))
        with self.assertRaises(ValueError):selector.selected_ctest(callback,self.output,'include',self.build)
        callback.assert_not_called()

    def test_unknown_profile_and_legacy_policy_do_not_gain_colab_alternative(self):
        self.dart(self.colab())
        for label in ['unknown', 'legacy']:
            manifest=copy.deepcopy(self.manifest)
            if label=='unknown':manifest['build_metadata']['dart_compatibility_profile']='unknown'
            else:manifest['build_metadata']['policy']='flat_literal_ctest_v1'
            callback=mock.Mock(side_effect=AssertionError('discovery forbidden'))
            with mock.patch.object(selector,'load_manifest',return_value=manifest),self.assertRaises(ValueError):
                selector.selected_ctest(callback,self.output,label,self.build)
            callback.assert_not_called()

if __name__ == '__main__': unittest.main()
