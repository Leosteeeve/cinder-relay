"""Re-key/export only the existing rig; no geometry regeneration. Open the .blend first."""
import bpy,sys,argparse
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--export-dir',required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(__file__).resolve().parent;sys.path.insert(0,str(source));from animate_restoration import author
assert Path(bpy.data.filepath)==source/'CR03_RookRestoration.blend'
rig=bpy.data.objects['CR03_RestorationRig'];skin=bpy.data.objects['SK_CR03_Restoration'];author(rig)
bpy.context.scene.frame_set(90);bpy.context.view_layer.update()
from mathutils import Vector
assert (rig.pose.bones['hand_L'].matrix.translation-Vector((-19,-24,111))).length<.01
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(source/'CR03_RookRestoration.blend'))
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);skin.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(Path(args.export_dir)/'SK_CR03_Restoration.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,bake_anim_step=1,mesh_smooth_type='FACE')
print('CR03_ANIMATION_EXPORTED',rig.animation_data.action.name)
