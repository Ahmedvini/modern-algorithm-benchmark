cmake_minimum_required(VERSION 3.16)
project(modern_algorithm_benchmark VERSION 0.1.0 LANGUAGES CXX)

option(MAB_ENABLE_SANITIZERS "Enable address and undefined-behavior sanitizers" OFF)
option(MAB_ENABLE_CUDA "Build the optional CUDA readiness probe (no GPU algorithms)" OFF)
option(MAB_ENABLE_CUDA_SORT "Build the separately opted-in CUB correctness adapter" OFF)
if(MAB_ENABLE_CUDA_SORT AND NOT MAB_ENABLE_CUDA)
    message(FATAL_ERROR "MAB_ENABLE_CUDA_SORT requires MAB_ENABLE_CUDA=ON")
endif()
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(mab_core src/algorithms/baselines.cpp src/datasets/generator.cpp
                     src/algorithms/quicksort.cpp src/algorithms/sorting.cpp
                     src/algorithms/pdqsort.cpp src/algorithms/timsort.cpp
                     src/algorithms/mergesort.cpp src/algorithms/radixsort.cpp)
target_include_directories(mab_core PUBLIC include)
target_include_directories(mab_core PRIVATE third_party/pdqsort)
target_include_directories(mab_core PRIVATE third_party/timsort/include)
target_compile_features(mab_core PUBLIC cxx_std_17)
set_target_properties(mab_core PROPERTIES CXX_EXTENSIONS OFF)
if(MSVC)
    target_compile_options(mab_core PUBLIC /W4)
else()
    target_compile_options(mab_core PUBLIC -Wall -Wextra -Wpedantic)
endif()
if(MAB_ENABLE_SANITIZERS)
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang" AND NOT MSVC)
        target_compile_options(mab_core PUBLIC -fsanitize=address,undefined -fno-omit-frame-pointer)
        target_link_options(mab_core PUBLIC -fsanitize=address,undefined)
    else()
        message(FATAL_ERROR "Sanitizers require a supported GCC/Clang toolchain")
    endif()
endif()

add_executable(algorithm_benchmark src/main.cpp)
target_link_libraries(algorithm_benchmark PRIVATE mab_core)

# Metrics are a separate library/executable; normal CLI links only mab_core.
add_library(mab_metrics src/benchmark/comparisons.cpp src/benchmark/memory.cpp
                        src/benchmark/memory_json.cpp)
target_link_libraries(mab_metrics PUBLIC mab_core)
target_include_directories(mab_metrics PRIVATE third_party/pdqsort third_party/timsort/include)
add_executable(sort_metrics src/benchmark/metrics_main.cpp)
target_link_libraries(sort_metrics PRIVATE mab_metrics)

add_library(mab_timing src/benchmark/timing.cpp src/benchmark/output.cpp)
target_link_libraries(mab_timing PUBLIC mab_core)
add_library(mab_comparison src/benchmark/comparison.cpp)
target_link_libraries(mab_comparison PUBLIC mab_timing)
add_executable(comparison_input src/benchmark/comparison_input_main.cpp)
target_link_libraries(comparison_input PRIVATE mab_comparison)
include(cmake/benchmark_metadata.cmake)
add_executable(sort_benchmark src/benchmark/timing_main.cpp)
target_include_directories(sort_benchmark PRIVATE "${CMAKE_BINARY_DIR}/generated/$<CONFIG>")
target_link_libraries(sort_benchmark PRIVATE mab_timing)

# Search is independent of the preserved sorting core and CLIs.
add_library(mab_search src/algorithms/searching.cpp)
target_link_libraries(mab_search PUBLIC mab_core)
add_library(mab_search_metrics src/benchmark/search_comparisons.cpp)
target_link_libraries(mab_search_metrics PUBLIC mab_search)
add_library(mab_search_timing src/benchmark/search_timing.cpp)
target_link_libraries(mab_search_timing PUBLIC mab_search mab_timing)
add_executable(search_benchmark src/benchmark/search_main.cpp)
target_include_directories(search_benchmark PRIVATE "${CMAKE_BINARY_DIR}/generated/$<CONFIG>")
target_link_libraries(search_benchmark PRIVATE mab_search_timing)
add_executable(search_counts src/benchmark/search_main.cpp)
target_compile_definitions(search_counts PRIVATE MAB_SEARCH_COUNTS=1)
target_include_directories(search_counts PRIVATE "${CMAKE_BINARY_DIR}/generated/$<CONFIG>")
target_link_libraries(search_counts PRIVATE mab_search_timing mab_search_metrics)

