"""Targeted owned-source mesh correction. Keeps all authored actions/rigs/UVs.
Re-export only the two affected skeletal sources, not all seven handling clips.
"""
import bpy,bmesh,json,sys,argparse
from pathlib import Path
from mathutils.bvhtree import BVHTree
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True)
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);here=Path(__file__).resolve().parent;out=Path(args.export_dir);receipts=[]
for filename,mesh_name,rig_name,export_name in [
 ('CR053_FirstPerson.blend','SK_CR053_FirstPersonArms','CR053_FirstPersonRig','SK_CR053_FirstPersonArms'),
 ('CR053_RookRestoration.blend','SK_CR053_Restoration','CR053_RestorationRig','SK_CR053_Restoration')]:
 bpy.ops.wm.open_mainfile(filepath=str(here/filename));bpy.context.preferences.filepaths.save_version=0
 scene=bpy.context.scene;assert scene.get('CR.Owner','').startswith('CinderRelay.Phase053.')
 mesh=bpy.data.objects[mesh_name];rig=bpy.data.objects[rig_name]
 assert not mesh.get('CR.CoveredSurfaceRevision'), 'Surface revision already applied; inspect before any further edit'
 glove=next(i for i,m in enumerate(mesh.data.materials) if 'glove' in m.name.lower())
 skin=next(i for i,m in enumerate(mesh.data.materials) if 'skin' in m.name.lower())
 tree=BVHTree.FromPolygons([v.co for v in mesh.data.vertices],[tuple(p.vertices) for p in mesh.data.polygons if p.material_index==glove])
 covered={}
 for v in mesh.data.vertices:
  n=v.normal.normalized();hit,normal,_,distance=tree.ray_cast(v.co+n*.5,-n,.65)
  covered[v.index]=hit is not None and normal.dot(n)>.1
 faces=[p.index for p in mesh.data.polygons if p.material_index==skin and all(covered[i] for i in p.vertices)]
 bm=bmesh.new();bm.from_mesh(mesh.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in faces],context='FACES');bm.to_mesh(mesh.data);bm.free();mesh.data.update()
 mesh['CR.CoveredSurfaceRevision']=1;mesh['CR.AdditionalHiddenFacesRemoved']=len(faces)
 # Pack resolvable appearance textures for a portable editable derivative.
 dependencies=[]
 for image in bpy.data.images:
  if image.source=='FILE' and not image.packed_file:
   path=Path(bpy.path.abspath(image.filepath));dependencies.append({'name':image.name,'path':str(path),'exists':path.exists()})
   if path.exists():image.pack()
 bpy.ops.wm.save_as_mainfile(filepath=str(here/filename))
 scene.frame_set(0);bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.fbx(filepath=str(out/(export_name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
 mesh.data.calc_loop_triangles();receipts.append({'source':filename,'removed_hidden_faces':len(faces),'triangles':len(mesh.data.loop_triangles),'vertices':len(mesh.data.vertices),'materials':len(mesh.data.materials),'texture_dependencies':dependencies})
(out/'surface-refinement.json').write_text(json.dumps(receipts,indent=2));print('CR053_SURFACE_PASS',json.dumps(receipts))
