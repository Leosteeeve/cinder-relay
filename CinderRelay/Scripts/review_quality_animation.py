"""Eight genuine UE-rendered poses with the actual workbench camera; no map saves.
This is pose/contact inspection, explicitly not proof of continuous motion quality.
"""
import unreal,time,json,traceback
from pathlib import Path
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05-1/animation-review';out.mkdir(parents=True,exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
bench=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.CRWorkbench))
mesh=unreal.EditorAssetLibrary.load_asset('/Game/Generated/Phase051/Animation/SK_CR051_Restoration');assert mesh;bench.hands.set_skeletal_mesh_asset(mesh);bench.hands.set_visibility(True)
bench.hands.set_editor_property('override_materials',[])
anim=unreal.EditorAssetLibrary.load_asset('/Game/Generated/Phase051/Animation/AN_CR051_RookRestoration');assert anim
bench.hands.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE);bench.hands.set_animation(anim);bench.hands.set_update_animation_in_editor(True);bench.hands.set_component_tick_enabled(True);bench.hands.play(False);bench.hands.set_play_rate(0)
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
camera=actors.spawn_actor_from_class(unreal.CameraActor,bench.camera.get_world_location());camera.set_actor_rotation(bench.camera.get_world_rotation(),False);camera.camera_component.set_field_of_view(bench.camera.field_of_view);actors.clear_actor_selection_set()
times=[1.5,3.2,5.6,7.2,10.5,13.7,16.6,20.2];index=0;task=None;handle=None;started=time.monotonic();changed=started;receipt=[]
def setup():
 global changed
 bench.hands.set_position(times[index],False);changed=time.monotonic()
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.unregister_slate_post_tick_callback(handle);(out/'review.json').write_text(json.dumps({'frames':receipt,'error':error,'continuous_playback_review':False},indent=2));unreal.log('CR051_ANIMATION_REVIEW '+str(error or 'PASS'));unreal.SystemLibrary.quit_editor()
def tick(delta):
 global index,task
 try:
  if time.monotonic()-started>160:raise RuntimeError('Bounded pose review timeout')
  if task and task.is_task_done():
   file=out/('frame-'+str(index)+'.png');assert file.exists() and file.stat().st_size>10000;receipt.append({'seconds':times[index],'path':str(file),'camera':str(camera.get_actor_transform()),'fov':camera.camera_component.field_of_view,'hand_R':str(bench.hands.get_socket_location('hand_R')),'optic':str(bench.hands.get_socket_location('optic'))});index+=1;task=None
   if index==len(times):finish();return
   setup()
  elif not task and time.monotonic()-changed>5:task=unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(out/('frame-'+str(index)+'.png')),camera=camera,force_game_view=True)
 except Exception:finish(traceback.format_exc())
unreal.EditorPythonScripting.set_keep_python_script_alive(True);setup();handle=unreal.register_slate_post_tick_callback(tick)