# Owned ordered structures are separate from preserved array/sorting algorithms.
add_library(mab_structures src/structures/skip_list.cpp src/structures/btree.cpp
                           src/structures/registry.cpp)
target_link_libraries(mab_structures PUBLIC mab_core)
add_library(mab_structure_timing src/benchmark/structure_timing.cpp)
target_link_libraries(mab_structure_timing PUBLIC mab_structures mab_search_timing)
add_executable(structure_benchmark src/benchmark/structure_main.cpp)
target_include_directories(structure_benchmark PRIVATE "${CMAKE_BINARY_DIR}/generated/$<CONFIG>")
target_link_libraries(structure_benchmark PRIVATE mab_structure_timing)

include(CTest)
if(BUILD_TESTING)
    find_package(Python3 REQUIRED COMPONENTS Interpreter)
    add_test(NAME experiment_pipeline
             COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_experiments.py
                     ${CMAKE_BINARY_DIR})
    add_executable(test_structures tests/test_structures.cpp)
    target_link_libraries(test_structures PRIVATE mab_structures)
    add_test(NAME structures COMMAND test_structures)
    add_executable(test_structure_timing tests/test_structure_timing.cpp)
    target_link_libraries(test_structure_timing PRIVATE mab_structure_timing)
    add_test(NAME structure_timing COMMAND test_structure_timing)
    add_test(NAME structure_framework
             COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_structure_benchmark.py
                     $<TARGET_FILE:structure_benchmark>)
    add_executable(test_searching tests/test_searching.cpp)
    target_link_libraries(test_searching PRIVATE mab_search_metrics)
    add_test(NAME searching COMMAND test_searching)
    add_executable(test_search_timing tests/test_search_timing.cpp)
    target_link_libraries(test_search_timing PRIVATE mab_search_timing)
    add_test(NAME search_timing COMMAND test_search_timing)
    add_test(NAME search_framework
             COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_search_benchmark.py
                     $<TARGET_FILE:search_benchmark> $<TARGET_FILE:search_counts>)
    add_executable(test_baselines tests/test_baselines.cpp)
    target_link_libraries(test_baselines PRIVATE mab_core)
    add_test(NAME baselines COMMAND test_baselines)
    add_test(NAME environment_manifest
             COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_environment.py)
    add_test(NAME cuda_preflight
             COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_cuda_preflight.py)
    add_test(NAME cuda_benchmark_analysis COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_cuda_benchmark.py)
    add_test(NAME cuda_sort_handoff
             COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_cuda_sort_handoff.py)
    add_executable(test_datasets tests/test_datasets.cpp)
    target_link_libraries(test_datasets PRIVATE mab_core)
    add_test(NAME datasets COMMAND test_datasets)
    add_test(NAME cli
             COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_cli.py
                     $<TARGET_FILE:algorithm_benchmark>)
    add_executable(test_quicksort tests/test_quicksort.cpp)
    target_link_libraries(test_quicksort PRIVATE mab_core)
    add_test(NAME quicksort COMMAND test_quicksort)
    add_executable(test_pdqsort tests/test_pdqsort.cpp)
    target_link_libraries(test_pdqsort PRIVATE mab_core)
    add_test(NAME pdqsort COMMAND test_pdqsort)
    add_executable(test_timsort tests/test_timsort.cpp)
    target_link_libraries(test_timsort PRIVATE mab_core)
    add_test(NAME timsort COMMAND test_timsort)
    add_executable(test_mergesort tests/test_mergesort.cpp)
    target_link_libraries(test_mergesort PRIVATE mab_core)
    add_test(NAME mergesort COMMAND test_mergesort)
    add_executable(test_radixsort tests/test_radixsort.cpp)
    target_link_libraries(test_radixsort PRIVATE mab_core)
    add_test(NAME radixsort COMMAND test_radixsort)
    add_executable(test_comparisons tests/test_comparisons.cpp)
    target_link_libraries(test_comparisons PRIVATE mab_metrics)
    add_test(NAME comparisons COMMAND test_comparisons)
    add_executable(test_memory tests/test_memory.cpp)
    target_link_libraries(test_memory PRIVATE mab_metrics)
    add_test(NAME memory COMMAND test_memory)
    # Compile the actual portable branch, rather than mock an unsupported result.
    add_executable(test_memory_unsupported tests/test_memory.cpp src/benchmark/memory.cpp
                   src/benchmark/memory_json.cpp)
    target_compile_definitions(test_memory_unsupported PRIVATE MAB_FORCE_UNSUPPORTED_MEMORY=1)
    target_link_libraries(test_memory_unsupported PRIVATE mab_core)
    add_test(NAME memory_unsupported COMMAND test_memory_unsupported)
    add_test(NAME metrics_cli
             COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_metrics_cli.py
                     $<TARGET_FILE:sort_metrics>)
    add_executable(test_timing tests/test_timing.cpp)
    target_link_libraries(test_timing PRIVATE mab_timing)
    add_test(NAME timing COMMAND test_timing)
    add_test(NAME benchmark_framework
             COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_benchmark.py
                     $<TARGET_FILE:sort_benchmark>)
