# Retained initial errors

Raw initial regression log: evidence_tests_attempt1.log (exit1, one fixture-construction error).

Transcription from observed tool output (not a rerun):

- Initial read-only orchestration: JavaScript SyntaxError: Missing initializer in const declaration. No shell command executed; corrected before baseline capture.
- Read-only Python manifest inspection printed non_timing_correctness_v3 and31, then KeyError: 'default_selection' at line4. Exit1. The manifest has no such field; corrected inspection derived names from tests/classification/diagnostic_only instead. No selector/discovery invoked.
- git status --short --branch: fatal: not a git repository (or any of the parent directories): .git. Exit128; no Git mutation.

The original test/source copies, intermediate logs and candidate/diff snapshots remain present. No historical failure was removed.
