# Fresh N=65,537 CUB workspace and resource validation

**Resource gate: GO. Immediate full-study launch: NO-GO.**
The isolated resource milestone passed. Full execution remains separately authorized
and needs a reviewed/tested full-matrix runner/analyzer plus fresh study prerequisites.
This run launched zero sorting calls, zero warm-ups and zero timing trials.

## Scope, frozen inputs and prior evidence

Read AGENTS, roadmap, README, experiment/frozen comparison protocols and accepted
pilot audit/report. Inspected CMake, production and prepared CUB interfaces, the
existing diagnostic, matrix/resource gates, runner and analyzer. No Git metadata
(git status128); no Git initialization, commit, push, driver changes or cleanup.
All three frozen asset hashes match freeze.json; freeze.json itself matches the
accepted-pilot identity. The planning-time execution_authorized=false field remains
unchanged; this user instruction authorizes resource diagnostics only.

Verified the accepted pilot seal's373 evidence/processed files and136 source files.
The new initial snapshot covers11165 prior result files. Frozen/source identities
are rechecked after execution; FINAL_INTEGRITY.json records the final preservation
check. No frozen protocol, matrix, resource CSV, production adapter, pin, license,
algorithm, test or previous result was edited.

Executed source bundle (unchanged accepted v2):
`results/raw/cpu_gpu_pilot_20261010T001232473460Z/cpu_gpu_pilot_source_v2.tar.gz`.
SHA256 `a923e54fb4d8323496c2e49342775d481b12af6b84bbafb4f2611614cb777510`
matches locally and remotely.166 source members inspected for safe paths and regular
files/directories before clean extraction. Existing remote paths were checked absent.
Current source and extracted protected source manifests match exactly.

## Actual fresh environment

Colab sessions initially reported none. Created new session
`cub-workspace-65537-20261010T110457Z`, actual server ID
`gpu-t4-s-kkb-usw4a0-1ii6d7odjost4`; status IDLE and inspected hardware before upload.
Tesla T4, compute7.5, UUIDGPU-254f8621-6cbe-18b0-bf2d-444f22727deb,
driver580.82.07, CUDA runtime/driver API13000, toolkit/nvcc13.0.88,
GCC13.3.0, CMake3.31.10, OpenMP4.5/-fopenmp/libgomp.
CUB3.0.1 (`CUB_VERSION=300001`), CCCL commit
f19d875da0d8bfb2e38c109b2b40522b8abbbbc3 unchanged.
Both pinned header hashes passed CMake; all1688 installed CCCL files match
the accepted pilot's complete dependency manifest. Full hashes retained.

Linux6.6.122+/glibc2.39/x86_64, Xeon@2GHz;2 logical CPUs on1 physical SMT core,
affinity[0,1], cpu.max=`max 100000`, memory.max=`max`, memory.current2756284416 bytes.
MemTotal13605830656 bytes; MemAvailable12532940800 bytes;
free disk75447238656 bytes. Snapshot load1.409/0.535/0.292.
No visible competing GPU process at the gate. Initial GPU40C/P8/0% utilization;
before diagnostic snapshot42C/SM300MHz/memory405MHz/power limit70W.
These are observations, not controlled temperatures or clocks.
Governor files unavailable; frequency, cache, thermal and background exclusivity
are uncontrolled. OMP_DYNAMIC=FALSE, THREAD_LIMIT=2, MAX_ACTIVE_LEVELS=1,
WAIT_POLICY=PASSIVE, PROC_BIND=FALSE. Selected CUDA/path environment settings and
full GPU before/after observations are retained in environment.json and gpu_after.json.

## Exact query and allocation contract

Built existing target in a clean new Release directory, C++17/CUDA17,
-O3 -DNDEBUG, CUDAarch75, sanitizers off. Only `--describe` and
`--resources 65537` ran. The latter calls existing query_comparison_resources:
signed std::int32_t pointer input/output, int item count65537, ascending
DeviceRadixSort::SortKeys full bits[0,32), null temp-storage sizing query.
Production-parameter path uses default stream; prepared path uses explicitly
created nonblocking private stream. No DeviceRadixSort execution call, input
generation, transfers, production sorter call or prepared sample was requested.

| Observation/calculation | Bytes | Result |
|---|---:|---|
| Prepared query |279295| within67108864/workspace cap |
| Production-parameter query |279295| within same cap |
| Prepared diagnostic cudaMalloc request |279295| success, checked cleanup |
| Production-parameter diagnostic cudaMalloc request |279295| success, checked cleanup |
| Diagnostic input allocation request |262148| success, checked cleanup |
| Diagnostic output allocation request |262148| success, checked cleanup |
| Actual diagnostic logical requests summed |1082886| calculated sum; physical footprint unknown |
| Combined future residency payload formula |1607182|16N+max(Wp,1)+max(Wa,1) |
| Frozen combined cap |268435456| passes |
| cudaMemGetInfo free before buffers |15527116800| half-free limit7763558400; passes |
| cudaMemGetInfo total |15637086208| runtime observation |
| Known future host payload |1572888|24N calculated; not allocated/measured here |

