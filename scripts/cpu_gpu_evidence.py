"""Strict retained evidence validation; no discovery, subprocesses or measurements.

No independent review is installed. Candidate selection/build material is never
trusted on first use. A future independently reviewed pin is a separate gate.
"""
import hashlib
from pathlib import Path
import re
import tempfile

from cpu_gpu_protocol import ROOT, canonical, require
from cpu_gpu_provenance import strict_json, TRUSTED_FREEZE_SHA256, validate_digest_map, valid_digest
from cpu_gpu_validation_policy import trusted_policy, classify
from cpu_gpu_evidence_io import EvidenceStore, command, digest
from cpu_gpu_build_provenance import validate_build
from ctest_build_guard import statements

POLICY = 'cpu_gpu_evidence_enforcement_v1'
APPROVAL = ROOT / 'docs/CPU_GPU_EVIDENCE_REVIEW_v1.json'
TRUSTED_APPROVAL_SHA256 = None  # Deliberately pending independent review; not a caller option.
BASE_SELECTION_SHA256 = 'fef39034b063c36dabc3eccf9dc6a162ebcf6a4e5cb44abeda83e93fbcf1a434'


def approval():
    require(TRUSTED_APPROVAL_SHA256 is not None, 'independent evidence/selection review not installed')
    store = EvidenceStore(APPROVAL.parent)
    value = store.json(dict(file=APPROVAL.name, sha256=TRUSTED_APPROVAL_SHA256))
    require(isinstance(value, dict) and value.get('schema_version') == 1 and value.get('policy') == POLICY and
            value.get('approved') is True and value.get('execution_authorized') is False,
            'invalid independent evidence review')
    required={'schema_version','policy','approved','execution_authorized','context','source_dir','build_dir','python',
              'selection_sha256','cpu_build_provenance_sha256','build_provenance_sha256','record_sha256','legacy_records',
              'preflight_report_sha256'}
    require(set(value)==required, 'incomplete/ambiguous independent evidence review')
    context=value['context']
    require(isinstance(context,dict) and set(context)=={'session_id','source_identity','build_identity','binary_identity','freeze_sha256'} and
            isinstance(context['session_id'],str) and context['session_id'] and
            all(valid_digest(context[n]) for n in context if n!='session_id'), 'invalid independent context')
    for name in ['source_dir','build_dir','python']:
        path=value[name]
        require(isinstance(path,str) and Path(path).is_absolute() and '..' not in Path(path).parts and str(Path(path))==path,
                'invalid independent path')
    for name in ['selection_sha256','build_provenance_sha256','preflight_report_sha256']:
        require(valid_digest(value[name]), 'invalid independent digest')
    validate_digest_map(value['record_sha256'],'independent framework records')
    require(set(value['record_sha256'])==set(trusted_policy()[0]['required_records']['full_study_prerequisites']),
            'incomplete independent framework record inventory')
    validate_digest_map(value['cpu_build_provenance_sha256'],'independent CPU build records')
    require(set(value['cpu_build_provenance_sha256'])=={'cpu_release','cpu_sanitize'}, 'incomplete independent CPU builds')
    require(isinstance(value['legacy_records'],dict) and set(value['legacy_records'])==
            {'cpu_release_ctest','cpu_sanitize_ctest','cuda_ctest','cuda_correctness','preflight'}, 'incomplete independent legacy records')
    for ref in value['legacy_records'].values():
        require(isinstance(ref,dict) and set(ref)=={'file','sha256'} and valid_digest(ref['sha256']) and
                isinstance(ref['file'],str) and ref['file'] and not Path(ref['file']).is_absolute() and
                '..' not in Path(ref['file']).parts and str(Path(ref['file']))==ref['file'], 'invalid independent legacy reference')
    return value


def candidate(candidate, current_source):
    """Inspect an inactive additive candidate, never activate the selector."""
    raw = (ROOT / 'docs/NON_TIMING_TEST_SELECTION_v3.json').read_bytes()
    require(digest(raw) == BASE_SELECTION_SHA256, 'base selection identity changed')
    base = strict_json(raw.decode())
    require(isinstance(candidate, dict) and candidate.get('schema_version') == 4 and
            candidate.get('policy') == 'non_timing_correctness_v4_candidate' and
            candidate.get('review_status') == 'pending_independent_review' and
            candidate.get('base_manifest_sha256') == BASE_SELECTION_SHA256,
            'invalid candidate selection identity/status')
    for key in ['tests', 'cpu_build_tests', 'cuda_additional_tests', 'build_metadata']:
        require(candidate.get(key) == base[key], 'candidate changed selection membership/commands: ' + key)
    require(candidate.get('reviewed_source_sha256') == current_source, 'candidate source additions/removals/hashes changed')
    old = base['reviewed_source_sha256']
    delta = dict(added=sorted(set(current_source)-set(old)), removed=sorted(set(old)-set(current_source)),
                 modified=sorted(p for p in set(old)&set(current_source) if old[p]!=current_source[p]))
    require(candidate.get('source_delta') == delta, 'candidate source delta mismatch')
    return delta


