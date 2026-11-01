"""Additive Phase051 depth pass. Representative first; -CR051Expand after render review.
All old actors/classes/transforms/collision remain exact baseline; no generator reruns.
"""
import unreal,json,ast
from pathlib import Path
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05-1';exports=out/'exports';root='/Game/Generated/Phase051';owner='CinderRelay.Phase051.v1';tag='CR_Phase051_Generated'
assets=unreal.EditorAssetLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools();lib=unreal.MaterialEditingLibrary;levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
manifest=json.loads((exports/'depth-manifest.json').read_text());baseline=json.loads((out/'editor-baseline.json').read_text())['actors']
def owned(path):
 a=assets.load_asset(path) if assets.does_asset_exist(path) else None
 if a:assert assets.get_metadata_tag(a,'CR.GeneratedBy')==owner,path
 return a
def save(a):assets.set_metadata_tag(a,'CR.GeneratedBy',owner);assert assets.save_loaded_asset(a);return a
materials={};master=assets.load_asset('/Game/Generated/Phase05/Materials/M_CR05_Surface');assert master
for n,color in manifest['palette'].items():
 path=root+'/Materials/MI_CR051_Depth'+n;m=owned(path)
 if not m:m=tools.create_asset('MI_CR051_Depth'+n,root+'/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew());lib.set_material_instance_parent(m,master)
 lib.set_material_instance_vector_parameter_value(m,'SurfaceColor',unreal.LinearColor(*color,1));lib.set_material_instance_vector_parameter_value(m,'ShadowColor',unreal.LinearColor(*(v*.8 for v in color),1));lib.set_material_instance_scalar_parameter_value(m,'Metallic',.5 if n in('Steel','Rust') else 0);lib.set_material_instance_scalar_parameter_value(m,'Roughness',.68 if n!='Glass' else .4);lib.update_material_instance(m);save(m);materials['CR051_Depth'+n]=m
meshes={}
for s in manifest['meshes']:
 name=s['name'];m=owned(root+'/Meshes/'+name)
 if not m or ('-cr051reimportdepth' in unreal.SystemLibrary.get_command_line().lower() and name in ('SM_CR051_VaultRoof','SM_CR051_SawtoothClerestory','SM_CR051_DistantDistrict')):
  ui=unreal.FbxImportUI();ui.automated_import_should_detect_type=False;ui.import_as_skeletal=False;ui.import_animations=False;ui.import_materials=False;ui.import_textures=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
  d=ui.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True
  task=unreal.AssetImportTask();task.filename=str(exports/(name+'.fbx'));task.destination_path=root+'/Meshes';task.destination_name=name;task.options=ui;task.automated=True;task.replace_existing=True;task.save=True;tools.import_asset_tasks([task]);m=assets.load_asset(root+'/Meshes/'+name);assert m,name
  slots=list(m.get_editor_property('static_materials'))
  for slot in slots:slot.set_editor_property('material_interface',materials[str(slot.get_editor_property('imported_material_slot_name'))])
  m.set_editor_property('static_materials',slots);save(m)
 b=m.get_bounds();assert all(abs(a-v)<max(1,v*.01) for a,v in zip([2*b.box_extent.x,2*b.box_extent.y,2*b.box_extent.z],s['dimensions_cm'])),name
 meshes[name.removeprefix('SM_CR051_')]=m
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent');existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
scope={'unreal':unreal};tree=ast.parse((p/'Scripts/migrate_streaming.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('vector','transform','snapshot')],type_ignores=[]),'snapshot','exec'),scope)
def verify_old():
 for n,record in baseline.items():
  assert n in existing,n
  expected={k:v for k,v in record.items() if k not in('level','hidden')};assert scope['snapshot'](existing[n])==expected,n
  assert existing[n].get_level().get_outer().get_name()==record['level'],n
verify_old()
def prop(label,key,zone,loc,yaw=0,scale=(1,1,1),shadow=True):
 a=existing.get(label)
 if a:assert tag in [str(t) for t in a.tags],label
 else:
  assert levels.set_current_level_by_name('L_CH01_'+zone);a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*loc));a.set_actor_label(label);a.tags=[tag];existing[label]=a
 a.modify();a.set_actor_location(unreal.Vector(*loc),False,False);a.set_actor_rotation(unreal.Rotator(yaw=yaw),False);a.set_actor_scale3d(unreal.Vector(*scale));c=a.static_mesh_component;c.set_static_mesh(meshes[key]);c.set_collision_profile_name('NoCollision');c.set_editor_property('can_ever_affect_navigation',False);c.set_cast_shadow(shadow)
 return a
prop('CR051_WarehouseVault','VaultRoof','RailYard',(750,-1000,635))
prop('CR051_WorkshopClerestory','SawtoothClerestory','Workshop',(1640,0,510))
prop('CR051_DistantDistrict','DistantDistrict','Persistent',(0,0,0),shadow=False)
prop('CR051_MidHall','IndustrialHall','RailYard',(7000,3500,0),yaw=10,shadow=False)
prop('CR051_MainChimney','Chimney','RailYard',(6200,-2900,0),shadow=False)
prop('CR051_WaterTower','WaterTower','RailYard',(3200,2400,0),shadow=False)
if '-cr051expand' in unreal.SystemLibrary.get_command_line().lower():
 for side in(-1,1):
  for i,x in enumerate((-1700,-1100,-500,100,700,1300)):
   prop('CR051_Perimeter'+str(side)+'_'+str(i),'BrokenPerimeter','RailYard',(x,side*1440,0),yaw=180 if side==1 else 0,scale=(1,1,(.88,1.12,.94,1.04,.82,1.15)[i]))
 prop('CR051_WestPerimeter','BrokenPerimeter','RailYard',(-2030,900,0),yaw=90,scale=(1.7,1,1.15))
 prop('CR051_SiloPair','SiloPair','RailYard',(1600,-2350,0),yaw=18,shadow=False)
 prop('CR051_SecondHall','IndustrialHall','RailYard',(-5000,-5500,0),yaw=-30,scale=(1.2,1,1.1),shadow=False)
 prop('CR051_SecondChimney','Chimney','RailYard',(6500,-3700,0),scale=(.8,.8,.72),shadow=False)
verify_old();assert levels.save_all_dirty_levels();assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent');existing={a.get_actor_label():a for a in actors.get_all_level_actors()};verify_old()
added={}
for n,a in existing.items():
 if tag not in [str(t) for t in a.tags]:continue
 c=a.static_mesh_component;assert str(c.get_collision_profile_name())=='NoCollision' and not c.get_editor_property('can_ever_affect_navigation'),n
 added[n]={'level':a.get_level().get_outer().get_name(),'mesh':c.static_mesh.get_path_name(),'transform':scope['transform'](a.get_actor_transform())}
(out/'depth-placement.json').write_text(json.dumps({'original_actor_count':len(baseline),'preserved':True,'added':added,'expanded':'-cr051expand' in unreal.SystemLibrary.get_command_line().lower()},indent=2));unreal.log('CR051_DEPTH_PLACEMENT_PASS '+str(len(added)));unreal.SystemLibrary.quit_editor()
