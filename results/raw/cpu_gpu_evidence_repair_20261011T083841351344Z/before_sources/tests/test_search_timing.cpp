#include "benchmark/search_timing.hpp"
#include "algorithms/baselines.hpp"
#include "test_support.hpp"
#include <algorithm>
#include <iostream>
#include <limits>

namespace {
mab::SearchResult wrong(const mab::Values&,mab::Key){return std::nullopt;}
mab::SearchResult throwing(const mab::Values&,mab::Key){throw std::runtime_error("deliberate search test exception");}
}
int main(){
    try{
        std::size_t cases=0,trials=0;
        for(const auto size:{0U,1U,2U,31U,64U,257U})for(const auto seed:{0ULL,1729ULL,18446744073709551615ULL})
            for(const auto dist:{mab::Distribution::uniform,mab::Distribution::nearly_sorted,mab::Distribution::reverse_sorted,mab::Distribution::duplicate_heavy}){
                mab::SearchConfig c;c.timing.dataset.size=size;c.timing.dataset.seed=seed;c.timing.dataset.distribution=dist;c.query_seed=seed;c.batch_size=16;c.timing.repetitions=2;
                auto data=mab::make_timing_input(c.timing);std::sort(data.begin(),data.end());const auto original=data;
                const auto batches=mab::make_search_batches(data,c),again=mab::make_search_batches(data,c);
                require(batches.size()==9,"category plan count");
                std::size_t eligible=0;
                for(std::size_t b=0;b<batches.size();++b){
                    const auto& batch=batches[b];require(mab::query_fingerprint(batch.queries)==mab::query_fingerprint(again[b].queries),"query reproducibility");
                    if(!batch.unavailable_reason.empty()){require(batch.queries.empty(),"unavailable queries fabricated");continue;}
                    ++eligible;require(batch.queries.size()==16,"batch size");std::size_t hits=0;
                    for(std::size_t i=0;i<batch.queries.size();++i){const auto& q=batch.queries[i];const auto found=std::find(data.begin(),data.end(),q.target);
                        mab::SearchResult oracle;if(found!=data.end())oracle=static_cast<std::size_t>(found-data.begin());
                        require(q.expected_position==oracle,"query expected answer differs from linear oracle");hits+=oracle.has_value();
                        if(q.selected_position)require(data[*q.selected_position]==q.target && oracle && *oracle<=*q.selected_position,"selected rank/first duplicate semantics");
                        if(batch.category=="mixed_50")require(oracle.has_value()==(i%2==0),"mixed exact ratio/order");
                        if(batch.category=="miss_below")require(q.target<data.front(),"below category");
                        if(batch.category=="miss_above")require(q.target>data.back(),"above category");
                        if(batch.category=="miss_between")require(q.target>data.front() && q.target<data.back() && !oracle,"between category");
                    }
                    if(batch.category=="mixed_50")require(hits==8,"50 percent hit ratio");
                    else require(hits==(batch.category.rfind("hit_",0)==0 ? 16U : 0U),"category hit ratio");
                    auto subset=c;subset.categories={batch.category};const auto alone=mab::make_search_batches(data,subset);
                    require(alone.size()==1 && mab::query_fingerprint(alone[0].queries)==mab::query_fingerprint(batch.queries),"subset changed category RNG");
                }
                const std::vector<mab::Searcher> algorithms(mab::searchers().begin(),mab::searchers().end());
                std::size_t observed=0;
                require(mab::run_search_trials(data,c,batches,algorithms,[&](const mab::SearchTrial& row){
                    require(row.status=="ok" && row.correctness=="passed" && row.elapsed_ns,"valid timed batch");
                    const auto offset=(seed%3+row.trial_index%3)%3;
                    require(row.algorithm==algorithms[(offset+row.execution_order)%3].name,"cyclic schedule");
                    ++observed;
                }),"search engine failed");
                require(observed==eligible*3*3,"warmup/measure count");require(data==original,"input modified");
                trials+=observed;++cases;
            }
        mab::SearchConfig c;c.batch_size=8;c.timing.dataset.size=5;
        const mab::Values duplicates{-2,-2,0,7,7};const auto batches=mab::make_search_batches(duplicates,c);
        require(batches[2].queries[0].selected_position==4 && batches[2].queries[0].expected_position==3,"last target duplicate rank");
        const auto low=std::numeric_limits<mab::Key>::min(),high=std::numeric_limits<mab::Key>::max();
        c.timing.dataset.size=2;const auto extrema=mab::make_search_batches({low,high},c);
        require(!extrema[4].unavailable_reason.empty() && !extrema[6].unavailable_reason.empty(),"unrepresentable range misses");
        require(extrema[5].queries[0].target==-1,"int64 gap midpoint");
        c.timing.dataset.size=3;const auto dense=mab::make_search_batches({-1,0,1},c);require(!dense[5].unavailable_reason.empty(),"dense gap policy");
        bool rejected=false;try{(void)mab::make_search_batches({2,0,1},c);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"unsorted input not rejected");
        rejected=false;try{mab::run_search_trials({2,0,1},c,dense,{{"linear_search",mab::linear_search,false}},[](const auto&){});}catch(const std::invalid_argument&){rejected=true;}require(rejected,"engine accepted unsorted input");
        c.timing.dataset.size=1;c.categories={"hit_first"};c.timing.warmups=0;
        const auto one=mab::make_search_batches({7},c);
        std::vector<mab::SearchTrial> failed;
        require(!mab::run_search_trials({7},c,one,{{"wrong",wrong,false}},[&](const auto& r){failed.push_back(r);}),"wrong result accepted");
        require(failed.size()==1 && failed[0].correctness=="failed" && failed[0].elapsed_ns,"wrong answer failure row");
        failed.clear();require(!mab::run_search_trials({7},c,one,{{"throw",throwing,false}},[&](const auto& r){failed.push_back(r);}),"exception accepted");
        require(failed.size()==1 && failed[0].correctness=="not_checked" && !failed[0].elapsed_ns,"exception failure row");
        auto tampered=one;tampered[0].queries[0].expected_position=std::nullopt;
        rejected=false;try{mab::run_search_trials({7},c,tampered,{{"linear_search",mab::linear_search,false}},[](const auto&){});}catch(const std::invalid_argument&){rejected=true;}require(rejected,"stale oracle not rejected");
        c.categories={"bad"};rejected=false;try{mab::validate_search_config(c);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"invalid category accepted");
        std::cout<<"Passed "<<cases<<" reproducible search/query configurations and "<<trials<<" validated timed batches, category/duplicate/extrema/precondition/failure checks\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
