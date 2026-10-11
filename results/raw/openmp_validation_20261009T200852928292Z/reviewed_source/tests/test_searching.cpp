#include "algorithms/searching.hpp"
#include "algorithms/baselines.hpp"
#include "benchmark/search_comparisons.hpp"
#include "datasets/generator.hpp"
#include "test_support.hpp"
#include <algorithm>
#include <iostream>
#include <limits>
#include <random>

int main() {
    try {
        std::size_t inputs = 0, checks = 0;
        const mab::Key low = std::numeric_limits<mab::Key>::min(), high = std::numeric_limits<mab::Key>::max();
        const auto check = [&](mab::Values values) {
            const auto before = values;
            for (const auto key : {low, low + 1, -2, -1, 0, 1, 2, high - 1, high}) {
                const auto found = std::find(values.begin(), values.end(), key);
                mab::SearchResult expected;
                if (found != values.end()) expected = static_cast<std::size_t>(found - values.begin());
                require(mab::linear_search(values, key) == expected, "unsorted linear oracle");
            }
            require(values == before, "linear changed input");
            std::sort(values.begin(), values.end());
            mab::Values targets{low, low + 1, -2, -1, 0, 1, 2, high - 1, high};
            if (!values.empty()) {
                targets.push_back(values.front()); targets.push_back(values[values.size()/2]); targets.push_back(values.back());
                for (std::size_t i = 0; i < 16; ++i) targets.push_back(values[i * (values.size()-1) / 16]);
            }
            for (const auto key : targets) {
                const auto found = std::find(values.begin(), values.end(), key);
                mab::SearchResult expected;
                if (found != values.end()) expected = static_cast<std::size_t>(found - values.begin());
                require(mab::std_lower_bound_search(values, key) == expected, "reference oracle mismatch");
                for (const auto& searcher : mab::searchers()) {
                    const auto public_fn = searcher.name == "linear_search" ? mab::linear_search :
                        searcher.name == "binary_search" ? mab::binary_search : mab::exponential_search;
                    require(public_fn(values, key) == expected, "public search mismatch");
                    require(mab::find_searcher(searcher.name).search(values, key) == expected, "registry mismatch");
                    const auto counted = mab::counted_search(searcher.name, values, key);
                    require(counted.position == expected, "counted mismatch");
                    (void)mab::counted_search(searcher.name, {}, 17);
                    require(mab::counted_search(searcher.name, values, key).key_comparisons == counted.key_comparisons,
                            "counter reset/isolation/repetition mismatch");
                    ++checks;
                }
            }
            ++inputs;
        };
        for (const auto& values : std::vector<mab::Values>{{}, {0}, {low}, {high}, {2,1}, {1,2},
             {low,low+1,-1,0,0,1,high-1,high}, {-8,-2,1,7}, {4,4,4,4}, {7,-1,0,7,-2}}) check(values);
        for (std::size_t size=0;size<=7;++size) {
            std::size_t total=1;for(std::size_t i=0;i<size;++i)total*=3;
            for(std::size_t word=0;word<total;++word){auto code=word;mab::Values v(size);for(auto& k:v){k=static_cast<mab::Key>(code%3)-1;code/=3;}check(v);}
        }
        for (const auto size : {0U,1U,2U,3U,4U,7U,8U,9U,15U,16U,17U,31U,32U,33U,63U,64U,65U,127U,128U,129U,257U,1024U,4096U}) {
            mab::Values spaced(size);for(std::size_t i=0;i<size;++i)spaced[i]=static_cast<mab::Key>(i*2)-4096;
            check(spaced); std::reverse(spaced.begin(),spaced.end());check(spaced);
            for(const auto seed : {0ULL,42ULL,1729ULL,18446744073709551615ULL})
                for(const auto distribution : {mab::Distribution::uniform,mab::Distribution::nearly_sorted,mab::Distribution::reverse_sorted,mab::Distribution::duplicate_heavy}) {
                    mab::DatasetConfig config;config.size=size;config.seed=seed;config.distribution=distribution;check(mab::generate_dataset(config));
                }
        }
        require(mab::counted_search("linear_search", {-2,0,0,7}, 0).key_comparisons==2, "linear exact count");
        require(mab::counted_search("binary_search", {-2,0,0,7}, 0).key_comparisons==4, "binary exact count");
        require(mab::counted_search("exponential_search", {-2,0,0,7}, 0).key_comparisons==5, "exponential exact count");
        for(const auto& s:mab::searchers())require(mab::counted_search(s.name, {}, 0).key_comparisons==0,"empty exact count");
        bool rejected=false;try{(void)mab::find_searcher("bad");}catch(const std::invalid_argument&){rejected=true;}
        require(rejected,"unknown registry name");
        std::cout << "Passed " << inputs << " search inputs and " << checks << " public/registry/counting oracle checks, exact predicates and reset/isolation tests\n";
    } catch (const std::exception& error) { std::cerr<<error.what()<<'\n';return 1; }
}
