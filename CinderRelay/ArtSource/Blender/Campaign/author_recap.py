"""Build the editable relay-repair performance and render its 24-second camera cut."""
import argparse
import math
from pathlib import Path
import random
import sys
sys.dont_write_bytecode = True

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
OUT = PROJECT.parent / '.environment-local' / 'campaign-3d' / 'recap'
parser = argparse.ArgumentParser()
parser.add_argument('--render', action='store_true')
parser.add_argument('--samples', default='')
parser.add_argument('--stage-only', action='store_true')
parser.add_argument('--workbench', action='store_true')
parser.add_argument('--shot-render', type=int, choices=range(1,7))
parser.add_argument('--output-dir', type=Path)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH' if args.workbench else 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start, scene.frame_end = 1, 576
scene.render.image_settings.file_format = 'JPEG'
scene.render.image_settings.quality = 89
scene.render.filepath = str(OUT) + '/'
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = -.55
scene.world = bpy.data.worlds.new('Cold night beyond the switchroom')
scene.world.color = (.12,.17,.19)
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes['Background']
bg.inputs[0].default_value = (.26,.37,.42,1)
bg.inputs[1].default_value = .15
if not args.workbench:
    scene.eevee.taa_render_samples = 32
    scene.eevee.use_shadows = True
else:
    sh = scene.display.shading
    sh.light = 'STUDIO'; sh.studio_light = 'paint.sl'; sh.color_type = 'MATERIAL'
    sh.show_shadows = True; sh.shadow_intensity = .42; sh.show_cavity = True
    sh.cavity_type = 'WORLD'; sh.cavity_ridge_factor = 1.12; sh.cavity_valley_factor = 1.2
    sh.show_specular_highlight = True; sh.background_type = 'WORLD'
    scene.display.render_aa = 'FXAA'

def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c

sets = collection('01 | Relay Nine switchroom')
instruments = collection('02 | Instruments and powered circuit')
crossing = collection('04 | Floodplain and survey aerial')
cameras = collection('05 | Six-shot edit and cinematography')
group = sets

def organize(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    group.objects.link(o)
    return o

def mat(name, rgb, metal=0., rough=.55, power=0.):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb,1); m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*rgb,1)
    b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    if power:
        b.inputs['Emission Color'].default_value = (*rgb,1)
        b.inputs['Emission Strength'].default_value = power
    return m

paint = mat('Petrol | worn station enamel',(.058,.173,.169),.37)
steel = mat('Pressed slate steel',(.18,.245,.245),.62,.42)
rib = mat('Oxidised petrol shadow',(.027,.058,.061),.42)
iron = mat('Rough graphite',(.041,.055,.059),.55)
rubber = mat('Black phenolic rubber',(.014,.019,.020),.1,.78)
brass = mat('Aged brass',(.52,.26,.075),.6)
orange = mat('Safety orange enamel',(.8,.25,.043),.28)
cream = mat('Faded ivory type',(.82,.79,.60),.1)
slate = mat('Weathered concrete',(.18,.224,.215))
rust = mat('Service oxidation',(.275,.12,.060),.36)
warm = mat('Incandescent practical',(.99,.59,.21),0,.4,3.5)
cool = mat('Cold latch indicator',(.13,.89,.90),0,.34,3.7)
blackglass = mat('Grid phosphor',(.015,.055,.059),.05,.38)

def mesh_obj(name, verts, faces, material):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); group.objects.link(o); o.data.materials.append(material)
    return o

def box(name, p, dims, m, bevel=0.):
    dx,dy,dz=(v*.5 for v in dims)
    verts=[(x,y,z) for z in (-dz,dz) for y in (-dy,dy) for x in (-dx,dx)]
    o=mesh_obj(name,verts,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],m)
    o.location=p
    if bevel:
        mod=o.modifiers.new('Fold radius','BEVEL'); mod.width=min(bevel,min(dims)*.44); mod.segments=2
        normals=o.modifiers.new('Machined normals','WEIGHTED_NORMAL'); normals.keep_sharp=True
    return o

