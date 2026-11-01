"""Observed visual corrections only: cabinet facing, task light, one animation reimport.
Then render four actual UE poses from the runtime workbench camera, without saving preview pose.
"""
import unreal,json,time,traceback
from pathlib import Path
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05';assets=unreal.EditorAssetLibrary
path='/Game/Generated/Phase05/Animation/AN_CR05_RookRestoration';anim=assets.load_asset(path);assert anim and assets.get_metadata_tag(anim,'CR.GeneratedBy')=='CinderRelay.Phase05.v1'
manager=unreal.InterchangeManager.get_interchange_manager_scripted();params=unreal.ImportAssetParameters();params.is_automated=True;params.follow_redirectors=True;params.replace_existing=True
if '-cr05reviewonly' not in unreal.SystemLibrary.get_command_line().lower():
 result=manager.reimport_asset(anim,params);assert result is not None and result is not False;assert assets.save_loaded_asset(anim)
assert abs(anim.sequence_length-22)<.05
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent');existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
for x in(5750,6050,6350,6650):
 a=existing['CR05_BunkerRack'+str(x)];a.modify();a.set_actor_rotation(unreal.Rotator(yaw=90),False)
for i in range(4):
 a=existing['CR05_WorkshopCabinet'+str(i)];a.modify();a.set_actor_rotation(unreal.Rotator(yaw=180),False)
assert levels.set_current_level_by_name('L_CH01_Workshop')
name='CR05_CalibrationTaskLight';a=existing.get(name)
if not a:a=actors.spawn_actor_from_class(unreal.PointLight,unreal.Vector(2240,-350,235));a.set_actor_label(name);a.tags=['CR_Phase05_Generated']
else:assert 'CR_Phase05_Generated' in [str(t) for t in a.tags]
a.modify();lc=a.light_component;lc.set_mobility(unreal.ComponentMobility.MOVABLE);lc.set_intensity_units(unreal.LightUnits.LUMENS);lc.set_intensity(320);lc.set_light_color(unreal.LinearColor(1,.76,.50));lc.set_editor_property('attenuation_radius',330);lc.set_editor_property('source_radius',14);lc.set_editor_property('cast_shadows',False)
for n in ('CR_PowerModule','CR_RelayTerminal','CR_SignalConsole'):
 a=existing[n];a.modify();a.presentation_mesh.set_collision_profile_name('NoCollision');a.presentation_mesh.set_editor_property('can_ever_affect_navigation',False)
assert levels.save_all_dirty_levels()
(out/'visual-corrections.json').write_text(json.dumps({'animation_reimport':path,'duration':anim.sequence_length,'cabinet_yaw':180,'rack_yaw':90,'axis_observation':'FBX handedness mirrors Y; authored cabinet -Y face imports as +Y','task_light_lumens':320},indent=2))
# Unsaved review poses; real Editor camera and imported animation, not gameplay validation.
bench=existing['CR03_CalibrationWorkbench'];hands=bench.hands;hands.set_visibility(True);hands.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE);hands.set_animation(anim);hands.set_update_animation_in_editor(True);hands.stop()
camera=actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(2238,-350,166));camera.set_actor_rotation(unreal.Rotator(pitch=-48),False);camera.camera_component.set_field_of_view(bench.camera.field_of_view);actors.clear_actor_selection_set()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));old=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
times=[3.,7.,13.,18.];i=0;task=None;began=time.monotonic();changed=began;receipt=[];handle=None
hands.set_position(times[i],False);unreal.EditorPythonScripting.set_keep_python_script_alive(True)
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',old);unreal.unregister_slate_post_tick_callback(handle);(out/'contact-render-review.json').write_text(json.dumps({'frames':receipt,'error':error,'temporal_motion_acceptance':False},indent=2));unreal.log('CR05_CONTACT_RENDER '+str(error or 'PASS'));unreal.SystemLibrary.quit_editor()
def tick(delta):
 global i,task,changed
 try:
  if time.monotonic()-began>90:raise RuntimeError('Bounded contact-render timeout')
  if task and task.is_task_done():
   target=out/('assembly-contact-'+str(int(times[i]))+'.png');assert target.exists() and target.stat().st_size>10000
   receipt.append({'seconds':times[i],'path':str(target)});i+=1;task=None
   if i==len(times):finish();return
   hands.set_position(times[i],False);changed=time.monotonic()
  elif not task and time.monotonic()-changed>5:
   task=unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(out/('assembly-contact-'+str(int(times[i]))+'.png')),camera=camera,force_game_view=True);assert task.is_valid_task()
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick)
