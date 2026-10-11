def _mab_extract():
    import hashlib,json,tarfile
    from pathlib import Path,PurePosixPath
    archive=Path('/content/cub_sort_source_v3_20261009T223853955936Z.tar.gz')
    expected='e4a5e21c02c6f5611b5577caac88abaa35856270af61b335bcf57a923e73dee1'
    actual=hashlib.sha256(archive.read_bytes()).hexdigest()
    assert actual==expected,(actual,expected)
    destination=Path('/content/mab_cub_20261009T223853955936Z_retry1')
    assert not destination.exists() and not destination.is_symlink()
    with tarfile.open(archive,'r:gz') as tar:
        members=tar.getmembers()
        names=[m.name for m in members]
        assert len(names)==len(set(names))
        for m in members:
            name=PurePosixPath(m.name)
            assert not name.is_absolute() and '..' not in name.parts
            assert name.parts and name.parts[0]=='modern-algorithm-benchmark'
            assert m.isfile() or m.isdir(),m.name
        destination.mkdir()
        tar.extractall(destination,filter='data')
    project=destination/'modern-algorithm-benchmark'
    manifest=json.loads((project/'SOURCE_SHA256.json').read_text())
    for name,sha in manifest.items():
        path=PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts
        assert hashlib.sha256((project/name).read_bytes()).hexdigest()==sha,name
    for folder in ('raw','processed','figures'):(project/'results'/folder).mkdir(parents=True,exist_ok=True)
    result={'archive_sha256':actual,'archive_members':names,'verified_source_files':len(manifest),'project':str(project)}
    with (destination/'extraction.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print('MAB_EXTRACTION_JSON='+json.dumps(result,sort_keys=True))
_mab_extract()
del _mab_extract
