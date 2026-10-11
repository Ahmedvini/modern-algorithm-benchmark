#pragma once

#include "algorithms/sorting.hpp"
#include "datasets/generator.hpp"

#include <cstdint>
#include <functional>
#include <optional>
#include <string>
#include <vector>

namespace mab {
struct TimingConfig {
    DatasetConfig dataset;
    bool sorted_input = false;
    std::size_t repetitions = 5;
    std::size_t warmups = 1;
    std::size_t memory_limit_mib = 256;
};

void validate_timing_config(const TimingConfig& config);
Values make_timing_input(const TimingConfig& config);
std::string_view timing_distribution(const TimingConfig& config);
std::size_t timing_swaps(const TimingConfig& config);
std::uint64_t input_fingerprint(const Values& values) noexcept;

struct TimingTrial {
    std::string_view algorithm;
    std::string_view phase;
    std::size_t trial_index;
    std::size_t execution_order;
    std::optional<std::uint64_t> elapsed_ns;
    std::string_view status;
    std::string_view correctness;
    std::string error;
    int requested_threads = 1;
    int actual_threads = 1;
    bool parallel_region = false;
};

// Sink and input restore/verification are outside the timed call. False means
// the first sort failed; its row was emitted and remaining trials were not run.
bool run_timing_trials(const Values& original, const TimingConfig& config,
                       const std::vector<Sorter>& sorters,
                       const std::function<void(const TimingTrial&)>& sink);
}  // namespace mab
