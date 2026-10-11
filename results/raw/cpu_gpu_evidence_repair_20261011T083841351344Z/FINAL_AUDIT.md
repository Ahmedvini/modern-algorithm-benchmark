# Evidence-enforcement repair — final audit

Verdict: **NO-GO**. Parser/provenance validators and an inactive candidate are implemented and focused-tested. Actual build provenance, approved selection, independent trust activation, identity-matched GPU/framework validation and final preflight remain blocked. No study authorization is granted.

Repository: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark.
Git status exited128: no Git metadata; branch/revision unavailable. Source identity is file hashes, not an invented commit.

## Gate table

| Gate | Status | Direct evidence / limit |
| --- | --- | --- |
| Starting review and baseline identity | PASS | BEFORE.json verified previous review seal and baseline before edits; 193 project files /12,307 historical result files |
| Frozen inputs, native/dependency preservation | PASS | FINAL_PRESERVATION.json: four frozen inputs,26 anchor paths,80 protected files,65 existing build metadata files unchanged |
| Strict byte and content parsing | PASS for focused paths |39 inert evidence regressions, including correctly rehashed adversarial records, actual parser paths and valid record models |
| Shared launch/analyzer rejection of unsupported evidence | PASS for negative paths |26 compatibility regressions; previous placeholder coverage cannot establish acceptance; no actual launcher/run loop invoked |
| Complete full-prerequisite acceptance | BLOCKED | Independent trust pin intentionally unset; no valid real full-prerequisite bundle accepted or full positive integration demonstrated |
| Default19 / path / discovery safeguards | PASS preservation | v3, selector and build guard byte-identical; candidate preserves every command/classification/property; current v3 source mismatch still rejected before discovery |
| Additive candidate approval / activation | BLOCKED | docs/NON_TIMING_TEST_SELECTION_v4.candidate.json remains pending; selector unchanged and cannot activate it |
| Build-provenance validator | PASS focused fixtures | Nonempty compile records, configure/build/compiler/link exit records, source/tool/metadata/product graph, actual inert binary rehash tests; no real compiler executed |
| Actual T4 build / comparison_input provenance | BLOCKED | No GPU/session/build operation authorized or run here; no intended real executable/provenance established |
| Existing classification compatibility | PASS focused | Nine unchanged validation-policy methods passed; correctness never promoted to timing/full eligibility |
| Fresh native Release / ASan / GPU/framework / resource / workers | BLOCKED, not run | Prior observations remain historical; changed Python source map cannot inherit full-suite validation |
| Historical result preservation | PASS |12,307/12,307 exact file membership and SHA256 matches, not count-only |
| Study launch | NOT RUN | Zero native tests, CTest discovery, builds, GPU commands, benchmark calls, warmups or measured trials |

## Root causes and repair

1. Compatibility previously hashed framework bodies but derived acceptance from separate caller-supplied coverage assertions. CPU command success was not semantically bound to a reviewed test plan, exact command, test inventory or actual build.
2. Build capture attached a current source map to existing binaries and accepted any compile-command list, including empty JSON. This was content identity, not proof those sources built those binaries.
3. v3 intentionally described150 files while the prior recovery contained153: five modified Python files and three additions. That source guard was correct and has not been disabled.

New EvidenceStore reads bounded regular files through one descriptor, verifies the hash of those exact bytes, caches that byte snapshot, and parses it with duplicate-key/nonfinite rejection. Unsafe paths/aliases fail. Private copies of verified raw bytes are used for read-only timing analyzers.

Strict record validation derives coverage from typed command results and actual retained contents: guarded CPU plan/manifest/commands/discovery/registry/properties, started/passed test names and summary, prepared result counts, worker threshold/call/environment outcomes, all workspace sizes and retained resource snapshot, production oracle result, complete raw timing/pilot bundles, and independent review decision. Contradictory or unsupported outer fields fail. CPU executable inventory includes build-relative binary arguments passed to Python wrappers as well as direct test executables.

