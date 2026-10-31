"""Create owned Phase02 content in the actual Editor; never regenerate old maps.

First run builds gunplay assets. -CRCreateEncounter additionally places the
two approved scouts and navigation after their native classes are available.
"""
import unreal, json, math, random, wave, struct, time
from pathlib import Path
ROOT='/Game/Generated/Phase02'
OWNER='CinderRelay.Phase02.v1'
META='CR.GeneratedBy'
assets=unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tools=unreal.AssetToolsHelpers.get_asset_tools()
out=Path(unreal.Paths.project_dir()).parent/'.environment-local/phase-02'
out.mkdir(parents=True,exist_ok=True)

def owned(path,cls,factory):
    if assets.does_asset_exist(path):
        asset=assets.load_asset(path)
        assert str(assets.get_metadata_tag(asset,META))==OWNER,'Refusing unowned asset '+path
        return asset
    folder,name=path.rsplit('/',1)
    asset=tools.create_asset(name,folder,cls,factory)
    assert asset
    assets.set_metadata_tag(asset,META,OWNER)
    return asset

def save(asset):
    assert assets.save_loaded_asset(asset,only_if_is_dirty=False)

def material(name,color,emissive=False):
    path=ROOT+'/Materials/'+name
    exists=assets.does_asset_exist(path)
    mat=owned(path,unreal.Material,unreal.MaterialFactoryNew())
    if not exists:
        c=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector)
        c.set_editor_property('constant',unreal.LinearColor(*color,1))
        unreal.MaterialEditingLibrary.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
        if emissive: unreal.MaterialEditingLibrary.connect_material_property(c,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        unreal.MaterialEditingLibrary.recompile_material(mat)
    save(mat)
    return mat

def data(path,cls):
    f=unreal.DataAssetFactory(); f.set_editor_property('data_asset_class',cls)
    return owned(path,cls,f)

def blueprint(name,parent):
    f=unreal.BlueprintFactory(); f.set_editor_property('parent_class',parent)
    return owned(ROOT+'/Blueprints/'+name,unreal.Blueprint,f)

def finish(bp):
    unreal.BlueprintEditorLibrary.compile_blueprint(bp); save(bp)
    return unreal.load_class(None,bp.get_path_name()+'_C')

def prototype_audio(name,kind):
    path=ROOT+'/Audio/'+name
    if assets.does_asset_exist(path):
        sound=assets.load_asset(path)
        assert str(assets.get_metadata_tag(sound,META))==OWNER
        return sound
    # Original, deterministic synthesized placeholder cues; no samples or external recording.
    rate=24000; duration={'shot':.26,'reload':2.4,'dry':.09,'hit':.12,'impact':.13,'hurt':.32}[kind]
    rng=random.Random(47); samples=[]
    for i in range(int(rate*duration)):
        t=i/rate; noise=rng.uniform(-1,1)
        if kind=='shot': value=(.7*noise+.3*math.sin(2*math.pi*95*t))*math.exp(-t*24)
        elif kind=='reload':
            value=sum((noise*.45+math.sin(2*math.pi*440*t)*.15)*math.exp(-max(0,t-p)*45) if p<=t<p+.16 else 0 for p in (0,.65,1.75,2.2))
        elif kind=='dry': value=math.sin(2*math.pi*550*t)*math.exp(-t*65)*.35
        elif kind=='hit': value=(math.sin(2*math.pi*1050*t)+math.sin(2*math.pi*1400*t))*.18*math.exp(-t*35)
        elif kind=='impact': value=noise*.4*math.exp(-t*45)
        else: value=(math.sin(2*math.pi*(100-80*t)*t)+noise*.15)*.3*math.exp(-t*12)
        samples.append(struct.pack('<h',int(max(-.95,min(.95,value))*32767)))
    source=out/(name+'.wav')
    with wave.open(str(source),'wb') as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate); wav.writeframes(b''.join(samples))
    task=unreal.AssetImportTask(); task.filename=str(source); task.destination_path=ROOT+'/Audio'; task.destination_name=name; task.automated=True; task.save=True; task.replace_existing=False
    tools.import_asset_tasks([task]); sound=assets.load_asset(path); assert sound,'Audio import failed '+name
    assets.set_metadata_tag(sound,META,OWNER); save(sound); return sound

