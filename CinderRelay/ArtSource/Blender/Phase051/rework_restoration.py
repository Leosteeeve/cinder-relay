"""Original editable derivative: connected gloves, two-bone IK, prop-relative grips.
Preserves Phase03/05 sources and all runtime sequence semantics. Exterior props only.
Run Blender --background --python this_file -- --export-dir <ignored exports>.
"""
import bpy, math, json, sys, argparse
from pathlib import Path
from mathutils import Vector, Matrix
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True)
out=Path(ap.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir);out.mkdir(parents=True,exist_ok=True)
src=Path(__file__).resolve().parent
original=src.parent/'Phase05/CR05_RookRestoration.blend'
bpy.ops.wm.open_mainfile(filepath=str(original));bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene.frame_set(0)
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01;scene.render.fps=30;scene.frame_start=0;scene.frame_end=660
with bpy.data.libraries.load(str(src/'CR051_Rook5.blend'),link=False) as (available,loaded):
 loaded.objects=['SM_CR051_Rook5','SM_CR051_SurveyOptic']
props={}
for o in loaded.objects:scene.collection.objects.link(o);props[o.name]=o
arm=bpy.data.armatures.new('CR051_ContactRig');rig=bpy.data.objects.new('CR051_RestorationRig',arm);scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(n,a,b,parent=None,connect=False):
 e=arm.edit_bones.new(n);e.head=a;e.tail=b;e.align_roll(Vector((0,0,1)))
 if parent:e.parent=arm.edit_bones[parent];e.use_connect=connect
 return e
bone('root',(0,0,0),(0,0,10));bone('weapon',(0,0,0),(10,0,0),'root');bone('optic',(0,0,0),(10,0,0),'root')
rest={};fingers={}
for side,sgn in [('L',-1),('R',1)]:
 s=Vector((-72,sgn*30,128));e=Vector((-42,sgn*45,111));w=Vector((-10,sgn*25,112));rest[side]=(s,e,w)
 bone('upperarm_'+side,s,e,'root');bone('forearm_'+side,e,w,'upperarm_'+side,True);bone('hand_'+side,w,w+Vector((7,0,0)),'forearm_'+side,True)
 fingers[side]=[]
 for d in range(5):
  inward=-sgn
  if d==0:start=w+Vector((2,inward*3.2,-.4));direction=Vector((.65,inward*.76,-.12)).normalized();length=6.3
  else:start=w+Vector((7.1,(d-2.5)*1.75,0));direction=Vector((1,(d-2.5)*.035,0)).normalized();length=(7.2,8.1,7.6,6.1)[d-1]
  parent='hand_'+side
  for j,ratio in enumerate((.44,.33,.23)):
   end=start+direction*length*ratio;n=f'finger{d}_{j}_{side}';bone(n,start,end,parent,j>0);fingers[side].append((n,start.copy(),end.copy(),.85 if d in(0,1,2,3) else .72));start=end;parent=n
bpy.ops.object.mode_set(mode='OBJECT')
def material(n,color,rough):
 m=bpy.data.materials.new(n);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;return m
glove=material('CR051_Glove',(.09,.07,.045),.76);cloth=material('CR051_Sleeve',(.15,.19,.18),.87);stitch=material('CR051_Seam',(.29,.22,.12),.8)
def ellipsoid(name,center,scale,mat,rotation=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=1,location=center);o=bpy.context.object;o.name=name;o.scale=scale
 if rotation:o.rotation_mode='QUATERNION';o.rotation_quaternion=rotation
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o
def capsule(name,a,b,r0,r1,mat):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();q=axis.to_track_quat('Z','Y');parts=[]
 bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=r0,radius2=r1,depth=(b-a).length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_mode='QUATERNION';o.rotation_quaternion=q;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 parts.append(o)
 for pos,r in[(a,r0),(b,r1)]:parts.append(ellipsoid(name+' round end',pos,(r,r,r),mat))
 return parts
