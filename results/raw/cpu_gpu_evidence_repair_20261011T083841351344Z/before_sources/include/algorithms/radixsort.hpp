#pragma once

#include "common/types.hpp"

namespace mab {
// Stable four-pass LSD radix-256 sort over the entire signed int32 domain.
// One N-key buffer per nontrivial call; no comparison-sort fallback.
void radix_sort(Values& values);
}  // namespace mab
