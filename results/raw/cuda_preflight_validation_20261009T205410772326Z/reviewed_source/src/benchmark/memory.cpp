#include "benchmark/memory.hpp"

#include <cerrno>
#include <limits>

#if defined(__linux__) && !defined(MAB_FORCE_UNSUPPORTED_MEMORY)
#include <sys/resource.h>
#endif

namespace mab {
ProcessMemory process_memory() {
#if defined(__linux__) && !defined(MAB_FORCE_UNSUPPORTED_MEMORY)
    rusage usage{};
    if (getrusage(RUSAGE_SELF, &usage) != 0)
        return {MemoryStatus::error, "getrusage_ru_maxrss", std::nullopt, errno};
    if (usage.ru_maxrss < 0 || static_cast<std::uint64_t>(usage.ru_maxrss) >
            std::numeric_limits<std::uint64_t>::max() / 1024)
        return {MemoryStatus::error, "getrusage_ru_maxrss", std::nullopt, EOVERFLOW};
    return {MemoryStatus::ok, "getrusage_ru_maxrss",
            static_cast<std::uint64_t>(usage.ru_maxrss) * 1024, std::nullopt};
#else
    return {};
#endif
}
}  // namespace mab
