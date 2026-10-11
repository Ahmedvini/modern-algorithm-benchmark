#include "algorithms/searching.hpp"
#include "algorithms/detail/search_impl.hpp"
#include <stdexcept>
#include <string>

namespace mab {
SearchResult linear_search(const Values& values, Key key) { return detail::linear_search_impl(values, key); }
SearchResult binary_search(const Values& values, Key key) { return detail::binary_search_impl(values, key); }
SearchResult exponential_search(const Values& values, Key key) { return detail::exponential_search_impl(values, key); }
const std::array<Searcher, 3>& searchers() noexcept {
    static const std::array<Searcher, 3> registry{{
        {"linear_search", linear_search, false}, {"binary_search", binary_search, true},
        {"exponential_search", exponential_search, true}}};
    return registry;
}
const Searcher& find_searcher(std::string_view name) {
    for (const auto& searcher : searchers()) if (searcher.name == name) return searcher;
    throw std::invalid_argument("unknown searcher: " + std::string(name));
}
}  // namespace mab
