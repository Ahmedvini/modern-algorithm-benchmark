#pragma once
#include "algorithms/parallel_mergesort.hpp"
#include "benchmark/timing.hpp"
namespace mab {
bool run_parallel_timing_trials(const Values& original,const TimingConfig& config,
    const std::vector<ConfiguredSorter>& sorters,const std::function<void(const TimingTrial&)>& sink);
} // namespace mab
