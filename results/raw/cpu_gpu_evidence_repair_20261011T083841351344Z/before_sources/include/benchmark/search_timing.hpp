#pragma once
#include "algorithms/searching.hpp"
#include "benchmark/timing.hpp"
#include <array>

namespace mab {
const std::array<std::string_view, 9>& query_categories() noexcept;
struct SearchConfig {
    TimingConfig timing;
    std::uint64_t query_seed = 2718;
    std::size_t batch_size = 1000;
    std::vector<std::string> categories; // Empty selects all, in fixed category order.
};
struct SearchQuery {
    Key target;
    SearchResult selected_position;
    SearchResult expected_position;
};
struct SearchBatch {
    std::string category;
    std::string unavailable_reason;
    std::vector<SearchQuery> queries;
};
void validate_search_config(const SearchConfig& config);
std::uint64_t query_fingerprint(const std::vector<SearchQuery>& queries) noexcept;
std::vector<SearchBatch> make_search_batches(const Values& sorted, const SearchConfig& config);
struct SearchTrial {
    std::string_view algorithm, category, phase;
    std::size_t trial_index, execution_order;
    std::optional<std::uint64_t> elapsed_ns;
    std::string_view status, correctness;
    std::string error;
};
// Validates sorted data and every expected answer before timing. Result buffer
// allocation and validation/sink occur outside timing; loop/dispatch/stores inside.
bool run_search_trials(const Values& sorted, const SearchConfig& config,
                       const std::vector<SearchBatch>& batches, const std::vector<Searcher>& algorithms,
                       const std::function<void(const SearchTrial&)>& sink);
}  // namespace mab
