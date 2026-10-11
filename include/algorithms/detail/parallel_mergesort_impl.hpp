#pragma once
#include "algorithms/parallel_mergesort.hpp"
#include <algorithm>
#include <functional>
#include <omp.h>
#include <stdexcept>
#include <type_traits>

namespace mab::detail {
struct NoParallelObserver {
    void task(std::size_t, std::size_t) const noexcept {}
    void merge(std::size_t, std::size_t, std::size_t) const noexcept {}
};
struct ParallelKeyLess {
    bool operator()(Key a, Key b) const noexcept { return a < b; }
};
template<class Less, class Observer>
void merge_range(Values& values, Values& buffer, std::size_t begin,
                 std::size_t middle, std::size_t end, Less less, Observer observer) noexcept {
    observer.merge(begin, middle, end);
    auto left=begin, right=middle, out=begin;
    while (left<middle && right<end) {
        if (less(values[right], values[left])) buffer[out++]=values[right++];
        else buffer[out++]=values[left++];
    }
    while (left<middle) buffer[out++]=values[left++];
    while (right<end) buffer[out++]=values[right++];
    std::copy(buffer.begin()+begin, buffer.begin()+end, values.begin()+begin);
}
template<class Less, class Observer>
void serial_range(Values& values, Values& buffer, std::size_t begin,
                  std::size_t end, Less less, Observer observer) noexcept {
    const auto size=end-begin;
    for (std::size_t width=1; width<size;) {
        for (auto first=begin; first<end;) {
            const auto middle=first+std::min(width,end-first);
            const auto last=middle+std::min(width,end-middle);
            merge_range(values,buffer,first,middle,last,less,observer);
            first=last;
        }
        if (width>=size-width) break;
        width*=2;
    }
}
template<class Less, class Observer>
void task_range(Values& values, Values& buffer, std::size_t begin,
                std::size_t end, Less less, Observer observer) noexcept {
    if (end-begin<=parallel_merge_grain) {
        serial_range(values,buffer,begin,end,less,observer);
        return;
    }
    const auto middle=begin+(end-begin)/2;
    #pragma omp task default(none) shared(values,buffer) firstprivate(begin,middle,less,observer)
    {
        observer.task(begin,middle);
        task_range(values,buffer,begin,middle,less,observer);
    }
    #pragma omp task default(none) shared(values,buffer) firstprivate(middle,end,less,observer)
    {
        observer.task(middle,end);
        task_range(values,buffer,middle,end,less,observer);
    }
    #pragma omp taskwait
    merge_range(values,buffer,begin,middle,end,less,observer);
}
template<class Less=ParallelKeyLess, class Observer=NoParallelObserver>
ParallelSortInfo parallel_merge_sort_impl(Values& values, int threads,
                                          Less less=Less{}, Observer observer=Observer{}) {
    static_assert(std::is_nothrow_invocable_r_v<bool,Less,Key,Key>);
    static_assert(std::is_nothrow_copy_constructible_v<Less> && std::is_nothrow_copy_constructible_v<Observer>);
    static_assert(noexcept(observer.task(0,0)) && noexcept(observer.merge(0,0,0)));
    if (threads<1 || threads>64) throw std::invalid_argument("threads must be in [1,64]");
    if (omp_get_level()>0) throw std::invalid_argument("nested OpenMP sorting is unsupported");
    if (values.size()<2) return {};
    Values buffer(values.size()); // All user allocation happens before tasks/mutation.
    if (threads==1 || values.size()<parallel_merge_threshold) {
        serial_range(values,buffer,0,values.size(),less,observer);
        return {};
    }
    int actual=1;
    #pragma omp parallel num_threads(threads) default(none) shared(values,buffer,actual) firstprivate(less,observer)
    {
        #pragma omp single
        {
            actual=omp_get_num_threads();
            task_range(values,buffer,0,values.size(),less,observer);
        }
    }
    return {actual,true};
}
} // namespace mab::detail
