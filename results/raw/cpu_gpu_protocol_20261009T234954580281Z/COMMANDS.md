# Protocol preparation commands

Initial inspection: `pwd` exit0; `git status --short` exit128 (no Git metadata).
Safe temporary-file write check passed. Read/search commands did not modify source.
See initial_inspection.json. No Colab/GPU/benchmark matrix command was run.

Validation commands below ran from the repository root through the evidence
record_command.py wrapper. JSON records retain full argv/stdout/stderr and exits.

```bash
/usr/bin/python3 results/raw/cpu_gpu_protocol_20261009T234954580281Z/verify_existing.py
```

Exit 0; full record: `commands/verify_existing.json`.

```bash
ctest --test-dir build/cuda_timing_20261009T231303050084Z/cpu-release --output-on-failure -V -R '^(datasets|timing|cuda_benchmark_analysis)$'
```

Exit 0; full record: `commands/targeted_cpu_ctest.json`.

```bash
/usr/bin/python3 results/raw/cpu_gpu_protocol_20261009T234954580281Z/build_protocol_assets.py --output build/cpu_gpu_protocol_20261009T234954580281Z/assets_a
```

Exit 0; full record: `commands/generate_assets.json`.

```bash
python3 results/raw/cpu_gpu_protocol_20261009T234954580281Z/build_protocol_assets.py --output build/cpu_gpu_protocol_20261009T234954580281Z/assets_final
```

Exit 0; full record: `commands/generate_final_assets.json`.

```bash
python3 results/raw/cpu_gpu_protocol_20261009T234954580281Z/freeze_protocol.py
```

Exit 0; full record: `commands/freeze_assets.json`.

```bash
python3 results/raw/cpu_gpu_protocol_20261009T234954580281Z/validate_protocol_assets.py
```

Exit 0; full record: `commands/validate_assets.json`.

```bash
python3 results/raw/cpu_gpu_protocol_20261009T234954580281Z/capture_local_environment.py
```

Exit 0; full record: `commands/local_planning_environment.json`.

Final integrity command/result will be appended after execution. Two failed
apply_patch context matches are recorded separately in editor_diagnostics.json.
They left README unchanged; corrected append succeeded.

Final integrity executed:

```bash
python3 results/raw/cpu_gpu_protocol_20261009T234954580281Z/final_review.py
```

Exit 0; commands/final_integrity.json. All10755 prior result files,1186 sealed smoke files,144 protected original source/doc files,26 source anchors and three frozen assets verified.
