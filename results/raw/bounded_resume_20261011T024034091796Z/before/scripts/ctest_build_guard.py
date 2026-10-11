"""Static, fail-closed gate for the reviewed flat CTest registry. Never runs CMake.

This is deliberately not a general CMake interpreter. Only literal generated
add_test/set_tests_properties declarations are supported. Includes, subdirectories,
hooks, control flow and new generator formats require a separate policy review.
"""
import hashlib
import os
from pathlib import Path
import re
import stat

from cpu_gpu_protocol import ROOT, require

HOOK_NAMES = {'CTestCustom.cmake', 'CTestCustom.ctest', 'CTestConfig.cmake'}
TOKEN = re.compile(r'"([^"\\\r\n]*)"|\[=\[([^\r\n]*?)\]=\]|([A-Za-z0-9_]+)')


def read_regular(path):
    """Reject symlinks/nonregular/unreadable files rather than interpreting them."""
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and bool(info.st_mode & 0o444),
            'unreadable/nonregular build metadata: ' + str(path))
    require(info.st_size <= 1024*1024, 'oversized build metadata')
    raw = path.read_bytes()
    text = raw.decode('utf-8', errors='strict')
    require(not any(c in text for c in ['\x00', '\r', '${', '$ENV{', '$<']),
            'ambiguous/expanded build metadata: ' + str(path))
    return text, hashlib.sha256(raw).hexdigest()


def statements(text):
    """Accept the small literal grammar emitted by the reviewed generators."""
    result = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            require(not line.startswith('#['), 'unreviewed bracket comment')
            continue
        match = re.fullmatch(r'(add_test|set_tests_properties)\((.*)\)', line)
        require(match is not None, 'unreviewed CTest statement (includes/subdirs/hooks forbidden)')
        tokens, cursor = [], 0
        arguments = match[2]
        while cursor < len(arguments):
            if arguments[cursor].isspace():
                cursor += 1
                continue
            token = TOKEN.match(arguments, cursor)
            require(token is not None, 'malformed/ambiguous CTest argument')
            tokens.append(next(group for group in token.groups() if group is not None))
            cursor = token.end()
            require(cursor == len(arguments) or arguments[cursor].isspace(),
                    'ambiguous adjacent CTest arguments')
        result.append((match[1], tokens))
    return result


def expand(value, build):
    return value.replace('@source', str(ROOT.resolve())).replace('@build', str(build))


def validate_dart(path, build, policy):
    # DartConfiguration is key/value data, not CMake. Do not evaluate it. These
    # reviewed dashboard commands are not invoked by our fixed -N/-R commands.
    require(stat.S_ISREG(path.lstat().st_mode) and bool(path.stat().st_mode & 0o444),
            'unreadable/nonregular Dart configuration')
    require(path.stat().st_size <= 1024*1024, 'oversized Dart configuration')
    raw = path.read_bytes()
    values = {}
    for line in raw.decode('utf-8', errors='strict').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        require(re.fullmatch(r'[A-Za-z][A-Za-z0-9]*: [^\x00\r\n]*', line) is not None,
                'malformed Dart configuration')
        key, value = line.split(': ', 1)
        require(key not in values, 'duplicate Dart setting')
        values[key] = value
    expected = policy['dart_defaults']
    require(set(values) == set(expected), 'unknown/missing Dart setting')
    for key, value in values.items():
        if key in policy['dart_inert_metadata']:
            # These values are output-only environment labels, never commands.
            require(not any(c in value for c in [';', '$', '\\', '"']), 'ambiguous Dart label')
        elif key in ['ConfigureCommand', 'MakeCommand']:
            # Only an absolute cmake executable and the exact reviewed arguments.
            pattern = (r'"/[^";\s]+/cmake" "' + re.escape(str(ROOT.resolve())) + r'"'
                       if key == 'ConfigureCommand' else
                       r'/[^";\s]+/cmake --build \. --config "\$\{CTEST_CONFIGURATION_TYPE\}"')
            require(re.fullmatch(pattern, value) is not None, 'unreviewed Dart command: ' + key)
        elif key == 'DefaultCTestConfigurationType':
            require(value in ['Release', 'Debug'], 'unreviewed build configuration')
        else:
            require(value == expand(expected[key], build), 'modified Dart setting: ' + key)
    return hashlib.sha256(raw).hexdigest()


