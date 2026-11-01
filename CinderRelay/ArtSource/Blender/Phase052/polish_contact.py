"""Pose/contact derivative of Phase051. Keep meshes, bone names and runtime22s.
Field calibration is fictional exterior presentation, not weapon construction.
"""
import argparse,json,math,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True)
out=Path(ap.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir);out.mkdir(parents=True,exist_ok=True)
src=Path(__file__).resolve().parent;original=src.parent/'Phase051/CR051_RookRestoration.blend'
bpy.ops.wm.open_mainfile(filepath=str(original));bpy.context.preferences.filepaths.save_version=0
rig=bpy.data.objects['CR051_RestorationRig'];rig.name='CR052_RestorationRig'
skin=bpy.data.objects['SK_CR051_Restoration'];skin.name='SK_CR052_Restoration'
scene=bpy.context.scene;scene.frame_start=0;scene.frame_end=660;scene.render.fps=30
# Only action/constraint keys are replaced. Connected glove geometry and editable rig remain.
rig.animation_data_clear()
for side in('L','R'):
    for n in('IK_Hand_','IK_ElbowPole_'):bpy.data.objects[n+side].animation_data_clear()
    for prop in('weapon','optic'):
        a=bpy.data.objects['CONTACT_'+prop+'_'+side];a.animation_data_clear()
        a.location.y=10.4 if prop=='weapon' else 9.8
        a.location.z=6.5 if prop=='weapon' else 15.0
R=Matrix.Rotation(math.pi/2,4,'Z')
def prop_key(prop,t,pos,tilt=(0,0,0)):
    b=rig.pose.bones[prop];b.rotation_mode='QUATERNION'
    rotation=R@Matrix.Rotation(math.radians(tilt[0]),4,'X')@Matrix.Rotation(math.radians(tilt[1]),4,'Y')@Matrix.Rotation(math.radians(tilt[2]),4,'Z')
    b.matrix_basis=b.bone.matrix_local.inverted()@Matrix.Translation(Vector(pos))@rotation@b.bone.matrix_local
    b.keyframe_insert('location',frame=round(t*30));b.keyframe_insert('rotation_quaternion',frame=round(t*30))
gun=[(0,(-40,-5,133),(0,-3,0)),(.8,(-32,-5,134),(0,-2,0)),(2.6,(-1,-4,113),(0,1,0)),(3.2,(0,-4,111),(0,0,0)),(3.5,(0,-4,111),(0,0,0)),(18.2,(0,-4,111),(0,0,0)),(19.2,(-2,-4,115),(0,-4,0)),(20.5,(-12,-3,124),(0,-9,-2)),(21.1,(-20,-3,129),(0,-6,-1)),(22,(-42,-5,137),(0,0,0))]
for t,p,r in gun:prop_key('weapon',t,p,r)
# Continuous object ownership: approach; inspect tilt; align above mount; micro adjustment;
# short seating stroke; deliberate small confirmation roll; reveal. No object teleports.
optic=[(0,(0,32,88),(0,0,0)),(4.4,(0,32,88),(0,0,0)),(5.4,(-6,23,102),(8,-8,5)),
 (6.4,(-10,15,113),(10,-16,8)),(7.2,(-10,15,113),(-8,10,-5)),(8.1,(-6,10,115),(3,4,2)),
 (9.1,(-1.0,-3,116.5),(0,1,1.5)),(9.8,(.6,-4.8,116.0),(0,-1,-1)),
 (10.5,(0,-4,115.2),(0,0,0)),(11.2,(0,-4,112.2),(0,0,0)),(11.55,(0,-4,111),(0,0,0)),
 (11.8,(0,-4,111.2),(0,0,0)),(12.15,(0,-4,111),(0,0,0)),
 (14.6,(0,-4,111),(0,0,0)),(18.2,(0,-4,111),(0,0,0))]+gun[-4:]
for t,p,r in optic:prop_key('optic',t,p,r)
influences={
 'L':{'weapon':[(0,1),(15.6,1),(16.5,0),(17.6,0),(18.2,1),(22,1)],'optic':[(0,0),(22,0)]},
 'R':{'weapon':[(0,1),(3.3,1),(4.1,0),(17.5,0),(18.3,1),(22,1)],'optic':[(0,0),(4.05,0),(4.4,1),(12.15,1),(12.7,0),(22,0)]}}
