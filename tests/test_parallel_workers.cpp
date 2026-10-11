#include "algorithms/parallel_mergesort.hpp"
#include "algorithms/mergesort.hpp"
#include "benchmark/output.hpp"
#include "datasets/generator.hpp"
#include "benchmark_build.hpp"
#include "parallel_build.hpp"
#include "test_support.hpp"
#include <omp.h>
#include <algorithm>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <limits>

int main(int argc, char** argv) {
    try {
        require(argc == 1, "worker diagnostic accepts no workload configuration");
        std::cout << "{\"schema_version\":1,\"artifact_kind\":\"correctness_validation\","
                     "\"scope\":\"openmp_workers_untimed_v1\",\"study_eligible\":false,\"executable\":"
                  << mab::json_string(std::filesystem::canonical(argv[0]).string())
                  << ",\"build_type\":" << mab::json_string(mab::build::configuration)
                  << ",\"compiler\":" << mab::json_string(mab::build::compiler_version)
                  << ",\"flags\":" << mab::json_string(mab::build::configuration_flags)
                  << ",\"sanitizers\":" << (mab::build::sanitizers?"true":"false")
                  << ",\"openmp_version\":" << mab::json_string(mab::parallel_build::version)
                  << ",\"openmp_flags\":" << mab::json_string(mab::parallel_build::flags)
                  << ",\"runtime_dynamic\":" << omp_get_dynamic()
                  << ",\"runtime_thread_limit\":" << omp_get_thread_limit()
                  << ",\"requested_threads\":2,\"team_size_is_task_participation\":false,\"environment\":{";
        bool first=true;
        for (auto name : {"OMP_NUM_THREADS","OMP_DYNAMIC","OMP_THREAD_LIMIT","OMP_MAX_ACTIVE_LEVELS","OMP_PROC_BIND","OMP_WAIT_POLICY"}) {
            if (!first) std::cout << ',';
            first=false;
            const char* value=std::getenv(name);
            std::cout << mab::json_string(name) << ':' << (value?mab::json_string(value):"null");
        }
        std::cout << "},\"calls\":[";
        first=true;
        std::size_t checks=0;
        for (std::size_t n : {0,1,32767,32768,32769,65537}) {
            mab::DatasetConfig c; c.size=n; c.seed=1729;
            auto input=mab::generate_dataset(c);
            if (n>1) { input[0]=std::numeric_limits<mab::Key>::min(); input[1]=std::numeric_limits<mab::Key>::max(); }
            if (n>4) { input[2]=0; input[3]=0; input[4]=-1; }
            auto expected=input; std::sort(expected.begin(),expected.end());
            auto sequential=input; mab::merge_sort(sequential);
            require(sequential==expected,"sequential oracle differs");
            for (bool registry : {false,true}) {
                auto actual=input;
                mab::ParallelSortInfo info;
                if (registry) {
                    const auto sorter=mab::find_parallel_sorter("parallel_merge_sort",2);
                    info=sorter.sort(actual,sorter.threads);
                } else info=mab::parallel_merge_sort(actual,2);
                require(actual==expected,"parallel output differs from CPU oracle");
                const bool parallel=n>=mab::parallel_merge_threshold;
                require(info.parallel_region==parallel && info.actual_threads==(parallel?2:1),"runtime team/threshold gate failed");
                if (!first) std::cout << ',';
                first=false;
                std::cout << "{\"size\":" << n << ",\"registry\":" << (registry?"true":"false")
                          << ",\"actual_team_size\":" << info.actual_threads
                          << ",\"parallel_region\":" << (info.parallel_region?"true":"false") << ",\"correctness\":true}";
                ++checks;
            }
        }
        std::cout << "],\"output_checks\":" << checks << ",\"status\":\"passed\"}\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Untimed worker diagnostic failed: " << e.what() << '\n'; return 1;
    }
}
