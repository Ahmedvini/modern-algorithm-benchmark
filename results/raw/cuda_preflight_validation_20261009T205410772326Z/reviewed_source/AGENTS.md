# Codex Project Brief — Modern Search & Sorting Benchmark

## Role and objective

Act as a senior C++ performance engineer and experimental researcher. Implement a reproducible, well-tested benchmark suite for **Large-Scale Evaluation of Modern Search and Sorting Algorithms**.

The core engine must be written in **C++17 or newer**. Use **Python** for data processing, plots, and report-generation support. Work incrementally, run tests after each meaningful change, document design choices, and never fabricate benchmark results.

The project is individual. GPU experiments may run on Google Colab or a cloud NVIDIA GPU. The schedule is flexible; correctness and reproducibility matter more than rushing.

## Important operating rules for Codex

1. Inspect the repository before editing. Read `README.md`, `docs/ROADMAP.md`, and `docs/EXPERIMENT_PROTOCOL.md` if present.
2. Maintain a working build. Make small, coherent changes and run the relevant tests after each phase.
3. Do not claim a feature is implemented until its code, tests, and documentation exist.
4. Do not fabricate timings, memory usage, hardware specifications, charts, citations, or conclusions.
5. Keep raw experiment output immutable; derived summaries and plots go in separate directories.
6. Benchmark in Release mode. Separate instrumented comparison-count runs from timing runs.
7. Record compiler, flags, OS, CPU, RAM, GPU/runtime (if applicable), seed, dataset distribution, input size, and repetition count.
8. Prefer established upstream implementations for complex algorithms. Preserve license notices and attribution.
9. Do not silently label `std::sort` as PDQSort or Timsort. State precisely which implementation is being benchmarked.
10. If a toolchain, GPU, dependency, or memory limit blocks a phase, explain the blocker and provide the best validated alternative without pretending the experiment ran.
11. Avoid unnecessary dependencies. Keep the C++ engine portable across Linux, Windows, and macOS where practical.
12. Update the roadmap and README whenever scope or command-line options change.

## Project goals

### Required sorting experiments

Implement and compare:
- **PDQSort**: use the official/upstream implementation when practical; record version/source and license.
- **Timsort**: use a genuine, clearly identified implementation. Do not call `std::stable_sort` Timsort.
- **QuickSort**: project implementation with robust pivot handling and bounded recursion/stack depth.

