"""Twelve native first-person pose captures, no map saves or transaction commits.
Static samples are not proof of smooth temporal animation; record playback separately.
"""
import unreal,time,json,traceback,uuid
from pathlib import Path
project=Path(unreal.Paths.project_dir());out=project.parent/'.environment-local/phase-05-3/workbench-review'/uuid.uuid4().hex[:10];out.mkdir(parents=True,exist_ok=False)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assets=unreal.EditorAssetLibrary
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
bench=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.CRWorkbench));component=bench.hands
component.set_skeletal_mesh_asset(assets.load_asset('/Game/Generated/Phase053/Assembly/Animation/SK_CR053_Restoration'));component.set_editor_property('override_materials',[]);component.set_visibility(True)
component.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE);component.set_animation(assets.load_asset('/Game/Generated/Phase053/Assembly/Animation/AN_CR053_RookRestoration'));component.set_update_animation_in_editor(True);component.set_component_tick_enabled(True);component.play(False);component.set_play_rate(0)
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
camera=actors.spawn_actor_from_class(unreal.CameraActor,bench.get_actor_location()+unreal.Vector(-66,0,172));camera.set_actor_rotation(unreal.Rotator(pitch=-58),False);camera.camera_component.set_field_of_view(66);actors.clear_actor_selection_set()
times=[6.4,11.55] if '-cr053contactonly' in unreal.SystemLibrary.get_command_line().lower() else [1.5,3.4,5.4,6.4,7.2,9.8,11.55,12.7,15.5,18.5,20.5,21.8]
index=0;task=None;busy=False;receipt=[];started=time.monotonic();changed=started
def setup():
 global changed
 component.set_position(times[index],False);changed=time.monotonic()
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.unregister_slate_post_tick_callback(handle)
 (out/'review.json').write_text(json.dumps({'frames':receipt,'error':error,'continuous_playback_review':False,'camera':'fixed representative settle -66,0,172 pitch -58 FOV66'},indent=2))
 unreal.log('CR053_HUMAN_REVIEW '+str(error or 'PASS')+' '+str(out));unreal.SystemLibrary.quit_editor()
def tick(delta):
 global index,task,busy
 if busy:return
 busy=True
 try:
  if time.monotonic()-started>210:raise RuntimeError('Bounded review timeout')
  if task and task.is_task_done():
   path=out/('frame-%02d.png'%index);assert path.exists() and path.stat().st_size>10000
   receipt.append({'seconds':times[index],'path':str(path),'camera':str(camera.get_actor_transform()),'hand_R':str(component.get_socket_location('hand_R')),'optic':str(component.get_socket_location('optic'))})
   index+=1;task=None
   if index==len(times):finish();return
   setup()
  elif not task and time.monotonic()-changed>4:
   task=unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(out/('frame-%02d.png'%index)),camera=camera,force_game_view=True)
 except Exception:finish(traceback.format_exc())
 finally:busy=False
unreal.EditorPythonScripting.set_keep_python_script_alive(True);setup();handle=unreal.register_slate_post_tick_callback(tick)