def validate_build_tree(build_dir, manifest, expected_command):
    """Return a fingerprint only after all reachable CTest metadata is classified.

    The project registers all tests at the root. Reject nested test files and all
    includes/subdirs instead of attempting to evaluate arbitrary CMake programs.
    Scan the whole tree for directory hooks, including unreachable nested hooks.
    """
    build = Path(build_dir).absolute()
    require(build == build.resolve() and build.is_dir(), 'missing/aliased build directory')
    for component in [build, *build.parents]:
        require(not component.is_symlink(), 'symlinked build directory')
    require(not any(k.startswith('CTEST_') for k in os.environ), 'unreviewed CTEST environment override')
    policy = manifest.get('build_metadata')
    require(isinstance(policy, dict) and policy.get('policy') == 'flat_literal_ctest_v1',
            'missing reviewed build-metadata policy')
    files = {}
    def onerror(error):
        raise ValueError('unreadable build tree: ' + str(error)) from error
    for directory, dirs, names in os.walk(build, followlinks=False, onerror=onerror):
        parent = Path(directory)
        require(bool(parent.stat().st_mode & 0o444) and bool(parent.stat().st_mode & 0o111),
                'unreadable build directory')
        for name in dirs + names:
            path = parent/name
            require(not path.is_symlink(), 'unreviewed build symlink: ' + str(path))
            require(name not in HOOK_NAMES and not name.endswith('.ctest'),
                    'unreviewed CTest hook/configuration: ' + str(path))
            if name in ['CTestTestfile.cmake', 'DartConfiguration.tcl']:
                require(parent == build and name in names, 'unreviewed nested CTest metadata: ' + str(path))
    testfile = build/'CTestTestfile.cmake'
    text, digest = read_regular(testfile)
    files['CTestTestfile.cmake'] = digest
    declarations, properties = {}, {}
    for command, args in statements(text):
        require(bool(args), 'empty CTest declaration')
        name = args[0]
        require(name in manifest['tests'], 'unreviewed CTest test name')
        if command == 'add_test':
            require(name not in declarations and name not in properties, 'duplicate/out-of-order CTest declaration')
            require([str(Path(a).resolve()) for a in args[1:]] == expected_command(manifest['tests'][name]['command'], build),
                    'unreviewed generated command: ' + name)
            declarations[name] = args[1:]
        else:
            require(name in declarations and name not in properties and len(args) >= 4 and args[1] == 'PROPERTIES'
                    and len(args) % 2 == 0, 'malformed/duplicate CTest properties')
            pairs = dict(zip(args[2::2], args[3::2]))
            require(len(pairs) == (len(args)-2)//2, 'duplicate CTest property')
            expected = policy['test_properties'].get(name)
            require(isinstance(expected, dict) and pairs == {k: expand(v, build) for k,v in expected.items()},
                    'unreviewed generated properties/hooks/fixtures: ' + name)
            properties[name] = pairs
    names = set(declarations)
    cpu = set(manifest['cpu_build_tests']); gpu = set(manifest['cuda_additional_tests'])
    require(names in [cpu, cpu | gpu] and set(properties) == names, 'incomplete/unreviewed generated registry')
    dart = build/'DartConfiguration.tcl'
    if dart.exists():
        files[dart.name] = validate_dart(dart, build, policy)
    return dict(policy=policy['policy'], build_dir=str(build), files_sha256=files,
                test_names=sorted(names), commands=declarations, properties=properties)
