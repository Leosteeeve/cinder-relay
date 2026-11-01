"""Original fictional exterior hero asset; no functional internals.
Centimeters, +X forward, +Z up. Curved lofts and swept exterior detail.
Creates a NEW source; never edits Phase03/05. Export intermediates are ignored.
"""
import bpy, math, json, argparse, sys
from pathlib import Path
from mathutils import Vector
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True)
out=Path(ap.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir);out.mkdir(parents=True,exist_ok=True)
src=Path(__file__).resolve().parent;tex=src.parents[1]/'Textures/Phase051'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
def material(name,color,metal,rough,texture=None):
 m=bpy.data.materials.new('CR051_'+name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if texture:
  for suffix,dest in [('diff','Base Color'),('arm','Roughness'),('nor_dx','Normal')]:
   path=tex/(texture+'_'+suffix+'_2k.jpg');assert path.exists(),path
   image=bpy.data.images.load(str(path),check_existing=True);n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=image
   if suffix=='diff':m.node_tree.links.new(n.outputs['Color'],p.inputs[dest])
   elif suffix=='arm':
    image.colorspace_settings.name='Non-Color';sep=m.node_tree.nodes.new('ShaderNodeSeparateColor');m.node_tree.links.new(n.outputs['Color'],sep.inputs['Color']);m.node_tree.links.new(sep.outputs['Green'],p.inputs[dest])
   else:
    image.colorspace_settings.name='Non-Color';normal=m.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.16;m.node_tree.links.new(n.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],p.inputs[dest])
 return m
mats={'Wood':material('Wood',(.21,.085,.035),0,.48,'wood_table_001'),'Steel':material('Steel',(.11,.15,.18),.85,.33),'Brass':material('Brass',(.33,.21,.075),.8,.4),'Rubber':material('Rubber',(.025,.031,.029),0,.78),'Lens':material('Lens',(.06,.27,.25),.15,.12),'Reticle':material('Reticle',(.06,.7,.42),0,.4)}
mats['Reticle'].node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(.06,.9,.4,1);mats['Reticle'].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=2
objects=[]
def mesh(name,verts,faces,mat,smooth=True):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.data.materials.append(mats[mat])
 for p in data.polygons:p.use_smooth=smooth
 uv=data.uv_layers.new(name='HeroUV')
 for face in data.polygons:
  axes=((1,2),(0,2),(0,1))[max(range(3),key=lambda i:abs(face.normal[i]))]
  for li in face.loop_indices:
   v=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/65+.5,v[axes[1]]/65+.5)
 objects.append(o);return o
def loft(name,rings,mat,n=48,sub=2):
 # rings: x, half-width, half-height, center-z; shape designed in profile.
 v=[(x,wy*math.cos(2*math.pi*j/n),z+hz*math.sin(2*math.pi*j/n)) for x,wy,hz,z in rings for j in range(n)]
 f=[(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j) for i in range(len(rings)-1) for j in range(n)];f+=[tuple(reversed(range(n))),tuple((len(rings)-1)*n+j for j in range(n))]
 o=mesh(name,v,f,mat)
 if sub:
  mod=o.modifiers.new('Editable surface subdivision','SUBSURF');mod.levels=sub;mod.render_levels=sub
 return o
def tube(name,points,radius,mat,sides=12):
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=10;curve.bevel_depth=radius;curve.bevel_resolution=3;sp=curve.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,curve);scene.collection.objects.link(o);o.data.materials.append(mats[mat]);objects.append(o);return o
def cylinder(name,a,b,radius,mat,n=48):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
 if u.length<.01:u=axis.cross(Vector((0,1,0)))
 u.normalize();w=axis.cross(u);verts=[tuple(p+radius*(u*math.cos(j*2*math.pi/n)+w*math.sin(j*2*math.pi/n))) for p in (a,b) for j in range(n)];faces=[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]+[tuple(reversed(range(n))),tuple(range(n,2*n))]
 o=mesh(name,verts,faces,mat);be=o.modifiers.new('Edge highlights','BEVEL');be.width=min(.08,radius*.12);be.segments=3;return o
def ring(name,x,z,wy,hz,thick,mat,n=64,depth=.4):
 verts=[]
 for px in (x-depth/2,x+depth/2):
  for offset in (0,thick):
   for j in range(n):
    a=2*math.pi*j/n;verts.append((px,(wy-offset)*math.cos(a),z+(hz-offset)*math.sin(a)))
 faces=[]
 for j in range(n):
  k=(j+1)%n
  faces += [(j,k,2*n+k,2*n+j),(n+j,3*n+j,3*n+k,n+k),(j,n+j,n+k,k),(2*n+j,2*n+k,3*n+k,3*n+j)]
 return mesh(name,verts,faces,mat)

