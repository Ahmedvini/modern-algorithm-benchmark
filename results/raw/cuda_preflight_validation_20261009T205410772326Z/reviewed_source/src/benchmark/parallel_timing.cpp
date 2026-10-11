#include "benchmark/parallel_timing.hpp"
#include "benchmark/detail/timing_impl.hpp"
namespace mab {
bool run_parallel_timing_trials(const Values& original,const TimingConfig& config,
    const std::vector<ConfiguredSorter>& sorters,const std::function<void(const TimingTrial&)>& sink) {
    for (const auto& sorter:sorters)
        if(sorter.threads<1 || sorter.threads>64) throw std::invalid_argument("threads must be in [1,64]");
    return detail::run_timing_engine(original,config,sorters,sink,
        [](const ConfiguredSorter& sorter,Values& values) { return sorter.sort(values,sorter.threads); });
}
} // namespace mab
