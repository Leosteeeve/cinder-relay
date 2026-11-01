"""Import only Phase05 authored presentation assets and configure existing owners.
Requires compiled Phase05 runtime. Never regenerates existing gameplay actors/maps.
"""
import json
from pathlib import Path
import unreal
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05';exports=out/'exports'
root='/Game/Generated/Phase05';owner='CinderRelay.Phase05.v1';tag='CR_Phase05_Generated'
assets=unreal.EditorAssetLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools();lib=unreal.MaterialEditingLibrary
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def owned(path):
 a=assets.load_asset(path) if assets.does_asset_exist(path) else None
 if a:assert assets.get_metadata_tag(a,'CR.GeneratedBy')==owner,path
 return a
def save(a):assets.set_metadata_tag(a,'CR.GeneratedBy',owner);assert assets.save_loaded_asset(a);return a
def create(n,folder,cls,factory):return owned(root+'/'+folder+'/'+n) or save(tools.create_asset(n,root+'/'+folder,cls,factory))
master=assets.load_asset(root+'/Materials/M_CR05_Surface');assert master
# Moving models use mesh UVs, not the environment's world-projected macro texture.
actor_master=owned(root+'/Materials/M_CR05_ActorSurface')
if not actor_master:
 actor_master=assets.duplicate_asset(master.get_path_name(),root+'/Materials/M_CR05_ActorSurface');assert actor_master
 sample=lib.create_material_expression(actor_master,unreal.MaterialExpressionTextureSampleParameter2D);sample.set_editor_property('parameter_name','SurfaceMask');sample.set_editor_property('texture',assets.load_asset(root+'/Textures/T_CR05_SurfaceMask'));sample.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
 color=lib.create_material_expression(actor_master,unreal.MaterialExpressionVectorParameter);color.set_editor_property('parameter_name','SurfaceColor');color.set_editor_property('default_value',unreal.LinearColor(.2,.2,.2,1))
 multiply=lib.create_material_expression(actor_master,unreal.MaterialExpressionMultiply);assert lib.connect_material_expressions(sample,'R',multiply,'A');assert lib.connect_material_expressions(color,'',multiply,'B');assert lib.connect_material_property(multiply,'',unreal.MaterialProperty.MP_BASE_COLOR);lib.recompile_material(actor_master);save(actor_master)
palette={'CR03_Graphite':((.16,.20,.23),.7,.42),'CR03_Amber':((.55,.28,.08),.45,.52),'CR03_Glove':((.115,.125,.11),0,.8),'CR03_Cuff':((.23,.25,.22),0,.85),'CR03_Lens':((.025,.45,.43),.35,.24),'CR03_Bench':((.13,.20,.22),.5,.68),
 'CR05_WardenCloth':((.115,.145,.14),0,.88),'CR05_WardenArmor':((.13,.18,.20),.45,.54),'CR05_WardenLeather':((.055,.046,.035),0,.8),'CR05_WardenVisor':((.055,.08,.08),.7,.24),'CR05_WardenRust':((.28,.14,.065),.35,.75),'CR05_WardenBand':((.51,.32,.13),.1,.7)}
