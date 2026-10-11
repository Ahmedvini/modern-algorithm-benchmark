#include "benchmark/search_timing.hpp"
#include "algorithms/baselines.hpp"
#include <algorithm>
#include <chrono>
#include <limits>
#include <random>
#include <stdexcept>

namespace mab {
const std::array<std::string_view,9>& query_categories() noexcept {
    static constexpr std::array<std::string_view,9> names{{"hit_first","hit_middle","hit_last","hit_random",
        "miss_below","miss_between","miss_above","mixed_50","miss_empty"}};
    return names;
}
void validate_search_config(const SearchConfig& config) {
    validate_timing_config(config.timing);
    if (config.batch_size < 2 || config.batch_size > 100000 || config.batch_size % 2)
        throw std::invalid_argument("batch size must be even and in [2, 100000]");
    const auto limit = static_cast<std::uint64_t>(config.timing.memory_limit_mib)*1024*1024;
    const auto query_bytes = static_cast<std::uint64_t>(config.batch_size)*128*9;
    if (query_bytes > limit || config.timing.dataset.size > (limit-query_bytes)/16)
        throw std::invalid_argument("search input/query workspace exceeds planning budget");
    for (std::size_t i=0;i<config.categories.size();++i) {
        if (std::find(query_categories().begin(),query_categories().end(),config.categories[i])==query_categories().end())
            throw std::invalid_argument("unknown query category: "+config.categories[i]);
        if (std::find(config.categories.begin(),config.categories.begin()+static_cast<std::ptrdiff_t>(i),config.categories[i])!=config.categories.begin()+static_cast<std::ptrdiff_t>(i))
            throw std::invalid_argument("duplicate query category");
    }
}
namespace {
std::uint64_t bounded_query(std::mt19937_64& engine, std::uint64_t bound) {
    const auto threshold=(std::uint64_t{0}-bound)%bound;
    std::uint64_t word;do{word=engine();}while(word<threshold);
    return word%bound;
}
void require_sorted(const Values& sorted, const SearchConfig& config) {
    validate_search_config(config);
    if (sorted.size()!=config.timing.dataset.size || !std::is_sorted(sorted.begin(),sorted.end()))
        throw std::invalid_argument("search benchmark requires matching size and ascending sorted data");
}
}
std::uint64_t query_fingerprint(const std::vector<SearchQuery>& queries) noexcept {
    std::uint64_t hash=14695981039346656037ULL;
    const auto append=[&](std::uint64_t word,unsigned bytes){
        for(unsigned i=0;i<bytes;++i){hash^=(word>>(i*8))&255U;hash*=1099511628211ULL;}
    };
    for(const auto& q:queries){append(static_cast<std::uint32_t>(q.target),4);
        append(q.selected_position ? static_cast<std::uint64_t>(*q.selected_position) : std::numeric_limits<std::uint64_t>::max(),8);
        append(q.expected_position ? static_cast<std::uint64_t>(*q.expected_position) : std::numeric_limits<std::uint64_t>::max(),8);}
    return hash;
}
std::vector<SearchBatch> make_search_batches(const Values& sorted, const SearchConfig& config) {
    require_sorted(sorted,config);
    std::vector<std::size_t> gaps;
    // Bound capacity rather than allowing geometric vector growth to exceed the
    // input/gap workspace allowance used by the resource planning guard.
    gaps.reserve(sorted.size());
    for(std::size_t i=1;i<sorted.size();++i)
        if(static_cast<std::int64_t>(sorted[i])-sorted[i-1]>1)gaps.push_back(i-1);
    const bool below=!sorted.empty() && sorted.front()>std::numeric_limits<Key>::min();
    const bool above=!sorted.empty() && sorted.back()<std::numeric_limits<Key>::max();
    std::vector<unsigned> misses;if(below)misses.push_back(4);if(!gaps.empty())misses.push_back(5);if(above)misses.push_back(6);
    std::vector<SearchBatch> batches;
    for(std::size_t category=0;category<query_categories().size();++category) {
        const std::string name(query_categories()[category]);
        if(!config.categories.empty() && std::find(config.categories.begin(),config.categories.end(),name)==config.categories.end())continue;
        SearchBatch batch{name,{}, {}};
        if(category<4 && sorted.empty())batch.unavailable_reason="requires nonempty input";
        if(category==4 && !below)batch.unavailable_reason="requires a representable value below a nonempty range";
        if(category==5 && gaps.empty())batch.unavailable_reason="no adjacent distinct-value gap containing a missing integer";
        if(category==6 && !above)batch.unavailable_reason="requires a representable value above a nonempty range";
        if(category==7 && (sorted.empty() || misses.empty()))batch.unavailable_reason="requires nonempty input and an available miss policy";
        if(category==8 && !sorted.empty())batch.unavailable_reason="only applicable to empty input";
        if(!batch.unavailable_reason.empty()){batches.push_back(std::move(batch));continue;}
        std::mt19937_64 engine(config.query_seed ^ (0x9e3779b97f4a7c15ULL*(category+1)));
        batch.queries.reserve(config.batch_size);
        for(std::size_t i=0;i<config.batch_size;++i) {
            auto policy=category;
            if(category==7)policy=i%2 ? misses[bounded_query(engine,misses.size())] : 3;
            SearchQuery q{0,std::nullopt,std::nullopt};
            if(policy<4) {
                const auto position=policy==0 ? 0 : policy==1 ? sorted.size()/2 : policy==2 ? sorted.size()-1 : static_cast<std::size_t>(bounded_query(engine,sorted.size()));
                q.selected_position=position;q.target=sorted[position];
            } else if(policy==4)q.target=static_cast<Key>(static_cast<std::int64_t>(sorted.front())-1);
            else if(policy==6)q.target=static_cast<Key>(static_cast<std::int64_t>(sorted.back())+1);
            else if(policy==5) {
                const auto left=gaps[bounded_query(engine,gaps.size())];
                q.target=static_cast<Key>(static_cast<std::int64_t>(sorted[left])+(static_cast<std::int64_t>(sorted[left+1])-sorted[left])/2);
            } else q.target=static_cast<Key>(static_cast<std::int64_t>(static_cast<std::uint32_t>(engine()))-(std::int64_t{1}<<31));
            q.expected_position=std_lower_bound_search(sorted,q.target);
            batch.queries.push_back(q);
        }
        batches.push_back(std::move(batch));
    }
    return batches;
}
bool run_search_trials(const Values& sorted,const SearchConfig& config,const std::vector<SearchBatch>& batches,
                       const std::vector<Searcher>& algorithms,const std::function<void(const SearchTrial&)>& sink) {
    if(algorithms.empty() || !sink)throw std::invalid_argument("search algorithms and sink must be nonempty");
    for(std::size_t i=0;i<algorithms.size();++i) {
        if(!algorithms[i].search || algorithms[i].name.empty())throw std::invalid_argument("invalid searcher");
        for(std::size_t j=0;j<i;++j)if(algorithms[i].name==algorithms[j].name)throw std::invalid_argument("duplicate searcher");
    }
    // Reconstruct the deterministic plan once outside timing, rejecting stale or
    // tampered answers/queries/category availability supplied through the API.
    const auto expected_batches=make_search_batches(sorted,config);
    if(batches.size()!=expected_batches.size())throw std::invalid_argument("query plan size mismatch");
    for(std::size_t i=0;i<batches.size();++i) {
        const auto& a=batches[i];const auto& b=expected_batches[i];
        if(a.category!=b.category || a.unavailable_reason!=b.unavailable_reason || a.queries.size()!=b.queries.size())
            throw std::invalid_argument("query plan mismatch");
        for(std::size_t q=0;q<a.queries.size();++q)
            if(a.queries[q].target!=b.queries[q].target || a.queries[q].selected_position!=b.queries[q].selected_position || a.queries[q].expected_position!=b.queries[q].expected_position)
                throw std::invalid_argument("query answer/identity mismatch");
    }
    std::vector<SearchResult> answers(config.batch_size);
    using Clock=std::chrono::steady_clock;static_assert(Clock::is_steady,"monotonic clock required");
    for(const auto phase:{std::string_view{"warmup"},std::string_view{"measure"}}) {
        const auto rounds=phase=="warmup" ? config.timing.warmups : config.timing.repetitions;
        for(std::size_t trial=0;trial<rounds;++trial)for(const auto& batch:batches) {
            if(!batch.unavailable_reason.empty())continue;
            const auto offset=(config.timing.dataset.seed%algorithms.size()+trial%algorithms.size())%algorithms.size();
            for(std::size_t order=0;order<algorithms.size();++order) {
                const auto& algorithm=algorithms[(offset+order)%algorithms.size()];
                SearchTrial row{algorithm.name,batch.category,phase,trial,order,std::nullopt,"ok","passed",{}};
                try {
                    const auto start=Clock::now();
                    for(std::size_t q=0;q<batch.queries.size();++q)answers[q]=algorithm.search(sorted,batch.queries[q].target);
                    const auto stop=Clock::now();
                    const auto elapsed=std::chrono::duration_cast<std::chrono::nanoseconds>(stop-start).count();
                    if(elapsed<0)throw std::runtime_error("negative steady-clock duration");
                    row.elapsed_ns=static_cast<std::uint64_t>(elapsed);
                } catch(const std::exception& e){row.status="error";row.correctness="not_checked";row.error=e.what();}
                catch(...){row.status="error";row.correctness="not_checked";row.error="non-standard search exception";}
                if(row.status=="ok")for(std::size_t q=0;q<batch.queries.size();++q)if(answers[q]!=batch.queries[q].expected_position) {
                    row.status="error";row.correctness="failed";row.error="answer differs from first-match oracle at query "+std::to_string(q);break;
                }
                sink(row);if(row.status!="ok")return false;
            }
        }
    }
    return true;
}
}  // namespace mab
