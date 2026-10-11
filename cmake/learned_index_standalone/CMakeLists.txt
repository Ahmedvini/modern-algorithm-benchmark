cmake_minimum_required(VERSION 3.16)
project(mab_learned_extension LANGUAGES CXX)
# Keep the historical root CMake/algorithm registrations unchanged. Compile the
# existing sources directly; their implementation remains shared with the engine.
get_filename_component(MAB_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
option(MAB_ENABLE_SANITIZERS "Address/undefined sanitizers for correctness" OFF)
add_library(mab_search
    "${MAB_ROOT}/src/algorithms/baselines.cpp" "${MAB_ROOT}/src/datasets/generator.cpp"
    "${MAB_ROOT}/src/algorithms/sorting.cpp" "${MAB_ROOT}/src/algorithms/quicksort.cpp"
    "${MAB_ROOT}/src/algorithms/pdqsort.cpp" "${MAB_ROOT}/src/algorithms/timsort.cpp"
    "${MAB_ROOT}/src/algorithms/mergesort.cpp" "${MAB_ROOT}/src/algorithms/radixsort.cpp"
    "${MAB_ROOT}/src/algorithms/searching.cpp" "${MAB_ROOT}/src/benchmark/search_timing.cpp"
    "${MAB_ROOT}/src/benchmark/timing.cpp" "${MAB_ROOT}/src/benchmark/output.cpp"
    "${MAB_ROOT}/src/benchmark/search_comparisons.cpp"
    "${MAB_ROOT}/src/benchmark/memory.cpp" "${MAB_ROOT}/src/benchmark/memory_json.cpp")
target_include_directories(mab_search PUBLIC "${MAB_ROOT}/include")
target_include_directories(mab_search PRIVATE "${MAB_ROOT}/third_party/pdqsort" "${MAB_ROOT}/third_party/timsort/include")
target_compile_features(mab_search PUBLIC cxx_std_17)
set_target_properties(mab_search PROPERTIES CXX_EXTENSIONS OFF)
if(MAB_ENABLE_SANITIZERS)
    target_compile_options(mab_search PUBLIC -fsanitize=address,undefined -fno-omit-frame-pointer)
    target_link_options(mab_search PUBLIC -fsanitize=address,undefined)
endif()
add_library(mab_learned_index "${MAB_ROOT}/src/indexes/learned_index.cpp")
target_link_libraries(mab_learned_index PUBLIC mab_search)
target_compile_options(mab_learned_index PRIVATE -Wall -Wextra -Wpedantic -Wconversion -Wshadow)
add_executable(test_learned_index "${MAB_ROOT}/tests/test_learned_index.cpp")
target_link_libraries(test_learned_index PRIVATE mab_learned_index)
enable_testing()
add_test(NAME learned_index_correctness COMMAND test_learned_index)
add_executable(learned_index_benchmark "${MAB_ROOT}/src/benchmark/learned_main.cpp")
target_link_libraries(learned_index_benchmark PRIVATE mab_learned_index)
target_compile_options(learned_index_benchmark PRIVATE -Wall -Wextra -Wpedantic -Wconversion -Wshadow)
if(MAB_ENABLE_SANITIZERS)
    target_compile_definitions(learned_index_benchmark PRIVATE MAB_LEARNED_SANITIZERS=1)
endif()
