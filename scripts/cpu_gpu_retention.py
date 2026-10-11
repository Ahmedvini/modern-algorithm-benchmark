"""Retain the complete verified reference graph; never execute stored commands."""
import json
from pathlib import Path

from cpu_gpu_evidence_io import EvidenceStore, digest
from cpu_gpu_protocol import require
from cpu_gpu_provenance import strict_json


def retain_evidence(document, source_root, destination):
    """Snapshot all nested {file, sha256} references before exclusive output.

    The caller must first validate the prerequisite's semantics. Retention grants
    no eligibility or authorization. Limits bound malformed/cyclic input graphs.
    """
    store = EvidenceStore(source_root)
    completed, visiting, hashes = set(), set(), {}
    total = 0

    def visit(value):
        nonlocal total
        if isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, dict):
            if 'file' in value and 'sha256' in value:
                require(set(value) == {'file', 'sha256'}, 'ambiguous retained reference')
                raw = store.raw(value)
                name = value['file']
                require(name not in hashes or hashes[name] == value['sha256'], 'conflicting retained digests')
                require(name not in visiting, 'cyclic retained references')
                if name in completed:
                    return
                hashes[name] = value['sha256']
                total += len(raw)
                require(len(hashes) <= 10000 and total <= 256 * 1024**2, 'retained evidence budget exceeded')
                visiting.add(name)
                if name.endswith('.json') or raw.lstrip().startswith((b'{', b'[')):
                    visit(strict_json(raw.decode('utf-8')))
                visiting.remove(name)
                completed.add(name)
            else:
                for item in value.values():
                    visit(item)

    visit(document)
    target = Path(destination).absolute()
    require(target.parent == target.parent.resolve(strict=True), 'aliased retention destination')
    target.mkdir()  # Existing directories and dangling symlinks fail; never merge.
    for name in sorted(hashes):
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(store.cache[name])
        require(digest(path.read_bytes()) == hashes[name], 'retained copy mismatch')
    with (target / 'RETAINED_SHA256.json').open('x') as stream:
        json.dump(hashes, stream, indent=2, sort_keys=True)
        stream.write('\n')
    return hashes
