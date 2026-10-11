#!/usr/bin/env python3
"""Generate the CPU-only release from raw-audited retained CPU studies."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import textwrap
import shutil
from verify_cpu import verify

ROOT = Path(__file__).resolve().parents[1]


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path): return json.loads(Path(path).read_text())
def require(ok, message):
    if not ok: raise ValueError(message)
def write(path, value):
    with path.open('x') as stream: json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')


def input_paths(evidence, learned, metrics):
    historical = ROOT / 'results/processed'
    return dict(sort1m=historical/'sorting_1m_20261009T172003802655Z/cross_seed.json',
        cpu=historical/'phase5_full_20261009T191000587965Z/summary.json',
        openmp=historical/'openmp_scaling_20261009T200852928292Z_retry1/summary.json',
        learned=learned/'summary.json',metrics=metrics/'summary.json',
        scale10=evidence/'sorting_10m_summary.json',scale100=evidence/'sorting_100m_summary.json')


def generate(evidence, learned, metrics, output):
    if output.exists() or output.is_symlink(): raise FileExistsError('report destination already exists')
    raw_audit = verify(evidence, learned, metrics)
    paths = input_paths(evidence, learned, metrics)
    inputs = {k:load(p) for k,p in paths.items()}
    for k in ['cpu','openmp','scale10','scale100']: require(inputs[k]['complete'] is True,'incomplete '+k)
    for k in ['learned','metrics']: require(inputs[k]['failed']==0 and inputs[k]['missing']==0,'incomplete '+k)
    require(inputs['learned']['configurations']==48 and inputs['metrics']['configurations']==240,'wrong extension coverage')
    require(sum(g['successful_trials'] for g in inputs['scale10']['groups'])==450,'10M trials')
    require(sum(g['successful_trials'] for g in inputs['scale100']['groups'])==150,'100M trials')
    for k in ['scale10','scale100']:
        require(all(g['failed_trials']==0 and g['missing_measured_trials']==0 and g['run_complete'] for g in inputs[k]['groups']), 'failed scale rows')
    output.mkdir()
    write(output/'RAW_VERIFICATION.json',raw_audit)
    write(output/'INPUTS_SHA256.json',{str(p.relative_to(ROOT)):sha(p) for p in paths.values()})
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    plt.rcParams.update({'font.size':10,'svg.hashsalt':'mab_final_report_v1'})
    plots=[]

    # The table and plots use one median per seed dataset, never pooled repetitions.
    fig,ax=plt.subplots(figsize=(8,4.8),layout='constrained')
    rows=[r for r in inputs['sort1m']['groups'] if r['distribution']=='uniform']
    x=list(range(len(rows)));y=[r['median_of_seed_medians_ns']/1e6 for r in rows]
    ax.bar(x,y,color='#326789')
    ax.errorbar(x,y,yerr=[[m-r['min_seed_median_ns']/1e6 for m,r in zip(y,rows)],
                 [r['max_seed_median_ns']/1e6-m for m,r in zip(y,rows)]],fmt='none',color='black',capsize=4)
    ax.set_xticks(x,[r['algorithm'] for r in rows],rotation=15)
    ax.set(ylabel='Sort latency (ms)',title='Retained 1M uniform study\nMedian of 3 seed medians; bars show cross-seed min–max; 5 trials/seed')
    ax.set_ylim(bottom=0);ax.grid(axis='y',alpha=.2)
    fig.savefig(output/'sorting_1m.png',dpi=220);plt.close(fig)
    plots.append(dict(file='sorting_1m.png',source=str(paths['sort1m'].relative_to(ROOT)),filters=dict(distribution='uniform'),unit='ms',method='median of seed medians; min/max spread'))

    # Scaling sizes are separate studies; lines describe observations, not a fitted model.
    fig,ax=plt.subplots(figsize=(8,4.8),layout='constrained')
    scale_rows=[]
    for algorithm in sorted({r['algorithm'] for r in inputs['sort1m']['groups']}):
        observed=[]
        for n,key in [(1000000,'sort1m'),(10000000,'scale10'),(100000000,'scale100')]:
            values=[r['median_of_seed_medians_ns'] if key=='sort1m' else r['median_ns'] for r in inputs[key]['groups'] if r['algorithm']==algorithm and r['distribution']=='uniform']
            require(bool(values),'missing scaling group')
            value=statistics.median(values)/1e9; observed.append(value)
            dataset_count = next(r['dataset_count'] for r in inputs[key]['groups'] if r['algorithm']==algorithm and r['distribution']=='uniform') if key=='sort1m' else len(values)
            scale_rows.append(dict(size=n,algorithm=algorithm,distribution='uniform',median_of_dataset_medians_seconds=value,datasets=dataset_count))
        ax.plot([1e6,1e7,1e8],observed,marker='o',label=algorithm)
    ax.set_xscale('log');ax.set_yscale('log');ax.grid(alpha=.25);ax.legend(fontsize=8)
    ax.set(xlabel='Input keys (log scale)',ylabel='Median sort latency (seconds, log scale)',
           title='Uniform scaling: observed CPU study medians\n1M/10M: 3 seeds; 100M: 1 seed; 5 trials/dataset; no extrapolation')
    fig.savefig(output/'cpu_scaling.png',dpi=220);plt.close(fig)
    plots.append(dict(file='cpu_scaling.png',sources=[str(paths[k].relative_to(ROOT)) for k in ['sort1m','scale10','scale100']],
                      filters=dict(distribution='uniform'),unit='seconds',method='within-dataset medians then equal seed weights',limitation='100M one seed; different run environments'))

    cpu=inputs['cpu'];max_search=max(r['size'] for r in cpu['cross_dataset'] if r['family']=='search')
    search=[r for r in cpu['cross_dataset'] if r['family']=='search' and r['size']==max_search and r['distribution']=='uniform' and r['query_category']=='mixed_50']
    structures=[r for r in cpu['cross_dataset'] if r['family']=='structures' and r['size']==max_search and r['distribution']=='uniform' and r['query_category']=='mixed_50' and r['operation']=='lookup']
    for name,group in [('search',search),('structures',structures)]:
        require(bool(group),'missing retained '+name+' data')
        fig,ax=plt.subplots(figsize=(8,4.8),layout='constrained')
        y=[r['statistics']['median']/r['batch_size'] for r in group]
        ax.errorbar(range(len(group)),y,yerr=[[m-r['statistics']['minimum']/r['batch_size'] for m,r in zip(y,group)],
                    [r['statistics']['maximum']/r['batch_size']-m for m,r in zip(y,group)]],fmt='o',color='#447b67',capsize=4)
        ax.set_xticks(range(len(group)),[r['algorithm'] for r in group],rotation=15)
        ax.set_yscale('log');ax.set(ylabel='Normalized batch average (ns/query, log scale)',title=f'Retained {name}, uniform N={max_search}, 50% hits\nDataset medians, then equal-weight distinct inputs; 1000 queries/batch')
        fig.savefig(output/(name+'.png'),dpi=220);plt.close(fig)
        plots.append(dict(file=name+'.png',source=str(paths['cpu'].relative_to(ROOT)),filters=dict(family=name,size=max_search,distribution='uniform',query_category='mixed_50'),
                          unit='normalized batch ns/query',method='dataset medians divided by batch size; log y-axis'))

    learned_rows=[r for r in inputs['learned']['cross_seed'] if r['size']==1000000]
    omp_rows=[r for r in inputs['openmp']['cross_dataset'] if r['size']==1000000 and r['distribution']=='uniform']
    fig,ax=plt.subplots(figsize=(8,4.8),layout='constrained')
    x=[r['threads'] for r in omp_rows];y=[r['algorithmic_speedup']['median'] for r in omp_rows]
    ax.errorbar(x,y,yerr=[[m-r['algorithmic_speedup']['minimum'] for m,r in zip(y,omp_rows)],
                         [r['algorithmic_speedup']['maximum']-m for m,r in zip(y,omp_rows)]],marker='o',capsize=4)
    ax.axhline(1,color='gray',linestyle='--');ax.set_xticks(x);ax.set_ylim(bottom=0);ax.grid(alpha=.2)
    ax.set(xlabel='Requested and observed team size',ylabel='Sequential Merge Sort / parallel Merge Sort',
           title='Retained OpenMP: uniform N=1,000,000\nMedian of 3 dataset ratios; min–max spread; 5 trials/dataset')
    fig.savefig(output/'openmp.png',dpi=220);plt.close(fig)
    plots.append(dict(file='openmp.png',source=str(paths['openmp'].relative_to(ROOT)),
        filters=dict(size=1000000,distribution='uniform'),unit='ratio',
        method='ratio of within-dataset medians to sequential merge; median/min/max across seed ratios'))
    for name in ['uniform_count.png','uniform_process_rss.png']:
        shutil.copyfile(metrics/name,output/name)
        plots.append(dict(file=name,source=str((metrics/name).relative_to(ROOT)),summary=str(paths['metrics'].relative_to(ROOT)),
            method='retained separate instrumented observations; median/min/max across three seeds',
            unit='comparisons/N' if name=='uniform_count.png' else 'process lifetime peak RSS MiB'))
    # Record rendering inputs and code as well as the numerical summaries.
    extra=[Path(__file__),Path(__file__).with_name('verify_cpu.py'),metrics/'uniform_count.png',metrics/'uniform_process_rss.png']
    write(output/'RENDER_INPUTS_SHA256.json',{str(p.relative_to(ROOT)):sha(p) for p in extra})
    sections=[]
    def section(title,body):sections.append((title,body))
    section('Abstract',
        'This individual C++17/Python project evaluates six sequential sorting implementations, OpenMP Merge Sort, '
        'three array searches, Skip List and four B-tree orders, plus a simple learned rank index. '
        'The retained CPU experiments and new held-out learned/10M/100M studies provide descriptive evidence. '
        'The new scale extension completed 600 measured sorts and 120 warm-ups, all correct. '
        'The learned study completed 480 measured query batches and 240 measured builds. '
        'This release is CPU-only: GPU/CUDA/CUB execution and comparisons are deferred, not completion requirements. '
        'No CPU-versus-GPU performance result is claimed. No universal performance ranking or significance claim is made.')
    section('Introduction and research questions',
        'How do input order and duplicate frequency affect concrete sort implementations? How do query outcome and location '
        'affect array and ordered-index lookup? How does OpenMP scaling compare with sequential Merge Sort? '
        'When does a rank model require correction or fallback? How do separate key-comparison and process-memory observations inform timing? '
        'The project addresses these questions with deterministic inputs, full oracle checking and retained raw data.')
    section('Related work and implementation identities',
        'PDQSort is Orson Peters’ upstream implementation at commit b1ef26a55cdb60d236a5cb199c4234c704f46726 (Zlib). '
        'Timsort is cpp-TimSort at99b612d9826e8387a30008f2b21be206181ad890 (MIT). std_sort is this toolchain’s standard-library sort, '
        'not renamed PDQSort or Timsort. QuickSort has a depth budget and heapsort fallback. Merge Sort is stable and uses a temporary vector. '
        'Signed Radix Sort uses four stable byte passes and a signed-order bit mapping. OpenMP tasks retain the sequential baseline. '
        'See docs/ALGORITHMS.md and vendor UPSTREAM.json files for licenses/hashes. Deferred GPU code is excluded from this release’s result inputs. '
        'The learned endpoint model and AlphaDev research review are documented in docs/LEARNED_INDEX_PROTOCOL_v1.md and docs/ALPHADEV_STUDY.md.')
    section('Methodology and environment',
        'Signed int32 generator-v1 uses a fresh mt19937_64(seed); distributions and rejection sampling are frozen in EXPERIMENT_PROTOCOL.md. '
        'All corresponding sorting calls use identical original inputs. Sorting uses steady_clock nanoseconds, excludes generation, input restoration, '
        'oracle work and serialization, and checks complete output equality after timing. Primary timing contains no comparison instrumentation. '
        'One warm-up and five repetitions are used. New CPU runs use Linux Pop!_OS kernel6.18.7, GCC13.3.0, CMake3.28.3, -O3 -DNDEBUG, '
        'Intel i5-11400H (6 physical/12 logical cores), and approximately16.48GB RAM. Governors report powersave; background load, caches, '
        'temperature and frequency were not controlled. Agent-launched benchmarks and builds were serialized; external background work was uncontrolled. '
        'Historical studies retain their own metadata and must not be treated as the same session. Study protocols and exact commands reside in the audit.')
    sort_table='|Algorithm|Distribution|Median of 3 dataset medians (ms)|Cross-seed min–max (ms)|\n|---|---|---:|---:|\n'
    for r in inputs['sort1m']['groups']:
        sort_table+=f"|{r['algorithm']}|{r['distribution']}|{r['median_of_seed_medians_ns']/1e6:.3f}|{r['min_seed_median_ns']/1e6:.3f}–{r['max_seed_median_ns']/1e6:.3f}|\n"
    section('Results: retained 1M sorting study',
        'Historical evidence:15 dataset configurations;450 measured sorts and90 warm-ups; six sorters, five distributions and three seeds. '
        'These observations show workload-dependent differences between concrete implementations, not a universal ordering.\n\n'+sort_table+'\n![1M uniform](sorting_1m.png)')
    scale_table='|N|Algorithm|Uniform median of dataset medians (s)|Seed datasets|\n|---:|---|---:|---:|\n'
    for r in scale_rows:scale_table+=f"|{r['size']}|{r['algorithm']}|{r['median_of_dataset_medians_seconds']:.6f}|{r['datasets']}|\n"
    section('Results: CPU scale extension',
        '10M:15 datasets across five distributions and three seeds;450 measured/90 warm-up sorts. '
        '100M:five datasets across five distributions and seed1729;150 measured/30 warm-up sorts. '
        'All six sorters completed every configuration with full equality to the oracle. '
        'The policy estimate was160MB array payload at10M and1.6GB at100M, with separate512MiB/2048MiB caps and more than3GiB RAM safety headroom. '
        'These planning quantities are not measured RSS. The100M command-level lifetime RSS is retained in the /usr/bin/time log; '
        'it cannot isolate a single sorter.\n\n'+scale_table+'\n![Observed scaling](cpu_scaling.png)')
    query_table='|Family|Algorithm|N|Normalized batch average (ns/query)|\n|---|---|---:|---:|\n'
    for r in search+structures:query_table+=f"|{r['family']}|{r['algorithm']}|{r['size']}|{r['statistics']['median']/r['batch_size']:.3f}|\n"
    section('Results: search and ordered structures',
        'The retained full CPU pipeline includes '+str(cpu['counts']['search']['successful_measured'])+' measured search batches and '
        +str(cpu['counts']['structures']['successful_measured'])+' measured structure operations. '
        'Construction and lookup remain separate. Binary/exponential search return the first equal array index; structures implement ordered maps with unique keys and first-inserted payloads. '
        'Mixed query batches use exact50% hit/miss ratios. The following is a representative retained uniform group. '
        'Batch time/query count is a normalized average, not a directly measured individual-query latency or maximum.\n\n'+query_table+
        '\n![Search](search.png)\n\n![Structures](structures.png)')
    learned_table='|Distribution|Algorithm|Operation|Median of 3 dataset medians (ns)|\n|---|---|---|---:|\n'
    for r in learned_rows:learned_table+=f"|{r['distribution']}|{r['algorithm']}|{r['operation']}|{r['median']:.1f}|\n"
    section('Results: learned rank index',
        'The fixed endpoint affine model uses radius32, certified local lower-bound correction and a full binary-search fallback. '
        'The evaluation has48 workload configurations (1K/10K/100K/1M, four distributions, seeds42/2718/314159) and1000 queries/configuration,500 hits/500 misses. '
        'These contain24 distinct sorted input vectors: uniform, reverse and nearly sorted collapse to identical contents after sorting for a given size/seed. '
        'Workload labels are kept separate and are not pooled as independent datasets. '
        'Evaluation seeds are held out from performance tuning; some also appear in correctness tests, which did not tune the model. '
        'The indexed vector itself supplies model endpoints; this is not unseen-key neural generalization. '
        '480 measured lookup batches,240 measured builds,144 warm-ups and48000 untimed diagnostic queries completed with no failures. '
        'Build includes the owned copy and validation. Query batches exclude build and diagnostics. '
        'summary.json retains fallback rates, correction distance, separate comparisons and logical memory. '
        'The model does not guarantee O(1) lookup; duplicate/skewed data can force O(logN) fallback.\n\n'+learned_table)
    omp_table='|Threads|Median sequential-baseline speedup|Min–max dataset speedup|Median efficiency|Parallel-one-thread baseline speedup|\n|---:|---:|---:|---:|---:|\n'
    for r in omp_rows:
        s=r['algorithmic_speedup']
        omp_table+=f"|{r['threads']}|{s['median']:.3f}|{s['minimum']:.3f}–{s['maximum']:.3f}|{r['algorithmic_efficiency']['median']:.3f}|{r['parallel_one_thread_speedup']['median']:.3f}|\n"
    section('Results: OpenMP scaling',
        'The retained OpenMP scaling study completed1800 measured sorts and360 warm-ups across requested1/2/4/8-thread configurations at32768/100000/1000000 keys. '
        'Its primary speedup baseline is sequential Merge Sort; parallel one-thread timing is separately identified. '
        'Speedup is T_sequential/T_parallel and efficiency is speedup/observed team size; values below1 are retained. '
        'Ratios are calculated within datasets before equal weighting distinct input fingerprints. '
        'The uniform1M table uses three seed datasets, each with five timings per implementation. '
        'Team size does not establish task participation, physical-core concurrency or race freedom.\n\n'+omp_table+'\n![OpenMP scaling](openmp.png)')
    section('Results: comparison counts and process memory',
        '240 separate sort_metrics executions provide exact key-comparison counts for five adapters and process RSS. '
        'Radix counting is unsupported. Counts have consistent executed-key-predicate semantics but do not model moves, cache misses or total instructions. '
        'RSS includes input/runtime/allocator/instrumentation and is not isolated auxiliary space. '
        'Each size/distribution/algorithm has three seed observations, not repeated RSS samples. '
        'Median and min–max across these observations describe different inputs, not independent process-repeatability estimates.\n\n'
        '![Separate comparison counts](uniform_count.png)\n\n![Process memory](uniform_process_rss.png)')
    section('Release scope and deferred work',
        'This is a complete CPU-only release for the declared studies. GPU execution, CUDA/CUB comparisons and the frozen CPU/GPU full study '
        'are outside the release acceptance criteria. Their source, pins, protocols, matrices and failed/partial validation attempts are preserved in place '
        'and indexed by docs/DEFERRED_GPU.md. Historical GPU pilots are separate earlier experiments, not observations from the unexecuted full protocol. '
        'No GPU numbers enter the report tables or plots, and no CPU-versus-GPU conclusion is made. '
        'The independent CPU/GPU approval gate remains enforced and unmodified; it is not a prerequisite for local CPU analysis or correctness. '
        'Individual-query maxima, isolated structure allocations and independent-machine replication remain documented limitations, not fabricated deliverables.')
    section('Statistical interpretation and threats to validity',
        'Repeated timings are first summarized within each dataset using median, mean, sample SD, min and max. '
        'Cross-seed summaries equally weight dataset medians; identical fingerprints are collapsed where the family analyzer specifies it. '
        'No outliers are discarded and no confidence interval or significance claim is inferred from three seeds. '
        '100M uses one seed, so only within-dataset variability exists. '
        'Shared runtime scheduling, SMT, allocator/cache history, frequency/thermal behavior and background load can confound observations. '
        'Key-only tests cannot empirically distinguish the order of equal payloads; stability follows the documented merge strategy and existing generic stability tests. '
        'Search individual-query maxima are not collected because the batch engine does not measure them; normalized batch maxima cannot substitute. '
        'Structure comparison/allocation metrics and a learned sorter selector remain unsupported/optional. '
        'ThreadSanitizer/OpenMP limitations in earlier audits mean ordinary passing tests are not a proof of race freedom.')
    section('Conclusion, reproducibility and references',
        'The validated CPU implementation, held-out model evaluation and completed100M feasibility extension support workload-specific analysis. '
        'The release conclusions concern CPU implementations only. GPU comparisons are deferred and do not prevent completion of this CPU-only scope. '
        'AlphaDev is reviewed from primary sources; no reinforcement-learning training or assembly discovery was reproduced.\n\n'
        'Regenerate this report with `python3 report/generate.py --evidence '+str(evidence.relative_to(ROOT))+
        ' --learned '+str(learned.relative_to(ROOT))+' --metrics '+str(metrics.relative_to(ROOT))+' --output NEW_REPORT_DIRECTORY`. '
        'INPUTS_SHA256.json identifies every source summary; PLOTS.json records filters, units and transformations. '
        'FINAL_AUDIT.md and COMMANDS.md retain actual validation/build/experiment commands and failures. '
        'Raw CSV remains immutable; derived outputs use new directories.\n\n'
        'Primary references: [PDQSort](https://github.com/orlp/pdqsort); [cpp-TimSort](https://github.com/timsort/cpp-TimSort); '
        '[Kraska et al., SIGMOD2018](https://arxiv.org/abs/1712.01208v3); '
        '[Mankowitz et al., Nature2023](https://www.nature.com/articles/s41586-023-06004-9); '
        '[official AlphaDev archive](https://github.com/google-deepmind/alphadev).')

    with (output/'FINAL_REPORT.md').open('x') as stream:
        stream.write('# Large-Scale Evaluation of Modern Search and Sorting Algorithms\n\n'
                     'CPU-only release v1: six sorters, search, structures, OpenMP and learned-index studies. GPU comparisons are deferred and excluded.\n\n')
        for i,(title,body) in enumerate(sections,1):stream.write(f'## {i}. {title}\n\n{body}\n\n')
    write(output/'PLOTS.json',plots)
    write(output/'RESULT_TABLES.json',dict(scope='cpu_only_release_v1',sorting_1m=inputs['sort1m']['groups'],
        cpu_scaling=scale_rows,search=search,structures=structures,learned_1m=learned_rows,
        openmp_1m_uniform=omp_rows,comparisons_memory=inputs['metrics']['groups']))

    slides=[
        ('Modern Search and Sorting Benchmark', ['CPU-only C++17/Python academic release','Correctness first; reproducible raw data; scope-specific observations','CPU studies complete for declared matrices; GPU execution/comparisons deferred'],None),
        ('Research questions and implementations', ['Six sequential sorters: std_sort, QuickSort, PDQSort, Timsort, Merge Sort, Signed Radix Sort','Linear/Binary/Exponential Search; Skip List; B-tree orders10/16/32/64','OpenMP Merge Sort and endpoint learned rank index'],None),
        ('Experimental design', ['Deterministic signed-int32 generator; identical inputs; oracle equality outside timing','Release, steady_clock; one warm-up/five measured repetitions','Separate key counts/process RSS; allocation scope documented per engine','Dataset medians first; no outlier removal or unsupported significance claims'],None),
        ('1M sorting: workload-specific observations',['Uniform group shown; other distributions differ','Three seed datasets, five trials each; spread is not a confidence interval'],'sorting_1m.png'),
        ('CPU scaling through100M',['10M:450 measured +90 warm-ups;100M:150 measured +30 warm-ups','All six sorters, five distributions;100M has one seed','Log/log axes; distinct study sessions; no extrapolated performance'],'cpu_scaling.png'),
        ('Search: query outcome and position matter',['Same1000-query mixed50% batch for each searcher','Normalized batch average, not directly measured individual-query latency'],'search.png'),
        ('Ordered structures',['Skip List and B-tree variants; ordered maps preserve first-inserted payloads','Construction and lookup timed separately; representative uniform lookup shown'],'structures.png'),
        ('Learned rank index',['Endpoint affine prediction; radius32 correction; certified binary fallback','48 held-out configurations;480 measured lookup batches;240 measured builds','48000 separate diagnostics; counts, correction distance, fallback and logical storage retained','No constant-time guarantee; duplicate-heavy data can be poorly predicted'],None),
        ('OpenMP scaling',['1800 sorts;360 warm-ups;1/2/4/8 teams','Sequential Merge Sort baseline; cross-seed median/min–max','Team size does not prove task participation or race freedom'],'openmp.png'),
        ('Comparison counts and memory',['240 separate instrumented executions; five comparison adapters; Radix count unsupported','Comparison counts exclude moves, bookkeeping and instructions','RSS is whole-process lifetime peak, not isolated auxiliary allocation','All plots derive from retained observations; missing metrics remain explicit'],None),
        ('Limitations and AlphaDev',['Background load, frequency, thermals and cache state not controlled','Three seeds do not establish statistical significance;100M has one seed','Batch averages cannot establish maximum individual-query latency','AlphaDev primary-source review only: no training/discovery reproduction'],None),
        ('Conclusion and reproducibility',['CPU-only studies/report are reproducible from retained raw evidence','All historical assets preserved; GPU source/protocols/pilots deferred in place','No CPU-versus-GPU comparison; deferred guards remain enforced','RAW_VERIFICATION.json, INPUTS_SHA256.json, PLOTS.json and audits trace the results'],None)]
    with (output/'PRESENTATION.md').open('x') as stream:
        for i,(title,bullets,image) in enumerate(slides,1):
            stream.write(f'# Slide{i}: {title}\n\n'+'\n'.join('- '+b for b in bullets)+'\n\n')
            if image:stream.write(f'![Data figure]({image})\n\n')
    with PdfPages(output/'PRESENTATION.pdf',metadata={'Title':'Modern Algorithm Benchmark','CreationDate':None,'ModDate':None}) as pdf:
        for i,(title,bullets,image) in enumerate(slides,1):
            fig=plt.figure(figsize=(16,9),facecolor='white')
            fig.text(.05,.91,title,fontsize=26,color='#18354c',weight='bold')
            y=.80
            if image:
                axis=fig.add_axes([.04,.08,.65,.67]);axis.imshow(plt.imread(output/image));axis.axis('off')
                x=.73;width=31;size=16
            else:x=.07;width=100;size=21
            for bullet in bullets:
                lines=textwrap.wrap(bullet,width=width)
                fig.text(x,y,'• '+('\n  '.join(lines)),fontsize=size,va='top',linespacing=1.4)
                y-=.052*len(lines)+.055
            fig.text(.05,.025,'Raw evidence retained • descriptive results • no universal ranking',fontsize=10,color='#555555')
            fig.text(.94,.025,str(i)+'/12',fontsize=12)
            pdf.savefig(fig);plt.close(fig)
    # Compact publication artifact; the full tables remain in Markdown/JSON.
    with PdfPages(output/'REPORT.pdf',metadata={'Title':'Modern Algorithm Benchmark Report','CreationDate':None,'ModDate':None}) as pdf:
        for title,body in sections:
            narrative=body.split('\n\n|')[0]
            lines=[]
            for paragraph in narrative.split('\n\n'):lines.extend(textwrap.wrap(paragraph,width=92)+[''])
            for offset in range(0,len(lines),48):
                fig=plt.figure(figsize=(8.27,11.69));fig.text(.08,.94,title,fontsize=17,weight='bold',va='top')
                fig.text(.08,.89,'\n'.join(lines[offset:offset+48]),fontsize=10,va='top',linespacing=1.4)
                fig.text(.08,.03,'Full tables and sources: FINAL_REPORT.md / INPUTS_SHA256.json',fontsize=8)
                pdf.savefig(fig);plt.close(fig)
        for name in ['sorting_1m.png','cpu_scaling.png','search.png','structures.png','openmp.png','uniform_count.png','uniform_process_rss.png']:
            fig,axis=plt.subplots(figsize=(8.27,6));axis.imshow(plt.imread(output/name));axis.axis('off');pdf.savefig(fig);plt.close(fig)
    write(output/'SHA256.json',{p.name:sha(p) for p in sorted(output.iterdir()) if p.is_file()})
    print('Generated CPU-only raw-audited report,12-slide PDF and7 figures:',output)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    for name in ['evidence','learned','metrics','output']:parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();generate(args.evidence.resolve(),args.learned.resolve(),args.metrics.resolve(),args.output)
