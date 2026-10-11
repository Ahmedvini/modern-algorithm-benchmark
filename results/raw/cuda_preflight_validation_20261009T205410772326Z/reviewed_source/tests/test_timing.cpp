#include "benchmark/timing.hpp"
#include "benchmark/output.hpp"
#include "test_support.hpp"

#include <algorithm>
#include <exception>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>

namespace {
mab::Values required_input;
std::size_t restored_calls = 0;
void checking_sort(mab::Values& values) {
    require(values == required_input, "sorter did not receive the original ordered input");
    ++restored_calls;
    std::sort(values.begin(), values.end());
}
void broken_sort(mab::Values&) {}
void throwing_sort(mab::Values&) { throw std::runtime_error("sort error, \"quoted\"\nline"); }
}  // namespace

int main() {
    try {
        std::size_t inputs = 0, trials = 0;
        for (const auto distribution : {mab::Distribution::uniform, mab::Distribution::nearly_sorted,
                mab::Distribution::reverse_sorted, mab::Distribution::duplicate_heavy}) {
            for (const auto seed : {std::uint64_t{0}, std::uint64_t{1729}, std::numeric_limits<std::uint64_t>::max()}) {
                for (const std::size_t size : {0, 1, 2, 31, 64, 257}) {
                    mab::TimingConfig config;
                    config.dataset.size = size;
                    config.dataset.seed = seed;
                    config.dataset.distribution = distribution;
                    config.repetitions = 2;
                    config.warmups = 1;
                    const auto original = mab::make_timing_input(config);
                    require(original == mab::make_timing_input(config) && original == mab::generate_dataset(config.dataset),
                            "timing input does not preserve generator v1");
                    require(mab::input_fingerprint(original) == mab::input_fingerprint(mab::make_timing_input(config)),
                            "input fingerprint not reproducible");
                    const std::vector<mab::Sorter> sorters{mab::sorters().begin(), mab::sorters().end()};
                    require(mab::run_timing_trials(original, config, sorters, [&](const mab::TimingTrial& row) {
                        require(row.status == "ok" && row.correctness == "passed" && row.elapsed_ns.has_value(),
                                "registered sorter failed timing validation");
                        require(row.execution_order < sorters.size(), "invalid execution order");
                        ++trials;
                    }), "timing engine failed");
                    ++inputs;
                    config.sorted_input = true;
                    auto expected = original;
                    // Sorted alias always uses the corresponding uniform sample.
                    auto uniform = config.dataset;
                    uniform.distribution = mab::Distribution::uniform;
                    expected = mab::generate_dataset(uniform);
                    std::sort(expected.begin(), expected.end());
                    require(mab::make_timing_input(config) == expected && mab::timing_swaps(config) == 0,
                            "sorted benchmark distribution constructed incorrectly");
                }
            }
        }
        mab::TimingConfig config;
        config.dataset.size = 5;
        config.repetitions = 3;
        config.warmups = 2;
        required_input = {9, -1, 4, 0, -7};
        const auto saved = required_input;
        std::vector<mab::TimingTrial> rows;
        require(mab::run_timing_trials(required_input, config,
                {{"first", checking_sort}, {"second", checking_sort}},
                [&](const mab::TimingTrial& row) { rows.push_back(row); }), "restore test failed");
        require(required_input == saved && restored_calls == 10 && rows.size() == 10, "input mutated or trials omitted");
        require(rows[0].algorithm == "second" && rows[2].algorithm == "first" && rows[4].phase == "measure",
                "seed-offset cyclic schedule/warmup separation changed");
        rows.clear();
        require(!mab::run_timing_trials(required_input, config, {{"broken", broken_sort}},
                [&](const mab::TimingTrial& row) { rows.push_back(row); }) && rows.size() == 1 &&
                rows[0].status == "error" && rows[0].correctness == "failed" && rows[0].elapsed_ns,
                "incorrect sorting was marked successful or not fail-fast");
        rows.clear();
        require(!mab::run_timing_trials(required_input, config, {{"throwing", throwing_sort}},
                [&](const mab::TimingTrial& row) { rows.push_back(row); }) && rows.size() == 1 &&
                rows[0].correctness == "not_checked" && !rows[0].elapsed_ns && !rows[0].error.empty(),
                "sort exception not recorded");
        for (const auto kind : {0, 1, 2, 3}) {
            auto invalid = config;
            if (kind == 0) invalid.repetitions = 0;
            if (kind == 1) invalid.warmups = 1001;
            if (kind == 2) invalid.memory_limit_mib = 0;
            if (kind == 3) invalid.dataset.size = std::numeric_limits<std::size_t>::max();
            bool rejected = false;
            try { mab::validate_timing_config(invalid); } catch (const std::invalid_argument&) { rejected = true; }
            require(rejected, "invalid benchmark config accepted");
        }
        require(mab::csv_field("plain") == "plain" && mab::csv_field("a,b") == "\"a,b\"" &&
                mab::csv_field("a\"b") == "\"a\"\"b\"" && mab::csv_field("a\nb") == "\"a\nb\"",
                "CSV field escaping changed");
        require(mab::json_string("a\"\\\n") == "\"a\\\"\\\\\\u000a\"", "JSON escaping changed");
        std::ostringstream csv;
        mab::write_csv_row(csv, {"", "a,b", "a\"b", "line\r\nend"});
        require(csv.str() == ",\"a,b\",\"a\"\"b\",\"line\r\nend\"\n", "CSV row formatting changed");
        std::cout << "Passed " << inputs << " reproducible distribution/seed/size inputs and " << trials
                  << " validated registry trials; sorted aliases, exact input restoration/order, failures, bounds and escaping passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