def join(parts,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:
  # Joining unlike UV layer names otherwise leaves the hero's UV0 at a single texel.
  if o.data.uv_layers:o.data.uv_layers.active.name='SurfaceUV'
  o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
def distance(p,a,b):
 delta=b-a;f=max(0,min(1,(p-a).dot(delta)/delta.length_squared));return (p-(a+f*delta)).length
skins=[]
for side in('L','R'):
 s,e,w=rest[side]
 parts=[ellipsoid('Glove palm '+side,w+Vector((3.7,0,0)),(5.1,4.05,1.85),glove),ellipsoid('Thumb pad '+side,w+Vector((2,-(1 if side=='R' else -1)*2.4,-.7)),(3,2.3,1.6),glove)]
 for n,a,b,r in fingers[side]:parts+=capsule('Anatomical glove '+n,a,b,r,r*.9,glove)
 hand=join(parts,'Continuous glove '+side)
 # Union rounded anatomy before weighting: joints are genuinely connected surfaces.
 rem=hand.modifiers.new('Connected glove topology','REMESH');rem.mode='VOXEL';rem.voxel_size=.23;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
 sm=hand.modifiers.new('Glove surface relaxation','SMOOTH');sm.factor=.6;sm.iterations=4;bpy.ops.object.modifier_apply(modifier=sm.name)
 segments=[('hand_'+side,w,w+Vector((6,0,0)),2.0)]+fingers[side]
 groups={n:hand.vertex_groups.new(name=n) for n,_,_,_ in segments}
 for v in hand.data.vertices:
  distances=sorted([(distance(v.co,a,b),n) for n,a,b,_ in segments])[:3]
  weights=[1/max(.3,d)**4 for d,n in distances];total=sum(weights)
  for (_,n),weight in zip(distances,weights):groups[n].add([v.index],weight/total,'REPLACE')
 skins.append(hand)
 # Continuous shaped sleeves, broad elbow cuff, and a fitted wrist gauntlet.
 for bn,a,b,r0,r1 in[('upperarm_'+side,s,e,6.4,5),('forearm_'+side,e,w-Vector((2,0,0)),5.4,3.1)]:
  o=join(capsule('Sleeve '+bn,a,b,r0,r1,cloth),'Sleeve '+bn);g=o.vertex_groups.new(name=bn);g.add(list(range(len(o.data.vertices))),1,'REPLACE');skins.append(o)
 cuff=ellipsoid('Wrist gauntlet '+side,w-Vector((1,0,0)),(3,4.4,2.4),glove);g=cuff.vertex_groups.new(name='hand_'+side);g.add(list(range(len(cuff.data.vertices))),1,'REPLACE');skins.append(cuff)
 # Raised stitching reads as deliberate glove construction; bound to the palm.
 for y in(-2.8,2.8):
  o=join(capsule('Palm stitch '+side,w+Vector((.8,y,1.65)),w+Vector((5.7,y,1.65)),.065,.065,stitch),'Palm stitch');g=o.vertex_groups.new(name='hand_'+side);g.add(list(range(len(o.data.vertices))),1,'REPLACE');skins.append(o)
for n,bn in [('SM_CR051_Rook5','weapon'),('SM_CR051_SurveyOptic','optic')]:
 o=props[n];g=o.vertex_groups.new(name=bn);g.add(list(range(len(o.data.vertices))),1,'REPLACE');skins.append(o)
skin=join(skins,'SK_CR051_Restoration');mod=skin.modifiers.new('Contact rig deformation','ARMATURE');mod.object=rig
# Give newly modeled gloves stable surface UVs without replacing hero UVs.
uv=skin.data.uv_layers.active or skin.data.uv_layers.new(name='RestorationUV')
for face in skin.data.polygons:
 if not skin.data.materials[face.material_index].name.startswith(('CR051_Glove','CR051_Sleeve','CR051_Seam')):continue
 axes=((1,2),(0,2),(0,1))[max(range(3),key=lambda i:abs(face.normal[i]))]
 for li in face.loop_indices:
  v=skin.data.vertices[skin.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/20,v[axes[1]]/20)
def empty(name):
 o=bpy.data.objects.new(name,None);scene.collection.objects.link(o);o.empty_display_type='SPHERE';o.empty_display_size=2;return o
R=Matrix.Rotation(math.pi/2,4,'Z');anchors={};controls={};constraints={}
for side in('L','R'):
 handrot=arm.bones['hand_'+side].matrix_local.to_3x3().to_4x4()
 for prop,offset in [('weapon',(-22 if side=='L' else 26,14,-1)),('optic',(-8,12,10))]:
  a=empty('CONTACT_'+prop+'_'+side);a.matrix_world=Matrix.Translation(Vector(offset))@R.inverted()@handrot
  c=a.constraints.new('CHILD_OF');c.name='Prop local grip (editable)';c.target=rig;c.subtarget=prop;c.inverse_matrix=arm.bones[prop].matrix_local.inverted();anchors[(side,prop)]=a
 control=empty('IK_Hand_'+side);control.rotation_mode='QUATERNION';control.matrix_world=arm.bones['hand_'+side].matrix_local.copy();controls[side]=control
 constraints[side]={}
 for prop in('weapon','optic'):
  c=control.constraints.new('COPY_TRANSFORMS');c.name='Hold '+prop;c.target=anchors[(side,prop)];c.influence=0;constraints[side][prop]=c
 pole=empty('IK_ElbowPole_'+side);pole.location=(-40,-95 if side=='L' else 95,82)
 ik=rig.pose.bones['forearm_'+side].constraints.new('IK');ik.target=control;ik.pole_target=pole;ik.chain_count=2;ik.use_stretch=False
 if side=='R':ik.pole_angle=math.pi
 # Native Blender IK and Copy Rotation evaluated at export; controls stay editable.
 rot=rig.pose.bones['hand_'+side].constraints.new('COPY_ROTATION');rot.target=control;rot.target_space='WORLD';rot.owner_space='WORLD'
def sample(t,keys):
 if t<=keys[0][0]:return Vector(keys[0][1])
 for (a,va),(b,vb) in zip(keys,keys[1:]):
  if t<=b:u=(t-a)/(b-a);u=u*u*(3-2*u);return Vector(va).lerp(Vector(vb),u)
 return Vector(keys[-1][1])
gunkeys=[(0,(-40,-5,133)),(.8,(-32,-5,133)),(3,(0,-4,111)),(18.5,(0,-4,111)),(19.7,(-4,-4,114)),(22,(-42,-5,137))]
optkeys=[(0,(0,32,88)),(4,(0,32,88)),(6,(-8,15,111)),(7.5,(-8,15,111)),(9,(-2,5,114)),(12,(0,-4,115)),(14,(0,-4,111)),(18.5,(0,-4,111)),(19.7,(-4,-4,114)),(22,(-42,-5,137))]
influence={'L':{'weapon':[(0,1),(14.5,1),(16,0),(17.3,0),(18.5,1),(22,1)],'optic':[(0,0),(22,0)]},'R':{'weapon':[(0,1),(3.1,1),(4,0),(17.3,0),(18.5,1),(22,1)],'optic':[(0,0),(4.6,0),(5.4,1),(14.4,1),(15.8,0),(22,0)]}}
for side,control in controls.items():
 keys=[(0,rest[side][2]),(3,(-14,-26 if side=='L' else 22,110)),(4.6,(-14,-26 if side=='L' else 24,106)),(14.4,(-14,-26 if side=='L' else -12,121)),(16.5,(-32,-27 if side=='L' else 27,112)),(18.5,(-14,-26 if side=='L' else 22,110)),(22,(-56,-27 if side=='L' else 21,136))]
 for t,pos in keys:
  control.location=pos;control.rotation_quaternion=arm.bones['hand_'+side].matrix_local.to_quaternion();control.keyframe_insert('location',frame=round(t*30));control.keyframe_insert('rotation_quaternion',frame=round(t*30))
 for prop,keys in influence[side].items():
  for t,value in keys:c=constraints[side][prop];c.influence=value;c.keyframe_insert('influence',frame=round(t*30))
# Only deliberate prop beats are keyed; native Bezier handles provide continuous easing.
for prop,keys in [('weapon',gunkeys),('optic',optkeys)]:
 b=rig.pose.bones[prop];b.rotation_mode='QUATERNION'
 for t,pos in keys:
  b.matrix_basis=b.bone.matrix_local.inverted()@Matrix.Translation(Vector(pos))@R@b.bone.matrix_local
  b.keyframe_insert('location',frame=round(t*30));b.keyframe_insert('rotation_quaternion',frame=round(t*30))
for side in('L','R'):
 keys=[(0,.65),(3,.65),(4.4,.10),(5.4,.72),(14.4,.72),(15.8,.10),(17.3,.12),(18.5,.65),(22,.65)] if side=='R' else [(0,.65),(14.5,.65),(16,.12),(17.3,.12),(18.5,.65),(22,.65)]
 for n,a,b,r in fingers[side]:
  d,j=int(n[6]),int(n.split('_')[1])
  pb=rig.pose.bones[n];pb.rotation_mode='XYZ'
  for t,grip in keys:pb.rotation_euler=(-grip*(.75,1.15,.85)[j] if d else -.38,0,0);pb.keyframe_insert('rotation_euler',frame=round(t*30))
for action in bpy.data.actions:
 if action.users:
  try:
   for fc in action.fcurves:
    for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
  except AttributeError:pass
rig.animation_data.action.name='AN_CR051_RookRestoration_22s'
contact=[]
for sec in(1,3,6,8,10,13,14,19,21):
 scene.frame_set(round(sec*30));bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();er=rig.evaluated_get(deps)
 for side in('L','R'):
  ctrl=controls[side].evaluated_get(deps).matrix_world.translation;wrist=er.pose.bones['forearm_'+side].tail;contact.append({'seconds':sec,'hand':side,'ik_error_cm':(wrist-ctrl).length})
assert max(r['ik_error_cm'] for r in contact)<.75,contact
scene['source_baseline']=str(original);scene['quality']='Connected original prototype gloves; authored IK/ChildOf grip contacts, not final anatomical realism.'
scene['controls']='IK_Hand_L/R and IK_ElbowPole_L/R; CONTACT_* anchors; animated Copy Transforms influences for hand ownership.'
scene['export']='FBX centimeters, -Y forward/Z up, bake native IK. UE import transforms must be checked.'
scene.frame_set(180);bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);skin.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(src/'CR051_RookRestoration.blend'))
bpy.ops.export_scene.fbx(filepath=str(out/'SK_CR051_Restoration.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
skin.data.calc_loop_triangles();receipt={'source':str(src/'CR051_RookRestoration.blend'),'bones':len(arm.bones),'triangles':len(skin.data.loop_triangles),'duration':22,'contact_samples':contact,'constraints':[c.type for b in rig.pose.bones for c in b.constraints],'materials':[m.name for m in skin.data.materials],'visual_status':'Pending real Unreal playback'}
(out/'restoration-manifest.json').write_text(json.dumps(receipt,indent=2));print('CR051_RESTORATION_SOURCE_PASS '+json.dumps(receipt))
