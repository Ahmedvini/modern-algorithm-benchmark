import hashlib,json,pathlib,tarfile
root=pathlib.Path('/content/cpu_gpu_pilot_20261010T001232473460Z_v1')
archive=pathlib.Path('/content/cpu_gpu_pilot_20261010T001232473460Z_evidence_v1.tar.gz')
files=[p for p in root.rglob('*') if p.is_file() and ('results' in p.relative_to(root).parts or p.parent==root)]
manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
with (root/'download_manifest.json').open('x') as f:json.dump(manifest,f,indent=2)
files.append(root/'download_manifest.json')
with tarfile.open(archive,'x:gz') as t:
 for p in sorted(files):t.add(p,arcname=str(p.relative_to(root)),recursive=False)
print(json.dumps(dict(path=str(archive),sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),files=len(files)),indent=2))
