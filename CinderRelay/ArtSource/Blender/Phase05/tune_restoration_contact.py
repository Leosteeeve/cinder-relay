"""Re-key only the existing Phase05 rig after actual first-person frame review.
Keep mesh, mirrored thumb, joint covers, sights, timeline length and original prop paths.
"""
import bpy,sys,argparse,ast
from pathlib import Path
from mathutils import Vector
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True);out=Path(ap.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir)
src=Path(__file__).resolve().parent;original=src.parent/'Phase03/CR03_RookRestoration.blend'
bpy.ops.wm.open_mainfile(filepath=str(src/'CR05_RookRestoration.blend'));bpy.context.preferences.filepaths.save_version=0
rig=bpy.data.objects['CR05_RestorationRig'];skin=bpy.data.objects['SK_CR05_Restoration']
# Reuse the exact original Phase05 authoring transformation; select only source-string
# preparation nodes, not its scene load/mesh edits/exports.
tree=ast.parse((src/'refine_restoration.py').read_text());nodes=[];active=False
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='base' for t in node.targets):active=True
 if active and isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='scope' for t in node.targets):break
 if active:nodes.append(node)
scope={'original':original};exec(compile(ast.Module(body=nodes,type_ignores=[]),'Phase05 choreography source','exec'),scope)
base=scope['base'];anchor="        for side,w in [('L',left),('R',right)]:"
assert anchor in base
adjust="""        left+=sample(t,[(0,(7,0,0)),(14,(7,0,0)),(17,(0,0,0)),(18.5,(7,0,0)),(22,(7,0,0))])
        right+=sample(t,[(0,(7,0,0)),(3.2,(7,0,0)),(4,(4,0,-7)),(15.5,(4,0,-7)),(17,(0,0,0)),(18.5,(7,0,0)),(22,(7,0,0))])
"""
base=base.replace(anchor,adjust+anchor);author={};exec(compile(base,'Contact-corrected action','exec'),author);author['author'](rig);rig.animation_data.action.name='AN_CR05_RookRestoration_22s'
rig['contact_revision']='First-person review: holding wrists +7cm toward near weapon surface; optic handling +4cm forward/-7cm vertically. Smooth anticipation/retreat. Original prop curves retained.'
scene=bpy.context.scene;scene.frame_start=0;scene.frame_end=660
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);skin.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(out/'SK_CR05_Restoration.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
scene.frame_set(210);bpy.ops.wm.save_as_mainfile(filepath=str(src/'CR05_RookRestoration.blend'));print('CR05_CONTACT_KEYS_PASS')
