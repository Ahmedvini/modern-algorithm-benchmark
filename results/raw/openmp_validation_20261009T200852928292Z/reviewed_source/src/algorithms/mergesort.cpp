#include "algorithms/mergesort.hpp"
#include "algorithms/detail/mergesort_impl.hpp"

namespace mab {
void merge_sort(Values& values) {
    detail::merge_sort_impl(values);
}
}  // namespace mab
