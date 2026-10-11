"""Inspect runtime files as files only; never load CUDA libraries or call APIs."""
import json
from pathlib import Path
libraries=[];macros={}
for prefix in [Path('/usr/local/cuda'),Path('/usr/local/cuda-13.0')]:
    for rel in ['lib64','targets/x86_64-linux/lib']:
        for p in sorted((prefix/rel).glob('libcudart.so*')):
            libraries.append(dict(path=str(p),resolved=str(p.resolve()),bytes=p.stat().st_size))
    for name in ['cuda_runtime_api.h','cuda.h','driver_types.h']:
        p=prefix/'include'/name
        if p.is_file():
            macros[str(p)]=[l for l in p.read_text().splitlines()
                if l.startswith(('#define CUDART_VERSION','#define CUDA_VERSION'))]
driver=Path('/proc/driver/nvidia/version')
print('MAB_RUNTIME_FILES_BEGIN')
print(json.dumps(dict(libraries=libraries,version_header_macros=macros,
    driver_version_file=driver.read_text() if driver.is_file() else None,
    device_nodes={str(p):p.exists() for p in [Path('/dev/nvidiactl'),Path('/dev/nvidia0')]},
    cuda_library_loaded=False,cuda_api_executed=False),indent=2))
print('MAB_RUNTIME_FILES_END')