endif()

if(MAB_ENABLE_CUDA)
    include(cmake/cuda.cmake)
endif()

# Optional OpenMP family; original six-entry registry and timing CLIs are unchanged.
option(MAB_ENABLE_OPENMP "Build the separate OpenMP parallel sorting family" ON)
if(MAB_ENABLE_OPENMP)
    find_package(OpenMP REQUIRED COMPONENTS CXX)
    find_package(Threads REQUIRED)
    add_library(mab_parallel src/algorithms/parallel_mergesort.cpp)
    target_link_libraries(mab_parallel PUBLIC mab_core OpenMP::OpenMP_CXX)
    add_library(mab_parallel_timing src/benchmark/parallel_timing.cpp)
    target_link_libraries(mab_parallel_timing PUBLIC mab_parallel mab_timing)
    foreach(pair IN ITEMS OpenMP_CXX_VERSION OpenMP_CXX_FLAGS OpenMP_CXX_LIBRARIES)
        mab_cxx_literal(${pair}_LITERAL "${${pair}}")
    endforeach()
    file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/generated/$<CONFIG>/parallel_build.hpp" CONTENT
"#pragma once
namespace mab::parallel_build {
inline constexpr const char* version = ${OpenMP_CXX_VERSION_LITERAL};
inline constexpr const char* flags = ${OpenMP_CXX_FLAGS_LITERAL};
inline constexpr const char* libraries = ${OpenMP_CXX_LIBRARIES_LITERAL};
}
")
    add_executable(parallel_sort_benchmark src/benchmark/parallel_main.cpp)
    target_include_directories(parallel_sort_benchmark PRIVATE "${CMAKE_BINARY_DIR}/generated/$<CONFIG>")
    target_link_libraries(parallel_sort_benchmark PRIVATE mab_parallel_timing)
    if(BUILD_TESTING)
        add_executable(test_parallel_mergesort tests/test_parallel_mergesort.cpp)
        target_link_libraries(test_parallel_mergesort PRIVATE mab_parallel_timing Threads::Threads)
        add_test(NAME parallel_mergesort COMMAND test_parallel_mergesort)
        set_tests_properties(parallel_mergesort PROPERTIES ENVIRONMENT "OMP_DYNAMIC=FALSE;OMP_THREAD_LIMIT=8;OMP_MAX_ACTIVE_LEVELS=1;OMP_WAIT_POLICY=PASSIVE")
        add_test(NAME parallel_framework COMMAND ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_parallel_benchmark.py $<TARGET_FILE:parallel_sort_benchmark>)
    endif()
endif()

