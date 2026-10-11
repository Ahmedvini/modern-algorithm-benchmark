# CPU/GPU evidence enforcement v1 — pending independent review

This repair does not approve selection, establish a T4 build, authorize validation,
or authorize timing. Frozen comparison inputs, validation-v2 and compatibility-v1
trust roots, the CUB 3.0.1 pin and the production adapters are unchanged.

`scripts/cpu_gpu_evidence.py` implements `cpu_gpu_evidence_enforcement_v1`.
Both the launcher prerequisite path and independent study analyzer already share
`cpu_gpu_framework_compatibility.validate_evidence`; neither may return success
without the new strict validator. Legacy source reviews remain legacy. They
cannot opt into the three framework exceptions implicitly.

## Trust and byte identity

The compatibility path now requires a separately reviewed, independently pinned
`docs/CPU_GPU_EVIDENCE_REVIEW_v1.json`. **It does not exist and its production pin
is deliberately `None`.** No CLI flag, supplied source map, digest or passing
assertion can install it. All current full-framework acceptance remains blocked.
Installing a review and activating a selection are separate reviewed changes.
Do not generate a self-approved review from these fixtures.

Trust activation is unresolved, not an installation recipe: naively replacing
the unset digest in this script with the hash of a review that binds this same
script's complete source map creates a circular digest dependency. Independent
review must establish a non-circular, independently protected authority (for
example a separately reviewed signing authority installed before evidence is
created), or approve a different external trust mechanism. This repair does not
install such an authority, normalize/exclude source hashes, accept caller trust
parameters, or claim that a usable full-study trust root exists. The unset pin
therefore remains a deliberate hard blocker, beyond candidate approval alone.

A future review must bind the exact source/build/binary/freeze/session context,
canonical source/build paths, Python path, selection digest, GPU and both CPU
build-provenance digests, all nine record digests, the five legacy command
references and preflight-report digest. It must explicitly withhold execution
authorization. This binds an external review decision, not a claim copied from
the prerequisite's mutable metadata. Hashes and command logs alone are not
independent attestations of execution.

`EvidenceStore` rejects unsafe paths and aliases, reads bounded regular files,
checks descriptor identity/size/change stamps, hashes the bytes read, and parses
that same private byte snapshot. Duplicate JSON keys and nonfinite numbers fail.
Nested references use the same store. Timing-bundle analyzers receive private
copies of verified bytes, never a second read of mutable original records.

## Required content

Each framework record is schema 1, kind `cpu_gpu_framework_record_v1`, with its
exact gate, independently reviewed context and typed evidence references
`{file, sha256}`. References are canonical paths relative to the evidence root.
The validator derives coverage; caller assertions must exactly match it.

| Gate | Validated contents |
| --- | --- |
| CPU Release / sanitizer | Exact approved manifest/source map; guarded selection plan, generated registry/properties, retained discovery JSON, exact execution command and directory, 21 unique started/passed tests, no failures/skips/contradictory sanitizer output; matching compiler/linker provenance and selected executable hashes |
| Prepared correctness | Exact existing untimed result schema, 163 inputs, 489 output and invalid-operation checks, zero failures, exact build-relative executable/command |
| Workers | Exact untimed scope/build/runtime/environment, twelve unique size/API checks, correct results, team 1 below 32,768 and team 2 at/above; team size is not task participation |
| Workspace | Three unique size/query commands (1,025 / 65,537 / 1,000,000), existing byte/cap/headroom formulas and retained host/disk/environment gate |
| Production GPU | Existing `verify_result` schema, CUB 300001, T4 capability 7.5, 475 inputs and 1,900 checks, exact executable |
| Timing smoke | Existing complete raw CUDA bundle parsed by the read-only analyzer; synthetic/validation records excluded |
| Pilot | Existing frozen six-dataset raw analyzer, 150 measured / 30 warm-ups, no failures/missing; matching source and comparison binary |
| Independent review | Explicit accepted decision tied to the independent context, with execution authorization false |

The five legacy logs must agree with independently pinned references. CPU and
production references must also equal the strict records' command references.
The retained preflight schema/source map and actual probe classification must
support operational readiness. The original 14-method GPU framework log check
remains mandatory. These readers never run the stored commands.