def selection_manifest(store, reference, approved, source):
    require(reference['sha256'] == approved['selection_sha256'], 'wrong approved selection snapshot')
    manifest = store.json(reference)
    # Existing v3 may only validate its exact historical source. Candidate v4 is
    # never accepted here. Activation requires another independently reviewed version.
    require(manifest.get('policy') in ['non_timing_correctness_v3', 'non_timing_correctness_v4'] and
            manifest.get('review_status', 'approved') == 'approved', 'selection candidate is not approved')
    base_raw = (ROOT/'docs/NON_TIMING_TEST_SELECTION_v3.json').read_bytes()
    require(digest(base_raw) == BASE_SELECTION_SHA256, 'base selection identity changed')
    base = strict_json(base_raw.decode())
    for key in ['tests','cpu_build_tests','cuda_additional_tests','build_metadata']:
        require(manifest.get(key) == base[key], 'approved default selection membership/commands changed')
    require(manifest.get('reviewed_source_sha256') == source, 'selection source snapshot mismatch')
    return manifest


def ctest_coverage(text, names):
    require(isinstance(text, str), 'missing CTest output')
    starts = re.findall(r'(?m)^\s*Start\s+\d+: ([a-z_]+)\s*$', text)
    passed = re.findall(r'(?m)^\s*\d+/\d+ Test\s+#\d+: ([a-z_]+)\s+\.*\s*Passed\s+[^\n]+$', text)
    require(len(starts) == len(names) and len(set(starts)) == len(names) and set(starts) == set(names) and
            len(passed) == len(names) and len(set(passed)) == len(names) and set(passed) == set(names),
            'missing/duplicate/failed CTest coverage')
    summaries = re.findall(r'(?m)^100% tests passed, 0 tests failed out of (\d+)\s*$', text)
    require(summaries == [str(len(names))] and not any(x in text for x in
            ['***Failed','***Skipped','FAILED (','ERROR:','AddressSanitizer:','runtime error:']),
            'contradictory CTest/sanitizer outcome')
    return len(names)


