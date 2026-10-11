#!/usr/bin/env python3
"""Strict unified statistics, deterministic plots and consolidated Markdown report."""
import argparse
import csv
import json
from pathlib import Path

from experiment_model import (PROTOCOL, aggregate, canonical, load_json, save_json,
                              tree_hashes, validate_study)
from plot_results import plot_summary


def table(headers,rows):
    def escape(value):return str(value).replace('|','\\|').replace('\n',' ')
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(escape(v) for v in row)+' |\n' for row in rows)+'\n'


def value(number):
    return 'unavailable' if number is None else format(number,'.6g')


def report(summary, validated, manifest):
    plan=validated['plan'];config=plan['configuration'];source=Path(plan['raw_path'])
    environment=load_json(source/'environment.json') if (source/'environment.json').exists() else {}
    snapshot=load_json(source/'preflight.json') if (source/'preflight.json').exists() else {}
    lines=['# Consolidated experiment report\n',
        '## Executive summary\n',
        f"Profile: **{config['profile']}**. Validated raw collection complete: **{summary['complete']}**. "
        'Smoke results validate the pipeline; they are not a completed full study.\n' if config['profile']!='full' else
        f"Profile: **full**. Validated full raw collection complete: **{summary['complete']}**.\n",
        'Results are descriptive, specific to the recorded implementations, workloads and session. No universal winner or statistical significance is asserted.\n',
        '## Protocol and environment\n',
        f"Protocol {PROTOCOL}; configuration SHA256 `{plan['configuration_sha256']}`. Family protocols remain unchanged; retained PROTOCOL_v1.md and protocol.json identify the new contract.\n",
        '```json\n'+json.dumps(environment,indent=2,sort_keys=True,allow_nan=False)+'\n```\n',
        'Resource/control snapshot:\n```json\n'+json.dumps(snapshot,indent=2,sort_keys=True,allow_nan=False)+'\n```\n',
        '## Workloads and trial design\n',
        '```json\n'+json.dumps(config,indent=2,sort_keys=True,allow_nan=False)+'\n```\n',
        'One serial family/configuration at a time; original engines retain cyclic algorithm order. Generation/restoration/query planning and correctness checks stay outside primary steady_clock timing. Sorting, construction and lookup are separate. Instrumentation is absent.\n',
        '## Correctness and completeness audit\n']
    fields=['successful_measured','failed_measured','missing_measured_known','warmup_rows','failed_warmups','missing_warmups_known','missing_configurations','unknown_lookup_missing_upper_bound']
    lines.append(table(['Family']+fields,[[f]+[c[k] for k in fields] for f,c in summary['counts'].items()]))
    lines.append(table(['Family','Command outcome','Exit status'],[[c['family'],c['status'],c['exit_code']] for c in summary['commands']]))
    unavailable=[e for e in summary['availability'] if not e['available']]
    lines.append(f"Unavailable category/configuration entries: {len(unavailable)} (recorded in summary; no invented trials). Missing configurations: {len(summary['missing_configurations'])}. Interrupted command count: {sum(c['status']=='interrupted' for c in summary['commands'])}.\n")
    lines+=['## Results by benchmark family\n',
        'Cross-dataset rows use equally weighted distinct-input medians after repeated trials are summarized within each dataset. Identical ordered fingerprints collapse to one input unit. Lookup values below are **normalized batch averages**, not individual-query latency. Complete per-dataset statistics/counts remain in summary.json and observations.jsonl.\n']
    for family in ['sorting','search','structures']:
        lines.append('### '+family+'\n');rows=[]
        for g in summary['cross_dataset']:
            if g['family']!=family:continue
            lookup=g['operation']=='lookup';factor=1/g['batch_size'] if lookup else 1/1e6
            s=g['statistics']
            rows.append([g['algorithm'],g['operation'],g['distribution'],g['size'],g['query_category'] or 'n/a',
                g['distinct_input_datasets'],g['declared_datasets'],'ns/query (normalized)' if lookup else 'ms',
                *[value(s[k]*factor if s[k] is not None else None) for k in ['median','mean','sample_stdev','minimum','maximum']],
                g['successful_trials'],g['failed_trials'],g['missing_trials']])
        lines.append(table(['Algorithm','Operation','Source distribution','N','Policy','Distinct inputs','Declared datasets','Unit',
            'Median','Mean','Sample SD','Min','Max','Successful trials','Failed','Missing'],rows))
    lines+=['## Variability and statistical interpretation\n',
        'All successful measured observations and outliers are retained. Warmups are preserved and excluded from statistics. Sample SD uses n−1 and is unavailable for fewer than two input units/trials. Min–max bars are descriptive spread, not confidence intervals. Repeated timings on one dataset are not independent datasets; seeds/query policies do not establish independent machine sessions. Different source distributions stay separate even when their sorted multisets coincide.\n']
    lines.append(table(['Figure','Spread / metric','Outputs'],[[f['id'],f['kind'],', '.join(f['outputs'].values())] for f in manifest['figures']]))
    lines+=['## Known measurement limitations and confounders\n',
        'Shared Linux machine; CPU frequency, cache, thermal state and background load were not controlled. Validation touches structures before lookup. Nanosecond units do not imply nanosecond accuracy; timer overhead is not subtracted. No direct per-query maxima, isolated structure memory, end-to-end index costs, confidence intervals or significance tests. No comparison or memory figures are fabricated from timing data.\n',
        '## Reproducibility instructions\n',
        'Regenerate to new, absent derived paths; never edit raw bundles:\n```sh\n'
        f"python3 scripts/analyze_experiment.py {plan['raw_path']} --output NEW_PROCESSED_DIRECTORY --figures NEW_FIGURE_DIRECTORY\n"
        f"python3 scripts/plot_results.py {plan['raw_path']} --output NEW_FIGURE_DIRECTORY\n```\n",
        'experiment.json contains exact runner/child commands. observations.jsonl traces every row to its raw CSV; plot_manifest.json records filters/transforms/source hashes/output hashes/plotting versions. Byte identity is checked on the same plotting stack, not promised across versions or platforms.\n',
        '## Deferred experiments and next steps\n',
        'Full preset is pending unless this report explicitly identifies a complete full run. Separate count/memory studies, independent-session replication, timer calibration and larger searches require explicit planning. Next roadmap implementation: Phase 6 OpenMP. No CUDA or 100M workload.\n']
    return '\n'.join(lines)