materials={}
for n,(color,metal,rough) in palette.items():
 m=create('MI_CR05_'+n,'Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew());lib.set_material_instance_parent(m,actor_master)
 lib.set_material_instance_vector_parameter_value(m,'SurfaceColor',unreal.LinearColor(*color,1));lib.set_material_instance_scalar_parameter_value(m,'Metallic',metal);lib.set_material_instance_scalar_parameter_value(m,'Roughness',rough);lib.set_material_instance_scalar_parameter_value(m,'Emissive',.5 if n=='CR03_Lens' else 0);lib.update_material_instance(m);save(m);materials[n]=m
def fbx(name,skeletal=False,skeleton=None):
 folder='Animation' if skeletal or skeleton else 'Meshes';path=root+'/'+folder+'/'+name
 obj=owned(path)
 if obj:return obj
 ui=unreal.FbxImportUI();ui.automated_import_should_detect_type=False;ui.import_mesh=skeleton is None;ui.import_as_skeletal=skeletal or skeleton is not None;ui.import_animations=skeletal or skeleton is not None;ui.import_materials=False;ui.import_textures=False;ui.create_physics_asset=False
 ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION if skeleton else unreal.FBXImportType.FBXIT_SKELETAL_MESH if skeletal else unreal.FBXImportType.FBXIT_STATIC_MESH
 if skeleton:ui.skeleton=skeleton
 data=ui.skeletal_mesh_import_data if skeletal else ui.static_mesh_import_data;data.convert_scene=True;data.convert_scene_unit=True;data.force_front_x_axis=False
 if not skeletal:data.combine_meshes=True;data.auto_generate_collision=False
 if skeletal or skeleton:ui.anim_sequence_import_data.set_editor_property('use_default_sample_rate',True)
 task=unreal.AssetImportTask();task.filename=str(exports/(name+'.fbx'));task.destination_path=root+'/'+folder;task.destination_name=name;task.options=ui;task.automated=True;task.save=True;tools.import_asset_tasks([task]);assert task.imported_object_paths,name
 for ap in task.imported_object_paths:save(assets.load_asset(ap))
 obj=assets.load_asset(path)
 if skeleton and not isinstance(obj,unreal.AnimSequence):
  candidates=[assets.load_asset(ap) for ap in task.imported_object_paths if isinstance(assets.load_asset(ap),unreal.AnimSequence)];assert len(candidates)==1;assert assets.rename_asset(candidates[0].get_path_name(),path);obj=assets.load_asset(path)
 assert obj,name
 if not skeleton:
  slots=list(obj.get_editor_property('materials' if skeletal else 'static_materials'))
  for slot in slots:
   key=str(slot.get_editor_property('imported_material_slot_name'));assert key in materials,key;slot.set_editor_property('material_interface',materials[key])
  obj.set_editor_property('materials' if skeletal else 'static_materials',slots);save(obj)
 return obj
rook=fbx('SM_CR05_Rook5');optic=fbx('SM_CR05_SurveyOptic');warden=fbx('SK_CR05_AshWarden',True);restoration=fbx('SK_CR05_Restoration',True)
def find_animation(mesh,name):
 target=root+'/Animation/'+name;found=owned(target)
 if found:return found
 candidates=[assets.load_asset(ap) for ap in assets.list_assets(root+'/Animation') if isinstance(assets.load_asset(ap),unreal.AnimSequence) and assets.load_asset(ap).get_editor_property('skeleton')==mesh.get_editor_property('skeleton')]
 assert len(candidates)==1,[a.get_name() for a in candidates]
 assert assets.rename_asset(candidates[0].get_path_name(),target);return save(assets.load_asset(target))
idle=find_animation(warden,'AN_CR05_Warden_Idle');assembly=find_animation(restoration,'AN_CR05_RookRestoration')
assert abs(assembly.sequence_length-22)<.05
animations={'Idle':idle}
for action in ('Walk','Alert','Attack','Hit','Death'):animations[action]=fbx('AN_CR05_Warden_'+action,skeleton=warden.get_editor_property('skeleton'))
sounds={}
for spec in json.loads((exports/'audio-manifest.json').read_text()):
 n=spec['name'];sound=owned(root+'/Audio/'+n)
 if not sound:
  task=unreal.AssetImportTask();task.filename=str(exports/(n+'.wav'));task.destination_path=root+'/Audio';task.destination_name=n;task.automated=True;task.save=True;tools.import_asset_tasks([task]);sound=assets.load_asset(root+'/Audio/'+n);assert sound
 sound.set_editor_property('looping',spec['loop']);save(sound);sounds[n.removeprefix('S_CR05_')]=sound
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent');existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
def actor(label,cls,zone,loc):
 a=existing.get(label)
 if a:assert tag in [str(t) for t in a.tags] and isinstance(a,cls)
 else:
  assert levels.set_current_level_by_name('L_CH01_'+zone);a=actors.spawn_actor_from_class(cls,unreal.Vector(*loc));a.set_actor_label(label);a.tags=[tag];existing[label]=a
 a.modify();return a
for name in ('CR02_Scout_1','CR02_Scout_2'):
 a=existing[name];a.modify();a.mesh.set_skeletal_mesh_asset(warden);a.mesh.set_relative_location(unreal.Vector(0,0,-90),False,False);a.mesh.set_relative_rotation(unreal.Rotator(),False,False);a.mesh.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);a.mesh.set_editor_property('can_ever_affect_navigation',False)
 for key,anim in animations.items():a.set_editor_property(key.lower()+'_animation',anim)
 a.set_editor_property('shot_sound',sounds['RookShot']);a.set_editor_property('hit_sound',sounds['Impact']);a.mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE);a.mesh.set_animation(idle)
 # Editor render visibility only; runtime BeginPlay independently selects the valid skeletal path.
 for c in a.silhouette.get_children_components(True):
  if isinstance(c,unreal.StaticMeshComponent):c.set_visibility(False)
