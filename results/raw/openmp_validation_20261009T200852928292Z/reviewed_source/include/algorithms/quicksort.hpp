#pragma once

#include "common/types.hpp"

namespace mab {
// Project median-of-three, three-way QuickSort with bounded stack/depth and
// heapsort fallback. Ascending signed int32 keys; not stable.
void quick_sort(Values& values);
}  // namespace mab
