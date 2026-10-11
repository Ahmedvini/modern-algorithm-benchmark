#include "benchmark/comparisons.hpp"
#include "benchmark/detail/counting_less.hpp"
#include "algorithms/detail/quicksort_impl.hpp"
#include "algorithms/sorting.hpp"
#include "datasets/generator.hpp"
#include "test_support.hpp"

#include <algorithm>
#include <exception>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>

namespace {
std::size_t checked = 0;
void check(const mab::Values& input) {
    auto expected = input;
    std::sort(expected.begin(), expected.end());
    for (const auto& sorter : mab::counted_sorters()) {
        auto production = input;
        mab::find_sorter(sorter.name).sort(production);
        auto counted = input;
        const auto count = sorter.sort(counted);
        require(counted == expected && counted == production, "counted/normal/reference output disagreement");
        auto repeated = input;
        require(sorter.sort(repeated) == count && repeated == expected, "count changed across identical runs");
        if (input.size() < 2) require(count == 0, "trivial input performed key comparisons");
        else require(count > 0, "nontrivial input reported no key comparisons");
        auto empty = mab::Values{};
        require(sorter.sort(empty) == 0, "counter was not reset after a nonempty run");
        // Interleave other sorter calls before repeating this sorter.
        for (const auto& other : mab::counted_sorters()) {
            mab::Values scratch{3, 1, 2};
            (void)other.sort(scratch);
        }
        repeated = input;
        require(sorter.sort(repeated) == count && repeated == expected, "interleaved runs shared counter state");
    }
    ++checked;
}

struct HeapObserver {
    std::size_t fallbacks = 0;
    void on_partition() const {}
    void on_stack_depth(std::size_t) const {}
    void on_heap_fallback(std::size_t) { ++fallbacks; }
};
}  // namespace

