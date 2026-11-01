"""Phase05 owned cosmetic pass. Run in Editor; -CR05Zone=yard first, then all.
Original gameplay actors, transforms, collision profiles and checkpoint IDs are preserved.
"""
import ast,json
from pathlib import Path
import unreal
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05';exports=out/'exports'
root='/Game/Generated/Phase05';owner='CinderRelay.Phase05.v1';tag='CR_Phase05_Generated'
all_zones='-cr05zone=all' in unreal.SystemLibrary.get_command_line().lower()
assets=unreal.EditorAssetLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools();lib=unreal.MaterialEditingLibrary
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
manifest=json.loads((exports/'environment-manifest.json').read_text());baseline=json.loads((out/'editor-baseline.json').read_text())['actors']
def owned(path):
 a=assets.load_asset(path) if assets.does_asset_exist(path) else None
 if a:assert assets.get_metadata_tag(a,'CR.GeneratedBy')==owner,'Refusing unowned asset '+path
 return a
def save(a):assets.set_metadata_tag(a,'CR.GeneratedBy',owner);assert assets.save_loaded_asset(a);return a
def create(name,folder,cls,factory):return owned(root+'/'+folder+'/'+name) or save(tools.create_asset(name,root+'/'+folder,cls,factory))
textures={}
for n in ('T_CR05_SurfaceMask','T_CR05_SurfaceNormal'):
 tex=owned(root+'/Textures/'+n)
 if not tex:
  task=unreal.AssetImportTask();task.filename=str(p/'ArtSource/Blender/Phase05'/(n+'.png'));task.destination_path=root+'/Textures';task.destination_name=n;task.automated=True;task.save=True;tools.import_asset_tasks([task]);tex=assets.load_asset(root+'/Textures/'+n);assert tex
  tex.set_editor_property('srgb',False)
  tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP if n.endswith('Normal') else unreal.TextureCompressionSettings.TC_MASKS);save(tex)
 textures[n]=tex
