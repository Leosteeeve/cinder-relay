"""Build the original repair machinery in Blender or author its two streamed levels in Unreal.

Blender: --background --factory-startup --python-exit-code 1 --python remake_interiors.py
Editor: -run=pythonscript -script=.../remake_interiors.py -CR06AuthorInteriors
Omit -CR06AuthorInteriors for a read-only native reload and validation.
"""
import ast
import hashlib
import json
import math
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT.parent / '.environment-local/phase-06/remake/interiors'
EXPORTS = OUT / 'exports'
ASSETS = '/Game/Generated/Phase06/Meshes/ServiceCircuit/'
OWNER = 'CinderRelay.Phase06.ServiceCircuit'
TAG = 'CR06_ServiceCircuit'
WORLD = '/Game/Generated/Phase01B/Maps/L_CH01_Persistent'
# (label, center at finished floor level, yaw, clear width, supply step)
GATES = {
    'Workshop': (
        ('SupplyPress', (3190, -2140, 0), 0, 470, 1),
        ('LoadPress', (2500, -3890, 0), 0, 470, 2),
        ('CradleCrosswalk', (2180, -4000, 0), 90, 440, 3),
    ),
    'RelayBunker': (
        ('BusBreaker', (6850, -2940, -600), 0, 570, 1),
        ('InterlockCrosswalk', (6170, -4510, -600), 90, 460, 2),
    ),
}
MACHINES = {
    'Workshop': [('BrakeCellA', 'Dynamometer', (3470, -2840, 0), 90),
                 ('BrakeCellB', 'Dynamometer', (3470, -4790, 0), 90)],
    'RelayBunker': [('SwitchBankA', 'Transformer', (6305, -1500, -600), 90),
                    ('SwitchBankB', 'Transformer', (6305, -3700, -600), 90),
                    ('SwitchBankC', 'Transformer', (5530, -2830, -600), 90)],
}


