"""Phase03 owned additions only. Run in the real Editor after the Blender export.
Existing Phase01/02 actors and rollback map are never regenerated or replaced.
Re-run updates only CR_Phase03_Generated actors and owned assets; imports are reused.
"""
import unreal,json,ast,math,wave,struct
from pathlib import Path
p=Path(unreal.Paths.project_dir()); out=p.parent/'.environment-local/phase-03'; exports=out/'exports'
root='/Game/Generated/Phase03'; owner='CinderRelay.Phase03.v1';tag='CR_Phase03_Generated'
tools=unreal.AssetToolsHelpers.get_asset_tools(); assets=unreal.EditorAssetLibrary
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); actors_api=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def mark(a):assets.set_metadata_tag(a,'CR.GeneratedBy',owner);assets.save_loaded_asset(a);return a
def owned(path):
    a=assets.load_asset(path) if assets.does_asset_exist(path) else None
    if a:assert assets.get_metadata_tag(a,'CR.GeneratedBy')==owner,'Refusing unowned asset '+path
    return a
def create(name,folder,cls,factory):
    return owned(root+'/'+folder+'/'+name) or mark(tools.create_asset(name,root+'/'+folder,cls,factory))
palette={'CR03_Graphite':((.065,.085,.095),.7,.32),'CR03_Amber':((.68,.29,.055),.5,.4),'CR03_Glove':((.15,.17,.16),0,.75),'CR03_Cuff':((.28,.31,.28),0,.83),'CR03_Lens':((.025,.65,.55),.35,.2),'CR03_Bench':((.14,.2,.22),.55,.65)}
materials={}
for name,(color,metal,rough) in palette.items():
    path=root+'/Materials/M_'+name;m=owned(path)
    if not m:
        m=create('M_'+name,'Materials',unreal.Material,unreal.MaterialFactoryNew())
        rgb=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-200,0);rgb.constant=unreal.LinearColor(*color,1)
        unreal.MaterialEditingLibrary.connect_material_property(rgb,'',unreal.MaterialProperty.MP_BASE_COLOR)
        for prop,val in [(unreal.MaterialProperty.MP_METALLIC,metal),(unreal.MaterialProperty.MP_ROUGHNESS,rough)]:
            node=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant);node.r=val;unreal.MaterialEditingLibrary.connect_material_property(node,'',prop)
        if name=='CR03_Lens':unreal.MaterialEditingLibrary.connect_material_property(rgb,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        unreal.MaterialEditingLibrary.recompile_material(m);mark(m)
    unreal.MaterialEditingLibrary.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
    mark(m);materials[name]=m
def import_fbx(name,skeletal=False):
    folder='Animation' if skeletal else 'Meshes';path=root+'/'+folder+'/'+name
    obj=owned(path)
    if obj:return obj
    ui=unreal.FbxImportUI();ui.set_editor_property('automated_import_should_detect_type',False)
    ui.import_mesh=True;ui.import_as_skeletal=skeletal;ui.import_animations=skeletal;ui.import_materials=False;ui.import_textures=False
    ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH if skeletal else unreal.FBXImportType.FBXIT_STATIC_MESH
    ui.create_physics_asset=False
    data=ui.skeletal_mesh_import_data if skeletal else ui.static_mesh_import_data
    data.convert_scene=True;data.convert_scene_unit=True;data.force_front_x_axis=False;data.import_uniform_scale=1
    if not skeletal:data.combine_meshes=True;data.auto_generate_collision=True
    else:
        ui.anim_sequence_import_data.set_editor_property('use_default_sample_rate',True)
    task=unreal.AssetImportTask();task.filename=str(exports/(name+'.fbx'));task.destination_path=root+'/'+folder;task.destination_name=name;task.automated=True;task.save=True;task.options=ui
    tools.import_asset_tasks([task]);assert task.imported_object_paths,'Import produced no objects '+name
    for ap in task.imported_object_paths:mark(assets.load_asset(ap))
    obj=assets.load_asset(path);assert obj
    slots=list(obj.get_editor_property('materials' if skeletal else 'static_materials'))
    for slot in slots:
        key=str(slot.get_editor_property('imported_material_slot_name'))
        assert key in materials,'Unexpected imported material '+key
        slot.set_editor_property('material_interface',materials[key])
    obj.set_editor_property('materials' if skeletal else 'static_materials',slots);mark(obj);return obj
rook=import_fbx('SM_CR03_Rook5');optic=import_fbx('SM_CR03_SurveyOptic');bench=import_fbx('SM_CR03_Workbench');rig=import_fbx('SK_CR03_Restoration',True)
# UE5.8 Interchange imported the legacy FBX UI but did not generate simple collision.
# Use the actual native Static Mesh Editor operation and verify its result explicitly.
mesh_editor=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for mesh in (optic,bench):
    if mesh_editor.get_simple_collision_count(mesh)==0:
        assert mesh_editor.add_simple_collisions(mesh,unreal.ScriptingCollisionShapeType.BOX)>=0
        mark(mesh)
    assert mesh_editor.get_simple_collision_count(mesh)>0
animations=list({assets.load_asset(x).get_path_name():assets.load_asset(x) for x in assets.list_assets(root+'/Animation',recursive=True) if isinstance(assets.load_asset(x),unreal.AnimSequence)}.values())
assert len(animations)==1;animation=animations[0]
if animation.get_name()!='AN_CR03_RookRestoration':
    assert assets.rename_asset(animation.get_path_name(),root+'/Animation/AN_CR03_RookRestoration');animation=assets.load_asset(root+'/Animation/AN_CR03_RookRestoration')
assert abs(animation.sequence_length-22)<.05
sound=owned(root+'/Audio/S_CR03_Calibration')
if not sound:
    audio=exports/'S_CR03_Calibration.wav';rate=24000
    with wave.open(str(audio),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
        w.writeframes(b''.join(struct.pack('<h',int(11000*math.sin(2*math.pi*(660 if i<rate*.18 else 880)*i/rate)*min(1,i/240)*math.exp(-i/rate*3))) for i in range(int(rate*.7))))
    task=unreal.AssetImportTask();task.filename=str(audio);task.destination_path=root+'/Audio';task.automated=True;task.save=True;tools.import_asset_tasks([task]);sound=mark(assets.load_asset(root+'/Audio/S_CR03_Calibration'))
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
existing={a.get_actor_label():a for a in actors_api.get_all_level_actors()}
tree=ast.parse((p/'Scripts/migrate_streaming.py').read_text(encoding='utf-8-sig'));scope={'unreal':unreal}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('vector','transform','snapshot')],type_ignores=[]),'snapshot','exec'),scope)
baseline=out/'editor-preflight.json'
if not baseline.exists():
    # Fresh checkout: take a read-only baseline before adding/moving any actors.
    baseline.write_text(json.dumps({'actors':{n:scope['snapshot'](a) for n,a in existing.items() if tag not in [str(t) for t in a.tags]}},indent=2))
