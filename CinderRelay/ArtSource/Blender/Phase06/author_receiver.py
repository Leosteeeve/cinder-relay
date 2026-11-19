"""Build the original Relay Nine carrier meter in centimetres. Run inside Blender."""
import argparse
import ast
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument('--export-dir', required=True, type=Path)
out = parser.parse_args(sys.argv[sys.argv.index('--') + 1:]).export_dir.resolve()
out.mkdir(parents=True, exist_ok=True)
here = Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version = 0
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = .01
mats = {}
parts = []
colors = {'Dark': (.045, .052, .05), 'Paint': (.13, .205, .215), 'Pale': (.56, .52, .39),
          'Steel': (.24, .28, .27), 'Amber': (.85, .32, .045), 'Pilot': (.19, .85, .79)}
for key, color in colors.items():
    mat = bpy.data.materials.new('CR06Meter_' + key)
    mat.diffuse_color = (*color, 1)
    mats[key] = mat

# Reuse only the project's mesh primitives. The legacy authoring entry never runs.
tree = ast.parse((here.parent / 'Phase052/polish_environment.py').read_text(encoding='utf-8'))
helpers = {'reg', 'mesh', 'bevel', 'box', 'beam', 'lathe', 'cyl', 'tube'}
exec(compile(ast.Module([fn for fn in tree.body if isinstance(fn, ast.FunctionDef) and fn.name in helpers], []),
             'service_mesh_primitives', 'exec'))
manifest = []


def export(name):
    bpy.ops.object.select_all(action='DESELECT')
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name='SurfaceUV')
    for face in obj.data.polygons:
        axes = ((1, 2), (0, 2), (0, 1))[max(range(3), key=lambda i: abs(face.normal[i]))]
        for index in face.loop_indices:
            v = obj.data.vertices[obj.data.loops[index].vertex_index].co
            uv.data[index].uv = (v[axes[0]] / 90, v[axes[1]] / 90)
    bpy.ops.export_scene.fbx(filepath=str(out / (name + '.fbx')), use_selection=True,
                             object_types={'MESH'}, axis_forward='-Y', axis_up='Z',
                             apply_unit_scale=True, bake_anim=False, mesh_smooth_type='FACE')
    obj.data.calc_loop_triangles()
    manifest.append({'name': name, 'triangles': len(obj.data.loop_triangles), 'dimensions_cm': list(obj.dimensions)})
    parts.clear()


box('Rolled frame', (0, 0, -4), (32, 488, 248), 'Dark', 6)
for side in (-1, 1):
    box('Side drawer', (-15, 177 * side, 0), (24, 113, 218), 'Paint', 5)
    for z in range(-74, 82, 15):
        box('Pressed cooling louvre', (-30, 177 * side, z), (9, 79, 5), 'Steel', 1)
    for z in (-95, 97):
        box('Drawer rail', (-27, 177 * side, z), (7, 94, 8), 'Dark', 1)
    for y in (129, 225):
        for z in (-99, 98):
            cyl('Captive fastener', (-31, y * side, z), 3.6, 5, 'Pale', 'X', 6)
    box('Plinth leg', (0, 175 * side, -169), (28, 42, 102), 'Paint', 3)
    box('Bolted foot', (-6, 175 * side, -218), (60, 63, 10), 'Steel', 2)
    tube('Conduit to dial', [(5, 197*side, -116), (5, 197*side, -139),
                             (5, 174*side, -158), (5, 73*side, -158), (5, 48*side, -120)], 7, 'Steel', 12)
cyl('Instrument flange', (-16, 0, 0), 115, 20, 'Steel', 'X', 80)
cyl('Dark rubber gasket', (-27, 0, 0), 106, 7, 'Dark', 'X', 80)
cyl('Enamel face', (-32, 0, 0), 101, 5, 'Pale', 'X', 80)
for i in range(33):
    theta = math.radians(-72 + i * 4.5)
    start = 78 if i % 4 == 0 else 87
    def tick_point(radius):
        return (-36.5, math.sin(theta) * radius, math.cos(theta) * radius)
    beam('Calibration division', tick_point(start), tick_point(95), 2.4, 2.7, 'Dark')
for i in range(12):
    theta = math.tau*i/12
    cyl('Flange nut', (-28, 110*math.sin(theta), 110*math.cos(theta)), 3, 5, 'Dark', 'X', 6)
for y in (-46, 0, 46):
    box('Indicator socket', (-36, y, -54), (4, 28, 11), 'Dark', 1.5)
    box('Indicator glass', (-39, y, -54), (3, 22, 5.5), 'Amber', 1)
export('SM_CR06_ReceiverDial')

# Origin is the meter pivot. A positive roll swings the pointer across the scale.
beam('Enamel pointer', (-42, 0, -18), (-42, 0, 82), 4.8, 6.2, 'Dark')
beam('Signal tip', (-45, 0, 56), (-45, 0, 84), 4.5, 4, 'Amber')
cyl('Hub', (-45, 0, 0), 12, 8, 'Steel', 'X', 28)
cyl('Pivot pin', (-51, 0, 0), 5, 5, 'Amber', 'X', 18)
export('SM_CR06_ReceiverNeedle')

bpy.ops.wm.save_as_mainfile(filepath=str(here / 'CR06_Receiver.blend'))
(out / 'receiver.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
