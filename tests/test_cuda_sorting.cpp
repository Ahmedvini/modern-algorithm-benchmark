#include "algorithms/cuda_sorting.hpp"
#include "datasets/generator.hpp"
#include "test_support.hpp"
#include <cuda_runtime_api.h>
#include <algorithm>
#include <iostream>
#include <limits>
#include <stdexcept>

int main() {
    int count = 0;
    const auto available = cudaGetDeviceCount(&count);
    if (available != cudaSuccess || count == 0) {
        std::cerr << "CUDA sorting unavailable: " << cudaGetErrorString(available) << '\n';
        return 77;
    }
    std::size_t cases = 0, checks = 0;
    try {
        const auto check = [&](const mab::Values& input) {
            auto expected = input;
            std::sort(expected.begin(), expected.end());
            auto actual = input;
            mab::cub_radix_sort(actual);
            require(actual == expected, "public CUB sorter differs from std::sort");
            ++checks;
            actual = input;
            mab::find_cuda_sorter("cub_radix_sort").sort(actual);
            require(actual == expected, "registered CUB sorter differs from std::sort");
            ++checks;
            // A different-size invocation between repetitions checks workspace isolation.
            mab::Values other{4, -1, 0, 4, -2};
            mab::cub_radix_sort(other);
            require(other == mab::Values({-2, -1, 0, 4, 4}), "interleaved CUB call failed");
            ++checks;
            actual = input;
            mab::cub_radix_sort(actual);
            require(actual == expected, "repeated CUB sort differs from std::sort");
            ++checks;
            ++cases;
        };
        const auto low = std::numeric_limits<mab::Key>::min();
        const auto high = std::numeric_limits<mab::Key>::max();
        for (const auto& input : std::vector<mab::Values>{
                 {}, {0}, {-1}, {low}, {high}, {1, 2}, {2, 1}, {1, 1},
                 {high, low, 0, -1, 1, low + 1, high - 1, low, high},
                 {-9, -1, -5, low}, {high, 9, 1, 5}, {0, 0, 0, 0}})
            check(input);
        std::size_t combinations = 1;
        for (std::size_t n = 0; n <= 4; ++n) {
            for (std::size_t code = 0; code < combinations; ++code) {
                auto remaining = code;
                mab::Values input(n);
                for (auto& key : input) {
                    key = static_cast<mab::Key>(remaining % 3) - 1;
                    remaining /= 3;
                }
                check(input);
            }
            combinations *= 3;
        }
        for (const auto distribution : {mab::Distribution::uniform, mab::Distribution::nearly_sorted,
                                       mab::Distribution::reverse_sorted, mab::Distribution::duplicate_heavy})
            for (const std::uint64_t seed : {0ULL, 42ULL, 1729ULL})
                for (const std::size_t n : {0, 1, 2, 3, 31, 32, 33, 255, 256, 257,
                                           1023, 1024, 1025, 4095, 4096, 4097, 65535, 65536, 65537}) {
                    mab::DatasetConfig config;
                    config.size = n; config.seed = seed; config.distribution = distribution;
                    const auto input = mab::generate_dataset(config);
                    check(input);
                    if (distribution == mab::Distribution::uniform) {
                        auto ascending = input;
                        std::sort(ascending.begin(), ascending.end());
                        check(ascending);
                        check(mab::Values(n, -7));
                    }
                }
        bool rejected = false;
        try { (void)mab::find_cuda_sorter("std_sort"); }
        catch (const std::invalid_argument&) { rejected = true; }
        require(rejected, "CUDA registry silently accepts a CPU algorithm");
        int runtime = 0, driver = 0, device = 0;
        require(cudaRuntimeGetVersion(&runtime) == cudaSuccess, "runtime version failed");
        require(cudaDriverGetVersion(&driver) == cudaSuccess, "driver version failed");
        require(cudaGetDevice(&device) == cudaSuccess, "current device failed");
        cudaDeviceProp prop{};
        require(cudaGetDeviceProperties(&prop, device) == cudaSuccess, "device properties failed");
        // GPU names are emitted by the preflight JSON; keep this record free of unchecked strings.
        std::cout << "{\"schema_version\":1,\"protocol\":\"cuda_sort_correctness_v2\","
                     "\"algorithm\":\"cub_radix_sort\",\"implementation_version\":\""
                  << mab::cuda_sort_version << "\",\"status\":\"ok\",\"cases\":" << cases
                  << ",\"output_checks\":" << checks << ",\"cub_version\":" << mab::cuda_sort_cub_version()
                  << ",\"runtime_api_version\":" << runtime << ",\"driver_api_version\":" << driver
                  << ",\"device\":" << device << ",\"compute_major\":" << prop.major
                  << ",\"compute_minor\":" << prop.minor << "}\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "CUDA sorting failed after " << cases << " complete cases: " << error.what() << '\n';
        return 1;
    }
}
