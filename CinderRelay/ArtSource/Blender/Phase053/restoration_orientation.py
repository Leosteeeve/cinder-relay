"""Continuous authored contact frames; evaluated in Blender, never at runtime."""
from mathutils import Vector,Matrix

def basis(direction,normal):
    y=Vector(direction).normalized();z=Vector(normal);z=(z-y*z.dot(y)).normalized()
    return Matrix((y.cross(z),y,z)).transposed()

def contact_orientation(t,weapon,optic):
    gun=basis(weapon.to_3x3()@Vector((.3,0,-1)),weapon.to_3x3()@Vector((0,1,0))).to_quaternion()
    held=basis(optic.to_3x3()@Vector((0,1,.4)),optic.to_3x3()@Vector((0,-.4,1))).to_quaternion()
    rest=basis((1,0,0),(0,0,1)).to_quaternion()
    def mix(a,b,start,end):
        u=max(0,min(1,(t-start)/(end-start)));return a.slerp(b,u*u*(3-2*u))
    if t<3.3:return gun
    if t<4.4:return mix(gun,held,3.3,4.4)
    if t<12.15:return held
    if t<13:return mix(held,rest,12.15,13)
    if t<17.5:return rest
    return mix(rest,gun,17.5,18.3)

def contact_curl(t):
    def mix(a,b,start,end):
        u=max(0,min(1,(t-start)/(end-start)));return a+(b-a)*u*u*(3-2*u)
    if t<3.3:return .9
    if t<3.85:return mix(.9,.3,3.3,3.85)
    if t<4.4:return mix(.3,.85,3.85,4.4)
    if t<12.15:return .85
    if t<13:return mix(.85,.25,12.15,13)
    if t<17.5:return .25
    return mix(.25,.9,17.5,18.3)
