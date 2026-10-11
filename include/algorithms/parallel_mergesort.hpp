#pragma once
#include "common/types.hpp"
#include <array>
#include <string_view>

namespace mab {
inline constexpr std::size_t parallel_merge_threshold = 32768;
inline constexpr std::size_t parallel_merge_grain = 16384;
inline constexpr std::string_view parallel_merge_version = "parallel_merge_sort_v1";
struct ParallelSortInfo {
    int actual_threads = 1; // Team size, not count of workers that executed tasks.
    bool parallel_region = false;
};
// Stable int32 sort. Requests [1,64], no invocation from an OpenMP region.
// Buffer allocation precedes mutation; task bodies do not throw or allocate.
ParallelSortInfo parallel_merge_sort(Values& values, int requested_threads);
struct ConfiguredSorter {
    std::string_view name;
    ParallelSortInfo (*sort)(Values&, int);
    int threads;
};
const std::array<ConfiguredSorter, 2>& parallel_sorters() noexcept;
ConfiguredSorter find_parallel_sorter(std::string_view name, int threads);
} // namespace mab
