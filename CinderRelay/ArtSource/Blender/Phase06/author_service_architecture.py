"""Create the original Chapter 01 service architecture kit in centimeters."""
import argparse
import ast
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


parser = argparse.ArgumentParser()
parser.add_argument('--export-dir', type=Path, required=True)
out = parser.parse_args(sys.argv[sys.argv.index('--') + 1:]).export_dir.resolve()
out.mkdir(parents=True, exist_ok=True)
here = Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version = 0
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = .01
parts = []
mats = {}
for key, color in {'Paint': (.13, .22, .23), 'Steel': (.22, .25, .26), 'Dark': (.05, .06, .06),
                   'Amber': (.58, .31, .05), 'Pale': (.49, .49, .39)}.items():
    material = bpy.data.materials.new('CR06A_' + key)
    material.diffuse_color = (*color, 1)
    mats[key] = material

helpers = ast.parse((here.parent / 'Phase052/polish_environment.py').read_text(encoding='utf-8'))
functions = {'reg', 'mesh', 'bevel', 'box', 'beam', 'lathe', 'cyl', 'tube'}
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n, ast.FunctionDef) and n.name in functions],
                       type_ignores=[]), 'project_mesh_helpers', 'exec'))

kit = []


def finish(name):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = 'SM_CR06_' + name
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name='SurfaceUV')
    for face in obj.data.polygons:
        axes = ((1, 2), (0, 2), (0, 1))[max(range(3), key=lambda i: abs(face.normal[i]))]
        for index in face.loop_indices:
            vertex = obj.data.vertices[obj.data.loops[index].vertex_index].co
            uv.data[index].uv = (vertex[axes[0]] / 105, vertex[axes[1]] / 105)
    bpy.ops.export_scene.fbx(filepath=str(out / (obj.name + '.fbx')), use_selection=True, object_types={'MESH'},
                             axis_forward='-Y', axis_up='Z', apply_unit_scale=True, bake_anim=False,
                             mesh_smooth_type='FACE')
    obj.data.calc_loop_triangles()
    kit.append(dict(name=obj.name, triangles=len(obj.data.loop_triangles), dimensions_cm=list(obj.dimensions),
                    materials=[m.name for m in obj.data.materials]))
    obj.hide_set(True)
    parts.clear()


# Gabled enclosure with folded roof sections, eaves, braces and standing seams.
for side in (-1, 1):
    rise, run = 151, -side*705
    length = math.hypot(rise, run)
    pitch = math.atan2(-rise, run)
    box('Standing seam roof', (side*352.5, 0, 72.5), (length, 950, 18), 'Dark', 2).rotation_euler.y = pitch
    for y in range(-448, 449, 112):
        box('Raised roof seam', (side*352.5, y, 82.5), (length, 4, 11), 'Steel', 1).rotation_euler.y = pitch
    box('Box gutter', (side * 704, 0, -9), (22, 954, 25), 'Steel', 3)
    for y in (-451, 451):
        outline = [(0, y, 143), (side * 683, y, 0), (0, y, 0)]
        vertices = [(x, yy + offset, z) for offset in (-8, 8) for x, yy, z in outline]
        faces = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
        mesh('Pressed gable skin', vertices, faces if side < 0 else [f[::-1] for f in faces], 'Paint')
        for x in (120, 240, 360, 480, 600):
            beam('Gable batten', (side*x, y, 0), (side*x, y, 143*(1-x/683)), 6, 20, 'Steel')
box('Saddle cap', (0, 0, 152), (36, 954, 17), 'Steel', 4)
finish('SignalStoreRoof')
assert all(lo < actual < hi for lo, actual, hi in zip((1400, 940, 160), kit[-1]['dimensions_cm'], (1450, 970, 195)))

box('Pressed wall cassette', (0, 0, 0), (225, 13, 304), 'Paint', 3)
for x in (-107, -54, 0, 54, 107):
    box('Cladding seam', (x, 0, 0), (5, 19, 301), 'Steel', 1.2)
