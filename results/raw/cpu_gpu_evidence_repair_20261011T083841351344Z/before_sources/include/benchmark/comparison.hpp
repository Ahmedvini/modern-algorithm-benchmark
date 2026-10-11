#pragma once
#include "algorithms/parallel_mergesort.hpp"
#include "benchmark/cuda_timing.hpp"
#include "benchmark/timing.hpp"
#include <array>
#include <functional>
#include <iosfwd>
#include <optional>

namespace mab {
// Comparison-only input helper; existing generator and CLIs are unchanged.
Values make_comparison_input(const TimingConfig& config, std::string_view distribution);
void write_comparison_input(const Values& values, std::ostream& output);
Values read_comparison_input(std::size_t size, std::istream& input);
struct ComparisonBackend {
    std::string id;
    void (*sort)(Values&) = nullptr;
    ParallelSortInfo (*parallel)(Values&, int) = nullptr;
    std::function<CudaTimingSample(const Values&, Values&)> prepared;
};
struct ComparisonTrial {
    std::string backend, phase, status = "ok", correctness = "passed", error;
    std::size_t trial_index = 0, execution_order = 0;
    std::optional<std::uint64_t> elapsed_ns;
    CudaTimingSample diagnostics;
    ParallelSortInfo parallel_info;
    bool prepared = false;
};
// Exactly W1/R5, five modes and cyclic rotation of the supplied frozen base order.
// Synchronization, attempts, restoration, validation and sinks are outside timers.
// Failure emits its row, stops immediately and leaves remaining trials missing.
bool run_comparison_trials(const Values& original, const Values& oracle, Values& working,
    const std::array<ComparisonBackend, 5>& base_order,
    const std::function<void()>& synchronize,
    const std::function<void(const ComparisonTrial&)>& attempt,
    const std::function<void(const ComparisonTrial&)>& sink);
} // namespace mab