bench=existing['CR03_CalibrationWorkbench'];bench.modify();bench.hands.set_skeletal_mesh_asset(restoration);bench.set_editor_property('assembly_mesh',restoration);bench.set_editor_property('activation_sound',sounds['Calibration'])
for i in range(bench.surface.get_num_materials()):
 n=str(bench.surface.get_editor_property('static_mesh').get_editor_property('static_materials')[i].get_editor_property('imported_material_slot_name'))
 if n in materials:bench.surface.set_material(i,materials[n])
sequence=create('LS_CR05_RookRestoration','Sequences',unreal.LevelSequence,unreal.LevelSequenceFactoryNew());sequence.set_display_rate(unreal.FrameRate(30,1));sequence.set_playback_start(0);sequence.set_playback_end(660)
if not sequence.get_bindings():
 binding=sequence.add_possessable(bench);unreal.MovieSceneBindingTagExtensions.tag_binding(binding,'CR03_Hands');track=binding.add_track(unreal.MovieSceneSkeletalAnimationTrack);section=track.add_section();section.set_range(0,660);params=section.get_editor_property('params');params.animation=assembly;section.set_editor_property('params',params);section.set_completion_mode(unreal.MovieSceneCompletionMode.RESTORE_STATE)
save(sequence);bench.set_editor_property('sequence',sequence)
# Native spatial ambient owners live in their zones. No persistent references between zones.
for zone,loc,sound,volume,radius in [('RailYard',(-300,0,260),'YardWind',.10,1600),('Workshop',(2700,0,260),'WorkshopHum',.07,600),('RelayBunker',(6300,300,-350),'BunkerHum',.09,650)]:
 a=actor('CR05_Ambience_'+zone,unreal.AmbientSound,zone,loc);c=a.audio_component;c.set_sound(sounds[sound]);c.set_volume_multiplier(volume);c.set_editor_property('auto_activate',True)
 settings=unreal.SoundAttenuationSettings();settings.set_editor_property('attenuate',True);settings.set_editor_property('spatialize',True);settings.set_editor_property('attenuation_shape_extents',unreal.Vector(radius,0,0));settings.set_editor_property('falloff_distance',550.0);settings.set_editor_property('enable_occlusion',True);settings.set_editor_property('occlusion_volume_attenuation',.35);c.set_editor_property('override_attenuation',True);c.set_editor_property('attenuation_overrides',settings)
presentation=actor('CR05_RelayPresentation',unreal.CRZonePresentation,'RelayBunker',(6700,-180,-360))
for n,model in [('CR_PowerModule','PowerUnit'),('CR_RelayTerminal','RelayTerminal'),('CR_SignalConsole','RelayTerminal')]:
 a=existing[n];a.modify();m=assets.load_asset(root+'/Meshes/SM_CR05_'+model);assert m
 a.presentation_mesh.set_static_mesh(m);a.presentation_mesh.set_collision_profile_name('NoCollision');a.presentation_mesh.set_editor_property('can_ever_affect_navigation',False);a.mesh.set_visibility(False)
for x in(5750,6050,6350,6650):
 a=existing['CR05_BunkerRack'+str(x)];a.modify();a.set_actor_rotation(unreal.Rotator(yaw=90),False)
for i in range(4):
 a=existing['CR05_WorkshopCabinet'+str(i)];a.modify();a.set_actor_rotation(unreal.Rotator(yaw=180),False)
