"""Real Unreal Editor renders, bounded camera samples; not gameplay acceptance.
No map/asset saves. Render warm-up does not stand in for streaming readiness.
"""
import json,time,traceback
from pathlib import Path
import unreal
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
old_throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
camera=actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(-1710,-60,165));camera.camera_component.set_field_of_view(85)
actors.clear_actor_selection_set()
shots=[('yard-representative',(-1710,-60,165),(-2,7,0))]
if '-cr05capture=all' in unreal.SystemLibrary.get_command_line().lower():
 shots += [('workshop-representative',(1950,130,155),(-3,-12,0)),('bunker-representative',(5520,100,-440),(-2,-5,0))]
started=time.monotonic();stage_started=started;index=0;task=None;receipt=[];handle=None
def setup():
 global stage_started
 _,loc,r=shots[index];camera.set_actor_location(unreal.Vector(*loc),False,False);camera.set_actor_rotation(unreal.Rotator(pitch=r[0],yaw=r[1],roll=r[2]),False)
 editor.set_level_viewport_camera_info(unreal.Vector(*loc),unreal.Rotator(pitch=r[0],yaw=r[1],roll=r[2]));stage_started=time.monotonic()
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',old_throttle)
 unreal.unregister_slate_post_tick_callback(handle)
 (out/'render-review.json').write_text(json.dumps({'actual_unreal_renders':receipt,'error':error,'gameplay_acceptance':False},indent=2),encoding='utf-8')
 if error:unreal.log_error('CR05_RENDER_FAIL '+error)
 else:unreal.log('CR05_RENDER_PASS '+str(receipt))
 unreal.SystemLibrary.quit_editor()
def tick(delta):
 global index,task
 try:
  if time.monotonic()-started>120:raise RuntimeError('Bounded render capture timeout')
  if task:
   if not task.is_task_done():return
   path=out/(shots[index][0]+'.png');assert path.exists() and path.stat().st_size>10000,'No actual rendered image'
   receipt.append({'path':str(path),'camera_cm':shots[index][1],'fov':85,'resolution':[1920,1080]});index+=1;task=None
   if index==len(shots):finish();return
   setup()
  elif time.monotonic()-stage_started>8:
   task=unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(out/(shots[index][0]+'.png')),camera=camera,force_game_view=True)
   assert task and task.is_valid_task(),'Native screenshot task rejected'
 except Exception:finish(traceback.format_exc())
setup();handle=unreal.register_slate_post_tick_callback(tick)
