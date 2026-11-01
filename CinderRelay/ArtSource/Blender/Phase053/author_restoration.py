"""Retarget the preserved 22s presentation to the same Phase053 human arms.
New derivative only. Weapon path is sampled from the accepted old source;
editable IK targets author the new contact/release poses. No runtime transaction.
"""
import argparse,bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True);ap.add_argument('--rebuild-owned',action='store_true')
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);here=Path(__file__).resolve().parent;out=Path(args.export_dir);out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(here))
from rig_contact import calibrate_pole
from restoration_orientation import contact_orientation,contact_curl
dest=here/'CR053_RookRestoration.blend'
if dest.exists():
    assert args.rebuild_owned
    bpy.ops.wm.open_mainfile(filepath=str(dest));assert bpy.context.scene.get('CR.Owner')=='CinderRelay.Phase053.Restoration.v1'
bpy.ops.wm.open_mainfile(filepath=str(here.parent/'Phase052/CR052_RookRestoration.blend'))
old=bpy.data.objects['CR052_RestorationRig'];weapon_path={}
for frame in range(661):
    bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
    weapon_path[frame]=old.pose.bones['weapon'].matrix@old.data.bones['weapon'].matrix_local.inverted()
bpy.ops.wm.open_mainfile(filepath=str(here/'CR053_FirstPerson.blend'));bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene.render.fps=30;scene.frame_start=0;scene.frame_end=660
scene['CR.Owner']='CinderRelay.Phase053.Restoration.v1'
rig=bpy.data.objects['CR053_FirstPersonRig'];skin=bpy.data.objects['SK_CR053_FirstPersonArms'];rig.animation_data_clear();rig.name='CR053_RestorationRig';skin.name='SK_CR053_Restoration'
for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
# Move the human shoulders to the bench; keep original limb lengths and hands.
offset=Vector((-41,0,150))
for v in skin.data.vertices:v.co+=offset
bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
# Connected endpoints propagate edits to their neighbors. Snapshot and disconnect
# first so a translated shared elbow is never translated twice.
original={b.name:(b.head.copy(),b.tail.copy(),b.use_connect) for b in rig.data.edit_bones}
for bone in rig.data.edit_bones:bone.use_connect=False
for bone in rig.data.edit_bones:
    if bone.name not in ('root','weapon','optic','feed','cycle_handle'):
        bone.head=original[bone.name][0]+offset;bone.tail=original[bone.name][1]+offset
for bone in rig.data.edit_bones:bone.use_connect=original[bone.name][2]
bpy.ops.object.mode_set(mode='OBJECT');bpy.context.view_layer.update()
rig.animation_data_create();action=bpy.data.actions.new('AN_CR053_RookRestoration');action.use_fake_user=True;rig.animation_data.action=action
def basis(direction,normal):
    y=Vector(direction).normalized();z=Vector(normal);z=(z-y*z.dot(y)).normalized();return Matrix((y.cross(z),y,z)).transposed()
rest={};axes={}
for side in ('L','R'):
    w=rig.data.bones['wrist.'+side].head_local
    y=(rig.data.bones['finger3-1.'+side].head_local-w).normalized();z=(rig.data.bones['finger2-1.'+side].head_local-w).cross(rig.data.bones['finger5-1.'+side].head_local-w).normalized()
    if z.dot(Vector((0,-1 if side=='L' else 1,0)))<0:z=-z
    rest[side]=basis(y,z)
    for d in range(1,6):
        for part in range(1,4):
            b=rig.data.bones[f'finger{d}-{part}.{side}'];axes[b.name]=b.matrix_local.to_3x3().inverted()@(b.tail_local-b.head_local).cross(z).normalized()
def hand(side,position,direction,normal,curl,frame):
    pb=rig.pose.bones['CTRL_Hand.'+side];pb.rotation_mode='QUATERNION'
    rot=basis(direction,normal)@rest[side].inverted()@rig.data.bones['wrist.'+side].matrix_local.to_3x3()
    pb.matrix=Matrix.Translation(position)@rot.to_4x4();pb.keyframe_insert('location',frame=frame);pb.keyframe_insert('rotation_quaternion',frame=frame)
    for d in range(1,6):
        for part in range(1,4):
            p=rig.pose.bones[f'finger{d}-{part}.{side}'];p.rotation_mode='QUATERNION'
            p.rotation_quaternion=Quaternion(axes[p.name],math.radians((48,68,38)[part-1])*curl*(.95 if d==1 else .8 if d==2 else 1))
            if d==1 and part==1:
                axis=p.bone.matrix_local.to_3x3().inverted()@rest[side].col[1];p.rotation_quaternion=Quaternion(axis,math.radians(-42 if side=='L' else 42))*p.rotation_quaternion
            p.keyframe_insert('rotation_quaternion',frame=frame)
def prop(name,matrix,frame):
    p=rig.pose.bones[name];p.rotation_mode='QUATERNION';p.matrix=matrix@p.bone.matrix_local
    p.keyframe_insert('location',frame=frame);p.keyframe_insert('rotation_quaternion',frame=frame)
R=Matrix.Rotation(math.pi/2,4,'Z')
# Same activation/seat timings as LS_CR052; optic starts on the nearer right-side
# surface to fit real human reach, then is held through inspection and seating.
optic_keys=[(0,(-8,-16,100),(0,0,0)),(4.4,(-8,-16,100),(0,0,0)),(5.4,(-10,-14,110),(7,-8,4)),
 (6.4,(-9,-13,116),(10,-12,6)),(7.2,(-9,-13,116),(-6,8,-4)),(8.1,(-6,-9,116),(3,4,2)),
 (9.1,(-1,-3,116.5),(0,1,1)),(10.5,(0,-4,115.2),(0,0,0)),(11.2,(0,-4,112.2),(0,0,0)),
 (11.55,(0,-4,111),(0,0,0)),(12.15,(0,-4,111),(0,0,0)),(18.2,(0,-4,111),(0,0,0))]
