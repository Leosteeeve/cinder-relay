"""Read-only Editor audit of preserved actors and Phase02 asset dependencies."""
import unreal,json,hashlib,ast
from pathlib import Path
project=Path(unreal.Paths.project_dir())
out=project.parent/'.environment-local/phase-02'
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Generated/Phase01B/Maps/L_CH01_Persistent')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
# Reuse only the pure snapshot helpers, never execute any old migration operation.
module=ast.parse((project/'Scripts/migrate_streaming.py').read_text(encoding='utf-8-sig'))
helpers=ast.Module(body=[node for node in module.body if isinstance(node,ast.FunctionDef) and node.name in ('vector','transform','snapshot')],type_ignores=[])
scope={'unreal':unreal}; exec(compile(helpers,'migration_snapshot_helpers','exec'),scope)
original=[a for a in actors if 'CR_Phase01A_Generated' in [str(t) for t in a.tags]]
assert len(original)==155
before=json.loads((project/'Saved/Phase01B/migration-comparison.json').read_text())['before']
differences=[a.get_actor_label() for a in original if scope['snapshot'](a)!=before[a.get_actor_label()]]
assert not differences, 'Original settings changed: '+str(differences)
assert hashlib.sha256((project/'Content/Generated/Phase01A/Maps/L_CH01_Greybox.umap').read_bytes()).hexdigest().upper()=='C22AC1DAFE74F3006CA8F2498E7AD81BA8AC827890C44B3554F31D0D13D3E733'
enemies=[a for a in actors if isinstance(a,unreal.CRAshWarden)]
assert len(enemies)==2 and len({str(e.enemy_id) for e in enemies})==2
assert all(e.get_level().get_outer().get_name()=='L_CH01_RailYard' and e.behavior and e.behavior.get_editor_property('root_node') for e in enemies)
assert len([a for a in actors if isinstance(a,unreal.CRAmmoPickup)])==1
assert len([a for a in actors if isinstance(a,unreal.CRChapterStreamingController)])==1
assert len([a for a in actors if isinstance(a,unreal.CRStreamingGate)])==2
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for name in ['RailYard','Workshop','RelayBunker']:
    level=unreal.GameplayStatics.get_streaming_level(world,'/Game/Generated/Phase01B/Maps/L_CH01_'+name)
    assert isinstance(level,unreal.LevelStreamingDynamic) and not level.get_editor_property('editor_streaming_volumes')
receipt=dict(passed=True,preserved_originals=155,differences=differences,scouts=[dict(id=str(e.enemy_id),level=e.get_level().get_outer().get_name()) for e in enemies])
(out/'asset-audit.json').write_text(json.dumps(receipt,indent=2))
unreal.log('CR02_ASSET_AUDIT_PASS '+json.dumps(receipt))
if '-CRCombatCheck' not in unreal.SystemLibrary.get_command_line():
    unreal.SystemLibrary.quit_editor()
