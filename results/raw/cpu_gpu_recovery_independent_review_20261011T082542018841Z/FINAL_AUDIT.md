# Independent review of CPU/GPU recovery

**Verdict: NO-GO.** This is an independent source/evidence review, not a prerequisite validation or study authorization. No tests, CTest discovery, configure/build, resource probes, Colab/GPU commands, sorting workloads, timing samples, pilots, warmups or study trials ran during this review. Only read-only inspection, AST parsing, byte hashing, and additive review-evidence writes occurred.

Reviewed recovery: results/raw/cpu_gpu_recovery_20261011T075800444473Z/.
This review's directory is recorded in COMMANDS.md. Existing implementation and historical evidence were not edited.

## Gate table

| Gate | Status | Independent finding |
| --- | --- | --- |
| Exact three-file compatibility exception and frozen adapter/CUB anchors | PASS | Pinned policy, parent policy, old CMake review and freeze hashes match actual bytes. Exceptions are exactly CMakeLists.txt, include/benchmark/cuda_timing.hpp, src/cuda/cub_timing.cu. Other frozen anchors remain authoritative. |
| Full prerequisite evidence enforcement / independent context | FAIL | Nine framework files are hashed without parsing their content; coverage assertions and session identity can be self-consistent without independently verified coverage. Existing passing public-validator fixtures demonstrate placeholder acceptance. |
| Existing path-identity / pre-discovery selector implementation | PASS | Exact implementation hashes unchanged; static gate remains before discovery and retains guard-approved absolute path through discovery, selection and execution rechecks. No discovery was invoked here. |
| Current source snapshot admitted by approved 19-test selector | BLOCKED | v3 still describes 150 files; current source has 153, with five modified and three added. Exact equality rejects before discovery. No updated v4 selection snapshot exists. |
| Recorded 26 new / 9 existing regression methods | PASS | Raw logs show exit0, every current method name exactly once as ok, 26/26 and 9/9. This verifies retained reports and source correspondence, not fresh execution or complete safety. |
| comparison_input missing/stale/mismatch enforcement relative to a captured snapshot | PASS | Actual files/paths are rehashed at launch and completion; missing entry/file, changed bytes and mismatched paths have retained inert regression coverage. |
| Intended build provenance and actual comparison_input identity | BLOCKED | Hash capture is not source-to-binary build proof; current intended remote executable is unavailable. Retained BUILD_COMPLETE.json does not contain comparison_input or input_tool_sha256. |
| Project/frozen/build/historical preservation | PASS | Recovery seal and inventories independently reconstructed; final review preservation is in FINAL_INTEGRITY.json. No count-only preservation claim. |
| Current T4 and identity-matched GPU/framework validation | BLOCKED | No new session/GPU validation attempted. Recovery's recorded session inventory reports no active sessions. Current availability is not independently probed here. |
| Full-study eligibility / launch | BLOCKED | Evidence enforcement, approved selection snapshot and current environment/build/coverage gates remain open. No launch authorized or attempted. |

## Finding 1 — coverage content is not enforced by the new public validation path

scripts/cpu_gpu_framework_compatibility.py:100-110 checks each framework reference's safe path and digest and constructs a hash map. It never reads/parses those nine record bodies. At :111-116 it builds classification context, including session_id copied from the same prerequisite document, and calls classify on the nested framework_validation assertions.

scripts/cpu_gpu_validation_policy.py:46-85 expects independent context and checks the asserted status/counts against policy and record hashes. It does not parse raw records. This is consistent with its documented limited classifier role, but the new launch integration provides no independently trusted assembler/review decision enforcing the underlying results. The parent documentation explicitly requires the assembler to parse actual command logs (docs/CPU_GPU_VALIDATION_POLICY_v2.md:35-40).

The existing positive fixture is concrete evidence of the gap:
- tests/test_framework_compatibility.py:58-74 uses placeholder CPU Release/sanitizer/preflight command output.
- :75-86 creates all nine framework files containing only synthetic_fixture and gate, then supplies separate passing coverage assertions.
- :94-97 calls the actual runner.validate_prerequisites.
- :138-139 requires that production validator to accept this data.
- :245-268 also reaches analyzer.validate_study_metadata; only the environment gate is mocked there.

The retained final_identity_hardening_tests.json records both positive methods passing. No new reproducer or tests ran during this review. Static tracing shows an otherwise self-consistent reference to a malformed or failed framework body is not inspected; existing negative tests mutate coverage assertions or leave stale hashes, not a failed body with recomputed consistent hashes.

