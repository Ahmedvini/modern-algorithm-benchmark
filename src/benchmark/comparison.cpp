#include "benchmark/comparison.hpp"
#include <algorithm>
#include <chrono>
#include <climits>
#include <istream>
#include <limits>
#include <ostream>
#include <set>
#include <stdexcept>

namespace mab {
static_assert(CHAR_BIT == 8 && sizeof(Key) == 4, "canonical input bytes require int32 and 8-bit bytes");
Values make_comparison_input(const TimingConfig& config, std::string_view distribution) {
    if (config.dataset.size > 1000000) throw std::invalid_argument("comparison size exceeds 1M");
    if (distribution != "signed_edges") {
        auto effective = config;
        effective.sorted_input = distribution == "sorted";
        if (!effective.sorted_input) effective.dataset.distribution = parse_distribution(distribution);
        return make_timing_input(effective);
    }
    validate_timing_config(config);
    Values result(config.dataset.size);
    constexpr Key lo = std::numeric_limits<Key>::min(), hi = std::numeric_limits<Key>::max();
    constexpr Key pattern[]{lo, hi, -1, 0, 1, lo + 1, hi - 1, 0};
    for (std::size_t i = 0; i < result.size(); ++i) result[i] = pattern[i % 8];
    return result;
}
void write_comparison_input(const Values& values, std::ostream& output) {
    for (const auto key : values) {
        const auto word = static_cast<std::uint32_t>(key);
        for (unsigned shift = 0; shift < 32; shift += 8)
            output.put(static_cast<char>((word >> shift) & 255U));
    }
    if (!output) throw std::runtime_error("input-file write failed");
}
Values read_comparison_input(std::size_t size, std::istream& input) {
    if (size > 1000000) throw std::invalid_argument("comparison size exceeds 1M");
    Values result(size);
    for (auto& key : result) {
        std::uint32_t word = 0;
        for (unsigned shift = 0; shift < 32; shift += 8) {
            const int byte = input.get();
            if (byte == std::char_traits<char>::eof()) throw std::runtime_error("truncated input file");
            word |= static_cast<std::uint32_t>(static_cast<unsigned char>(byte)) << shift;
        }
        // Conversion through int64 avoids implementation-defined unsigned->signed overflow.
        const auto value = word < (std::uint32_t{1} << 31) ? static_cast<std::int64_t>(word)
            : static_cast<std::int64_t>(word) - (std::int64_t{1} << 32);
        key = static_cast<Key>(value);
    }
    if (input.get() != std::char_traits<char>::eof()) throw std::runtime_error("extra input bytes");
    if (input.bad()) throw std::runtime_error("input-file read failed");
    return result;
}
bool run_comparison_trials(const Values& original, const Values& oracle, Values& working,
    const std::array<ComparisonBackend, 5>& modes, const std::function<void()>& synchronize,
    const std::function<void(const ComparisonTrial&)>& attempt,
    const std::function<void(const ComparisonTrial&)>& sink) {
    using Clock = std::chrono::steady_clock;
    static_assert(Clock::is_steady, "monotonic comparison timer required");
    if (original.size() != oracle.size() || working.size() != original.size() ||
        &original == &working || &oracle == &working)
        throw std::invalid_argument("invalid comparison buffers");
    std::set<std::string> names;
    for (const auto& mode : modes) {
        if (!names.insert(mode.id).second ||
            (static_cast<int>(mode.sort != nullptr) + static_cast<int>(mode.parallel != nullptr) +
             static_cast<int>(static_cast<bool>(mode.prepared))) != 1)
            throw std::invalid_argument("duplicate or ambiguous comparison backend");
    }
    std::size_t order = 0;
    for (const std::string phase : {"warmup", "measure"}) {
        for (std::size_t round = 0; round < (phase == "warmup" ? 1U : 5U); ++round) {
            for (std::size_t position = 0; position < modes.size(); ++position) {
                const auto& mode = modes[(position + round) % modes.size()];
                ComparisonTrial trial;
                trial.backend = mode.id; trial.phase = phase; trial.trial_index = round;
                trial.execution_order = order++; trial.prepared = static_cast<bool>(mode.prepared);
                attempt(trial); // Durable attempt record before any operation that may fail.
                try {
                    std::copy(original.begin(), original.end(), working.begin());
                    synchronize();
                    if (mode.prepared) trial.diagnostics = mode.prepared(original, working);
                    else {
                        Clock::time_point start, stop;
                        if (mode.parallel) {
                            start = Clock::now();
                            trial.parallel_info = mode.parallel(working, 2);
                            stop = Clock::now();
                        } else {
                            start = Clock::now();
                            mode.sort(working);
                            stop = Clock::now();
                        }
                        const auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
                        if (elapsed < 0) throw std::runtime_error("negative comparison duration");
                        trial.elapsed_ns = static_cast<std::uint64_t>(elapsed);
                    }
                    if (working != oracle) {
                        trial.correctness = "failed";
                        throw std::runtime_error("output differs from std::sort oracle");
                    }
                    if (mode.parallel && (trial.parallel_info.actual_threads !=
                        (original.size() < parallel_merge_threshold ? 1 : 2) ||
                        trial.parallel_info.parallel_region != (original.size() >= parallel_merge_threshold)))
                        throw std::runtime_error("unexpected actual OpenMP team/region");
                } catch (const std::exception& error) {
                    trial.status = "error"; trial.error = error.what(); trial.elapsed_ns.reset();
                    if (trial.correctness != "failed") trial.correctness = "not_checked";
                }
                sink(trial);
                if (trial.status != "ok") return false;
            }
        }
    }
    return true;
}
} // namespace mab
