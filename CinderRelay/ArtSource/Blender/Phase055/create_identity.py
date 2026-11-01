"""Original CINDER RELAY key-art stage. Creates only the Phase055 derivative.

Meters, deterministic seed, real Blender/Cycles rendering. No external photograph,
game screenshot, generated raster or paid provider. Old project kits are appended
read-only and packed into this independently editable stage.
"""
import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SRC = Path(__file__).resolve().parent
ROOT = SRC.parents[2]
OUT = ROOT / 'ArtSource' / 'Interface' / 'Phase055'
OUT.mkdir(parents=True, exist_ok=True)
LOG = ROOT.parent / '.environment-local' / 'phase-05-5' / 'art'
LOG.mkdir(parents=True, exist_ok=True)
ap = argparse.ArgumentParser()
ap.add_argument('--preview', action='store_true')
ap.add_argument('--render-only', action='store_true')
ap.add_argument('--portrait-only', action='store_true')
args = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
rng = random.Random(55091)

def material(name, color, metallic=0, rough=.7, variation=.2, emission=0):
    m = bpy.data.materials.new('CR055_' + name)
    m.use_nodes = True
    m.diffuse_color = (*color, 1)
    n = m.node_tree.nodes
    bs = n.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = rough
    if emission:
        bs.inputs['Emission Color'].default_value = (*color, 1)
        bs.inputs['Emission Strength'].default_value = emission
    elif variation:
        tex = n.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 4.2
        tex.inputs['Detail'].default_value = 4
        tex.inputs['Roughness'].default_value = .72
        coords=n.new('ShaderNodeTexCoord')
        m.node_tree.links.new(coords.outputs['Object'],tex.inputs['Vector'])
        ramp = n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .25
        ramp.color_ramp.elements[0].color = tuple(c * (1-variation) for c in color) + (1,)
        ramp.color_ramp.elements[1].position = .75
        ramp.color_ramp.elements[1].color = tuple(c * (1+variation) for c in color) + (1,)
        m.node_tree.links.new(tex.outputs['Fac'], ramp.inputs[0])
        m.node_tree.links.new(ramp.outputs['Color'], bs.inputs['Base Color'])
        bump = n.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .22
        bump.inputs['Distance'].default_value = .055
        m.node_tree.links.new(tex.outputs['Fac'], bump.inputs['Height'])
        m.node_tree.links.new(bump.outputs['Normal'], bs.inputs['Normal'])
    return m

def cube(name, pos, size, mat, bevel=0):
    x,y,z=(a*.5 for a in size)
    d=bpy.data.meshes.new(name)
    d.from_pydata([(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)],[],[(2,6,4,0),(5,7,3,1),(4,5,1,0),(3,7,6,2),(1,3,2,0),(6,7,5,4)])
    d.update();o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o);o.location=pos
    if mat: o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Edge softness', 'BEVEL'); b.width=bevel; b.segments=2
        o.modifiers.new('Weighted edge normals', 'WEIGHTED_NORMAL')
    return o

def beam(name, a, b, width, depth, mat):
    a,b=Vector(a),Vector(b)
    o=cube(name,(a+b)/2,(width,depth,(b-a).length),mat,.015)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    return o

def cylinder(name,pos,radius,depth,mat,axis='Z',vertices=24):
    vs=[(radius*math.cos(i*math.tau/vertices),radius*math.sin(i*math.tau/vertices),z) for z in(-depth/2,depth/2) for i in range(vertices)]
    fs=[tuple(reversed(range(vertices))),tuple(range(vertices,vertices*2))]+[(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
    o=mesh(name,vs,fs,mat);o.location=pos
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    elif axis=='X':o.rotation_euler[1]=math.pi/2
    for p in o.data.polygons:p.use_smooth=True
    b=o.modifiers.new('Rounded edge','BEVEL');b.width=min(radius*.08,.035);b.segments=2
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def mesh(name,vs,fs,mat):
    d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update()
    o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat);return o

def cable(name,pts,rad,mat):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=16
    c.bevel_depth=rad;c.bevel_resolution=2
    s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);return o

def area(name,pos,target,color,energy,size,size_y=None):
    d=bpy.data.lights.new(name,'AREA');d.color=color;d.energy=energy;d.shape='DISK';d.size=size
    if size_y: d.shape='RECTANGLE';d.size_y=size_y
    o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o);o.location=pos
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o

