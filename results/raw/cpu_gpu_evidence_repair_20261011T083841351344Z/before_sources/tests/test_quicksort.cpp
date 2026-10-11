#include "algorithms/quicksort.hpp"
#include "algorithms/detail/quicksort_impl.hpp"
#include "algorithms/sorting.hpp"
#include "datasets/generator.hpp"
#include "test_support.hpp"

#include <algorithm>
#include <exception>
#include <iostream>
#include <limits>
#include <stdexcept>

namespace {
struct Observer {
    std::size_t partitions = 0;
    std::size_t heap_fallbacks = 0;
    std::size_t heap_elements = 0;
    std::size_t max_stack_depth = 0;

    void on_partition() { ++partitions; }
    void on_heap_fallback(std::size_t size) {
        require(size > 1, "fallback called on a trivial range");
        ++heap_fallbacks;
        heap_elements += size;
    }
    void on_stack_depth(std::size_t depth) {
        max_stack_depth = std::max(max_stack_depth, depth);
    }
};

std::size_t checked = 0;
Observer check(const mab::Values& input) {
    auto expected = input;
    std::sort(expected.begin(), expected.end());
    auto actual = input;
    mab::quick_sort(actual);
    require(actual == expected, "public QuickSort differs from full std::sort reference");
    actual = input;
    Observer observer;
    const auto budget = mab::detail::quick_sort_depth_budget(input.size());
    mab::detail::quick_sort_with_depth(actual, budget, observer);
    require(actual == expected, "observed QuickSort differs from full std::sort reference");
    require(observer.max_stack_depth <= 1 + budget / 2, "smaller-partition stack bound exceeded");
    ++checked;
    return observer;
}
}  // namespace

int main() {
    try {
        const auto low = std::numeric_limits<mab::Key>::min();
        const auto high = std::numeric_limits<mab::Key>::max();
        const std::vector<mab::Values> edges{
            {}, {0}, {low}, {high}, {2, 1}, {1, 2}, {1, 1}, {3, 2, 1}, {1, 3, 2},
            {low, high}, {high, low, 0, -1, 1, low, high}, {-5, -3, -7, -1},
            {4, 4, 4, 4}, {0, 1, 0, -1, 0}};
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
        const mab::Distribution distributions[]{mab::Distribution::uniform,
            mab::Distribution::nearly_sorted, mab::Distribution::reverse_sorted,
            mab::Distribution::duplicate_heavy};
        for (const auto distribution : distributions) {
            for (const std::uint64_t seed : {std::uint64_t{0}, std::uint64_t{1},
                    std::uint64_t{42}, std::uint64_t{1729}, std::numeric_limits<std::uint64_t>::max()}) {
                for (const std::size_t size : {0, 1, 2, 3, 15, 16, 17, 31, 32, 63, 64,
                                              127, 128, 255, 256, 257, 1023, 1024, 4096, 10000}) {
                    mab::DatasetConfig config;
                    config.size = size;
                    config.seed = seed;
                    config.distribution = distribution;
                    check(mab::generate_dataset(config));
                }
            }
        }
        require(mab::detail::quick_sort_depth_budget(0) == 0 &&
                mab::detail::quick_sort_depth_budget(1) == 0 &&
                mab::detail::quick_sort_depth_budget(2) == 2 &&
                mab::detail::quick_sort_depth_budget(7) == 4 &&
                mab::detail::quick_sort_depth_budget(8) == 6,
                "depth budget must equal twice floor(log2(n))");

        // Explicitly exhaust the budget and observe the actual fallback call.
        const mab::Values forced_input{high, -4, 9, low, 0, 9, 3, -8, 1, 7};
        auto expected = forced_input;
        std::sort(expected.begin(), expected.end());
        auto forced = forced_input;
        Observer exhausted;
        mab::detail::quick_sort_with_depth(forced, 0, exhausted);
        require(forced == expected && exhausted.partitions == 0 && exhausted.heap_fallbacks == 1 &&
                exhausted.heap_elements == forced.size(), "zero budget did not exercise whole-range heapsort");
        forced = forced_input;
        Observer one_partition;
        mab::detail::quick_sort_with_depth(forced, 1, one_partition);
        require(forced == expected && one_partition.partitions == 1 && one_partition.heap_fallbacks > 0,
                "one-level budget did not exercise heapsort on partitioned subranges");
        for (const auto& trivial : {mab::Values{}, mab::Values{1}}) {
            auto values = trivial;
            Observer observer;
            mab::detail::quick_sort_with_depth(values, 0, observer);
            require(values == trivial && observer.heap_fallbacks == 0, "trivial exhausted-budget range changed");
        }
        // Both balanced children inherit the consumed budget: one recursive,
        // one iterative. This checks fallback bounds and sibling propagation.
        mab::Values balanced{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14};
        const auto balanced_expected = balanced;
        Observer siblings;
        mab::detail::quick_sort_with_depth(balanced, 1, siblings);
        require(balanced == balanced_expected && siblings.partitions == 1 &&
                siblings.heap_fallbacks == 2 && siblings.heap_elements == 14 &&
                siblings.max_stack_depth == 2, "both children must inherit the exhausted budget");
        mab::Values subrange{high, 9, -3, 0, low, high, low};
        auto subrange_expected = subrange;
        std::sort(subrange_expected.begin() + 1, subrange_expected.end() - 1);
        Observer bounded;
        mab::detail::quick_sort_range(subrange, 1, subrange.size() - 1, 0, bounded, 1);
        require(subrange == subrange_expected && bounded.heap_fallbacks == 1 &&
                bounded.heap_elements == 5, "heapsort fallback modified range sentinels");

        // Adversarial orderings use the production depth budget, not an override.
        std::size_t default_fallbacks = 0;
        for (const std::size_t size : {127, 1024, 4096, 10000}) {
            mab::Values ascending(size), organ_pipe(size), sawtooth(size), alternating(size);
            for (std::size_t i = 0; i < size; ++i) {
                ascending[i] = static_cast<mab::Key>(i);
                organ_pipe[i] = static_cast<mab::Key>(std::min(i, size - 1 - i));
                sawtooth[i] = static_cast<mab::Key>(i % 17) - 8;
                alternating[i] = i % 2 == 0 ? static_cast<mab::Key>(i / 2) :
                                               static_cast<mab::Key>(size - 1 - i / 2);
            }
            auto descending = ascending;
            std::reverse(descending.begin(), descending.end());
            for (const auto& values : {ascending, descending, organ_pipe, sawtooth, alternating}) {
                default_fallbacks += check(values).heap_fallbacks;
            }
            const auto equal = check(mab::Values(size, -7));
            require(equal.partitions == 1 && equal.heap_fallbacks == 0,
                    "all-equal input should finish in one three-way partition");
        }
        require(default_fallbacks > 0, "adversarial inputs did not exercise the production depth limit");
        require(mab::find_sorter("quick_sort").sort == &mab::quick_sort,
                "registry must select the project implementation");
        bool rejected = false;
        try { (void)mab::find_sorter("unknown"); }
        catch (const std::invalid_argument&) { rejected = true; }
        require(rejected, "unknown sorter accepted");
        std::cout << "Passed " << checked << " QuickSort differential cases through public and observed paths; "
                  << "forced zero-budget fallback=" << exhausted.heap_fallbacks
                  << ", one-budget fallback=" << one_partition.heap_fallbacks
                  << ", balanced-child fallbacks=" << siblings.heap_fallbacks
                  << ", sentinel-range fallback=" << bounded.heap_fallbacks
                  << ", default-budget adversarial fallbacks=" << default_fallbacks << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
