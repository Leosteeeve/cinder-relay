"""Blender-only pole calibration for the original human two-bone editing rig."""
import bpy,math
from mathutils import Vector

def calibrate_pole(rig,side,frame,world_hint):
    """Solve the rest-roll offset against an explicit elbow target, then keep it.
    IK pole_angle depends on bone roll; zero is not anatomically meaningful.
    This authoring-time angular search never runs in Unreal or changes reach.
    """
    scene=bpy.context.scene;scene.frame_set(frame)
    target=rig.pose.bones['CTRL_Elbow.'+side]
    transform=target.matrix.copy();transform.translation=Vector(world_hint);target.matrix=transform
    ik=rig.pose.bones['CTRL_forearm.'+side].constraints[0]
    best=(float('inf'),0)
    for step in range(144):
        angle=-math.pi+step*math.tau/144;ik.pole_angle=angle;bpy.context.view_layer.update()
        elbow=rig.pose.bones['CTRL_forearm.'+side].head
        score=(elbow-Vector(world_hint)).length_squared
        if score<best[0]:best=(score,angle)
    ik.pole_angle=best[1];bpy.context.view_layer.update()
    return {'pole_angle_degrees':math.degrees(best[1]),'hint':list(world_hint),'elbow':list(rig.pose.bones['CTRL_forearm.'+side].head)}
