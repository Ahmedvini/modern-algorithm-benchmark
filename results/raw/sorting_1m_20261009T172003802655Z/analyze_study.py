#!/usr/bin/env python3
"""Study-specific descriptive analysis; reuse the established strict raw parser."""
import argparse,csv,hashlib,itertools,json,statistics,sys
from pathlib import Path
root=Path.cwd();sys.path.insert(0,str(root/'scripts'))
from analyze_results import analyze,summarize_samples
SORTS=['std_sort','quick_sort','pdq_sort','tim_sort','merge_sort','radix_sort']
DISTS=['uniform','sorted','reverse_sorted','duplicate_heavy','nearly_sorted']
SEEDS=[1729,42,2718]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def seed_summary(groups):
    result=[]
    for algorithm,distribution in itertools.product(SORTS,DISTS):
        chosen=[g for g in groups if (g['algorithm'],g['distribution'])==(algorithm,distribution)]
        assert len(chosen)==3 and {g['seed'] for g in chosen}==set(SEEDS)
        assert all(g['size']==1000000 and g['successful_trials']==5 and g['failed_trials']==0 and g['missing_measured_trials']==0 and g['failed_warmups']==0 and g['run_complete'] for g in chosen)
        assert len({(g['compiler_id'],g['compiler_version'],g['build_type'],g['sanitizers'],g['platform'],g['architecture']) for g in chosen})==1
        medians=[next(g['median_ns'] for g in chosen if g['seed']==seed) for seed in SEEDS]
        result.append({'algorithm':algorithm,'distribution':distribution,'size':1000000,'dataset_count':3,'successful_trials':sum(g['successful_trials'] for g in chosen),'failed_trials':sum(g['failed_trials'] for g in chosen),'seed_medians_ns':[{'seed':s,'median_ns':v} for s,v in zip(SEEDS,medians)],'median_of_seed_medians_ns':statistics.median(medians),'mean_of_seed_medians_ns':statistics.mean(medians),'sample_stdev_of_seed_medians_ns':statistics.stdev(medians),'min_seed_median_ns':min(medians),'max_seed_median_ns':max(medians)})
    return result

def self_test():
    base={'size':1000000,'successful_trials':5,'failed_trials':0,'missing_measured_trials':0,'failed_warmups':0,'run_complete':True,'compiler_id':'fixture','compiler_version':'fixture','build_type':'Release','sanitizers':False,'platform':'fixture','architecture':'fixture'}
    groups=[dict(base,algorithm=a,distribution=d,seed=s,median_ns=m) for a,d in itertools.product(SORTS,DISTS) for s,m in zip(SEEDS,[10,20,30])]
    result=seed_summary(groups)
    assert len(result)==30 and all(g['median_of_seed_medians_ns']==20 and g['mean_of_seed_medians_ns']==20 and g['sample_stdev_of_seed_medians_ns']==10 and g['min_seed_median_ns']==10 and g['max_seed_median_ns']==30 and g['dataset_count']==3 and g['successful_trials']==15 for g in result)
    assert summarize_samples([10,20,30])=={'successful_trials':3,'median_ns':20,'mean_ns':20,'stdev_ns':10.0,'min_ns':10,'max_ns':30}
    for broken in [groups[:-1],groups+[groups[0]], [dict(g,seed=0) if i==0 else g for i,g in enumerate(groups)], [dict(g,failed_trials=1) if i==0 else g for i,g in enumerate(groups)]]:
        try:seed_summary(broken)
        except AssertionError:pass
        else:raise AssertionError('invalid dataset grouping accepted')
    print('Synthetic-only tests passed: known statistics, seed-unit aggregation, missing/duplicate/invalid-seed/failure rejection; no fixture observations written.')