for n in ('CR_WorkbenchLabel','CR03_BenchSign','CR05_BunkerNine','CR_RelayLabel','CR_SignalLabel'):
 if n in existing:existing[n].modify();existing[n].set_actor_hidden_in_game(True)
for n in ('CR_WorkshopRear-440','CR_WorkshopRear440','CR_WorkshopLintelRear'):
 a=existing[n];a.modify();a.static_mesh_component.set_material(0,assets.load_asset(root+'/Materials/MI_CR05_Paint'))
for suffix,duration,sound,keys in [('RelayPower',4,'PowerRise',[(0,0),(8,80),(13,0),(30,180),(37,20),(70,400),(120,500)]),('RelayEnding',8,'SignalEnding',[(0,500),(50,700),(80,300),(105,650),(125,80),(138,550),(160,180),(180,600),(240,500)])]:
 seq=create('LS_CR05_'+suffix,'Sequences',unreal.LevelSequence,unreal.LevelSequenceFactoryNew());seq.set_display_rate(unreal.FrameRate(30,1));seq.set_playback_start(0);seq.set_playback_end(duration*30)
 if not seq.get_bindings():
  binding=seq.add_possessable(presentation);unreal.MovieSceneBindingTagExtensions.tag_binding(binding,'CR05_Presentation')
  child=seq.add_possessable(presentation.status_light);child.set_parent(binding);track=child.add_track(unreal.MovieSceneFloatTrack);track.set_property_name_and_path('Intensity','Intensity');section=track.add_section();section.set_range(0,duration*30);section.set_completion_mode(unreal.MovieSceneCompletionMode.KEEP_STATE)
  channel=section.get_all_channels()[0]
  for frame,value in keys:channel.add_key(unreal.FrameNumber(frame),value,interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
  track=binding.add_track(unreal.MovieSceneAudioTrack);section=track.add_section();section.set_range(0,duration*30);section.set_sound(sounds[sound]);section.set_completion_mode(unreal.MovieSceneCompletionMode.RESTORE_STATE)
 save(seq);presentation.set_editor_property('power_sequence' if suffix=='RelayPower' else 'ending_sequence',seq)
weapon=assets.load_asset('/Game/Generated/Phase02/Data/DA_Rook5');assert weapon
balance_names=('magazine_capacity','initial_reserve','shot_interval','reload_duration','body_damage','head_multiplier','range','aim_fov');balance={n:weapon.get_editor_property(n) for n in balance_names}
for prop,key in [('shot_sound','RookShot'),('impact_sound','Impact'),('hit_sound','Impact'),('reload_sound','Reload')]:weapon.set_editor_property(prop,sounds[key])
assert balance=={n:weapon.get_editor_property(n) for n in balance_names};assets.save_loaded_asset(weapon)
bp=assets.load_asset('/Game/Generated/Phase02/Blueprints/BP_CRCombatCharacter');assert bp;cdo=unreal.get_default_object(bp.generated_class());cdo.set_editor_property('yard_footstep',sounds['FootYard']);cdo.set_editor_property('interior_footstep',sounds['FootMetal']);cdo.weapon_view.set_editor_property('rook_appearance',rook);cdo.weapon_view.set_editor_property('survey_appearance',optic);unreal.BlueprintEditorLibrary.compile_blueprint(bp);assets.save_loaded_asset(bp)
assert levels.save_all_dirty_levels()
receipt={'warden':warden.get_path_name(),'actions':{n:{'path':a.get_path_name(),'seconds':a.sequence_length} for n,a in animations.items()},'restoration':assembly.get_path_name(),'restoration_seconds':assembly.sequence_length,'hands_bones':bench.hands.get_num_bones(),'warden_bones':existing['CR02_Scout_1'].mesh.get_num_bones(),'audio':{n:a.get_path_name() for n,a in sounds.items()},'balance_unchanged':balance,'actors_added':[n for n in existing if n.startswith('CR05_')],'assets':list(assets.list_assets(root,recursive=True))}
(out/'presentation-assets.json').write_text(json.dumps(receipt,indent=2));unreal.log('CR05_PRESENTATION_ASSETS_PASS '+str(receipt['hands_bones']));unreal.SystemLibrary.quit_editor()
