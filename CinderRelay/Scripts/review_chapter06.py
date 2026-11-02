"""Native Editor screenshots. Transient camera only; never saves preview state."""
import unreal,time,json,traceback
from pathlib import Path
out=Path(unreal.Paths.project_dir()).parent/'.environment-local/phase-06/visuals-integrated';out.mkdir(parents=True,exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
shots=[('yard-approach',(-1450,0,165),(-2,0,0)),('mechanical-door',(1250,-40,165),(4,4,0)),
       ('workshop-diagnostic',(2400,0,165),(0,65,0)),('diagnostic-control',(2110,260,160),(0,90,0)),
       ('relay-machinery',(5100,-40,-335),(-5,0,0)),('service-walk',(5820,-430,-435),(-5,35,0))]
camera=actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(*shots[0][1]));camera.camera_component.set_field_of_view(85)
actors.clear_actor_selection_set()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
old=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
started=time.monotonic();changed=started;index=0;task=None;handle=None;receipt=[]
def setup():
    global changed
    _,loc,r=shots[index];camera.set_actor_location(unreal.Vector(*loc),False,False);camera.set_actor_rotation(unreal.Rotator(pitch=r[0],yaw=r[1],roll=r[2]),False);changed=time.monotonic()
def finish(error=None):
    settings.set_editor_property('bThrottleCPUWhenNotForeground',old);unreal.unregister_slate_post_tick_callback(handle)
    (out/'editor-frames.json').write_text(json.dumps(dict(frames=receipt,error=error,gameplay_acceptance=False),indent=2));unreal.log('CR06_CAPTURE '+str(error or 'PASS'));unreal.SystemLibrary.quit_editor()
def tick(delta):
    global index,task
    try:
        if time.monotonic()-started>150:raise RuntimeError('Bounded capture timeout')
        if task and task.is_task_done():
            path=out/(shots[index][0]+'.png');assert path.exists() and path.stat().st_size>10000
            receipt.append(dict(path=str(path),camera=shots[index][1],rotation=shots[index][2]));index+=1;task=None
            if index==len(shots):finish();return
            setup()
        elif not task and time.monotonic()-changed>6:
            task=unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(out/(shots[index][0]+'.png')),camera=camera,force_game_view=True);assert task and task.is_valid_task()
    except Exception:finish(traceback.format_exc())
unreal.EditorPythonScripting.set_keep_python_script_alive(True);setup();handle=unreal.register_slate_post_tick_callback(tick)
