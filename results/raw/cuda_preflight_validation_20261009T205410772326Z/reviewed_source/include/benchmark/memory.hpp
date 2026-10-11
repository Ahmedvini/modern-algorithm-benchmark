#pragma once

#include <cstdint>
#include <iosfwd>
#include <optional>
#include <string_view>

namespace mab {
enum class MemoryStatus { ok, unsupported, error };

struct ProcessMemory {
    MemoryStatus status = MemoryStatus::unsupported;
    std::string_view method = "none";
    std::optional<std::uint64_t> peak_rss_bytes;
    std::optional<int> error_code;
};

// Linux: getrusage(RUSAGE_SELF).ru_maxrss in KiB, normalized to bytes.
// Other platforms return unsupported. This high-water mark is never reset.
ProcessMemory process_memory();
void write_memory_json(std::ostream& output, const ProcessMemory& memory);
}  // namespace mab
