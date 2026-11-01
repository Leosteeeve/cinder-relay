"""Original nonplayable industrial depth kit: shaped roofs, curved tanks, layered skyline.
No existing map or asset is read/written. Centimeters; no source game designs.
"""
import bpy,math,json,argparse,sys,random
from pathlib import Path
from mathutils import Vector
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True);out=Path(ap.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir);out.mkdir(parents=True,exist_ok=True)
src=Path(__file__).resolve().parent;bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
palette={'Concrete':(.31,.32,.30),'Steel':(.16,.21,.23),'Rust':(.24,.115,.055),'Glass':(.055,.09,.11),'Dark':(.07,.09,.10)}
materials=[]
for n,c in palette.items():
 m=bpy.data.materials.new('CR051_Depth'+n);m.diffuse_color=(*c,1);materials.append(m)
V=[];F=[];M=[];manifest=[]
def face(vertices,mat=0):
 s=len(V);V.extend(vertices);F.append(tuple(range(s,s+len(vertices))));M.append(mat)
def prism(profile,z0,z1,mat=0):
 lower=[(x,y,z0) for x,y in profile];upper=[(x,y,z1) for x,y in profile];face(list(reversed(lower)),mat);face(upper,mat)
 for i in range(len(profile)):j=(i+1)%len(profile);face([lower[i],lower[j],upper[j],upper[i]],mat)
def rect(x,y,w,d,z0,z1,mat=0):prism([(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)],z0,z1,mat)
def bar(a,b,r=5,mat=1,n=8):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
 if u.length<.01:u=axis.cross(Vector((0,1,0)))
 u.normalize();v=axis.cross(u);rings=[[tuple(p+r*(u*math.cos(j*math.tau/n)+v*math.sin(j*math.tau/n))) for j in range(n)] for p in (a,b)]
 face(list(reversed(rings[0])),mat);face(rings[1],mat)
 for j in range(n):face([rings[0][j],rings[0][(j+1)%n],rings[1][(j+1)%n],rings[1][j]],mat)
def radial(cx,cy,rings,mat=1,n=32):
 for (z0,r0),(z1,r1) in zip(rings,rings[1:]):
  for j in range(n):
   a,b=j*math.tau/n,(j+1)*math.tau/n;face([(cx+r0*math.cos(a),cy+r0*math.sin(a),z0),(cx+r0*math.cos(b),cy+r0*math.sin(b),z0),(cx+r1*math.cos(b),cy+r1*math.sin(b),z1),(cx+r1*math.cos(a),cy+r1*math.sin(a),z1)],mat)
def finish(name):
 global V,F,M
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(V,[],F);mesh.update();o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o)
 for m in materials:mesh.materials.append(m)
 uv=mesh.uv_layers.new(name='IndustrialUV')
 for f,mi in zip(mesh.polygons,M):
  f.material_index=mi;axes=((1,2),(0,2),(0,1))[max(range(3),key=lambda i:abs(f.normal[i]))]
  for li in f.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/250,v[axes[1]]/250)
 mesh.calc_loop_triangles();manifest.append({'name':name,'triangles':len(mesh.loop_triangles),'dimensions_cm':list(o.dimensions)})
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False,mesh_smooth_type='FACE')
 V=[];F=[];M=[];return o

# A true vaulted corrugated cap over the preserved warehouse roof, with end trusses.
for i in range(36):
 y0=-350+700*i/36;y1=-350+700*(i+1)/36;z0=220*math.sqrt(max(0,1-(y0/350)**2));z1=220*math.sqrt(max(0,1-(y1/350)**2))
 face([(-490,y0,z0),(490,y0,z0),(490,y1,z1),(-490,y1,z1)],2)
 face([(-490,y1,z1),(490,y1,z1),(490,y0,z0),(-490,y0,z0)],2)
 for x in(-492,492):bar((x,y0,z0),(x,y1,z1),5,1)
for y in(-350,-210,-70,70,210,350):bar((-490,y,220*math.sqrt(max(0,1-(y/350)**2))),(490,y,220*math.sqrt(max(0,1-(y/350)**2))),3,1)
for x in(-492,492):
 bar((x,-350,0),(x,350,0),7)
 for y in(-280,-140,0,140,280):bar((x,y,0),(x,y+70,220*math.sqrt(max(0,1-((y+70)/350)**2))),3)
finish('SM_CR051_VaultRoof')
# Sawtooth workshop frontage: angled rooflets and recessed clerestory glazing.
for y in(-525,-175,175,525):
 face([(-100,y-175,0),(100,y-175,0),(100,y+175,140),(-100,y+175,140)],1)
 face([(-100,y+175,140),(100,y+175,140),(100,y-175,0),(-100,y-175,0)],1)
 face([(-97,y+173,10),(97,y+173,10),(97,y+173,132),(-97,y+173,132)],3)
 for x in(-104,104):bar((x,y-175,0),(x,y+175,140),5);bar((x,y+175,0),(x,y+175,140),5)
finish('SM_CR051_SawtoothClerestory')
# Broken wall profile: variable parapet, leaning buttress, exposed reinforcing rods.
top=[(-300,490),(-230,490),(-215,465),(-150,470),(-120,395),(-80,420),(-35,385),(40,465),(125,465),(160,520),(300,520)]
profile=[(-300,0),(300,0)]+list(reversed(top))
for y in(-20,20):face([(x,y,z) for x,z in (profile if y==20 else list(reversed(profile)))],0)
for (x0,z0),(x1,z1) in zip(profile,profile[1:]+profile[:1]):face([(x0,-20,z0),(x1,-20,z1),(x1,20,z1),(x0,20,z0)],0)
for x in(-270,240):
 face([(x-20,-75,0),(x+20,-75,0),(x+14,-20,495),(x-14,-20,495)],0);bar((x,-25,40),(x,-25,510),6,2)
