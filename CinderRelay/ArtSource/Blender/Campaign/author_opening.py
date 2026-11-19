"""Create the editable 18-second arrival film. Run under Blender 4.5 in background mode."""
import math
import random
import sys
from pathlib import Path
import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from elias import build_elias,pose_elias

PROJECT=HERE.parents[2]
OUT=PROJECT.parent/'.environment-local/campaign-3d/opening'
OUT.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
scene.unit_settings.system='METRIC'
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples=8
scene.eevee.use_raytracing=False
scene.render.resolution_x=1280
scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.render.fps=24
scene.frame_start=1
scene.frame_end=432
scene.render.image_settings.file_format='JPEG'
scene.render.image_settings.quality=90
scene.render.image_settings.color_mode='RGB'
scene.render.filepath='//../../../../.environment-local/campaign-3d/opening/'
scene.render.use_file_extension=True
scene.render.use_sequencer=False
scene.render.use_compositing=False
scene.view_settings.view_transform='AgX'
scene.view_settings.exposure=.32
scene.world.use_nodes=True
world=scene.world.node_tree.nodes.get('Background')
world.inputs['Color'].default_value=(.235,.325,.365,1)
world.inputs['Strength'].default_value=.78
nodes=scene.world.node_tree.nodes
links=scene.world.node_tree.links
skycoords=nodes.new('ShaderNodeTexCoord')
altitude=nodes.new('ShaderNodeSeparateXYZ')
links.new(skycoords.outputs['Normal'],altitude.inputs[0])
skygradient=nodes.new('ShaderNodeValToRGB')
for element in list(skygradient.color_ramp.elements)[1:]:skygradient.color_ramp.elements.remove(element)
skygradient.color_ramp.elements[0].color=(.63,.365,.235,1)
for pos,color in ((.06,(.52,.40,.30)),(.18,(.305,.374,.393)),(.44,(.147,.265,.336)),(1,(.048,.14,.235))):
    stop=skygradient.color_ramp.elements.new(pos);stop.color=(*color,1)
height=nodes.new('ShaderNodeMath');height.operation='ABSOLUTE'
links.new(altitude.outputs['Z'],height.inputs[0])
links.new(height.outputs[0],skygradient.inputs['Fac'])
links.new(skygradient.outputs['Color'],world.inputs['Color'])
scene.world.color=(.19,.25,.28)
TAU=math.tau
def mat(title,color,rough=.8,metal=0,em=0):
    m=bpy.data.materials.new(title)
    m.use_nodes=True;m.diffuse_color=(*color,1)
    node=m.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value=(*color,1)
    node.inputs['Roughness'].default_value=rough
    node.inputs['Metallic'].default_value=metal
    if em:
        node.inputs['Emission Color'].default_value=(*color,1)
        node.inputs['Emission Strength'].default_value=em
    return m
materials={k:mat(k,*vals) for k,vals in {
    'Ash slab':((.21,.232,.22),.96),'Ballast':((.124,.144,.14),.96),
    'Rail steel':((.235,.24,.219),.59,.65),'Sleepers':((.16,.122,.086),.92),
    'Petrol paint':((.12,.24,.231),.68,.24),'Peeling steel':((.22,.30,.287),.74,.38),
    'Black iron':((.044,.072,.078),.64,.44),'Soot':((.059,.071,.066),.96),
    'Warm rust':((.32,.174,.098),.80,.32),'Ash':((.405,.417,.376),.90),
    'Chalk':((.75,.72,.57),.87),'Ochre enamel':((.65,.339,.080),.60,.22),
    'Glass dark':((.044,.084,.083),.36,.35),'Red lens':((.285,.039,.022),.38,.32),
    'Amber lamp':((1,.48,.13),.40,.02,4.0),'Verdigris':((.15,.241,.209),.88),
    'Distance':((.121,.193,.202),.97),'Distant ash':((.226,.295,.286),.98)
}.items()}
# Patchy oxidized paint and the apron take the same light differently across their surfaces.
for key,grain,strength,distance in (('Ash slab',4,.26,.022),('Ballast',19,.33,.03),
        ('Sleepers',7.5,.27,.013),('Petrol paint',7,.17,.004),('Warm rust',12,.26,.005)):
    tree=materials[key].node_tree;node=tree.nodes.get('Principled BSDF')
    noise=tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=grain
    noise.inputs['Detail'].default_value=3.0
    coord=tree.nodes.new('ShaderNodeTexCoord');tree.links.new(coord.outputs['Object'],noise.inputs['Vector'])
    ramp=tree.nodes.new('ShaderNodeValToRGB');base=materials[key].diffuse_color[:3]
    ramp.color_ramp.elements[0].color=(*(v*.48 for v in base),1)
    ramp.color_ramp.elements[1].color=(*(min(1,v*1.47) for v in base),1)
    tree.links.new(noise.outputs['Fac'],ramp.inputs['Fac']);tree.links.new(ramp.outputs[0],node.inputs['Base Color'])
    bump=tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength
    bump.inputs['Distance'].default_value=distance;tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
    tree.links.new(bump.outputs[0],node.inputs['Normal'])

