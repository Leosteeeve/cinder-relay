"""Phase054 owned decoration only. Native imports and map saves; old actors are immutable.
Run with UnrealEditor-Cmd -run=pythonscript -script=... after author_utility_kit.py.
"""
import ast,json
from pathlib import Path
import unreal
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05-4';exports=out/'exports'
root='/Game/Generated/Phase054';owner='CinderRelay.Phase054.v1';tag='CR_Phase054_Generated'
assets=unreal.EditorAssetLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
scope={'unreal':unreal};tree=ast.parse((p/'Scripts/migrate_streaming.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('vector','transform','snapshot')],type_ignores=[]),'snapshot','exec'),scope)
def snapshot(a):
    r=scope['snapshot'](a);r['level']=a.get_level().get_outer().get_name()
    if isinstance(a,unreal.CRCheckpoint):r['checkpoint_id']=str(a.checkpoint_id)
    return r
existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
baseline_path=out/'before-inventory.json'
if not baseline_path.exists():baseline_path.write_text(json.dumps({n:snapshot(a) for n,a in existing.items() if tag not in [str(t) for t in a.tags]},indent=2),encoding='utf-8')
baseline=json.loads(baseline_path.read_text(encoding='utf-8'))
def verify():
    for name,record in baseline.items():
        assert name in existing,name
        assert snapshot(existing[name])==record,'Original actor changed: '+name
verify()
manifest=json.loads((exports/'environment-manifest.json').read_text(encoding='utf-8'));meshes={};imports=[]
for spec in manifest['meshes']:
    name=spec['name'];path=root+'/Meshes/'+name
    m=assets.load_asset(path) if assets.does_asset_exist(path) else None
    if m:assert assets.get_metadata_tag(m,'CR.GeneratedBy')==owner,path
    else:
        ui=unreal.FbxImportUI();ui.automated_import_should_detect_type=False;ui.import_mesh=True;ui.import_as_skeletal=False;ui.import_animations=False;ui.import_materials=False;ui.import_textures=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
        d=ui.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True
        task=unreal.AssetImportTask();task.filename=str(exports/(name+'.fbx'));task.destination_path=root+'/Meshes';task.destination_name=name;task.options=ui;task.automated=True;task.save=True;task.replace_existing=False
        tools.import_asset_tasks([task]);m=assets.load_asset(path);assert m,name
        slots=list(m.get_editor_property('static_materials'))
        for slot in slots:
            key=str(slot.get_editor_property('imported_material_slot_name')).removeprefix('CR054_')
            material=assets.load_asset('/Game/Generated/Phase052/Materials/MI_CR052_'+key);assert material,key
            slot.set_editor_property('material_interface',material)
        m.set_editor_property('static_materials',slots);assets.set_metadata_tag(m,'CR.GeneratedBy',owner);assert assets.save_loaded_asset(m)
    bounds=m.get_bounds();dimensions=[2*bounds.box_extent.x,2*bounds.box_extent.y,2*bounds.box_extent.z]
    assert all(abs(a-b)<max(1,b*.01) for a,b in zip(dimensions,spec['dimensions_cm'])),(name,dimensions)
    meshes[name.removeprefix('SM_CR054_')]=m;imports.append({'asset':m.get_path_name(),'dimensions_cm':dimensions,'triangles':spec['triangles']})

def actor(name,cls,zone,loc,yaw=0):
    label='CR054_'+name;a=existing.get(label)
    if a:assert tag in [str(t) for t in a.tags] and isinstance(a,cls),label
    else:
        assert levels.set_current_level_by_name('L_CH01_'+zone)
        a=actors.spawn_actor_from_class(cls,unreal.Vector(*loc));a.set_actor_label(label);a.tags=[tag];existing[label]=a
    a.modify();a.set_actor_location(unreal.Vector(*loc),False,False);a.set_actor_rotation(unreal.Rotator(yaw=yaw),False);return a
def prop(name,key,zone,loc,yaw=0,scale=(1,1,1)):
    a=actor(name,unreal.StaticMeshActor,zone,loc,yaw);a.set_actor_scale3d(unreal.Vector(*scale));c=a.static_mesh_component
    m=meshes.get(key) or assets.load_asset(key);assert m,key
    c.set_static_mesh(m);c.set_collision_profile_name('NoCollision');c.set_editor_property('can_ever_affect_navigation',False);a.set_actor_enable_collision(False);return a

# Functional bays are behind the existing benches, never inside the camera/hand volume.
prop('CalibrationTools','ToolWall','Workshop',(2300,-675,125),0)
prop('PowerTools','ToolWall','Workshop',(2820,-675,125),0)
prop('RepairSupplies','ServiceShelf','Workshop',(3170,-635,0),0)
prop('EntryDistribution','ElectricalPanel','Workshop',(1740,440,130),-90)
prop('RelayAccessDistribution','ElectricalPanel','Workshop',(3530,-430,115),90)
prop('MotorService','ElectricalPanel','Workshop',(3100,675,190),180)
for i,x in enumerate((2010,2600,3190)):
    for side in(-300,300):prop('WorkshopOverhead'+str(i)+'_'+str(side),'OverheadServices','Workshop',(x,side,440))
prop('RepairCart','/Game/Generated/Phase052/Meshes/SM_CR052_MaintenanceTrolley','Workshop',(3010,-555,0),-8)
prop('ServiceSpool','/Game/Generated/Phase052/Meshes/SM_CR052_CableSpool','Workshop',(3390,535,0),20,scale=(.65,.65,.65))

# Supporting ramp and bunker use the same visual service language, with clear center paths.
for i,x in enumerate((3900,4500,5100)):
    z=400-(x-3600)/3
    a=prop('RampOverhead'+str(i),'OverheadServices','RelayBunker',(x,-30,z),scale=(.9,.7,.7))
    a.set_actor_rotation(unreal.Rotator(pitch=-18.435),False)
prop('BunkerDistribution','ElectricalPanel','RelayBunker',(6100,-630,-340),0)
prop('BunkerMaintenanceRack','ServiceShelf','RelayBunker',(5630,-575,-600),0)
for i,x in enumerate((5700,6300,6900)):prop('BunkerOverhead'+str(i),'OverheadServices','RelayBunker',(x,-330,-160))

# Rail-side clusters relate to real service uses and leave center/flank/cover positions intact.
prop('YardPneumatics','PneumaticSkid','RailYard',(-1080,-520,0),12)
prop('YardSupply','TracksideService','RailYard',(-1280,1100,0),165)
prop('EntrySupply','TracksideService','RailYard',(1120,-600,0),80)
prop('FlankPneumatics','PneumaticSkid','RailYard',(650,1120,0),-12)
prop('WarehouseRepairShelf','ServiceShelf','RailYard',(-350,-1150,0),180)
for i,x in enumerate((-1400,-700,0,700)):
    prop('RailMaintenanceSleeper'+str(i),'/Game/Generated/Phase052/Meshes/SM_CR052_ScrapStack','RailYard',(x,1180,0),12+i*9,scale=(.7,.7,.65))

grime=assets.load_asset('/Game/Generated/Phase052/Materials/M_CR052_ServiceGrime');assert grime
for i,(zone,loc,size,yaw) in enumerate([
    ('Workshop',(2300,-425,3),(150,80),7),('Workshop',(2810,-380,3),(130,80),-9),
    ('Workshop',(3120,420,3),(150,120),18),('Workshop',(2050,0,3),(230,90),0),
    ('RelayBunker',(5650,-520,-596),(160,90),4),('RailYard',(-1080,-520,4),(175,125),12),
    ('RailYard',(650,1120,4),(160,110),-12)]):
    a=actor('UseHistory'+str(i),unreal.DecalActor,zone,loc,yaw);a.set_actor_rotation(unreal.Rotator(pitch=-90,yaw=yaw),False)
    a.decal.set_decal_material(grime);a.decal.set_editor_property('decal_size',unreal.Vector(15,*size));a.decal.set_editor_property('fade_screen_size',.007)
for name,loc,color,power in [('ToolTask',(2500,-500,300),(1,.74,.48),210),('AccessService',(3350,-440,290),(.64,.77,.82),130)]:
    a=actor(name,unreal.PointLight,'Workshop',loc);c=a.light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity_units(unreal.LightUnits.LUMENS);c.set_intensity(power);c.set_light_color(unreal.LinearColor(*color));c.set_editor_property('attenuation_radius',420);c.set_editor_property('source_radius',25);c.set_editor_property('cast_shadows',False)

verify()
for zone in ['RailYard','Workshop','RelayBunker']:
    assert levels.set_current_level_by_name('L_CH01_'+zone);assert levels.save_current_level()
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
existing={a.get_actor_label():a for a in actors.get_all_level_actors()};verify()
added={}
for n,a in existing.items():
    if tag not in [str(t) for t in a.tags]:continue
    if isinstance(a,unreal.StaticMeshActor):
        c=a.static_mesh_component;assert str(c.get_collision_profile_name())=='NoCollision' and not c.get_editor_property('can_ever_affect_navigation'),n
    added[n]=snapshot(a)
(out/'environment-import.json').write_text(json.dumps({'original_actors_unchanged':len(baseline),'imports':imports,'added':added,'old_assets_replaced':False},indent=2),encoding='utf-8')
unreal.log('CR054_ENVIRONMENT_PASS originals='+str(len(baseline))+' added='+str(len(added)))
