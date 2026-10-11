#pragma once
#include "algorithms/searching.hpp"
#include <cstdint>
namespace mab {
struct SearchCount { SearchResult position; std::uint64_t key_comparisons; };
// Separate synchronous execution; sorted preconditions match the normal API.
// Count every executed binary key < or == predicate, excluding bookkeeping.
SearchCount counted_search(std::string_view name, const Values& values, Key key);
}  // namespace mab
