#include "benchmark/timing.hpp"
#include "benchmark/output.hpp"
#include "benchmark_build.hpp"

#include <charconv>
#include <chrono>
#include <exception>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>

namespace fs = std::filesystem;
namespace {
template <typename T> T number(std::string_view text) {
    T result{};
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), result);
    if (text.empty() || parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size())
        throw std::invalid_argument("expected unsigned decimal integer: " + std::string(text));
    return result;
}

std::ofstream new_file(const fs::path& path) {
    std::ofstream stream;
    stream.exceptions(std::ios::failbit | std::ios::badbit);
    stream.imbue(std::locale::classic());
    stream.open(path, std::ios::binary);
    return stream;
}

void json_file(const fs::path& path, const std::string& content) {
    auto stream = new_file(path);
    stream << content << '\n';
    stream.close();
}

std::string optional_text(const fs::path& path) {
    std::ifstream stream(path, std::ios::binary);
    if (!stream) return {};
    return std::string(std::istreambuf_iterator<char>(stream), std::istreambuf_iterator<char>());
}

std::vector<mab::Sorter> selected_sorters(std::string_view names) {
    if (names == "all") return {mab::sorters().begin(), mab::sorters().end()};
    std::vector<mab::Sorter> selected;
    while (true) {
        const auto comma = names.find(',');
        const auto& sorter = mab::find_sorter(names.substr(0, comma));
        for (const auto& prior : selected)
            if (prior.name == sorter.name) throw std::invalid_argument("duplicate sorter");
        selected.push_back(sorter);
        if (comma == std::string_view::npos) break;
        names.remove_prefix(comma + 1);
    }
    return selected;
}

void usage() {
    std::cout << "Usage: sort_benchmark --output NEW_DIRECTORY [--sort NAME[,NAME...]|all]\n"
                 "  [--size N] [--seed S] [--distribution uniform|sorted|reverse_sorted|duplicate_heavy|nearly_sorted]\n"
                 "  [--swaps K] [--distinct K] [--repetitions R] [--warmups W]\n"
                 "  [--memory-limit-mib M] [--run-id ID] [--validation-only] [--list-sorts] [--help]\n"
                 "Defaults: std_sort, size=1000, seed=1729, uniform, R=5, W=1, M=256.\n"
                 "Performance runs require Release without sanitizers. Output must not exist.\n";
}
}  // namespace

