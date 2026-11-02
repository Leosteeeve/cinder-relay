"""Bounded Phase06 import and placement. Never executes previous generators.
Only owns CR06-tagged additions and explicit door/HUD changes. CP anchors/IDs remain fixed.
"""
import unreal, json
from pathlib import Path
p=Path(unreal.Paths.project_dir()); out=p.parent/'.environment-local/phase-06'; exp=out/'exports'
assets=unreal.EditorAssetLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
root='/Game/Generated/Phase06';owner='CinderRelay.Phase06.v1';tag='CR_Phase06'
# Optional targeted migration registers GUIDs through native UWidgetBlueprint::OnVariableAdded.
apply_artwork='-cr06artwork' in unreal.SystemLibrary.get_command_line().lower()
if apply_artwork:
    hud=assets.load_asset('/Game/Generated/Phase055/Interface/Widgets/WBP_CR_HUDRoot')
meshes={};imports=[]
for item in json.loads((exp/'chapter-kit.json').read_text()):
    path=root+'/Meshes/'+item['name'];m=assets.load_asset(path) if assets.does_asset_exist(path) else None
    if m: assert assets.get_metadata_tag(m,'CR.GeneratedBy')==owner,path
    else:
        ui=unreal.FbxImportUI();ui.automated_import_should_detect_type=False;ui.import_mesh=True;ui.import_as_skeletal=False;ui.import_animations=False;ui.import_materials=False;ui.import_textures=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
        ui.static_mesh_import_data.combine_meshes=True;ui.static_mesh_import_data.auto_generate_collision=False;ui.static_mesh_import_data.convert_scene=True;ui.static_mesh_import_data.convert_scene_unit=True
        task=unreal.AssetImportTask();task.filename=str(exp/(item['name']+'.fbx'));task.destination_path=root+'/Meshes';task.destination_name=item['name'];task.options=ui;task.automated=True;task.save=False
        tools.import_asset_tasks([task]);m=assets.load_asset(path);assert m,path
        slots=list(m.get_editor_property('static_materials'))
        for slot in slots:
            key=str(slot.get_editor_property('imported_material_slot_name')).removeprefix('CR06_')
            mat=assets.load_asset('/Game/Generated/Phase052/Materials/MI_CR052_'+key);assert mat,key;slot.set_editor_property('material_interface',mat)
        m.set_editor_property('static_materials',slots);assets.set_metadata_tag(m,'CR.GeneratedBy',owner);assert assets.save_loaded_asset(m)
    b=m.get_bounds();dims=[2*b.box_extent.x,2*b.box_extent.y,2*b.box_extent.z]
    assert all(abs(a-b)<max(1,b*.01) for a,b in zip(dims,item['dimensions_cm'])),(path,dims)
    meshes[item['name'].removeprefix('SM_CR06_')]=m;imports.append(dict(asset=path,dimensions_cm=dims))

assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
def anchor_value(a):
    v=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
    return [round(x,5) for x in (v.x,v.y,v.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z)]
anchors={n:anchor_value(a) for n,a in existing.items() if isinstance(a,unreal.CRCheckpoint)}
assert len(anchors)==3
before=out/'audit/anchors-numeric-before.json'
expected={'CP00_START_YARD':[-1450,0,110], 'CP01_WORKSHOP_ENTRY':[2050,0,110], 'CP02_RELAY_ACCESS':[4050,0,-40.18861]}
assert all(all(abs(anchors[n][i]-v)<.0001 for i,v in enumerate(xyz)) for n,xyz in expected.items()),anchors
if not before.exists():before.write_text(json.dumps(anchors,indent=2))
assert anchors==json.loads(before.read_text()),'Checkpoint transforms changed'
def actor(name,cls,zone,loc,yaw=0):
    label='CR06_'+name;a=existing.get(label)
    if a:assert tag in [str(x) for x in a.tags] and isinstance(a,cls),label
    else:
        assert levels.set_current_level_by_name('L_CH01_'+zone)
        a=actors.spawn_actor_from_class(cls,unreal.Vector(*loc));a.set_actor_label(label);a.tags=[tag];existing[label]=a
    a.modify();a.set_actor_location(unreal.Vector(*loc),False,False);a.set_actor_rotation(unreal.Rotator(yaw=yaw),False);return a
