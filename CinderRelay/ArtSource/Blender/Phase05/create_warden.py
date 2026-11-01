"""Original clothed scout with editable weighted rig/actions. Centimeters, +X facing.
No external models, scans or motion data. Cosmetic animation never applies damage.
"""
import bpy, math, json, argparse, sys
from pathlib import Path
from mathutils import Vector, Matrix
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True)
out=Path(ap.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir);out.mkdir(parents=True,exist_ok=True)
src=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01;scene.render.fps=30
bpy.context.preferences.filepaths.save_version=0
mats={}
for name,color,metal,rough in [('Cloth',(.115,.145,.14),0,.88),('Armor',(.13,.18,.20),.45,.54),('Leather',(.055,.046,.035),0,.8),('Visor',(.055,.08,.08),.7,.24),('Rust',(.28,.14,.065),.35,.75),('Band',(.51,.32,.13),.1,.7)]:
 m=bpy.data.materials.new('CR05_Warden'+name);m.diffuse_color=(*color,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;mats[name]=m
parts=[]
def weight(o,bone,mat):
 o.data.materials.append(mats[mat]);g=o.vertex_groups.new(name=bone);g.add(list(range(len(o.data.vertices))),1,'REPLACE');parts.append(o);return o
def ellipsoid(name,loc,size,bone,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,radius=1,location=loc);o=bpy.context.object;o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for p in o.data.polygons:p.use_smooth=True
 return weight(o,bone,mat)
def plate(name,loc,size,bone,mat,r=1):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=o.modifiers.new('Tailored edge','BEVEL');mod.width=r;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name);return weight(o,bone,mat)
def limb(name,a,b,width,bone,mat):
 a,b=Vector(a),Vector(b);o=ellipsoid(name,(a+b)/2,(width,width*.95,(b-a).length*.57),bone,mat);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
data=bpy.data.armatures.new('CR05_WardenSkeleton');rig=bpy.data.objects.new('CR05_WardenRig',data);scene.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(n,h,t,parent='root'):
 b=data.edit_bones.new(n);b.head=h;b.tail=t
 if parent:b.parent=data.edit_bones[parent]
bone('root',(0,0,0),(0,0,10),None);bone('pelvis',(0,0,85),(0,0,105));bone('spine',(0,0,105),(0,0,138),'pelvis');bone('neck',(0,0,138),(0,0,150),'spine');bone('head',(0,0,150),(0,0,175),'neck')
rest={}
for side,s in [('L',-1),('R',1)]:
 hip=Vector((0,s*12,86));knee=Vector((3,s*13,48));ankle=Vector((0,s*13,10));shoulder=Vector((0,s*25,138));elbow=Vector((13,s*30,114));wrist=Vector((33,s*12,126))
 for n,h,t,par in [('thigh',hip,knee,'pelvis'),('shin',knee,ankle,'thigh_'+side),('foot',ankle,ankle+Vector((16,0,-4)),'shin_'+side),('upperarm',shoulder,elbow,'spine'),('forearm',elbow,wrist,'upperarm_'+side),('hand',wrist,wrist+Vector((8,0,0)),'forearm_'+side)]:bone(n+'_'+side,h,t,par)
 rest[side]=(hip,knee,ankle,shoulder,elbow,wrist)
bone('weapon',(39,4,132),(49,4,132),'spine');bpy.ops.object.mode_set(mode='OBJECT')
ellipsoid('Padded jacket',(0,0,119),(17,27,29),'spine','Cloth');ellipsoid('Coat skirt',(-1,0,90),(18,25,17),'pelvis','Cloth')
plate('Segmented chest shell',(15,0,125),(6,40,28),'spine','Armor',2)
for y in (-18,-6,6,18):plate('Belt utility pouch',(17,y,102),(10,9,14),'spine','Leather',1.5)
plate('Service backpack',(-20,0,123),(16,32,37),'spine','Armor',3);plate('Faded identity strip',(19,-7,133),(1,18,3),'spine','Band',.3)
ellipsoid('Hood',(0,0,156),(14,16,20),'head','Cloth');ellipsoid('Helmet crown',(0,0,165),(15,17,13),'head','Armor')
plate('Continuous dark visor',(12,0,159),(6,24,10),'head','Visor',3)
ellipsoid('Filter housing',(14,0,149),(7,10,7),'head','Leather')
for y in(-10,10):ellipsoid('Filter canister',(13,y,149),(5,5,5),'head','Armor')
for side,s in [('L',-1),('R',1)]:
 hip,knee,ankle,shoulder,elbow,wrist=rest[side]
 limb('Trouser thigh',hip,knee,11,'thigh_'+side,'Cloth');limb('Trouser lower',knee,ankle,8,'shin_'+side,'Cloth');ellipsoid('Knee pad',knee+Vector((7,0,0)),(5,8,10),'shin_'+side,'Armor')
 plate('Boot',(6,s*13,7),(29,17,14),'foot_'+side,'Leather',3);plate('Boot sole',(6,s*13,1.5),(30,18,3),'foot_'+side,'Armor',.6)
 limb('Jacket sleeve',shoulder,elbow,10,'upperarm_'+side,'Cloth');limb('Forearm wrap',elbow,wrist,8,'forearm_'+side,'Cloth');ellipsoid('Shoulder cap',shoulder,(11,12,11),'upperarm_'+side,'Armor')
 ellipsoid('Gloved hand',wrist+Vector((4,0,0)),(8,5,5),'hand_'+side,'Leather');plate('Wrist guard',wrist-Vector((2,0,-4)),(10,11,3),'hand_'+side,'Armor')
