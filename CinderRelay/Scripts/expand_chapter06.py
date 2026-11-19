"""Author the Chapter 01 expansion in the three existing streamed levels."""
import json
from pathlib import Path

import unreal


levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assets = unreal.EditorAssetLibrary
world = '/Game/Generated/Phase01B/Maps/L_CH01_Persistent'
tag = 'CR_Phase06_Expanded'
assert levels.load_level(world)
scene = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
cube = assets.load_asset('/Engine/BasicShapes/Cube')
palette = {name: assets.load_asset('/Game/Generated/Phase052/Materials/MI_CR052_' + name)
           for name in ('Steel', 'Paint', 'Dark', 'Amber', 'Pale')}
assert all(palette.values())
added = {}


def state(a):
    p = a.get_actor_location()
    r = a.get_actor_rotation()
    s = a.get_actor_scale3d()
    return [round(v, 6) for v in (p.x, p.y, p.z, r.pitch, r.yaw, r.roll, s.x, s.y, s.z)]


anchors = {name: state(actor) for name, actor in scene.items() if isinstance(actor, unreal.CRCheckpoint)}


def select(zone):
    assert levels.set_current_level_by_name('L_CH01_' + zone)


def actor(name, cls, pos, yaw=0):
    label = 'CR06X_' + name
    a = scene.get(label)
    if a:
        assert tag in [str(t) for t in a.tags] and isinstance(a, cls), label
    else:
        a = actors.spawn_actor_from_class(cls, unreal.Vector(*pos))
        assert a
        a.set_actor_label(label)
        a.tags = [tag]
        scene[label] = a
    a.modify()
    a.set_actor_location(unreal.Vector(*pos), False, False)
    a.set_actor_rotation(unreal.Rotator(yaw=yaw), False)
    added[label] = a
    return a


def box(name, pos, size, material='Paint', solid=True):
    a = actor(name, unreal.StaticMeshActor, pos)
    c = a.static_mesh_component
    c.set_static_mesh(cube)
    c.set_material(0, palette[material])
    c.set_collision_profile_name('BlockAll' if solid else 'NoCollision')
    c.set_editor_property('can_ever_affect_navigation', False)
    a.set_actor_enable_collision(solid)
    a.set_actor_scale3d(unreal.Vector(*(n / 100 for n in size)))
    return a


def wall_x(name, left, right, y, floor, height=430, material='Paint'):
    return box(name, ((left + right) / 2, y, floor + height / 2), (right - left, 36, height), material)


def wall_y(name, x, lower, upper, floor, height=430, material='Paint'):
    return box(name, (x, (upper + lower) / 2, floor + height / 2), (36, upper - lower, height), material)


def aperture(name, x, y, floor, span):
    for side in (-1, 1):
        box(name + 'Jamb' + str(side), (x + side * span / 2, y, floor + 175), (32, 82, 350), 'Steel')
    box(name + 'Lintel', (x, y, floor + 369), (span + 32, 88, 38), 'Amber')


def sign(name, pos, text, yaw=90, width=315, height=70, font_size=21):
    # A dark non-colliding face mounted to the enclosure. Text remains editable.
    x, y, z = pos
    facing = 1 if yaw == 90 else -1
    box(name + 'Plate', (x, y - facing * 4, z), (width, 7, height), 'Dark', False)
    t = actor(name, unreal.TextRenderActor, pos, yaw).text_render
    t.set_text(text)
    t.set_world_size(font_size)
    t.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    t.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
    t.set_text_render_color(unreal.Color(239, 223, 184, 255))


def light(name, pos, color, intensity=450):
    c = actor(name, unreal.PointLight, pos).light_component
    c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_intensity_units(unreal.LightUnits.LUMENS)
    c.set_intensity(intensity)
    c.set_light_color(unreal.LinearColor(*color, 1))
    c.set_editor_property('attenuation_radius', 1050)
    c.set_editor_property('cast_shadows', False)


def hide(name):
    a = scene[name]
    a.modify()
    a.set_actor_hidden_in_game(True)
    a.set_actor_enable_collision(False)
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        c.set_visibility(False)
        c.set_editor_property('can_ever_affect_navigation', False)


def relocate(name, pos, yaw=None):
    a = scene[name]
    a.modify()
    a.set_actor_location(unreal.Vector(*pos), False, False)
    if yaw is not None:
        a.set_actor_rotation(unreal.Rotator(yaw=yaw), False)
    return a


