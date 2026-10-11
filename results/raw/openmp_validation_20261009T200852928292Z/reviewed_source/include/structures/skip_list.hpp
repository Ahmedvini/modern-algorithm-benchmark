#pragma once
#include "structures/ordered_index.hpp"
#include <random>
#include <vector>

namespace mab {
class SkipList final : public OrderedIndex {
public:
    static constexpr std::size_t max_levels = 32;
    explicit SkipList(std::uint64_t seed = 1729);
    ~SkipList() override;
    bool insert(Key key, std::size_t value) override;
    std::optional<std::size_t> find(Key key) const noexcept override;
    std::size_t size() const noexcept override;
    bool validate() const override;
    std::size_t levels() const noexcept;
    std::uint64_t shape_fingerprint() const noexcept;
private:
    struct Node;
    std::array<Node*, max_levels> head_{};
    std::vector<std::unique_ptr<Node>> nodes_;
    std::mt19937_64 engine_;
};
}  // namespace mab
