# Independent CPU/GPU safety-repair review

**Decision: NO-GO.** Analyzer provenance repair passes this review. Preservation
checks pass. The reusable non-timing selector still lacks a guard against
directory-level CTest hooks/includes, including before discovery. Do not run fresh
prerequisites, resource checks or the study on this decision. This review ends here.

Evidence directory: `results/raw/cpu_gpu_repair_review_20261010T185659333607Z/`.
Only this new directory was written. No project source/document, frozen input,
production adapter, existing build metadata or historical evidence was modified.

## Scope and method

Read AGENTS.md and the repair and previous review's FINAL_AUDIT.md, COMMANDS.md
and FINAL_INTEGRITY.json first. Reviewed current README/roadmap/protocol, source,
CTest registrations, selection manifest, regression fixtures, retained outputs and
installed CMake documentation. STATIC_INVENTORY.json identifies55 exact project
files with hashes/line references, plus inspected local build metadata. Command
records retain full source-inspection output. Reviewed evidence also includes
the accepted pilot source provenance/processed summaries, old tooling seal,
workspace history covered by retained result hashes, repair BEFORE.json,
attempt1/ files, FULL_ANALYSIS_PROBE.json and focused/framework command logs.

No CTest command (including discovery), test suite, sorter, benchmark, GPU command,
prerequisite validator, fresh resource check or summary regeneration was run.
The only executable review logic beyond file reads/hashing/AST parsing calls pure
provenance and selection functions with subprocess.run/Popen blocked. It never
calls selected_ctest, analyzer analyze/main, environment/resource gates or a test
runner. Inert metadata fixtures under UNEXECUTED_* were never interpreted by CTest.

## Review A — PASS, with explicit trust boundaries

Production analysis path is scripts/analyze_cpu_gpu.py main:346 -> analyze:117.
Run-kind gate:123 requires performance unless the internal API explicitly opts
into synthetic fixtures. Study branch:134 -> validate_study_metadata:68 ->
validate_retained_source:85. Pilot performance branch:135 invokes the same source
check directly. allow-incomplete and require-marker flags do not bypass source
validation. The public CLI exposes no synthetic opt-in. Other standalone CUDA
analysis handles the separate prepared diagnostic protocol and cannot substitute
for the five-mode primary comparison analyzer. The internal allow_synthetic=True
path intentionally skips performance provenance for test fixtures; it is not
performance authorization, and callers must preserve that boundary.

cpu_gpu_provenance.py:42 validates the freeze against the independently pinned
SHA256518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6.
It requires the exact three frozen assets, validates their hashes, strictly parses
the verified matrix and obtains the expected adapter/source identities from it.
The existing CMake exception is independently pinned to review hash
b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a.
These identities match historical seals and actual files; they are not learned
from retained run claims. Altering source/prerequisite/build/raw maps together
cannot redefine the expected production digest. Only the exact pre-existing CMake
exception is allowed. Legacy omitted documentation is directly verified against
its frozen digest. Missing roots, invalid hashes, noncanonical paths, duplicate
JSON keys, inconsistent anchors or CMake claims fail closed.

Independently executed offline helper checks accepted the immutable pilot's valid
source claim and rejected altered adapter/timing/CUB-pin/CMake digests, a mutually
altered model/map, missing/malformed/ambiguous freeze files and duplicate JSON keys.
See OFFLINE_PATH_REVIEW.json: one positive/nine negative provenance checks.
These are metadata-only checks, not a fresh full-analyzer or benchmark run.

The original full-matrix reproducer is byte-identical across the previous review,
repair fixture and retained repair copy (SHA2561588c1ce06ded80b91d9806673b883effb7c98b0ace8d1eadb5c04688072142c).
Source inspection confirms it calls analyze(directory) with run_kind=performance,
without allow_synthetic or mocked provenance, accepts the baseline, changes the
claimed production digest, refreshes all associated hashes/maps, then calls the
full analyzer again. The sealed repair output records baseline accepted and
rejection specifically `retained protected source differs from trusted anchor:
src/cuda/cub_sort.cu`;1200/240 synthetic counts remain test data. The focused test
copies and executes that full reproducer, rather than testing only a helper.
This review verified its bytes, retained log and call path; it did NOT rerun the
reproducer or its regression suite. Their observed success is historical evidence.

