#pragma once

#include "common/types.hpp"

#include <cstddef>
#include <optional>

namespace mab {
// The installed C++ standard library's std::sort, with ascending signed keys.
void std_sort(Values& values);

// Requires ascending sorted data. Returns the first matching index, or nullopt.
std::optional<std::size_t> std_lower_bound_search(const Values& values, Key key);
}  // namespace mab
