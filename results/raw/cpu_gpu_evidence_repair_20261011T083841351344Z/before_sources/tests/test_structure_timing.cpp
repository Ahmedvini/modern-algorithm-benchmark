#include "benchmark/structure_timing.hpp"
#include "test_support.hpp"
#include <algorithm>
#include <iostream>
#include <limits>
#include <map>

namespace {
std::unique_ptr<mab::OrderedIndex> throwing(std::uint64_t) {throw std::runtime_error("deliberate factory failure");}
class WrongAbsent final : public mab::OrderedIndex {
    std::map<mab::Key,std::size_t> data;
public:
    bool insert(mab::Key key,std::size_t value) override {return data.emplace(key,value).second;}
    std::optional<std::size_t> find(mab::Key key) const noexcept override {
        const auto found=data.find(key);return found==data.end() ? 0 : found->second;
    }
    std::size_t size() const noexcept override {return data.size();}
    bool validate() const override {return true;}
};
std::unique_ptr<mab::OrderedIndex> wrong(std::uint64_t) {return std::make_unique<WrongAbsent>();}
class BrokenBuild final : public mab::OrderedIndex {
public:
    bool insert(mab::Key,std::size_t) override {return false;}
    std::optional<std::size_t> find(mab::Key) const noexcept override {return std::nullopt;}
    std::size_t size() const noexcept override {return 0;}
    bool validate() const override {return true;}
};
std::unique_ptr<mab::OrderedIndex> broken(std::uint64_t) {return std::make_unique<BrokenBuild>();}
std::unique_ptr<mab::OrderedIndex> null_factory(std::uint64_t) {return {};}
}
int main() {
    try {
        std::size_t cases=0,rows=0;
        for (const auto size : {0U,1U,2U,31U,64U,257U}) for (const auto seed : {0ULL,1729ULL,18446744073709551615ULL})
            for (const auto dist : {mab::Distribution::uniform,mab::Distribution::nearly_sorted,mab::Distribution::reverse_sorted,mab::Distribution::duplicate_heavy}) {
                mab::StructureConfig config;config.search.batch_size=16;config.search.timing.repetitions=2;
                config.search.timing.dataset.size=size;config.search.timing.dataset.seed=seed;
                config.search.timing.dataset.distribution=dist;config.structure_seed=seed;
                const auto original=mab::make_timing_input(config.search.timing);
                const auto w=mab::make_structure_workload(original,config);
                const auto again=mab::make_structure_workload(original,config);
                require(w.original==original && w.sorted==again.sorted,"input/reproduction");
                for (const auto& e : w.entries) {
                    const auto found=std::find(w.sorted.begin(),w.sorted.end(),e.key);
                    require(e.value==static_cast<std::size_t>(found-w.sorted.begin()),"first payload linear oracle");
                }
                std::size_t available=0;
                for (std::size_t b=0;b<w.batches.size();++b) {
                    require(mab::query_fingerprint(w.batches[b].queries)==mab::query_fingerprint(again.batches[b].queries),"same query plan");
                    available+=w.batches[b].unavailable_reason.empty();
                }
                std::size_t observed=0;
                require(mab::run_structure_trials(w,config,{mab::index_factories().begin(),mab::index_factories().end()},[&](const auto& row) {
                    require(row.status=="ok" && row.correctness=="passed" && row.elapsed_ns,"timing correctness");
                    require(row.algorithm==mab::index_factories()[(seed%5+row.trial_index%5+row.execution_order)%5].name,"schedule");
                    require((row.operation=="build")==row.category.empty(),"separate operation rows");++observed;
                }),"structure engine failed");
                require(observed==(available+1)*5*3,"planned trial count");require(w.original==original,"input mutated");rows+=observed;++cases;
            }
        mab::StructureConfig c;c.search.timing.dataset.size=5;c.search.batch_size=8;c.search.timing.warmups=0;c.search.categories={"miss_above"};
        auto w=mab::make_structure_workload({7,-2,7,0,-2},c);
        require(w.entries[0].value==3 && w.entries[2].value==3 && w.unique_keys==3,"unsorted insertion rank mapping");
        std::vector<mab::StructureTrial> failed;
        require(!mab::run_structure_trials(w,c,{{"throw",throwing}},[&](const auto& row){failed.push_back(row);}),"factory exception accepted");
        require(failed.size()==1 && failed[0].operation=="build" && failed[0].correctness=="not_checked" && !failed[0].elapsed_ns,"exception row");
        failed.clear();require(!mab::run_structure_trials(w,c,{{"broken",broken}},[&](const auto& row){failed.push_back(row);}),"broken build accepted");
        require(failed.size()==1 && failed[0].correctness=="failed" && failed[0].elapsed_ns,"build validation failure row");
        failed.clear();require(!mab::run_structure_trials(w,c,{{"null",null_factory}},[&](const auto& row){failed.push_back(row);}),"null factory accepted");
        require(failed.size()==1 && failed[0].correctness=="not_checked" && !failed[0].elapsed_ns,"null factory failure row");
        failed.clear();require(!mab::run_structure_trials(w,c,{{"wrong",wrong}},[&](const auto& row){failed.push_back(row);}),"wrong miss accepted");
        require(failed.size()==2 && failed[0].status=="ok" && failed[1].operation=="lookup" && failed[1].correctness=="failed" && failed[1].elapsed_ns,"wrong lookup row");
        auto tampered=w;tampered.entries[0].value=0;
        bool rejected=false;try {mab::run_structure_trials(tampered,c,{mab::index_factories()[0]},[](const auto&){});} catch (const std::invalid_argument&) {rejected=true;}
        require(rejected,"tampered rank accepted");
        tampered=w;tampered.batches[0].queries[0].target=0;
        rejected=false;try {mab::run_structure_trials(tampered,c,{mab::index_factories()[0]},[](const auto&){});} catch (const std::invalid_argument&) {rejected=true;}
        require(rejected,"tampered query accepted");
        c.search.timing.dataset.size=3;c.search.categories={};
        const auto lo=std::numeric_limits<mab::Key>::min(),hi=std::numeric_limits<mab::Key>::max();
        const auto edge=mab::make_structure_workload({hi,lo,hi},c);
        require(mab::run_structure_trials(edge,c,{mab::index_factories().begin(),mab::index_factories().end()},[](const auto& r){require(r.status=="ok","extrema trial");}),"extrema failed");
        c.search.timing.dataset.size=1000000;c.search.timing.memory_limit_mib=1;
        rejected=false;try {mab::validate_structure_config(c);} catch(const std::invalid_argument&) {rejected=true;}
        require(rejected,"resource planning bound");
        std::cout<<"Passed "<<cases<<" reproducible structure workloads and "<<rows<<" validated build/lookup rows, rank/query tamper, failure, extrema and resource checks\n";
    } catch (const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
