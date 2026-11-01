"""Focused saved-profile correction for Phase05-owned static decoration only."""
import unreal,json
from pathlib import Path
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);path='/Game/Generated/Phase01B/Maps/L_CH01_Persistent'
assert levels.load_level(path);fixed=[]
for a in actors.get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor) and 'CR_Phase05_Generated' in [str(t) for t in a.tags]:
  a.modify();c=a.static_mesh_component;c.modify();c.set_collision_profile_name('NoCollision');c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);c.set_editor_property('can_ever_affect_navigation',False);a.set_actor_enable_collision(False);fixed.append(a.get_actor_label())
assert levels.save_all_dirty_levels();assert levels.load_level(path)
for a in actors.get_all_level_actors():
 if a.get_actor_label() in fixed:
  assert not a.get_actor_enable_collision();assert a.static_mesh_component.get_collision_profile_name()=='NoCollision';assert a.static_mesh_component.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
out=Path(unreal.Paths.project_dir()).parent/'.environment-local/phase-05';(out/'collision-repair.json').write_text(json.dumps(fixed,indent=2));unreal.log('CR05_SAVED_COLLISION_PASS '+str(len(fixed)));unreal.SystemLibrary.quit_editor()
