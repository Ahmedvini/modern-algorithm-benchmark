#include "algorithms/pdqsort.hpp"
#include "algorithms/sorting.hpp"
#include "datasets/generator.hpp"
#include "test_support.hpp"

#include <algorithm>
#include <exception>
#include <iostream>
#include <limits>
#include <stdexcept>

namespace {
std::size_t checked = 0;
void check(const mab::Values& input) {
    auto expected = input;
    std::sort(expected.begin(), expected.end());
    auto actual = input;
    mab::pdq_sort(actual);
    require(actual == expected, "public PDQSort differs from full std::sort reference");
    actual = input;
    mab::find_sorter("pdq_sort").sort(actual);
    require(actual == expected, "registered PDQSort differs from full std::sort reference");
    ++checked;
}
}  // namespace

int main() {
    try {
        const auto low = std::numeric_limits<mab::Key>::min();
        const auto high = std::numeric_limits<mab::Key>::max();
        const std::vector<mab::Values> edges{
            {}, {0}, {-1}, {low}, {high}, {2, 1}, {1, 2}, {1, 1},
            {3, 2, 1}, {1, 3, 2}, {low, high}, {high, low, 0, -1, 1, low, high},
            {-5, -3, -7, -1}, {4, 4, 4, 4}, {0, 1, 0, -1, 0}};
        for (const auto& values : edges) check(values);

        std::size_t combinations = 1;
        for (std::size_t size = 0; size <= 7; ++size) {
            for (std::size_t code = 0; code < combinations; ++code) {
                auto remaining = code;
                mab::Values values(size);
                for (auto& key : values) {
                    key = static_cast<mab::Key>(remaining % 3) * 2 - 2;
                    remaining /= 3;
                }
                check(values);
            }
            combinations *= 3;
        }

        // Includes both sides of upstream insertion-sort (24), block (64)
        // and ninther (128) thresholds, and multiple partition-sized arrays.
        const mab::Distribution distributions[]{mab::Distribution::uniform,
            mab::Distribution::nearly_sorted, mab::Distribution::reverse_sorted,
            mab::Distribution::duplicate_heavy};
        for (const auto distribution : distributions) {
            for (const std::uint64_t seed : {std::uint64_t{0}, std::uint64_t{1},
                    std::uint64_t{42}, std::uint64_t{1729}, std::numeric_limits<std::uint64_t>::max()}) {
                for (const std::size_t size : {0, 1, 2, 3, 7, 8, 15, 16, 17, 23, 24, 25,
                        31, 32, 33, 63, 64, 65, 127, 128, 129, 255, 256, 257,
                        511, 512, 513, 1024, 4096, 10000}) {
                    mab::DatasetConfig config;
                    config.size = size;
                    config.seed = seed;
                    config.distribution = distribution;
                    check(mab::generate_dataset(config));
                }
            }
        }

        for (const std::size_t size : {23, 24, 25, 63, 64, 65, 127, 128, 129, 1024, 4096, 10000}) {
            mab::Values ascending(size), organ_pipe(size), sawtooth(size), alternating(size), extrema(size);
            for (std::size_t i = 0; i < size; ++i) {
                ascending[i] = static_cast<mab::Key>(i);
                organ_pipe[i] = static_cast<mab::Key>(std::min(i, size - 1 - i));
                sawtooth[i] = static_cast<mab::Key>(i % 17) - 8;
                alternating[i] = i % 2 == 0 ? static_cast<mab::Key>(i / 2) :
                                               static_cast<mab::Key>(size - 1 - i / 2);
                extrema[i] = i % 2 == 0 ? low : high;
            }
            auto descending = ascending;
            std::reverse(descending.begin(), descending.end());
            auto rotated = ascending;
            std::rotate(rotated.begin(), rotated.begin() + static_cast<mab::Values::difference_type>(size / 3),
                        rotated.end());
            auto reverse_runs = ascending;
            for (std::size_t first = 0; first < size; first += 32) {
                const auto last = std::min(first + 32, size);
                std::reverse(reverse_runs.begin() + static_cast<mab::Values::difference_type>(first),
                             reverse_runs.begin() + static_cast<mab::Values::difference_type>(last));
            }
            for (const auto& values : {ascending, descending, organ_pipe, sawtooth, alternating,
                                      extrema, rotated, reverse_runs}) {
                check(values);
            }
            check(mab::Values(size, -7));
            check(mab::Values(size, low));
            check(mab::Values(size, high));
        }

        require(mab::find_sorter("pdq_sort").sort == &mab::pdq_sort,
                "registry must select the upstream PDQSort adapter");
        require(mab::sorters().front().name == "std_sort", "default registry order changed");
        bool rejected = false;
        try { (void)mab::find_sorter("pdqsort"); }
        catch (const std::invalid_argument&) { rejected = true; }
        require(rejected, "unregistered algorithm alias accepted");
        std::cout << "Passed " << checked << " PDQSort differential cases through public and registry paths\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
