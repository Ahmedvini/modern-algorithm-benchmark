# Evidence-document correction failures

Two apply_patch operations on this new review directory failed while clarifying
the bootstrap transcript. Neither was a shell command, test, or workload.
Both included a mismatched FINAL_AUDIT context in the same atomic patch as an
EARLY_COMMANDS correction. They made no project/historical changes. The first
rejection's unchanged EARLY_COMMANDS text is retained in
commands/evidence_patch_rejection_state.json (read-only command exit0). The
successful correction was then confined to EARLY_COMMANDS.

Exact observed tool errors:

```text
apply_patch verification failed: Failed to find expected lines in /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/ctest_guard_review_20261010T232702450912Z/FINAL_AUDIT.md:
own?
```

```text
apply_patch verification failed: Failed to find expected lines in /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/ctest_guard_review_20261010T232702450912Z/FINAL_AUDIT.md:
and pure path arithmetic. It did not import repository modules, call
```

These are evidence-authoring mistakes, not successful checks. All wrapped
inspection/hash/AST commands exited0. No test was rerun to address either error.
