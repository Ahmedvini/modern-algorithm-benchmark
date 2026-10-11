#include "benchmark/search_timing.hpp"
#include "benchmark/output.hpp"
#include "benchmark_build.hpp"
#ifdef MAB_SEARCH_COUNTS
#include "benchmark/search_comparisons.hpp"
#endif
#include <algorithm>
#include <charconv>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <locale>
#include <sstream>
#include <thread>

namespace fs=std::filesystem;
namespace {
template<typename T>T number(std::string_view text){
    T value{};const auto parsed=std::from_chars(text.data(),text.data()+text.size(),value);
    if(text.empty() || parsed.ec!=std::errc{} || parsed.ptr!=text.data()+text.size())
        throw std::invalid_argument("expected unsigned decimal integer: "+std::string(text));
    return value;
}
std::vector<std::string> split(std::string_view text){
    std::vector<std::string> result;
    while(true){const auto comma=text.find(',');result.emplace_back(text.substr(0,comma));
        if(comma==std::string_view::npos) break;
        text.remove_prefix(comma+1);
    }
    return result;
}
std::vector<mab::Searcher> select(std::string_view names){
    if(names=="all")return {mab::searchers().begin(),mab::searchers().end()};
    std::vector<mab::Searcher> result;
    for(const auto& name:split(names)){
        const auto& algorithm=mab::find_searcher(name);
        for(const auto& previous:result)if(previous.name==name)throw std::invalid_argument("duplicate searcher");
        result.push_back(algorithm);
    }
    return result;
}
std::ofstream file(const fs::path& path){
    std::ofstream stream;stream.exceptions(std::ios::badbit|std::ios::failbit);
    stream.imbue(std::locale::classic());stream.open(path,std::ios::binary);return stream;
}
void json_file(const fs::path& path,const std::string& data){auto stream=file(path);stream<<data<<'\n';stream.close();}
std::string optional_text(const fs::path& path){std::ifstream stream(path);return stream ? std::string(std::istreambuf_iterator<char>(stream),{}) : std::string{};}
std::string position(mab::SearchResult value){return value ? std::to_string(*value) : "";}
std::string strings(const std::vector<std::string>& items){
    std::string result="[";for(std::size_t i=0;i<items.size();++i){if(i)result+=',';result+=mab::json_string(items[i]);}return result+"]";
}
struct Object {
    std::ostringstream stream;bool first=true;
    Object(){stream.imbue(std::locale::classic());stream<<'{';}
    void raw(std::string_view name,const std::string& encoded){if(!first)stream<<',';first=false;stream<<mab::json_string(name)<<':'<<encoded;}
    void text(std::string_view name,std::string_view value){raw(name,mab::json_string(value));}
    void integer(std::string_view name,std::uint64_t value){raw(name,std::to_string(value));}
    std::string finish(){return stream.str()+"}";}
};
void usage(){
#ifdef MAB_SEARCH_COUNTS
    std::cout<<"Usage: search_counts --output NEW_DIRECTORY (separate counts; no timing)\n";
#else
    std::cout<<"Usage: search_benchmark --output NEW_DIRECTORY [--repetitions R] [--warmups W] [--validation-only]\n";
#endif
    std::cout<<"  [--search NAME[,NAME...]|all] [--size N] [--seed S] [--query-seed S]\n"
        "  [--distribution uniform|sorted|reverse_sorted|duplicate_heavy|nearly_sorted]\n"
        "  [--queries Q] [--categories NAME[,NAME...]|all] [--swaps K] [--distinct K]\n"
        "  [--memory-limit-mib M] [--run-id ID] [--list-searches] [--help]\n"
        "Defaults: linear_search, N=1000, seed=1729, query-seed=2718, uniform, Q=1000, all categories, M=256.\n";
}
}
int main(int argc,char** argv){
    fs::path output;bool owns=false;
    try{
        mab::SearchConfig config;std::string names="linear_search",run_id;bool validation=false;
        std::vector<std::string> invocation;for(int i=0;i<argc;++i)invocation.emplace_back(argv[i]);
        for(int i=1;i<argc;++i){
            const std::string_view option(argv[i]);
            if(option=="--help"){usage();return 0;}
            if(option=="--list-searches"){for(const auto& s:mab::searchers())std::cout<<s.name<<'\n';return 0;}
#ifndef MAB_SEARCH_COUNTS
            if(option=="--validation-only"){validation=true;continue;}
#endif
            if(option!="--output" && option!="--search" && option!="--size" && option!="--seed" && option!="--query-seed" &&
               option!="--distribution" && option!="--queries" && option!="--categories" && option!="--swaps" && option!="--distinct" &&
               option!="--memory-limit-mib" && option!="--run-id"
#ifndef MAB_SEARCH_COUNTS
               && option!="--repetitions" && option!="--warmups"
#endif
               )throw std::invalid_argument("unknown option: "+std::string(option));
            if(++i==argc)throw std::invalid_argument("missing value for "+std::string(option));
            const std::string_view value(argv[i]);
            if(option=="--output")output=std::string(value);
            else if(option=="--search"){(void)select(value);names=value;}
            else if(option=="--size")config.timing.dataset.size=number<std::size_t>(value);
            else if(option=="--seed")config.timing.dataset.seed=number<std::uint64_t>(value);
            else if(option=="--query-seed")config.query_seed=number<std::uint64_t>(value);
            else if(option=="--queries")config.batch_size=number<std::size_t>(value);
            else if(option=="--distribution"){
                config.timing.sorted_input=value=="sorted";
                if(!config.timing.sorted_input)config.timing.dataset.distribution=mab::parse_distribution(value);
            }else if(option=="--categories"){
                config.categories=value=="all" ? std::vector<std::string>{} : split(value);
                mab::SearchConfig category_check;
                category_check.categories=config.categories;
                mab::validate_search_config(category_check);
            }
            else if(option=="--swaps")config.timing.dataset.nearly_sorted_swaps=number<std::size_t>(value);
            else if(option=="--distinct")config.timing.dataset.duplicate_cardinality=number<std::uint64_t>(value);
            else if(option=="--memory-limit-mib")config.timing.memory_limit_mib=number<std::size_t>(value);
            else if(option=="--repetitions")config.timing.repetitions=number<std::size_t>(value);
            else if(option=="--warmups")config.timing.warmups=number<std::size_t>(value);
            else run_id=value;
        }
        mab::validate_search_config(config);const auto algorithms=select(names);
        if(output.empty())throw std::invalid_argument("--output NEW_DIRECTORY is required");
#ifndef MAB_SEARCH_COUNTS
        if(!validation && (std::string_view(mab::build::configuration)!="Release" || mab::build::sanitizers))
            throw std::invalid_argument("performance requires Release without sanitizers; use --validation-only for tests");
#else
        (void)validation;
#endif
        if(run_id.empty()) run_id=output.filename().string();
        if(run_id.empty()) throw std::invalid_argument("empty run identifier");
        if(!fs::create_directory(output)) throw std::runtime_error("output already exists: "+output.string());
        owns=true;
        auto data=mab::make_timing_input(config.timing);
#ifndef MAB_SEARCH_COUNTS
        using Clock=std::chrono::steady_clock;const auto preprocess_start=Clock::now();
#endif
        std::sort(data.begin(),data.end());
#ifndef MAB_SEARCH_COUNTS
        const auto preprocess_ns=std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now()-preprocess_start).count();
#endif
        const auto batches=mab::make_search_batches(data,config);
        const auto input_hash=std::to_string(mab::input_fingerprint(data));
        std::size_t available=0,query_rows=0,total_hits=0;
        std::string category_plan="[";
        for(std::size_t b=0;b<batches.size();++b){
            const auto& batch=batches[b];const auto hits=static_cast<std::size_t>(std::count_if(batch.queries.begin(),batch.queries.end(),[](const auto& q){return q.expected_position.has_value();}));
            Object entry;entry.text("category",batch.category);entry.raw("available",batch.unavailable_reason.empty()?"true":"false");entry.text("reason",batch.unavailable_reason);
            entry.integer("batch_size",batch.queries.size());entry.integer("hit_queries",hits);entry.integer("miss_queries",batch.queries.size()-hits);
            entry.text("query_hash_fnv1a64",std::to_string(mab::query_fingerprint(batch.queries)));
            if(b) category_plan+=',';
            category_plan+=entry.finish();
            if(batch.unavailable_reason.empty()) ++available;
            query_rows+=batch.queries.size();
            total_hits+=hits;
        }
        category_plan+=']';
        std::vector<std::string> algorithm_names;for(const auto& a:algorithms)algorithm_names.emplace_back(a.name);
#ifdef MAB_SEARCH_COUNTS
        const std::string protocol="search_counts_v1",kind="comparison_counts";
        const auto expected_rows=query_rows*algorithms.size();
#else
        const std::string protocol="search_batch_v1",kind=validation?"validation":"performance";
        const auto expected_rows=available*algorithms.size()*(config.timing.repetitions+config.timing.warmups);
#endif
        Object meta;meta.integer("schema_version",1);meta.text("protocol",protocol);meta.text("run_id",run_id);meta.text("run_kind",kind);
        meta.integer("size",data.size());meta.integer("seed",config.timing.dataset.seed);meta.text("distribution",mab::timing_distribution(config.timing));
        meta.integer("nearly_sorted_swaps",mab::timing_swaps(config.timing));meta.integer("duplicate_cardinality",config.timing.dataset.duplicate_cardinality);
        meta.text("dataset_generator","mt19937_64_v1");meta.text("input_hash_fnv1a64",input_hash);meta.text("input_order","ascending");
        meta.text("preprocessing","std_sort_ascending_outside_lookup");meta.integer("query_seed",config.query_seed);meta.text("query_generator","mt19937_64_queries_v1");
        meta.integer("batch_size",config.batch_size);meta.raw("algorithms",strings(algorithm_names));meta.raw("categories",category_plan);
        meta.integer("query_rows",query_rows);meta.integer("hit_queries",total_hits);meta.integer("miss_queries",query_rows-total_hits);
        meta.integer("expected_rows",expected_rows);meta.integer("memory_limit_mib",config.timing.memory_limit_mib);
        meta.integer("planned_array_query_bytes",static_cast<std::uint64_t>(data.size())*16+static_cast<std::uint64_t>(config.batch_size)*128*9);
        meta.text("compiler_id",mab::build::compiler_id);meta.text("compiler_version",mab::build::compiler_version);meta.text("compiler_path",mab::build::compiler_path);
        meta.text("build_type",mab::build::configuration);meta.raw("sanitizers",mab::build::sanitizers?"true":"false");meta.integer("cplusplus",__cplusplus);
        meta.text("platform",mab::build::platform);meta.text("architecture",mab::build::architecture);
        meta.text("cmake_global_flags",mab::build::global_flags);meta.text("cmake_configuration_flags",mab::build::configuration_flags);
        meta.raw("invocation",strings(invocation));meta.integer("started_unix_seconds",static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now().time_since_epoch()).count()));
        meta.integer("logical_cpu_count_hint",std::thread::hardware_concurrency());meta.text("linux_cpuinfo",optional_text("/proc/cpuinfo"));meta.text("linux_meminfo",optional_text("/proc/meminfo"));
