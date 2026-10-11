#pragma once
#include "benchmark/timing.hpp"
#include <algorithm>
#include <chrono>
#include <stdexcept>
#include <type_traits>
namespace mab::detail {
template<class Entry, class Invoke>
bool run_timing_engine(const Values& original, const TimingConfig& config,
                       const std::vector<Entry>& sorters,
                       const std::function<void(const TimingTrial&)>& sink, Invoke invoke) {
    validate_timing_config(config);
    if (original.size() != config.dataset.size || sorters.empty() || !sink)
        throw std::invalid_argument("invalid timing input/sorters/sink");
    for (std::size_t i = 0; i < sorters.size(); ++i) {
        if (!sorters[i].sort || sorters[i].name.empty()) throw std::invalid_argument("invalid sorter");
        for (std::size_t j = 0; j < i; ++j)
            if (sorters[i].name == sorters[j].name) throw std::invalid_argument("duplicate sorter");
    }
    auto expected = original;
    std::sort(expected.begin(), expected.end());
    Values working(original.size());
    using Clock = std::chrono::steady_clock;
    static_assert(Clock::is_steady, "timing requires a monotonic clock");
    for (const auto phase : {std::string_view{"warmup"}, std::string_view{"measure"}}) {
        const auto repetitions = phase == "warmup" ? config.warmups : config.repetitions;
        for (std::size_t trial = 0; trial < repetitions; ++trial) {
            const auto offset = (config.dataset.seed % sorters.size() + trial % sorters.size()) % sorters.size();
            for (std::size_t order = 0; order < sorters.size(); ++order) {
                const auto& sorter = sorters[(offset + order) % sorters.size()];
                std::copy(original.begin(), original.end(), working.begin());
                TimingTrial result{sorter.name, phase, trial, order, std::nullopt, "ok", "passed", {}};
                if constexpr (!std::is_void_v<decltype(invoke(sorter,working))>) {
                    result.requested_threads=sorter.threads;
                    result.actual_threads=0; // Unknown if invocation throws.
                }
                try {
                    const auto start = Clock::now();
                    if constexpr (std::is_void_v<decltype(invoke(sorter,working))>) {
                        invoke(sorter,working);
                    } else {
                        const auto info=invoke(sorter,working);
                        const auto stop=Clock::now();
                        const auto elapsed=std::chrono::duration_cast<std::chrono::nanoseconds>(stop-start).count();
                        if (elapsed<0) throw std::runtime_error("negative steady-clock duration");
                        result.elapsed_ns=static_cast<std::uint64_t>(elapsed);
                        result.actual_threads=info.actual_threads;
                        result.parallel_region=info.parallel_region;
                    }
                    if constexpr (std::is_void_v<decltype(invoke(sorter,working))>) {
                        const auto stop = Clock::now();
                        const auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
                        if (elapsed < 0) throw std::runtime_error("negative steady-clock duration");
                        result.elapsed_ns = static_cast<std::uint64_t>(elapsed);
                    }
                } catch (const std::exception& error) {
                    result.status = "error";
                    result.correctness = "not_checked";
                    result.error = error.what();
                } catch (...) {
                    result.status = "error";
                    result.correctness = "not_checked";
                    result.error = "non-standard sorter exception";
                }
                if (result.status == "ok" && working != expected) {
                    result.status = "error";
                    result.correctness = "failed";
                    result.error = "full sorted output differs from std::sort reference";
                }
                sink(result);
                if (result.status != "ok") return false;
            }
        }
    }
    return true;
}
} // namespace mab::detail