def text(name,zone,loc,body,yaw=180,size=17):
    a=actor(name,unreal.TextRenderActor,zone,loc,yaw);c=a.text_render;c.set_text(body);c.set_world_size(size);c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER);c.set_text_render_color(unreal.Color(220,177,105,255));return a
def prop(name,zone,loc,mesh,scale=(1,1,1),yaw=0,collision=False):
    a=actor(name,unreal.StaticMeshActor,zone,loc,yaw);a.set_actor_scale3d(unreal.Vector(*scale));c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_collision_profile_name('BlockAll' if collision else 'NoCollision');c.set_editor_property('can_ever_affect_navigation',collision);return a

cube=assets.load_asset('/Engine/BasicShapes/Cube');steel=assets.load_asset('/Game/Generated/Phase052/Materials/MI_CR052_Steel')
for key in ('AB','BC'):
    g=existing['CR_Gate_'+key];g.modify();g.door.set_mobility(unreal.ComponentMobility.MOVABLE)
    g.door.set_static_mesh(meshes['RollerShutter' if key=='AB' else 'IsolationDoor']);g.door.set_relative_scale3d(unreal.Vector(1,1,1));g.door.set_collision_profile_name('NoCollision')
    for c in (g.control_outside,g.control_inside):c.set_static_mesh(cube);c.set_material(0,steel)
    prop('DoorFrame_'+key,'Persistent',(g.get_actor_location().x,0,0),meshes['DoorFrame'])
    x=g.get_actor_location().x
    for side in(-1,1):text('DoorControl_'+key+str(side),'Persistent',(x+side*62,-230,195),'E / OPEN - CLOSE',yaw=180 if side==-1 else 0,size=12)

for step,(x,y,yaw) in enumerate([(2110,450,-90),(3100,300,-90),(3160,-430,90)]):
    a=actor('Diagnostic'+str(step),unreal.CRMaintenanceStation,'Workshop',(x,y,130),yaw)
    a.set_editor_property('step',step);a.panel.set_static_mesh(meshes['DiagnosticPanel'])
    a.display.set_editor_property('relative_location',unreal.Vector(28,0,58))
    a.display.set_text(['01 / ROUTE\nBENCH SUPPLY\nREADY','02 / VERIFY\nTEST LOAD\nAWAIT PREVIOUS STEP','03 / RELEASE\nMODULE CRADLE\nAWAIT PREVIOUS STEP'][step])
    # Exact simple query collision for authored panel; imported mesh source remains cosmetic elsewhere.
    body=a.panel.static_mesh.get_editor_property('body_setup')
    body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    assets.save_loaded_asset(a.panel.static_mesh)
board=prop('DiagnosticNoticeBoard','Workshop',(2700,553,285),cube,scale=(5.0,.07,1.0));board.static_mesh_component.set_material(0,assets.load_asset('/Game/Generated/Phase052/Materials/MI_CR052_Dark'))
text('DiagnosticInstructions','Workshop',(2700,547,270),'MODULE TEST / FOLLOW BAY LABELS\n01 ROUTE   02 VERIFY   03 RELEASE',yaw=-90,size=14)
text('OpticGuide','Workshop',(2070,-470,235),'OPTIONAL / SURVEY OPTIC\nCalibration bench / tighter sight picture',yaw=90,size=15)