The legacy CPU command records are checked only for successful command status/exit and hash in scripts/run_cpu_gpu_pilot.py:118-127 and scripts/analyze_cpu_gpu.py:92-100. Their command arguments, guarded selection plan, discovered/selected test identities and actual test counts are not bound to the claimed 21-test coverage. Thus the selector itself remains fail-closed, but the new prerequisite path does not prove that accepted CPU evidence went through that selector. The current source-snapshot rejection does not automatically prevent someone supplying purported full prerequisites directly to the launch validator.

The new code does additionally parse CUDA framework output and production correctness at compatibility.py:121-146. Those checks, exact adapter anchors, explicit policy agreement and the CLI execution latch remain intact. This finding is not a claim that a real study was launched or that frozen adapters can be changed. It is a remaining evidence-enforcement weakness, partly inherited from the legacy prerequisite validator, which passing metadata tests do not close.

Required repair/review: validate raw record schemas and outcomes for every required gate, or require an independently protected, reviewed assembly decision binding the raw outputs, exact guarded CPU selection, session, source and build identities. Add negative fixtures with failed/malformed/wrong-selection record bodies and all consistency hashes recomputed. Preserve historical evidence classification and reject unsupported evidence. Do not create timing evidence under this review.

## Finding 2 — the 19-test rejection is intentional and precisely attributable

scripts/non_timing_tests.py:31-33 requires reviewed_source_sha256 == source_manifest(). Its active manifest remains docs/NON_TIMING_TEST_SELECTION_v3.json, SHA256 fef39034b063c36dabc3eccf9dc6a162ebcf6a4e5cb44abeda83e93fbcf1a434.

Independent file hashing reproduces:
- Snapshot150 / current153.
- Modified: scripts/analyze_cpu_gpu.py, scripts/cpu_gpu_protocol.py, scripts/cpu_gpu_provenance.py, scripts/run_cpu_gpu_pilot.py, scripts/run_cpu_gpu_study.py.
- Added: scripts/cpu_gpu_build_identity.py, scripts/cpu_gpu_framework_compatibility.py, tests/test_framework_compatibility.py.
- Removed: none.

README/ROADMAP and the two new documentation files are not in source_manifest's source directories. No NON_TIMING_TEST_SELECTION_v4.json or other updated selection manifest was found. The current source map in the compatibility review is not an approved selection snapshot.

The exact unchanged default selection is:
baselines, cli, comparisons, cpu_gpu_comparison_framework, cuda_benchmark_analysis, cuda_preflight, cuda_sort_handoff, datasets, environment_manifest, memory, memory_unsupported, mergesort, metrics_cli, pdqsort, quicksort, radixsort, searching, structures, timsort.

Both scripts/non_timing_tests.py and scripts/ctest_build_guard.py, their v3 manifest, old policy and test registrations have unchanged recovery-baseline hashes. pre_discovery_gate calls load_manifest before build validation; selected_ctest retains guard['build_dir'] at :141-144, compares metadata after discovery and rechecks immediately before execution (:146-152). CLI and direct selection also use the gate. No path-identity or pre-discovery protection was weakened by this recovery.

Resolution is a separately reviewed additive snapshot after source/evidence fixes, preserving these exact19 defaults and timing exclusions. Do not disable the equality guard or overwrite v3.

## Finding 3 — executable content identity is useful but not build provenance

scripts/cpu_gpu_build_identity.py:24-42 checks explicit schema, frozen identity, source map, exact11-file inventory, comparison/input hashes and optionally compile-command hash. capture(:45-72) rejects missing/non-executable/aliased paths and wrong cache settings. verify(:75-79) checks canonical intended executable/input paths and compares a fresh capture with the retained snapshot.

The launcher applies verification before launch and again before completion; the analyzer binds retained comparison/input/compile digests. Tests :209-243 cover changed input bytes even with updated top-level prerequisite hash, missing document/entry/file, stale snapshots, wrong paths/symlinks, wrong configuration and source/compile mismatches. Logged passes match those current methods.

Limitation: capture assigns the current source map to whatever files currently exist and accepts compile_commands.json if it is any JSON list (:68-72). The positive fixture explicitly uses inert text files and an empty list (:41-51). A newly captured snapshot therefore cannot establish that binaries were built from the reviewed source. This limitation is candidly documented in the module and compatibility guide (:68-70); it must remain a separate blocking provenance gate, not be treated as repaired by hashing alone.

The retained bounded BUILD_COMPLETE.json under results/raw/bounded_resume_20261011T024034091796Z/downloaded/evidence/ has build/source_verified/identities fields but no comparison_input identity. No actual missing remote hash was inferred or replaced. Independent build/link evidence and the exact intended comparison_input bytes remain required.

