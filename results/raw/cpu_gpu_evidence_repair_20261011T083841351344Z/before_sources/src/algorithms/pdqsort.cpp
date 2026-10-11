#include "algorithms/pdqsort.hpp"

#include "pdqsort.h"

namespace mab {
void pdq_sort(Values& values) {
    ::pdqsort(values.begin(), values.end());
}
}  // namespace mab
