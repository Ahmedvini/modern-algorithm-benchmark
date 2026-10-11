#include "algorithms/detail/parallel_mergesort_impl.hpp"
#include "algorithms/mergesort.hpp"
#include "benchmark/parallel_timing.hpp"
#include "test_support.hpp"
#include <atomic>
#include <future>
#include <iostream>
#include <limits>

namespace {
struct Trace {
    std::atomic<std::size_t> tasks{0}, merges{0};
    std::atomic<unsigned> workers{0};
    std::atomic<bool> bad{false};
    std::size_t size;
};
struct Observer {
    Trace* trace;
    void task(std::size_t begin,std::size_t end) const noexcept {
        if(begin>=end || end>trace->size) trace->bad.store(true);
        trace->tasks.fetch_add(1);
        trace->workers.fetch_or(1U<<static_cast<unsigned>(omp_get_thread_num()));
    }
    void merge(std::size_t begin,std::size_t middle,std::size_t end) const noexcept {
        if(begin>middle || middle>end || end>trace->size) trace->bad.store(true);
        trace->merges.fetch_add(1);
    }
};
struct GroupLess { bool operator()(mab::Key a,mab::Key b) const noexcept { return a/100000<b/100000; } };
}
int main() {
 try {
    std::size_t cases=0, output_checks=0;
    const auto check=[&](const mab::Values& input) {
        auto expected=input, sequential=input;
        std::sort(expected.begin(),expected.end());mab::merge_sort(sequential);
        require(expected==sequential,"sequential baseline mismatch");
        for(int p:{1,2,4,8}) {
            auto actual=input;
            const auto info=mab::parallel_merge_sort(actual,p);
            require(actual==expected,"parallel differential/permutation mismatch");++output_checks;
            require(info.actual_threads>=1 && info.actual_threads<=p,"invalid team size");
            const bool region=p>1 && input.size()>=mab::parallel_merge_threshold;
            require(info.parallel_region==region,"parallel threshold mismatch");
            if(!region) require(info.actual_threads==1,"serial call claims team");
            actual=input;
            const auto sorter=mab::find_parallel_sorter("parallel_merge_sort",p);
            sorter.sort(actual,sorter.threads);
            require(actual==expected,"registered/repeated sort mismatch");++output_checks;
            mab::Values small{3,-1,0};mab::parallel_merge_sort(small,p);
            require(small==mab::Values({-1,0,3}),"workspace isolation");
        }
        ++cases;
    };
    const auto lo=std::numeric_limits<mab::Key>::min(),hi=std::numeric_limits<mab::Key>::max();
    for(const auto& v:std::vector<mab::Values>{{},{0},{lo},{hi},{2,1},{1,2},{1,1},{hi,lo,0,-1,1,lo+1,hi-1,hi,lo}})check(v);
    std::size_t combinations=1;
    for(std::size_t n=0;n<=5;++n) {
        for(std::size_t code=0;code<combinations;++code) {
            auto x=code;mab::Values v(n);for(auto& k:v){k=static_cast<mab::Key>(x%3)-1;x/=3;}check(v);
        }
        combinations*=3;
    }
    for(auto seed:{std::uint64_t{42},std::uint64_t{1729}})
      for(std::size_t n:{0,1,2,3,7,31,16383,16384,16385,32767,32768,32769,65535,65536,65537})
        for(int distribution=0;distribution<5;++distribution) {
            mab::TimingConfig config;config.dataset.size=n;config.dataset.seed=seed;
            config.sorted_input=distribution==4;
            config.dataset.distribution=static_cast<mab::Distribution>(distribution==4?0:distribution);
            check(mab::make_timing_input(config));
        }
    check(mab::Values(65537,lo));
    mab::Values decorated(65537);
    for(std::size_t i=0;i<decorated.size();++i)decorated[i]=static_cast<mab::Key>((i%7)*100000+i);
    auto stable=decorated;std::stable_sort(stable.begin(),stable.end(),GroupLess{});
    Trace trace;trace.size=decorated.size();
    const auto info=mab::detail::parallel_merge_sort_impl(decorated,8,GroupLess{},Observer{&trace});
    require(decorated==stable,"stable projected-key order mismatch");
    require(trace.tasks>0 && trace.merges>0 && !trace.bad,"task/merge observer validation failed");
    require(info.parallel_region && info.actual_threads>=2,"parallel fixture did not form a team");
    const auto concurrent=[&](int p) {mab::TimingConfig c;c.dataset.size=131073;c.dataset.seed=static_cast<std::uint64_t>(p);
        auto v=mab::make_timing_input(c),expected=v;std::sort(expected.begin(),expected.end());
        for(int i=0;i<5;++i){auto copy=v;mab::parallel_merge_sort(copy,p);if(copy!=expected)return false;}return true;};
    auto a=std::async(std::launch::async,concurrent,2),b=std::async(std::launch::async,concurrent,4);
    require(a.get() && b.get(),"concurrent independent invocations failed");
    for(int invalid:{-1,0,65}) {mab::Values v{2,1};bool rejected=false;
        try{mab::parallel_merge_sort(v,invalid);}catch(const std::invalid_argument&){rejected=true;}
        require(rejected && v==mab::Values({2,1}),"invalid threads mutated input");}
    bool nested_rejected=false;
    #pragma omp parallel num_threads(2) shared(nested_rejected)
    {
        #pragma omp single
        {mab::Values v{2,1};try{mab::parallel_merge_sort(v,2);}catch(const std::invalid_argument&){nested_rejected=true;}}
    }
    require(nested_rejected,"nested OpenMP call was not rejected");
    bool serialized_rejected=false;
    #pragma omp parallel num_threads(1) shared(serialized_rejected)
    {
        mab::Values v{2,1};
        try{mab::parallel_merge_sort(v,2);}catch(const std::invalid_argument&){serialized_rejected=true;}
    }
    require(serialized_rejected,"serialized enclosing OpenMP region was not rejected");
    mab::TimingConfig c;c.dataset.size=32768;c.repetitions=2;c.warmups=1;
    auto v=mab::make_timing_input(c);std::size_t rows=0;
    require(mab::run_parallel_timing_trials(v,c,{mab::find_parallel_sorter("merge_sort",4),mab::find_parallel_sorter("parallel_merge_sort",4)},
        [&](const mab::TimingTrial& row){require(row.status=="ok" && row.correctness=="passed" && row.elapsed_ns.has_value(),"timing correctness");
            require(row.requested_threads==(row.algorithm=="merge_sort"?1:4),"requested team metadata");++rows;}),"shared timing failed");
    require(rows==6,"shared timing row count");
    require(mab::sorters().size()==6 && mab::sorters().front().name=="std_sort","old registry/default changed");
    std::cout<<"Passed "<<cases<<" inputs, "<<output_checks<<" public/registry output checks at threads1/2/4/8; 10 concurrent large calls; "
             <<trace.tasks<<" observed tasks, "<<trace.merges<<" observed merges, worker mask="<<trace.workers
             <<"; stability, threshold, nested rejection and 6 timing rows passed\n";
    return 0;
 } catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
