#include "algorithms/cuda_sorting.hpp"
#include "benchmark/comparison.hpp"
#include "benchmark/cuda_comparison.hpp"
#include "benchmark/output.hpp"
#include "benchmark/memory.hpp"
#include "benchmark_build.hpp"
#include "cuda_benchmark_build.hpp"
#include "parallel_build.hpp"
#include <algorithm>
#include <charconv>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <map>
#include <sstream>
#include <stdexcept>

namespace fs=std::filesystem;
namespace {
template<class T> T number(const std::string& s) {
    T value{}; const auto r=std::from_chars(s.data(),s.data()+s.size(),value);
    if(s.empty() || r.ec!=std::errc{} || r.ptr!=s.data()+s.size()) throw std::invalid_argument("expected unsigned decimal");
    return value;
}
struct Object {
    std::map<std::string,std::string> fields;
    void text(const std::string& k,const std::string& v) { fields[k]=mab::json_string(v); }
    void integer(const std::string& k,std::uint64_t v) { fields[k]=std::to_string(v); }
    std::string str() const {
        std::string result="{"; bool first=true;
        for(const auto& f:fields) { if(!first)result+=','; first=false; result+=mab::json_string(f.first)+':'+f.second; }
        return result+'}';
    }
};
std::ofstream file(const fs::path& p) {
    std::ofstream out; out.exceptions(std::ios::badbit|std::ios::failbit);
    out.imbue(std::locale::classic()); out.open(p,std::ios::binary);return out;
}
void json(const fs::path& p,const Object& o) { auto out=file(p);out<<o.str()<<'\n';out.close(); }
std::string decimal(double v) { std::ostringstream s;s.imbue(std::locale::classic());s<<std::setprecision(17)<<v;return s.str(); }
Object describe() {
    Object o;
    o.text("compiler_id",mab::build::compiler_id);o.text("compiler_version",mab::build::compiler_version);
    o.text("compiler_path",mab::build::compiler_path);o.text("build_type",mab::build::configuration);
    o.fields["sanitizers"]=mab::build::sanitizers?"true":"false";
    o.text("global_flags",mab::build::global_flags);o.text("configuration_flags",mab::build::configuration_flags);
    o.text("platform",mab::build::platform);o.text("architecture",mab::build::architecture);
    o.text("source_dir",mab::build::source_dir);o.text("binary_dir",mab::build::binary_dir);
    o.text("cuda_compiler_version",mab::cuda_build::compiler_version);o.text("cuda_toolkit_version",mab::cuda_build::toolkit_version);
    o.text("cuda_flags",mab::cuda_build::flags);o.text("cuda_release_flags",mab::cuda_build::release_flags);
    o.text("cuda_architectures",mab::cuda_build::architectures);
    o.text("openmp_version",mab::parallel_build::version);o.text("openmp_flags",mab::parallel_build::flags);
    o.text("openmp_libraries",mab::parallel_build::libraries);o.integer("cub_version",mab::cuda_sort_cub_version());
    o.integer("cxx_standard",17);o.text("implementation_version","cpu_gpu_comparison_driver_v1");
    return o;
}
Object resource_object(const mab::CudaComparisonResources& r,std::size_t n) {
    Object o;o.integer("size",n);o.text("gpu_name",r.gpu_name);
    o.integer("compute_major",r.compute_major);o.integer("compute_minor",r.compute_minor);
    o.integer("runtime_api_version",r.runtime_version);o.integer("driver_api_version",r.driver_version);
    o.integer("free_device_bytes_before_buffers",r.free_device_bytes);o.integer("total_device_bytes",r.total_device_bytes);
    o.integer("prepared_query_bytes",r.prepared_query_bytes);o.integer("adapter_query_bytes",r.adapter_query_bytes);
    o.integer("prepared_diagnostic_cudaMalloc_requested_bytes",r.prepared_diagnostic_allocation_bytes);
    o.integer("adapter_diagnostic_cudaMalloc_requested_bytes",r.adapter_diagnostic_allocation_bytes);
    o.integer("workspace_policy_cap_each_bytes",64*1024*1024);o.integer("known_host_peak_payload_bytes",24*n);
    o.integer("combined_device_payload_bytes",16*n+r.prepared_diagnostic_allocation_bytes+r.adapter_diagnostic_allocation_bytes);
    o.text("production_workspace_observation","not instrumented; isolated same-parameter sizing query only");
    o.text("allocation_observation","successful diagnostic cudaMalloc request sizes; allocator physical footprint not measured");
    return o;
}
const std::vector<std::string> primary_fields={"schema_version","protocol","run_id","matrix_sha256","build_id","environment_id",
    "dataset_id","input_sha256","input_hash_fnv1a64","size","distribution","seed","dataset_generator","nearly_sorted_swaps",
    "duplicate_cardinality","backend_id","algorithm","implementation_identity_ref","scope","phase","trial_index","execution_order",
    "global_trial_index","requested_cpu_threads","actual_cpu_threads","parallel_region","elapsed_ns","elapsed_unit","status","correctness","error"};
const std::vector<std::string> prepared_fields={"schema_version","protocol","run_id","algorithm","implementation_version","distribution","size",
    "seed","nearly_sorted_swaps","duplicate_cardinality","dataset_generator","input_hash_fnv1a64","phase","trial_index",
    "h2d_ns","device_sort_ns","d2h_ns","end_to_end_ns","elapsed_unit","status","correctness","error"};
}
int main(int argc,char** argv) {
    fs::path output;bool owns=false;
    try {
        if(argc==2 && std::string(argv[1])=="--describe") { std::cout<<describe().str()<<'\n';return 0; }
        if(argc==3 && std::string(argv[1])=="--resources") {
            auto n=number<std::size_t>(argv[2]);std::cout<<resource_object(mab::query_comparison_resources(n),n).str()<<'\n';return 0;
        }
        std::map<std::string,std::string> a;
        const std::vector<std::string> required={"--output","--input","--size","--distribution","--seed","--swaps","--distinct",
            "--dataset-id","--input-sha256","--input-fnv","--matrix-sha256","--build-id","--environment-id","--run-id","--global-offset","--base-order"};
        for(int i=1;i<argc;i+=2) {
            if(i+1==argc || std::find(required.begin(),required.end(),argv[i])==required.end() || !a.emplace(argv[i],argv[i+1]).second)
                throw std::invalid_argument("invalid/duplicate argument");
        }
        if(a.size()!=required.size()) throw std::invalid_argument("missing required arguments");
        for(const auto name:{"--dataset-id","--input-sha256","--matrix-sha256","--build-id","--environment-id"}) {
            const auto& s=a.at(name);
            if(s.size()!=64 || s.find_first_not_of("0123456789abcdef")!=std::string::npos) throw std::invalid_argument("invalid SHA256 identifier");
        }
        if(std::string(mab::build::configuration)!="Release" || mab::build::sanitizers)
            throw std::invalid_argument("primary comparison requires unsanitized Release");
        const auto n=number<std::size_t>(a.at("--size"));
        if(n!=1025 && n!=65537 && n!=1000000) throw std::invalid_argument("size outside frozen domain");
        (void)number<std::uint64_t>(a.at("--seed"));(void)number<std::size_t>(a.at("--swaps"));
        if(number<std::size_t>(a.at("--distinct"))!=16) throw std::invalid_argument("cardinality outside frozen domain");
        const auto offset=number<std::size_t>(a.at("--global-offset"));
        if(offset>1410) throw std::invalid_argument("global trial offset outside bounded matrix");
        const auto& distribution=a.at("--distribution");
        if(distribution!="signed_edges" && distribution!="sorted") (void)mab::parse_distribution(distribution);
        output=a.at("--output");if(!fs::create_directory(output)) throw std::runtime_error("output already exists");owns=true;
        std::ifstream input(a.at("--input"),std::ios::binary);
        const auto original=mab::read_comparison_input(n,input);
        const auto fingerprint=std::to_string(mab::input_fingerprint(original));
        if(fingerprint!=a.at("--input-fnv")) throw std::runtime_error("input fingerprint mismatch");
        auto oracle=original;std::sort(oracle.begin(),oracle.end());mab::Values working(n);
        const auto queried=mab::query_comparison_resources(n);
        auto resource=resource_object(queried,n);
        mab::CudaTimingSession session(n,256);
        if(session.info().workspace_bytes!=queried.prepared_query_bytes) throw std::runtime_error("prepared workspace query changed");
        resource.integer("prepared_session_query_bytes",session.info().workspace_bytes);
        resource.integer("prepared_session_cudaMalloc_requested_bytes",std::max(session.info().workspace_bytes,std::size_t{1}));
        resource.integer("prepared_pinned_host_buffers_requested_bytes",8*n);
        resource.integer("prepared_device_key_buffers_requested_bytes",8*n);
        json(output/"resources.json",resource);
        const auto& cpu_std=mab::find_sorter("std_sort");const auto& cpu_merge=mab::find_sorter("merge_sort");
        const auto parallel=mab::find_parallel_sorter("parallel_merge_sort",2);const auto& gpu=mab::find_cuda_sorter("cub_radix_sort");
        std::map<std::string,mab::ComparisonBackend> modes;
        modes.emplace("cpu_std_sort",mab::ComparisonBackend{"cpu_std_sort",cpu_std.sort,nullptr,{}});
        modes.emplace("cpu_merge_sort",mab::ComparisonBackend{"cpu_merge_sort",cpu_merge.sort,nullptr,{}});
        modes.emplace("cpu_parallel_merge_sort_t2",mab::ComparisonBackend{"cpu_parallel_merge_sort_t2",nullptr,parallel.sort,{}});
        modes.emplace("gpu_cub_adapter",mab::ComparisonBackend{"gpu_cub_adapter",gpu.sort,nullptr,{}});
        modes.emplace("gpu_cub_prepared",mab::ComparisonBackend{"gpu_cub_prepared",nullptr,nullptr,
            [&](const mab::Values& in,mab::Values& out){return session.sample(in,out);}});
        std::array<mab::ComparisonBackend,5> order;
        std::istringstream ids(a.at("--base-order"));std::string id;std::size_t index=0;
        while(std::getline(ids,id,',')) { if(index==5) throw std::invalid_argument("too many modes");order[index++]=modes.at(id); }
        if(index!=5) throw std::invalid_argument("incomplete mode order");
        std::vector<std::uint64_t> calibration;calibration.reserve(1000);
        for(int i=0;i<1000;++i) { const auto start=std::chrono::steady_clock::now();const auto stop=std::chrono::steady_clock::now();
            calibration.push_back(static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(stop-start).count())); }
        std::sort(calibration.begin(),calibration.end());Object clock;
        clock.integer("pairs",1000);clock.fields["median_ns"]=decimal((calibration[499]+calibration[500])/2.0);
        clock.text("policy","diagnostic_only_no_subtraction");json(output/"timer_calibration.json",clock);
        auto prepared_dir=output/"prepared";fs::create_directory(prepared_dir);
        auto meta=describe();meta.text("protocol","cuda_sort_timing_v1");meta.integer("schema_version",1);
        meta.text("run_id",a.at("--run-id"));meta.text("algorithm","cub_radix_sort");meta.text("implementation_version","cub_radix_sort_v1");
        meta.text("distribution",distribution);meta.integer("size",n);meta.integer("seed",number<std::uint64_t>(a.at("--seed")));
        meta.integer("nearly_sorted_swaps",number<std::uint64_t>(a.at("--swaps")));meta.integer("duplicate_cardinality",16);
        meta.text("dataset_generator",distribution=="signed_edges"?"signed_edges_v1":"mt19937_64_v1");meta.text("input_hash_fnv1a64",fingerprint);
        meta.integer("warmups",1);meta.integer("repetitions",5);meta.integer("expected_rows",6);meta.text("elapsed_unit","ns");
        meta.text("run_kind","performance");meta.text("allocation_policy","prepared_pinned_reuse_v1");meta.text("stream_policy","private_nonblocking_serial");
        meta.text("end_to_end_clock","steady_clock");meta.text("phase_clock","cuda_event_float_ms_to_ns");
        meta.text("gpu_name",session.info().device_name);meta.integer("requested_device",session.info().device);meta.integer("actual_device",session.info().device);
        meta.integer("compute_major",session.info().compute_major);meta.integer("compute_minor",session.info().compute_minor);
        meta.integer("runtime_api_version",session.info().runtime_version);meta.integer("driver_api_version",session.info().driver_version);
        meta.integer("device_memory_bytes",session.info().device_memory_bytes);meta.integer("workspace_bytes",session.info().workspace_bytes);
        json(prepared_dir/"run.json",meta);
        auto primary=file(output/"primary.csv"),prepared=file(prepared_dir/"trials.csv"),sidecar=file(output/"prepared_order.csv"),attempts=file(output/"attempts.jsonl");
        mab::write_csv_row(primary,primary_fields);mab::write_csv_row(prepared,prepared_fields);
        mab::write_csv_row(sidecar,{"dataset_id","backend_id","phase","trial_index","execution_order","global_trial_index"});
        const auto generator=distribution=="signed_edges"?"signed_edges_v1":"mt19937_64_v1";
        const auto ok=mab::run_comparison_trials(original,oracle,working,order,mab::synchronize_comparison_device,
            [&](const mab::ComparisonTrial& t) {
                Object event;event.text("backend_id",t.backend);event.text("phase",t.phase);event.integer("trial_index",t.trial_index);
                event.integer("execution_order",t.execution_order);event.integer("global_trial_index",offset+t.execution_order);
                attempts<<event.str()<<'\n';attempts.flush();
            },[&](const mab::ComparisonTrial& t) {
                const bool success=t.status=="ok";
                if(t.prepared) {
                    const auto& d=t.diagnostics;
                    mab::write_csv_row(prepared,{"1","cuda_sort_timing_v1",a.at("--run-id"),"cub_radix_sort","cub_radix_sort_v1",distribution,
                        a.at("--size"),a.at("--seed"),a.at("--swaps"),"16",generator,fingerprint,t.phase,std::to_string(t.trial_index),
                        success?decimal(d.h2d_ns):"",success?decimal(d.device_sort_ns):"",success?decimal(d.d2h_ns):"",
                        success?std::to_string(d.end_to_end_ns):"","ns",t.status,t.correctness,t.error});prepared.flush();
                    mab::write_csv_row(sidecar,{a.at("--dataset-id"),t.backend,t.phase,std::to_string(t.trial_index),std::to_string(t.execution_order),std::to_string(offset+t.execution_order)});sidecar.flush();
                } else {
                    const bool is_gpu=t.backend=="gpu_cub_adapter",is_parallel=t.backend=="cpu_parallel_merge_sort_t2";
                    const auto algorithm=is_gpu?"cub_radix_sort":is_parallel?"parallel_merge_sort":t.backend=="cpu_std_sort"?"std_sort":"merge_sort";
                    mab::write_csv_row(primary,{"1","cpu_gpu_host_call_v1",a.at("--run-id"),a.at("--matrix-sha256"),a.at("--build-id"),a.at("--environment-id"),
                        a.at("--dataset-id"),a.at("--input-sha256"),fingerprint,a.at("--size"),distribution,a.at("--seed"),generator,a.at("--swaps"),"16",
                        t.backend,algorithm,t.backend,"host_vector_api_call_v1",t.phase,std::to_string(t.trial_index),std::to_string(t.execution_order),
                        std::to_string(offset+t.execution_order),is_gpu?"":is_parallel?"2":"1",is_gpu?"":success?std::to_string(t.parallel_info.actual_threads):"",
                        is_gpu?"":success?(t.parallel_info.parallel_region?"true":"false"):"",t.elapsed_ns?std::to_string(*t.elapsed_ns):"","ns",t.status,t.correctness,t.error});primary.flush();
                }
            });
        primary.close();prepared.close();sidecar.close();attempts.close();session.close();
        if(!ok) throw std::runtime_error("comparison trial failed; partial rows retained");
        auto memory=file(output/"process_memory.json");mab::write_memory_json(memory,mab::process_memory());memory<<'\n';memory.close();
        Object complete;complete.integer("schema_version",1);complete.fields["complete"]="true";complete.integer("rows",6);json(prepared_dir/"COMPLETE.json",complete);
        complete.integer("rows",30);json(output/"COMPLETE.json",complete);return 0;
    } catch(const std::exception& error) {
        if(owns) {try {Object fail;fail.fields["complete"]="false";fail.text("error",error.what());json(output/"FAILED.json",fail);}catch(...) {}}
        std::cerr<<"error: "<<error.what()<<'\n';return 1;
    }
}
