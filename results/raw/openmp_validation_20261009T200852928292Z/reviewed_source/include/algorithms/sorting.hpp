#pragma once

#include "common/types.hpp"

#include <array>
#include <string_view>

namespace mab {
struct Sorter {
    std::string_view name;
    void (*sort)(Values&);
};

const std::array<Sorter, 6>& sorters() noexcept;
const Sorter& find_sorter(std::string_view name);
}  // namespace mab
