"""Import owned Phase051 hero assets through real UE APIs. Old assets remain untouched."""
import json
from pathlib import Path
import unreal
p=Path(unreal.Paths.project_dir());out=p.parent/'.environment-local/phase-05-1';exports=out/'exports';src=p/'ArtSource/Textures/Phase051'
root='/Game/Generated/Phase051';owner='CinderRelay.Phase051.v1'
assets=unreal.EditorAssetLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools();lib=unreal.MaterialEditingLibrary
def owned(path):
 a=assets.load_asset(path) if assets.does_asset_exist(path) else None
 if a:assert assets.get_metadata_tag(a,'CR.GeneratedBy')==owner,path
 return a
def save(a):assets.set_metadata_tag(a,'CR.GeneratedBy',owner);assert assets.save_loaded_asset(a);return a
def create(name,folder,cls,factory):return owned(root+'/'+folder+'/'+name) or save(tools.create_asset(name,root+'/'+folder,cls,factory))
textures={}
for item in json.loads((src/'provenance.json').read_text(encoding='utf-8-sig')):
 n='T_CR051_'+Path(item['File']).stem;tex=owned(root+'/Textures/'+n)
 if not tex:
  task=unreal.AssetImportTask();task.filename=str(src/item['File']);task.destination_path=root+'/Textures';task.destination_name=n;task.automated=True;task.save=True;tools.import_asset_tasks([task]);tex=assets.load_asset(root+'/Textures/'+n);assert tex
  tex.set_editor_property('srgb',item['Channel']=='Diffuse');tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP if item['Channel']=='nor_dx' else unreal.TextureCompressionSettings.TC_DEFAULT if item['Channel']=='Diffuse' else unreal.TextureCompressionSettings.TC_MASKS);save(tex)
 textures[(item['Asset'],item['Channel'])]=tex
materials={}
for name,color,metal,rough in [('Wood',(.65,.65,.65),0,.5),('Steel',(.18,.23,.27),.8,.4),('Brass',(.32,.19,.065),.75,.4),('Rubber',(.024,.03,.028),0,.8),('Lens',(.055,.22,.18),.05,.1),('Reticle',(.04,.8,.32),0,.5)]:
 path=root+'/Materials/M_CR051_'+name;m=owned(path)
 if not m:
  m=create('M_CR051_'+name,'Materials',unreal.Material,unreal.MaterialFactoryNew())
  def node(cls):return lib.create_material_expression(m,cls)
  def val(x):
   n=node(unreal.MaterialExpressionConstant);n.set_editor_property('r',x);return n
  def col(x):
   n=node(unreal.MaterialExpressionConstant3Vector);n.set_editor_property('constant',unreal.LinearColor(*x,1));return n
  def link(a,output,b,input):assert lib.connect_material_expressions(a,output,b,input),(name,output,input)
  def prop(a,out,which):assert lib.connect_material_property(a,out,which)
  def sample(key,channel):
   n=node(unreal.MaterialExpressionTextureSample);n.set_editor_property('texture',textures[(key,channel)]);n.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if channel=='nor_dx' else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR if channel=='Diffuse' else unreal.MaterialSamplerType.SAMPLERTYPE_MASKS);return n
  base=col(color);rough_node=val(rough)
  if name in ('Wood','Steel'):
   key='wood_table_001' if name=='Wood' else 'rusty_metal_02';diff=sample(key,'Diffuse');arm=sample(key,'arm');normal=sample(key,'nor_dx')
   tint=node(unreal.MaterialExpressionMultiply);link(diff,'RGB' if name=='Wood' else 'R',tint,'A');link(base,'',tint,'B');base=tint
   if name=='Steel':
    bias=node(unreal.MaterialExpressionAdd);link(base,'',bias,'A');link(col((.045,.06,.07)),'',bias,'B');base=bias
   rough_mul=node(unreal.MaterialExpressionMultiply);link(arm,'G',rough_mul,'A');link(val(.3),'',rough_mul,'B');rough_add=node(unreal.MaterialExpressionAdd);link(rough_mul,'',rough_add,'A');link(val(.32 if name=='Wood' else .24),'',rough_add,'B');rough_node=rough_add
   blend=node(unreal.MaterialExpressionLinearInterpolate);link(col((0,0,1)),'',blend,'A');link(normal,'RGB',blend,'B');link(val(.3 if name=='Wood' else .2),'',blend,'Alpha');prop(blend,'',unreal.MaterialProperty.MP_NORMAL)
  prop(base,'',unreal.MaterialProperty.MP_BASE_COLOR);prop(val(metal),'',unreal.MaterialProperty.MP_METALLIC);prop(rough_node,'',unreal.MaterialProperty.MP_ROUGHNESS)
  if name=='Lens':
   m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);m.set_editor_property('two_sided',True);prop(val(.08),'',unreal.MaterialProperty.MP_OPACITY)
  if name=='Reticle':
   m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);em=node(unreal.MaterialExpressionMultiply);link(base,'',em,'A');link(val(2.5),'',em,'B');prop(em,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
  lib.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH);lib.recompile_material(m);save(m)
 materials['CR051_'+name]=m
