#pragma once

#include "common/types.hpp"

#include <algorithm>
#include <cstddef>
#include <functional>
#include <utility>

namespace mab::detail {
// Internal observer interface is instantiated only by correctness tests.
// The production instantiation has no counters or runtime observer branches.
struct NoQuickSortObserver {
    void on_partition() const noexcept {}
    void on_heap_fallback(std::size_t) const noexcept {}
    void on_stack_depth(std::size_t) const noexcept {}
};

inline std::size_t quick_sort_depth_budget(std::size_t size) noexcept {
    std::size_t logarithm = 0;
    while (size > 1) {
        size >>= 1;
        ++logarithm;
    }
    return 2 * logarithm;
}

template <typename Compare>
Key median_of_three(Key first, Key middle, Key last, Compare compare) {
    if (compare(first, middle)) {
        if (compare(middle, last)) return middle;
        return compare(first, last) ? last : first;
    }
    if (compare(first, last)) return first;
    return compare(middle, last) ? last : middle;
}

inline Key median_of_three(Key first, Key middle, Key last) noexcept {
    return median_of_three(first, middle, last, std::less<Key>{});
}

template <typename Observer, typename Compare = std::less<Key>>
void quick_sort_range(Values& values, std::size_t begin, std::size_t end,
                      std::size_t budget, Observer& observer, std::size_t stack_depth,
                      Compare compare = {}) {
    observer.on_stack_depth(stack_depth);
    // All ranges are half-open; empty/singleton ranges need no work.
    while (end - begin > 1) {
        if (budget == 0) {
            observer.on_heap_fallback(end - begin);
            const auto first = values.begin() + static_cast<Values::difference_type>(begin);
            const auto last = values.begin() + static_cast<Values::difference_type>(end);
            std::make_heap(first, last, compare);
            std::sort_heap(first, last, compare);
            return;
        }
        --budget;
        observer.on_partition();
        const Key pivot = median_of_three(values[begin], values[begin + (end - begin) / 2],
                                          values[end - 1], compare);
        // [begin,lower) < pivot, [lower,current) == pivot,
        // [current,upper) unclassified, [upper,end) > pivot.
        auto lower = begin;
        auto current = begin;
        auto upper = end;
        while (current < upper) {
            if (compare(values[current], pivot)) {
                std::swap(values[lower], values[current]);
                ++lower;
                ++current;
            } else if (compare(pivot, values[current])) {
                --upper;  // current < upper before decrement prevents underflow.
                std::swap(values[current], values[upper]);
            } else {
                ++current;
            }
        }
        // The pivot is a copied input key, so its equal group is nonempty.
        // Recurse into the smaller strict partition; iterate over the larger.
        if (lower - begin < end - upper) {
            if (lower - begin > 1) {
                quick_sort_range(values, begin, lower, budget, observer, stack_depth + 1, compare);
            }
            begin = upper;
        } else {
            if (end - upper > 1) {
                quick_sort_range(values, upper, end, budget, observer, stack_depth + 1, compare);
            }
            end = lower;
        }
    }
}

// Internal seam for observed tests and a separately counted comparator.
// Normal callers use std::less<Key> with no counter or runtime selection.
template <typename Observer, typename Compare = std::less<Key>>
void quick_sort_with_depth(Values& values, std::size_t budget, Observer& observer,
                           Compare compare = {}) {
    quick_sort_range(values, 0, values.size(), budget, observer, 1, compare);
}
}  // namespace mab::detail
