"""One bounded actual-input Editor route with existing restoration acceptance.
Copies evidence into Phase05; never writes player saves or claims human pacing.
"""
import unreal,time,json,shutil,traceback
from pathlib import Path
assert '-CRRestorationCheck' in unreal.SystemLibrary.get_command_line()
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05/editor-smoke';out.mkdir(parents=True,exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
source=Path(unreal.Paths.project_saved_dir())/'Phase03';receipt=source/'acceptance.json';old=receipt.stat().st_mtime_ns if receipt.exists() else None
if source.exists():
 backup=out/'previous-receipts';backup.mkdir(exist_ok=True)
 for file in source.glob('*'):
  if file.is_file() and not (backup/file.name).exists():shutil.copy2(file,backup/file.name)
started=time.monotonic();ending=False;handle=None;observed=[];last_sample=0
def supervise(delta):
 global ending,last_sample
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
 if world and time.monotonic()-last_sample>.25:
  last_sample=time.monotonic()
  for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.CRZonePresentation):
   observed.append({'elapsed':last_sample-started,'light_intensity':a.status_light.intensity,'objective':str(unreal.GameplayStatics.get_game_mode(world).get_objective())})
 if not ending and receipt.exists() and receipt.stat().st_mtime_ns!=old:
  unreal.log('CR05_EDITOR_ROUTE_RECEIPT '+receipt.read_text(encoding='utf-8-sig'));ending=True;levels.editor_request_end_play()
 if not ending and time.monotonic()-started>630:
  unreal.log_error('CR05_EDITOR_ROUTE_TIMEOUT');ending=True;levels.editor_request_end_play()
 if ending and not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world():
  (out/'native-light-timeline.json').write_text(json.dumps(observed,indent=2))
  for file in source.glob('*'):
   if file.is_file():shutil.copy2(file,out/file.name)
  settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
unreal.EditorPythonScripting.set_keep_python_script_alive(True);handle=unreal.register_slate_post_tick_callback(supervise);levels.editor_request_begin_play()