# One continuous contoured stock rather than separate blocky receiver/grip/stock cubes.
loft('Sculpted walnut stock',[(-50,1.9,5,-4),(-49.7,2.3,6,-4),(-46,2.6,6.6,-4),(-36,2.6,5.9,-2.5),(-29,2.1,3.2,-1),(-25,1.8,2.2,-1.3),(-21,1.9,2.2,-3),(-17,2.2,3.5,-3.2),(-12,2.8,3.3,-2.5),(-7,3.4,2.8,-2.2),(9,3.3,2.9,-2),(14,2.7,2.8,-1.7),(17,2.5,2.3,-1.5),(17.4,2.2,2,-1.5)],'Wood',48,2)
loft('Oval receiver exterior',[(-21,.2,.2,2),(-20,2.3,2.5,2),(-18,3.2,3.1,2),(-14,3.35,3.2,2),(8,3.2,3,2),(13,2.5,2.6,2),(16,2.1,2.1,2),(16.5,2,2,2)],'Steel',48,2)
loft('Tapered rounded fore-end',[(14,2.6,2.3,-1.4),(15,2.9,2.5,-1.4),(24,2.6,2.3,-1.1),(34,2.2,1.9,-.8),(38,1.95,1.7,-.6),(38.5,1.8,1.6,-.6)],'Wood',48,2)
cylinder('Exterior barrel',(13,0,2.3),(66,0,2.3),1.18,'Steel',64)
for x,r in [(18,1.45),(36,1.48),(61.7,1.5),(65.9,1.4)]:ring('Barrel band',x,2.3,r,r,.22,'Steel',48,.9)
ring('Muzzle dark opening',66.22,2.3,1.2,1.2,.42,'Rubber',48,.12)
cylinder('Muzzle recess',(66.1,0,2.3),(66.18,0,2.3),.76,'Rubber',48)
loft('Rubber shoulder pad',[(-51.1,2.4,6,-4),(-51,2.6,6.4,-4),(-49.8,2.6,6.4,-4),(-49.5,2.3,6,-4)],'Rubber',48,1)
# Coherent curved exterior guard and service detail, intentionally fictional.
tube('Exterior trigger guard',[(-15,0,-4),(-16,0,-7),(-14,0,-9),(-9,0,-9.5),(-5,0,-8),(-4,0,-5)],.4,'Steel')
tube('Guard insert',[(-10,0,-4),(-9.8,0,-6),(-10.4,0,-7)],.24,'Steel')
loft('Flush lower housing',[(-2,1.9,1,-6),(0,2.2,1.2,-6),(8,2.1,1.1,-6),(10,1.5,.8,-6)],'Steel',32,1)
for x in (-16,-9,7,32):
 for side in (-1,1):
  cylinder('Exterior fastener',(x,side*3.15,.7),(x,side*3.32,.7),.35,'Steel',24)
  tube('Fastener slot',[(x-.18,side*3.34,.7),(x+.18,side*3.34,.7)],.035,'Rubber')
for y in (-1,1):
 tube('Fore-end seam',[(x,y*w,z) for x,w,z in [(15,2.6,-.1),(22,2.5,.1),(31,2.1,.2),(36,1.8,.25)]],.055,'Rubber')
 tube('Stock inlay',[(x,y*w,z) for x,w,z in [(-45,2.55,-.5),(-39,2.7,.5),(-33,2.4,1),(-30,2.1,1)]],.07,'Brass')
# Low visual notch and post; axis exactly z8.2, +X. No large golden blocks.
profile=[(-1.25,7.2),(-1.25,8.2),(-.42,8.2),(-.30,7.84),(.30,7.84),(.42,8.2),(1.25,8.2),(1.25,7.2)]
verts=[(x,y,z) for x in(-16.2,-15.8) for y,z in profile];n=len(profile)
leaf=mesh('Formed notched rear leaf',verts,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)],'Steel',False)
bevel=leaf.modifiers.new('Leaf rounded edges','BEVEL');bevel.width=.055;bevel.segments=3
for side in (-1,1):
 tube('Rear sight white index',[(-16.26,side*.65,8.12),(-16.26,side*.95,8.12)],.04,'Brass')
 tube('Rear leaf support',[(-16,side*.9,5.1),(-16,side*.9,7.3)],.18,'Steel')
