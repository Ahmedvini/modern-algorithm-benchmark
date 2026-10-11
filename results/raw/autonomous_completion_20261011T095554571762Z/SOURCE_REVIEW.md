# Source review inventory

No Git metadata exists. BASELINE.json retains original digests; CHANGES.json lists all additions/modifications and final hashes. Only three pre-existing Python source/test files changed.

- non_timing_tests.py: additive v5 local snapshot; exact pinned-v3 classifications/commands; shared static hook/path guard and rechecks unchanged.
- run_cpu_gpu_pilot.py: full-study evidence retention copies recursively verified nested references, without changing algorithm, timing, pilot or launch eligibility.
- test_evidence_enforcement.py: historical snapshot regression explicitly selects immutable v3 after authorized local-default activation; failure expectation retained.

Existing CMake, native production algorithms, runtime/timing framework, vendor code and licenses are unchanged. Learned index is separately compiled and does not alter registries.

## cmake/learned_index_standalone/CMakeLists.txt

SHA-256: `dca1ec7099cfe782be3238ddb543744cb143e8c6febbbe2980222a73c95cb7da`

````text
cmake_minimum_required(VERSION 3.16)
project(mab_learned_extension LANGUAGES CXX)
# Keep the historical root CMake/algorithm registrations unchanged. Compile the
# existing sources directly; their implementation remains shared with the engine.
get_filename_component(MAB_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
option(MAB_ENABLE_SANITIZERS "Address/undefined sanitizers for correctness" OFF)
add_library(mab_search
    "${MAB_ROOT}/src/algorithms/baselines.cpp" "${MAB_ROOT}/src/datasets/generator.cpp"
    "${MAB_ROOT}/src/algorithms/sorting.cpp" "${MAB_ROOT}/src/algorithms/quicksort.cpp"
    "${MAB_ROOT}/src/algorithms/pdqsort.cpp" "${MAB_ROOT}/src/algorithms/timsort.cpp"
    "${MAB_ROOT}/src/algorithms/mergesort.cpp" "${MAB_ROOT}/src/algorithms/radixsort.cpp"
    "${MAB_ROOT}/src/algorithms/searching.cpp" "${MAB_ROOT}/src/benchmark/search_timing.cpp"
    "${MAB_ROOT}/src/benchmark/timing.cpp" "${MAB_ROOT}/src/benchmark/output.cpp"
    "${MAB_ROOT}/src/benchmark/search_comparisons.cpp"
    "${MAB_ROOT}/src/benchmark/memory.cpp" "${MAB_ROOT}/src/benchmark/memory_json.cpp")
target_include_directories(mab_search PUBLIC "${MAB_ROOT}/include")
target_include_directories(mab_search PRIVATE "${MAB_ROOT}/third_party/pdqsort" "${MAB_ROOT}/third_party/timsort/include")
target_compile_features(mab_search PUBLIC cxx_std_17)
set_target_properties(mab_search PROPERTIES CXX_EXTENSIONS OFF)
if(MAB_ENABLE_SANITIZERS)
    target_compile_options(mab_search PUBLIC -fsanitize=address,undefined -fno-omit-frame-pointer)
    target_link_options(mab_search PUBLIC -fsanitize=address,undefined)
endif()
add_library(mab_learned_index "${MAB_ROOT}/src/indexes/learned_index.cpp")
target_link_libraries(mab_learned_index PUBLIC mab_search)
target_compile_options(mab_learned_index PRIVATE -Wall -Wextra -Wpedantic -Wconversion -Wshadow)
add_executable(test_learned_index "${MAB_ROOT}/tests/test_learned_index.cpp")
target_link_libraries(test_learned_index PRIVATE mab_learned_index)
enable_testing()
add_test(NAME learned_index_correctness COMMAND test_learned_index)
add_executable(learned_index_benchmark "${MAB_ROOT}/src/benchmark/learned_main.cpp")
target_link_libraries(learned_index_benchmark PRIVATE mab_learned_index)
target_compile_options(learned_index_benchmark PRIVATE -Wall -Wextra -Wpedantic -Wconversion -Wshadow)
if(MAB_ENABLE_SANITIZERS)
    target_compile_definitions(learned_index_benchmark PRIVATE MAB_LEARNED_SANITIZERS=1)
endif()

````

## include/indexes/learned_index.hpp

SHA-256: `be8901c3d2c0b399390def4d513e6534cc4373b5dbcc221b9687474660c2a803`

````text
#pragma once

#include "algorithms/searching.hpp"
#include <cstdint>

namespace mab {
struct RankDiagnostic {
    SearchResult result;
    std::size_t predicted_position;
    std::size_t lower_bound_position;
    std::size_t correction_distance;
    std::uint64_t comparisons;
    bool fallback;
};

// Immutable endpoint-trained rank model; ascending input is validated at build.
// Lookup returns the FIRST equal position, including duplicate keys.
class LearnedIndex {
public:
    explicit LearnedIndex(const Values& sorted);
    SearchResult find(Key key) const;
    RankDiagnostic diagnose(Key key) const;
    std::size_t size() const noexcept { return values_.size(); }
    std::size_t owned_capacity_bytes() const noexcept { return values_.capacity() * sizeof(Key); }
    static constexpr std::size_t correction_radius = 32;

private:
    Values values_;
    template<class Less> std::size_t predict(Key key, Less less) const;
    template<class Less> RankDiagnostic lookup(Key key, Less less) const;
};
}  // namespace mab

````

## scripts/cpu_gpu_retention.py

SHA-256: `8475ab7499f2366fd8b28c06440aefef74a36239d21e613950a46f837507660e`

````text
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

````

## scripts/learned_study.py

SHA-256: `847b14dfd4ae9c1042a50097bd9d286f9d550d475e2ea766b8ed89e08f363f97`

````text
#!/usr/bin/env python3
"""Run/analyze the separate held-out learned-rank study; never invokes GPU work."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / 'docs/studies/learned_rank_v1.matrix.json'
ALGORITHMS = ['binary_search', 'learned_rank']
FIELDS = ['algorithm', 'operation', 'phase', 'trial_index', 'execution_order', 'elapsed_ns', 'queries', 'correctness']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def samples(values):
    require(bool(values), 'empty sample')
    return dict(n=len(values), median=statistics.median(values), mean=statistics.mean(values),
                sample_sd=statistics.stdev(values) if len(values) > 1 else None, minimum=min(values), maximum=max(values))


def cells():
    matrix = json.loads(MATRIX.read_text())
    require(matrix['protocol'] == 'learned_rank_v1' and matrix['warmups'] == 1 and matrix['repetitions'] == 5, 'wrong matrix')
    require(len(matrix['cells']) == 48 and len({c['id'] for c in matrix['cells']}) == 48, 'matrix coverage')
    return matrix['cells']


def validate_cell(directory, cell):
    directory = Path(directory)
    require(not (directory / 'FAILED.json').exists(), 'failed configuration')
    complete = json.loads((directory / 'COMPLETE.json').read_text())
    require(complete == dict(complete=True, rows=18, diagnostic_queries=1000), 'incomplete configuration')
    meta = json.loads((directory / 'run.json').read_text())
    expected = dict(schema_version=1, protocol='learned_rank_v1', size=cell['size'], seed=cell['seed'],
                    distribution=cell['distribution'], query_seed=2718, queries=1000, hits=500, misses=500,
                    warmups=1, repetitions=5, radius=32, build_type='Release', clock='steady_clock')
    require(all(meta.get(k) == v for k, v in expected.items()), 'metadata/configuration mismatch')
    require(all(isinstance(meta.get(k), str) and meta[k].isdigit() for k in ['input_fingerprint', 'query_fingerprint']), 'missing dataset/query identity')
    with (directory / 'trials.csv').open(newline='') as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames == FIELDS, 'trial schema mismatch')
        rows = list(reader)
    require(len(rows) == 18, 'missing trials')
    seen, groups = set(), {}
    for row in rows:
        require(set(row) == set(FIELDS) and None not in row.values(), 'malformed trial')
        require(row['phase'] in ['warmup', 'measure'] and row['correctness'] == 'passed', 'failed/unknown trial')
        require(all(row[k].isascii() and row[k].isdigit() for k in ['trial_index', 'execution_order', 'elapsed_ns', 'queries']), 'invalid numeric trial')
        trial, order = int(row['trial_index']), int(row['execution_order'])
        require(trial < (1 if row['phase'] == 'warmup' else 5), 'unexpected trial')
        identity = row['phase'], trial, row['algorithm'], row['operation']
        require(identity not in seen, 'duplicate trial'); seen.add(identity)
        if row['operation'] == 'build':
            require(row['algorithm'] == 'learned_rank' and row['queries'] == '0' and order == 0, 'invalid build row')
        else:
            require(row['operation'] == 'lookup_batch' and row['algorithm'] in ALGORITHMS and row['queries'] == '1000', 'invalid query row')
            require(order in [0, 1] and ALGORITHMS[(cell['seed'] % 2 + trial % 2 + order) % 2] == row['algorithm'], 'execution order mismatch')
        if row['phase'] == 'measure':
            groups.setdefault((row['algorithm'], row['operation']), []).append(int(row['elapsed_ns']))
    require(set(groups) == {('learned_rank', 'build'), ('learned_rank', 'lookup_batch'), ('binary_search', 'lookup_batch')} and
            all(len(v) == 5 for v in groups.values()), 'mode coverage incomplete')
    with (directory / 'diagnostics.csv').open(newline='') as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames == ['query_id', 'target', 'expected_position', 'actual_position', 'predicted_position',
                'lower_bound_position', 'correction_distance', 'fallback', 'learned_comparisons', 'binary_comparisons'], 'diagnostic schema mismatch')
        diagnostics = list(reader)
    require(len(diagnostics) == 1000, 'missing diagnostics')
    hits, fallback, distances, comparisons = 0, 0, [], []
    for i, row in enumerate(diagnostics):
        require(row['query_id'] == str(i) and row['expected_position'] == row['actual_position'], 'diagnostic identity/output mismatch')
        require(-2**31 <= int(row['target']) < 2**31, 'target outside signed int32')
        if row['expected_position']:
            require(0 <= int(row['expected_position']) < cell['size'], 'invalid hit position'); hits += 1
        prediction, lower = int(row['predicted_position']), int(row['lower_bound_position'])
        require(0 <= prediction < cell['size'] and 0 <= lower <= cell['size'], 'invalid rank')
        distance = int(row['correction_distance'])
        require(distance == abs(prediction - lower) and row['fallback'] in ['true', 'false'], 'invalid correction diagnostic')
        require(int(row['learned_comparisons']) >= 0 and int(row['binary_comparisons']) >= 0, 'invalid comparison counts')
        if row['expected_position']: require(int(row['expected_position']) == lower, 'first-match position mismatch')
        fallback += row['fallback'] == 'true'; distances.append(distance)
        comparisons.append([int(row['learned_comparisons']), int(row['binary_comparisons'])])
    require(hits == 500, 'hit/miss ratio mismatch')
    memory = json.loads((directory / 'memory.json').read_text())
    require(memory['owned_capacity_bytes'] >= 4 * cell['size'] and memory['object_bytes'] > 0, 'invalid memory report')
    return dict(id=cell['id'], size=cell['size'], seed=cell['seed'], distribution=cell['distribution'],
                input_fingerprint=meta['input_fingerprint'], query_fingerprint=meta['query_fingerprint'],
                timings=[dict(algorithm=a, operation=o, unit='ns', **samples(v)) for (a, o), v in sorted(groups.items())],
                fallback_queries=fallback, queries=1000, mean_correction_distance=statistics.mean(distances),
                mean_learned_comparisons=statistics.mean(v[0] for v in comparisons),
                mean_binary_comparisons=statistics.mean(v[1] for v in comparisons), memory=memory)


def analyze(raw, output):
    raw, output = Path(raw), Path(output)
    require((raw / 'COMPLETE.json').is_file(), 'study incomplete')
    manifest = json.loads((raw / 'study.json').read_text())
    require(manifest['matrix_sha256'] == sha(MATRIX), 'matrix changed')
    require(manifest['cells'] == cells(), 'wrong study matrix')
    # Retained raw seal is checked before deriving any statistics.
    for relative, digest in manifest['raw_sha256'].items():
        require(Path(relative).as_posix() == relative and not Path(relative).is_absolute() and '..' not in Path(relative).parts, 'unsafe raw path')
        require(sha(raw / relative) == digest, 'raw record changed: ' + relative)
    datasets = [validate_cell(raw / c['id'], c) for c in cells()]
    aggregate = {}
    for dataset in datasets:
        for timing in dataset['timings']:
            key = dataset['size'], dataset['distribution'], timing['algorithm'], timing['operation']
            aggregate.setdefault(key, []).append(timing['median'])
    cross = [dict(size=n, distribution=d, algorithm=a, operation=o, unit='ns',
                  aggregation='equal-weight dataset medians', **samples(v)) for (n, d, a, o), v in sorted(aggregate.items())]
    output.mkdir()
    write(output / 'summary.json', dict(protocol='learned_rank_v1', configurations=48, measured_query_batches=480,
          warmup_query_batches=96, measured_builds=240, warmup_builds=48, failed=0, missing=0,
          datasets=datasets, cross_seed=cross))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 10, 'svg.hashsalt': 'learned_rank_v1'})
    plot_manifest = []
    for distribution in sorted({d['distribution'] for d in datasets}):
        fig, ax = plt.subplots(figsize=(7, 4.5), layout='constrained')
        for algorithm in ALGORITHMS:
            values = [r for r in cross if r['distribution'] == distribution and r['algorithm'] == algorithm and r['operation'] == 'lookup_batch']
            x, y = [r['size'] for r in values], [r['median'] / 1000 for r in values]
            ax.errorbar(x, y, yerr=[[r['median']/1000-r['minimum']/1000 for r in values],
                        [r['maximum']/1000-r['median']/1000 for r in values]], marker='o', capsize=4, label=algorithm)
        ax.set_xscale('log'); ax.set_ylim(bottom=0)
        ax.set(xlabel='Stored keys (log scale)', ylabel='Normalized batch average (ns/query)',
               title=f'{distribution}: median of 3 dataset medians\nBars: min–max across seeds; 5 trials/dataset; 1000 queries/batch')
        ax.legend(); ax.grid(alpha=.25)
        name = distribution + '_lookup.png'
        fig.savefig(output / name, dpi=220); plt.close(fig)
        plot_manifest.append(dict(file=name, source='summary.json', distribution=distribution, operation='lookup_batch',
                                  transformation='median dataset batch nanoseconds / 1000', spread='cross-seed min/max'))
    write(output / 'plots.json', plot_manifest)
    with (output / 'REPORT.md').open('x') as stream:
        stream.write('# Held-out learned rank study\n\n48 datasets; 480 measured lookup batches, 240 measured builds; '
                     '96 lookup and 48 build warm-ups. All outputs passed; zero missing/failed trials. '
                     'Each dataset has 500 hit and 500 miss queries. Repetitions are summarized within a dataset; '
                     'cross-seed values equally weight three dataset medians. All outliers retained.\n\n'
                     '|N|Distribution|Algorithm|Operation|Median of dataset medians (ns)|Cross-seed min–max (ns)|\n'
                     '|---:|---|---|---|---:|---:|\n')
        for r in cross:
            stream.write(f"|{r['size']}|{r['distribution']}|{r['algorithm']}|{r['operation']}|{r['median']:.1f}|{r['minimum']:.1f}–{r['maximum']:.1f}|\n")
        stream.write('\nLogical index capacity excludes allocator metadata. Process lifetime peak RSS includes input, queries, '
                     'index, runtime and allocator; it does not isolate index memory. No individual-query maximum was measured. '
                     'Frequency, thermal state and background load were not controlled. These are descriptive results, '
                     'with no statistical-significance or universal-ranking claim. See diagnostics in summary.json for fallback '
                     'frequency, rank correction distance and separate comparison counts.\n')
    write(output / 'SHA256.json', {p.name: sha(p) for p in sorted(output.iterdir()) if p.is_file()})


def run(binary, output):
    binary, output = Path(binary).resolve(strict=True), Path(output)
    output.mkdir()
    model = dict(protocol='learned_rank_v1', matrix_sha256=sha(MATRIX), binary=str(binary), binary_sha256=sha(binary), cells=cells())
    write(output / 'STARTED.json', model)
    for cell in model['cells']:
        argv = [str(binary), '--output', str((output / cell['id']).absolute()), '--size', str(cell['size']),
                '--seed', str(cell['seed']), '--distribution', cell['distribution']]
        result = subprocess.run(argv, text=True, capture_output=True, timeout=300)
        write(output / (cell['id'] + '.command.json'), dict(argv=argv, exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr))
        print(cell['id'], 'exit', result.returncode, flush=True)
        require(result.returncode == 0, 'failed dataset: ' + cell['id'])
        validate_cell(output / cell['id'], cell)
    require(sha(binary) == model['binary_sha256'], 'executable changed during study')
    model['raw_sha256'] = {str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*')) if p.is_file()}
    write(output / 'study.json', model)
    write(output / 'COMPLETE.json', dict(complete=True, configurations=48, measured=720, warmups=144))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    sub = parser.add_subparsers(dest='mode', required=True)
    execute = sub.add_parser('run'); execute.add_argument('--binary', type=Path, required=True); execute.add_argument('--output', type=Path, required=True)
    analysis = sub.add_parser('analyze'); analysis.add_argument('--raw', type=Path, required=True); analysis.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.mode == 'run': run(args.binary, args.output)
    else: analyze(args.raw, args.output)

````

## scripts/non_timing_tests.py

SHA-256: `ccbebcdd02792abc39e8bce04c58ffc96f787d68568b025da5b4eb5a48cb471d`

````text
#!/usr/bin/env python3
"""Fail-closed CTest selection; CLI prints a plan and never executes tests."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from cpu_gpu_protocol import ROOT, dump_new, require, sha, source_manifest
from cpu_gpu_provenance import strict_json, validate_digest_map
from ctest_build_guard import validate_build_tree

# v1-v4 remain immutable history. v5 is a separately recorded local source
# review under the user's standing authorization, NOT full-study eligibility.
MANIFEST = ROOT / 'docs/NON_TIMING_TEST_SELECTION_v5.json'
BASE_SELECTION_SHA256 = 'fef39034b063c36dabc3eccf9dc6a162ebcf6a4e5cb44abeda83e93fbcf1a434'
SAFE_CLASSES = {'cpu_correctness', 'gpu_correctness'}
CLASSES = SAFE_CLASSES | {'timing'}
# Fixtures/dependencies can implicitly schedule tests outside an -R expression.
SAFE_PROPERTIES = {'WORKING_DIRECTORY', 'TIMEOUT', 'SKIP_RETURN_CODE', 'LABELS'}
TIMING_ENTRY_POINTS = {'test_experiments.py', 'test_structure_timing', 'test_structure_benchmark.py',
    'test_search_timing', 'test_search_benchmark.py', 'test_timing', 'test_benchmark.py',
    'test_parallel_mergesort', 'test_parallel_benchmark.py', 'test_comparison'}


def load_manifest():
    manifest = strict_json(MANIFEST.read_text())
    require(isinstance(manifest, dict) and type(manifest.get('schema_version')) is int and
            manifest['schema_version'] in [1, 2, 3, 5] and manifest.get('policy') in
            ['non_timing_correctness_v1', 'non_timing_correctness_v2', 'non_timing_correctness_v3', 'non_timing_correctness_v5'],
            'invalid non-timing manifest')
    if manifest['schema_version'] == 5:
        base_path = ROOT / 'docs/NON_TIMING_TEST_SELECTION_v3.json'
        require(sha(base_path) == BASE_SELECTION_SHA256 and manifest.get('base_manifest_sha256') == BASE_SELECTION_SHA256,
                'base selection identity changed')
        base = strict_json(base_path.read_text())
        for key in ['tests', 'cpu_build_tests', 'cuda_additional_tests', 'build_metadata']:
            require(manifest.get(key) == base[key], 'v5 changed approved selection/commands: ' + key)
        require(manifest.get('policy') == 'non_timing_correctness_v5' and
                manifest.get('scope') == 'local_correctness_only' and manifest.get('full_study_eligible') is False,
                'invalid v5 selection scope')
    hashes = manifest.get('reviewed_source_sha256')
    validate_digest_map(hashes, 'reviewed non-timing source snapshot')
    require(hashes == source_manifest(), 'non-timing source snapshot changed; review and reclassify before execution')
    tests = manifest.get('tests')
    require(isinstance(tests, dict) and bool(tests), 'missing test classifications')
    for name, entry in tests.items():
        require(isinstance(name, str) and re.fullmatch('[a-z_]+', name) and isinstance(entry, dict),
                'invalid test classification')
        require(entry.get('classification') in CLASSES and isinstance(entry.get('reason'), str) and entry['reason'],
                'unclassified test: ' + name)
        require(isinstance(entry.get('command'), list) and bool(entry['command']) and
                all(isinstance(a, str) and a for a in entry['command']), 'missing reviewed command: ' + name)
    cpu = manifest.get('cpu_build_tests'); gpu = manifest.get('cuda_additional_tests')
    require(isinstance(cpu, list) and isinstance(gpu, list) and cpu and gpu and
            all(isinstance(n, str) for n in cpu + gpu) and len(set(cpu + gpu)) == len(cpu + gpu) and
            set(cpu + gpu) == set(tests), 'invalid discovery coverage manifest')
    return manifest


def expected_command(pattern, build_dir):
    result = []
    for token in pattern:
        if token == '@python':
            result.append(str(Path(sys.executable).resolve()))
        elif token == '@build':
            result.append(str(build_dir.resolve()))
        elif token == '@source':
            result.append(str(ROOT.resolve()))
        elif token.startswith('@build/'):
            relative = token[len('@build/'):]
            require(Path(relative).name == relative and relative not in ['.', '..'], 'unsafe reviewed binary')
            result.append(str((build_dir / relative).resolve()))
        elif token.startswith('@source/'):
            relative = token[len('@source/'):]
            require(not Path(relative).is_absolute() and '..' not in Path(relative).parts, 'unsafe reviewed source')
            result.append(str((ROOT / relative).resolve()))
        else:
            raise ValueError('unreviewed command token: ' + token)
    return result


def pre_discovery_gate(build_dir):
    """Shared static gate; never invokes CTest or evaluates CMake code."""
    manifest = load_manifest()
    return manifest, validate_build_tree(build_dir, manifest, expected_command)


def select_tests(discovery, build_dir, allow_gpu=False, allow_diagnostics=False):
    manifest, guard = pre_discovery_gate(build_dir)
    build_dir = Path(guard['build_dir'])
    require(isinstance(discovery, dict) and discovery.get('kind') == 'ctestInfo' and
            discovery.get('version') == {'major': 1, 'minor': 0} and isinstance(discovery.get('tests'), list),
            'invalid CTest JSON discovery')
    tests = discovery['tests']; names = [t.get('name') if isinstance(t, dict) else None for t in tests]
    require(all(isinstance(n, str) for n in names) and len(set(names)) == len(names), 'duplicate/malformed discovered tests')
    expected_cpu = set(manifest['cpu_build_tests']); expected_gpu = set(manifest['cuda_additional_tests'])
    require(set(names) in [expected_cpu, expected_cpu | expected_gpu], 'unknown/missing/unclassified discovered tests')
    require(set(names) == set(guard['test_names']), 'discovery differs from guarded registry coverage')
    if allow_gpu:
        require(set(names) == expected_cpu | expected_gpu, 'GPU correctness requested from non-CUDA build')
    selected, excluded = [], []
    for test in tests:
        name = test['name']; entry = manifest['tests'][name]; classification = entry['classification']
        command = test.get('command')
        require(isinstance(command, list) and all(isinstance(a, str) for a in command) and
                [str(Path(a).resolve()) for a in command] ==
                [str(Path(a).resolve()) for a in guard['commands'][name]],
                'discovery differs from guarded registry: ' + name)
        if (classification == 'timing' or (classification == 'gpu_correctness' and not allow_gpu)
                or (entry.get('diagnostic_only') is True and not allow_diagnostics)):
            excluded.append(dict(name=name, classification=classification, reason=entry['reason']))
            continue
        command = test.get('command')
        require(isinstance(command, list) and all(isinstance(a, str) for a in command), 'missing discovered command: ' + name)
        entry_points = {Path(a).name for a in command}
        require(not (entry_points & TIMING_ENTRY_POINTS) and
                not ('test_cuda_benchmark.py' in entry_points and len(command) != 2),
                'timing entry point cannot be selected: ' + name)
        require([str(Path(a).resolve()) for a in command] == expected_command(entry['command'], build_dir),
                'unreviewed CTest command/arguments: ' + name)
        properties = test.get('properties', [])
        require(isinstance(properties, list) and all(isinstance(p, dict) and p.get('name') in SAFE_PROPERTIES
                for p in properties), 'unsafe/unreviewed CTest properties: ' + name)
        require(len({p['name'] for p in properties}) == len(properties), 'duplicate discovered property: ' + name)
        expected_properties = guard['properties'][name]
        for prop in properties:
            key, value = prop['name'], prop.get('value')
            if key == 'WORKING_DIRECTORY':
                require(value == str(build_dir), 'unreviewed discovery working directory: ' + name)
            elif key in ['TIMEOUT', 'SKIP_RETURN_CODE']:
                require(key in expected_properties and value == int(expected_properties[key]),
                        'unreviewed discovery numeric property: ' + name)
            else:
                raise ValueError('unreviewed discovered property: ' + key)
        selected.append(name)
    require(bool(selected), 'empty non-timing selection')
    expression = '^(' + '|'.join(re.escape(n) for n in sorted(selected)) + ')$'
    argv = ['ctest', '--test-dir', str(build_dir), '--output-on-failure', '-V', '--parallel', '1', '-R', expression]
    return dict(schema_version=1, policy=manifest['policy'], manifest_sha256=sha(MANIFEST),
                allow_gpu_correctness=allow_gpu, selected=sorted(selected), excluded=excluded,
                discovered_count=len(tests), selected_count=len(selected), ctest_argv=argv,
                build_metadata=guard,
                tests_executed=False, full_protocol_prerequisites=False)


def selected_ctest(call, output, name, build_dir, allow_gpu=False, prefix=None, allow_diagnostics=False):
    """Discover and save the exact safe selection before the caller executes it."""
    require(list(prefix or []) in [[],
        ['env', '-u', 'ASAN_OPTIONS', '-u', 'LSAN_OPTIONS', 'UBSAN_OPTIONS=halt_on_error=1'],
        ['env', 'ASAN_OPTIONS=detect_leaks=0', 'UBSAN_OPTIONS=halt_on_error=1']], 'unreviewed CTest wrapper')
    _, guarded = pre_discovery_gate(build_dir)
    # Retain the exact checked identity; the callback may use a different cwd.
    build_dir = Path(guarded['build_dir'])
    discovery = call(name + '_discovery', ['ctest', '--test-dir', str(build_dir), '-N', '--show-only=json-v1'], 60)
    require(discovery.get('exit_code', 0) == 0, 'CTest discovery failed')
    plan = select_tests(strict_json(discovery['stdout']), build_dir, allow_gpu, allow_diagnostics)
    require(plan['build_metadata'] == guarded, 'build metadata changed during discovery')
    dump_new(output / (name + '_selection.json'), plan)
    # Repeat source AND generated-metadata checks at the execution boundary.
    _, final_guard = pre_discovery_gate(build_dir)
    require(final_guard == guarded, 'build metadata changed before execution')
    result = call(name, list(prefix or []) + plan['ctest_argv'], 900)
    require(re.search(r'0 tests failed out of ' + str(plan['selected_count']) + r'(?:\s|$)', result['stdout']) and
            '***Skipped' not in result['stdout'], 'non-timing correctness coverage failed/skipped')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--discovery-json', type=Path, help='Read retained discovery without invoking CTest')
    parser.add_argument('--allow-gpu-correctness', action='store_true')
    parser.add_argument('--allow-diagnostics', action='store_true', help='Include separately reviewed untimed diagnostics')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        _, guarded = pre_discovery_gate(args.build_dir)
        build_dir = Path(guarded['build_dir'])
        if args.discovery_json:
            discovery = strict_json(args.discovery_json.read_text())
        else:
            child = subprocess.run(['ctest', '--test-dir', str(build_dir), '-N', '--show-only=json-v1'],
                                   capture_output=True, text=True, check=True, timeout=60)
            discovery = strict_json(child.stdout)
        plan = select_tests(discovery, build_dir, args.allow_gpu_correctness, args.allow_diagnostics)
        require(plan['build_metadata'] == guarded, 'build metadata changed during discovery')
        if args.output:
            dump_new(args.output, plan)
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('selection error: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

````

## scripts/run_cpu_gpu_pilot.py

SHA-256: `799394fe375d9fd384e59246396dc47d0a7e023cf2c80b5ec8a89ca36e903124`

````text
#!/usr/bin/env python3
"""Run only the frozen six-dataset pilot. No full-study or resume mode exists."""
import argparse
import datetime
import hashlib
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
import capture_environment
from analyze_cpu_gpu import analyze, validate_resources
from cpu_gpu_protocol import (BACKENDS, FREEZE, MATRIX, PROTOCOL, ROOT, canonical, dump_new,
                              load_protocol, require, schedule, sha, verify_source_extension)

def invoke(directory, name, argv, timeout=600, env=None):
    record = dict(argv=[str(x) for x in argv], cwd=str(ROOT), started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  omp_environment={k: (env or os.environ).get(k) for k in ['OMP_DYNAMIC','OMP_THREAD_LIMIT','OMP_MAX_ACTIVE_LEVELS','OMP_WAIT_POLICY','OMP_PROC_BIND']})
    dump_new(directory/(name+'_started.json'), record)
    started = time.monotonic()
    try:
        child = subprocess.Popen(record['argv'], cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True, start_new_session=True)
    except OSError as error:
        record.update(exit_code=None,status='unavailable',stdout='',stderr=str(error),wall_seconds=time.monotonic()-started)
        dump_new(directory/(name+'.json'),record)
        raise RuntimeError(name+' could not launch: '+str(error)) from error
    try:
        stdout, stderr = child.communicate(timeout=timeout)
        status = 'completed'
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as error:
        os.killpg(child.pid, signal.SIGTERM)
        try:stdout,stderr=child.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid,signal.SIGKILL);stdout,stderr=child.communicate()
        status = 'timeout' if isinstance(error,subprocess.TimeoutExpired) else 'interrupted'
    record.update(exit_code=child.returncode, status=status, stdout=stdout, stderr=stderr, wall_seconds=time.monotonic()-started)
    dump_new(directory/(name+'.json'),record)
    print(name, status, 'exit', child.returncode, flush=True)
    if status=='interrupted':raise KeyboardInterrupt
    if status!='completed' or child.returncode!=0:raise RuntimeError(name+' '+status+' exit '+str(child.returncode))
    return record

def read_optional(path):
    try:return Path(path).read_text().strip()
    except OSError:return None

def snapshot(build_dir, binary, output):
    env = capture_environment.capture(build_dir, 'run_cpu_gpu_pilot.py (same VM CPU/GPU)')
    env['record_kind']='cpu_gpu_pilot_environment';env['workload']='frozen six-dataset pilot'
    env['gpu_status']='see actual fresh device/workspace probes';env['affinity']=sorted(os.sched_getaffinity(0))
    env['load_average']=list(os.getloadavg());env['disk_free_bytes']=shutil.disk_usage(output).free
    paths=['/sys/fs/cgroup/cpu.max','/sys/fs/cgroup/memory.max','/sys/fs/cgroup/memory.current',
           '/sys/fs/cgroup/cpu/cpu.cfs_quota_us','/sys/fs/cgroup/cpu/cpu.cfs_period_us',
           '/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_quota_us','/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_period_us',
           '/sys/fs/cgroup/memory/memory.limit_in_bytes','/sys/fs/cgroup/memory/memory.usage_in_bytes']
    env['resource_files']={p:read_optional(p) for p in paths}
    env['cgroup_mountinfo']=read_optional('/proc/self/mountinfo')
    env['governors']={str(p):read_optional(p) for p in Path('/sys/devices/system/cpu').glob('cpu*/cpufreq/scaling_governor')}
    env['omp_environment']={k:os.environ.get(k) for k in ['OMP_DYNAMIC','OMP_THREAD_LIMIT','OMP_MAX_ACTIVE_LEVELS','OMP_WAIT_POLICY','OMP_PROC_BIND']}
    env['binary_linkage']=capture_environment.probe(['ldd',str(binary)])
    env['nvidia_smi']=capture_environment.probe(['nvidia-smi'])
    env['gpu_processes']=capture_environment.probe(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader,nounits'])
    env['gpu_details']=capture_environment.probe(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total,memory.free,temperature.gpu,clocks.sm,clocks.mem,power.limit','--format=csv,noheader,nounits'])
    env['nvcc']=capture_environment.probe(['nvcc','--version'])
    env['measurement_controls']='frequency/cache/thermal/background exclusivity not controlled; observable checks only'
    return env

def environment_gate(environment):
    require(platform.system()=='Linux', 'pilot currently requires Linux')
    require(len(environment['affinity'])>=2,'fewer than two available logical CPUs')
    require(environment['disk_free_bytes']>=1024**3,'less than1GiB free disk')
    memory={line.split(':')[0]:line.split(':')[1].strip() for line in environment['linux_meminfo'].splitlines() if ':' in line}
    require(int(memory['MemAvailable'].split()[0])*1024>=1024**3,'less than1GiB MemAvailable')
    files=environment['resource_files']
    quota=files['/sys/fs/cgroup/cpu.max']
    if quota and quota.split()[0]!='max':require(int(quota.split()[0])/int(quota.split()[1])>=2,'CPU quota below two CPUs')
    for cpu in ['/sys/fs/cgroup/cpu','/sys/fs/cgroup/cpu,cpuacct']:
        q=files[cpu+'/cpu.cfs_quota_us'];p=files[cpu+'/cpu.cfs_period_us']
        if q and p and int(q)>0:require(int(q)/int(p)>=2,'CPU quota below two CPUs')
    for maximum,current in [('/sys/fs/cgroup/memory.max','/sys/fs/cgroup/memory.current'),
                            ('/sys/fs/cgroup/memory/memory.limit_in_bytes','/sys/fs/cgroup/memory/memory.usage_in_bytes')]:
        limit=files[maximum];used=files[current]
        if limit and limit!='max' and used:require(int(limit)-int(used)>=1024**3,'less than1GiB cgroup memory headroom')
    for name in ['nvidia_smi','gpu_processes','gpu_details','nvcc']:
        require(environment[name].get('returncode')==0,'environment command unavailable: '+name)
    require(not environment['gpu_processes']['stdout'].strip(),'visible competing GPU process; stop before timing')

def input_command(tool, cell, destination):
    r=cell['recipe']
    return [str(tool),'--output',str(destination),'--size',str(r['size']),'--seed',str(r['seed']),
            '--distribution',r['distribution'],'--swaps',str(r['nearly_sorted_swaps']),'--distinct',str(r['duplicate_cardinality'])]

def worker_command(tool, cell, destination, identifiers, offset):
    r=cell['recipe']
    return [str(tool),'--output',str(destination/'measurements'),'--input',str(destination/'input.bin'),
            '--size',str(r['size']),'--seed',str(r['seed']),'--distribution',r['distribution'],
            '--swaps',str(r['nearly_sorted_swaps']),'--distinct',str(r['duplicate_cardinality']),
            '--dataset-id',cell['dataset_id'],'--base-order',','.join(cell['warmup_order'][0]),'--global-offset',str(offset)] + [
                item for key in ['input-sha256','input-fnv','matrix-sha256','build-id','environment-id','run-id']
                for item in ['--'+key,identifiers[key]]]

def validate_prerequisites(path, executable, input_tool, model, compatibility_policy=None):
    from cpu_gpu_provenance import strict_json
    p=strict_json(path.read_text())
    require(p.get('framework_compatibility_policy') == compatibility_policy,
            'prerequisite/launch framework compatibility policy mismatch')
    require(p.get('protocol')==PROTOCOL and p.get('complete') is True,'prerequisite validation incomplete')
    require(p.get('validation_scope','full_protocol_v1')=='full_protocol_v1' and p.get('study_eligible',True) is True,
            'non-timing subset is not full study prerequisites')
    source=verify_source_extension(model, compatibility_policy)
    require(p['source_sha256']==source['current_source_sha256'],'source changed after prerequisite validation')
    require(p['binary_sha256']==sha(executable) and p['input_tool_sha256']==sha(input_tool),'binary changed after validation')
    required={'cpu_release_ctest','cpu_sanitize_ctest','cuda_ctest','cuda_correctness','preflight'}
    records=p['records']
    require(required<=set(records),'missing prerequisite commands')
    for name,record in records.items():
        relative=Path(record['file'])
        require(not relative.is_absolute() and '..' not in relative.parts,'unsafe prerequisite record path')
        command_path=path.parent/record['file']
        require(sha(command_path)==record['sha256'],'prerequisite record changed')
        result=strict_json(command_path.read_text())
        require(result['exit_code']==0 and result.get('status')=='completed','failed prerequisite '+name)
    if compatibility_policy is not None:
        from cpu_gpu_framework_compatibility import validate_evidence
        from cpu_gpu_build_identity import verify
        validate_evidence(p,path.parent,model,source,sha(executable),sha(input_tool))
        verify(p['build_identity'],executable,input_tool)
    return p

def run(args, part='pilot'):
    model=load_protocol()
    require(part in ['pilot','study'],'unknown matrix part')
    cells=model[part]['cells'];expected=model[part]['expected']
    per_dataset=len(BACKENDS)*(model['warmups']+model['repetitions'])
    output=args.output.absolute() # Preserve final component: mkdir rejects dangling symlinks.
    if args.dry_run:
        placeholders={k:'<'+k+'>' for k in ['input-sha256','input-fnv','build-id','environment-id']}
        placeholders.update({'matrix-sha256':sha(MATRIX),'run-id':output.name})
        print(json.dumps(dict(protocol=PROTOCOL,part=part,expected=expected,resources=model['resources'],
            timeout_policy=model['timeout_policy'],resume_supported=False,
            commands=[dict(input=input_command(args.input_tool,c,output/('data_'+c['dataset_id'])),
                           worker=worker_command(args.executable,c,output/('data_'+c['dataset_id']),placeholders,i*per_dataset))
                      for i,c in enumerate(cells)]),indent=2,sort_keys=True));return 0
    require(args.prerequisites is not None,'--prerequisites is required for actual execution')
    output.mkdir();(output/'commands').mkdir()
    dump_new(output/'plan.json',dict(protocol=PROTOCOL,part=part,expected=expected,
        trials=[row for i,cell in enumerate(cells) for row in schedule(cell,i*per_dataset)],resume_supported=False))
    def partial_audit():
        if (output/'run.json').exists():
            try:dump_new(output/'PARTIAL_ANALYSIS.json',analyze(output,allow_incomplete=True,require_marker=False))
            except Exception as error:dump_new(output/'PARTIAL_ANALYSIS_ERROR.json',dict(error=str(error),
                note='Malformed/unavailable raw evidence cannot be summarized; plan and command/attempt logs remain retained.'))
    try:
        compatibility_policy=getattr(args,'framework_compatibility_policy',None)
        require(compatibility_policy is None or part=='study','framework compatibility is study-only; historical pilot unchanged')
        source=verify_source_extension(model,compatibility_policy)
        prereq=validate_prerequisites(args.prerequisites,args.executable,args.input_tool,model,
                                     compatibility_policy=compatibility_policy)
        dump_new(output/'prerequisites.json',prereq);dump_new(output/'source_review.json',source)
        if part=='study':
            from cpu_gpu_retention import retain_evidence
            retain_evidence(prereq,args.prerequisites.parent,output/'prerequisite_commands')
        policy=model['openmp_policy']['environment']
        os.environ.update(policy)
        describe=invoke(output/'commands','describe',[args.executable,'--describe'],60)
        build_description=json.loads(describe['stdout'])
        require(build_description['build_type']=='Release' and build_description['sanitizers'] is False and build_description['cub_version']==300001,'wrong build configuration')
        require(build_description['global_flags']=='' and build_description['configuration_flags'].split()==['-O3','-DNDEBUG'] and
                build_description['cuda_flags']=='' and build_description['cuda_release_flags'].split()==['-O3','-DNDEBUG'] and
                build_description['cuda_architectures']=='75','unexpected build flags')
        build_dir=Path(build_description['binary_dir'])
        build=dict(description=build_description,binary_sha256=sha(args.executable),input_tool_sha256=sha(args.input_tool),
                   compile_commands_sha256=sha(build_dir/'compile_commands.json'),source_review_sha256=sha(output/'source_review.json'))
        dump_new(output/'build.json',build)
        environment=snapshot(build_dir,args.executable,output)
        if part=='study':
            environment.update(record_kind='cpu_gpu_study_environment',workload='frozen48-dataset study',
                               workload_note='Primary host-call timing and separate prepared diagnostics.')
        dump_new(output/'environment.json',environment);environment_gate(environment)
        resources={}
        for n in sorted({c['recipe']['size'] for c in cells}):
            record=invoke(output/'commands','resources_'+str(n),[args.executable,'--resources',str(n)],60)
            resources[str(n)]=json.loads(record['stdout'])
            validate_resources(resources[str(n)],n)
        dump_new(output/'workspace_queries.json',resources)
        meta=dict(schema_version=1,protocol=PROTOCOL,matrix_part=part,run_kind='performance',run_id=output.name,
                  matrix_sha256=sha(MATRIX),freeze_sha256=sha(FREEZE),build_id=hashlib.sha256(canonical(build)).hexdigest(),
                  environment_id=hashlib.sha256(canonical(environment)).hexdigest(),prerequisites_passed=True,
                  dataset_ids=[c['dataset_id'] for c in cells],
                  implementations={b:dict(source_review='source_review.json',build='build.json',cub_pin=model['dependency'] if b.startswith('gpu_') else None) for b in BACKENDS})
        dump_new(output/'run.json',meta)
        for source_file in [MATRIX,FREEZE]:shutil.copyfile(source_file,output/source_file.name)
        if part=='study':
            shutil.copyfile(ROOT/'docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md',output/'CPU_GPU_COMPARISON_PROTOCOL_v1.md')
            shutil.copyfile(build_dir/'compile_commands.json',output/'compile_commands.json')
            shutil.copyfile(build_dir/'CMakeCache.txt',output/'CMakeCache.txt')
        deadline=time.monotonic()+model['timeout_policy'][part+'_total_seconds']
        for i,cell in enumerate(cells):
            directory=output/('data_'+cell['dataset_id'])
            dataset_deadline=min(deadline,time.monotonic()+model['timeout_policy']['per_dataset_seconds'])
            require(time.monotonic()<dataset_deadline,part+' total timeout before input')
            invoke(output/'commands','input_'+str(i),input_command(args.input_tool,cell,directory),max(.001,dataset_deadline-time.monotonic()))
            input_meta=json.loads((directory/'input.json').read_text())
            require(all(input_meta[k]==v for k,v in cell['recipe'].items() if k!='key_type'),'generated recipe mismatch')
            dataset=dict(recipe=cell['recipe'],dataset_id=cell['dataset_id'],input_sha256=sha(directory/'input.bin'),input_hash_fnv1a64=input_meta['input_hash_fnv1a64'])
            dump_new(directory/'dataset.json',dataset)
            identifiers={'input-sha256':dataset['input_sha256'],'input-fnv':dataset['input_hash_fnv1a64'],'matrix-sha256':meta['matrix_sha256'],
                         'build-id':meta['build_id'],'environment-id':meta['environment_id'],'run-id':meta['run_id']}
            require(time.monotonic()<dataset_deadline,part+' dataset timeout before worker')
            invoke(output/'commands','dataset_'+str(i),worker_command(args.executable,cell,directory,identifiers,i*per_dataset),dataset_deadline-time.monotonic())
        # Validate first; do not create a completion marker from subprocess exits alone.
        report=analyze(output,require_marker=False)
        after=snapshot(build_dir,args.executable,output)
        if part=='study':
            after.update(record_kind='cpu_gpu_study_environment',workload='frozen48-dataset study',
                         workload_note='After primary host-call timing and separate prepared diagnostics.')
            environment_gate(after)
        dump_new(output/'environment_after.json',after)
        require(verify_source_extension(model,compatibility_policy)==source,'source changed during run')
        if compatibility_policy is not None:
            from cpu_gpu_build_identity import verify
            verify(prereq['build_identity'],args.executable,args.input_tool)
        dump_new(output/'COMPLETE.json',dict(complete=report['complete'],measured=report['measured'],warmups=report['warmups']))
        dump_new(output/'RAW_SHA256.json',{str(p.relative_to(output)):sha(p) for p in sorted(output.rglob('*')) if p.is_file()})
        print(part+' complete:'+str(expected['measured_invocations'])+' measured/'+str(expected['warmup_invocations'])+' warm-ups.');return 0
    except KeyboardInterrupt:
        dump_new(output/'INTERRUPTED.json',dict(complete=False,error='interrupted'));partial_audit();return 130
    except Exception as error:
        dump_new(output/'FAILED.json',dict(complete=False,error=str(error)));partial_audit();print(error,file=sys.stderr);return 1

def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--executable',type=Path,required=True)
    parser.add_argument('--input-tool',type=Path,required=True);parser.add_argument('--prerequisites',type=Path);parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args();args.executable=args.executable.absolute();args.input_tool=args.input_tool.absolute()
    try:return run(args)
    except (OSError,ValueError,KeyError) as error:print(error,file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())

````

## src/benchmark/learned_main.cpp

SHA-256: `4e3a37861eab2f9de0ec070358693f3f6d8495ee3e50c50abda795ee5b504bae`

````text
#include "indexes/learned_index.hpp"
#include "benchmark/search_timing.hpp"
#include "benchmark/search_comparisons.hpp"
#include "benchmark/output.hpp"
#include "benchmark/memory.hpp"

#include <algorithm>
#include <charconv>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <locale>
#include <memory>

namespace fs = std::filesystem;
namespace {
using Clock = std::chrono::steady_clock;
static_assert(Clock::is_steady, "monotonic clock required");
template<class T> T number(std::string_view text) {
    T value{};
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), value);
    if (text.empty() || text.front() < '0' || text.front() > '9' || parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size())
        throw std::invalid_argument("expected unsigned decimal integer");
    return value;
}
std::ofstream file(const fs::path& path) {
    std::ofstream result;
    result.exceptions(std::ios::badbit | std::ios::failbit);
    result.imbue(std::locale::classic());
    result.open(path, std::ios::binary);
    return result;
}
std::string position(mab::SearchResult result) { return result ? std::to_string(*result) : ""; }
std::uint64_t elapsed(Clock::time_point start, Clock::time_point stop) {
    const auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
    if (ns < 0) throw std::runtime_error("negative monotonic duration");
    return static_cast<std::uint64_t>(ns);
}
}

int main(int argc, char** argv) {
    fs::path output;
    bool owns = false;
    try {
        mab::SearchConfig config;
        config.categories = {"mixed_50"};
        for (int i = 1; i < argc; ++i) {
            const std::string option(argv[i]);
            if (option == "--help") {
                std::cout << "learned_index_benchmark --output NEW_DIR [--size N] [--seed S] [--distribution NAME]\n"
                             "Protocol learned_rank_v1: 1000 queries, query seed2718, warmups1, repetitions5, radius32.\n";
                return 0;
            }
            if (option != "--output" && option != "--size" && option != "--seed" && option != "--distribution")
                throw std::invalid_argument("unknown option: " + option);
            if (++i == argc) throw std::invalid_argument("missing option value");
            const std::string_view value(argv[i]);
            if (option == "--output") output = value;
            else if (option == "--size") config.timing.dataset.size = number<std::size_t>(value);
            else if (option == "--seed") config.timing.dataset.seed = number<std::uint64_t>(value);
            else config.timing.dataset.distribution = mab::parse_distribution(value);
        }
        if (output.empty() || config.timing.dataset.size == 0 || config.timing.dataset.size > 1000000)
            throw std::invalid_argument("output required; size in [1,1000000]");
        mab::validate_search_config(config);
#if !defined(NDEBUG) || defined(MAB_LEARNED_SANITIZERS)
        throw std::invalid_argument("timing requires Release without sanitizers");
#endif
        if (!fs::create_directory(output)) throw std::runtime_error("output already exists");
        owns = true;
        auto values = mab::generate_dataset(config.timing.dataset);
        std::sort(values.begin(), values.end());
        const auto batches = mab::make_search_batches(values, config);
        if (batches.size() != 1 || !batches[0].unavailable_reason.empty()) throw std::runtime_error("query batch unavailable");
        const auto& queries = batches[0].queries;
        const auto hits = std::count_if(queries.begin(), queries.end(), [](const auto& q) { return q.expected_position.has_value(); });
        if (hits != 500 || queries.size() != 1000) throw std::runtime_error("hit/miss contract mismatch");
        auto metadata = file(output / "run.json");
        metadata << "{\"schema_version\":1,\"protocol\":\"learned_rank_v1\",\"size\":" << values.size()
                 << ",\"seed\":" << config.timing.dataset.seed << ",\"distribution\":"
                 << mab::json_string(mab::distribution_name(config.timing.dataset.distribution))
                 << ",\"input_fingerprint\":\"" << mab::input_fingerprint(values)
                 << "\",\"query_fingerprint\":\"" << mab::query_fingerprint(queries)
                 << "\",\"query_seed\":2718,\"queries\":1000,\"hits\":500,\"misses\":500,\"warmups\":1,\"repetitions\":5,\"radius\":32,"
                    "\"compiler\":" << mab::json_string(__VERSION__) << ",\"build_type\":\"Release\",\"clock\":\"steady_clock\"}\n";
        metadata.close();
        auto trials = file(output / "trials.csv");
        mab::write_csv_row(trials, {"algorithm", "operation", "phase", "trial_index", "execution_order", "elapsed_ns", "queries", "correctness"});
        std::vector<mab::SearchResult> answers(queries.size());
        std::size_t rows = 0;
        for (const auto& phase : {std::string("warmup"), std::string("measure")}) {
            const auto repetitions = phase == "warmup" ? 1U : 5U;
            for (std::size_t trial = 0; trial < repetitions; ++trial) {
                const auto build_start = Clock::now();
                const auto index = std::make_unique<mab::LearnedIndex>(values);
                const auto build_stop = Clock::now();
                mab::write_csv_row(trials, {"learned_rank", "build", phase, std::to_string(trial), "0",
                    std::to_string(elapsed(build_start, build_stop)), "0", "passed"});
                ++rows;
                const auto offset = (config.timing.dataset.seed % 2 + trial % 2) % 2;
                for (std::size_t order = 0; order < 2; ++order) {
                    const bool learned = (offset + order) % 2 == 1;
                    // Select dispatch outside the timed interval. Result stores and loop are inside.
                    const auto start = Clock::now();
                    if (learned) for (std::size_t q = 0; q < queries.size(); ++q) answers[q] = index->find(queries[q].target);
                    else for (std::size_t q = 0; q < queries.size(); ++q) answers[q] = mab::binary_search(values, queries[q].target);
                    const auto stop = Clock::now();
                    bool correct = true;
                    for (std::size_t q = 0; q < queries.size(); ++q) if (answers[q] != queries[q].expected_position) correct = false;
                    mab::write_csv_row(trials, {learned ? "learned_rank" : "binary_search", "lookup_batch", phase,
                        std::to_string(trial), std::to_string(order), std::to_string(elapsed(start, stop)), "1000", correct ? "passed" : "failed"});
                    trials.flush(); ++rows;
                    if (!correct) throw std::runtime_error("query output differs from oracle");
                }
            }
        }
        trials.close();
        const mab::LearnedIndex index(values);
        auto diagnostics = file(output / "diagnostics.csv");
        mab::write_csv_row(diagnostics, {"query_id", "target", "expected_position", "actual_position", "predicted_position",
            "lower_bound_position", "correction_distance", "fallback", "learned_comparisons", "binary_comparisons"});
        for (std::size_t q = 0; q < queries.size(); ++q) {
            const auto diagnostic = index.diagnose(queries[q].target);
            const auto binary = mab::counted_search("binary_search", values, queries[q].target);
            if (diagnostic.result != queries[q].expected_position || binary.position != diagnostic.result)
                throw std::runtime_error("untimed comparison result mismatch");
            mab::write_csv_row(diagnostics, {std::to_string(q), std::to_string(queries[q].target), position(queries[q].expected_position),
                position(diagnostic.result), std::to_string(diagnostic.predicted_position), std::to_string(diagnostic.lower_bound_position),
                std::to_string(diagnostic.correction_distance), diagnostic.fallback ? "true" : "false",
                std::to_string(diagnostic.comparisons), std::to_string(binary.key_comparisons)});
        }
        diagnostics.close();
        auto memory = file(output / "memory.json");
        memory << "{\"owned_capacity_bytes\":" << index.owned_capacity_bytes() << ",\"object_bytes\":" << sizeof(index)
               << ",\"process_lifetime_peak\":";
        mab::write_memory_json(memory, mab::process_memory());
        memory << "}\n"; memory.close();
        auto complete = file(output / "COMPLETE.json");
        complete << "{\"complete\":true,\"rows\":" << rows << ",\"diagnostic_queries\":1000}\n";
        complete.close();
        std::cout << "Completed " << rows << " rows (15 measured, 3 warmup), 1000 untimed query diagnostics: " << output << '\n';
        return 0;
    } catch (const std::exception& error) {
        if (owns) { try { auto failed = file(output / "FAILED.json"); failed << "{\"error\":" << mab::json_string(error.what()) << "}\n"; } catch (...) {} }
        std::cerr << error.what() << '\n'; return 1;
    }
}

````

## src/indexes/learned_index.cpp

SHA-256: `8dacf529c1ab2e1224476db2eb437262c2037b83d34aac40b6596bb56bc4e5cc`

````text
#include "indexes/learned_index.hpp"

#include <algorithm>
#include <stdexcept>

namespace mab {
LearnedIndex::LearnedIndex(const Values& sorted) : values_(sorted) {
    if (!std::is_sorted(values_.begin(), values_.end()))
        throw std::invalid_argument("learned index requires ascending input");
}

template<class Less> std::size_t LearnedIndex::predict(Key key, Less less) const {
    if (values_.size() < 2 || !less(values_.front(), values_.back()) || !less(values_.front(), key)) return 0;
    if (!less(key, values_.back())) return values_.size() - 1;
    const auto offset = static_cast<std::int64_t>(key) - values_.front();
    const auto span = static_cast<std::int64_t>(values_.back()) - values_.front();
    const auto position = static_cast<long double>(offset) / static_cast<long double>(span)
                        * static_cast<long double>(values_.size() - 1);
    // Clamp before conversion, including implementations where floating arithmetic rounds up.
    if (position >= static_cast<long double>(values_.size() - 1)) return values_.size() - 1;
    return static_cast<std::size_t>(position);
}

template<class Less> RankDiagnostic LearnedIndex::lookup(Key key, Less less) const {
    const auto n = values_.size();
    const auto prediction = predict(key, less);
    const auto begin = prediction > correction_radius ? prediction - correction_radius : 0;
    const auto end = n == 0 ? 0 : prediction + std::min(n - prediction, correction_radius + 1);
    const auto lower_bound = [&](std::size_t lo, std::size_t hi) {
        while (lo < hi) {
            const auto middle = lo + (hi - lo) / 2;
            if (less(values_[middle], key)) lo = middle + 1;
            else hi = middle;
        }
        return lo;
    };
    auto position = lower_bound(begin, end);
    // A local answer is valid only if no earlier equal key was excluded and
    // the lower bound was found before the right boundary (or that boundary is n).
    const bool fallback = (begin != 0 && !less(values_[begin - 1], key)) ||
                          (position == end && end != n);
    if (fallback) position = lower_bound(0, n);
    SearchResult result;
    if (position < n && !less(key, values_[position])) result = position;
    const auto distance = position > prediction ? position - prediction : prediction - position;
    return {result, prediction, position, distance, 0, fallback};
}

SearchResult LearnedIndex::find(Key key) const {
    return lookup(key, [](Key a, Key b) { return a < b; }).result;
}

RankDiagnostic LearnedIndex::diagnose(Key key) const {
    std::uint64_t comparisons = 0;
    auto result = lookup(key, [&](Key a, Key b) { ++comparisons; return a < b; });
    result.comparisons = comparisons;
    return result;
}
}  // namespace mab

````

## tests/test_evidence_enforcement.py

SHA-256: `48d7a5783f66273ca8cc54f926921953e16194808e99824919f09ca5d9598bf0`

````text
"""Inert evidence parser regressions. All execution/discovery is forbidden.

Compiler records and CTest stdout here are clearly synthetic unit fixtures, not
observed builds/tests. No fixture installs the independent production trust pin.
"""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
with mock.patch.object(subprocess,'run',side_effect=AssertionError('execution forbidden')), \
     mock.patch.object(subprocess,'Popen',side_effect=AssertionError('execution forbidden')):
    import cpu_gpu_evidence as evidence
    from cpu_gpu_evidence_io import EvidenceStore, digest, command
    from cpu_gpu_build_provenance import validate_build
    import cpu_gpu_protocol as protocol
    import cpu_gpu_build_identity as identity


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        for target in ['subprocess.run','subprocess.Popen','os.system']:
            patch=mock.patch(target,side_effect=AssertionError('execution/discovery forbidden'))
            patch.start();self.addCleanup(patch.stop)
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        self.root=Path(temporary.name)
        self.source=protocol.source_manifest()
        self.review=dict(context={'synthetic_unit_context':True}, source_dir=str(ROOT),
                         build_dir=str(self.root/'build'), record_sha256={})

    def put(self,name,value):
        raw=value if isinstance(value,bytes) else json.dumps(value,sort_keys=True).encode()
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        return dict(file=name,sha256=digest(raw))

    def store(self):return EvidenceStore(self.root)

    def cmd(self,argv,cwd=None,stdout='synthetic unit output',**more):
        return dict(argv=argv,cwd=cwd or str(ROOT),exit_code=0,status='completed',stdout=stdout,stderr='',**more)

    def proof(self,outputs=('comparison_input',),sanitize=False,prefix='proof'):
        build=str(self.root/('san' if sanitize else 'build'));src=str(ROOT)
        tool='/usr/bin/c++';cmake='/usr/bin/cmake';obj=build+'/input.o'
        argv=[tool,'-c',src+'/src/benchmark/comparison_input_main.cpp','-o',obj]
        cache=('CMAKE_HOME_DIRECTORY:INTERNAL='+src+'\nCMAKE_BUILD_TYPE:STRING='+('Debug' if sanitize else 'Release')+
               '\nMAB_ENABLE_SANITIZERS:BOOL='+('ON' if sanitize else 'OFF')+'\n').encode()
        meta={'CMakeCache.txt':self.put(prefix+'/cache',cache),
              'compile_commands.json':self.put(prefix+'/compile.json',[
                  dict(directory=build,file=argv[2],arguments=argv)]),
              'CTestTestfile.cmake':self.put(prefix+'/registry',b'# inert\n')}
        out_hash=digest(b'synthetic executable; never executed')
        compile_ref=self.put(prefix+'/compile_exit.json',self.cmd(argv,build,
            operation='compile',output=obj,output_sha256=digest(b'object'),
            source_before_sha256=self.source,source_after_sha256=self.source))
        steps=[compile_ref]
        for name in outputs:
            steps.append(self.put(prefix+'/'+name+'.json',self.cmd([tool,obj,'-o',build+'/'+name],build,
                operation='link',output=build+'/'+name,output_sha256=out_hash,
                inputs_sha256={'input.o':digest(b'object')},source_before_sha256=self.source,source_after_sha256=self.source)))
        value=dict(schema_version=1,kind='cpu_gpu_build_provenance_v1',source_dir=src,build_dir=build,
            source_sha256=self.source,source_after_sha256=self.source,build_type='Debug' if sanitize else 'Release',
            sanitizers=sanitize,outputs_sha256={n:out_hash for n in outputs},metadata=meta,
            toolchain={t:dict(sha256=digest(b'synthetic tool'),version=self.put(prefix+'/tool_'+Path(t).name,
                         self.cmd([t,'--version']))) for t in [cmake,tool]},
            configure=self.put(prefix+'/configure',self.cmd([cmake,'-S',src,'-B',build])),
            build=self.put(prefix+'/build',self.cmd([cmake,'--build',build,'--verbose'])),steps=steps)
        return self.put(prefix+'/provenance.json',value),value

    def cpu(self,sanitize=False):
        gate='cpu_sanitize' if sanitize else 'cpu_release'
        manifest=json.loads((ROOT/'docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())
        # Models a future approved source review, without changing v3 or installing it.
        manifest['reviewed_source_sha256']=self.source
        mref=self.put('selection_manifest.json',manifest)
        build=str(self.root/('san' if sanitize else 'build'));src=str(ROOT)
        def expand(v):return sys.executable if v=='@python' else v.replace('@build',build).replace('@source',src)
        names=sorted(n for n,t in manifest['tests'].items() if t['classification']=='cpu_correctness')
        all_names=sorted(manifest['cpu_build_tests'])
        commands={n:[expand(v) for v in manifest['tests'][n]['command']] for n in all_names}
        executables=sorted({Path(token).name for n in names for token in commands[n] if token.startswith(build+'/')})
        pref,proof=self.proof(executables,sanitize)
        lines=[];properties={}
        for n in all_names:
            args=[n]+commands[n]
            lines.append('add_test('+' '.join(json.dumps(a) for a in args)+')')
            props={k:expand(v) for k,v in manifest['build_metadata']['test_properties'][n].items()}
            properties[n]=props
            args=[n,'PROPERTIES']+[v for pair in props.items() for v in pair]
            lines.append('set_tests_properties('+' '.join(json.dumps(a) for a in args)+')')
        # Backtrace values have semicolons, not Python/JSON escape sequences.
        proof['metadata']['CTestTestfile.cmake']=self.put('proof/registry',('\n'.join(lines)+'\n').encode())
        pref=self.put('proof/provenance.json',proof)
        argv=['ctest','--test-dir',build,'--output-on-failure','-V','--parallel','1','-R','^('+'|'.join(names)+')$']
        plan=dict(policy=manifest['policy'],selected=names,selected_count=len(names),manifest_sha256=mref['sha256'],
            allow_gpu_correctness=False,tests_executed=False,full_protocol_prerequisites=False,
            discovered_count=len(all_names),ctest_argv=argv,build_metadata=dict(build_dir=build,test_names=all_names,
            commands=commands,properties=properties,files_sha256={'CTestTestfile.cmake':proof['metadata']['CTestTestfile.cmake']['sha256']}))
        discovery=dict(kind='ctestInfo',version=dict(major=1,minor=0),tests=[
            dict(name=n,command=commands[n],properties=[]) for n in all_names])
        text='\n'.join('Start '+str(i)+': '+n+'\n'+str(i)+'/21 Test #'+str(i)+': '+n+' ..... Passed 0.001 sec'
                       for i,n in enumerate(names,1))+'\n100% tests passed, 0 tests failed out of 21\n'
        prefix=['env','-u','ASAN_OPTIONS','-u','LSAN_OPTIONS','UBSAN_OPTIONS=halt_on_error=1'] if sanitize else []
        record=dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate=gate,context=self.review['context'],
            manifest=mref,selection=self.put('selection_plan.json',plan),build_provenance=pref,
            executables_sha256=proof['outputs_sha256'],guarded_metadata={'CTestTestfile.cmake':proof['metadata']['CTestTestfile.cmake']},
            discovery=self.put('discovery.json',self.cmd(['ctest','--test-dir',build,'-N','--show-only=json-v1'],stdout=json.dumps(discovery))),
            command=self.put('cpu_command.json',self.cmd(prefix+argv,stdout=text)))
        self.review.update(selection_sha256=mref['sha256'],python=sys.executable,cpu_build_provenance_sha256={gate:pref['sha256']})
        return record

    def check(self,record):
        ref=self.put('framework.json',record)
        self.review['record_sha256'][record['gate']]=ref['sha256']
        return evidence.record_coverage(self.store(),record['gate'],ref,self.review,self.source)

    def prepared(self):
        value=dict(schema_version=1,artifact_kind='correctness_validation',scope='prepared_cuda_untimed_v1',
            study_eligible=False,status='passed',inputs=163,output_checks=489,invalid_operations_rejected=489,failures=0)
        record=dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate='gpu_prepared',context=self.review['context'],
            command=self.put('prepared_command.json',self.cmd([self.review['build_dir']+'/test_cuda_prepared_correctness'],stdout=json.dumps(value))))
        return record,value

    def test_valid_prepared_record_is_derived(self):
        r,v=self.prepared();self.assertEqual(self.check(r),dict(inputs=163,output_checks=489,failures=0))

    def test_hash_consistent_placeholder_and_malformed_schema_rejected(self):
        for value in [{},dict(synthetic_fixture=True,gate='gpu_prepared'),[],dict(schema_version=True,kind='cpu_gpu_framework_record_v1')]:
            ref=self.put('placeholder.json',value);self.review['record_sha256']['gpu_prepared']=ref['sha256']
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'unsupported framework record schema'):
                evidence.record_coverage(self.store(),'gpu_prepared',ref,self.review,self.source)

    def test_contradictory_outer_record_cannot_override_valid_body(self):
        r,v=self.prepared();r['status']='failed'
        with self.assertRaisesRegex(ValueError,'contradictory framework record fields'):self.check(r)

    def test_derived_claim_supports_every_original_gate_including_pilot_missing(self):
        for gate,coverage in evidence.trusted_policy()[0]['coverage'].items():
            with self.subTest(gate=gate):
                claim=evidence.derived_claim(dict(sha256='0'*64),coverage)
                self.assertEqual(claim['status'],'passed');self.assertEqual(claim['missing'],0)
                for key,value in coverage.items():self.assertEqual(claim[key],value)

    def test_hash_consistent_failed_incomplete_prepared_records_rejected(self):
        for key,value in [('status','failed'),('inputs',162),('output_checks',488),('failures',1),('study_eligible',True)]:
            r,v=self.prepared();v[key]=value
            r['command']=self.put('prepared_command.json',self.cmd([self.review['build_dir']+'/test_cuda_prepared_correctness'],stdout=json.dumps(v)))
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'incomplete/failed prepared'):self.check(r)

    def test_hash_consistent_incorrect_exit_status_rejected(self):
        r,v=self.prepared();result=self.store().json(r['command']);result['exit_code']=1
        r['command']=self.put('prepared_command.json',result)
        with self.assertRaisesRegex(ValueError,'failed/incomplete command'):self.check(r)

    def test_hash_consistent_wrong_context_build_and_command_rejected(self):
        r,v=self.prepared();r['context']={'wrong_source':True}
        with self.assertRaisesRegex(ValueError,'context mismatch'):self.check(r)
        r,v=self.prepared();result=self.store().json(r['command']);result['argv'][0]='/other/build/test_cuda_prepared_correctness'
        r['command']=self.put('prepared_command.json',result)
        with self.assertRaisesRegex(ValueError,'executed command identity'):self.check(r)

    def test_duplicate_json_keys_rejected_with_correct_hash(self):
        ref=self.put('duplicate.json',b'{"inputs":163,"inputs":0}')
        with self.assertRaises(ValueError):self.store().json(ref)

    def test_tampered_and_stale_hash_rejected(self):
        ref=self.put('record.json',dict(status='passed'));self.put('record.json',dict(status='failed'))
        with self.assertRaisesRegex(ValueError,'hash mismatch'):self.store().json(ref)

    def test_hash_and_parser_share_immutable_bytes(self):
        ref=self.put('record.json',dict(status='passed'));store=self.store();store.raw(ref)
        changed=self.put('record.json',dict(status='failed'))
        self.assertEqual(store.json(ref),dict(status='passed'))
        with self.assertRaisesRegex(ValueError,'hash mismatch'):store.json(changed)

    def test_alias_and_path_substitution_rejected(self):
        ref=self.put('record.json',{})
        (self.root/'alias.json').symlink_to(self.root/'record.json')
        for path in ['alias.json','../record.json','./record.json']:
            with self.subTest(path=path),self.assertRaises(ValueError):self.store().raw(dict(ref,file=path))

    def test_valid_cpu_release_record_bound_to_plan_commands_and_build(self):
        self.assertEqual(self.check(self.cpu()),dict(passed=21))

    def test_valid_cpu_sanitizer_record(self):
        self.assertEqual(self.check(self.cpu(True)),dict(passed=21))

    def test_wrong_selection_manifest_rejected_with_consistent_hash(self):
        r=self.cpu();m=self.store().json(r['manifest']);m['reviewed_source_sha256']={'wrong':'0'*64}
        r['manifest']=self.put('selection_manifest.json',m)
        with self.assertRaisesRegex(ValueError,'wrong approved selection snapshot'):self.check(r)
        self.review['selection_sha256']=r['manifest']['sha256']
        with self.assertRaisesRegex(ValueError,'source snapshot mismatch'):self.check(r)

    def test_cpu_missing_duplicate_conflicting_or_failed_tests_rejected(self):
        for mode in ['missing','duplicate','failed','contradictory']:
            r=self.cpu();result=self.store().json(r['command']);lines=result['stdout'].splitlines()
            if mode=='missing':lines=lines[2:]
            elif mode=='duplicate':lines=lines[:2]+lines
            elif mode=='failed':lines[1]=lines[1].replace('Passed','***Failed')
            else:lines.append('ERROR: AddressSanitizer: rejected fixture')
            result['stdout']='\n'.join(lines);r['command']=self.put('cpu_command.json',result)
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'CTest coverage|contradictory CTest'):self.check(r)

    def test_cpu_command_and_plan_tampering_rejected(self):
        for mode in ['selection','argv','cwd','exit','executables']:
            r=self.cpu()
            if mode=='selection':
                p=self.store().json(r['selection']);p['selected'].pop();r['selection']=self.put('selection_plan.json',p)
            elif mode=='executables':r['executables_sha256']={}
            else:
                c=self.store().json(r['command'])
                if mode=='argv':c['argv'][-1]='.*'
                elif mode=='cwd':c['cwd']='/another/source'
                else:c['exit_code']=1
                r['command']=self.put('cpu_command.json',c)
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'plan coverage|command identity|working directory|failed/incomplete|executable coverage'):self.check(r)

    def test_discovery_includes_fixtures_or_modified_commands_rejected(self):
        for mode in ['fixtures','commands','duplicate']:
            r=self.cpu();d=self.store().json(r['discovery']);value=json.loads(d['stdout'])
            if mode=='fixtures':value['tests'][0]['properties']=[dict(name='FIXTURES_REQUIRED',value='unreviewed')]
            elif mode=='commands':value['tests'][0]['command']=['/unreviewed/wrapper']
            else:value['tests'][0]=value['tests'][1]
            d['stdout']=json.dumps(value);r['discovery']=self.put('discovery.json',d)
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'unsafe discovery|command substitution|duplicate discovery'):self.check(r)

    def test_valid_build_graph_is_not_empty_compile_list(self):
        ref,p=self.proof();self.assertEqual(validate_build(self.store(),ref,self.source,p['outputs_sha256']),p)

    def test_arbitrary_empty_or_fabricated_compile_list_rejected(self):
        for entries in [[],[{}],{},[dict(directory='/wrong',file='/unreviewed')]]:
            ref,p=self.proof();p['metadata']['compile_commands.json']=self.put('proof/compile.json',entries)
            ref=self.put('proof/provenance.json',p)
            with self.subTest(entries=entries),self.assertRaisesRegex(ValueError,'compile-command|compile source/build'):
                validate_build(self.store(),ref,self.source,p['outputs_sha256'])

    def test_missing_compiler_linker_or_failed_exit_evidence_rejected(self):
        for mode in ['none','compile','link','failed','object']:
            ref,p=self.proof()
            if mode=='none':p['steps']=[]
            elif mode=='compile':p['steps']=p['steps'][1:]
            elif mode=='link':p['steps']=p['steps'][:1]
            else:
                s=self.store().json(p['steps'][1])
                if mode=='failed':s['exit_code']=2
                else:s['inputs_sha256']['input.o']='0'*64
                p['steps'][1]=self.put('proof/comparison_input.json',s)
            ref=self.put('proof/provenance.json',p)
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'missing compiler|lacks earlier|missing/stale|failed/incomplete|object hash'):
                validate_build(self.store(),ref,self.source,p['outputs_sha256'])

    def test_stale_build_source_outputs_and_other_build_rejected(self):
        for mode in ['source','output','missing','build']:
            ref,p=self.proof();required=dict(p['outputs_sha256'])
            if mode=='source':p['source_after_sha256']={'stale':'0'*64}
            elif mode=='output':required['comparison_input']='0'*64
            elif mode=='missing':required['missing_binary']='0'*64
            else:p['build_dir']='/another/build'
            ref=self.put('proof/provenance.json',p)
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'stale build|missing build output|different provenance build'):
                validate_build(self.store(),ref,self.source,required,str(self.root/'build'))

    def test_missing_trusted_review_is_not_trust_on_first_use(self):
        with self.assertRaisesRegex(ValueError,'review not installed'):evidence.approval()

    def test_malformed_missing_or_mutated_independent_anchor_rejected(self):
        for data in [b'{',b'{}',b'{"policy":1,"policy":2}']:
            ref=self.put('review.json',data)
            with mock.patch.object(evidence,'APPROVAL',self.root/'review.json'), \
                 mock.patch.object(evidence,'TRUSTED_APPROVAL_SHA256',ref['sha256']),self.assertRaises(ValueError):evidence.approval()
        with mock.patch.object(evidence,'APPROVAL',self.root/'absent'), \
             mock.patch.object(evidence,'TRUSTED_APPROVAL_SHA256','0'*64),self.assertRaises(OSError):evidence.approval()

    def candidate(self):
        base=json.loads((ROOT/'docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())
        old=base['reviewed_source_sha256'];source=self.source
        return dict(base,schema_version=4,policy='non_timing_correctness_v4_candidate',
            review_status='pending_independent_review',base_manifest_sha256=evidence.BASE_SELECTION_SHA256,
            reviewed_source_sha256=source,source_delta=dict(added=sorted(set(source)-set(old)),removed=sorted(set(old)-set(source)),
                modified=sorted(n for n in set(source)&set(old) if source[n]!=old[n])))

    def test_inactive_candidate_preserves_default_19_and_classifications(self):
        c=self.candidate();delta=evidence.candidate(c,self.source);self.assertTrue(delta['added'])
        base=json.loads((ROOT/'docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())
        self.assertEqual(c['tests'],base['tests']);self.assertEqual(c['cpu_build_tests'],base['cpu_build_tests'])
        default=sorted(n for n,v in c['tests'].items() if v['classification']=='cpu_correctness' and not v.get('diagnostic_only'))
        self.assertEqual(default,sorted('baselines cli comparisons cpu_gpu_comparison_framework cuda_benchmark_analysis cuda_preflight cuda_sort_handoff datasets environment_manifest memory memory_unsupported mergesort metrics_cli pdqsort quicksort radixsort searching structures timsort'.split()))

    def test_candidate_unreviewed_add_remove_path_or_hash_changes_rejected(self):
        for mode in ['add','remove','path','hash','test']:
            c=copy.deepcopy(self.candidate())
            if mode=='add':c['reviewed_source_sha256']['unapproved']='0'*64
            elif mode=='remove':c['reviewed_source_sha256'].pop('CMakeLists.txt')
            elif mode=='path':c['reviewed_source_sha256']['../CMakeLists.txt']=c['reviewed_source_sha256'].pop('CMakeLists.txt')
            elif mode=='hash':c['reviewed_source_sha256']['CMakeLists.txt']='0'*64
            else:c['tests']['parallel_mergesort']['classification']='cpu_correctness'
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'candidate source|candidate changed'):evidence.candidate(c,self.source)

    def test_candidate_cannot_establish_approved_selection(self):
        c=self.candidate();ref=self.put('candidate.json',c)
        with self.assertRaisesRegex(ValueError,'candidate is not approved'):
            evidence.selection_manifest(self.store(),ref,dict(selection_sha256=ref['sha256']),self.source)

    def test_full_validator_rejects_internally_consistent_unsupported_assertion(self):
        cpu=self.cpu();cpu['context']=None
        outputs=identity.EXECUTABLES+('libmab_parallel.a','libmab_cuda_timing.a')
        bref,bproof=self.proof(outputs,prefix='main_build')
        build_identity=dict(source_dir=str(ROOT),build_dir=bproof['build_dir'],build_provenance=bref,
            files_sha256=dict(bproof['outputs_sha256'],**{n:r['sha256'] for n,r in bproof['metadata'].items()}))
        context=dict(session_id='inert-unit',source_identity=digest(protocol.canonical(self.source)),
            build_identity=digest(protocol.canonical(build_identity)),binary_identity=bproof['outputs_sha256']['cpu_gpu_comparison'],
            freeze_sha256=evidence.TRUSTED_FREEZE_SHA256)
        self.review.update(context=context,build_provenance_sha256=bref['sha256'])
        cpu['context']=context
        parent,anchors=evidence.trusted_policy();names=parent['required_records']['full_study_prerequisites']
        refs={n:self.put('full_'+n+'.json',cpu if n=='cpu_release' else {}) for n in names}
        self.review['record_sha256']={n:r['sha256'] for n,r in refs.items()}
        records={n:dict(dict(status='passed',exit_code=0,skipped=0,missing=0,sha256=refs[n]['sha256']),**parent['coverage'][n]) for n in names}
        records['cpu_release']['passed']=22
        p=dict(session_id='inert-unit',build_provenance=bref,framework_records=refs,framework_validation=dict(records=records))
        with mock.patch.object(evidence,'approval',return_value=self.review), \
             self.assertRaisesRegex(ValueError,'coverage assertion unsupported by actual record: cpu_release'):
            evidence.validate_full(p,self.store(),self.source,build_identity)

    def test_workspace_missing_or_duplicate_size_is_rejected(self):
        r=dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate='workspace',context=self.review['context'],commands=[],
               environment=self.put('unused_environment.json',{}))
        with self.assertRaisesRegex(ValueError,'missing workspace size coverage'):self.check(r)

    def test_independent_review_failed_decision_rejected_with_correct_hash(self):
        r=dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate='independent_review',context=self.review['context'],
            decision=self.put('decision.json',dict(schema_version=1,kind='independent_evidence_review_v1',accepted=False,
                execution_authorized=False,context=self.review['context'])))
        with self.assertRaisesRegex(ValueError,'decision not accepted'):self.check(r)

    def test_synthetic_timing_bundle_cannot_qualify_as_performance(self):
        for gate in ['pilot','timing_smoke']:
            r=dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate=gate,context=self.review['context'],
                raw_files={'run.json':self.put('raw_run.json',dict(run_kind='synthetic_test_fixture')),
                           'COMPLETE.json':self.put('raw_complete.json',{})})
            with self.subTest(gate=gate),self.assertRaisesRegex(ValueError,'synthetic/validation timing evidence cannot qualify'):self.check(r)

    def smoke(self):
        # Synthetic CSV values for parser tests, never observed measurements.
        import csv,io
        from analyze_cuda_results import FIELDS,SHARED,METRICS
        meta=dict(schema_version=1,protocol='cuda_sort_timing_v1',algorithm='cub_radix_sort',
            implementation_version='cub_radix_sort_v1',elapsed_unit='ns',allocation_policy='prepared_pinned_reuse_v1',
            stream_policy='private_nonblocking_serial',end_to_end_clock='steady_clock',phase_clock='cuda_event_float_ms_to_ns',
            distribution='uniform',dataset_generator='mt19937_64_v1',size=4,seed=1729,nearly_sorted_swaps=0,
            duplicate_cardinality=16,repetitions=2,warmups=1,expected_rows=3,cub_version=300001,run_kind='performance',
            sanitizers=False,build_type='Release',compiler_id='GNU',compiler_version='13.3.0',platform='Linux',
            architecture='x86_64',gpu_name='Tesla T4',cuda_compiler_version='13.0',cuda_toolkit_version='13.0',
            run_id='synthetic_parser_unit_only',runtime_api_version=13000,driver_api_version=13000,
            requested_device=0,actual_device=0,compute_major=7,compute_minor=5,device_memory_bytes=16*1024**3,
            workspace_bytes=32,input_hash_fnv1a64='123')
        out=io.StringIO();writer=csv.DictWriter(out,fieldnames=FIELDS);writer.writeheader()
        for phase,trial in [('warmup',0),('measure',0),('measure',1)]:
            writer.writerow(dict({k:meta[k] for k in SHARED},phase=phase,trial_index=trial,
                **{k:1 for k in METRICS},elapsed_unit='ns',status='ok',correctness='passed',error=''))
        refs={'run.json':self.put('smoke/run.json',meta),'trials.csv':self.put('smoke/trials.csv',out.getvalue().encode()),
              'COMPLETE.json':self.put('smoke/COMPLETE.json',dict(schema_version=1,complete=True,rows=3))}
        return dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate='timing_smoke',context=self.review['context'],raw_files=refs)

    def test_valid_smoke_csv_model_parsed_without_measurements(self):
        self.assertEqual(self.check(self.smoke()),dict(complete=True,correctness=True))

    def test_hash_consistent_missing_duplicate_and_invalid_timing_rows_rejected(self):
        for mode in ['missing','duplicate','invalid']:
            r=self.smoke();raw=self.store().raw(r['raw_files']['trials.csv']).decode();lines=raw.splitlines()
            if mode=='missing':lines.pop()
            elif mode=='duplicate':lines[-1]=lines[-2]
            else:lines[-1]=lines[-1].replace(',1,1,1,1,ns,',',nan,1,1,1,ns,')
            r['raw_files']['trials.csv']=self.put('smoke/trials.csv',('\n'.join(lines)+'\n').encode())
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'completion|duplicate|invalid timing'):self.check(r)

    def identity_fixture(self):
        outputs=identity.EXECUTABLES+('libmab_parallel.a','libmab_cuda_timing.a')
        ref,proof=self.proof(outputs)
        build=Path(proof['build_dir']);build.mkdir()
        cache=self.store().raw(proof['metadata']['CMakeCache.txt'])
        cache+=b'MAB_ENABLE_OPENMP:BOOL=ON\nMAB_ENABLE_CUDA:BOOL=ON\nMAB_ENABLE_CUDA_SORT:BOOL=ON\n'
        cache+=b'MAB_ENABLE_CPU_GPU_COMPARISON:BOOL=ON\nCMAKE_CUDA_ARCHITECTURES:STRING=75\n'
        proof['metadata']['CMakeCache.txt']=self.put('proof/cache',cache)
        self.put('proof/provenance.json',proof)
        # The retained records are copied under the intended build, like a future
        # reviewed build capture. Inert fixture bytes, never executed.
        import shutil
        shutil.copytree(self.root/'proof',build/'proof')
        for name,reference in proof['metadata'].items():
            (build/name).write_bytes(self.store().raw(reference))
        for name in outputs:
            (build/name).write_bytes(b'synthetic executable; never executed')
            if name in identity.EXECUTABLES:(build/name).chmod(0o700)
        return build,build/ref['file']

    def test_capture_requires_compile_link_proof_not_just_json_list(self):
        build,path=self.identity_fixture()
        document=identity.capture(build,path)
        identity.verify(document,build/'cpu_gpu_comparison',build/'comparison_input')
        (build/'compile_commands.json').write_text('[]')
        with self.assertRaisesRegex(ValueError,'empty/malformed compile-command'):identity.capture(build,path)

    def test_actual_fixture_binary_hash_mismatch_and_missing_binary_rejected(self):
        build,path=self.identity_fixture();document=identity.capture(build,path)
        (build/'comparison_input').write_text('stale bytes')
        with self.assertRaisesRegex(ValueError,'stale build output'):identity.verify(document,build/'cpu_gpu_comparison',build/'comparison_input')
        (build/'comparison_input').unlink()  # Inert temporary fixture only.
        with self.assertRaises(OSError):identity.capture(build,path)

    def test_snapshot_only_is_never_accepted_as_provenance(self):
        build,path=self.identity_fixture();document=identity.capture_snapshot(build)
        with self.assertRaisesRegex(ValueError,'missing build provenance identity'):
            identity.verify(document,build/'cpu_gpu_comparison',build/'comparison_input')

    def test_default_guard_still_rejects_changed_source_and_inactive_candidate(self):
        import non_timing_tests as selector
        # v3 remains immutable and must still reject the extended source. A
        # separately reviewed local selection may now be active; do not confuse
        # that activation with accepting the historical v3 or inactive v4.
        with mock.patch.object(selector,'MANIFEST',ROOT/'docs/NON_TIMING_TEST_SELECTION_v3.json'), \
             self.assertRaisesRegex(ValueError,'source snapshot changed'):selector.load_manifest()
        ref=self.put('inactive.json',self.candidate())
        with mock.patch.object(selector,'MANIFEST',self.root/ref['file']),self.assertRaisesRegex(ValueError,'invalid non-timing manifest'):
            selector.load_manifest()  # Pure JSON/source validation, never discovery.

    def workspace(self):
        refs=[]
        for n in [1025,65537,1000000]:
            v=dict(size=n,gpu_name='Tesla T4',compute_major=7,compute_minor=5,
                prepared_query_bytes=32,adapter_query_bytes=32,free_device_bytes_before_buffers=8*1024**3,
                prepared_diagnostic_cudaMalloc_requested_bytes=32,adapter_diagnostic_cudaMalloc_requested_bytes=32,
                combined_device_payload_bytes=16*n+64,known_host_peak_payload_bytes=24*n,
                total_device_bytes=16*1024**3,driver_api_version=13000,runtime_api_version=13000,
                workspace_policy_cap_each_bytes=64*1024**2,
                allocation_observation='successful diagnostic cudaMalloc request sizes; allocator physical footprint not measured',
                production_workspace_observation='not instrumented; isolated same-parameter sizing query only')
            refs.append(self.put('resource_'+str(n),self.cmd([self.review['build_dir']+'/cpu_gpu_comparison','--resources',str(n)],stdout=json.dumps(v))))
        keys=['/sys/fs/cgroup/cpu.max','/sys/fs/cgroup/memory.max','/sys/fs/cgroup/memory.current',
              '/sys/fs/cgroup/memory/memory.limit_in_bytes','/sys/fs/cgroup/memory/memory.usage_in_bytes']
        for directory in ['/sys/fs/cgroup/cpu','/sys/fs/cgroup/cpu,cpuacct']:
            keys.extend(directory+'/'+name for name in ['cpu.cfs_quota_us','cpu.cfs_period_us'])
        env=dict(affinity=[0,1],disk_free_bytes=2*1024**3,linux_meminfo='MemAvailable: 2097152 kB',
                 resource_files={k:None for k in keys},**{n:dict(returncode=0,stdout='') for n in ['nvidia_smi','gpu_processes','gpu_details','nvcc']})
        return dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate='workspace',context=self.review['context'],
                    commands=refs,environment=self.put('environment.json',env))

    def test_valid_workspace_all_sizes_and_retained_host_disk_limits(self):
        self.assertEqual(self.check(self.workspace()),dict(sizes=[1025,65537,1000000],all_limits_passed=True))

    def test_duplicate_workspace_size_or_insufficient_resource_snapshot_rejected(self):
        r=self.workspace();r['commands'][2]=r['commands'][0]
        with self.assertRaisesRegex(ValueError,'duplicate/invalid workspace size'):self.check(r)
        r=self.workspace();env=self.store().json(r['environment']);env['disk_free_bytes']=0
        r['environment']=self.put('environment.json',env)
        with self.assertRaisesRegex(ValueError,'free disk'):self.check(r)

    def workers(self):
        value=dict(schema_version=1,artifact_kind='correctness_validation',scope='openmp_workers_untimed_v1',study_eligible=False,
            status='passed',executable=self.review['build_dir']+'/test_parallel_workers',build_type='Release',sanitizers=False,
            requested_threads=2,runtime_dynamic=0,runtime_thread_limit=2,team_size_is_task_participation=False,
            compiler='13.3.0',flags='-O3 -DNDEBUG',openmp_version='4.5',openmp_flags='-fopenmp',
            environment=protocol.load_protocol()['openmp_policy']['environment'],output_checks=12,
            calls=[dict(size=n,registry=r,correctness=True,actual_team_size=2 if n>=32768 else 1,parallel_region=n>=32768)
                   for n in [0,1,32767,32768,32769,65537] for r in [False,True]])
        record=dict(schema_version=1,kind='cpu_gpu_framework_record_v1',gate='workers',context=self.review['context'])
        return record,value

    def test_valid_worker_threshold_contents_and_conflicting_calls(self):
        for mode in ['valid','duplicate','failed','team','environment']:
            r,v=self.workers()
            if mode=='duplicate':v['calls'][0]=v['calls'][1]
            elif mode=='failed':v['calls'][0]['correctness']=False
            elif mode=='team':v['calls'][-1]['actual_team_size']=1
            elif mode=='environment':v['environment']={}
            r['command']=self.put('workers.json',self.cmd([v['executable']],stdout=json.dumps(v)))
            if mode=='valid':self.assertEqual(self.check(r),dict(output_checks=12,threshold_team_verified=True))
            else:
                with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'worker threshold|worker environment'):self.check(r)


