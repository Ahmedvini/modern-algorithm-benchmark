#pragma once
#include "benchmark/search_timing.hpp"
#include "structures/ordered_index.hpp"

namespace mab {
struct StructureConfig {
    SearchConfig search;
    std::uint64_t structure_seed = 1729;
};
struct IndexEntry { Key key; std::size_t value; };
struct StructureWorkload {
    Values original, sorted;
    std::vector<IndexEntry> entries;
    std::vector<SearchBatch> batches;
    std::size_t unique_keys;
};
void validate_structure_config(const StructureConfig& config);
StructureWorkload make_structure_workload(Values original, const StructureConfig& config);
struct StructureTrial {
    std::string_view algorithm, operation, category, phase;
    std::size_t trial_index, execution_order;
    std::optional<std::uint64_t> elapsed_ns;
    std::string_view status, correctness;
    std::string error;
};
// Construction includes constructor/insertion; lookup uses the freshly built
// structure. Destruction, full oracle/invariant validation and sink are outside.
bool run_structure_trials(const StructureWorkload& workload, const StructureConfig& config,
                          const std::vector<IndexFactory>& factories,
                          const std::function<void(const StructureTrial&)>& sink);
}  // namespace mab