No trust-on-first-use or self-referential adapter expectation remains in that path.
Trust still rests on reviewed analyzer code and pinned local roots. Hashes enforce
identity/consistency, not signed proof that timings or hardware execution occurred.
The selection manifest is a reviewed repository policy, not a signed attestation;
editing both code and policy requires independent review, not merely resealing.

## Review B — NO-GO: directory-level CTest execution is unguarded

The exact reported19-group CPU selection is reproduced by the pure selector using
retained discovery and the current reviewed source/command manifest. The141-file
source snapshot matches actual bytes. Unknown/missing/duplicate tests, changed
source, unreviewed test commands, fixture requirements, dependencies and per-test
environment overrides are rejected in offline checks. parallel_mergesort and the
other nine CPU timing groups remain excluded. Its known N32768/W1/R2 six-row path
was inspected at tests/test_parallel_mergesort.cpp:103 and was not executed.

The12 selected C++ groups are correctness/invariant/counting/memory tests; source
and shared headers contain no timing-engine invocation. CLI/metrics children are
correctness/counting programs. The seven Python groups use synthetic fixtures,
failure/collision paths, small untimed input generation, or CUDA-disabled configure
checks. cuda_benchmark_analysis gets no executable argument and skips its two GPU
methods; preflight/handoff collections use doubles. No selected source path was
found to dispatch a real timed worker through its own test body. The static symbol
scan is supporting evidence, not a formal proof of arbitrary binary behavior.

**Blocking gap:** scripts/non_timing_tests.py:69 validates test JSON, exact
commands and per-test properties. It does not inspect CTestCustom.cmake,
CTestCustom.ctest, CTestTestfile.cmake includes or their transitive configuration.
cpu_gpu_protocol.py source_manifest excludes build metadata. selected_ctest:110
invokes CTest discovery before load_manifest/source checking;:115 later invokes
CTest again, rechecking only source. The selector CLI's default branch:132 also
invokes CTest before validation. There is no build-metadata fingerprint or hook
guard before discovery or execution.

Installed primary CMake documentation inspected, not executed:

- /usr/share/cmake-3.28/Help/command/ctest_read_custom_files.rst: plain CTest reads
  CTestCustom.cmake/.ctest from the binary directory by default.
- /usr/share/cmake-3.28/Help/variable/CTEST_CUSTOM_PRE_TEST.rst and
  CTEST_CUSTOM_POST_TEST.rst: command hooks surround test execution.
- /usr/share/cmake-3.28/Help/prop_dir/TEST_INCLUDE_FILES.rst and
  TEST_INCLUDE_FILE.rst: specified CMake files are processed when CTest runs.

These are outside a per-test -R filter and need not appear in test JSON. CMake
includes can themselves contain executable statements; -N is not a sandbox for
interpreting arbitrary CTest configuration.

Pure metadata reproduction: OFFLINE_PATH_REVIEW.json accepts19 tests despite an
unreviewed pre-test hook/include. HOOK_METADATA_REVIEW.json strengthens that check
by copying/rebasing all29 actual registrations as text, adding an inert include
and a pre-test command string, then obtaining an accepted19-test plan. Subprocess
execution was blocked; no CTest discovery, hook, binary or timing ran. The proof is
acceptance of unreviewed execution metadata, not a claim of a runtime hook exploit
having been executed. Actual local Release and sanitizer directories inspected
contain no custom hook files or include/execute_process directives. This finding
does NOT establish historical timing or corruption; it establishes that the
reusable guard does not enforce its fail-closed contract for another build tree.

The prerequisite-only entry point correctly uses the helper for all three CTest
phases and cannot broaden test names via its flags. Nevertheless directory hooks
can add commands beyond that approved selection. Newly scoped correctness-only
manifests are correctly marked ineligible, and runner/analyzer reject them as the
frozen full-study gate. No frozen prerequisites were weakened by this finding.

