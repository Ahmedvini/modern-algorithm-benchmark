def _mab_validate():
    import datetime,json,subprocess,sys,time
    from pathlib import Path
    parent=Path('/content/mab_cub_20261009T223853955936Z_retry1')
    project=parent/'modern-algorithm-benchmark'
    output=project/'results/raw/NEW_CUB_CORRECTNESS'
    assert not output.exists() and not output.is_symlink()
    argv=['python3','scripts/validate_cuda_sort.py','--output','results/raw/NEW_CUB_CORRECTNESS']
    record={'argv':argv,'cwd':str(project),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with (parent/'runner_started.json').open('x') as f:json.dump(record,f,indent=2)
    start=time.monotonic()
    try:
        result=subprocess.run(argv,cwd=project,capture_output=True,text=True,timeout=2400)
        record.update(exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr,status='completed')
    except subprocess.TimeoutExpired as error:
        def text(s):return s.decode(errors='replace') if isinstance(s,bytes) else s or ''
        record.update(exit_code=None,stdout=text(error.stdout),stderr=text(error.stderr),status='timeout')
    record.update(wall_seconds=time.monotonic()-start,ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    with (parent/'runner.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
    print('MAB_RUNNER_JSON='+json.dumps(record,sort_keys=True))
    for name in ['FAILED.json','INTERRUPTED.json','COMPLETE.json','configure.json','build.json','sorting.json','ctest.json']:
        path=output/name
        if path.is_file():print('MAB_ARTIFACT '+name+'='+path.read_text())
    print('MAB_FILES_JSON='+json.dumps([str(x.relative_to(output)) for x in sorted(output.rglob('*')) if x.is_file() and 'build' not in x.relative_to(output).parts]))
_mab_validate()
del _mab_validate