#ifndef MAB_SEARCH_COUNTS
        meta.integer("repetitions",config.timing.repetitions);meta.integer("warmups",config.timing.warmups);meta.text("clock","steady_clock");
        meta.integer("clock_period_num",Clock::period::num);meta.integer("clock_period_den",Clock::period::den);
        meta.text("elapsed_unit","ns");meta.text("order_policy","seed_offset_cyclic_v1");meta.integer("preprocessing_sort_ns",static_cast<std::uint64_t>(preprocess_ns));
#else
        meta.text("comparison_convention","key_predicate_v1");
#endif
        for(const auto name:{"CMakeCache.txt","compile_commands.json","pdqsort_upstream.json","timsort_upstream.json"}){
            const auto path=fs::path(mab::build::binary_dir)/name;if(fs::exists(path))fs::copy_file(path,output/name);
        }
        fs::copy_file(fs::path(mab::build::binary_dir)/"generated"/mab::build::configuration/"source_hashes.json",output/"source_hashes.json");
        json_file(output/"run.json",meta.finish());
        auto queries=file(output/"queries.csv");mab::write_csv_row(queries,{"query_category","query_id","target","selected_position","expected_position","expected_hit"});
        for(const auto& batch:batches)for(std::size_t i=0;i<batch.queries.size();++i){const auto& q=batch.queries[i];
            mab::write_csv_row(queries,{batch.category,std::to_string(i),std::to_string(q.target),position(q.selected_position),position(q.expected_position),q.expected_position?"true":"false"});}
        queries.close();std::size_t actual=0;
