"""Native, bounded authoring for the Relay Bunker shuttle's stationary enclosure.

Run read-only by default. -CR06RepairAccessFrame creates/updates only owned frame
actors, moves the machine's display clear of its housing, and saves RelayBunker.
The existing shuttle, barrier, stop control, timing and checkpoint data stay intact.
"""
import json
from pathlib import Path
import unreal


TAG = 'CR_Phase06_AccessFrame'
# Local centimetres relative to CR06_AccessMachinery; the south service lane
# remains 260 cm wide. Housing conceals the existing ceiling retraction pocket.
PARTS = [
    ('GuideSouth', (0, -320, 250), (100, 40, 500), 'Steel'),
    ('GuideNorth', (0, 320, 250), (100, 40, 500), 'Steel'),
    ('HeadHousing', (0, 0, 415), (125, 680, 170), 'Paint'),
    ('NorthInfill', (0, 490, 250), (70, 300, 500), 'Paint'),
    ('NorthWallFixing', (0, 635, 250), (110, 30, 500), 'Steel'),
    ('ServiceWallPost', (0, -625, 250), (100, 50, 500), 'Steel'),
    ('ServiceHeader', (0, -490, 400), (100, 340, 200), 'Steel'),
    ('GuideMarkSouth', (-53, -320, 140), (6, 20, 250), 'Amber'),
    ('GuideMarkNorth', (-53, 320, 140), (6, 20, 250), 'Amber'),
    ('HousingSeam', (-65, 0, 495), (5, 620, 8), 'Dark'),
]


def frame_name(suffix):
    return 'CR06_AccessFrame_' + suffix


def author_access_frame(levels, actors):
    existing = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
    machine = existing['CR06_AccessMachinery']
    assert 'CR_Phase06' in [str(t) for t in machine.tags]
    assert levels.set_current_level_by_name('L_CH01_RelayBunker')
    cube = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cube')
    for suffix, offset, size, material in PARTS:
        name = frame_name(suffix)
        a = existing.get(name)
        if a:
            assert TAG in [str(t) for t in a.tags], 'Unowned actor: ' + name
        else:
            a = actors.spawn_actor_from_class(unreal.StaticMeshActor, machine.get_actor_location())
            a.set_actor_label(name)
            a.tags = ['CR_Phase06', TAG]
        a.modify()
        a.set_actor_location(machine.get_actor_location() + unreal.Vector(*offset), False, False)
        a.set_actor_rotation(unreal.Rotator(), False)
        a.set_actor_scale3d(unreal.Vector(*(v / 100 for v in size)))
        c = a.static_mesh_component
        c.set_static_mesh(cube)
        c.set_material(0, unreal.EditorAssetLibrary.load_asset(
            '/Game/Generated/Phase052/Materials/MI_CR052_' + material))
        c.set_collision_profile_name('NoCollision' if suffix.startswith(('GuideMark', 'HousingSeam')) else 'BlockAll')
        c.set_editor_property('can_ever_affect_navigation', False)
    machine.modify()
    # Text was inside the new housing; put it 17.5 cm in front of the face.
    machine.status.set_editor_property('relative_location', unreal.Vector(-80, 0, 355))


def snapshot(a):
    return dict(transform=str(a.get_actor_transform()), components=[
        dict(name=c.get_name(), transform=str(c.get_relative_transform()),
             collision=str(c.get_collision_profile_name()))
        for c in a.get_components_by_class(unreal.PrimitiveComponent)
        if not isinstance(c, unreal.TextRenderComponent)])


def validate(actors):
    existing = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
    missing = [frame_name(s) for s, *_ in PARTS if frame_name(s) not in existing]
    assert not missing, 'Shuttle has no stationary wall connection: ' + ', '.join(missing)
    boxes = {}
    for suffix, *_ in PARTS:
        a = existing[frame_name(suffix)]
        origin, extent = a.get_actor_bounds(False)
        boxes[suffix] = ([origin.x-extent.x, origin.y-extent.y, origin.z-extent.z],
                         [origin.x+extent.x, origin.y+extent.y, origin.z+extent.z])
    def touches(a, b):
        return all(a[0][i] <= b[1][i]+.1 and b[0][i] <= a[1][i]+.1 for i in range(3))
    def wall(name):
        o, e = existing[name].get_actor_bounds(False)
        return ([o.x-e.x, o.y-e.y, o.z-e.z], [o.x+e.x, o.y+e.y, o.z+e.z])
    assert touches(boxes['NorthWallFixing'], wall('CR_BunkerSide650'))
    assert touches(boxes['ServiceWallPost'], wall('CR_BunkerSide-650'))
    for a, b in [('GuideNorth','HeadHousing'), ('GuideSouth','HeadHousing'),
                 ('GuideNorth','NorthInfill'), ('NorthInfill','NorthWallFixing'),
                 ('GuideSouth','ServiceHeader'), ('ServiceHeader','ServiceWallPost')]:
        assert touches(boxes[a], boxes[b]), 'Disconnected frame: ' + a + '/' + b
    # Real saved bounds must leave a 84 cm wide, 192 cm tall player envelope
    # on both the existing center crossing and south service-walk route.
    machine = existing['CR06_AccessMachinery'].get_actor_location()
    for y in (0, -430):
        envelope = ([machine.x-100, machine.y+y-42, machine.z+2],
                    [machine.x+100, machine.y+y+42, machine.z+194])
        for name, box in boxes.items():
            assert not touches(envelope, box), 'Frame obstructs player route: ' + name
    return dict(wall_connections=True, center_and_service_envelopes_clear=True, bounds=boxes)


if __name__ == '__main__':
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    path = '/Game/Generated/Phase01B/Maps/L_CH01_Persistent'
    assert levels.load_level(path)
    before = {a.get_actor_label(): snapshot(a) for a in actors.get_all_level_actors()}
    apply = '-cr06repairaccessframe' in unreal.SystemLibrary.get_command_line().lower()
    if apply:
        author_access_frame(levels, actors)
        assert levels.save_current_level()
        assert levels.load_level(path)
    result = validate(actors)
    after = {a.get_actor_label(): snapshot(a) for a in actors.get_all_level_actors()}
    changed = [n for n in before if n != 'CR06_AccessMachinery'
               and not n.startswith('CR06_AccessFrame_') and before[n] != after.get(n)]
    assert not changed, 'Unrelated actor change: ' + ', '.join(changed)
    # TextRender is intentionally not in this primitive snapshot; all machine
    # collision/control/shuttle transforms and profiles must remain identical.
    assert before['CR06_AccessMachinery'] == after['CR06_AccessMachinery']
    result['unrelated_actors_unchanged'] = len(before) - 1
    result['applied'] = apply
    out = Path(unreal.Paths.project_dir()).parent / '.environment-local/phase-06/door-seam'
    out.mkdir(parents=True, exist_ok=True)
    (out / ('native-after.json' if apply else 'native-check.json')).write_text(json.dumps(result, indent=2))
    unreal.log('CR06_ACCESS_FRAME PASS ' + str(result['unrelated_actors_unchanged']))
