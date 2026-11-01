"""Derivative human-arm handling source. Run in Blender; never edits review/old sources.

Controls remain editable; FBX bakes evaluated IK, not a runtime solver. All exterior
handling is fictional. Gameplay timers and ammunition are not authored here.
"""
import argparse, bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Matrix, Vector, Quaternion
from mathutils.bvhtree import BVHTree

ap=argparse.ArgumentParser()
ap.add_argument('--export-dir', required=True)
ap.add_argument('--rebuild-owned', action='store_true')
ap.add_argument('--skip-atlas', action='store_true')
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here))
from rig_contact import calibrate_pole
out=Path(args.export_dir);out.mkdir(parents=True,exist_ok=True)
dest=here/'CR053_FirstPerson.blend'
if dest.exists():
    assert args.rebuild_owned, 'Refusing to replace derivative without explicit owned rebuild'
    bpy.ops.wm.open_mainfile(filepath=str(dest))
    assert bpy.context.scene.get('CR.Owner')=='CinderRelay.Phase053.FirstPerson.v1'
bpy.ops.wm.open_mainfile(filepath=str(here/'CR053_EliasArms.blend'))
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene['CR.Owner']='CinderRelay.Phase053.FirstPerson.v1'
scene.render.fps=60
rig=bpy.data.objects['CR053_EliasRig'];skin=bpy.data.objects['SK_CR053_EliasArms']
rig.name='CR053_FirstPersonRig';skin.name='SK_CR053_FirstPersonArms'
rig.animation_data_clear()
for obj in list(bpy.data.objects):
    if obj not in (rig,skin):bpy.data.objects.remove(obj,do_unlink=True)
for pb in rig.pose.bones:
    pb.matrix_basis=Matrix.Identity(4)
    for con in list(pb.constraints):pb.constraints.remove(con)

def select(objects,active=None):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects:ob.hide_set(False);ob.select_set(True)
    bpy.context.view_layer.objects.active=active or objects[0]

# Repair atlas on final topology. This avoids interpolation across the previous
# pre-decimation UV seams; original procedural nodes remain editable in source.
texdir=here/'FirstPersonTextures';texdir.mkdir(exist_ok=True)
select([skin]);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.018)
bpy.ops.object.mode_set(mode='OBJECT')
for mat in skin.data.materials:
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF')
    mix=next(n for n in nodes if n.type=='MIX_RGB')
    bump=next(n for n in nodes if n.type=='BUMP')
    links.new(mix.outputs[0],p.inputs['Base Color']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
if not args.skip_atlas:
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=4
    scene.render.bake.margin=10;scene.render.bake.use_clear=True
    for suffix,kind in [('BaseColor','DIFFUSE'),('Normal','NORMAL')]:
        im=bpy.data.images.new('T_CR053_FP_'+suffix,width=2048,height=2048,alpha=False)
        if suffix=='Normal':im.colorspace_settings.name='Non-Color'
        for mat in skin.data.materials:
            node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;mat.node_tree.nodes.active=node
        if kind=='DIFFUSE':bpy.ops.object.bake(type=kind,pass_filter={'COLOR'})
        else:bpy.ops.object.bake(type=kind)
        im.filepath_raw=str(texdir/('T_CR053_FP_'+suffix+'.png'));im.file_format='PNG';im.save()
for mat in skin.data.materials:
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF')
    for suffix in ('BaseColor','Normal'):
        path=texdir/('T_CR053_FP_'+suffix+'.png');assert path.exists()
        im=bpy.data.images.load(str(path),check_existing=True);im.pack()
        node=nodes.new('ShaderNodeTexImage');node.image=im
        if suffix=='BaseColor':links.new(node.outputs['Color'],p.inputs['Base Color'])
        else:
            im.colorspace_settings.name='Non-Color';nm=nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.3
            links.new(node.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs[0],p.inputs['Normal'])

# The anatomical candidate left skin beneath the fitted glove. Independent
# decimation can make that hidden skin poke through at a bend. Remove only faces
# whose every corner has actual glove coverage along its outward normal; never
# remove exposed fingers or infer coverage from weight/name alone. UVs stay put.
glove_index=next(i for i,m in enumerate(skin.data.materials) if 'glove' in m.name.lower())
skin_index=next(i for i,m in enumerate(skin.data.materials) if 'skin' in m.name.lower())
glove_faces=[tuple(p.vertices) for p in skin.data.polygons if p.material_index==glove_index]
glove_tree=BVHTree.FromPolygons([v.co for v in skin.data.vertices],glove_faces)
covered={}
for vertex in skin.data.vertices:
    direction=vertex.normal.normalized()
    hit,normal,_,distance=glove_tree.ray_cast(vertex.co+direction*.5,-direction,.65)
    covered[vertex.index]=hit is not None and normal.dot(direction)>.1
hidden=[p.index for p in skin.data.polygons if p.material_index==skin_index and all(covered[i] for i in p.vertices)]
bm=bmesh.new();bm.from_mesh(skin.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in hidden],context='FACES');bm.to_mesh(skin.data);bm.free();skin.data.update()
skin['CR.HiddenCoveredSkinFaces']=len(hidden)

