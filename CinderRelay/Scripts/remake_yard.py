"""Incrementally build the transfer spur in the existing Chapter 01 Rail Yard."""
import json
from pathlib import Path

import unreal


levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assets = unreal.EditorAssetLibrary
chapter = '/Game/Generated/Phase01B/Maps/L_CH01_Persistent'
zone = 'L_CH01_RailYard'
owner = 'CR_Phase06_TransferSpur'
prefix = 'CR06_Spur_'


def asset(path):
    value = assets.load_asset(path)
    assert value, path
    return value


def xyz(vector):
    return [round(v, 4) for v in (vector.x, vector.y, vector.z)]


def transform(a):
    rot = a.get_actor_rotation()
    return xyz(a.get_actor_location()) + [round(v, 4) for v in (rot.pitch, rot.yaw, rot.roll)] + xyz(a.get_actor_scale3d())


def yard_map():
    scene = {}
    for a in actors.get_all_level_actors():
        if a.get_level().get_outer().get_name().rsplit('/', 1)[-1] == zone:
            name = a.get_actor_label()
            assert name not in scene, 'Duplicate yard label: ' + name
            scene[name] = a
    return scene


def checkpoint_anchors():
    return {str(a.get_editor_property('checkpoint_id')): transform(a) for a in actors.get_all_level_actors()
            if isinstance(a, unreal.CRCheckpoint)}


def existing(name, tag):
    a = scene[name]
    assert tag in [str(t) for t in a.tags], 'Unowned yard actor: ' + name
    return a


def place(name, cls, pos, yaw=0, scale=(1, 1, 1)):
    label = prefix + name
    a = scene.get(label)
    if a is None:
        a = actors.spawn_actor_from_class(cls, unreal.Vector(*pos))
        assert a and a.get_level().get_outer().get_name().rsplit('/', 1)[-1] == zone, label
        a.set_actor_label(label)
        a.tags = [owner]
        scene[label] = a
    else:
        assert isinstance(a, cls) and owner in [str(t) for t in a.tags], label
    a.modify()
    a.set_actor_location(unreal.Vector(*pos), False, False)
    a.set_actor_rotation(unreal.Rotator(yaw=yaw), False)
    a.set_actor_scale3d(unreal.Vector(*scale))
    added.add(label)
    return a


def prop(name, mesh, pos, yaw=0, scale=(1, 1, 1), material=None, solid=False):
    a = place(name, unreal.StaticMeshActor, pos, yaw, scale)
    c = a.static_mesh_component
    c.set_static_mesh(mesh)
    if material is not None:
        c.set_material(0, palette[material])
    c.set_collision_profile_name('BlockAll' if solid else 'NoCollision')
    c.set_editor_property('can_ever_affect_navigation', solid)
    a.set_actor_enable_collision(solid)
    return a


def block(name, pos, size, material='Steel', solid=False):
    return prop(name, cube, pos, scale=tuple(n / 100 for n in size), material=material, solid=solid)


def retire(name, tag):
    # Preserve the original actor and its asset references for rollback.
    a = existing(name, tag)
    a.modify()
    a.set_actor_hidden_in_game(True)
    a.set_actor_enable_collision(False)
    for c in a.get_components_by_class(unreal.PrimitiveComponent):
        c.modify()
        c.set_visibility(False)
        c.set_collision_profile_name('NoCollision')
        c.set_editor_property('can_ever_affect_navigation', False)
    retired.add(name)


def relocate(name, tag, pos):
    a = existing(name, tag)
    a.modify()
    a.set_actor_location(unreal.Vector(*pos), False, False)


def sign(name, pos, yaw, words, width, height, font):
    prop(name + 'Plate', plaque, pos, yaw, (.72, width / 240, height / 72))
    offset = unreal.Rotator(yaw=yaw).get_forward_vector() * 7
    text = place(name, unreal.TextRenderActor, xyz(unreal.Vector(*pos) + offset), yaw).text_render
    text.set_text(words)
    text.set_world_size(font)
    text.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    text.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
    text.set_text_render_color(unreal.Color(247, 219, 147))