# Isolated comparison opt-in; existing CUDA-only and CPU builds remain supported.
option(MAB_ENABLE_CPU_GPU_COMPARISON "Build the frozen-protocol CPU/GPU comparison worker" OFF)
if(MAB_ENABLE_CPU_GPU_COMPARISON)
    if(NOT MAB_ENABLE_CUDA_SORT OR NOT MAB_ENABLE_OPENMP)
        message(FATAL_ERROR "CPU/GPU comparison requires CUDA, CUDA_SORT and OpenMP enabled")
    endif()
    add_library(mab_cuda_comparison src/cuda/comparison_resources.cu)
    target_include_directories(mab_cuda_comparison PUBLIC include)
    target_include_directories(mab_cuda_comparison SYSTEM PRIVATE "${MAB_CUB_INCLUDE_DIR}")
    target_compile_options(mab_cuda_comparison PRIVATE "-Xcompiler=-Wall,-Wextra,-Wpedantic")
    target_link_libraries(mab_cuda_comparison PUBLIC CUDA::cudart)
    set_target_properties(mab_cuda_comparison PROPERTIES CUDA_STANDARD 17 CUDA_STANDARD_REQUIRED ON
                          CUDA_EXTENSIONS OFF CUDA_RUNTIME_LIBRARY Shared)
    add_executable(cpu_gpu_comparison src/benchmark/cpu_gpu_main.cpp)
    target_include_directories(cpu_gpu_comparison PRIVATE "${CMAKE_BINARY_DIR}/generated/$<CONFIG>")
    target_link_libraries(cpu_gpu_comparison PRIVATE mab_comparison mab_parallel mab_cuda_sort mab_cuda_timing mab_cuda_comparison mab_metrics)
endif()
if(BUILD_TESTING)
    add_executable(test_comparison tests/test_comparison.cpp)
    target_link_libraries(test_comparison PRIVATE mab_comparison)
    if(MAB_ENABLE_OPENMP)
        target_link_libraries(test_comparison PRIVATE mab_parallel)
        target_compile_definitions(test_comparison PRIVATE MAB_TEST_COMPARISON_OPENMP=1)
    endif()
    add_test(NAME comparison_engine COMMAND test_comparison)
    set_tests_properties(comparison_engine PROPERTIES ENVIRONMENT "OMP_DYNAMIC=FALSE;OMP_THREAD_LIMIT=2;OMP_MAX_ACTIVE_LEVELS=1;OMP_WAIT_POLICY=PASSIVE;OMP_PROC_BIND=FALSE")
    add_test(NAME cpu_gpu_comparison_framework COMMAND ${Python3_EXECUTABLE}
             ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_cpu_gpu_comparison.py $<TARGET_FILE:comparison_input>)
endif()

# Explicitly isolated correctness diagnostics. No benchmark executable is invoked.
option(MAB_ENABLE_VALIDATION_DIAGNOSTICS "Build untimed validation diagnostics" OFF)
if(MAB_ENABLE_VALIDATION_DIAGNOSTICS AND BUILD_TESTING)
    add_library(mab_diagnostic_output src/benchmark/output.cpp)
    target_link_libraries(mab_diagnostic_output PUBLIC mab_core)
    add_test(NAME validation_policy COMMAND ${Python3_EXECUTABLE}
             ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_validation_policy.py)
    if(MAB_ENABLE_OPENMP)
        add_executable(test_parallel_workers tests/test_parallel_workers.cpp)
        target_include_directories(test_parallel_workers PRIVATE "${CMAKE_BINARY_DIR}/generated/$<CONFIG>")
        target_link_libraries(test_parallel_workers PRIVATE mab_parallel mab_diagnostic_output)
        add_test(NAME parallel_workers_correctness COMMAND test_parallel_workers)
    endif()
    if(MAB_ENABLE_CUDA_SORT)
        add_executable(test_cuda_prepared_correctness tests/test_cuda_prepared_correctness.cpp)
        target_link_libraries(test_cuda_prepared_correctness PRIVATE mab_cuda_timing mab_diagnostic_output)
        add_test(NAME cuda_prepared_correctness COMMAND test_cuda_prepared_correctness)
        set_tests_properties(cuda_prepared_correctness PROPERTIES SKIP_RETURN_CODE 77 TIMEOUT 240)
    endif()
endif()