int main() {
    try {
        // Manually verified comparator accounting, including equal/self keys.
        std::uint64_t first = 0, second = 0;
        mab::detail::CountingLess less(first), independent(second);
        auto copied = less;
        require(less(-1, 0) && !copied(0, -1) && !less(7, 7), "counting comparator ordering changed");
        require(first == 3 && second == 0, "comparator copies did not share only their local counter");
        require(independent(-2, 1) && second == 1 && first == 3, "independent comparator state changed");
        first = std::numeric_limits<std::uint64_t>::max();
        bool overflow = false;
        try { (void)less(0, 1); } catch (const std::overflow_error&) { overflow = true; }
        require(overflow && first == std::numeric_limits<std::uint64_t>::max(), "counter wrapped on overflow");

        // QuickSort traces include pivot-selection comparisons and both tests
        // of an equal key. [1,2]: pivot=2, median costs 3, partition costs 3.
        // [2,1]: pivot=1, median costs 3, partition costs 4. [1,1]: 3+4.
        for (const auto& fixture : std::vector<std::pair<mab::Values, std::uint64_t>>{
                {{}, 0}, {{7}, 0}, {{1, 2}, 6}, {{2, 1}, 7}, {{1, 1}, 7}, {{1, 1, 1}, 9}}) {
            auto values = fixture.first;
            require(mab::find_counted_sorter("quick_sort").sort(values) == fixture.second,
                    "manually verified QuickSort comparison count changed");
            auto expected = fixture.first;
            std::sort(expected.begin(), expected.end());
            require(values == expected, "exact-count fixture not sorted");
        }

        // Independently count just the STL heap calls, then exhaust QuickSort's
        // budget. This checks comparator forwarding through its fallback.
        mab::Values heap_input{9, -4, 7, 0, 7, -10, 5};
        auto heap_reference = heap_input;
        std::uint64_t heap_count = 0;
        auto heap_less = [&](mab::Key a, mab::Key b) { ++heap_count; return a < b; };
        std::make_heap(heap_reference.begin(), heap_reference.end(), heap_less);
        std::sort_heap(heap_reference.begin(), heap_reference.end(), heap_less);
        std::uint64_t fallback_count = 0;
        HeapObserver observer;
        mab::detail::quick_sort_with_depth(heap_input, 0, observer, mab::detail::CountingLess(fallback_count));
        require(observer.fallbacks == 1 && fallback_count == heap_count && fallback_count > 0 &&
                heap_input == heap_reference, "heapsort fallback comparisons were omitted");

        const auto low = std::numeric_limits<mab::Key>::min();
        const auto high = std::numeric_limits<mab::Key>::max();
        for (const auto& input : std::vector<mab::Values>{
                {}, {0}, {-1}, {low}, {high}, {1, 2}, {2, 1}, {1, 1},
                {-5, -3, -7}, {low, high, 0, -1, 1, low, high}, {0, 0, 0, 0}}) check(input);
        std::size_t combinations = 1;
        for (std::size_t size = 0; size <= 6; ++size) {
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
            for (const std::uint64_t seed : {std::uint64_t{0}, std::uint64_t{42}, std::uint64_t{1729}}) {
                for (const std::size_t size : {0, 1, 2, 7, 23, 24, 25, 31, 32, 33, 63, 64, 65,
                                             127, 128, 129, 255, 256, 257, 1024, 4096}) {
                    mab::DatasetConfig config;
                    config.size = size;
                    config.seed = seed;
                    config.distribution = distribution;
                    check(mab::generate_dataset(config));
                }
            }
        }
        for (const std::size_t size : {31, 32, 63, 64, 127, 128, 1024, 4096}) {
            mab::Values ascending(size), organ_pipe(size), sawtooth(size), alternating(size);
            for (std::size_t i = 0; i < size; ++i) {
                ascending[i] = static_cast<mab::Key>(i) - static_cast<mab::Key>(size / 2);
                organ_pipe[i] = static_cast<mab::Key>(std::min(i, size - 1 - i));
                sawtooth[i] = static_cast<mab::Key>(i % 17) - 8;
                alternating[i] = i % 2 == 0 ? low : high;
            }
            auto descending = ascending;
            std::reverse(descending.begin(), descending.end());
            for (const auto& pattern : {ascending, descending, organ_pipe, sawtooth, alternating,
                                       mab::Values(size, -7)}) check(pattern);
        }
        // Radix sorting has no key predicate metric; it must not masquerade as
        // a comparison sorter reporting zero. All other registry names count.
        require(mab::counted_sorters().size() + 1 == mab::sorters().size(), "unexpected counting coverage");
        for (const auto& sorter : mab::sorters()) {
            if (sorter.name == "radix_sort") continue;
            require(mab::find_counted_sorter(sorter.name).sort != nullptr, "missing counted adapter");
        }
        bool unsupported = false;
        try { (void)mab::find_counted_sorter("radix_sort"); }
        catch (const std::invalid_argument& error) {
            unsupported = std::string(error.what()).find("unsupported") != std::string::npos;
        }
        require(unsupported, "radix comparison metric not explicitly unsupported");

        // Bottom-up run widths 1,2,... with no key predicate on leftover tails.
        // Each active merge compares right < left, selecting left on equality.
        for (const auto& fixture : std::vector<std::pair<mab::Values, std::uint64_t>>{
                {{}, 0}, {{7}, 0}, {{1, 2}, 1}, {{2, 1}, 1}, {{1, 1}, 1},
                {{1, 2, 3}, 3}, {{3, 2, 1}, 2}, {{1, 1, 1}, 3},
                {{1, 2, 3, 4}, 4}, {{4, 3, 2, 1}, 4}, {{1, 3, 2, 4}, 5}}) {
            auto values = fixture.first;
            require(mab::find_counted_sorter("merge_sort").sort(values) == fixture.second,
                    "manually verified Merge Sort comparison count changed");
            auto expected = fixture.first;
            std::sort(expected.begin(), expected.end());
            require(values == expected, "Merge Sort exact-count fixture not sorted");
        }
        require(mab::counted_sorters().front().name == "std_sort", "counted default changed");
        bool rejected = false;
        try { (void)mab::find_counted_sorter("unknown"); }
        catch (const std::invalid_argument&) { rejected = true; }
        require(rejected, "unknown counted sorter accepted");
        std::cout << "Passed " << checked << " comparison differential/reset/repetition inputs across "
                  << mab::counted_sorters().size() << " sorters; six exact QuickSort and eleven exact Merge Sort fixtures, "
                     "radix unsupported, comparator isolation/overflow and counted heapsort fallback passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
