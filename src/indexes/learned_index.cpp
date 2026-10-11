#include "indexes/learned_index.hpp"

#include <algorithm>
#include <stdexcept>

namespace mab {
LearnedIndex::LearnedIndex(const Values& sorted) : values_(sorted) {
    if (!std::is_sorted(values_.begin(), values_.end()))
        throw std::invalid_argument("learned index requires ascending input");
}

template<class Less> std::size_t LearnedIndex::predict(Key key, Less less) const {
    if (values_.size() < 2 || !less(values_.front(), values_.back()) || !less(values_.front(), key)) return 0;
    if (!less(key, values_.back())) return values_.size() - 1;
    const auto offset = static_cast<std::int64_t>(key) - values_.front();
    const auto span = static_cast<std::int64_t>(values_.back()) - values_.front();
    const auto position = static_cast<long double>(offset) / static_cast<long double>(span)
                        * static_cast<long double>(values_.size() - 1);
    // Clamp before conversion, including implementations where floating arithmetic rounds up.
    if (position >= static_cast<long double>(values_.size() - 1)) return values_.size() - 1;
    return static_cast<std::size_t>(position);
}

template<class Less> RankDiagnostic LearnedIndex::lookup(Key key, Less less) const {
    const auto n = values_.size();
    const auto prediction = predict(key, less);
    const auto begin = prediction > correction_radius ? prediction - correction_radius : 0;
    const auto end = n == 0 ? 0 : prediction + std::min(n - prediction, correction_radius + 1);
    const auto lower_bound = [&](std::size_t lo, std::size_t hi) {
        while (lo < hi) {
            const auto middle = lo + (hi - lo) / 2;
            if (less(values_[middle], key)) lo = middle + 1;
            else hi = middle;
        }
        return lo;
    };
    auto position = lower_bound(begin, end);
    // A local answer is valid only if no earlier equal key was excluded and
    // the lower bound was found before the right boundary (or that boundary is n).
    const bool fallback = (begin != 0 && !less(values_[begin - 1], key)) ||
                          (position == end && end != n);
    if (fallback) position = lower_bound(0, n);
    SearchResult result;
    if (position < n && !less(key, values_[position])) result = position;
    const auto distance = position > prediction ? position - prediction : prediction - position;
    return {result, prediction, position, distance, 0, fallback};
}

SearchResult LearnedIndex::find(Key key) const {
    return lookup(key, [](Key a, Key b) { return a < b; }).result;
}

RankDiagnostic LearnedIndex::diagnose(Key key) const {
    std::uint64_t comparisons = 0;
    auto result = lookup(key, [&](Key a, Key b) { ++comparisons; return a < b; });
    result.comparisons = comparisons;
    return result;
}
}  // namespace mab
