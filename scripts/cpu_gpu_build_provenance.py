"""Validate retained compiler/linker results. Hashes alone are not build proof.

An independently pinned review must also approve the resulting provenance digest.
This module reads records only. It never invokes a compiler or a binary.
"""
from pathlib import Path
import shlex

from cpu_gpu_protocol import canonical, require
from cpu_gpu_provenance import validate_digest_map, valid_digest
from cpu_gpu_evidence_io import command, digest


def compile_entries(value, source_dir, build_dir, source):
    require(isinstance(value, list) and value, 'empty/malformed compile-command evidence')
    result = {}
    for entry in value:
        require(isinstance(entry, dict) and entry.get('directory') == build_dir and
                isinstance(entry.get('file'), str), 'compile source/build identity mismatch')
        path = Path(entry['file'])
        require(path.is_absolute() and '..' not in path.parts and path.is_relative_to(source_dir),
                'compile source path substitution')
        relative = str(path.relative_to(source_dir))
        require(relative in source, 'unreviewed compile source')
        require(('arguments' in entry) != ('command' in entry), 'ambiguous compile command')
        argv = entry.get('arguments') if 'arguments' in entry else shlex.split(entry['command'])
        require(isinstance(argv, list) and all(isinstance(a, str) and a for a in argv) and
                len(argv) >= 5 and '-c' in argv and argv.count('-o') == 1 and
                argv.index('-o') + 1 < len(argv) and str(path) in argv and
                not any(a in [';', '&&', '||', '|', '>', '<'] for a in argv), 'invalid compile invocation')
        output = Path(argv[argv.index('-o') + 1])
        if not output.is_absolute(): output = Path(build_dir) / output
        require('..' not in output.parts and output.is_relative_to(build_dir) and str(output) not in result,
                'duplicate/unsafe compile output')
        result[str(output)] = dict(argv=argv, source=relative)
    return result


def validate_build(store, reference, expected_source, required_outputs, expected_build=None):
    proof = store.json(reference)
    require(isinstance(proof, dict) and type(proof.get('schema_version')) is int and proof['schema_version'] == 1 and
            proof.get('kind') == 'cpu_gpu_build_provenance_v1', 'missing build provenance schema')
    require(proof.get('source_sha256') == expected_source and proof.get('source_after_sha256') == expected_source,
            'stale build provenance source')
    source, build = proof.get('source_dir'), proof.get('build_dir')
    for value in [source, build]:
        require(isinstance(value, str) and Path(value).is_absolute() and '..' not in Path(value).parts and
                str(Path(value)) == value, 'ambiguous provenance directory')
    require(expected_build is None or build == expected_build, 'different provenance build')
    outputs = proof.get('outputs_sha256')
    validate_digest_map(outputs, 'build output identities')
    require(set(required_outputs) <= set(outputs), 'missing build output provenance')
    for name, expected in required_outputs.items():
        require(outputs[name] == expected, 'stale build output: ' + name)
    metadata = proof.get('metadata')
    require(isinstance(metadata, dict) and set(metadata) == {'CMakeCache.txt', 'compile_commands.json', 'CTestTestfile.cmake'},
            'missing generated build metadata')
    cache = store.raw(metadata['CMakeCache.txt']).decode('utf-8')
    cache_values = {}
    for line in cache.splitlines():
        if not line or line.startswith(('#', '//')): continue
        require('=' in line and ':' in line.split('=', 1)[0], 'malformed build cache')
        field, value = line.split('=', 1); key = field.split(':', 1)[0]
        require(key not in cache_values, 'duplicate build cache key'); cache_values[key] = value
    require(cache_values.get('CMAKE_HOME_DIRECTORY') == source and
            cache_values.get('CMAKE_BUILD_TYPE') == proof.get('build_type') and
            proof.get('build_type') in ['Release', 'Debug'] and type(proof.get('sanitizers')) is bool and
            cache_values.get('MAB_ENABLE_SANITIZERS') == ('ON' if proof['sanitizers'] else 'OFF'),
            'build configuration provenance mismatch')
    entries = compile_entries(store.json(metadata['compile_commands.json']), source, build, expected_source)
    store.raw(metadata['CTestTestfile.cmake'])
    tools = proof.get('toolchain')
    require(isinstance(tools, dict) and tools, 'missing toolchain provenance')
    for path, tool in tools.items():
        require(Path(path).is_absolute() and isinstance(tool, dict) and valid_digest(tool.get('sha256')),
                'invalid compiler/tool identity')
        observed = command(store.json(tool['version']), cwd=source)
        require(observed['argv'] == [path, '--version'] and observed['stdout'].strip(), 'tool version evidence mismatch')
    configure = command(store.json(proof['configure']), cwd=source)
    require(configure['argv'][0] in tools and Path(configure['argv'][0]).name == 'cmake' and
            configure['argv'].count('-S') == 1 and configure['argv'].count('-B') == 1 and
            configure['argv'][configure['argv'].index('-S')+1] == source and
            configure['argv'][configure['argv'].index('-B')+1] == build,
            'configure source/build mismatch')
    build_command = command(store.json(proof['build']), cwd=source)
    require(build_command['argv'][0] == configure['argv'][0] and build_command['argv'][1:3] == ['--build', build] and
            '--verbose' in build_command['argv'], 'verbose build command provenance missing')
    steps = proof.get('steps')
    require(isinstance(steps, list) and steps, 'missing compiler/linker exit records')
    seen, compiled, linked, products = set(), set(), set(), {}
    for reference in steps:
        require(reference['file'] not in seen, 'duplicate build command record'); seen.add(reference['file'])
        record = command(store.json(reference), cwd=build)
        require(record.get('source_before_sha256') == expected_source and record.get('source_after_sha256') == expected_source,
                'compiler/linker source snapshot mismatch')
        argv = record['argv']; require(argv[0] in tools, 'unrecorded compiler/linker tool')
        output = record.get('output')
        require(isinstance(output, str) and Path(output).is_absolute() and '..' not in Path(output).parts and
                Path(output).is_relative_to(build), 'unsafe compiler/linker output')
        if record.get('operation') == 'compile':
            require(output in entries and entries[output]['argv'] == argv and output not in compiled,
                    'compile database/command mismatch')
            compiled.add(output)
        else:
            require(record.get('operation') in ['link', 'archive'] and output not in linked and
                    output not in entries and (output in argv or str(Path(output).relative_to(build)) in argv),
                    'invalid/duplicate linker output')
            objects = record.get('inputs_sha256')
            validate_digest_map(objects, 'linked object identities')
            require(objects and all(str(Path(build)/p) in compiled or str(Path(build)/p) in linked for p in objects),
                    'link input lacks earlier compiler/archive provenance')
            linked.add(output)
        require(valid_digest(record.get('output_sha256')), 'missing actual build product hash')
        # Object/library bytes are bound across the complete recorded command graph.
        if record.get('operation') != 'compile':
            for name, expected in objects.items():
                require(products.get(str(Path(build)/name)) == expected, 'linked object hash mismatch')
        products[output] = record['output_sha256']
    require(set(entries) == compiled, 'missing compiler exit records')
    require(all(str(Path(build)/name) in linked and products[str(Path(build)/name)] == value
                for name, value in outputs.items()), 'missing/stale executable or library link provenance')
    return proof
