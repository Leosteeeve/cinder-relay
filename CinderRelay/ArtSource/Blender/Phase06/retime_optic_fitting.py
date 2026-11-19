"""Retime the accepted hand and prop motion in one editable Phase06 derivative."""
import argparse
import json
from pathlib import Path
import sys

import bpy


args = argparse.ArgumentParser()
args.add_argument('--export-dir', required=True, type=Path)
out = args.parse_args(sys.argv[sys.argv.index('--') + 1:]).export_dir.resolve()
out.mkdir(parents=True, exist_ok=True)
here = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(here.parent / 'Phase053/CR053_RookRestoration.blend'))
rig = bpy.data.objects['CR053_RestorationRig']
skin = bpy.data.objects['SK_CR053_Restoration']
original = rig.animation_data.action
action = original.copy()
action.name = 'AN_CR06_OpticFitting'
action.use_fake_user = True
rig.animation_data.action = action

# Move the reach earlier and hold the seating/check portion longer. The same
# monotone mapping is used for every hand, grip target, wrist and prop track.
points = [(0, 0), (99, 75), (132, 117), (162, 147), (220, 216),
          (300, 312), (365, 396), (390, 423), (450, 450), (660, 660)]


def remap(frame):
    for (start, target), (end, finish) in zip(points, points[1:]):
        if frame <= end:
            return target + (frame-start) * (finish-target) / (end-start)
    return frame


for curve in action.fcurves:
    for key in curve.keyframe_points:
        key.co.x = remap(key.co.x)
    curve.update()

bpy.context.scene.frame_set(0)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(here / 'CR06_OpticFitting.blend'), relative_remap=True)
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
skin.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.export_scene.fbx(filepath=str(out / 'AN_CR06_OpticFitting.fbx'), use_selection=True,
                         object_types={'ARMATURE', 'MESH'}, axis_forward='-Y', axis_up='Z',
                         apply_unit_scale=True, add_leaf_bones=False, use_armature_deform_only=True,
                         bake_anim=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                         bake_anim_simplify_factor=0)
(out / 'retime.json').write_text(json.dumps(dict(frames=points, duration=22, curves=len(action.fcurves),
                                                seat=round(remap(347)), secure=round(remap(400))), indent=2))
