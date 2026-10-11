#pragma once

#include "common/types.hpp"

#include <algorithm>
#include <functional>
#include <utility>

namespace mab::detail {
// The counted path instantiates this strategy with CountingLess; the production
// default has no counter or runtime instrumentation switch.
template <typename Less = std::less<Key>>
void merge_sort_impl(Values& values, Less less = Less{}) {
    const auto size = values.size();
    if (size < 2) return;
    Values buffer(size);
    auto* source = &values;
    auto* destination = &buffer;
    for (std::size_t width = 1; width < size;) {
        for (std::size_t begin = 0; begin < size;) {
            // Clamp before addition; never form begin+2*width or overflow width.
            const auto middle = begin + std::min(width, size - begin);
            const auto end = middle + std::min(width, size - middle);
            auto left = begin;
            auto right = middle;
            auto output = begin;
            while (left < middle && right < end) {
                // Taking the left key on equality preserves stable run order.
                if (less((*source)[right], (*source)[left]))
                    (*destination)[output++] = (*source)[right++];
                else
                    (*destination)[output++] = (*source)[left++];
            }
            while (left < middle) (*destination)[output++] = (*source)[left++];
            while (right < end) (*destination)[output++] = (*source)[right++];
            begin = end;
        }
        std::swap(source, destination);
        if (width >= size - width) break;
        width *= 2;
    }
    // Preserve the caller's vector storage even when the last pass used buffer.
    if (source != &values) std::copy(source->begin(), source->end(), values.begin());
}
}  // namespace mab::detail
