"""Read-only saved-map/collision/ownership audit against the Phase04 baseline."""
import ast,json,hashlib
from collections import Counter
from pathlib import Path
import unreal
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05';assets=unreal.EditorAssetLibrary
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
all_actors=list(actors.get_all_level_actors());now={a.get_actor_label():a for a in all_actors};assert len(now)==len(all_actors),'Duplicate actor labels'
baseline=json.loads((out/'editor-baseline.json').read_text())['actors'];scope={'unreal':unreal};tree=ast.parse((p/'Scripts/migrate_streaming.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('vector','transform','snapshot')],type_ignores=[]),'snapshot','exec'),scope)
def shape(r):
 r=json.loads(json.dumps(r));r.pop('hidden',None);r.pop('level',None);r.pop('checkpoint_id',None)
 r['components']=[c for c in r['components'] if c['name']!='PresentationMesh']
 for c in r['components']:
  for k in ('materials','intensity','color'):c.pop(k,None)
  # Only the previously unused visual skeletal component gets a feet-origin offset/no-collision.
  if r['label'] in ('CR02_Scout_1','CR02_Scout_2') and c['cls']=='/Script/Engine.SkeletalMeshComponent':
   for k in ('transform','enabled','profile'):c.pop(k,None)
 if r['label']=='CR_Sun':r.pop('transform',None);[c.pop('transform',None) for c in r['components']]
 return r
differences=[n for n,r in baseline.items() if n not in now or shape(scope['snapshot'](now[n]))!=shape(r)]
assert not differences,'Unexpected original gameplay structure change '+str(differences)
for n,r in baseline.items():
 assert now[n].get_level().get_outer().get_name()==r['level'],n
 if 'checkpoint_id' in r:assert str(now[n].checkpoint_id)==r['checkpoint_id']
added=[a for n,a in now.items() if n not in baseline]
collision_errors=[]
for a in added:
 assert 'CR_Phase05_Generated' in [str(t) for t in a.tags]
 if isinstance(a,unreal.StaticMeshActor):
  c=a.static_mesh_component
  if c.get_collision_enabled()!=unreal.CollisionEnabled.NO_COLLISION or c.get_editor_property('can_ever_affect_navigation'):collision_errors.append({'actor':a.get_actor_label(),'enabled':str(c.get_collision_enabled()),'profile':str(c.get_collision_profile_name()),'nav':c.get_editor_property('can_ever_affect_navigation')})
 if a.get_level().get_outer().get_name()=='L_CH01_Persistent':assert a.get_actor_label()=='CR05_AtmosphericHaze'
assert not collision_errors,'Decorative collision/nav mismatch '+json.dumps(collision_errors)
hashes=json.loads((out/'baseline-hashes.json').read_text())
protected=[k for k in hashes if '/Phase01A/Maps/' in k or '/ArtSource/Blender/Phase03/' in k or k.endswith('CRChapterSaveGame.cpp') or k.endswith('CRChapterSaveGame.h')]
assert all(hashlib.sha256((p.parent/k).read_bytes()).hexdigest()==hashes[k] for k in protected),'Protected rollback/source/schema changed'
receipt={'original_actors':len(baseline),'cosmetic_actors':len(added),'ownership':dict(Counter(a.get_level().get_outer().get_name() for a in added)),'original_structure_differences':differences,'protected_hashes_verified':protected,'checkpoint_anchors':{n:scope['snapshot'](a)['transform'] for n,a in now.items() if isinstance(a,unreal.CRCheckpoint)},'runtime_streaming_test':False}
(out/'asset-validation.json').write_text(json.dumps(receipt,indent=2));unreal.log('CR05_ASSET_VALIDATION_PASS '+json.dumps(receipt));unreal.SystemLibrary.quit_editor()
