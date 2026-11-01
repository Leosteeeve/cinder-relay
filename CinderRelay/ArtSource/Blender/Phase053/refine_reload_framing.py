"""Correct the owned Reload clip after actual native video exposed low framing.

Edits one existing action, no geometry/material/skeleton regeneration. The old
unit leaves below the view; the replacement is deliberately held up and turned
toward the camera so the five fictional ammunition indicators can be inspected.
"""
import argparse, ast, bpy, json, math, sys
from pathlib import Path
from mathutils import Matrix, Vector, Quaternion

ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True)
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
here=Path(__file__).resolve().parent;out=Path(args.export_dir)
source=here/'CR053_FirstPerson.blend';bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;assert scene.get('CR.Owner')=='CinderRelay.Phase053.FirstPerson.v1'
rig=bpy.data.objects['CR053_FirstPersonRig'];skin=bpy.data.objects['SK_CR053_FirstPersonArms']
action=bpy.data.actions['AN_CR053_Reload'];rig.animation_data.action=action
scene.frame_start=0;scene.frame_end=144
# Reuse the exact source authoring functions without executing its rebuild path.
tree=ast.parse((here/'author_first_person.py').read_text())
names={'frame_basis','hand','prop','pose','select'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'handling_helpers','exec'))
hand_basis={};curl_axes={}
for side in ('L','R'):
    w=rig.data.bones['wrist.'+side].head_local
    long=(rig.data.bones['finger3-1.'+side].head_local-w).normalized()
    normal=(rig.data.bones['finger2-1.'+side].head_local-w).cross(rig.data.bones['finger5-1.'+side].head_local-w).normalized()
    if normal.dot(Vector((0,-1 if side=='L' else 1,0)))<0:normal=-normal
    normal=(normal-long*normal.dot(long)).normalized()
    hand_basis[side]=Matrix((long.cross(normal),long,normal)).transposed()
    for digit in range(1,6):
        for segment in range(1,4):
            bone=rig.data.bones[f'finger{digit}-{segment}.{side}']
            curl_axes[bone.name]=bone.matrix_local.to_3x3().inverted()@(bone.tail_local-bone.head_local).cross(normal).normalized()
for fc in list(action.fcurves):action.fcurves.remove(fc)
keys=[
    (0,(0,0,0),0,0),(18,(0,0,0),0,1),(30,(0,0,-1),0,1),
    (46,(0,12,-6),-35,1),(57,(0,12,-35),-55,1),(66,(0,12,-35),-55,1),
    (82,(0,17,2),-65,1),(94,(0,17,2),-65,1),(103,(0,8,0),-30,1),
    (111,(0,0,0),0,1),(127,(0,0,0),0,.4),(144,(0,0,0),0,0)]
for f,feedpos,yaw,weight in keys:
    scene.frame_set(f)
    wm=Matrix.Translation((3*weight,5*weight,10*weight))@Matrix.Rotation(math.radians(-28*weight),4,'X')
    fm=Matrix.Translation(feedpos)@Matrix.Rotation(math.radians(yaw),4,'Z')
    pose(f,wm,feed=fm)
    if 18<=f<=111:
        # Grip tracks the same authored feed transform; never key an independent
        # world-space hand path while the component moves.
        grip=wm@fm
        hand('L',grip@Vector((5,5,-11)),grip.to_3x3()@Vector((.2,-1,.55)),grip.to_3x3()@Vector((0,.5,1)),.85,f)
    bpy.context.view_layer.update()
for fc in action.fcurves:
    for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
scene['CR.ReloadFramingRevision']=1;scene.frame_set(0)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
select([rig,skin],rig)
bpy.ops.export_scene.fbx(filepath=str(out/'AN_CR053_Reload.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
(out/'reload-framing.json').write_text(json.dumps({'action':action.name,'seconds':2.4,'native_review_pending':True,'geometry_changed':False,'keys':keys},indent=2))
print('CR053_RELOAD_FRAMING_PASS')
