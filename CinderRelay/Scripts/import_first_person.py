"""Import owned Phase053 handling assets through native UE FBX APIs.
No map or gameplay Blueprint activation. Existing generations are immutable here.
"""
import json
from pathlib import Path
import unreal
project=Path(unreal.Paths.project_dir());evidence=project.parent/'.environment-local/phase-05-3'
exports=evidence/'handling-exports';root='/Game/Generated/Phase053/Gameplay';owner='CinderRelay.Phase053.Handling.v1'
assets=unreal.EditorAssetLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools();lib=unreal.MaterialEditingLibrary
def owned(path):
    obj=assets.load_asset(path) if assets.does_asset_exist(path) else None
    if obj:assert assets.get_metadata_tag(obj,'CR.GeneratedBy')==owner,path
    return obj
def save(obj):
    assets.set_metadata_tag(obj,'CR.GeneratedBy',owner);assert assets.save_loaded_asset(obj);return obj
def task(filename,name,folder,options=None):
    t=unreal.AssetImportTask();t.filename=str(filename);t.destination_path=root+'/'+folder;t.destination_name=name
    t.automated=True;t.save=True
    if options:t.options=options
    tools.import_asset_tasks([t]);assert t.imported_object_paths,str(filename)
    for p in t.imported_object_paths:save(assets.load_asset(p))
    return t
textures={}
for suffix in ('BaseColor','Normal'):
    name='T_CR053_FP_'+suffix;t=owned(root+'/Textures/'+name)
    if not t:
        task(project/'ArtSource/Blender/Phase053/FirstPersonTextures'/(name+'.png'),name,'Textures')
        t=assets.load_asset(root+'/Textures/'+name);t.set_editor_property('srgb',suffix=='BaseColor')
        if suffix=='Normal':t.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP);t.set_editor_property('flip_green_channel',True)
        save(t)
    textures[suffix]=t
materials={}
for name,rough in [('Skin',.64),('Glove',.76),('Sleeve',.86)]:
    m=owned(root+'/Materials/M_CR053_FP_'+name)
    if not m:
        m=tools.create_asset('M_CR053_FP_'+name,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
        for suffix,prop in [('BaseColor',unreal.MaterialProperty.MP_BASE_COLOR),('Normal',unreal.MaterialProperty.MP_NORMAL)]:
            s=lib.create_material_expression(m,unreal.MaterialExpressionTextureSample);s.set_editor_property('texture',textures[suffix]);s.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if suffix=='Normal' else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
            lib.connect_material_property(s,'RGB',prop)
        c=lib.create_material_expression(m,unreal.MaterialExpressionConstant);c.set_editor_property('r',rough);lib.connect_material_property(c,'',unreal.MaterialProperty.MP_ROUGHNESS)
        lib.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH);lib.recompile_material(m);save(m)
    materials[name]=m
mesh=owned(root+'/Animation/SK_CR053_FirstPersonArms')
if not mesh:
    owned(root+'/Animation/SK_CR053_FirstPersonArms_Skeleton');owned(root+'/Animation/SK_CR053_FirstPersonArms_Anim')
    ui=unreal.FbxImportUI();ui.automated_import_should_detect_type=False;ui.import_mesh=True;ui.import_as_skeletal=True;ui.import_animations=True
    ui.import_materials=False;ui.import_textures=False;ui.create_physics_asset=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH
    ui.anim_sequence_import_data.set_editor_property('use_default_sample_rate',False);ui.anim_sequence_import_data.set_editor_property('custom_sample_rate',60)
    task(exports/'SK_CR053_FirstPersonArms.fbx','SK_CR053_FirstPersonArms','Animation',ui)
    mesh=assets.load_asset(root+'/Animation/SK_CR053_FirstPersonArms')
if '-cr053reimporthandlingmesh' in unreal.SystemLibrary.get_command_line().lower():
    manager=unreal.InterchangeManager.get_interchange_manager_scripted();params=unreal.ImportAssetParameters()
    params.is_automated=True;params.replace_existing=True;params.follow_redirectors=True
    assert manager.reimport_asset(mesh,params) is not False
slots=list(mesh.get_editor_property('materials'))
for slot in slots:
    key=str(slot.get_editor_property('imported_material_slot_name'));name=next(n for n in materials if n.lower() in key.lower());slot.set_editor_property('material_interface',materials[name])
