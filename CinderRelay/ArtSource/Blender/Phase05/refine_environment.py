"""Targeted05A correction: rail roof winding + one structural gantry. Preserve other meshes."""
import ast,bpy,bmesh,json,sys,argparse,math
from pathlib import Path
from mathutils import Vector
parser=argparse.ArgumentParser();parser.add_argument('--export-dir',required=True);opt=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
src=Path(__file__).resolve().parent;out=Path(opt.export_dir);scene=bpy.context.scene
assert Path(bpy.data.filepath)==src/'CR05_IndustrialKit.blend'
bpy.context.preferences.filepaths.save_version=0
rail=bpy.data.objects['SM_CR05_RailServiceCar'];bm=bmesh.new();bm.from_mesh(rail.data)
faces=[f for f in bm.faces if len(f.verts)==4 and min(v.co.z for v in f.verts)>=379.9 and abs(max(v.co.x for v in f.verts)-min(v.co.x for v in f.verts)-926)<.01 and f.normal.z<0]
assert len(faces) in (0,12),len(faces)
bmesh.ops.reverse_faces(bm,faces=faces);bm.to_mesh(rail.data);bm.free()
def export(o):
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(out/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE')
export(rail)
parts=[];kit=[];mats={n.removeprefix('CR05_'):m for n,m in bpy.data.materials.items()}
tree=ast.parse((src/'create_environment.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'geometry-helpers','exec'),globals())
if 'SM_CR05_Gantry' not in bpy.data.objects:
 for z in(0,90):beam('TrussChord',(0,-1370,z),(0,1370,z),14,16,'Steel')
 for i in range(14):
  y=-1370+i*2740/14;beam('Diagonal',(0,y,0),(0,y+2740/14,90),7,7,'Rust')
  if i%2==0:beam('CrossVertical',(0,y,0),(0,y,90),7,7,'Steel')
 tube('SuspendedCable',[(20,y,10-26*math.sin((y+1370)/2740*math.pi)) for y in range(-1370,1371,137)],2.5,'Dark')
 finish('Gantry')
 manifest=json.loads((out/'environment-manifest.json').read_text());manifest['meshes']+=kit
 (out/'environment-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(src/'CR05_IndustrialKit.blend'))
print('CR05_ENVIRONMENT_REFINED roof_faces=',len(faces),'new_meshes=',[m['name'] for m in kit])
