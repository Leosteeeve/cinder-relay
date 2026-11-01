"""Original Phase052 near-field kit; native Blender centimeters and editable sources.
Only exports this kit. No old source, collision, level or gameplay mutation.
"""
import argparse, json, math, random, sys
from pathlib import Path
import bpy
from mathutils import Vector

ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True)
out=Path(ap.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir);out.mkdir(parents=True,exist_ok=True)
src=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
palette={'Paint':((.13,.205,.215),.22,.68),'Steel':((.20,.24,.25),.72,.48),
 'Rust':((.20,.085,.037),.25,.82),'Dark':((.045,.052,.05),.25,.68),
 'Amber':((.42,.26,.07),.1,.7),'Glass':((.035,.073,.078),.5,.28),
 'Wood':((.18,.12,.055),0,.85),'Concrete':((.24,.25,.23),0,.9),
 'Leaf':((.10,.125,.065),0,.9),'Pale':((.42,.43,.35),.05,.75)}
mats={};parts=[];kit=[];rng=random.Random(5201)
for k,(c,m,r) in palette.items():
    a=bpy.data.materials.new('CR052_'+k);a.use_nodes=True;a.diffuse_color=(*c,1)
    bs=a.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Metallic'].default_value=m;bs.inputs['Roughness'].default_value=r;mats[k]=a
def reg(o,mat):
    o.data.materials.append(mats[mat]);parts.append(o);return o
def mesh(name,v,f,mat):
    d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);return reg(o,mat)
def bevel(o,w=.6,n=2):
    bpy.context.view_layer.objects.active=o
    b=o.modifiers.new('Manufactured edge radius','BEVEL');b.width=w;b.segments=n;bpy.ops.object.modifier_apply(modifier=b.name)
    return o
def box(name,p,d,mat='Steel',w=.6):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);reg(o,mat)
    if w:bevel(o,w)
    return o
def beam(name,a,b,w,d,mat='Steel'):
    a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(w,d,(b-a).length),mat);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def lathe(name,center,profile,mat='Steel',axis='Z',n=32):
    # Profile is (axial distance, radius); ordered rings preserve actual rim depth.
    v=[];f=[]
    for z,r in profile:
        for i in range(n):
            t=2*math.pi*i/n;u=r*math.cos(t);w=r*math.sin(t)
            q=(z,u,w) if axis=='X' else (u,z,w) if axis=='Y' else (u,w,z)
            v.append(tuple(center[j]+q[j] for j in range(3)))
    for j in range(len(profile)-1):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;f.append((a,b,b+n,a+n))
    if axis=='Y':f=[tuple(reversed(face)) for face in f]
    o=mesh(name,v,f,mat)
    for p in o.data.polygons:p.use_smooth=True
    return o
def cyl(name,p,r,d,mat='Steel',axis='Z',n=20):
    return lathe(name,p,[(-d/2,0),(-d/2,r),(d/2,r),(d/2,0)],mat,axis,n)
def tube(name,pts,r,mat='Steel',sides=8):
    v=[];f=[]
    for i,p in enumerate(pts):
        d=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)])
        q=d.to_track_quat('Z','Y')
        for k in range(sides):v.append(Vector(p)+q@Vector((r*math.cos(k*math.tau/sides),r*math.sin(k*math.tau/sides),0)))
    for i in range(len(pts)-1):
        for k in range(sides):a=i*sides+k;b=i*sides+(k+1)%sides;f.append((a,b,b+sides,a+sides))
    o=mesh(name,v,f,mat)
    for p in o.data.polygons:p.use_smooth=True
    return o
def profile_x(name,x0,x1,section,mat):
    v=[(x,y,z) for x in(x0,x1) for y,z in section];n=len(section)
    f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,v,f,mat)
