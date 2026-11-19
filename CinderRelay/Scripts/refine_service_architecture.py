"""Import and place the Phase06 service architecture kit in the existing streamed maps."""
import json
import hashlib
from pathlib import Path

import unreal


levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
assets = unreal.EditorAssetLibrary
project = Path(unreal.Paths.project_dir())
out = project.parent / '.environment-local/phase-06/refinement'
exports = out / 'exports'
world = '/Game/Generated/Phase01B/Maps/L_CH01_Persistent'
root = '/Game/Generated/Phase06/Meshes/ServiceArchitecture'
owner = 'CinderRelay.Phase06.ServiceArchitecture'
tag = 'CR_Phase06_ServiceArchitecture'


def asset(path):
    result = assets.load_asset(path)
    assert result, path
    return result


palette = {f'CR06A_{name}': asset('/Game/Generated/Phase052/Materials/MI_CR052_' + name)
           for name in ('Paint', 'Steel', 'Dark', 'Amber', 'Pale')}
kit = {}
stats = {}
for spec in json.loads((exports / 'mesh-manifest.json').read_text()):
    name = spec['name']
    path = root + '/' + name
    source = exports / (name + '.fbx')
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    mesh = assets.load_asset(path) if assets.does_asset_exist(path) else None
    if mesh:
        assert assets.get_metadata_tag(mesh, 'CR.GeneratedBy') == owner, path
    if not mesh or assets.get_metadata_tag(mesh, 'CR.SourceFbxSha256') != digest:
        ui = unreal.FbxImportUI()
        ui.automated_import_should_detect_type = False
        ui.import_mesh = True
        ui.import_as_skeletal = False
        ui.import_animations = False
        ui.import_materials = False
        ui.import_textures = False
        ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
        ui.static_mesh_import_data.combine_meshes = True
        ui.static_mesh_import_data.auto_generate_collision = False
        ui.static_mesh_import_data.convert_scene = True
        ui.static_mesh_import_data.convert_scene_unit = True
        task = unreal.AssetImportTask()
        task.filename = str(source)
        task.destination_path = root
        task.destination_name = name
        task.options = ui
        task.automated = True
        task.replace_existing = mesh is not None
        task.replace_existing_settings = True
        task.save = False
        tools.import_asset_tasks([task])
        mesh = asset(path)
        materials = list(mesh.get_editor_property('static_materials'))
        for slot in materials:
            key = str(slot.get_editor_property('imported_material_slot_name'))
            assert key in palette, key
            slot.set_editor_property('material_interface', palette[key])
        mesh.set_editor_property('static_materials', materials)
        assets.set_metadata_tag(mesh, 'CR.GeneratedBy', owner)
        assets.set_metadata_tag(mesh, 'CR.SourceFbxSha256', digest)
        assert assets.save_loaded_asset(mesh)
    kit[name.removeprefix('SM_CR06_')] = mesh
    extents = mesh.get_bounds().box_extent * 2
    dimensions = [extents.x, extents.y, extents.z]
    assert all(abs(a-b) < 1 for a,b in zip(sorted(dimensions), sorted(spec['dimensions_cm']))), (name, dimensions)
    stats[name] = dict(dimensions_cm=dimensions, source_triangles=spec['triangles'])

assert levels.load_level(world)
scene = {a.get_actor_label(): a for a in actors.get_all_level_actors()}


def position(actor):
    p = actor.get_actor_location()
    return (p.x, p.y, p.z)


anchors = {name: position(a) for name, a in scene.items() if isinstance(a, unreal.CRCheckpoint)}
added = set()
plaque = asset('/Game/Generated/Phase06/Meshes/SM_CR06_ServicePlaque')
cube = asset('/Engine/BasicShapes/Cube')


def select(zone):
    assert levels.set_current_level_by_name('L_CH01_' + zone)


def get_actor(name, cls, pos, yaw):
    name = 'CR06A_' + name
    a = scene.get(name)
    if a is None:
        a = actors.spawn_actor_from_class(cls, unreal.Vector(*pos))
        assert a, name
        a.set_actor_label(name)
        a.tags = [tag]
        scene[name] = a
    assert isinstance(a, cls) and tag in [str(t) for t in a.tags], name
    a.modify()
    a.set_actor_location(unreal.Vector(*pos), False, False)
    a.set_actor_rotation(unreal.Rotator(yaw=yaw), False)
    added.add(name)
    return a


def prop(name, model, pos, yaw=0, scale=(1, 1, 1), structural=False):
    a = get_actor(name, unreal.StaticMeshActor, pos, yaw)
    a.set_actor_scale3d(unreal.Vector(*scale))
    a.set_actor_enable_collision(False)
    c = a.static_mesh_component
    c.set_static_mesh(kit[model] if isinstance(model, str) else model)
    c.set_collision_profile_name('NoCollision')
    c.set_editor_property('can_ever_affect_navigation', False)
    c.set_editor_property('visible_in_ray_tracing', structural)
    c.set_editor_property('affect_distance_field_lighting', structural)
    return a


def suppress(name):
    a = scene['CR06X_' + name]
    a.modify()
    c = a.static_mesh_component
    c.set_visibility(False)
    c.set_editor_property('cast_hidden_shadow', False)


def portal(name, pos, span):
    prop(name, 'ServicePortal', pos, scale=(span / 456, 1, 1))


