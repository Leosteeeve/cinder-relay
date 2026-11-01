"""Targeted atlas/budget pass on the saved Phase053 candidate; no mesh regeneration."""
import argparse,bpy,bmesh,json,sys,math
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True)
out=Path(ap.parse_args(sys.argv[sys.argv.index('--')+1:]).export_dir);out.mkdir(parents=True,exist_ok=True)
here=Path(__file__).resolve().parent;source=here/'CR053_EliasArms.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;skin=bpy.data.objects['SK_CR053_EliasArms'];rig=bpy.data.objects['CR053_EliasRig']
assert not skin.get('CR053.AtlasFinished',False),'Edit existing finished candidate; do not repeat this pass'
scene.frame_set(0)
bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);bpy.context.view_layer.objects.active=skin
def weight(vertex,prefix):return sum(g.weight for g in vertex.groups if skin.vertex_groups[g.group].name.startswith(prefix))
hidden=[]
for p in skin.data.polygons:
    if p.material_index!=0:continue
    if all(weight(skin.data.vertices[i],('upperarm','lowerarm01'))>.92 for i in p.vertices) or all(weight(skin.data.vertices[i],('wrist','metacarpal','finger1-1','finger2-1','finger3-1','finger4-1','finger5-1'))>.90 for i in p.vertices):hidden.append(p.index)
bm=bmesh.new();bm.from_mesh(skin.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in hidden],context='FACES');bm.to_mesh(skin.data);bm.free();skin.data.update()
skin.data.calc_loop_triangles();before=len(skin.data.loop_triangles)
if before>35000:
    mod=skin.modifiers.new('Bounded review topology budget','DECIMATE');mod.ratio=34000/before;mod.use_collapse_triangulate=True
    bpy.ops.object.modifier_move_up(modifier=mod.name)
    bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.object.vertex_group_limit_total(limit=4);bpy.ops.object.vertex_group_normalize_all(lock_active=False)
texture_dir=here/'Textures';texture_dir.mkdir(exist_ok=True)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=4
scene.render.bake.margin=12;scene.render.bake.use_clear=True
targets=[]
for material in skin.data.materials:
    n=material.node_tree.nodes.new('ShaderNodeTexImage');n.name='CR053_AtlasBakeTarget';material.node_tree.nodes.active=n;targets.append(n)
for suffix,kind in [('BaseColor','DIFFUSE'),('Normal','NORMAL')]:
    image=bpy.data.images.new('T_CR053_Arms_'+suffix,width=2048,height=2048,alpha=False)
    if suffix=='Normal':image.colorspace_settings.name='Non-Color'
    for n in targets:n.image=image
    if kind=='DIFFUSE':bpy.ops.object.bake(type=kind,pass_filter={'COLOR'})
    else:bpy.ops.object.bake(type=kind)
    image.filepath_raw=str(texture_dir/('T_CR053_Arms_'+suffix+'.png'));image.file_format='PNG';image.save()
# Runtime/export materials consume the baked atlas. Keep procedural nodes editable but disconnected.
for material in skin.data.materials:
    nodes=material.node_tree.nodes;links=material.node_tree.links;p=nodes.get('Principled BSDF')
    uv=nodes.new('ShaderNodeTexCoord')
    base=nodes.new('ShaderNodeTexImage');base.image=bpy.data.images['T_CR053_Arms_BaseColor'];links.new(uv.outputs['UV'],base.inputs['Vector']);links.new(base.outputs['Color'],p.inputs['Base Color'])
    normal=nodes.new('ShaderNodeTexImage');normal.image=bpy.data.images['T_CR053_Arms_Normal'];normal.image.colorspace_settings.name='Non-Color'
    convert=nodes.new('ShaderNodeNormalMap');convert.inputs['Strength'].default_value=.45;links.new(uv.outputs['UV'],normal.inputs['Vector']);links.new(normal.outputs['Color'],convert.inputs['Color']);links.new(convert.outputs['Normal'],p.inputs['Normal'])
skin['CR053.AtlasFinished']=True
skin.data.calc_loop_triangles();triangles=len(skin.data.loop_triangles)
assert triangles<=35000,triangles
for image in bpy.data.images:
    if image.name.startswith('T_CR053_Arms_'):image.pack()
scene.frame_set(30)
bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(source))
bpy.ops.export_scene.fbx(filepath=str(out/'SK_CR053_EliasArms.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
# Meter-normalized GLB is produced only by export_elias_review.py.
receipt=json.loads((out/'arms-source-receipt.json').read_text(encoding='utf-8'))
receipt.update({'vertices':len(skin.data.vertices),'triangles':triangles,'hidden_faces_removed':len(hidden),'triangles_before_budget_pass':before,'max_skin_influences':4,'textures_baked':True,'texture_size':2048,'textures':['T_CR053_Arms_BaseColor.png','T_CR053_Arms_Normal.png']})
(out/'arms-source-receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print('CR053_ATLAS_FINISH_PASS',json.dumps(receipt))
