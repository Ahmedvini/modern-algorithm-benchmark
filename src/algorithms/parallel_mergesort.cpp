#include "algorithms/detail/parallel_mergesort_impl.hpp"
#include "algorithms/mergesort.hpp"
#include <stdexcept>
#include <string>

namespace mab {
ParallelSortInfo parallel_merge_sort(Values& values, int threads) {
    return detail::parallel_merge_sort_impl(values,threads);
}
namespace {
ParallelSortInfo sequential(Values& values,int) { merge_sort(values); return {}; }
}
const std::array<ConfiguredSorter,2>& parallel_sorters() noexcept {
    static const std::array<ConfiguredSorter,2> registry{{
        {"merge_sort",sequential,1},{"parallel_merge_sort",parallel_merge_sort,1}}};
    return registry;
}
ConfiguredSorter find_parallel_sorter(std::string_view name,int threads) {
    if (threads<1 || threads>64) throw std::invalid_argument("threads must be in [1,64]");
    for (auto sorter:parallel_sorters()) if (sorter.name==name) {
        sorter.threads=name=="merge_sort"?1:threads;
        return sorter;
    }
    throw std::invalid_argument("unknown configured sorter: "+std::string(name));
}
} // namespace mab
