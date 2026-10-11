"""Evidence-only design/report assembly. No project imports, tests or subprocesses."""
import datetime
import hashlib
import json
import shlex
from pathlib import Path

R = Path.cwd()
E = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    with (E / name).open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')

b = json.loads((E / 'BEFORE.json').read_text())
preservation = {}
for key, mapping in b.items():
    bad = [p for p, h in mapping.items() if not (R / p).is_file() or sha(R / p) != h]
    assert not bad, (key, bad)
    preservation[key] = {'verified': len(mapping), 'changed_or_missing': bad}
actual = {str(p.relative_to(R)) for p in (R / 'results').rglob('*') if p.is_file() and not p.is_relative_to(E)}
assert actual == set(b['historical_results_sha256'])
preservation['historical_membership'] = {'before': len(actual), 'after': len(actual), 'missing': [], 'unexpected': []}
old = R / 'results/raw/cpu_gpu_prelaunch_validation_20261011T014309468088Z'
previous = json.loads((old / 'FINAL_INTEGRITY.json').read_text())['evidence_sha256']
assert all(sha(old / p) == h for p, h in previous.items())
assert set(previous) == {str(p.relative_to(old)) for p in old.rglob('*') if p.is_file() and p.name != 'FINAL_INTEGRITY.json'}
preservation['latest_validation_sealed_members_verified'] = len(previous)
freeze = R / 'docs/studies/cpu_gpu_comparison_v1.freeze.json'
assert sha(freeze) == '518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6'
members = json.loads(freeze.read_text())['files_sha256']
assert all(sha(R / p) == h for p, h in members.items())
matrix = json.loads((R / 'docs/studies/cpu_gpu_comparison_v1.matrix.json').read_text())
anchors = matrix['source_at_freeze_sha256'].copy()
review = R / 'docs/CPU_GPU_DRIVER_REVIEW_v1.json'
assert sha(review) == 'b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a'
exception = json.loads(review.read_text())
assert anchors['CMakeLists.txt'] == exception['frozen_cmake_sha256']
anchors['CMakeLists.txt'] = exception['current_cmake_sha256']
assert all(sha(R / p) == h for p, h in anchors.items())
initial = json.loads((R / 'results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/BEFORE.json').read_text())['current_source_sha256']
production = {p: h for p, h in initial.items() if p.startswith(('src/', 'include/', 'third_party/')) or p == 'CMakeLists.txt'}
assert all(sha(R / p) == h for p, h in production.items())
pin = R / 'third_party/cub/UPSTREAM.json'
assert sha(pin) == '477b1ee70b0a9113c9f98b263c19a31d05ccee54f45ce8476aec4cc98965ced1'
policy = json.loads((R / 'docs/NON_TIMING_TEST_SELECTION_v1.json').read_text())
assert all(sha(R / p) == h for p, h in policy['reviewed_source_sha256'].items())
cpu = sorted(n for n, t in policy['tests'].items() if t['classification'] == 'cpu_correctness')
assert len(cpu) == 19 and 'parallel_mergesort' not in cpu
preservation.update(frozen_members_sha256=members, effective_anchors_verified=len(anchors),
                    production_header_dependency_files_verified=len(production),
                    reviewed_source_files_verified=len(policy['reviewed_source_sha256']),
                    cub_pin_sha256=sha(pin))
save('PRESERVATION.json', preservation)
sessions = json.loads((E / 'current_sessions.json').read_text())
status = json.loads((E / 'current_status.json').read_text())
assert 'No active sessions found' in sessions['stdout']
assert "Session 'cpu-gpu-validation' not found" in status['stdout']

