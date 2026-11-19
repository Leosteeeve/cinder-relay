"""Import the three Phase06 visual derivatives and apply them to the active chapter."""
import json
from pathlib import Path

import unreal


project = Path(unreal.Paths.project_dir())
evidence = project.parent / '.environment-local/phase-06/finish-pass'
exports = evidence / 'exports'
asset_root = '/Game/Generated/Phase06/Meshes'
owner = 'CinderRelay.Phase06.VisualRefinement.v1'
assets = unreal.EditorAssetLibrary
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()


def asset(path):
    obj = assets.load_asset(path)
    assert obj, path
    return obj


def import_mesh(name, materials, skeleton=None):
    path = asset_root + '/' + name
    if assets.does_asset_exist(path):
        mesh = asset(path)
        assert assets.get_metadata_tag(mesh, 'CR.GeneratedBy') == owner, path
        return mesh
    ui = unreal.FbxImportUI()
    ui.automated_import_should_detect_type = False
    ui.import_mesh = True
    ui.import_as_skeletal = bool(skeleton)
    ui.import_animations = False
    ui.import_materials = False
    ui.import_textures = False
    ui.create_physics_asset = False
    if skeleton:
        ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
        ui.skeleton = skeleton
        data = ui.skeletal_mesh_import_data
    else:
        ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
        data = ui.static_mesh_import_data
        data.combine_meshes = True
        data.auto_generate_collision = False
    data.convert_scene = True
    data.convert_scene_unit = True
    task = unreal.AssetImportTask()
    task.filename = str(exports / (name + '.fbx'))
    task.destination_path = asset_root
    task.destination_name = name
    task.automated = True
    task.options = ui
    task.save = False
    tools.import_asset_tasks([task])
    mesh = asset(path)
    prop = 'materials' if skeleton else 'static_materials'
    slots = list(mesh.get_editor_property(prop))
    for slot in slots:
        key = str(slot.get_editor_property('imported_material_slot_name'))
        slot.set_editor_property('material_interface', materials[key])
    mesh.set_editor_property(prop, slots)
    assets.set_metadata_tag(mesh, 'CR.GeneratedBy', owner)
    return mesh


def material_slots(mesh, prop):
    return {str(slot.get_editor_property('imported_material_slot_name')):
            slot.get_editor_property('material_interface') for slot in mesh.get_editor_property(prop)}


def coords(vector):
    return [vector.x, vector.y, vector.z]


def size(mesh):
    return coords(mesh.get_bounds().box_extent * 2)


old_rook = asset('/Game/Generated/Phase051/Meshes/SM_CR051_Rook5')
old_warden = asset('/Game/Generated/Phase05/Animation/SK_CR05_AshWarden')
skeleton = old_warden.get_editor_property('skeleton')
rook = import_mesh('SM_CR06_Rook5Service', material_slots(old_rook, 'static_materials'))
warden = import_mesh('SK_CR06_AshWardenService', material_slots(old_warden, 'materials'), skeleton)
assert warden.get_editor_property('skeleton') == skeleton
palette = {f'CR06_{key}': asset('/Game/Generated/Phase052/Materials/MI_CR052_' + key)
           for key in ('Steel', 'Dark', 'Amber')}
plaque = import_mesh('SM_CR06_ServicePlaque', palette)
assert all(abs(a - b) < 1 for a, b in zip(size(rook), size(old_rook))), (size(rook), size(old_rook))
assert all(abs(a - b) < 1 for a, b in zip(size(plaque), (14.2, 240, 72))), size(plaque)
old_socket = old_rook.find_socket('SightAnchor_Iron')
new_socket = rook.find_socket('SightAnchor_Iron')
if not new_socket:
    new_socket = unreal.StaticMeshSocket(outer=rook)
    new_socket.set_editor_property('socket_name', 'SightAnchor_Iron')
    rook.add_socket(new_socket)
for prop in ('relative_location', 'relative_rotation', 'relative_scale'):
    new_socket.set_editor_property(prop, old_socket.get_editor_property(prop))

world = '/Game/Generated/Phase01B/Maps/L_CH01_Persistent'
assert levels.load_level(world)
scene = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
anchors = {n: coords(a.get_actor_location()) for n, a in scene.items() if isinstance(a, unreal.CRCheckpoint)}
new_bones = []
for name in ('CR02_Scout_1', 'CR02_Scout_2'):
    actor = scene[name]
    component = actor.mesh
    old_bones = [str(component.get_bone_name(i)) for i in range(component.get_num_bones())]
    for mode in ('idle', 'walk', 'alert', 'attack', 'hit', 'death'):
        assert actor.get_editor_property(mode + '_animation').get_editor_property('skeleton') == skeleton
    actor.modify()
    component.set_skeletal_mesh_asset(warden)
    new_bones = [str(component.get_bone_name(i)) for i in range(component.get_num_bones())]
    assert old_bones == new_bones and len(new_bones) == 19, (old_bones, new_bones)
    component.set_animation(actor.get_editor_property('idle_animation'))


