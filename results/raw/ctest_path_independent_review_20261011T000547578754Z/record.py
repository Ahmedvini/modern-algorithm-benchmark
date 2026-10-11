import datetime,json,subprocess,sys
from pathlib import Path
e=Path(__file__).resolve().parent
name=sys.argv[1]; argv=sys.argv[2:]
r=subprocess.run(argv,capture_output=True,text=True)
d={'argv':argv,'cwd':str(Path.cwd()),'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'classification':'read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks'}
with (e/(name+'.json')).open('x') as f: json.dump(d,f,indent=2); f.write('\n')
print(r.stdout,end=''); print(r.stderr,end='',file=sys.stderr); print('RECORDED EXIT',r.returncode)
sys.exit(r.returncode)
