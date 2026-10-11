## CUB handoff final review revision2 — GPU correctness still pending

Final output-safety review found that resolving the requested path before mkdir
could follow a dangling symlink. Corrected to preserve the final path component
with Path.absolute(), so exclusive mkdir rejects existing and dangling symlinks.
New regression verifies no subprocess or target creation. Twelve host handoff
methods now pass. This is a host runner fix, not a CUDA algorithm change.
The initial source bundle/audit and all earlier validation evidence remain intact.
Use CUDA_SORT_VALIDATION_GUIDE_v2.md and cub_sort_source_v2.tar.gz for the corrected
handoff; v1 is retained history. Frozen CUDA_SORT_PROTOCOL_v1.md is unchanged.

Fresh narrow tests and Release configure/build/CTest all exited0:26/26 groups,
28.88s. Fresh Debug ASan/UBSan configure/build/CTest exited0:
26/26 groups,80.80s, leak detection enabled, no ptrace retry.
Zero failed/skipped CPU groups;12 host methods pass standalone and in each suite.
GPU sorting remains uncompiled/unexecuted:1 GPU test group unexecuted,475 expected
inputs/1900 expected output checks, not passes. Earlier local CUDA configure1
(no compiler), preflight2(unavailable), Git128(no metadata) and historical T4
runtime/cloud-CPU evidence remain exactly as recorded in the initial audit.

The first candidate bundle's137 files were also independently extracted/hash
verified, relocated CUDA/CUDA-SORT/OpenMP/testing OFF configure/build/registry
returned0/0/0 and six CPU sorters; that fallback had testing OFF. Correction changes
only host handoff/script/test/docs; CUDA adapter/CMake are unchanged. The corrected
bundle is separately source-hash verified and preserves every original result.
All 8,709 pre-task artifacts and all 8,798 pre-correction artifacts
(including first candidate archive and its relocation evidence) remain unchanged.
Current source differences/patch/manifest and final_review.json are retained here.

Evidence: results/raw/cub_sort_final_review_20261009T222209607981Z/COMMANDS.md, commands/*.json and FINAL_AUDIT.md.
Initial audit/evidence: results/raw/cub_sort_validation_20261009T220322089788Z/FINAL_AUDIT.md and COMMANDS.md.
No CUDA implementation validation, GPU smoke, full study, timing values or100M run
is claimed. No system configuration, driver change, commit or push. Current
roadmap CUDA work is incomplete; ready for corrected cloud handoff only.

Next: transfer the corrected v2 archive using source_bundle.json's SHA256, verify
its source manifest, follow docs/CUDA_SORT_VALIDATION_GUIDE_v2.md and run:
```sh
python3 scripts/validate_cuda_sort.py --output results/raw/NEW_CUB_CORRECTNESS
```
Preserve/return full success/failure evidence. Actual installed CUB must match the
reviewed version/header pin or be deliberately reviewed before any pin update.
Only observed GPU sorting success permits the separate timing milestone.

Corrected source bundle:
```json
{
  "archive": "results/raw/cub_sort_final_review_20261009T222209607981Z/cub_sort_source_v2.tar.gz",
  "sha256": "e155579bf9f9847ae1ced84c07f6e179d98215962076d1c0aea8133de00a190f",
  "source_files": 138,
  "bytes": 288335,
  "members": 139,
  "member_hashes_verified": true,
  "earlier_candidate_preserved": true
}
```
