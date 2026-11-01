"""Targeted additions to the original environment kit; does not regenerate its railcars."""
import bpy,ast,json,math,argparse,sys
from pathlib import Path
from mathutils import Vector
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True);out=Path(ap.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir);src=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(src/'CR05_IndustrialKit.blend'));bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;manifest=json.loads((out/'environment-manifest.json').read_text());mats={};parts=[];kit=[]
for k,(color,metal,rough) in manifest['palette'].items():
 m=bpy.data.materials.get('CR05_'+k)
 if not m:
  m=bpy.data.materials.new('CR05_'+k);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 mats[k]=m
tree=ast.parse((src/'create_environment.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'Environment geometry helpers','exec'))
for obj in scene.objects:obj.hide_set(True)
if 'SM_CR05_PowerUnit' not in bpy.data.objects:
 box('PowerHousing',(0,0,0),(80,86,86),'Steel',5)
 for y in(-44,44):
  for x in(-28,-14,0,14,28):box('HeatSink',(x,y,0),(5,8,80),'Dark',1)
 for x in(-34,34):box('CornerProtection',(x,0,0),(12,95,96),'Rust',2)
 tube('CarryHandle',[(-19,-25,44),(-19,-25,57),(-19,25,57),(-19,25,44)],4,'Dark')
 box('Readout',(-42,0,12),(2,49,24),'Glass',1)
 for y in(-15,0,15):box('ChargeLamp',(-44,y,12),(1,5,15),'Cyan',.4)
 finish('PowerUnit')
if 'SM_CR05_RelayTerminal' not in bpy.data.objects:
 box('TerminalBody',(0,0,0),(88,96,100),'Paint',4)
 box('RecessedFace',(-45,0,4),(6,86,87),'Dark',2)
 box('ScreenFrame',(-50,0,17),(8,75,48),'Steel',2)
 box('ScreenGlass',(-55,0,18),(2,63,35),'Glass',1)
 for z in(9,17,25):box('ScreenGlyph',(-56,-5,z),(1,42 if z!=17 else 28,1.5),'Cyan',.2)
 box('KeyboardTray',(-58,0,-29),(28,82,7),'Steel',2)
 for y in range(-28,30,8):
  for x in(-62,-54):box('Key',(x,y,-24),(5,5,3),'Dark',.5)
 for y in(-34,34):cyl('Dial',(-52,y,-6),5,6,'Amber','X',12)
 for y in(-40,40):tube('Guard',[(-51,y,-42),(-67,y,-42),(-67,y,37),(-51,y,37)],2,'Rust')
 finish('RelayTerminal')
names={m['name'] for m in kit};manifest['meshes']=[m for m in manifest['meshes'] if m['name'] not in names]+kit
(out/'environment-manifest.json').write_text(json.dumps(manifest,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(src/'CR05_IndustrialKit.blend'));print('CR05_TERMINAL_SOURCE_PASS',names)
