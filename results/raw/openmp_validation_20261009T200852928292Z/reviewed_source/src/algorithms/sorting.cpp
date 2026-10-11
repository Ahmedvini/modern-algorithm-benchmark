#include "algorithms/sorting.hpp"
#include "algorithms/baselines.hpp"
#include "algorithms/quicksort.hpp"
#include "algorithms/pdqsort.hpp"
#include "algorithms/timsort.hpp"
#include "algorithms/mergesort.hpp"
#include "algorithms/radixsort.hpp"

#include <stdexcept>
#include <string>

namespace mab {
const std::array<Sorter, 6>& sorters() noexcept {
    static const std::array<Sorter, 6> registry{{
        {"std_sort", std_sort}, {"quick_sort", quick_sort}, {"pdq_sort", pdq_sort},
        {"tim_sort", tim_sort}, {"merge_sort", merge_sort}, {"radix_sort", radix_sort}}};
    return registry;
}

const Sorter& find_sorter(std::string_view name) {
    for (const auto& sorter : sorters()) {
        if (sorter.name == name) return sorter;
    }
    throw std::invalid_argument("unknown sorter: " + std::string(name));
}
}  // namespace mab
