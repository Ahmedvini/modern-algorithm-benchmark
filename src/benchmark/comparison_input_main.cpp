#include "benchmark/comparison.hpp"
#include "benchmark/output.hpp"
#include <charconv>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>

namespace {
template<class T> T number(const std::string& s) {
    T value{}; auto result = std::from_chars(s.data(), s.data() + s.size(), value);
    if (s.empty() || result.ec != std::errc{} || result.ptr != s.data() + s.size())
        throw std::invalid_argument("expected unsigned decimal");
    return value;
}
}
int main(int argc, char** argv) {
    try {
        std::map<std::string,std::string> args;
        for (int i = 1; i < argc; i += 2) {
            if (i + 1 == argc || !args.emplace(argv[i],argv[i+1]).second) throw std::invalid_argument("invalid arguments");
        }
        for (const auto& arg : args)
            if (arg.first != "--output" && arg.first != "--size" && arg.first != "--seed" &&
                arg.first != "--distribution" && arg.first != "--swaps" && arg.first != "--distinct")
                throw std::invalid_argument("unknown argument");
        mab::TimingConfig config;
        config.dataset.size = number<std::size_t>(args.at("--size"));
        config.dataset.seed = number<std::uint64_t>(args.at("--seed"));
        config.dataset.nearly_sorted_swaps = number<std::size_t>(args.at("--swaps"));
        config.dataset.duplicate_cardinality = number<std::uint64_t>(args.at("--distinct"));
        const auto& distribution = args.at("--distribution");
        const auto values = mab::make_comparison_input(config, distribution);
        const std::filesystem::path output(args.at("--output"));
        if (!std::filesystem::create_directory(output)) throw std::runtime_error("output exists");
        std::ofstream binary(output / "input.bin",std::ios::binary);
        mab::write_comparison_input(values,binary); binary.close();
        if (!binary) throw std::runtime_error("input close failed");
        std::ofstream meta(output / "input.json");
        meta << "{\"size\":" << values.size() << ",\"seed\":" << config.dataset.seed
             << ",\"distribution\":" << mab::json_string(distribution)
             << ",\"dataset_generator\":" << mab::json_string(distribution == "signed_edges" ? "signed_edges_v1" : "mt19937_64_v1")
             << ",\"nearly_sorted_swaps\":" << *config.dataset.nearly_sorted_swaps
             << ",\"duplicate_cardinality\":" << config.dataset.duplicate_cardinality
             << ",\"input_hash_fnv1a64\":" << mab::json_string(std::to_string(mab::input_fingerprint(values))) << "}\n";
        meta.close(); if (!meta) throw std::runtime_error("input metadata write failed");
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