design = {
    'design_only': True, 'validation_executed': False,
    'approved_cpu_selection': cpu,
    'frozen_sizes': [row['size'] for row in matrix['resources']['table']],
    'resource_formulas_and_limits': matrix['resources'],
    'openmp_policy': matrix['openmp_policy'],
    'changes_implemented': [],
    'gate_paths': {
        '1_cpu': 'Existing 19-test manifest and shared static guard/selector; no new algorithm/test code required. Approved isolated orchestration still needed.',
        '2_sanitizers': 'Existing Debug ASan/UBSan flags and same selection; no new algorithm/test code required.',
        '3_prepared_gpu': 'Existing constructor/info/close covers initialization only. No untimed prepared execution API. New test-only executable plus explicitly reviewed shared untimed execution access/refactor is needed for full coverage.',
        '4_resources': 'Existing worker --resources N early-return branch and bounded query/allocation diagnostic; no new code required for all frozen sizes.',
        '5_workers': 'New test-only executable directly calling production public/registry sorter, checking returned actual team and oracle output; optional separate observer diagnostics must distinguish task participation from team size.'
    },
    'unresolved_eligibility': 'Existing correctness-only prerequisite scope is intentionally rejected for full study. A separately reviewed explicit eligibility mapping/versioned extension is required; never relabel a 19-test subset full_protocol_v1.'
}
save('VALIDATION_DESIGN.json', design)

