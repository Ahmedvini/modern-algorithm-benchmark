#include "algorithms/cuda_sorting.hpp"
#include "benchmark/cuda_timing.hpp"
#include "benchmark/timing.hpp"
#include "benchmark/output.hpp"
#include "benchmark_build.hpp"
#include "cuda_benchmark_build.hpp"
#include <algorithm>
#include <charconv>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <sstream>
#include <stdexcept>
namespace fs = std::filesystem;
namespace {
template<class T> T number(std::string_view text) {
    T n{}; const auto r = std::from_chars(text.data(), text.data() + text.size(), n);
    if (text.empty() || r.ec != std::errc{} || r.ptr != text.data() + text.size())
        throw std::invalid_argument("expected unsigned decimal: " + std::string(text));
    return n;
}
std::ofstream file(const fs::path& p) {
    std::ofstream out; out.exceptions(std::ios::badbit | std::ios::failbit);
    out.imbue(std::locale::classic()); out.open(p, std::ios::binary); return out;
}
void json(const fs::path& p, const std::string& value) { auto f = file(p); f << value << '\n'; f.close(); }
std::string decimal(double value) {
    std::ostringstream s; s.imbue(std::locale::classic());
    s << std::setprecision(std::numeric_limits<double>::max_digits10) << value; return s.str();
}
}
int main(int argc, char** argv) {
    fs::path output; bool owns = false;
    try {
        mab::TimingConfig config; std::string distribution = "uniform", run_id;
        bool validation_only = false;
        std::vector<std::string> invocation;
        for (int i = 0; i < argc; ++i) invocation.emplace_back(argv[i]);
        for (int i = 1; i < argc; ++i) {
            const std::string_view option(argv[i]);
            if (option == "--help") {
                std::cout << "cuda_sort_benchmark --output NEW_DIRECTORY [--size N] [--seed S]\n"
                    "[--distribution uniform|sorted|reverse_sorted|duplicate_heavy|nearly_sorted|signed_edges]\n"
                    "[--sort cub_radix_sort] [--swaps K] [--distinct K] [--warmups W] [--repetitions R]\n"
                    "[--memory-limit-mib M] [--run-id ID] [--validation-only] [--list-sorts]\n"
                    "Defaults N1000/S1729/uniform/W1/R5/M256; size capped at1M. Prepared-buffer timing.\n";
                return 0;
            }
            if (option == "--list-sorts") { std::cout << "cub_radix_sort\n"; return 0; }
            if (option == "--validation-only") { validation_only = true; continue; }
            if (option != "--output" && option != "--size" && option != "--seed" &&
                option != "--distribution" && option != "--swaps" && option != "--distinct" &&
                option != "--warmups" && option != "--repetitions" && option != "--memory-limit-mib" &&
                option != "--run-id" && option != "--sort") throw std::invalid_argument("unknown option");
            if (++i == argc) throw std::invalid_argument("missing option value");
            const std::string_view value(argv[i]);
            if (option == "--output") output = std::string(value);
            else if (option == "--size") config.dataset.size = number<std::size_t>(value);
            else if (option == "--seed") config.dataset.seed = number<std::uint64_t>(value);
            else if (option == "--distribution") distribution = value;
            else if (option == "--swaps") config.dataset.nearly_sorted_swaps = number<std::size_t>(value);
            else if (option == "--distinct") config.dataset.duplicate_cardinality = number<std::uint64_t>(value);
            else if (option == "--warmups") config.warmups = number<std::size_t>(value);
            else if (option == "--repetitions") config.repetitions = number<std::size_t>(value);
            else if (option == "--memory-limit-mib") config.memory_limit_mib = number<std::size_t>(value);
            else if (option == "--run-id") run_id = value;
            else (void)mab::find_cuda_sorter(value);
        }
        config.sorted_input = distribution == "sorted";
        if (!config.sorted_input && distribution != "signed_edges")
            config.dataset.distribution = mab::parse_distribution(distribution);
        mab::validate_timing_config(config);
        if (config.dataset.size > (static_cast<std::uint64_t>(config.memory_limit_mib) * 1024 * 1024) / (5 * sizeof(mab::Key)))
            throw std::invalid_argument("host payload budget exceeded");
        if (config.dataset.size > 1000000) throw std::invalid_argument("milestone size cap is1000000");
        if (output.empty()) throw std::invalid_argument("--output is required");
        if (!validation_only && (std::string_view(mab::build::configuration) != "Release" || mab::build::sanitizers))
            throw std::invalid_argument("performance requires unsanitized Release");
        if (run_id.empty()) run_id = output.filename().string();
        if (run_id.empty()) throw std::invalid_argument("empty run identifier");
        if (!fs::create_directory(output)) throw std::runtime_error("output already exists");
        owns = true;
        auto original = mab::make_timing_input(config);
        if (distribution == "signed_edges") {
            const mab::Key lo = std::numeric_limits<mab::Key>::min(), hi = std::numeric_limits<mab::Key>::max();
            const mab::Key pattern[]{lo, hi, -1, 0, 1, lo + 1, hi - 1, 0};
            for (std::size_t i = 0; i < original.size(); ++i) original[i] = pattern[i % 8];
        }
        auto expected = original; std::sort(expected.begin(), expected.end());
        mab::Values working(original.size());
        mab::CudaTimingSession session(original.size(), config.memory_limit_mib);
        const auto& info = session.info();
        const auto hash = std::to_string(mab::input_fingerprint(original));
        const auto swaps = distribution == "signed_edges" ? 0 : mab::timing_swaps(config);
        std::ostringstream meta; meta.imbue(std::locale::classic()); meta << '{';
        bool first = true;
        auto field = [&](const std::string& key, const std::string& value) {
            if (!first) meta << ',';
            first = false; meta << mab::json_string(key) << ':' << value;
        };
        auto text = [&](const std::string& key, const std::string& value) { field(key, mab::json_string(value)); };
        auto integer = [&](const std::string& key, std::uint64_t value) { field(key, std::to_string(value)); };
        integer("schema_version", 1); text("protocol", "cuda_sort_timing_v1"); text("run_id", run_id);
        text("algorithm", "cub_radix_sort"); text("implementation_version", "cub_radix_sort_v1");
        text("run_kind", validation_only ? "validation" : "performance");
        text("distribution", distribution); integer("size", original.size()); integer("seed", config.dataset.seed);
        integer("nearly_sorted_swaps", swaps); integer("duplicate_cardinality", config.dataset.duplicate_cardinality);
        text("dataset_generator", distribution == "signed_edges" ? "signed_edges_v1" : "mt19937_64_v1");
        text("input_hash_fnv1a64", hash); integer("warmups", config.warmups); integer("repetitions", config.repetitions);
        integer("expected_rows", config.warmups + config.repetitions); text("elapsed_unit", "ns");
        text("allocation_policy", "prepared_pinned_reuse_v1"); text("stream_policy", "private_nonblocking_serial");
        text("end_to_end_clock", "steady_clock"); text("phase_clock", "cuda_event_float_ms_to_ns");
        integer("memory_limit_mib", config.memory_limit_mib); integer("workspace_bytes", info.workspace_bytes);
        integer("requested_device", info.device); integer("actual_device", info.device); text("gpu_name", info.device_name);
        integer("compute_major", info.compute_major); integer("compute_minor", info.compute_minor);
        integer("device_memory_bytes", info.device_memory_bytes); integer("runtime_api_version", info.runtime_version);
        integer("driver_api_version", info.driver_version); integer("cub_version", mab::cuda_sort_cub_version());
        text("compiler_id", mab::build::compiler_id); text("compiler_version", mab::build::compiler_version);
        text("build_type", mab::build::configuration); field("sanitizers", mab::build::sanitizers ? "true" : "false");
        text("platform", mab::build::platform); text("architecture", mab::build::architecture);
        text("cuda_compiler_version", mab::cuda_build::compiler_version); text("cuda_toolkit_version", mab::cuda_build::toolkit_version);
        text("cuda_flags", mab::cuda_build::flags); text("cuda_release_flags", mab::cuda_build::release_flags);
        text("cuda_architectures", mab::cuda_build::architectures);
        std::ostringstream args; args << '[';
        for (std::size_t i = 0; i < invocation.size(); ++i) { if (i) args << ','; args << mab::json_string(invocation[i]); }
        args << ']'; field("invocation", args.str()); meta << '}'; json(output / "run.json", meta.str());
        for (const auto name : {"CMakeCache.txt", "compile_commands.json"})
            fs::copy_file(fs::path(mab::build::binary_dir) / name, output / name);
        fs::copy_file(fs::path(mab::build::source_dir) / "third_party/cub/UPSTREAM.json", output / "cub_upstream.json");
        fs::copy_file(fs::path(mab::build::source_dir) / "third_party/cub/LICENSE", output / "cub_LICENSE");
        fs::copy_file(fs::path(mab::build::binary_dir) / "generated" / mab::build::configuration / "source_hashes.json",
                      output / "cpu_source_hashes.json");
        auto csv = file(output / "trials.csv");
        mab::write_csv_row(csv, {"schema_version","protocol","run_id","algorithm","implementation_version",
            "distribution","size","seed","nearly_sorted_swaps","duplicate_cardinality","dataset_generator",
            "input_hash_fnv1a64","phase","trial_index","h2d_ns","device_sort_ns","d2h_ns","end_to_end_ns",
            "elapsed_unit","status","correctness","error"});
        std::size_t rows = 0;
        for (const std::string phase : {"warmup", "measure"}) {
            const auto count = phase == "warmup" ? config.warmups : config.repetitions;
            for (std::size_t i = 0; i < count; ++i) {
                mab::CudaTimingSample sample; std::string error, status = "ok", correctness = "passed";
                try { sample = session.sample(original, working); }
                catch (const std::exception& failure) { error = failure.what(); status = "error"; correctness = "not_checked"; }
                if (status == "ok" && working != expected) { status = "error"; correctness = "failed"; error = "output differs from std::sort"; }
                const bool ok = status == "ok";
                mab::write_csv_row(csv, {"1","cuda_sort_timing_v1",run_id,"cub_radix_sort","cub_radix_sort_v1",
                    distribution,std::to_string(original.size()),std::to_string(config.dataset.seed),std::to_string(swaps),
                    std::to_string(config.dataset.duplicate_cardinality),distribution == "signed_edges" ? "signed_edges_v1" : "mt19937_64_v1",
                    hash,phase,std::to_string(i),ok ? decimal(sample.h2d_ns) : "",ok ? decimal(sample.device_sort_ns) : "",
                    ok ? decimal(sample.d2h_ns) : "",ok ? std::to_string(sample.end_to_end_ns) : "","ns",status,correctness,error});
                csv.flush(); ++rows;
                if (!ok) throw std::runtime_error(error);
            }
        }
        csv.close(); session.close();
        json(output / "COMPLETE.json", "{\"schema_version\":1,\"complete\":true,\"rows\":" + std::to_string(rows) + "}");
        std::cout << "Completed " << config.repetitions << " measured and " << config.warmups << " warmup trials\n";
        return 0;
    } catch (const std::exception& error) {
        if (owns) { try { json(output / "FAILED.json", "{\"complete\":false,\"error\":" + mab::json_string(error.what()) + "}"); } catch (...) {} }
        std::cerr << "error: " << error.what() << '\n'; return 1;
    }
}
