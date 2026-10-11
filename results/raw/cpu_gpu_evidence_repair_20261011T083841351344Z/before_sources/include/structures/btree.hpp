#pragma once
#include "structures/ordered_index.hpp"

namespace mab {
class BTree final : public OrderedIndex {
public:
    // Even maximum child count M, 4..64; minimum degree is M/2.
    explicit BTree(std::size_t order = 16);
    ~BTree() override;
    bool insert(Key key, std::size_t value) override;
    std::optional<std::size_t> find(Key key) const noexcept override;
    std::size_t size() const noexcept override { return size_; }
    bool validate() const override;
    std::size_t height() const noexcept;
    std::size_t split_count() const noexcept { return splits_; }
private:
    struct Node;
    std::size_t order_, size_ = 0, splits_ = 0;
    std::unique_ptr<Node> root_;
    void split_child(Node& parent, std::size_t index, std::unique_ptr<Node> sibling);
    void insert_nonfull(Node& node, Key key, std::size_t value);
};
}  // namespace mab
