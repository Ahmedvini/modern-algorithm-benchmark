#include "algorithms/cuda_sorting.hpp"
#include <cub/device/device_radix_sort.cuh>
#include <cub/version.cuh>
#include <cuda_runtime.h>

#include <climits>
#include <cstdio>
#include <limits>
#include <stdexcept>
#include <string>

namespace mab {
namespace {
static_assert(sizeof(Key) * CHAR_BIT == 32 && std::numeric_limits<Key>::is_signed,
              "CUB adapter requires signed 32-bit keys");
static_assert(CUB_VERSION == 300001, "Review a new CUB version before changing the pin");

void checked(cudaError_t status, const char* operation) {
    if (status != cudaSuccess)
        throw std::runtime_error(std::string(operation) + ": " + cudaGetErrorString(status)
                                 + " (CUDA " + std::to_string(static_cast<int>(status)) + ")");
}
class DeviceBuffer {
public:
    explicit DeviceBuffer(std::size_t bytes) {
        // A non-null buffer distinguishes execution from CUB's sizing query.
        checked(cudaMalloc(&pointer_, bytes ? bytes : 1), "cudaMalloc");
    }
    DeviceBuffer(const DeviceBuffer&) = delete;
    DeviceBuffer& operator=(const DeviceBuffer&) = delete;
    ~DeviceBuffer() noexcept {
        if (pointer_) {
            const auto status = cudaFree(pointer_);
            if (status != cudaSuccess)
                std::fprintf(stderr, "CUDA cleanup during unwinding: %s\n", cudaGetErrorString(status));
        }
    }
    void* get() const noexcept { return pointer_; }
    void close() {
        void* allocation = pointer_;
        pointer_ = nullptr; // One free attempt, including when the runtime reports an error.
        checked(cudaFree(allocation), "cudaFree");
    }
private:
    void* pointer_ = nullptr;
};
} // namespace

void cub_radix_sort(Values& values) {
    if (values.size() > static_cast<std::size_t>(INT_MAX) ||
        values.size() > std::numeric_limits<std::size_t>::max() / sizeof(Key))
        throw std::length_error("cub_radix_sort size exceeds supported item/byte count");
    int device = 0;
    cudaDeviceProp properties{};
    checked(cudaGetDevice(&device), "cudaGetDevice");
    checked(cudaGetDeviceProperties(&properties, device), "cudaGetDeviceProperties");
    if (values.size() < 2) return;

    Values output(values.size());
    const auto bytes = values.size() * sizeof(Key);
    const int count = static_cast<int>(values.size());
    DeviceBuffer input(bytes), sorted(bytes);
    auto* in = static_cast<Key*>(input.get());
    auto* out = static_cast<Key*>(sorted.get());
    std::size_t workspace_bytes = 0;
    checked(cub::DeviceRadixSort::SortKeys(nullptr, workspace_bytes, in, out, count, 0, 32),
            "CUB SortKeys workspace query");
    DeviceBuffer workspace(workspace_bytes);
    checked(cudaMemcpy(in, values.data(), bytes, cudaMemcpyHostToDevice), "H2D cudaMemcpy");
    checked(cub::DeviceRadixSort::SortKeys(workspace.get(), workspace_bytes, in, out, count, 0, 32),
            "CUB SortKeys");
    checked(cudaGetLastError(), "CUB launch status");
    checked(cudaStreamSynchronize(nullptr), "CUB stream synchronize");
    checked(cudaMemcpy(output.data(), out, bytes, cudaMemcpyDeviceToHost), "D2H cudaMemcpy");
    workspace.close();
    sorted.close();
    input.close();
    values.swap(output);
}

const std::array<Sorter, 1>& cuda_sorters() noexcept {
    static const std::array<Sorter, 1> registry{{{"cub_radix_sort", cub_radix_sort}}};
    return registry;
}
const Sorter& find_cuda_sorter(std::string_view name) {
    for (const auto& sorter : cuda_sorters())
        if (sorter.name == name) return sorter;
    throw std::invalid_argument("unknown CUDA sorter: " + std::string(name));
}
int cuda_sort_cub_version() noexcept { return CUB_VERSION; }
} // namespace mab
