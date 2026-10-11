#include "benchmark/comparisons.hpp"
#include "benchmark/memory.hpp"
#include "algorithms/sorting.hpp"
#include "datasets/generator.hpp"

#include <algorithm>
#include <charconv>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {
template <typename T>
T unsigned_number(std::string_view text) {
    T value{};
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), value);
    if (parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size())
        throw std::invalid_argument("expected an unsigned decimal integer: " + std::string(text));
    return value;
}

void usage() {
    std::cout << "Usage: sort_metrics [--size N] [--seed S]\n"
                 "  [--sort std_sort|quick_sort|pdq_sort|tim_sort|merge_sort]\n"
                 "  [--distribution uniform|nearly_sorted|reverse_sorted|duplicate_heavy]\n"
                 "  [--swaps K] [--distinct K] [--help]\n"
                 "Separate key-comparison counts and process peak RSS; no timing.\n"
                 "radix_sort comparison counting is unsupported (no key comparisons).\n";
}
}  // namespace

int main(int argc, char** argv) {
    try {
        mab::DatasetConfig config;
        const auto* counted = &mab::find_counted_sorter("std_sort");
        for (int i = 1; i < argc; ++i) {
            const std::string_view option(argv[i]);
            if (option == "--help") { usage(); return 0; }
            if (option != "--size" && option != "--seed" && option != "--distribution" &&
                option != "--swaps" && option != "--distinct" && option != "--sort")
                throw std::invalid_argument("unknown option: " + std::string(option));
            if (++i == argc) throw std::invalid_argument("missing value for " + std::string(option));
            const std::string_view value(argv[i]);
            if (option == "--size") config.size = unsigned_number<std::size_t>(value);
            else if (option == "--seed") config.seed = unsigned_number<std::uint64_t>(value);
            else if (option == "--distribution") config.distribution = mab::parse_distribution(value);
            else if (option == "--swaps") config.nearly_sorted_swaps = unsigned_number<std::size_t>(value);
            else if (option == "--sort") counted = &mab::find_counted_sorter(value);
            else config.duplicate_cardinality = unsigned_number<std::uint64_t>(value);
        }
        const auto& normal = mab::find_sorter(counted->name);
        auto values = mab::generate_dataset(config);
        const auto comparisons = counted->sort(values);
        // Capture before validation copies/reference sorting affect the high-water mark.
        const auto memory = mab::process_memory();
        auto expected = mab::generate_dataset(config);
        std::sort(expected.begin(), expected.end());
        if (values != expected) throw std::runtime_error("instrumented sort correctness failure");
        auto production = mab::generate_dataset(config);
        normal.sort(production);
        if (values != production) throw std::runtime_error("instrumented/normal sort disagreement");
        const bool memory_error = memory.status == mab::MemoryStatus::error;
        std::cout << "{\"schema_version\":1,\"mode\":\"sort_metrics\",\"status\":\""
                  << (memory_error ? "partial" : "ok") << "\",\"sort_algorithm\":\"" << counted->name
                  << "\",\"instrumented_implementation\":\"" << counted->implementation
                  << "\",\"comparison_convention\":\"key_less_than_v1\",\"key_comparisons\":" << comparisons
                  << ",\"dataset_generator\":\"mt19937_64_v1\",\"size\":" << config.size
                  << ",\"seed\":" << config.seed << ",\"distribution\":\""
                  << mab::distribution_name(config.distribution)
                  << "\",\"nearly_sorted_swaps\":" << mab::swap_count(config)
                  << ",\"duplicate_cardinality\":" << config.duplicate_cardinality
                  << ",\"memory_sample_point\":\"after_instrumented_sort_before_validation\",\"process_memory\":";
        mab::write_memory_json(std::cout, memory);
        std::cout << "}\n";
        if (memory_error) {
            std::cerr << "error: process memory measurement failed (code " << *memory.error_code << ")\n";
            return 1;
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
