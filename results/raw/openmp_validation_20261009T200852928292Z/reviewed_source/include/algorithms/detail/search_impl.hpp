#pragma once

#include "algorithms/searching.hpp"
#include <functional>

namespace mab::detail {
template <typename Equal = std::equal_to<Key>>
SearchResult linear_search_impl(const Values& values, Key key, Equal equal = {}) {
    for (std::size_t i = 0; i < values.size(); ++i)
        if (equal(values[i], key)) return i;
    return std::nullopt;
}

template <typename Less>
std::size_t lower_bound_index(const Values& values, Key key, std::size_t first,
                             std::size_t last, Less less) {
    while (first < last) {
        const auto middle = first + (last - first) / 2;
        if (less(values[middle], key)) first = middle + 1;
        else last = middle;
    }
    return first;
}

template <typename Less = std::less<Key>, typename Equal = std::equal_to<Key>>
SearchResult binary_search_impl(const Values& values, Key key, Less less = {}, Equal equal = {}) {
    const auto index = lower_bound_index(values, key, 0, values.size(), less);
    if (index < values.size() && equal(values[index], key)) return index;
    return std::nullopt;
}

template <typename Less = std::less<Key>, typename Equal = std::equal_to<Key>>
SearchResult exponential_search_impl(const Values& values, Key key, Less less = {}, Equal equal = {}) {
    if (values.empty()) return std::nullopt;
    if (!less(values[0], key)) return equal(values[0], key) ? SearchResult{0} : std::nullopt;
    std::size_t bound = 1;
    while (bound < values.size() && less(values[bound], key)) {
        // Clamp before doubling; also avoids wraparound for size_t maxima.
        if (bound > (values.size() - 1) / 2) { bound = values.size(); break; }
        bound *= 2;
    }
    const auto end = bound < values.size() ? bound + 1 : values.size();
    const auto index = lower_bound_index(values, key, bound / 2, end, less);
    if (index < values.size() && equal(values[index], key)) return index;
    return std::nullopt;
}
}  // namespace mab::detail
