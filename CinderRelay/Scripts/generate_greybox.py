"""Create owned Phase 01A assets with the actual Unreal Editor (UE 5.8).

Run from a fresh Editor commandlet; see docs/WINDOWS_SETUP.md. Never deletes
assets or actors. Stable labels and asset metadata prevent duplicate generation
and refuse collisions with content not owned by this script.
"""
import json
import math
from pathlib import Path
import unreal

ROOT = '/Game/Generated/Phase01A'
MAP = ROOT + '/Maps/L_CH01_Greybox'
OWNER = 'CinderRelay.Phase01A.v1'
META = 'CR.GeneratedBy'
TAG = 'CR_Phase01A_Generated'
assets = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
created_assets = []


def owned_asset(path, asset_class, factory):
    if assets.does_asset_exist(path):
        asset = assets.load_asset(path)
        if str(assets.get_metadata_tag(asset, META)) != OWNER:
            raise RuntimeError('Refusing to overwrite unowned asset: ' + path)
        if not isinstance(asset, asset_class):
            raise RuntimeError('Existing asset has wrong class: ' + path)
        return asset, False
    folder, name = path.rsplit('/', 1)
    asset = tools.create_asset(name, folder, asset_class, factory)
    if not asset:
        raise RuntimeError('Asset creation failed: ' + path)
    assets.set_metadata_tag(asset, META, OWNER)
    created_assets.append(path)
    return asset, True


def save(asset):
    if not assets.save_loaded_asset(asset, only_if_is_dirty=False):
        raise RuntimeError('Could not save ' + asset.get_path_name())


