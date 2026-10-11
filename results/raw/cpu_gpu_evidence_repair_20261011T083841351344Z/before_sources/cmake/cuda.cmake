# This file is included only on explicit opt-in; no CUDA discovery for CPU users.
if(CMAKE_VERSION VERSION_LESS 3.18)
    message(FATAL_ERROR "MAB_ENABLE_CUDA requires CMake >= 3.18; CPU builds require only 3.16")
endif()
if(MAB_ENABLE_SANITIZERS)
    message(FATAL_ERROR "Use separate CPU sanitizer and CUDA build directories")
endif()
include(CheckLanguage)
check_language(CUDA)
if(NOT CMAKE_CUDA_COMPILER)
    message(FATAL_ERROR "CUDA compiler unavailable; use MAB_ENABLE_CUDA=OFF and scripts/cuda_preflight.py")
endif()
enable_language(CUDA)
if(NOT CMAKE_CUDA_COMPILER_ID STREQUAL "NVIDIA")
    message(FATAL_ERROR "This CUDA readiness target currently supports NVIDIA nvcc only")
endif()
find_package(CUDAToolkit 11.0 REQUIRED)
add_executable(cuda_runtime_probe src/cuda/runtime_probe.cu)
set_target_properties(cuda_runtime_probe PROPERTIES CUDA_STANDARD 17 CUDA_STANDARD_REQUIRED ON
                      CUDA_EXTENSIONS OFF CUDA_RUNTIME_LIBRARY Shared)
target_link_libraries(cuda_runtime_probe PRIVATE CUDA::cudart)
if(BUILD_TESTING)
    add_test(NAME cuda_runtime_smoke COMMAND cuda_runtime_probe)
    set_tests_properties(cuda_runtime_smoke PROPERTIES SKIP_RETURN_CODE 77 TIMEOUT 60)
endif()

if(MAB_ENABLE_CUDA_SORT)
    if(CUDAToolkit_VERSION VERSION_LESS 13.0)
        message(FATAL_ERROR "The reviewed CUB correctness adapter requires toolkit >=13.0")
    endif()
    find_path(MAB_CUB_INCLUDE_DIR cub/version.cuh
              HINTS ${CUDAToolkit_INCLUDE_DIRS}
              PATH_SUFFIXES cccl NO_DEFAULT_PATH)
    if(NOT MAB_CUB_INCLUDE_DIR)
        message(FATAL_ERROR "Toolkit CUB headers unavailable")
    endif()
    file(SHA256 "${MAB_CUB_INCLUDE_DIR}/cub/version.cuh" cub_version_hash)
    file(SHA256 "${MAB_CUB_INCLUDE_DIR}/cub/device/device_radix_sort.cuh" cub_sort_hash)
    if(NOT cub_version_hash STREQUAL "316819d3be158deebcf40e96dde6d8d08e7910e9740a69b111677d0c5a21c124"
       OR NOT cub_sort_hash STREQUAL "7190cd469e955b2bd08dacb6e4a06a4600ee9d6547747a8148750bb6a97d29be")
        message(FATAL_ERROR "Installed CUB differs from reviewed v3.0.1 headers (version=${cub_version_hash}, SortKeys=${cub_sort_hash}); preserve diagnostics and review the dependency before changing the pin")
    endif()
    add_library(mab_cuda_sort src/cuda/cub_sort.cu)
    target_include_directories(mab_cuda_sort SYSTEM PRIVATE "${MAB_CUB_INCLUDE_DIR}")
    # Do not inherit mab_core's host-only warning switches into nvcc.
    target_include_directories(mab_cuda_sort PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
    target_compile_features(mab_cuda_sort PUBLIC cxx_std_17)
    target_compile_options(mab_cuda_sort PRIVATE "-Xcompiler=-Wall,-Wextra,-Wpedantic")
    target_link_libraries(mab_cuda_sort PUBLIC CUDA::cudart)
    set_target_properties(mab_cuda_sort PROPERTIES CUDA_STANDARD 17 CUDA_STANDARD_REQUIRED ON
                          CUDA_EXTENSIONS OFF CUDA_RUNTIME_LIBRARY Shared)
    # Benchmark-only prepared execution, separate from the production adapter.
    add_library(mab_cuda_timing src/cuda/cub_timing.cu)
    target_include_directories(mab_cuda_timing PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
    target_include_directories(mab_cuda_timing SYSTEM PRIVATE "${MAB_CUB_INCLUDE_DIR}")
    target_compile_options(mab_cuda_timing PRIVATE "-Xcompiler=-Wall,-Wextra,-Wpedantic")
    target_link_libraries(mab_cuda_timing PUBLIC CUDA::cudart)
    set_target_properties(mab_cuda_timing PROPERTIES CUDA_STANDARD 17 CUDA_STANDARD_REQUIRED ON
                          CUDA_EXTENSIONS OFF CUDA_RUNTIME_LIBRARY Shared)
    foreach(pair IN ITEMS CMAKE_CUDA_COMPILER_VERSION CUDAToolkit_VERSION CMAKE_CUDA_FLAGS
                          CMAKE_CUDA_FLAGS_RELEASE CMAKE_CUDA_ARCHITECTURES)
        mab_cxx_literal(${pair}_LITERAL "${${pair}}")
    endforeach()
    file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/generated/$<CONFIG>/cuda_benchmark_build.hpp" CONTENT
"#pragma once
namespace mab::cuda_build {
inline constexpr const char* compiler_version = ${CMAKE_CUDA_COMPILER_VERSION_LITERAL};
inline constexpr const char* toolkit_version = ${CUDAToolkit_VERSION_LITERAL};
inline constexpr const char* flags = ${CMAKE_CUDA_FLAGS_LITERAL};
inline constexpr const char* release_flags = ${CMAKE_CUDA_FLAGS_RELEASE_LITERAL};
inline constexpr const char* architectures = ${CMAKE_CUDA_ARCHITECTURES_LITERAL};
}
")
    add_executable(cuda_sort_benchmark src/benchmark/cuda_main.cpp)
    target_include_directories(cuda_sort_benchmark PRIVATE "${CMAKE_BINARY_DIR}/generated/$<CONFIG>")
    target_link_libraries(cuda_sort_benchmark PRIVATE mab_cuda_timing mab_cuda_sort mab_timing)
    if(BUILD_TESTING)
        add_test(NAME cuda_benchmark_gpu_framework COMMAND ${Python3_EXECUTABLE}
                 ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_cuda_benchmark.py $<TARGET_FILE:cuda_sort_benchmark>)
        set_tests_properties(cuda_benchmark_gpu_framework PROPERTIES TIMEOUT 180)
        add_executable(test_cuda_sorting tests/test_cuda_sorting.cpp)
        target_link_libraries(test_cuda_sorting PRIVATE mab_cuda_sort mab_core)
        add_test(NAME cuda_sorting COMMAND test_cuda_sorting)
        set_tests_properties(cuda_sorting PROPERTIES SKIP_RETURN_CODE 77 TIMEOUT 240)
    endif()
endif()