# Original project ROOK exterior, same identity and authored material provenance.
with bpy.data.libraries.load(str(src.parent/'Phase03/CR03_RookRestoration.blend'),link=False) as (a,b):b.objects=['SM_CR03_Rook5']
gun=b.objects[0];scene.collection.objects.link(gun);gun.hide_set(False);gun.hide_render=False;gun.location=(39,4,132);gun.scale=(.65,.65,.65);g=gun.vertex_groups.new(name='weapon');g.add(list(range(len(gun.data.vertices))),1,'REPLACE');parts.append(gun)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();skin=bpy.context.object;skin.name='SK_CR05_AshWarden';scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
uv=skin.data.uv_layers.active or skin.data.uv_layers.new(name='ClothUV')
for face in skin.data.polygons:
 axes=((1,2),(0,2),(0,1))[max(range(3),key=lambda i:abs(face.normal[i]))]
 for li in face.loop_indices:
  v=skin.data.vertices[skin.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/80,v[axes[1]]/80)
mod=skin.modifiers.new('Editable skin','ARMATURE');mod.object=rig;skin.parent=rig
def aim(h,t):return Matrix.Translation(h)@(t-h).to_track_quat('Y','Z').to_matrix().to_4x4()
def ik(a,target,length1,length2,pole):
 d=target-a;dist=min(d.length,length1+length2-.01);axis=d.normalized();v=Vector(pole);v=(v-axis*v.dot(axis)).normalized();along=(length1**2-length2**2+dist**2)/(2*dist);return a+axis*along+v*math.sqrt(max(0,length1**2-along**2))
clips={'Idle':3,'Walk':1,'Alert':1.1,'Attack':.4,'Hit':.4,'Death':1.8};receipt=[]
for name,duration in clips.items():
 rig.animation_data_clear();end=round(duration*30);scene.frame_start=0;scene.frame_end=end
 for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
 for f in range(end+1):
  scene.frame_set(f);t=f/30;u=f/end;targets={}
  def pose(n,m):
   pb=rig.pose.bones[n];parent=pb.bone.parent;pr=parent.matrix_local if parent else Matrix.Identity(4);pp=targets.get(parent.name,pr) if parent else Matrix.Identity(4)
   pb.matrix_basis=pb.bone.matrix_local.inverted()@pr@pp.inverted()@m;pb.rotation_mode='QUATERNION';targets[n]=m
   for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=f)
  breathe=math.sin(t*2*math.pi/duration)*.6
  death=(u*u*(3-2*u)) if name=='Death' else 0
  root=Matrix.Translation((0,0,0))
  pose('root',root@data.bones['root'].matrix_local)
  # Collapse is an authored root/spine animation, with no damage or movement authority.
  body=Matrix.Translation((-18*death,0,-65*death))@Matrix.Translation((0,0,85))@Matrix.Rotation(-1.15*death,4,'Y')@Matrix.Translation((0,0,-85))
  if name=='Hit':body=Matrix.Translation((-4*math.sin(math.pi*u),0,0))@body
  if name=='Alert':body=Matrix.Rotation(.12*math.sin(math.pi*u),4,'Z')@body
  for n in ('pelvis','spine','neck','head'):pose(n,body@Matrix.Translation((0,0,breathe))@data.bones[n].matrix_local)
  for side,s in [('L',-1),('R',1)]:
   hip,knee,ankle,shoulder,elbow,wrist=rest[side];target=ankle.copy()
   if name=='Walk':phase=t*2*math.pi+(math.pi if s<0 else 0);target+=Vector((23*math.sin(phase),0,max(0,math.cos(phase))*9))
   k=ik(hip,target,(knee-hip).length,(ankle-knee).length,(1,0,0))
   pose('thigh_'+side,body@aim(hip,k));pose('shin_'+side,body@aim(k,target));pose('foot_'+side,body@Matrix.Translation(target-ankle)@data.bones['foot_'+side].matrix_local)
   recoil=-2.5*math.sin(math.pi*u)*math.exp(-u*4) if name=='Attack' else 0
   w=wrist+Vector((recoil,0,breathe));e=ik(shoulder,w,(elbow-shoulder).length,(wrist-elbow).length,(0,s,-1))
   pose('upperarm_'+side,body@aim(shoulder,e));pose('forearm_'+side,body@aim(e,w));pose('hand_'+side,body@Matrix.Translation(w-wrist)@data.bones['hand_'+side].matrix_local)
  pose('weapon',body@Matrix.Translation((recoil,0,breathe))@data.bones['weapon'].matrix_local)
 action=rig.animation_data.action;action.name='AN_CR05_Warden_'+name;action.use_fake_user=True
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);skin.select_set(True);bpy.context.view_layer.objects.active=rig
 filename='SK_CR05_AshWarden' if name=='Idle' else 'AN_CR05_Warden_'+name
 bpy.ops.export_scene.fbx(filepath=str(out/(filename+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0)
 receipt.append({'name':action.name,'seconds':duration,'export':filename+'.fbx'})
rig.animation_data.action=bpy.data.actions['AN_CR05_Warden_Idle'];scene.frame_end=90;scene.frame_set(0);skin.data.calc_loop_triangles()
rig['quality']='Original stylized industrial scout, rigid cloth panels and rounded weighted limbs; provisional anatomy, no external motion data.'
bpy.ops.wm.save_as_mainfile(filepath=str(src/'CR05_AshWarden.blend'))
(out/'warden-manifest.json').write_text(json.dumps({'bones':len(data.bones),'triangles':len(skin.data.loop_triangles),'actions':receipt,'materials':[m.name for m in skin.data.materials]},indent=2))
print('CR05_WARDEN_SOURCE_PASS',len(data.bones),len(skin.data.loop_triangles))
