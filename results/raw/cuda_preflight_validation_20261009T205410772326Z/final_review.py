from pathlib import Path
import json,sys,hashlib,shutil,re
root=Path.cwd();p=json.loads((root/'build/phase7_paths.json').read_text());e=root/p['evidence'];h=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
before=json.loads((e/'source_before.json').read_text());after=json.loads((e/'source_after.json').read_text());changes=json.loads((e/'file_changes.json').read_text())
assert all(h(root/f)==s for f,s in after.items()) and len(after)==126
assert all(h(e/'reviewed_source'/f)==s for f,s in after.items())
assert len(changes['modified'])==4 and len(changes['added'])==6
protected={f:s for f,s in before.items() if f not in changes['modified']};assert len(protected)==116 and all(h(root/f)==s for f,s in protected.items())
for name in ['prior_artifacts_sha256.json','initial_preflight_sha256.json']:
 expected=json.loads((e/name).read_text());assert all(h(root/f)==s for f,s in expected.items())
protocol=json.loads((e/'protocol.json').read_text());assert h(root/protocol['path'])==protocol['sha256']==h(e/'PROTOCOL_v1.md')
preflight=root/p['preflight_reviewed'];report=json.loads((preflight/'report.json').read_text());marker=json.loads((preflight/'COMPLETE.json').read_text())
assert marker['discovery_complete'] and not marker['cuda_operational']
assert all(h(preflight/f)==s for f,s in marker['files_sha256'].items())
assert report['classification']['state']=='gpu_driver_unavailable' and report['classification']['gpu_detected']
assert not report['classification']['device0_kernel_verified']
assert all(h(root/f)==s for f,s in report['source_sha256'].items())
assert all(report['probes'][name]['status']=='skipped' for name in ['configure','build','runtime'])
assert report['discovery']['tools']['nvcc'] is None and report['discovery']['tools']['nvidia_smi'] is None
for name in ['local_preflight','reviewed_local_preflight']:assert json.loads((e/'commands'/(name+'.json')).read_text())['exit_code']==2
for kind in ['release','sanitize']:
 for action in ['configure','build','ctest']:
  record=json.loads((e/'commands'/('reviewed_'+kind+'_'+action+'.json')).read_text());assert record['exit_code']==0
  if action=='build':assert not re.search(r'warning:|error:',record['stdout']+record['stderr'],re.I)
  if action=='ctest':assert '100% tests passed, 0 tests failed out of 25' in record['stdout'] and 'Ran 22 tests' in record['stdout']
 shutil.copyfile(root/'build'/kind/'Testing/Temporary/LastTest.log',e/('final_'+kind+'_LastTest.log'))
for name in ['reviewed_preflight_unit_tests','cpu_environment','cpu_fallback_configure','cpu_fallback_build','cpu_fallback_registry','source_bundle']:assert json.loads((e/'commands'/(name+'.json')).read_text())['exit_code']==0
registry=json.loads((e/'commands/cpu_fallback_registry.json').read_text())['stdout'].splitlines();assert registry==['std_sort','quick_sort','pdq_sort','tim_sort','merge_sort','radix_sort']
for build in ['release','sanitize','cuda_cpu_fallback']:
 cache=(root/'build'/build/'CMakeCache.txt').read_text();assert 'MAB_ENABLE_CUDA:BOOL=OFF' in cache and 'CMAKE_CUDA_COMPILER:' not in cache
commands=json.loads((root/'build/release/compile_commands.json').read_text());assert not any(entry['file'].endswith('.cu') for entry in commands)
source=json.loads((root/'build/release/generated/Release/source_hashes.json').read_text());assert all(h(root/f['path'])==f['sha256'] for f in source['files'])
package=json.loads((e/'source_bundle_validation.json').read_text());assert package['byte_identical_repack'] and package['extracted_source_hashes_match'] and package['relocated_cuda_off_configure_exit']==0
assert h(root/package['archive'])==package['sha256']
block='## Phase 7 — CUDA readiness'+(root/'docs/AUDIT.md').read_text().split('## Phase 7 — CUDA readiness',1)[1]
assert (e/'FINAL_AUDIT.md').read_text().startswith(block.lstrip())
proof=dict(complete=True,scope='Phase7 CUDA preflight and cloud guide; original GPU sorting/timing remain pending',release_groups=25,sanitizer_groups=25,preflight_build_isolation_methods=22,leak_detection_enabled=True,
 local_preflight_exit=2,local_readiness=report['classification']['state'],gpu_pci_detected=True,gpu_model_evidence='lspci: GA107M GeForce RTX 3050 Ti Mobile',cuda_configure='not attempted: nvcc unavailable',cuda_probe_compile='not run',cuda_kernel_execution='not run',colab_execution='not run',
 prior_artifacts_unchanged=8447,original_project_files_unchanged=116,source_files=126,modified_files=4,added_files=6,source_archive_sha256=package['sha256'],archive_repack_byte_identical=True,archive_manifest_and_relocated_off_configure_verified=True,
 protocol_sha256=protocol['sha256'],source_manifest_sha256=h(e/'source_after.json'),patch_sha256=h(e/'changes.patch'),audit_sha256=h(e/'FINAL_AUDIT.md'))
with (e/'final_review.json').open('x') as stream:json.dump(proof,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps(proof,indent=2))
