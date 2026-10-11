def _mab_progress():
    import json,subprocess
    from pathlib import Path
    parent=Path('/content/mab_cub_20261009T223853955936Z_retry1')
    r=subprocess.run(['ps','-eo','pid,ppid,etime,args'],capture_output=True,text=True,timeout=20)
    selected=[line for line in r.stdout.splitlines() if any(s in line for s in ['validate_cuda_sort.py','test_cuda_sorting','nvcc','cmake --build'])]
    print('MAB_PROGRESS_JSON='+json.dumps({'parent_files':[x.name for x in parent.iterdir()],'validation_processes':selected,'ps_exit':r.returncode}))
_mab_progress()
del _mab_progress