def point(name,pos,color,power,radius=.2):
    d=bpy.data.lights.new(name,'POINT');d.energy=power;d.color=color;d.shadow_soft_size=radius
    o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o);o.location=pos;return o

def text_obj(name,text,pos,size,mat):
    c=bpy.data.curves.new(name,'FONT');c.body=text;c.size=size;c.align_x='CENTER';c.extrude=.004
    c.font=bpy.data.fonts.load(str(OUT/'Fonts'/'BarlowCondensed-SemiBold.ttf'))
    o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.location=pos
    o.rotation_euler=(math.pi/2,0,0);o.data.materials.append(mat);return o

def append_kit(names):
    old=SRC.parent/'Phase052'/'CR052_YardDetail.blend'
    with bpy.data.libraries.load(str(old),link=False) as (a,b):b.objects=[n for n in a.objects if n in names]
    result={}
    for o in b.objects:
        if o:
            bpy.context.scene.collection.objects.link(o);o.hide_set(False);o.hide_render=False
            o.scale=(.01,.01,.01);o['source']='Original project Phase052 read-only append'
            result[o.name]=o
    return result

def build():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.context.preferences.filepaths.save_version=0
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    steel=material('Wet charcoal steel',(.085,.105,.11),.75,.32,.42)
    rust=material('Oxidized iron',(.20,.105,.055),.55,.59,.65)
    pale=material('Worn chalk enamel',(.36,.37,.32),.18,.65,.5)
    wood=material('Rail tie timber',(.08,.069,.052),0,.92,.65)
    brick=material('Station blockwork',(.21,.205,.18),0,.94,.62)
    concrete=material('Wet service apron',(.065,.079,.075),.12,.64,.65)
    dark=material('Deep shadow',(.015,.021,.023),.15,.65,.25)
    rail=material('Polished rail crown',(.19,.23,.24),.92,.24,.2)
    gravel=material('Rail ballast',(.095,.104,.095),0,.89,.6)
    glass=material('Window reflection',(.08,.14,.15),.8,.12,.15)
    amber=material('Maintenance amber',(.88,.38,.10),0,.28,0,3)
    cyan=material('Distant carrier cyan',(.17,.54,.53),0,.25,0,4)
    ochre=material('Old safety enamel',(.36,.22,.08),.3,.65,.45)
    puddle=material('Shallow rainwater',(.055,.08,.085),.52,.1,.08)
    grass=material('Spent olive grass',(.095,.11,.069),0,.9,.4)

    # Wide wet base and two hand-laid rail routes; a curve is implied by the sleeper drift.
    cube('Entire service ground',(0,32,-.35),(200,220,.6),concrete)
    for track_x in (1.0,8.0):
        cube('Raised ballast bed',(track_x,26,-.09),(3.6,150,.25),gravel,.1)
        for j in range(99):
            y=-43+j*1.35
            tie=cube('Rail sleeper %d'%j,(track_x+rng.uniform(-.04,.04),y,.055),(2.9,.24,.16),wood,.035)
            tie.rotation_euler[2]=rng.uniform(-.025,.025)
        for side in (-.79,.79):
            cube('Rail foot',(track_x+side,26,.19),(.22,150,.08),rust,.015)
            cube('Rail web',(track_x+side,26,.265),(.07,150,.15),rust,.01)
            cube('Rail head',(track_x+side,26,.36),(.13,150,.08),rail,.025)
        for j in range(20):
            y=-26+j*3.5
            for side in (-.79,.79):
                cube('Tie chair',(track_x+side,y,.16),(.33,.32,.06),steel,.015)
    # Shared low-poly ballast instances; intentional form detail limited to foreground.
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1)
    stone=bpy.context.object;stone.name='Ballast master';stone.data.materials.append(gravel)
    for i in range(1450):
        o=stone if i==0 else bpy.data.objects.new('Ballast aggregate',stone.data)
        if i:bpy.context.scene.collection.objects.link(o)
        lane=rng.choice((1.,8.));o.location=(lane+rng.uniform(-1.75,1.75),rng.uniform(-24,42),.075)
        o.scale=(rng.uniform(.05,.14),rng.uniform(.06,.16),rng.uniform(.04,.1));o.rotation_euler=(rng.random()*2,rng.random(),rng.random()*6)
    for i in range(300):
        o=bpy.data.objects.new('Scattered apron rubble',stone.data);bpy.context.scene.collection.objects.link(o)
        o.location=(rng.uniform(-15,21),rng.uniform(-25,35),-.02)
        o.scale=(rng.uniform(.05,.28),rng.uniform(.06,.30),rng.uniform(.025,.09));o.rotation_euler=(rng.random()*2,rng.random(),rng.random()*6)
    for i in range(40):
        x,y=rng.uniform(-16,18),rng.uniform(-32,30);rx,ry=rng.uniform(.5,2.5),rng.uniform(.4,1.2)
        vs=[(x+math.cos(t*math.tau/16)*rx*rng.uniform(.8,1.1),y+math.sin(t*math.tau/16)*ry*rng.uniform(.8,1.1),-.043) for t in range(16)]
        mesh('Broken rainwater patch',vs,[tuple(range(16))],puddle)
    for i in range(80):
        x=rng.uniform(-15,20);y=rng.uniform(-25,29)
        if .1<x<2 or 7<x<9:continue
        vs=[];fs=[]
        for j in range(5):
            a=rng.random()*math.tau;h=rng.uniform(.16,.55);base=len(vs)
            vs += [(x-.025,y,-.04),(x+.025,y,-.04),(x+.1*math.cos(a),y+.1*math.sin(a),h)]
            fs.append((base,base+1,base+2))
        mesh('Crack-rooted weed',vs,fs,grass)

    # Relay Nine: a long industrial shed with genuinely missing roof bays and open glazing.
    cube('Station foundation',(14,35,.3),(19,22,.6),brick,.08)
    cube('Station right wall',(23.1,35,3.65),(.5,22,6.5),brick,.035)
    cube('Station back wall',(14,45.8,3.5),(18.5,.5,6.2),brick,.035)
    # Broken front wall piers preserve a wide warm workshop entrance.
    for x,w in [(5.5,1.2),(10.5,1.1),(19.7,2.0),(22.6,1.0)]:
        cube('Front masonry pier',(x,24.2,3.25),(w,.6,5.9),brick,.04)
    cube('Station doorway lintel',(15.5,24.2,5.8),(8.8,.7,.65),brick,.025)
    cube('Window sill left',(8,24,1.65),(4.2,.8,.35),pale,.025)
    cube('Window head left',(8,24,5.3),(4.2,.7,.4),brick,.025)
    for x in (6.2,7.3,8.4,9.6):beam('Broken window mullion',(x,23.85,1.8),(x,23.85,5.15),.065,.12,steel)
    for z in (2.6,3.5,4.4):beam('Window transom',(6,23.85,z),(10,23.85,z),.06,.1,steel)
    for x,z in [(6.2,2.8),(7.3,3.7),(8.4,4.5)]:
        mesh('Broken pane',[(x,23.82,z),(x+.9,23.82,z),(x+.4,23.82,z+.65)],[(0,1,2)],glass)
    for y in (24.3,29,34,39,44.8):
        for x in (5,23):beam('Roof support column',(x,y,.7),(x,y,6.2),.22,.22,steel)
        beam('Gable left chord',(5,y,6.25),(14,y,9.15),.22,.18,steel)
        beam('Gable right chord',(14,y,9.15),(23,y,6.25),.22,.18,steel)
        beam('Gable tie',(5,y,6.2),(23,y,6.2),.17,.17,steel)
        for x in (7.4,10.2,14,17.8,20.6):
            top=9.15-abs(x-14)*2.9/9
            beam('Truss vertical',(x,y,6.2),(x,y,top),.11,.11,rust)
        beam('Truss left diagonal',(5,y,6.2),(10.2,y,7.92),.12,.12,rust)
        beam('Truss right diagonal',(23,y,6.2),(17.8,y,7.92),.12,.12,rust)
    # Corroded roof segments, many missing in the front bay so the trusses silhouette.
    for side in (-1,1):
        for ix in range(8):
            x=14+side*(ix+0.5)*1.12
            for iy in range(4):
                if (iy==0 and ix in (0,1,3,4,5)) or (iy==1 and ix in (1,4)):continue
                y=26.7+iy*5.05;z=9.15-abs(x-14)*2.9/9
                o=cube('Corrugated roof panel',(x,y,z),(1.16,4.98,.055),rust if rng.random()<.4 else steel)
                o.rotation_euler[1]=side*math.atan(2.9/9)
                # Formed standing seam ribs, visible against the sky.
                for dx in (-.36,0,.36):
                    beam('Roof standing rib',(x+dx,y-2.45,z+side*(-dx)*.32+.04),(x+dx,y+2.45,z+side*(-dx)*.32+.04),.035,.045,steel)
    beam('Bent roof edge',(5,24,6.2),(9,23.2,5.6),.22,.19,rust)
    # Wall courses, cracks and purposeful surface remnants.
    for z in (1.1,1.8,2.5,3.2,3.9,4.6,5.3):
        cube('Masonry horizontal mortar',(23.37,35,z),(.015,21.5,.025),dark)
    for k in range(15):
        y=25+k*1.3;z=rng.choice((1.4,2.1,2.8,3.5,4.2,4.9))
        cube('Masonry vertical mortar',(23.38,y,z),(.015,.025,.65),dark)
    cube('Relay Nine sign back',(15.1,23.68,6.12),(7.0,.17,1.15),dark,.06)
    cube('Sign amber inset',(11.95,23.56,6.15),(.1,.02,.8),ochre)
    text_obj('Editable station label','RELAY NINE',(15.15,23.54,5.86),.81,pale)
    # Warm practical lamp, doorway spill and a faint rear carrier display.
    cube('Lamp bracket',(16.4,23.6,5.1),(1.2,.65,.12),steel,.035)
    cube('Maintenance luminaire',(16.4,23.5,5.0),(.82,.23,.13),amber,.02)
    area('Warm maintenance doorway',(16.3,25,4.5),(14,16,1), (1,.48,.19),1400,4,3)
    point('Task lamp halo',(16.4,23.2,4.9),(1,.44,.13),150,.35)
    cube('Back carrier slit',(13,45.46,3.5),(2.5,.04,.08),cyan)
    point('Back carrier illumination',(13,44,3.5),(.2,.65,.7),130,.55)
    # Interior shelves and gantry remain restrained behind the dark doorway.
    for x in (12,19):
        for z in (.9,2.1,3.3):cube('Workshop shelving',(x,31,z),(2.7,.7,.1),steel,.025)
        for dx in (-1.35,1.35):beam('Shelf upright',(x+dx,31,.6),(x+dx,31,4.1),.08,.08,steel)
    cylinder('Industrial upright tank',(20.4,35,2.2),1.0,3.5,steel)
    cable('Overhead drooping cable',[(5,24,6),(9,25,5.2),(13,26,5.6),(20,27,6)],.035,dark)

    # Original earlier project kit, correctly rescaled from centimeters into stage meters.
    kit=append_kit(['SM_CR052_CableSpool','SM_CR052_MaintenanceTrolley','SM_CR052_ScrapStack','SM_CR052_ServiceCrate'])
    placements={'SM_CR052_RailServiceCar':((-7,15,.2),math.pi/2),
                'SM_CR052_CableSpool':((5.8,-15,.1),.3),
                'SM_CR052_MaintenanceTrolley':((20.1,20.7,.65),1.8),
                'SM_CR052_ScrapStack':((3.8,-19,.12),.1),
                'SM_CR052_ServiceCrate':((5.1,16.5,.22),-.4)}
    for name,o in kit.items():o.location=placements[name][0];o.rotation_euler[2]=placements[name][1]

    # Distinctive damaged mechanical signal in foreground, entirely original geometry.
    sx,sy=6.4,-3.0
    cube('Signal concrete footing',(sx,sy,.25),(1.2,1.1,.5),brick,.08)
    cylinder('Signal pole',(sx,sy,2.6),.13,4.8,steel)
    cube('Signal control cabinet',(sx+.4,sy,.95),(.55,.55,1.15),ochre,.04)
    for z in (.65,.75,.85):cube('Cabinet vent',(sx+.4,sy-.285,z),(.35,.015,.035),dark)
    # Bent head, missing protective panel, two opaque lenses and one small live indicator.
    cube('Signal head shell',(sx-.17,sy,4.8),(.85,.45,1.7),steel,.13)
    for z in (4.35,4.88,5.4):
        cylinder('Signal hood ring',(sx-.17,sy-.29,z),.285,.28,rust,'Y')
        cylinder('Signal glass',(sx-.17,sy-.45,z),.23,.025,amber if z==4.35 else dark,'Y')
        cube('Signal hood visor',(sx-.17,sy-.5,z+.26),(.64,.55,.05),steel,.025)
    # Lighting is small and purposeful, not a glowing screen-wide motif.
    point('Signal low maintenance light',(sx-.17,sy-.65,4.35),(1,.37,.1),38,.12)
    beam('Broken signal support',(sx,sy,3.9),(sx+.75,sy-.4,4.3),.08,.08,rust)
    cable('Disconnected service cable',[(sx+.4,sy,1.8),(sx+.95,sy-.3,1),(sx+1.2,sy-1,.18),(sx+2.2,sy-1.4,.14)],.045,dark)
    for x,y in [(4,-10),(3,-17),(8,-12)]:
        o=cube('Detached sheet debris',(x,y,.12),(rng.uniform(.6,1.6),rng.uniform(.6,2),.05),rust,.01);o.rotation_euler[2]=rng.random()*3

    # Left edge holds dark negative space; silhouettes only, no distracting text or lamps.
    for x,y,z in [(-16,-3,6),(-14,14,5.5),(-16,29,5)]:
        beam('Unpowered yard pole',(x,y,0),(x,y,z),.16,.16,dark)
        beam('Cross arm',(x-1.3,y,z-.4),(x+1.3,y,z-.4),.12,.12,dark)
    cable('Abandoned overhead wire',[(-16,-3,5.7),(-15,6,4.8),(-14,14,5.2),(-15,21,4.4),(-16,29,4.7)],.022,dark)
    # Skyline: old blocks and functional towers in several fog layers.
    for i in range(20):
        x=-55+i*6.4+rng.uniform(-1,1);y=rng.uniform(100,150);h=rng.uniform(12,30)
        cube('Fog city building',(x,y,h/2),(rng.uniform(3,7),rng.uniform(5,9),h),brick,.08)
        if i%3==0:
            cube('Rooftop plant',(x,y,h+1),(2.5,2,2),steel,.03)
        if i%2==0:
            for z in range(3,int(h)-1,3):
                for dx in (-1,0,1):cube('Distant dead window',(x+dx,y-4.55,z),(.45,.025,.7),dark)
    for x,y,h in [(31,65,24),(43,81,31),(-24,86,26)]:
        cylinder('Exhaust tower',(x,y,h/2),.75,h,steel,vertices=16)
        for z in range(3,int(h),4):cylinder('Tower seam',(x,y,z),.82,.15,rust,vertices=16)
    for z in (4,10,16,22):
        beam('Carrier mast crossbar',(35,61,z),(39,61,z),.12,.12,steel)
    for x in (35,39):beam('Carrier mast upright',(x,61,0),(37,61,26),.18,.18,steel)
    for z in range(0,22,4):
        beam('Carrier mast diagonal',(35,61,z),(39-(z/26)*2,61,z+4),.08,.08,rust)
    cylinder('Carrier lamp',(37,61,26),.18,.22,cyan)
    point('Distant carrier beacon',(37,60.8,26),(.2,.8,.8),40,.3)

    # Fog layered through physical volume. Low density leaves foreground readable.
    fog=bpy.data.materials.new('CR055_Depth haze');fog.use_nodes=True
    fog.node_tree.nodes.clear();v=fog.node_tree.nodes.new('ShaderNodeVolumePrincipled')
    v.inputs['Density'].default_value=.012;v.inputs['Color'].default_value=(.43,.50,.52,1);v.inputs['Anisotropy'].default_value=.15
    out=fog.node_tree.nodes.new('ShaderNodeOutputMaterial');fog.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume'])
    cube('Atmospheric depth',(0,110,32),(240,220,66),fog)
    world=bpy.data.worlds.new('CR055 Overcast blue hour');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.18,.21,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.4;scene.world=world
    area('Cold open sky',(5,5,35),(8,20,0),(.48,.62,.7),6000,45)
    area('Foreground reflected sky',(-4,-30,13),(8,8,0),(.47,.6,.68),2000,24)
    area('Roof rim',(5,48,24),(14,29,5),(.52,.66,.72),6000,24)

    camd=bpy.data.cameras.new('CR055_LandscapeLens');cam=bpy.data.objects.new('CR055_LandscapeCamera',camd);scene.collection.objects.link(cam)
    cam.location=(-16.5,-36,5.2);cam.rotation_euler=(Vector((6.8,29,6.7))-cam.location).to_track_quat('-Z','Y').to_euler()
    camd.lens=42;camd.clip_end=350;camd.dof.use_dof=False;scene.camera=cam
    portrait_data=camd.copy();portrait_data.name='CR055_PortraitLens';portrait_data.lens=34
    portrait=bpy.data.objects.new('CR055_PortraitCamera',portrait_data);scene.collection.objects.link(portrait)
    portrait.location=(-9,-35,5.0);portrait.rotation_euler=(Vector((11,28,7.0))-portrait.location).to_track_quat('-Z','Y').to_euler()
    scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=True
    scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3;scene.cycles.volume_bounces=1
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
    scene.render.resolution_percentage=100;scene.render.film_transparent=False
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.1
    scene.use_nodes=True;n=scene.node_tree.nodes;n.clear()
    layer=n.new('CompositorNodeRLayers');glare=n.new('CompositorNodeGlare');glare.glare_type='FOG_GLOW';glare.quality='HIGH';glare.threshold=1.4
    comp=n.new('CompositorNodeComposite');scene.node_tree.links.new(layer.outputs['Image'],glare.inputs['Image']);scene.node_tree.links.new(glare.outputs['Image'],comp.inputs['Image'])
    scene['brief']='THE LAST SIGNAL: rail approach, damaged signaling fixture, Relay Nine, warm maintenance light, fog skyline and restrained carrier cyan. Promotional environment interpretation; no new story facts.'
    scene['source_policy']='Original Blender geometry plus read-only appended original Phase052 meshes. Procedural materials only. No external image textures.'
    scene.render.resolution_x=2560;scene.render.resolution_y=1440
    # Font is packed for self-contained editable station signage; its license is retained externally.
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'CR055_TheLastSignal.blend'))

