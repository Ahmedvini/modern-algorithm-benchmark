#include "benchmark/output.hpp"

#include <ostream>

namespace mab {
std::string csv_field(std::string_view value) {
    if (value.find_first_of(",\"\r\n") == std::string_view::npos) return std::string(value);
    std::string escaped = "\"";
    for (const auto character : value) {
        escaped += character;
        if (character == '"') escaped += '"';
    }
    return escaped + '"';
}

std::string json_string(std::string_view value) {
    constexpr char hex[] = "0123456789abcdef";
    std::string escaped = "\"";
    for (const unsigned char character : value) {
        if (character == '"' || character == '\\') {
            escaped += '\\';
            escaped += static_cast<char>(character);
        } else if (character < 32) {
            escaped += "\\u00";
            escaped += hex[character >> 4];
            escaped += hex[character & 15];
        } else escaped += static_cast<char>(character);
    }
    return escaped + '"';
}

void write_csv_row(std::ostream& output, const std::vector<std::string>& fields) {
    bool first = true;
    for (const auto& field : fields) {
        if (!first) output << ',';
        output << csv_field(field);
        first = false;
    }
    output << '\n';
}
}  // namespace mab