machine=actor('AccessMachinery',unreal.CRAccessMachinery,'RelayBunker',(5650,0,-600))
machine.shuttle.set_static_mesh(meshes['AccessShuttle']);machine.shuttle.set_relative_scale3d(unreal.Vector(1,1,1))
machine.control.set_static_mesh(meshes['DiagnosticPanel']);machine.control.set_relative_scale3d(unreal.Vector(1,1,1));machine.control.set_editor_property('relative_rotation',unreal.Rotator(yaw=180))
text('MachineStop','RelayBunker',(6050,390,-390),'LOCAL MACHINERY STOP\nE / LATCH',yaw=180,size=16)
text('ServiceWalk','RelayBunker',(5510,-430,-550),'SERVICE WALK',yaw=180,size=15)
for i,x in enumerate((5475,5650,5825,6000)):
    a=prop('SafeWalkMark'+str(i),'RelayBunker',(x,-430,-598),cube,scale=(1.1,.12,.025));a.static_mesh_component.set_material(0,assets.load_asset('/Game/Generated/Phase052/Materials/MI_CR052_Amber'))
lamp=actor('AccessTaskLight',unreal.PointLight,'RelayBunker',(5440,-220,-290));lamp.light_component.set_mobility(unreal.ComponentMobility.MOVABLE);lamp.light_component.set_intensity_units(unreal.LightUnits.LUMENS);lamp.light_component.set_intensity(270);lamp.light_component.set_light_color(unreal.LinearColor(.85,.72,.51));lamp.light_component.set_editor_property('attenuation_radius',650);lamp.light_component.set_editor_property('cast_shadows',False)

# A screened approach/retreat pocket. The center benchmark lane and north bypass stay open.
for i,(loc,scale) in enumerate([((-1120,-280,140),(.55,4.5,2.8)),((-720,230,60),(2.2,2.2,1.2)),((450,-250,60),(2.2,2.2,1.2))]):
    a=prop('YardCover'+str(i),'RailYard',loc,cube,scale=scale,collision=True);a.static_mesh_component.set_material(0,steel)
    a.static_mesh_component.set_visibility(False)
    if i==0:
        prop('ApproachPartition','RailYard',(-1120,-280,0),assets.load_asset('/Game/Generated/Phase05/Meshes/SM_CR05_CorrugatedPanel'),scale=(1.5,1,.58),yaw=90)
    else:
        for j,(dx,dy) in enumerate([(-53,-50),(-53,50),(53,-50),(53,50)]):
            prop('CoverCase'+str(i)+'_'+str(j),'RailYard',(loc[0]+dx,loc[1]+dy,0),assets.load_asset('/Game/Generated/Phase052/Meshes/SM_CR052_ServiceCrate'),scale=(1.05,1.05,1.58))
text('ApproachWorkOrder','RailYard',(-1500,-350,220),'RELAY NINE / SERVICE ROUTE\nWorkshop: inspect replacement module\nNorth track: alternate approach',yaw=0,size=18)
text('BypassMarker','RailYard',(-980,1170,140),'SERVICE ACCESS / WORKSHOP',yaw=180,size=14)
text('InterruptedWork','RailYard',(750,-1250,180),'LOCAL WORK ORDER\nPOWER UNIT REMOVED\nReplacement held at Workshop test bench',yaw=90,size=16)

# Reparent only the existing background. Preserve every authored widget and event binding.
if apply_artwork:
    assert assets.get_metadata_tag(hud,'CR.GeneratedBy')=='CinderRelay.Phase055.Interface.v1'
    assert unreal.CRInterfaceLibrary.upgrade_designer_artwork_aspect(hud)
    unreal.BlueprintEditorLibrary.compile_blueprint(hud);assert assets.save_loaded_asset(hud)
for zone in ('Persistent','RailYard','Workshop','RelayBunker'):
    assert levels.set_current_level_by_name('L_CH01_'+zone);assert levels.save_current_level()
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
after={a.get_actor_label():anchor_value(a) for a in actors.get_all_level_actors() if isinstance(a,unreal.CRCheckpoint)}
assert after==anchors,'Anchor changed during save'
(out/'audit/authoring.json').write_text(json.dumps(dict(imports=imports,anchors_unchanged=after,added=[n for n in existing if n.startswith('CR06_')]),indent=2),encoding='utf-8')
unreal.log('CR06_AUTHORING PASS')
