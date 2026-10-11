#include "benchmark/timing.hpp"
#include "benchmark/detail/timing_impl.hpp"

#include <algorithm>
#include <chrono>
#include <limits>
#include <stdexcept>

namespace mab {
void validate_timing_config(const TimingConfig& config) {
    if (config.repetitions == 0 || config.repetitions > 10000)
        throw std::invalid_argument("repetitions must be in [1, 10000]");
    if (config.warmups > 1000) throw std::invalid_argument("warmups must be in [0, 1000]");
    if (config.memory_limit_mib == 0 || config.memory_limit_mib > 65536)
        throw std::invalid_argument("memory limit must be in [1, 65536] MiB");
    const auto limit = static_cast<std::uint64_t>(config.memory_limit_mib) * 1024 * 1024;
    // Three retained arrays plus allowance for a linear sort workspace.
    if (config.dataset.size > limit / (4 * sizeof(Key)) ||
        config.dataset.size > Values{}.max_size())
        throw std::invalid_argument("size exceeds planned array/workspace memory budget");
    if (config.dataset.duplicate_cardinality == 0 || config.dataset.duplicate_cardinality > (std::uint64_t{1} << 32))
        throw std::invalid_argument("duplicate cardinality must be in [1, 4294967296]");
    (void)distribution_name(config.dataset.distribution);
    // Bound generation work as well as allocation; existing generator API is unchanged.
    if (timing_swaps(config) > 10000000)
        throw std::invalid_argument("benchmark swap request exceeds 10000000");
}

std::string_view timing_distribution(const TimingConfig& config) {
    return config.sorted_input ? "sorted" : distribution_name(config.dataset.distribution);
}

std::size_t timing_swaps(const TimingConfig& config) {
    return config.sorted_input ? 0 : swap_count(config.dataset);
}

Values make_timing_input(const TimingConfig& config) {
    validate_timing_config(config);
    auto dataset = config.dataset;
    if (config.sorted_input) {
        dataset.distribution = Distribution::nearly_sorted;
        dataset.nearly_sorted_swaps = 0;
    }
    return generate_dataset(dataset);
}

std::uint64_t input_fingerprint(const Values& values) noexcept {
    // FNV-1a of low-to-high bytes of uint32 keys, independent of host endian.
    std::uint64_t hash = 14695981039346656037ULL;
    for (const auto key : values) {
        const auto word = static_cast<std::uint32_t>(key);
        for (unsigned int shift = 0; shift < 32; shift += 8) {
            hash ^= (word >> shift) & 255U;
            hash *= 1099511628211ULL;
        }
    }
    return hash;
}

bool run_timing_trials(const Values& original, const TimingConfig& config,
                       const std::vector<Sorter>& sorters,
                       const std::function<void(const TimingTrial&)>& sink) {
    return detail::run_timing_engine(original,config,sorters,sink,
        [](const Sorter& sorter, Values& values) { sorter.sort(values); });
}
} // namespace mab
