"""Read-only final Phase051 ownership/collision/rollback and import contract audit."""
import unreal,json,ast,hashlib
from pathlib import Path
from collections import Counter
p=Path(unreal.Paths.project_dir()).resolve();out=p.parent/'.environment-local/phase-05-1';assets=unreal.EditorAssetLibrary
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
all_actors=list(actors.get_all_level_actors());now={a.get_actor_label():a for a in all_actors};assert len(now)==len(all_actors)
scope={'unreal':unreal};tree=ast.parse((p/'Scripts/migrate_streaming.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('vector','transform','snapshot')],type_ignores=[]),'snapshot','exec'),scope)
before=json.loads((out/'editor-baseline.json').read_text())['actors']
for n,r in before.items():
 assert n in now and now[n].get_level().get_outer().get_name()==r['level'],n
 assert scope['snapshot'](now[n])=={k:v for k,v in r.items() if k not in('level','hidden')},n
added=[a for n,a in now.items() if n not in before]
for a in added:
 assert 'CR_Phase051_Generated' in [str(t) for t in a.tags]
 c=a.static_mesh_component;assert c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION and not c.get_editor_property('can_ever_affect_navigation'),a.get_actor_label()
 if a.get_level().get_outer().get_name()=='L_CH01_Persistent':assert a.get_actor_label()=='CR051_DistantDistrict'
bench=now['CR03_CalibrationWorkbench'];assert '/Phase051/' in bench.get_editor_property('assembly_mesh').get_path_name();assert '/Phase051/' in bench.get_editor_property('sequence').get_path_name()
assert bench.hands.get_num_bones()==40
changed=[];protected=0
for item in json.loads((out/'baseline-hashes.json').read_text()):
 f=Path(item['Path']);same=f.exists() and hashlib.sha256(f.read_bytes()).hexdigest().upper()==item['SHA256'].upper()
 if not same:changed.append(str(f.relative_to(p.parent)))
 if 'Phase01A' in f.parts or ('ArtSource' in f.parts and f.suffix=='.blend'):
  assert same,str(f);protected+=1
bp=assets.load_asset('/Game/Generated/Phase02/Blueprints/BP_CRCombatCharacter');view=unreal.get_default_object(bp.generated_class()).weapon_view
for key,socket in [('rook_appearance','SightAnchor_Iron'),('survey_appearance','SightAnchor_Optic')]:
 m=view.get_editor_property(key);assert m and '/Phase051/' in m.get_path_name() and m.find_socket(socket)
textures={}
for path in assets.list_assets('/Game/Generated/Phase051/Textures'):
 t=assets.load_asset(path);textures[t.get_name()]={'width':t.blueprint_get_size_x(),'height':t.blueprint_get_size_y(),'compression':str(t.compression_settings),'srgb':t.srgb}
 assert textures[t.get_name()]['width']==2048
receipt={'original_actors_preserved':len(before),'added_actors':len(added),'ownership':dict(Counter(a.get_level().get_outer().get_name() for a in added)),'protected_hashes_verified':protected,'changed_existing_binary_files':changed,'textures':textures,'checkpoint_transforms':{n:scope['transform'](a.get_actor_transform()) for n,a in now.items() if isinstance(a,unreal.CRCheckpoint)},'native_runtime_streaming_acceptance':False}
(out/'asset-validation.json').write_text(json.dumps(receipt,indent=2));unreal.log('CR051_ASSET_VALIDATION_PASS '+str(len(added)));unreal.SystemLibrary.quit_editor()