if __name__=='__main__':
    unittest.main()

````

## tests/test_evidence_retention.py

SHA-256: `8c47e1271f436ed8a0cbdb2a40b255c133436bd5667eb5085f12150fe2c46641`

````text
"""Inert graph preservation tests; no CTest, compiler, GPU or timer calls."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from cpu_gpu_evidence_io import digest
from cpu_gpu_retention import retain_evidence


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.target = self.root / 'retained'
        for name in ['subprocess.run', 'subprocess.Popen', 'os.system']:
            guard = patch(name, side_effect=AssertionError('workload forbidden'))
            guard.start()
            self.addCleanup(guard.stop)

    def put(self, name, value):
        raw = value if isinstance(value, bytes) else json.dumps(value).encode()
        p = self.source / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
        return dict(file=name, sha256=digest(raw))

    def test_nested_evidence_remains_self_contained(self):
        child = self.put('nested/command.json', {'stdout': 'observed fixture only'})
        parent = self.put('record.json', {'command': child})
        manifest = retain_evidence({'records': [parent, child]}, self.source, self.target)
        self.assertEqual(set(manifest), {'record.json', 'nested/command.json'})
        self.assertEqual((self.target / child['file']).read_bytes(), (self.source / child['file']).read_bytes())
        self.assertEqual(json.loads((self.target / 'RETAINED_SHA256.json').read_text()), manifest)

    def test_stale_nested_reference_rejected_before_writing(self):
        child = self.put('child.json', {})
        parent = self.put('parent.json', {'child': child})
        self.put('child.json', {'changed': True})
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            retain_evidence(parent, self.source, self.target)
        self.assertFalse(self.target.exists())

    def test_malformed_reference_or_json_fails_closed(self):
        for raw in [b'{', b'{"duplicate":1,"duplicate":2}']:
            ref = self.put('broken.json', raw)
            with self.assertRaises(ValueError):
                retain_evidence(ref, self.source, self.target)
        ref = self.put('valid.json', {})
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            retain_evidence(dict(ref, ignored=True), self.source, self.target)
        self.assertFalse(self.target.exists())

    def test_unsafe_path_and_alias_rejected(self):
        ref = self.put('valid.json', {})
        (self.source / 'alias.json').symlink_to('valid.json')
        for name in ['../valid.json', './valid.json', 'alias.json']:
            with self.assertRaises((ValueError, OSError)):
                retain_evidence(dict(ref, file=name), self.source, self.target)
        self.assertFalse(self.target.exists())

    def test_existing_output_never_merged_or_overwritten(self):
        ref = self.put('valid.json', {})
        self.target.mkdir()
        sentinel = self.target / 'keep'
        sentinel.write_text('historical')
        with self.assertRaises(FileExistsError):
            retain_evidence(ref, self.source, self.target)
        self.assertEqual(sentinel.read_text(), 'historical')

    def test_conflicting_reference_cannot_change_snapshot(self):
        ref = self.put('valid.json', {})
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            retain_evidence([ref, dict(ref, sha256='0' * 64)], self.source, self.target)
        self.assertFalse(self.target.exists())


if __name__ == '__main__':
    unittest.main()

````

## tests/test_learned_index.cpp

SHA-256: `6562b2ce5a089a23ec074be5f1362d33c9dcd28a3b6802a42f5ee61ee9072b51`

````text
#include "indexes/learned_index.hpp"
#include "datasets/generator.hpp"

#include <algorithm>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>

namespace {
std::size_t datasets = 0, checks = 0, fallbacks = 0;
void verify(mab::Values values, const mab::Values& queries) {
    std::sort(values.begin(), values.end());
    const mab::LearnedIndex index(values);
    const auto copy = index;
    if (index.size() != values.size() || index.owned_capacity_bytes() < values.size() * sizeof(mab::Key))
        throw std::runtime_error("size/storage mismatch");
    ++datasets;
    for (const auto key : queries) {
        const auto it = std::lower_bound(values.begin(), values.end(), key);
        const auto position = static_cast<std::size_t>(it - values.begin());
        const mab::SearchResult expected = it != values.end() && *it == key ? mab::SearchResult(position) : std::nullopt;
        const auto diagnostic = index.diagnose(key);
        const auto repeat = index.diagnose(key);
        if (index.find(key) != expected || copy.find(key) != expected || diagnostic.result != expected ||
            diagnostic.lower_bound_position != position || repeat.comparisons != diagnostic.comparisons ||
            repeat.fallback != diagnostic.fallback || diagnostic.correction_distance !=
            (position > diagnostic.predicted_position ? position - diagnostic.predicted_position : diagnostic.predicted_position - position))
            throw std::runtime_error("learned-index oracle/diagnostic mismatch");
        ++checks;
        if (diagnostic.fallback) ++fallbacks;
    }
}
}

int main() {
    try {
        const auto low = std::numeric_limits<mab::Key>::min();
        const auto high = std::numeric_limits<mab::Key>::max();
        const mab::Values edges{low, low + 1, -2, -1, 0, 1, 2, high - 1, high};
        for (const auto& data : std::vector<mab::Values>{{}, {0}, {low}, {high}, {1, 0}, edges,
                mab::Values(1000, 0), {-9, -9, -9, -1, 2, 2, 2}, {low, 0, 0, 0, high}}) verify(data, edges);
        bool rejected = false;
        try { const mab::LearnedIndex bad({1, 0}); } catch (const std::invalid_argument&) { rejected = true; }
        if (!rejected) throw std::runtime_error("unsorted input accepted");
        // Hand-verifiable predicate counts: empty does no key work; singleton
        // equal performs one lower-bound predicate and one equality predicate.
        if (mab::LearnedIndex({}).diagnose(0).comparisons != 0 ||
            mab::LearnedIndex({0}).diagnose(0).comparisons != 2 ||
            mab::LearnedIndex({-1, 1}).diagnose(0).comparisons != 6)
            throw std::runtime_error("small exact comparison count mismatch");
        for (const auto seed : {1729ULL, 42ULL, 2718ULL}) {
            for (const auto size : {0U, 1U, 2U, 31U, 32U, 33U, 63U, 64U, 65U, 127U, 1025U, 65537U}) {
                for (const auto distribution : {mab::Distribution::uniform, mab::Distribution::nearly_sorted,
                        mab::Distribution::reverse_sorted, mab::Distribution::duplicate_heavy}) {
                    mab::DatasetConfig config;
                    config.size = size; config.seed = seed; config.distribution = distribution;
                    auto data = mab::generate_dataset(config);
                    auto queries = edges;
                    // Every key for small datasets, deterministic spaced keys for larger ones.
                    const auto stride = std::max<std::size_t>(1, data.size() / 1000);
                    for (std::size_t i = 0; i < data.size(); i += stride) queries.push_back(data[i]);
                    std::mt19937_64 engine(seed);
                    for (int i = 0; i < 100; ++i) queries.push_back(static_cast<mab::Key>(
                        static_cast<std::int64_t>(engine() & 0xffffffffULL) - 2147483648LL));
                    verify(std::move(data), queries);
                }
            }
        }
        if (fallbacks == 0) throw std::runtime_error("fallback was not exercised");
        std::cout << "learned index: " << datasets << " datasets, " << checks
                  << " oracle checks, " << fallbacks << " observed fallbacks; unsorted rejection passed\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}

````

## tests/test_learned_study.py

SHA-256: `4e3cc8fe1398c5a256bb45c8cf2e19d2ec4b1fecee4aa4c1b2a9a8a5969b5e40`

````text
"""Synthetic analysis regressions: never launches a benchmark or subprocess."""
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import learned_study as study


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cell = dict(id='fixture', size=1000, seed=42, distribution='uniform')
        self.forbid = patch('subprocess.run', side_effect=AssertionError('workload forbidden'))
        self.forbid.start(); self.addCleanup(self.forbid.stop)
        self.encode('COMPLETE.json', dict(complete=True, rows=18, diagnostic_queries=1000))
        self.encode('run.json', dict(schema_version=1, protocol='learned_rank_v1', size=1000, seed=42, distribution='uniform',
            query_seed=2718, queries=1000, hits=500, misses=500, warmups=1, repetitions=5, radius=32,
            build_type='Release', clock='steady_clock', input_fingerprint='123', query_fingerprint='456'))
        self.encode('memory.json', dict(owned_capacity_bytes=4000, object_bytes=24))
        self.rows = []
        for phase, rounds in [('warmup', 1), ('measure', 5)]:
            for trial in range(rounds):
                self.rows.append(['learned_rank', 'build', phase, trial, 0, (trial + 1)*1000, 0, 'passed'])
                for order in range(2):
                    algorithm = study.ALGORITHMS[(trial + order) % 2]
                    self.rows.append([algorithm, 'lookup_batch', phase, trial, order, (trial + 1)*100, 1000, 'passed'])
        self.save_rows()
        with (self.root / 'diagnostics.csv').open('w', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['query_id', 'target', 'expected_position', 'actual_position', 'predicted_position', 'lower_bound_position',
                'correction_distance', 'fallback', 'learned_comparisons', 'binary_comparisons'])
            for q in range(1000): writer.writerow([q, q, q if q % 2 == 0 else '', q if q % 2 == 0 else '', q, q, 0, 'false', 4, 10])

    def encode(self, name, data): (self.root / name).write_text(json.dumps(data))
    def save_rows(self):
        with (self.root / 'trials.csv').open('w', newline='') as stream:
            writer = csv.writer(stream); writer.writerow(study.FIELDS); writer.writerows(self.rows)
    def test_valid_statistics(self):
        result = study.validate_cell(self.root, self.cell)
        lookup = next(t for t in result['timings'] if t['algorithm'] == 'binary_search')
        self.assertEqual(lookup['median'], 300); self.assertEqual(lookup['mean'], 300)
        self.assertAlmostEqual(lookup['sample_sd'], 158.113883008419)
        self.assertEqual((lookup['minimum'], lookup['maximum'], lookup['n']), (100, 500, 5))
    def test_missing(self):
        self.rows.pop(); self.save_rows()
        with self.assertRaisesRegex(ValueError, 'missing trials'): study.validate_cell(self.root, self.cell)
    def test_duplicate(self):
        self.rows[-1] = self.rows[-2]; self.save_rows()
        with self.assertRaisesRegex(ValueError, 'duplicate'): study.validate_cell(self.root, self.cell)
    def test_failed(self):
        self.rows[-1][-1] = 'failed'; self.save_rows()
        with self.assertRaisesRegex(ValueError, 'failed/unknown'): study.validate_cell(self.root, self.cell)
    def test_wrong_identity(self):
        with self.assertRaisesRegex(ValueError, 'configuration mismatch'): study.validate_cell(self.root, dict(self.cell, seed=43))
    def test_invalid_time(self):
        self.rows[-1][5] = '-1'; self.save_rows()
        with self.assertRaisesRegex(ValueError, 'numeric'): study.validate_cell(self.root, self.cell)
    def test_wrong_order(self):
        self.rows[-1][4] = 7; self.save_rows()
        with self.assertRaisesRegex(ValueError, 'order'): study.validate_cell(self.root, self.cell)
    def test_interrupted(self):
        self.encode('FAILED.json', dict(error='interrupted'))
        with self.assertRaisesRegex(ValueError, 'failed configuration'): study.validate_cell(self.root, self.cell)
    def test_hit_ratio(self):
        text = (self.root / 'diagnostics.csv').read_text().replace('0,0,0,0,0,0,0,false', '0,0,,,0,0,0,false')
        (self.root / 'diagnostics.csv').write_text(text)
        with self.assertRaisesRegex(ValueError, 'ratio'): study.validate_cell(self.root, self.cell)


if __name__ == '__main__': unittest.main()

````

## tests/test_selection_activation.py

SHA-256: `ff6f7af55b8f426545e6e0fbb9dbf206b9931781c43bd41faefa00bb8f65415a`

````text
"""Inert source-review activation checks; never invokes discovery or tests."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import non_timing_tests as selector


