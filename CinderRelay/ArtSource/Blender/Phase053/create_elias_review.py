"""Phase053 anatomical review candidate from pinned CC0 MakeHuman graphical data.
Not combat integration. Does not open or overwrite previous source assets.
Blender 4.5 LTS, centimeters, +X forward, +Z up. No MakeHuman program code used.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector, Quaternion

ap=argparse.ArgumentParser()
ap.add_argument('--source-dir',required=True)
ap.add_argument('--export-dir',required=True)
opt=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(opt.source_dir); out=Path(opt.export_dir);out.mkdir(parents=True,exist_ok=True)
here=Path(__file__).resolve().parent
for item in json.loads((here/'upstream-manifest.json').read_text(encoding='utf-8-sig'))['files']:
    content=(source/item['name']).read_bytes()
    assert len(content)==item['bytes'] and hashlib.sha256(content).hexdigest()==item['sha256'],item['name']
blend=here/'CR053_EliasArms.blend'
if blend.exists():raise FileExistsError('Preserve candidate; edit the saved Blender source instead of regenerating it')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
scene.render.fps=60;scene.frame_start=0;scene.frame_end=180
bpy.context.preferences.filepaths.save_version=0
skel=json.loads((source/'default.mhskel').read_text(encoding='utf-8'))
weights=json.loads((source/'default_weights.mhw').read_text(encoding='utf-8'))
assert skel['license']=='CC0' and weights['license']=='CC0'
vertices=[];uvs=[];faces=[];faceuv=[];group=''
for line in (source/'base.obj').read_text(encoding='utf-8').splitlines():
    part=line.split()
    if not part:continue
    if part[0]=='v':vertices.append(Vector(tuple(map(float,part[1:4]))))
    elif part[0]=='vt':uvs.append(tuple(map(float,part[1:3])))
    elif part[0]=='g':group=part[1]
    elif part[0]=='f' and group=='body':
        parts=[t.split('/') for t in part[1:]]
        faces.append([int(t[0])-1 for t in parts]);faceuv.append([int(t[1])-1 for t in parts])
# Small authored shape adjustments using upstream graphical morphs; no race/story assignment.
morphs={name:strength for side in('l','r') for name,strength in(
    (side+'-lowerarm-muscle-incr.target',.38),
    (side+'-upperarm-muscle-incr.target',.22),
    (side+'-hand-scale-incr.target',.09))}
for name,strength in morphs.items():
    for line in (source/name).read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'):continue
        i,x,y,z=line.split();vertices[int(i)]+=Vector((float(x),float(y),float(z)))*strength
names=[n for n in skel['bones'] if n.startswith(('upperarm','lowerarm','wrist','metacarpal','finger'))]
weight_map={n:dict(weights['weights'].get(n,[])) for n in names}
arm_weight=[sum(w.get(i,0) for w in weight_map.values()) for i in range(len(vertices))]
selected=[i for i,f in enumerate(faces) if all(arm_weight[v]>.45 and abs(vertices[v].x)>1.55 for v in f)]
used=sorted({v for i in selected for v in faces[i]});remap={v:i for i,v in enumerate(used)}
def point(key):return sum((vertices[i] for i in skel['joints'][key]),Vector())/len(skel['joints'][key])
origin=(point(skel['bones']['upperarm01.L']['head'])+point(skel['bones']['upperarm01.R']['head']))*.5
def convert(v):
    v=(v-origin)*11.0
    return Vector((v.z-24,v.x,v.y-16))
def joint(key):return convert(point(key))
mesh=bpy.data.meshes.new('CR053_ConnectedAnatomy')
mesh.from_pydata([convert(vertices[v]) for v in used],[],[[remap[v] for v in faces[i]] for i in selected]);mesh.update()
skin=bpy.data.objects.new('SK_CR053_EliasArms',mesh);scene.collection.objects.link(skin)
uv=mesh.uv_layers.new(name='ArmsUV')
for poly,src_index in zip(mesh.polygons,selected):
    poly.use_smooth=True
    for li,src_uv in zip(poly.loop_indices,faceuv[src_index]):uv.data[li].uv=uvs[src_uv]
for n in names:
    vg=skin.vertex_groups.new(name=n)
    for original,value in weight_map[n].items():
        if original in remap and value>0:vg.add([remap[original]],value/arm_weight[original],'REPLACE')

def material(name,color,rough,cloth=False):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    p=nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=rough
    p.inputs['Subsurface Weight'].default_value=.055 if name.endswith('Skin') else 0
    tex=nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=2.5;tex.inputs['Detail'].default_value=3
    coord=nodes.new('ShaderNodeTexCoord');links.new(coord.outputs['Object'],tex.inputs['Vector'])
    mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[1].default_value=(*(c*.6 for c in color),1);mix.inputs[2].default_value=(*color,1)
    links.new(tex.outputs['Fac'],mix.inputs[0]);links.new(mix.outputs[0],p.inputs['Base Color'])
    fine=nodes.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=42 if cloth else 27;fine.inputs['Detail'].default_value=2
    links.new(coord.outputs['Object'],fine.inputs['Vector'])
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.035 if cloth else .014
    links.new(fine.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
    mat.diffuse_color=(*color,1)
    return mat
skinmat=material('CR053_Skin',(.36,.205,.13),.58)
glovemat=material('CR053_WorkGlove',(.055,.062,.052),.79,True)
clothmat=material('CR053_WorkSleeve',(.115,.145,.13),.87,True)
skin.data.materials.append(skinmat)

# Garment surfaces follow authored anatomical edge flow, never cylinder segments.
def garment(name,predicate,offset,material,fold=False):
    keep=[p for p in skin.data.polygons if predicate(p)]
    ids=sorted({v for p in keep for v in p.vertices});mapping={v:i for i,v in enumerate(ids)}
    positions=[]
    for i in ids:
        v=skin.data.vertices[i];delta=offset
        if fold:delta+=.15*math.sin(v.co.z*1.55+v.co.y*.26)+.1*math.cos(v.co.x*1.8-v.co.z*.4)
        positions.append(v.co+v.normal*delta)
    m=bpy.data.meshes.new(name);m.from_pydata(positions,[],[[mapping[v] for v in p.vertices] for p in keep]);m.update()
    o=bpy.data.objects.new(name,m);scene.collection.objects.link(o);m.materials.append(material)
    for n in names:
        original=skin.vertex_groups[n];g=o.vertex_groups.new(name=n)
        for old,new in mapping.items():
            w=next((entry.weight for entry in skin.data.vertices[old].groups if entry.group==original.index),0)
            if w:g.add([new],w,'REPLACE')
    for p in m.polygons:p.use_smooth=True
    bpy.context.view_layer.objects.active=o
    solid=o.modifiers.new('Turned fabric edge','SOLIDIFY');solid.thickness=.065;solid.offset=0
    bpy.ops.object.modifier_apply(modifier=solid.name)
    return o
def weight_at(poly,prefix):
    return sum(sum(g.weight for g in skin.data.vertices[v].groups if skin.vertex_groups[g.group].name.startswith(prefix)) for v in poly.vertices)/len(poly.vertices)
def glove_face(poly):
    return weight_at(poly,('wrist','metacarpal','finger1-1','finger2-1','finger3-1','finger4-1','finger5-1'))>.65
def sleeve_face(poly):
    return weight_at(poly,('upperarm','lowerarm01'))>.72
glove=garment('Fitted fingerless work gloves',glove_face,.09,glovemat)
sleeve=garment('Fitted work sleeves',sleeve_face,.48,clothmat,True)
bpy.ops.object.select_all(action='DESELECT')
for o in(skin,glove,sleeve):o.select_set(True)
bpy.context.view_layer.objects.active=skin;bpy.ops.object.join()
# Unified atlas; editable garments retain one deforming mesh after the join.
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(72),island_margin=.012);bpy.ops.object.mode_set(mode='OBJECT')
sub=skin.modifiers.new('Anatomical surface subdivision','SUBSURF');sub.levels=1;sub.render_levels=1
bpy.ops.object.modifier_apply(modifier=sub.name)

arm=bpy.data.armatures.new('CR053_AnatomicalRig');rig=bpy.data.objects.new('CR053_EliasRig',arm);scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
root=arm.edit_bones.new('root');root.head=(0,0,0);root.tail=(0,0,10)
for n in names:
    spec=skel['bones'][n];bone=arm.edit_bones.new(n);bone.head=joint(spec['head']);bone.tail=joint(spec['tail'])
    plane=skel['planes'][spec['rotation_plane']];a,b,c=[joint(k) for k in plane]
    normal=(b-a).cross(c-a).normalized()
    if normal.length>0:bone.align_roll(normal)
for n in names:
    parent=skel['bones'][n]['parent'];arm.edit_bones[n].parent=arm.edit_bones.get(parent,root)
for side in('L','R'):
    upper=arm.edit_bones.new('CTRL_upperarm.'+side);upper.head=arm.edit_bones['upperarm01.'+side].head;upper.tail=arm.edit_bones['lowerarm01.'+side].head;upper.parent=root;upper.use_deform=False
    lower=arm.edit_bones.new('CTRL_forearm.'+side);lower.head=upper.tail;lower.tail=arm.edit_bones['wrist.'+side].head;lower.parent=upper;lower.use_connect=True;lower.use_deform=False
bpy.ops.object.mode_set(mode='OBJECT')
mod=skin.modifiers.new('Human skin deformation','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True;skin.parent=rig
controls=[]
for side in('L','R'):
    wrist=arm.bones['wrist.'+side]
    target=bpy.data.objects.new('IK_Hand.'+side,None);scene.collection.objects.link(target);target.empty_display_type='ARROWS';target.empty_display_size=3;target.matrix_world=wrist.matrix_local.copy();controls.append(target)
    elbow=bpy.data.objects.new('IK_Elbow.'+side,None);scene.collection.objects.link(elbow);elbow.empty_display_size=2;elbow.location=arm.bones['lowerarm01.'+side].head_local+Vector((-20,20 if side=='L' else -20,-20));controls.append(elbow)
    ik=rig.pose.bones['CTRL_forearm.'+side].constraints.new('IK');ik.target=target;ik.pole_target=elbow;ik.chain_count=2;ik.use_stretch=False
    # Keep IK disabled in anatomy-only samples; the controls are editable for C/D.
    ik.influence=0
    for dst,ctrl in(('upperarm01.','CTRL_upperarm.'),('lowerarm01.','CTRL_forearm.')):
        con=rig.pose.bones[dst+side].constraints.new('COPY_ROTATION');con.name='IK rotation (review disabled)';con.target=rig;con.subtarget=ctrl+side;con.target_space='WORLD';con.owner_space='WORLD';con.influence=0
    con=rig.pose.bones['wrist.'+side].constraints.new('COPY_ROTATION');con.name='IK wrist (review disabled)';con.target=target;con.target_space='WORLD';con.owner_space='WORLD';con.influence=0

# A bounded anatomical articulation clip, not a claimed reload/weapon animation.
samples=[(0,0),(30,.26),(60,.80),(90,.56),(120,0),(150,.62),(180,0)]
for side in('L','R'):
    wrist=arm.bones['wrist.'+side].head_local
    index=arm.bones['finger2-1.'+side].head_local-wrist
    little=arm.bones['finger5-1.'+side].head_local-wrist
    palm=index.cross(little).normalized()
    if palm.dot(Vector((0,-1 if side=='L' else 1,0)))<0:palm=-palm
    for d in range(1,6):
        for part in range(1,4):
            n=f'finger{d}-{part}.{side}';pb=rig.pose.bones[n];pb.rotation_mode='QUATERNION'
            longitudinal=pb.bone.tail_local-pb.bone.head_local
            axis=pb.bone.matrix_local.to_3x3().inverted()@longitudinal.cross(palm).normalized()
            for frame,amount in samples:
                angle=amount*math.radians((52,76,49)[part-1])*(.72 if d==1 else .9 if d==5 else 1)
                pb.rotation_quaternion=Quaternion(axis,angle);pb.keyframe_insert('rotation_quaternion',frame=frame)
    for frame,angle in[(0,0),(30,0),(60,0),(90,.28),(120,-.28),(150,0),(180,0)]:
        for n,fraction in [('lowerarm02.',.45),('wrist.',.55)]:
            pb=rig.pose.bones[n+side];pb.rotation_mode='XYZ';pb.rotation_euler.y=angle*fraction;pb.keyframe_insert('rotation_euler',frame=frame)
rig.animation_data.action.name='AN_CR053_AnatomyReview'
for fc in rig.animation_data.action.fcurves:
    for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
for frame,label in[(0,'OPEN PALM'),(30,'RELAXED'),(60,'CURL'),(90,'WRIST TWIST'),(120,'OPEN AND COUNTER TWIST'),(150,'GRIP'),(180,'RELEASE')]:scene.timeline_markers.new(label,frame=frame)
scene.frame_set(30)
rig['provenance']='CC0 MakeHuman anatomical graphical data; a8bc2d54ff0ac92e78ff71431b1023eda42bf482. New garment/art edits: Cinder Relay.'
rig['review_status']='Anatomy candidate only. Owner review required before weapon/workbench integration.'
rig['bone_contract']='Original MakeHuman named finger/metacarpal/wrist and split forearm chains; NOT Manny/UE mannequin compatible by name.'
scene['phase']='05.3 Checkpoint B candidate'
scene['shape_morphs']=json.dumps(morphs)
skin.data.calc_loop_triangles()
weighted=[sum(g.weight for g in v.groups) for v in skin.data.vertices]
assert min(weighted)>.98 and max(weighted)<1.02,(min(weighted),max(weighted))
# Source preview camera frames both hands without changing the mesh or rig.
bpy.ops.object.camera_add(location=(80,-70,15));cam=bpy.context.object;cam.name='AnatomyReviewCamera'
center=(rig.pose.bones['wrist.L'].head+rig.pose.bones['wrist.R'].head)*.5+Vector((6,0,-4))
cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=55;cam.data.clip_start=.1;cam.data.clip_end=10000;scene.camera=cam
for pos,power,size in[((40,-45,65),1300,65),((5,65,25),900,70),((-55,-5,65),1100,50)]:
    bpy.ops.object.light_add(type='AREA',location=pos);lamp=bpy.context.object;lamp.data.energy=power;lamp.data.shape='DISK';lamp.data.size=size;lamp.rotation_euler=(center-lamp.location).to_track_quat('-Z','Y').to_euler()
scene.world=bpy.data.worlds.new('CR053_ReviewWorld');scene.world.color=(.11,.11,.11)
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.export_scene.fbx(filepath=str(out/'SK_CR053_EliasArms.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
# Meter-normalized GLB is produced only by export_elias_review.py.
receipt={'source':str(blend),'upstream_commit':'a8bc2d54ff0ac92e78ff71431b1023eda42bf482','source_vertices_used':len(used),'vertices':len(skin.data.vertices),'triangles':len(skin.data.loop_triangles),'material_slots':len(skin.data.materials),'deform_bones':len(names)+1,'edit_control_bones':4,'weighted_range':[min(weighted),max(weighted)],'review_clip_seconds':3,'fps':60,'runtime_integrated':False,'human_approval':False,'textures_baked':False}
(out/'arms-source-receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print('CR053_ARMS_SOURCE_PASS',json.dumps(receipt))
