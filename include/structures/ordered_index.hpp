#pragma once
#include "common/types.hpp"
#include <array>
#include <memory>
#include <optional>
#include <string_view>

namespace mab {
// Ordered int32 -> size_t map. Duplicate insert preserves the first payload.
// No update/erase; instances own storage, return values, and are noncopyable.
class OrderedIndex {
public:
    OrderedIndex() = default;
    virtual ~OrderedIndex() = default;
    OrderedIndex(const OrderedIndex&) = delete;
    OrderedIndex& operator=(const OrderedIndex&) = delete;
    OrderedIndex(OrderedIndex&&) = delete;
    OrderedIndex& operator=(OrderedIndex&&) = delete;
    virtual bool insert(Key key, std::size_t value) = 0;
    virtual std::optional<std::size_t> find(Key key) const noexcept = 0;
    virtual std::size_t size() const noexcept = 0;
    // Diagnostic traversal outside timing; allocation failures may propagate.
    virtual bool validate() const = 0;
};
struct IndexFactory {
    std::string_view name;
    std::unique_ptr<OrderedIndex> (*create)(std::uint64_t seed);
};
const std::array<IndexFactory, 5>& index_factories() noexcept;
const IndexFactory& find_index_factory(std::string_view name);
}  // namespace mab