def collection(n):
    c=bpy.data.collections.new(n);scene.collection.children.link(c);return c
ground=collection('01 / Ash-covered right of way')
architecture=collection('02 / Platform and workshop')
terminal=collection('03 / Relay cabinet and dead signal')
horizon=collection('04 / Foundry silhouettes and airborne ash')
lighting=collection('05 / Practical and daylight')
cams=collection('06 / Cut cameras')
def obj(n,verts,faces,m,c):
    d=bpy.data.meshes.new(n)
    d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(n,d)
    c.objects.link(o);d.materials.append(materials[m]);return o
def box(n,p,d,m,c=architecture,rot=(0,0,0),bevel=0):
    x,y,z=(a/2 for a in d)
    vs=[(i*x,j*y,k*z) for k in (-1,1) for j in (-1,1) for i in (-1,1)]
    f=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    o=obj(n,vs,f,m,c);o.location=p;o.rotation_euler=rot
    if bevel:
        b=o.modifiers.new('Pressed edge','BEVEL');b.width=bevel;b.segments=2
    return o
def beam(n,a,b,w,d,m,c=architecture):
    a,b=Vector(a),Vector(b);o=box(n,(a+b)/2,(w,d,(b-a).length),m,c)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def pipe(n,a,b,r,m,c=architecture,seg=16,r2=None):
    a,b=Vector(a),Vector(b);v=b-a;u=v.normalized()
    e=u.cross(Vector((0,0,1)) if abs(u.z)<.8 else Vector((1,0,0))).normalized()
    f=u.cross(e);verts=[]
    for p,rr in ((a,r),(b,r if r2 is None else r2)):
        for i in range(seg):verts.append(p+rr*(e*math.cos(i*TAU/seg)+f*math.sin(i*TAU/seg)))
    polys=[tuple(reversed(range(seg))),tuple(range(seg,seg*2))]
    polys += [(i,(i+1)%seg,(i+1)%seg+seg,i+seg) for i in range(seg)]
    o=obj(n,verts,polys,m,c)
    for m in o.data.polygons[2:]:m.use_smooth=True
    return o
def label(n,value,p,size,m,normal_yaw=math.pi,c=terminal):
    d=bpy.data.curves.new(n,'FONT');d.body=value;d.size=size;d.align_x='CENTER';d.align_y='CENTER'
    d.extrude=.0007;d.space_character=1.09
    o=bpy.data.objects.new(n,d);c.objects.link(o);d.materials.append(materials[m])
    o.location=p;o.rotation_euler=(math.pi/2,0,normal_yaw);return o
