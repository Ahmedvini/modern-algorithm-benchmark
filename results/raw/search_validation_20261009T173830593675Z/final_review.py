import difflib,hashlib,json,re
from pathlib import Path
root=Path.cwd();raw=Path(__file__).resolve().parent;paths=json.loads((raw/'paths.json').read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((raw/'repository_before.json').read_text())
current={str(p.relative_to(root)):digest(p) for p in sorted(root.rglob('*')) if p.is_file() and p.parts[len(root.parts)] not in ['build','results','.git'] and '__pycache__' not in p.parts}
modified=sorted(name for name,value in before.items() if current.get(name)!=value);added=sorted(set(current)-set(before))
assert set(modified)=={'CMakeLists.txt','README.md','docs/ALGORITHMS.md','docs/AUDIT.md','docs/BENCHMARKING.md','docs/EXPERIMENT_PROTOCOL.md','docs/METRICS.md','docs/ROADMAP.md'} and len(added)==14
for name,value in json.loads((raw/'prior_results_sha256.json').read_text()).items():assert digest(root/name)==value,name
for name,value in json.loads((raw/'smoke_before_analysis_sha256.json').read_text()).items():assert digest(raw/name)==value,name
assert digest(root/'docs/SEARCH_PROTOCOL_v1.md')==json.loads((raw/'protocol_before_implementation.json').read_text())['sha256']
report=json.loads((raw/'verification.json').read_text());assert digest(Path(paths['processed']))==report['summary_sha256']
for build,config in [('release','Release'),('sanitize','Debug')]:
    for item in json.loads((root/'build'/build/'generated'/config/'source_hashes.json').read_text())['files']:assert digest(root/item['path'])==item['sha256']
links=[]
for name in modified+added:
    if not name.endswith('.md'):continue
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',(root/name).read_text()):
        if target.startswith('http') or ('search' not in target.lower() and 'SEARCH_PROTOCOL' not in target):continue
        assert ((root/name).parent/target).exists(),(name,target)
        links.append({'file':name,'target':target})
patch=''
for name in modified:
    patch+=''.join(difflib.unified_diff((Path(paths['backup'])/name).read_text().splitlines(keepends=True),(root/name).read_text().splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
for name in added:patch+=''.join(difflib.unified_diff([],(root/name).read_text().splitlines(keepends=True),fromfile='/dev/null',tofile='b/'+name))
with (raw/'changes.patch').open('x') as f:f.write(patch)
result={'modified_files':modified,'added_files':added,'current_project_sha256':current,'existing_sorting_algorithms_generator_tests_tools_and_vendors_preserved':True,'prior_results_and_frozen_sorting_study_preserved':True,'summary_regenerated_and_unchanged':True,'documentation_links_checked':links,'milestone_complete':'Phase 3 array search and batch infrastructure; individual-query timing and large search experiments deferred'}
with (raw/'final_review.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print('Final review passed; changed files:',modified,'added:',added)
