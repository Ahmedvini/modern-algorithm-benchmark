"""Inert provenance regressions; fake binaries are hashed, never executed.

All subprocess, shell and runner execution paths are blocked, including imports.
The positive full-evidence fixtures model metadata, not observed GPU execution.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
with mock.patch.object(subprocess, 'run', side_effect=AssertionError('import subprocess forbidden')), \
     mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('import subprocess forbidden')), \
     mock.patch.object(os, 'system', side_effect=AssertionError('import shell forbidden')):
    import cpu_gpu_protocol as protocol
    import cpu_gpu_provenance as provenance
    import cpu_gpu_framework_compatibility as compatibility
    import cpu_gpu_build_identity as identity
    import cpu_gpu_validation_policy as validation
    import run_cpu_gpu_pilot as runner
    import analyze_cpu_gpu as analyzer


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        for target in ['subprocess.run', 'subprocess.Popen', 'os.system', 'run_cpu_gpu_pilot.invoke']:
            patch = mock.patch(target, side_effect=AssertionError('workload/discovery forbidden'))
            patch.start(); self.addCleanup(patch.stop)
        self.model = protocol.load_protocol()
        self.source = protocol.verify_source_extension(self.model, compatibility.POLICY_ID)
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.build = self.root / 'build'; self.build.mkdir()
        for name in identity.FILES:
            (self.build / name).write_text('inert ' + name)
            if name in identity.EXECUTABLES:
                (self.build / name).chmod(0o700)
        settings = dict(CMAKE_HOME_DIRECTORY=str(ROOT), CMAKE_BUILD_TYPE='Release',
                        MAB_ENABLE_OPENMP='ON', MAB_ENABLE_CUDA='ON', MAB_ENABLE_CUDA_SORT='ON',
                        MAB_ENABLE_CPU_GPU_COMPARISON='ON', MAB_ENABLE_SANITIZERS='OFF',
                        CMAKE_CUDA_ARCHITECTURES='75')
        (self.build / 'CMakeCache.txt').write_text('\n'.join(k + ':STRING=' + v for k, v in settings.items()))
        (self.build / 'compile_commands.json').write_text('[]')
        self.document = identity.capture(self.build)
        self.binary = self.build / 'cpu_gpu_comparison'; self.input = self.build / 'comparison_input'

    def fixture(self):
        parent, anchors = validation.trusted_policy()
        records = {}
        legacy = {}
        for name in ['cpu_release_ctest', 'cpu_sanitize_ctest', 'cuda_ctest', 'cuda_correctness', 'preflight']:
            stdout = 'synthetic non-executed fixture'
            if name == 'cuda_ctest':
                stdout = ('11: Ran 14 tests in 0.001s\n11: OK (skipped=2)\n'
                          'Start 27: cuda_benchmark_gpu_framework\n27: Ran 14 tests in 0.001s\n27: OK\n'
                          '27/32 Test #27: cuda_benchmark_gpu_framework ..... Passed 0.001 sec\n')
            if name == 'cuda_correctness':
                stdout = json.dumps(dict(schema_version=1, protocol='cuda_sort_correctness_v2',
                    algorithm='cub_radix_sort', implementation_version='cub_radix_sort_v1', status='ok',
                    cases=475, output_checks=1900, cub_version=300001, runtime_api_version=13000,
                    driver_api_version=13000, compute_major=7, compute_minor=5, device=0))
            file = self.root / (name + '.json')
            argv = ['synthetic-not-executed']
            if name == 'cuda_ctest': argv = ['ctest', '--test-dir', str(self.build), '--output-on-failure', '-V']
            if name == 'cuda_correctness': argv = [str(self.build / 'test_cuda_sorting')]
            file.write_text(json.dumps(dict(status='completed', exit_code=0, stdout=stdout, stderr='', argv=argv)))
            legacy[name] = dict(file=file.name, sha256=protocol.sha(file))
        for name in parent['required_records']['full_study_prerequisites']:
            file = self.root / ('framework_' + name + '.json')
            file.write_text(json.dumps(dict(synthetic_fixture=True, gate=name)))
            records[name] = dict(file=file.name, sha256=protocol.sha(file))
        bundle = dict(schema_version=2, policy='cpu_gpu_validation_v2', artifact_kind='full_study_prerequisites',
                      status='passed', study_eligible=False, execution_authorized=False,
                      protected_source_sha256=anchors, session_id='synthetic-session',
                      source_identity=hashlib.sha256(protocol.canonical(self.source['current_source_sha256'])).hexdigest(),
                      build_identity=hashlib.sha256(protocol.canonical(self.document)).hexdigest(),
                      binary_identity=protocol.sha(self.binary), freeze_sha256=provenance.TRUSTED_FREEZE_SHA256,
                      records={n: dict(dict(status='passed', exit_code=0, skipped=0, missing=0,
                                           sha256=records[n]['sha256']), **parent['coverage'][n]) for n in records})
        p = dict(schema_version=1, protocol=protocol.PROTOCOL, complete=True, validation_scope='full_protocol_v1', study_eligible=True,
                 framework_compatibility_policy=compatibility.POLICY_ID, source_sha256=self.source['current_source_sha256'],
                 binary_sha256=protocol.sha(self.binary), input_tool_sha256=protocol.sha(self.input),
                 records=legacy, build_identity=self.document, framework_validation=bundle,
                 framework_records=records, session_id='synthetic-session')
        return p

    def validate(self, prerequisite):
        path = self.root / 'prerequisite.json'; path.write_text(json.dumps(prerequisite))
        return runner.validate_prerequisites(path, self.binary, self.input, self.model,
                                             compatibility_policy=compatibility.POLICY_ID)

    def test_explicit_exact_approved_sources_accepted(self):
        provenance.validate_retained_source(self.source, self.model)
        self.assertEqual(len(self.source['changed_anchors']), 3)

    def test_legacy_default_still_rejects_current_framework(self):
        with self.assertRaisesRegex(ValueError, 'protected source/pin changed'):
            protocol.verify_source_extension(self.model)

    def test_unknown_policy_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unknown framework'):
            protocol.verify_source_extension(self.model, 'accept-anything')

    def test_original_adapter_pin_and_each_framework_digest_cannot_change(self):
        for path in ['src/cuda/cub_sort.cu', 'third_party/cub/UPSTREAM.json'] + self.source['changed_anchors']:
            altered = copy.deepcopy(self.source); altered['current_source_sha256'][path] = '0' * 64
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'protected source mismatch'):
                provenance.validate_retained_source(altered, self.model)

    def test_mutually_consistent_model_and_map_cannot_redefine_anchor(self):
        altered = copy.deepcopy(self.source); model = copy.deepcopy(self.model)
        altered['current_source_sha256']['src/cuda/cub_sort.cu'] = '0' * 64
        model['source_at_freeze_sha256']['src/cuda/cub_sort.cu'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'model differs from trusted'):
            provenance.validate_retained_source(altered, model)

    def test_missing_changed_or_unreadable_policy_fails_closed(self):
        for text in [None, '{', '{}', '{"policy":1,"policy":2}']:
            file = self.root / 'missing_policy.json'
            if text is not None: file.write_text(text)
            with self.subTest(text=text), mock.patch.object(compatibility, 'POLICY', file), \
                 self.assertRaisesRegex(ValueError, 'trust root missing/changed'):
                compatibility.approved_anchors(self.model)

    def test_missing_or_modified_review_identity_fails_closed(self):
        for field in ['framework_compatibility_policy', 'compatibility_policy_sha256', 'changed_anchors', 'cmake_review_sha256']:
            altered = copy.deepcopy(self.source); altered.pop(field)
            with self.subTest(field=field), self.assertRaises(ValueError):
                provenance.validate_retained_source(altered, self.model)

    def test_complete_synthetic_launch_metadata_accepted_without_execution(self):
        p = self.fixture(); self.assertEqual(self.validate(p), p)

    def test_correctness_bundle_cannot_replace_full_evidence(self):
        p = self.fixture(); p['framework_validation']['artifact_kind'] = 'correctness_validation'
        with self.assertRaisesRegex(ValueError, 'correctness is insufficient'): self.validate(p)

    def test_missing_framework_coverage_rejected(self):
        for name in validation.trusted_policy()[0]['required_records']['full_study_prerequisites']:
            p = self.fixture(); p['framework_validation']['records'].pop(name); p['framework_records'].pop(name)
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'record coverage'): self.validate(p)

    def test_failed_stale_or_incomplete_evidence_rejected(self):
        for field, value in [('exit_code', 1), ('missing', 1), ('skipped', 1), ('status', 'interrupted')]:
            p = self.fixture(); p['framework_validation']['records']['gpu_prepared'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): self.validate(p)
        p = self.fixture(); p['framework_validation']['binary_identity'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'stale context'): self.validate(p)

    def test_framework_record_hash_mismatch_rejected(self):
        p = self.fixture(); (self.root / p['framework_records']['pilot']['file']).write_text('{}')
        with self.assertRaisesRegex(ValueError, 'record changed'): self.validate(p)

    def test_prepared_or_host_only_output_cannot_replace_gpu_framework(self):
        for text in ['163 inputs 489 checks', 'Ran 14 tests\nOK (skipped=2)',
                     'Start 27: cuda_benchmark_gpu_framework\n27: Ran 14 tests in 0.1s\n27: OK (skipped=2)\n'
                     '27/32 Test #27: cuda_benchmark_gpu_framework ... Passed 0.1 sec']:
            p = self.fixture(); file = self.root / p['records']['cuda_ctest']['file']
            d = json.loads(file.read_text()); d['stdout'] = text; file.write_text(json.dumps(d))
            p['records']['cuda_ctest']['sha256'] = protocol.sha(file)
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'GPU timing-framework coverage absent'):
                self.validate(p)

    def test_duplicate_framework_group_and_missing_legacy_command_rejected(self):
        p = self.fixture(); file = self.root / p['records']['cuda_ctest']['file']
        d = json.loads(file.read_text()); d['stdout'] += d['stdout']; file.write_text(json.dumps(d))
        p['records']['cuda_ctest']['sha256'] = protocol.sha(file)
        with self.assertRaisesRegex(ValueError, 'GPU timing-framework coverage absent'): self.validate(p)
        p = self.fixture(); p['records'].pop('preflight')
        with self.assertRaisesRegex(ValueError, 'missing prerequisite commands'): self.validate(p)

    def test_legacy_baseline_still_accepted_by_provenance_without_compatibility(self):
        legacy = dict(current_source_sha256=dict(self.source['current_source_sha256']),
                      changed_anchors=['CMakeLists.txt'], cmake_review_sha256=provenance.TRUSTED_CMAKE_REVIEW_SHA256)
        legacy['current_source_sha256'].update({k: v for k, v in provenance.trusted_source_anchors(self.model).items()
                                                if not k.startswith('docs/')})
        provenance.validate_retained_source(legacy, self.model)

    def test_incomplete_production_oracle_cannot_be_substituted(self):
        p = self.fixture(); file = self.root / p['records']['cuda_correctness']['file']
        d = json.loads(file.read_text()); v = json.loads(d['stdout']); v['cases'] = 163
        d['stdout'] = json.dumps(v); file.write_text(json.dumps(d)); p['records']['cuda_correctness']['sha256'] = protocol.sha(file)
        with self.assertRaisesRegex(ValueError, 'incomplete sort result: cases'): self.validate(p)

    def test_stale_gpu_command_paths_rejected_even_when_hashes_updated(self):
        for name in ['cuda_ctest', 'cuda_correctness']:
            p = self.fixture(); file = self.root / p['records'][name]['file']
            d = json.loads(file.read_text()); d['argv'] = [a.replace(str(self.build), '/stale/build') for a in d['argv']]
            file.write_text(json.dumps(d)); p['records'][name]['sha256'] = protocol.sha(file)
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'identity mismatch'): self.validate(p)

    def test_omitted_or_mismatched_opt_in_rejected(self):
        p = self.fixture(); p.pop('framework_compatibility_policy')
        with self.assertRaisesRegex(ValueError, 'policy mismatch'): self.validate(p)

    def test_compatible_prerequisites_require_explicit_full_scope(self):
        for field in ['schema_version', 'validation_scope', 'study_eligible']:
            p = self.fixture(); p.pop(field)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'explicit full prerequisite scope'):
                self.validate(p)

    def test_stale_input_binary_rejected_even_with_updated_prerequisite_digest(self):
        p = self.fixture(); self.input.write_text('changed binary bytes')
        p['input_tool_sha256'] = protocol.sha(self.input)
        with self.assertRaisesRegex(ValueError, 'executable identity mismatch'): self.validate(p)

    def test_missing_input_identity_and_stale_build_snapshot_rejected(self):
        for value in [None, {}, dict(self.document, schema_version=True)]:
            p = self.fixture(); p['build_identity'] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'missing/wrong build identity'): self.validate(p)
        p = self.fixture(); p['build_identity']['files_sha256'].pop('comparison_input')
        with self.assertRaisesRegex(ValueError, 'build file identity'): self.validate(p)
        self.document = identity.capture(self.build)
        (self.build / 'comparison_input').write_text('new bytes')
        with self.assertRaisesRegex(ValueError, 'stale or mismatched'): identity.verify(self.document, self.binary, self.input)

    def test_absent_input_file_cannot_be_captured(self):
        self.input.unlink()  # Inert temporary fixture only.
        with self.assertRaises((OSError, ValueError)): identity.capture(self.build)

    def test_symlink_or_different_build_identity_cannot_be_used(self):
        alias = self.root / 'alias'; alias.symlink_to(self.build, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'aliased/symlink'): identity.capture(alias)
        other = self.root / 'another_input'; other.write_text(self.input.read_text()); other.chmod(0o700)
        with self.assertRaisesRegex(ValueError, 'different comparison build'): identity.verify(self.document, self.binary, other)

    def test_wrong_build_configuration_rejected(self):
        file = self.build / 'CMakeCache.txt'; file.write_text(file.read_text().replace('Release', 'Debug'))
        with self.assertRaisesRegex(ValueError, 'unexpected source/build'): identity.capture(self.build)

    def test_source_or_compile_manifest_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, 'stale build source'):
            identity.validate_document(self.document, {'other': '0' * 64}, protocol.sha(self.binary), protocol.sha(self.input))
        with self.assertRaisesRegex(ValueError, 'compile identity mismatch'):
            identity.validate_document(self.document, self.source['current_source_sha256'],
                                       protocol.sha(self.binary), protocol.sha(self.input), '0' * 64)

    def test_analyzer_public_study_path_requires_same_full_evidence(self):
        p = self.fixture()
        d = dict(build_type='Release', sanitizers=False, cub_version=300001, cuda_architectures='75', cxx_standard=17,
                 global_flags='', cuda_flags='', configuration_flags='-O3 -DNDEBUG', cuda_release_flags='-O3 -DNDEBUG')
        self.write('source_review.json', self.source)
        build = dict(description=d, binary_sha256=protocol.sha(self.binary), input_tool_sha256=protocol.sha(self.input),
                     source_review_sha256=protocol.sha(self.root / 'source_review.json'),
                     compile_commands_sha256=protocol.sha(self.build / 'compile_commands.json'))
        self.write('build.json', build); self.write('prerequisites.json', p)
        self.write('environment.json', dict(omp_environment=self.model['openmp_policy']['environment']))
        (self.root / 'compile_commands.json').write_bytes((self.build / 'compile_commands.json').read_bytes())
        for file in [protocol.FREEZE, protocol.MATRIX, ROOT / 'docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md']:
            (self.root / file.name).write_bytes(file.read_bytes())
        for reference in list(p['records'].values()) + list(p['framework_records'].values()):
            destination = self.root / 'prerequisite_commands' / reference['file']; destination.parent.mkdir(exist_ok=True)
            destination.write_bytes((self.root / reference['file']).read_bytes())
        meta = dict(freeze_sha256=protocol.sha(protocol.FREEZE), run_kind='performance', implementations={
            b: dict(source_review='source_review.json', build='build.json',
                    cub_pin=self.model['dependency'] if b.startswith('gpu_') else None) for b in protocol.BACKENDS})
        with mock.patch.object(runner, 'environment_gate'):
            analyzer.validate_study_metadata(self.root, meta, self.model)
            p['framework_validation']['artifact_kind'] = 'correctness_validation'; self.write('prerequisites.json', p)
            with self.assertRaisesRegex(ValueError, 'correctness is insufficient'):
                analyzer.validate_study_metadata(self.root, meta, self.model)

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value))


if __name__ == '__main__':
    with mock.patch.object(subprocess, 'run', side_effect=AssertionError('subprocess forbidden')), \
         mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('subprocess forbidden')), \
         mock.patch.object(os, 'system', side_effect=AssertionError('shell forbidden')):
        unittest.main()
