"""Re-export the existing review source. FBX stays centimeters, glTF is meters."""
import bpy,sys,argparse,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True)
out=Path(ap.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir)
out.mkdir(parents=True,exist_ok=True)
source=Path(__file__).resolve().parent/'CR053_EliasArms.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
skin=bpy.data.objects['SK_CR053_EliasArms'];rig=bpy.data.objects['CR053_EliasRig']
bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.context.scene.frame_set(0)
bpy.ops.export_scene.fbx(filepath=str(out/'SK_CR053_EliasArms.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
# glTF has meter-native geometry. Normalize actual mesh/bone coordinates together;
# a scaled armature node leaves misleading bounds for static package inspectors.
# This scene is an export-only copy; the centimeter .blend and FBX stay unchanged.
for vertex in skin.data.vertices:vertex.co*=.01
bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
for bone in rig.data.edit_bones:bone.head*=.01;bone.tail*=.01
bpy.ops.object.mode_set(mode='OBJECT')
for obj in bpy.data.objects:
    if obj.type=='EMPTY':obj.location*=.01
for action in bpy.data.actions:
    for curve in action.fcurves:
        if curve.data_path.endswith('location'):
            for key in curve.keyframe_points:key.co.y*=.01;key.handle_left.y*=.01;key.handle_right.y*=.01
bpy.context.scene.unit_settings.scale_length=1
bpy.context.view_layer.update()
bpy.ops.export_scene.gltf(filepath=str(out/'SK_CR053_EliasArms.glb'),export_format='GLB',use_selection=True,export_animations=True,export_skins=True,export_yup=True,export_tangents=True)
print('CR053_EXPORT_PASS centimeters=FBX meters=GLB source_unchanged=true')