## Inventory and tests

All seven modified and five added files were inspected. STATIC_REVIEW.json independently reconstructs the exact CHANGES_FINAL.diff from seven retained original copies plus current files, confirms each original copy's baseline digest, and confirms no other project change/removal. New source/policy integration requires further review because it alters full-study acceptance, despite no native algorithm changes.

Seven modified: README.md; docs/ROADMAP.md; scripts/analyze_cpu_gpu.py; scripts/cpu_gpu_protocol.py; scripts/cpu_gpu_provenance.py; scripts/run_cpu_gpu_pilot.py; scripts/run_cpu_gpu_study.py.
Five added: docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.json; docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.md; scripts/cpu_gpu_build_identity.py; scripts/cpu_gpu_framework_compatibility.py; tests/test_framework_compatibility.py.

LOG_REVIEW.json records actual retained argv/exit statuses, current AST method inventory, logged method names, and summary matches. Latest26/26 and existing9/9 logs end OK with no reported failures/skips; none rerun here. The initial23-method attempt is retained with exit1,11 ok and12 errors from duplicate missing keyword arguments. The corrected23/23, then24/24 and26/26 attempts remain intact. No failures were deleted.

Tests block subprocess.run/Popen, os.system and runner.invoke and use inert temporary binaries. They exercise real launch prerequisite validation and analyzer metadata functions, not full orchestration. They do not test every new branch through the CLI/run loop, independently validated build provenance, underlying framework-record parsing, independently obtained session context, or current GPU execution.

Native C++ sources were unchanged, so prior native observations are not erased. However the changed Python validation/analyzer/runner sources mean prior end-to-end framework and guarded-suite evidence cannot be silently relabeled as passing for this new source map. These35 focused methods are not a fresh Release/ASan/GPU regression suite.

Primary/prepared metric separation is preserved: analyze_cpu_gpu.py:195 rejects prepared backend rows in primary scope; :313-319 forms ratios only with gpu_cub_adapter host_call_e2e_ns. No metric definitions, matrix cells or production algorithms changed.

## Integrity and claim boundaries

Independently verified before review:
- Recovery seal32 members, plus its seal file33: exact member map and SHA256 match.
- Recovery baseline12,261 historical files: every current file digest matches; those files plus33 recovery files give this review's starting12,294-result-file baseline.
- Project188 before recovery /193 after: exactly7 changes and5 additions; no removal; reconstructed final diff identical.
- Frozen4 files, protected80 production/header/dependency files and existing65 build-metadata files match baseline bytes.
- All26 original frozen-anchor paths match recovery-start bytes; exactly the three approved historical framework exceptions differ from the original freeze. CUB3.0.1/CCCL f19d875da0d8bfb2e38c109b2b40522b8abbbbc3 remains unchanged.
- Prior final-preflight seal hash and all23 member hashes match independently.

FINAL_INTEGRITY.json records the after-review exact membership/hash comparisons against this review's BASELINE.json, including all12,294 pre-existing result files. No implementation, frozen input, build metadata or historical evidence file was modified during review. Only this new evidence directory was added.

The recorded no-workload claim is consistent with the recovery command inventory, inert test source and preserved artifact maps. Filesystem seals are not external attestations of remote execution or proof of unlogged activity. This review independently ran zero workloads; it did not refresh session state or verify current GPU readiness. Retained Release21/21, ASan21/21 and GPU/worker/resource claims remain historical; their existence is not a new validation PASS. Warning counts were not freshly generated or independently recounted in this review.

## Prioritized recovery plan

1. Repair evidence-content and independent-context binding in the compatibility launcher/analyzer path, without weakening anchors or promoting correctness-only data. Add hash-consistent adversarial record tests and preserve all stricter checks. Review that change independently.
2. After fixes stabilize, create/review an additive source-selection snapshot preserving19 defaults, diagnostic opt-in and timing exclusions. Retain v3 unchanged. Do not execute discovery until the new snapshot and path/build guard are approved.
3. Establish separately authorized accessible T4 environment and independently validated intended build. Record actual comparison_input and all other binary/library/metadata hashes with configure/compile/link/source evidence. Do not reuse missing or stale worker identities.
4. Obtain only separately authorized, identity-matched bounded correctness, sanitizer, resource and worker evidence. Resolve required full GPU-framework/timing evidence explicitly; current non-timing review cannot generate it or relabel historical smoke/pilot coverage.
5. A later independent final preflight must assess complete prerequisites and integrity before any separate study-authorization decision.

Stop after this review. Full-study eligibility is not established and launch is not authorized.
