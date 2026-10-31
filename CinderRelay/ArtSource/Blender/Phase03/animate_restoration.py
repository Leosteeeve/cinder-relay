"""Editable 22-second skeletal performance. Re-author action without regenerating geometry."""
import bpy, math
from mathutils import Vector, Matrix
def author(rig):
    scene=bpy.context.scene;armdata=rig.data
    rig.animation_data_clear()
    for old in list(bpy.data.actions):
        if old.name.startswith('AN_CR03_RookRestoration_22s') and old.users==0: bpy.data.actions.remove(old)
    rest={side:(armdata.bones['upperarm_'+side].head_local.copy(),armdata.bones['forearm_'+side].head_local.copy(),armdata.bones['hand_'+side].head_local.copy()) for side in ('L','R')}
    def sample(t,keys):
        if t<=keys[0][0]:return Vector(keys[0][1])
        for (a,va),(b,vb) in zip(keys,keys[1:]):
            if t<=b:u=(t-a)/(b-a);u=u*u*(3-2*u);return Vector(va).lerp(Vector(vb),u)
        return Vector(keys[-1][1])
    gunkeys=[(0,(-40,-5,133)),(.8,(-32,-5,133)),(3,(0,-4,111)),(18.5,(0,-4,111)),(19.7,(-4,-4,114)),(22,(-42,-5,137))]
    optic_keys=[(0,(10,42,88)),(4,(10,42,88)),(6,(-8,15,115)),(7.5,(-8,15,115)),(9,(-2,5,117)),(12,(0,-4,115)),(14,(0,-4,111)),(18.5,(0,-4,111)),(19.7,(-4,-4,114)),(22,(-42,-5,137))]
    rot=Matrix.Rotation(math.pi/2,4,'Z')
    def pose_matrix(name,mat):
        b=rig.pose.bones[name]; b.rotation_mode='QUATERNION'
        parent=b.bone.parent
        # Solve local basis from this frame's explicit parent target, not stale depsgraph matrices.
        parent_pose=targets.get(parent.name,parent.matrix_local) if parent else Matrix.Identity(4)
        parent_rest=parent.matrix_local if parent else Matrix.Identity(4)
        b.matrix_basis=b.bone.matrix_local.inverted() @ parent_rest @ parent_pose.inverted() @ mat
        targets[name]=mat.copy()
        b.keyframe_insert('location');b.keyframe_insert('rotation_quaternion');b.keyframe_insert('scale')
    def aim_matrix(head,tail):return Matrix.Translation(head)@(tail-head).to_track_quat('Y','Z').to_matrix().to_4x4()
    for f in range(0,661,2):
        targets={}
        scene.frame_set(f);t=f/30;g=sample(t,gunkeys);op=sample(t,optic_keys)
        pose_matrix('weapon',Matrix.Translation(g)@rot@armdata.bones['weapon'].matrix_local)
        # Optic follows exactly the same exterior alignment as the weapon after seating.
        pose_matrix('optic',Matrix.Translation(op)@rot@armdata.bones['optic'].matrix_local)
        left=sample(t,[(0,(-59,-25,132)),(.8,(-51,-25,132)),(3,(-19,-24,111)),(4,(-19,-24,110)),(14,(-19,-24,110)),(17,(-32,-27,109)),(18.5,(-19,-24,111)),(19.7,(-23,-24,114)),(22,(-61,-25,137))])
        right=sample(t,[(0,(-59,16,132)),(.8,(-51,16,132)),(3,(-19,17,111)),(4,(-3,39,106)),(6,(-21,12,133)),(7.5,(-21,12,133)),(9,(-15,2,135)),(12,(-13,-7,133)),(14,(-13,-7,129)),(15.5,(-13,-7,129)),(17,(-32,25,112)),(18.5,(-19,17,111)),(19.7,(-23,17,114)),(22,(-61,16,137))])
        for side,w in [('L',left),('R',right)]:
            shoulder,_,_=rest[side];sgn=-1 if side=='L' else 1;elbow=w+Vector((-29,sgn*12,-7))
            pose_matrix('upperarm_'+side,aim_matrix(shoulder,elbow));pose_matrix('forearm_'+side,aim_matrix(elbow,w));pose_matrix('hand_'+side,aim_matrix(w,w+Vector((10,0,0))))
            for d in range(5):
                for j in range(3):
                    b=rig.pose.bones[f'finger{d}_{j}_{side}'];b.rotation_mode='XYZ'
                    curl=.22+.14*math.sin(min(t,15)*.6+d*.3)
                    b.rotation_euler=(curl if d else .25,0,0);b.keyframe_insert('rotation_euler')
    rig.animation_data.action.name='AN_CR03_RookRestoration_22s'
