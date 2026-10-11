#include "benchmark/structure_timing.hpp"
#include <algorithm>
#include <chrono>
#include <stdexcept>

namespace mab {
void validate_structure_config(const StructureConfig& config) {
    validate_search_config(config.search);
    const auto limit = static_cast<std::uint64_t>(config.search.timing.memory_limit_mib)*1024*1024;
    const auto query_bytes = static_cast<std::uint64_t>(config.search.batch_size)*128*9;
    if (query_bytes > limit || config.search.timing.dataset.size > (limit-query_bytes)/512)
        throw std::invalid_argument("structure/query workspace exceeds planning budget");
}
StructureWorkload make_structure_workload(Values original, const StructureConfig& config) {
    validate_structure_config(config);
    if (original.size() != config.search.timing.dataset.size) throw std::invalid_argument("structure input size mismatch");
    StructureWorkload result;
    result.original = std::move(original); result.sorted = result.original;
    std::sort(result.sorted.begin(),result.sorted.end());
    result.unique_keys = 0;
    for (std::size_t i=0;i<result.sorted.size();++i)
        if (!i || result.sorted[i-1] != result.sorted[i]) ++result.unique_keys;
    result.entries.reserve(result.original.size());
    for (const auto key : result.original) result.entries.push_back({key,static_cast<std::size_t>(
        std::lower_bound(result.sorted.begin(),result.sorted.end(),key)-result.sorted.begin())});
    result.batches = make_search_batches(result.sorted,config.search);
    return result;
}
bool run_structure_trials(const StructureWorkload& workload, const StructureConfig& config,
                          const std::vector<IndexFactory>& factories,
                          const std::function<void(const StructureTrial&)>& sink) {
    if (factories.empty() || !sink) throw std::invalid_argument("nonempty factories and sink required");
    for (std::size_t i=0;i<factories.size();++i) {
        if (!factories[i].create || factories[i].name.empty()) throw std::invalid_argument("invalid index factory");
        for (std::size_t j=0;j<i;++j) if (factories[i].name==factories[j].name) throw std::invalid_argument("duplicate structure");
    }
    // Reconstruct reference before timing: reject caller-supplied stale ranks,
    // category availability, query identity and even fingerprint collisions.
    const auto expected = make_structure_workload(workload.original,config);
    if (workload.sorted!=expected.sorted || workload.unique_keys!=expected.unique_keys ||
        workload.entries.size()!=expected.entries.size() || workload.batches.size()!=expected.batches.size())
        throw std::invalid_argument("structure workload mismatch");
    for (std::size_t i=0;i<expected.entries.size();++i)
        if (workload.entries[i].key!=expected.entries[i].key || workload.entries[i].value!=expected.entries[i].value)
            throw std::invalid_argument("structure entry mismatch");
    for (std::size_t b=0;b<expected.batches.size();++b) {
        const auto& a=workload.batches[b]; const auto& e=expected.batches[b];
        if (a.category!=e.category || a.unavailable_reason!=e.unavailable_reason || a.queries.size()!=e.queries.size())
            throw std::invalid_argument("structure query plan mismatch");
        for (std::size_t q=0;q<a.queries.size();++q)
            if (a.queries[q].target!=e.queries[q].target || a.queries[q].expected_position!=e.queries[q].expected_position ||
                a.queries[q].selected_position!=e.queries[q].selected_position) throw std::invalid_argument("structure query mismatch");
    }
    using Clock=std::chrono::steady_clock;
    static_assert(Clock::is_steady,"monotonic clock required");
    const auto duration = [](Clock::time_point start, Clock::time_point end) {
        const auto ns=std::chrono::duration_cast<std::chrono::nanoseconds>(end-start).count();
        if (ns<0) throw std::runtime_error("negative duration");
        return static_cast<std::uint64_t>(ns);
    };
    std::vector<SearchResult> answers(config.search.batch_size);
    for (const auto phase : {std::string_view{"warmup"},std::string_view{"measure"}}) {
        const auto rounds=phase=="warmup" ? config.search.timing.warmups : config.search.timing.repetitions;
        for (std::size_t trial=0;trial<rounds;++trial) {
            const auto offset=(config.search.timing.dataset.seed%factories.size()+trial%factories.size())%factories.size();
            for (std::size_t order=0;order<factories.size();++order) {
                const auto& factory=factories[(offset+order)%factories.size()];
                StructureTrial row{factory.name,"build","",phase,trial,order,std::nullopt,"ok","passed",{}};
                std::unique_ptr<OrderedIndex> index;
                try {
                    const auto start=Clock::now();
                    index=factory.create(config.structure_seed);
                    if (!index) throw std::runtime_error("null structure factory result");
                    for (const auto& entry : workload.entries) index->insert(entry.key,entry.value);
                    const auto stop=Clock::now(); row.elapsed_ns=duration(start,stop);
                } catch (const std::exception& e) {row.status="error";row.correctness="not_checked";row.error=e.what();}
                catch (...) {row.status="error";row.correctness="not_checked";row.error="non-standard construction exception";}
                if (row.status=="ok") {
                    try {
                        if (index->size()!=workload.unique_keys || !index->validate()) throw std::runtime_error("structure size/invariant failure");
                        for (const auto& entry : workload.entries)
                            if (index->find(entry.key)!=entry.value) throw std::runtime_error("structure payload differs from first-rank oracle");
                    } catch (const std::exception& e) {row.status="error";row.correctness="failed";row.error=e.what();}
                    catch (...) {row.status="error";row.correctness="failed";row.error="non-standard validation exception";}
                }
                sink(row); if (row.status!="ok") return false;
                for (const auto& batch : workload.batches) {
                    if (!batch.unavailable_reason.empty()) continue;
                    row.operation="lookup";row.category=batch.category;row.elapsed_ns.reset();
                    try {
                        const auto start=Clock::now();
                        for (std::size_t q=0;q<batch.queries.size();++q) answers[q]=index->find(batch.queries[q].target);
                        const auto stop=Clock::now();row.elapsed_ns=duration(start,stop);
                    } catch (const std::exception& e) {row.status="error";row.correctness="not_checked";row.error=e.what();}
                    catch (...) {row.status="error";row.correctness="not_checked";row.error="non-standard lookup exception";}
                    if (row.status=="ok") for (std::size_t q=0;q<batch.queries.size();++q)
                        if (answers[q]!=batch.queries[q].expected_position) {
                            row.status="error";row.correctness="failed";row.error="structure answer differs at query "+std::to_string(q);break;
                        }
                    sink(row);if (row.status!="ok") return false;
                }
                // Unique ownership destroyed after all lookup/validation timers.
            }
        }
    }
    return true;
}
}  // namespace mab
