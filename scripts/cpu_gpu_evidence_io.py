"""Read and hash the same retained bytes; never execute retained commands."""
import hashlib
import os
from pathlib import Path
import stat

from cpu_gpu_protocol import require
from cpu_gpu_provenance import strict_json, valid_digest


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


class EvidenceStore:
    def __init__(self, root):
        self.root = Path(root).absolute()
        require(self.root == self.root.resolve(strict=True), 'aliased evidence root')
        self.cache = {}

    def raw(self, reference):
        require(isinstance(reference, dict) and set(reference) == {'file', 'sha256'},
                'invalid evidence reference')
        name, expected = reference['file'], reference['sha256']
        require(isinstance(name, str) and name and valid_digest(expected), 'invalid evidence digest/path')
        relative = Path(name)
        require(not relative.is_absolute() and '..' not in relative.parts and str(relative) == name,
                'unsafe evidence path')
        if name not in self.cache:
            path = self.root / relative
            require(path == path.resolve(strict=True) and path.is_relative_to(self.root), 'aliased evidence path')
            descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(descriptor, 'rb') as stream:
                before = os.fstat(stream.fileno())
                require(stat.S_ISREG(before.st_mode) and before.st_size <= 64 * 1024**2,
                        'nonregular/oversized evidence')
                raw = stream.read(64 * 1024**2 + 1)
                after = os.fstat(stream.fileno())
            require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) ==
                    (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns),
                    'evidence changed while reading')
            require(len(raw) == before.st_size, 'incomplete evidence read')
            self.cache[name] = raw
        raw = self.cache[name]
        require(digest(raw) == expected, 'retained evidence hash mismatch: ' + name)
        return raw

    def json(self, reference):
        return strict_json(self.raw(reference).decode('utf-8', errors='strict'))


def command(value, expected_argv=None, cwd=None):
    require(isinstance(value, dict) and type(value.get('exit_code')) is int and value['exit_code'] == 0 and
            value.get('status') == 'completed', 'failed/incomplete command evidence')
    require(isinstance(value.get('argv'), list) and value['argv'] and
            all(isinstance(a, str) and a for a in value['argv']) and
            isinstance(value.get('stdout'), str) and isinstance(value.get('stderr'), str),
            'malformed command evidence')
    if expected_argv is not None:
        require(value['argv'] == expected_argv, 'executed command identity mismatch')
    if cwd is not None:
        require(value.get('cwd') == cwd, 'executed working directory mismatch')
    return value