for z in (-148, 146):
    box('Kick flashing', (0, 0, z), (229, 23, 12), 'Dark', 2)
finish('SignalStoreCladding')

# Clearance uses the old jamb and collision envelope. This is a visual portal skin.
for x in (-228, 228):
    box('Roll-formed post', (x, 0, 176), (38, 92, 352), 'Dark', 5)
    box('Post face', (x, 0, 184), (30, 98, 322), 'Steel', 3)
    for z in (20, 316, 336):
        cyl('Anchor bolt', (x, -50, z), 4, 3, 'Pale', 'Y', 6)
        cyl('Anchor bolt', (x, 50, z), 4, 3, 'Pale', 'Y', 6)
    box('Guard strip', (x, 0, 85), (32, 105, 18), 'Amber', 2)
box('Folded header', (0, 0, 371), (498, 103, 49), 'Dark', 5)
box('Header cap', (0, 0, 384), (475, 114, 14), 'Steel', 3)
finish('ServicePortal')


def bulkhead(kind, width):
    box('Recessed equipment back', (0, 0, 198), (width, 30, 396), 'Dark', 4)
    for x in (-width/2 + 23, width/2 - 23):
        box('Folded side stile', (x, 0, 195), (40, 43, 386), 'Steel', 4)
    for z in (18, 358, 389):
        box('Riveted channel', (0, 0, z), (width - 24, 38, 13), 'Steel', 2)
    box('Recessed sign mount', (0, 0, 287), (width-56, 36, 78), 'Paint', 1.8)
    for x in (-width/2+42, width/2-42):
        box('Service circuit strip', (x, 0, 293), (7, 44, 28), 'Amber', 1)

    for side in (-1, 1):
        # Hardware wraps the face uniformly so the hardware keeps its silhouette on either side.
        if kind == 'Supply':
            x = side*143
            for dy in (-20, 20):
                tube('Supply conduit', [(x,dy,38),(x,dy,181),(x+side*12,dy,205),(x-side*38,dy,205)], 9, 'Steel', 10)
            for z in (70, 148, 183):
                cyl('Union collar', (x, 0, z), 18, 11, 'Paint', 'Z', 12)
        elif kind == 'Load':
            box('Load bank case', (side*137, 0, 120), (105, 58, 186), 'Paint', 5)
            for z in range(54, 185, 19):
                box('Vent lip', (side*137, 0, z), (84, 66, 5), 'Steel', 1)
        elif kind == 'Cradle':
            x = side*155
            box('Extractor rail', (x, 0, 126), (38, 53, 209), 'Steel', 3)
            for z in (76, 163):
                box('Lock carriage', (x, 0, z), (62, 70, 36), 'Paint', 4)
                box('Witness stripe', (x, 0, z), (42, 73, 6), 'Amber', 1)
        elif kind == 'Bus':
            for i in range(3):
                x = side*(103+i*33)
                beam('Insulated service trunk', (x,0,39),(x,0,222), 15, 56, 'Paint')
                for z in (65, 125, 181):
                    box('Ceramic bracket', (x,0,z), (22, 62, 15), 'Pale', 1.5)
        else:
            x = side*157
            cyl('Actuator sleeve', (x, 0, 95), 31, 122, 'Paint', 'Z', 16)
            cyl('Actuator rod', (x, 0, 184), 12, 77, 'Steel', 'Z', 12)
            for z in (42, 149, 221):
                cyl('Actuator bearing', (x, 0, z), 34, 15, 'Steel', 'Z', 16)
    finish(kind + 'Bulkhead')


for label, width in (('Supply', 490), ('Load', 490), ('Cradle', 490), ('Bus', 540), ('Interlock', 540)):
    bulkhead(label, width)

assert len(kit) == 8 and sum(r['triangles'] for r in kit) < 24000
for obj in bpy.context.scene.objects:
    obj.hide_set(False)
bpy.ops.wm.save_as_mainfile(filepath=str(here / 'CR06_ServiceArchitecture.blend'))
(out / 'mesh-manifest.json').write_text(json.dumps(kit, indent=2))
