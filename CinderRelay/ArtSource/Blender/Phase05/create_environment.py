"""Original editable industrial kit. Blender4.5, centimeters, +X forward/+Z up.
Exports only owned meshes; never opens or overwrites Phase03 source.
"""
import argparse, json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector

args=argparse.ArgumentParser();args.add_argument('--export-dir',required=True)
opt=args.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(opt.export_dir);out.mkdir(parents=True,exist_ok=True)
src=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
bpy.context.preferences.filepaths.save_version=0
palette={'Steel':((.18,.235,.26),.7,.52),'Paint':((.16,.24,.28),.35,.65),'Rust':((.23,.115,.065),.25,.87),
         'Dark':((.025,.033,.037),.25,.7),'Concrete':((.30,.30,.27),0,.93),'Amber':((.65,.34,.10),.25,.55),
         'Glass':((.025,.065,.073),.6,.24),'Light':((.85,.60,.29),.1,.35),'Cyan':((.08,.40,.43),.2,.35),'Wood':((.19,.135,.08),0,.9),'Leaf':((.13,.16,.10),0,.95)}
mats={}
for key,(color,metal,rough) in palette.items():
 m=bpy.data.materials.new('CR05_'+key);m.use_nodes=True;m.diffuse_color=(*color,1)
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;mats[key]=m
parts=[];kit=[]
def register(o,mat):
 o.data.materials.append(mats[mat]);parts.append(o);return o
def bevel(o,width=.7,segments=2):
 if width:
  bpy.context.view_layer.objects.active=o;b=o.modifiers.new('Edge radius','BEVEL');b.width=width;b.segments=segments;bpy.ops.object.modifier_apply(modifier=b.name)
 return o
def box(n,p,s,mat='Steel',r=.7):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=s
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bevel(o,r);return register(o,mat)
def cyl(n,p,radius,depth,mat='Steel',axis='Z',vertices=20):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=p);o=bpy.context.object;o.name=n
 if axis=='X':o.rotation_euler[1]=math.pi/2
 if axis=='Y':o.rotation_euler[0]=math.pi/2
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);bevel(o,.4,1)
 for face in o.data.polygons:face.use_smooth=len(face.vertices)==4
 return register(o,mat)
def beam(n,a,b,width,depth,mat='Steel'):
 a,b=Vector(a),Vector(b);o=box(n,(a+b)/2,(width,depth,(b-a).length),mat)
 o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def mesh(n,verts,faces,mat):
 data=bpy.data.meshes.new(n);data.from_pydata(verts,[],faces);data.update();o=bpy.data.objects.new(n,data);scene.collection.objects.link(o);return register(o,mat)
def tube(n,points,r,mat='Steel'):
 data=bpy.data.curves.new(n,'CURVE');data.dimensions='3D';data.resolution_u=2;data.bevel_depth=r;data.bevel_resolution=1
 spline=data.splines.new('POLY');spline.points.add(len(points)-1)
 for point,co in zip(spline.points,points):point.co=(*co,1)
 o=bpy.data.objects.new(n,data);scene.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');return register(o,mat)