def rod(name, start, end, radius, m, sides=12):
    a,b=Vector(start),Vector(end); d=b-a
    verts=[(radius*math.cos(i*math.tau/sides),radius*math.sin(i*math.tau/sides),z) for z in (-d.length/2,d.length/2) for i in range(sides)]
    faces=[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]+[(i,(i+1)%sides,sides+(i+1)%sides,sides+i) for i in range(sides)]
    o=mesh_obj(name,verts,faces,m);o.location=(a+b)*.5;o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    return o

def cable(name,points,r,m):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=5;cu.bevel_depth=r;cu.bevel_resolution=1
    spline=cu.splines.new('BEZIER');spline.bezier_points.add(len(points)-1)
    for b,p in zip(spline.bezier_points,points):
        b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
    ob=bpy.data.objects.new(name,cu);group.objects.link(ob);cu.materials.append(m);return ob

def text(name,words,pos,height,m,center=True,front=1):
    cu=bpy.data.curves.new(name,'FONT');cu.body=words;cu.size=height;cu.align_x='CENTER' if center else 'LEFT';cu.align_y='CENTER';cu.extrude=.0005
    ob=bpy.data.objects.new(name,cu);group.objects.link(ob);cu.materials.append(m);ob.location=pos
    ob.rotation_euler=(math.pi/2,0,math.pi if front==1 else 0)
    return ob

def append(name,file,p,s=1.,yaw=0):
    with bpy.data.libraries.load(str(file),link=False) as (available,load):
        assert name in available.objects,(name,str(file))
        load.objects=[name]
    obj=load.objects[0];group.objects.link(obj);obj.location=p;obj.scale=(s,)*3;obj.rotation_euler=(0,0,math.radians(yaw))
    obj.hide_render=False;obj.hide_viewport=False;obj.hide_set(False)
    for m in obj.data.materials:
        if m and not m.use_nodes:
            color=tuple(m.diffuse_color);m.use_nodes=True
            b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=color;b.inputs['Roughness'].default_value=.52
    return obj

def life(o,channel,values):
    for f,v in values:
        setattr(o,channel,v);o.keyframe_insert(data_path=channel,frame=f)

