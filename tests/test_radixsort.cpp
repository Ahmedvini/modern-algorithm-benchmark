#include "algorithms/radixsort.hpp"
#include "test_integer_sorts.hpp"

#include <exception>
#include <iostream>

int main() {
    try {
        const auto checked = check_integer_sort("radix_sort", &mab::radix_sort);
        std::cout << "Passed " << checked
                  << " Signed Radix Sort differential cases through public/registry/repeated paths\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
