#pragma once

#include "common/types.hpp"

namespace mab {
// Unmodified upstream orlp/pdqsort; version and license in third_party/pdqsort.
// Ascending signed int32 keys, in place, not stable.
void pdq_sort(Values& values);
}  // namespace mab