class ActivationTests(unittest.TestCase):
    def setUp(self):
        self.manifest = selector.load_manifest()
        self.forbid = patch('subprocess.run', side_effect=AssertionError('discovery forbidden'))
        self.forbid.start(); self.addCleanup(self.forbid.stop)

    def test_approved_names_and_scope_unchanged(self):
        base = json.loads((selector.ROOT / 'docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())
        for key in ['tests', 'cpu_build_tests', 'cuda_additional_tests', 'build_metadata']:
            self.assertEqual(self.manifest[key], base[key])
        self.assertEqual(sum(e['classification'] == 'cpu_correctness' and not e.get('diagnostic_only') for e in base['tests'].values()), 19)
        self.assertFalse(self.manifest['full_study_eligible'])

    def test_add_remove_and_changed_source_rejected(self):
        for kind in ['add', 'remove', 'change']:
            source = dict(self.manifest['reviewed_source_sha256'])
            key = next(iter(source))
            if kind == 'add': source['scripts/unreviewed.py'] = 'a' * 64
            elif kind == 'remove': source.pop(key)
            else: source[key] = 'a' * 64
            with self.subTest(kind=kind), patch.object(selector, 'source_manifest', return_value=source):
                with self.assertRaisesRegex(ValueError, 'source snapshot changed'): selector.load_manifest()

    def test_manifest_cannot_change_approved_command_or_selection(self):
        original = selector.strict_json
        for key in ['tests', 'cpu_build_tests', 'cuda_additional_tests', 'build_metadata']:
            changed = copy.deepcopy(self.manifest); changed[key] = {} if isinstance(changed[key], dict) else []
            def parse(text):
                value = original(text)
                return changed if value.get('schema_version') == 5 else value
            with self.subTest(key=key), patch.object(selector, 'strict_json', side_effect=parse):
                with self.assertRaisesRegex(ValueError, 'changed approved selection'): selector.load_manifest()


if __name__ == '__main__': unittest.main()

````

