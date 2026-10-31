"""Bounded source correction: open optic aperture and re-key existing rig; preserve other geometry."""
import bpy,bmesh,sys,argparse,json
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--export-dir',required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(__file__).resolve().parent;out=Path(args.export_dir);out.mkdir(parents=True,exist_ok=True)
assert Path(bpy.data.filepath)==source/'CR03_RookRestoration.blend'
rig=bpy.data.objects['CR03_RestorationRig'];skin=bpy.data.objects['SK_CR03_Restoration'];old=bpy.data.objects['SM_CR03_SurveyOptic']
idx=skin.vertex_groups['optic'].index;remove=[v.index for v in skin.data.vertices if any(g.group==idx and g.weight>.99 for g in v.groups)]
bm=bmesh.new();bm.from_mesh(skin.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in remove],context='VERTS');bm.to_mesh(skin.data);bm.free()
bpy.data.objects.remove(old,do_unlink=True)
parts=[]
for n,p,s,m in [('Foot',(-3,0,8),(9,6,2),'Amber'),('Left',(-3,-3,12),(10,.8,6),'Graphite'),('Right',(-3,3,12),(10,.8,6),'Graphite'),('Top',(-3,0,15),(10,6.8,.8),'Graphite'),('Bottom',(-3,0,9),(10,6.8,.8),'Graphite'),('IndicatorFront',(2.1,0,14.5),(.25,4.7,.3),'Lens'),('IndicatorRear',(-8.1,0,14.5),(.25,4.7,.3),'Lens'),('Selector',(-3,-3.8,12),(3,1,2.5),'Amber')]:
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name='Survey_'+n;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    mod=o.modifiers.new('Machined edge radius','BEVEL');mod.width=.25;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);o.data.materials.append(bpy.data.materials['CR03_'+m]);parts.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();optic=bpy.context.object;optic.name='SM_CR03_SurveyOptic';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(out/'SM_CR03_SurveyOptic.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE')
copy=optic.copy();copy.data=optic.data.copy();bpy.context.scene.collection.objects.link(copy);g=copy.vertex_groups.new(name='optic');g.add(list(range(len(copy.data.vertices))),1,'REPLACE')
bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);copy.select_set(True);bpy.context.view_layer.objects.active=skin;bpy.ops.object.join()
optic.hide_set(True);optic.hide_render=True
sys.path.insert(0,str(source));from animate_restoration import author;author(rig)
bpy.context.scene.frame_set(90);bpy.context.view_layer.update()
assert (rig.pose.bones['hand_L'].matrix.translation-__import__('mathutils').Vector((-19,-24,111))).length<.01
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(source/'CR03_RookRestoration.blend'))
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);skin.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(out/'SK_CR03_Restoration.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,bake_anim_step=1,mesh_smooth_type='FACE')
print('CR03_REFINED',len(skin.data.vertices),'vertices; corrected world-space hand targets; open optical aperture')