for side in('L','R'):
    sign=-1 if side=='L' else 1
    # Bring shoulders slightly forward and outward: the elbow bends visibly rather than
    # spending the whole shot as a straight sleeve extending from the bottom edge.
    shoulder=rig.pose.bones['upperarm_'+side]
    for t,v in[(0,(6,sign*5,-2)),(3.4,(11,sign*8,-4)),(6.4,(13,sign*7,-3)),(10.5,(11,sign*8,-4)),(14,(12,sign*9,-4)),(18.2,(9,sign*6,-3)),(22,(5,sign*4,-1))]:
        shoulder.location=shoulder.bone.matrix_local.to_3x3().inverted()@Vector(v)
        shoulder.keyframe_insert('location',frame=round(t*30))
    pole=bpy.data.objects['IK_ElbowPole_'+side]
    for t,xyz in[(0,(-43,sign*80,92)),(3.4,(-34,sign*91,84)),(6.4,(-29,sign*81,95)),(9.5,(-32,sign*87,89)),(13,(-36,sign*90,85)),(17,(-42,sign*77,94)),(20.5,(-37,sign*83,98)),(22,(-44,sign*80,96))]:
        pole.location=xyz;pole.keyframe_insert('location',frame=round(t*30))
    control=bpy.data.objects['IK_Hand_'+side];control.rotation_mode='QUATERNION'
    rest=rig.data.bones['hand_'+side].matrix_local.to_quaternion()
    keys=[(0,(-14,sign*24,119)),(3.6,(-16,sign*25,117)),(4.05,(-12,25,102)),(4.4,(-10,24,103)),
          (12.15,(-10,-12,126)),(12.7,(-11,-11,125)),(13.15,(-9,-10,123)),
          (13.8,(-8.5,-10.5,122)),(14.3,(-10,-11,123)),(14.7,(-14,-12,126)),
          (16.5,(-27,sign*27,114)),(17.6,(-18,sign*24,118)),(18.3,(-12,sign*22,119)),(22,(-50,sign*22,139))]
    if side=='L':keys=[(0,(-14,-25,118)),(15.6,(-14,-26,118)),(16.5,(-24,-31,114)),(17.6,(-20,-26,116)),(18.2,(-12,-26,118)),(22,(-50,-27,140))]
    for t,pos in keys:
        control.location=pos
        # Intentional wrist roll for the exterior secure/confirm touch, not global shake.
        roll=math.radians(8 if 13.1<=t<=14.3 else -4 if 6<t<9 else 0)
        control.rotation_quaternion=Matrix.Rotation(roll,4,'X').to_quaternion()@rest
        control.keyframe_insert('location',frame=round(t*30));control.keyframe_insert('rotation_quaternion',frame=round(t*30))
    for prop,keys in influences[side].items():
        c=control.constraints['Hold '+prop]
        for t,v in keys:c.influence=v;c.keyframe_insert('influence',frame=round(t*30))
    # Independent finger acquisition/release: middle/ring settle before index; little
    # finger uses a shorter, softer wrap. Thumb opposition is asymmetric and deliberate.
    grips=[(0,.72),(3.35,.72),(3.8,.16),(4.05,.12),(4.4,.88),(11.55,.88),(12.2,.92),(12.7,.38),(13.15,.57),(14.3,.57),(14.8,.18),(17.6,.18),(18.3,.75),(22,.75)] if side=='R' else [(0,.72),(15.5,.72),(16.3,.18),(17.6,.18),(18.3,.75),(22,.75)]
    for digit in range(5):
        for j in range(3):
            b=rig.pose.bones[f'finger{digit}_{j}_{side}'];b.rotation_mode='XYZ'
            for t,g in grips:
                phase=(0,.07,0,.035,.105)[digit] if t not in(0,22) else 0
                strength=(.8,1.05,1.0,.94,.82)[digit]
                if digit==0:b.rotation_euler=(-g*(.45,.78,.65)[j],0,sign*g*.8 if j==0 else 0)
                else:b.rotation_euler=(-g*(.85,1.25,.93)[j]*strength,0,(digit-2.5)*.025 if j==0 else 0)
                b.keyframe_insert('rotation_euler',frame=min(660,round((t+phase)*30)))
for obj in [rig]+[bpy.data.objects[n+s] for n in('IK_Hand_','IK_ElbowPole_') for s in('L','R')]:
    if not obj.animation_data or not obj.animation_data.action:continue
    for fc in obj.animation_data.action.fcurves:
        for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
rig.animation_data.action.name='AN_CR052_RookRestoration_22s'
contact=[]
for sec in(1,3.4,4.4,6.4,7.2,9.8,11.55,12.15,13.8,15.5,18.3,20.5):
    scene.frame_set(round(sec*30));bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();er=rig.evaluated_get(deps)
    for side in('L','R'):
        ctrl=bpy.data.objects['IK_Hand_'+side].evaluated_get(deps).matrix_world.translation
        wrist=er.pose.bones['forearm_'+side].tail
        contact.append({'seconds':sec,'hand':side,'ik_error_cm':(wrist-ctrl).length,'wrist':list(wrist),'elbow':list(er.pose.bones['forearm_'+side].head)})
assert max(r['ik_error_cm'] for r in contact)<1.0,contact
scene['source_baseline']='../Phase051/CR051_RookRestoration.blend'
scene['contact_beats']='lift4.4-6.4 inspect6.4-8.1 align9.1 micro-adjust9.8 seat11.55 secure13.15-14.3 confirm15 reveal19.2-21.1'
scene['quality']='Editable original prototype; actual Unreal continuous visual review still required.'
scene.frame_set(294);bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);skin.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(src/'CR052_RookRestoration.blend'))
bpy.ops.export_scene.fbx(filepath=str(out/'SK_CR052_Restoration.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
skin.data.calc_loop_triangles()
(out/'contact-manifest.json').write_text(json.dumps({'source':str(src/'CR052_RookRestoration.blend'),'bones':len(rig.data.bones),'triangles':len(skin.data.loop_triangles),'duration':22,'contact_samples':contact,'mesh_rebuilt':False},indent=2))
print('CR052_CONTACT_SOURCE_PASS')
