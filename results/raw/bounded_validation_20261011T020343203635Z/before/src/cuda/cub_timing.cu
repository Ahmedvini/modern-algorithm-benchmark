#include "benchmark/cuda_timing.hpp"
#include <cub/device/device_radix_sort.cuh>
#include <cub/version.cuh>
#include <cuda_runtime.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <limits>
#include <stdexcept>

namespace mab {
namespace {
static_assert(CUB_VERSION == 300001, "Keep the reviewed CUB dependency pin");
static_assert(sizeof(Key) == 4 && std::numeric_limits<Key>::is_signed, "signed int32 required");
void checked(cudaError_t status, const char* operation) {
    if (status != cudaSuccess)
        throw std::runtime_error(std::string(operation) + ": " + cudaGetErrorString(status));
}
void secondary(cudaError_t status) noexcept {
    if (status != cudaSuccess) std::fprintf(stderr, "CUDA timing cleanup: %s\n", cudaGetErrorString(status));
}
}
struct CudaTimingSession::Impl {
    CudaTimingInfo info;
    std::size_t size = 0, bytes = 0;
    Key *host_input = nullptr, *host_output = nullptr, *input = nullptr, *output = nullptr;
    void* workspace = nullptr;
    cudaStream_t stream = nullptr;
    std::array<cudaEvent_t, 4> events{};
    bool closed = false;
    ~Impl() noexcept {
        if (stream) secondary(cudaStreamSynchronize(stream));
        for (auto e : events) if (e) secondary(cudaEventDestroy(e));
        if (workspace) secondary(cudaFree(workspace));
        if (output) secondary(cudaFree(output));
        if (input) secondary(cudaFree(input));
        if (host_output) secondary(cudaFreeHost(host_output));
        if (host_input) secondary(cudaFreeHost(host_input));
        if (stream) secondary(cudaStreamDestroy(stream));
    }
    void init(std::size_t n, std::size_t memory_limit_mib) {
        if (n > 1000000 || memory_limit_mib == 0 || memory_limit_mib > 65536)
            throw std::invalid_argument("CUDA timing size/limit outside milestone bounds");
        size = n; bytes = n * sizeof(Key);
        const auto limit = static_cast<std::uint64_t>(memory_limit_mib) * 1024 * 1024;
        if (bytes > limit / 5) throw std::invalid_argument("host payload budget exceeded");
        checked(cudaGetDevice(&info.device), "get device");
        cudaDeviceProp prop{};
        checked(cudaGetDeviceProperties(&prop, info.device), "device properties");
        info.device_name = prop.name; info.compute_major = prop.major; info.compute_minor = prop.minor;
        info.device_memory_bytes = prop.totalGlobalMem;
        checked(cudaRuntimeGetVersion(&info.runtime_version), "runtime version");
        checked(cudaDriverGetVersion(&info.driver_version), "driver version");
        if (size < 2) return;
        std::size_t available = 0, total = 0;
        checked(cudaMemGetInfo(&available, &total), "device free memory");
        if (bytes > available / 4) throw std::runtime_error("device keys exceed half free memory");
        checked(cudaStreamCreateWithFlags(&stream, cudaStreamNonBlocking), "create private stream");
        for (auto& event : events) checked(cudaEventCreate(&event), "create timing event");
        checked(cudaMallocHost(reinterpret_cast<void**>(&host_input), bytes), "allocate pinned input");
        checked(cudaMallocHost(reinterpret_cast<void**>(&host_output), bytes), "allocate pinned output");
        checked(cudaMalloc(reinterpret_cast<void**>(&input), bytes), "allocate device input");
        checked(cudaMalloc(reinterpret_cast<void**>(&output), bytes), "allocate device output");
        checked(cub::DeviceRadixSort::SortKeys(nullptr, info.workspace_bytes, input, output,
                static_cast<int>(size), 0, 32, stream), "workspace sizing");
        if (2 * bytes > limit || info.workspace_bytes > limit - 2 * bytes ||
            2 * bytes > available / 2 || info.workspace_bytes > available / 2 - 2 * bytes)
            throw std::runtime_error("CUDA workspace exceeds device budget");
        checked(cudaMalloc(&workspace, info.workspace_bytes ? info.workspace_bytes : 1), "allocate workspace");
    }
};
CudaTimingSession::CudaTimingSession(std::size_t n, std::size_t limit)
    : impl_(std::make_unique<Impl>()) { impl_->init(n, limit); }
CudaTimingSession::~CudaTimingSession() = default;
const CudaTimingInfo& CudaTimingSession::info() const noexcept { return impl_->info; }
CudaTimingSample CudaTimingSession::sample(const Values& input, Values& output) {
    auto& s = *impl_;
    if (s.closed || input.size() != s.size || output.size() != s.size || &input == &output)
        throw std::invalid_argument("invalid prepared CUDA timing buffers/session");
    using Clock = std::chrono::steady_clock;
    static_assert(Clock::is_steady, "monotonic host timer required");
    CudaTimingSample result;
    if (s.size < 2) {
        const auto start = Clock::now();
        if (s.size) output[0] = input[0];
        const auto stop = Clock::now();
        result.end_to_end_ns = static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count());
        return result;
    }
    std::copy(input.begin(), input.end(), s.host_input);
    checked(cudaStreamSynchronize(s.stream), "prior stream synchronize");
    const auto start = Clock::now();
    checked(cudaEventRecord(s.events[0], s.stream), "record H2D start");
    checked(cudaMemcpyAsync(s.input, s.host_input, s.bytes, cudaMemcpyHostToDevice, s.stream), "H2D");
    checked(cudaEventRecord(s.events[1], s.stream), "record sort start");
    checked(cub::DeviceRadixSort::SortKeys(s.workspace, s.info.workspace_bytes, s.input, s.output,
            static_cast<int>(s.size), 0, 32, s.stream), "CUB SortKeys");
    checked(cudaGetLastError(), "CUB launch status");
    checked(cudaEventRecord(s.events[2], s.stream), "record D2H start");
    checked(cudaMemcpyAsync(s.host_output, s.output, s.bytes, cudaMemcpyDeviceToHost, s.stream), "D2H");
    checked(cudaEventRecord(s.events[3], s.stream), "record D2H stop");
    checked(cudaEventSynchronize(s.events[3]), "pipeline completion");
    const auto stop = Clock::now();
    const auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
    if (elapsed < 0) throw std::runtime_error("negative host duration");
    result.end_to_end_ns = static_cast<std::uint64_t>(elapsed);
    std::array<double*, 3> metrics{{&result.h2d_ns, &result.device_sort_ns, &result.d2h_ns}};
    for (std::size_t i = 0; i < metrics.size(); ++i) {
        float ms = 0;
        checked(cudaEventElapsedTime(&ms, s.events[i], s.events[i + 1]), "event elapsed time");
        if (!std::isfinite(ms) || ms < 0) throw std::runtime_error("invalid event duration");
        *metrics[i] = static_cast<double>(ms) * 1000000.0;
    }
    std::copy(s.host_output, s.host_output + s.size, output.begin());
    return result;
}
void CudaTimingSession::close() {
    auto& s = *impl_;
    if (s.closed) return;
    if (s.stream) checked(cudaStreamSynchronize(s.stream), "close synchronize");
    for (auto& event : s.events) if (event) {
        const auto e = event; event = nullptr; checked(cudaEventDestroy(e), "destroy event");
    }
    auto release_device = [](auto*& pointer) {
        if (pointer) { auto* value = pointer; pointer = nullptr; checked(cudaFree(value), "free device buffer"); }
    };
    release_device(s.workspace); release_device(s.output); release_device(s.input);
    for (auto** p : {&s.host_output, &s.host_input})
        if (*p) { auto* value = *p; *p = nullptr; checked(cudaFreeHost(value), "free pinned buffer"); }
    if (s.stream) { const auto stream = s.stream; s.stream = nullptr; checked(cudaStreamDestroy(stream), "destroy stream"); }
    s.closed = true;
}
} // namespace mab
