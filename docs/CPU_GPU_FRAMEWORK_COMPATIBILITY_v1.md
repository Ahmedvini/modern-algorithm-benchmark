# Explicit CPU/GPU framework compatibility v1

The later [evidence-enforcement repair](CPU_GPU_EVIDENCE_ENFORCEMENT_v1.md)
requires independently reviewed content, guarded CPU plans and actual build
provenance. Its independent trust pin is not installed: no current full-framework
bundle qualifies. The historical explanation below does not waive these checks.

This additive policy repairs source compatibility, not missing validation or
execution permission. The frozen comparison protocol, matrix, resources, CUB
3.0.1 pin, production sorter and all historical evidence remain unchanged.

The machine policy is `CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.json`, independently
pinned by SHA256 in `scripts/cpu_gpu_framework_compatibility.py`. It inherits the
unchanged, pinned validation-v2 policy and original frozen provenance roots.
Only the exact already approved CMake, prepared header and prepared CUDA source
digests are exceptions. No caller-supplied digest can redefine those exceptions.
Unknown policies, altered/missing roots and inconsistent source claims fail closed.

Legacy source reviews and pilot analysis retain their original behavior. The
full-study runner has an explicit `--framework-compatibility-policy
cpu_gpu_framework_compatibility_v1` option, which must match the prerequisite
document and retained source review. **Do not run the study from this document.**
Compatibility is not applied implicitly and cannot be used for a replacement pilot.

## Required evidence

An opted-in prerequisite document retains all existing full-protocol requirements:
complete protocol identity, source map, comparison and input-tool hashes, successful
hashed CPU Release/sanitizer, CUDA CTest, production correctness and preflight records.
It additionally requires explicit schema 1/full-protocol scope, `build_identity`,
`framework_validation`, `framework_records`, and `session_id`.

`framework_validation` is a validation-v2 **full_study_prerequisites** artifact.
All nine original coverage gates remain required: Release21, sanitizer21,
prepared163/489, all three workspace sizes, worker12, production475/1900,
timing smoke, pilot150/30 and independent review. Its expected source, binary
and build identities are recomputed from the checked source and build identity;
each original record must be retained and match its digest. Correctness-only
artifacts cannot be promoted by adding an eligibility flag.

In addition, the original CUDA CTest log must show one actual, passed
`cuda_benchmark_gpu_framework` group with14 methods and no skips in that group.
The ordinary host-only group's intentional skips do not hide a GPU group failure.
The production correctness log must parse as475/1900 through the existing
correctness verifier. Both command paths must identify the declared GPU build.
The analyzer enforces the same requirements independently of the launcher.
Prepared diagnostics remain excluded from primary paired speedup calculations.

Evidence assembly and independent review must inspect the underlying command
outputs; coverage assertions or a content hash alone are not proof of execution.
This implementation does not generate full prerequisites, authenticate remote
logs, relabel historical builds, grant user authorization or waive missing timing
coverage. No currently retained correctness bundle satisfies these full gates.

## Build identity snapshots

`scripts/cpu_gpu_build_identity.py` captures hashes without executing anything:

```sh
python3 -B scripts/cpu_gpu_build_identity.py --build-dir /absolute/verified/gpu-release --build-provenance /absolute/verified/gpu-release/provenance.json --output /new/path/BUILD_IDENTITY.json
```

Use only an independently validated intended build. The output path must not
exist. Required entries include the comparison executable, **comparison_input**,
worker/prepared/production test executables, GPU timing executable, parallel and
prepared libraries, cache, compile commands and CTest registration metadata.
The snapshot records the current source map and frozen identity; it rejects
missing files, path aliases/symlinks and unexpected source/build configuration.
The launcher rehashes all entries, checks exact executable paths and source
identity, and verifies the snapshot again before completion. The analyzer checks
the retained snapshot against source, binary, input-tool and compile identities.

This is content identity, not proof that a freshly captured binary was built
from those sources. Original configure/build/link logs and independent review
are still necessary. Updating a stale binary's prerequisite hash alone is
insufficient: the retained build snapshot and validation context must also match.

## Validation and remaining gates

Focused tests use inert temporary files, block subprocess/runner execution and
exercise public launch-validation and analyzer paths. Run with:

```sh
python3 -B tests/test_framework_compatibility.py -v
python3 -B tests/test_validation_policy.py -v
```

Current recovery:26 new tests and9 existing policy tests pass. An initial fixture
construction error is retained in the recovery evidence. No CTest, build, GPU
workload or timing trial ran. Colab authentication succeeds but reports no active
sessions; current GPU evidence and the intended input-tool hash remain unavailable.

The unchanged v3 non-timing selector intentionally rejects the changed Python
source snapshot. A separately reviewed additive selection manifest is required
before future native-suite execution; never bypass that rejection or rewrite v3.
Independent policy/diff review, an accessible approved T4, current build identities,
applicable complete coverage and fresh resource/worker checks remain necessary.
Recovery audit: `results/raw/cpu_gpu_recovery_20261011T075800444473Z/FINAL_AUDIT.md`.
