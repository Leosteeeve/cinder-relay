"""Import new owned IK-baked skeletal content. Activate only after rendered review."""
import unreal,json
from pathlib import Path
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05-1';root='/Game/Generated/Phase051';owner='CinderRelay.Phase051.v1'
assets=unreal.EditorAssetLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools();lib=unreal.MaterialEditingLibrary
def owned(path):
 a=assets.load_asset(path) if assets.does_asset_exist(path) else None
 if a:assert assets.get_metadata_tag(a,'CR.GeneratedBy')==owner,path
 return a
def save(a):assets.set_metadata_tag(a,'CR.GeneratedBy',owner);assert assets.save_loaded_asset(a);return a
materials={}
for n in('Wood','Steel','Brass','Rubber','Lens','Reticle'):materials['CR051_'+n]=assets.load_asset(root+'/Materials/M_CR051_'+n)
master=assets.load_asset('/Game/Generated/Phase05/Materials/M_CR05_ActorSurface');assert master
for name,col in [('Glove',(.045,.035,.025)),('Sleeve',(.06,.08,.08)),('Seam',(.18,.14,.08))]:
 n='MI_CR051_'+name;m=owned(root+'/Materials/'+n) or tools.create_asset(n,root+'/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew());lib.set_material_instance_parent(m,master);lib.set_material_instance_vector_parameter_value(m,'SurfaceColor',unreal.LinearColor(*col,1));lib.set_material_instance_scalar_parameter_value(m,'Metallic',0);lib.set_material_instance_scalar_parameter_value(m,'Roughness',.82);lib.update_material_instance(m);save(m);materials['CR051_'+name]=m
mesh=owned(root+'/Animation/SK_CR051_Restoration')
if not mesh:
 ui=unreal.FbxImportUI();ui.automated_import_should_detect_type=False;ui.import_mesh=True;ui.import_as_skeletal=True;ui.import_animations=True;ui.import_materials=False;ui.import_textures=False;ui.create_physics_asset=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH
 data=ui.skeletal_mesh_import_data;data.convert_scene=True;data.convert_scene_unit=True;data.force_front_x_axis=False;ui.anim_sequence_import_data.set_editor_property('use_default_sample_rate',True)
 task=unreal.AssetImportTask();task.filename=str(out/'exports/SK_CR051_Restoration.fbx');task.destination_path=root+'/Animation';task.destination_name='SK_CR051_Restoration';task.options=ui;task.automated=True;task.save=True;tools.import_asset_tasks([task]);assert task.imported_object_paths
 for ap in task.imported_object_paths:save(assets.load_asset(ap))
 mesh=assets.load_asset(root+'/Animation/SK_CR051_Restoration');assert mesh
 slots=list(mesh.get_editor_property('materials'))
 for slot in slots:
  key=str(slot.get_editor_property('imported_material_slot_name'));assert key in materials,key;slot.set_editor_property('material_interface',materials[key])
 mesh.set_editor_property('materials',slots);save(mesh)
anim=owned(root+'/Animation/AN_CR051_RookRestoration')
if not anim:
 candidates=[assets.load_asset(a) for a in assets.list_assets(root+'/Animation') if isinstance(assets.load_asset(a),unreal.AnimSequence)]
 assert len(candidates)==1;assert assets.rename_asset(candidates[0].get_path_name(),root+'/Animation/AN_CR051_RookRestoration');anim=save(assets.load_asset(root+'/Animation/AN_CR051_RookRestoration'))
assert abs(anim.sequence_length-22)<.05
if '-cr051reimportanimation' in unreal.SystemLibrary.get_command_line().lower():
 manager=unreal.InterchangeManager.get_interchange_manager_scripted();params=unreal.ImportAssetParameters();params.is_automated=True;params.follow_redirectors=True;params.replace_existing=True
 for a in (mesh,anim):
  result=manager.reimport_asset(a,params);assert result is not None and result is not False;save(a)
 slots=list(mesh.get_editor_property('materials'))
 for slot in slots:
  key=str(slot.get_editor_property('imported_material_slot_name'));assert key in materials,key;slot.set_editor_property('material_interface',materials[key])
 mesh.set_editor_property('materials',slots);save(mesh)
seq=owned(root+'/Sequences/LS_CR051_RookRestoration')
if not seq:
 seq=assets.duplicate_asset('/Game/Generated/Phase05/Sequences/LS_CR05_RookRestoration',root+'/Sequences/LS_CR051_RookRestoration');assert seq
 for b in seq.get_bindings():
  for t in b.get_tracks():
   if isinstance(t,unreal.MovieSceneSkeletalAnimationTrack):
    for s in t.get_sections():params=s.get_editor_property('params');params.animation=anim;s.set_editor_property('params',params)
 save(seq)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
bench=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if isinstance(a,unreal.CRWorkbench))
before={'mesh':str(bench.get_editor_property('assembly_mesh')),'sequence':str(bench.get_editor_property('sequence'))}
activate='-cr051activate' in unreal.SystemLibrary.get_command_line().lower()
bench.hands.set_skeletal_mesh_asset(mesh)
bench.hands.set_editor_property('override_materials',[])
bones=[str(bench.hands.get_bone_name(i)) for i in range(bench.hands.get_num_bones())]
assert len(bones)==40 and all(n in bones for n in('root','weapon','optic','hand_L','hand_R','finger0_0_L','finger0_0_R')),bones
if activate:
 bench.modify();bench.set_editor_property('assembly_mesh',mesh);bench.set_editor_property('sequence',seq);assert levels.save_all_dirty_levels()
(out/'animation-import.json').write_text(json.dumps({'mesh':mesh.get_path_name(),'animation':anim.get_path_name(),'sequence':seq.get_path_name(),'seconds':anim.sequence_length,'bones':bones,'previous':before,'activated':activate},indent=2));unreal.log('CR051_ANIMATION_IMPORT_PASS active='+str(activate));unreal.SystemLibrary.quit_editor()
