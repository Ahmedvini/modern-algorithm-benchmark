#include "benchmark/search_comparisons.hpp"
#include "algorithms/detail/search_impl.hpp"
#include <functional>
#include <limits>
#include <stdexcept>

namespace mab {
namespace {
template <typename Predicate> struct CountPredicate {
    std::uint64_t* counter;
    bool operator()(Key a, Key b) const {
        if (*counter == std::numeric_limits<std::uint64_t>::max())
            throw std::overflow_error("search comparison counter overflow");
        ++*counter;
        return Predicate{}(a, b);
    }
};
}
SearchCount counted_search(std::string_view name, const Values& values, Key key) {
    (void)find_searcher(name);
    std::uint64_t count = 0;
    const CountPredicate<std::less<Key>> less{&count};
    const CountPredicate<std::equal_to<Key>> equal{&count};
    SearchResult result;
    if (name == "linear_search") result = detail::linear_search_impl(values, key, equal);
    else if (name == "binary_search") result = detail::binary_search_impl(values, key, less, equal);
    else result = detail::exponential_search_impl(values, key, less, equal);
    return {result, count};
}
}  // namespace mab
