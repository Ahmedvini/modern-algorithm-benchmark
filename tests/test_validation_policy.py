"""Synthetic classification and static untimed-path tests; no subprocesses/workloads."""
import copy
import hashlib
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import cpu_gpu_validation_policy as p
from cpu_gpu_provenance import TRUSTED_FREEZE_SHA256, strict_json


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy, self.anchors = p.trusted_policy()
        self.context = dict(session_id='synthetic-session', source_identity='a'*64,
                            build_identity='b'*64, binary_identity='c'*64,
                            freeze_sha256=TRUSTED_FREEZE_SHA256)

    def fixture(self, kind='correctness_validation'):
        records = {name: dict(dict(status='passed',exit_code=0,skipped=0,missing=0,sha256='d'*64),
                             **self.policy['coverage'].get(name, {}))
                   for name in self.policy['required_records'][kind]}
        context = dict(self.context,record_sha256={name:'d'*64 for name in records})
        artifact = dict(schema_version=2,policy='cpu_gpu_validation_v2',artifact_kind=kind,status='passed',
                        study_eligible=False,execution_authorized=False,records=records,
                        protected_source_sha256=self.anchors,**self.context)
        return artifact,context

    def test_four_kinds_are_distinct_and_never_authorize_execution(self):
        for kind in sorted(p.KINDS):
            a,c=self.fixture(kind); r=p.classify(a,c)
            self.assertEqual(r['artifact_kind'],kind); self.assertFalse(r['study_eligible'])
            self.assertFalse(r['execution_authorized'])
            self.assertEqual(r['bounded_validation_ready'],kind=='correctness_validation')

    def test_missing_unknown_or_ambiguous_fields_rejected(self):
        for field in ['policy','artifact_kind','status','study_eligible','execution_authorized','records','session_id']:
            a,c=self.fixture(); a.pop(field)
            with self.subTest(field=field), self.assertRaises(ValueError): p.classify(a,c)
        a,c=self.fixture(); a['artifact_kind']='build_pass'
        with self.assertRaises(ValueError): p.classify(a,c)
        with self.assertRaises(ValueError): strict_json('{"artifact_kind":1,"artifact_kind":2}')

    def test_failed_interrupted_skipped_and_missing_records_rejected(self):
        for field,value in [('status','failed'),('status','interrupted'),('exit_code',1),('skipped',1),('missing',1)]:
            a,c=self.fixture(); a['records']['cpu_release'][field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError): p.classify(a,c)
        a,c=self.fixture(); a['records'].pop('gpu_prepared')
        with self.assertRaises(ValueError): p.classify(a,c)

    def test_stale_context_and_mutually_consistent_adapter_maps_rejected(self):
        for field in self.context:
            a,c=self.fixture(); a[field]='stale'
            with self.subTest(field=field), self.assertRaises(ValueError): p.classify(a,c)
        a,c=self.fixture(); a['protected_source_sha256']=dict(self.anchors)
        a['protected_source_sha256']['src/cuda/cub_sort.cu']='0'*64
        c['protected_source_sha256']=a['protected_source_sha256']
        with self.assertRaises(ValueError): p.classify(a,c)

    def test_record_hash_and_counts_must_match(self):
        a,c=self.fixture(); a['records']['cpu_release']['sha256']='0'*64
        with self.assertRaises(ValueError): p.classify(a,c)
        a,c=self.fixture(); a['records']['gpu_prepared']['inputs']=1
        with self.assertRaises(ValueError): p.classify(a,c)

    def test_correctness_cannot_be_promoted_by_claims(self):
        for field in ['study_eligible','execution_authorized']:
            a,c=self.fixture(); a[field]=True
            with self.assertRaises(ValueError): p.classify(a,c)
        a,c=self.fixture(); a['artifact_kind']='full_study_prerequisites'
        with self.assertRaises(ValueError): p.classify(a,c)

    def test_trusted_policy_missing_malformed_or_changed_fails_closed(self):
        with mock.patch.object(p,'POLICY',ROOT/'NO_SUCH_POLICY'):
            with self.assertRaises(ValueError): p.trusted_policy()
        with mock.patch.object(p,'sha',return_value='0'*64):
            with self.assertRaises(ValueError): p.trusted_policy()

    def test_current_protected_sources_match_approved_exceptions(self):
        p.verify_current_sources()

    def test_untimed_gpu_and_worker_paths_have_no_measurement_calls(self):
        source=(ROOT/'src/cuda/cub_timing.cu').read_text()
        body=source.split('void CudaTimingSession::execute_untimed(',1)[1].split('void CudaTimingSession::close()',1)[0]
        for forbidden in ['Clock','chrono','cudaEvent','sample(']: self.assertNotIn(forbidden,body)
        for helper in ['s.h2d();','s.sort();','s.d2h();']: self.assertIn(helper,body)
        for name in ['tests/test_parallel_workers.cpp','tests/test_cuda_prepared_correctness.cpp']:
            text=(ROOT/name).read_text()
            for forbidden in ['Clock::now','steady_clock','cudaEventRecord','cudaEventElapsedTime','.sample(']:
                self.assertNotIn(forbidden,text)


if __name__=='__main__': unittest.main()
