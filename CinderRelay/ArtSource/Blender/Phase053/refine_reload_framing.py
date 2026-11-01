"""Non-destructive wrist/contact correction of the Phase053 handling source.

Preserves the original .blend and every previous action. Corrects the shared
right-hand grip in seven clips and the left-hand Reload prop-relative contact.
No rest pose, skin, pole, bone name, runtime duration or cosmetic cue changes.
"""
import argparse, ast, bpy, json, math, sys
from pathlib import Path
from mathutils import Matrix, Vector, Quaternion

ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True)
ap.add_argument('--replace-owned-derivative',action='store_true')
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
here=Path(__file__).resolve().parent;out=Path(args.export_dir)
source=here/'CR053_FirstPerson.blend';destination=here/'CR053_FirstPerson_ReloadCorrected.blend'
if destination.exists():
    assert args.replace_owned_derivative,'Use explicit replacement for the owned corrected derivative'
    bpy.ops.wm.open_mainfile(filepath=str(destination))
    assert bpy.context.scene.get('CR.ReloadRigCorrection')==1
bpy.ops.wm.open_mainfile(filepath=str(source));out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene;assert scene.get('CR.Owner')=='CinderRelay.Phase053.FirstPerson.v1'
rig=bpy.data.objects['CR053_FirstPersonRig'];skin=bpy.data.objects['SK_CR053_FirstPersonArms']
clips=[bpy.data.actions['AN_CR053_'+n] for n in ('Idle','Walk','Sprint','ADS','FireCycle','Reload','Dry')]
for clip in clips:
    rollback=clip.copy();rollback.name=clip.name+'_Rollback_PreReloadFix';rollback.use_fake_user=True
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
# The inverted wrist also exists in the common ready pose, so correcting only
# Reload would snap back into the defect at the blend boundary. Only right-hand
# control/digit curves change in the other six clips; all prop/left curves stay.
for clip in clips:
    if clip==action:continue
    rig.animation_data.action=clip
    times=sorted({round(k.co.x) for fc in clip.fcurves for k in fc.keyframe_points})
    for f in times:
        scene.frame_set(f);bpy.context.view_layer.update()
        wm=rig.pose.bones['weapon'].matrix@rig.data.bones['weapon'].matrix_local.inverted()
        cycle={14:((-24,-8,-1),.55),20:((-29,-8,-1),.65),25:((-29,-8,-1),.65),35:((-24,-8,-1),.6)}
        pos,curl=cycle.get(f,((-27,-5,-7),.9)) if clip.name.endswith('FireCycle') else ((-27,-5,-7),.9)
        hand('R',wm@Vector(pos),wm.to_3x3()@Vector((1,0,.2)),wm.to_3x3()@Vector((0,1,0)),curl,f)
rig.animation_data.action=action
for fc in list(action.fcurves):action.fcurves.remove(fc)
keys=[
    (0,(0,0,0),0,0),(18,(0,0,0),0,1),(30,(0,0,-1),0,1),
    (46,(0,12,-6),-35,1),(57,(0,12,-35),-55,1),(66,(0,12,-35),-55,1),
    (82,(0,17,2),-65,1),(94,(0,17,2),-65,1),(103,(0,8,0),-30,1),
    (111,(0,0,0),0,1),(127,(0,0,0),0,.4),(144,(0,0,0),0,0)]
for f,feedpos,yaw,weight in keys:
    scene.frame_set(f)
    # Reduce the raised roll that pushed the supporting wrist over the stock.
    wm=Matrix.Translation((3*weight,5*weight,5*weight))@Matrix.Rotation(math.radians(-15*weight),4,'X')
    fm=Matrix.Translation(feedpos)@Matrix.Rotation(math.radians(yaw),4,'Z')
    pose(f,wm,feed=fm)
    if 18<=f<=111:
        # Grip tracks the same authored feed transform; never key an independent
        # world-space hand path while the component moves.
        grip=wm@fm
        hand('L',grip@Vector((-3,6,-14)),grip.to_3x3()@Vector((1,-.2,.25)),grip.to_3x3()@Vector((0,-1,0)),.85,f)
    bpy.context.view_layer.update()
for fc in action.fcurves:
    for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
scene['CR.ReloadFramingRevision']=2;scene['CR.ReloadRigCorrection']=1;scene.frame_set(0)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(destination))
for clip in clips:
    rig.animation_data.action=clip;scene.frame_start=0;scene.frame_end=round(clip.frame_range[1]);scene.frame_set(0)
    select([rig,skin],rig)
    filename='SK_CR053_FirstPersonArms' if clip.name.endswith('_Idle') else clip.name
    bpy.ops.export_scene.fbx(filepath=str(out/(filename+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
(out/'reload-framing.json').write_text(json.dumps({'source':str(destination),'action':action.name,'seconds':2.4,'native_review_pending':True,'geometry_changed':False,'rest_pose_changed':False,'pole_angles_changed':False,'corrected_clips':[c.name for c in clips],'keys':keys},indent=2))
print('CR053_RELOAD_FRAMING_PASS')