def finish(name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='SM_CR05_'+name
 scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 # Original tileable UVs: consistent 200cm projection per dominant face, no auto-unwrap dependency.
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='Surface200cm')
 for face in o.data.polygons:
  ax=max(range(3),key=lambda i:abs(face.normal[i]));axes=((1,2),(0,2),(0,1))[ax]
  for li in face.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/200,v[axes[1]]/200)
 o['authorship']='Original Cinder Relay Phase05 authored geometry; no external source'
 o['units']='centimeters; +X forward; +Z up; render-only placement'
 bpy.ops.export_scene.fbx(filepath=str(out/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE')
 o.data.calc_loop_triangles();kit.append({'name':o.name,'triangles':len(o.data.loop_triangles),'dimensions_cm':list(o.dimensions),'materials':[m.name for m in o.data.materials]})
 o.hide_set(True);o.hide_render=True;parts.clear();return o

# A complete rail maintenance car: recessed door/window bays, rolled roof, bogies and service hardware.
box('LongitudinalChassis',(0,0,117),(918,260,35),'Dark',2)
for y in(-133,133):box('LoadBeam',(0,y,130),(914,15,38),'Rust',1)
for x in(-365,-295,295,365):
 cyl('Axle',(x,0,69),10,315,'Dark','Y')
 for y in(-151,151):
  cyl('RailWheel',(x,y,70),61,24,'Dark','Y',28);cyl('WheelRim',(x,y,70),62,5,'Steel','Y',28)
  cyl('Hub',(x,y+(-15 if y<0 else 15),70),21,9,'Rust','Y')
for x in(-330,330):
 for y in(-120,120):
  box('BogieSide',(x,y,79),(170,22,28),'Steel',2)
  for dx in(-35,35):
   for z in(89,94,99,104):cyl('SuspensionRing',(x+dx,y,z),15,3,'Dark','Z',12)
box('CabinFloor',(0,0,145),(898,303,12),'Steel',1)
for y in(-153,153):
 box('LowerSkirt',(0,y,180),(895,7,60),'Rust',1)
 box('WaistStrip',(0,y*1.015,218),(898,5,8),'Amber',.8)
 for a,b in[(-450,-315),(-295,-155),(-135,135),(155,295),(315,450)]:
  box('SideStile',((a+b)/2,y,294),(b-a,8,151),'Paint',.6)
 for x in(-305,-145,145,305):box('Rib',(x,y*1.03,291),(9,10,156),'Steel',.6)
 for x in(-375,-225,225,375):
  # Opaque recessed glazing, angled streak seams supplied by material; no expensive translucent windows.
  box('WindowGasket',(x,y*1.03,303),(106,3,87),'Dark',3)
  box('WindowGlass',(x,y*1.043,305),(91,2,72),'Glass',2)
  box('WindowSill',(x,y*1.052,260),(112,9,7),'Steel',.6)
 box('SlidingDoor',(0,y*1.04,281),(184,8,170),'Paint',1)
 for x in(-79,79):box('DoorFrame',(x,y*1.065,281),(7,5,170),'Rust',.4)
 box('DoorRail',(0,y*1.06,369),(236,8,8),'Steel',.6)
 tube('DoorHandle',[(54,y*1.08,270),(54,y*1.11,270),(54,y*1.11,298),(54,y*1.08,298)],2.0,'Steel')
 box('ServicePlaque',(-235,y*1.065,226),(115,1.4,22),'Amber',.5)
 for x in range(-430,450,90):cyl('SkirtRivet',(x,y*1.045,193),2,2,'Steel','Y',8)
for x in(-449,449):
 box('EndWall',(x,0,275),(7,305,240),'Paint',1)
 box('EndServiceDoor',(x*1.013,0,269),(4,106,198),'Rust',1)
 for y in(-98,98):tube('GrabRail',[(x*1.025,y,163),(x*1.04,y,176),(x*1.04,y,300),(x*1.025,y,311)],2.5)
 box('Coupler',(x*1.08,0,103),(55,34,24),'Dark',2)
# Rolled roof profile with longitudinal stiffening. Mesh topology is an authored sheet, not another box.
verts=[]
for x in(-463,463):
 for i in range(13):
  y=-167+i*334/12;verts.append((x,y,380+25*(1-(y/167)**2)))
mesh('RolledRoof',verts,[(i,13+i,14+i,i+1) for i in range(12)],'Steel')
for y in(-145,-85,0,85,145):box('RoofRib',(0,y,381+25*(1-(y/167)**2)),(920,4,4),'Rust',.8)
rail=finish('RailServiceCar')

# Reusable structural I-beam, corrugated sheet and cross brace.
for z in(5,395):box('Flange',(0,0,z),(30,30,10),'Rust',.5)
box('Web',(0,0,200),(8,23,380),'Steel',.5)
for y in(-13,13):box('IFlange',(0,y,200),(28,5,380),'Steel',.5)
for x in(-10,10):
 for y in(-10,10):cyl('AnchorBolt',(x,y,12),2.4,8,'Dark',vertices=8)
finish('SteelColumn')
verts=[]
for z in(0,400):
 for i in range(61):verts.append((-150+i*5,2.2*math.sin(i*math.pi/2),z))
sheet=mesh('Corrugation',verts,[(i,i+1,62+i,61+i) for i in range(60)],'Paint')
for x in(-145,0,145):box('EdgeFixing',(x,-3,200),(5,5,400),'Rust',.5)
finish('CorrugatedPanel')
for a,b in[((-150,0,0),(150,0,280)),((150,0,0),(-150,0,280))]:beam('Diagonal',a,b,6,7,'Rust')
finish('CrossBrace')

# Cabinets have inset doors, vents, hinges, handles and instrument faces.
box('CabinetCase',(0,0,100),(115,62,200),'Paint',2)
box('Plinth',(0,0,8),(120,68,16),'Dark',1)
for x in(-28,28):
 box('Door',(x,-33,107),(53,4,176),'Steel',1)
 for z in(35,57,79):box('Vent',(x,-35.5,z),(39,1,3),'Dark',.4)
 tube('Handle',[(x+17,-37,102),(x+17,-42,102),(x+17,-42,123),(x+17,-37,123)],1.3)
 for z in(35,165):box('Hinge',(x-23,-36,z),(4,4,9),'Rust',.5)
box('AssetLabel',(0,-36,178),(37,1,12),'Amber',.4)
finish('ServiceCabinet')
box('RackBack',(0,0,130),(150,65,260),'Dark',2)
for z in(25,73,121,169,217):
 box('RackUnit',(0,-35,z),(137,6,41),'Steel',1)
 box('Screen',(-35,-39,z+4),(40,2,23),'Glass',1)
 for x in(6,22,38,54):cyl('ControlDial',(x,-40,z),5,4,'Dark','Y',12)
 box('StatusLight',(0,-40,z+14),(65,1,2),'Cyan',.2)
for x in(-69,69):box('RackUpright',(x,-39,130),(5,5,250),'Rust',.5)
finish('ControlRack')

# Pump/motor assembly, pipe runs and caged lamps.
box('EquipmentBase',(0,0,10),(160,105,20),'Dark',1.5)
cyl('Motor',(0,0,60),42,95,'Steel','X',28)
for x in range(-40,45,10):cyl('CoolingFin',(x,0,60),46,3,'Paint','X',24)
cyl('EndHousing',(55,0,60),49,20,'Rust','X',28)
tube('ReturnPipe',[(60,0,92),(60,0,150),(-45,0,150),(-45,0,102)],9,'Steel')
for x in(-60,60):box('Mount',(x,0,25),(18,90,26),'Rust',1)
finish('PumpMotor')
for y in(-14,14):
 cyl('Conduit',(0,y,0),5,300,'Steel','X')
 for x in(-130,0,130):cyl('Collar',(x,y,0),7,7,'Rust','X',12)
for x in(-130,0,130):box('WallBracket',(x,0,-6),(9,50,4),'Dark',.6)
finish('TwinConduit')
cyl('LampBack',(0,0,0),22,8,'Dark','Z');cyl('LampLens',(0,0,-6),18,5,'Light','Z',24)
for a in range(0,360,60):
 x,y=20*math.cos(math.radians(a)),20*math.sin(math.radians(a));tube('Cage',[(x,y,0),(x,y,-12),(0,0,-17)],1,'Steel')
finish('CagedLamp')

# Original maintenance dressing: bounded deliberate clusters, not random arena blocking.
box('ToolTray',(0,0,1),(45,27,2),'Rust',1)
for y in(-12,12):box('TrayLip',(0,y,3),(45,2,5),'Steel',.3)
for x in(-14,0,14):
 box('Handle',(x,0,4),(5,16,4),'Dark',1);cyl('ToolShank',(x,12,4),1.5,12,'Steel','Y',10)
finish('ToolTray')
cyl('CableCoil',(0,0,7),32,12,'Dark','Z',28)
for a in range(0,360,45):
 r=math.radians(a);tube('CoilTexture',[(31*math.cos(r),31*math.sin(r),2),(32*math.cos(r),32*math.sin(r),13)],1.6,'Steel')
finish('CableSpool')
for i,(x,y,z,a) in enumerate([(-40,-8,6,.12),(12,5,9,-.15),(50,-12,4,.3)]):
 o=box('BrokenSleepers',(x,y,z),(82,18,9),'Wood',1);o.rotation_euler[2]=a
for x,y,z in[(-35,28,4),(8,-30,6),(55,24,3)]:box('ScrapPlate',(x,y,z),(32,23,3),'Rust',.4)
finish('MaintenanceDebris')
for i in range(9):
 a=i*2.4;r=(i%3)*8;h=24+(i%4)*8;x,y=r*math.cos(a),r*math.sin(a)
 beam('DryStem',(x,y,0),(x+math.sin(a)*8,y+math.cos(a)*9,h),1,1,'Wood')
 for z in(h*.45,h*.7):
  o=mesh('Leaf',[(x,y,z),(x+math.cos(a)*14,y+math.sin(a)*14,z+5),(x+math.cos(a+.3)*7,y+math.sin(a+.3)*7,z+7)],[(0,1,2),(2,1,0)],'Leaf')
finish('WeedCluster')

scene['authorship']='Original geometry authored for Cinder Relay Phase05; no downloaded assets'
scene['export_convention']='UE centimeters; FBX -Y forward/Z up converts authored +X convention; validate imported bounds'
rail.hide_set(False);rail.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(src/'CR05_IndustrialKit.blend'))
(out/'environment-manifest.json').write_text(json.dumps({'blender':bpy.app.version_string,'meshes':kit,'palette':palette},indent=2),encoding='utf-8')
assert max(m['triangles'] for m in kit)<35000
print('CR05_ENVIRONMENT_AUTHORED',json.dumps(kit))
