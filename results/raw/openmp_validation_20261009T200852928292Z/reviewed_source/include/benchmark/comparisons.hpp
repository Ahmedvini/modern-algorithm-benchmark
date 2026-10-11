#pragma once

#include "common/types.hpp"

#include <array>
#include <cstdint>
#include <string_view>

namespace mab {
struct CountedSorter {
    std::string_view name;
    std::string_view implementation;
    std::uint64_t (*sort)(Values&);
};

// Each call starts at zero; only sorting key less-than evaluations are counted.
// Keep these functions separate from normal sorting/timing paths.
const std::array<CountedSorter, 5>& counted_sorters() noexcept;
// radix_sort is registered for normal sorting but has no key predicate metric.
const CountedSorter& find_counted_sorter(std::string_view name);
}  // namespace mab
