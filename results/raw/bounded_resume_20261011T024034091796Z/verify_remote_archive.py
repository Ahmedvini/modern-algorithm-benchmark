"""Hash and safely inspect/extract evidence archives; never executes their contents."""
from pathlib import Path, PurePosixPath
import hashlib, json, sys, tarfile

e = Path(__file__).resolve().parent
archive = e/sys.argv[1]
expected = sys.argv[2]
destination = e/sys.argv[3]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(archive) == expected, 'remote archive hash mismatch'
assert not destination.exists(), 'evidence destination collision'
with tarfile.open(archive, 'r:gz') as source:
    members=source.getmembers()
    assert len({m.name for m in members}) == len(members)
    for member in members:
        path=PurePosixPath(member.name)
        assert member.isfile() and not path.is_absolute() and '..' not in path.parts
        assert path.parts[0]=='evidence' and member.size < 50*1024*1024
    destination.mkdir()
    source.extractall(destination,filter='data')
root=destination/'evidence'
seal=json.loads((root/'REMOTE_INTEGRITY.json').read_text())
assert all(sha(root/p)==digest for p,digest in seal.items())
assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} == set(seal)|{'REMOTE_INTEGRITY.json'}
print(json.dumps(dict(archive=str(archive),sha256=expected,sealed_members=len(seal),extracted_files=len(seal)+1,
                     content_and_membership_verified=True),indent=2))
