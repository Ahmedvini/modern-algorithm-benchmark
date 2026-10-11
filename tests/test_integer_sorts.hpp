#pragma once

#include "algorithms/sorting.hpp"
#include "datasets/generator.hpp"
#include "test_support.hpp"

#include <algorithm>
#include <limits>
#include <string_view>

// Shared differential cases for the two project int32 baselines. Every input
// goes through the public function, registry, and a repeated public invocation.
inline std::size_t check_integer_sort(std::string_view name, void (*sort)(mab::Values&)) {
    std::size_t checked = 0;
    const auto check = [&](const mab::Values& input) {
        auto expected = input;
        std::sort(expected.begin(), expected.end());
        auto actual = input;
        sort(actual);
        require(actual == expected, "public integer sorter differs from std::sort");
        actual = input;
        mab::find_sorter(name).sort(actual);
        require(actual == expected, "registered integer sorter differs from std::sort");
        // Different-size calls between repetitions must not leak workspace state.
        mab::Values scratch{4, -1, 0, 4, -2};
        sort(scratch);
        require(scratch == mab::Values({-2, -1, 0, 4, 4}), "interleaved call failed");
        actual = input;
        sort(actual);
        require(actual == expected, "repeated integer sort differs from std::sort");
        sort(actual);
        require(actual == expected, "sorting already sorted result changed values");
        ++checked;
    };
    const auto low = std::numeric_limits<mab::Key>::min();
    const auto high = std::numeric_limits<mab::Key>::max();
    for (const auto& input : std::vector<mab::Values>{
            {}, {0}, {-1}, {low}, {high}, {1, 2}, {2, 1}, {1, 1},
            {low, high}, {high, low, 0, -1, 1, low + 1, high - 1, low, high},
            {-5, -3, -7, -1}, {7, 1, 3, high, 256, 65536}, {0, 0, 0, 0},
            {0, -1, 1, 0, -1, 1}, {-65537, -65536, -65535, -257, -256, -255,
             -1, 0, 1, 255, 256, 257, 65535, 65536, 65537}}) check(input);

    std::size_t combinations = 1;
    for (std::size_t size = 0; size <= 7; ++size) {
        for (std::size_t code = 0; code < combinations; ++code) {
            auto remaining = code;
            mab::Values input(size);
            for (auto& key : input) {
                key = static_cast<mab::Key>(remaining % 3) - 1;
                remaining /= 3;
            }
            check(input);
        }
        combinations *= 3;
    }
    for (const auto distribution : {mab::Distribution::uniform, mab::Distribution::nearly_sorted,
            mab::Distribution::reverse_sorted, mab::Distribution::duplicate_heavy}) {
        for (const auto seed : {std::uint64_t{0}, std::uint64_t{1}, std::uint64_t{42},
                std::uint64_t{1729}, std::numeric_limits<std::uint64_t>::max()}) {
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
    for (const std::size_t size : {3, 7, 16, 17, 31, 32, 33, 63, 64, 65, 257, 4096}) {
        mab::Values ascending(size), organ_pipe(size), sawtooth(size), alternating(size), runs(size);
        for (std::size_t i = 0; i < size; ++i) {
            ascending[i] = static_cast<mab::Key>(i) - static_cast<mab::Key>(size / 2);
            organ_pipe[i] = static_cast<mab::Key>(std::min(i, size - 1 - i));
            sawtooth[i] = static_cast<mab::Key>(i % 17) - 8;
            alternating[i] = i % 2 == 0 ? low : high;
            runs[i] = static_cast<mab::Key>((size - i / 7) * 7 + i % 7);
        }
        auto descending = ascending;
        std::reverse(descending.begin(), descending.end());
        for (const auto& input : {ascending, descending, organ_pipe, sawtooth, alternating, runs,
                mab::Values(size, -7), mab::Values(size, low), mab::Values(size, high)}) check(input);
    }
    // Every possible digit value at each of the four bit positions, embedded in
    // varied other digits. int64 arithmetic constructs keys without signed overflow.
    for (unsigned int shift = 0; shift < 32; shift += 8) {
        mab::Values digits;
        for (std::uint32_t byte = 0; byte < 256; ++byte) {
            const auto mask = std::uint32_t{255} << shift;
            const auto word = (std::uint32_t{0x5a81c307U} & ~mask) | (byte << shift);
            digits.push_back(static_cast<mab::Key>(static_cast<std::int64_t>(word) - (std::int64_t{1} << 31)));
        }
        std::reverse(digits.begin(), digits.end());
        check(digits);
        std::rotate(digits.begin(), digits.begin() + 85, digits.end());
        check(digits);
        digits.insert(digits.end(), {low, high, -1, 0, 1, low, high});
        check(digits);
    }
    require(mab::find_sorter(name).sort == sort, "registry points at the wrong public adapter");
    require(mab::sorters().front().name == "std_sort", "default registry order changed");
    return checked;
}
