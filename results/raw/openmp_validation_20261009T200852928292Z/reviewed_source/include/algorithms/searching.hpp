#pragma once

#include "common/types.hpp"
#include <array>
#include <cstddef>
#include <optional>
#include <string_view>

namespace mab {
using SearchResult = std::optional<std::size_t>;
// All return the first equal key's index, or nullopt. Linear accepts any order.
SearchResult linear_search(const Values& values, Key key);
// Preconditions: values is ascending. No per-call validation or sorting.
SearchResult binary_search(const Values& values, Key key);
SearchResult exponential_search(const Values& values, Key key);
struct Searcher {
    std::string_view name;
    SearchResult (*search)(const Values&, Key);
    bool requires_sorted;
};
const std::array<Searcher, 3>& searchers() noexcept;
const Searcher& find_searcher(std::string_view name);
}  // namespace mab