def illumination(name,pos,target,color,energy,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color
    o=bpy.data.objects.new(name,d);group.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o

# Riveted switchroom, a cable gallery and a recessed instrument work bay.
box('Reinforced slab',(0,0,-.1),(9,9,.19),slate)
for x in range(-4,5):
    box('Slab expansion seam',(x,0,0),(.014,8,.006),iron)
for y in range(-3,5):
    box('Slab expansion seam',(0,y,0),(8,.015,.006),iron)
box('North bulkhead',(0,-1.36,1.67),(8,.2,3.36),slate)
box('West bulkhead',(-3.1,1.05,1.67),(.22,4.95,3.36),paint)
# The reaction reverse looks into this service aisle. Keep the dark bulkhead and
# active lamp in the actor's room visible behind him rather than the exterior stage.
box('Far switchroom wall',(0,2.50,1.68),(8,.23,3.37),rib)
box('East switchroom wall',(2.90,.77,1.69),(.19,3.64,3.38),rib)
for x in (-2.7,-1.7,-.7,.3,1.3,2.3):
    box('Far wall field',(x,2.35,1.47),(.94,.12,2.8),paint,.015)
    box('Far wall column',(x-.44,2.21,1.55),(.056,.16,3.0),iron)
for z in (.46,.58,2.23):
    rod('Transit pipe across switchroom',(-3.1,2.14,z),(2.88,2.14,z),.048,steel,16)
for y in (-.30,.40,1.1,1.8):
    box('East air distribution',(2.80,y,1.32),(.065,.62,2.18),paint,.02)
    for z in (.53,.61,.69,.77,.85,.93):
        box('Extract grille',(2.75,y,z),(.035,.53,.031),iron)
for y in (.22,1.38):
    rod('East work lamp',(2.71,y-.15,1.84),(2.71,y+.15,1.84),.033,warm)
for x in (-3,-2.05,-1.1,-.15,.8,1.75,2.7,3.65):
    box('Pressed wall module',(x,-1.235,1.49),(.90,.09,2.88),paint,.035)
    for z in (.18,2.83):
        for xx in (x-.39,x+.39):
            rod('Hex structural rivet',(xx,-1.174,z),(xx,-1.157,z),.026,steel,6)
    box('Raised kickplate',(x,-1.161,.46),(.78,.03,.54),rib,.01)
    box('Cable tray bracket',(x,-1.045,2.69),(.065,.31,.06),steel)
for z in (2.61,2.71,2.82):
    rod('Overhead east cable tray',(-3.2,-1.05,z),(3.6,-1.05,z),.035,iron)
for x in (-2.7,1.42,2.21):
    for delta in (0,.085):
        cable('Bent conduit riser',[(x+delta,-1.12,.05),(x+delta,-1.12,2.14),(x+delta+.19,-1.12,2.41),(x+delta+.79,-1.12,2.42)],.031,steel)
for x in (-2.75,-1.85,1.35,2.12):
    box('Spare relay cabinet',(x,-1.02,1.05),(.64,.37,2.04),rib,.025)
    box('Gasketed relay door',(x,-.815,1.15),(.55,.043,1.61),paint,.019)
    for i in range(13):
        box('Cooling louvers',(x,-.783,.72+i*.035),(.40,.025,.017),iron,.004)
    box('Cabinet label',(x,-.781,1.58),(.29,.025,.11),cream,.005)
    text('Panel serial','L / 9', (x,-.761,1.58),.052,iron)
for x in (-1.70,.9,2.67):
    box('Bench task light enclosure',(x,-.85,2.38),(.74,.19,.10),iron,.022)
    box('Prismatic work light',(x,-.746,2.36),(.60,.025,.054),warm,.016)
    for dx in (-.23,-.08,.08,.23):box('Lamp grille',(x+dx,-.723,2.36),(.014,.020,.071),steel)
box('Shuttering shadow rail',(0,-.95,.105),(4.65,.40,.18),iron,.014)
box('Switch bank plinth',(.05,-.92,.49),(1.94,.50,.92),paint,.037)
box('Switch bank lower access',(.12,-.648,.60),(1.67,.041,.79),rib,.018)
for i in range(17):box('Long folded radiator fin',(-.6+i*.092,-.61,.61),(.035,.065,.59),steel,.007)
for x in (-.63,.72):
    for z in (.24,.99):rod('Access cover fastener',(x,-.60,z),(x,-.578,z),.018,brass,6)
box('Main enamel fascia',(.04,-.84,1.655),(1.85,.44,.49),paint,.039)
box('West fascia support',(-.43,-.84,1.18),(.86,.40,.50),paint,.025)
box('East fascia support',(.72,-.84,1.18),(.45,.40,.50),paint,.025)
rod('Operator steady rail',(-.23,-.557,1.245),(-.033,-.557,1.245),.022,steel)
for x in (-.23,-.033):rod('Steady rail fixing',(x,-.66,1.245),(x,-.557,1.245),.024,steel)
box('Identification plate',(-.35,-.601,2.08),(1.18,.035,.25),iron,.018)
text('Nameplate','RELAY   NINE',(-.35,-.578,2.10),.135,cream)
text('Division','MERIDIAN     /     LOCAL SWITCHBOARD',(-.35,-.578,2.00),.034,cream)
for x in (-.85,.15):
    for z in (1.98,2.18):rod('Nameplate screw',(x,-.58,z),(x,-.56,z),.012,brass,8)

group=instruments
lib=HERE.parent/'Phase05'/'CR05_IndustrialKit.blend'
meterlib=HERE.parent/'Phase06'/'CR06_Receiver.blend'
dial=append('SM_CR06_ReceiverDial',meterlib,(-.42,-.615,1.66),.00265,-90)
needle=append('SM_CR06_ReceiverNeedle',meterlib,(-.42,-.615,1.66),.00265,-90)
needle.rotation_mode='XYZ'
life(needle,'rotation_euler',[(1,(math.radians(-57),0,-math.pi/2)),(264,(math.radians(-57),0,-math.pi/2)),(281,(math.radians(24),0,-math.pi/2)),(291,(math.radians(10),0,-math.pi/2)),(301,(math.radians(14),0,-math.pi/2)),(315,(math.radians(30),0,-math.pi/2)),(330,(math.radians(11),0,-math.pi/2)),(365,(math.radians(13),0,-math.pi/2)),(370,(math.radians(48),0,-math.pi/2)),(395,(math.radians(17),0,-math.pi/2))])

# The original Chapter 01 power unit, seated by its upper carry grip.
# Model-space -X faces the operator; the original handle is at (-19,0,57) cm.
socket_x=.28; socket_z=1.14; module_scale=.00268
for x in (.108,.452):box('Socket upright',(x,-.635,1.185),(.042,.27,.425),steel,.01)
for z in (.982,1.398):box('Socket sill',(socket_x,-.635,z),(.385,.27,.032),steel,.009)
box('Socket recess',(socket_x,-.758,socket_z),(.3,.015,.278),rubber)
for x in (.125,.435):box('Insulated guide rail',(x,-.61,socket_z),(.014,.30,.23),orange,.004)
text('Receptacle designation','MODULE  /  09',(.285,-.495,1.398),.031,cream)
power=append('SM_CR05_PowerUnit',lib,(socket_x,-.12,socket_z),module_scale,-90)
module_keys=[(1,(.265,-.105,.947)),(47,(.26,-.12,.97)),(87,(.275,-.17,1.12)),(105,(.28,-.205,1.14)),(138,(.28,-.28,1.14)),(168,(.28,-.55,1.14)),(176,(.28,-.612,1.14)),(576,(.28,-.612,1.14))]
life(power,'location',module_keys)
handle_offset=Vector((0,.051,.153))

switch= bpy.data.objects.new('Isolator handle pivot',None);group.objects.link(switch)
switch.location=(.51,-.55,1.45)
rod('Isolator horizontal boss',(.45,-.55,1.45),(.57,-.55,1.45),.046,brass,20)
for name,a,b,r,material in [('Link',(0,0,0),(0,.014,.175),.019,steel),('Handle',(-.065,.014,.175),(.065,.014,.175),.025,orange)]:
    o=rod(name,a,b,r,material,16);o.parent=switch
lever_keys=[(1,-60),(214,-60),(230,-64),(249,-118),(260,-152),(576,-152)]
life(switch,'rotation_euler',[(f,(math.radians(a),0,0)) for f,a in lever_keys])
text('Lock legend','ISOLATE',(.68,-.604,1.54),.032,cream)
text('Lock legend','RUN',(.66,-.604,1.34),.035,cream)
for col,x in enumerate((.34,.48,.62,.76)):
    box('Lamp bezel',(x,-.622,1.71),(.093,.03,.098),iron,.014)
    lamp=box('Restoration pilot '+str(col),(x,-.645+ .044,1.71),(.063,.02,.061),warm,.013)
    life(lamp,'scale',[(1,(.001,.001,.001)),(259+col*2,(.001,.001,.001)),(263+col*2,(1,1,1))])

# An oscilloscope beside the analog instrument makes the two distinct events legible.
before_scope=set(group.objects)
box('Return comparator housing',(.40,-.802,1.94),(.81,.25,.35),iron,.028)
box('Cathode screen',(.40,-.661,1.94),(.69,.035,.228),blackglass,.025)
for i in range(9):box('Scope reticle',(.07+i*.082,-.638,1.94),(.002,.004,.188),steel)
for i in range(5):box('Scope reticle',(.40,-.638,1.856+i*.042),(.65,.004,.002),steel)
text('Scope stamp','RETURN  /  TRACE',(.40,-.665,2.087),.03,cream)
box('Quiet trace',(.40,-.628,1.94),(.63,.004,.0035),cool)
for signal,(x,m,start) in enumerate(((.51,warm,315),(.272,cool,367))):
    pts=[(x+dx,-.62,1.94+z) for dx,z in ((-.065,0),(-.038,0),(-.024,.021),(-.015,-.027),(0,.089),(.010,-.052),(.024,.022),(.038,-.008),(.052,0),(.068,0))]
    trace=cable('Local impulse' if not signal else 'Delayed return',pts,.005,m)
    for f,v in [(1,True),(start-1,True),(start,False)]:
        trace.hide_render=v;trace.keyframe_insert(data_path='hide_render',frame=f)
    for f,v in [(1,True),(start-1,True),(start,False)]:
        trace.hide_viewport=v;trace.keyframe_insert(data_path='hide_viewport',frame=f)
confirm_display=[
    box('Acknowledgement raster',(.40,-.608,1.944),(.672,.008,.204),blackglass,.007),
    text('Incoming network','MERIDIAN NETWORK',(.40,-.601,1.974),.047,cool),
    text('Terminal acknowledgement','CONNECTION RESTORED',(.40,-.600,1.906),.037,cream)]
for o in confirm_display:
    for f,value in ((1,True),(379,True),(380,False)):
        o.hide_render=value;o.keyframe_insert(data_path='hide_render',frame=f)
        o.hide_viewport=value;o.keyframe_insert(data_path='hide_viewport',frame=f)
# Leave enough room beside the deeper analog instrument for both display lines.
for o in set(group.objects)-before_scope: o.location.x += .33

# Camera-facing panels use warm keys with a cool truss rim and negative fill.
group=cameras
illumination('Workshop practical softbox',(.85,-.16,2.90),(.15,-.42,1.22),(1,.57,.27),88,1.12)
illumination('Window rim',(-1.5,1.8,2.75),(0,-.25,1.3),(.37,.73,.91),124,1.85)
illumination('Face return bounce',(-1.10,-.60,1.66),(0,-.02,1.54),(.71,.84,.91),25,.98)
illumination('Steel instrument skim',(1.44,.48,1.88),(.24,-.56,1.32),(.55,.76,.81),32,1.1)

group=crossing
echo=HERE.parent/'Chapter02'/'CR02_EchoCrossing.blend'
water=mat('Floodplain silver / cold',(.085,.182,.213),.27,.27)
skyline=mat('Misty floodplain ridge',(.155,.23,.24))
dawn=mat('Horizon at dawn',(.48,.41,.31),0,.85,.38)
box('River',(16,16,-.13),(140,115,.2),water)
random.seed(97)
for k in range(105):
    x,y=random.uniform(-4,45),random.uniform(5,36)
    box('Rippling water',(x,y,-.024),(random.uniform(.16,1),.015,.005),steel)
def hill(y,z,m):
    xs=range(-160,250,2);vs=[(x,y,-2) for x in xs]+[(x,y,z+math.sin(x*.18)*1.4+math.sin(x*.73)*.18) for x in xs]
    n=len(xs);mesh_obj('River ridge',vs,[(i,i+1,i+1+n,i+n) for i in range(n-1)],m)
hill(37,1.45,skyline);hill(47,3.0,dawn)
sky=mat('Floodplain sky',(.4,.5,.5))
nt=sky.node_tree;nt.nodes.clear()
geo=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0])
ratio=nt.nodes.new('ShaderNodeMath');ratio.operation='MULTIPLY';ratio.inputs[1].default_value=.038;nt.links.new(sep.outputs['Z'],ratio.inputs[0])
gradient=nt.nodes.new('ShaderNodeValToRGB');nt.links.new(ratio.outputs[0],gradient.inputs[0])
gradient.color_ramp.elements[0].color=(.86,.51,.30,1);gradient.color_ramp.elements[1].color=(.12,.27,.35,1)
gradient.color_ramp.elements.new(.24).color=(.55,.55,.47,1)
sky_emit=nt.nodes.new('ShaderNodeEmission');nt.links.new(gradient.outputs[0],sky_emit.inputs['Color'])
sky_out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(sky_emit.outputs[0],sky_out.inputs[0])
box('Layered dawn sky',(43,68,110),(750,1,260),sky)
for i in range(42):
    x=8+i*.77;height=.8+.47*math.sin(i*2.1)
    rod('Far pollarded trees',(x,34,.3),(x,34,height+1.25),.053,skyline)
