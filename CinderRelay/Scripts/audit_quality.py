"""Read-only Phase05.1 baseline and matched in-engine environment captures."""
import ast,json,time,traceback
from pathlib import Path
import unreal
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05-1';out.mkdir(parents=True,exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
scope={'unreal':unreal};tree=ast.parse((p/'Scripts/migrate_streaming.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('vector','transform','snapshot')],type_ignores=[]),'snapshot','exec'),scope)
records={}
for a in actors.get_all_level_actors():
 r=scope['snapshot'](a);r['level']=a.get_level().get_outer().get_name();r['hidden']=a.get_editor_property('hidden');records[a.get_actor_label()]=r
before=out/'editor-baseline.json'
if not before.exists():before.write_text(json.dumps({'actors':records},indent=2))
assets=unreal.EditorAssetLibrary
rook=assets.load_asset('/Game/Generated/Phase05/Meshes/SM_CR05_Rook5')
unreal.log('CR051_BASELINE '+str(len(records))+' actors; socket bindings='+str([n for n in dir(rook) if 'socket' in n]))
unreal.log('CR051_SOCKET_API '+str(unreal.StaticMeshSocket.__doc__))
shots=[('spawn',(-1710,-60,165),(-2,7,0)),('train-route',(-600,700,165),(-2,-20,0)),('workshop-entrance',(1120,0,165),(-2,0,0)),('outer-walls',(-1000,0,165),(5,-80,0))]
pair='-cr051perimeterpair' in unreal.SystemLibrary.get_command_line().lower()
if pair:shots=[('perimeter-before',(700,500,165),(15,60,0)),('perimeter-after',(700,500,165),(15,60,0))]
camera=actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(*shots[0][1]));camera.camera_component.set_field_of_view(85);actors.clear_actor_selection_set()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));old=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
after='-cr051after' in unreal.SystemLibrary.get_command_line().lower();prefix='after' if after else 'before'
started=time.monotonic();changed=started;index=0;task=None;receipt=[];handle=None
def setup():
 global changed
 if pair:
  for a in actors.get_all_level_actors():
   if 'CR_Phase051_Generated' in [str(t) for t in a.tags]:a.set_is_temporarily_hidden_in_editor(index==0);a.set_actor_hidden_in_game(index==0)
 _,loc,r=shots[index];camera.set_actor_location(unreal.Vector(*loc),False,False);camera.set_actor_rotation(unreal.Rotator(pitch=r[0],yaw=r[1],roll=r[2]),False);changed=time.monotonic()
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',old);unreal.unregister_slate_post_tick_callback(handle)
 (out/('perimeter-frames.json' if pair else prefix+'-frames.json')).write_text(json.dumps({'frames':receipt,'error':error},indent=2));unreal.log('CR051_CAPTURE '+str(error or 'PASS'));unreal.SystemLibrary.quit_editor()
def tick(delta):
 global index,task
 try:
  if time.monotonic()-started>140:raise RuntimeError('Bounded capture timeout')
  if task and task.is_task_done():
   path=out/(prefix+'-'+shots[index][0]+'.png');assert path.exists() and path.stat().st_size>10000;receipt.append({'path':str(path),'location':shots[index][1],'rotation':shots[index][2],'fov':85});index+=1;task=None
   if index==len(shots):finish();return
   setup()
  elif not task and time.monotonic()-changed>7:task=unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(out/(prefix+'-'+shots[index][0]+'.png')),camera=camera,force_game_view=True)
 except Exception:finish(traceback.format_exc())
unreal.EditorPythonScripting.set_keep_python_script_alive(True);setup();handle=unreal.register_slate_post_tick_callback(tick)