No new timing data is generated. Historical smoke/pilot evidence is not relabeled
to match changed sources or binaries. In particular the unchanged pilot analyzer
rejects framework-exception source maps: resolving any compatibility transition
requires independent review, not an implicit waiver here.

Conditional LeakSanitizer retries are not silently accepted by this new record
format: CPU sanitizer evidence currently requires the documented leak-enabled
command. Supporting a ptrace-limited retry needs a separately reviewed extension
retaining both the original failure and the diagnostic retry. Retained remote
Dart metadata also requires the same source root for its existing static parser;
relocation is blocked rather than interpreted permissively.

## Build provenance versus a content snapshot

`capture_snapshot()` explicitly provides content identity only. It cannot satisfy
`verify()`. The public capture CLI additionally requires `--build-provenance`.
`scripts/cpu_gpu_build_provenance.py` validates a retained schema-1
`cpu_gpu_build_provenance_v1` graph:

- Identical complete source maps before and after; canonical source/build paths.
- Successful actual configure and verbose build command records and tool-version
  records, tool identities, generated cache/compile database/CTest metadata.
- Nonempty compile database with reviewed translation units and unique outputs.
- Separate actual compiler/linker command records, exit codes, source maps and
  product hashes; every compile command accounted for; linked object/library
  hashes agree through the graph; all requested binaries have link provenance.
- Exact resulting executable/library hashes, including `comparison_input`.

The intended build's actual regular executable files must exist and match the
proof. Empty arbitrary compile-command lists, snapshot-only manifests, missing
commands, failed commands, stale objects and foreign-build evidence are rejected.
The independent review additionally pins the complete proof digest. An internally
consistent synthetic graph is useful only as a unit fixture, not build proof.

Future, separately authorized build procedure: capture the actual configure,
verbose build, compiler and linker invocations and their exit statuses during an
isolated documented build, retaining all stdout/stderr and source/tool/metadata/
object/output identities. **This task did not run that build and does not provide
an execution collector or certify existing logs as sufficient.** Review the
collection/assembly procedure before executing it; do not reconstruct successful
exit records retrospectively from `compile_commands.json`.

Only after genuine records exist, the read-only content/proof check is:

```sh
python3 -B scripts/cpu_gpu_build_identity.py \
  --build-dir /absolute/verified/gpu-release \
  --build-provenance /absolute/verified/gpu-release/provenance.json \
  --output /new/path/BUILD_IDENTITY.json
```

There is no current identity-matched T4 build or verified `comparison_input`
executable under this repair. No real build-provenance PASS is claimed.

## Selection candidate and validation scope

`NON_TIMING_TEST_SELECTION_v3.json` remains unchanged and active. Its exact source
map intentionally rejects the changed tree before discovery. The inactive
`NON_TIMING_TEST_SELECTION_v4.candidate.json` preserves every test, command,
classification, property and default19 name, and inventories every source
membership/hash difference. It grants no approval to new regression files. The
selector is unchanged and does not support this pending candidate. Independent
review must approve the candidate and any explicit activation change first.

Only inert Python regressions run for this repair. They block subprocess/shell
execution, write clearly synthetic fixtures in temporary directories and invoke
real evidence-parser paths. Positive CPU/build/prepared fixtures test parsing,
not actual compiler, CTest or GPU execution. There is no accepted end-to-end full
prerequisite fixture or real full-study proof; the absent independent pin is a
deliberate blocker. Native Release/ASan/GPU/framework tests need identity-matched
reruns only after separately approved selection/environment/build steps.

Next gates: independent repair/candidate review; reviewed actual build collection;
separately authorized T4 build and bounded validation; resolution of all required
timing/framework evidence without relabeling; independent final preflight and
separate study authorization. No benchmark launch is permitted by this document.

Full-run retention also requires review before activation: the current study
runner copies only top-level prerequisite/command records. The new format has
nested manifest, build and raw-bundle references, which need a verified recursive
retention mechanism before a future run can be independently reanalyzed from its
own output directory. This repair leaves that launcher unchanged and blocked;
it does not test or certify full-run evidence assembly.
