#include "algorithms/quicksort.hpp"
#include "algorithms/detail/quicksort_impl.hpp"

namespace mab {
void quick_sort(Values& values) {
    detail::NoQuickSortObserver observer;
    detail::quick_sort_with_depth(values, detail::quick_sort_depth_budget(values.size()), observer);
}
}  // namespace mab
