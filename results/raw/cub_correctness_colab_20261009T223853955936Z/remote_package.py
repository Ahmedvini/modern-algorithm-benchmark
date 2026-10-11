def _mab_package():
    import hashlib,io,json,tarfile
    from pathlib import Path
    roots={'attempt1':Path('/content/mab_cub_20261009T223853955936Z'),'retry1':Path('/content/mab_cub_20261009T223853955936Z_retry1')}
    files={};skipped=[]
    for label,parent in roots.items():
        run=parent/'modern-algorithm-benchmark/results/raw/NEW_CUB_CORRECTNESS'
        assert (run/'FAILED.json').is_file() or (run/'COMPLETE.json').is_file() or (run/'INTERRUPTED.json').is_file()
        for path in sorted(run.rglob('*')):
            if path.is_symlink():skipped.append(str(path));continue
            if path.is_file():files[label+'/NEW_CUB_CORRECTNESS/'+str(path.relative_to(run))]=path
        for name in ['extraction.json','runner_started.json','runner.json','dependency_inspection.json']:
            path=parent/name
            if path.is_file():files[label+'/'+name]=path
        files[label+'/SOURCE_SHA256.json']=parent/'modern-algorithm-benchmark/SOURCE_SHA256.json'
    manifest={name:{'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size} for name,path in files.items()}
    archive=Path('/content/mab_cub_20261009T223853955936Z_retry1/colab_evidence.tar.gz')
    assert not archive.exists() and not archive.is_symlink()
    with tarfile.open(archive,'w:gz') as tar:
        for name,path in sorted(files.items()):tar.add(path,arcname=name,recursive=False)
        data=(json.dumps({'files':manifest,'skipped_symlinks':skipped},indent=2,sort_keys=True)+'\n').encode()
        member=tarfile.TarInfo('EVIDENCE_SHA256.json');member.size=len(data);member.mode=0o644;tar.addfile(member,io.BytesIO(data))
    assert all(hashlib.sha256(path.read_bytes()).hexdigest()==manifest[name]['sha256'] for name,path in files.items())
    result={'archive':str(archive),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size,'files':len(files),'skipped_symlinks':skipped}
    with (roots['retry1']/'evidence_export.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print('MAB_EXPORT_JSON='+json.dumps(result,sort_keys=True))
_mab_package()
del _mab_package
