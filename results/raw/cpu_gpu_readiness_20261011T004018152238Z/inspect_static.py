"""Read/hash existing protocol, review and artifacts. Never execute project code."""
import hashlib
import json
from pathlib import Path
import shutil

root=Path.cwd();e=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(mapping):return {'count':len(mapping),'differences':[k for k,v in mapping.items() if not (root/k).is_file() or sha(root/k)!=v]}
review=root/'results/raw/ctest_path_independent_review_20261011T000547578754Z'
seal=read(review/'FINAL_INTEGRITY.json')
freeze=root/'docs/studies/cpu_gpu_comparison_v1.freeze.json'
cmake_review=root/'docs/CPU_GPU_DRIVER_REVIEW_v1.json'
assert sha(freeze)=='518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6'
assert sha(cmake_review)=='b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a'
frozen=verify(read(freeze)['files_sha256']);assert not frozen['differences']
matrix=read(root/'docs/studies/cpu_gpu_comparison_v1.matrix.json')
anchors=dict(matrix['source_at_freeze_sha256']);anchors['CMakeLists.txt']=read(cmake_review)['current_cmake_sha256']
anchor_result=verify(anchors);assert not anchor_result['differences']
review_result=verify(seal['evidence_sha256']);assert not review_result['differences']
policy=read(root/'docs/NON_TIMING_TEST_SELECTION_v1.json')
source=verify(policy['reviewed_source_sha256']);assert not source['differences']
assert sha(root/'third_party/cub/UPSTREAM.json')==seal['cub_pin_sha256']
assert sha(root/'src/cuda/cub_sort.cu')==seal['production_adapter_sha256']
caches=[]
for p in sorted((root/'build').rglob('CMakeCache.txt')):
    values={line.split('=',1)[0]:line.split('=',1)[1] for line in p.read_text(errors='replace').splitlines()
            if '=' in line and not line.startswith(('#','//'))}
    selected={k:v for k,v in values.items() if any(s in k for s in ['CMAKE_BUILD_TYPE:','CMAKE_HOME_DIRECTORY:',
        'CMAKE_CXX_COMPILER:','CMAKE_CUDA_COMPILER:','CMAKE_CXX_FLAGS','CMAKE_CUDA_FLAGS','CMAKE_CUDA_ARCHITECTURES',
        'MAB_ENABLE_','MAB_CUB_','OpenMP_CXX_','CUDAToolkit_'])}
    artifacts={name:{'present':(p.parent/name).is_file(),
        'sha256':sha(p.parent/name) if (p.parent/name).is_file() else None}
        for name in ['sort_benchmark','cpu_gpu_comparison','comparison_input','cuda_sort_benchmark','test_cuda_sorting']}
    dependency=values.get('MAB_CUB_INCLUDE_DIR:PATH')
    caches.append({'cache':str(p.relative_to(root)),'sha256':sha(p),'metadata':selected,
        'artifacts':artifacts,'cub_include_present':Path(dependency).is_dir() if dependency else None})
data={'frozen':frozen,'protected_anchors':anchor_result,'review_seal':review_result,
      'reviewed_source':source,'cub_pin':read(root/'third_party/cub/UPSTREAM.json'),
      'freeze_sha256':sha(freeze),'production_adapter_sha256':sha(root/'src/cuda/cub_sort.cu'),
      'build_caches':caches,'tools':{n:shutil.which(n) for n in ['cmake','python3','gcc','g++','nvcc','nvidia-smi','lscpu','ldconfig','colab']},
      'study_execution_authorized':False,'artifacts_executed':False}
with (e/'STATIC_READINESS.json').open('x') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(data,indent=2,sort_keys=True))
