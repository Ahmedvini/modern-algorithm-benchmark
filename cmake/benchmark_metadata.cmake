# These are CMake-configured values, not guessed effective compiler flags.
# Full per-translation-unit commands are copied when compile_commands.json exists.
function(mab_cxx_literal output value)
    string(REPLACE "\\" "\\\\" escaped "${value}")
    string(REPLACE "\"" "\\\"" escaped "${escaped}")
    string(REPLACE "\n" "\\n" escaped "${escaped}")
    string(REPLACE "\r" "\\r" escaped "${escaped}")
    set(${output} "\"${escaped}\"" PARENT_SCOPE)
endfunction()
foreach(key IN ITEMS CMAKE_CXX_COMPILER_ID CMAKE_CXX_COMPILER_VERSION CMAKE_CXX_COMPILER
                     CMAKE_SYSTEM_NAME CMAKE_SYSTEM_PROCESSOR CMAKE_CXX_FLAGS
                     CMAKE_CXX_FLAGS_RELEASE CMAKE_CXX_FLAGS_DEBUG
                     CMAKE_CXX_FLAGS_RELWITHDEBINFO CMAKE_CXX_FLAGS_MINSIZEREL
                     CMAKE_BINARY_DIR CMAKE_SOURCE_DIR)
    mab_cxx_literal(${key}_LITERAL "${${key}}")
endforeach()
# A reconfigure is triggered when recorded source contents change.
file(GLOB_RECURSE mab_recorded_sources CONFIGURE_DEPENDS
     "${CMAKE_SOURCE_DIR}/include/*.hpp" "${CMAKE_SOURCE_DIR}/src/*.cpp"
     "${CMAKE_SOURCE_DIR}/third_party/*.h" "${CMAKE_SOURCE_DIR}/third_party/*.hpp"
     "${CMAKE_SOURCE_DIR}/third_party/UPSTREAM.json")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${mab_recorded_sources})
set(mab_source_manifest "{\"schema_version\":1,\"hash_algorithm\":\"sha256\",\"files\":[")
set(mab_separator "")
foreach(source IN LISTS mab_recorded_sources)
    file(RELATIVE_PATH relative "${CMAKE_SOURCE_DIR}" "${source}")
    file(SHA256 "${source}" digest)
    mab_cxx_literal(relative_json "${relative}")
    string(APPEND mab_source_manifest "${mab_separator}{\"path\":${relative_json},\"sha256\":\"${digest}\"}")
    set(mab_separator ",")
endforeach()
string(APPEND mab_source_manifest "]}\n")
file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/generated/$<CONFIG>/source_hashes.json" CONTENT "${mab_source_manifest}")
configure_file("${CMAKE_SOURCE_DIR}/third_party/pdqsort/UPSTREAM.json"
               "${CMAKE_BINARY_DIR}/pdqsort_upstream.json" COPYONLY)
configure_file("${CMAKE_SOURCE_DIR}/third_party/timsort/UPSTREAM.json"
               "${CMAKE_BINARY_DIR}/timsort_upstream.json" COPYONLY)
file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/generated/$<CONFIG>/benchmark_build.hpp" CONTENT
"#pragma once
namespace mab::build {
inline constexpr const char* compiler_id = ${CMAKE_CXX_COMPILER_ID_LITERAL};
inline constexpr const char* compiler_version = ${CMAKE_CXX_COMPILER_VERSION_LITERAL};
inline constexpr const char* compiler_path = ${CMAKE_CXX_COMPILER_LITERAL};
inline constexpr const char* platform = ${CMAKE_SYSTEM_NAME_LITERAL};
inline constexpr const char* architecture = ${CMAKE_SYSTEM_PROCESSOR_LITERAL};
inline constexpr const char* configuration = \"$<CONFIG>\";
inline constexpr const char* global_flags = ${CMAKE_CXX_FLAGS_LITERAL};
inline constexpr const char* configuration_flags = $<$<CONFIG:Release>:${CMAKE_CXX_FLAGS_RELEASE_LITERAL}>$<$<CONFIG:Debug>:${CMAKE_CXX_FLAGS_DEBUG_LITERAL}>$<$<CONFIG:RelWithDebInfo>:${CMAKE_CXX_FLAGS_RELWITHDEBINFO_LITERAL}>$<$<CONFIG:MinSizeRel>:${CMAKE_CXX_FLAGS_MINSIZEREL_LITERAL}>$<$<NOT:$<OR:$<CONFIG:Release>,$<CONFIG:Debug>,$<CONFIG:RelWithDebInfo>,$<CONFIG:MinSizeRel>>>:\"\">;
inline constexpr bool sanitizers = $<IF:$<BOOL:${MAB_ENABLE_SANITIZERS}>,true,false>;
inline constexpr const char* binary_dir = ${CMAKE_BINARY_DIR_LITERAL};
inline constexpr const char* source_dir = ${CMAKE_SOURCE_DIR_LITERAL};
}
")
