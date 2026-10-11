import hashlib,json,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parent/'upstream_v3_0_1';root.mkdir()
requests=[]
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'mab-correctness-review'}),timeout=60) as r:data=r.read();status=r.status
    requests.append({'url':url,'http_status':status,'sha256':hashlib.sha256(data).hexdigest()})
    return data
ref=json.loads(get('https://api.github.com/repos/NVIDIA/cccl/git/ref/tags/v3.0.1'))
obj=ref['object'];objects=[ref]
while obj['type']=='tag':
    item=json.loads(get(obj['url']));objects.append(item);obj=item['object']
assert obj['type']=='commit'
commit=obj['sha']
files={}
for name,path in [('cub_version.cuh','cub/cub/version.cuh'),('device_radix_sort.cuh','cub/cub/device/device_radix_sort.cuh'),('LICENSE','LICENSE')]:
    url='https://raw.githubusercontent.com/NVIDIA/cccl/'+commit+'/'+path
    data=get(url);(root/name).write_bytes(data)
    files[name]={'commit_url':url,'sha256':hashlib.sha256(data).hexdigest()}
result={'upstream':'https://github.com/NVIDIA/cccl','reference_release':'v3.0.1','commit':commit,'tag_resolution':objects,'files':files,'requests':requests}
(root/'review.json').write_text(json.dumps(result,indent=2)+'\n')
installed=json.loads((root.parent/'dependency_inspection.json').read_text())
assert files['cub_version.cuh']['sha256']==installed['files']['cub/version.cuh']['sha256']
assert files['device_radix_sort.cuh']['sha256']==installed['files']['cub/device/device_radix_sort.cuh']['sha256']
assert files['LICENSE']['sha256']==hashlib.sha256(Path('third_party/cub/LICENSE').read_bytes()).hexdigest()
print(json.dumps({'commit':commit,'files':files,'installed_matches':True,'license_unchanged':True},indent=2))
