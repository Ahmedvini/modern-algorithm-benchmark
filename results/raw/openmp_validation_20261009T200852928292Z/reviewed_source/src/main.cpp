#include "algorithms/baselines.hpp"
#include "algorithms/sorting.hpp"
#include "datasets/generator.hpp"

#include <algorithm>
#include <charconv>
#include <exception>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {
template <typename T>
T unsigned_number(std::string_view text) {
    T value{};
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), value);
    if (parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size()) {
        throw std::invalid_argument("expected an unsigned decimal integer: " + std::string(text));
    }
    return value;
}

void usage() {
    std::cout << "Usage: algorithm_benchmark [--size N] [--seed S]\n"
                 "  [--sort std_sort|quick_sort|pdq_sort|tim_sort|merge_sort|radix_sort]\n"
                 "  [--distribution uniform|nearly_sorted|reverse_sorted|duplicate_heavy]\n"
                 "  [--swaps K] [--distinct K] [--help]\n"
                 "Correctness-only sorting and std_lower_bound checks; no timing.\n";
}
}  // namespace

int main(int argc, char** argv) {
    try {
        mab::DatasetConfig config;
        const auto* sorter = &mab::find_sorter("std_sort");
        for (int i = 1; i < argc; ++i) {
            const std::string_view option(argv[i]);
            if (option == "--help") {
                usage();
                return 0;
            }
            if (option != "--size" && option != "--seed" && option != "--distribution" &&
                option != "--swaps" && option != "--distinct" && option != "--sort") {
                throw std::invalid_argument("unknown option: " + std::string(option));
            }
            if (++i == argc) throw std::invalid_argument("missing value for " + std::string(option));
            const std::string_view value(argv[i]);
            if (option == "--size") config.size = unsigned_number<std::size_t>(value);
            else if (option == "--seed") config.seed = unsigned_number<std::uint64_t>(value);
            else if (option == "--distribution") config.distribution = mab::parse_distribution(value);
            else if (option == "--swaps") config.nearly_sorted_swaps = unsigned_number<std::size_t>(value);
            else if (option == "--sort") sorter = &mab::find_sorter(value);
            else config.duplicate_cardinality = unsigned_number<std::uint64_t>(value);
        }
        auto values = mab::generate_dataset(config);
        auto expected = values;
        std::stable_sort(expected.begin(), expected.end());
        sorter->sort(values);
        if (values != expected) throw std::runtime_error("sort correctness failure");
        // Validate the reference search adapter against a separate linear oracle.
        const mab::Key queries[]{std::numeric_limits<mab::Key>::min(), -1, 0, 1,
                                 std::numeric_limits<mab::Key>::max(),
                                 values.empty() ? 0 : values[values.size() / 2]};
        for (const auto key : queries) {
            const auto found = std::find(values.begin(), values.end(), key);
            const auto actual = mab::std_lower_bound_search(values, key);
            if ((found == values.end() && actual.has_value()) ||
                (found != values.end() && (!actual || *actual != static_cast<std::size_t>(found - values.begin())))) {
                throw std::runtime_error("search correctness failure");
            }
        }
        std::cout << "{\"schema_version\":1,\"mode\":\"correctness\",\"status\":\"ok\","
                     "\"sort_algorithm\":\"" << sorter->name << "\",\"search_algorithm\":\"std_lower_bound\","
                     "\"dataset_generator\":\"mt19937_64_v1\",\"size\":" << config.size
                  << ",\"seed\":" << config.seed << ",\"distribution\":\""
                  << mab::distribution_name(config.distribution)
                  << "\",\"nearly_sorted_swaps\":" << mab::swap_count(config)
                  << ",\"duplicate_cardinality\":" << config.duplicate_cardinality << "}\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