def enclosure(name, left, right, far, near, floor):
    length = near - far
    center = ((left + right) / 2, (near + far) / 2)
    box(name + 'Floor', (*center, floor - 20), (right - left, length, 40), 'Steel')
    box(name + 'Ceiling', (*center, floor + 445), (right - left, length, 36), 'Dark')
    wall_y(name + 'West', left, far, near, floor)
    wall_y(name + 'East', right, far, near, floor)
    wall_x(name + 'End', left, right, far, floor)


def room_kit(name, x, y, floor, width, color):
    # Overhead truss, wall stanchions and a maintenance light establish a repeated structural bay.
    box(name + 'Rib', (x, y, floor + 414), (width, 64, 45), 'Steel')
    for side in (-1, 1):
        box(name + 'Column' + str(side), (x + side * (width / 2 - 28), y, floor + 212), (48, 66, 424), 'Steel')
    light(name + 'Light', (x, y, floor + 340), color, 630)


def station_mount(name, pos):
    x, y, z = pos
    box(name + 'Stand', (x, y - 9, z - 110), (80, 50, 160), 'Steel')


select('RailYard')
hide('CR_YardBoundary1400')
hide('CR051_Perimeter1_4')
wall_x('YardNorthWest', -2000, 415, 1400, 0, 320)
wall_x('YardNorthEast', 985, 1600, 1400, 0, 320)
box('SignalApron', (-150, 2370, -24), (3150, 1960, 48), 'Steel')
wall_y('ApronWest', -1710, 1390, 3350, 0, 350)
wall_y('ApronEast', 1420, 1390, 3350, 0, 350)
wall_x('ApronNorth', -1710, 1420, 3350, 0, 350)
wall_x('ApronSealWest', -1710, 415, 1426, 0, 320)
wall_x('ApronSealEast', 985, 1420, 1426, 0, 320)
aperture('ApronEntrance', 700, 1400, 0, 510)
sign('ApronRoute', (700, 1363, 359), 'SIGNAL STORE  /  OPTIONAL SALVAGE', -90, 478, 55, 18)
wall_x('StoreFrontWest', -1040, -690, 2280, 0, 320)
wall_x('StoreFrontEast', -220, 270, 2280, 0, 320)
wall_y('StoreWest', -1040, 2280, 3130, 0, 320)
wall_y('StoreEast', 270, 2280, 3130, 0, 320)
wall_x('StoreBack', -1040, 270, 3130, 0, 320)
box('StoreRoof', (-385, 2710, 342), (1360, 920, 48), 'Dark')
aperture('StoreDoor', -455, 2280, 0, 430)
sign('StoreSign', (-455, 2234, 322), 'SURVEY EQUIPMENT STORE', -90, 425, 60, 20)
light('StoreUtility', (-450, 2720, 255), (1, .73, .43), 725)
relocate('CR03_YardCache', (-480, 2910, 72))
relocate('CR03_YardCacheStand', (-480, 2910, 36))
relocate('CR03_CacheSign', (-480, 2964, 145), -90)

select('Workshop')
hide('CR_WorkshopSide-700')
for name in ('CR05_WorkshopWall0_-685', 'CR05_WorkshopWall1_-685', 'CR05_WorkshopWall3_-685', 'CR05_WorkshopWall4_-685'):
    hide(name)
wall_x('WorkshopWestStub', 1600, 1750, -700, 0, 500)
wall_x('WorkshopCenterStub', 2190, 2920, -700, 0, 500)
wall_x('WorkshopEastStub', 3400, 3600, -700, 0, 500)
for name, x, span, text in (('TestHall', 3160, 460, 'MODULE TEST HALL'), ('TestReturn', 1970, 420, 'RETURN WALK')):
    aperture(name, x, -700, 0, span)
    box(name + 'SealedHead', (x, -700, 444), (span + 22, 38, 112), 'Paint')
    sign(name + 'Sign', (x, -646, 413), text, width=span - 30)
