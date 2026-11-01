"""Original centimeter-scale maintenance kit. Reuses only pure project-owned mesh helpers.
No old generator body or old Blender source is executed/overwritten.
"""
import argparse, ast, json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector

ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True)
out=Path(ap.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir);out.mkdir(parents=True,exist_ok=True)
src=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
palette={'Paint':((.13,.205,.215),.22,.68),'Steel':((.20,.24,.25),.72,.48),'Rust':((.20,.085,.037),.25,.82),'Dark':((.045,.052,.05),.25,.68),'Amber':((.42,.26,.07),.1,.7),'Pale':((.42,.43,.35),.05,.75)}
mats={};parts=[];kit=[]
for key,(color,metal,rough) in palette.items():
    m=bpy.data.materials.new('CR054_'+key);m.use_nodes=True;m.diffuse_color=(*color,1)
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;mats[key]=m
helpers=ast.parse((src.parent/'Phase052/polish_environment.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['reg','mesh','bevel','box','beam','lathe','cyl','tube','profile_x']],type_ignores=[]),'project_mesh_helpers','exec'))

def finish(name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='SM_CR054_'+name
    scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    uv=o.data.uv_layers.active or o.data.uv_layers.new(name='SurfaceUV')
    for face in o.data.polygons:
        axes=((1,2),(0,2),(0,1))[max(range(3),key=lambda i:abs(face.normal[i]))]
        for li in face.loop_indices:
            v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/110,v[axes[1]]/110)
    o['authorship']='Original Cinder Relay Phase054';o['function']='Cosmetic; no collision or persistent state'
    bpy.ops.export_scene.fbx(filepath=str(out/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False,mesh_smooth_type='FACE')
    o.data.calc_loop_triangles();kit.append({'name':o.name,'triangles':len(o.data.loop_triangles),'dimensions_cm':list(o.dimensions),'materials':[m.name for m in o.data.materials]})
    o.hide_set(True);parts.clear()

def loop(name,center,r,axis='Y',mat='Dark'):
    pts=[]
    for i in range(33):
        t=i*math.tau/32
        q=(r*math.cos(t),0,r*math.sin(t)) if axis=='Y' else (r*math.cos(t),r*math.sin(t),0)
        pts.append(tuple(center[k]+q[k] for k in range(3)))
    tube(name,pts,1.4,mat)

# Wall-mounted organized tool station; front faces -Y, lower edge at Z0.
box('Enamel backing',(0,0,75),(235,5,150),'Paint',1.2)
for x in(-116,116):beam('Edge channel',(x,-3,0),(x,-3,150),4,5,'Steel')
for z in(15,53,91,129):beam('Slotted hanger rail',(-110,-5,z),(110,-5,z),3,4,'Steel')
for i in range(7):
    x=-94+i*25;z=112-(i%3)*12
    beam('Tool shank',(x,-10,z-25),(x+3,-10,z+9),2.7,3.5,'Steel')
    cyl('Tool ring',(x+3,-10,z+14),5,3,'Steel','Y',20)
    cyl('Tool recess',(x+3,-11.7,z+14),2.7,.8,'Dark','Y',16)
    box('Grip sleeve',(x,-10,z-16),(5,5,16),'Amber' if i%2 else 'Dark',1.4)
for x in(-76,-8,58):
    box('Parts tray',(x,-22,23),(58,36,4),'Steel',.8)
    for dx in(-27,27):box('Tray rim',(x+dx,-22,28),(3,36,10),'Paint')
    for j in range(4):cyl('Spare washer',(x-18+j*11,-22,27),3.6,2,'Rust','Z',12)
loop('Hanging service lead',(84,-11,84),21)
box('Task header',(0,-5,144),(150,2,10),'Amber')
finish('ToolWall')

# Open shelving, purposeful repair supplies, broad empty middle aisle retained.
for x in(-90,90):
    for y in(-26,26):beam('Shelf upright',(x,y,0),(x,y,210),4,4,'Paint')
for z in(18,78,138,198):
    box('Folded shelf',(0,0,z),(186,62,3),'Steel')
    beam('Rear lip',(-90,29,z+5),(90,29,z+5),3,9,'Paint')
for x,z in[(-55,38),(24,38),(-25,98),(58,158)]:
    box('Repair case',(x,0,z),(49,42,32),'Paint',2)
    box('Case lid',(x,0,z+16),(51,44,4),'Steel')
    tube('Handle',[(x-9,-22,z+6),(x-9,-28,z+9),(x+9,-28,z+9),(x+9,-22,z+6)],1.4,'Dark')
for x in(-62,-18):
    cyl('Coiled cable',(x,0,160),16,23,'Dark','Y')
    for y in(-14,14):cyl('Reel flange',(x,y,160),21,2,'Rust','Y')
beam('Back diagonal',(-90,29,20),(90,29,195),3,3,'Steel')
finish('ServiceShelf')

# Twin overhead services: round duct and open cable ladder, visually below the old ceiling.
cyl('Ventilation duct',(0,-32,0),20,580,'Steel','X',24)
for x in(-275,-140,0,140,275):
    cyl('Duct clamp',(x,-32,0),22,6,'Rust','X',24)
    beam('Ceiling hanger',(x,-32,23),(x,-32,60),2,2,'Dark')
for y in(18,75):beam('Cable tray side',(-295,y,0),(295,y,0),4,8,'Paint')
for x in range(-280,281,35):beam('Cable tray rung',(x,18,-2),(x,75,-2),3,3,'Steel')
for y in(31,43,55,65):tube('Cable bundle',[(-295,y,2),(-160,y,3),(110,y+2,2),(295,y,2)],2,'Dark')
finish('OverheadServices')

# Externalized electrical distribution; no functional gameplay switches.
box('Wall mounting plate',(0,0,75),(185,4,150),'Paint',1)
for x in(-60,0,60):
    box('Service enclosure',(x,-13,100),(50,25,70),'Steel',2)
    box('Recessed face',(x,-27,100),(43,2,61),'Dark')
    cyl('Isolation dial',(x,-31,110),10,6,'Pale','Y')
    beam('Handle',(x,-36,102),(x,-36,117),4,3,'Amber')
    for z in(80,85,90):box('Vent slot',(x,-29,z),(30,1,1.3),'Steel',0)
    tube('Looped conduit',[(x,-12,65),(x,-12,43),(x+12,-12,31),(x+12,-12,5)],2.4,'Dark')
    box('Circuit label',(x,-29,127),(27,1,5),'Pale',0)
for x in(-84,84):beam('Ground bus',(x,-8,10),(x,-8,140),2.5,3,'Rust')
finish('ElectricalPanel')

# Rail-side pneumatic service skid: compound curved forms, distinct from existing skyline.
for y in(-60,60):beam('Skid rail',(-110,y,9),(110,y,9),14,14,'Rust')
lathe('Pressure reservoir',(0,0,72),[(-100,0),(-98,20),(-88,34),(-70,39),(68,39),(88,32),(99,16),(101,0)],'Paint','X',32)
for x in(-60,60):
    cyl('Reservoir band',(x,0,72),40.5,5,'Steel','X')
    for y in(-24,24):beam('Mount foot',(x,y,18),(x,y,40),10,12,'Steel')
cyl('Pump motor',(10,0,135),19,65,'Dark','X')
for x in range(-22,43,7):cyl('Cooling fin',(x,0,135),21,2,'Steel','X')
tube('Delivery pipe',[(48,0,135),(70,0,135),(78,0,120),(78,0,95)],4,'Rust')
cyl('Gauge stem',(-63,0,120),3,22,'Steel')
cyl('Gauge face',(-63,-5,137),11,7,'Pale','Y',24)
beam('Gauge needle',(-63,-9,137),(-68,-9,142),1,1,'Dark')
loop('Service hose',(-65,-47,66),33)
finish('PneumaticSkid')

# Short rail-side signal service cabinet and exposed protected cable route.
box('Pedestal',(0,0,25),(58,44,50),'Rust',2)
box('Service housing',(0,0,90),(76,55,95),'Paint',4)
box('Sloped hood',(0,0,140),(88,68,8),'Steel',2).rotation_euler.y=.1
for z in range(68,121,9):box('Louver',(0,-29,z),(56,4,4),'Dark',.8)
for x in(-30,30):tube('Supply conduit',[(x,5,46),(x,5,12),(x+18,5,5),(x+110,5,5)],3,'Dark')
box('Service plate',(0,-31,128),(45,2,10),'Amber')
finish('TracksideService')

for o in bpy.data.objects:o.hide_set(False)
bpy.ops.wm.save_as_mainfile(filepath=str(src/'CR054_IndustrialUtilities.blend'))
(out/'environment-manifest.json').write_text(json.dumps({'authorship':'Original project-owned utility geometry','unit':'cm','palette':palette,'meshes':kit},indent=2),encoding='utf-8')
print('CR054_KIT',sum(k['triangles'] for k in kit),len(kit))
