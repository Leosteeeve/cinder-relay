"""Phase04: add only three owned persistent checkpoint markers using real Editor APIs.
Run after building CinderRelayEditor. No old generator, deletion, or asset import.
"""
import ast
import hashlib
import json
import shutil
from pathlib import Path
import unreal

p = Path(unreal.Paths.project_dir())
out = p.parent / '.environment-local/phase-04'
out.mkdir(parents=True, exist_ok=True)
asset = '/Game/Generated/Phase01B/Maps/L_CH01_Persistent'
disk = p / 'Content/Generated/Phase01B/Maps/L_CH01_Persistent.umap'
backup = out / 'L_CH01_Persistent.before-phase04.umap'
if not backup.exists():
    shutil.copy2(disk, backup)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level(asset)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
scope = {'unreal': unreal}
tree = ast.parse((p / 'Scripts/migrate_streaming.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('vector','transform','snapshot')], type_ignores=[]), 'snapshot', 'exec'), scope)
tag = 'CR_Phase04_Checkpoint'
existing = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
before = {n: scope['snapshot'](a) for n,a in existing.items() if tag not in [str(t) for t in a.tags]}
(out / 'anchors-before.json').write_text(json.dumps(before, indent=2), encoding='utf-8')
assert levels.set_current_level_by_name('L_CH01_Persistent')
receipt = []
for name, x in [('CP00_START_YARD', -1450), ('CP01_WORKSHOP_ENTRY', 2050), ('CP02_RELAY_ACCESS', 4050)]:
    # Derive height from actual registered collision, not assumed Blender/Editor transforms.
    a = existing.get(name)
    if a:
        assert isinstance(a, unreal.CRCheckpoint) and tag in [str(t) for t in a.tags], 'Unowned checkpoint label'
    else:
        a = actors.spawn_actor_from_class(unreal.CRCheckpoint, unreal.Vector(x,0,100))
        a.set_actor_label(name)
        a.tags = [tag, 'CR_Zone_Shared']
    a.modify()
    a.set_editor_property('checkpoint_id', name)
    a.set_actor_location(unreal.Vector(x,0,100), False, False)
    assert a.snap_to_safe_floor(), 'Native Editor floor query failed for ' + name
    a.set_actor_rotation(unreal.Rotator(), False)
    assert a.get_level().get_outer().get_name() == 'L_CH01_Persistent'
    receipt.append({'id':name, 'position':scope['vector'](a.get_actor_location()), 'floor':scope['vector'](a.get_actor_location()-unreal.Vector(0,0,110))})
after = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
assert all(n in after and scope['snapshot'](after[n]) == s for n,s in before.items()), 'Existing actor changed'
assert len([a for a in after.values() if isinstance(a, unreal.CRCheckpoint)]) == 3
assert levels.save_current_level()
# Release Python wrappers before re-opening to validate actual saved persistence.
del existing, after, a, world
assert levels.load_level(asset)
saved = [a for a in actors.get_all_level_actors() if isinstance(a, unreal.CRCheckpoint)]
assert sorted(str(a.checkpoint_id) for a in saved) == sorted(r['id'] for r in receipt)
report = {'preserved_actor_count':len(before), 'added_markers':receipt, 'asset':asset,
          'backup_sha256':hashlib.sha256(backup.read_bytes()).hexdigest(), 'saved_sha256':hashlib.sha256(disk.read_bytes()).hexdigest()}
(out/'checkpoint-assets.json').write_text(json.dumps(report,indent=2), encoding='utf-8')
unreal.log('CR04_ASSETS_PASS '+json.dumps(report))
unreal.SystemLibrary.quit_editor()
