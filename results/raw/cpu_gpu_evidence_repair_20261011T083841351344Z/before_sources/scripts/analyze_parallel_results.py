#!/usr/bin/env python3
"""Strict parallel timing validation and paired, dataset-level scaling analysis."""
import argparse
import csv
import json
from pathlib import Path
import statistics
from analyze_results import FIELDS as BASE_FIELDS, integer, summarize_samples
from experiment_model import load_json, save_json, sha256, tree_hashes

PROTOCOL='parallel_sort_timing_v1'
FIELDS=BASE_FIELDS+['implementation_version','requested_threads','actual_threads','parallel_region']
ALGORITHMS=['merge_sort','parallel_merge_sort']


def stats(values):
    return dict(count=len(values),median=statistics.median(values) if values else None,
                mean=statistics.mean(values) if values else None,
                sample_stdev=statistics.stdev(values) if len(values)>1 else None,
                minimum=min(values) if values else None,maximum=max(values) if values else None)


def read_bundle(path, allow_incomplete=False):
    if path.is_symlink():raise ValueError('symlink bundle rejected')
    m=load_json(path/'run.json')
    if m['protocol']!=PROTOCOL or m['schema_version']!=1 or m['algorithms']!=ALGORITHMS:
        raise ValueError('incompatible parallel bundle')
    if type(m['parallel_threads']) is not int or not 1<=m['parallel_threads']<=64:
        raise ValueError('invalid configured threads')
    if m['parallel_threshold']!=32768 or m['task_grain']!=16384 or m['openmp_macro']<=0:
        raise ValueError('implementation contract differs')
    if not 1<=m['repetitions']<=10000 or not 0<=m['warmups']<=1000:raise ValueError('invalid rounds')
    for sidecar in ['source_hashes.json','compile_commands.json','CMakeCache.txt','pdqsort_upstream.json','timsort_upstream.json']:
        if not (path/sidecar).is_file():raise ValueError('missing provenance: '+sidecar)
    rows=[];seen=set();failed=False
    with (path/'trials.csv').open(newline='',encoding='utf-8') as stream:
        reader=csv.DictReader(stream,strict=True)
        if reader.fieldnames!=FIELDS:raise ValueError('parallel CSV schema mismatch')
        for row in reader:
            if failed or set(row)!=set(FIELDS) or any(v is None for v in row.values()):raise ValueError('malformed/fail-fast rows')
            if row['protocol']!=PROTOCOL or row['schema_version']!='1' or row['elapsed_unit']!='ns':raise ValueError('protocol/unit mismatch')
            for key in ['run_id','run_kind','distribution','size','seed','nearly_sorted_swaps','duplicate_cardinality','dataset_generator',
                        'input_hash_fnv1a64','repetitions','warmups','compiler_id','compiler_version','build_type','platform','architecture']:
                if row[key]!=str(m[key]):raise ValueError('metadata mismatch: '+key)
            if row['sanitizers']!=str(m['sanitizers']).lower():raise ValueError('sanitizer metadata mismatch')
            for key in ['size','seed','nearly_sorted_swaps','duplicate_cardinality','input_hash_fnv1a64','repetitions','warmups']:
                integer(row[key])
            if row['run_kind'] not in ['performance','validation'] or (row['run_kind']=='performance' and (m['build_type']!='Release' or m['sanitizers'])):
                raise ValueError('invalid performance build')
            index=len(rows);warm=m['warmups']*2;phase='warmup' if index<warm else 'measure';offset_index=index if index<warm else index-warm
            trial=offset_index//2;order=offset_index%2
            if row['phase']!=phase or integer(row['trial_index'])!=trial or integer(row['execution_order'])!=order or trial>=(m['warmups'] if phase=='warmup' else m['repetitions']):
                raise ValueError('trial schedule mismatch')
            if row['algorithm']!=ALGORITHMS[(m['seed']%2+trial%2+order)%2]:raise ValueError('algorithm order mismatch')
            identity=(phase,trial,row['algorithm'])
            if identity in seen:raise ValueError('duplicate trial identity')
            seen.add(identity)
            parallel=row['algorithm']=='parallel_merge_sort';request=m['parallel_threads'] if parallel else 1
            if integer(row['requested_threads'])!=request or row['implementation_version']!=('parallel_merge_sort_v1' if parallel else 'merge_sort_v1'):
                raise ValueError('implementation/request mismatch')
            if row['status']=='ok':
                if row['correctness']!='passed' or row['error']:raise ValueError('invalid successful correctness')
                integer(row['elapsed_ns']);actual=integer(row['actual_threads']);region=parallel and request>1 and m['size']>=32768
                if not 1<=actual<=request or row['parallel_region']!=str(region).lower() or (not region and actual!=1):raise ValueError('invalid actual team metadata')
            elif row['status']=='error':
                if row['correctness'] not in ['failed','not_checked'] or not row['error']:raise ValueError('missing failure diagnostic')
                if row['elapsed_ns']:integer(row['elapsed_ns'])
                failed=True
            else:raise ValueError('invalid status')
            rows.append(row)
    expected=2*(m['warmups']+m['repetitions']);complete=False
    if m['expected_measured_rows']!=2*m['repetitions'] or m['expected_warmup_rows']!=2*m['warmups']:raise ValueError('planned row mismatch')
    if (path/'COMPLETE.json').exists():
        done=load_json(path/'COMPLETE.json');complete=done.get('complete') is True and done.get('schema_version')==1 and done.get('rows')==expected
        if not complete or len(rows)!=expected or failed or (path/'FAILED.json').exists():raise ValueError('contradictory completion')
    if not complete and not allow_incomplete:raise ValueError('incomplete bundle')
    groups=[]
    for name in ALGORITHMS:
        selected=[r for r in rows if r['algorithm']==name and r['phase']=='measure'];ok=[r for r in selected if r['status']=='ok']
        group={k:m[k] for k in ['size','seed','distribution','input_hash_fnv1a64','parallel_threads','run_kind','compiler_id','compiler_version','build_type','sanitizers','platform','architecture']}
        group.update(algorithm=name,actual_threads=sorted({integer(r['actual_threads']) for r in ok}),
                     successful_trials=len(ok),failed_trials=len(selected)-len(ok),missing_trials=m['repetitions']-len(selected),
                     warmup_rows=sum(r['phase']=='warmup' and r['algorithm']==name for r in rows),
                     failed_warmups=sum(r['phase']=='warmup' and r['algorithm']==name and r['status']!='ok' for r in rows),
                     missing_warmups=m['warmups']-sum(r['phase']=='warmup' and r['algorithm']==name for r in rows),
                     timing_ns=summarize_samples([integer(r['elapsed_ns']) for r in ok]),source_csv=str(path/'trials.csv'))
        if len(group['actual_threads'])>1:raise ValueError('mixed actual teams require separate configurations')
        groups.append(group)
    return m,rows,groups,complete


