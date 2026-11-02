"""Original Phase06 chapter kit, centimeters. Does not run or modify older generators."""
import bpy, json, sys, argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--export-dir',required=True)
out=Path(p.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir);out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
mats={};parts=[];manifest=[]
for key,color in {'Steel':(.2,.24,.25),'Paint':(.13,.205,.215),'Dark':(.045,.052,.05),'Amber':(.42,.26,.07),'Pale':(.42,.43,.35)}.items():
    m=bpy.data.materials.new('CR06_'+key);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.6;mats[key]=m
def box(name,loc,size,mat='Steel',bevel=.8):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[mat])
    if bevel:
        b=o.modifiers.new('Manufactured edges','BEVEL');b.width=bevel;b.segments=2;bpy.ops.object.modifier_apply(modifier=b.name)
    parts.append(o);return o
def finish(name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='SM_CR06_'+name
    scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    uv=o.data.uv_layers.active or o.data.uv_layers.new(name='SurfaceUV')
    for face in o.data.polygons:
        axes=((1,2),(0,2),(0,1))[max(range(3),key=lambda i:abs(face.normal[i]))]
        for li in face.loop_indices:
            v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/110,v[axes[1]]/110)
    bpy.ops.export_scene.fbx(filepath=str(out/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False,mesh_smooth_type='FACE')
    o.data.calc_loop_triangles();manifest.append(dict(name=o.name,dimensions_cm=list(o.dimensions),triangles=len(o.data.loop_triangles)))
    o['authorship']='Original Cinder Relay Phase06';o.hide_set(True);parts.clear()

# Centered door leaves; native roller gathers into its header, isolation plate retracts below.
for i in range(18):
    z=-165+i*19.4
    box('Folded roller slat',(0,0,z),(14,354,18.3),'Paint')
    for x in (-8,8):box('Slat seam',(x,0,z+7),(2,354,2),'Steel',.25)
box('Lower seal',(0,0,-173),(18,358,6),'Dark')
for y in(-145,145):box('Lift reinforcement',(-10,y,0),(5,12,336),'Steel')
finish('RollerShutter')

box('Isolation plate',(0,0,0),(24,356,348),'Paint',2)
for x in(-15,15):
    for z in(-135,0,135):box('Structural rib',(x,0,z),(9,350,15),'Steel')
    for y in(-155,155):box('Vertical brace',(x,y,0),(9,18,335),'Steel')
    box('Maintenance band',(x*1.35,0,-97),(2,300,14),'Amber',.2)
    for y in(-130,-65,0,65,130):box('Band interruption',(x*1.45,y,-97),(2,14,14),'Dark',.1)
finish('IsolationDoor')

for y in(-195,195):
    box('Guide rail',(0,y,175),(45,26,350),'Steel')
    box('Dark track',(-25,y,175),(4,10,330),'Dark')
box('Roll housing',(0,0,395),(90,435,85),'Paint',3)
for y in(-215,215):box('Housing end cap',(0,y,395),(96,8,91),'Steel')
for x in(-48,48):box('Housing hazard band',(x,0,385),(2,370,15),'Amber')
finish('DoorFrame')

# Mechanic's physical panel, front +X; display is native editable TextRender.
box('Control cabinet',(0,0,0),(25,65,86),'Paint',2)
box('Faceplate',(14,0,0),(5,58,78),'Steel')
box('Readout recess',(17,0,16),(3,44,27),'Dark')
box('Selector bezel',(18,-16,-22),(5,17,17),'Dark')
box('Selector handle',(23,-16,-22),(12,5,18),'Amber')
box('Confirm pad',(20,16,-22),(6,17,13),'Pale')
finish('DiagnosticPanel')

# Industrial shuttle remains visibly mechanical; no electrical hazards or damage simulation.
box('Shuttle body',(0,0,0),(45,600,300),'Paint',2)
for y in(-275,-140,0,140,275):box('Shuttle vertical support',(-26,y,0),(10,13,290),'Steel')
for z in(-120,120):box('Shuttle warning band',(-32,0,z),(3,590,16),'Amber')
finish('AccessShuttle')

for o in scene.objects:o.hide_set(False)
bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).parent/'CR06_ChapterMechanics.blend'))
(out/'chapter-kit.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('CR06_KIT',sum(i['triangles'] for i in manifest),len(manifest))
