#pragma once

#include "common/types.hpp"

#include <cstddef>
#include <cstdint>
#include <optional>
#include <string_view>

namespace mab {
enum class Distribution { uniform, nearly_sorted, reverse_sorted, duplicate_heavy };

struct DatasetConfig {
    std::size_t size = 1000;
    std::uint64_t seed = 1729;
    Distribution distribution = Distribution::uniform;
    std::optional<std::size_t> nearly_sorted_swaps;
    std::uint64_t duplicate_cardinality = 16;
};

Distribution parse_distribution(std::string_view name);
std::string_view distribution_name(Distribution distribution);
std::size_t swap_count(const DatasetConfig& config);
Values generate_dataset(const DatasetConfig& config);
}  // namespace mab