for x in (12.3,14.5,16.9):
    for y in (15.25,16.55):rod('Jetty timber pile',(x,y,-.19),(x,y,.68),.072,rust)
box('Old river jetty',(14.65,15.90,.58),(5.4,1.55,.18),steel,.008)
box('Receiver deck',(20,15,1.16),(5.5,4.3,.32),steel,.04)
for x in (17.8,22.2):
    for y in (13.3,16.7):rod('Tower pile',(x,y,-.12),(x,y,1.18),.115,rust,16)
for y in (13.3,16.7):rod('Diagonal bracing',(17.8,y,.04),(22.2,y,1.05),.062,steel)
append('SM_CR02_AerialDish',echo,(20,15,1.32),.0095,-107)
append('SM_CR02_SurveyLaunch',echo,(13.6,17,.03),.0075,32)
for x in (9.5,14.,18.3):
    rod('River carrier pole',(x,14,0),(x,14,3.35),.061,iron)
    rod('Ceramic cross bar',(x-.43,14,3.12),(x+.43,14,3.12),.031,steel)
for x0,x1 in ((9.5,14),(14,18.3),(18.3,21)):
    cable('Line over water',[(x0,14,3.14),((x0+x1)/2,14,2.78),(x1,14,3.14)],.009,iron)
group=cameras
illumination('Dawn across water',(15,10,13),(20,15,2),(1,.72,.43),7000,9)
illumination('Cloud bank',(22,21,9),(20,15,3),(.55,.76,.88),3200,7)