def analyze(source,allow_incomplete=False):
    source=Path(source).resolve();plan=load_json(source/'matrix.json')
    if plan['protocol']!=PROTOCOL or plan['schema_version']!=1:raise ValueError('incompatible matrix')
    from run_parallel_matrix import make_plan
    cases=plan['cases'];config=plan['configuration']
    rebuilt=make_plan(config,Path(plan['binary']),source,Path(plan['processed_path']),Path(plan['figure_path']))
    if plan!=rebuilt:raise ValueError('matrix plan/configuration fingerprint differs')
    expected=[dict(size=n,seed=s,distribution=d,threads=p) for n in config['sizes'] for s in config['seeds'] for d in config['distributions'] for p in config['threads']]
    if cases!=expected or len(cases)!=len(plan['commands']) or len(cases)!=len(plan['runs']) or len(set(plan['runs']))!=len(cases):raise ValueError('matrix coverage mismatch')
    if any(Path(n).name!=n or n in ['.','..'] for n in plan['runs']):raise ValueError('invalid bundle path')
    if {p.name for p in source.iterdir() if p.is_dir()}!=set(n for n in plan['runs'] if (source/n).is_dir()):raise ValueError('extra bundle')
    protocol=load_json(source/'protocol.json')
    if sha256(source/'PROTOCOL_v1.md')!=protocol['sha256']:raise ValueError('protocol hash differs')
    collected=(source/'COLLECTED.json').exists()
    if collected:
        c=load_json(source/'COLLECTED.json')
        if c.get('complete') is not True or c.get('runs')!=len(cases):raise ValueError('invalid collection marker')
    complete=collected and not (source/'FAILED.json').exists() and not (source/'INTERRUPTED.json').exists();groups=[];observations=[];missing=[];commands=[];input_hashes={};build_id=None
    for index,(name,case,command) in enumerate(zip(plan['runs'],cases,plan['commands'])):
        result_path=source/(name+'_command.json');result=load_json(result_path) if result_path.exists() else None
        if result and (result['command']!=command or type(result['exit_code']) not in [int,type(None)]):raise ValueError('command metadata mismatch')
        command_ok=result is not None and result['status']=='successful' and result['exit_code']==0
        commands.append(dict(run=name,status=result['status'] if result else 'missing',exit_code=result['exit_code'] if result else None))
        if not command_ok:complete=False
        if not (source/name/'run.json').exists():missing.append(name);complete=False;continue
        m,rows,cell,done=read_bundle(source/name,allow_incomplete)
        for k in ['size','seed','distribution']:
            if m[k]!=case[k]:raise ValueError('matrix/bundle workload differs')
        expected_swaps=0 if case['distribution']=='sorted' else case['size']//100
        if m['parallel_threads']!=case['threads'] or m['repetitions']!=config['repetitions'] or m['warmups']!=config['warmups'] or m['duplicate_cardinality']!=config['distinct'] or m['nearly_sorted_swaps']!=expected_swaps or m['invocation']!=command:
            raise ValueError('matrix/bundle configuration differs')
        identity=(case['size'],case['seed'],case['distribution']);fingerprint=m['input_hash_fnv1a64']
        if identity in input_hashes and input_hashes[identity]!=fingerprint:raise ValueError('thread cases received different data')
        input_hashes[identity]=fingerprint
        signature=(m['compiler_id'],m['compiler_version'],m['build_type'],m['sanitizers'],m['openmp_flags'],m['openmp_runtime_libraries'],sha256(source/name/'source_hashes.json'),sha256(source/name/'compile_commands.json'))
        if build_id is not None and signature!=build_id:raise ValueError('incompatible build identity')
        build_id=signature
        if config['require_requested_teams']:
            for row in rows:
                if row['status']=='ok' and row['parallel_region']=='true' and row['actual_threads']!=row['requested_threads']:raise ValueError('runtime contracted a required study team')
        complete=complete and done;groups.extend(cell)
        observations.extend(dict(source_csv=str(source/name/'trials.csv'),row_index=i,raw=row) for i,row in enumerate(rows))
    marker_path=source/'COMPLETE.json'
    if marker_path.exists():
        marker=load_json(marker_path);current=tree_hashes(source);current.pop('COMPLETE.json',None)
        if marker.get('complete') is not True or marker.get('runs')!=len(cases) or marker.get('raw_sha256')!=current or not complete or (source/'FAILED.json').exists() or (source/'INTERRUPTED.json').exists():raise ValueError('matrix completion/hash contradiction')
    elif not collected and not allow_incomplete:raise ValueError('incomplete matrix')
    if not complete and not allow_incomplete:raise ValueError('incomplete matrix')
    lookup={(g['size'],g['seed'],g['distribution'],g['parallel_threads'],g['algorithm']):g for g in groups}
    ratios=[]
    for g in groups:
        if g['algorithm']!='parallel_merge_sort':continue
        key=(g['size'],g['seed'],g['distribution']);p=g['parallel_threads'];seq=lookup.get((*key,p,'merge_sort'));one=lookup.get((*key,1,'parallel_merge_sort'))
        valid=g['size']>=32768 and g['actual_threads']==[p] and all(x is not None and x['missing_trials']==x['failed_trials']==0 and x['timing_ns']['median_ns']>0 for x in [g,seq,one])
        par=g['timing_ns']['median_ns'];s=seq['timing_ns']['median_ns']/par if valid else None;i=one['timing_ns']['median_ns']/par if valid else None
        ratios.append(dict(size=g['size'],seed=g['seed'],distribution=g['distribution'],input_hash_fnv1a64=g['input_hash_fnv1a64'],threads=p,
                           algorithmic_speedup=s,parallel_one_thread_speedup=i,algorithmic_efficiency=s/p if valid else None,
                           parallel_one_thread_efficiency=i/p if valid else None,parallel_median_ns=par,
                           unavailable_reason=None if valid else 'requires above-threshold complete positive medians, request1 baseline and exact observed team'))
    cross=[]
    for key in sorted({(g['size'],g['distribution'],g['threads']) for g in ratios}):
        entries=[g for g in ratios if (g['size'],g['distribution'],g['threads'])==key];units={}
        for g in entries:units.setdefault(g['input_hash_fnv1a64'],[]).append(g)
        row=dict(size=key[0],distribution=key[1],threads=key[2],declared_datasets=len(entries),distinct_inputs=len(units),unavailable_datasets=sum(g['unavailable_reason'] is not None for g in entries))
        for metric in ['algorithmic_speedup','parallel_one_thread_speedup','algorithmic_efficiency','parallel_one_thread_efficiency','parallel_median_ns']:
            samples=[statistics.median([g[metric] for g in bucket if g[metric] is not None]) for bucket in units.values() if any(g[metric] is not None for g in bucket)]
            row[metric]=stats(samples)
        cross.append(row)
    missing_trials=len(missing)*2*config['repetitions']+sum(g['missing_trials'] for g in groups)
    return dict(schema_version=1,protocol=PROTOCOL,source=str(source),complete=complete,configuration=config,build_identity=build_id,
                successful_measured=sum(g['successful_trials'] for g in groups),failed_measured=sum(g['failed_trials'] for g in groups),missing_measured=missing_trials,
                warmup_rows=sum(g['warmup_rows'] for g in groups),failed_warmups=sum(g['failed_warmups'] for g in groups),
                missing_warmups=len(missing)*2*config['warmups']+sum(g['missing_warmups'] for g in groups),missing_configurations=missing,
                commands=commands,groups=groups,dataset_ratios=ratios,cross_dataset=cross,
                aggregation='Within-dataset medians, ratios before equal-weight distinct-input summaries; all outliers retained; SD ddof1; no confidence interval.'),observations


