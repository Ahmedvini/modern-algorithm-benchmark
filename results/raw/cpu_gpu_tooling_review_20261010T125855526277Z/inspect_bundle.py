import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile

root=Path.cwd()
base=Path(__file__).resolve().parent
old=root/'results/raw/cpu_gpu_full_tooling_20261010T121208603276Z'
source=json.loads((old/'FINAL_INTEGRITY.json').read_text())['current_source_sha256']
observed={}
with tarfile.open(old/'full_matrix_tooling_source.tar.gz') as archive:
    members=archive.getmembers()
    for member in members:
        path=PurePosixPath(member.name)
        assert not path.is_absolute() and '..' not in path.parts
        assert member.isfile() or member.isdir()
        if member.isfile():
            relative='/'.join(path.parts[1:])
            with archive.extractfile(member) as stream:
                digest=hashlib.sha256(stream.read()).hexdigest()
            observed[relative]=digest
assert all(observed[p]==digest for p,digest in source.items())
before=json.loads((old/'source_before.json').read_text())['current_source_sha256']
changed=sorted(p for p in before if source.get(p)!=before[p])
added=sorted(set(source)-set(before))
report=dict(archive_members=len(members),source_files_matched=len(source),unsafe_members=0,
    extracted=False,changed_source_files_in_tooling_milestone=changed,added_source_files_in_tooling_milestone=added,
    documentation_changes=['README.md','docs/AUDIT.md','docs/ROADMAP.md','docs/CPU_GPU_FULL_MATRIX_TOOLING_v1.md'])
with (base/'BUNDLE_REVIEW.json').open('x') as stream:json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps(report,indent=2))
