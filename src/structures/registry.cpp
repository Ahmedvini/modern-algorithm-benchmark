#include "structures/btree.hpp"
#include "structures/skip_list.hpp"
#include <stdexcept>
#include <string>

namespace mab {
namespace {
std::unique_ptr<OrderedIndex> skip(std::uint64_t seed) { return std::make_unique<SkipList>(seed); }
template<std::size_t M> std::unique_ptr<OrderedIndex> tree(std::uint64_t) { return std::make_unique<BTree>(M); }
}
const std::array<IndexFactory,5>& index_factories() noexcept {
    static constexpr std::array<IndexFactory,5> factories{{{"skip_list",skip},{"btree_m10",tree<10>},
        {"btree_m16",tree<16>},{"btree_m32",tree<32>},{"btree_m64",tree<64>}}};
    return factories;
}
const IndexFactory& find_index_factory(std::string_view name) {
    for (const auto& factory : index_factories()) if (factory.name == name) return factory;
    throw std::invalid_argument("unknown structure: "+std::string(name));
}
}  // namespace mab
