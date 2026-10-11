#include "benchmark/cuda_timing.hpp"
#include "benchmark/output.hpp"
#include "datasets/generator.hpp"
#include "test_support.hpp"
#include <cuda_runtime_api.h>
#include <algorithm>
#include <iostream>
#include <limits>

// Deliberately no sample(), clocks, benchmark runner, warmups or metric output.
int main() {
    int devices = 0;
    if (cudaGetDeviceCount(&devices) != cudaSuccess || devices == 0) {
        std::cerr << "Prepared CUDA correctness unavailable\n";
        return 77;
    }
    std::size_t inputs = 0, checks = 0, rejected = 0;
    try {
        auto reject = [&](auto operation) {
            bool failed = false;
            try { operation(); } catch (const std::invalid_argument&) { failed = true; }
            require(failed, "invalid prepared operation was accepted");
            ++rejected;
        };
        auto check = [&](const mab::Values& input) {
            auto expected = input;
            std::sort(expected.begin(), expected.end());
            mab::CudaTimingSession session(input.size(), 256);
            mab::Values output(input.size());
            session.execute_untimed(input, output);
            require(output == expected, "prepared result differs from std::sort"); ++checks;
            require(input.size() == expected.size(), "input length changed");
            mab::CudaTimingSession other(5, 256);
            mab::Values small{4, -1, 0, 4, -2}, small_output(5);
            other.execute_untimed(small, small_output);
            require(small_output == mab::Values({-2,-1,0,4,4}), "interleaved session failed"); ++checks;
            other.close();
            session.execute_untimed(input, output);
            require(output == expected, "repeated prepared call failed"); ++checks;
            auto alias = input;
            reject([&] { session.execute_untimed(alias, alias); });
            mab::Values wrong(input.size() + 1);
            reject([&] { session.execute_untimed(input, wrong); });
            session.close();
            reject([&] { session.execute_untimed(input, output); });
            ++inputs;
        };
        const auto lo = std::numeric_limits<mab::Key>::min(), hi = std::numeric_limits<mab::Key>::max();
        for (const auto& v : std::vector<mab::Values>{{}, {lo}, {hi}, {1,0}, {1,1},
             {hi,lo,0,-1,1,lo+1,hi-1,lo,hi}, {-8,-2,-9,-1}}) check(v);
        for (auto distribution : {mab::Distribution::uniform, mab::Distribution::nearly_sorted,
                                  mab::Distribution::reverse_sorted, mab::Distribution::duplicate_heavy})
            for (std::uint64_t seed : {42ULL,1729ULL})
                for (std::size_t n : {0,1,2,31,32,33,255,256,257,1023,1024,1025,65537}) {
                    mab::DatasetConfig config; config.size=n; config.seed=seed; config.distribution=distribution;
                    auto v=mab::generate_dataset(config); check(v);
                    if (distribution == mab::Distribution::uniform) {
                        std::sort(v.begin(),v.end()); check(v);
                        check(mab::Values(n,-7));
                    }
                }
        std::cout << "{\"schema_version\":1,\"artifact_kind\":\"correctness_validation\","
                     "\"scope\":\"prepared_cuda_untimed_v1\",\"study_eligible\":false,\"status\":\"passed\","
                     "\"inputs\":" << inputs << ",\"output_checks\":" << checks
                  << ",\"invalid_operations_rejected\":" << rejected << ",\"failures\":0}\n";
        return 0;
    } catch (const std::exception& e) {
        std::cout << "{\"status\":\"failed\",\"inputs_completed\":" << inputs
                  << ",\"output_checks\":" << checks << ",\"error\":" << mab::json_string(e.what()) << "}\n";
        return 1;
    }
}