before=json.loads(baseline.read_text())['actors']
def actor(label,cls,zone,location):
    a=existing.get(label)
    if a:assert tag in [str(t) for t in a.tags] and isinstance(a,cls),'Unowned actor '+label
    else:
        assert levels.set_current_level_by_name('L_CH01_'+zone)
        a=actors_api.spawn_actor_from_class(cls,unreal.Vector(*location));a.set_actor_label(label);a.tags=[tag,'CR_Zone_'+('A_RailYard' if zone=='RailYard' else 'B_Workshop')]
    # Native transform setters alone do not dirty an existing Editor map package.
    a.modify()
    return a
workbench=actor('CR03_CalibrationWorkbench',unreal.CRWorkbench,'Workshop',(2300,-350,0));workbench.surface.set_static_mesh(bench);workbench.hands.set_skeletal_mesh_asset(rig)
workbench.set_editor_property('assembly_mesh',rig);workbench.set_editor_property('activation_sound',sound)
sequence=create('LS_CR03_RookRestoration','Sequences',unreal.LevelSequence,unreal.LevelSequenceFactoryNew())
sequence.set_display_rate(unreal.FrameRate(30,1));sequence.set_playback_start(0);sequence.set_playback_end(660)
bindings=sequence.get_bindings()
if not bindings:
    binding=sequence.add_possessable(workbench);binding.set_name('Workshop restoration / runtime owner')
    unreal.MovieSceneBindingTagExtensions.tag_binding(binding,'CR03_Hands')
    track=binding.add_track(unreal.MovieSceneSkeletalAnimationTrack);section=track.add_section();section.set_range(0,660)
    params=section.get_editor_property('params');params.animation=animation;section.set_editor_property('params',params)
    section.set_completion_mode(unreal.MovieSceneCompletionMode.RESTORE_STATE)
else:assert len(bindings)==1
workbench.set_editor_property('sequence',sequence);mark(sequence)
for label,zone,location in [('CR03_YardCache','RailYard',(-1280,-450,65)),('CR03_WorkshopBackup','Workshop',(2310,-308,88))]:
    a=actor(label,unreal.CRSalvagePickup,zone,location);a.set_editor_property('source_id',label);a.mesh.set_static_mesh(optic);a.set_actor_rotation(unreal.Rotator(yaw=90),False)
crate=actor('CR03_YardCacheStand',unreal.StaticMeshActor,'RailYard',(-1280,-450,32));crate.static_mesh_component.set_static_mesh(assets.load_asset('/Engine/BasicShapes/Cube'));crate.set_actor_scale3d(unreal.Vector(.65,.65,.64));crate.static_mesh_component.set_material(0,materials['CR03_Bench'])
for label,zone,loc,text in [('CR03_BenchSign','Workshop',(2340,-350,171),'SURVEY OPTIC\nCALIBRATION BENCH'),('CR03_CacheSign','RailYard',(-1280,-450,115),'SALVAGE\nSURVEY OPTIC')]:
    a=actor(label,unreal.TextRenderActor,zone,loc);a.set_actor_rotation(unreal.Rotator(yaw=180),False)
    c=a.text_render;c.set_text(text);c.set_world_size(13);c.set_text_render_color(unreal.Color(255,180,70));c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
# All pre-existing named actors must still match their preflight snapshots before save.
now={a.get_actor_label():a for a in actors_api.get_all_level_actors()}
diff=[name for name,snap in before.items() if name not in now or scope['snapshot'](now[name])!=snap];assert not diff,'Existing actors changed '+str(diff)
assert levels.save_all_dirty_levels()
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
reloaded={a.get_actor_label():a for a in actors_api.get_all_level_actors()}
for label in ('CR03_YardCache','CR03_WorkshopBackup'):
    r=reloaded[label].get_actor_rotation();assert abs(r.yaw-90)<.01 and abs(r.pitch)<.01,'Saved rotation failed '+label
receipt={'preserved_actors':len(before),'added_actors':[n for n in now if n not in before],'animation':animation.get_path_name(),'duration':animation.sequence_length,'sequence':sequence.get_path_name(),'mesh_bounds':str(rook.get_bounds()),'skeletal_bounds':str(rig.get_bounds()),'assets':[str(x) for x in assets.list_assets(root,recursive=True)]}
(out/'asset-generation.json').write_text(json.dumps(receipt,indent=2));unreal.log('CR03_ASSETS_PASS '+json.dumps(receipt))
unreal.SystemLibrary.quit_editor()