select([rig]);bpy.ops.object.mode_set(mode='EDIT')
bones=rig.data.edit_bones
for side in ('L','R'):
    upper=bones['CTRL_upperarm.'+side];lower=bones['CTRL_forearm.'+side]
    upper.align_roll(bones['upperarm01.'+side].z_axis)
    lower.align_roll(bones['lowerarm01.'+side].z_axis)
    for name,pos in [('Hand',bones['wrist.'+side].head),('Elbow',Vector((-35,40 if side=='L' else -40,-30)))]:
        b=bones.new('CTRL_'+name+'.'+side);b.head=pos;b.tail=pos+Vector((0,3,0));b.parent=bones['root'];b.use_deform=False
    for destbone,control in [('upperarm01.','CTRL_upperarm.'),('lowerarm01.','CTRL_forearm.')]:
        original=bones[destbone+side];helper=bones.new('CTRL_deform_'+destbone+side)
        helper.head=original.head;helper.tail=original.tail;helper.roll=original.roll;helper.parent=bones[control+side];helper.use_deform=False
    alias=bones.new('hand_'+side);alias.head=bones['wrist.'+side].head;alias.tail=bones['wrist.'+side].tail;alias.parent=bones['wrist.'+side]
for name,pos in [('weapon',(0,0,0)),('feed',(0,0,0)),('cycle_handle',(0,0,0)),('optic',(0,0,0))]:
    b=bones.new(name);b.head=pos;b.tail=Vector(pos)+Vector((0,10,0));b.parent=bones['root'] if name=='weapon' else bones['weapon']
bpy.ops.object.mode_set(mode='OBJECT')
hand_basis={};curl_axes={}
for side in ('L','R'):
    ik=rig.pose.bones['CTRL_forearm.'+side].constraints.new('IK');ik.name='Two bone elbow contact'
    ik.target=rig;ik.subtarget='CTRL_Hand.'+side;ik.pole_target=rig;ik.pole_subtarget='CTRL_Elbow.'+side;ik.chain_count=2;ik.use_stretch=False
    for name in ('upperarm01.','lowerarm01.'):
        con=rig.pose.bones[name+side].constraints.new('COPY_ROTATION');con.target=rig;con.subtarget='CTRL_deform_'+name+side;con.target_space='WORLD';con.owner_space='WORLD'
    con=rig.pose.bones['wrist.'+side].constraints.new('COPY_ROTATION');con.target=rig;con.subtarget='CTRL_Hand.'+side;con.target_space='WORLD';con.owner_space='WORLD'
    w=rig.data.bones['wrist.'+side].head_local
    long=(rig.data.bones['finger3-1.'+side].head_local-w).normalized()
    normal=(rig.data.bones['finger2-1.'+side].head_local-w).cross(rig.data.bones['finger5-1.'+side].head_local-w).normalized()
    if normal.dot(Vector((0,-1 if side=='L' else 1,0)))<0:normal=-normal
    normal=(normal-long*normal.dot(long)).normalized()
    hand_basis[side]=Matrix((long.cross(normal),long,normal)).transposed()
    for digit in range(1,6):
        for segment in range(1,4):
            bone=rig.data.bones[f'finger{digit}-{segment}.{side}']
            curl_axes[bone.name]=bone.matrix_local.to_3x3().inverted()@(bone.tail_local-bone.head_local).cross(normal).normalized()

