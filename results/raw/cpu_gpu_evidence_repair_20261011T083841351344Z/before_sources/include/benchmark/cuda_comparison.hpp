#pragma once
#include <cstddef>
#include <string>
namespace mab {
struct CudaComparisonResources {
    std::size_t prepared_query_bytes = 0, adapter_query_bytes = 0;
    std::size_t prepared_diagnostic_allocation_bytes = 0, adapter_diagnostic_allocation_bytes = 0;
    std::size_t free_device_bytes = 0, total_device_bytes = 0;
    std::string gpu_name;
    int compute_major = 0, compute_minor = 0, runtime_version = 0, driver_version = 0;
};
// Isolated sizing/allocation diagnostic, not instrumentation of production calls.
CudaComparisonResources query_comparison_resources(std::size_t size);
void synchronize_comparison_device();
} // namespace mab