def render(summary,source,output,figures):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    matplotlib.rcParams.update({'svg.hashsalt':PROTOCOL,'font.family':'DejaVu Sans','pdf.fonttype':42})
    figures.mkdir(exist_ok=False);entries=[]
    for distribution in summary['configuration']['distributions']:
        selected=[g for g in summary['cross_dataset'] if g['distribution']==distribution]
        for metric,unit in [('parallel_median_ns','ms'),('algorithmic_speedup','Sequential Merge Sort / parallel'),('parallel_one_thread_speedup','Parallel one-thread / parallel'),('algorithmic_efficiency','Sequential-baseline speedup / actual team size')]:
            fig,ax=plt.subplots(figsize=(7,4.5));points=[]
            for n in summary['configuration']['sizes']:
                rows=[g for g in selected if g['size']==n and g[metric]['median'] is not None];rows.sort(key=lambda g:g['threads'])
                if not rows:continue
                factor=1e-6 if metric=='parallel_median_ns' else 1
                x=[g['threads'] for g in rows];y=[g[metric]['median']*factor for g in rows]
                lo=[(g[metric]['median']-g[metric]['minimum'])*factor for g in rows];hi=[(g[metric]['maximum']-g[metric]['median'])*factor for g in rows]
                ax.errorbar(x,y,yerr=[lo,hi],marker='o',capsize=3,label=f'N={n}; datasets={rows[0][metric]["count"]}')
                points.extend(dict(size=n,threads=g['threads'],statistics=g[metric]) for g in rows)
            ax.set(xlabel=('Requested threads; below threshold executes serial1' if metric=='parallel_median_ns' else 'Requested = observed team size; parallel request1 is serial'),ylabel=unit,ylim=(0,None),title=f'{distribution}: median of dataset summaries; min–max spread')
            ax.set_xticks(summary['configuration']['threads']);ax.grid(alpha=.2)
            if points:ax.legend(fontsize=8)
            else:ax.text(.5,.5,'Scaling metric unavailable for this workload',ha='center',transform=ax.transAxes)
            fig.tight_layout();name=distribution+'_'+metric;outputs={}
            for fmt in ['svg','pdf']:
                file=name+'.'+fmt;fig.savefig(figures/file,metadata={'Date':None,'Creator':PROTOCOL} if fmt=='svg' else {'CreationDate':None,'ModDate':None,'Creator':PROTOCOL,'Producer':PROTOCOL});outputs[fmt]=file
            plt.close(fig);entries.append(dict(distribution=distribution,metric=metric,unit=unit,points=points,outputs=outputs))
    save_json(figures/'plot_manifest.json',dict(protocol=PROTOCOL,source_sha256={k:v for k,v in tree_hashes(source).items() if k not in ['COMPLETE.json','analysis_command.json','final_resources.json']},summary_sha256=sha256(output/'summary.json'),matplotlib_version=matplotlib.__version__,figures=entries,output_sha256=tree_hashes(figures)))
    lines=['# OpenMP scaling report','',f'Complete: {summary["complete"]}. Measured successes {summary["successful_measured"]}; failed {summary["failed_measured"]}; missing {summary["missing_measured"]}; warmups {summary["warmup_rows"]}.',
           '', 'Sequential merge_sort is the primary baseline; parallel request1 is a separate implementation baseline. Ratios use within-dataset medians before equal weighting distinct input fingerprints. Min/max spreads are not confidence intervals. All outliers retained.',
           '', '| N | Distribution | Threads | Datasets | Sequential-baseline speedup median / min / max | Efficiency median | Parallel1 speedup median |', '|---:|---|---:|---:|---|---:|---:|']
    def f(x):return 'unavailable' if x is None else format(x,'.6g')
    for row in summary['cross_dataset']:
        s=row['algorithmic_speedup'];lines.append(f'| {row["size"]} | {row["distribution"]} | {row["threads"]} | {s["count"]} | {f(s["median"])} / {f(s["minimum"])} / {f(s["maximum"])} | {f(row["algorithmic_efficiency"]["median"])} | {f(row["parallel_one_thread_speedup"]["median"])} |')
    lines+=['','## Environment','```json',json.dumps(load_json(source/'environment.json'),indent=2,sort_keys=True),'```','',
            '## Limitations and reproduction','One shared Linux session, unpinned frequency/affinity/thermal/background load; fixed configuration order and odd-repetition cyclic imbalance. Serial parent merges limit parallelism. Actual team size is not a count of task-executing workers. No race-freedom, significance or universal superiority claim. No isolated memory/counting or CUDA/100M experiment.',
            '','Full ns statistics, failures and every raw row remain in summary.json/observations.jsonl. Plot stack/points/source hashes are in plot_manifest.json. Regenerate to new paths:',
            f'`python3 scripts/analyze_parallel_results.py {source} --output NEW_PROCESSED --figures NEW_FIGURES`','']
    with (output/'REPORT.md').open('x') as stream:stream.write('\n'.join(lines))


