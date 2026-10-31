"""UE 5.8 Editor-only, one-way non-destructive Phase 01A -> Phase 01B migration.

Run in the full Editor with -ExecutePythonScript (not the Python commandlet).
Real world duplication + EditorLevelUtils.move_actors_to_level. Never respawns
the 155 source actors. A completed rerun audits only; partial/unowned destinations
are refused rather than repaired by deleting user content.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path
import unreal

SOURCE = '/Game/Generated/Phase01A/Maps/L_CH01_Greybox'
ROOT = '/Game/Generated/Phase01B/Maps/'
PERSISTENT = ROOT + 'L_CH01_Persistent'
MAPS = [ROOT + 'L_CH01_' + n for n in ('RailYard', 'Workshop', 'RelayBunker')]
OWNER = 'CinderRelay.Phase01B.v1'
META = 'CR.GeneratedBy'
TAG = 'CR_Phase01A_Generated'
ZONE_TAGS = ['CR_Zone_A_RailYard', 'CR_Zone_B_Workshop', 'CR_Zone_C_RelayBunker']
PERSIST = {
    'CR_PlayerStart', 'CR_WorkshopFront-440', 'CR_WorkshopFront440',
    'CR_WorkshopLintelFront', 'CR_WorkshopRear-440', 'CR_WorkshopRear440',
    'CR_WorkshopLintelRear', 'CR_WorkshopEntrance', 'CR_EntranceStripe-205',
    'CR_EntranceStripe205', 'CR_BunkerDirection',
}
assets = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
out = Path(unreal.Paths.project_saved_dir()) / 'Phase01B'
out.mkdir(parents=True, exist_ok=True)
source_file = Path(unreal.Paths.project_content_dir()) / 'Generated/Phase01A/Maps/L_CH01_Greybox.umap'
source_hash = hashlib.sha256(source_file.read_bytes()).hexdigest()


def vector(value):
    return [round(value.x, 5), round(value.y, 5), round(value.z, 5)]


def transform(value):
    q = value.rotation
    return [vector(value.translation), [round(v, 5) for v in (q.x, q.y, q.z, q.w)], vector(value.scale3d)]


def snapshot(actor):
    result = dict(label=actor.get_actor_label(), cls=actor.get_class().get_path_name(),
                  transform=transform(actor.get_actor_transform()),
                  collision=actor.get_actor_enable_collision(),
                  tags=sorted(str(t) for t in actor.tags if not str(t).startswith('CR_Ready_')),
                  components=[])
    if isinstance(actor, unreal.CRInteractionActor):
        result['kind'] = str(actor.get_editor_property('kind'))
        result['used'] = actor.get_editor_property('used')
    for component in actor.get_components_by_class(unreal.ActorComponent):
        data = dict(name=component.get_name(), cls=component.get_class().get_path_name())
        if isinstance(component, unreal.SceneComponent):
            data['transform'] = transform(component.get_world_transform())
            data['mobility'] = str(component.mobility)
        if isinstance(component, unreal.PrimitiveComponent):
            data.update(profile=str(component.get_collision_profile_name()),
                        enabled=str(component.get_collision_enabled()),
                        object_type=str(component.get_collision_object_type()),
                        overlaps=component.get_editor_property('generate_overlap_events'))
        if isinstance(component, unreal.StaticMeshComponent):
            mesh = component.static_mesh
            data['mesh'] = mesh.get_path_name() if mesh else None
            data['materials'] = [m.get_path_name() if m else None for m in component.get_materials()]
        if isinstance(component, unreal.BoxComponent):
            data['extent'] = vector(component.get_unscaled_box_extent())
        if isinstance(component, unreal.LightComponent):
            data['intensity'] = component.intensity
            color = component.light_color
            data['color'] = [color.r, color.g, color.b, color.a]
        result['components'].append(data)
    result['components'].sort(key=lambda c: c['name'])
    return result


def source_actors():
    found = [a for a in actors.get_all_level_actors() if TAG in [str(t) for t in a.tags]]
    assert len(found) == 155, f'Expected 155 original actors, got {len(found)}'
    assert len({a.get_actor_label() for a in found}) == 155, 'Duplicate original labels'
    return found


def level_name(actor):
    return actor.get_level().get_outer().get_name()


def target(actor):
    tags = [str(t) for t in actor.tags]
    if actor.get_actor_label() in PERSIST or 'CR_Zone_Shared' in tags:
        return 'L_CH01_Persistent'
    matches = [i for i, tag in enumerate(ZONE_TAGS) if tag in tags]
    assert len(matches) == 1, f'Ambiguous ownership: {actor.get_actor_label()}'
    return MAPS[matches[0]].rsplit('/', 1)[1]


assert levels.load_level(SOURCE), 'Cannot open rollback map'
before, errors = {}, []
for a in source_actors():
    try:
        before[a.get_actor_label()] = snapshot(a)
    except Exception as error:
        errors.append(f'{a.get_actor_label()}: {type(error).__name__}: {error}')
assert not errors, 'Read-only snapshot API preflight failed: ' + '; '.join(errors)
del a  # Python wrappers hold strong UObject references across an Editor map load.
desired = {a.get_actor_label(): target(a) for a in source_actors()}
exists = [assets.does_asset_exist(p) for p in [PERSISTENT] + MAPS]
if all(exists):
    for path in [PERSISTENT] + MAPS:
        assert str(assets.get_metadata_tag(assets.load_asset(path), META)) == OWNER, 'Unowned destination: ' + path
    assert (out / 'migration.json').exists(), 'Existing maps require the original migration receipt for audit-only rerun'
    assert levels.load_level(PERSISTENT)
else:
    assert not any(exists[1:]), 'Partial sublevel migration exists; refusing automatic deletion or reconstruction'
    if exists[0]:
        assert str(assets.get_metadata_tag(assets.load_asset(PERSISTENT), META)) == OWNER, 'Unowned partial copy'
    else:
        duplicate = assets.duplicate_asset(SOURCE, PERSISTENT)
        assert duplicate, 'Editor world duplication failed; rollback map remains intact'
        assets.set_metadata_tag(duplicate, META, OWNER)
        assert assets.save_loaded_asset(duplicate, only_if_is_dirty=False)
        del duplicate  # Avoid FPyReferenceCollector retaining a world during LoadLevel GC.
    assert levels.load_level(PERSISTENT)
    copied = {a.get_actor_label(): snapshot(a) for a in source_actors()}
    (out / 'copy-comparison.json').write_text(json.dumps(dict(before=before, copied=copied), indent=2), encoding='utf-8')
    assert copied == before, 'Partial copy differs from original; see Saved/Phase01B/copy-comparison.json'
    for index, path in enumerate(MAPS):
        level = unreal.EditorLevelUtils.create_new_streaming_level(unreal.LevelStreamingDynamic, path, False)
        assert level, 'Cannot create native streaming level: ' + path
        level.set_editor_property('initially_loaded', False)
        level.set_editor_property('initially_visible', False)
        level.set_editor_property('should_be_loaded', False)
        level.set_editor_property('should_be_visible', False)
        level.set_editor_property('should_block_on_load', False)
        level.set_editor_property('should_block_on_unload', False)
        level.set_editor_property('editor_streaming_volumes', [])
        moving = [a for a in source_actors() if desired[a.get_actor_label()] == path.rsplit('/', 1)[1]]
        assert level.get_loaded_level(), 'New sublevel was not loaded by the Editor'
        actors.set_selected_level_actors(moving)
        assert len(actors.get_selected_level_actors()) == len(moving), 'Editor selection unavailable; use full Editor -ExecutePythonScript'
        count = unreal.EditorLevelUtils.move_actors_to_level(moving, level, False, False)
        assert count == len(moving), f'Incomplete move: {path}: {count}/{len(moving)}'
        world = level.get_loaded_level().get_outer()
        assets.set_metadata_tag(world, META, OWNER)
    after = {a.get_actor_label(): snapshot(a) for a in source_actors()}
    differences = [label for label in before if before[label] != after.get(label)]
    (out / 'migration-comparison.json').write_text(json.dumps(dict(before=before, after=after, differences=differences), indent=2), encoding='utf-8')
    assert not differences, 'Migration changed actor settings: ' + ', '.join(differences)
    for actor in source_actors():
        assert level_name(actor) == desired[actor.get_actor_label()]
        label = actor.get_actor_label()
        if label in ('CR_WorkshopEntry', 'CR_AccessRamp'):
            actor.set_editor_property('tags', list(actor.tags) + [unreal.Name('CR_Ready_' + label[3:])])
    assert levels.set_current_level_by_name('L_CH01_Persistent')
    controller = actors.spawn_actor_from_class(unreal.CRChapterStreamingController, unreal.Vector(0,0,0))
    controller.set_actor_label('CR_ChapterStreamingController')
    controller.set_editor_property('tags', [unreal.Name('CR_Phase01B_Generated')])
    cube = assets.load_asset('/Engine/BasicShapes/Cube')
    material = assets.load_asset('/Game/Generated/Phase01A/Materials/M_RustedIron')
    assert cube and material
    for index, x in enumerate((1600, 3600)):
        gate = actors.spawn_actor_from_class(unreal.CRStreamingGate, unreal.Vector(x,0,0))
        gate.set_actor_label('CR_Gate_' + ('AB' if index == 0 else 'BC'))
        gate.set_editor_property('left_zone', index)
        gate.set_editor_property('tags', [unreal.Name('CR_Phase01B_Generated')])
        gate.door.set_static_mesh(cube)
        gate.door.set_material(0, material)
    assert levels.save_all_dirty_levels()

inventory = []
for actor in source_actors():
    assert before[actor.get_actor_label()] == snapshot(actor), 'Post-save actor mismatch: ' + actor.get_actor_label()
    assert level_name(actor) == desired[actor.get_actor_label()]
    inventory.append(dict(label=actor.get_actor_label(), level=level_name(actor), cls=actor.get_class().get_path_name()))
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
streaming = unreal.GameplayStatics.get_streaming_level
registrations = []
for path in MAPS:
    level = streaming(world, path)
    assert isinstance(level, unreal.LevelStreamingDynamic)
    assert not level.get_editor_property('initially_loaded')
    assert not level.get_editor_property('initially_visible')
    assert not level.get_editor_property('editor_streaming_volumes')
    registrations.append(dict(path=path, cls=level.get_class().get_path_name(), initial_loaded=False, initial_visible=False))
all_actors = actors.get_all_level_actors()
assert sum(isinstance(a, unreal.CRChapterStreamingController) for a in all_actors) == 1
assert sum(isinstance(a, unreal.CRStreamingGate) for a in all_actors) == 2
assert hashlib.sha256(source_file.read_bytes()).hexdigest() == source_hash, 'Original map bytes changed'
receipt = dict(passed=True, original_sha256=source_hash, original_count=155,
               original_actor_counts=dict(Counter(v['level'] for v in inventory)),
               additions={'L_CH01_Persistent': ['CR_ChapterStreamingController','CR_Gate_AB','CR_Gate_BC']},
               maps=[PERSISTENT]+MAPS, registrations=registrations, actors=inventory,
               actor_settings_equal=True, rerun_audit_only=all(exists))
(out / 'migration.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
unreal.log('CR_MIGRATION_PASS ' + json.dumps(receipt['original_actor_counts']))
if '-run=pythonscript' not in unreal.SystemLibrary.get_command_line().lower():
    unreal.SystemLibrary.quit_editor()
