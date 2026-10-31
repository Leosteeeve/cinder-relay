"""Open the actual persistent world and begin PIE with -CRStreamAcceptance.

The opt-in native Development runner drives Enhanced Input and checks streaming,
backtracking, objectives, failure/retry, and restart. It exits its own process.
No Editor scripting dependency is carried into the packaged game.
"""
import unreal
from collections import Counter
from pathlib import Path
import json
import time

assert '-CRStreamAcceptance' in unreal.SystemLibrary.get_command_line()
performance = unreal.get_default_object(unreal.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
original_throttle = performance.get_editor_property('bThrottleCPUWhenNotForeground')
performance.set_editor_property('bThrottleCPUWhenNotForeground', False)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
owned = [a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
         if 'CR_Phase01A_Generated' in [str(t) for t in a.tags]]
assert len(owned) == 155
assert Counter(a.get_level().get_outer().get_name() for a in owned) == {
    'L_CH01_Persistent': 15, 'L_CH01_RailYard': 86,
    'L_CH01_Workshop': 22, 'L_CH01_RelayBunker': 32}
unreal.log('CR_ASSET_REOPEN_PASS 155 original actors, four registered worlds')
del owned
receipt = Path(unreal.Paths.project_saved_dir()) / 'Phase01B/acceptance.json'
previous_mtime = receipt.stat().st_mtime_ns if receipt.exists() else None
ending = False
started = time.monotonic()


def supervise(delta):
    global ending
    if not ending and receipt.exists() and receipt.stat().st_mtime_ns != previous_mtime:
        result = json.loads(receipt.read_text(encoding='utf-8-sig'))
        unreal.log('CR_EDITOR_RECEIPT ' + json.dumps(result))
        ending = True
        levels.editor_request_end_play()
    if not ending and time.monotonic() - started > 390:
        unreal.log_error('CR_EDITOR_ACCEPTANCE_TIMEOUT: no fresh receipt; old result is invalid')
        ending = True
        levels.editor_request_end_play()
    if ending and not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world():
        performance.set_editor_property('bThrottleCPUWhenNotForeground', original_throttle)
        unreal.unregister_slate_post_tick_callback(callback)
        unreal.SystemLibrary.quit_editor()


unreal.EditorPythonScripting.set_keep_python_script_alive(True)
callback = unreal.register_slate_post_tick_callback(supervise)
levels.editor_request_begin_play()