for x,z in top[3:8]:bar((x,0,z-10),(x+8,0,z+65),1.7,2,6)
finish('SM_CR051_BrokenPerimeter')
# Midground silo pair with curved shoulders, flanged seams, ladders and pipework.
for cx,h in [(-180,1800),(180,1550)]:
 radial(cx,0,[(0,130),(80,140),(h-160,140),(h-50,95),(h,0)],1,40)
 for z in range(180,h-150,260):radial(cx,0,[(z,143),(z+9,143)],2,40)
 for x in(cx-27,cx+27):bar((x,-148,30),(x,-148,h-70),3)
 for z in range(60,h-70,38):bar((cx-27,-149,z),(cx+27,-149,z),2)
 for z in range(200,h-100,250):
  for i in range(8):a,b=math.pi+i*math.pi/8,math.pi+(i+1)*math.pi/8;bar((cx+55*math.cos(a),-147+55*math.sin(a),z),(cx+55*math.cos(b),-147+55*math.sin(b),z),2)
bar((-180,0,150),(180,0,150),24,2,24);bar((180,0,150),(180,220,150),24,2,24)
finish('SM_CR051_SiloPair')
# Slender elevated water tank, braced rather than a rectangular tower.
radial(0,0,[(1150,165),(1170,190),(1510,190),(1570,140),(1650,0)],1,40)
for x in(-110,110):
 for y in(-110,110):bar((x*1.4,y*1.4,0),(x,y,1180),12);bar((x*1.4,y*1.4,150),(-x,y,1050),5)
for z in(1200,1460):radial(0,0,[(z,193),(z+8,193)],2,40)
bar((0,0,1570),(0,0,1780),7);finish('SM_CR051_WaterTower')
# Tall tapered chimney, offset lip and a few bands. No interior.
radial(0,0,[(0,135),(150,145),(260,125),(2100,72),(2450,64),(2460,78),(2500,78),(2500,52),(2430,52)],2,40)
for z,r in [(400,120),(1100,99),(1800,80)]:radial(0,0,[(z,r+3),(z+12,r+3)],1,40)
finish('SM_CR051_Chimney')
# Midground industrial hall with an angled sawtooth roof and layered window bands.
rect(0,0,2400,1100,0,850,0)
for x in range(-1200,1200,400):
 face([(x,-550,850),(x,550,850),(x+400,550,1150),(x+400,-550,1150)],2)
 face([(x+399,-540,860),(x+399,540,860),(x+399,540,1140),(x+399,-540,1140)],3)
 for y in(-558,558):
  rect(x+200,y,335,8,260,690,3)
  for xx in(x+30,x+200,x+370):bar((xx,y,240),(xx,y,710),7)
for x in(-1180,-800,-400,0,400,800,1180):bar((x,-568,0),(x,-568,855),12)
finish('SM_CR051_IndustrialHall')
# Combined small persistent skyline: six distant exterior shells, chamfered footprints,
# stepped crowns, recessed window ribbons and broken top parapets; no rooms or collision.
rng=random.Random(2118051)
for idx,(cx,cy,w,d,h) in enumerate([(22000,-9000,2500,2000,8000),(26000,-5000,1800,2400,10500),(31500,1500,2800,2400,12500),(24000,7000,2100,1800,6900),(39000,-15000,3000,2800,13500),(42000,13500,2800,2600,11900),(-3000,-25000,2800,2000,8200),(6000,24000,2000,2200,9500)]):
 c=w*.13
 footprint=[(cx-w/2+c,cy-d/2),(cx+w/2-c,cy-d/2),(cx+w/2,cy-d/2+c),(cx+w/2,cy+d/2-c),(cx+w/2-c,cy+d/2),(cx-w/2+c,cy+d/2),(cx-w/2,cy+d/2-c),(cx-w/2,cy-d/2+c)]
 prism(footprint,0,h,0)
 for z in range(250,h-250,340):
  # Recessed dark ribbon and protruding floor band produce readable distant depth.
  for y in(cy-d/2-5,cy+d/2+5):rect(cx,y,w-2*c,10,z,z+220,3)
  for x in(cx-w/2-5,cx+w/2+5):rect(x,cy,10,d-2*c,z,z+220,3)
  band=[(cx+(x-cx)*1.018,cy+(y-cy)*1.018) for x,y in footprint];prism(band,z+225,z+248,1)
 for x in(cx-w*.35,cx-w*.12,cx+w*.12,cx+w*.35):
  for y in(cy-d/2-15,cy+d/2+15):rect(x,y,38,45,0,h+70,0)
 crown=[(cx+(x-cx)*.66,cy+(y-cy)*.66) for x,y in footprint];prism(crown,h,h+350+(idx%3)*200,4)
 if idx%2:bar((cx,cy,h+400),(cx-160,cy,h+1100),20,1)
 else:radial(cx,cy,[(h+350,220),(h+750,220),(h+830,0)],1,16)
finish('SM_CR051_DistantDistrict')
scene['authorship']='Original project industrial silhouette kit; backdrop only, no playable interiors.'
bpy.ops.wm.save_as_mainfile(filepath=str(src/'CR051_IndustrialDepth.blend'));(out/'depth-manifest.json').write_text(json.dumps({'meshes':manifest,'palette':palette},indent=2));print('CR051_DEPTH_SOURCE '+json.dumps(manifest))
