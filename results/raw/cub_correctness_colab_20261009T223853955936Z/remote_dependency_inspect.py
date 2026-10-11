def _mab_dependency_inspect():
    import hashlib,json
    from pathlib import Path
    parent=Path('/content/mab_cub_20261009T223853955936Z')
    build=parent/'modern-algorithm-benchmark/results/raw/NEW_CUB_CORRECTNESS/build'
    cache=(build/'CMakeCache.txt').read_text()
    include=Path(next(line.split('=',1)[1] for line in cache.splitlines() if line.startswith('MAB_CUB_INCLUDE_DIR:PATH=')))
    names=['cub/version.cuh','cub/device/device_radix_sort.cuh','thrust/version.h','cuda/std/version','cuda/version']
    result={'include_root':str(include),'files':{}}
    for name in names:
        path=include/name
        if path.is_file():result['files'][name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'text':path.read_text() if 'radix_sort' not in name else None}
    with (parent/'dependency_inspection.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print('MAB_DEPENDENCY_JSON='+json.dumps(result,sort_keys=True))
_mab_dependency_inspect()
del _mab_dependency_inspect
