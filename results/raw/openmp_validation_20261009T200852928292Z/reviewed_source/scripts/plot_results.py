#!/usr/bin/env python3
"""Revalidate experiment raw data and generate deterministic SVG/PDF spread plots."""
import argparse
import csv
from collections import defaultdict
import json
from pathlib import Path

from experiment_model import (ALGORITHMS, FAMILIES, PROTOCOL, aggregate, canonical,
                              save_json, sha256, tree_hashes, validate_study)


def plot_summary(summary, validated, output):
    import matplotlib
    matplotlib.use('Agg',force=True)
    import matplotlib.pyplot as plt
    import numpy
    from matplotlib import font_manager
    output=Path(output);output.mkdir(exist_ok=False)
    rc={'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.labelsize':9,
        'legend.fontsize':8,'svg.hashsalt':PROTOCOL,'svg.fonttype':'none',
        'pdf.fonttype':42,'figure.dpi':150,'savefig.dpi':300,'axes.grid':True,'grid.alpha':0.2}
    sources={}
    raw=Path(validated['plan']['raw_path'])
    for family in FAMILIES:
        for name,digest in tree_hashes(raw/family).items() if (raw/family).is_dir() else []:
            sources[family+'/'+name]=digest
    for name in ['experiment.json','environment.json','PROTOCOL_v1.md','protocol.json']:
        if (raw/name).exists():sources[name]=sha256(raw/name)
    figures=[]
    groups=defaultdict(list)
    for group in summary['cross_dataset']:
        # Metadata changes create separate panels rather than incomparable pooling.
        key=tuple((f,canonical(group[f])) for f in ['family','operation','distribution','query_category','query_seed',
            'structure_seed','batch_size','run_kind','compiler_id','compiler_version','build_type','sanitizers',
            'platform','architecture','source_manifest_sha256','cmake_flags_sha256','duplicate_cardinality'])
        groups[key].append(group)
    config=validated['plan']['configuration']
    all_algorithms=[a for family in FAMILIES for a in ALGORITHMS[family]]
    colors={a:plt.get_cmap('tab20')(i) for i,a in enumerate(all_algorithms)}
    with plt.rc_context(rc):
        for key,values in sorted(groups.items(),key=lambda pair:canonical(pair[0])):
            filters={k:json.loads(v) for k,v in key}
            family=filters['family'];operation=filters['operation'];category=filters['query_category']
            lookup=operation=='lookup';scale=1/filters['batch_size'] if lookup else 1/1000000
            metric='normalized batch-average ns/query' if lookup else 'construction ms' if operation=='build' else 'sorting ms'
            for spread in ['dataset_median_range','measured_trial_range']:
                fig,ax=plt.subplots(figsize=(7.2,4.8));points=[];ids=[]
                for algorithm in config['algorithms'][family]:
                    series=sorted([g for g in values if g['algorithm']==algorithm and g['statistics']['median'] is not None],key=lambda g:g['size'])
                    if not series:continue
                    x=[];y=[];lo=[];hi=[]
                    for g in series:
                        center=g['statistics']['median']
                        if spread=='dataset_median_range':low=g['statistics']['minimum'];high=g['statistics']['maximum']
                        else:
                            matches=[d for d in summary['per_dataset'] if d['family']==family and d['operation']==operation and
                                d['distribution']==g['distribution'] and d['query_category']==g['query_category'] and d['algorithm']==algorithm and
                                d['size']==g['size'] and all(d.get(k)==g.get(k) for k in ['query_seed','structure_seed','batch_size','source_manifest_sha256','run_kind']) and d['successful_trials']]
                            low=min(d['statistics']['minimum'] for d in matches);high=max(d['statistics']['maximum'] for d in matches)
                        x.append(g['size']);y.append(center*scale);lo.append((center-low)*scale);hi.append((high-center)*scale)
                        points.append(dict(algorithm=algorithm,size=g['size'],center=center*scale,lower=low*scale,upper=high*scale,
                                           distinct_input_datasets=g['distinct_input_datasets'],declared_datasets=g['declared_datasets']))
                        ids+=g['dataset_groups']
                    ax.errorbar(x,y,yerr=[lo,hi],marker='o',markersize=4,capsize=3,linewidth=1.2,label=algorithm,color=colors[algorithm])
                ax.set_xscale('symlog',linthresh=1);sizes=sorted({g['size'] for g in values})
                ax.set_xticks(sizes,labels=[f'{n:,}' for n in sizes]);ax.set_xlabel('Input size N (symlog; linear at N ≤ 1)')
                ax.set_ylabel(metric);ax.set_ylim(bottom=0)
                counts=sorted({g['distinct_input_datasets'] for g in values});declared=sorted({g['declared_datasets'] for g in values})
                spread_label='min–max of distinct dataset medians' if spread=='dataset_median_range' else 'min–max of all successful measured trials'
                ax.set_title(f"{family} / {operation} / {filters['distribution']}"+(f" / {category}" if category else '')+'\n'+
                    f"Center: median of dataset medians; {spread_label}\n"+
                    f"Distinct inputs {counts}; declared datasets {declared}; R={config['repetitions']}")
                if points:ax.legend(loc='best')
                else:ax.text(0.5,0.5,'No successful timing evidence',transform=ax.transAxes,ha='center')
                fig.tight_layout()
                index=len(figures);name=f'figure_{index:03d}_{family}_{operation}_{spread}'
                for fmt in ['svg','pdf']:
                    metadata={'Date':None,'Creator':PROTOCOL} if fmt=='svg' else {'CreationDate':None,'ModDate':None,'Creator':PROTOCOL,'Producer':PROTOCOL}
                    fig.savefig(output/(name+'.'+fmt),format=fmt,metadata=metadata)
                plt.close(fig)
                figures.append(dict(id=name,kind=spread,filters=filters,metric=metric,axis_scale={'x':'symlog; linthresh=1','y':'linear; minimum=0'},
                    transformation='equal weight distinct input medians; '+spread_label,unit='ns/query' if lookup else 'ms',
                    conversion=scale,points=points,dataset_groups=sorted(set(ids)),outputs={fmt:name+'.'+fmt for fmt in ['svg','pdf']}))
        fig,ax=plt.subplots(figsize=(7.2,4.6));labels=[];values=[]
        for family in FAMILIES:
            for field in ['successful_measured','failed_measured','missing_measured_known','failed_warmups']:
                labels.append(family+'\n'+field.replace('_',' '));values.append(summary['counts'][family][field])
        ax.bar(range(len(values)),values,color=['#247ba0' if i%4==0 else '#d1495b' for i in range(len(values))])
        ax.set_xticks(range(len(values)),labels=labels,rotation=70,ha='right',fontsize=7);ax.set_ylabel('Recorded / known planned trial count')
        ax.set_ylim(bottom=0,top=max(1,max(values)*1.1));ax.set_title('Correctness and completeness audit\nUnknown lookup omissions and interrupted commands remain in report tables')
        fig.tight_layout();name='figure_completeness'
        for fmt in ['svg','pdf']:
            fig.savefig(output/(name+'.'+fmt),format=fmt,metadata={'Date':None,'Creator':PROTOCOL} if fmt=='svg' else {'CreationDate':None,'ModDate':None,'Creator':PROTOCOL,'Producer':PROTOCOL})
        plt.close(fig)
        figures.append(dict(id=name,kind='completeness',filters={},metric='trial count',transformation='exact counts; unknown missing lookup counts not invented',
                            labels=labels,values=values,commands=summary['commands'],outputs={fmt:name+'.'+fmt for fmt in ['svg','pdf']}))
    font=Path(font_manager.findfont('DejaVu Sans'))
    manifest=dict(schema_version=1,protocol=PROTOCOL,source=summary['source'],configuration_sha256=summary['configuration_sha256'],
        source_sha256=sources,figures=figures,output_sha256=tree_hashes(output),
        plotting=dict(matplotlib=matplotlib.__version__,numpy=numpy.__version__,backend='Agg',font=font.name,font_sha256=sha256(font),rc=rc),
        unavailable_figures=[dict(metric='key comparisons',reason='Separate instrumented study not supplied; timing rows contain no counts'),
                             dict(metric='memory',reason='No matching memory study supplied; theoretical space is not measured RSS')],
        limitations='Descriptive single-session data; spread is not a confidence interval; normalized batches are not individual latency.')
    save_json(output/'plot_manifest.json',manifest)
    return manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('source',type=Path);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--allow-incomplete',action='store_true');args=parser.parse_args()
    try:
        validated=validate_study(args.source,args.allow_incomplete);summary=aggregate(validated)
        plot_summary(summary,validated,args.output)
        print(args.output)
        if not summary['complete']:parser.exit(1,'incomplete plots retain failed/missing context\n')
    except (OSError,ValueError,KeyError,TypeError,ImportError,csv.Error) as error:
        parser.exit(1,'plot failed: '+str(error)+'\n')


if __name__=='__main__':main()
