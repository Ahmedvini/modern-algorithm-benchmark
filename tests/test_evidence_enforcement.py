"""Inert evidence parser regressions. All execution/discovery is forbidden.

Compiler records and CTest stdout here are clearly synthetic unit fixtures, not
observed builds/tests. No fixture installs the independent production trust pin.
"""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
with mock.patch.object(subprocess,'run',side_effect=AssertionError('execution forbidden')), \
     mock.patch.object(subprocess,'Popen',side_effect=AssertionError('execution forbidden')):
    import cpu_gpu_evidence as evidence
    from cpu_gpu_evidence_io import EvidenceStore, digest, command
    from cpu_gpu_build_provenance import validate_build
    import cpu_gpu_protocol as protocol
    import cpu_gpu_build_identity as identity


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        for target in ['subprocess.run','subprocess.Popen','os.system']:
            patch=mock.patch(target,side_effect=AssertionError('execution/discovery forbidden'))
            patch.start();self.addCleanup(patch.stop)
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        self.root=Path(temporary.name)
        self.source=protocol.source_manifest()
        self.review=dict(context={'synthetic_unit_context':True}, source_dir=str(ROOT),
                         build_dir=str(self.root/'build'), record_sha256={})

    def put(self,name,value):
        raw=value if isinstance(value,bytes) else json.dumps(value,sort_keys=True).encode()
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        return dict(file=name,sha256=digest(raw))

    def store(self):return EvidenceStore(self.root)

    def cmd(self,argv,cwd=None,stdout='synthetic unit output',**more):
        return dict(argv=argv,cwd=cwd or str(ROOT),exit_code=0,status='completed',stdout=stdout,stderr='',**more)

    def proof(self,outputs=('comparison_input',),sanitize=False,prefix='proof'):
        build=str(self.root/('san' if sanitize else 'build'));src=str(ROOT)
        tool='/usr/bin/c++';cmake='/usr/bin/cmake';obj=build+'/input.o'
        argv=[tool,'-c',src+'/src/benchmark/comparison_input_main.cpp','-o',obj]
        cache=('CMAKE_HOME_DIRECTORY:INTERNAL='+src+'\nCMAKE_BUILD_TYPE:STRING='+('Debug' if sanitize else 'Release')+
               '\nMAB_ENABLE_SANITIZERS:BOOL='+('ON' if sanitize else 'OFF')+'\n').encode()
        meta={'CMakeCache.txt':self.put(prefix+'/cache',cache),
              'compile_commands.json':self.put(prefix+'/compile.json',[
                  dict(directory=build,file=argv[2],arguments=argv)]),
              'CTestTestfile.cmake':self.put(prefix+'/registry',b'# inert\n')}
        out_hash=digest(b'synthetic executable; never executed')
        compile_ref=self.put(prefix+'/compile_exit.json',self.cmd(argv,build,
            operation='compile',output=obj,output_sha256=digest(b'object'),
            source_before_sha256=self.source,source_after_sha256=self.source))
        steps=[compile_ref]
        for name in outputs:
            steps.append(self.put(prefix+'/'+name+'.json',self.cmd([tool,obj,'-o',build+'/'+name],build,
                operation='link',output=build+'/'+name,output_sha256=out_hash,
                inputs_sha256={'input.o':digest(b'object')},source_before_sha256=self.source,source_after_sha256=self.source)))
        value=dict(schema_version=1,kind='cpu_gpu_build_provenance_v1',source_dir=src,build_dir=build,
            source_sha256=self.source,source_after_sha256=self.source,build_type='Debug' if sanitize else 'Release',
            sanitizers=sanitize,outputs_sha256={n:out_hash for n in outputs},metadata=meta,
            toolchain={t:dict(sha256=digest(b'synthetic tool'),version=self.put(prefix+'/tool_'+Path(t).name,
                         self.cmd([t,'--version']))) for t in [cmake,tool]},
            configure=self.put(prefix+'/configure',self.cmd([cmake,'-S',src,'-B',build])),
            build=self.put(prefix+'/build',self.cmd([cmake,'--build',build,'--verbose'])),steps=steps)
        return self.put(prefix+'/provenance.json',value),value

    def cpu(self,sanitize=False):
        gate='cpu_sanitize' if sanitize else 'cpu_release'
        manifest=json.loads((ROOT/'docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())
        # Models a future approved source review, without changing v3 or installing it.
        manifest['reviewed_source_sha256']=self.source
        mref=self.put('selection_manifest.json',manifest)
        build=str(self.root/('san' if sanitize else 'build'));src=str(ROOT)
        def expand(v):return sys.executable if v=='@python' else v.replace('@build',build).replace('@source',src)
        names=sorted(n for n,t in manifest['tests'].items() if t['classification']=='cpu_correctness')
        all_names=sorted(manifest['cpu_build_tests'])
        commands={n:[expand(v) for v in manifest['tests'][n]['command']] for n in all_names}
        executables=sorted({Path(token).name for n in names for token in commands[n] if token.startswith(build+'/')})
        pref,proof=self.proof(executables,sanitize)
        lines=[];properties={}
        for n in all_names:
            args=[n]+commands[n]
            lines.append('add_test('+' '.join(json.dumps(a) for a in args)+')')
            props={k:expand(v) for k,v in manifest['build_metadata']['test_properties'][n].items()}
            properties[n]=props
            args=[n,'PROPERTIES']+[v for pair in props.items() for v in pair]
            lines.append('set_tests_properties('+' '.join(json.dumps(a) for a in args)+')')
        # Backtrace values have semicolons, not Python/JSON escape sequences.
        proof['metadata']['CTestTestfile.cmake']=self.put('proof/registry',('\n'.join(lines)+'\n').encode())
        pref=self.put('proof/provenance.json',proof)
        argv=['ctest','--test-dir',build,'--output-on-failure','-V','--parallel','1','-R','^('+'|'.join(names)+')$']
        plan=dict(policy=manifest['policy'],selected=names,selected_count=len(names),manifest_sha256=mref['sha256'],
            allow_gpu_correctness=False,tests_executed=False,full_protocol_prerequisites=False,
            discovered_count=len(all_names),ctest_argv=argv,build_metadata=dict(build_dir=build,test_names=all_names,
            commands=commands,properties=properties,files_sha256={'CTestTestfile.cmake':proof['metadata']['CTestTestfile.cmake']['sha256']}))
        discovery=dict(kind='ctestInfo',version=dict(major=1,minor=0),tests=[
            dict(name=n,command=commands[n],properties=[]) for n in all_names])
        text='\n'.join('Start '+str(i)+': '+n+'\n'+str(i)+'/21 Test #'+str(i)+': '+n+' ..... Passed 0.001 sec'
                       for i,n in enumerate(names,1))+'\n100% tests passed, 0 tests failed out of 21\n'
        prefix=['env','-u','ASAN_OPTIONS','-u','LSAN_OPTIONS','UBSAN_OPTIONS=halt_on_error=1'] if sanitize else []
        record=dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate=gate,context=self.review['context'],
            manifest=mref,selection=self.put('selection_plan.json',plan),build_provenance=pref,
            executables_sha256=proof['outputs_sha256'],guarded_metadata={'CTestTestfile.cmake':proof['metadata']['CTestTestfile.cmake']},
            discovery=self.put('discovery.json',self.cmd(['ctest','--test-dir',build,'-N','--show-only=json-v1'],stdout=json.dumps(discovery))),
            command=self.put('cpu_command.json',self.cmd(prefix+argv,stdout=text)))
        self.review.update(selection_sha256=mref['sha256'],python=sys.executable,cpu_build_provenance_sha256={gate:pref['sha256']})
        return record

    def check(self,record):
        ref=self.put('framework.json',record)
        self.review['record_sha256'][record['gate']]=ref['sha256']
        return evidence.record_coverage(self.store(),record['gate'],ref,self.review,self.source)

    def prepared(self):
        value=dict(schema_version=1,artifact_kind='correctness_validation',scope='prepared_cuda_untimed_v1',
            study_eligible=False,status='passed',inputs=163,output_checks=489,invalid_operations_rejected=489,failures=0)
        record=dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate='gpu_prepared',context=self.review['context'],
            command=self.put('prepared_command.json',self.cmd([self.review['build_dir']+'/test_cuda_prepared_correctness'],stdout=json.dumps(value))))
        return record,value

    def test_valid_prepared_record_is_derived(self):
        r,v=self.prepared();self.assertEqual(self.check(r),dict(inputs=163,output_checks=489,failures=0))

    def test_hash_consistent_placeholder_and_malformed_schema_rejected(self):
        for value in [{},dict(synthetic_fixture=True,gate='gpu_prepared'),[],dict(schema_version=True,kind='cpu_gpu_framework_record_v1')]:
            ref=self.put('placeholder.json',value);self.review['record_sha256']['gpu_prepared']=ref['sha256']
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'unsupported framework record schema'):
                evidence.record_coverage(self.store(),'gpu_prepared',ref,self.review,self.source)

    def test_contradictory_outer_record_cannot_override_valid_body(self):
        r,v=self.prepared();r['status']='failed'
        with self.assertRaisesRegex(ValueError,'contradictory framework record fields'):self.check(r)

    def test_derived_claim_supports_every_original_gate_including_pilot_missing(self):
        for gate,coverage in evidence.trusted_policy()[0]['coverage'].items():
            with self.subTest(gate=gate):
                claim=evidence.derived_claim(dict(sha256='0'*64),coverage)
                self.assertEqual(claim['status'],'passed');self.assertEqual(claim['missing'],0)
                for key,value in coverage.items():self.assertEqual(claim[key],value)

    def test_hash_consistent_failed_incomplete_prepared_records_rejected(self):
        for key,value in [('status','failed'),('inputs',162),('output_checks',488),('failures',1),('study_eligible',True)]:
            r,v=self.prepared();v[key]=value
            r['command']=self.put('prepared_command.json',self.cmd([self.review['build_dir']+'/test_cuda_prepared_correctness'],stdout=json.dumps(v)))
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'incomplete/failed prepared'):self.check(r)

    def test_hash_consistent_incorrect_exit_status_rejected(self):
        r,v=self.prepared();result=self.store().json(r['command']);result['exit_code']=1
        r['command']=self.put('prepared_command.json',result)
        with self.assertRaisesRegex(ValueError,'failed/incomplete command'):self.check(r)

    def test_hash_consistent_wrong_context_build_and_command_rejected(self):
        r,v=self.prepared();r['context']={'wrong_source':True}
        with self.assertRaisesRegex(ValueError,'context mismatch'):self.check(r)
        r,v=self.prepared();result=self.store().json(r['command']);result['argv'][0]='/other/build/test_cuda_prepared_correctness'
        r['command']=self.put('prepared_command.json',result)
        with self.assertRaisesRegex(ValueError,'executed command identity'):self.check(r)

    def test_duplicate_json_keys_rejected_with_correct_hash(self):
        ref=self.put('duplicate.json',b'{"inputs":163,"inputs":0}')
        with self.assertRaises(ValueError):self.store().json(ref)

    def test_tampered_and_stale_hash_rejected(self):
        ref=self.put('record.json',dict(status='passed'));self.put('record.json',dict(status='failed'))
        with self.assertRaisesRegex(ValueError,'hash mismatch'):self.store().json(ref)

    def test_hash_and_parser_share_immutable_bytes(self):
        ref=self.put('record.json',dict(status='passed'));store=self.store();store.raw(ref)
        changed=self.put('record.json',dict(status='failed'))
        self.assertEqual(store.json(ref),dict(status='passed'))
        with self.assertRaisesRegex(ValueError,'hash mismatch'):store.json(changed)

    def test_alias_and_path_substitution_rejected(self):
        ref=self.put('record.json',{})
        (self.root/'alias.json').symlink_to(self.root/'record.json')
        for path in ['alias.json','../record.json','./record.json']:
            with self.subTest(path=path),self.assertRaises(ValueError):self.store().raw(dict(ref,file=path))

    def test_valid_cpu_release_record_bound_to_plan_commands_and_build(self):
        self.assertEqual(self.check(self.cpu()),dict(passed=21))

    def test_valid_cpu_sanitizer_record(self):
        self.assertEqual(self.check(self.cpu(True)),dict(passed=21))

    def test_wrong_selection_manifest_rejected_with_consistent_hash(self):
        r=self.cpu();m=self.store().json(r['manifest']);m['reviewed_source_sha256']={'wrong':'0'*64}
        r['manifest']=self.put('selection_manifest.json',m)
        with self.assertRaisesRegex(ValueError,'wrong approved selection snapshot'):self.check(r)
        self.review['selection_sha256']=r['manifest']['sha256']
        with self.assertRaisesRegex(ValueError,'source snapshot mismatch'):self.check(r)

    def test_cpu_missing_duplicate_conflicting_or_failed_tests_rejected(self):
        for mode in ['missing','duplicate','failed','contradictory']:
            r=self.cpu();result=self.store().json(r['command']);lines=result['stdout'].splitlines()
            if mode=='missing':lines=lines[2:]
            elif mode=='duplicate':lines=lines[:2]+lines
            elif mode=='failed':lines[1]=lines[1].replace('Passed','***Failed')
            else:lines.append('ERROR: AddressSanitizer: rejected fixture')
            result['stdout']='\n'.join(lines);r['command']=self.put('cpu_command.json',result)
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'CTest coverage|contradictory CTest'):self.check(r)

    def test_cpu_command_and_plan_tampering_rejected(self):
        for mode in ['selection','argv','cwd','exit','executables']:
            r=self.cpu()
            if mode=='selection':
                p=self.store().json(r['selection']);p['selected'].pop();r['selection']=self.put('selection_plan.json',p)
            elif mode=='executables':r['executables_sha256']={}
            else:
                c=self.store().json(r['command'])
                if mode=='argv':c['argv'][-1]='.*'
                elif mode=='cwd':c['cwd']='/another/source'
                else:c['exit_code']=1
                r['command']=self.put('cpu_command.json',c)
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'plan coverage|command identity|working directory|failed/incomplete|executable coverage'):self.check(r)

    def test_discovery_includes_fixtures_or_modified_commands_rejected(self):
        for mode in ['fixtures','commands','duplicate']:
            r=self.cpu();d=self.store().json(r['discovery']);value=json.loads(d['stdout'])
            if mode=='fixtures':value['tests'][0]['properties']=[dict(name='FIXTURES_REQUIRED',value='unreviewed')]
            elif mode=='commands':value['tests'][0]['command']=['/unreviewed/wrapper']
            else:value['tests'][0]=value['tests'][1]
            d['stdout']=json.dumps(value);r['discovery']=self.put('discovery.json',d)
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'unsafe discovery|command substitution|duplicate discovery'):self.check(r)

    def test_valid_build_graph_is_not_empty_compile_list(self):
        ref,p=self.proof();self.assertEqual(validate_build(self.store(),ref,self.source,p['outputs_sha256']),p)

    def test_arbitrary_empty_or_fabricated_compile_list_rejected(self):
        for entries in [[],[{}],{},[dict(directory='/wrong',file='/unreviewed')]]:
            ref,p=self.proof();p['metadata']['compile_commands.json']=self.put('proof/compile.json',entries)
            ref=self.put('proof/provenance.json',p)
            with self.subTest(entries=entries),self.assertRaisesRegex(ValueError,'compile-command|compile source/build'):
                validate_build(self.store(),ref,self.source,p['outputs_sha256'])

    def test_missing_compiler_linker_or_failed_exit_evidence_rejected(self):
        for mode in ['none','compile','link','failed','object']:
            ref,p=self.proof()
            if mode=='none':p['steps']=[]
            elif mode=='compile':p['steps']=p['steps'][1:]
            elif mode=='link':p['steps']=p['steps'][:1]
            else:
                s=self.store().json(p['steps'][1])
                if mode=='failed':s['exit_code']=2
                else:s['inputs_sha256']['input.o']='0'*64
                p['steps'][1]=self.put('proof/comparison_input.json',s)
            ref=self.put('proof/provenance.json',p)
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'missing compiler|lacks earlier|missing/stale|failed/incomplete|object hash'):
                validate_build(self.store(),ref,self.source,p['outputs_sha256'])

    def test_stale_build_source_outputs_and_other_build_rejected(self):
        for mode in ['source','output','missing','build']:
            ref,p=self.proof();required=dict(p['outputs_sha256'])
            if mode=='source':p['source_after_sha256']={'stale':'0'*64}
            elif mode=='output':required['comparison_input']='0'*64
            elif mode=='missing':required['missing_binary']='0'*64
            else:p['build_dir']='/another/build'
            ref=self.put('proof/provenance.json',p)
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'stale build|missing build output|different provenance build'):
                validate_build(self.store(),ref,self.source,required,str(self.root/'build'))

    def test_missing_trusted_review_is_not_trust_on_first_use(self):
        with self.assertRaisesRegex(ValueError,'review not installed'):evidence.approval()

    def test_malformed_missing_or_mutated_independent_anchor_rejected(self):
        for data in [b'{',b'{}',b'{"policy":1,"policy":2}']:
            ref=self.put('review.json',data)
            with mock.patch.object(evidence,'APPROVAL',self.root/'review.json'), \
                 mock.patch.object(evidence,'TRUSTED_APPROVAL_SHA256',ref['sha256']),self.assertRaises(ValueError):evidence.approval()
        with mock.patch.object(evidence,'APPROVAL',self.root/'absent'), \
             mock.patch.object(evidence,'TRUSTED_APPROVAL_SHA256','0'*64),self.assertRaises(OSError):evidence.approval()

    def candidate(self):
        base=json.loads((ROOT/'docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())
        old=base['reviewed_source_sha256'];source=self.source
        return dict(base,schema_version=4,policy='non_timing_correctness_v4_candidate',
            review_status='pending_independent_review',base_manifest_sha256=evidence.BASE_SELECTION_SHA256,
            reviewed_source_sha256=source,source_delta=dict(added=sorted(set(source)-set(old)),removed=sorted(set(old)-set(source)),
                modified=sorted(n for n in set(source)&set(old) if source[n]!=old[n])))

    def test_inactive_candidate_preserves_default_19_and_classifications(self):
        c=self.candidate();delta=evidence.candidate(c,self.source);self.assertTrue(delta['added'])
        base=json.loads((ROOT/'docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())
        self.assertEqual(c['tests'],base['tests']);self.assertEqual(c['cpu_build_tests'],base['cpu_build_tests'])
        default=sorted(n for n,v in c['tests'].items() if v['classification']=='cpu_correctness' and not v.get('diagnostic_only'))
        self.assertEqual(default,sorted('baselines cli comparisons cpu_gpu_comparison_framework cuda_benchmark_analysis cuda_preflight cuda_sort_handoff datasets environment_manifest memory memory_unsupported mergesort metrics_cli pdqsort quicksort radixsort searching structures timsort'.split()))

    def test_candidate_unreviewed_add_remove_path_or_hash_changes_rejected(self):
        for mode in ['add','remove','path','hash','test']:
            c=copy.deepcopy(self.candidate())
            if mode=='add':c['reviewed_source_sha256']['unapproved']='0'*64
            elif mode=='remove':c['reviewed_source_sha256'].pop('CMakeLists.txt')
            elif mode=='path':c['reviewed_source_sha256']['../CMakeLists.txt']=c['reviewed_source_sha256'].pop('CMakeLists.txt')
            elif mode=='hash':c['reviewed_source_sha256']['CMakeLists.txt']='0'*64
            else:c['tests']['parallel_mergesort']['classification']='cpu_correctness'
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'candidate source|candidate changed'):evidence.candidate(c,self.source)

    def test_candidate_cannot_establish_approved_selection(self):
        c=self.candidate();ref=self.put('candidate.json',c)
        with self.assertRaisesRegex(ValueError,'candidate is not approved'):
            evidence.selection_manifest(self.store(),ref,dict(selection_sha256=ref['sha256']),self.source)

    def test_full_validator_rejects_internally_consistent_unsupported_assertion(self):
        cpu=self.cpu();cpu['context']=None
        outputs=identity.EXECUTABLES+('libmab_parallel.a','libmab_cuda_timing.a')
        bref,bproof=self.proof(outputs,prefix='main_build')
        build_identity=dict(source_dir=str(ROOT),build_dir=bproof['build_dir'],build_provenance=bref,
            files_sha256=dict(bproof['outputs_sha256'],**{n:r['sha256'] for n,r in bproof['metadata'].items()}))
        context=dict(session_id='inert-unit',source_identity=digest(protocol.canonical(self.source)),
            build_identity=digest(protocol.canonical(build_identity)),binary_identity=bproof['outputs_sha256']['cpu_gpu_comparison'],
            freeze_sha256=evidence.TRUSTED_FREEZE_SHA256)
        self.review.update(context=context,build_provenance_sha256=bref['sha256'])
        cpu['context']=context
        parent,anchors=evidence.trusted_policy();names=parent['required_records']['full_study_prerequisites']
        refs={n:self.put('full_'+n+'.json',cpu if n=='cpu_release' else {}) for n in names}
        self.review['record_sha256']={n:r['sha256'] for n,r in refs.items()}
        records={n:dict(dict(status='passed',exit_code=0,skipped=0,missing=0,sha256=refs[n]['sha256']),**parent['coverage'][n]) for n in names}
        records['cpu_release']['passed']=22
        p=dict(session_id='inert-unit',build_provenance=bref,framework_records=refs,framework_validation=dict(records=records))
        with mock.patch.object(evidence,'approval',return_value=self.review), \
             self.assertRaisesRegex(ValueError,'coverage assertion unsupported by actual record: cpu_release'):
            evidence.validate_full(p,self.store(),self.source,build_identity)

    def test_workspace_missing_or_duplicate_size_is_rejected(self):
        r=dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate='workspace',context=self.review['context'],commands=[],
               environment=self.put('unused_environment.json',{}))
        with self.assertRaisesRegex(ValueError,'missing workspace size coverage'):self.check(r)

    def test_independent_review_failed_decision_rejected_with_correct_hash(self):
        r=dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate='independent_review',context=self.review['context'],
            decision=self.put('decision.json',dict(schema_version=1,kind='independent_evidence_review_v1',accepted=False,
                execution_authorized=False,context=self.review['context'])))
        with self.assertRaisesRegex(ValueError,'decision not accepted'):self.check(r)

    def test_synthetic_timing_bundle_cannot_qualify_as_performance(self):
        for gate in ['pilot','timing_smoke']:
            r=dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate=gate,context=self.review['context'],
                raw_files={'run.json':self.put('raw_run.json',dict(run_kind='synthetic_test_fixture')),
                           'COMPLETE.json':self.put('raw_complete.json',{})})
            with self.subTest(gate=gate),self.assertRaisesRegex(ValueError,'synthetic/validation timing evidence cannot qualify'):self.check(r)

    def smoke(self):
        # Synthetic CSV values for parser tests, never observed measurements.
        import csv,io
        from analyze_cuda_results import FIELDS,SHARED,METRICS
        meta=dict(schema_version=1,protocol='cuda_sort_timing_v1',algorithm='cub_radix_sort',
            implementation_version='cub_radix_sort_v1',elapsed_unit='ns',allocation_policy='prepared_pinned_reuse_v1',
            stream_policy='private_nonblocking_serial',end_to_end_clock='steady_clock',phase_clock='cuda_event_float_ms_to_ns',
            distribution='uniform',dataset_generator='mt19937_64_v1',size=4,seed=1729,nearly_sorted_swaps=0,
            duplicate_cardinality=16,repetitions=2,warmups=1,expected_rows=3,cub_version=300001,run_kind='performance',
            sanitizers=False,build_type='Release',compiler_id='GNU',compiler_version='13.3.0',platform='Linux',
            architecture='x86_64',gpu_name='Tesla T4',cuda_compiler_version='13.0',cuda_toolkit_version='13.0',
            run_id='synthetic_parser_unit_only',runtime_api_version=13000,driver_api_version=13000,
            requested_device=0,actual_device=0,compute_major=7,compute_minor=5,device_memory_bytes=16*1024**3,
            workspace_bytes=32,input_hash_fnv1a64='123')
        out=io.StringIO();writer=csv.DictWriter(out,fieldnames=FIELDS);writer.writeheader()
        for phase,trial in [('warmup',0),('measure',0),('measure',1)]:
            writer.writerow(dict({k:meta[k] for k in SHARED},phase=phase,trial_index=trial,
                **{k:1 for k in METRICS},elapsed_unit='ns',status='ok',correctness='passed',error=''))
        refs={'run.json':self.put('smoke/run.json',meta),'trials.csv':self.put('smoke/trials.csv',out.getvalue().encode()),
              'COMPLETE.json':self.put('smoke/COMPLETE.json',dict(schema_version=1,complete=True,rows=3))}
        return dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate='timing_smoke',context=self.review['context'],raw_files=refs)

    def test_valid_smoke_csv_model_parsed_without_measurements(self):
        self.assertEqual(self.check(self.smoke()),dict(complete=True,correctness=True))

    def test_hash_consistent_missing_duplicate_and_invalid_timing_rows_rejected(self):
        for mode in ['missing','duplicate','invalid']:
            r=self.smoke();raw=self.store().raw(r['raw_files']['trials.csv']).decode();lines=raw.splitlines()
            if mode=='missing':lines.pop()
            elif mode=='duplicate':lines[-1]=lines[-2]
            else:lines[-1]=lines[-1].replace(',1,1,1,1,ns,',',nan,1,1,1,ns,')
            r['raw_files']['trials.csv']=self.put('smoke/trials.csv',('\n'.join(lines)+'\n').encode())
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'completion|duplicate|invalid timing'):self.check(r)

    def identity_fixture(self):
        outputs=identity.EXECUTABLES+('libmab_parallel.a','libmab_cuda_timing.a')
        ref,proof=self.proof(outputs)
        build=Path(proof['build_dir']);build.mkdir()
        cache=self.store().raw(proof['metadata']['CMakeCache.txt'])
        cache+=b'MAB_ENABLE_OPENMP:BOOL=ON\nMAB_ENABLE_CUDA:BOOL=ON\nMAB_ENABLE_CUDA_SORT:BOOL=ON\n'
        cache+=b'MAB_ENABLE_CPU_GPU_COMPARISON:BOOL=ON\nCMAKE_CUDA_ARCHITECTURES:STRING=75\n'
        proof['metadata']['CMakeCache.txt']=self.put('proof/cache',cache)
        self.put('proof/provenance.json',proof)
        # The retained records are copied under the intended build, like a future
        # reviewed build capture. Inert fixture bytes, never executed.
        import shutil
        shutil.copytree(self.root/'proof',build/'proof')
        for name,reference in proof['metadata'].items():
            (build/name).write_bytes(self.store().raw(reference))
        for name in outputs:
            (build/name).write_bytes(b'synthetic executable; never executed')
            if name in identity.EXECUTABLES:(build/name).chmod(0o700)
        return build,build/ref['file']

    def test_capture_requires_compile_link_proof_not_just_json_list(self):
        build,path=self.identity_fixture()
        document=identity.capture(build,path)
        identity.verify(document,build/'cpu_gpu_comparison',build/'comparison_input')
        (build/'compile_commands.json').write_text('[]')
        with self.assertRaisesRegex(ValueError,'empty/malformed compile-command'):identity.capture(build,path)

    def test_actual_fixture_binary_hash_mismatch_and_missing_binary_rejected(self):
        build,path=self.identity_fixture();document=identity.capture(build,path)
        (build/'comparison_input').write_text('stale bytes')
        with self.assertRaisesRegex(ValueError,'stale build output'):identity.verify(document,build/'cpu_gpu_comparison',build/'comparison_input')
        (build/'comparison_input').unlink()  # Inert temporary fixture only.
        with self.assertRaises(OSError):identity.capture(build,path)

    def test_snapshot_only_is_never_accepted_as_provenance(self):
        build,path=self.identity_fixture();document=identity.capture_snapshot(build)
        with self.assertRaisesRegex(ValueError,'missing build provenance identity'):
            identity.verify(document,build/'cpu_gpu_comparison',build/'comparison_input')

    def test_default_guard_still_rejects_changed_source_and_inactive_candidate(self):
        import non_timing_tests as selector
        # v3 remains immutable and must still reject the extended source. A
        # separately reviewed local selection may now be active; do not confuse
        # that activation with accepting the historical v3 or inactive v4.
        with mock.patch.object(selector,'MANIFEST',ROOT/'docs/NON_TIMING_TEST_SELECTION_v3.json'), \
             self.assertRaisesRegex(ValueError,'source snapshot changed'):selector.load_manifest()
        ref=self.put('inactive.json',self.candidate())
        with mock.patch.object(selector,'MANIFEST',self.root/ref['file']),self.assertRaisesRegex(ValueError,'invalid non-timing manifest'):
            selector.load_manifest()  # Pure JSON/source validation, never discovery.

    def workspace(self):
        refs=[]
        for n in [1025,65537,1000000]:
            v=dict(size=n,gpu_name='Tesla T4',compute_major=7,compute_minor=5,
                prepared_query_bytes=32,adapter_query_bytes=32,free_device_bytes_before_buffers=8*1024**3,
                prepared_diagnostic_cudaMalloc_requested_bytes=32,adapter_diagnostic_cudaMalloc_requested_bytes=32,
                combined_device_payload_bytes=16*n+64,known_host_peak_payload_bytes=24*n,
                total_device_bytes=16*1024**3,driver_api_version=13000,runtime_api_version=13000,
                workspace_policy_cap_each_bytes=64*1024**2,
                allocation_observation='successful diagnostic cudaMalloc request sizes; allocator physical footprint not measured',
                production_workspace_observation='not instrumented; isolated same-parameter sizing query only')
            refs.append(self.put('resource_'+str(n),self.cmd([self.review['build_dir']+'/cpu_gpu_comparison','--resources',str(n)],stdout=json.dumps(v))))
        keys=['/sys/fs/cgroup/cpu.max','/sys/fs/cgroup/memory.max','/sys/fs/cgroup/memory.current',
              '/sys/fs/cgroup/memory/memory.limit_in_bytes','/sys/fs/cgroup/memory/memory.usage_in_bytes']
        for directory in ['/sys/fs/cgroup/cpu','/sys/fs/cgroup/cpu,cpuacct']:
            keys.extend(directory+'/'+name for name in ['cpu.cfs_quota_us','cpu.cfs_period_us'])
        env=dict(affinity=[0,1],disk_free_bytes=2*1024**3,linux_meminfo='MemAvailable: 2097152 kB',
                 resource_files={k:None for k in keys},**{n:dict(returncode=0,stdout='') for n in ['nvidia_smi','gpu_processes','gpu_details','nvcc']})
        return dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate='workspace',context=self.review['context'],
                    commands=refs,environment=self.put('environment.json',env))

    def test_valid_workspace_all_sizes_and_retained_host_disk_limits(self):
        self.assertEqual(self.check(self.workspace()),dict(sizes=[1025,65537,1000000],all_limits_passed=True))

    def test_duplicate_workspace_size_or_insufficient_resource_snapshot_rejected(self):
        r=self.workspace();r['commands'][2]=r['commands'][0]
        with self.assertRaisesRegex(ValueError,'duplicate/invalid workspace size'):self.check(r)
        r=self.workspace();env=self.store().json(r['environment']);env['disk_free_bytes']=0
        r['environment']=self.put('environment.json',env)
        with self.assertRaisesRegex(ValueError,'free disk'):self.check(r)

    def workers(self):
        value=dict(schema_version=1,artifact_kind='correctness_validation',scope='openmp_workers_untimed_v1',study_eligible=False,
            status='passed',executable=self.review['build_dir']+'/test_parallel_workers',build_type='Release',sanitizers=False,
            requested_threads=2,runtime_dynamic=0,runtime_thread_limit=2,team_size_is_task_participation=False,
            compiler='13.3.0',flags='-O3 -DNDEBUG',openmp_version='4.5',openmp_flags='-fopenmp',
            environment=protocol.load_protocol()['openmp_policy']['environment'],output_checks=12,
            calls=[dict(size=n,registry=r,correctness=True,actual_team_size=2 if n>=32768 else 1,parallel_region=n>=32768)
                   for n in [0,1,32767,32768,32769,65537] for r in [False,True]])
        record=dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate='workers',context=self.review['context'])
        return record,value

    def test_valid_worker_threshold_contents_and_conflicting_calls(self):
        for mode in ['valid','duplicate','failed','team','environment']:
            r,v=self.workers()
            if mode=='duplicate':v['calls'][0]=v['calls'][1]
            elif mode=='failed':v['calls'][0]['correctness']=False
            elif mode=='team':v['calls'][-1]['actual_team_size']=1
            elif mode=='environment':v['environment']={}
            r['command']=self.put('workers.json',self.cmd([v['executable']],stdout=json.dumps(v)))
            if mode=='valid':self.assertEqual(self.check(r),dict(output_checks=12,threshold_team_verified=True))
            else:
                with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'worker threshold|worker environment'):self.check(r)


if __name__=='__main__':
    unittest.main()
