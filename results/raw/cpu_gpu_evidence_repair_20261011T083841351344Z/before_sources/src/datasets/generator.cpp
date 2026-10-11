#include "datasets/generator.hpp"

#include <algorithm>
#include <functional>
#include <random>
#include <stdexcept>
#include <string>

namespace mab {
namespace {
// Explicit rejection mapping avoids library-dependent uniform distributions.
std::uint64_t bounded(std::mt19937_64& engine, std::uint64_t bound) {
    const std::uint64_t threshold = (std::uint64_t{0} - bound) % bound;
    std::uint64_t word;
    do {
        word = engine();
    } while (word < threshold);
    return word % bound;
}
}  // namespace

Distribution parse_distribution(std::string_view name) {
    if (name == "uniform") return Distribution::uniform;
    if (name == "nearly_sorted") return Distribution::nearly_sorted;
    if (name == "reverse_sorted") return Distribution::reverse_sorted;
    if (name == "duplicate_heavy") return Distribution::duplicate_heavy;
    throw std::invalid_argument("unknown distribution: " + std::string(name));
}

std::string_view distribution_name(Distribution distribution) {
    switch (distribution) {
        case Distribution::uniform: return "uniform";
        case Distribution::nearly_sorted: return "nearly_sorted";
        case Distribution::reverse_sorted: return "reverse_sorted";
        case Distribution::duplicate_heavy: return "duplicate_heavy";
    }
    throw std::invalid_argument("invalid distribution enum");
}

std::size_t swap_count(const DatasetConfig& config) {
    return config.nearly_sorted_swaps.value_or(config.size / 100);
}

Values generate_dataset(const DatasetConfig& config) {
    (void)distribution_name(config.distribution);  // Validate before allocation.
    constexpr auto key_domain = std::uint64_t{1} << 32;
    if (config.duplicate_cardinality == 0 || config.duplicate_cardinality > key_domain) {
        throw std::invalid_argument("duplicate cardinality must be in [1, 4294967296]");
    }
    std::mt19937_64 engine(config.seed);
    Values values(config.size);
    for (auto& key : values) {
        if (config.distribution == Distribution::duplicate_heavy) {
            const auto word = bounded(engine, config.duplicate_cardinality);
            key = static_cast<Key>(static_cast<std::int64_t>(word) -
                                   static_cast<std::int64_t>(config.duplicate_cardinality / 2));
        } else {
            const auto word = static_cast<std::uint32_t>(engine());
            key = static_cast<Key>(static_cast<std::int64_t>(word) - (std::int64_t{1} << 31));
        }
    }
    if (config.distribution == Distribution::reverse_sorted) {
        std::sort(values.begin(), values.end(), std::greater<Key>{});
    } else if (config.distribution == Distribution::nearly_sorted) {
        std::sort(values.begin(), values.end());
        if (values.size() > 1) {
            for (std::size_t i = 0; i < swap_count(config); ++i) {
                const auto first = static_cast<std::size_t>(bounded(engine, values.size()));
                const auto second = static_cast<std::size_t>(bounded(engine, values.size()));
                std::swap(values[first], values[second]);
            }
        }
    }
    return values;
}
}  // namespace mab
