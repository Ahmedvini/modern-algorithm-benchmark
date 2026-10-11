#pragma once

#include "common/types.hpp"

#include <cstdint>
#include <limits>
#include <stdexcept>

namespace mab::detail {
// Copies refer to the same run-local counter. No counter survives the run.
class CountingLess {
public:
    explicit CountingLess(std::uint64_t& count) noexcept : count_(&count) {}

    bool operator()(Key left, Key right) const {
        if (*count_ == std::numeric_limits<std::uint64_t>::max())
            throw std::overflow_error("key comparison counter overflow");
        ++*count_;
        return left < right;
    }

private:
    std::uint64_t* count_;
};
}  // namespace mab::detail