manifest=json.loads((exports/'rook-manifest.json').read_text());meshes={};receipt=[]
for spec in manifest['meshes']:
 name=spec['name'];mesh=owned(root+'/Meshes/'+name)
 if not mesh or '-cr051reimport' in unreal.SystemLibrary.get_command_line().lower():
  ui=unreal.FbxImportUI();ui.automated_import_should_detect_type=False;ui.import_mesh=True;ui.import_as_skeletal=False;ui.import_animations=False;ui.import_materials=False;ui.import_textures=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
  d=ui.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.force_front_x_axis=False
  task=unreal.AssetImportTask();task.filename=str(exports/(name+'.fbx'));task.destination_path=root+'/Meshes';task.destination_name=name;task.options=ui;task.automated=True;task.save=True;task.replace_existing=True;task.replace_existing_settings=True;tools.import_asset_tasks([task]);mesh=assets.load_asset(root+'/Meshes/'+name);assert mesh,name
  slots=list(mesh.get_editor_property('static_materials'))
  for slot in slots:
   key=str(slot.get_editor_property('imported_material_slot_name'));assert key in materials,key;slot.set_editor_property('material_interface',materials[key])
  mesh.set_editor_property('static_materials',slots)
 socket_name='SightAnchor_Iron' if name.endswith('Rook5') else 'SightAnchor_Optic';definition=manifest['sights'][socket_name]
 socket=mesh.find_socket(socket_name)
 if not socket:socket=unreal.StaticMeshSocket(outer=mesh);socket.set_editor_property('socket_name',socket_name);mesh.add_socket(socket)
 socket.set_editor_property('relative_location',unreal.Vector(*definition['location']));socket.set_editor_property('relative_rotation',unreal.Rotator());save(mesh)
 bounds=mesh.get_bounds();dims=[2*bounds.box_extent.x,2*bounds.box_extent.y,2*bounds.box_extent.z]
 assert all(abs(a-b)<max(.25,b*.01) for a,b in zip(dims,spec['dimensions_cm'])),(name,dims,spec['dimensions_cm'])
 receipt.append({'mesh':mesh.get_path_name(),'bounds_cm':dims,'source_triangles':spec['triangles'],'socket':socket_name,'socket_position':str(socket.relative_location),'materials':len(mesh.get_editor_property('static_materials'))});meshes[name]=mesh
bp=assets.load_asset('/Game/Generated/Phase02/Blueprints/BP_CRCombatCharacter');assert bp;cdo=unreal.get_default_object(bp.generated_class());cdo.weapon_view.set_editor_property('rook_appearance',meshes['SM_CR051_Rook5']);cdo.weapon_view.set_editor_property('survey_appearance',meshes['SM_CR051_SurveyOptic']);cdo.weapon_view.set_editor_property('sight_eye_relief',28.0);unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert assets.save_loaded_asset(bp)
(out/'hero-import.json').write_text(json.dumps({'meshes':receipt,'materials':{k:v.get_path_name() for k,v in materials.items()},'textures':len(textures),'rollback_unchanged':True},indent=2));unreal.log('CR051_HERO_IMPORT_PASS '+str(receipt));unreal.SystemLibrary.quit_editor()
