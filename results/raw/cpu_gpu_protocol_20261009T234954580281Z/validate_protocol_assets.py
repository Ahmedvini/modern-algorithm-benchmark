"""Host-only static protocol validation, not a CPU/GPU benchmark driver."""
import copy,csv,hashlib,importlib.util,json,math,tempfile,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
MATRIX=Path('docs/studies/cpu_gpu_comparison_v1.matrix.json')
MODEL=json.loads(MATRIX.read_text())
BACKENDS={'cpu_std_sort','cpu_merge_sort','cpu_parallel_merge_sort_t2','gpu_cub_adapter','gpu_cub_prepared'}
SEEDED={'uniform','sorted','reverse_sorted','duplicate_heavy','nearly_sorted'}

def canonical(v):
    return json.dumps(v,ensure_ascii=True,allow_nan=False,separators=(',',':'),sort_keys=True).encode('ascii')

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def validate(m):
    if m['protocol']!='cpu_gpu_comparison_v1' or m['schema_version']!=1:
        raise ValueError('Wrong protocol/schema')
    if m['execution_authorized'] is not False or m['comparison_implementation']!='not_implemented':
        raise ValueError('Planning asset misrepresents readiness')
    if m['warmups']!=1 or m['repetitions']!=5 or m['max_size']!=1000000:
        raise ValueError('Outside frozen repetitions/size contract')
    modes={b['id']:b for b in m['backend_modes']}
    if len(m['backend_modes'])!=5 or set(modes)!=BACKENDS:raise ValueError('Invalid modes')
    for name,mode in modes.items():
        scope='cuda_sort_timing_v1_four_metrics' if name=='gpu_cub_prepared' else 'host_vector_api_call_v1'
        if mode['scope']!=scope:raise ValueError('Incompatible timing scope')
    if m['dependency']['commit']!='f19d875da0d8bfb2e38c109b2b40522b8abbbbc3' or m['dependency']['cub_version']!=300001:
        raise ValueError('Pin changed')
    if m['timing_scopes']['allowed_ratio_denominator']!='gpu_cub_adapter':raise ValueError('Incompatible ratio')
    for kind,ns,ds,seeds in [('study',[1025,65537,1000000],SEEDED|{'signed_edges'},[1729,42,2718]),
                              ('pilot',[1025,1000000],{'uniform','duplicate_heavy','signed_edges'},[1729])]:
        cells=m[kind]['cells'];seen=set();identities=set();actual=set()
        for c in cells:
            r=c['recipe'];n=r['size'];d=r['distribution'];s=r['seed']
            if type(n)is not int or n not in ns or d not in ds or s not in seeds:raise ValueError('Invalid recipe')
            if d=='signed_edges' and s!=1729:raise ValueError('Fake seed replication')
            if r['key_type']!='signed_int32' or r['duplicate_cardinality']!=16:raise ValueError('Invalid input type/domain')
            if r['nearly_sorted_swaps']!=(n//100 if d=='nearly_sorted' else 0):raise ValueError('Wrong swap count')
            if r['dataset_generator']!=('signed_edges_v1' if d=='signed_edges' else 'mt19937_64_v1'):raise ValueError('Generator mismatch')
            dataset=hashlib.sha256(canonical(r)).hexdigest()
            if c['dataset_id']!=dataset or dataset in seen:raise ValueError('Duplicate/mismatched dataset')
            seen.add(dataset);actual.add((n,d,s))
            base=sorted(BACKENDS,key=lambda b:(hashlib.sha256(f'314159|{dataset}|{b}'.encode()).hexdigest(),b))
            if c['warmup_order']!=[base] or c['measure_order']!=[base[i:]+base[:i] for i in range(5)]:
                raise ValueError('Order mismatch')
            for phase,orders in [('warmup',c['warmup_order']),('measure',c['measure_order'])]:
                for trial,order in enumerate(orders):
                    for backend in order:
                        identity=(dataset,backend,phase,trial)
                        if identity in identities:raise ValueError('Duplicate trial')
                        identities.add(identity)
        expected={(n,d,s) for n in ns for d in ds for s in ([1729] if d=='signed_edges' else seeds)}
        if actual!=expected:raise ValueError('Incomplete matrix')
        if cells!=sorted(cells,key=lambda c:(hashlib.sha256(f'314159|{c["dataset_id"]}'.encode()).hexdigest(),c['dataset_id'])):
            raise ValueError('Dataset order mismatch')
        counts=m[kind]['expected'];count=len(expected)
        independently_counted={'datasets':count,'backend_configurations':count*5,'measured_invocations':count*25,
            'warmup_invocations':count*5,'primary_measured_rows':count*20,'primary_warmup_rows':count*4,
            'prepared_measured_rows':count*5,'prepared_warmup_rows':count,'measured_prepared_metric_values':count*20,
            'total_invocations':len(identities),'paired_primary_ratios':count*3}
        if counts!=independently_counted:raise ValueError('Trial count mismatch')
    return True

class ProtocolTests(unittest.TestCase):
    def test_complete_frozen_matrix(self):self.assertTrue(validate(MODEL))
    def test_manual_totals(self):
        self.assertEqual(MODEL['study']['expected']['datasets'],48)
        self.assertEqual(MODEL['study']['expected']['measured_invocations'],1200)
        self.assertEqual(MODEL['study']['expected']['warmup_invocations'],240)
        self.assertEqual(MODEL['pilot']['expected']['total_invocations'],180)
    def test_balanced_five_rounds(self):
        for cell in MODEL['study']['cells']:
            for position in range(5):
                self.assertEqual({r[position] for r in cell['measure_order']},BACKENDS)
    def test_pilot_is_strict_subset(self):
        a={c['dataset_id'] for c in MODEL['pilot']['cells']};b={c['dataset_id'] for c in MODEL['study']['cells']}
        self.assertTrue(a<b);self.assertFalse(MODEL['pilot']['reuse_in_study'])
    def test_reject_duplicate_or_missing_dataset(self):
        for operation in ('duplicate','missing'):
            m=copy.deepcopy(MODEL)
            if operation=='duplicate':m['study']['cells'].append(copy.deepcopy(m['study']['cells'][0]))
            else:m['study']['cells'].pop()
            with self.assertRaises(ValueError):validate(m)
    def test_reject_oversize_or_wrong_protocol(self):
        for operation in ('size','protocol','repetitions'):
            m=copy.deepcopy(MODEL)
            if operation=='size':m['study']['cells'][0]['recipe']['size']=1000001
            elif operation=='protocol':m['protocol']='unreviewed'
            else:m['repetitions']=4
            with self.assertRaises(ValueError):validate(m)
    def test_reject_scope_or_dependency_change(self):
        for operation in ('scope','pin','ratio'):
            m=copy.deepcopy(MODEL)
            if operation=='scope':m['backend_modes'][0]['scope']='device_sort'
            elif operation=='pin':m['dependency']['cub_version']=300000
            else:m['timing_scopes']['allowed_ratio_denominator']='gpu_cub_prepared'
            with self.assertRaises(ValueError):validate(m)
    def test_reject_false_completion_or_order(self):
        for operation in ('completion','order'):
            m=copy.deepcopy(MODEL)
            if operation=='completion':m['execution_authorized']=True
            else:m['study']['cells'][0]['measure_order'][0].reverse()
            with self.assertRaises(ValueError):validate(m)
    def test_resource_formulas_and_unknowns(self):
        with Path('docs/studies/cpu_gpu_comparison_v1.resources.csv').open(newline='') as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),3)
        for r in rows:
            n=int(r['size'])
            self.assertEqual(int(r['known_host_peak_payload_bytes']),4*n*(3+2+1))
            self.assertEqual(int(r['combined_device_planning_cap_bytes']),4*n*(2+2)+2*64*1024**2)
            self.assertEqual(r['adapter_workspace_bytes'],'unknown_requires_query')
            self.assertEqual(r['prepared_workspace_current_bytes'],'unknown_requires_query')
        self.assertEqual(int(rows[-1]['known_host_peak_payload_bytes']),24000000)
        self.assertEqual(int(rows[-1]['combined_device_planning_cap_bytes']),150217728)
        self.assertEqual(rows[-1]['prepared_workspace_historical_bytes'],'')
    def test_statistical_units_and_gates(self):
        s=MODEL['statistics']
        self.assertEqual(s['cross_dataset_weight'],'equal per distinct input_sha256')
        self.assertFalse(s['warmups_in_statistics']);self.assertIsNone(s['confidence_intervals'])
        self.assertEqual(s['outlier_policy'],'retain_all')
        self.assertTrue(MODEL['launch_gates']['review_before_study'])
        self.assertFalse(MODEL['launch_gates']['current_session_verified'])
    def test_source_anchors_match(self):
        for p,h in MODEL['source_at_freeze_sha256'].items():self.assertEqual(digest(p),h,p)
    def test_freeze_hashes_and_schema(self):
        freeze=json.loads(Path('docs/studies/cpu_gpu_comparison_v1.freeze.json').read_text())
        self.assertEqual(len(freeze['files_sha256']),3)
        for p,h in freeze['files_sha256'].items():self.assertEqual(digest(p),h,p)
        fields=MODEL['primary_schema']['csv_fields']
        self.assertEqual(len(fields),31);self.assertEqual(len(fields),len(set(fields)))
        self.assertEqual(MODEL['primary_schema']['status'],'specified_not_implemented')
    def test_byte_for_byte_regeneration(self):
        spec=importlib.util.spec_from_file_location('protocol_builder',HERE/'build_protocol_assets.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(prefix='mab_protocol_check_') as temp:
            output=Path(temp)/'assets';module.write(output)
            for suffix in ['matrix.json','resources.csv']:
                self.assertEqual(Path('docs/studies/cpu_gpu_comparison_v1.'+suffix).read_bytes(),
                                 (output/('cpu_gpu_comparison_v1.'+suffix)).read_bytes())
    def test_runtime_model_is_estimate(self):
        for section in ('pilot','study'):
            estimate=MODEL['estimation'][section]
            self.assertEqual(estimate['kind'],'planning_model_not_measurement')
            self.assertTrue(math.isfinite(estimate['model_seconds']))
            self.assertEqual(estimate['contingency_budget_seconds'],4*estimate['model_seconds'])
        self.assertAlmostEqual(MODEL['estimation']['study']['model_seconds'],158.09991629182707)

if __name__=='__main__':unittest.main(verbosity=2)
