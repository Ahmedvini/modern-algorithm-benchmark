#pragma once

#include <iosfwd>
#include <string>
#include <string_view>
#include <vector>

namespace mab {
std::string csv_field(std::string_view value);
std::string json_string(std::string_view value);
void write_csv_row(std::ostream& output, const std::vector<std::string>& fields);
}  // namespace mab