def analyze(source, output, figures, allow_incomplete=False):
    source=Path(source).resolve();output=Path(output).absolute();figures=Path(figures).absolute()
    paths=[source,output.resolve(),figures.resolve()]
    for i,a in enumerate(paths):
        for b in paths[i+1:]:
            if a==b or a in b.parents or b in a.parents:raise ValueError('raw/derived outputs must not overlap')
    if output.exists() or output.is_symlink() or figures.exists() or figures.is_symlink():raise FileExistsError('derived output already exists')
    validated=validate_study(source,allow_incomplete);summary=aggregate(validated)
    if not (source/'COLLECTED.json').exists() and not allow_incomplete:
        raise ValueError('analysis requires a validated collection marker')
    before=tree_hashes(source)
    output.mkdir(exist_ok=False)
    try:
        save_json(output/'summary.json',summary)
        with (output/'observations.jsonl').open('x',encoding='utf-8') as stream:
            for obj in validated['observations']:stream.write(canonical(obj)+'\n')
        manifest=plot_summary(summary,validated,figures)
        with (output/'REPORT.md').open('x',encoding='utf-8') as stream:stream.write(report(summary,validated,manifest))
        if tree_hashes(source)!=before:raise ValueError('raw inputs changed during analysis')
        save_json(output/('COMPLETE.json' if summary['complete'] else 'INCOMPLETE.json'),dict(protocol=PROTOCOL,complete=summary['complete'],
            files_sha256=tree_hashes(output),figures_sha256=tree_hashes(figures)))
    except Exception as error:
        try:save_json(output/'FAILED.json',dict(complete=False,error=str(error)))
        except OSError:pass
        raise
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('source',type=Path);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--figures',type=Path,required=True);parser.add_argument('--allow-incomplete',action='store_true');args=parser.parse_args()
    try:
        result=analyze(args.source,args.output,args.figures,args.allow_incomplete);print(args.output)
        if not result['complete']:parser.exit(1,'partial experiment retained; no completion claim\n')
    except (OSError,ValueError,KeyError,TypeError,ImportError,csv.Error) as error:
        parser.exit(1,'unified analysis failed: '+str(error)+'\n')


if __name__=='__main__':main()