enclosure('TestAnnex', 1600, 3600, -5650, -680, 0)
wall_y('TestReturnSpine', 2180, -4330, -700, 0)
wall_x('TestBayOneScreen', 2180, 2910, -2140, 0)
wall_x('TestBayTwoScreen', 2800, 3600, -3890, 0)
for index, (x, y, title) in enumerate(((3190, -1700, '01   BENCH SUPPLY'),
                                        (2500, -3350, '02   LOAD TEST'),
                                        (2480, -5100, '03   MODULE RELEASE'))):
    pos = (x, y, 130)
    relocate('CR06_Diagnostic' + str(index), pos, 90)
    station_mount('TestStation' + str(index), pos)
    box('TestBackplate' + str(index), (x, y - 33, 200), (490, 30, 400), 'Paint')
    sign('TestHeading' + str(index), (x, y - 13, 287), title, width=420)
    light('TestSpot' + str(index), (x, y + 160, 285), (1, .69, .41))
for index, y in enumerate((-1120, -2620, -4360, -5300)):
    room_kit('TestRib' + str(index), 2590, y, 0, 1930, (.75, .83, 1))
for index, y in enumerate(range(-1100, -5151, -450)):
    box('TestWalk' + str(index), (1910, y, 1), (30, 198, 2), 'Amber', False)
    if index % 3 == 0:
        light('TestReturnLight' + str(index), (1910, y, 330), (.61, .78, .82), 335)

select('RelayBunker')
hide('CR_BunkerSide-650')
wall_x('RelayWestStub', 5400, 5650, -650, -600, 500)
wall_x('RelayCenterStub', 6060, 6300, -650, -600, 500)
wall_x('RelayEastStub', 6750, 7200, -650, -600, 500)
for name, x, span, text in (('RelayLower', 6525, 430, 'AUXILIARY SERVICE'), ('RelayReturn', 5850, 390, 'RETURN WALK')):
    aperture(name, x, -650, -600, span)
    box(name + 'SealedHead', (x, -650, -156), (span + 28, 38, 112), 'Paint')
    sign(name + 'Sign', (x, -594, -187), text, width=span - 15)
enclosure('RelayAnnex', 5400, 7200, -5980, -630, -600)
wall_y('RelayReturnSpine', 6170, -4830, -650, -600)
wall_x('RelayServiceScreen', 6170, 6420, -2940, -600)
panel = assets.load_asset('/Game/Generated/Phase06/Meshes/SM_CR06_DiagnosticPanel')
for index, (x, y, title) in enumerate(((6710, -2280, 'A   PRIME SERVICE BUS'),
                                        (6710, -5350, 'B   RELEASE INTERLOCK'))):
    pos = (x, y, -470)
    a = actor('RelayStation' + str(index), unreal.CRMaintenanceStation, pos, 90)
    a.tags = [tag, 'CR06RelayService']
    a.set_editor_property('step', index)
    a.panel.set_static_mesh(panel)
    a.display.set_editor_property('relative_location', unreal.Vector(28, 0, 58))
    a.display.set_text(title)
    station_mount('RelayStation' + str(index), pos)
    box('RelayBackplate' + str(index), (x, y - 33, -400), (540, 30, 400), 'Paint')
    sign('RelayHeading' + str(index), (x, y - 13, -310), title, width=450)
    light('RelaySpot' + str(index), (x, y + 185, -300), (.48, .83, 1), 560)
for index, y in enumerate((-1250, -2950, -4480, -5680)):
    room_kit('RelayRib' + str(index), 6300, y, -600, 1740, (.47, .73, .86))
for index, y in enumerate(range(-1150, -5510, -450)):
    box('RelayWalk' + str(index), (5840, y, -599), (30, 198, 2), 'Amber', False)
    if index % 3 == 0:
        light('RelayReturnLight' + str(index), (5840, y, -260), (.61, .78, .82), 435)

for zone in ('RailYard', 'Workshop', 'RelayBunker'):
    select(zone)
    assert levels.save_current_level()
assert levels.load_level(world)
actual = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
assert anchors == {n: state(actual[n]) for n in anchors}, 'Checkpoint transform drift'
assert all(label in actual for label in added)
assert all(actual['CR06_Diagnostic' + str(i)].get_actor_location().y < -1000 for i in range(3))
out = Path(unreal.Paths.project_dir()).parent / '.environment-local/phase-06/expanded'
out.mkdir(parents=True, exist_ok=True)
(out / 'layout.json').write_text(json.dumps(dict(new_actors=len(added), anchors=anchors,
    test_annex_m=[20, 49.7], relay_annex_m=[18, 53.5], signal_apron_m=[31.5, 19.6]), indent=2))
unreal.log('CR06_EXPANSION_LAYOUT PASS')