audit = '''# Session recovery investigation and correctness-only validation design

**NO-GO — validation not executed**

This task performed installed-help/documentation and local source/evidence inspection, plus the documented active-session list/status lookups. It did not execute tests, CTest discovery, builds, sanitizer tools, GPU/resource probes, workloads or benchmarks. No proposal below was implemented or run. All existing project/evidence files were preserved.

## A. Session recovery

Installed `colab version` reports **0.7.4** (exit0). Read `colab --help`, bundled `colab readme`, and help for sessions/status/url/console/ssh. The supported documented non-destructive operations `colab sessions` and `colab status --session cpu-gpu-validation` both exited0, but again reported **no active sessions on the server** and **session not found**. These are semantic recovery failures despite shell success. No recovery was achieved, no replacement was provisioned, and no remote command or GPU/resource probe was issued.

`colab url --session cpu-gpu-validation --open` is the documented browser-attach operation **only if that original session is active and identifiable again**. Its help explicitly describes attachment to an existing VM without assignment; it does not revive a missing VM. The command was not executed, so no session URL was printed/stored. In contrast, `colab ssh` help explicitly says that both bare invocation and `-s NAME` can create a missing session. It is not a safe recovery shortcut and was not invoked. No restart-kernel, new, run, console, repl, exec, auth, install or update action was attempted.

There is no documented restore/revive operation in the installed CLI help/README for an endpoint absent from the backend list. This does not prove permanent deletion or that a different authenticated browser could never locate the VM. User action: inspect the original Colab browser workspace's **Runtime → Manage sessions** for the already allocated runtime; this UI inspection is a recommendation, not a tested recovery procedure. Do not allocate or switch runtimes as a substitute. If the original runtime is still present, re-establish its visibility/identity and then use the documented existing-session URL operation. If absent, recovery is unresolved and replacement requires separate authorization. Do not send tokens/codes/cookies. No credential/config files were read and no auth override was chosen. Installed main help and README disagree about the default auth strategy; this investigation did not guess or change it.

Part A stops at the absence of a documented recovery operation for the current state. Part B below is independent static design work, not an attempt to bypass that stop.

## B. Five validation paths — proposed, not executed

### 1. CPU regression: reuse existing correctness targets

Files: CMakeLists.txt; docs/NON_TIMING_TEST_SELECTION_v1.json; scripts/non_timing_tests.py; scripts/ctest_build_guard.py; relevant source/test hashes embedded in that reviewed manifest. The approved CPU selection is:

`baselines, cli, comparisons, cpu_gpu_comparison_framework, cuda_benchmark_analysis, cuda_preflight, cuda_sort_handoff, datasets, environment_manifest, memory, memory_unsupported, mergesort, metrics_cli, pdqsort, quicksort, radixsort, searching, structures, timsort`.

The manifest supplies exact executable/Python argv and classification, not just names. C++ targets include test_baselines/test_comparisons/test_datasets/test_memory/test_memory_unsupported/test_mergesort/test_pdqsort/test_quicksort/test_radixsort/test_searching/test_structures/test_timsort; Python entries invoke the reviewed correctness CLI/input/metrics tools or synthetic framework analysis. In particular, cuda_benchmark_analysis supplies **no GPU executable**, causing the GPU CLI class to skip; that does not constitute a passed GPU test. Some approved host tests run CUDA-OFF CMake option checks or other subprocesses, so correctness-only is not synonymous with read-only.

Reuse the intended Release configuration from scripts/validate_cpu_gpu_pilot.py:43–47 in a new exclusive absolute build directory: C++17, -O3 -DNDEBUG, empty global CXX flags, MAB_ENABLE_OPENMP=ON, BUILD_TESTING=ON, MAB_ENABLE_CUDA=OFF, MAB_ENABLE_CPU_GPU_COMPARISON=OFF, sanitizersOFF. Configuration/build is future work requiring execution authorization, not part of this investigation. No new algorithm/test implementation is needed for these19 groups.

Before any discovery, call the existing **pre_discovery_gate** on the canonical absolute directory. It checks exact reviewed source membership/hashes, rejects CTEST environment overrides, symlinked/unknown/unreadable/malformed metadata, directory hooks, includes/subdirs and unreviewed commands/properties/fixtures/dependencies. It supports only its reviewed flat layout; do not broaden that layout to make a build pass. Keep source/build trees quiescent.

Conditional future **discovery-only** command template (not run; variables must first identify verified, absolute paths and NEW_EVIDENCE must be exclusive):

```bash
python3 -B scripts/non_timing_tests.py --build-dir "$ABS_RELEASE_BUILD" --output "$NEW_EVIDENCE/release_selection.json"
```

The CLI guards **before** discovery and returns only a plan. Review its discovered registry completeness, exact19 selected names, command/property matches and exclusions. Never run broad CTest or a name-only handcrafted regex. For later execution reuse `selected_ctest(call, output, name, canonical_build, allow_gpu=False)` with a reviewed command recorder; it retains the guard's absolute path and rechecks metadata/source before execution (non_timing_tests.py:133–150). This requires a narrow orchestration invocation reviewed before execution, not the all-in-one pilot validator. Pass criteria: all expected19 groups executed successfully, no unexpected/missing groups or CTest-level skips/failures, documented intentional Python GPU-method skips, full logs, before/after identities. Risk: reviewed source or generated registry changes must fail closed, even if changes appear harmless.

### 2. ASan/UBSan: reuse same approved selection

Actual configuration is in **CMakeLists.txt:27–33**, not a separate cmake/sanitizers.cmake: GCC/Clang only, compile `-fsanitize=address,undefined -fno-omit-frame-pointer`, link `-fsanitize=address,undefined`. Use separate Debug, CUDA-OFF/OpenMP-ON build with MAB_ENABLE_SANITIZERS=ON, same source and19-test selection, and retained cache/compile commands proving flag propagation. No new correctness code is required. Timing/benchmark targets remain excluded even if compiled.

Conditional future sanitizer **discovery-only** plan:

```bash
python3 -B scripts/non_timing_tests.py --build-dir "$ABS_SANITIZER_BUILD" --output "$NEW_EVIDENCE/sanitizer_selection.json"
```

After review, use selected_ctest with the established prefix `['env','-u','ASAN_OPTIONS','-u','LSAN_OPTIONS','UBSAN_OPTIONS=halt_on_error=1']`. Only if retained output actually reproduces `LeakSanitizer does not work under ptrace`, preserve that failed attempt and use the established detect_leaks=0 rerun. Any other failure stops. Do not pre-disable leaks or change flags/tests. Pass:19 approved groups complete, no sanitizer findings/unexplained failures/skips, flags and leak policy supported by logs. CPU sanitizers do not validate GPU memory, and ordinary/OpenMP correctness tests do not prove race freedom.

### 3. Prepared GPU framework: new untimed execution access is required

Files: include/benchmark/cuda_timing.hpp:19–34; src/cuda/cub_timing.cu:43–118; tests/test_cuda_benchmark.py:147–167; src/benchmark/cuda_main.cpp:142–161; tests/test_cuda_sorting.cpp for the independent production oracle pattern.

Current reusable API exposes constructor, info(), close() and **sample() only**. Constructor/info/close can validate initialization/lifetime with no sort or elapsed-time query, but this proves neither transfers nor prepared-sort output. sample() always measures host/event timings, including trivial sizes. `--validation-only` changes a label/build restriction; the benchmark still runs warm-up/measure loops and serializes latency rows. The real GPU framework test passes W1/R2 across sizes/distributions and is forbidden unchanged. Production cub_radix_sort correctness cannot substitute for the different prepared-buffer/private-stream path.

Propose a new isolated correctness-only test executable reusing deterministic input/oracle routines: empty/singleton, signed extrema, duplicates, ordered/reverse, seeded random, threshold-adjacent/non-power-of-two sizes; restored inputs, complete-vector equality, repeated/interleaved sizes, invalid buffer/lifetime cases, explicit checked cleanup and CUDA error status. It must have no performance CLI, sample(), clock reads, CUDA-event recording/elapsed queries, warm-up/measure phases, benchmark CSV or timing statistics. Record input/check counts and source/dependency/binary identity instead.

**Important implementation dependency:** an entry point alone cannot access the session's private buffers or reuse an untimed prepared execution path, because none exists. Full production-framework coverage requires separately approved minimal shared untimed transfer/SortKeys/synchronize/output access, with the existing timed sample wrapping that same core. This may involve a small internal framework refactor/access API, not merely adding a test file. Preserve the production cub_radix_sort adapter and all existing timed boundaries; validate any refactor separately. A separate raw-CUB test that duplicates the pipeline proves CUB behavior, not the existing framework, and cannot close this gate alone. Until the refactor/access and protected-identity implications are reviewed, there is **no safe existing full-coverage command** to propose. Initialization-only coverage is partial and must be labelled so.

### 4. Workspace/resources: existing bounded non-timing diagnostic

Files: include/benchmark/cuda_comparison.hpp; src/cuda/comparison_resources.cu:32–62; src/benchmark/cpu_gpu_main.cpp:87–88; frozen matrix/resources/protocol. The complete frozen size domain is **1,025;65,537;1,000,000**. All are supported by the diagnostic's [2,1M] bound;0/1 are unsupported by this API but outside this matrix.

After future environment/source/binary verification and headroom approval, the safe **diagnostic command templates** are:

```bash
"$VERIFIED_COMPARISON_EXECUTABLE" --resources 1025
"$VERIFIED_COMPARISON_EXECUTABLE" --resources 65537
"$VERIFIED_COMPARISON_EXECUTABLE" --resources 1000000
```

This early-return branch never enters the worker's sort/trial path. It calls signed-int32 CUB SortKeys with null temporary storage, bits[0,32), default stream and private nonblocking stream, querying the two requirements independently. It does **not** execute the sorting API with allocated temporary storage. It does perform checked diagnostic allocations: two4N device key buffers (8N total), then both max(W,1) workspaces, with checked releases. The API snapshots cudaMemGetInfo before allocation, checks16N<=half free memory before keys, checks each workspace<=64MiB and the full-study device estimate<=256MiB/half free before workspaces. It does not allocate the host/oracle/working/pinned full benchmark workload or both persistent device key pairs. No timings are returned. This is not a zero-allocation sizing API.

Future procedure: preserve point-in-time RAM/cgroup/CPU/disk/GPU identity and competing-process diagnostics outside workloads; require1GiB MemAvailable and applicable cgroup headroom and1GiB disk. Run one supported size at a time, retain raw diagnostic JSON and exit status, independently check units/arithmetic and requirements/allocations. Stop on cap/driver/allocation/cleanup errors. Do not enlarge caps. No new code is needed for this bounded procedure. If zero allocations are required instead, the existing API cannot meet that stricter requirement; a separately reviewed query-only diagnostic would be needed. No assumptions about querying with invalid/null key pointers are made.

| N | Estimated host24N bytes | Diagnostic device requested payload8N+Wa+Wp, excluding context | Full-study device estimate16N+Wa+Wp |
|---:|---:|---|---|
|1,025|24,600|8,200+Wa+Wp|16,400+Wa+Wp|
|65,537|1,572,888|524,296+Wa+Wp|1,048,592+Wa+Wp|
|1,000,000|24,000,000|8,000,000+Wa+Wp|16,000,000+Wa+Wp|

Wa/Wp are max(queried bytes,1). Report queries, cudaMalloc requested bytes/success and free-memory snapshots separately from **physical allocation or RSS**; allocator/context/staging overhead is not isolated. Pass: every frozen size has both checked queries/allocations/cleanup and independently verified headroom/caps. A snapshot cannot guarantee later availability. Resource checks do not authorize the study.

### 5. Actual worker verification: add a test-only entry point

Files: include/algorithms/parallel_mergesort.hpp:7–16; include/algorithms/detail/parallel_mergesort_impl.hpp:46–89; src/algorithms/parallel_mergesort.cpp:7–8; tests/test_parallel_mergesort.cpp:11–28,103–108. Production parallel_merge_sort and registry calls are untimed. At requested threads2, sizes below32,768 stay serial; at/above32,768, actual team size is captured **inside** the OpenMP region using omp_get_num_threads(). Task grain is16,384. The combined existing test unconditionally adds six timing rows, so it must not run.

Propose a new small standalone correctness executable linked to the same reviewed mab_parallel implementation/build as the comparison worker. Use fixed inputs at0/1/32,767/32,768/32,769/65,537, boundary/extreme/duplicate/random fixtures and repeated public/registry calls; check full std::sort/sequential output equality, parallel_region and actual_threads (1 below threshold,2 at/above). No timing headers, clock calls, trial engine, warm-ups or performance outputs. Apply frozen OMP_DYNAMIC=FALSE, OMP_THREAD_LIMIT=2, OMP_MAX_ACTIVE_LEVELS=1, OMP_PROC_BIND=FALSE, OMP_WAIT_POLICY=PASSIVE. No new production-sort implementation is needed.

Retain actual CPU affinity/cgroup quota and logical/physical topology, runtime linkage, compile flags, both diagnostic and comparison-worker hashes, source manifest and shared-library/archive identity. An unbound separate executable does not prove the reviewed worker uses the same implementation. Resolve the old worker mismatch by new matching identities, not by reusing prior PREREQUISITES.json.

The returned actual_threads is **team size, not the number of distinct workers executing tasks** (explicit in parallel_mergesort.hpp:11). An optional separate internal Observer test can reuse the existing atomic task/worker-mask pattern to report participation; that is instrumented diagnostic coverage, not the public uninstrumented worker. Two created team members do not guarantee both execute tasks on every run. Do not force task scheduling/barriers or assert more participation than observed. Pass/fail should enforce the frozen actual-team contract; report a one-worker task mask distinctly if it occurs. Ordinary tests cannot prove race freedom. No command is specified for this not-yet-existing executable.

## C. Integration and remaining blockers

CPU regression/sanitizer selection and bounded resource checks reuse current code. Actual-team validation needs a new test-only entry point. Full prepared-framework validation needs new test code **and** reviewed untimed access/shared-core work; initializer-only reuse is insufficient. No such additions were made.

Source-policy hashes cover the complete reviewed implementation set. Adding test files/targets or changing framework internals can invalidate the source snapshot/build registry/protected anchors, even if the intent is test-only. Obtain separate implementation approval and independent source/policy review; do not silently update frozen files, CMake exception pins or classification hashes. If the frozen identity contract disallows the proposed framework change, report that conflict and propose a new separately approved version while preserving v1, rather than modifying it in place.

There is also an explicit prerequisite-eligibility mismatch: scripts/validate_cpu_gpu_pilot.py produces non_timing_correctness_v1/study_eligible=false for its safe subset; scripts/analyze_cpu_gpu.py:88–103 and run_cpu_gpu_pilot.py reject it for full study. The broader validator runs timing-bearing GPU tests and then a pilot. Do not execute it or rebrand19 groups as full_protocol_v1. A separately reviewed eligibility mapping/versioned validation extension must state which new correctness diagnostics satisfy the frozen requirements, with provenance/resource/team bindings. This design does not approve that change.

Remaining blockers: original approved session absent; remote source/executable identity unavailable; GPU untimed API/coverage absent; standalone worker diagnostic absent; reviewed policy/eligibility integration unresolved. No current gate passed. Historical production correctness and warning analysis remain historical, not new validation. No performance claim is made.

## D. Evidence, commands and preservation

All operations and statuses are in COMMANDS.md/per-command JSON. Two read-only inspection attempts failed and are preserved: precise_interfaces exited1 because the system Python environment lacks google-colab-cli distribution metadata (the installed CLI itself worked and reported0.7.4); corrected_interfaces exited1 because cmake/sanitizers.cmake does not exist. Its earlier interface reads succeeded; the actual sanitizer configuration was then inspected in CMakeLists.txt with exit0. Neither is a failed validation test or an attempted dependency repair. Batched help/read commands have recorded overall shell statuses, not invented separate statuses. No credentials or credential files were inspected.

Independently verified the latest validation's14 sealed members with exact membership. All **11,874** starting result files retain exact membership and SHA256 contents, excluding only this new directory; the count includes the prior validation's15 files. Also verified177 project files,65 build-metadata entries,26 effective protected anchors (existing approved CMake exception only),80 production/header/dependency files,144 reviewed source entries, the frozen three members/freeze manifest and unchanged CUB3.0.1 pin. See PRESERVATION.json and FINAL_INTEGRITY.json. No source, test, CMake/build metadata, protocol or previous evidence file changed. Only this new design evidence was written.

Stop here. Recovery and implementation/execution decisions remain separate. No study authorization is requested or implied.

NO-GO — validation not executed
'''
with (E / 'FINAL_AUDIT.md').open('x') as f:
    f.write(audit)