master=owned(root+'/Materials/M_CR05_Surface')
if not master or assets.get_metadata_tag(master,'CR05.MaterialComplete')!='1':
 master=create('M_CR05_Surface','Materials',unreal.Material,unreal.MaterialFactoryNew());lib.delete_all_material_expressions(master)
 def node(cls):return lib.create_material_expression(master,cls)
 def connect(a,output,b,input):
  # Single-input native expression nodes may expose an empty pin name, not "Input".
  names=list(lib.get_material_expression_input_names(b))
  if input not in names and len(names)==1:input=names[0]
  assert lib.connect_material_expressions(a,output,b,input),(a,output,b,input,names)
 def param(name,value,vector=False):
  n=node(unreal.MaterialExpressionVectorParameter if vector else unreal.MaterialExpressionScalarParameter);n.set_editor_property('parameter_name',name)
  n.set_editor_property('default_value',unreal.LinearColor(*value,1) if vector else value);return n
 color=param('SurfaceColor',(.15,.22,.25),True);dark=param('ShadowColor',(.05,.07,.08),True)
 tex=node(unreal.MaterialExpressionTextureObjectParameter);tex.set_editor_property('parameter_name','SurfaceMask');tex.set_editor_property('texture',textures['T_CR05_SurfaceMask'])
 fn=node(unreal.MaterialExpressionMaterialFunctionCall);fn.set_editor_property('material_function',assets.load_asset('/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture'))
 ins=list(lib.get_material_expression_input_names(fn));outs=list(lib.get_material_expression_output_names(fn))
 unreal.log('CR05_MATERIAL_PINS '+str((ins,outs)))
 def pin(names,needle):return next(n for n in names if n.replace(' ','').lower().startswith(needle.lower()))
 connect(tex,'',fn,pin(ins,'TextureObject'))
 size=node(unreal.MaterialExpressionConstant3Vector);size.set_editor_property('constant',unreal.LinearColor(180,180,180,1));connect(size,'',fn,pin(ins,'TextureSize'))
 mask=node(unreal.MaterialExpressionComponentMask);mask.set_editor_property('r',True);mask.set_editor_property('g',False);mask.set_editor_property('b',False);mask.set_editor_property('a',False);connect(fn,pin(outs,'XYZ'),mask,'Input')
 blend=node(unreal.MaterialExpressionLinearInterpolate);connect(dark,'',blend,'A');connect(color,'',blend,'B');connect(mask,'',blend,'Alpha');assert lib.connect_material_property(blend,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for prop,name,value in ((unreal.MaterialProperty.MP_METALLIC,'Metallic',.4),(unreal.MaterialProperty.MP_ROUGHNESS,'Roughness',.7)):
  assert lib.connect_material_property(param(name,value),'',prop)
 normal=node(unreal.MaterialExpressionTextureSampleParameter2D);normal.set_editor_property('parameter_name','MicroNormal');normal.set_editor_property('texture',textures['T_CR05_SurfaceNormal']);normal.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
 assert lib.connect_material_property(normal,'RGB',unreal.MaterialProperty.MP_NORMAL)
 emit=node(unreal.MaterialExpressionMultiply);connect(color,'',emit,'A');connect(param('Emissive',0),'',emit,'B');assert lib.connect_material_property(emit,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 lib.set_material_usage(master,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH);lib.recompile_material(master);assets.set_metadata_tag(master,'CR05.MaterialComplete','1');save(master)
materials={}
for key,(color,metal,rough) in manifest['palette'].items():
 m=create('MI_CR05_'+key,'Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew());lib.set_material_instance_parent(m,master)
 lib.set_material_instance_vector_parameter_value(m,'SurfaceColor',unreal.LinearColor(*color,1))
 lib.set_material_instance_vector_parameter_value(m,'ShadowColor',unreal.LinearColor(*(v*.55 for v in color),1))
 lib.set_material_instance_scalar_parameter_value(m,'Metallic',metal);lib.set_material_instance_scalar_parameter_value(m,'Roughness',rough)
 lib.set_material_instance_scalar_parameter_value(m,'Emissive',2.0 if key=='Light' else .65 if key=='Cyan' else 0)
 lib.update_material_instance(m);save(m);materials['CR05_'+key]=m
meshes={};bounds=[]
for spec in manifest['meshes']:
 name=spec['name'];m=owned(root+'/Meshes/'+name)
 if not m or (name=='SM_CR05_RailServiceCar' and '-cr05refreshrail' in unreal.SystemLibrary.get_command_line().lower()):
  ui=unreal.FbxImportUI();ui.automated_import_should_detect_type=False;ui.import_mesh=True;ui.import_as_skeletal=False;ui.import_animations=False;ui.import_materials=False;ui.import_textures=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
  d=ui.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.force_front_x_axis=False
  task=unreal.AssetImportTask();task.filename=str(exports/(name+'.fbx'));task.destination_path=root+'/Meshes';task.destination_name=name;task.options=ui;task.automated=True;task.save=True;task.replace_existing=True;task.replace_existing_settings=True;tools.import_asset_tasks([task]);m=assets.load_asset(root+'/Meshes/'+name);assert m
  slots=list(m.get_editor_property('static_materials'))
  for slot in slots:
   key=str(slot.get_editor_property('imported_material_slot_name'));assert key in materials,key;slot.set_editor_property('material_interface',materials[key])
  m.set_editor_property('static_materials',slots);save(m)
 b=m.get_bounds();dims=[b.box_extent.x*2,b.box_extent.y*2,b.box_extent.z*2]
 # Exact export/import orientation must match the actual model, not a presumed FBX convention.
 assert all(abs(a-v)<max(2,v*.025) for a,v in zip(dims,spec['dimensions_cm'])),(name,dims,spec['dimensions_cm'])
 bounds.append({'mesh':name,'import_dimensions_cm':dims,'triangles_authored':spec['triangles']});meshes[name.removeprefix('SM_CR05_')]=m
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
def actor(label,cls,zone,loc,rot=0):
 a=existing.get(label)
 if a:assert tag in [str(t) for t in a.tags] and isinstance(a,cls),'Unowned actor '+label
 else:
  assert levels.set_current_level_by_name('L_CH01_'+zone);a=actors.spawn_actor_from_class(cls,unreal.Vector(*loc));a.set_actor_label(label);a.tags=[tag];existing[label]=a
 a.modify();a.set_actor_location(unreal.Vector(*loc),False,False);a.set_actor_rotation(unreal.Rotator(yaw=rot),False);return a
def prop(label,mesh,zone,loc,rot=0,scale=(1,1,1)):
 a=actor('CR05_'+label,unreal.StaticMeshActor,zone,loc,rot);a.set_actor_scale3d(unreal.Vector(*scale));c=a.static_mesh_component;c.set_static_mesh(meshes[mesh]);c.set_collision_profile_name('NoCollision');c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);c.set_editor_property('can_ever_affect_navigation',False);a.set_actor_enable_collision(False);return a
def skin(a,key):
 a.modify()
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  for i in range(c.get_num_materials()):c.set_material(i,materials['CR05_'+key])
def hide(a):a.modify();a.set_actor_hidden_in_game(True)
# Material-only changes on existing shells; transform/collision remain the audited values.
for name,a in list(existing.items()):
 zone=a.get_level().get_outer().get_name()
 if not (zone=='L_CH01_RailYard' or (all_zones and zone in ('L_CH01_Workshop','L_CH01_RelayBunker'))):continue
 if not isinstance(a,unreal.StaticMeshActor) or name.startswith('CR05_'):continue
 if any(x in name for x in ('CarBody','CarRoof','CarWindow','Wheel')):hide(a);continue
 key='Concrete' if any(x in name for x in ('Floor','AccessRamp','RampWall','BunkerSide','Barrier')) else 'Dark' if 'Roof' in name else 'Wood' if 'Sleeper' in name else 'Amber' if any(x in name for x in ('Stripe','Guide')) else 'Paint' if any(x in name for x in ('Warehouse','Workshop','Storage')) else 'Steel'
 skin(a,key)
for n in ('CR_WorkshopFront-440','CR_WorkshopFront440','CR_WorkshopLintelFront'):skin(existing[n],'Paint')
# Hide oversized instruction billboards; functional HUD remains. Actor is retained for rollback.
for n in ('CR02_ScoutWarning','CR_YardIntro'):
 if n in existing:hide(existing[n])
for lane,x in[(-800,-950),(800,-350)]:prop('RailCar'+str(lane),'RailServiceCar','RailYard',(x,lane,0))
for i,x in enumerate((-1200,-350,500,1250)):
 for y in(-1370,1370):prop(f'YardColumn{i}_{y}','SteelColumn','RailYard',(x,y,0),scale=(1.2,1.2,1.5))
for x in(-1200,500):prop('Gantry'+str(x),'Gantry','RailYard',(x,0,600))
for x in(470,1030):prop('WarehouseFront'+str(x),'CorrugatedPanel','RailYard',(x,-680,0),180,scale=(1.1,1,1.25))
for x in(350,650,950):prop('WarehousePanel'+str(x),'CorrugatedPanel','RailYard',(x,-1320,0),scale=(1,1,1.5))
for i,y in enumerate((-1120,-820)):
 prop('WarehouseSidePanel'+str(i),'CorrugatedPanel','RailYard',(1217,y,0),90,scale=(1,1,1.5))
for i,(x,y) in enumerate([(-1730,-1210),(-400,-1210),(720,1220),(1260,-1150)]):
 prop('YardDebris'+str(i),'MaintenanceDebris','RailYard',(x,y,6),i*57)
 prop('YardWeed'+str(i),'WeedCluster','RailYard',(x+80,y,5),i*23,scale=(1.3,1.3,1.3))
prop('YardPump','PumpMotor','RailYard',(920,-1150,0),90)
for y in(-470,470):
 prop('WorkshopEntryColumn'+str(y),'SteelColumn','RailYard',(1550,y,0),scale=(1.3,1.3,1.2))
 prop('EntryLamp'+str(y),'CagedLamp','RailYard',(1530,y,325),scale=(1.1,1.1,1.1))
 lamp=actor('CR05_EntryPractical'+str(y),unreal.PointLight,'RailYard',(1500,y,295));lc=lamp.light_component;lc.set_mobility(unreal.ComponentMobility.MOVABLE);lc.set_intensity_units(unreal.LightUnits.LUMENS);lc.set_editor_property('use_inverse_squared_falloff',True);lc.set_intensity(420);lc.set_light_color(unreal.LinearColor(1,.58,.26));lc.set_editor_property('attenuation_radius',460);lc.set_editor_property('cast_shadows',True)
for n in ('CR_Gate_AB','CR_Gate_BC'):skin(existing[n],'Dark')
# Environment light changes are local content, no renderer/scalability change.
sun=existing['CR_Sun'];sun.modify();sun.light_component.set_intensity(2.4);sun.light_component.set_light_color(unreal.LinearColor(.76,.84,.94));sun.light_component.set_light_source_angle(5.0);sun.set_actor_rotation(unreal.Rotator(pitch=-28,yaw=-35),False)
sky=existing['CR_SkyLight'];sky.modify();sky.light_component.set_intensity(1.2)
atmos=existing['CR_Atmosphere'];atmos.modify();ac=atmos.get_component_by_class(unreal.SkyAtmosphereComponent);ac.set_mie_scattering_scale(5);ac.set_mie_anisotropy(.3)
post=existing['CR_Exposure'];post.modify();settings=post.get_editor_property('settings')
settings.set_editor_property('auto_exposure_min_brightness',0.0);settings.set_editor_property('auto_exposure_max_brightness',3.0)
post.set_editor_property('settings',settings)
fog=actor('CR05_AtmosphericHaze',unreal.ExponentialHeightFog,'Persistent',(0,0,0));fc=fog.get_component_by_class(unreal.ExponentialHeightFogComponent);fc.set_editor_property('fog_density',.018);fc.set_editor_property('fog_height_falloff',.25);fc.set_editor_property('start_distance',300.0);fc.set_editor_property('bEnableVolumetricFog',False)
if all_zones:
 # 05A actual renders were inspected before enabling expansion. This is not final human art acceptance.
 assert (out/'render-review.json').exists(),'A real representative render is required first'
 for n,a in list(existing.items()):
  if n.startswith(('CR_StorageFrame','CR_StorageCrate','CR_ServerRack','CR_ServerIndicator','CR_BrokenMachine')):hide(a)
 for i,x in enumerate((1850,2120,2700,3250)):
  prop('WorkshopCabinet'+str(i),'ServiceCabinet','Workshop',(x,590,0),180)
 for i,x in enumerate((1810,2110,2700,3000,3300)):
  for y in(-685,685):
   prop('WorkshopWall'+str(i)+'_'+str(y),'CorrugatedPanel','Workshop',(x,y,0),180 if y<0 else 0,scale=(1,1,1.2))
   prop('WorkshopPipe'+str(i)+'_'+str(y),'TwinConduit','Workshop',(x,y*.97,410))
 for x in(1850,2600,3360):
  for y in(-620,620):prop('WorkshopFrame'+str(x)+'_'+str(y),'SteelColumn','Workshop',(x,y,0),scale=(1,1,1.23))
 prop('WorkshopMotor','PumpMotor','Workshop',(3100,420,0),90,scale=(1.35,1.35,1.35))
 prop('WorkshopCable','CableSpool','Workshop',(3230,530,5));prop('PowerBenchTools','ToolTray','Workshop',(2720,-365,107),90)
 # Keep calibration camera/hand volume and Survey Optic/power-module interaction volumes empty.
 prop('CalibrationCable','CableSpool','Workshop',(2460,-560,4),scale=(.8,.8,.8))
 for x in(2150,2950):prop('WorkshopPendant'+str(x),'CagedLamp','Workshop',(x,0,380),scale=(1.5,1.5,1.5))
 for x in(5750,6050,6350,6650):prop('BunkerRack'+str(x),'ControlRack','RelayBunker',(x,515,-600))
 for x in(5600,5900,6200,6500,6800):
  for y in(-620,620):prop('BunkerConduit'+str(x)+'_'+str(y),'TwinConduit','RelayBunker',(x,y,-210))
 for x in(5580,6300,7050):
  for y in(-600,600):prop('BunkerSupport'+str(x)+'_'+str(y),'SteelColumn','RelayBunker',(x,y,-600),scale=(.8,.8,1.23))
 for i,x in enumerate((3800,4100,4400,4700,5000)):
  z=-(x-3600)/3+130
  a=prop('RampConduit'+str(i),'TwinConduit','RelayBunker',(x,175,z));a.set_actor_rotation(unreal.Rotator(pitch=-18.435),False)
 for x in(5650,6750):prop('BunkerCeilingLamp'+str(x),'CagedLamp','RelayBunker',(x,0,-125))
 # Replace only light units/colors/intensity. Shared shell, safe floors and navigation are untouched.
 for n,lumens,color in [('CR_WorkshopLight1',1100,(1,.62,.31)),('CR_WorkshopLight2',800,(1,.70,.43)),('CR_RampLamp1',170,(.32,.58,.62)),('CR_RampLamp2',170,(.32,.58,.62)),('CR_BunkerLight1',650,(.27,.54,.59)),('CR_BunkerLight2',450,(.32,.57,.61))]:
  a=existing[n];a.modify();lc=a.light_component;lc.set_intensity_units(unreal.LightUnits.LUMENS);lc.set_editor_property('use_inverse_squared_falloff',True);lc.set_intensity(lumens);lc.set_light_color(unreal.LinearColor(*color));lc.set_editor_property('cast_shadows',True)
 def sign(label,zone,loc,text,yaw=0,size=9):
  a=actor('CR05_'+label,unreal.TextRenderActor,zone,loc,yaw);c=a.text_render;c.set_text(text);c.set_world_size(size);c.set_text_render_color(unreal.Color(170,170,143));c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
 sign('WorkshopRecord','Workshop',(2670,649,185),'MAINTENANCE / OPEN WORK ORDER\nRelay Nine: power unit removed.\nReturn replacement to access terminal.',-90,8)
 sign('YardServiceMark','RailYard',(-955,-963,233),'R-09 / FIELD SERVICE',-90,9)
 sign('BunkerRecord','RelayBunker',(6100,-635,-425),'LOCAL CONTROL / RELAY NINE\nCARRIER TEST INCOMPLETE\nAwaiting acknowledgement.',90,9)
 sign('BunkerNine','RelayBunker',(7160,0,-250),'09\nMERIDIAN / RELAY',180,24)
# Compare all original actor transforms/collision/profile/IDs. Materials, hidden flags and light settings are intentional changes.
scope={'unreal':unreal};tree=ast.parse((p/'Scripts/migrate_streaming.py').read_text(encoding='utf-8-sig'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('vector','transform','snapshot')],type_ignores=[]),'snapshot','exec'),scope)
def structural(r):
 r=json.loads(json.dumps(r));r.pop('hidden',None);r.pop('level',None);r.pop('checkpoint_id',None)
 r['components']=[c for c in r['components'] if c['name']!='PresentationMesh']
 for c in r['components']:
  c.pop('materials',None);c.pop('intensity',None);c.pop('color',None)
  if r['label'] in ('CR02_Scout_1','CR02_Scout_2') and c['cls']=='/Script/Engine.SkeletalMeshComponent':
   for k in ('transform','enabled','profile'):c.pop(k,None)
 if r['label']=='CR_Sun':r.pop('transform',None);[c.pop('transform',None) for c in r['components']]
 return r
changed=[n for n,r in baseline.items() if n not in existing or structural(scope['snapshot'](existing[n]))!=structural(r)]
assert not changed,'Unexpected gameplay structure change '+str(changed)
for n,r in baseline.items():
 if 'checkpoint_id' in r:assert str(existing[n].checkpoint_id)==r['checkpoint_id']
assert levels.save_all_dirty_levels()
receipt={'stage':'05B' if all_zones else '05A','preserved_gameplay_actors':len(baseline),'added_actors':[{'label':n,'level':a.get_level().get_outer().get_name()} for n,a in existing.items() if n not in baseline],'bounds':bounds,'assets':list(assets.list_assets(root,recursive=True))}
(out/('zone-assets.json' if all_zones else 'yard-assets.json')).write_text(json.dumps(receipt,indent=2),encoding='utf-8');unreal.log('CR05_ENVIRONMENT_PASS '+str(len(receipt['added_actors'])))
unreal.SystemLibrary.quit_editor()