Required follow-up: before ANY CTest invocation, validate reviewed source plus
generated test metadata and reject or explicitly verify directory hooks/includes.
Recheck that metadata before execution, or use an execution mechanism that does
not interpret unreviewed CTest configuration. Add inert regression cases for
pre/post hooks, executable includes and changes between discovery/execution, and
assert rejection before the subprocess callback. No source repair is applied in
this review. Do not test the guard by running a real timing hook.

## Review C — PASS for independently checked preservation claims

EVIDENCE_VERIFICATION.json records fresh direct file-hash comparisons:

- All11345 historical result files: zero missing/changed; their baseline set is
  identical to the original tooling/review lineage plus accepted earlier evidence.
- All46 repair evidence files are additive, disjoint from that historical set;
  exactly45 are listed in the repair seal, plus its self-excluded seal itself.
- All141 repaired source identities, six documented files, four frozen files,
  26 protected anchors with the existing CMake exception, and80 production/header/
  dependency files match. Both earlier evidence seals (85 tooling /30 review) match.
- Freeze/CMake review pins match literal trusted identities. CUB3.0.1/version300001
  commit f19d875da0d8bfb2e38c109b2b40522b8abbbbc3 and production adapter digest
  b6d7f37c7494587fc6e4a676c00c166dc322d31cce96710811e3a4cb9cd8b9cb unchanged.
- Five retained pilot summary copies, including original processed/summary.json,
  processed/summary_regenerated.json, reviewed/summary.json and both review copies,
  are byte-identical with SHA25607e69e2e0c8853f93d3f3da895337b5e4b72e5e2dd0ff0577db3cbd1f7053a22.
  This review compared bytes; it did not regenerate or launch measurements.
- Initial regression log really records21 methods,3 failures/1 error (17 passes),
  rejecting valid legacy maps for omitted docs/CUDA_TIMING_PROTOCOL_v1.md before
  the intended adapter checks. attempt1/ contains original code/manifest/tests.
  The retained diff adds direct frozen-document verification and leaves code
  anchor enforcement intact. Final22/22 and existing50/50 success logs match the
  sealed repaired sources. These test results were inspected, not rerun here.

Preservation is established relative to retained hash baselines, not an external
signed historical filesystem snapshot. Filesystem tracing does not exist, so no
claim is made about arbitrary transient writes in earlier runs. The prior audit-
generation quoting failure has narrative disclosure but no separate raw command
record; its exact failed stderr cannot be independently recovered here. This does
not undermine the retained initial regression log/correction above.

## Commands, failures and omissions

COMMANDS.md and commands/*.json retain exact review argv, exits and safety classes.
All source/doc reads, hashes, byte comparisons, AST inspection and offline metadata
checks exit0 except:

- Initial evidence checker exit1: compared absolute seal keys with relative file
  paths. Every preceding file-byte comparison passed. Original checker/log retained;
  v2 normalizes path representations and exits0 with all preservation assertions.
- Read-only compatibility diff exit1: expected diff-found status, not test failure.

No unit suite/CTest selection was executed. No fresh build, CPU/GPU prerequisite,
resource allocation/probe, benchmark, pilot, full study,100M experiment, commit or
push. No GPU commands at all. Review-only helper checks blocked subprocesses.

At final sealing all11391 pre-existing result files and 195 project
files remain unchanged. New review evidence is confined here: 57 files;
total result-file count is 11448. FINAL_INTEGRITY.json verifies that claim
and hashes this review's evidence, excluding itself.

## Exact next action

Repair and independently regression-review the CTest directory-hook/discovery
guard as a separate non-timing task. Do not run fresh prerequisites or resources
based on this NO-GO review. After that repair passes review, fresh validation and
study authorization still require separate explicit decisions. Shared-cloud,
SMT/thermal/frequency/cache variability and unverified future hardware/binaries
remain separate execution concerns, not resolved by source review.
