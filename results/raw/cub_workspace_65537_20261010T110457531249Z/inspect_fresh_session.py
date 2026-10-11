import json, pathlib, subprocess, platform
for command in [["nvidia-smi"],["nvcc","--version"],["cmake","--version"],["g++","--version"]]:
 r=subprocess.run(command,capture_output=True,text=True)
 print(json.dumps(dict(argv=command,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr)))
 assert r.returncode==0
for name in ["/content/cub_workspace_65537_20261010T110457531249Z","/content/cub_workspace_source_65537.tar.gz"]:
 assert not pathlib.Path(name).exists(),name
print("FRESH_DESTINATION_CHECK_PASSED")