# The shared actor's -Y front faces the equipment. Hand targets track the actual prop grip.
if not args.stage_only:
    sys.path.insert(0,str(HERE))
    from elias import build_elias,pose_elias
    rig=build_elias(name='Elias')
    rig['Performance']='CH01 | carry, insert, isolate, listen, survey'
    def eval_vec(keys,f):
        for (a,p),(b,q) in zip(keys,keys[1:]):
            if f<=b:return Vector(p).lerp(Vector(q),max(0,min(1,(f-a)/(b-a))))
        return Vector(keys[-1][1])
    # Key each contact from the evaluated prop, including interpolation used by Blender.
    power_grip=lambda: tuple(power.location+handle_offset)
    def lever_grip():
        v=switch.rotation_euler.to_matrix() @ Vector((.012,.014,.175))
        return tuple(switch.location+v)
    left=[(1,(-.26,-.11,1.01)),(49,(-.27,-.13,1.03)),(91,(-.18,-.41,1.22)),(112,(-.13,-.53,1.245)),(268,(-.13,-.53,1.245)),(295,(-.17,-.41,1.16)),(360,(-.20,-.25,1.10)),(435,(-.23,-.20,1.00)),(495,(-.23,-.10,.91))]
    for f in sorted(set([1,47,87,105,138,168,176,185,198,205,214,230,249,260,271,287,315,334,367,382,404,431,462,488,505,576]+list(range(93,267,6)))):
        scene.frame_set(f)
        if f<=184:r=power_grip()
        elif f<214:r=tuple(Vector(power_grip()).lerp(Vector(lever_grip()),(f-184)/30))
        elif f<=264:r=lever_grip()
        else:r=tuple(eval_vec([(264,lever_grip()),(286,(.37,-.37,1.19)),(365,(.34,-.23,1.13)),(430,(.31,-.19,1.10)),(488,(.29,-.10,.97))],f))
        look_yaw = 0 if f<313 else -9 if f<367 else max(-35,-9-(f-367)*.26)
        pitch = -13 if f<267 else -2 if f<365 else 4
        pose_elias(rig,f,root=(0,-.035,0),yaw=0,walk=0,stride=0,look=(look_yaw,pitch),lean=4.,reach_l=tuple(eval_vec(left,f)),reach_r=r,curl=.58 if f<267 else .25)