def save(path,obj):
    with path.open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--self-test',action='store_true');parser.add_argument('--study',type=Path)
    args=parser.parse_args()
    if args.self_test:self_test();return
    assert args.study is not None
    raw=args.study.resolve();paths=json.loads((raw/'paths.json').read_text());matrix=Path(paths['matrix']);out=Path(paths['processed'])
    parsed=analyze(matrix)
    assert parsed==json.loads((out/'per_seed.json').read_text()) and parsed['complete'] and not parsed['missing_runs']
    groups=parsed['groups'];expected=set(itertools.product(SORTS,DISTS,SEEDS))
    assert len(groups)==90 and {(g['algorithm'],g['distribution'],g['seed']) for g in groups}==expected
    cross=seed_summary(groups)
    with (out/'per_seed.csv').open('x',newline='',encoding='utf-8') as f:
        fields=['algorithm','distribution','size','seed','successful_trials','failed_trials','missing_measured_trials','median_ns','mean_ns','stdev_ns','min_ns','max_ns']
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(groups)
    aggregate={'schema_version':1,'study':paths['study'],'source':str(matrix),'elapsed_unit':'ns','aggregation_unit':'one median per seed dataset','method':'equal-weight descriptive statistics of three five-trial seed medians; no pooled trial statistics','stdev_definition':'sample_ddof_1_across_seed_medians','outlier_policy':'retain_all','groups':cross}
    save(out/'cross_seed.json',aggregate)
    fields=['algorithm','distribution','size','dataset_count','successful_trials','failed_trials','median_of_seed_medians_ns','mean_of_seed_medians_ns','sample_stdev_of_seed_medians_ns','min_seed_median_ns','max_seed_median_ns']
    with (out/'cross_seed.csv').open('x',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(cross)
    lines=['# 1M sorting study: descriptive results','',f"Study: `{paths['study']}`.",'','15 configurations completed: 450 measured trials and 90 warm-ups, all passed; no failed or missing trials. Six sorters, N=1,000,000, five distributions, seeds 1729/42/2718.','', '## Cross-seed results','', 'Each row describes three dataset medians (five trials per seed). All rows have 15 successful trials, zero failed trials and three datasets. The standard deviation below is sample SD across three seed medians; min/max are the smallest/largest seed median, not the extremes of all 15 trials. Milliseconds = nanoseconds / 1,000,000; tables round to three decimals, JSON/CSV retain precision. No outliers removed and no significance test performed.','', '| Algorithm | Distribution | Median of medians (ms) | Mean of medians (ms) | Sample SD (ms) | Min median (ms) | Max median (ms) |','| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    keys=['median_of_seed_medians_ns','mean_of_seed_medians_ns','sample_stdev_of_seed_medians_ns','min_seed_median_ns','max_seed_median_ns']
    for g in cross:lines.append('| '+g['algorithm']+' | '+g['distribution']+' | '+' | '.join(f"{g[k]/1000000:.3f}" for k in keys)+' |')
    lines+=['','## Results by dataset seed','','All 90 rows below describe five repeated timings of one dataset, with successful/failed counts explicit. SD is sample SD across repetitions, and min/max retain every successful observation.','', '| Algorithm | Distribution | Seed | Successful | Failed | Median (ms) | Mean (ms) | Sample SD (ms) | Min (ms) | Max (ms) |','| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for g in groups:lines.append('| '+g['algorithm']+' | '+g['distribution']+' | '+str(g['seed'])+' | '+str(g['successful_trials'])+' | '+str(g['failed_trials'])+' | '+' | '.join(f"{g[k]/1000000:.3f}" for k in ['median_ns','mean_ns','stdev_ns','min_ns','max_ns'])+' |')
    lines+=['','## Interpretation and limitations','','These are descriptive observations on one shared Pop!_OS machine, GNU 13.3.0, Release -O3 -DNDEBUG, dynamically managed powersave frequency policy. Seeds vary data, while repeated timings reuse that data; trials are not independent datasets. Algorithm effects can depend on distribution, ordering, implementation, compiler and hardware. No universal ranking or statistical significance is asserted.','','CPU affinity, frequency, thermal state, cache state and background activity were not controlled. Input copying warms memory; algorithm-owned allocation is timed. No timer-overhead subtraction. No measured RSS or comparison-count study was run alongside these primary timings. The 16 MB array/workspace estimate is planning only, not measured algorithm memory.','','The immutable v1 protocol and environment snapshots are retained under the raw study directory. Per-seed statistics reuse scripts/analyze_results.py; the retained analyze_study.py verifies all groups and produces this table plus equal-weight cross-seed statistics. No sizes above 1M, CUDA or GPU workload was run.']
    with (out/'RESULTS.md').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
    print('Regenerated per-seed summary exactly; wrote 90 per-seed and 30 cross-seed groups, retained all observations.')
if __name__=='__main__':main()