def model_kit():
    import bpy
    from mathutils import Vector

    EXPORTS.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = .01
    materials = {}
    for name, color in {'Dark': (.055,.063,.068), 'Steel': (.24,.27,.29), 'Paint': (.1,.23,.23),
                        'Amber': (.76,.34,.05), 'Pale': (.6,.6,.47)}.items():
        m = bpy.data.materials.new('Circuit_' + name)
        m.diffuse_color = (*color, 1)
        materials[name] = m
    # Reuse only the project's primitive mesh helpers and FBX writer, without running either generator.
    helpers = dict(bpy=bpy, Vector=Vector, math=math, scene=scene, parts=[], mats=materials, kit=[], out=EXPORTS)
    wanted = {'reg', 'mesh', 'bevel', 'box', 'beam', 'lathe', 'cyl', 'tube'}
    for source, names in ((PROJECT / 'ArtSource/Blender/Phase052/polish_environment.py', wanted),
                          (PROJECT / 'ArtSource/Blender/Phase06/author_service_architecture.py', {'finish'})):
        functions = [n for n in ast.parse(source.read_text(encoding='utf8')).body
                     if isinstance(n, ast.FunctionDef) and n.name in names]
        assert len(functions) == len(names)
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), 'exec'), helpers)
    box, beam, lathe, cyl, tube, finish = [helpers[k] for k in ('box', 'beam', 'lathe', 'cyl', 'tube', 'finish')]

    # Both frames span 480 cm between the jambs. All leaves have their local origin at the top hinge.
    for relay in (False, True):
        height = 402 if relay else 322
        for s in (-1, 1):
            x = s * 254
            box('Grouted anchor shoe', (x,0,9), (44,86,18), 'Dark', 3)
            box('Folded steel channel', (x,0,height/2), (29,58,height), 'Paint', 2)
            for y in (-31,31):
                box('Replaceable guide face', (x,y,height/2), (30,6,height-12), 'Steel', 1)
                for z in (30,53,77):
                    box('Warning band', (x,y,z), (26,8,8), 'Amber', 1)
            if relay:
                cyl('Counterbalance casing', (x+21*s,0,252), 20,220,'Dark','Z')
                cyl('Cylinder gland', (x+21*s,0,145), 23,15,'Steel','Z')
            else:
                for z in (110,185,255):
                    cyl('Door guide roller', (x,0,z), 13,45,'Steel','Y')
        if relay:
            box('Interlock headstock', (0,0,364), (544,88,78), 'Dark', 5)
            for x in range(-225,226,75):
                box('Segmented armored cowl', (x,0,365), (70,94,68), 'Paint', 3)
            for y in (-48,48):
                box('Track inspection line', (0,y,336), (470,4,5), 'Pale', 1)
        else:
            box('Hinge girder', (0,0,286), (542,60,42), 'Paint', 3)
            cyl('Torsion barrel', (0,0,277), 24,474,'Steel','X',24)
            for x in (-211,-148,148,211):
                cyl('Barrel collar', (x,0,277), 29,14,'Dark','X',20)
            for side in (-1,1):
                beam('Over-centre header brace', (side*247,0,314),(side*160,0,278),12,49,'Amber')
        box('Pilot lamp bracket', (0,39,258), (70,18,16),'Dark',2)
        box('Opal lamp lens', (0,49,257), (59,5,9),'Pale',1)
        finish('Circuit' + ('InterlockFrame' if relay else 'PressFrame'))

    for relay in (False, True):
        for z in (-8,-122):
            box('Edge rail', (0,0,z), (478,14,16),'Steel',2)
        for x in (-231,231):
            box('Stile', (x,0,-65), (16,16,126),'Paint',2)
        if relay:
            box('Press-formed shutter', (0,0,-65), (458,10,102),'Paint',3)
            for x in (-177,-89,0,89,177):
                box('Deep vertical pressing', (x,0,-65), (48,17,85),'Dark',3)
                box('Steel rib cap', (x,0,-65), (33,19,66),'Steel',2)
            for y in (-10,10):
                box('Checker band', (0,y,-112), (435,3,5),'Amber',1)
        else:
            for x in (-172,-57,57,172):
                beam('Welded diagonal stay',(x-52,0,-112),(x+52,0,-17),7,8,'Paint')
            for x in range(-201,202,40):
                box('Expanded steel safety grille', (x,0,-65),(3,4,100),'Dark',.5)
            for z in (-48,-80):
                box('Grille stiffener', (0,0,z),(446,5,4),'Dark',.5)
            for x in (-165,0,165):
                cyl('Hinge knuckle', (x,0,-127), 9,39,'Amber','X',14)
        finish('Circuit' + ('InterlockLeaf' if relay else 'PressLeaf'))

    # A brake-test motor on a skid: dished flywheel, exposed shaft, bearing pedestals and protective cage.
    box('Grouted plinth', (0,0,12), (510,169,24),'Dark',4)
    for y in (-58,58):
        box('Rolled skid member',(0,y,29),(489,22,18),'Steel',2)
    for x in (-179,-72,86,197):
        box('Cast mounting feet',(x,0,49),(57,130,29),'Paint',5)
    cyl('Test motor barrel',(-119,0,114),62,173,'Paint','X',32)
    for x in range(-181,-59,14):
        cyl('Motor cooling fin',(x,0,114),69,6,'Dark','X',28)
    for x in (-202,-42):
        lathe('Machined end bell',(x,0,114),[(-13,0),(-12,44),(-2,62),(8,59),(13,34),(14,0)],'Steel','X',32)
    cyl('Through shaft',(86,0,114),12,286,'Steel','X',20)
    for x in (29,168):
        box('Bearing pedestal',(x,0,80),(36,54,82),'Paint',5)
        cyl('Bearing cap',(x,0,116),25,42,'Steel','X')
    for x in (76,111):
        lathe('Brake drum rim',(x,0,114),[(-12,0),(-12,20),(-5,33),(-5,66),(-13,70),(-13,78),
                                         (13,78),(13,70),(5,66),(5,33),(12,20),(12,0)],'Amber','X',36)
    for y in (-79,79):
        tube('Guard return',[(4,y,32),(4,y,190),(17,y,205),(171,y,205),(184,y,190),(184,y,32)],4,'Steel')
        for z in (70,111,153):
            box('Cage bar',(94,y,z),(175,4,5),'Steel',1)
    box('Terminal box',(-124,0,188),(81,78,28),'Paint',3)
    tube('Cable exit',[(-111,4,201),(-111,4,224),(-158,4,242),(-212,4,219),(-226,4,68)],6,'Dark')
    finish('CircuitDynamometer')

    # Oil tank, radiator fins, busbars and ceramic standoffs give the underground hall a different skyline.
    box('Bund base',(0,0,12),(490,166,24),'Dark',4)
    box('Transformer tank',(0,0,101),(400,109,151),'Paint',8)
    for x in range(-180,181,20):
        box('Pressed cooling radiator',(x,0,103),(7,150,124),'Steel',3)
    box('Bolted tank lid',(0,0,185),(421,136,16),'Dark',3)
    for x in (-150,0,150):
        cyl('Porcelain core',(x,0,227),13,78,'Pale','Z',20)
        for z in (204,218,232,246):
            lathe('Glazed insulator skirt',(x,0,z),[(-4,10),(-3,24),(1,24),(4,13)],'Pale','Z',24)
        cyl('Terminal cap',(x,0,267),15,14,'Amber','Z',16)
    tube('High conductor',[(-205,0,208),(-179,0,274),(-150,0,279),(-75,0,309),(0,0,279),
                            (75,0,307),(150,0,279),(178,0,271),(211,0,201)],5,'Amber')
    for x in (-225,225):
        cyl('Flanged service pipe',(x,0,97),15,124,'Steel','Z',16)
        for z in (52,146):
            cyl('Service flange',(x,0,z),21,10,'Dark','Z',16)
    finish('CircuitTransformer')
    # Glazed openings would hide the lettered route in darkness. A see-through truss instead separates
    # the energized forward floor from the return gallery and lets players watch repairs across the aisle.
    for z in (7,211):
        box('Gallery edge channel',(0,0,z),(400,24,14),'Steel',2)
    for x in (-192,0,192):
        box('Gallery upright',(x,0,108),(15,22,206),'Paint',2)
    for x in range(-168,169,28):
        box('Protective grille',(x,0,110),(3,8,196),'Dark',.5)
    for x in (-96,96):
        beam('Gallery tension diagonal',(x-86,0,16),(x+86,0,201),9,14,'Steel')
    box('Handrail',(0,0,45),(397,32,7),'Amber',1.3)
    finish('CircuitGallery')
    manifest = helpers['kit']
    assert len(manifest) == 7 and all(0 < obj['triangles'] < 18000 for obj in manifest), manifest
    (EXPORTS / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    print('CR06_INTERIOR_MODELS PASS', [(m['name'], m['triangles']) for m in manifest])


def author_levels():
    import unreal as ue

    levels = ue.get_editor_subsystem(ue.LevelEditorSubsystem)
    actors = ue.get_editor_subsystem(ue.EditorActorSubsystem)
    assets = ue.EditorAssetLibrary
    apply = '-cr06authorinteriors' in ue.SystemLibrary.get_command_line().lower()
    assert levels.load_level(WORLD)
    palette = {name: assets.load_asset('/Game/Generated/Phase052/Materials/MI_CR052_' + name)
               for name in ('Paint', 'Steel', 'Dark', 'Amber', 'Pale')}
    assert all(palette.values())
    kit = {}
    manifest = json.loads((EXPORTS / 'manifest.json').read_text())
    for spec in manifest:
        name = spec['name']
        path = ASSETS + name
        fbx = EXPORTS / (name + '.fbx')
        digest = hashlib.sha256(fbx.read_bytes()).hexdigest()
        mesh = assets.load_asset(path) if assets.does_asset_exist(path) else None
        if mesh:
            assert assets.get_metadata_tag(mesh, 'CR.GeneratedBy') == OWNER, path
        if apply and (not mesh or assets.get_metadata_tag(mesh, 'CR.SourceFbxSha256') != digest):
            ui = ue.FbxImportUI()
            ui.automated_import_should_detect_type = False
            ui.import_mesh = True
            ui.import_as_skeletal = False
            ui.import_animations = False
            ui.import_materials = False
            ui.import_textures = False
            ui.mesh_type_to_import = ue.FBXImportType.FBXIT_STATIC_MESH
            options = ui.static_mesh_import_data
            options.combine_meshes = True
            options.auto_generate_collision = name.endswith(('Gallery', 'Dynamometer', 'Transformer'))
            options.convert_scene = True
            options.convert_scene_unit = True
            task = ue.AssetImportTask()
            task.filename = str(fbx)
            task.destination_path = ASSETS.rstrip('/')
            task.destination_name = name
            task.options = ui
            task.automated = True
            task.replace_existing = mesh is not None
            task.replace_existing_settings = True
            task.save = False
            ue.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
            mesh = assets.load_asset(path)
            assert isinstance(mesh, ue.StaticMesh), path
            slots = list(mesh.get_editor_property('static_materials'))
            for slot in slots:
                key = str(slot.get_editor_property('imported_material_slot_name'))
                assert key.startswith('Circuit_'), (name, key)
                slot.set_editor_property('material_interface', palette[key.removeprefix('Circuit_')])
            mesh.set_editor_property('static_materials', slots)
            assets.set_metadata_tag(mesh, 'CR.GeneratedBy', OWNER)
            assets.set_metadata_tag(mesh, 'CR.SourceFbxSha256', digest)
            assert assets.save_loaded_asset(mesh), path
        assert mesh and assets.get_metadata_tag(mesh, 'CR.SourceFbxSha256') == digest, path
        bounds = mesh.get_bounds()
        dim = bounds.box_extent * 2
        assert all(abs(a - b) < 1 for a,b in zip((dim.x,dim.y,dim.z), spec['dimensions_cm'])), (name, dim)
        if name.endswith('Leaf'):
            assert abs(bounds.origin.z + bounds.box_extent.z) < 1, (name, bounds.origin)
        kit[name.removeprefix('SM_CR06_Circuit')] = mesh

    def inventory():
        return {a.get_actor_label(): a for a in actors.get_all_level_actors()}

    def level_name(actor):
        return str(actor.get_level().get_outer().get_name()).rsplit('/', 1)[-1]

    def transform(a):
        p, r, s = a.get_actor_location(), a.get_actor_rotation(), a.get_actor_scale3d()
        return tuple(round(v, 3) for v in (p.x, p.y, p.z, r.pitch, r.yaw, r.roll, s.x, s.y, s.z))

    scene = inventory()
    assert len([a for a in scene.values() if isinstance(a, ue.CRCheckpoint)]) == 3
    anchors = {n: transform(a) for n,a in scene.items() if isinstance(a, ue.CRCheckpoint)}
    controls = {n: transform(a) for n,a in scene.items() if isinstance(a, (ue.CRMaintenanceStation, ue.CRAccessMachinery))}
    assert len(controls) == 6, controls
    cube = assets.load_asset('/Engine/BasicShapes/Cube')
    changes = {}
    expected = {}

    def get_owned(name, cls, loc, yaw=0):
        label = 'CR06I_' + name
        a = scene.get(label)
        if a is not None:
            assert isinstance(a, cls) and TAG in [str(t) for t in a.tags], label
            assert level_name(a) == 'L_CH01_' + zone, label
        else:
            a = actors.spawn_actor_from_class(cls, ue.Vector(*loc))
            assert a, label
            a.set_actor_label(label)
            a.tags = [TAG]
            scene[label] = a
        a.modify()
        a.set_actor_location(ue.Vector(*loc), False, False)
        a.set_actor_rotation(ue.Rotator(yaw=yaw), False)
        return a

    def box(name, loc, size):
        a = get_owned(name, ue.StaticMeshActor, loc)
        a.static_mesh_component.set_static_mesh(cube)
        a.static_mesh_component.set_material(0, palette['Paint'])
        a.static_mesh_component.set_collision_profile_name('BlockAll')
        a.set_actor_scale3d(ue.Vector(*(v / 100 for v in size)))
        return a

    def equipment(name, kind, pos, yaw, scaled_x=1):
        actor = get_owned(name, ue.StaticMeshActor, pos, yaw)
        actor.set_actor_scale3d(ue.Vector(scaled_x,1,1))
        actor.static_mesh_component.set_static_mesh(kit[kind])
        actor.static_mesh_component.set_collision_profile_name('BlockAll')
        actor.static_mesh_component.set_editor_property('can_ever_affect_navigation', False)
        return actor

    def task_light(name, pos, relay):
        x, y, floor = pos
        face = 1 if relay else -1
        fixture = get_owned(name + 'TaskStrip', ue.StaticMeshActor, (x+face*145, y, floor+425))
        fixture.set_actor_scale3d(ue.Vector(.085, 1.12, .045))
        fixture.static_mesh_component.set_static_mesh(cube)
        fixture.static_mesh_component.set_material(0, assets.load_asset('/Game/Generated/Phase05/Materials/MI_CR05_Light'))
        fixture.static_mesh_component.set_collision_profile_name('NoCollision')
        fixture.set_actor_enable_collision(False)
        light = get_owned(name + 'TaskLight', ue.PointLight, (x+face*158, y-38, floor+313)).light_component
        light.set_mobility(ue.ComponentMobility.MOVABLE)
        light.set_intensity_units(ue.LightUnits.LUMENS)
        light.set_intensity(820)
        light.set_light_color(ue.LinearColor(.67, .84, 1., 1.) if relay else ue.LinearColor(1., .81, .59, 1.))
        light.set_editor_property('attenuation_radius', 515)
        light.set_editor_property('cast_shadows', False)
        light.set_editor_property('indirect_lighting_intensity', .38)

    def gallery(x, near, far, floor, center, span, spine, is_relay):
        # Keep the former spine actor and its collision ownership as the long base below the panels.
        # Open a full-height crosscut and split the grating around it, without making an invisible wall.
        outer = scene[spine]
        assert 'CR_Phase06_Expanded' in [str(t) for t in outer.tags], spine
        outer.modify()
        label = 'Breaker' if is_relay else 'Test'
        for index, (start, end) in enumerate(((center + span/2, near), (far, center - span/2))):
            length = end - start
            pos = (x, (start+end)/2, floor+50)
            if index == 0:
                outer.set_actor_location(ue.Vector(*pos), False, False)
                outer.set_actor_scale3d(ue.Vector(.36, length/100, 1))
            else:
                box(label + 'GalleryPlinth', pos, (36, length, 100))
            count = max(1, round(length / 410))
            pitch = length/count
            for i in range(count):
                equipment(f'{label}Gallery{index}_{i}', 'Gallery', (x, start + pitch*(i+.5), floor+100),
                          90, pitch/400)

    def backplate_label(name, x, y, z, face_offset, text):
        # Gate-local X runs along the spine. TextRender local +X is its reading face.
        for i, face in enumerate((1,-1)):
            a = get_owned(name + 'Route' + str(i), ue.TextRenderActor, (x + face*face_offset,y,z), 0 if face == 1 else 180)
            t = a.text_render
            t.set_text(text)
            t.set_world_size(16)
            t.set_horizontal_alignment(ue.HorizTextAligment.EHTA_CENTER)
            t.set_vertical_alignment(ue.VerticalTextAligment.EVRTA_TEXT_CENTER)
            t.set_text_render_color(ue.Color(255,201,113,255))

    if apply:
        for zone, gates in GATES.items():
            assert levels.set_current_level_by_name('L_CH01_' + zone)
            is_relay = zone == 'RelayBunker'
            for name, loc, yaw, width, stage in gates:
                x, y, z = loc
                gate = get_owned(name, ue.CRServiceCircuit, loc, yaw)
                gate.set_editor_property('relay_circuit', is_relay)
                gate.set_editor_property('required_step', stage)
                gate.set_actor_scale3d(ue.Vector(width/480, 1, 1))
                frame, leaf = ('InterlockFrame', 'InterlockLeaf') if is_relay else ('PressFrame', 'PressLeaf')
                for prop, mesh in (('housing', frame), ('upper_leaf', leaf), ('lower_leaf', leaf)):
                    component = gate.get_editor_property(prop)
                    component.modify()
                    component.set_static_mesh(kit[mesh])
                if yaw == 0:
                    left, right = {'SupplyPress': (2910,3600), 'LoadPress': (2180,2800),
                                   'BusBreaker': (6420,7200)}[name]
                    for side, (start,end) in enumerate(((left,x-width/2), (x+width/2,right))):
                        box(name + 'Abutment' + str(side), ((start+end)/2, y, z+178),
                            (end-start, 44, 356))
                else:
                    if is_relay:
                        gallery(x,-650,-4830,z,y,width,'CR06X_RelayReturnSpine',True)
                    else:
                        gallery(x,-700,-4330,z,y,width,'CR06X_TestReturnSpine',False)
                    backplate_label(name,x,y,z + (365 if is_relay else 288), 49 if is_relay else 31,
                                    'CROSSWALK   /   STOP CONTROL' if is_relay else 'CROSSWALK   /   MODULE BENCH')
            for name, model, pos, yaw in MACHINES[zone]:
                equipment(name, model, pos, yaw)
                task_light(name, pos, is_relay)
            assert levels.save_current_level()

    # Reload both original levels and verify from persisted components, including a capsule-wide
    # path through the open frame at each acceptance route's actual crossing line.
    assert levels.load_level(WORLD)
    scene = inventory()
    assert anchors == {n: transform(scene[n]) for n in anchors}
    assert controls == {n: transform(scene[n]) for n in controls}
    inspected_blockers = {}
    for zone, gates in GATES.items():
        blockers = {}
        for label, a in scene.items():
            if not isinstance(a, ue.StaticMeshActor) or level_name(a) != 'L_CH01_' + zone:
                continue
            c = a.static_mesh_component
            if not a.get_actor_enable_collision() or c.get_collision_enabled() == ue.CollisionEnabled.NO_COLLISION:
                continue
            if c.get_collision_response_to_channel(ue.CollisionChannel.ECC_PAWN) == ue.CollisionResponseType.ECR_BLOCK:
                blockers[label] = a.get_actor_bounds(True)
        gallery_floor = 'CR06X_RelayAnnexFloor' if zone == 'RelayBunker' else 'CR06X_TestAnnexFloor'
        assert len(blockers) >= 15 and gallery_floor in blockers, (zone, 'missing collision inventory', blockers.keys())
        inspected_blockers[zone] = len(blockers)
        for name, loc, yaw, width, stage in gates:
            actor = scene['CR06I_' + name]
            assert level_name(actor) == 'L_CH01_' + zone
            assert transform(actor)[:3] == loc and abs(actor.get_actor_rotation().yaw-yaw) < .1, name
            assert actor.get_editor_property('required_step') == stage
            is_relay = zone == 'RelayBunker'
            assert actor.get_editor_property('relay_circuit') == is_relay
            assert actor.get_editor_property('housing').static_mesh == kit['InterlockFrame' if is_relay else 'PressFrame']
            for prop in ('upper_leaf','lower_leaf'):
                moving = actor.get_editor_property(prop)
                assert moving.static_mesh == kit['InterlockLeaf' if is_relay else 'PressLeaf']
                assert str(moving.get_collision_profile_name()) == 'NoCollision'
            passage = actor.get_editor_property('passage')
            e = passage.get_scaled_box_extent()
            assert abs(e.x*2-width) < .1 and abs(e.z-130) < .1 and str(passage.get_collision_profile_name()) == 'BlockAll'
            fixture_x = {'SupplyPress':3190, 'LoadPress':2490, 'BusBreaker':7032}.get(name)
            if fixture_x:
                assert abs(fixture_x - loc[0]) + 45 < width/2, name
            else:
                # The original end-around route remains available on either side of these new crosscuts.
                spine = scene['CR06X_RelayReturnSpine' if is_relay else 'CR06X_TestReturnSpine']
                center, size = spine.get_actor_bounds(False)
                assert abs(center.y - size.y - (loc[1] + width/2)) < .5, (name,center,size)
                assert abs(center.z + size.z - (loc[2] + 100)) < .5, name
            # These conservative world-aligned extents include every colliding mesh in this level.
            # Once the leaf opens a standing player must fit here without overlapping any fixed wall.
            cx, cy, cz = fixture_x or loc[0], loc[1], loc[2]+98
            for label, (origin,extent) in blockers.items():
                overlap = (abs(cx-origin.x)<42+extent.x and abs(cy-origin.y)<42+extent.y
                           and abs(cz-origin.z)<96+extent.z)
                assert not overlap, (name, 'colliding fixed mesh in passage', label, origin, extent)
            expected[name] = dict(level=zone, stage=stage, width_cm=width, closed_height_cm=e.z*2)
        for name, model, pos, yaw in MACHINES[zone]:
            actor = scene['CR06I_' + name]
            assert actor.static_mesh_component.static_mesh == kit[model] and transform(actor)[:3] == pos
            assert scene['CR06I_' + name + 'TaskLight'].light_component.get_editor_property('intensity') == 820
        changes[zone] = len([a for a in scene.values() if TAG in [str(t) for t in a.tags]
                             and level_name(a) == 'L_CH01_' + zone])
    OUT.mkdir(parents=True, exist_ok=True)
    result = dict(applied=apply, models=manifest, circuits=expected, actors_per_level=changes, checkpoints=anchors,
                  inspected_fixed_blockers=inspected_blockers, preserved_controls=controls)
    (OUT / ('native-author.json' if apply else 'native-verify.json')).write_text(json.dumps(result, indent=2))
    ue.log('CR06_INTERIORS PASS ' + str(changes))


if __name__ == '__main__':
    try:
        import unreal
    except ImportError:
        model_kit()
    else:
        author_levels()
