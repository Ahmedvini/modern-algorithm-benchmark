#include "benchmark/memory.hpp"
#include "test_support.hpp"

#include <exception>
#include <iostream>
#include <sstream>
#include <stdexcept>

namespace {
std::string format(const mab::ProcessMemory& report) {
    std::ostringstream stream;
    mab::write_memory_json(stream, report);
    return stream.str();
}
}  // namespace

int main() {
    try {
        const auto unsupported = mab::ProcessMemory{};
        require(format(unsupported) == "{\"status\":\"unsupported\",\"metric\":\"peak_rss\","
                "\"scope\":\"process_lifetime\",\"unit\":\"bytes\",\"method\":\"none\","
                "\"value\":null,\"error_code\":null}", "unsupported memory JSON changed");
        const mab::ProcessMemory ok{mab::MemoryStatus::ok, "getrusage_ru_maxrss", 4096, std::nullopt};
        require(format(ok) == "{\"status\":\"ok\",\"metric\":\"peak_rss\",\"scope\":\"process_lifetime\","
                "\"unit\":\"bytes\",\"method\":\"getrusage_ru_maxrss\",\"value\":4096,\"error_code\":null}",
                "supported memory JSON changed");
        auto zero = ok;
        zero.peak_rss_bytes = 0;
        require(format(zero).find("\"value\":0") != std::string::npos, "zero memory confused with unavailable");
        const mab::ProcessMemory error{mab::MemoryStatus::error, "getrusage_ru_maxrss", std::nullopt, 22};
        require(format(error) == "{\"status\":\"error\",\"metric\":\"peak_rss\",\"scope\":\"process_lifetime\","
                "\"unit\":\"bytes\",\"method\":\"getrusage_ru_maxrss\",\"value\":null,\"error_code\":22}",
                "failed measurement falsely reported a value");
        for (const auto& invalid : {mab::ProcessMemory{mab::MemoryStatus::ok, "getrusage_ru_maxrss", std::nullopt, std::nullopt},
                mab::ProcessMemory{mab::MemoryStatus::unsupported, "none", 4096, std::nullopt},
                mab::ProcessMemory{mab::MemoryStatus::error, "getrusage_ru_maxrss", std::nullopt, std::nullopt},
                mab::ProcessMemory{mab::MemoryStatus::unsupported, "unescaped\"method", std::nullopt, std::nullopt}}) {
            bool rejected = false;
            try { (void)format(invalid); } catch (const std::invalid_argument&) { rejected = true; }
            require(rejected, "inconsistent memory report accepted");
        }
        const auto first = mab::process_memory();
        const auto second = mab::process_memory();
#if defined(__linux__) && !defined(MAB_FORCE_UNSUPPORTED_MEMORY)
        require(first.status == mab::MemoryStatus::ok && second.status == mab::MemoryStatus::ok,
                "Linux getrusage failed");
        require(first.method == "getrusage_ru_maxrss" && first.peak_rss_bytes && !first.error_code,
                "Linux memory report metadata inconsistent");
        require(*first.peak_rss_bytes % 1024 == 0 && *second.peak_rss_bytes >= *first.peak_rss_bytes,
                "RSS unit conversion or process high-water semantics invalid");
#else
        require(first.status == mab::MemoryStatus::unsupported && second.status == mab::MemoryStatus::unsupported &&
                !first.peak_rss_bytes && !first.error_code && first.method == "none", "unsupported branch fabricated memory");
#endif
        std::cout << "Passed memory JSON supported/zero/error/unsupported fixtures, four invalid reports, "
                     "and repeated platform probes\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
