"""Small exterior/aim-reference addition to Phase05 derivative, retaining its animation keys."""
import bpy,argparse,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True);out=Path(ap.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir)
src=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(src/'CR05_RookRestoration.blend'));bpy.context.preferences.filepaths.save_version=0
rig=bpy.data.objects['CR05_RestorationRig'];skin=bpy.data.objects['SK_CR05_Restoration'];rook=bpy.data.objects.get('SM_CR05_Rook5') or bpy.data.objects['SM_CR03_Rook5'];optic=bpy.data.objects.get('SM_CR05_SurveyOptic') or bpy.data.objects['SM_CR03_SurveyOptic']
if not rook.get('phase05_iron_sights'):
 for name,loc,size in [('RearLeft',(-5,-2.6,9),(3,.8,4)),('RearRight',(-5,2.6,9),(3,.8,4)),('FrontPost',(34,0,9.5),(1.2,.9,1))]:
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='CR05_'+name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);m=o.modifiers.new('Rounded sight','BEVEL');m.width=.16;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name);o.data.materials.append(bpy.data.materials['CR03_Amber'])
  copy=o.copy();copy.data=o.data.copy();bpy.context.scene.collection.objects.link(copy);g=copy.vertex_groups.new(name='weapon');g.add(list(range(len(copy.data.vertices))),1,'REPLACE')
  bpy.ops.object.select_all(action='DESELECT');copy.select_set(True);skin.hide_set(False);skin.select_set(True);bpy.context.view_layer.objects.active=skin;bpy.ops.object.join()
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);rook.hide_set(False);rook.select_set(True);bpy.context.view_layer.objects.active=rook;bpy.ops.object.join()
 rook['phase05_iron_sights']=True
rook.name='SM_CR05_Rook5';optic.name='SM_CR05_SurveyOptic'
for o in (rook,optic):
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='SurfaceUV')
 for face in o.data.polygons:
  axes=((1,2),(0,2),(0,1))[max(range(3),key=lambda i:abs(face.normal[i]))]
  for li in face.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/80,v[axes[1]]/80)
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(out/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
 o.hide_set(True);o.hide_render=True
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);skin.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(out/'SK_CR05_Restoration.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0)
bpy.ops.wm.save_as_mainfile(filepath=str(src/'CR05_RookRestoration.blend'));print('CR05_ROOK_EXTERIOR_PASS')
