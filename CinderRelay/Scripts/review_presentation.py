"""Phase052 native before/after audit and rendered samples; never saves preview state."""
import ast, json, time, traceback
from pathlib import Path
import unreal

p = Path(unreal.Paths.project_dir())
out = p.parent / '.environment-local/phase-05-2'
out.mkdir(parents=True, exist_ok=True)
after = '-cr052after' in unreal.SystemLibrary.get_command_line().lower()
prefix = 'after' if after else 'before'
if not after and any(out.glob('before-*')):
    raise FileExistsError('Original before evidence already exists; preserve it. Use -CR052After for current-map review.')
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
scope = {'unreal': unreal}
tree = ast.parse((p/'Scripts/migrate_streaming.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('vector','transform','snapshot')], type_ignores=[]), 'snapshot', 'exec'), scope)
records = {}
lighting = {}
for a in actors.get_all_level_actors():
    r = scope['snapshot'](a)
    r['level'] = a.get_level().get_outer().get_name()
    r['hidden'] = a.get_editor_property('hidden')
    r['bounds'] = str(a.get_actor_bounds(False))
    records[a.get_actor_label()] = r
    if isinstance(a, unreal.PostProcessVolume):
        s = a.get_editor_property('settings')
        lighting[a.get_actor_label()] = {n: str(s.get_editor_property(n)) for n in (
            'auto_exposure_min_brightness','auto_exposure_max_brightness','auto_exposure_bias',
            'override_auto_exposure_min_brightness','override_auto_exposure_max_brightness',
            'local_exposure_shadow_contrast_scale','local_exposure_highlight_contrast_scale')}
(out/(prefix+'-inventory.json')).write_text(json.dumps({'actors':records,'lighting':lighting}, indent=2))
shots = [('spawn',(-1710,-60,165),(-2,7,0)),
         ('train-route',(-650,430,165),(-2,38,0)),
         ('workshop-entrance',(1120,0,165),(-2,0,0)),
         ('workshop-interior',(1950,100,165),(-3,-15,0)),
         ('shadow-flank',(-950,1150,165),(-3,-5,0)),
         ('midground',(700,500,165),(10,65,0))]
camera = actors.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*shots[0][1]))
camera.camera_component.set_field_of_view(85)
actors.clear_actor_selection_set()
settings = unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
old = settings.get_editor_property('bThrottleCPUWhenNotForeground')
settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
started = time.monotonic(); changed = started; index = 0; task = None; handle = None; receipt = []
def setup():
    global changed
    _,loc,r = shots[index]
    camera.set_actor_location(unreal.Vector(*loc),False,False)
    camera.set_actor_rotation(unreal.Rotator(pitch=r[0],yaw=r[1],roll=r[2]),False)
    changed = time.monotonic()
def finish(error=None):
    settings.set_editor_property('bThrottleCPUWhenNotForeground',old)
    unreal.unregister_slate_post_tick_callback(handle)
    (out/(prefix+'-frames.json')).write_text(json.dumps({'frames':receipt,'error':error,'gameplay_test':False},indent=2))
    unreal.log('CR052_CAPTURE '+str(error or 'PASS'))
    unreal.SystemLibrary.quit_editor()
def tick(delta):
    global index,task
    try:
        if time.monotonic()-started>180: raise RuntimeError('Bounded render timeout')
        if task and task.is_task_done():
            path = out/(prefix+'-'+shots[index][0]+'.png')
            assert path.exists() and path.stat().st_size>10000
            receipt.append({'path':str(path),'camera_cm':shots[index][1],'rotation':shots[index][2],'fov':85})
            index += 1; task = None
            if index==len(shots): finish(); return
            setup()
        elif not task and time.monotonic()-changed>6:
            task=unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(out/(prefix+'-'+shots[index][0]+'.png')),camera=camera,force_game_view=True)
            assert task and task.is_valid_task()
    except Exception: finish(traceback.format_exc())
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
setup(); handle=unreal.register_slate_post_tick_callback(tick)