# Existing hero geometry is a source reference, not a new weapon/gameplay asset.
with bpy.data.libraries.load(str(here.parent/'Phase051/CR051_Rook5.blend'),link=False) as (src,dst):
    dst.objects=['SM_CR051_Rook5','SM_CR051_SurveyOptic']
for obj in dst.objects:
    scene.collection.objects.link(obj);obj.hide_render=False;obj.hide_set(False)
    mod=obj.modifiers.new('Fictional exterior attachment','ARMATURE');mod.object=rig
    vg=obj.vertex_groups.new(name='optic' if 'Survey' in obj.name else 'weapon');vg.add(list(range(len(obj.data.vertices))),1,'REPLACE')
    obj.parent=rig
    obj['CR.SourceReferenceOnly']=True

metal=next(m for m in bpy.data.materials if m.name.endswith('_Steel'))
brass=next(m for m in bpy.data.materials if m.name.endswith('_Brass'))
def mesh(name,verts,faces,material):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.materials.append(material);data.update()
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj)
    for p in data.polygons:p.use_smooth=True
    return obj
def cylinder(name,start,end,radius,material):
    a=Vector(start);b=Vector(end);bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=radius,depth=(b-a).length,location=(a+b)*.5)
    obj=bpy.context.object;obj.name=name;obj.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();obj.data.materials.append(material)
    return obj
def join(parts,name,bone):
    select(parts)
    for p in parts:
        bpy.context.view_layer.objects.active=p
        for mod in list(p.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();obj=bpy.context.object;obj.name=name
    scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    if not obj.data.uv_layers:
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False)
    if bone:
        vg=obj.vertex_groups.new(name=bone);vg.add(list(range(len(obj.data.vertices))),1,'REPLACE');obj.parent=rig
        mod=obj.modifiers.new('Exterior prop attachment','ARMATURE');mod.object=rig
    return obj
profile=[(-.5,-5.7),(9,-5.7),(9,-8),(7.5,-14),(0,-13.5),(-1,-8)]
verts=[(x,y,z) for y in (-2.15,2.15) for x,z in profile];n=len(profile)
feed=mesh('External five-round feeding shell',verts,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],metal)
bevel=feed.modifiers.new('Pressed curved edges','BEVEL');bevel.width=.34;bevel.segments=4
parts=[feed]
for x in (1,2.5,4,5.5,7):
    parts.append(cylinder('Decorative round indicator',(x,-2.22,-7),(x,-2.22,-10),.32,brass))
join(parts,'SM_CR053_Feed','feed')
parts=[cylinder('Exterior handle stalk',(-14,-3.8,2.7),(-14,-6.5,2.7),.3,metal),cylinder('Rounded cycle pad',(-14.9,-6.5,2.7),(-13.1,-6.5,2.7),.62,metal)]
join(parts,'SM_CR053_CycleHandle','cycle_handle')
case=join([cylinder('Stylized cosmetic case',(-1,0,0),(1,0,0),.3,brass)],'SM_CR053_Case',None)
case.hide_render=True;case.hide_set(True)

def frame_basis(direction,normal):
    y=Vector(direction).normalized();z=Vector(normal);z=(z-y*z.dot(y)).normalized()
    return Matrix((y.cross(z),y,z)).transposed()