def cpu_record(store, record, approved, source, gate):
    manifest = selection_manifest(store, record['manifest'], approved, source)
    plan = store.json(record['selection'])
    expected_names = sorted(n for n,t in manifest['tests'].items() if t['classification']=='cpu_correctness')
    require(len(expected_names) == 21 and plan.get('selected') == expected_names and
            plan.get('selected_count') == 21 and plan.get('manifest_sha256') == record['manifest']['sha256'] and
            plan.get('allow_gpu_correctness') is False and plan.get('tests_executed') is False and
            plan.get('full_protocol_prerequisites') is False and plan.get('policy') == manifest['policy'],
            'CPU selection plan coverage/identity mismatch')
    proof = validate_build(store, record['build_provenance'], source, record['executables_sha256'])
    require(record['build_provenance']['sha256'] == approved['cpu_build_provenance_sha256'][gate],
            'unapproved CPU build provenance')
    require(proof['build_type'] == ('Debug' if gate=='cpu_sanitize' else 'Release') and
            proof['sanitizers'] is (gate=='cpu_sanitize'), 'wrong CPU build/sanitizer configuration')
    build, source_dir = proof['build_dir'], proof['source_dir']
    def expand(pattern):
        return [approved['python'] if p=='@python' else
                p.replace('@source',source_dir).replace('@build',build) for p in pattern]
    all_names = sorted(manifest['cpu_build_tests'])
    commands = {n:expand(manifest['tests'][n]['command']) for n in all_names}
    executables = {Path(token).name for n in expected_names for token in commands[n]
                   if token.startswith(build+'/')}
    require(set(record['executables_sha256']) == executables and
            all(proof['outputs_sha256'][n] == value for n,value in record['executables_sha256'].items()),
            'CPU executable coverage/identity mismatch')
    metadata = plan.get('build_metadata', {})
    require(metadata.get('build_dir') == build and metadata.get('test_names') == all_names and
            metadata.get('commands') == commands and plan.get('discovered_count') == len(all_names),
            'guarded build/command identity mismatch')
    declarations, properties = {}, {}
    registry = store.raw(proof['metadata']['CTestTestfile.cmake']).decode()
    for operation, args in statements(registry):
        require(args and args[0] in all_names, 'unreviewed retained registry')
        name = args[0]
        if operation=='add_test':
            require(name not in declarations and args[1:]==commands[name], 'modified/duplicate retained command')
            declarations[name] = args[1:]
        else:
            require(name in declarations and name not in properties and len(args)%2==0 and args[1]=='PROPERTIES',
                    'ambiguous retained properties')
            pairs = dict(zip(args[2::2],args[3::2]))
            expected = {k:v.replace('@source',source_dir).replace('@build',build)
                        for k,v in manifest['build_metadata']['test_properties'][name].items()}
            require(len(pairs)==(len(args)-2)//2 and pairs==expected, 'unsafe retained hooks/fixtures/properties')
            properties[name] = pairs
    require(sorted(declarations)==all_names and sorted(properties)==all_names and metadata.get('properties')==properties and
            metadata.get('files_sha256',{}).get('CTestTestfile.cmake')==proof['metadata']['CTestTestfile.cmake']['sha256'],
            'retained guarded registry mismatch')
    # Additional metadata must be independently retained; unknown generated files
    # cannot be smuggled into the plan. This does not rerun the guard or discovery.
    metadata_refs = record.get('guarded_metadata')
    require(isinstance(metadata_refs, dict) and set(metadata_refs)==set(metadata['files_sha256']) and
            set(metadata_refs) <= {'CTestTestfile.cmake','DartConfiguration.tcl'}, 'unreviewed guarded metadata')
    for name, ref in metadata_refs.items():
        require(ref['sha256']==metadata['files_sha256'][name], 'guarded metadata identity mismatch')
        raw = store.raw(ref)
        if name == 'DartConfiguration.tcl':
            # Reuse the static dashboard parser on verified private bytes. It
            # cannot evaluate CMake or execute dashboard commands.
            from ctest_build_guard import validate_dart
            with tempfile.TemporaryDirectory(prefix='mab-dart-snapshot-') as temporary:
                path = Path(temporary)/name; path.write_bytes(raw)
                require(source_dir == str(ROOT.resolve()),
                        'Dart source relocation requires independent metadata review')
                validate_dart(path,Path(build),manifest['build_metadata'])
    discovery = command(store.json(record['discovery']),
                        ['ctest','--test-dir',build,'-N','--show-only=json-v1'], source_dir)
    discovered = strict_json(discovery['stdout'])
    require(discovered.get('kind')=='ctestInfo' and discovered.get('version')==dict(major=1,minor=0) and
            isinstance(discovered.get('tests'),list), 'malformed retained discovery')
    tests = discovered['tests']
    require(len(tests)==len(all_names) and sorted(t.get('name','') for t in tests)==all_names,
            'missing/duplicate discovery tests')
    for test in tests:
        require(test.get('command')==commands[test['name']], 'discovered command substitution')
        props = test.get('properties',[])
        require(isinstance(props,list) and len({p['name'] for p in props})==len(props), 'duplicate discovery properties')
        for prop in props:
            name,value=prop['name'],prop.get('value')
            require((name=='WORKING_DIRECTORY' and value==build) or
                    (name in ['TIMEOUT','SKIP_RETURN_CODE'] and str(value)==properties[test['name']].get(name)),
                    'unsafe discovery dependency/fixture/property')
    expression = '^('+'|'.join(expected_names)+')$'
    argv = ['ctest','--test-dir',build,'--output-on-failure','-V','--parallel','1','-R',expression]
    require(plan.get('ctest_argv')==argv, 'CPU selection execution command mismatch')
    prefix = ['env','-u','ASAN_OPTIONS','-u','LSAN_OPTIONS','UBSAN_OPTIONS=halt_on_error=1'] if gate=='cpu_sanitize' else []
    result = command(store.json(record['command']), prefix+argv, source_dir)
    # Conditional no-leaks evidence is not silently accepted; unsupported retry
    # formats must get their own reviewed extension and original ptrace record.
    count = ctest_coverage(result['stdout']+'\n'+result['stderr'], expected_names)
    return dict(passed=count)


def timing_bundle(store, record, gate, context):
    files = record.get('raw_files')
    require(isinstance(files,dict) and files and 'run.json' in files and 'COMPLETE.json' in files,
            'missing timing raw bundle')
    # Copy the verified bytes to private files for existing read-only analyzers.
    # They cannot reread mutable original evidence between hashing and parsing.
    with tempfile.TemporaryDirectory(prefix='mab-evidence-snapshot-') as temporary:
        root = Path(temporary)
        for relative, reference in files.items():
            path = Path(relative)
            require(not path.is_absolute() and '..' not in path.parts and str(path)==relative,
                    'unsafe raw bundle path')
            raw = store.raw(reference)
            if path.suffix=='.json': strict_json(raw.decode())
            target = root/path; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(raw)
        meta = strict_json((root/'run.json').read_text())
        require(meta.get('run_kind')=='performance', 'synthetic/validation timing evidence cannot qualify')
        if gate=='pilot':
            from analyze_cpu_gpu import analyze
            require(meta.get('matrix_part')=='pilot', 'wrong timing evidence scope')
            source = strict_json((root/'source_review.json').read_text())
            build = strict_json((root/'build.json').read_text())
            require(digest(canonical(source['current_source_sha256']))==context['source_identity'] and
                    build.get('binary_sha256')==context['binary_identity'], 'pilot source/binary mismatch')
            report = analyze(root)
            require(report['complete'] and report['measured']==dict(successful=150,failed=0,interrupted=0,missing=0) and
                    report['warmups']==dict(successful=30,failed=0,interrupted=0,missing=0), 'incomplete pilot raw coverage')
            return dict(measured=150,warmups=30,failed=0,missing=0)
        from analyze_cuda_results import read_bundle
        meta, report = read_bundle(root)
        require(meta.get('gpu_name')=='Tesla T4' and (meta.get('compute_major'),meta.get('compute_minor'))==(7,5) and
                report['complete'] and not any(report[k] for k in
                ['failed_trials','missing_trials','failed_warmups','missing_warmups']), 'incomplete timing smoke')
        return dict(complete=True,correctness=True)


def record_coverage(store, name, reference, reviewed, source):
    record = store.json(reference)
    require(isinstance(record,dict) and type(record.get('schema_version')) is int and record['schema_version']==1 and
            record.get('kind')=='cpu_gpu_framework_record_v1' and record.get('gate')==name,
            'unsupported framework record schema: '+name)
    fields={'cpu_release':{'manifest','selection','build_provenance','executables_sha256','guarded_metadata','discovery','command'},
            'cpu_sanitize':{'manifest','selection','build_provenance','executables_sha256','guarded_metadata','discovery','command'},
            'gpu_prepared':{'command'},'production_gpu':{'command'},'workers':{'command'},
            'workspace':{'commands','environment'},'pilot':{'raw_files'},'timing_smoke':{'raw_files'},
            'independent_review':{'decision'}}
    require(name in fields and set(record)=={'schema_version','kind','gate','context'}|fields[name],
            'unknown/missing/contradictory framework record fields: '+name)
    require(record.get('context')==reviewed['context'], 'framework source/build/session context mismatch')
    if name in ['cpu_release','cpu_sanitize']:
        coverage = cpu_record(store,record,reviewed,source,name)
    elif name in ['timing_smoke','pilot']:
        coverage = timing_bundle(store,record,name,reviewed['context'])
    elif name=='independent_review':
        decision = store.json(record['decision'])
        require(decision==dict(schema_version=1,kind='independent_evidence_review_v1',accepted=True,
                              execution_authorized=False,context=reviewed['context']), 'review decision not accepted/current')
        coverage = dict(accepted=True)
    elif name=='workspace':
        from analyze_cpu_gpu import validate_resources
        refs = record.get('commands')
        require(isinstance(refs,list) and len(refs)==3, 'missing workspace size coverage')
        sizes=[]
        for ref in refs:
            result = command(store.json(ref),cwd=reviewed['source_dir'])
            value = strict_json(result['stdout']); n=value.get('size')
            require(set(value)=={'size','gpu_name','compute_major','compute_minor','prepared_query_bytes','adapter_query_bytes',
                    'free_device_bytes_before_buffers','prepared_diagnostic_cudaMalloc_requested_bytes',
                    'adapter_diagnostic_cudaMalloc_requested_bytes','combined_device_payload_bytes','known_host_peak_payload_bytes',
                    'total_device_bytes','driver_api_version','runtime_api_version','workspace_policy_cap_each_bytes',
                    'allocation_observation','production_workspace_observation'} and
                    value['runtime_api_version']>=13000 and value['driver_api_version']>=13000 and
                    value['total_device_bytes']>=value['free_device_bytes_before_buffers'] and
                    value['workspace_policy_cap_each_bytes']==64*1024**2 and
                    value['allocation_observation']=='successful diagnostic cudaMalloc request sizes; allocator physical footprint not measured' and
                    value['production_workspace_observation']=='not instrumented; isolated same-parameter sizing query only',
                    'unsupported/contradictory workspace schema')
            require(type(n) is int and n in [1025,65537,1000000] and n not in sizes, 'duplicate/invalid workspace size')
            command(result,[str(Path(reviewed['build_dir'])/'cpu_gpu_comparison'),'--resources',str(n)])
            validate_resources(value,n);sizes.append(n)
        require(sorted(sizes)==[1025,65537,1000000], 'missing workspace coverage')
        from run_cpu_gpu_pilot import environment_gate
        environment_gate(store.json(record['environment']))  # Retained snapshot only; never calls snapshot().
        coverage = dict(sizes=sorted(sizes),all_limits_passed=True)
    else:
        executable = {'gpu_prepared':'test_cuda_prepared_correctness','workers':'test_parallel_workers',
                      'production_gpu':'test_cuda_sorting'}.get(name)
        require(executable is not None, 'unknown framework gate')
        result = command(store.json(record['command']),[str(Path(reviewed['build_dir'])/executable)],reviewed['source_dir'])
        value = strict_json(result['stdout'])
        if name=='production_gpu':
            from validate_cuda_sort import verify_result
            value=verify_result(value)
            require((value['compute_major'],value['compute_minor'])==(7,5), 'wrong production correctness device')
            coverage=dict(inputs=value['cases'],output_checks=value['output_checks'])
        elif name=='gpu_prepared':
            require(value==dict(schema_version=1,artifact_kind='correctness_validation',scope='prepared_cuda_untimed_v1',
                study_eligible=False,status='passed',inputs=163,output_checks=489,invalid_operations_rejected=489,failures=0),
                'incomplete/failed prepared correctness')
            coverage=dict(inputs=value['inputs'],output_checks=value['output_checks'],failures=value['failures'])
        else:
            from cpu_gpu_protocol import load_protocol
            required_environment = load_protocol()['openmp_policy']['environment']
            require(all(value.get('environment',{}).get(k)==v for k,v in required_environment.items()),
                    'worker environment mismatch')
            require(set(value)=={'schema_version','artifact_kind','scope','study_eligible','status','executable','build_type',
                    'compiler','flags','sanitizers','openmp_version','openmp_flags','runtime_dynamic','runtime_thread_limit',
                    'requested_threads','team_size_is_task_participation','environment','calls','output_checks'} and
                    isinstance(value['compiler'],str) and value['compiler'] and value['flags'].split()==['-O3','-DNDEBUG'] and
                    value['openmp_flags']=='-fopenmp' and value['openmp_version']=='4.5', 'unsupported worker schema/toolchain')
            require(value.get('schema_version')==1 and value.get('scope')=='openmp_workers_untimed_v1' and
                    value.get('artifact_kind')=='correctness_validation' and value.get('study_eligible') is False and
                    value.get('status')=='passed' and value.get('executable')==result['argv'][0] and
                    value.get('build_type')=='Release' and value.get('sanitizers') is False and
                    value.get('requested_threads')==2 and value.get('runtime_dynamic')==0 and
                    value.get('runtime_thread_limit')==2 and value.get('team_size_is_task_participation') is False,
                    'invalid worker runtime/build evidence')
            calls = value.get('calls'); require(isinstance(calls,list) and len(calls)==12, 'missing worker checks')
            expected = {(n,r) for n in [0,1,32767,32768,32769,65537] for r in [False,True]};seen=set()
            for call in calls:
                require(type(call.get('size')) is int and type(call.get('registry')) is bool, 'malformed worker call')
                key=(call['size'],call['registry']);parallel=call['size']>=32768
                require(key in expected and key not in seen and call.get('correctness') is True and
                        call.get('actual_team_size')==(2 if parallel else 1) and call.get('parallel_region') is parallel,
                        'duplicate/failed worker threshold evidence');seen.add(key)
            require(value.get('output_checks')==len(seen), 'worker check count mismatch')
            coverage=dict(output_checks=len(seen),threshold_team_verified=True)
    require(reference['sha256']==reviewed['record_sha256'].get(name), 'unapproved framework record identity: '+name)
    return coverage


def derived_claim(reference, coverage):
    # Pilot coverage contains its own zero missing count; merge explicitly rather
    # than passing duplicate keyword arguments to dict().
    return dict(dict(status='passed',exit_code=0,skipped=0,missing=0,sha256=reference['sha256']),**coverage)


def validate_full(prerequisite, store, source, identity):
    reviewed = approval()
    context = reviewed.get('context')
    require(isinstance(context,dict) and context==dict(
        session_id=prerequisite.get('session_id'),source_identity=digest(canonical(source)),
        build_identity=digest(canonical(identity)),binary_identity=identity['files_sha256']['cpu_gpu_comparison'],
        freeze_sha256=TRUSTED_FREEZE_SHA256), 'independent current context mismatch')
    require(reviewed.get('build_dir')==identity['build_dir'] and reviewed.get('source_dir')==identity['source_dir'],
            'independent build directory mismatch')
    ref = prerequisite.get('build_provenance')
    require(isinstance(ref,dict) and ref.get('sha256')==reviewed.get('build_provenance_sha256') and
            identity.get('build_provenance',{}).get('sha256')==ref['sha256'], 'missing/unapproved build provenance')
    from cpu_gpu_build_identity import EXECUTABLES
    outputs = {n:identity['files_sha256'][n] for n in EXECUTABLES+('libmab_parallel.a','libmab_cuda_timing.a')}
    proof=validate_build(store,ref,source,outputs,identity['build_dir'])
    require(proof['build_type']=='Release' and proof['sanitizers'] is False and
            all(proof['metadata'][n]['sha256']==identity['files_sha256'][n] for n in proof['metadata']),
            'build metadata provenance mismatch')
    parent,_ = trusted_policy();names=parent['required_records']['full_study_prerequisites']
    references=prerequisite['framework_records'];artifact=prerequisite['framework_validation']
    require(set(references)==set(names) and set(reviewed.get('record_sha256',{}))==set(names), 'framework record inventory mismatch')
    require(len({r['file'] for r in references.values()})==len(names), 'duplicate framework record aliases')
    derived={}
    for name in names:
        coverage=record_coverage(store,name,references[name],reviewed,source)
        claimed=artifact['records'][name]
        expected=derived_claim(references[name],coverage)
        require(canonical(claimed)==canonical(expected), 'coverage assertion unsupported by actual record: '+name)
        derived[name]=expected
    # Legacy records must be the same command bytes inspected by the strict CPU
    # and production records; wrappers cannot validate one log and execute another.
    for legacy,name in [('cpu_release_ctest','cpu_release'),('cpu_sanitize_ctest','cpu_sanitize'),('cuda_correctness','production_gpu')]:
        record=store.json(references[name])
        require(prerequisite['records'][legacy]==record['command'], 'legacy/strict command evidence conflict')
    legacy=prerequisite['records']
    require(set(legacy)=={'cpu_release_ctest','cpu_sanitize_ctest','cuda_ctest','cuda_correctness','preflight'} and
            legacy==reviewed.get('legacy_records'), 'unapproved/ambiguous legacy command identities')
    for reference in legacy.values():
        command(store.json(reference),cwd=reviewed['source_dir'])
    preflight=prerequisite.get('preflight_report')
    require(isinstance(preflight,dict) and preflight.get('sha256')==reviewed.get('preflight_report_sha256'),
            'missing/unapproved preflight report')
    report=store.json(preflight)
    require(isinstance(report,dict) and report.get('schema_version')==1 and
            report.get('protocol')=='cuda_preflight_v1' and report.get('record_kind')=='cuda_readiness' and
            report.get('source_sha256')=={p:source[p] for p in
                ['CMakeLists.txt','cmake/cuda.cmake','src/cuda/runtime_probe.cu','scripts/cuda_preflight.py']},
            'preflight source/schema mismatch')
    from cuda_preflight import classify as preflight_classify
    classification=preflight_classify(report['discovery'],report['probes'])
    require(classification==report.get('classification') and classification['state']=='operational' and
            classification['device0_kernel_verified'] is True, 'preflight probes do not support readiness')
    derived_artifact=dict(artifact,records=derived)
    return classify(derived_artifact,dict(context,record_sha256={n:r['sha256'] for n,r in references.items()}))
