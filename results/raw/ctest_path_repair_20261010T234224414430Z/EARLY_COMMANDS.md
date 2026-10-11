# Early read-only inspections and evidence bootstrap

The following shell invocations returned overall exit0 in terminal output.
Individual statements in multiline shells were not separately instrumented;
`rg --files` found no nested AGENTS.md and had no output. Some large output was
truncated. No reconstructed stdout is represented as a retained raw log.

```sh
pwd
cat AGENTS.md
cat results/raw/ctest_guard_review_20261010T232702450912Z/FINAL_AUDIT.md
ls results/raw/ctest_guard_review_20261010T232702450912Z
```

Independent inspection shells ran concurrently, each exit0:

```sh
cat scripts/non_timing_tests.py scripts/ctest_build_guard.py tests/ctest_fixture.py tests/test_ctest_build_guard.py
```

```sh
cat results/raw/ctest_guard_review_20261010T232702450912Z/FINAL_INTEGRITY.json
cat results/raw/ctest_guard_review_20261010T232702450912Z/COMMANDS.md
rg --files -g AGENTS.md scripts tests docs
sed -n '1,125p' scripts/validate_cpu_gpu_pilot.py
sed -n '1,52p' scripts/run_cpu_gpu_pilot.py
tail -n 30 README.md docs/ROADMAP.md docs/EXPERIMENT_PROTOCOL.md
```

The bootstrap was `python3 -B -c PROGRAM`, exit0. BEFORE.json retains the exact
complete `sys.orig_argv` (including PROGRAM), cwd, every starting hash and the
Git-metadata absence observation. It created this new timestamped directory with
mkdir, hashed existing files, excluded its own new directory from the baseline,
and copied seven source/document originals exclusively under before/. No prior
evidence path was reused. COMMANDS.md renders that exact executable argv.

All subsequent shell child commands are recorded in commands/*.json. Tool edits
used apply_patch, which returned success for each edit; they have no shell exit
code. Seven current project files were modified as listed in FILE_REVIEW.json;
other tool writes created only new programs/audit documents under this directory.
There were no rejected tool edits or unexpected failed commands in this repair.
The intentional pre-fix regression exit1 is retained in full, with its candidate
source, and is distinguished from the post-fix passing runs.
