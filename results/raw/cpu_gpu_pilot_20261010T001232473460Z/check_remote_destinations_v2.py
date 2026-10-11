from pathlib import Path
paths=[Path('/content/cpu_gpu_pilot_20261010T001232473460Z_source_v2.tar.gz'),Path('/content/cpu_gpu_pilot_20261010T001232473460Z_v2')]
for p in paths:
 if p.exists() or p.is_symlink():raise RuntimeError('Refusing existing remote destination: '+str(p))
print('Exclusive remote destinations available:',*[str(p) for p in paths])