assert levels.load_level(chapter)
assert levels.set_current_level_by_name(zone)
scene = yard_map()
anchors = checkpoint_anchors()
assert len(anchors) == 3
ids = {n: str(scene[n].get_editor_property('enemy_id')) for n in ('CR02_Scout_1', 'CR02_Scout_2')}
added, retired = set(), set()
cube = asset('/Engine/BasicShapes/Cube')
cylinder = asset('/Engine/BasicShapes/Cylinder')
palette = {n: asset('/Game/Generated/Phase052/Materials/MI_CR052_' + n)
           for n in ('Dark', 'Steel', 'Paint', 'Rust', 'Amber', 'Pale')}
mesh05 = '/Game/Generated/Phase05/Meshes/SM_CR05_'
mesh06 = '/Game/Generated/Phase06/Meshes/SM_CR06_'
plaque = asset(mesh06 + 'ServicePlaque')
column = asset(mesh05 + 'SteelColumn')
gantry = asset(mesh05 + 'Gantry')
cladding = asset('/Game/Generated/Phase06/Meshes/ServiceArchitecture/SM_CR06_SignalStoreCladding')
railcar = existing('CR05_RailCar800', 'CR_Phase05_Generated').static_mesh_component.static_mesh
assert railcar.get_name() == 'SM_CR052_RailServiceCar'

# The north wagon is a visible service car plus twelve retained Phase01 collision shells.
# Replace all thirteen locally; neither the south car nor its collision changes.
retire('CR05_RailCar800', 'CR_Phase05_Generated')
shells = ['CR_CarBody800', 'CR_CarRoof800']
shells += [f'CR_Wheel800_{x}_{y}' for x in (-310, 310) for y in (-170, 170)]
shells += [f'CR_CarWindow800_{x}_{y}' for x in (-280, 0, 280) for y in (-158, 158)]
for label in shells:
    retire(label, 'CR_Phase01A_Generated')

# The expansion used two parallel solid wall sections behind a visual perimeter.
# Open both, then close only the stretches outside the wagon envelope.
for name in ('YardNorthWest', 'ApronSealWest'):
    retire('CR06X_' + name, 'CR_Phase06_Expanded')
for index in (1, 2):
    retire('CR051_Perimeter1_' + str(index), 'CR_Phase051_Generated')
for end, left, right in (('West', -2000, -1265), ('East', -195, 415)):
    block('Retaining' + end, ((left + right) / 2, 1411, 160), (right - left, 70, 320), 'Paint', True)
relocate('CR05_Gantry-1200', 'CR_Phase05_Generated', (-1380, 0, 600))
relocate('CR052_GantryServices-1200', 'CR_Phase052_Generated', (-1380, 0, 600))
for y in (-1370, 1370):
    relocate('CR05_YardColumn0_' + str(y), 'CR_Phase05_Generated', (-1380, y, 0))
relocate('CR05_YardColumn1_1370', 'CR_Phase05_Generated', (-160, 1370, 0))
relocate('CR054_RailMaintenanceSleeper1', 'CR_Phase054_Generated', (-1450, 1010, 0))

h = place('TransferHoist', unreal.CRYardHoist, (-730, 1400, 0))
h.wagon.set_static_mesh(railcar)
h.panel.set_static_mesh(asset(mesh06 + 'DiagnosticPanel'))
for cable in (h.west_cable, h.east_cable):
    cable.set_static_mesh(cylinder)
    cable.set_material(0, palette['Steel'])

# A four-legged transfer frame straddles the bay. Shafts reel the moving cables
# straight up from the two roof hatches. The full lift still has head clearance above.
for side, y in (('Yard', 1145), ('Apron', 1655)):
    for end, x in (('West', -1265), ('East', -195)):
        block(end + side + 'Foot', (x, y, 23), (96, 100, 46), 'Dark', True)
        height = column.get_bounds().box_extent.z * 2
        prop(end + side + 'Column', column, (x, y, 40), scale=(1.22, 1.22, 888 / height))
        block(end + side + 'Core', (x, y, 472), (32, 36, 866), 'Steel', True)
        block(end + side + 'Band', (x, y, 117), (44, 48, 24), 'Amber')
    width = gantry.get_bounds().box_extent.y * 2
    prop(side + 'Truss', gantry, (-730, y, 925), 90, scale=(1, 1170 / width, .64))
for end, x in (('West', -1040), ('East', -420)):
    block(end + 'Bridge', (x, 1400, 957), (51, 550, 32), 'Rust')
    wheel = prop(end + 'Drum', cylinder, (x, 1400, 946), scale=(.54, .54, .92), material='Steel')
    wheel.set_actor_rotation(unreal.Rotator(pitch=90), False)