def finish(name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='SM_CR052_'+name
    scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    uv=o.data.uv_layers.active or o.data.uv_layers.new(name='SurfaceUV')
    for face in o.data.polygons:
        axes=((1,2),(0,2),(0,1))[max(range(3),key=lambda i:abs(face.normal[i]))]
        for li in face.loop_indices:
            v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/150,v[axes[1]]/150)
    o['authorship']='Original Cinder Relay Phase052; no third-party geometry';o['purpose']='Cosmetic only; keep existing gameplay collision'
    bpy.ops.export_scene.fbx(filepath=str(out/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False,mesh_smooth_type='FACE')
    o.data.calc_loop_triangles();kit.append({'name':o.name,'triangles':len(o.data.loop_triangles),'dimensions_cm':list(o.dimensions),'materials':[m.name for m in o.data.materials]})
    o.hide_set(True);parts.clear();return o

# Maintenance coach: shaped shell, recessed bays, layered underframe and profiled wheel faces.
section=[(-151,151),(151,151),(157,305),(148,354),(130,378),(88,398),(0,407),(-88,398),(-130,378),(-148,354),(-157,305)]
profile_x('Formed maintenance coach shell',-449,449,section,'Paint')
for y in(-124,124):beam('Longitudinal load channel',(-455,y,126),(455,y,126),20,24,'Rust')
for x in(-380,-200,0,200,380):beam('Underfloor crossmember',(x,-140,133),(x,140,133),13,17,'Steel')
for x in(-330,330):
    cyl('Underframe reservoir',(x,0,101),19,115,'Dark','Y')
    for y in(-152,152):
        sign=1 if y>0 else -1
        for dx in(-52,52):
            wheel=(x+dx,y,63)
            lathe('Forged wheel rim and dished web',wheel,[(-14,16),(-14,55),(-11,61),(-7,61),(-7,55),(9,55),(12,51),(12,43),(7,40),(5,25),(14,22),(14,0)],'Steel','Y',40)
            cyl('Wheel face inset',(x+dx,y+sign*15,63),38,1.6,'Dark','Y',32)
            lathe('Exposed axle cap',(x+dx,y+sign*17,63),[(-3,0),(-3,17),(0,20),(4,16),(4,0)],'Rust','Y',24)
            for k in range(6):
                a=k*math.tau/6;cyl('Hub fastener',(x+dx+12*math.cos(a),y+sign*22,63+12*math.sin(a)),2.1,3,'Steel','Y',6)
            cyl('Axle',(x+dx,0,63),9,290,'Dark','Y')
        beam('Bogie box girder',(x-85,y-sign*24,94),(x+85,y-sign*24,94),18,22,'Paint')
        for dx in(-24,24):
            pts=[(x+dx+9*math.cos(t*math.tau/12),y-sign*24+9*math.sin(t*math.tau/12),99+t*.65) for t in range(61)]
            tube('Visible suspension coil',pts,1.8,'Steel',6)
        beam('Diagonal bogie brace',(x-76,y-sign*24,92),(x,y-sign*24,123),8,9,'Steel')
        beam('Diagonal bogie brace',(x+76,y-sign*24,92),(x,y-sign*24,123),8,9,'Steel')
for side in(-1,1):
    y=side*158
    for x in(-368,-218,218,368):
        box('Pressed recessed window gasket',(x,y,302),(113,3,84),'Dark',5)
        box('Dusty inset glass',(x,y+side*2,302),(98,2,69),'Glass',4)
        for z in(264,342):box('Window reveal trim',(x,y+side*4,z),(115,6,5),'Steel')
        box('Pressed lower service panel',(x,y+side,209),(124,4,76),'Rust',4)
        for z in(185,201,217):box('Panel strengthening bead',(x,y+side*4,z),(106,3,3),'Paint')
    for x in(-440,-292,-142,142,292,440):
        tube('Formed body rib',[(x,side*153,151),(x,side*161,290),(x,side*153,350),(x,side*132,379)],2.4,'Steel')
    box('Door recessed gasket',(0,y+side,252),(192,5,200),'Dark',5)
    box('Sliding service door',(0,y+side*5,252),(178,7,189),'Paint',5)
    for z in(196,222,248,274,300):box('Door stiffening crease',(0,y+side*10,z),(148,2.6,3),'Steel')
    box('Door running channel',(0,y+side*9,355),(248,11,9),'Rust')
    for x in(-70,70):cyl('Door rollers',(x,y+side*15,352),8,5,'Steel','Y')
    tube('Recessed pull handle',[(58,y+side*12,238),(58,y+side*21,243),(58,y+side*21,272),(58,y+side*12,278)],2,'Steel')
    for z in(90,120):box('Folded access step',(0,y+side*13,z),(170,34,4),'Steel')
    box('Faded service band',(0,y+side*3,170),(895,2,11),'Amber')
for x in(-455,455):
    s=1 if x>0 else -1
    box('End framed inspection door',(x,0,265),(5,112,194),'Dark',6)
    box('End panel',(x+s*4,0,266),(5,96,175),'Rust',5)
    for y in(-100,100):tube('End safety handrail',[(x+s*8,y,166),(x+s*17,y,176),(x+s*17,y,310),(x+s*8,y,318)],2.5)
    for y in(-96,96):cyl('Shock buffer',(x+s*20,y,120),15,35,'Dark','X');cyl('Buffer face',(x+s*40,y,120),22,5,'Steel','X')
    beam('Coupler shank',(x,0,105),(x+s*57,0,105),23,18,'Dark')
for x in(-300,50,300):
    for y in(-115,-55,0,55,115):box('Roof vent rib',(x,y,410-abs(y)*.18),(80,8,5),'Dark')
    box('Riveted roof hatch',(x,0,412),(108,72,8),'Steel',6)
finish('RailServiceCar')

# Portal lives outside the unchanged +/-180cm doorway and gate plane.
for y in(-213,213):
    box('Portal base shoe',(0,y,15),(65,55,30),'Concrete',4)
    box('Door guide outer case',(0,y,188),(45,44,346),'Steel',2)
    box('Door channel recess',(-24,y,190),(3,20,310),'Dark')
    for z in range(55,335,47):box('Segmented hazard panel',(-27,y,z),(3,27,18),'Amber')
    for z in(30,345):cyl('Frame bolt',(-28,y,z),4,4,'Steel','X',6)
box('Rolling shutter casing',(5,0,412),(66,454,68),'Paint',8)
for y in range(-190,200,38):box('Casing ventilation slot',(-30,y,407),(3,18,4),'Dark')
for y in(-226,226):cyl('Shutter motor end',(-1,y,413),29,35,'Steel','Y',28)
for y in(-290,290):
    beam('Canopy bracket',(10,y,470),(-112,y,414),10,13,'Steel')
    beam('Bracket tie',(10,y,410),(-112,y,414),8,8,'Rust')
profile_x('Folded canopy',-120,22,[(-350,473),(350,473),(350,479),(-350,479)],'Steel')
for y in(-340,340):tube('Drain downpipe',[(5,y,470),(5,y,335),(-3,y,310),(-3,y,22)],5,'Rust')
box('Utility fuse case',(-3,-325,196),(35,72,105),'Paint',4)
for z in(165,184,203,222):box('Fuse case louver',(-22,-325,z),(3,49,5),'Dark')
tube('Protected electrical conduit',[(10,-325,248),(10,-325,353),(10,-255,353),(10,-255,420)],3,'Steel')
box('Service identification panel',(-36,0,453),(3,260,27),'Dark',3)
finish('WorkshopPortal')

# End-support detail plus pipe runs. Existing truss silhouette is retained.
for side in(-1,1):
    y=side*1330
    box('Gantry bearing plate',(0,y,0),(70,90,12),'Steel',2)
    beam('Braced shoulder',(-15,y-side*15,0),(-15,y-side*150,-75),12,14,'Rust')
    for x in(-25,25):
        for dy in(-28,28):cyl('Anchor fixing',(x,y+dy,10),4.5,10,'Steel','Z',6)
for x in(-27,27):
    tube('Cross-yard pipe',[(x,-1370,25),(x,-1260,45),(x,1260,45),(x,1370,25)],8,'Paint',12)
    for y in(-1100,-700,0,700,1100):
        cyl('Flange collar',(x,y,45),13,6,'Rust','Y',16)
        beam('Pipe hanger',(x,y,45),(x,y,80),4,4,'Steel')
finish('GantryServices')

# Curated modular service props, no random occupancy of the main route.
for side in(-1,1):
    cyl('Spool wooden cheek',(0,side*31,55),53,7,'Wood','Y',32)
    cyl('Spool hub',(0,side*36,55),12,5,'Steel','Y')
    for a in range(0,360,45):cyl('Spool bolt',(37*math.cos(math.radians(a)),side*36,55+37*math.sin(math.radians(a))),2,3,'Dark','Y',6)
cyl('Cable drum core',(0,0,55),25,59,'Dark','Y')
for y in range(-25,26,4):lathe('Wound cable',(0,y,55),[(-1.6,40),(-1.4,44),(1.4,44),(1.6,40)],'Dark','Y',32)
tube('Loose cable tail',[(30,12,20),(45,25,6),(72,39,4),(90,15,4),(102,4,4)],2,'Dark')
finish('CableSpool')
lathe('Rolled drum body',(0,0,0),[(2,0),(2,27),(5,29),(22,29),(23,31),(26,31),(27,29),(65,29),(66,31),(69,31),(70,29),(87,29),(90,27),(90,0)],'Paint','Z',32)
for z in(4,24,67,88):lathe('Drum rim',(0,0,z),[(-1.5,28),(0,31),(1.5,28)],'Steel','Z',32)
cyl('Drum bung',(12,8,91),4,2,'Rust');finish('Barrel')
for z in(7,25,43,61):
    for y in(-36,36):box('Crate slat',(0,y,z),(99,5,15),'Wood')
    for x in(-47,47):box('Crate end slat',(x,0,z),(5,72,15),'Wood')
for y in(-24,0,24):box('Crate lid',(0,y,72),(100,22,7),'Wood')
for x in(-37,37):
    for y in(-40,40):box('Crate brace',(x,y,38),(10,5,75),'Steel')
finish('ServiceCrate')
box('Trolley tray',(0,0,35),(155,75,8),'Steel',4)
for y in(-35,35):box('Trolley rim',(0,y,42),(155,4,12),'Rust')
for x in(-62,62):
    for y in(-28,28):cyl('Trolley caster',(x,y,15),12,8,'Dark','Y',16)
tube('Push handle',[(-74,-32,36),(-89,-32,100),(-89,32,100),(-74,32,36)],3,'Steel')
for y in(-20,0,20):tube('Stored pipe section',[(-50,y,48),(35,y,48),(53,y,62)],6,'Rust',12)
finish('MaintenanceTrolley')
box('Raised utility enclosure',(0,0,110),(62,92,185),'Paint',5)
box('Inspection door',(-34,0,110),(5,82,172),'Steel',3)
for z in range(60,155,12):box('Louver',(-38,0,z),(4,63,3),'Dark')
tube('Conduit riser',[(17,45,0),(17,45,185),(17,55,204)],4,'Rust')
cyl('Access handle',(-40,30,116),3,15,'Amber','Z');finish('UtilityBox')
for i in range(7):
    x=rng.uniform(-90,90);y=rng.uniform(-55,55)
    b=box('Stacked cut channel',(x,y,8+i*3),(rng.uniform(55,130),12,6),'Rust');b.rotation_euler.z=rng.uniform(-.55,.55)
for i in range(3):tube('Bent scrap',[(i*25-30,-35,8),(i*25,0,22),(i*25+20,40,13)],5,'Steel')
finish('ScrapStack')
for i in range(8):
    a=i*math.tau/8;x=10*math.cos(a);y=10*math.sin(a)
    tube('Dry weed stem',[(x,y,0),(x*1.6,y*1.6,15),(x*2.8,y*2.8,27+i%3*6)],.4,'Leaf',4)
    for z in(9,18):mesh('Dry leaf',[(x*1.3,y*1.3,z),(x*3,y*3,z+3),(x*1.4+2,y*1.4,z+5)],[(0,1,2)],'Leaf')
finish('WeedTuft')
# Midground nonplayable roof / tank group, readable through skyline gaps.
for x,y,w,h in[(0,0,900,630),(720,300,650,860)]:
    box('Service annex',(x,y,h/2),(w,720,h),'Concrete',3)
    profile_x('Pitched factory roof',x-w/2-25,x+w/2+25,[(-385+y,h),(385+y,h),(385+y,h+20),(y,h+170),(-385+y,h+20)],'Steel')
    for z in range(170,h-50,150):
        for dx in range(-int(w/2)+75,int(w/2)-20,130):box('Inset factory window',(x+dx,y-362,z),(82,3,95),'Glass')
    for dx in(-w/2+30,w/2-30):box('Facade pilaster',(x+dx,y-366,h/2),(23,16,h),'Steel')
for x,y in[(-440,470),(-70,550)]:
    lathe('Riveted process tank',(x,y,0),[(0,135),(540,135),(590,105),(615,25),(615,0)],'Paint','Z',24)
    for z in(70,260,450):lathe('Tank seam',(x,y,z),[(-3,134),(0,139),(3,134)],'Rust','Z',24)
    tube('Tank pipe',[(x+125,y,70),(x+180,y,70),(x+180,y,550),(x+70,y,590)],10,'Steel',10)
for x,y,z in[(250,0,800),(780,270,1020)]:
    cyl('Short ventilation stack',(x,y,z+110),39,220,'Rust','Z',16)
    cyl('Rain cowl',(x,y,z+230),58,16,'Steel','Z',16)
finish('MidgroundWorks')

for o in bpy.context.scene.objects:o.hide_set(False)
bpy.ops.wm.save_as_mainfile(filepath=str(src/'CR052_YardDetail.blend'))
(out/'environment-manifest.json').write_text(json.dumps({'source':str(src/'CR052_YardDetail.blend'),'palette':palette,'meshes':kit},indent=2))
print('CR052_ENVIRONMENT_SOURCE_PASS '+json.dumps({'meshes':len(kit),'triangles':sum(x['triangles'] for x in kit)}))
