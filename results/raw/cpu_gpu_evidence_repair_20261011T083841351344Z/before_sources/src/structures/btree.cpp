#include "structures/btree.hpp"
#include <functional>
#include <limits>
#include <stdexcept>
#include <vector>

namespace mab {
struct BTree::Node {
    struct Entry { Key key; std::size_t value; };
    std::vector<Entry> entries;
    std::vector<std::unique_ptr<Node>> children;
    explicit Node(std::size_t order) { entries.reserve(order-1); children.reserve(order); }
    bool leaf() const noexcept { return children.empty(); }
};
BTree::BTree(std::size_t order) : order_(order) {
    if (order < 4 || order > 64 || order % 2) throw std::invalid_argument("B-tree order must be even in [4,64]");
}
BTree::~BTree() = default; // Balanced depth bounds recursive ownership destruction.
std::optional<std::size_t> BTree::find(Key key) const noexcept {
    auto node = root_.get();
    while (node) {
        std::size_t i = 0;
        while (i < node->entries.size() && node->entries[i].key < key) ++i;
        if (i < node->entries.size() && node->entries[i].key == key) return node->entries[i].value;
        node = node->leaf() ? nullptr : node->children[i].get();
    }
    return std::nullopt;
}
void BTree::split_child(Node& parent, std::size_t index, std::unique_ptr<Node> sibling) {
    if (splits_ == std::numeric_limits<std::size_t>::max()) throw std::length_error("B-tree split count overflow");
    auto& left = *parent.children[index];
    const auto t = order_/2;
    const auto median = left.entries[t-1];
    for (std::size_t i = t; i < left.entries.size(); ++i) sibling->entries.push_back(left.entries[i]);
    if (!left.leaf()) {
        for (std::size_t i = t; i < left.children.size(); ++i) sibling->children.push_back(std::move(left.children[i]));
        left.children.resize(t);
    }
    left.entries.resize(t-1);
    // All vector capacity and allocations were acquired before mutation.
    parent.entries.insert(parent.entries.begin()+static_cast<std::ptrdiff_t>(index), median);
    parent.children.insert(parent.children.begin()+static_cast<std::ptrdiff_t>(index+1), std::move(sibling));
    ++splits_;
}
void BTree::insert_nonfull(Node& node, Key key, std::size_t value) {
    std::size_t i = 0;
    while (i < node.entries.size() && node.entries[i].key < key) ++i;
    if (node.leaf()) {
        node.entries.insert(node.entries.begin()+static_cast<std::ptrdiff_t>(i), Node::Entry{key,value});
        return;
    }
    if (node.children[i]->entries.size() == order_-1) {
        auto sibling = std::make_unique<Node>(order_);
        split_child(node, i, std::move(sibling));
        if (node.entries[i].key < key) ++i;
    }
    insert_nonfull(*node.children[i], key, value);
}
bool BTree::insert(Key key, std::size_t value) {
    if (find(key)) return false; // optional(0) is present; duplicates never split.
    if (size_ == std::numeric_limits<std::size_t>::max()) throw std::length_error("B-tree size overflow");
    if (!root_) root_ = std::make_unique<Node>(order_);
    if (root_->entries.size() == order_-1) {
        if (splits_ == std::numeric_limits<std::size_t>::max()) throw std::length_error("B-tree split count overflow");
        auto parent = std::make_unique<Node>(order_);
        auto sibling = std::make_unique<Node>(order_);
        parent->children.push_back(std::move(root_));
        split_child(*parent, 0, std::move(sibling));
        root_ = std::move(parent);
    }
    insert_nonfull(*root_, key, value); ++size_; return true;
}
std::size_t BTree::height() const noexcept {
    std::size_t h = 0;
    for (auto n = root_.get(); n; n = n->leaf() ? nullptr : n->children[0].get()) ++h;
    return h;
}
bool BTree::validate() const {
    if (!root_) return size_ == 0;
    std::size_t count = 0;
    std::optional<std::size_t> leaf_depth;
    std::function<bool(const Node&, bool, std::optional<Key>, std::optional<Key>, std::size_t)> visit;
    visit = [&](const Node& n, bool root, std::optional<Key> low, std::optional<Key> high, std::size_t depth) {
        if (n.entries.empty() || n.entries.size() > order_-1 || (!root && n.entries.size() < order_/2-1)) return false;
        if (n.entries.size() > size_-count) return false;
        count += n.entries.size();
        for (std::size_t i = 0; i < n.entries.size(); ++i) {
            const auto key = n.entries[i].key;
            if ((low && !(*low < key)) || (high && !(key < *high)) || (i && !(n.entries[i-1].key < key))) return false;
        }
        if (n.leaf()) {
            if (leaf_depth && *leaf_depth != depth) return false;
            leaf_depth = depth; return true;
        }
        if (n.children.size() != n.entries.size()+1 || n.children.size() > order_) return false;
        for (std::size_t i = 0; i < n.children.size(); ++i) {
            if (!n.children[i] || !visit(*n.children[i], false, i ? std::optional<Key>(n.entries[i-1].key) : low,
                    i < n.entries.size() ? std::optional<Key>(n.entries[i].key) : high, depth+1)) return false;
        }
        return true;
    };
    return visit(*root_, true, std::nullopt, std::nullopt, 0) && count == size_;
}
}  // namespace mab