def hand(side,pos,direction,normal,curl,frame):
    target=frame_basis(direction,normal)@hand_basis[side].inverted()@rig.data.bones['wrist.'+side].matrix_local.to_3x3()
    pb=rig.pose.bones['CTRL_Hand.'+side];pb.rotation_mode='QUATERNION'
    pb.matrix=Matrix.Translation(pos)@target.to_4x4()
    pb.keyframe_insert('location',frame=frame);pb.keyframe_insert('rotation_quaternion',frame=frame)
    for digit in range(1,6):
        for segment in range(1,4):
            pb=rig.pose.bones[f'finger{digit}-{segment}.{side}'];pb.rotation_mode='QUATERNION'
            amount=curl*(.67 if digit==1 else .80 if digit==2 else 1)
            pb.rotation_quaternion=Quaternion(curl_axes[pb.name],math.radians((48,68,38)[segment-1])*amount)
            # Opposition originates at the thumb base, not equal twisting of all phalanges.
            if digit==1 and segment==1:
                local=pb.bone.matrix_local.to_3x3().inverted()@hand_basis[side].col[1]
                pb.rotation_quaternion=Quaternion(local,math.radians(-24 if side=='L' else 24))*pb.rotation_quaternion
            pb.keyframe_insert('rotation_quaternion',frame=frame)

def prop(name,matrix,frame):
    pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix=matrix@pb.bone.matrix_local
    pb.keyframe_insert('location',frame=frame);pb.keyframe_insert('rotation_quaternion',frame=frame)

def pose(frame,weapon=None,right=None,left=None,feed=None,cycle=0,curl=(.9,.85)):
    wm=weapon or Matrix.Identity(4)
    prop('weapon',wm,frame)
    # Blender evaluates a child matrix setter against its evaluated parent.
    # Flush the parent before keying children, including the first key of a clip.
    bpy.context.view_layer.update()
    prop('feed',wm@(feed or Matrix.Identity(4)),frame)
    prop('cycle_handle',wm@Matrix.Translation((-cycle,0,0)),frame)
    prop('optic',wm,frame)
    for side,position,direction,normal,amount in [
        # Anatomical right wrist approaches the stock from behind/below. The
        # old downward palm axis (.3,0,-1) forced a >100-degree wrist fold.
        ('R',right or (-27,-5,-7),(1,0,.2),(0,1,0),curl[0]),
        ('L',left or (18,7,-10),(.2,-1,.55),(0,.5,1),curl[1])]:
        hand(side,wm@Vector(position),wm.to_3x3()@Vector(direction),wm.to_3x3()@Vector(normal),amount,frame)
    bpy.context.view_layer.update()

def action(name,length):
    rig.animation_data_create();a=bpy.data.actions.new('AN_CR053_'+name);a.use_fake_user=True;rig.animation_data.action=a
    scene.frame_start=0;scene.frame_end=length
    return a

