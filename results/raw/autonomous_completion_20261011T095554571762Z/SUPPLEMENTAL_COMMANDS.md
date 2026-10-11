# Supplemental terminal and editing activity

`command_*.json` contains exact commands, cwd, timestamps, stdout/stderr and real
exit codes for the substantive workflow. The following inspection calls occurred
outside that recorder. They are listed explicitly rather than inventing captured
stdout, timestamps or provenance. No unrecorded benchmark/test/build is claimed.

- Startup `pwd; cat AGENTS.md; cat docs/ROADMAP.md; cat results/raw/cpu_gpu_final_critical_review_20261011T093808369140Z/FINAL_AUDIT.md`
  (separate newline-delimited shell commands), exit0.
- Startup README/EXPERIMENT_PROTOCOL/source inventory and `colab --help` inspection
  ended0; `rg` reported initially absent `report/` and `notebooks/`. The exact
  startup read and bootstrap are described in the audit; their stdout was not
  retained by the later recorder.
- Initial bootstrap Python read the previous integrity seal, verified its40
  evidence files and baseline maps, created this exclusive evidence directory,
  and wrote BASELINE.json and record.py, exit0. No old files were written.
- Resumption `pwd` / directory listing / `pgrep -af 'collect_metrics.py|learned_study.py|record.py'`,
  exit1 because pgrep found no running matching process. It did not start a workload.
- Read-only Python inspected the last10 command records and two metrics output
  directories; `ls` of learned regeneration and `cat report/test_tools.py`, exit0.
- `sed -n '1,230p' report/generate.py`, `cat docs/ROADMAP.md`, baseline head, exit0;
  output truncated in the conversation, complete source remains on disk.
- Python inspected retained1M cross_seed.json and learned run.json fingerprints,
  exit0:48 configurations,24 distinct sorted vectors.
- `command -v pdfinfo`, `command -v pdftoppm`, `sed -n '1,180p' scripts/learned_study.py`,
  `sed -n '1,180p' src/indexes/learned_index.cpp`, exit0.
- `sed -n '1,150p' report/autonomous_20261011T095554571762Z/PRESENTATION.md` and
  `rg -n 'source_manifest|def verify_current_sources|ANCHORS|def approval'` over
  the three corresponding scripts, exit0.
- Local images `presentation_page10.png` and `presentation_page12.png` were
  inspected with view_image, successfully; these are file reads, not shell commands.

Source/documentation edits used apply_patch. An initial rejected patch is retained
in EDIT_FAILURE.md. No shell exit status is invented for apply_patch/web/view_image.
No Git mutation, publication, credential read, remote upload or GPU execution occurred.
