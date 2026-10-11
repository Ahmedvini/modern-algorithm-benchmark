#pragma once
#include "common/types.hpp"
#include <cstddef>
#include <cstdint>
#include <memory>
#include <string>

namespace mab {
struct CudaTimingSample {
    double h2d_ns = 0, device_sort_ns = 0, d2h_ns = 0;
    std::uint64_t end_to_end_ns = 0;
};
struct CudaTimingInfo {
    int device = 0, compute_major = 0, compute_minor = 0;
    int runtime_version = 0, driver_version = 0;
    std::string device_name;
    std::size_t device_memory_bytes = 0, workspace_bytes = 0;
};
// Benchmark-only prepared execution. Does not change cub_radix_sort's contract.
// Owns pinned/device buffers, stream/events; no copy/move or shared state.
class CudaTimingSession {
public:
    CudaTimingSession(std::size_t size, std::size_t memory_limit_mib);
    ~CudaTimingSession();
    CudaTimingSession(const CudaTimingSession&) = delete;
    CudaTimingSession& operator=(const CudaTimingSession&) = delete;
    CudaTimingSession(CudaTimingSession&&) = delete;
    CudaTimingSession& operator=(CudaTimingSession&&) = delete;
    CudaTimingSample sample(const Values& input, Values& output);
    const CudaTimingInfo& info() const noexcept;
    void close(); // Checked release before a successful run's completion marker.
private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};
} // namespace mab
