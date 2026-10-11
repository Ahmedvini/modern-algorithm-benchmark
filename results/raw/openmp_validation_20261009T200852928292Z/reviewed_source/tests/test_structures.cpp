#include "structures/btree.hpp"
#include "structures/skip_list.hpp"
#include "datasets/generator.hpp"
#include "test_support.hpp"
#include <algorithm>
#include <iostream>
#include <limits>
#include <map>
#include <random>
#include <type_traits>

static_assert(!std::is_copy_constructible_v<mab::SkipList> && !std::is_move_constructible_v<mab::SkipList>);
static_assert(!std::is_copy_assignable_v<mab::SkipList> && !std::is_move_assignable_v<mab::SkipList>);
static_assert(!std::is_copy_constructible_v<mab::BTree> && !std::is_move_constructible_v<mab::BTree>);
static_assert(!std::is_copy_assignable_v<mab::BTree> && !std::is_move_assignable_v<mab::BTree>);
namespace {
std::size_t cases = 0, checks = 0, inserts = 0, invariants = 0;
void lookup(const mab::OrderedIndex& index, const std::map<mab::Key,std::size_t>& oracle, mab::Key key) {
    const auto found = oracle.find(key);
    const auto actual = index.find(key);
    if (found == oracle.end()) require(!actual,"map oracle absence mismatch");
    else require(actual && *actual == found->second,"map oracle payload mismatch");
    ++checks;
}
void check_case(const mab::Values& keys) {
    for (const auto& factory : mab::index_factories()) {
        auto index = factory.create(42);
        std::map<mab::Key,std::size_t> oracle;
        require(index->size() == 0 && index->validate(),"empty invariants"); ++invariants;
        lookup(*index,oracle,0);
        for (std::size_t i=0;i<keys.size();++i) {
            const auto payload = i%7 == 0 ? std::numeric_limits<std::size_t>::max() : i;
            const bool expected = oracle.emplace(keys[i],payload).second;
            require(index->insert(keys[i],payload) == expected,"insert return mismatch"); ++inserts;
            require(index->size() == oracle.size(),"unique size mismatch");
            lookup(*index,oracle,keys[i]);
            if (keys.size() <= 64 || i%127 == 0) {
                require(index->validate(),"post-insert invariant"); ++invariants;
                if (keys.size() <= 64) for (const auto& entry : oracle) lookup(*index,oracle,entry.first);
            }
        }
        require(index->validate(),"final invariants"); ++invariants;
        for (unsigned repeat=0;repeat<3;++repeat) {
            for (const auto& entry : oracle) lookup(*index,oracle,entry.first);
            for (const auto key : {std::numeric_limits<mab::Key>::min(),std::numeric_limits<mab::Key>::max(),mab::Key{-1},mab::Key{0},mab::Key{1},mab::Key{127}}) lookup(*index,oracle,key);
        }
        for (const auto key : keys) { require(!index->insert(key,0),"duplicate returned new"); lookup(*index,oracle,key); ++inserts; }
        require(index->size() == oracle.size() && index->validate(),"duplicates broke invariants"); ++invariants;
        ++cases;
    }
}
}
int main() {
    try {
        const auto lo = std::numeric_limits<mab::Key>::min(), hi = std::numeric_limits<mab::Key>::max();
        for (const mab::Values& values : std::vector<mab::Values>{{},{0},{lo},{hi},{lo,hi,0,-1,1,lo,hi},{1,0},{0,1},{3,3,3,3},{-9,-1,-5},{lo,lo+1,hi-1,hi}}) check_case(values);
        for (unsigned length=0;length<=6;++length) {
            std::size_t possibilities=1; for (unsigned i=0;i<length;++i) possibilities*=3;
            for (std::size_t word=0;word<possibilities;++word) {
                auto digits=word; mab::Values values(length);
                for (auto& key : values) { key=static_cast<mab::Key>(digits%3)-1; digits/=3; }
                check_case(values);
            }
        }
        for (const auto n : {0U,1U,2U,9U,10U,15U,16U,31U,32U,63U,64U,257U,4096U})
            for (const auto seed : {0ULL,42ULL,1729ULL,18446744073709551615ULL})
                for (const auto d : {mab::Distribution::uniform,mab::Distribution::nearly_sorted,mab::Distribution::reverse_sorted,mab::Distribution::duplicate_heavy}) {
                    mab::DatasetConfig c; c.size=n;c.seed=seed;c.distribution=d;check_case(mab::generate_dataset(c));
                }
        for (const auto n : {10U,64U,1024U,10000U}) {
            mab::Values ascending(n); for (std::size_t i=0;i<n;++i) ascending[i]=static_cast<mab::Key>(i)-static_cast<mab::Key>(n/2);
            check_case(ascending);std::reverse(ascending.begin(),ascending.end());check_case(ascending);
            std::mt19937_64 engine(2718);std::shuffle(ascending.begin(),ascending.end(),engine);check_case(ascending);
            for (auto& key : ascending) key%=13;
            check_case(ascending);
        }
        // Concrete public APIs: promotion/split evidence, duplicate shape and seed isolation.
        mab::SkipList a(1729),b(1729),c(42);
        for (int i=0;i<10000;++i) { require(a.insert(i,0) && b.insert(i,0) && c.insert(i,0),"public insertion");require(!b.insert(i,77),"duplicate public insertion"); }
        require(a.validate() && b.validate() && c.validate(),"public skip invariant");
        require(a.find(0)==0 && a.find(9999)==0,"zero skip payload must be present");
        require(a.levels()>1 && a.levels()<=32,"multiple levels not exercised");
        require(a.shape_fingerprint()==b.shape_fingerprint() && a.shape_fingerprint()!=c.shape_fingerprint(),"seed/duplicate RNG contract");
        std::size_t splits=0;
        for (const auto order : {4U,10U,16U,32U,64U}) {
            mab::BTree tree(order);
            for (int i=0;i<10000;++i) require(tree.insert(i,static_cast<std::size_t>(i)),"public tree insert");
            require(tree.height()>=3 && tree.split_count()>2 && tree.validate(),"multiple root/nonroot splits not exercised");
            require(tree.find(0)==0,"zero tree payload must be present");
            const auto before=tree.split_count();require(!tree.insert(123,999) && tree.find(123)==123 && tree.split_count()==before,"duplicate tree changed");
            splits+=before;
        }
        for (const auto order : {0U,1U,3U,5U,65U,100U}) {
            bool rejected=false;try {mab::BTree invalid(order);} catch (const std::invalid_argument&) {rejected=true;}
            require(rejected,"invalid order accepted");
        }
        bool rejected=false;try {(void)mab::find_index_factory("unknown");} catch(const std::invalid_argument&) {rejected=true;}
        require(rejected,"unknown registry name");
        std::cout<<"Passed "<<cases<<" structure/input cases, "<<inserts<<" differential insertion attempts, "<<checks<<" map-oracle lookups, "<<invariants<<" invariant validations; public fixtures: skip levels="<<a.levels()<<", B-tree splits="<<splits<<"\n";
    } catch (const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