lines = ['# Recovery/design inspection commands', '',
         'No validation workload, GPU/resource probe, CTest discovery, build, benchmark or replacement session was executed. Proposed commands in FINAL_AUDIT.md were not run.', '']
for item in json.loads((E / 'CONTROL_COMMANDS.json').read_text()):
    lines += ['## Baseline creation', '', 'Exit:0; local hashing and exclusive new evidence writes.', '', '```bash', item['command'], '```', '']
statuses = {}
for p in sorted(E.glob('*.json')):
    d = json.loads(p.read_text())
    if not isinstance(d, dict) or not {'argv', 'exit_code', 'scope'} <= d.keys():
        continue
    statuses[p.name] = d['exit_code']
    lines += ['## ' + p.name, '', 'Exit:' + str(d['exit_code']) + '; classification: ' + d['scope'], '',
              '```bash', shlex.join(d['argv']), '```', '', 'cwd: `' + d['cwd'] + '`.', '']
assert {k for k, v in statuses.items() if v != 0} == {'precise_interfaces.json', 'corrected_interfaces.json'}
lines += ['## Evidence-only tool action and final seal', '',
          'apply_patch added only this new directory\'s finalize.py and returned success; no project implementation changed.', '',
          '```bash', 'python3 -B ' + str(E.relative_to(R) / 'finalize.py'), '```', '',
          'Exit:0 upon successful completion. Standard-library reads/hashes and exclusive evidence writes only; no subprocesses, project imports or workloads. Its source is retained.', '',
          'Each recorded command used the evidence recorder wrapper `python3 -B ' + str(E.relative_to(R) / 'record.py') + ' NAME SCOPE TIMEOUT CHILD_ARGV...`.',
          'Terminal polls retrieved output of baseline hashing only. The recorder redacts URL-shaped public documentation text; original local source/help remains authoritative.']
with (E / 'COMMANDS.md').open('x') as f:
    f.write('\n'.join(lines) + '\n')
manifest = dict(schema_version=1, verdict='NO-GO — validation not executed',
                created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                existing_session_recovered=False, replacement_created=False, validation_executed=False,
                builds=0, tests=0, ctest_discovery=0, gpu_execution=0, resource_probes=0,
                warmups=0, measured_trials=0, source_changes=[], study_authorized=False,
                command_exit_codes=statuses, preservation=preservation,
                evidence_sha256={str(p.relative_to(E)): sha(p) for p in sorted(E.rglob('*')) if p.is_file()},
                seal_note='Self excluded. Retained local integrity, not external signed attestation.')
save('FINAL_INTEGRITY.json', manifest)
assert all(sha(E / p) == h for p, h in manifest['evidence_sha256'].items())
print(json.dumps({'verdict': manifest['verdict'], 'historical_files_preserved': len(actual),
                  'sealed_members': len(manifest['evidence_sha256']), 'exit_code': 0}, indent=2))