def area(n,p,target,color,power,size):
    d=bpy.data.lights.new(n,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(n,d);lighting.objects.link(o);o.location=p
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def point(n,p,color,power,radius):
    d=bpy.data.lights.new(n,'POINT');d.energy=power;d.color=color;d.shadow_soft_size=radius
    o=bpy.data.objects.new(n,d);lighting.objects.link(o);o.location=p

# Long rails and dusty flange grooves lead toward the station. Separate ballast faces form organic drift edges.
box('Embankment',(-8,0,-.25),(160,160,.46),'Ballast',ground)
box('Service apron',(.55,.3,-.092),(3.1,22,.18),'Ash slab',ground)
for j in range(-6,7):
    y=j*1.65
    box('Apron joint',(0.55,y,-.0005),(3.04,.012,.002),'Soot',ground)
    if j%2==0:box('Old edge demarcation',(-.65,y+.3,.003),(.065,.83,.004),'Chalk',ground)
for x in (-4.86,-3.43,2.48,3.91):
    box('Rail foot',(x,.6,-.009),(.16,45,.022),'Rail steel',ground)
    box('Rail web',(x,.6,.029),(.045,45,.075),'Warm rust',ground)
    box('Polished rail head',(x,.6,.075),(.092,45,.03),'Rail steel',ground,bevel=.01)
for j in range(-27,30):
    for x in (-4.14,3.19):
        box('Creosote sleeper',(x,j*.71,-.047),(2.3,.21,.084),'Sleepers',ground)
rng=random.Random(2118)
for i in range(130):
    x=rng.choice((-1,1))*rng.uniform(1.49,7.7)
    y=rng.uniform(-12,13);wid=rng.uniform(.04,.17)
    box('Ash shale',(x,y,.007),(wid,wid*rng.uniform(.56,1.38),rng.uniform(.011,.047)),
        rng.choice(('Ash','Ballast','Soot')),ground,(0,rng.uniform(-.13,.13),rng.uniform(0,3)))
for s in (-1,1):
    vs=[];faces=[]
    for i in range(36):
        y=-16+i*.93;a=1.35+.16*math.sin(i*.51)+.11*rng.random()
        vs.extend([(s*a,y,.006),(s*(a+.28+rng.random()*.27),y,.038+rng.random()*.065),(s*(a+1.04),y,-.011)])
    for i in range(35):
        for k in range(2):
            q=i*3+k
            face=(q,q+3,q+4,q+1);faces.append(face if s<0 else tuple(reversed(face)))
    obj('Banked powder along platform',vs,faces,'Ash',ground)

# West workshop is intentionally the only occupied pool of warm light, separate from the unpowered line.
box('Workshop rear shell',(-7.25,-4.4,2.03),(3.95,7.1,4.1),'Petrol paint',architecture)
for y,w in ((-6.70,2.1),(-2.45,3.1)):
    box('Recessed brick portal wing',(-5.14,y,1.56),(.38,w,3.14),'Peeling steel',architecture)
box('Doorway recess',(-5.185,-5.06,1.45),(.12,1.68,2.9),'Black iron')
box('Shut roller',(-5.09,-5.06,1.42),(.09,1.49,2.76),'Soot')
for z in range(1,16):
    box('Shutter slat',(-5.028,-5.06,z*.174),(.024,1.45,.037),'Rail steel')
box('Workshop canopy',(-4.96,-4.75,3.15),(1.16,5.3,.19),'Black iron')
box('Workshop lamp casing',(-4.91,-5.06,2.95),(.31,1.47,.18),'Black iron')
box('Workshop amber practical',(-4.735,-5.06,2.94),(.024,1.26,.083),'Amber lamp')
point('Workshop entry spill',(-4.45,-5.06,2.87),(1,.42,.12),160,.58)
label('Fixed workshop plate','WORKSHOP',(-4.92,-5.06,2.63),.19,'Chalk',math.pi/2,architecture)
for y in (-7.7,-6.9,-4.0,-3.13,-2.25,-1.33):
    beam('Workshop standing seam',(-5.20,y,.12),(-5.20,y,4.14),.06,.065,'Black iron')
box('Workshop clerestory',(-5.18,-4.38,3.77),(.18,6.46,.67),'Black iron')
for j in range(9):
    box('High-level frosted window',(-5.079,-7.21+j*.706,3.77),(.025,.63,.49),'Glass dark')

# The abandoned platform is built from riveted H columns, worn cappings and broken signal cables.
for x in (-2.31,5.59):
    for y in (-10,-4.3,2.1,8.15,14.5):
        box('Concrete column socket',(x,y,.12),(.47,.44,.26),'Ash slab')
        box('Column web',(x,y,2.2),(.11,.16,4.25),'Peeling steel')
        for dx in (-.104,.104):box('Riveted column flange',(x+dx,y,2.19),(.042,.25,4.25),'Black iron')
        beam('Canopy angle bracket',(x,y,3.32),(x+(.88 if x<0 else -.88),y,4.2),.081,.10,'Warm rust')
    box('Gantry stringer',(x,1.5,4.2),(.16,28,.22),'Black iron')
for j,y in enumerate((-10,-4.3,2.1,8.15,14.5)):
    box('Station crossbar',(1.64,y,4.23),(8.3,.16,.24),'Black iron')
    if j!=2:
        for k in range(3):
            box('Broken canopy strip',(-1.92+k*.53,y+1.14,4.39),(.50,3.07,.061),'Peeling steel',
                architecture,(.015*(k-1),.04*k,0))
for x in (-2.28,5.54):
    for j,(start,end) in enumerate(((-10,-4.3),(-4.3,2.1),(2.1,8.15),(8.15,14.5))):
        for k in range(4):
            def wire(t):return (x,start+(end-start)*t,4.08-.38*4*t*(1-t))
            pipe('Sagged signal wire',wire(k/4),wire((k+1)/4),.012,'Black iron',architecture,6)

# Instrument face (+Y): the glove can physically reach the unlit dial without intersecting the shell.
box('Bench foundation',(.22,-2.64,.09),(.96,.61,.18),'Ash slab',terminal,bevel=.033)
box('Relay cabinet body',(.22,-2.65,.77),(.79,.48,1.23),'Petrol paint',terminal,bevel=.045)
box('Rain hood',(.22,-2.62,1.51),(.88,.62,.095),'Peeling steel',terminal,bevel=.02)
box('Front panel',(.22,-2.386,1.19),(.70,.06,.51),'Black iron',terminal,bevel=.016)
box('Inspection bezel',(.22,-2.345,1.251),(.442,.04,.212),'Peeling steel',terminal,bevel=.017)
box('Sleeping relay window',(.22,-2.322,1.25),(.39,.018,.164),'Glass dark',terminal,bevel=.010)
materials['Glass powder']=mat('Soot powder on inspection glass',(.18,.197,.163),.94)
for j in range(9):
    x=.055+j*.040
    smudge=box('Ash wiped off instrument glass', (x,-2.309,1.26+.007*math.sin(j*1.84)),
               (.041,.001,.053+.016*math.cos(j*2.27)),'Glass powder',terminal)
    f=250+(8-j)*3
    for fr,amount in ((1,1),(f,1),(f+4,.015),(432,.015)):
        smudge.scale=(amount,1,amount);smudge.keyframe_insert(data_path='scale',frame=fr)
for x in (.08,.16,.24,.32):
    box('Cold indicator bar',(x,-2.307,1.254),(.024,.006,.062),'Soot',terminal)
for x in (-.064,.507):
    for z in (1.020,1.386):
        pipe('Cabinet screw',(x,-2.35,z),(x,-2.341,z),.012,'Rail steel',terminal,8)
for z in (.41,.47,.53,.59,.65):
    box('Vent louvre',(.22,-2.40,z),(.48,.047,.025),'Black iron',terminal)
label('Circuit engraving','LINE STATUS',(.22,-2.344,1.397),.044,'Chalk')
label('Relay designation','RELAY  09',(.22,-2.346,1.101),.049,'Chalk')
for s in (-1,1):
    pipe('Feed pipe',(.22+s*.29,-2.83,.28),(.22+s*.29,-2.83,-.013),.036,'Warm rust',terminal)
pipe('Fixed signal standard',(-1.40,-1.35,0),(-1.40,-1.35,3.58),.094,'Peeling steel',terminal)
box('Signal plinth',(-1.40,-1.35,.10),(.44,.43,.20),'Ash slab',terminal)
box('Signal head',(-1.40,-1.35,2.98),(.51,.22,1.1),'Black iron',terminal,bevel=.19)
for i,z in enumerate((2.72,3.18)):
    pipe('Signal bezel',(-1.4,-1.26,z),(-1.4,-1.16,z),.178,'Rail steel',terminal,24)
    pipe('Unpowered signal glass',(-1.4,-1.155,z),(-1.4,-1.141,z),.139,'Glass dark' if i else 'Red lens',terminal,28)
    box('Signal visor',(-1.4,-1.104,z+.155),(.37,.31,.039),'Black iron',terminal,bevel=.016)
box('Track number plate',(-1.4,-1.24,2.218),(.49,.036,.245),'Soot',terminal,bevel=.018)
label('Station number','09',(-1.4,-1.211,2.22),.16,'Chalk')

# Receding industrial skyline: roof breaks, vent silhouettes and a disused service water tower.
for i in range(19):
    x=-14.2-rng.uniform(0,12);y=-33+i*3.6;h=rng.uniform(2.2,5.0)
    box('Distant workshop mass',(x,y,h/2),(rng.uniform(3,7),rng.uniform(2.9,6.0),h),'Distance',horizon)
    if i%3==0:pipe('Foundry vent',(x,y,h),(x,y,h+rng.uniform(1.6,5.4)),.22,'Distant ash',horizon)
# Slow dawn behind the foreground silhouette: layered sawteeth and a low conveyor crossing the view.
for j in range(6):
    y=2.0+j*1.36;lo=3.12;hi=4.06;xl=-12.4;xr=-8.6
    verts=[(x,y+a,z) for x in (xl,xr) for a,z in ((0,lo),(1.34,lo),(1.34,hi))]
    obj('Sawtooth monitor',verts,[(0,2,1),(3,4,5),(0,3,5,2),(1,2,5,4),(0,1,4,3)],'Distance',horizon)
    box('Monitor glass',(xr+.024,y+1.16,3.49),(.04,.23,.53),'Glass dark',horizon)
for x,y,h in ((-15,9,6.3),(-17,16,7.6),(-18,19,6.6)):
    pipe('Stack shaft',(x,y,.18),(x,y,h),.24,'Distant ash',horizon,20,.18)
    pipe('Masonry lip',(x,y,h-.10),(x,y,h+.09),.21,'Distance',horizon,20)
for j in range(10):
    y=-10+j*2.5
    beam('Lattice conveyor upper chord',(-11.7,y,3.38),(-11.7,y+2.5,3.38),.113,.12,'Distance',horizon)
    beam('Lattice conveyor lower chord',(-11.7,y,2.73),(-11.7,y+2.5,2.73),.12,.13,'Distance',horizon)
    beam('Conveyor diagonal',(-11.7,y,2.73),(-11.7,y+2.5,3.38),.09,.08,'Peeling steel',horizon)
    if j%3==0:box('Conveyor trestle',(-11.7,y,1.36),(.16,.18,2.72),'Distance',horizon)
for j,(x,y) in enumerate(((-9.25,6.3),(8.0,-10.3))):
    for a,b in ((-.72,-.72),(.72,-.72),(-.72,.72),(.72,.72)):
        beam('Tower leg',(x+a*1.35,y+b*1.35,0),(x+a,y+b,4.1),.10,.12,'Black iron',horizon)
    pipe('Tank bowl',(x,y,3.72),(x,y,4.30),.34,'Warm rust',horizon,32,1.16)
    pipe('Water tower',(x,y,4.28),(x,y,6.03),1.16,'Distance',horizon,32)
    pipe('Ribbed tank crown',(x,y,6.0),(x,y,6.42),1.20,'Peeling steel',horizon,32,.12)
    for z in (4.45,5.35,5.9):pipe('Tank retaining band',(x,y,z),(x,y,z+.046),1.18,'Black iron',horizon,32)
flakes=[];ff=[]
for i in range(135):
    x,y,z=rng.uniform(-6,5),rng.uniform(-8,10),rng.uniform(.25,5)
    size=rng.uniform(.006,.017);base=len(flakes)
    flakes.extend([(x-size,y,z),(x+size,y,z+.005),(x,y+.003,z+size*.45)])
    ff.append((base,base+1,base+2))
ash=obj('Slow airborne ash',flakes,ff,'Ash',horizon)
for f,pos in ((1,(-.43,0,.32)),(432,(.60,-.37,-.41))):
    ash.location=pos;ash.keyframe_insert(data_path='location',frame=f)

# Soft daylight and the independent workshop fixture preserve legible facial planes in close-up.
data=bpy.data.lights.new('Low morning sun','SUN');data.energy=2.35;data.angle=.20;data.color=(1,.80,.61)
sun=bpy.data.objects.new('Low morning sun',data);lighting.objects.link(sun)
sun.rotation_euler=(math.radians(42),math.radians(-20),math.radians(-31))
area('Sky bounce',(2.7,-3.55,3.65),(0,-1.85,1.18),(.66,.80,.96),210,4.0)
area('Amber return',(-1.15,-2.65,2.27),(0,-1.85,1.47),(1,.49,.23),180,1.45)
area('Apron sky fill',(1.7,3.25,4.7),(0,2,1.24),(.60,.73,.86),235,5.1)
area('Dawn edge on coat',(-2.28,4.3,2.55),(0,2.4,1.04),(1,.48,.22),310,2.4)

rig=build_elias()
def interp(t,keys):
    if t<=keys[0][0]:return keys[0][1]
    for (a,av),(b,bv) in zip(keys,keys[1:]):
        if t<=b:return av+(bv-av)*(t-a)/(b-a)
    return keys[-1][1]
yk=[(1,4.60),(120,.96),(178,-.82),(204,-1.59),(216,-1.85),(432,-1.85)]
stride=[(1,.94),(178,.94),(204,.67),(216,0),(432,0)]
for frame in sorted(set(range(1,433,4))|{120,121,204,216,217,251,263,275,287,291,297,312,313,432}):
    y=interp(frame,yk)
    contact=None
    if 213<=frame<=326:
        pts=[(213,(.294,-1.95,.85)),(229,(.30,-2.05,1.00)),(248,(.367,-2.291,1.236)),
             (263,(.201,-2.302,1.255)),(275,(.074,-2.300,1.255)),(283,(.092,-2.247,1.222)),
             (291,(.111,-2.296,1.166)),(297,(.129,-2.215,1.15)),(313,(.265,-2.053,.97)),(326,(.291,-1.97,.856))]
        contact=tuple(interp(frame,[(f,p[k]) for f,p in pts]) for k in range(3))
    turn=interp(frame,[(1,0),(316,0),(353,-19),(394,-34),(432,-34)])
    look=interp(frame,[(1,5),(100,-4),(137,-13),(168,-23),(205,6),(235,19),(277,19),(315,7),(346,-42),(387,-63)])
    pitch=interp(frame,[(1,-2),(130,0),(175,8),(217,-6),(257,-16),(310,-13),(345,4),(410,6)])
    bend=interp(frame,[(1,3),(216,4),(243,10),(299,11),(335,1)])
    pose_elias(rig,frame,root=(0,y,0),yaw=turn,walk=(frame-1)*TAU/32,stride=interp(frame,stride),
               look=(look-turn,pitch),lean=bend,reach_r=contact,curl=.37 if contact is None else .14,
               hand_dir_r=((.06,-.075,-1) if frame<=279 else (.04,-.35,-.94)) if contact is not None else None)

def camera(name,first,last,keys):
    d=bpy.data.cameras.new(name);d.sensor_width=36;d.clip_end=200;d.dof.use_dof=True;d.dof.aperture_fstop=6.3
    c=bpy.data.objects.new(name,d);cams.objects.link(c)
    for f,pos,target,lens in keys:
        c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
        c.keyframe_insert(data_path='location',frame=f);c.keyframe_insert(data_path='rotation_euler',frame=f)
        d.lens=lens;d.keyframe_insert(data_path='lens',frame=f)
        d.dof.focus_distance=(Vector(target)-c.location).length
        d.dof.keyframe_insert(data_path='focus_distance',frame=f)
    marker=scene.timeline_markers.new(name,frame=first);marker.camera=c
    return c
first=camera('01 / Crossing the siding',1,120,[(1,(3.03,1.50,.94),(-.52,4.28,1.11),31),
              (65,(3.08,.28,1.01),(-.27,2.54,1.09),34),(120,(2.90,-.54,1.12),(-.10,1.04,1.09),35)])
camera('02 / Dead signal',121,216,[(121,(1.3,2.64,1.69),(-.43,-1.30,1.91),28),
              (177,(1.31,1.21,1.71),(-.38,-1.89,1.83),28),(216,(1.32,.20,1.76),(-.30,-2.12,1.60),30)])
camera('03 / Witness glass',217,312,[(217,(1.20,-1.82,1.52),(.09,-2.09,1.405),36),
              (248,(.85,-1.58,1.13),(.204,-2.276,1.254),41),
              (291,(.82,-1.56,1.117),(.190,-2.292,1.24),43),
              (312,(.90,-1.58,1.225),(.16,-2.23,1.30),38)])
camera('04 / Workshop light',313,432,[(313,(.98,-.96,1.58),(-.1,-1.91,1.48),45),
              (355,(1.33,-.39,1.63),(-.83,-2.47,1.52),37),(432,(2.13,.75,1.58),(-3.47,-4.04,1.72),31)])
scene.camera=first
scene.frame_set(1)
# Save standard linear interpolation for the stepped walk samples; camera keys retain their eased travel.
if rig.animation_data and rig.animation_data.action:
    a=rig.animation_data.action
    for layer in a.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for k in curve.keyframe_points:k.interpolation='LINEAR'
source=HERE/'CR_Opening3D.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print('CR_OPENING_SOURCE',source,'frames',scene.frame_start,scene.frame_end,'bones',len(rig.data.bones))