#ifdef MAB_SEARCH_COUNTS
        auto csv=file(output/"counts.csv");mab::write_csv_row(csv,{"algorithm","query_category","query_id","target","expected_position","actual_position","key_comparisons","comparison_convention","correctness"});
        for(const auto& batch:batches)for(const auto& a:algorithms)for(std::size_t i=0;i<batch.queries.size();++i){const auto& q=batch.queries[i];const auto result=mab::counted_search(a.name,data,q.target);
            const bool correct=result.position==q.expected_position;
            mab::write_csv_row(csv,{std::string(a.name),batch.category,std::to_string(i),std::to_string(q.target),position(q.expected_position),position(result.position),std::to_string(result.key_comparisons),"key_predicate_v1",correct?"passed":"failed"});
            csv.flush();++actual;if(!correct)throw std::runtime_error("counted search answer mismatch");}
#else
        auto csv=file(output/"trials.csv");mab::write_csv_row(csv,{"schema_version","protocol","run_id","run_kind","algorithm","distribution","size","seed","input_hash_fnv1a64","query_seed","query_generator","query_category","query_hash_fnv1a64","batch_size","hit_queries","miss_queries","phase","trial_index","execution_order","elapsed_ns","elapsed_unit","status","correctness","error","repetitions","warmups","compiler_id","compiler_version","build_type","sanitizers","platform","architecture"});
        const auto complete=mab::run_search_trials(data,config,batches,algorithms,[&](const mab::SearchTrial& row){
            const auto batch=std::find_if(batches.begin(),batches.end(),[&](const auto& b){return b.category==row.category;});
            const auto hits=std::count_if(batch->queries.begin(),batch->queries.end(),[](const auto& q){return q.expected_position.has_value();});
            mab::write_csv_row(csv,{"1",protocol,run_id,kind,std::string(row.algorithm),std::string(mab::timing_distribution(config.timing)),std::to_string(data.size()),std::to_string(config.timing.dataset.seed),input_hash,std::to_string(config.query_seed),"mt19937_64_queries_v1",std::string(row.category),std::to_string(mab::query_fingerprint(batch->queries)),std::to_string(config.batch_size),std::to_string(hits),std::to_string(batch->queries.size()-static_cast<std::size_t>(hits)),std::string(row.phase),std::to_string(row.trial_index),std::to_string(row.execution_order),row.elapsed_ns?std::to_string(*row.elapsed_ns):"","ns",std::string(row.status),std::string(row.correctness),row.error,std::to_string(config.timing.repetitions),std::to_string(config.timing.warmups),mab::build::compiler_id,mab::build::compiler_version,mab::build::configuration,mab::build::sanitizers?"true":"false",mab::build::platform,mab::build::architecture});
            csv.flush();++actual;
        });
        if(!complete)throw std::runtime_error("search failed; inspect retained trials.csv");
#endif
        csv.close();if(actual!=expected_rows)throw std::runtime_error("incomplete row count");
        json_file(output/"COMPLETE.json","{\"schema_version\":1,\"complete\":true,\"rows\":"+std::to_string(actual)+"}");
        std::cout<<"Completed "<<actual<<" rows; available categories="<<available<<"; raw data: "<<output<<'\n';return 0;
    }catch(const std::exception& error){
        if(owns)try{json_file(output/"FAILED.json","{\"complete\":false,\"error\":"+mab::json_string(error.what())+"}");}catch(...){}
        std::cerr<<"error: "<<error.what()<<'\n';return 1;
    }
}
