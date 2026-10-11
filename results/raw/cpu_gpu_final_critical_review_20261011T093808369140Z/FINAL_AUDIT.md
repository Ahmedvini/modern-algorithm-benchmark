# Final critical CPU/GPU preflight review

**NO-GO — one or more required validation gates remain open.**

This is an independent file/content review of the existing repair, not a new validation run. No source, test, policy, selector, protocol, build or historical result was changed. No tests, discovery, builds, cloud commands, GPU operations, prerequisites, resource probes, warm-ups or measured trials were executed. Conditional study authorization was not exercised because required gates remain blocked.

## Decision table

| Required gate | Status | Direct evidence and precise limitation |
| --- | --- | --- |
| 1. Evidence-enforcement correctness | BLOCKED | Record parsers, shared launch/analyzer calls and fail-closed behavior are present; retained 39 adversarial tests match current methods. Full enforcement cannot be certified as usable while its independent trust root is absent: scripts/cpu_gpu_evidence.py:19-25,339-340. |
| 2. Valid positive integration path | BLOCKED | No complete production-path positive fixture/bundle. tests/test_evidence_enforcement.py:118-121 accepts component records using caller-created unit review maps; :311-330 patches approval and rejects the first unsupported CPU assertion. Public compatibility and analyzer tests require rejection at the missing pin (tests/test_framework_compatibility.py:142-145,252-275). Nested evidence is validated but not fully retained by the runner. |
| 3. Approved selection identity | BLOCKED | v3 unchanged, exact19 preserved. Current157-file map differs from approved150: seven additions, five modifications, no removals. Candidate classifications/commands/properties equal v3 exactly. Candidate remains pending, unsupported by the active selector; explicit acceptance/activation has not occurred. SELECTION_REVIEW.json. |
| 4. Source/build/executable identity | BLOCKED | Current source identity established by hashes; no Git metadata (exit128). Actual current T4 compiler/linker proof and intended comparison_input executable identity not established. Snapshot/proof validators exist, but only synthetic proof models pass. cpu_gpu_build_identity.py:77-103; cpu_gpu_build_provenance.py:39-122. |
| 5. CPU Release and sanitizer evidence | BLOCKED | Retained actual Release21/21 and ASan/UBSan21/21, both exit0, verified from command stdout and plans. Historical tested source150 differs from current157, including six changed source paths. No identity-matched current suite; original passes remain valid historical observations. HISTORICAL_VALIDATION_REVIEW.json and HISTORICAL_SOURCE_APPLICABILITY.json. |
| 6. Identity-matched GPU/framework correctness | BLOCKED | Historical prepared163 inputs/489 output checks/489 invalid-operation rejections exist, exit0. They are correctness-only and do not satisfy the mandatory GPU14-method timing-framework check in cpu_gpu_framework_compatibility.py:121-133. No current intended build/evidence bundle is established. |
| 7. Resource and worker readiness | BLOCKED | Historical three workspace results and12 worker checks retained, but no current approved build/session identity. No cloud operation was attempted: Step3 depends on satisfactory local code/policy eligibility, which is absent. Current authentication/session availability is unknown, not inferred unavailable. |
| 8. Frozen protocol and input integrity | PASS | Independently rehashed four frozen files;26 protected anchor chain entries including the previously pinned CMake review and exactly three authorized framework exceptions;80 protected files and CUB3.0.1 unchanged. ANCHOR_VERIFICATION.json, INITIAL_VERIFICATION.json. |
| 9. Final eligibility | BLOCKED | Mandatory shared validate_full calls approval() and cannot succeed. Existing launch latch, default legacy rejection, protocol/anchor checks and primary/prepared separation were not bypassed. No full-study command invoked. |

## Critical findings

### Evidence enforcement works as a fail-closed parser repair, not a completed eligibility system

EvidenceStore reads/hashes/parses the same cached descriptor bytes (scripts/cpu_gpu_evidence_io.py:21-49), rejects unsafe aliases/paths, and uses strict duplicate-key/nonfinite JSON parsing. cpu_gpu_evidence.py:238-330 validates each gate's actual supported contents and derives coverage; :363-366 compares derived coverage with claims. CPU record validation binds manifest, selection, source/build proof, executable inventory, retained registry/discovery, exact execution argv/cwd/exit and actual test names (:109-199). Hash-consistent malformed/failed/wrong-context records are covered by current retained regressions. Same-byte nested references are validated; source/binary maps alone cannot install the trust root.

Both launch prerequisites (run_cpu_gpu_pilot.py:128-132) and independent analyzer (analyze_cpu_gpu.py:106-109) call shared compatibility.validate_evidence, which must return validate_full (:147). The legacy route rejects the two changed framework source anchors, so dropping the explicit compatibility option does not make the current tree eligible.

However, TRUSTED_APPROVAL_SHA256 is None and docs/CPU_GPU_EVIDENCE_REVIEW_v1.json is absent. No valid full bundle can pass. The documented naive installation is circular: the review would bind the same complete source map containing the validator's own changed hardcoded pin. This cannot be resolved by this review pretending to supply a trusted digest. The missing independent, non-circular authority is a specific external approval/activation blocker (docs/CPU_GPU_EVIDENCE_ENFORCEMENT_v1.md:15-30).

Two concrete integration requirements remain:
- run_cpu_gpu_pilot.py:166-171 copies only top-level legacy/framework records. New records reference nested selections, manifests, build commands/metadata and timing bundles. A self-contained full run would lose required evidence; no complete retention/integration positive test establishes otherwise.
- cpu_gpu_evidence.py:224-225 requires historical pilot source and binary to equal the current full context. The accepted pilot predates the current source. The pilot path is explicitly legacy-only (run_cpu_gpu_pilot.py:160); its analyzer applies legacy anchors. Historical timing evidence cannot be relabeled or made current by changing consistency hashes. Resolve this explicit compatibility requirement without a prohibited new pilot or weakening checks.

