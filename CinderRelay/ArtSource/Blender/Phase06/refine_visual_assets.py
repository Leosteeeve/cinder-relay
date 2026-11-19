"""Original Phase06 visual derivatives. The retained source projects are read-only inputs."""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy


parser = argparse.ArgumentParser()
parser.add_argument('--export-dir', type=Path, required=True)
output = parser.parse_args(sys.argv[sys.argv.index('--') + 1:]).export_dir.resolve()
output.mkdir(parents=True, exist_ok=True)
source = Path(__file__).resolve().parent
manifest = {}


def select(*objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def box(name, center, size, material, bevel=.2, bone=None, angle=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.rotation_euler.x = math.radians(angle)
    obj.data.materials.append(material)
    edge = obj.modifiers.new('Formed edges', 'BEVEL')
    edge.width = bevel
    edge.segments = 2
    bpy.ops.object.modifier_apply(modifier=edge.name)
    if bone:
        obj.vertex_groups.new(name=bone).add(list(range(len(obj.data.vertices))), 1, 'REPLACE')
    return obj


def merge(base, additions):
    select(base, *additions)
    bpy.ops.object.join()


def save_export(mesh, name, rig=None):
    select(mesh, *([rig] if rig else []))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(source / (name + '.blend')), relative_remap=True)
    if rig:
        rig.data.pose_position = 'REST'
    bpy.ops.export_scene.fbx(filepath=str(output / (name + '.fbx')), use_selection=True,
                             object_types={'MESH', 'ARMATURE'} if rig else {'MESH'},
                             axis_forward='-Y', axis_up='Z', add_leaf_bones=False, bake_anim=False,
                             apply_unit_scale=True, mesh_smooth_type='FACE')
    mesh.data.calc_loop_triangles()
    manifest[name] = {'triangles': len(mesh.data.loop_triangles),
                      'bones': [b.name for b in rig.data.bones] if rig else []}


bpy.ops.wm.open_mainfile(filepath=str(source.parent / 'Phase051/CR051_Rook5.blend'))
rook = bpy.data.objects['SM_CR051_Rook5']
steel, brass = (bpy.data.materials['CR051_' + name] for name in ('Steel', 'Brass'))
# Small external service plates follow the upper receiver. Grip, sight and prop contact surfaces stay clear.
trim = []
for side in (-1, 1):
    trim.append(box('Stamped service plate', (-7, side * 2.85, 3.65), (12, .7, 1.9), steel, .25))
    for x in (-11.5, -2.5):
        trim.append(box('Plate rivet', (x, side * 3.22, 3.65), (.42, .18, .42), brass, .08))
    for x in (-9, -7, -5):
        trim.append(box('Calibration index', (x, side * 3.23, 3.65), (.6, .12, .17), brass, .035))
merge(rook, trim)
save_export(rook, 'SM_CR06_Rook5Service')

bpy.ops.wm.open_mainfile(filepath=str(source.parent / 'Phase05/CR05_AshWarden.blend'))
warden = bpy.data.objects['SK_CR05_AshWarden']
rig = bpy.data.objects['CR05_WardenRig']
armor, leather, band = (bpy.data.materials['CR05_Warden' + name] for name in ('Armor', 'Leather', 'Band'))
shell = [box('Face shield brow', (13.5, 0, 165), (6, 28, 3.6), armor, 1, 'head'),
         box('Backpack spine', (-29, 0, 123), (5, 19, 32), leather, 1.3, 'spine'),
         box('Yard identification tab', (19, 11, 137), (2, 11, 5), band, .55, 'spine')]
for sign, side in ((-1, 'L'), (1, 'R')):
    shell.append(box('Shoulder mantle ' + side, (0, sign * 27.5, 146), (21, 17, 6),
                     armor, 2, 'upperarm_' + side, -sign * 18))
    shell.append(box('Shoulder identification ' + side, (4, sign * 34.5, 147), (8, 2.4, 3.5),
                     band, .6, 'upperarm_' + side, -sign * 18))
merge(warden, shell)
save_export(warden, 'SK_CR06_AshWardenService', rig)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = .01
steel, dark, amber = (bpy.data.materials.new('CR06_' + name) for name in ('Steel', 'Dark', 'Amber'))
# +X face. The 8 cm reach behind the origin intersects the mounting surface.
plate = box('Beveled folded enclosure', (-2, 0, 0), (12, 240, 72), steel, 2)
parts = [box('Recessed reading surface', (4, 0, 0), (2, 228, 60), dark, 1.5),
         box('Enamel stripe', (5.2, 0, -26), (1.2, 198, 2.5), amber, .4)]
for y in (-115, 115):
    for z in (-29, 29):
        parts.append(box('Captive fastener', (4.8, y, z), (2.8, 3, 3), steel, .65))
merge(plate, parts)
plate.name = 'SM_CR06_ServicePlaque'
bpy.context.scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
save_export(plate, 'SM_CR06_ServicePlaque')
(output / 'visual-asset-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