def render():
    scene=bpy.context.scene
    try:
        pref=bpy.context.preferences.addons['cycles'].preferences
        pref.compute_device_type='OPTIX';pref.get_devices()
        for device in pref.devices:device.use=device.type!='CPU'
        if any(d.use for d in pref.devices):scene.cycles.device='GPU'
    except Exception as error:print('CR055_GPU_FALLBACK',str(error))
    files=[]
    if not args.portrait_only:
        scene.render.resolution_x=1280 if args.preview else 2560
        scene.render.resolution_y=720 if args.preview else 1440
        scene.cycles.samples=24 if args.preview else 96
        target=LOG/'keyart-preview.png' if args.preview else OUT/'CR055_KeyArt_Landscape.png'
        scene.render.filepath=str(target);bpy.ops.render.render(write_still=True);files.append(target)
        if not args.preview:
            im=bpy.data.images.load(str(target),check_existing=False);im.scale(1920,1080)
            im.filepath_raw=str(OUT/'CR055_MenuBackground.png');im.file_format='PNG';im.save();files.append(Path(im.filepath_raw))
    if not args.preview:
        scene.camera=bpy.data.objects['CR055_PortraitCamera']
        scene.render.resolution_x=1600;scene.render.resolution_y=2400;scene.cycles.samples=96
        target=OUT/'CR055_KeyArt_Portrait.png';scene.render.filepath=str(target)
        bpy.ops.render.render(write_still=True);files.append(target)
    data={'blender':bpy.app.version_string,'renderer':'Cycles / OptiX if available','seed':55091,'samples':scene.cycles.samples,'source':str(SRC/'CR055_TheLastSignal.blend'),'original_author':'Cinder Relay project / Phase055 authoring','files':[]}
    for p in files:data['files'].append({'path':str(p.relative_to(ROOT.parent)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
    (LOG/('preview-render.json' if args.preview else 'render-result.json')).write_text(json.dumps(data,indent=2),encoding='utf-8')

if not args.render_only:build()
render()
