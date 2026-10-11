#include "algorithms/baselines.hpp"

#include <algorithm>

namespace mab {
void std_sort(Values& values) {
    std::sort(values.begin(), values.end());
}

std::optional<std::size_t> std_lower_bound_search(const Values& values, Key key) {
    const auto found = std::lower_bound(values.begin(), values.end(), key);
    if (found == values.end() || *found != key) {
        return std::nullopt;
    }
    return static_cast<std::size_t>(found - values.begin());
}
}  // namespace mab