Useful additional CPU baselines:
- `std::sort` (document the standard-library implementation as the library's sorting implementation, commonly introsort-based; do not assume every implementation is identical).
- Merge Sort.
- Signed-integer Radix Sort.

### Required searching experiments

Implement and compare:
- Linear Search.
- Binary Search.
- Exponential Search.

Advanced data structures:
- Skip List.
- B-Tree or M-way search tree; evaluate multiple branching factors such as M = 10, 16, 32, and 64 where practical.
- Learned Index: predict a key's rank in sorted data and correct the prediction with a bounded search or binary-search fallback.

For every search method, document whether data must be sorted, index/structure build cost, lookup complexity, extra memory, and behavior for duplicate keys.

### Dataset generation

Generate deterministic, seeded signed 32-bit integer datasets for:
- Uniform random values.
- Nearly sorted values.
- Reverse-sorted values.
- Duplicate-heavy values.

Define each distribution precisely in documentation. All sorting algorithms in a comparison must receive identical copies of the same generated data. Keep the seed and dataset-generation parameters in every result row.

### Required workload and metrics

Use a baseline of **1,000,000 values** and **1,000 search queries**, then scale through sizes such as 1K, 10K, 100K, 1M, 10M, and optionally 100M if memory permits.

Sorting metrics:
- Wall-clock execution time.
- Number of key comparisons, measured in a separate instrumented build/run.
- Peak process memory and/or clearly defined auxiliary memory.
- Correctness against a trusted reference and preservation of the input multiset.

Searching metrics:
- Total and average lookup time.
- Maximum observed per-query latency, clearly distinguished from theoretical worst-case complexity.
- Number of comparisons where feasible.
- Index/data-structure build time and memory.
- Both successful and unsuccessful queries. Fix and document the hit/miss ratio; use exactly the same query set for each algorithm.

Measurement quality:
- Run multiple repetitions (default 5 or more where affordable); report median and variability (e.g. min/max or IQR).
- Keep correctness checks outside timed sections.
- Avoid mixing comparison instrumentation with performance timings.
- Use a monotonic high-resolution clock; account for timer overhead for extremely fast queries.
- Record full environment and exact command/configuration.
- Use warmups when justified and describe them.
- Preserve raw CSV/JSON data separately from processed summaries and figures.

## Bonus work — complete all feasible items

### Bonus A: OpenMP parallel sorting
- Implement a documented parallel sort (e.g. parallel merge sort).
- Support configurable thread counts, including 1, 2, 4, and 8 when available.
- Validate against a trusted CPU reference.
- Report speedup `T1 / Tp` and efficiency `(T1 / Tp) / p`.
- Record thread count, compiler flags, and hardware details. Check race conditions.

### Bonus B: CUDA GPU sorting
- Prefer a reputable primitive such as NVIDIA CUB `DeviceRadixSort`, or another documented GPU sorting algorithm.
- Run on Google Colab or a cloud GPU only after confirming the actual GPU/runtime.
- Validate GPU output against the CPU reference.
- Measure and report separately:
  1. Host-to-device transfer.
  2. GPU kernel/algorithm execution.
  3. Device-to-host transfer.
  4. End-to-end latency including transfers and relevant setup.
- State whether allocation/setup is included in each metric. Synchronize correctly when timing GPU work.
- Document CUDA version, GPU model, driver/runtime, input size, and memory constraints.
- If no GPU is available, complete the CPU project and provide a reproducible notebook/instructions; mark GPU results as not run.

### Bonus C: Learned Index
- Implement a simple, explainable learned index over sorted integer keys.
- Measure build/training time, model/index memory, query latency, correction distance, and fallback frequency.
- Evaluate on multiple distributions and held-out seeds. Do not tune and report performance only on the same exact generated sample.
- Compare against binary search using identical queries.
- Document duplicate-key handling and model limitations.

### Bonus D: AlphaDev / AI-based algorithm discovery
- Include a technically accurate research section explaining AlphaDev's reinforcement-learning approach and the small sorting routines/instruction sequences it discovered.
- Do not claim to have reproduced DeepMind/AlphaDev training unless the actual training system is implemented.
- Optional extension: build a small algorithm selector using dataset features to choose among implemented sorters. Evaluate it on held-out datasets and compare with the best fixed algorithm.

### Bonus E: 100-million-element sort
- Only attempt after 1M and 10M correctness/performance runs are stable.
- Estimate memory before allocation. One 100M-element int32 array is approximately 400 MB decimal; copies, sort buffers, indexes, and process overhead can multiply this requirement.
- Run algorithms one at a time when needed; avoid retaining unnecessary copies.
- Record peak memory, wall time, environment, seed, and correctness checksum.
- If resources do not permit the experiment, report the limitation honestly and provide the largest completed size.

## Repository layout

Maintain a clear structure similar to:

```text
.
├── README.md
├── AGENTS.md
├── CMakeLists.txt
├── include/
│   ├── algorithms/
│   ├── datasets/
│   ├── benchmark/
│   └── common/
├── src/
│   ├── algorithms/
│   ├── datasets/
│   ├── benchmark/
│   └── main.cpp
├── tests/
├── scripts/
│   ├── run_matrix.py
│   ├── analyze_results.py
│   └── plot_results.py
├── notebooks/
│   └── cuda_sorting_colab.ipynb
├── docs/
│   ├── ROADMAP.md
│   ├── EXPERIMENT_PROTOCOL.md
│   ├── ALGORITHMS.md
│   └── RESULTS.md
├── report/
│   ├── REPORT_TEMPLATE.md
│   └── SLIDE_OUTLINE.md
└── results/
    ├── raw/
    ├── processed/
    └── figures/
```

Adapt an existing repository rather than duplicating it. Keep the public CLI and file naming documented.

## Implementation phases

### Phase 0 — Audit and establish baseline
- Inspect the existing source and repository state.
- Identify incomplete, incorrect, or untested code.
- Build using CMake in Release mode.
- Run current tests; fix defects before adding features.
- Record a baseline environment manifest.

Acceptance: clean build, test command documented, and no unexplained test failures.

### Phase 1 — Correctness-first core
- Centralize algorithm interfaces and dataset generation.
- Add deterministic distributions and command-line configuration.
- Add unit/property tests for empty arrays, one element, sorted/reverse data, duplicates, negative values, integer boundaries, and randomized arrays.
- Verify sorted order and equality to a trusted reference, not only `is_sorted`.
- Verify search hit/miss correctness, including duplicates and boundary keys.
- Add sanitizers in a suitable Debug test configuration where supported.

Acceptance: all algorithms pass the test suite and can be invoked consistently.

### Phase 2 — Required sorting algorithms
- Integrate PDQSort and a genuine Timsort implementation.
- Keep QuickSort as the project baseline.
- Add Merge Sort and Radix Sort as useful extra baselines if not already present.
- Add separate comparison-count instrumentation and memory measurement.
- Test all algorithms across every distribution.

Acceptance: same data, correctness checks, repeatable timing CSV, comparison counts, and documented implementations/licenses.

### Phase 3 — Search benchmarks
- Generate a deterministic query set containing successful and unsuccessful queries at a documented ratio.
- Reuse that exact query set across algorithms.
- Implement linear, binary, and exponential search.
- Record average and max observed latency, comparisons, correctness, and repetitions.
- Add per-query measurements only if timer resolution and overhead make them meaningful.

Acceptance: results include both hit and miss workloads; correctness is independently checked.

### Phase 4 — Search data structures
- Implement Skip List and B-Tree/M-way tree.
- Keep construction/build time separate from query time, and also report end-to-end cost when useful.
- Evaluate multiple branching factors and discuss memory/cache trade-offs.
- Define duplicate semantics consistently.

Acceptance: all data structures pass differential tests against a sorted-vector reference.

### Phase 5 — Experiment orchestration and analysis
- Add a script to run the complete experiment matrix with stable seeds/configuration.
- Save raw records with schema/version information.
- Add Python summaries and publication-quality plots for time vs. N, distributions, comparisons, memory, search performance, and variability.
- Include error bars or spread indicators where appropriate.
- Make plots reproducible from raw data.

Acceptance: one documented command can run a small smoke matrix; analysis never silently drops failed runs.

### Phase 6 — OpenMP
- Implement and test parallel sorting.
- Sweep supported thread counts.
- Report scaling, speedup, and efficiency.
- Use identical inputs and compiler options for fair comparison.

Acceptance: correctness under multiple thread counts; results include the number of threads and hardware context.

### Phase 7 — CUDA
- Create a reproducible Colab notebook and/or cloud execution guide.
- Implement the selected GPU sorter with correct synchronization and transfers.
- Verify output against CPU reference.
- Report kernel-only and end-to-end timing separately.

Acceptance: verified GPU device and software details, correctness check, and complete timing breakdown—or a clearly documented not-run status.

### Phase 8 — Learned Index and AlphaDev study
- Implement and test the Learned Index.
- Compare with binary search on identical hit/miss queries.
- Write the AlphaDev research section using primary sources.
- Optionally implement and validate a learned algorithm selector.

Acceptance: build/query/memory metrics, held-out evaluation, and no unsupported claims.

### Phase 9 — 100M scale
- Profile memory before running.
- Increase scale gradually and keep raw results.
- Run feasible algorithms and document any omitted experiments with reasons.

Acceptance: measured size and resource use are reported honestly.

### Phase 10 — Report and presentation
Create a rigorous report with:
1. Abstract.
2. Introduction and research questions.
3. Related work and algorithm overview.
4. Experimental methodology and hardware/software environment.
5. Results and plots.
6. Discussion of theoretical vs observed behavior.
7. Limitations and threats to validity.
8. Conclusion and future work.
9. References.

Create a 10–12-slide presentation with the problem, methodology, algorithms, dataset design, measured results, CPU/GPU/parallel bonus findings, limitations, and conclusion.

Only include actual measurements in results. Label unavailable experiments explicitly. Cite primary papers and official implementations.

## Quality and correctness requirements

- Use clear names, const-correctness, RAII, and appropriate C++ standard-library facilities.
- Avoid undefined behavior, signed overflow, unsafe indexing, and unbounded recursion.
- Use deterministic seeds and log all parameters.
- Validate output against a trusted reference and compare the full sorted result where practical.
- Keep timed regions minimal and consistent.
- Handle duplicates, negative integers, empty input, and extreme integer values.
- Avoid measuring file I/O or dataset generation as sorting time unless explicitly reported as an additional end-to-end metric.
- Keep each CSV column documented and use a stable schema.
- Add tests for CSV parsing and Python analysis.
- Do not hide failed runs; record their status and error.
- Preserve third-party license and attribution files.
- Update docs and roadmap as features become complete.

## First task to execute now

Start by auditing the current repository. Then:
1. List the existing files and identify what is implemented versus missing.
2. Build the project in Release mode.
3. Run all current tests and fix any correctness/build problems.
4. Add or improve differential/property tests before implementing new algorithms.
5. Report a concise audit: current status, tests run and their actual outcomes, blockers, and the next smallest implementation step.
6. Do not start CUDA or 100M runs until the baseline is correct and tested.

Proceed autonomously in small validated steps. Ask a question only when a real blocker requires a user decision; otherwise choose a sensible documented default.