def write_analysis(source,output,figures,allow_incomplete=False):
    source=Path(source).resolve();output=Path(output).absolute();figures=Path(figures).absolute()
    paths=[source,output.resolve(),figures.resolve()]
    if any(a==b or a in b.parents or b in a.parents for i,a in enumerate(paths) for b in paths[i+1:]):raise ValueError('overlapping outputs')
    if output.exists() or figures.exists() or output.is_symlink() or figures.is_symlink():raise FileExistsError('derived output exists')
    summary,rows=analyze(source,allow_incomplete);before=tree_hashes(source);output.mkdir(exist_ok=False)
    save_json(output/'summary.json',summary)
    with (output/'observations.jsonl').open('x') as stream:
        for row in rows:stream.write(json.dumps(row,sort_keys=True,allow_nan=False)+'\n')
    render(summary,source,output,figures)
    if tree_hashes(source)!=before:raise ValueError('raw mutated during analysis')
    save_json(output/('COMPLETE.json' if summary['complete'] else 'INCOMPLETE.json'),dict(complete=summary['complete'],files_sha256=tree_hashes(output),figures_sha256=tree_hashes(figures)))
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__,allow_abbrev=False);p.add_argument('source',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--figures',type=Path,required=True);p.add_argument('--allow-incomplete',action='store_true');args=p.parse_args()
    try:
        result=write_analysis(args.source,args.output,args.figures,args.allow_incomplete);print(args.output)
        if not result['complete']:p.exit(1,'partial analysis retained\n')
    except (OSError,ValueError,KeyError,TypeError,csv.Error) as error:p.exit(1,'analysis failed: '+str(error)+'\n')
if __name__=='__main__':main()