def part(label, level, mesh, location, yaw, scale, material=None):
    a = scene.get(label)
    if a is None:
        assert levels.set_current_level_by_name('L_CH01_' + level)
        a = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*location))
        a.set_actor_label(label)
        a.tags = ['CR_Phase06_VisualRefinement']
    else:
        assert any(str(t) in ('CR_Phase06', 'CR_Phase06_VisualRefinement') for t in a.tags), label
    a.modify()
    a.set_actor_location(unreal.Vector(*location), False, False)
    a.set_actor_rotation(unreal.Rotator(yaw=yaw), False)
    a.set_actor_scale3d(unreal.Vector(*scale))
    c = a.static_mesh_component
    c.set_static_mesh(mesh)
    # The reading surface must use its own material slots, not the old cube override.
    for i in range(c.get_num_materials()):
        c.set_material(i, material if i == 0 else None)
    c.set_collision_profile_name('NoCollision')
    c.set_editor_property('can_ever_affect_navigation', False)
    a.set_actor_enable_collision(False)


def sign(label, position, text, font_size):
    a = scene[label]
    assert 'CR_Phase06' in [str(t) for t in a.tags]
    a.modify()
    a.set_actor_location(unreal.Vector(*position), False, False)
    a.text_render.set_text(text)
    a.text_render.set_world_size(font_size)
    a.text_render.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
    a.text_render.set_text_render_color(unreal.Color(238, 225, 186, 255))


part('CR06_DiagnosticNoticeBoard', 'Workshop', plaque, (2900, 681, 310), -90, (1, 1.43, 1.14))
sign('CR06_DiagnosticInstructions', (2900, 674, 315),
     'RELAY NINE / REPLACEMENT MODULE\n01 ROUTE   02 VERIFY   03 RELEASE', 17)
part('CR06_StopPlate', 'RelayBunker', plaque, (6046, 390, -401), 180, (1, .46, .63))
sign('CR06_MachineStop', (6039, 390, -397), 'MACHINERY STOP\nE / LATCH', 12)
part('CR06_ServiceWalkPlate', 'RelayBunker', plaque, (5601, -490, -255), 180, (.8, .66, .8))
sign('CR06_ServiceWalk', (5595, -490, -251), 'SERVICE WALK\nALWAYS OPEN', 14)
cube = asset('/Engine/BasicShapes/Cube')
part('CR06_StopPedestal', 'RelayBunker', cube, (6050, 390, -555), 0, (.4, .52, .9), palette['CR06_Steel'])
part('CR06_StopPlateMount', 'RelayBunker', cube, (6050, 390, -425), 0, (.18, .22, .62), palette['CR06_Steel'])

character = asset('/Game/Generated/Phase02/Blueprints/BP_CRCombatCharacter')
cdo = unreal.get_default_object(character.generated_class())
cdo.weapon_view.set_editor_property('rook_appearance', rook)
unreal.BlueprintEditorLibrary.compile_blueprint(character)
assert unreal.get_default_object(character.generated_class()).weapon_view.get_editor_property('rook_appearance') == rook
for item in (rook, warden, plaque, character):
    assert assets.save_loaded_asset(item)
for zone in ('RailYard', 'Workshop', 'RelayBunker'):
    assert levels.set_current_level_by_name('L_CH01_' + zone)
    assert levels.save_current_level()
assert levels.load_level(world)
saved = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
assert anchors == {n: coords(saved[n].get_actor_location()) for n in anchors}
for name in ('CR02_Scout_1', 'CR02_Scout_2'):
    assert saved[name].mesh.get_skeletal_mesh_asset() == warden
for name in ('CR06_DiagnosticNoticeBoard', 'CR06_StopPlate', 'CR06_ServiceWalkPlate'):
    assert saved[name].static_mesh_component.static_mesh == plaque
receipt = dict(anchors=anchors, warden_bones=new_bones, original_skeleton=skeleton.get_path_name(),
               old_rook_cm=size(old_rook), new_rook_cm=size(rook), plaque_cm=size(plaque))
(evidence / 'native-import.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
unreal.log('CR06_VISUAL_REFINEMENT PASS')
