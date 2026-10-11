#include "indexes/learned_index.hpp"
#include "benchmark/search_timing.hpp"
#include "benchmark/search_comparisons.hpp"
#include "benchmark/output.hpp"
#include "benchmark/memory.hpp"

#include <algorithm>
#include <charconv>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <locale>
#include <memory>

namespace fs = std::filesystem;
namespace {
using Clock = std::chrono::steady_clock;
static_assert(Clock::is_steady, "monotonic clock required");
template<class T> T number(std::string_view text) {
    T value{};
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), value);
    if (text.empty() || text.front() < '0' || text.front() > '9' || parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size())
        throw std::invalid_argument("expected unsigned decimal integer");
    return value;
}
std::ofstream file(const fs::path& path) {
    std::ofstream result;
    result.exceptions(std::ios::badbit | std::ios::failbit);
    result.imbue(std::locale::classic());
    result.open(path, std::ios::binary);
    return result;
}
std::string position(mab::SearchResult result) { return result ? std::to_string(*result) : ""; }
std::uint64_t elapsed(Clock::time_point start, Clock::time_point stop) {
    const auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
    if (ns < 0) throw std::runtime_error("negative monotonic duration");
    return static_cast<std::uint64_t>(ns);
}
}

int main(int argc, char** argv) {
    fs::path output;
    bool owns = false;
    try {
        mab::SearchConfig config;
        config.categories = {"mixed_50"};
        for (int i = 1; i < argc; ++i) {
            const std::string option(argv[i]);
            if (option == "--help") {
                std::cout << "learned_index_benchmark --output NEW_DIR [--size N] [--seed S] [--distribution NAME]\n"
                             "Protocol learned_rank_v1: 1000 queries, query seed2718, warmups1, repetitions5, radius32.\n";
                return 0;
            }
            if (option != "--output" && option != "--size" && option != "--seed" && option != "--distribution")
                throw std::invalid_argument("unknown option: " + option);
            if (++i == argc) throw std::invalid_argument("missing option value");
            const std::string_view value(argv[i]);
            if (option == "--output") output = value;
            else if (option == "--size") config.timing.dataset.size = number<std::size_t>(value);
            else if (option == "--seed") config.timing.dataset.seed = number<std::uint64_t>(value);
            else config.timing.dataset.distribution = mab::parse_distribution(value);
        }
        if (output.empty() || config.timing.dataset.size == 0 || config.timing.dataset.size > 1000000)
            throw std::invalid_argument("output required; size in [1,1000000]");
        mab::validate_search_config(config);
#if !defined(NDEBUG) || defined(MAB_LEARNED_SANITIZERS)
        throw std::invalid_argument("timing requires Release without sanitizers");
#endif
        if (!fs::create_directory(output)) throw std::runtime_error("output already exists");
        owns = true;
        auto values = mab::generate_dataset(config.timing.dataset);
        std::sort(values.begin(), values.end());
        const auto batches = mab::make_search_batches(values, config);
        if (batches.size() != 1 || !batches[0].unavailable_reason.empty()) throw std::runtime_error("query batch unavailable");
        const auto& queries = batches[0].queries;
        const auto hits = std::count_if(queries.begin(), queries.end(), [](const auto& q) { return q.expected_position.has_value(); });
        if (hits != 500 || queries.size() != 1000) throw std::runtime_error("hit/miss contract mismatch");
        auto metadata = file(output / "run.json");
        metadata << "{\"schema_version\":1,\"protocol\":\"learned_rank_v1\",\"size\":" << values.size()
                 << ",\"seed\":" << config.timing.dataset.seed << ",\"distribution\":"
                 << mab::json_string(mab::distribution_name(config.timing.dataset.distribution))
                 << ",\"input_fingerprint\":\"" << mab::input_fingerprint(values)
                 << "\",\"query_fingerprint\":\"" << mab::query_fingerprint(queries)
                 << "\",\"query_seed\":2718,\"queries\":1000,\"hits\":500,\"misses\":500,\"warmups\":1,\"repetitions\":5,\"radius\":32,"
                    "\"compiler\":" << mab::json_string(__VERSION__) << ",\"build_type\":\"Release\",\"clock\":\"steady_clock\"}\n";
        metadata.close();
        auto trials = file(output / "trials.csv");
        mab::write_csv_row(trials, {"algorithm", "operation", "phase", "trial_index", "execution_order", "elapsed_ns", "queries", "correctness"});
        std::vector<mab::SearchResult> answers(queries.size());
        std::size_t rows = 0;
        for (const auto& phase : {std::string("warmup"), std::string("measure")}) {
            const auto repetitions = phase == "warmup" ? 1U : 5U;
            for (std::size_t trial = 0; trial < repetitions; ++trial) {
                const auto build_start = Clock::now();
                const auto index = std::make_unique<mab::LearnedIndex>(values);
                const auto build_stop = Clock::now();
                mab::write_csv_row(trials, {"learned_rank", "build", phase, std::to_string(trial), "0",
                    std::to_string(elapsed(build_start, build_stop)), "0", "passed"});
                ++rows;
                const auto offset = (config.timing.dataset.seed % 2 + trial % 2) % 2;
                for (std::size_t order = 0; order < 2; ++order) {
                    const bool learned = (offset + order) % 2 == 1;
                    // Select dispatch outside the timed interval. Result stores and loop are inside.
                    const auto start = Clock::now();
                    if (learned) for (std::size_t q = 0; q < queries.size(); ++q) answers[q] = index->find(queries[q].target);
                    else for (std::size_t q = 0; q < queries.size(); ++q) answers[q] = mab::binary_search(values, queries[q].target);
                    const auto stop = Clock::now();
                    bool correct = true;
                    for (std::size_t q = 0; q < queries.size(); ++q) if (answers[q] != queries[q].expected_position) correct = false;
                    mab::write_csv_row(trials, {learned ? "learned_rank" : "binary_search", "lookup_batch", phase,
                        std::to_string(trial), std::to_string(order), std::to_string(elapsed(start, stop)), "1000", correct ? "passed" : "failed"});
                    trials.flush(); ++rows;
                    if (!correct) throw std::runtime_error("query output differs from oracle");
                }
            }
        }
        trials.close();
        const mab::LearnedIndex index(values);
        auto diagnostics = file(output / "diagnostics.csv");
        mab::write_csv_row(diagnostics, {"query_id", "target", "expected_position", "actual_position", "predicted_position",
            "lower_bound_position", "correction_distance", "fallback", "learned_comparisons", "binary_comparisons"});
        for (std::size_t q = 0; q < queries.size(); ++q) {
            const auto diagnostic = index.diagnose(queries[q].target);
            const auto binary = mab::counted_search("binary_search", values, queries[q].target);
            if (diagnostic.result != queries[q].expected_position || binary.position != diagnostic.result)
                throw std::runtime_error("untimed comparison result mismatch");
            mab::write_csv_row(diagnostics, {std::to_string(q), std::to_string(queries[q].target), position(queries[q].expected_position),
                position(diagnostic.result), std::to_string(diagnostic.predicted_position), std::to_string(diagnostic.lower_bound_position),
                std::to_string(diagnostic.correction_distance), diagnostic.fallback ? "true" : "false",
                std::to_string(diagnostic.comparisons), std::to_string(binary.key_comparisons)});
        }
        diagnostics.close();
        auto memory = file(output / "memory.json");
        memory << "{\"owned_capacity_bytes\":" << index.owned_capacity_bytes() << ",\"object_bytes\":" << sizeof(index)
               << ",\"process_lifetime_peak\":";
        mab::write_memory_json(memory, mab::process_memory());
        memory << "}\n"; memory.close();
        auto complete = file(output / "COMPLETE.json");
        complete << "{\"complete\":true,\"rows\":" << rows << ",\"diagnostic_queries\":1000}\n";
        complete.close();
        std::cout << "Completed " << rows << " rows (15 measured, 3 warmup), 1000 untimed query diagnostics: " << output << '\n';
        return 0;
    } catch (const std::exception& error) {
        if (owns) { try { auto failed = file(output / "FAILED.json"); failed << "{\"error\":" << mab::json_string(error.what()) << "}\n"; } catch (...) {} }
        std::cerr << error.what() << '\n'; return 1;
    }
}
