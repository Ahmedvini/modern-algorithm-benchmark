#include "indexes/learned_index.hpp"
#include "datasets/generator.hpp"

#include <algorithm>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>

namespace {
std::size_t datasets = 0, checks = 0, fallbacks = 0;
void verify(mab::Values values, const mab::Values& queries) {
    std::sort(values.begin(), values.end());
    const mab::LearnedIndex index(values);
    const auto copy = index;
    if (index.size() != values.size() || index.owned_capacity_bytes() < values.size() * sizeof(mab::Key))
        throw std::runtime_error("size/storage mismatch");
    ++datasets;
    for (const auto key : queries) {
        const auto it = std::lower_bound(values.begin(), values.end(), key);
        const auto position = static_cast<std::size_t>(it - values.begin());
        const mab::SearchResult expected = it != values.end() && *it == key ? mab::SearchResult(position) : std::nullopt;
        const auto diagnostic = index.diagnose(key);
        const auto repeat = index.diagnose(key);
        if (index.find(key) != expected || copy.find(key) != expected || diagnostic.result != expected ||
            diagnostic.lower_bound_position != position || repeat.comparisons != diagnostic.comparisons ||
            repeat.fallback != diagnostic.fallback || diagnostic.correction_distance !=
            (position > diagnostic.predicted_position ? position - diagnostic.predicted_position : diagnostic.predicted_position - position))
            throw std::runtime_error("learned-index oracle/diagnostic mismatch");
        ++checks;
        if (diagnostic.fallback) ++fallbacks;
    }
}
}

int main() {
    try {
        const auto low = std::numeric_limits<mab::Key>::min();
        const auto high = std::numeric_limits<mab::Key>::max();
        const mab::Values edges{low, low + 1, -2, -1, 0, 1, 2, high - 1, high};
        for (const auto& data : std::vector<mab::Values>{{}, {0}, {low}, {high}, {1, 0}, edges,
                mab::Values(1000, 0), {-9, -9, -9, -1, 2, 2, 2}, {low, 0, 0, 0, high}}) verify(data, edges);
        bool rejected = false;
        try { const mab::LearnedIndex bad({1, 0}); } catch (const std::invalid_argument&) { rejected = true; }
        if (!rejected) throw std::runtime_error("unsorted input accepted");
        // Hand-verifiable predicate counts: empty does no key work; singleton
        // equal performs one lower-bound predicate and one equality predicate.
        if (mab::LearnedIndex({}).diagnose(0).comparisons != 0 ||
            mab::LearnedIndex({0}).diagnose(0).comparisons != 2 ||
            mab::LearnedIndex({-1, 1}).diagnose(0).comparisons != 6)
            throw std::runtime_error("small exact comparison count mismatch");
        for (const auto seed : {1729ULL, 42ULL, 2718ULL}) {
            for (const auto size : {0U, 1U, 2U, 31U, 32U, 33U, 63U, 64U, 65U, 127U, 1025U, 65537U}) {
                for (const auto distribution : {mab::Distribution::uniform, mab::Distribution::nearly_sorted,
                        mab::Distribution::reverse_sorted, mab::Distribution::duplicate_heavy}) {
                    mab::DatasetConfig config;
                    config.size = size; config.seed = seed; config.distribution = distribution;
                    auto data = mab::generate_dataset(config);
                    auto queries = edges;
                    // Every key for small datasets, deterministic spaced keys for larger ones.
                    const auto stride = std::max<std::size_t>(1, data.size() / 1000);
                    for (std::size_t i = 0; i < data.size(); i += stride) queries.push_back(data[i]);
                    std::mt19937_64 engine(seed);
                    for (int i = 0; i < 100; ++i) queries.push_back(static_cast<mab::Key>(
                        static_cast<std::int64_t>(engine() & 0xffffffffULL) - 2147483648LL));
                    verify(std::move(data), queries);
                }
            }
        }
        if (fallbacks == 0) throw std::runtime_error("fallback was not exercised");
        std::cout << "learned index: " << datasets << " datasets, " << checks
                  << " oracle checks, " << fallbacks << " observed fallbacks; unsorted rejection passed\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
