"""Targeted derivative of the accepted Phase03 source. Never saves over Phase03.
Fix inward left thumb, preserve prop paths/22s beats, solve fixed-length elbows,
replace oscillating fingers with task-specific anticipation/hold/release poses.
"""
import bpy,math,json,sys,argparse
from pathlib import Path
from mathutils import Vector,Matrix
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True);out=Path(ap.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir)
src=Path(__file__).resolve().parent;original=src.parent/'Phase03/CR03_RookRestoration.blend'
bpy.ops.wm.open_mainfile(filepath=str(original));bpy.context.preferences.filepaths.save_version=0
rig=bpy.data.objects['CR03_RestorationRig'];skin=bpy.data.objects['SK_CR03_Restoration'];scene=bpy.context.scene
# Actual ownership is verified by the Armature modifier and named vertex weights.
assert any(m.type=='ARMATURE' and m.object==rig for m in skin.modifiers)
rig.animation_data_clear();scene.frame_set(0)
for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
thumb={skin.vertex_groups['finger0_'+str(j)+'_L'].index for j in range(3)}
pivot=rig.data.bones['hand_L'].head_local.y
for v in skin.data.vertices:
 if any(g.group in thumb and g.weight>.5 for g in v.groups):v.co.y=2*pivot-v.co.y
bpy.ops.object.select_all(action='DESELECT');rig.hide_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for j in range(3):
 b=rig.data.edit_bones['finger0_'+str(j)+'_L'];b.head.y=2*pivot-b.head.y;b.tail.y=2*pivot-b.tail.y
bpy.ops.object.mode_set(mode='OBJECT')
base=(original.parent/'animate_restoration.py').read_text()
old="shoulder,_,_=rest[side];sgn=-1 if side=='L' else 1;elbow=w+Vector((-29,sgn*12,-7))"
new="""shoulder,rest_elbow,rest_wrist=rest[side];sgn=-1 if side=='L' else 1
            a=(rest_elbow-shoulder).length;b=(rest_wrist-rest_elbow).length
            shoulder=shoulder.copy();delta=w-shoulder
            # A small shoulder reach keeps both segment lengths fixed; shoulder stays off-camera.
            reach=max(0,delta.length-(a+b)*.975);shoulder+=delta.normalized()*reach
            delta=w-shoulder;d=delta.length;axis=delta.normalized()
            pole=Vector((0,sgn,-.55));pole=(pole-axis*pole.dot(axis)).normalized()
            along=(a*a-b*b+d*d)/(2*d);elbow=shoulder+axis*along+pole*math.sqrt(max(0,a*a-along*along))"""
assert old in base;base=base.replace(old,new)
old="curl=.22+.14*math.sin(min(t,15)*.6+d*.3)\n                    b.rotation_euler=(curl if d else .25,0,0);b.keyframe_insert('rotation_euler')"
new="""grip=sample(t,[(0,(.52,0,0)),(3,(.55,0,0)),(3.7,(.12,0,0)),(5.2,(.62,0,0)),(12,(.62,0,0)),(14.4,(.38,0,0)),(16.4,(.12,0,0)),(18.4,(.55,0,0)),(22,(.55,0,0))]).x if side=='R' else sample(t,[(0,(.52,0,0)),(14,(.52,0,0)),(16,(.14,0,0)),(18.4,(.52,0,0)),(22,(.52,0,0))]).x
                    curl=grip*(.8,1.05,.7)[j]*(1+.05*(d-2))
                    b.rotation_euler=(curl if d else .25,0,0);b.keyframe_insert('rotation_euler')"""
assert old in base;base=base.replace(old,new)
scope={};exec(compile(base,'Phase05 targeted choreography','exec'),scope);scope['author'](rig)
rig.animation_data.action.name='AN_CR05_RookRestoration_22s';rig.name='CR05_RestorationRig';skin.name='SK_CR05_Restoration'
rig['phase05_changes']='Left thumb mirrored inward; fixed segment lengths with off-camera shoulder reach; stable authored grip holds; original prop curves and 22s duration retained.'
uv=skin.data.uv_layers.active or skin.data.uv_layers.new(name='SurfaceUV')
for face in skin.data.polygons:
 axes=((1,2),(0,2),(0,1))[max(range(3),key=lambda i:abs(face.normal[i]))]
 for li in face.loop_indices:
  v=skin.data.vertices[skin.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/80,v[axes[1]]/80)
# Rounded cuffs bridge existing segment joins without replacing the entire kit.
for side in ('L','R'):
 for joint,bn,radius in [('elbow','forearm_',5.5),('wrist','hand_',4.8)]:
  b=rig.data.bones[bn+side];bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=radius,location=b.head_local);o=bpy.context.object;o.name='CR05_'+joint+'_'+side;o.data.materials.append(bpy.data.materials['CR03_Cuff']);g=o.vertex_groups.new(name=bn+side);g.add(list(range(len(o.data.vertices))),1,'REPLACE')
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);skin.hide_set(False);skin.select_set(True);bpy.context.view_layer.objects.active=skin;bpy.ops.object.join()
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);skin.select_set(True);bpy.context.view_layer.objects.active=rig
scene.frame_start=0;scene.frame_end=660
bpy.ops.export_scene.fbx(filepath=str(out/'SK_CR05_Restoration.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0)
scene.frame_set(180);bpy.ops.wm.save_as_mainfile(filepath=str(src/'CR05_RookRestoration.blend'))
(out/'restoration-manifest.json').write_text(json.dumps({'original_untouched':str(original),'bones':len(rig.data.bones),'duration':22,'mesh':skin.name,'action':rig.animation_data.action.name,'thumb_mirrored':'L','visual_acceptance':'Requires Unreal playback review'},indent=2))
print('CR05_RESTORATION_SOURCE_PASS')