def optic_at(t):
    if t>=18.2:return weapon_path[round(t*30)]
    for i in range(len(optic_keys)-1):
        a,b=optic_keys[i:i+2]
        if a[0]<=t<=b[0]:
            u=(t-a[0])/(b[0]-a[0]);u=u*u*(3-2*u);pos=Vector(a[1]).lerp(Vector(b[1]),u);tilt=Vector(a[2]).lerp(Vector(b[2]),u)
            return Matrix.Translation(pos)@R@Matrix.Rotation(math.radians(tilt.x),4,'X')@Matrix.Rotation(math.radians(tilt.y),4,'Y')@Matrix.Rotation(math.radians(tilt.z),4,'Z')
    return Matrix.Translation(optic_keys[0][1])@R
def blend(a,b,t,start,end):
    u=max(0,min(1,(t-start)/(end-start)));u=u*u*(3-2*u);return a.lerp(b,u)
errors=[]
# Dense prop sampling preserves the old trajectory; contact targets are explicit
# at 15Hz with baked 30Hz export. Finger curls only change at grasp/release beats.
for frame in range(0,661,2):
    t=frame/30
    # Keep the original path shape/timing, move the presentation within human
    # reach on the near half of the same bench. Shoulder cuts stay behind view.
    near_side=Matrix.Translation((-25,0,0))
    wm=near_side@weapon_path[frame];om=near_side@optic_at(t)
    prop('weapon',wm,frame);bpy.context.view_layer.update()
    prop('optic',om,frame);prop('feed',wm,frame);prop('cycle_handle',wm,frame)
    right_grip=wm@Vector((-20,-5,1));left_grip=wm@Vector((18,7,-10))
    optic_grip=om@Vector((-8,-4,6));rest_right=Vector((-53,-25,112));rest_left=Vector((-55,22,108))
    if t<3.3:rp=right_grip;curl=.9;rot=wm.to_3x3();direction=rot@Vector((.3,0,-1));normal=rot@Vector((0,1,0))
    elif t<4.4:
        rp=blend(right_grip,optic_grip,t,3.3,4.4);curl=.45;direction=Vector((-1,0,.1));normal=Vector((0,0,1))
    elif t<12.15:rp=optic_grip;curl=.85;direction=om.to_3x3()@Vector((0,1,.4));normal=om.to_3x3()@Vector((0,-.4,1))
    elif t<13:rp=blend(optic_grip,rest_right,t,12.15,13);curl=.25;direction=Vector((1,0,0));normal=Vector((0,0,1))
    elif t<17.5:rp=rest_right;curl=.25;direction=Vector((1,0,0));normal=Vector((0,0,1))
    else:rp=blend(rest_right,right_grip,t,17.5,18.3);curl=.9;direction=wm.to_3x3()@Vector((.3,0,-1));normal=wm.to_3x3()@Vector((0,1,0))
    if 15.6<t<16.5:lp=blend(left_grip,rest_left,t,15.6,16.5)
    elif 16.5<=t<17.6:lp=rest_left
    elif 17.6<=t<18.2:lp=blend(rest_left,left_grip,t,17.6,18.2)
    else:lp=left_grip
    orientation=contact_orientation(t,wm,om)
    hand('R',rp,orientation@Vector((0,1,0)),orientation@Vector((0,0,1)),contact_curl(t),frame)
    hand('L',lp,wm.to_3x3()@Vector((.2,-1,.55)),wm.to_3x3()@Vector((0,.5,1)),.85 if t<15.6 or t>=18.2 else .3,frame)
    scene.frame_set(frame);bpy.context.view_layer.update()
    errors.append(max((rig.pose.bones['wrist.'+s].head-rig.pose.bones['CTRL_Hand.'+s].head).length for s in ('L','R')))
for fc in action.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
pole_calibration={s:calibrate_pole(rig,s,180,(-62,38 if s=='L' else -38,98)) for s in ('L','R')}
# Share one skeletal draw source with the bench, keeping editable original props
# as hidden source copies; no independent character identity or primitive hands.
meshes=[skin]+[bpy.data.objects[n] for n in ('SM_CR051_Rook5','SM_CR051_SurveyOptic','SM_CR053_Feed','SM_CR053_CycleHandle')]
bpy.ops.object.select_all(action='DESELECT')
for obj in meshes:obj.hide_set(False);obj.select_set(True)
bpy.context.view_layer.objects.active=skin;bpy.ops.object.join();skin=bpy.context.object
scene.frame_set(180)
camera=scene.camera;camera.location=(-66,0,172);camera.rotation_euler=(Vector((0,0,111))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=28
for lamp in [o for o in bpy.data.objects if o.type=='LIGHT']:lamp.location.z+=135
scene['CR.Status']='Human-arm workbench derivative. Actual UE contact and lifecycle review pending.'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(out/'SK_CR053_Restoration.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
scene.render.filepath=str(out/'workbench-blender-contact.png');bpy.ops.render.render(write_still=True)
(out/'restoration-source.json').write_text(json.dumps({'source':str(dest),'seconds':22,'fps':30,'max_wrist_target_error_cm_before_pole_calibration':max(errors),'pole_calibration':pole_calibration,'native_review_pending':True},indent=2))
print('CR053_RESTORATION_SOURCE_PASS max_target_error_cm='+str(max(errors)))
