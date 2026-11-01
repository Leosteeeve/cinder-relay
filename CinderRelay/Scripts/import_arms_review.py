"""Import the isolated Phase053 anatomical review kit. Never activates gameplay assets."""
import json
from pathlib import Path
import unreal

project = Path(unreal.Paths.project_dir())
evidence = project.parent / '.environment-local/phase-05-3'
root = '/Game/Generated/Phase053/Review'
owner = 'CinderRelay.Phase053.Review.v1'
assets = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
lib = unreal.MaterialEditingLibrary


def owned(path):
    result = assets.load_asset(path) if assets.does_asset_exist(path) else None
    if result:
        assert assets.get_metadata_tag(result, 'CR.GeneratedBy') == owner, path
    return result


def save(asset):
    assets.set_metadata_tag(asset, 'CR.GeneratedBy', owner)
    assert assets.save_loaded_asset(asset)
    return asset


textures = {}
for suffix in ('BaseColor', 'Normal'):
    name = 'T_CR053_Arms_' + suffix
    texture = owned(root + '/Textures/' + name)
    if not texture:
        task = unreal.AssetImportTask()
        task.filename = str(project / 'ArtSource/Blender/Phase053/Textures' / (name + '.png'))
        task.destination_path = root + '/Textures'
        task.destination_name = name
        task.automated = True
        task.save = True
        tools.import_asset_tasks([task])
        texture = assets.load_asset(root + '/Textures/' + name)
        assert texture
        texture.set_editor_property('srgb', suffix == 'BaseColor')
        if suffix == 'Normal':
            texture.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP)
            texture.set_editor_property('flip_green_channel', True)
        save(texture)
    textures[suffix] = texture

materials = {}
for name, roughness in [('Skin', .64), ('Glove', .76), ('Sleeve', .86)]:
    material = owned(root + '/Materials/M_CR053_' + name)
    if not material:
        material = tools.create_asset('M_CR053_' + name, root + '/Materials', unreal.Material, unreal.MaterialFactoryNew())
        for channel, prop in [('BaseColor', unreal.MaterialProperty.MP_BASE_COLOR), ('Normal', unreal.MaterialProperty.MP_NORMAL)]:
            sample = lib.create_material_expression(material, unreal.MaterialExpressionTextureSample)
            sample.set_editor_property('texture', textures[channel])
            sample.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if channel == 'Normal' else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
            result = sample
            output = 'RGB'
            if channel == 'Normal':
                neutral = lib.create_material_expression(material, unreal.MaterialExpressionConstant3Vector)
                neutral.set_editor_property('constant', unreal.LinearColor(0, 0, 1, 1))
                result = lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate)
                result.set_editor_property('const_alpha', .45)
                lib.connect_material_expressions(neutral, '', result, 'A')
                lib.connect_material_expressions(sample, 'RGB', result, 'B')
                output = ''
            assert lib.connect_material_property(result, output, prop)
        value = lib.create_material_expression(material, unreal.MaterialExpressionConstant)
        value.set_editor_property('r', roughness)
        lib.connect_material_property(value, '', unreal.MaterialProperty.MP_ROUGHNESS)
        lib.set_material_usage(material, unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
        lib.recompile_material(material)
        save(material)
    materials[name] = material

mesh = owned(root + '/Animation/SK_CR053_EliasArms')
if not mesh:
    # Reject foreign same-name helper assets before FBX import can reuse them.
    owned(root + '/Animation/SK_CR053_EliasArms_Skeleton')
    owned(root + '/Animation/SK_CR053_EliasArms_Anim')
    ui = unreal.FbxImportUI()
    ui.automated_import_should_detect_type = False
    ui.import_mesh = True
    ui.import_as_skeletal = True
    ui.import_animations = True
    ui.import_materials = False
    ui.import_textures = False
    ui.create_physics_asset = False
    ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
    ui.skeletal_mesh_import_data.convert_scene = True
    ui.skeletal_mesh_import_data.convert_scene_unit = True
    ui.skeletal_mesh_import_data.force_front_x_axis = False
    ui.anim_sequence_import_data.set_editor_property('use_default_sample_rate', False)
    ui.anim_sequence_import_data.set_editor_property('custom_sample_rate', 60)
    task = unreal.AssetImportTask()
    task.filename = str(evidence / 'exports/SK_CR053_EliasArms.fbx')
    task.destination_path = root + '/Animation'
    task.destination_name = 'SK_CR053_EliasArms'
    task.options = ui
    task.automated = True
    task.save = True
    tools.import_asset_tasks([task])
    assert task.imported_object_paths
    for path in task.imported_object_paths:
        save(assets.load_asset(path))
    mesh = assets.load_asset(root + '/Animation/SK_CR053_EliasArms')
    assert mesh
slots = list(mesh.get_editor_property('materials'))
assert len(slots) == 3, str(slots)
for slot in slots:
    key = str(slot.get_editor_property('imported_material_slot_name'))
    matches = [name for name in materials if name.lower() in key.lower()]
    assert len(matches) == 1, key
    slot.set_editor_property('material_interface', materials[matches[0]])
mesh.set_editor_property('materials', slots)
save(mesh)
animation = owned(root + '/Animation/AN_CR053_AnatomyReview')
if not animation:
    candidate = owned(root + '/Animation/SK_CR053_EliasArms_Anim')
    assert isinstance(candidate, unreal.AnimSequence), 'Expected owned FBX review animation is missing'
    assert abs(candidate.sequence_length - 3) < .02, candidate.sequence_length
    assert assets.rename_asset(candidate.get_path_name(), root + '/Animation/AN_CR053_AnatomyReview')
    animation = save(assets.load_asset(root + '/Animation/AN_CR053_AnatomyReview'))
assert abs(animation.sequence_length - 3) < .02, animation.sequence_length

levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
map_path = root + '/Maps/L_CR053_ArmsReview'
if assets.does_asset_exist(map_path):
    # Never hold a Python reference to a separately loaded UWorld across LoadLevel.
    # UE must release the old world/package during the map transition.
    assert levels.load_level(map_path)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert assets.get_metadata_tag(world, 'CR.GeneratedBy') == owner, map_path
else:
    assert levels.new_level(map_path)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    save(world)
existing = {a.get_actor_label(): a for a in actors.get_all_level_actors()}


def actor(label, cls, position):
    result = existing.get(label)
    if result:
        assert 'CR053_Review' in [str(t) for t in result.tags], label
    else:
        result = actors.spawn_actor_from_class(cls, unreal.Vector(*position))
        result.set_actor_label(label)
        result.tags = ['CR053_Review']
    return result


hands = actor('CR053_AnatomyCandidate', unreal.SkeletalMeshActor, (0, 0, 100))
component = hands.skeletal_mesh_component
component.set_skeletal_mesh_asset(mesh)
component.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
component.set_animation(animation)
component.set_update_animation_in_editor(True)
component.play(False)
component.set_play_rate(0)
component.set_position(.5, False)
component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
bones = [str(component.get_bone_name(i)) for i in range(component.get_num_bones())]
assert all(any(n.startswith(prefix) for n in bones) for prefix in ('wrist', 'finger1', 'finger5', 'lowerarm02')), bones
dimensions = mesh.get_imported_bounds().box_extent * 2
assert 80 < max(dimensions.x, dimensions.y, dimensions.z) < 140, str(dimensions)
floor = actor('CR053_ReviewFloor', unreal.StaticMeshActor, (0, 0, 25))
floor.static_mesh_component.set_static_mesh(assets.load_asset('/Engine/BasicShapes/Plane'))
floor.set_actor_scale3d(unreal.Vector(8, 8, 1))
floor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
stage = owned(root + '/Materials/M_CR053_ReviewStage')
if not stage:
    stage = tools.create_asset('M_CR053_ReviewStage', root + '/Materials', unreal.Material, unreal.MaterialFactoryNew())
    color = lib.create_material_expression(stage, unreal.MaterialExpressionConstant3Vector)
    color.set_editor_property('constant', unreal.LinearColor(.035, .041, .045, 1))
    lib.connect_material_property(color, '', unreal.MaterialProperty.MP_BASE_COLOR)
    roughness = lib.create_material_expression(stage, unreal.MaterialExpressionConstant)
    roughness.set_editor_property('r', .85)
    lib.connect_material_property(roughness, '', unreal.MaterialProperty.MP_ROUGHNESS)
    lib.recompile_material(stage)
    save(stage)
floor.static_mesh_component.set_material(0, stage)
for label, pos, intensity, color, size in [
    ('Key', (90, -100, 200), 1800, (1, .90, .81), 110),
    ('Fill', (30, 110, 150), 1400, (.80, .90, 1), 120),
    ('Rim', (-100, -5, 185), 1600, (1, 1, 1), 90),
]:
    light = actor('CR053_' + label, unreal.RectLight, pos)
    light.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(light.get_actor_location(), unreal.Vector(-10, 0, 65)), False)
    lc = light.light_component
    lc.set_mobility(unreal.ComponentMobility.MOVABLE)
    lc.set_intensity_units(unreal.LightUnits.LUMENS)
    lc.set_intensity(intensity)
    lc.set_light_color(unreal.LinearColor(*color, 1))
    lc.set_editor_property('source_width', size)
    lc.set_editor_property('source_height', size)
    lc.set_editor_property('attenuation_radius', 800)
