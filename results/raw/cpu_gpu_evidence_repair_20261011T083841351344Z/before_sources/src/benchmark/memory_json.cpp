#include "benchmark/memory.hpp"

#include <ostream>
#include <stdexcept>

namespace mab {
void write_memory_json(std::ostream& output, const ProcessMemory& memory) {
    const char* status = nullptr;
    switch (memory.status) {
        case MemoryStatus::ok: status = "ok"; break;
        case MemoryStatus::unsupported: status = "unsupported"; break;
        case MemoryStatus::error: status = "error"; break;
    }
    if (!status || (memory.status == MemoryStatus::ok) != memory.peak_rss_bytes.has_value() ||
        (memory.status == MemoryStatus::error) != memory.error_code.has_value() ||
        (memory.method != "none" && memory.method != "getrusage_ru_maxrss") ||
        (memory.status == MemoryStatus::unsupported) != (memory.method == "none"))
        throw std::invalid_argument("inconsistent process memory report");
    output << "{\"status\":\"" << status << "\",\"metric\":\"peak_rss\",\"scope\":\"process_lifetime\","
              "\"unit\":\"bytes\",\"method\":\"" << memory.method << "\",\"value\":";
    if (memory.peak_rss_bytes) output << *memory.peak_rss_bytes;
    else output << "null";
    output << ",\"error_code\":";
    if (memory.error_code) output << *memory.error_code;
    else output << "null";
    output << '}';
}
}  // namespace mab
