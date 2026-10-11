#include <cuda_runtime.h>
#include <iostream>
#include <string>
#include <vector>

namespace {
std::string quote(const char* text) {
    std::string result="\"";
    const char* digits="0123456789abcdef";
    for (const unsigned char c:std::string(text)) {
        if (c=='"' || c=='\\') { result+='\\'; result+=static_cast<char>(c); }
        else if (c<32) { result+="\\u00"; result+=digits[c>>4]; result+=digits[c&15]; }
        else result+=static_cast<char>(c);
    }
    return result+'"';
}
__global__ void write_value(int* value) { *value=1729; }
}
int main() {
    int driver=0,runtime=0,count=0;
    const auto driver_status=cudaDriverGetVersion(&driver);
    const auto runtime_status=cudaRuntimeGetVersion(&runtime);
    auto status=cudaGetDeviceCount(&count);
    std::string stage="enumerate";
    int exit_code=(status!=cudaSuccess || count==0)?77:0;
    std::vector<cudaDeviceProp> devices;
    if (!exit_code) {
        for(int i=0;i<count;++i) {
            cudaDeviceProp prop{};status=cudaGetDeviceProperties(&prop,i);
            if(status!=cudaSuccess) { stage="properties";exit_code=1;break; }
            devices.push_back(prop);
        }
    }
    int* device=nullptr;int result=0;
    if(!exit_code) { stage="select";status=cudaSetDevice(0);if(status!=cudaSuccess)exit_code=1; }
    if(!exit_code) { stage="allocate";status=cudaMalloc(reinterpret_cast<void**>(&device),sizeof(int));if(status!=cudaSuccess)exit_code=1; }
    if(!exit_code) {
        stage="launch";write_value<<<1,1>>>(device);status=cudaGetLastError();if(status!=cudaSuccess)exit_code=1;
    }
    if(!exit_code) { stage="synchronize";status=cudaDeviceSynchronize();if(status!=cudaSuccess)exit_code=1; }
    if(!exit_code) { stage="copy_back";status=cudaMemcpy(&result,device,sizeof(int),cudaMemcpyDeviceToHost);if(status!=cudaSuccess)exit_code=1; }
    if(!exit_code && result!=1729) { stage="verify";exit_code=1; }
    if(device) {
        const auto freed=cudaFree(device);
        if(!exit_code && freed!=cudaSuccess) { stage="free";status=freed;exit_code=1; }
    }
    if(!exit_code)stage="complete";
    std::cout<<"{\"schema_version\":1,\"record_kind\":\"cuda_runtime_probe\",\"status\":"
             <<quote(exit_code==0?"ok":exit_code==77?"unavailable":"error")
             <<",\"stage\":"<<quote(stage.c_str())<<",\"cuda_error_code\":"<<static_cast<int>(status)
             <<",\"cuda_error\":"<<quote(cudaGetErrorString(status))
             <<",\"driver_api_version\":"<<(driver_status==cudaSuccess?std::to_string(driver):"null")
             <<",\"driver_version_status\":"<<static_cast<int>(driver_status)
             <<",\"runtime_api_version\":"<<(runtime_status==cudaSuccess?std::to_string(runtime):"null")
             <<",\"runtime_version_status\":"<<static_cast<int>(runtime_status)
             <<",\"device_count\":"<<count<<",\"tested_device\":"<<(exit_code==77?"null":"0")
             <<",\"kernel_result\":"<<result<<",\"devices\":[";
    for(std::size_t i=0;i<devices.size();++i) {
        if(i)std::cout<<',';
        const auto& prop=devices[i];
        std::cout<<"{\"ordinal\":"<<i<<",\"name\":"<<quote(prop.name)
                 <<",\"compute_major\":"<<prop.major<<",\"compute_minor\":"<<prop.minor
                 <<",\"total_global_memory_bytes\":"<<prop.totalGlobalMem<<'}';
    }
    std::cout<<"]}\n";
    return exit_code;
}
