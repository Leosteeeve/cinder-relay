"""Read-only native reopen validation for the independently saved title stage."""
import hashlib
import json
import struct
from pathlib import Path
import bpy

SRC=Path(__file__).resolve().parent
ROOT=SRC.parents[2]
ART=ROOT/'ArtSource/Interface/Phase055'
assert Path(bpy.data.filepath).name=='CR055_TheLastSignal.blend',bpy.data.filepath
names={o.name for o in bpy.data.objects}
for required in ('CR055_LandscapeCamera','CR055_PortraitCamera','Signal head shell','Atmospheric depth','Editable station label'):
    assert required in names,required
assert bpy.data.objects['Editable station label'].data.body=='RELAY NINE'
unpacked=[]
for img in bpy.data.images:
    if img.source=='FILE' and not img.packed_file:unpacked.append(img.filepath)
for font in bpy.data.fonts:
    if font.filepath not in ('','<builtin>','Bfont') and not font.packed_file:unpacked.append(font.filepath)
assert not unpacked,unpacked
specs={
 'CR055_KeyArt_Landscape.png':((2560,1440),'Promotional original Blender plate'),
 'CR055_MenuBackground.png':((1920,1080),'Runtime title-only background source; no title typography'),
 'CR055_KeyArt_Portrait.png':((1600,2400),'Promotional original Blender plate'),
 'CR055_Cover_Landscape.png':((2560,1440),'Promotional composite; editable SVG counterpart'),
 'CR055_Cover_Portrait.png':((1600,2400),'Promotional composite; editable SVG counterpart'),
 'CR055_GameIcon.png':((512,512),'Original monogram on steel'),
 'CR055_RelayMark.png':((512,512),'Original transparent monogram'),
}
files=[]
for name,(dims,role) in specs.items():
    p=ART/name;data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n',name
    actual=struct.unpack('>II',data[16:24]);assert actual==dims,(name,actual,dims)
    files.append({'path':p.relative_to(ROOT.parent).as_posix(),'dimensions':actual,'role':role,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
for p in [SRC/'CR055_TheLastSignal.blend',SRC/'create_identity.py',ART/'create_identity_graphics.py']+sorted(ART.glob('*.svg')):
    files.append({'path':p.relative_to(ROOT.parent).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
source=SRC.parent/'Phase052/CR052_YardDetail.blend'
receipt={
 'phase':'05.5','source_type':'Original AI-assisted Blender geometry/vector authoring, no image-generation service',
 'blender':bpy.app.version_string,'render_engine':bpy.context.scene.render.engine,'color_management':{'transform':bpy.context.scene.view_settings.view_transform,'look':bpy.context.scene.view_settings.look,'exposure':bpy.context.scene.view_settings.exposure},
 'objects':len(bpy.data.objects),'source_meshes':len(bpy.data.meshes),'external_unpacked_dependencies':unpacked,
 'readonly_original_kit':{'path':source.relative_to(ROOT.parent).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'appended':['SM_CR052_CableSpool','SM_CR052_MaintenanceTrolley','SM_CR052_ScrapStack','SM_CR052_ServiceCrate']},
 'cameras':{o.name:{'location':list(o.location),'rotation_radians':list(o.rotation_euler),'lens_mm':o.data.lens} for o in bpy.data.objects if o.type=='CAMERA'},
 'files':files,'native_reopen_passed':True,
 'not_proven':['Unreal runtime import/texture residency','Packaged menu function','Human artistic acceptance']}
(ART/'export-metadata.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print('CR055_IDENTITY_SOURCE_VERIFIED',json.dumps({'objects':receipt['objects'],'files':len(files),'unpacked_dependencies':len(unpacked)}))
