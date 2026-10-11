#include "algorithms/mergesort.hpp"
#include "algorithms/detail/mergesort_impl.hpp"
#include "test_integer_sorts.hpp"

#include <exception>
#include <iostream>

int main() {
    try {
        const auto checked = check_integer_sort("merge_sort", &mab::merge_sort);
        // Distinguishable int32 keys in equal-comparator groups verify the
        // internal stable merge policy without changing the public element type.
        mab::Values groups{11, 21, 10, 20, 12, 22, 13};
        mab::detail::merge_sort_impl(groups, [](mab::Key a, mab::Key b) { return a / 10 < b / 10; });
        require(groups == mab::Values({11, 10, 12, 13, 21, 20, 22}), "equal-group merge order is not stable");
        std::cout << "Passed " << checked
                  << " Merge Sort differential cases through public/registry/repeated paths; stable merge fixture passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
