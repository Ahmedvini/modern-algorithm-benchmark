#pragma once

#include <stdexcept>
#include <string>

inline void require(bool condition, const std::string& message) {
    // Unlike assert(), this remains active in Release builds with NDEBUG.
    if (!condition) {
        throw std::runtime_error(message);
    }
}