for side in (-1, 1):
    block('TransferRail' + str(side), (-740, 1400 + side * 150, 5), (1290, 13, 10), 'Steel')
block('PumpPlinth', (-916, 1048, 12), (170, 120, 24), 'Paint', True)
prop('HydraulicPump', asset(mesh05 + 'PumpMotor'), (-916, 1048, 24), 180)

# The opening booth screens the operator from both original scout spawns.
# Its south edge leaves the center approach and the historical slide fixture clear.
block('BoothBack', (-1030, 238, 145), (30, 307, 290), 'Paint', True)
prop('BoothOuterSkin', cladding, (-1011, 238, 148), 90, scale=(1.28, 1, .93))
block('BoothRoof', (-1111, 238, 299), (200, 330, 18), 'Amber')
block('BreakerStand', (-1119, 210, 129), (20, 79, 258), 'Steel', True)
prop('BreakerStatusBack', plaque, (-1161, 210, 211), 180, (.5, .80, .90))
sign('BoothFascia', (-1215, 238, 299), 180, 'TRANSFER HOIST', 280, 42, 20)
sign('ApronEntry', (-730, 1130, 879), -90, 'SIGNAL STORE', 331, 66, 29)
block('EntrySignBar', (-730, 1145, 905), (190, 17, 85), 'Steel')
for n, y in enumerate((475, 670, 865)):
    block('ServiceMark' + str(n), (-890, y, 1.7), (12, 83, 3), 'Amber')

assert levels.save_current_level()
assert levels.load_level(chapter)
scene = yard_map()
assert checkpoint_anchors() == anchors
assert all(str(scene[n].get_editor_property('enemy_id')) == key for n, key in ids.items())
assert {n for n, a in scene.items() if owner in [str(t) for t in a.tags]} == added
assert all(not scene[n].get_actor_enable_collision() for n in retired)
h = scene[prefix + 'TransferHoist']
assert h.wagon.static_mesh.get_name() == railcar.get_name()
assert xyz(h.console_face.get_world_location()) == [-1135, 210, 134]
assert xyz(h.wagon_body.get_scaled_box_extent()) == [504, 175, 206]

# Query the saved Editor world with the actual standing capsule dimensions. The
# same saved level must block the new cut, leave the east walk open and contain
# no duplicate wall/car in the cut after a lift. Ignore only the raised wagon
# when checking that last condition; the live fixture tests the moving component.
world = editor.get_editor_world()
solid_types = [unreal.ObjectTypeQuery.ECC_WORLD_STATIC, unreal.ObjectTypeQuery.ECC_WORLD_DYNAMIC]


def blockers(pos, ignored=()):
    found = unreal.SystemLibrary.capsule_overlap_components(world, unreal.Vector(*pos), 42, 96, solid_types,
                                                            unreal.PrimitiveComponent, list(ignored))
    return sorted({c.get_owner().get_actor_label() for c in (found or [])
                   if c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)
                   == unreal.CollisionResponseType.ECR_BLOCK})


section = [(-730, y, 116) for y in range(1050, 1851, 30)]
closed = {p[1]: blockers(p) for p in section if 1250 <= p[1] <= 1540}
assert all(names == [prefix + 'TransferHoist'] for names in closed.values()), closed
assert all(not blockers(p, (h,)) for p in section), 'Additional collision under the raised wagon'
east_walk = [(700, y, 116) for y in range(1290, 1611, 30)]
assert all(not blockers(p) for p in east_walk), 'Quiet east apron entry obstructed'
assert not blockers((-1300, 130, 116)), 'Booth approach obstructed'

out = Path(unreal.Paths.project_dir()).parent / '.environment-local/phase-06/remake'
out.mkdir(parents=True, exist_ok=True)
(out / 'yard-native.json').write_text(json.dumps(dict(actors=sorted(added), retired=sorted(retired), anchors=anchors,
    scout_ids=ids, console_cm=xyz(h.console_face.get_world_location()), lift_cm=310, closed_cut=closed,
    checked_clear_cut_samples=len(section), checked_clear_east_samples=len(east_walk)), indent=2), encoding='utf-8')
unreal.log('CR06_REMAKE_YARD PASS')
