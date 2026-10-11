#include "algorithms/timsort.hpp"
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
    mab::tim_sort(actual);
    require(actual == expected, "public Timsort differs from full std::sort reference");
    actual = input;
    mab::find_sorter("tim_sort").sort(actual);
    require(actual == expected, "registered Timsort differs from full std::sort reference");
    ++checked;
}

// Ascending runs with descending boundaries; also test duplicates and reversed runs.
void check_runs(const std::vector<std::size_t>& lengths) {
    mab::Values runs;
    mab::Key base = 20000;
    for (const auto length : lengths) {
        for (std::size_t i = 0; i < length; ++i)
            runs.push_back(base + static_cast<mab::Key>(i));
        base -= 1000;
    }
    check(runs);
    auto duplicates = runs;
    for (auto& key : duplicates) key /= 4;
    check(duplicates);
    std::reverse(runs.begin(), runs.end());
    check(runs);
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

        // Short-sort cutoff 32, minrun rounding at 64, powers of two and short tails.
        const mab::Distribution distributions[]{mab::Distribution::uniform,
            mab::Distribution::nearly_sorted, mab::Distribution::reverse_sorted,
            mab::Distribution::duplicate_heavy};
        for (const auto distribution : distributions) {
            for (const std::uint64_t seed : {std::uint64_t{0}, std::uint64_t{1},
                    std::uint64_t{42}, std::uint64_t{1729}, std::numeric_limits<std::uint64_t>::max()}) {
                for (const std::size_t size : {0, 1, 2, 3, 7, 15, 16, 17, 31, 32, 33,
                        63, 64, 65, 95, 96, 97, 127, 128, 129, 255, 256, 257,
                        511, 512, 513, 1023, 1024, 4096, 10000}) {
                    mab::DatasetConfig config;
                    config.size = size;
                    config.seed = seed;
                    config.distribution = distribution;
                    check(mab::generate_dataset(config));
                }
            }
        }

        for (const std::size_t size : {31, 32, 33, 63, 64, 65, 127, 128, 129, 1024, 4096, 10000}) {
            mab::Values ascending(size), organ_pipe(size), sawtooth(size), extrema(size), descending_duplicates(size);
            for (std::size_t i = 0; i < size; ++i) {
                ascending[i] = static_cast<mab::Key>(i) - static_cast<mab::Key>(size / 2);
                organ_pipe[i] = static_cast<mab::Key>(std::min(i, size - 1 - i));
                sawtooth[i] = static_cast<mab::Key>(i % 17) - 8;
                extrema[i] = i % 2 == 0 ? low : high;
                descending_duplicates[i] = -static_cast<mab::Key>(i / 3);
            }
            auto descending = ascending;
            std::reverse(descending.begin(), descending.end());
            auto rotated = ascending;
            std::rotate(rotated.begin(), rotated.begin() + static_cast<mab::Values::difference_type>(size / 3),
                        rotated.end());
            auto reverse_runs = ascending;
            for (std::size_t first = 0; first < size; first += 33) {
                const auto last = std::min(first + 33, size);
                std::reverse(reverse_runs.begin() + static_cast<mab::Values::difference_type>(first),
                             reverse_runs.begin() + static_cast<mab::Values::difference_type>(last));
            }
            for (const auto& values : {ascending, descending, organ_pipe, sawtooth, extrema,
                                      descending_duplicates, rotated, reverse_runs}) check(values);
            check(mab::Values(size, -7));
            check(mab::Values(size, low));
            check(mab::Values(size, high));
        }

        for (const auto& lengths : std::vector<std::vector<std::size_t>>{
                {32, 32}, {33, 32, 1}, {64, 33, 32}, {256, 128, 64, 32, 33},
                {33, 32, 64, 128, 256}, {512, 256, 128, 64, 32, 33, 1},
                {65, 64, 63, 62, 61, 60, 59, 58}, std::vector<std::size_t>(100, 33)}) {
            check_runs(lengths);
        }

        // Unequal and overlapping ascending runs, including long winner blocks.
        // These inputs target merge behavior; no internal branch coverage is claimed.
        for (const std::size_t first_size : {1, 31, 32, 33, 64, 257, 4096}) {
            for (const std::size_t second_size : {1, 31, 32, 33, 64, 257, 4096}) {
                mab::Values runs;
                for (std::size_t i = 0; i < first_size; ++i)
                    runs.push_back(static_cast<mab::Key>(2 * i));
                for (std::size_t i = 0; i < second_size; ++i)
                    runs.push_back(static_cast<mab::Key>(2 * i) - 1);
                check(runs);
                for (auto& key : runs) key /= 8;
                check(runs);
            }
        }

        require(mab::find_sorter("tim_sort").sort == &mab::tim_sort,
                "registry must select the upstream Timsort adapter");
        require(mab::sorters().front().name == "std_sort", "default registry order changed");
        bool rejected = false;
        try { (void)mab::find_sorter("timsort"); }
        catch (const std::invalid_argument&) { rejected = true; }
        require(rejected, "unregistered algorithm alias accepted");
        std::cout << "Passed " << checked << " Timsort differential cases through public and registry paths\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
