"""One bounded integrated PIE route, supervised by a fresh native acceptance receipt."""
import unreal,time,json
from pathlib import Path
assert '-CRRestorationCheck' in unreal.SystemLibrary.get_command_line()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
bench=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if isinstance(a,unreal.CRWorkbench))
rig=bench.hands
(Path(unreal.Paths.project_dir()).parent/'.environment-local/phase-03/imported-rig.json').write_text(json.dumps({'bone_count':rig.get_num_bones(),'bones':[str(rig.get_bone_name(i)) for i in range(rig.get_num_bones())],'surface_collision':str(bench.surface.get_collision_enabled()),'native_box_extent':str(bench.interaction_bounds.get_unscaled_box_extent())},indent=2))
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
receipt=Path(unreal.Paths.project_saved_dir())/'Phase03/acceptance.json';old=receipt.stat().st_mtime_ns if receipt.exists() else None
started=time.monotonic();ending=False
def supervise(delta):
    global ending
    if not ending and receipt.exists() and receipt.stat().st_mtime_ns!=old:
        unreal.log('CR03_EDITOR_RECEIPT '+receipt.read_text(encoding='utf-8-sig'));ending=True;levels.editor_request_end_play()
    if not ending and time.monotonic()-started>630:
        unreal.log_error('CR03_EDITOR_TIMEOUT');ending=True;levels.editor_request_end_play()
    if ending and not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world():
        settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
unreal.EditorPythonScripting.set_keep_python_script_alive(True);handle=unreal.register_slate_post_tick_callback(supervise);levels.editor_request_begin_play()