def material(name, color, emissive=False):
    mat, new = owned_asset(ROOT + '/Materials/' + name, unreal.Material, unreal.MaterialFactoryNew())
    if new:
        node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector)
        node.set_editor_property('constant', unreal.LinearColor(*color, 1.0))
        unreal.MaterialEditingLibrary.connect_material_property(node, '', unreal.MaterialProperty.MP_BASE_COLOR)
        rough = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant)
        rough.set_editor_property('r', 0.82)
        unreal.MaterialEditingLibrary.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
        if emissive:
            unreal.MaterialEditingLibrary.connect_material_property(node, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        unreal.MaterialEditingLibrary.recompile_material(mat)
        save(mat)
    return mat


def data_asset(name, cls):
    factory = unreal.DataAssetFactory()
    factory.set_editor_property('data_asset_class', cls)
    return owned_asset(ROOT + '/Input/' + name, cls, factory)


def blueprint(name, parent):
    factory = unreal.BlueprintFactory()
    factory.set_editor_property('parent_class', parent)
    bp, new = owned_asset(ROOT + '/Blueprints/' + name, unreal.Blueprint, factory)
    return bp


def finish_blueprint(bp):
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    save(bp)
    return unreal.load_class(None, bp.get_path_name() + '_C')


def main():
    # The commandlet is expected to start without a user editing session.
    # Refuse an unowned existing map before touching any associated content.
    if assets.does_asset_exist(MAP):
        existing = assets.load_asset(MAP)
        if str(assets.get_metadata_tag(existing, META)) != OWNER:
            raise RuntimeError('Map exists and is not owned. Nothing may replace it: ' + MAP)

    mats = {
        'concrete': material('M_Concrete', (0.24, 0.28, 0.30)),
        'wall': material('M_PaleMetal', (0.44, 0.47, 0.44)),
        'rust': material('M_RustedIron', (0.32, 0.12, 0.055)),
        'dark': material('M_Charcoal', (0.045, 0.06, 0.075)),
        'steel': material('M_RailSteel', (0.16, 0.20, 0.23)),
        'amber': material('M_WayfindingAmber', (0.95, 0.45, 0.055)),
        'blue': material('M_WorkshopBlue', (0.055, 0.22, 0.30)),
        'cyan': material('M_RelayCyan', (0.06, 0.8, 0.7), True),
    }

    context, _ = data_asset('IMC_Exploration', unreal.InputMappingContext)
    context.unmap_all()
    input_spec = [
        ('Forward', 'W', 'forward_action', False), ('Back', 'S', 'back_action', False),
        ('Right', 'D', 'right_action', False), ('Left', 'A', 'left_action', False),
        ('LookYaw', 'MouseX', 'yaw_action', True), ('LookPitch', 'MouseY', 'pitch_action', True),
        ('Sprint', 'LeftShift', 'sprint_action', False), ('Crouch', 'LeftControl', 'crouch_action', False),
        ('Jump', 'SpaceBar', 'jump_action', False), ('Interact', 'E', 'interact_action', False),
    ]
    action_defaults = {}
    for name, key, prop, axis in input_spec:
        action, _ = data_asset('IA_' + name, unreal.InputAction)
        action.set_editor_property('value_type', unreal.InputActionValueType.AXIS1D if axis else unreal.InputActionValueType.BOOLEAN)
        input_key = unreal.Key()
        input_key.set_editor_property('key_name', key)
        context.map_key(action, input_key)
        save(action)
        action_defaults[prop] = action
    save(context)

    player_bp = blueprint('BP_CRCharacter', unreal.CRCharacter)
    player_class = unreal.load_class(None, player_bp.get_path_name() + '_C')
    defaults = unreal.get_default_object(player_class)
    defaults.set_editor_property('mapping_context', context)
    for prop, action in action_defaults.items():
        defaults.set_editor_property(prop, action)
    player_class = finish_blueprint(player_bp)

    mode_bp = blueprint('BP_CRGameMode', unreal.CRGameMode)
    defaults = unreal.get_default_object(unreal.load_class(None, mode_bp.get_path_name() + '_C'))
    defaults.set_editor_property('default_pawn_class', player_class)
    mode_class = finish_blueprint(mode_bp)

    interaction_classes = {}
    for name, kind in [('PowerModule', unreal.CRInteractionKind.POWER_MODULE),
                       ('RelayTerminal', unreal.CRInteractionKind.RELAY),
                       ('SignalConsole', unreal.CRInteractionKind.SIGNAL)]:
        bp = blueprint('BP_' + name, unreal.CRInteractionActor)
        defaults = unreal.get_default_object(unreal.load_class(None, bp.get_path_name() + '_C'))
        defaults.set_editor_property('kind', kind)
        interaction_classes[name] = finish_blueprint(bp)

    if assets.does_asset_exist(MAP):
        if not levels.load_level(MAP):
            raise RuntimeError('Could not load owned map')
    else:
        if not levels.new_level(MAP, False):
            raise RuntimeError('Could not create non-partitioned map')
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assets.set_metadata_tag(world, META, OWNER)
    # Persist ownership immediately: a later API failure must not strand our own map.
    if not levels.save_current_level():
        raise RuntimeError('Could not persist map ownership checkpoint')
    world.get_world_settings().set_editor_property('default_game_mode', mode_class)
    world.get_world_settings().set_editor_property('kill_z', -3000.0)
    by_label = {}
    for actor in actors.get_all_level_actors():
        label = actor.get_actor_label()
        if label in by_label and label.startswith('CR_'):
            raise RuntimeError('Duplicate generated label already exists: ' + label)
        by_label[label] = actor
    expected = []

    def spawn(name, cls, location, rotation=(0, 0, 0), zone='Shared'):
        # Python positional Rotator order differs from C++ FRotator. Always name axes.
        rotator = unreal.Rotator(pitch=rotation[0], yaw=rotation[1], roll=rotation[2])
        label = 'CR_' + name
        actor = by_label.get(label)
        if actor:
            expected_class = cls.static_class() if isinstance(cls, type) else cls
            if TAG not in [str(t) for t in actor.tags] or actor.get_class() != expected_class:
                raise RuntimeError('Refusing conflicting actor: ' + label)
        else:
            actor = actors.spawn_actor_from_class(cls, unreal.Vector(*location), rotator)
            if not actor:
                raise RuntimeError('Spawn failed: ' + label)
            actor.set_actor_label(label)
            by_label[label] = actor
        actor.set_editor_property('tags', [unreal.Name(TAG), unreal.Name('CR_Zone_' + zone)])
        actor.set_folder_path('Phase01A/' + zone)
        actor.set_actor_location(unreal.Vector(*location), False, False)
        actor.set_actor_rotation(rotator, False)
        expected.append(label)
        return actor

    cube = assets.load_asset('/Engine/BasicShapes/Cube')
    cylinder = assets.load_asset('/Engine/BasicShapes/Cylinder')
    if not cube or not cylinder:
        raise RuntimeError('Installed Engine basic shapes are missing')

    def box(name, loc, size, mat='concrete', zone='A_RailYard', rotation=(0, 0, 0), mesh=None):
        actor = spawn(name, unreal.StaticMeshActor, loc, rotation, zone)
        comp = actor.static_mesh_component
        comp.set_mobility(unreal.ComponentMobility.STATIC)
        comp.set_static_mesh(mesh or cube)
        comp.set_material(0, mats[mat])
        comp.set_collision_profile_name('BlockAll')
        actor.set_actor_scale3d(unreal.Vector(*(v / 100 for v in size)))
        return actor

    def sign(name, text, loc, size=38, zone='A_RailYard', yaw=180, color=(240, 181, 70, 255)):
        actor = spawn(name, unreal.TextRenderActor, loc, (0, yaw, 0), zone)
        text_comp = actor.text_render
        text_comp.set_text(text)
        text_comp.set_world_size(size)
        text_comp.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
        text_comp.set_text_render_color(unreal.Color(*color))
        return actor

    def light(name, loc, color, intensity=6500, radius=1000, zone='Shared'):
        actor = spawn(name, unreal.PointLight, loc, zone=zone)
        comp = actor.point_light_component
        comp.set_mobility(unreal.ComponentMobility.MOVABLE)
        comp.set_intensity(intensity)
        comp.set_light_color(unreal.LinearColor(*color, 1))
        comp.set_attenuation_radius(radius)
        comp.set_editor_property('source_radius', 12.0)

    # Units: centimeters. Yard top z=0, bunker floor z=-600. No teleport links.
    box('YardFloor', (-200, 0, -30), (3600, 2800, 60))
    box('YardBackWall', (-2000, 0, 180), (40, 2800, 360), 'dark')
    for y in [-1400, 1400]:
        box('YardBoundary' + str(y), (-200, y, 160), (3600, 40, 320), 'rust')
    for y in [-1050, 1050]:
        box('YardFrontBarrier' + str(y), (1600, y, 130), (40, 700, 260), 'dark')
    for lane in [-800, 800]:
        for segment, (start, end) in enumerate([(-1800, -300), (-240, 340), (430, 1120)]):
            for offset in [-75, 75]:
                box(f'Rail_{lane}_{segment}_{offset}', ((start+end)/2, lane+offset, 8), (end-start, 12, 16), 'steel')
        for x in range(-1780, 1100, 170):
            box(f'Sleeper_{lane}_{x}', (x, lane, 3), (35, 210, 6), 'dark')
        car_x = -950 if lane < 0 else -350
        box(f'CarBody{lane}', (car_x, lane, 230), (900, 310, 280), 'rust')
        box(f'CarRoof{lane}', (car_x, lane, 380), (930, 330, 30), 'dark')
        for x_offset in [-310, 310]:
            for side in [-170, 170]:
                box(f'Wheel{lane}_{x_offset}_{side}', (car_x+x_offset, lane+side, 65), (130, 130, 35), 'steel', rotation=(0, 0, 90), mesh=cylinder)
        for offset in [-280, 0, 280]:
            for side in [-158, 158]:
                box(f'CarWindow{lane}_{offset}_{side}', (car_x+offset, lane+side, 260), (160, 8, 100), 'dark')
    # Warehouse occupies a side spur; center route stays clear.
    box('WarehouseBack', (750, -1300, 300), (900, 30, 600), 'wall')
    box('WarehouseSideLeft', (300, -1000, 300), (30, 600, 600), 'wall')
    box('WarehouseSideRight', (1200, -1000, 300), (30, 600, 600), 'wall')
    box('WarehouseRoof', (750, -1000, 610), (940, 650, 40), 'rust')
    box('WarehouseDoorLeft', (470, -700, 250), (340, 30, 500), 'wall')
    box('WarehouseDoorRight', (1030, -700, 250), (340, 30, 500), 'wall')
    sign('WarehouseSign', 'FREIGHT / 09', (750, -675, 530), 45, yaw=90)
    for i, y in enumerate([-270, 270]):
        box(f'ApproachBarrier{i}', (1100, y, 55), (230, 75, 110), 'amber')
    sign('YardIntro', 'RELAY NINE\nMAINTENANCE ACCESS  >', (-1500, -350, 180), 36, yaw=90)

    B = 'B_Workshop'
    box('WorkshopFloor', (2600, 0, -25), (2000, 1400, 50), zone=B)
    for y in [-700, 700]:
        box('WorkshopSide' + str(y), (2600, y, 250), (2000, 30, 500), 'wall', B)
    for x, title in [(1600, 'Front'), (3600, 'Rear')]:
        for y in [-440, 440]:
            box('Workshop' + title + str(y), (x, y, 250), (30, 520, 500), 'blue', B)
        box('WorkshopLintel' + title, (x, 0, 425), (30, 360, 150), 'blue', B)
    box('WorkshopRoof', (2600, 0, 515), (2030, 1430, 30), 'dark', B)
    sign('WorkshopEntrance', 'MAINTENANCE WORKSHOP', (1575, 0, 370), 38, B)
    for y in [-205, 205]:
        box('EntranceStripe' + str(y), (1578, y, 160), (18, 30, 320), 'amber', B)
    entry = spawn('WorkshopEntry', unreal.CRWorkshopTrigger, (1790, 0, 160), zone=B)
    entry.volume.set_box_extent(unreal.Vector(100, 180, 160))
    box('WorkbenchTop', (2800, -365, 95), (280, 120, 20), 'steel', B)
    for x in [2690, 2910]:
        box('WorkbenchLeg' + str(x), (x, -365, 42), (20, 100, 84), 'blue', B)
    sign('WorkbenchLabel', 'SERVICE BENCH\nFUNCTIONAL POWER MODULE', (2800, -445, 225), 23, B, yaw=90)
    for x in [2050, 2320]:
        box('StorageFrame' + str(x), (x, 590, 140), (220, 140, 280), 'dark', B)
        for z in [55, 150, 245]:
            box(f'StorageCrate{x}_{z}', (x, 505, z), (170, 40, 60), 'rust', B)
    box('BrokenMachine', (3100, 420, 110), (240, 180, 220), 'steel', B)
    box('BrokenMachineHead', (3070, 420, 245), (120, 150, 70), 'rust', B, rotation=(0, 0, 15))
    sign('BunkerDirection', 'RELAY NINE\nLOWER ACCESS', (3555, 0, 370), 32, B)
    light('WorkshopLight1', (2150, 0, 400), (1, 0.76, 0.46), zone=B)
    light('WorkshopLight2', (3050, -80, 400), (0.65, 0.86, 1), zone=B)

    C = 'C_RelayBunker'
    slope = -math.degrees(math.atan2(600, 1800))
    length = math.hypot(1800, 600)
    box('AccessRamp', (4500, 0, -316), (length+40, 360, 30), 'concrete', C, rotation=(slope, 0, 0))
    for y in [-195, 195]:
        box('RampWall' + str(y), (4500, y, -100), (length+50, 30, 430), 'wall', C, rotation=(slope, 0, 0))
        box('RampGuide' + str(y), (4500, y*0.92, -170), (length, 12, 10), 'amber', C, rotation=(slope, 0, 0))
    box('RampCeiling', (4500, 0, 160), (length+50, 430, 30), 'dark', C, rotation=(slope, 0, 0))
    light('RampLamp1', (4000, 0, 175), (1, 0.55, 0.22), 3500, 700, C)
    light('RampLamp2', (4950, 0, -145), (0.35, 0.75, 1), 3500, 700, C)
    box('BunkerFloor', (6300, 0, -630), (1800, 1300, 60), 'concrete', C)
    for y in [-650, 650]:
        box('BunkerSide' + str(y), (6300, y, -350), (1800, 30, 500), 'wall', C)
    box('BunkerRear', (7200, 0, -350), (30, 1300, 500), 'dark', C)
    for y in [-415, 415]:
        box('BunkerFront' + str(y), (5400, y, -350), (30, 470, 500), 'wall', C)
    box('BunkerLintel', (5400, 0, -175), (30, 360, 150), 'wall', C)
    box('BunkerRoof', (6300, 0, -85), (1830, 1330, 30), 'dark', C)
    for x in [5750, 6050, 6350, 6650]:
        box('ServerRack' + str(x), (x, 515, -465), (160, 180, 270), 'steel', C)
        box('ServerIndicator' + str(x), (x, 418, -405), (100, 8, 16), 'cyan', C)
    box('RelayPedestal', (6200, -320, -555), (160, 120, 90), 'dark', C)
    box('SignalPedestal', (6900, 0, -550), (140, 200, 100), 'steel', C)
    sign('RelayLabel', 'RELAY NINE\nPOWER INPUT', (6195, -410, -335), 28, C, yaw=90)
    sign('EndingLocation', 'MERIDIAN\nSIGNAL MONITOR', (7175, 0, -240), 48, C)
    light('BunkerLight1', (5800, 0, -200), (0.5, 0.7, 1), 7000, 1000, C)
    light('BunkerLight2', (6650, -150, -200), (0.2, 1, 0.85), 7000, 1000, C)

    for name, loc, size, mat, zone in [
        ('PowerModule', (2800, -365, 127), (48, 38, 44), 'cyan', B),
        ('RelayTerminal', (6200, -320, -455), (110, 90, 110), 'amber', C),
        ('SignalConsole', (6900, 0, -450), (100, 180, 100), 'cyan', C),
    ]:
        actor = spawn(name, interaction_classes[name], loc, zone=zone)
        actor.mesh.set_static_mesh(cube)
        actor.mesh.set_material(0, mats[mat])
        actor.set_actor_scale3d(unreal.Vector(*(v/100 for v in size)))
        actor.mesh.set_collision_profile_name('BlockAll')

    spawn('PlayerStart', unreal.PlayerStart, (-1450, 0, 100), zone='A_RailYard')
    sun = spawn('Sun', unreal.DirectionalLight, (0, 0, 1500), (-45, -25, 0))
    sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
    sun_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    sun_component.set_intensity(6)
    sun_component.set_editor_property('atmosphere_sun_light', True)
    spawn('Atmosphere', unreal.SkyAtmosphere, (0, 0, 0))
    sky = spawn('SkyLight', unreal.SkyLight, (0, 0, 1000))
    sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    sky.light_component.set_editor_property('real_time_capture', True)
    sky.light_component.set_intensity(1)
    # Exposure adapts to the dim interior; no change to project-wide renderer architecture.
    post = spawn('Exposure', unreal.PostProcessVolume, (0, 0, 0))
    post.set_editor_property('unbound', True)
    settings = post.get_editor_property('settings')
    settings.set_editor_property('override_auto_exposure_min_brightness', True)
    settings.set_editor_property('override_auto_exposure_max_brightness', True)
    settings.set_editor_property('auto_exposure_min_brightness', -2.0)
    settings.set_editor_property('auto_exposure_max_brightness', 5.0)
    post.set_editor_property('settings', settings)
    if not levels.save_current_level():
        raise RuntimeError('Greybox map save failed')
    # Re-query after saving: proves stable unique actor labels, not visual acceptance.
    labels = [a.get_actor_label() for a in actors.get_all_level_actors()]
    for label in expected:
        if labels.count(label) != 1:
            raise RuntimeError('Actor uniqueness check failed: ' + label)
    receipt = {
        'map': MAP, 'owner': OWNER, 'expected_owned_actors': len(expected),
        'all_level_actors': len(labels), 'new_assets': created_assets,
        'input_mappings': len(input_spec), 'world_partition': False,
        'zones_cm': {'yard': [-2000, 1600, -1400, 1400, 0],
                     'workshop': [1600, 3600, -700, 700, 0],
                     'ramp': [3600, 5400, -180, 180, '0 to -600'],
                     'bunker': [5400, 7200, -650, 650, -600]},
    }
    out = Path(unreal.Paths.project_saved_dir()) / 'Phase01A'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'generation.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    unreal.log('CR_GREYBOX_GENERATED ' + json.dumps(receipt))


main()
