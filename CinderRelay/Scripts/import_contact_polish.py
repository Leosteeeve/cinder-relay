"""Import Phase052 contact derivative and native camera/audio presentation tracks.
Explicit activation switches only the existing bench's soft appearance references.
"""
import json
from pathlib import Path
import unreal
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05-2'
root='/Game/Generated/Phase052';owner='CinderRelay.Phase052.v1'
assets=unreal.EditorAssetLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools()
def owned(path):
    a=assets.load_asset(path) if assets.does_asset_exist(path) else None
    if a:assert assets.get_metadata_tag(a,'CR.GeneratedBy')==owner,path
    return a
def save(a):assets.set_metadata_tag(a,'CR.GeneratedBy',owner);assert assets.save_loaded_asset(a);return a
mesh=owned(root+'/Animation/SK_CR052_Restoration')
if not mesh:
    ui=unreal.FbxImportUI();ui.automated_import_should_detect_type=False;ui.import_mesh=True;ui.import_as_skeletal=True;ui.import_animations=True;ui.import_materials=False;ui.import_textures=False;ui.create_physics_asset=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH
    d=ui.skeletal_mesh_import_data;d.convert_scene=True;d.convert_scene_unit=True;d.force_front_x_axis=False;ui.anim_sequence_import_data.set_editor_property('use_default_sample_rate',True)
    t=unreal.AssetImportTask();t.filename=str(out/'exports/SK_CR052_Restoration.fbx');t.destination_path=root+'/Animation';t.destination_name='SK_CR052_Restoration';t.options=ui;t.automated=True;t.save=True
    tools.import_asset_tasks([t]);assert t.imported_object_paths
    for path in t.imported_object_paths:save(assets.load_asset(path))
    mesh=assets.load_asset(root+'/Animation/SK_CR052_Restoration');assert mesh
if '-cr052reimportanimation' in unreal.SystemLibrary.get_command_line().lower():
    manager=unreal.InterchangeManager.get_interchange_manager_scripted();params=unreal.ImportAssetParameters();params.is_automated=True;params.replace_existing=True;params.follow_redirectors=True
    for a in [assets.load_asset(x) for x in assets.list_assets(root+'/Animation') if isinstance(assets.load_asset(x),(unreal.SkeletalMesh,unreal.AnimSequence))]:
        assert manager.reimport_asset(a,params) is not False;save(a)
slots=list(mesh.get_editor_property('materials'))
for s in slots:
    key=str(s.get_editor_property('imported_material_slot_name')).removeprefix('CR051_')
    path='/Game/Generated/Phase051/Materials/'+('MI_CR051_' if key in('Glove','Sleeve','Seam') else 'M_CR051_')+key
    m=assets.load_asset(path);assert m,path;s.set_editor_property('material_interface',m)
mesh.set_editor_property('materials',slots);save(mesh)
anim=owned(root+'/Animation/AN_CR052_RookRestoration')
if not anim:
    candidates=[assets.load_asset(x) for x in assets.list_assets(root+'/Animation') if isinstance(assets.load_asset(x),unreal.AnimSequence)]
    assert len(candidates)==1;assert assets.rename_asset(candidates[0].get_path_name(),root+'/Animation/AN_CR052_RookRestoration');anim=save(assets.load_asset(root+'/Animation/AN_CR052_RookRestoration'))