A full compatibility acceptance must reach validate_full through the shared compatibility validator. Coverage assertions must exactly equal derived results. Legacy CPU/production references must be the same strict command records; all legacy records and preflight report also require independent binding. Existing protected-anchor, explicit-opt-in, GPU14-method framework,475/1900 production, source/path and primary/prepared separation checks remain.

The new independent-review pin is deliberately unset. No caller can provide its own trust parameter or activate the candidate. This closes acceptance by default, rather than asserting that complete production eligibility now works.

## Files changed

Six modified:
- README.md; docs/ROADMAP.md — current pending evidence gate and documentation link.
- docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.md — stronger evidence requirements and required build-provenance CLI argument.
- scripts/cpu_gpu_framework_compatibility.py — verified-byte reads and mandatory strict shared validation.
- scripts/cpu_gpu_build_identity.py — snapshot-only API separated from capture/verify requiring compiler/linker provenance.
- tests/test_framework_compatibility.py — old unsafe positive now rejects; inert compile fixture strengthened; all26 methods retained.

Six added:
- scripts/cpu_gpu_evidence_io.py — immutable-byte reference/command reader.
- scripts/cpu_gpu_build_provenance.py — offline configure/compile/link graph and output identity validator.
- scripts/cpu_gpu_evidence.py — strict framework, CPU-plan, candidate and independent-context enforcement.
- tests/test_evidence_enforcement.py —39 inert methods, with subprocess/shell blocked.
- docs/CPU_GPU_EVIDENCE_ENFORCEMENT_v1.md — schemas, trust limits, blocked activation and future build requirements.
- docs/NON_TIMING_TEST_SELECTION_v4.candidate.json — inactive additive157-file source snapshot, exact membership differences/reasons, no test approval.

CHANGE_INVENTORY.json and CHANGES_VERIFIED.diff describe the actual final changes. Earlier diffs/candidate versions remain retained. Existing CMake registrations, production algorithms, CUB3.0.1/CCCL f19d875da0d8bfb2e38c109b2b40522b8abbbbc3, original v3, parent policy JSON and compatibility policy JSON remain unchanged.

## Fresh focused tests, exact commands and outcomes

All commands ran from repository root with Python -B. No CTest or native executable was invoked.

| Command | Actual exit | Final result / log |
| --- | --- | --- |
| python3 -B tests/test_evidence_enforcement.py -v |0|39/39, zero failures/errors/skips; evidence_tests_reviewed.log |
| python3 -B tests/test_framework_compatibility.py -v |0|26/26, zero failures/errors/skips; compatibility_reviewed.log |
| python3 -B tests/test_validation_policy.py -v |0|9/9, zero failures/errors/skips; validation_policy_reviewed.log |

Final distinct methods: **74 passed**. These are Python parser/classifier unit tests, not fresh Release21/21, ASan21/21 or GPU execution.

Adversaries recompute their hashes and, where necessary, unit review maps: malformed/placeholder records, failed/incomplete results, duplicate/conflicting CTest and worker calls, wrong selection/source/build/context, changed command/directory/exit, unapproved candidate membership/path/hash, missing link/compiler exits, stale objects/outputs, missing/inert executable hashes, synthetic timing scope, malformed/missing independent anchor, tampering/stale reference digests and unsupported coverage claims. Valid CPU Release/sanitizer, prepared, worker, workspace, build and timing-CSV *unit models* remain accepted by their actual parsers. An all-gate claim assembly regression covers pilot's missing field.

Positive command/compile/CSV fixtures are deliberately synthetic. No compiler, CTest test, CUDA sorter or timer produced those modeled values. Public launch/analyzer negative paths and strict full-validator unsupported-claim rejection are tested. There is no real complete positive full-study integration run or provenance attestation.

