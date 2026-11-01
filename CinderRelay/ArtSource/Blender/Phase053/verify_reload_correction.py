"""Read-only evaluated-pose/FBX regression and genuine six-stage source renders.

Run with Blender --background --python ... -- --evidence-dir <ignored path>
--export-dir <handling FBX path>. No source or Unreal assets are saved here.
"""
import argparse, bpy, hashlib, json, math, sys
from pathlib import Path
from mathutils import Vector

ap=argparse.ArgumentParser();ap.add_argument('--evidence-dir',required=True);ap.add_argument('--export-dir',required=True)
ap.add_argument('--skip-renders',action='store_true')
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);here=Path(__file__).resolve().parent
out=Path(args.evidence_dir);out.mkdir(parents=True,exist_ok=True)
frames=[0,18,30,46,57,66,82,94,111,127,144]
stages={'hold':0,'release':18,'removed':46,'replacement':82,'seated':111,'ready':144}
def vec(v):return [float(x) for x in v]
def mat(m):return [vec(row) for row in m]
def inspect(source,tag):
    bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;rig=bpy.data.objects['CR053_FirstPersonRig']
    mesh=bpy.data.objects['SK_CR053_FirstPersonArms']
    rest={b.name:{'matrix':mat(b.matrix_local),'parent':b.parent.name if b.parent else None} for b in rig.data.bones}
    data={'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'rest':rest,'object_matrix':mat(rig.matrix_world),'determinant':rig.matrix_world.determinant(),'nla_tracks':len(rig.animation_data.nla_tracks),'actions':{},'mesh_hash':hashlib.sha256(str(([vec(v.co) for v in mesh.data.vertices],[tuple(p.vertices) for p in mesh.data.polygons])).encode()).hexdigest()}
    for name in ['Idle','Walk','Sprint','ADS','FireCycle','Reload','Dry']:
        a=bpy.data.actions['AN_CR053_'+name];rig.animation_data.action=a
        poses=[]
        for f in frames if name=='Reload' else sorted({0,int(a.frame_range[1]/2),int(a.frame_range[1])}):
            scene.frame_set(f);bpy.context.view_layer.update();er=rig.evaluated_get(bpy.context.evaluated_depsgraph_get());p=er.pose.bones
            row={'frame':f,'hands':{},'bones':{}}
            for side in ('L','R'):
                w=p['wrist.'+side];e=p['CTRL_forearm.'+side];m=p['finger3-1.'+side]
                row['hands'][side]={'wrist':vec(w.head),'quat_wxyz':vec(w.matrix.to_quaternion()),'elbow':vec(e.head),'mcp':vec(m.head),'bend_degrees':math.degrees((w.head-e.head).angle(m.head-w.head)),'target_error_cm':(w.head-p['CTRL_Hand.'+side].head).length}
            for n in ['root','weapon','feed','wrist.L','wrist.R','finger3-1.L','finger3-1.R']:
                row['bones'][n]={'position':vec(p[n].head),'quat_wxyz':vec(p[n].matrix.to_quaternion()),'determinant':p[n].matrix.determinant()}
            poses.append(row)
        data['actions'][name]={'seconds':a.frame_range[1]/60,'slot':str(rig.animation_data.action_slot),'poses':poses}
    if tag=='after':
        assert all(b['determinant']>.99 for a in data['actions'].values() for p in a['poses'] for b in p['bones'].values())
        assert max(p['hands']['R']['bend_degrees'] for p in data['actions']['Reload']['poses'])<55
        assert max(p['hands']['L']['bend_degrees'] for p in data['actions']['Reload']['poses'])<80
        assert len([a for a in bpy.data.actions if a.name.endswith('_Rollback_PreReloadFix')])==7
    rig.animation_data.action=bpy.data.actions['AN_CR053_Reload']
    scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
    scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
    scene.camera.location=(-48,10,10);scene.camera.rotation_euler=Vector((1,0,0)).to_track_quat('-Z','Y').to_euler();scene.camera.data.angle=math.radians(90)
    bpy.data.objects['SM_CR051_SurveyOptic'].hide_render=True
    for o in scene.objects:
        if o.type=='LIGHT':o.data.energy*=3
    for stage,f in ([] if args.skip_renders else stages.items()):
        scene.frame_set(f);scene.render.filepath=str(out/f'{tag}-{stage}.png');bpy.ops.render.render(write_still=True)
    return data

before=inspect(here/'CR053_FirstPerson.blend','before')
after=inspect(here/'CR053_FirstPerson_ReloadCorrected.blend','after')
assert before['rest']==after['rest'] and before['mesh_hash']==after['mesh_hash']
assert before['object_matrix']==after['object_matrix'] and after['nla_tracks']==0
assert after['actions']['Reload']['seconds']==2.4
fbx=Path(args.export_dir)/'AN_CR053_Reload.fbx'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=60
# Blender's importer otherwise shifts FBX time zero to frame 1 by default.
bpy.ops.import_scene.fbx(filepath=str(fbx),automatic_bone_orientation=False,anim_offset=0.0)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');fbx_rows=[];max_error=0
for i,f in enumerate(frames):
    bpy.context.scene.frame_set(f);bpy.context.view_layer.update();p=rig.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones
    row={'frame':f,'bones':{}}
    for n in ['weapon','feed','wrist.L','wrist.R','finger3-1.L','finger3-1.R']:
        v=(rig.matrix_world@p[n].head)*100;expected=Vector(after['actions']['Reload']['poses'][i]['bones'][n]['position'])
        error=(v-expected).length;max_error=max(max_error,error)
        row['bones'][n]={'position_cm':vec(v),'error_cm':error}
    fbx_rows.append(row)
result={'before':before,'after':after,'fbx':{'sha256':hashlib.sha256(fbx.read_bytes()).hexdigest(),'bones':[b.name for b in rig.data.bones],'object_matrix':mat(rig.matrix_world),'positive_determinant':rig.matrix_world.determinant()>0,'max_position_error_cm':max_error,'poses':fbx_rows}}
(out/'evaluated-comparison.json').write_text(json.dumps(result,indent=2))
assert max_error<.01,max_error
print('CR_RELOAD_SOURCE_VALIDATION_PASS FBX_MAX_CM',max_error)
