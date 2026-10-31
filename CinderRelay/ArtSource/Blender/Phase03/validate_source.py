"""Read-only validation of the actual saved source; writes evidence only to --receipt."""
import bpy,json,sys,argparse
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--receipt',required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
assert bpy.data.filepath.endswith('CR03_RookRestoration.blend')
rig=bpy.data.objects['CR03_RestorationRig'];mesh=bpy.data.objects['SK_CR03_Restoration'];scene=bpy.context.scene
assert len(rig.data.bones)==39 and len(mesh.vertex_groups)==38
assert mesh.modifiers['Editable skeletal skin'].object==rig
assert rig.animation_data.action and tuple(rig.animation_data.action.frame_range)==(0,660)
weighted=sum(1 for v in mesh.data.vertices if len(v.groups)>1);assert weighted>0
positions={}
for second in (0,3,7,13,18,22):
    scene.frame_set(second*30);bpy.context.view_layer.update()
    positions[str(second)]={name:list(rig.pose.bones[name].matrix.translation) for name in ('hand_L','hand_R','weapon','optic')}
assert (rig.pose.bones['hand_R'].matrix.translation).length>0
receipt={'source':bpy.data.filepath,'blender':bpy.app.version_string,'bones':len(rig.data.bones),'multi_weight_vertices':weighted,'action':rig.animation_data.action.name,'duration_seconds':22,'sampled_bone_positions_cm':positions,'source_modified':False}
Path(args.receipt).write_text(json.dumps(receipt,indent=2));print('CR03_SOURCE_VALIDATED',weighted,'blended vertices')
