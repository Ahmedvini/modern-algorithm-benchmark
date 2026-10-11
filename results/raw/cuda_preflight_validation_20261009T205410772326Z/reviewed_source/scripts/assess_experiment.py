#!/usr/bin/env python3
"""Conservative wall-runtime forecast from a validated pilot; not benchmark results."""
import argparse
import math
from pathlib import Path

from experiment_model import (FAMILIES, aggregate, configurations, load_json, preset,
                              resources, save_json, validate_config, validate_study)
from run_experiments import check_resources, resource_snapshot


def work(config, family):
    total=0.0
    for n,seed,qseed,distribution in configurations(config,family):
        if family=='search':cost=max(1,n)*config['queries']
        elif family=='structures':cost=max(1,n)*math.log2(n+2)+config['queries']*math.log2(n+2)*len(config['categories'])
        else:cost=max(1,n)*math.log2(n+2)
        total+=cost
    return total*len(config['algorithms'][family])*(config['warmups']+config['repetitions'])


def forecast(pilot, target, safety_factor=4):
    validate_config(pilot);validate_config(target)
    if type(safety_factor) not in (float,int) or not math.isfinite(safety_factor) or safety_factor<1:
        raise ValueError('invalid safety factor')
    return {f:safety_factor*work(target,f)/work(pilot,f) for f in FAMILIES}


def assess(source, target, runtime_budget_seconds=3600):
    validated=validate_study(source);pilot=validated['plan']['configuration'];ratios=forecast(pilot,target)
    raw=Path(source);families={}
    for family in FAMILIES:
        command=load_json(raw/(family+'_command.json'));wall=command['wall_seconds']
        if type(wall) not in (int,float) or not math.isfinite(wall) or wall<=0:raise ValueError('invalid observed pilot wall duration')
        families[family]=dict(pilot_wall_seconds=wall,forecast_multiplier=ratios[family],forecast_wall_seconds=wall*ratios[family])
    estimate=sum(f['forecast_wall_seconds'] for f in families.values())
    snapshot=resource_snapshot(raw.parent);estimates=resources(target)
    try:check_resources(snapshot,estimates);resource_gate=True;reason=None
    except ValueError as error:resource_gate=False;reason=str(error)
    return dict(schema_version=1,record_kind='runtime_resource_forecast',pilot=str(raw.resolve()),target_configuration=target,
        families=families,forecast_total_family_wall_seconds=estimate,safety_factor=4,
        runtime_budget_seconds=runtime_budget_seconds,resource_gate_passed=resource_gate,resource_gate_error=reason,
        runtime_gate_passed=estimate<=runtime_budget_seconds,full_execution_recommended=resource_gate and estimate<=runtime_budget_seconds,
        resource_snapshot=snapshot,resource_estimates=estimates,
        model='Scale overhead-inclusive family wall by N*log2(N+2) for sorting, N*Q for array search, N*log2(N+2)+Q*log2(N+2)*categories for structures; include algorithms/rounds/configurations; safety factor4.',
        limitations='Forecast, not measured full runtime. Tiny pilots inflate fixed setup cost when extrapolated; use an intermediate pilot to refine. Distribution, validation, cache/load/frequency/allocator changes can invalidate scaling. Plot/report cost is separate; retain observed analysis wall as a planning reference.',
        pilot_analysis_wall_seconds=load_json(raw/'analysis_command.json').get('wall_seconds') if (raw/'analysis_command.json').exists() else None)


def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('pilot',type=Path);parser.add_argument('--config',type=Path)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--runtime-budget-seconds',type=int,default=3600)
    args=parser.parse_args()
    try:
        if args.runtime_budget_seconds<=0:raise ValueError('runtime budget must be positive')
        result=assess(args.pilot,load_json(args.config) if args.config else preset('full'),args.runtime_budget_seconds)
        save_json(args.output,result);print(args.output)
    except (OSError,ValueError,KeyError,TypeError) as error:parser.exit(1,'assessment failed: '+str(error)+'\n')


if __name__=='__main__':main()
