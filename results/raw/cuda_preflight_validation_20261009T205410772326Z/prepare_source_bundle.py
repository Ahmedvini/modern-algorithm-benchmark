from pathlib import Path
import sys,json,hashlib,shutil,tarfile,gzip,io,tempfile,subprocess,difflib
root=Path.cwd();p=json.loads((root/'build/phase7_paths.json').read_text());e=root/p['evidence'];old=json.loads((e/'source_before.json').read_text());backup=root/p['backup']
h=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
files={f.relative_to(root).as_posix():h(f) for folder in ['include','src','scripts','tests','docs','cmake','third_party'] for f in (root/folder).rglob('*') if f.is_file() and '__pycache__' not in f.parts}
for name in ['AGENTS.md','README.md','CMakeLists.txt']:files[name]=h(root/name)
files=dict(sorted(files.items()));modified=sorted(f for f,s in old.items() if files[f]!=s);added=sorted(set(files)-set(old))
assert set(modified)=={'CMakeLists.txt','README.md','docs/ROADMAP.md','docs/AUDIT.md'}
assert len(files)==126 and len(added)==6 and len(old)-len(modified)==116
for f,s in old.items():assert h(backup/f)==s
with (e/'source_after.json').open('x') as stream:json.dump(files,stream,indent=2,sort_keys=True);stream.write('\n')
with (e/'file_changes.json').open('x') as stream:json.dump(dict(modified=modified,added=added,protected_original_files=116),stream,indent=2);stream.write('\n')
reviewed=e/'reviewed_source';reviewed.mkdir()
for name in files:
 out=reviewed/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/name,out)
shutil.copyfile(e/'source_after.json',reviewed/'SOURCE_SHA256.json')
patch=[]
for name in modified+added:
 before=(backup/name).read_text().splitlines(keepends=True) if name in old else []
 patch.extend(difflib.unified_diff(before,(root/name).read_text().splitlines(keepends=True),fromfile='a/'+name if name in old else '/dev/null',tofile='b/'+name))
with (e/'changes.patch').open('x') as stream:stream.write(''.join(patch))
def bundle():
 buffer=io.BytesIO()
 with gzip.GzipFile(fileobj=buffer,mode='wb',filename='',mtime=0) as zipped:
  with tarfile.open(fileobj=zipped,mode='w') as archive:
   for name in [*files,'SOURCE_SHA256.json']:
    data=(reviewed/name).read_bytes();info=tarfile.TarInfo('modern-algorithm-benchmark/'+name);info.size=len(data);info.mode=0o644;info.mtime=0;archive.addfile(info,io.BytesIO(data))
 return buffer.getvalue()
data=bundle();assert data==bundle()
archive=e/'phase7_source.tar.gz'
with archive.open('xb') as stream:stream.write(data)
records=[]
with tempfile.TemporaryDirectory(prefix='mab_cloud_source_check_') as temporary:
 cmd=['tar','-xzf',str(archive),'-C',temporary];r=subprocess.run(cmd,capture_output=True,text=True);records.append(dict(command=cmd,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0
 checkout=Path(temporary)/'modern-algorithm-benchmark';manifest=json.loads((checkout/'SOURCE_SHA256.json').read_text());assert manifest==files and all(h(checkout/f)==s for f,s in manifest.items())
 cmd=['cmake','-S',str(checkout),'-B',str(Path(temporary)/'build'),'-DCMAKE_BUILD_TYPE=Release','-DMAB_ENABLE_CUDA=OFF','-DMAB_ENABLE_OPENMP=OFF','-DBUILD_TESTING=OFF'];r=subprocess.run(cmd,capture_output=True,text=True);records.append(dict(command=cmd,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0
 cache=(Path(temporary)/'build/CMakeCache.txt').read_text();assert 'MAB_ENABLE_CUDA:BOOL=OFF' in cache and 'CMAKE_CUDA_COMPILER:' not in cache
result=dict(archive=archive.relative_to(root).as_posix(),sha256=h(archive),bytes=archive.stat().st_size,source_files=len(files),archive_members=len(files)+1,byte_identical_repack=True,extracted_source_hashes_match=True,relocated_cuda_off_configure_exit=0,commands=records)
for name,value in [('source_bundle.json',{k:v for k,v in result.items() if k!='commands'}),('source_bundle_validation.json',result)]:
 with (e/name).open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
with (e/'FINAL_AUDIT.md').open('a') as stream:stream.write('\nSource archive identity (local extraction/manifest/relocation check passed):\n```json\n'+json.dumps({k:v for k,v in result.items() if k!='commands'},indent=2,sort_keys=True)+'\n```\n')
print(json.dumps({k:v for k,v in result.items() if k!='commands'},indent=2));print(json.dumps(dict(modified=modified,added=added),indent=2))
