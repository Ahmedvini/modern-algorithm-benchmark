#include "benchmark/comparison.hpp"
#include <algorithm>
#include <iostream>
#include <random>
#include <sstream>
#include <stdexcept>

namespace {
void require(bool v) { if(!v) throw std::runtime_error("comparison test assertion failed"); }
void normal(mab::Values& v) { std::sort(v.begin(),v.end()); }
void broken(mab::Values&) { throw std::runtime_error("injected fixture failure"); }
}
int main() {
    try {
        std::size_t inputs=0,checks=0;
        for(const auto n:{0U,1U,2U,7U,31U,1025U,32767U,32768U,32769U,65537U}) {
            for(const auto d:{"uniform","sorted","reverse_sorted","duplicate_heavy","nearly_sorted","signed_edges"}) {
                mab::TimingConfig c;c.dataset.size=n;c.dataset.seed=1729;c.dataset.nearly_sorted_swaps=n/100;
                const auto original=mab::make_comparison_input(c,d);
                require(original==mab::make_comparison_input(c,d));
                std::ostringstream bytes(std::ios::binary);mab::write_comparison_input(original,bytes);
                std::istringstream in(bytes.str(),std::ios::binary);require(original==mab::read_comparison_input(n,in));
                auto oracle=original;normal(oracle);mab::Values working(n);
                // Explicit test doubles for scheduler plumbing; these are not GPU results.
                std::array<mab::ComparisonBackend,5> modes{{{"fixture_a",normal,nullptr,{}},
                    {"fixture_b",normal,nullptr,{}},{"fixture_c",normal,nullptr,{}},{"fixture_d",normal,nullptr,{}},
                    {"fixture_diagnostic",nullptr,nullptr,[](const mab::Values& input,mab::Values& out){out=input;normal(out);return mab::CudaTimingSample{};}}}};
#ifdef MAB_TEST_COMPARISON_OPENMP
                modes[2]={"actual_parallel",nullptr,mab::parallel_merge_sort,{}};
#endif
                std::size_t attempts=0,rows=0,syncs=0;
                for(int repeat=0;repeat<2;++repeat) {
                    require(mab::run_comparison_trials(original,oracle,working,modes,[&]{++syncs;},
                        [&](const mab::ComparisonTrial& t){require(t.execution_order==attempts%30);++attempts;},
                        [&](const mab::ComparisonTrial& t){require(t.status=="ok" && t.correctness=="passed");
                            require(t.execution_order==rows%30);const auto round=t.phase=="warmup"?0:t.trial_index;
                            require(t.backend==modes[((t.execution_order%5)+round)%5].id);++rows;++checks;}));
                }
                require(rows==60 && attempts==60 && syncs==60);++inputs;
            }
        }
        const mab::Values original{2,1},oracle{1,2};mab::Values working(2);
        std::array<mab::ComparisonBackend,5> modes;
        for(std::size_t i=0;i<5;++i)modes[i]={std::to_string(i),normal,nullptr,{}};
        modes[0].sort=broken;std::size_t rows=0;
        require(!mab::run_comparison_trials(original,oracle,working,modes,[]{},[](const auto&){},[&](const auto& t){
            ++rows;require(t.status=="error" && !t.elapsed_ns && t.correctness=="not_checked");}));
        require(rows==1);
        for(const auto& text:{std::string("\0",1),std::string(9,'\0')}) {
            bool rejected=false;try {std::istringstream in(text);(void)mab::read_comparison_input(2,in);}catch(const std::exception&){rejected=true;}
            require(rejected);
        }
        std::cout<<"Passed "<<inputs<<" inputs, "<<checks<<" trial checks, repeated isolation, portable input I/O and failure fixtures\n";
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
