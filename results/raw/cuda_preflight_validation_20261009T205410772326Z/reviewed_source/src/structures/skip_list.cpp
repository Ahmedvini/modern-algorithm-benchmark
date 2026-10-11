#include "structures/skip_list.hpp"
#include <limits>
#include <stdexcept>
#include <unordered_set>

namespace mab {
struct SkipList::Node {
    Key key;
    std::size_t value;
    std::vector<Node*> next;
    Node(Key k, std::size_t v, std::size_t height) : key(k), value(v), next(height, nullptr) {}
};
SkipList::SkipList(std::uint64_t seed) : engine_(seed) {}
SkipList::~SkipList() = default; // Independent owners, no recursive link destruction.
std::size_t SkipList::size() const noexcept { return nodes_.size(); }
std::optional<std::size_t> SkipList::find(Key key) const noexcept {
    const Node* current = nullptr;
    for (std::size_t level = max_levels; level-- > 0;) {
        auto next = current ? current->next[level] : head_[level];
        while (next && next->key < key) { current = next; next = current->next[level]; }
    }
    const auto candidate = current ? current->next[0] : head_[0];
    return candidate && candidate->key == key ? std::optional<std::size_t>(candidate->value) : std::nullopt;
}
bool SkipList::insert(Key key, std::size_t value) {
    std::array<Node*, max_levels> previous{};
    Node* current = nullptr;
    for (std::size_t level = max_levels; level-- > 0;) {
        auto next = current ? current->next[level] : head_[level];
        while (next && next->key < key) { current = next; next = current->next[level]; }
        previous[level] = current;
    }
    const auto candidate = current ? current->next[0] : head_[0];
    if (candidate && candidate->key == key) return false;
    if (size() == std::numeric_limits<std::size_t>::max()) throw std::length_error("skip list size overflow");
    std::size_t height = 1;
    while (height < max_levels && (engine_() & 1U)) ++height;
    auto owner = std::make_unique<Node>(key, value, height);
    auto node = owner.get();
    nodes_.push_back(std::move(owner)); // No links changed until ownership succeeds.
    for (std::size_t level = 0; level < height; ++level) {
        auto& link = previous[level] ? previous[level]->next[level] : head_[level];
        node->next[level] = link; link = node;
    }
    return true;
}
std::size_t SkipList::levels() const noexcept {
    std::size_t result = 0;
    for (std::size_t i = 0; i < max_levels; ++i) if (head_[i]) result = i+1;
    return result;
}
std::uint64_t SkipList::shape_fingerprint() const noexcept {
    std::uint64_t hash = 14695981039346656037ULL;
    for (auto n = head_[0]; n; n = n->next[0]) {
        const auto word = static_cast<std::uint32_t>(n->key);
        for (unsigned i = 0; i < 4; ++i) { hash ^= (word >> (8*i)) & 255U; hash *= 1099511628211ULL; }
        hash ^= n->next.size(); hash *= 1099511628211ULL;
    }
    return hash;
}
bool SkipList::validate() const {
    std::unordered_set<const Node*> owned;
    for (const auto& n : nodes_) {
        if (!n || n->next.empty() || n->next.size() > max_levels || !owned.insert(n.get()).second) return false;
    }
    std::vector<const Node*> base;
    for (const Node* n = head_[0]; n;) {
        if (!owned.count(n) || base.size() >= size() || (!base.empty() && !(base.back()->key < n->key))) return false;
        base.push_back(n); n = n->next[0];
    }
    if (base.size() != size()) return false;
    for (std::size_t level = 1; level < max_levels; ++level) {
        const Node* current = head_[level];
        for (const auto n : base) if (n->next.size() > level) {
            if (current != n) return false;
            current = n->next[level];
        }
        if (current) return false;
    }
    return true;
}
}  // namespace mab
