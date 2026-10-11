#include "algorithms/timsort.hpp"

#include "gfx/timsort.hpp"

namespace mab {
void tim_sort(Values& values) {
    gfx::timsort(values.begin(), values.end());
}
}  // namespace mab
