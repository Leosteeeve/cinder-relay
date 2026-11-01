"""Edit only existing owned wrist orientation keys. Preserve geometry/UVs/props."""
import bpy,sys,argparse,json,math
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from restoration_orientation import contact_orientation,contact_curl,basis
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True);args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(args.export_dir);source=here/'CR053_RookRestoration.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
assert scene.get('CR.Owner')=='CinderRelay.Phase053.Restoration.v1'
rig=bpy.data.objects['CR053_RestorationRig'];mesh=bpy.data.objects['SK_CR053_Restoration'];action=rig.animation_data.action
assert not scene.get('CR.ContinuousFingerRevision'),'Already applied; inspect before repeating'
w=rig.data.bones['wrist.R'].head_local;y=rig.data.bones['finger3-1.R'].head_local-w
z=(rig.data.bones['finger2-1.R'].head_local-w).cross(rig.data.bones['finger5-1.R'].head_local-w)
if z.dot(Vector((0,1,0)))<0:z=-z
rest=basis(y,z);target=rig.pose.bones['CTRL_Hand.R'];before=[];after=[]
def sample():
    values=[]
    for f in range(661):
        scene.frame_set(f);values.append(target.matrix.to_quaternion().copy())
    return max(math.degrees(a.rotation_difference(b).angle) for a,b in zip(values,values[1:]))
old=sample()
if scene.get('CR.ContinuousContactRevision'):
    old=json.loads((out/'orientation-continuity.json').read_text())['before_max_degrees_per_30fps_frame']
for frame in range(0,661,2):
    scene.frame_set(frame)
    wm=rig.pose.bones['weapon'].matrix@rig.data.bones['weapon'].matrix_local.inverted()
    om=rig.pose.bones['optic'].matrix@rig.data.bones['optic'].matrix_local.inverted()
    orientation=contact_orientation(frame/30,wm,om)
    m=Matrix.Translation(target.matrix.translation)@orientation.to_matrix().to_4x4()@rest.inverted().to_4x4()@rig.data.bones['wrist.R'].matrix_local.to_3x3().to_4x4()
    target.matrix=m;target.keyframe_insert('rotation_quaternion',frame=frame)
    for digit in range(1,6):
        for segment in range(1,4):
            bone=rig.data.bones[f'finger{digit}-{segment}.R'];p=rig.pose.bones[bone.name]
            axis=bone.matrix_local.to_3x3().inverted()@(bone.tail_local-bone.head_local).cross(rest.col[2]).normalized()
            p.rotation_mode='QUATERNION'
            p.rotation_quaternion=Quaternion(axis,math.radians((48,68,38)[segment-1])*contact_curl(frame/30)*(.95 if digit==1 else .8 if digit==2 else 1))
            if digit==1 and segment==1:
                opposition=bone.matrix_local.to_3x3().inverted()@rest.col[1]
                p.rotation_quaternion=Quaternion(opposition,math.radians(42))*p.rotation_quaternion
            p.keyframe_insert('rotation_quaternion',frame=frame)
for fc in action.fcurves:
    if 'CTRL_Hand.R' in fc.data_path and 'rotation_quaternion' in fc.data_path:
        for k in fc.keyframe_points:k.interpolation='LINEAR'
new=sample();assert new<25,(old,new)
scene['CR.ContinuousContactRevision']=1;scene['CR.ContinuousFingerRevision']=1;bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(source));scene.frame_set(0)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(out/'SK_CR053_Restoration.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
(out/'orientation-continuity.json').write_text(json.dumps({'before_max_degrees_per_30fps_frame':old,'after_max_degrees_per_30fps_frame':new,'geometry_unchanged':True,'human_playback_acceptance':False},indent=2))
print('CR053_ORIENTATION_PASS',old,new)
