# Held-out learned rank study

48 datasets; 480 measured lookup batches, 240 measured builds; 96 lookup and 48 build warm-ups. All outputs passed; zero missing/failed trials. Each dataset has 500 hit and 500 miss queries. Repetitions are summarized within a dataset; cross-seed values equally weight three dataset medians. All outliers retained.

|N|Distribution|Algorithm|Operation|Median of dataset medians (ns)|Cross-seed min–max (ns)|
|---:|---|---|---|---:|---:|
|1000|duplicate_heavy|binary_search|lookup_batch|18934.0|17340.0–20314.0|
|1000|duplicate_heavy|learned_rank|build|386.0|372.0–398.0|
|1000|duplicate_heavy|learned_rank|lookup_batch|20473.0|20297.0–20716.0|
|1000|nearly_sorted|binary_search|lookup_batch|35939.0|35811.0–40949.0|
|1000|nearly_sorted|learned_rank|build|390.0|376.0–716.0|
|1000|nearly_sorted|learned_rank|lookup_batch|28635.0|28591.0–33511.0|
|1000|reverse_sorted|binary_search|lookup_batch|35643.0|35033.0–37409.0|
|1000|reverse_sorted|learned_rank|build|392.0|372.0–397.0|
|1000|reverse_sorted|learned_rank|lookup_batch|26767.0|26737.0–27781.0|
|1000|uniform|binary_search|lookup_batch|34833.0|33840.0–36759.0|
|1000|uniform|learned_rank|build|375.0|355.0–386.0|
|1000|uniform|learned_rank|lookup_batch|27221.0|26636.0–29231.0|
|10000|duplicate_heavy|binary_search|lookup_batch|27185.0|26668.0–27442.0|
|10000|duplicate_heavy|learned_rank|build|3680.0|3581.0–3783.0|
|10000|duplicate_heavy|learned_rank|lookup_batch|23800.0|23307.0–24681.0|
|10000|nearly_sorted|binary_search|lookup_batch|54947.0|51682.0–57922.0|
|10000|nearly_sorted|learned_rank|build|3684.0|3501.0–5263.0|
|10000|nearly_sorted|learned_rank|lookup_batch|40475.0|36205.0–42652.0|
|10000|reverse_sorted|binary_search|lookup_batch|58539.0|58094.0–60054.0|
|10000|reverse_sorted|learned_rank|build|3910.0|3807.0–5962.0|
|10000|reverse_sorted|learned_rank|lookup_batch|44365.0|40807.0–53307.0|
|10000|uniform|binary_search|lookup_batch|50496.0|50130.0–51283.0|
|10000|uniform|learned_rank|build|3317.0|3227.0–3399.0|
|10000|uniform|learned_rank|lookup_batch|41821.0|36831.0–42654.0|
|100000|duplicate_heavy|binary_search|lookup_batch|26907.0|25351.0–27310.0|
|100000|duplicate_heavy|learned_rank|build|32319.0|31843.0–33232.0|
|100000|duplicate_heavy|learned_rank|lookup_batch|22637.0|21611.0–25953.0|
|100000|nearly_sorted|binary_search|lookup_batch|62917.0|60108.0–63877.0|
|100000|nearly_sorted|learned_rank|build|31280.0|30694.0–32300.0|
|100000|nearly_sorted|learned_rank|lookup_batch|61156.0|55671.0–61483.0|
|100000|reverse_sorted|binary_search|lookup_batch|61911.0|61603.0–64697.0|
|100000|reverse_sorted|learned_rank|build|32129.0|31577.0–35584.0|
|100000|reverse_sorted|learned_rank|lookup_batch|61253.0|57787.0–62421.0|
|100000|uniform|binary_search|lookup_batch|75762.0|61581.0–79907.0|
|100000|uniform|learned_rank|build|38582.0|31368.0–39275.0|
|100000|uniform|learned_rank|lookup_batch|68246.0|57979.0–73331.0|
|1000000|duplicate_heavy|binary_search|lookup_batch|34160.0|32546.0–39903.0|
|1000000|duplicate_heavy|learned_rank|build|578882.0|493773.0–632170.0|
|1000000|duplicate_heavy|learned_rank|lookup_batch|33748.0|26759.0–37245.0|
|1000000|nearly_sorted|binary_search|lookup_batch|154655.0|108419.0–155036.0|
|1000000|nearly_sorted|learned_rank|build|829069.0|600864.0–967037.0|
|1000000|nearly_sorted|learned_rank|lookup_batch|107055.0|101354.0–139109.0|
|1000000|reverse_sorted|binary_search|lookup_batch|106410.0|95385.0–126401.0|
|1000000|reverse_sorted|learned_rank|build|554255.0|513670.0–571018.0|
|1000000|reverse_sorted|learned_rank|lookup_batch|94804.0|86904.0–115216.0|
|1000000|uniform|binary_search|lookup_batch|125127.0|120908.0–171715.0|
|1000000|uniform|learned_rank|build|664637.0|590833.0–1044690.0|
|1000000|uniform|learned_rank|lookup_batch|115328.0|110159.0–136460.0|

Logical index capacity excludes allocator metadata. Process lifetime peak RSS includes input, queries, index, runtime and allocator; it does not isolate index memory. No individual-query maximum was measured. Frequency, thermal state and background load were not controlled. These are descriptive results, with no statistical-significance or universal-ranking claim. See diagnostics in summary.json for fallback frequency, rank correction distance and separate comparison counts.
