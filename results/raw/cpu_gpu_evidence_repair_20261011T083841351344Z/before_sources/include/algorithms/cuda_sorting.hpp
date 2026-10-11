#pragma once
#include "algorithms/sorting.hpp"

namespace mab {
inline constexpr std::string_view cuda_sort_version = "cub_radix_sort_v1";
// Requires a usable current CUDA device, including for empty/singleton input.
// Full signed-int32 ascending order. Throws on CUDA errors; no CPU fallback.
// Successful checked cleanup precedes host mutation.
void cub_radix_sort(Values& values);
const std::array<Sorter, 1>& cuda_sorters() noexcept;
const Sorter& find_cuda_sorter(std::string_view name);
int cuda_sort_cub_version() noexcept;
} // namespace mab
