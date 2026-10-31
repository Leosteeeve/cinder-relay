"""Supervise one opt-in PIE combat check; a fresh receipt is mandatory."""
import unreal,json,time,runpy
from pathlib import Path
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if '-CRCombatCheck' in unreal.SystemLibrary.get_command_line():
    runpy.run_path(str(Path(unreal.Paths.project_dir())/'Scripts/audit_combat.py'))
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground'); settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
receipt=Path(unreal.Paths.project_saved_dir())/'Phase02/acceptance.json'
old=receipt.stat().st_mtime_ns if receipt.exists() else None
ending=False; started=time.monotonic()
def supervise(delta):
    global ending
    if not ending and receipt.exists() and receipt.stat().st_mtime_ns!=old:
        unreal.log('CR02_EDITOR_RECEIPT '+receipt.read_text(encoding='utf-8-sig')); ending=True; levels.editor_request_end_play()
    if not ending and time.monotonic()-started>420:
        unreal.log_error('CR02_EDITOR_TIMEOUT no fresh receipt'); ending=True; levels.editor_request_end_play()
    if ending and not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world():
        settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
        unreal.unregister_slate_post_tick_callback(handle); unreal.SystemLibrary.quit_editor()
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
handle=unreal.register_slate_post_tick_callback(supervise)
levels.editor_request_begin_play()