cylinder('Front sight ramp',(53,0,3.4),(53,0,7.9),.42,'Steel',32)
cylinder('Front sight post',(53,0,7.6),(53,0,8.2),.13,'Brass',24)
for side in (-1,1):tube('Front protective wing',[(52.8,side*1.1,4.5),(52.8,side*1.6,6.8),(52.8,side*1.4,7.7)],.18,'Steel')
# Small formed service plate and engraved fictional marking, not copied branding.
tube('Service plate rim',[(-15,-3.35,2),(-14,-3.5,3.2),(-7,-3.5,3.2),(-6,-3.35,2),(-15,-3.35,2)],.06,'Brass')
bpy.ops.object.text_add(location=(-14,-3.48,2.3),rotation=(math.pi/2,0,0));label=bpy.context.object;label.name='Original ROOK-5 exterior marking';label.data.body='ROOK-5';label.data.size=.8;label.data.extrude=.012;label.data.materials.append(mats['Brass']);objects.append(label)
gun_parts=list(objects);objects=[]
# Survey optic: short oval hood, slim base, real lens plane and aperture-bound reticle.
ring('Survey continuous thin-walled housing',-8.75,11.6,2.8,2.4,.28,'Steel',96,8.5)
for x in (-13,-4.5):ring('Survey machined rim',x,11.6,2.94,2.54,.4,'Steel',96,.45)
for y in (-1.7,1.7):tube('Survey mounting shoe',[(-12,y,5),(-12,y,7.7),(-9,y,9.25),(-5,y,7.7),(-5,y,5)],.28,'Steel')
cylinder('Survey calibration dial',(-8,-2.5,11.5),(-8,-3.6,11.5),.82,'Steel',48)
for j in range(16):
 a=j*math.pi/8;tube('Dial knurl',[(-8+.78*math.cos(a),-2.8,11.5+.78*math.sin(a)),(-8+.78*math.cos(a),-3.5,11.5+.78*math.sin(a))],.045,'Brass')
ring('Survey aperture seal',-12.9,11.6,2.6,2.2,.12,'Rubber',64,.22)
n=64;v=[(-5,0,11.6)]+[(-5,2.52*math.cos(2*math.pi*j/n),11.6+2.12*math.sin(2*math.pi*j/n)) for j in range(n)];mesh('Survey lens',v,[(0,1+j,1+(j+1)%n) for j in range(n)],'Lens')
ring('Etched optical reticle',-5.02,11.6,.22,.22,.025,'Reticle',48,.015)
cylinder('Optical center',(-5.04,0,11.6),(-5.06,0,11.6),.035,'Reticle',16)
for sy,sz in [(1,0),(-1,0),(0,-1)]:tube('Optical reticle index',[(-5.03,sy*.32,11.6+sz*.32),(-5.03,sy*.55,11.6+sz*.55)],.019,'Reticle')
optic_parts=list(objects)
def evaluated_copy(parts,name):
 copies=[];bpy.ops.object.select_all(action='DESELECT')
 for p in parts:
  p.select_set(False);o=p.copy();o.data=p.data.copy();scene.collection.objects.link(o);o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');copies.append(bpy.context.object);bpy.ops.object.select_all(action='DESELECT')
 for o in copies:o.select_set(True)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 # Converted curves/text get stable planar UVs; authored loft UVs remain.
 if not o.data.uv_layers:o.data.uv_layers.new(name='HeroUV')
 return o
rook=evaluated_copy(gun_parts,'SM_CR051_Rook5');optic=evaluated_copy(optic_parts,'SM_CR051_SurveyOptic')
manifest={'convention':'centimeters +X forward +Z up; FBX -Y/Z; verify actual import','meshes':[],'sights':{'SightAnchor_Iron':{'location':[-16,0,8.2],'rotation':[0,0,0]},'SightAnchor_Optic':{'location':[-13,0,11.6],'rotation':[0,0,0]}}}
for o in (rook,optic):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;o.data.calc_loop_triangles()
 bpy.ops.export_scene.fbx(filepath=str(out/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE')
 manifest['meshes'].append({'name':o.name,'triangles':len(o.data.loop_triangles),'dimensions_cm':list(o.dimensions),'materials':[m.name for m in o.data.materials]})
source_col=bpy.data.collections.new('EDITABLE SURFACES - nonexport');scene.collection.children.link(source_col)
for o in gun_parts+optic_parts:
 for c in list(o.users_collection):c.objects.unlink(o)
 source_col.objects.link(o)
source_col.hide_render=True;source_col.hide_viewport=True
for name,s in manifest['sights'].items():
 o=bpy.data.objects.new(name,None);scene.collection.objects.link(o);o.location=s['location'];o.empty_display_type='ARROWS';o.empty_display_size=3
scene['authorship']='Original fictional exterior, no functional internal mechanisms. CC0 wood/rust maps separately registered.'
scene['review']='Requires actual Unreal sight/visual acceptance, not production-quality certification.'
for image in bpy.data.images:
 if image.source=='FILE':image.filepath=bpy.path.relpath(image.filepath,start=str(src))
bpy.ops.wm.save_as_mainfile(filepath=str(src/'CR051_Rook5.blend'))
(out/'rook-manifest.json').write_text(json.dumps(manifest,indent=2));print('CR051_ROOK_SOURCE '+json.dumps(manifest))