int main(int argc, char** argv) {
    fs::path output;
    bool owns_output = false;
    try {
        mab::TimingConfig config;
        std::string sorter_names = "std_sort", run_id;
        bool validation_only = false;
        std::vector<std::string> invocation;
        for (int i = 0; i < argc; ++i) invocation.emplace_back(argv[i]);
        for (int i = 1; i < argc; ++i) {
            const std::string_view option(argv[i]);
            if (option == "--help") { usage(); return 0; }
            if (option == "--list-sorts") {
                for (const auto& sorter : mab::sorters()) std::cout << sorter.name << '\n';
                return 0;
            }
            if (option == "--validation-only") { validation_only = true; continue; }
            if (option != "--output" && option != "--sort" && option != "--size" && option != "--seed" &&
                option != "--distribution" && option != "--swaps" && option != "--distinct" &&
                option != "--repetitions" && option != "--warmups" && option != "--memory-limit-mib" && option != "--run-id")
                throw std::invalid_argument("unknown option: " + std::string(option));
            if (++i == argc) throw std::invalid_argument("missing value for " + std::string(option));
            const std::string_view value(argv[i]);
            if (option == "--output") output = std::string(value);
            else if (option == "--sort") { (void)selected_sorters(value); sorter_names = value; }
            else if (option == "--size") config.dataset.size = number<std::size_t>(value);
            else if (option == "--seed") config.dataset.seed = number<std::uint64_t>(value);
            else if (option == "--distribution") {
                config.sorted_input = value == "sorted";
                if (!config.sorted_input) config.dataset.distribution = mab::parse_distribution(value);
            } else if (option == "--swaps") config.dataset.nearly_sorted_swaps = number<std::size_t>(value);
            else if (option == "--distinct") config.dataset.duplicate_cardinality = number<std::uint64_t>(value);
            else if (option == "--repetitions") config.repetitions = number<std::size_t>(value);
            else if (option == "--warmups") config.warmups = number<std::size_t>(value);
            else if (option == "--memory-limit-mib") config.memory_limit_mib = number<std::size_t>(value);
            else run_id = value;
        }
        mab::validate_timing_config(config);
        const auto selected = selected_sorters(sorter_names);
        if (output.empty()) throw std::invalid_argument("--output NEW_DIRECTORY is required");
        if (!validation_only && (std::string_view(mab::build::configuration) != "Release" || mab::build::sanitizers))
            throw std::invalid_argument("performance requires Release without sanitizers; use --validation-only for tests");
        if (run_id.empty()) run_id = output.filename().string();
        if (run_id.empty()) throw std::invalid_argument("empty run identifier");
        // Atomic directory creation provides portable exclusive result ownership.
        if (!fs::create_directory(output)) throw std::runtime_error("output already exists: " + output.string());
        owns_output = true;
        const auto original = mab::make_timing_input(config);
        const auto hash = std::to_string(mab::input_fingerprint(original));
        const std::string run_kind = validation_only ? "validation" : "performance";
        const auto measured_rows = config.repetitions * selected.size();
        const auto warmup_rows = config.warmups * selected.size();
        const auto started = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
        bool commands_copied = false;
        const fs::path commands = fs::path(mab::build::binary_dir) / "compile_commands.json";
        if (fs::exists(commands)) {
            fs::copy_file(commands, output / "compile_commands.json");
            commands_copied = true;
        }
        for (const auto name : {"pdqsort", "timsort"})
            fs::copy_file(fs::path(mab::build::binary_dir) / (std::string(name) + "_upstream.json"),
                          output / (std::string(name) + "_upstream.json"));
        fs::copy_file(fs::path(mab::build::binary_dir) / "generated" / mab::build::configuration / "source_hashes.json",
                      output / "source_hashes.json");
        const auto cache = fs::path(mab::build::binary_dir) / "CMakeCache.txt";
        if (fs::exists(cache)) fs::copy_file(cache, output / "CMakeCache.txt");
        std::ostringstream metadata;
        metadata.imbue(std::locale::classic());
        metadata << "{\"schema_version\":1,\"protocol\":\"sort_timing_v1\",\"run_id\":" << mab::json_string(run_id)
                 << ",\"run_kind\":" << mab::json_string(run_kind) << ",\"started_unix_seconds\":" << started
                 << ",\"size\":" << config.dataset.size << ",\"seed\":" << config.dataset.seed
                 << ",\"distribution\":" << mab::json_string(mab::timing_distribution(config))
                 << ",\"nearly_sorted_swaps\":" << mab::timing_swaps(config)
                 << ",\"duplicate_cardinality\":" << config.dataset.duplicate_cardinality
                 << ",\"dataset_generator\":\"mt19937_64_v1\",\"input_hash_fnv1a64\":" << mab::json_string(hash)
                 << ",\"repetitions\":" << config.repetitions << ",\"warmups\":" << config.warmups
                 << ",\"expected_measured_rows\":" << measured_rows << ",\"expected_warmup_rows\":" << warmup_rows
                 << ",\"memory_limit_mib\":" << config.memory_limit_mib
                 << ",\"planned_array_workspace_bytes\":" << static_cast<std::uint64_t>(original.size()) * 4 * sizeof(mab::Key)
                 << ",\"clock\":\"steady_clock\",\"clock_period_num\":" << std::chrono::steady_clock::period::num
                 << ",\"clock_period_den\":" << std::chrono::steady_clock::period::den
                 << ",\"elapsed_unit\":\"ns\",\"order_policy\":\"seed_offset_cyclic_v1\",\"compiler_id\":"
                 << mab::json_string(mab::build::compiler_id) << ",\"compiler_version\":" << mab::json_string(mab::build::compiler_version)
                 << ",\"compiler_path\":" << mab::json_string(mab::build::compiler_path)
                 << ",\"build_type\":" << mab::json_string(mab::build::configuration)
                 << ",\"sanitizers\":" << (mab::build::sanitizers ? "true" : "false") << ",\"cplusplus\":" << __cplusplus
                 << ",\"cmake_global_flags\":" << mab::json_string(mab::build::global_flags)
                 << ",\"cmake_configuration_flags\":" << mab::json_string(mab::build::configuration_flags)
                 << ",\"compile_commands_available\":" << (commands_copied ? "true" : "false")
                 << ",\"platform\":" << mab::json_string(mab::build::platform)
                 << ",\"architecture\":" << mab::json_string(mab::build::architecture)
                 << ",\"logical_cpu_count_hint\":" << std::thread::hardware_concurrency()
                 << ",\"linux_cpuinfo\":" << mab::json_string(optional_text("/proc/cpuinfo"))
                 << ",\"linux_meminfo\":" << mab::json_string(optional_text("/proc/meminfo"))
                 << ",\"algorithms\":[";
        for (std::size_t i = 0; i < selected.size(); ++i) {
            if (i) metadata << ',';
            metadata << mab::json_string(selected[i].name);
        }
        metadata << "],\"invocation\":[";
        for (std::size_t i = 0; i < invocation.size(); ++i) {
            if (i) metadata << ',';
            metadata << mab::json_string(invocation[i]);
        }
        metadata << "]}";
        json_file(output / "run.json", metadata.str());
        auto csv = new_file(output / "trials.csv");
        mab::write_csv_row(csv, {"schema_version", "protocol", "run_id", "run_kind", "algorithm", "distribution",
            "size", "seed", "nearly_sorted_swaps", "duplicate_cardinality", "dataset_generator", "input_hash_fnv1a64",
            "phase", "trial_index", "execution_order", "elapsed_ns", "elapsed_unit", "status", "correctness", "error",
            "repetitions", "warmups", "compiler_id", "compiler_version", "build_type", "sanitizers", "platform", "architecture"});
        std::size_t actual_rows = 0;
        const auto completed = mab::run_timing_trials(original, config, selected, [&](const mab::TimingTrial& row) {
            mab::write_csv_row(csv, {"1", "sort_timing_v1", run_id, run_kind, std::string(row.algorithm),
                std::string(mab::timing_distribution(config)), std::to_string(original.size()), std::to_string(config.dataset.seed),
                std::to_string(mab::timing_swaps(config)), std::to_string(config.dataset.duplicate_cardinality), "mt19937_64_v1", hash,
                std::string(row.phase), std::to_string(row.trial_index), std::to_string(row.execution_order),
                row.elapsed_ns ? std::to_string(*row.elapsed_ns) : "", "ns", std::string(row.status), std::string(row.correctness), row.error,
                std::to_string(config.repetitions), std::to_string(config.warmups), mab::build::compiler_id, mab::build::compiler_version,
                mab::build::configuration, mab::build::sanitizers ? "true" : "false", mab::build::platform, mab::build::architecture});
            csv.flush();
            ++actual_rows;
        });
        csv.close();
        if (!completed) throw std::runtime_error("sort failed; inspect retained trials.csv");
        if (actual_rows != measured_rows + warmup_rows) throw std::runtime_error("incomplete trial count");
        json_file(output / "COMPLETE.json", "{\"schema_version\":1,\"complete\":true,\"rows\":" + std::to_string(actual_rows) + "}");
        std::cout << "Completed " << measured_rows << " measured trials; raw data: " << (output / "trials.csv") << '\n';
        return 0;
    } catch (const std::exception& error) {
        if (owns_output) {
            try { json_file(output / "FAILED.json", "{\"complete\":false,\"error\":" + mab::json_string(error.what()) + "}"); }
            catch (...) { /* The stderr error and absent completion marker remain authoritative. */ }
        }
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