def sign(name, pos, yaw, words, return_walk=False, support_z=None):
    # The existing plaque's long axis is local Y and the reading face is +X.
    prop(name + 'Plate', plaque, pos, yaw, scale=(.65, 1.50, .73))
    direction = 1 if yaw == 90 else -1
    front = (pos[0], pos[1] + direction*9, pos[2])
    text = get_actor(name, unreal.TextRenderActor, front, yaw).text_render
    text.set_text(words)
    text.set_world_size(22)
    text.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
    text.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
    text.set_text_render_color(unreal.Color(255, 198, 97) if return_walk else unreal.Color(182, 233, 240))
    if support_z is not None:
        for side in (-1, 1):
            base = pos[2] + 21
            mount = prop(f'{name}Support{side}', cube, (pos[0]+side*122, pos[1], (base+support_z)/2),
                         scale=(.045, .045, (support_z-base)/100))
            mount.static_mesh_component.set_material(0, palette['CR06A_Steel'])


def retire_sign(name):
    for suffix in ('', 'Plate'):
        a = scene['CR06X_' + name + suffix]
        a.modify()
        a.set_actor_hidden_in_game(True)
        for component in a.get_components_by_class(unreal.PrimitiveComponent):
            component.set_visibility(False)


def light(name, radius, indirect):
    a = scene['CR06X_' + name]
    a.modify()
    c = a.light_component
    c.set_editor_property('attenuation_radius', radius)
    c.set_editor_property('indirect_lighting_intensity', indirect)


select('RailYard')
suppress('StoreRoof')
prop('StoreRoof', 'SignalStoreRoof', (-385, 2710, 321), structural=True)
for index, y in enumerate((2415, 2653, 2891, 3075)):
    prop(f'StoreCladdingW{index}', 'SignalStoreCladding', (-1062, y, 158), 90,
         scale=((.56 if index == 3 else 1), 1, 1))
for index, x in enumerate((-864, -84, 154)):
    prop(f'StoreCladdingS{index}', 'SignalStoreCladding', (x, 2256, 158))
portal('StorePortal', (-455, 2280, 0), 430)
light('StoreUtility', 530, .45)
sign('SalvageOptional', (76, 2239, 192), -90, 'OPTIONAL   /   SALVAGE')

select('Workshop')
portal('WorkshopEntrance', (3160, -700, 0), 460)
portal('WorkshopReturn', (1970, -700, 0), 420)
for index, (kind, x, y) in enumerate((('Supply', 3190, -1700), ('Load', 2500, -3350), ('Cradle', 2480, -5100))):
    suppress(f'TestBackplate{index}')
    prop(kind + 'Bulkhead', kind + 'Bulkhead', (x, y-33, 0), structural=True)
    light(f'TestSpot{index}', 560, .45)
for index in range(4):
    light(f'TestRib{index}Light', 740, .40)
for index in (0, 3, 6, 9):
    light(f'TestReturnLight{index}', 660, .38)
retire_sign('TestHallSign')
sign('TestHallEntry', (3158, -638, 419), 90, 'MODULE TEST HALL   /   01')
sign('TestToward02', (3195, -2095, 299), 90, '02   /   LOAD TEST', support_z=429)
sign('TestToward03', (2530, -3824, 299), 90, '03   /   MODULE RELEASE', support_z=429)
sign('WorkshopFarReturn', (1905, -5623, 245), 90, 'AMBER RETURN   /   BENCH', True)
sign('WorkshopNearReturn', (1920, -752, 386), -90, 'EXIT   /   MODULE BENCH', True)

select('RelayBunker')
portal('AuxiliaryEntrance', (6525, -650, -600), 430)
portal('AuxiliaryReturn', (5850, -650, -600), 390)
for index, (kind, y) in enumerate((('Bus', -2280), ('Interlock', -5350))):
    suppress(f'RelayBackplate{index}')
    prop(kind + 'Bulkhead', kind + 'Bulkhead', (6710, y-33, -600), structural=True)
    light(f'RelaySpot{index}', 550, .40)
for index in range(4):
    light(f'RelayRib{index}Light', 760, .45)
for index in (0, 3, 6, 9):
    light(f'RelayReturnLight{index}', 670, .37)
retire_sign('RelayLowerSign')
sign('BusEntry', (6525, -588, -179), 90, 'AUXILIARY SERVICE   /   A')
sign('InterlockRoute', (6870, -2930, -293), 90, 'B   /   RELEASE INTERLOCK', support_z=-180)
sign('RelayFarReturn', (5840, -5953, -353), 90, 'AMBER RETURN   /   STOP', True)
sign('RelayNearReturn', (5850, -702, -214), -90, 'EXIT   /   MACHINERY STOP', True)

for zone in ('RailYard', 'Workshop', 'RelayBunker'):
    select(zone)
    assert levels.save_current_level()
assert levels.load_level(world)
scene = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
assert anchors == {name: position(scene[name]) for name in anchors}
assert all(label in scene for label in added)
assert all(not scene[label].get_actor_enable_collision() for label in added if isinstance(scene[label], unreal.StaticMeshActor))
(out / 'architecture-native.json').write_text(json.dumps(dict(assets=stats, actors=sorted(added), checkpoints=anchors), indent=2))
unreal.log('CR06_SERVICE_ARCHITECTURE PASS')
