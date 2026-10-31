"""Original Cinder Relay prototype. Blender 4.5 LTS; numeric units are centimeters.
Run: blender --background --factory-startup --python this.py -- --export-dir PATH
Creates editable source, static exterior FBXs and one baked skeletal performance.
No real firearm internals: the action is fictional optical calibration.
"""
import bpy, math, json, sys, argparse
from pathlib import Path
from mathutils import Vector, Matrix
args=argparse.ArgumentParser(); args.add_argument('--export-dir',required=True)
opt=args.parse_args(sys.argv[sys.argv.index('--')+1:]); out=Path(opt.export_dir);out.mkdir(parents=True,exist_ok=True)
source=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
scene.render.fps=30;scene.frame_start=0;scene.frame_end=660
def material(name,color,metal=0,rough=.5):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m
mats=[material('CR03_Graphite',(.065,.085,.095),.7,.32),material('CR03_Amber',(.68,.29,.055),.5,.4),material('CR03_Glove',(.15,.17,.16),0,.75),material('CR03_Cuff',(.28,.31,.28),0,.83),material('CR03_Lens',(.025,.65,.55),.35,.2),material('CR03_Bench',(.14,.2,.22),.55,.65)]
def box(name,loc,size,mat,bevel=.6):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Machined edge radius','BEVEL');mod.width=bevel;mod.segments=3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    o.data.materials.append(mats[mat]);return o
def join(objects,name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
    scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
gun=[]
for name,pos,size,mat in [('Receiver',(0,0,0),(30,6.6,10),0),('BarrelGuard',(28,0,2),(28,4.5,4.5),0),('Grip',(-8,0,-8),(7,5.4,12),2),('Stock',(-23,0,-1),(19,5.7,8),0),('Butt',(-33,0,-1),(3,6.8,10),2),('Feed',(7,0,-8),(7,5,10),0),('Spine',(1,0,6),(24,4,2),1),('Crown',(43,0,2),(4,5.5,5.5),0)]:gun.append(box('Rook_'+name,pos,size,mat))
for x in (16,20,24,28,32):
    for y in (-2.4,2.4):gun.append(box('ShroudVent',(x,y,2),(1.4,.3,2.6),2,.15))
for x in (-3,3,9):gun.append(box('ReceiverFastener',(x,-3.45,0),(1,.35,1),1,.15))
gun.append(box('Rook_ID_Plate',(-10,-3.5,2),(7,.25,2.5),1,.2))
rook=join(gun,'SM_CR03_Rook5')
optic=[]
for n,p,s,m in [('Foot',(-3,0,8),(9,6,2),1),('Left',(-3,-3,12),(10,.8,6),0),('Right',(-3,3,12),(10,.8,6),0),('Top',(-3,0,15),(10,6.8,.8),0),('Bottom',(-3,0,9),(10,6.8,.8),0),('IndicatorFront',(2.1,0,14.5),(.25,4.7,.3),4),('IndicatorRear',(-8.1,0,14.5),(.25,4.7,.3),4),('Selector',(-3,-3.8,12),(3,1,2.5),1)]:optic.append(box('Survey_'+n,p,s,m,.25))
survey=join(optic,'SM_CR03_SurveyOptic')
benchparts=[box('Top',(0,0,94),(90,150,8),5,1),box('WorkMat',(-2,0,98.3),(62,112,1.2),2,.8)]
for x in(-34,34):
    for y in(-62,62):benchparts.append(box('Leg',(x,y,45),(7,7,90),0,.7))
benchparts += [box('RearRail',(36,0,108),(5,144,17),5),box('AmberStrip',(-43,0,93),(1,140,2),1,.3),box('CalibrationPad',(10,42,100),(19,24,2),0,.6)]
bench=join(benchparts,'SM_CR03_Workbench')
def export_static(o):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.export_scene.fbx(filepath=str(out/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
for o in (rook,survey,bench):export_static(o)
# Keep static originals in a separate editable collection, not part of the rig export.
static=bpy.data.collections.new('Static appearance sources');scene.collection.children.link(static)
for o in (rook,survey,bench):
    for c in list(o.users_collection):c.objects.unlink(o)
    static.objects.link(o)
    o.hide_set(True);o.hide_render=True
armdata=bpy.data.armatures.new('CR03_RestorationSkeleton');rig=bpy.data.objects.new('CR03_RestorationRig',armdata);scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent='root'):
    b=armdata.edit_bones.new(name);b.head=head;b.tail=tail
    if parent:b.parent=armdata.edit_bones[parent]
    return b
bone('root',(0,0,0),(0,0,10),None);bone('weapon',(0,0,0),(10,0,0));bone('optic',(0,0,0),(10,0,0))
rest={}
for side,sgn in [('L',-1),('R',1)]:
    shoulder=Vector((-78,sgn*30,128));elbow=Vector((-48,sgn*38,110));wrist=Vector((-20,sgn*25,112))
    bone('upperarm_'+side,shoulder,elbow);bone('forearm_'+side,elbow,wrist,'upperarm_'+side);bone('hand_'+side,wrist,wrist+Vector((10,0,0)),'forearm_'+side)
    rest[side]=(shoulder,elbow,wrist)
    for d in range(5):
        start=wrist+Vector((6 if d==0 else 9,(-4.5 if d==0 else (d-2.5)*2.1),0))
        direction=Vector((.65,-.75,0)) if d==0 else Vector((1,0,0));parent='hand_'+side
        for j,length in enumerate((3.1,2.5,1.8)):
            name=f'finger{d}_{j}_{side}';end=start+direction*length;bone(name,start,end,parent);start=end;parent=name
bpy.ops.object.mode_set(mode='OBJECT')
skin=[]
def weight(o,name,secondary=None):
    g=o.vertex_groups.new(name=name);g.add(list(range(len(o.data.vertices))),1,'REPLACE')
    if secondary:
        h=o.vertex_groups.new(name=secondary)
        # A real weighted transition at the cuff/palm; joint motion deforms these vertices.
        for v in o.data.vertices:
            if v.co.x<0:g.add([v.index],.7,'REPLACE');h.add([v.index],.3,'REPLACE')
    skin.append(o)
def segment(name,a,b,radius,mat):
    length=(b-a).length;o=box(name,(a+b)*.5,(radius,length,radius),mat,min(.8,radius*.2))
    o.rotation_mode='QUATERNION';o.rotation_quaternion=(b-a).to_track_quat('Y','Z');return o
for side in ('L','R'):
    shoulder,elbow,wrist=rest[side]
    weight(segment('Sleeve_'+side,shoulder,elbow,10,3),'upperarm_'+side)
    weight(segment('Forearm_'+side,elbow,wrist,8.5,3),'forearm_'+side)
    palm=box('GlovePalm_'+side,wrist+Vector((4,0,0)),(11,8.7,3.5),2,1.3);weight(palm,'hand_'+side,'forearm_'+side)
    weight(box('KnuckleGuard_'+side,wrist+Vector((7,0,2.1)),(4,8,1.3),0,.65),'hand_'+side)
    weight(box('WristCuff_'+side,wrist+Vector((-1,0,0)),(3.5,10,5),1,.7),'hand_'+side,'forearm_'+side)
    for d in range(5):
        for j in range(3):
            n=f'finger{d}_{j}_{side}';b=armdata.bones[n];weight(segment('Glove_'+n,b.head_local,b.tail_local,1.8 if d else 2.2,2),n)
for original,name in ((rook,'weapon'),(survey,'optic')):
    o=original.copy();o.data=original.data.copy();scene.collection.objects.link(o);o.hide_set(False);o.hide_render=False;weight(o,name)
sk=join(skin,'SK_CR03_Restoration');mod=sk.modifiers.new('Editable skeletal skin','ARMATURE');mod.object=rig;sk.parent=rig
sys.path.insert(0,str(source))
from animate_restoration import author
author(rig)
for marker,t in [('Place ROOK-5',3),('Inspect Survey Optic',6),('Align optical module',10),('Calibration verified',15),('Retrieve upgrade',19),('Return to gameplay',22)]:scene.timeline_markers.new(marker,frame=int(t*30))
scene.frame_set(330)
rig['convention']='Centimeters; +X gameplay forward; +Z up. Bench weapon rotated +90 Z. Verify FBX import.'
rig['quality']='Original segmented glove prototype, not anatomical final art. Skin weights and editable baked skeletal action.'
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);sk.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(out/'SK_CR03_Restoration.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,bake_anim_step=1)
# Inspection camera / lighting are editable source aids, never part of the FBX export.
bench.hide_render=False;bench.hide_set(False)
bpy.ops.object.camera_add(location=(-62,0,166));cam=bpy.context.object;cam.name='AssemblyReviewCamera';cam.rotation_euler=(Vector((0,0,100))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=24;cam.data.clip_start=.1;cam.data.clip_end=10000;scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-20,-20,220));lamp=bpy.context.object;lamp.data.energy=130;lamp.data.shape='DISK';lamp.data.size=150
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
scene.world.color=(.15,.15,.15)
bpy.ops.wm.save_as_mainfile(filepath=str(source/'CR03_RookRestoration.blend'))
receipt={'blender':bpy.app.version_string,'bones':len(armdata.bones),'vertices':len(sk.data.vertices),'duration':22,'fps':30,'frames':[0,660],'action':rig.animation_data.action.name,'weighted_groups':len(sk.vertex_groups),'exports':[p.name for p in out.glob('*.fbx')]}
(out/'blender-receipt.json').write_text(json.dumps(receipt,indent=2));print('CR03_BLENDER_PASS',json.dumps(receipt))
