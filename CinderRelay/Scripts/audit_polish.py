"""Read-only Phase05 Editor baseline. Never runs any older generator."""
import ast, json
from pathlib import Path
import unreal
p=Path(unreal.Paths.project_dir()); out=p.parent/'.environment-local/phase-05'
out.mkdir(parents=True,exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assets=unreal.EditorAssetLibrary
assert levels.load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
scope={'unreal':unreal}
tree=ast.parse((p/'Scripts/migrate_streaming.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('vector','transform','snapshot')],type_ignores=[]),'snapshot','exec'),scope)
records={}
for a in actors.get_all_level_actors():
    r=scope['snapshot'](a);r['level']=a.get_level().get_outer().get_name()
    r['hidden']=a.get_editor_property('hidden'); records[a.get_actor_label()]=r
    if isinstance(a,unreal.CRCheckpoint): r['checkpoint_id']=str(a.checkpoint_id)
report={'actors':records,'assets':list(assets.list_assets('/Game/Generated',recursive=True)),'bindings':{n:hasattr(unreal,n) for n in ['EditorLevelLibrary','AutomationLibrary','MovieSceneFloatTrack','MovieSceneAudioTrack','InstancedStaticMeshComponent','AnimSequence','AnimBlueprintFactory']}}
destination=out/'editor-baseline.json'
assert not destination.exists(),'Read-only baseline already exists; inspect it rather than overwrite'
destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
unreal.log('CR05_AUDIT_PASS '+str(len(records))+' actors')
unreal.SystemLibrary.quit_editor()
