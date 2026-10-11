#pragma once

#include "common/types.hpp"

namespace mab {
// Stable bottom-up merging, one N-key buffer per nontrivial call. Ascending int32.
void merge_sort(Values& values);
}  // namespace mab