assert abs(anim.sequence_length-22)<.05
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
bench=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.CRWorkbench))
seq=owned(root+'/Sequences/LS_CR052_RookRestoration')
if not seq:
    seq=assets.duplicate_asset('/Game/Generated/Phase051/Sequences/LS_CR051_RookRestoration',root+'/Sequences/LS_CR052_RookRestoration');assert seq
    for b in seq.get_bindings():
        for t in b.get_tracks():
            if isinstance(t,unreal.MovieSceneSkeletalAnimationTrack):
                for s in t.get_sections():params=s.get_editor_property('params');params.animation=anim;s.set_editor_property('params',params)
    # Native child binding resolves from the existing tagged bench at runtime.
    parent=next(b for b in seq.get_bindings() if any(isinstance(t,unreal.MovieSceneSkeletalAnimationTrack) for t in b.get_tracks()))
    child=seq.add_possessable(bench.camera);child.set_parent(parent)
    tr=child.add_track(unreal.MovieScene3DTransformTrack);section=tr.add_section();section.set_range(0,660);section.set_completion_mode(unreal.MovieSceneCompletionMode.RESTORE_STATE)
    channels=section.get_all_channels()
    # Small head settle and final reveal; no camera cuts or uncontrolled shake.
    poses=[(0,(-62,0,166),(0,-48,0)),(36,(-66,0,172),(0,-46,0)),(108,(-67,0,172),(0,-46,0)),
           (228,(-65,-.6,173),(0,-47,0)),(345,(-64,0,171),(0,-47.5,0)),(450,(-66,0,172),(0,-46,0)),
           (573,(-68,0,174),(0,-44,0)),(624,(-67,0,173),(0,-44.5,0)),(660,(-62,0,166),(0,-48,0))]
    for frame,pos,rot in poses:
        for i,v in enumerate((*pos,*rot,1,1,1)):channels[i].add_key(unreal.FrameNumber(frame),v,interpolation=unreal.MovieSceneKeyInterpolation.AUTO)
    save(seq)
if assets.get_metadata_tag(seq,'CR052.ContactAudio')!='1':
    parent=next(b for b in seq.get_bindings() if any(isinstance(t,unreal.MovieSceneSkeletalAnimationTrack) for t in b.get_tracks()))
    for name,start,duration in [('Seat',347,8),('Secure',400,12)]:
        path=root+'/Audio/S_CR052_'+name;sound=owned(path)
        if not sound:
            t=unreal.AssetImportTask();t.filename=str(p/'ArtSource/Audio/Phase052'/('S_CR052_'+name+'.wav'));t.destination_path=root+'/Audio';t.destination_name='S_CR052_'+name;t.automated=True;t.save=True;tools.import_asset_tasks([t]);sound=assets.load_asset(path);assert sound;save(sound)
        track=parent.add_track(unreal.MovieSceneAudioTrack);s=track.add_section();s.set_range(start,start+duration);s.set_sound(sound);s.set_completion_mode(unreal.MovieSceneCompletionMode.RESTORE_STATE)
    assets.set_metadata_tag(seq,'CR052.ContactAudio','1');save(seq)
# UE 5.8 audio caches completion intent in PostEditChangeProperty(EvalOptions).
# set_completion_mode alone updates the live value but not that serialized cache.
for binding in seq.get_bindings():
    for track in binding.get_tracks():
        if isinstance(track,unreal.MovieSceneAudioTrack):
            for section in track.get_sections():
                options=section.get_editor_property('eval_options')
                options.set_editor_property('completion_mode',unreal.MovieSceneCompletionMode.RESTORE_STATE)
                section.set_editor_property('eval_options',options)
save(seq)
bench.hands.set_skeletal_mesh_asset(mesh);bench.hands.set_editor_property('override_materials',[])
bones=[str(bench.hands.get_bone_name(i)) for i in range(bench.hands.get_num_bones())]
assert len(bones)==40 and all(x in bones for x in('weapon','optic','hand_L','hand_R'))
activated='-cr052activate' in unreal.SystemLibrary.get_command_line().lower()
if activated:
    bench.modify();bench.set_editor_property('assembly_mesh',mesh);bench.set_editor_property('sequence',seq);assert levels.save_all_dirty_levels()
(out/'contact-import.json').write_text(json.dumps({'mesh':mesh.get_path_name(),'animation':anim.get_path_name(),'sequence':seq.get_path_name(),'duration':anim.sequence_length,'bones':bones,'activated':activated,'camera_tracks':'Native component transform with RestoreState'},indent=2))
unreal.log('CR052_CONTACT_IMPORT_PASS active='+str(activated));unreal.SystemLibrary.quit_editor()
