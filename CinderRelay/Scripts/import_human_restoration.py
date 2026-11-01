"""Owned Phase053 native workbench derivative; activation is an explicit flag."""
import json
from pathlib import Path
import unreal
project=Path(unreal.Paths.project_dir());out=project.parent/'.environment-local/phase-05-3'
assets=unreal.EditorAssetLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools()
root='/Game/Generated/Phase053/Assembly';owner='CinderRelay.Phase053.Restoration.v1'
def owned(path):
    a=assets.load_asset(path) if assets.does_asset_exist(path) else None
    if a:assert assets.get_metadata_tag(a,'CR.GeneratedBy')==owner,path
    return a
def save(a):assets.set_metadata_tag(a,'CR.GeneratedBy',owner);assert assets.save_loaded_asset(a);return a
mesh=owned(root+'/Animation/SK_CR053_Restoration')
if not mesh:
    owned(root+'/Animation/SK_CR053_Restoration_Skeleton');owned(root+'/Animation/SK_CR053_Restoration_Anim')
    ui=unreal.FbxImportUI();ui.automated_import_should_detect_type=False;ui.import_mesh=True;ui.import_as_skeletal=True;ui.import_animations=True;ui.import_materials=False;ui.import_textures=False;ui.create_physics_asset=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH
    ui.anim_sequence_import_data.set_editor_property('use_default_sample_rate',True)
    t=unreal.AssetImportTask();t.filename=str(out/'handling-exports/SK_CR053_Restoration.fbx');t.destination_path=root+'/Animation';t.destination_name='SK_CR053_Restoration';t.options=ui;t.automated=True;t.save=True;tools.import_asset_tasks([t])
    assert t.imported_object_paths
    for p in t.imported_object_paths:save(assets.load_asset(p))
    mesh=assets.load_asset(root+'/Animation/SK_CR053_Restoration')
if '-cr053reimportassemblymesh' in unreal.SystemLibrary.get_command_line().lower():
    manager=unreal.InterchangeManager.get_interchange_manager_scripted();params=unreal.ImportAssetParameters()
    params.is_automated=True;params.replace_existing=True;params.follow_redirectors=True
    assert manager.reimport_asset(mesh,params) is not False
slots=list(mesh.get_editor_property('materials'))
for s in slots:
    name=str(s.get_editor_property('imported_material_slot_name'))
    if name.startswith('CR051_'):path='/Game/Generated/Phase051/Materials/M_CR051_'+name.removeprefix('CR051_')
    else:
        kind=next(n for n in ('Skin','Glove','Sleeve') if n.lower() in name.lower());path='/Game/Generated/Phase053/Gameplay/Materials/M_CR053_FP_'+kind
    mat=assets.load_asset(path);assert mat,path;s.set_editor_property('material_interface',mat)
mesh.set_editor_property('materials',slots);save(mesh)
anim=owned(root+'/Animation/AN_CR053_RookRestoration')
if not anim:
    raw=owned(root+'/Animation/SK_CR053_Restoration_Anim');assert isinstance(raw,unreal.AnimSequence) and abs(raw.sequence_length-22)<.02
    assert assets.rename_asset(raw.get_path_name(),root+'/Animation/AN_CR053_RookRestoration');anim=save(assets.load_asset(root+'/Animation/AN_CR053_RookRestoration'))
assert abs(anim.sequence_length-22)<.02
if '-cr053reimportassembly' in unreal.SystemLibrary.get_command_line().lower():
    manager=unreal.InterchangeManager.get_interchange_manager_scripted();params=unreal.ImportAssetParameters()
    params.is_automated=True;params.replace_existing=True;params.follow_redirectors=True
    assert manager.reimport_asset(anim,params) is not False
    save(anim)
seq=owned(root+'/Sequences/LS_CR053_RookRestoration')
if not seq:
    seq=assets.duplicate_asset('/Game/Generated/Phase052/Sequences/LS_CR052_RookRestoration',root+'/Sequences/LS_CR053_RookRestoration');assert seq
    for binding in seq.get_bindings():
        for track in binding.get_tracks():
            if isinstance(track,unreal.MovieSceneSkeletalAnimationTrack):
                for section in track.get_sections():
                    params=section.get_editor_property('params');params.animation=anim;section.set_editor_property('params',params)
            if isinstance(track,unreal.MovieScene3DTransformTrack):
                for section in track.get_sections():
                    channels=section.get_all_channels()
                    for key in channels[4].get_keys():key.set_value(key.get_value()-12.0)
    save(seq)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
bench=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.CRWorkbench))
bench.hands.set_skeletal_mesh_asset(mesh);bench.hands.set_editor_property('override_materials',[])
bones=[str(bench.hands.get_bone_name(i)) for i in range(bench.hands.get_num_bones())]
assert all(n in bones for n in ('hand_R','hand_L','weapon','optic','wrist_R','wrist_L')),bones
active='-cr053activateassembly' in unreal.SystemLibrary.get_command_line().lower()
if active:
    bench.modify();bench.set_editor_property('assembly_mesh',mesh);bench.set_editor_property('sequence',seq);assert levels.save_all_dirty_levels()
(out/'human-restoration-import.json').write_text(json.dumps({'mesh':mesh.get_path_name(),'animation':anim.get_path_name(),'sequence':seq.get_path_name(),'seconds':anim.sequence_length,'bones':bones,'activated':active},indent=2))
unreal.log('CR053_HUMAN_RESTORATION_IMPORT_PASS active='+str(active))
if not globals().get('CR053_KEEP_EDITOR_OPEN',False):unreal.SystemLibrary.quit_editor()
