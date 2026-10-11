#include "benchmark/comparisons.hpp"
#include "benchmark/detail/counting_less.hpp"
#include "algorithms/detail/quicksort_impl.hpp"
#include "algorithms/detail/mergesort_impl.hpp"

#include "pdqsort.h"

// Upstream audits compare keys after sorting; those are not algorithm work.
#ifdef GFX_TIMSORT_ENABLE_AUDIT
#error "Comparison counting requires Timsort audits to be disabled"
#endif
#include "gfx/timsort.hpp"

#include <algorithm>
#include <functional>
#include <stdexcept>
#include <string>
#include <type_traits>

namespace mab {
namespace {
std::uint64_t counted_std_sort(Values& values) {
    std::uint64_t count = 0;
    std::sort(values.begin(), values.end(), detail::CountingLess(count));
    return count;
}

std::uint64_t counted_quick_sort(Values& values) {
    std::uint64_t count = 0;
    detail::NoQuickSortObserver observer;
    detail::quick_sort_with_depth(values, detail::quick_sort_depth_budget(values.size()),
                                  observer, detail::CountingLess(count));
    return count;
}

std::uint64_t counted_pdq_sort(Values& values) {
    // A custom comparator bypasses upstream's std::less trait. Explicitly use
    // its public branchless entry point to preserve production's int32 policy.
    static_assert(pdqsort_detail::is_default_compare<std::less<Key>>::value &&
                  std::is_arithmetic<Key>::value, "production PDQSort policy changed");
    std::uint64_t count = 0;
    ::pdqsort_branchless(values.begin(), values.end(), detail::CountingLess(count));
    return count;
}

std::uint64_t counted_tim_sort(Values& values) {
    std::uint64_t count = 0;
    gfx::timsort(values.begin(), values.end(), detail::CountingLess(count));
    return count;
}

std::uint64_t counted_merge_sort(Values& values) {
    std::uint64_t count = 0;
    detail::merge_sort_impl(values, detail::CountingLess(count));
    return count;
}
}  // namespace

const std::array<CountedSorter, 5>& counted_sorters() noexcept {
    static const std::array<CountedSorter, 5> registry{{
        {"std_sort", "std_sort_counting_less", counted_std_sort},
        {"quick_sort", "project_quick_sort_counting_less", counted_quick_sort},
        {"pdq_sort", "upstream_pdqsort_branchless_counting_less", counted_pdq_sort},
        {"tim_sort", "upstream_gfx_timsort_counting_less", counted_tim_sort},
        {"merge_sort", "project_merge_sort_counting_less", counted_merge_sort}}};
    return registry;
}

const CountedSorter& find_counted_sorter(std::string_view name) {
    if (name == "radix_sort")
        throw std::invalid_argument("comparison counting unsupported for sorter: radix_sort (no key comparisons)");
    for (const auto& sorter : counted_sorters())
        if (sorter.name == name) return sorter;
    throw std::invalid_argument("unknown counted sorter: " + std::string(name));
}
}  // namespace mab