def camera(name,start,end,eye,aim,end_eye,end_aim,lens):
    data=bpy.data.cameras.new(name);data.lens=lens;data.sensor_width=36;data.clip_start=.025;data.clip_end=200
    c=bpy.data.objects.new(name,data);group.objects.link(c)
    for frame,p,t in [(start,eye,aim),(end,end_eye,end_aim)]:
        c.location=p;c.rotation_euler=(Vector(t)-Vector(p)).to_track_quat('-Z','Y').to_euler()
        c.keyframe_insert(data_path='location',frame=frame);c.keyframe_insert(data_path='rotation_euler',frame=frame)
    mk=scene.timeline_markers.new(name,frame=start);mk.camera=c
    return c

group=cameras
first=camera('01 | Return to Relay Nine',1,96,(2.57,2.07,1.83),(.02,-.55,1.28),(1.96,1.76,1.63),(.035,-.53,1.28),39)
camera('02 | The recovered module',97,204,(1.14,.32,1.72),(.23,-.42,1.19),(1.06,.24,1.67),(.25,-.49,1.18),40)
camera('03 | Throw the isolator',205,300,(1.16,.19,1.64),(.40,-.51,1.40),(1.15,.14,1.69),(.40,-.53,1.48),38)
camera('04 | A second trace',301,402,(.75,.71,1.98),(.68,-.64,1.89),(.80,.65,2.03),(.71,-.64,1.91),43)
camera('05 | Listening',403,504,(-.85,-.415,1.66),(-.012,-.064,1.53),(-.755,-.395,1.69),(-.002,-.074,1.56),43)
camera('06 | The river aerial',505,576,(9,3.5,2.75),(18.60,15,2.49),(10.6,5.2,2.70),(19.1,15,2.50),34)
scene.camera=first;scene.frame_set(1)
for number,title in [(176,'Power unit seats'),(260,'Isolator stop'),(267,'Pilot bank wakes'),(315,'Local impulse'),(367,'Delayed return'),(431,'Elias turns toward the line')]:
    scene.timeline_markers.new(title,frame=number)
if not args.stage_only:
    scene.render.filepath = '//renders/recap/'
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'CR_Recap3D.blend'),compress=True)
if args.samples:
    for token in args.samples.split(','):
        f=int(token);scene.frame_set(f);scene.render.filepath=str(OUT.parent/f'recap-review-{f:04d}.jpg')
        bpy.ops.render.render(write_still=True)
if args.render:
    if args.shot_render:
        cuts=((1,96),(97,204),(205,300),(301,402),(403,504),(505,576))
        scene.frame_start,scene.frame_end=cuts[args.shot_render-1]
    render_dir=args.output_dir or OUT;render_dir.mkdir(parents=True,exist_ok=True)
    scene.render.filepath=str(render_dir)+'/'
    bpy.ops.render.render(animation=True)