clips=[]
for name,length in [('Idle',240),('Walk',60),('Sprint',48),('ADS',60),('FireCycle',54),('Reload',144),('Dry',15)]:
    a=action(name,length);clips.append((a,length))
    if name in ('Idle','ADS','Walk','Sprint'):
        for f in range(0,length+1,length//4):
            wave=[0,1,0,-1,0][f//(length//4)]
            if name=='ADS':wm=Matrix.Identity(4)
            elif name=='Idle':wm=Matrix.Translation((0,0,wave*.12))
            elif name=='Walk':wm=Matrix.Translation((0,wave*.38,abs(wave)*.32))@Matrix.Rotation(math.radians(wave*.45),4,'X')
            else:wm=Matrix.Translation((-2,0,-5+abs(wave)*.5))@Matrix.Rotation(math.radians(-14+wave),4,'Y')
            pose(f,wm)
    elif name=='FireCycle':
        for f,recoil,handpos,travel,c in [
            (0,0,None,0,.9),(3,-2.2,None,0,.9),(7,-.7,None,0,.9),
            (14,0,(-24,-8,-1),0,.55),(20,0,(-29,-8,-1),5,.65),
            (25,0,(-29,-8,-1),5,.65),(35,0,(-24,-8,-1),0,.6),
            (44,0,None,0,.9),(54,0,None,0,.9)]:
            pose(f,Matrix.Translation((recoil,0,0)),right=handpos,cycle=travel,curl=(c,.85))
        a['Cue.EjectCase']=20/60
    elif name=='Reload':
        # The original unit leaves the image below; replacement enters visibly,
        # with five decorative round indicators. No ammo value changes here.
        # Same corrected contact contract as the non-destructive refinement.
        # A deliberate full rebuild must not regenerate the old wrist grip.
        for f,feedpos,yaw,weight in [
            (0,(0,0,0),0,0),(18,(0,0,0),0,1),(30,(0,0,-1),0,1),
            (46,(0,12,-6),-35,1),(57,(0,12,-35),-55,1),(66,(0,12,-35),-55,1),
            (82,(0,17,2),-65,1),(94,(0,17,2),-65,1),(103,(0,8,0),-30,1),
            (111,(0,0,0),0,1),(127,(0,0,0),0,.4),(144,(0,0,0),0,0)]:
            wm=Matrix.Translation((3*weight,5*weight,5*weight))@Matrix.Rotation(math.radians(-15*weight),4,'X')
            fm=Matrix.Translation(feedpos)@Matrix.Rotation(math.radians(yaw),4,'Z')
            pose(f,wm,feed=fm)
            if 18<=f<=111:
                grip=wm@fm
                hand('L',grip@Vector((-3,6,-14)),grip.to_3x3()@Vector((1,-.2,.25)),grip.to_3x3()@Vector((0,-1,0)),.85,f)
        a['Cue.FeedOut']=30/60;a['Cue.FeedIn']=111/60
    else:
        for f,x in [(0,0),(3,-.25),(8,0),(15,0)]:pose(f,Matrix.Translation((x,0,0)))
    for fc in a.fcurves:
        for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'

# A useful source camera approximates the existing hip contract; native UE
# captures still decide acceptance because first-person rendering scales depth.
bpy.ops.object.camera_add(location=(-38,14,15));cam=bpy.context.object;cam.name='FP_Hip_Reference'
cam.rotation_euler=Vector((1,0,0)).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=22;cam.data.clip_start=.1;scene.camera=cam
for loc,power,size in [((0,-45,65),1600,75),((15,55,35),1000,60)]:
    bpy.ops.object.light_add(type='AREA',location=loc);lamp=bpy.context.object;lamp.data.energy=power;lamp.data.size=size;lamp.rotation_euler=(Vector((0,0,-5))-lamp.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
rig.animation_data.action=clips[0][0];scene.frame_start=0;scene.frame_end=240;scene.frame_set(0)
pole_calibration={s:calibrate_pole(rig,s,0,(-34,32 if s=='L' else -32,-38)) for s in ('L','R')}
scene['CR.Status']='Editable handling candidate; native visual/runtime verification pending'
select([rig,skin],rig);bpy.ops.wm.save_as_mainfile(filepath=str(dest))
receipts=[]
for a,length in clips:
    rig.animation_data.action=a;scene.frame_start=0;scene.frame_end=length;scene.frame_set(0)
    select([rig,skin],rig)
    filename='SK_CR053_FirstPersonArms' if a.name.endswith('_Idle') else a.name
    bpy.ops.export_scene.fbx(filepath=str(out/(filename+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
    receipts.append({'clip':a.name,'frames':length,'seconds':length/60,'cues':dict(a.items())})
rig.animation_data.action=clips[0][0];scene.frame_start=0;scene.frame_end=240;scene.frame_set(0)
scene.render.filepath=str(out/'held-pose-blender.png');bpy.ops.render.render(write_still=True)
error={s:(rig.pose.bones['wrist.'+s].head-rig.pose.bones['CTRL_Hand.'+s].head).length for s in ('L','R')}
(out/'handling-source.json').write_text(json.dumps({'source':str(dest),'clips':receipts,'ik_wrist_error_cm':error,'pole_calibration':pole_calibration,'owner_approval':'anatomy direction only; handling pending'},indent=2))
print('CR053_HANDLING_SOURCE_PASS',json.dumps(error))