post = actor('CR053_Exposure', unreal.PostProcessVolume, (0, 0, 0))
post.set_editor_property('unbound', True)
settings = post.get_editor_property('settings')
for key, value in [('override_auto_exposure_min_brightness', True), ('override_auto_exposure_max_brightness', True), ('auto_exposure_min_brightness', 7.0), ('auto_exposure_max_brightness', 7.0)]:
    settings.set_editor_property(key, value)
post.set_editor_property('settings', settings)
camera = actor('CR053_ReviewCamera', unreal.CameraActor, (135, -100, 120))
camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(), unreal.Vector(-10, 0, 65)), False)
camera.camera_component.set_field_of_view(60)
actors.clear_actor_selection_set()
assert levels.save_current_level()
save(world)
(evidence / 'arms-import.json').write_text(json.dumps({
    'mesh': mesh.get_path_name(), 'animation': animation.get_path_name(), 'map': map_path,
    'duration_seconds': animation.sequence_length, 'bones': bones, 'bounds_cm': [dimensions.x, dimensions.y, dimensions.z],
    'materials': [str(s.get_editor_property('imported_material_slot_name')) for s in slots],
    'activated_in_gameplay': False, 'owner_visual_approval': False,
}, indent=2), encoding='utf-8')
unreal.log('CR053_ARMS_IMPORT_PASS')
if '-cr053capturereview' in unreal.SystemLibrary.get_command_line().lower():
    # Stay in this world; the capture script must not LoadLevel with our UWorld reference alive.
    import runpy
    runpy.run_path(str(project / 'Scripts/review_arms.py'), init_globals={'CR053_MAP_ALREADY_OPEN': True})
else:
    unreal.SystemLibrary.quit_editor()
