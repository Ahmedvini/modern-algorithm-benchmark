#include "algorithms/radixsort.hpp"

#include <array>
#include <limits>
#include <utility>

namespace mab {
namespace {
static_assert(std::numeric_limits<Key>::is_signed && std::numeric_limits<Key>::digits == 31 &&
              std::numeric_limits<std::uint32_t>::digits == 32,
              "radix_sort requires signed int32 keys and unsigned uint32 words");

std::size_t digit(Key key, unsigned int shift) noexcept {
    // Conversion to unsigned is modulo 2^32, defined even for INT32_MIN.
    // Flipping bit 31 maps signed ascending order to unsigned ascending order.
    const auto ordered = static_cast<std::uint32_t>(key) ^ std::uint32_t{0x80000000U};
    return static_cast<std::size_t>((ordered >> shift) & std::uint32_t{255});
}
}  // namespace

void radix_sort(Values& values) {
    if (values.size() < 2) return;
    Values buffer(values.size());
    auto* source = &values;
    auto* destination = &buffer;
    for (unsigned int shift = 0; shift < 32; shift += 8) {
        std::array<std::size_t, 256> positions{};
        for (const auto key : *source) ++positions[digit(key, shift)];
        std::size_t prefix = 0;
        for (auto& position : positions) {
            const auto count = position;
            position = prefix;
            prefix += count;
        }
        // Forward scatter into exclusive prefixes preserves each digit's order.
        for (const auto key : *source)
            (*destination)[positions[digit(key, shift)]++] = key;
        std::swap(source, destination);
    }
    // Four passes place the result back in values; no conversion back from an
    // out-of-range unsigned key is needed because we scatter original Key values.
}
}  // namespace mab
