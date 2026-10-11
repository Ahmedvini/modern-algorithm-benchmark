# CUB correctness validation on Colab v3

Use the new retry bundle recorded in
`results/raw/cub_correctness_colab_20261009T223853955936Z/retry_source_bundle.json`.
The original corrected v2 bundle remains retained with its original hash; its first
Colab attempt exposed the CUB 3.0.0 versus 3.0.1 dependency mismatch. This retry
implements [correctness protocol v2](CUDA_SORT_PROTOCOL_v2.md) with verified CUB
3.0.1 hashes. The sorter implementation and all 475 fixtures are unchanged.

Follow v2's archive SHA-256, member safety and source-manifest verification steps,
using a new empty extraction directory. Preserve any existing remote checkout.
From the new source root, run:

```sh
python3 scripts/validate_cuda_sort.py --output results/raw/NEW_CUB_CORRECTNESS
```

The output must be absent. The runner performs fresh kernel preflight, derives
the architecture from device0, configures/builds `test_cuda_sorting`, runs the
475-input/1,900-check executable and repeats it through targeted `cuda_sorting`
CTest. It rejects skips, mismatching protocol/dependency identities and incomplete
results. COMPLETE is correctness evidence only. Preserve failed/timeout/interrupt
markers, command records, preflight, dependency/source manifests and build cache.

The installed local Colab CLI 0.7.4 accepts these commands (session must already
be registered in the selected local configuration):

```sh
colab sessions
colab status --session SESSION
colab upload LOCAL_ARCHIVE /content/UNUSED_ARCHIVE.tar.gz --session SESSION
colab exec --session SESSION --file LOCAL_PYTHON_PAYLOAD --timeout 2500
colab download REMOTE_EVIDENCE_ARCHIVE LOCAL_UNUSED_PATH --session SESSION
```

Use `colab --config PRIVATE_CONFIG ...` when the assignment needs an isolated local
alias. Keep runtime proxy credentials in private CLI state, outside evidence.
`sessions` can list an assignment that `status` cannot resolve locally; CLI 0.7.4
may return0 for that logical error. Inspect output, remote subprocess exit status
and terminal markers, not just the CLI exit code. Do not allocate a new GPU merely
to fix a missing local alias. Uploaded bytes must independently match the expected
hash remotely before extraction. Downloaded evidence must also be hash-verified.

Export to unique paths before the ephemeral session ends. No driver installation,
CPU substitution, GPU timing or full study is part of this command. The current
audit records observed execution status separately from these instructions.
