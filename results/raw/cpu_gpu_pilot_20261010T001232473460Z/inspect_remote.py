import json,platform,subprocess,shutil,os
commands=[['nvidia-smi'],['nvcc','--version'],['cmake','--version'],['c++','--version'],['lscpu','-J'],['uname','-a']]
report={'platform':platform.platform(),'affinity':sorted(os.sched_getaffinity(0)),'commands':[]}
for command in commands:
 try:
  p=subprocess.run(command,capture_output=True,text=True,timeout=30);report['commands'].append({'argv':command,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 except (OSError,subprocess.TimeoutExpired) as error:report['commands'].append({'argv':command,'error':str(error)})
print(json.dumps(report,indent=2))