These are existing requirements, not new speculative gates. No correction/activation was made: the first necessary authority is unavailable, and the user specifically requires BLOCKED when trust cannot be established. Creating a self-approved pin, activating v4 implicitly, editing historical evidence, or using an old binary would violate the governing instructions.

### Candidate review and preserved selection

SELECTION_REVIEW.json independently inventories every source difference and the candidate's reasons. All four classification/command/property fields match v3. The seven additions are build identity/provenance, verified-byte/evidence/compatibility modules and their two inert regression files. The five modifications connect existing source review, prerequisite runner, analyzer and study CLI to explicit compatibility. None adds a default approved test.

The exact19 remain:
baselines, cli, comparisons, cpu_gpu_comparison_framework, cuda_benchmark_analysis, cuda_preflight, cuda_sort_handoff, datasets, environment_manifest, memory, memory_unsupported, mergesort, metrics_cli, pdqsort, quicksort, radixsort, searching, structures, timsort.

v3 SHA256: fef39034b063c36dabc3eccf9dc6a162ebcf6a4e5cb44abeda83e93fbcf1a434.
Inactive candidate SHA256: 9d39e00b3910975f56b6c2eb0c08a7f57a23ab0762fc789c261a936e82aa0a71.

The membership-preservation review is favorable; it is not approval of a usable end-to-end eligibility system or candidate activation. The default source equality check (non_timing_tests.py:25-33) correctly rejects this changed tree. Pre-discovery hook/literal-metadata and absolute guarded-path retention/rechecks remain unchanged (:72-75,141-151; ctest_build_guard.py:113-179). No actual selector/discovery was run.

### Build identity and evidence reuse

The build validator now requires nonempty compile records, successful configure/verbose build/tool records, linked-product hash graph and source/configuration agreement; identity.verify recaptures actual required files, including comparison_input. Tests exercise missing/stale/mismatched executable and snapshot-only rejection. The complete production eligibility path additionally requires independently approved proof hashes.

These validators do not themselves collect genuine executions. The positive synthetic fixture creates inert text executables and modeled exit records (tests/test_evidence_enforcement.py:48-74,384-409); accepting that fixture is parser coverage, not observed compilation. No genuine current collector/build proof or intended comparison_input bytes were available in the reviewed repair. An arbitrary consistent JSON graph cannot be promoted to a real build.

The final39/26/9 retained logs match every AST test method and the source seal; corresponding actual execution records each report exit0. These74 focused successes are reused without rerunning unchanged tests. The complete production positive path is absent. The earlier28-method attempt's27 passes/one fixture error and all corrected attempts remain retained.

Actual historical Release21/21 and sanitizer21/21 logs contain the matching21 selected names and successful summary. Their source differs from current157 (HISTORICAL_SOURCE_APPLICABILITY.json). Historical prepared/worker/resource commands are also parsed in HISTORICAL_VALIDATION_REVIEW.json; none is silently relabeled. Resource observations are historical queried/requested bytes, not new physical allocation measurements:

| N | Prepared query bytes | Production-parameter query bytes | Combined device payload bytes | Known host peak payload bytes |
| --- | ---: | ---: | ---: | ---: |
|1025|1|1|16402|24600|
|65537|279295|279295|1607182|1572888|
|1000000|4178687|4178687|24357374|24000000|

Frozen workspace cap remains64MiB each, payload cap256MiB; device payload must also fit half currently free device memory. Disk and host headroom requirements remain1GiB. No current resource snapshot or future availability guarantee is claimed. Worker evidence reports runtime team sizes, not task participation or separate physical cores. No new compiler diagnostics were generated or suppressed; older341-warning claims were not refreshed.

## Integrity and executed scope

INITIAL_VERIFICATION.json independently verified the prior repair's227 sealed members and all12,307 earlier result files. Together with the prior repair's seal, the exact current historical baseline is12,535 files, not an assumed count. Current199 project files match the repair seal;80 protected files,65 build-metadata files and four frozen files match retained maps. The retained final2181-line diff reconstructs byte-identically (LOG_AND_DIFF_REVIEW.json). Final integrity repeats complete path+digest comparisons and records only this new review directory as additive.

No source changes, test reruns, build, CTest, eligibility activation, cloud/GPU action, resource probe or benchmark execution occurred. This review does not claim remote availability or prove unlogged activity outside its commands. SHA256 seals establish content preservation, not external attestation of historical execution.

COMMANDS.md and command_*.json retain exact inspections, output and statuses. Read-only inspection mistakes are preserved: missing guessed prerequisite path (exit2), missing guessed GPU .cu filename, anchor assertion assuming the pre-framework CMake digest equaled the original freeze (inner Python exit1 while the surrounding inspection shell exited0), null command-record parsing (exit1), and a too-broad filename match assertion (exit1). Corrected inspections use the actual prerequisite filename, .cpp test, pinned CMake-review chain and exact test-execution filter. These did not execute any workload or alter project files.

## Shortest blocking resolutions

1. Establish an explicitly accepted, non-circular independent approval authority and approved selection activation; preserve v3/exact19 and all existing guard checks.
2. Complete only required nested-evidence retention/positive integration and resolve the policy's applicability to retained timing/pilot evidence without relabeling or prohibited reruns.
3. Then establish a current T4 source/build/compiler/linker/input-executable identity and perform only missing identity-matched bounded correctness, sanitizer, workspace and worker checks. Current session state was not probed because local eligibility was already blocked.

No additional pilot, timing smoke, optional hardening or new benchmark milestone is recommended. The conditional full-study launch rule was not satisfied. **Benchmark trials launched:0.**
