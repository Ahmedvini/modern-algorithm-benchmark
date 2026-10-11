#pragma once

#include "algorithms/searching.hpp"
#include <cstdint>

namespace mab {
struct RankDiagnostic {
    SearchResult result;
    std::size_t predicted_position;
    std::size_t lower_bound_position;
    std::size_t correction_distance;
    std::uint64_t comparisons;
    bool fallback;
};

// Immutable endpoint-trained rank model; ascending input is validated at build.
// Lookup returns the FIRST equal position, including duplicate keys.
class LearnedIndex {
public:
    explicit LearnedIndex(const Values& sorted);
    SearchResult find(Key key) const;
    RankDiagnostic diagnose(Key key) const;
    std::size_t size() const noexcept { return values_.size(); }
    std::size_t owned_capacity_bytes() const noexcept { return values_.capacity() * sizeof(Key); }
    static constexpr std::size_t correction_radius = 32;

private:
    Values values_;
    template<class Less> std::size_t predict(Key key, Less less) const;
    template<class Less> RankDiagnostic lookup(Key key, Less less) const;
};
}  // namespace mab
