#include "benchmark/cuda_comparison.hpp"
#include <cub/device/device_radix_sort.cuh>
#include <cub/version.cuh>
#include <cuda_runtime.h>
#include <algorithm>
#include <cstdio>
#include <stdexcept>
#include <cstdint>

namespace mab {
namespace {
static_assert(CUB_VERSION == 300001, "Preserve reviewed CUB 3.0.1 pin");
void check(cudaError_t status, const char* operation) {
    if (status != cudaSuccess) throw std::runtime_error(std::string(operation)+": "+cudaGetErrorString(status));
}
struct Buffer {
    void* pointer = nullptr;
    Buffer() = default;
    Buffer(const Buffer&) = delete;
    Buffer& operator=(const Buffer&) = delete;
    void allocate(std::size_t bytes) { check(cudaMalloc(&pointer,bytes),"diagnostic cudaMalloc"); }
    void close() { auto p=pointer; pointer=nullptr; if(p) check(cudaFree(p),"diagnostic cudaFree"); }
    ~Buffer() { if(pointer) { auto s=cudaFree(pointer); if(s!=cudaSuccess) std::fprintf(stderr,"diagnostic cleanup: %s\n",cudaGetErrorString(s)); } }
};
struct Stream {
    cudaStream_t value = nullptr;
    ~Stream() { if(value) { auto s=cudaStreamDestroy(value); if(s!=cudaSuccess) std::fprintf(stderr,"diagnostic stream cleanup: %s\n",cudaGetErrorString(s)); } }
    void close() { auto s=value; value=nullptr; check(cudaStreamDestroy(s),"diagnostic destroy stream"); }
};
}
void synchronize_comparison_device() { check(cudaDeviceSynchronize(),"pre-call device synchronize"); }
CudaComparisonResources query_comparison_resources(std::size_t n) {
    if (n < 2 || n > 1000000) throw std::invalid_argument("resource diagnostic size outside [2,1M]");
    CudaComparisonResources result;
    int device=0; cudaDeviceProp prop{};
    check(cudaGetDevice(&device),"diagnostic get device");
    check(cudaGetDeviceProperties(&prop,device),"diagnostic device properties");
    result.gpu_name=prop.name; result.compute_major=prop.major; result.compute_minor=prop.minor;
    if (result.gpu_name!="Tesla T4" || prop.major!=7 || prop.minor!=5)
        throw std::runtime_error("frozen pilot requires Tesla T4 compute7.5");
    check(cudaRuntimeGetVersion(&result.runtime_version),"diagnostic runtime version");
    check(cudaDriverGetVersion(&result.driver_version),"diagnostic driver version");
    synchronize_comparison_device();
    check(cudaMemGetInfo(&result.free_device_bytes,&result.total_device_bytes),"diagnostic free memory");
    if (16*n > result.free_device_bytes/2) throw std::runtime_error("insufficient device key-buffer headroom");
    Buffer input, output, prepared_workspace, adapter_workspace;
    input.allocate(4*n); output.allocate(4*n);
    auto* in=static_cast<std::int32_t*>(input.pointer); auto* out=static_cast<std::int32_t*>(output.pointer);
    Stream stream; check(cudaStreamCreateWithFlags(&stream.value,cudaStreamNonBlocking),"diagnostic create stream");
    check(cub::DeviceRadixSort::SortKeys(nullptr,result.adapter_query_bytes,in,out,static_cast<int>(n),0,32),"default-stream workspace query");
    check(cub::DeviceRadixSort::SortKeys(nullptr,result.prepared_query_bytes,in,out,static_cast<int>(n),0,32,stream.value),"private-stream workspace query");
    constexpr std::size_t cap=64*1024*1024;
    if (result.adapter_query_bytes>cap || result.prepared_query_bytes>cap)
        throw std::runtime_error("workspace exceeds frozen 64MiB cap: adapter="+std::to_string(result.adapter_query_bytes)+" prepared="+std::to_string(result.prepared_query_bytes));
    result.adapter_diagnostic_allocation_bytes=std::max(result.adapter_query_bytes,std::size_t{1});
    result.prepared_diagnostic_allocation_bytes=std::max(result.prepared_query_bytes,std::size_t{1});
    const auto peak=16*n+result.adapter_diagnostic_allocation_bytes+result.prepared_diagnostic_allocation_bytes;
    if (peak>256*1024*1024 || peak>result.free_device_bytes/2) throw std::runtime_error("combined frozen device budget exceeded");
    adapter_workspace.allocate(result.adapter_diagnostic_allocation_bytes);
    prepared_workspace.allocate(result.prepared_diagnostic_allocation_bytes);
    prepared_workspace.close(); adapter_workspace.close(); output.close(); input.close(); stream.close();
    return result;
}
} // namespace mab