Initial failed attempt retained: evidence_tests_attempt1.log, exit1,28 methods,27 passed/one fixture error (duplicate missing keyword in dict construction). Corrected attempt2 passed28; expanded attempt3 passed35; later final39 passed. All intermediate logs are retained. Final static review also corrected the corresponding duplicate-keyword hazard in derived full claims before any full evidence execution; the new all-gate regression passes. Read-only inspection's missing default_selection key and an initial JavaScript orchestration syntax error are transcribed in INITIAL_ERRORS.md; neither launched a workload. Git status exit128 is preserved in command records.

## Selection and preservation

Starting150-to153 discrepancy is independently retained from the prior review. This repair adds four source files; final candidate contains157. Relative to v3: seven additions, five modified source files, zero removals. Every path/reason is in candidate.source_change_reasons and FINAL_SELECTION.json. The prior five modified files are unchanged in this task.

Default19:
baselines, cli, comparisons, cpu_gpu_comparison_framework, cuda_benchmark_analysis, cuda_preflight, cuda_sort_handoff, datasets, environment_manifest, memory, memory_unsupported, mergesort, metrics_cli, pdqsort, quicksort, radixsort, searching, structures, timsort.

The two opt-in CPU diagnostics remain opt-in, timing exclusions unchanged, and new Python tests are not implicitly registered or approved. Tests call only the pure manifest loader to prove rejection; no real selector discovery or CTest was run.

FINAL_PRESERVATION.json verifies:
- Historical12,307 before/after, complete path+digest maps equal; new evidence directory excluded explicitly.
- Protected80 and build metadata65 before/after, complete membership+digests equal.
- Frozen4 and all26 anchor paths unchanged from task start. Three previously authorized framework digests already differ from original freeze; this task changes none of them.
- Project193 before /199 after: exactly six modified, six added, zero removed.
- Latest prior independent-review seal and all its members preserved.
- v3/default guard/policy/production dependency pins unchanged.

FINAL_INTEGRITY.json seals new evidence members (excluding itself), final project identities and these verified preservation claims using the established SHA256 member-map convention. It is a content seal, not an external attestation of execution.

## Unresolved blockers, in priority order

1. **Independent repair and trust-activation design review.** A hardcoded digest of a review that includes this same validator's complete source map would be circular. The pin remains None. A non-circular separately protected authority/approval mechanism must be reviewed before activation; no hash exclusions/normalization or self-approval were introduced.
2. **Candidate approval and explicit selector activation.** v3 remains active and rejects the changed tree. The candidate is not authorization; it has not been independently reviewed or used for eligibility.
3. **Complete nested evidence retention/integration.** Existing runner copies top-level records only; the new schema needs verified nested manifest/provenance/raw references retained for independent post-run analysis. The runner remains unchanged and blocked. Full positive evidence assembly, including conditional LSan retry/source-relocated Dart support, is not certified.
4. **Actual build collection/provenance.** Validators require actual configure/compiler/linker commands and exit/product identities. No execution collector or T4 build was run/established here. Do not reconstruct successful exit records from a compile database. comparison_input's actual intended binary remains unavailable, not assumed.
5. **Separately authorized identity-matched validation and timing-evidence compatibility.** No existing GPU/CPU historical result is relabeled. The unchanged pilot analyzer rejects framework-exception source maps; any transition needs explicit independent review. All required real coverage, resource/environment and binary identities remain gates.
6. **Separate final preflight and authorization.** Neither this repair nor its unit tests authorizes any study, pilot, smoke, warmup, measured trial or 100M run.

No build warnings were generated: no compiler ran. Existing nvcc warning claims and old sanitizer results were not refreshed. No cloud authentication/session/GPU operations occurred.

Command-record limitation: initial file-inspection tool outputs were observed before the structured accumulator existed; available exact inspections and all focused execution commands/statuses are recorded, while unretained initial shell text is explicitly not reconstructed as observed execution. The source patch tools are documented by final diff/inventory, not represented as shell commands.

**Stop here. Next permitted action: separate independent review of this repair, its inactive candidate and unresolved trust/retention design. No prerequisite checks or study launch.**
