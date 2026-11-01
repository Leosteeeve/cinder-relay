"""Pose-only refinement of the Phase051 source; no mesh/texture/rig regeneration."""
import bpy,sys,argparse,math
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True);out=Path(ap.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir)
src=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(src/'CR051_RookRestoration.blend'));bpy.context.preferences.filepaths.save_version=0
rig=bpy.data.objects['CR051_RestorationRig'];skin=bpy.data.objects['SK_CR051_Restoration'];scene=bpy.context.scene
for side in('L','R'):
 for prop in('weapon','optic'):
  anchor=bpy.data.objects['CONTACT_'+prop+'_'+side];anchor.location.y=12 if prop=='weapon' else 10
  if prop=='weapon':anchor.location.z=2
 keys=[(0,.65),(3,.65),(4.4,.10),(5.4,.72),(14.4,.72),(15.8,.10),(17.3,.12),(18.5,.65),(22,.65)] if side=='R' else [(0,.65),(14.5,.65),(16,.12),(17.3,.12),(18.5,.65),(22,.65)]
 for j in range(3):
  b=rig.pose.bones[f'finger0_{j}_{side}'];b.rotation_mode='XYZ'
  for t,grip in keys:
   b.rotation_euler=(-grip*(.5,.8,.6)[j],0,(-1 if side=='L' else 1)*grip*.85 if j==0 else 0);b.keyframe_insert('rotation_euler',frame=round(t*30))
scene['contact_refinement']='2cm palm approach; thumb acquires opposing grip and releases with each deliberate contact. Pose-only derivative edit.'
scene.frame_set(210);bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);skin.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(src/'CR051_RookRestoration.blend'))
bpy.ops.export_scene.fbx(filepath=str(out/'SK_CR051_Restoration.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
print('CR051_CONTACT_TUNED_NO_GEOMETRY_REGENERATION')
