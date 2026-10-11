#include "algorithms/baselines.hpp"
#include "algorithms/sorting.hpp"
#include "datasets/generator.hpp"
#include "test_support.hpp"

#include <algorithm>
#include <exception>
#include <functional>
#include <iostream>
#include <limits>
#include <stdexcept>

namespace {
template <typename Function>
void must_reject(Function function) {
    bool rejected = false;
    try {
        function();
    } catch (const std::invalid_argument&) {
        rejected = true;
    }
    require(rejected, "invalid generator configuration was accepted");
}
}  // namespace

int main() {
    try {
        const mab::Distribution distributions[]{mab::Distribution::uniform,
            mab::Distribution::nearly_sorted, mab::Distribution::reverse_sorted,
            mab::Distribution::duplicate_heavy};
        std::size_t cases = 0;
        for (const std::uint64_t seed : {std::uint64_t{0}, std::uint64_t{1},
                std::uint64_t{1729}, std::uint64_t{42}, std::numeric_limits<std::uint64_t>::max()}) {
            for (const std::size_t size : {0, 1, 2, 3, 31, 32, 63, 64, 127, 128, 1000}) {
                for (const auto distribution : distributions) {
                    mab::DatasetConfig config;
                    config.size = size;
                    config.seed = seed;
                    config.distribution = distribution;
                    const auto values = mab::generate_dataset(config);
                    require(values.size() == size, "wrong dataset size");
                    require(values == mab::generate_dataset(config), "generation not reproducible");
                    require(mab::parse_distribution(mab::distribution_name(distribution)) == distribution,
                            "distribution name round trip failed");
                    auto actual = values;
                    auto expected = values;
                    std::stable_sort(expected.begin(), expected.end());
                    mab::std_sort(actual);
                    require(actual == expected, "distribution differential sort failed");
                    for (const auto& sorter : mab::sorters()) {
                        auto registered_output = values;
                        sorter.sort(registered_output);
                        require(registered_output == expected,
                                "registered sorter failed distribution differential check");
                    }
                    if (distribution == mab::Distribution::reverse_sorted) {
                        require(std::is_sorted(values.begin(), values.end(), std::greater<mab::Key>{}),
                                "reverse distribution is not nonincreasing");
                    }
                    if (distribution == mab::Distribution::duplicate_heavy) {
                        require(std::all_of(values.begin(), values.end(), [](mab::Key key) {
                            return key >= -8 && key <= 7;
                        }), "duplicate-heavy key outside defined domain");
                    } else {
                        auto uniform_config = config;
                        uniform_config.distribution = mab::Distribution::uniform;
                        auto uniform = mab::generate_dataset(uniform_config);
                        std::stable_sort(uniform.begin(), uniform.end());
                        require(uniform == expected, "ordering transform changed input multiset");
                    }
                    ++cases;
                }
            }
        }
        mab::DatasetConfig fixture;
        fixture.size = 8;
        const mab::Values uniform_expected{1566717807, -1420077265, 1110825626, 1556303738,
                                          695661999, -1549569978, -1307804991, 1406835019};
        require(mab::generate_dataset(fixture) == uniform_expected, "uniform v1 fixture changed");
        fixture.distribution = mab::Distribution::duplicate_heavy;
        require(mab::generate_dataset(fixture) == mab::Values{7, 7, 2, 2, 7, -2, -7, 3},
                "duplicate-heavy v1 fixture changed");
        fixture.duplicate_cardinality = 1;
        require(mab::generate_dataset(fixture) == mab::Values(8, 0), "cardinality one should be all zero");
        fixture.duplicate_cardinality = std::uint64_t{1} << 32;
        require(mab::generate_dataset(fixture) == uniform_expected, "full int32 domain mapping changed");
        fixture.duplicate_cardinality = 0;
        must_reject([&] { (void)mab::generate_dataset(fixture); });
        fixture.duplicate_cardinality = (std::uint64_t{1} << 32) + 1;
        must_reject([&] { (void)mab::generate_dataset(fixture); });
        fixture.duplicate_cardinality = 16;
        fixture.distribution = static_cast<mab::Distribution>(99);
        must_reject([&] { (void)mab::generate_dataset(fixture); });
        must_reject([] { (void)mab::parse_distribution("unknown"); });

        fixture.distribution = mab::Distribution::nearly_sorted;
        fixture.nearly_sorted_swaps = 0;
        auto sorted = uniform_expected;
        std::sort(sorted.begin(), sorted.end());
        require(mab::generate_dataset(fixture) == sorted, "zero swaps should produce sorted data");
        // Full outputs independently verified using a Python MT19937-64
        // reference and a separately compiled probe of the current generator.
        struct SwapFixture {
            std::uint64_t seed;
            mab::Values before;
            mab::Values after;
            std::size_t changed_positions;
        };
        const SwapFixture swap_fixtures[]{
            // size 4: self-swaps at indices 0 and 3, respectively.
            {11, {-1890549451, -1483881485, 292151025, 1797203965},
                 {-1890549451, -1483881485, 292151025, 1797203965}, 0},
            {28, {-405710623, 701992933, 771250229, 1587115924},
                 {-405710623, 701992933, 771250229, 1587115924}, 0},
            // size 4: endpoint pair (0,3) and interior pair (1,2).
            {13, {-1617578993, 364859267, 842348706, 1742204363},
                 {1742204363, 364859267, 842348706, -1617578993}, 2},
            {8, {955182970, 1293152134, 1392846233, 1566112152},
                {955182970, 1392846233, 1293152134, 1566112152}, 2},
            // size 8: distinct pair (7,1), with mixed signed values.
            {1729, {-1549569978, -1420077265, -1307804991, 695661999,
                     1110825626, 1406835019, 1556303738, 1566717807},
                    {-1549569978, 1566717807, -1307804991, 695661999,
                     1110825626, 1406835019, 1556303738, -1420077265}, 2}};
        for (const auto& test : swap_fixtures) {
            mab::DatasetConfig config;
            config.size = test.before.size();
            config.seed = test.seed;
            config.distribution = mab::Distribution::nearly_sorted;
            config.nearly_sorted_swaps = 0;
            require(mab::generate_dataset(config) == test.before, "zero-swap v1 fixture changed");
            require(std::adjacent_find(test.before.begin(), test.before.end()) == test.before.end(),
                    "swap fixture must contain distinct int32 keys");
            config.nearly_sorted_swaps = 1;
            const auto actual = mab::generate_dataset(config);
            require(actual == test.after, "one-swap v1 fixture changed");
            std::size_t changed = 0;
            for (std::size_t i = 0; i < actual.size(); ++i) changed += actual[i] != test.before[i];
            require(changed == test.changed_positions, "incorrect count of changed positions");
        }
        fixture.nearly_sorted_swaps = 5;
        require(mab::generate_dataset(fixture) == mab::Values{
            1556303738, -1549569978, 1406835019, 695661999,
            1110825626, -1307804991, -1420077265, 1566717807},
            "five-swap v1 fixture changed");
        // Empty and singleton inputs skip swaps even for the largest request.
        for (const std::size_t size : {0, 1}) {
            mab::DatasetConfig config;
            config.size = size;
            config.distribution = mab::Distribution::nearly_sorted;
            config.nearly_sorted_swaps = 0;
            const auto before = mab::generate_dataset(config);
            config.nearly_sorted_swaps = std::numeric_limits<std::size_t>::max();
            require(mab::generate_dataset(config) == before,
                    "swap requests changed empty or singleton input");
        }
        fixture.nearly_sorted_swaps = 100;
        fixture.size = 0;
        require(mab::generate_dataset(fixture).empty(), "empty nearly sorted failed");
        fixture.size = 1;
        require(mab::generate_dataset(fixture).size() == 1, "singleton nearly sorted failed");
        fixture.distribution = mab::Distribution::uniform;
        fixture.size = 32;
        fixture.seed = 0;
        const auto first_seed = mab::generate_dataset(fixture);
        fixture.seed = 1;
        require(first_seed != mab::generate_dataset(fixture), "selected distinct seeds produced identical fixture");
        std::cout << "Passed " << cases << " distribution/size/seed cases, five exact one-swap fixtures, "
                     "one five-swap fixture, empty/singleton swap checks, and existing fixtures/validation\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