All checked CUDA calls/allocations/cleanup returned successfully before JSON output.
Both diagnostic workspaces coexist while allocated. The diagnostic uses one
input/output pair; the frozen combined formula budgets both prepared and production
pairs concurrently. That combined layout and pinned host buffers were not allocated
here. Successful requested bytes do **not** establish allocator-rounded physical
allocation, production allocation instrumentation or isolated process RSS. Runtime,
context, allocator/pageable staging and task overhead remain outside payload formulas.
Fresh1GiB host MemAvailable/applicable cgroup and disk gates pass without cap changes.
The frozen CSV's279295-byte historical prepared value agrees; its unknown fields
remain unchanged. Actual current queries reside only in this new evidence directory.

## Validation and evidence

Configure/build/describe/resource diagnostic/GPU metadata commands all exit0;
see COMMANDS.md and full local/remote JSON command logs. Fresh build warning count341,
all known nvcc-generated `style of line directive is a GCC extension`, no new category
or suppression. No new CUB/compiler incompatibility. Git status128 is expected
for absent metadata; no failed CUDA/resource command occurred.

Independent local validation checked the archive SHA256
`880a55d64834c59f0a461eb558b9527583aef0d5a61a7d77e76e997527f83872`, all19 inner manifest files,
remote exit statuses, COMPLETE.json, absence of FAILED.json, exact resource JSON,
frozen formulas/caps, environment gates, source equivalence and full installed tree.
CLI exit0 alone was not used as proof. See INDEPENDENT_VERIFICATION.json.
Fresh sorting correctness/CPU CTest/sanitizer/kernel-smoke tests were not run in
this unchanged-code, query-only milestone. Accepted pilot Release/sanitizer/GPU
correctness outcomes remain historical, not reproduced here. No inference of GPU
sort correctness or race freedom is made from these allocation checks.

## Pilot variability and go/no-go review

Reviewed retained statistics.csv, five samples per input, all outliers retained.
Sample coefficient of variation=100*sampleSD/mean, used descriptively:
- N1025 uniform prepared D2H:65.34%, min3072.000/max11232.000ns (see exact JSON values).
- N1025 signed_edges sequential merge primary:32.82%, min14935/max28465ns.
- N1M uniform prepared device sort:17.00%, min326175.988/max524800.003ns.
Exact means/SD/extrema for all48 groups are in pilot_variability_review.json;
rounded figures here must be read against those retained values.
Only one input/seed per pilot workload and one cloud session were observed.
Five repeat timings do not create five independent datasets. CPU SMT, cloud load,
uncontrolled frequency/thermal/cache state, allocator/context history and float-ms
event precision limit interpretation. No CI, significance, ranking or outlier removal.
Prepared metrics cannot be CPU host-call ratio denominators.

Resource feasibility for N65537 is GO under the unchanged limits. Together with
accepted1025/1M observations it removes the previously missing-size workspace
uncertainty, but all sizes must be rechecked in the eventual study VM.
Immediate full-study launch is NO-GO: current run_cpu_gpu_pilot.py explicitly
supports pilot only; analyze_cpu_gpu.py requires matrix_part=pilot, six datasets,
and workspace keys1025/1M. No full-matrix invocation/completeness analysis is yet
validated. Separate authorization is also absent. No frozen-protocol defect or
parameter change is needed to add that missing orchestration/analysis support.

**Exact next milestone:** implement/review/test a separate full-matrix orchestration
and analyzer path consuming the unchanged study cells/counts; validate strict
1200 measured+240 warm-up completeness, three-size resource coverage, paired and
cross-input summaries using deterministic synthetic fixtures. Then request explicit
study authorization and rerun frozen fresh-environment/build/CPU-sanitizer/GPU-
correctness prerequisites and resource gates before any main timing. The retained
pilot7.360s *8 =58.88s count-only proxy (plus historical541.073s prerequisites) is
not a measured full runtime or a guarantee; preserve1800s main timeout and headroom.

## Changed files

Only docs/AUDIT.md and docs/ROADMAP.md status additions, plus this unique evidence
directory: inspection/remote/verification/report/sealing scripts; command logs;
before-documentation snapshots; source/freeze/prior-artifact manifests; downloaded
archive and safely extracted environment/build/header/query/allocation evidence;
pilot variability review; final audit, commands and integrity manifest.
No production/test/CMake/README/frozen file change. No pilot/full study/100M run.