mesh.set_editor_property('materials',slots);save(mesh)
skeleton=mesh.get_editor_property('skeleton')
# Register the native slot used by the small C++ graph and dynamic montages.
if hasattr(skeleton,'register_slot_node'):skeleton.register_slot_node('WeaponAction')
save(skeleton)
clips=[]
for name,seconds in [('Idle',4),('Walk',1),('Sprint',.8),('ADS',1),('FireCycle',.9),('Reload',2.4),('Dry',.25)]:
    path=root+'/Animation/AN_CR053_'+name;anim=owned(path)
    if not anim:
        if name=='Idle':
            raw=owned(root+'/Animation/SK_CR053_FirstPersonArms_Anim');assert isinstance(raw,unreal.AnimSequence) and abs(raw.sequence_length-seconds)<.02
            assert assets.rename_asset(raw.get_path_name(),path)
        else:
            ui=unreal.FbxImportUI();ui.automated_import_should_detect_type=False;ui.import_mesh=False;ui.import_as_skeletal=True;ui.import_animations=True;ui.import_materials=False;ui.import_textures=False
            ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;ui.skeleton=skeleton;ui.anim_sequence_import_data.set_editor_property('use_default_sample_rate',False);ui.anim_sequence_import_data.set_editor_property('custom_sample_rate',60)
            t=task(exports/('AN_CR053_'+name+'.fbx'),'AN_CR053_'+name,'Animation',ui)
            actual=next(assets.load_asset(p) for p in t.imported_object_paths if isinstance(assets.load_asset(p),unreal.AnimSequence))
            if actual.get_path_name().split('.')[0]!=path:assert assets.rename_asset(actual.get_path_name(),path)
        anim=save(assets.load_asset(path))
    if ('-cr053reimporthandling' in unreal.SystemLibrary.get_command_line().lower()
        or (name=='Reload' and '-cr053reimportreload' in unreal.SystemLibrary.get_command_line().lower())):
        manager=unreal.InterchangeManager.get_interchange_manager_scripted();params=unreal.ImportAssetParameters()
        params.is_automated=True;params.replace_existing=True;params.follow_redirectors=True
        assert manager.reimport_asset(anim,params) is not False
        save(anim)
    assert isinstance(anim,unreal.AnimSequence) and abs(anim.sequence_length-seconds)<.02,(name,str(anim))
    clips.append({'path':anim.get_path_name(),'seconds':anim.sequence_length})
    cues={'FireCycle':[('EjectCase',20/60)],'Reload':[('FeedOut',30/60),('FeedIn',111/60)]}.get(name,[])
    if cues and assets.get_metadata_tag(anim,'CR.CosmeticCues')!='1':
        notify_class=unreal.load_class(None,'/Script/CinderRelay.CRWeaponCueNotify');assert notify_class
        unreal.AnimationLibrary.add_animation_notify_track(anim,'CR053_Cosmetic',unreal.LinearColor(.2,.8,.8,1))
        for cue,seconds_at in cues:
            notify=unreal.AnimationLibrary.add_animation_notify_event(anim,'CR053_Cosmetic',seconds_at,notify_class)
            assert notify;notify.set_editor_property('cue',cue)
        assets.set_metadata_tag(anim,'CR.CosmeticCues','1');save(anim)
for name in ('Feed','CycleHandle','Case'):
    path=root+'/Meshes/SM_CR053_'+name;m=owned(path)
    if not m:
        ui=unreal.FbxImportUI();ui.automated_import_should_detect_type=False;ui.import_mesh=True;ui.import_as_skeletal=False;ui.import_materials=False;ui.import_textures=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
        ui.static_mesh_import_data.combine_meshes=True;ui.static_mesh_import_data.auto_generate_collision=False
        task(exports/('SM_CR053_'+name+'.fbx'),'SM_CR053_'+name,'Meshes',ui);m=assets.load_asset(path)
        for i,slot in enumerate(m.get_editor_property('static_materials')):
            key=str(slot.get_editor_property('imported_material_slot_name')).removeprefix('CR051_');mat=assets.load_asset('/Game/Generated/Phase051/Materials/M_CR051_'+key);assert mat,key;m.set_material(i,mat)
        save(m)
(evidence/'handling-import.json').write_text(json.dumps({'mesh':mesh.get_path_name(),'skeleton':skeleton.get_path_name(),'clips':clips,'runtime_activation':False},indent=2))
unreal.log('CR053_HANDLING_IMPORT_PASS')
if not globals().get('CR053_KEEP_EDITOR_OPEN',False):unreal.SystemLibrary.quit_editor()
