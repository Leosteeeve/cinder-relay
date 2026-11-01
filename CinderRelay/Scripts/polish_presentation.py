"""Phase052 owned environment import and bounded cosmetic integration.
Preserves all gameplay transforms/collision/IDs and prior source assets.
"""
import ast, json
from pathlib import Path
import unreal
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05-2';exports=out/'exports'
root='/Game/Generated/Phase052';owner='CinderRelay.Phase052.v1';tag='CR_Phase052_Generated'
assets=unreal.EditorAssetLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools();lib=unreal.MaterialEditingLibrary
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
manifest=json.loads((exports/'environment-manifest.json').read_text())
baseline=json.loads((out/'before-inventory.json').read_text())['actors']
def owned(path):
    a=assets.load_asset(path) if assets.does_asset_exist(path) else None
    if a:assert assets.get_metadata_tag(a,'CR.GeneratedBy')==owner,path
    return a
def save(a):
    assets.set_metadata_tag(a,'CR.GeneratedBy',owner);assert assets.save_loaded_asset(a);return a
def create(name,folder,cls,factory):
    return owned(root+'/'+folder+'/'+name) or save(tools.create_asset(name,root+'/'+folder,cls,factory))

# UV-based wear and roughness variation from already licensed source textures;
# no screen-space noise, secondary camera or new expensive rendering feature.
master=owned(root+'/Materials/M_CR052_Surface')
if not master:
    master=create('M_CR052_Surface','Materials',unreal.Material,unreal.MaterialFactoryNew())
    def node(cls):return lib.create_material_expression(master,cls)
    def link(a,o,b,i):assert lib.connect_material_expressions(a,o,b,i),(o,i)
    def par(name,value,vector=False):
        n=node(unreal.MaterialExpressionVectorParameter if vector else unreal.MaterialExpressionScalarParameter)
        n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',unreal.LinearColor(*value,1) if vector else value);return n
    def sample(name,sampler):
        n=node(unreal.MaterialExpressionTextureSample);n.set_editor_property('texture',assets.load_asset('/Game/Generated/Phase051/Textures/T_CR051_rusty_metal_02_'+name+'_2k'));n.set_editor_property('sampler_type',sampler);return n
    diffuse=sample('diff',unreal.MaterialSamplerType.SAMPLERTYPE_COLOR);arm=sample('arm',unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    color=par('SurfaceColor',(.15,.21,.22),True);dark=par('ShadowColor',(.08,.1,.1),True)
    blend=node(unreal.MaterialExpressionLinearInterpolate);link(dark,'',blend,'A');link(color,'',blend,'B');link(diffuse,'R',blend,'Alpha');lib.connect_material_property(blend,'',unreal.MaterialProperty.MP_BASE_COLOR)
    rough=node(unreal.MaterialExpressionLinearInterpolate);link(par('RoughnessLow',.48),'',rough,'A');link(par('Roughness',.78),'',rough,'B');link(arm,'G',rough,'Alpha');lib.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
    lib.connect_material_property(par('Metallic',.3),'',unreal.MaterialProperty.MP_METALLIC)
    normal=sample('nor_dx',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    flat=node(unreal.MaterialExpressionConstant3Vector);flat.set_editor_property('constant',unreal.LinearColor(0,0,1,1))
    nb=node(unreal.MaterialExpressionLinearInterpolate);link(flat,'',nb,'A');link(normal,'RGB',nb,'B');link(par('NormalStrength',.18),'',nb,'Alpha');lib.connect_material_property(nb,'',unreal.MaterialProperty.MP_NORMAL)
    lib.recompile_material(master);save(master)
materials={}
for key,(color,metal,rough) in manifest['palette'].items():
    m=create('MI_CR052_'+key,'Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    lib.set_material_instance_parent(m,master)
    lib.set_material_instance_vector_parameter_value(m,'SurfaceColor',unreal.LinearColor(*color,1))
    lib.set_material_instance_vector_parameter_value(m,'ShadowColor',unreal.LinearColor(*(v*.62 for v in color),1))
    for n,v in [('Metallic',metal),('Roughness',rough),('RoughnessLow',max(.2,rough-.2)),('NormalStrength',.22 if key not in('Glass','Leaf') else .04)]:lib.set_material_instance_scalar_parameter_value(m,n,v)
    lib.update_material_instance(m);save(m);materials['CR052_'+key]=m
meshes={};imports=[]
for spec in manifest['meshes']:
    name=spec['name'];m=owned(root+'/Meshes/'+name)
    if not m or '-cr052reimport' in unreal.SystemLibrary.get_command_line().lower():
        ui=unreal.FbxImportUI();ui.automated_import_should_detect_type=False;ui.import_mesh=True;ui.import_as_skeletal=False;ui.import_animations=False;ui.import_materials=False;ui.import_textures=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
        d=ui.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True
        task=unreal.AssetImportTask();task.filename=str(exports/(name+'.fbx'));task.destination_path=root+'/Meshes';task.destination_name=name;task.options=ui;task.automated=True;task.save=True;task.replace_existing=True
        tools.import_asset_tasks([task]);m=assets.load_asset(root+'/Meshes/'+name);assert m,name
        slots=list(m.get_editor_property('static_materials'))
        for s in slots:s.set_editor_property('material_interface',materials[str(s.get_editor_property('imported_material_slot_name'))])
        m.set_editor_property('static_materials',slots);save(m)
    b=m.get_bounds();dims=[2*b.box_extent.x,2*b.box_extent.y,2*b.box_extent.z]
    assert all(abs(a-v)<max(1,v*.01) for a,v in zip(dims,spec['dimensions_cm'])),(name,dims)
    meshes[name.removeprefix('SM_CR052_')]=m;imports.append({'path':m.get_path_name(),'dimensions_cm':dims,'source_triangles':spec['triangles']})
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
scope={'unreal':unreal};tree=ast.parse((p/'Scripts/migrate_streaming.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('vector','transform','snapshot')],type_ignores=[]),'snapshot','exec'),scope)
def structural(r):
    r=json.loads(json.dumps(r))
    for k in('hidden','bounds','level'):r.pop(k,None)
    for c in r['components']:
        for k in('mesh','materials','intensity','color'):c.pop(k,None)
    return r
def verify():
    for n,r in baseline.items():
        assert n in existing,n
        assert structural(scope['snapshot'](existing[n]))==structural(r),n
        assert existing[n].get_level().get_outer().get_name()==r['level'],n
verify()
def actor(name,cls,zone,loc,yaw=0):
    n='CR052_'+name;a=existing.get(n)
    if a:assert tag in [str(t) for t in a.tags] and isinstance(a,cls),n
    else:
        assert levels.set_current_level_by_name('L_CH01_'+zone);a=actors.spawn_actor_from_class(cls,unreal.Vector(*loc));a.set_actor_label(n);a.tags=[tag];existing[n]=a
    a.modify();a.set_actor_location(unreal.Vector(*loc),False,False);a.set_actor_rotation(unreal.Rotator(yaw=yaw),False);return a
def prop(name,key,loc,yaw=0,zone='RailYard',scale=(1,1,1),shadow=True):
    a=actor(name,unreal.StaticMeshActor,zone,loc,yaw);a.set_actor_scale3d(unreal.Vector(*scale));c=a.static_mesh_component;c.set_static_mesh(meshes[key]);c.set_collision_profile_name('NoCollision');c.set_editor_property('can_ever_affect_navigation',False);c.set_cast_shadow(shadow);a.set_actor_enable_collision(False);return a
for name in('CR05_RailCar-800','CR05_RailCar800'):
    a=existing[name];assert a.static_mesh_component.get_collision_profile_name()=='NoCollision';a.modify();a.static_mesh_component.set_static_mesh(meshes['RailServiceCar']);a.static_mesh_component.set_editor_property('override_materials',[])
prop('WorkshopPortal','WorkshopPortal',(1540,0,0))
for x in(-1200,500):prop('GantryServices'+str(x),'GantryServices',(x,0,600))
# Three separate maintenance stories at the margins; center, flank and cover routes stay open.
for n,key,loc,yaw in[
 ('CableStation','CableSpool',(-1050,-430,0),18),('CableCrate','ServiceCrate',(-925,-435,0),-8),
 ('CableBarrel','Barrel',(-830,-465,0),0),('CableScrap','ScrapStack',(-1170,-475,0),12),
 ('ServiceTrolley','MaintenanceTrolley',(370,1040,0),-18),('ServiceSpool','CableSpool',(520,1065,0),30),
 ('ServiceCase','UtilityBox',(820,1250,0),-90),('ServiceCrate','ServiceCrate',(760,1090,0),8),
 ('EntryCrate','ServiceCrate',(1360,510,0),-7),('EntryBarrel','Barrel',(1250,560,0),0),
 ('EntryBarrel2','Barrel',(1314,585,0),0),('EntryScrap','ScrapStack',(1090,1030,0),-20)]:prop(n,key,loc,yaw)
prop('MidgroundNorth','MidgroundWorks',(2600,3600,0),-15,shadow=False)
prop('MidgroundSouth','MidgroundWorks',(-400,-3650,0),22,scale=(.85,.85,.78),shadow=False)
prop('MidgroundRear','MidgroundWorks',(4100,1500,0),-90,scale=(1.1,1.1,1.35),shadow=False)
for i,loc in enumerate([(-1560,1210,0),(-1320,1240,0),(-650,1190,0),(1020,1280,0),(1430,1010,0),(-1520,-1200,0),(700,-1260,0)]):prop('Weed'+str(i),'WeedTuft',loc,i*31,shadow=False)
# Sparse native decals tie service clusters to the ground. Original Phase05 mask;
# feathered bounds avoid opaque rectangles and retain the original collision floor.
decal=owned(root+'/Materials/M_CR052_ServiceGrime')
if not decal:
    decal=create('M_CR052_ServiceGrime','Materials',unreal.Material,unreal.MaterialFactoryNew())
    decal.set_editor_property('material_domain',unreal.MaterialDomain.MD_DEFERRED_DECAL)
    decal.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
    def dn(cls):return lib.create_material_expression(decal,cls)
    def dc(x):
        a=dn(unreal.MaterialExpressionConstant);a.set_editor_property('r',x);return a
    def dl(a,o,b,i):
        names=list(lib.get_material_expression_input_names(b))
        if i not in names and len(names)==1:i=names[0]
        assert lib.connect_material_expressions(a,o,b,i),(o,i)
    uv=dn(unreal.MaterialExpressionTextureCoordinate);sub=dn(unreal.MaterialExpressionSubtract);dl(uv,'',sub,'A');dl(dc(.5),'',sub,'B')
    dot=dn(unreal.MaterialExpressionDotProduct);dl(sub,'',dot,'A');dl(sub,'',dot,'B')
    mul=dn(unreal.MaterialExpressionMultiply);dl(dot,'',mul,'A');dl(dc(4.3),'',mul,'B')
    inv=dn(unreal.MaterialExpressionOneMinus);dl(mul,'',inv,'Input')
    sat=dn(unreal.MaterialExpressionSaturate);dl(inv,'',sat,'Input')
    tex=dn(unreal.MaterialExpressionTextureSample);tex.set_editor_property('texture',assets.load_asset('/Game/Generated/Phase05/Textures/T_CR05_SurfaceMask'));tex.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    op=dn(unreal.MaterialExpressionMultiply);dl(sat,'',op,'A');dl(tex,'R',op,'B')
    strength=dn(unreal.MaterialExpressionMultiply);dl(op,'',strength,'A');dl(dc(.56),'',strength,'B')
    col=dn(unreal.MaterialExpressionConstant3Vector);col.set_editor_property('constant',unreal.LinearColor(.055,.045,.028,1))
    lib.connect_material_property(col,'',unreal.MaterialProperty.MP_BASE_COLOR);lib.connect_material_property(strength,'',unreal.MaterialProperty.MP_OPACITY);lib.connect_material_property(dc(.95),'',unreal.MaterialProperty.MP_ROUGHNESS)
    lib.recompile_material(decal);save(decal)
for i,(x,y,sx,sy) in enumerate([(-1030,-440,170,110),(-600,-50,260,90),(40,360,210,70),(370,1050,150,130),(1320,530,130,100),(-350,800,360,150),(-950,-800,360,150)]):
    a=actor('ServiceGrime'+str(i),unreal.DecalActor,'RailYard',(x,y,8));a.set_actor_rotation(unreal.Rotator(pitch=-90,yaw=i*23),False)
    a.decal.set_decal_material(decal);a.decal.set_editor_property('decal_size',unreal.Vector(20,sx,sy));a.decal.set_editor_property('fade_screen_size',.005)
# Actual fixtures at shadow-route and interior sides. Non-shadowed fill is bounded in radius.
for name,zone,loc,lumens,color,radius in[
 ('FlankBounce','RailYard',(-850,1140,245),300,(.58,.70,.83),560),
 ('YardServiceFill','RailYard',(-600,-320,440),160,(.63,.73,.84),800),
 ('WorkshopEntryFill','Workshop',(1860,0,285),520,(1,.72,.43),530),
 ('WorkshopAisleFill','Workshop',(2800,200,300),360,(.82,.76,.61),600)]:
    a=actor(name,unreal.PointLight,zone,loc);c=a.light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity_units(unreal.LightUnits.LUMENS);c.set_intensity(lumens);c.set_light_color(unreal.LinearColor(*color));c.set_editor_property('attenuation_radius',radius);c.set_editor_property('source_radius',35);c.set_editor_property('cast_shadows',False)
# Metering is retained. Local contrast preserves shadow information without a global EV lift.
a=existing['CR_Exposure'];a.modify();s=a.get_editor_property('settings')
s.set_editor_property('override_local_exposure_shadow_contrast_scale',True);s.set_editor_property('local_exposure_shadow_contrast_scale',.8)
s.set_editor_property('override_local_exposure_highlight_contrast_scale',True);s.set_editor_property('local_exposure_highlight_contrast_scale',.9);a.set_editor_property('settings',s)
verify();assert levels.save_all_dirty_levels()
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent');existing={a.get_actor_label():a for a in actors.get_all_level_actors()};verify()
added={}
for n,a in existing.items():
    if tag not in [str(t) for t in a.tags]:continue
    if isinstance(a,unreal.StaticMeshActor):
        c=a.static_mesh_component;assert str(c.get_collision_profile_name())=='NoCollision' and not c.get_editor_property('can_ever_affect_navigation'),n
    added[n]={'level':a.get_level().get_outer().get_name(),'transform':scope['transform'](a.get_actor_transform())}
(out/'environment-import.json').write_text(json.dumps({'imports':imports,'original_actors_preserved':len(baseline),'added':added,'altered_old_appearance':['CR05_RailCar-800','CR05_RailCar800','CR_Exposure'],'global_quality_unchanged':True},indent=2))
unreal.log('CR052_ENVIRONMENT_PASS '+str(len(added)));unreal.SystemLibrary.quit_editor()
