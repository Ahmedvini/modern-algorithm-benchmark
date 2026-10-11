#include "algorithms/baselines.hpp"
#include "algorithms/sorting.hpp"
#include "test_support.hpp"

#include <algorithm>
#include <exception>
#include <iostream>
#include <limits>
#include <random>

int main() {
    try {
        const auto low = std::numeric_limits<mab::Key>::min();
        const auto high = std::numeric_limits<mab::Key>::max();
        const std::vector<mab::Values> cases{
            {}, {0}, {-1}, {low}, {high}, {1, 2, 3}, {3, 2, 1},
            {7, 7, 7}, {-4, 2, -4, 0, 2}, {high, low, 0, -1, high, low}};
        std::size_t checked = 0;
        std::size_t search_checks = 0;
        const auto check = [&checked, &search_checks, low, high](mab::Values values) {
            const auto input = values;
            auto expected = values;
            std::stable_sort(expected.begin(), expected.end());
            mab::std_sort(values);
            require(values == expected, "full output differs from stable_sort reference");
            require(std::is_sorted(values.begin(), values.end()), "output is not sorted");
            for (const auto& sorter : mab::sorters()) {
                auto actual = input;
                sorter.sort(actual);
                require(actual == expected, "registered sorter differs from full-vector reference");
            }
            const auto search = [&](mab::Key key) {
                const auto expected_position = std::find(values.begin(), values.end(), key);
                const auto actual_position = mab::std_lower_bound_search(values, key);
                if (expected_position == values.end()) {
                    require(!actual_position, "search reported a miss as a hit");
                } else {
                    require(actual_position && *actual_position ==
                                static_cast<std::size_t>(expected_position - values.begin()),
                            "search must return the first duplicate's position");
                }
                ++search_checks;
            };
            for (const auto key : {low, high, mab::Key{-3}, mab::Key{-2}, mab::Key{-1},
                                   mab::Key{0}, mab::Key{1}, mab::Key{2}, mab::Key{3}}) {
                search(key);
            }
            for (const auto key : values) search(key);
            ++checked;
        };
        for (const auto& values : cases) {
            check(values);
        }
        std::mt19937 engine(1729);
        for (std::size_t size = 0; size < 300; ++size) {
            mab::Values values(size);
            for (auto& key : values) {
                key = static_cast<mab::Key>(engine() % 41) - 20;
            }
            check(values);
        }
        // Exhaust all arrays of length 0..7 over {-2, 0, 2}, stressing duplicates.
        std::size_t combinations = 1;
        for (std::size_t size = 0; size <= 7; ++size) {
            for (std::size_t code = 0; code < combinations; ++code) {
                auto remainder = code;
                mab::Values values(size);
                for (auto& key : values) {
                    key = static_cast<mab::Key>(remainder % 3) * 2 - 2;
                    remainder /= 3;
                }
                check(values);
            }
            combinations *= 3;
        }
        std::cout << "Passed " << checked << " full-vector differential sort cases and "
                  << search_checks << " linear-oracle search checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