metal=material('M_RookMetal',(.065,.075,.085))
accent=material('M_RookAmber',(.85,.38,.06),True)
weapon=data(ROOT+'/Data/DA_Rook5',unreal.CRWeaponData)
weapon.set_editor_property('metal_material',metal); weapon.set_editor_property('accent_material',accent)
for kind,prop in [('shot','shot_sound'),('reload','reload_sound'),('dry','dry_sound'),('hit','hit_sound'),('impact','impact_sound'),('hurt','hurt_sound')]:
    weapon.set_editor_property(prop,prototype_audio('S_Proto_'+kind.title(),kind))
save(weapon)
context=data(ROOT+'/Input/IMC_Combat',unreal.InputMappingContext); context.unmap_all()
actions={}
for name,key in [('Fire','LeftMouseButton'),('Aim','RightMouseButton'),('Reload','R')]:
    action=data(ROOT+'/Input/IA_'+name,unreal.InputAction); action.set_editor_property('value_type',unreal.InputActionValueType.BOOLEAN)
    k=unreal.Key(); k.set_editor_property('key_name',key); context.map_key(action,k); save(action); actions[name.lower()+'_action']=action
save(context)
parent=unreal.load_class(None,'/Game/Generated/Phase01A/Blueprints/BP_CRCharacter.BP_CRCharacter_C')
bp=blueprint('BP_CRCombatCharacter',parent)
cdo=unreal.get_default_object(unreal.load_class(None,bp.get_path_name()+'_C'))
cdo.set_editor_property('rook_data',weapon); cdo.set_editor_property('combat_mapping_context',context)
for name,action in actions.items(): cdo.set_editor_property(name,action)
player=finish(bp)
mode=blueprint('BP_CRCombatGameMode',unreal.load_class(None,'/Game/Generated/Phase01A/Blueprints/BP_CRGameMode.BP_CRGameMode_C'))
unreal.get_default_object(unreal.load_class(None,mode.get_path_name()+'_C')).set_editor_property('default_pawn_class',player)
mode_class=finish(mode)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode',mode_class)
assert levels.save_all_dirty_levels()
unreal.log('CR02_GUNPLAY_ASSETS_PASS')
if '-CRCreateEncounter' in unreal.SystemLibrary.get_command_line():
    # Runtime nodes are serialized by Editor APIs; no raw asset fabrication.
    board=owned(ROOT+'/AI/BB_AshWarden',unreal.BlackboardData,unreal.BlackboardDataFactory())
    keys=[]
    for key,type_name in [('State','BlackboardKeyType_Int'),('HasSight','BlackboardKeyType_Bool'),('LastKnown','BlackboardKeyType_Vector')]:
        kind=unreal.load_class(None,'/Script/AIModule.'+type_name); assert kind
        entry=unreal.BlackboardEntry(); entry.set_editor_property('entry_name',key); entry.set_editor_property('key_type',unreal.new_object(kind,outer=board)); keys.append(entry)
    board.set_editor_property('keys',keys); save(board)
    tree=owned(ROOT+'/AI/BT_AshWarden',unreal.BehaviorTree,unreal.BehaviorTreeFactory())
    tree.set_editor_property('blackboard_asset',board)
    if not tree.get_editor_property('root_node'):
        root=unreal.new_object(unreal.BTComposite_Sequence,outer=tree)
        task=unreal.new_object(unreal.CRBTTaskWarden,outer=tree)
        wait=unreal.new_object(unreal.BTTask_Wait,outer=tree)
        for prop,value in [('wait_time',.25),('random_deviation',0)]:
            setting=wait.get_editor_property(prop); setting.set_editor_property('default_value',value); wait.set_editor_property(prop,setting)
        children=[]
        for node in [task,wait]:
            child=unreal.BTCompositeChild(); child.set_editor_property('child_task',node); children.append(child)
        root.set_editor_property('children',children); tree.set_editor_property('root_node',root)
    save(tree)
    enemy_bp=blueprint('BP_AshWarden',unreal.CRAshWarden)
    enemy_cdo=unreal.get_default_object(unreal.load_class(None,enemy_bp.get_path_name()+'_C'))
    enemy_cdo.set_editor_property('behavior',tree)
    enemy_cdo.set_editor_property('shot_sound',weapon.get_editor_property('shot_sound'))
    enemy_cdo.set_editor_property('hit_sound',weapon.get_editor_property('impact_sound'))
    enemy_cdo.set_editor_property('death_sound',weapon.get_editor_property('hurt_sound'))
    enemy_class=finish(enemy_bp)
    assert levels.set_current_level_by_name('L_CH01_RailYard')
    existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
    def placed(label,cls,pos):
        if label in existing:
            a=existing[label]; assert 'CR_Phase02_Generated' in [str(t) for t in a.tags], 'Refusing unowned actor '+label
            return a
        a=actors.spawn_actor_from_class(cls,unreal.Vector(*pos)); assert a
        a.set_actor_label(label); a.set_editor_property('tags',[unreal.Name('CR_Phase02_Generated')]); return a
    cloth=material('M_WardenCloth',(.19,.23,.20)); helmet=material('M_WardenHelmet',(.37,.14,.07))
    for i,pos in enumerate([(200,-350,92),(850,400,92)]):
        enemy=placed('CR02_Scout_'+str(i+1),enemy_class,pos)
        enemy.set_editor_property('enemy_id','CR02_Scout_'+str(i+1)); enemy.set_actor_rotation(unreal.Rotator(pitch=0,yaw=180,roll=0),False)
        enemy.set_editor_property('attack_interval',1.8+i*.25)
        for mesh in enemy.get_components_by_class(unreal.StaticMeshComponent): mesh.set_material(0,helmet if mesh==enemy.head else cloth)
    ammo=placed('CR02_AmmoCase',unreal.CRAmmoPickup,(1250,450,45))
    ammo.mesh.set_static_mesh(assets.load_asset('/Engine/BasicShapes/Cube')); ammo.mesh.set_material(0,accent); ammo.set_actor_scale3d(unreal.Vector(.35,.55,.35))
    nav=placed('CR02_YardNavBounds',unreal.NavMeshBoundsVolume,(-200,0,150))
    nav.set_actor_scale3d(unreal.Vector(18,14,3))
    origin,extent=nav.get_actor_bounds(False)
    assert extent.x>1500 and extent.y>1000 and extent.z>200, 'Native volume factory did not create valid bounds; do not fake brush geometry'
    warning=placed('CR02_ScoutWarning',unreal.TextRenderActor,(-950,-250,190))
    warning.text_render.set_text('ASH WARDEN SCOUTS AHEAD\nUse cover. The north rail line offers a way around.')
    warning.text_render.set_world_size(24); warning.set_actor_rotation(unreal.Rotator(pitch=0,yaw=180,roll=0),False)
    assert levels.set_current_level_by_name('L_CH01_Persistent')
    assert levels.save_all_dirty_levels()
    # Navigation bounds requests are processed by the native nav-system tick,
    # not synchronously inside spawn_actor_from_class. Observe actual data.
    nav_started=time.monotonic()
    def finish_navigation(delta):
        recasts=[a for a in actors.get_all_level_actors() if isinstance(a,unreal.RecastNavMesh)]
        if not recasts:
            if time.monotonic()-nav_started>30:
                unreal.log_error('CR02_NAV_BLOCKED: no native Recast data after bounds registration')
                unreal.unregister_slate_post_tick_callback(nav_callback); unreal.SystemLibrary.quit_editor()
            return
        for recast in recasts:
            recast.set_editor_property('runtime_generation',unreal.RuntimeGenerationType.DYNAMIC)
            recast.set_editor_property('force_rebuild_on_load',True)
        assert levels.save_all_dirty_levels()
        inventory=[dict(label=a.get_actor_label(),cls=a.get_class().get_path_name(),level=a.get_level().get_outer().get_name()) for a in actors.get_all_level_actors()]
        (out/'encounter-assets.json').write_text(json.dumps(inventory,indent=2))
        unreal.log('CR02_ENCOUNTER_ASSETS_PASS two scouts, ammo, bounds and warning; native recast='+str(len(recasts)))
        unreal.unregister_slate_post_tick_callback(nav_callback); unreal.SystemLibrary.quit_editor()
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    nav_callback=unreal.register_slate_post_tick_callback(finish_navigation)
else:
    unreal.SystemLibrary.quit_editor()
