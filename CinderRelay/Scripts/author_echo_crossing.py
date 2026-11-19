"""Build the Echo Crossing art kit in Blender, then author and validate its native map in Unreal.

Blender: --background --factory-startup --python-exit-code 1 --python author_echo_crossing.py
Add -- --blend-only to save the editable mesh library after the source export. Reopen the .blend
with --python author_echo_crossing.py -- --verify-blend to compare all eight meshes and materials.
Unreal: -run=pythonscript -script=.../author_echo_crossing.py -CR02AuthorEcho
Omit the author flag for read-only reload verification. -CR02EchoViews uses a real Editor viewport.
For an existing Echo map, -CR02MoorLaunch applies the moored vessel, reeds and scenic bank override
without rebuilding the level. -CR02CheckMooring repeats just its native validation.
"""
import ast
import hashlib
import json
import math
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT.parent / '.environment-local/chapter-02'
EXPORT = OUT / 'exports'
ROOT = '/Game/Generated/Chapter02'
MAP = ROOT + '/Maps/L_CH02_EchoCrossing'
TAG = 'CR02_EchoCrossing'
MODE = '/Game/Generated/Phase02/Blueprints/BP_CRCombatGameMode.BP_CRCombatGameMode_C'
STATIONS = ((0,'LineTap',(1570,250,125),180),(4,'Log',(3020,930,125),-90),
            (1,'ArchivePlate',(4960,-405,125),90),(2,'Aerial',(7670,-150,545),180),
            (3,'Transmit',(8330,260,545),180))
ROUTE = [(-1250,0),(0,0),(800,0),(1400,250),(1640,430),(2100,430),(3010,430),(3020,760),
         (3020,430),(4060,430),(4390,430),(4580,-235),(4960,-235),(5040,-80),(5520,0),
         (5890,0),(7180,0),(7350,0),(7500,-150),(7500,100),(7920,260),(8160,260)]
BASE_ART = {'AerialDish', 'BreakawayArm', 'PorcelainCatch', 'Riverbanks', 'PierBent', 'PipeRail', 'ArchiveChart'}
ART = BASE_ART | {'SurveyLaunch'}
BLEND = PROJECT / 'ArtSource/Blender/Chapter02/CR02_EchoCrossing.blend'
PALETTE = dict(Steel=(.23,.29,.30), Dark=(.045,.068,.073), Paint=(.14,.27,.28), Pale=(.59,.58,.43),
               Amber=(.74,.35,.055), Concrete=(.33,.35,.32), Clay=(.28,.19,.105),
               Reed=(.19,.23,.12), Silt=(.18,.16,.105), Signal=(1,.47,.05), Wood=(.28,.19,.11),
               Rust=(.35,.15,.067), Glass=(.037,.092,.104))


def model_kit():
    import bpy
    from mathutils import Vector
    EXPORT.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = .01
    mats = {}
    for key, color in PALETTE.items():
        mat = bpy.data.materials.new('Echo_' + key)
        mat.diffuse_color = (*color, 1)
        mats[key] = mat
    ns = dict(bpy=bpy, Vector=Vector, math=math, scene=scene, parts=[], mats=mats)
    blend_only='--blend-only' in sys.argv
    launch_source='--launch-and-blend' in sys.argv
    lib = PROJECT / 'ArtSource/Blender/Phase052/polish_environment.py'
    wanted = {'reg','mesh','bevel','box','beam','lathe','cyl','tube'}
    tree = ast.parse(lib.read_text(encoding='utf8'))
    exec(compile(ast.Module([n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted], []),
                 str(lib), 'exec'), ns)
    box, beam, lathe, cyl, tube, mesh = [ns[k] for k in ('box','beam','lathe','cyl','tube','mesh')]
    manifest = {}

    def finish(name):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in ns['parts']:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = ns['parts'][0]
        bpy.ops.object.join()
        obj = bpy.context.object
        obj.name = 'SM_CR02_' + name
        scene.cursor.location = (0,0,0)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name='SurfaceUV')
        for face in obj.data.polygons:
            axes = ((1,2),(0,2),(0,1))[max(range(3), key=lambda i: abs(face.normal[i]))]
            for loop in face.loop_indices:
                v = obj.data.vertices[obj.data.loops[loop].vertex_index].co
                uv.data[loop].uv = (v[axes[0]]/160,v[axes[1]]/160)
        if not blend_only and (not launch_source or name=='SurveyLaunch'):
            bpy.ops.export_scene.fbx(filepath=str(EXPORT / (obj.name + '.fbx')), use_selection=True, object_types={'MESH'},
                                     axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False,mesh_smooth_type='FACE')
        obj.data.calc_loop_triangles()
        manifest[name] = dict(dimensions=list(obj.dimensions), triangles=len(obj.data.loop_triangles))
        obj.hide_set(True)
        ns['parts'].clear()

    # Panelized parabolic collector on a cast azimuth yoke. The shaft is placed by the level,
    # and its pivot stays fixed when the station controller rotates the entire head.
    cyl('Bearing base',(0,0,19),62,38,'Paint','Z',32)
    for z in (8,28):
        cyl('Machined race',(0,0,z),67,7,'Steel','Z',36)
    for y in (-52,52):
        beam('Yoke fork', (0,y,36), (-30,y,164), 20,16,'Steel')
        cyl('Elevation trunnion',(-29,y,164),25,20,'Amber','Y',24)
    axis = Vector((.78,0,.63)).normalized()
    vertical = Vector((-axis.z,0,axis.x))
    horizontal = Vector((0,1,0))
    center = Vector((-20,0,238))

    def dish(r, theta, inset=0):
        return center + r*(math.cos(theta)*horizontal+math.sin(theta)*vertical) + axis*(r*r/650+inset)

    for segment in range(20):
        a = segment*math.tau/20
        b = (segment+1)*math.tau/20
        for low, high in ((8,68),(68,133),(133,202),(202,252)):
            points = [tuple(dish(radius,theta)) for radius,theta in ((low,a),(high,a),(high,b),(low,b))]
            points += [tuple(dish(radius,theta,-3)) for radius,theta in ((low,a),(high,a),(high,b),(low,b))]
            face = mesh('Pressed alloy petal',points,[(0,1,2,3),(7,6,5,4),(4,5,1,0),(1,5,6,2),(2,6,7,3),(3,7,4,0)],
                        'Pale' if (segment+int(low))%4 else 'Steel')
        tube('Back rib',[dish(r,a,-8) for r in (9,68,133,202,253)],4.5,'Dark')
    for r in (133,251):
        tube('Rolled reflector hoop',[dish(r,i*math.tau/48,-3) for i in range(49)],4,'Steel')
    focus = center + axis*165
    for i in range(3):
        beam('Feed support',dish(228,(i+.25)*math.tau/3),focus,6,6,'Steel')
    box('Receiver feed',focus,(35,27,27),'Amber',4)
    beam('Tilt shaft',(-29,0,164),center,58,44,'Paint')
    finish('AerialDish')

    # Local origin at the hinge. The native actor lifts this in a single non-repeating motion.
    box('Barrier beam',(0,159,0),(21,318,22),'Paint',3)
    cyl('Hinge boss',(0,0,0),25,46,'Steel','X',20)
    for y in range(42,306,44):
        box('Warning band',(0,y,1),(23,20,23),'Amber',1)
        box('Lower grille picket',(0,y,-62),(9,9,111),'Steel',2)
    box('Lower rail',(0,163,-115),(12,273,12),'Dark',2)
    box('Ceramic carrier',(-20,160,7),(32,51,18),'Dark',2)
    finish('BreakawayArm')
    box('Enamel release block',(0,0,0),(19,62,60),'Amber',5)
    for x in (-10,10):
        box('Luminous catch face',(x,0,0),(2,45,43),'Signal',1)
        for s in (-1,1):
            beam('Raised cross',(x+s, -13,-s*13),(x+s,13,s*13),4,4,'Dark')
    finish('PorcelainCatch')

    # A complete row of high and low shore elevations makes a flood valley in every viewing direction.
    for bank in (-1,1):
        verts = []
        rows = 9
        count = 75
        for i in range(count):
            x = -19000+i*580
            shore = 2150+410*math.sin(x*.0007+bank*2)+180*math.sin(x*.0017)
            heights = [-260,-206,-180,-127,-55,100,365,870,1190]
            offsets = [-140,0,110,230,420,840,1600,3300,6300]
            for j in range(rows):
                oscillation = (math.sin(x*.0012+j*.71)*.54+math.sin(x*.00046+bank+j)*.46)
                zz = heights[j]+oscillation*(8+j*j*7)
                yy = bank*(shore+offsets[j] + oscillation*(j*j*8))
                verts.append((x,yy,zz))
        for strip,mat in ((range(0,2),'Silt'),(range(2,4),'Clay'),(range(4,8),'Reed')):
            faces = []
            for i in range(count-1):
                for j in strip:
                    p = i*rows+j
                    face=(p,p+rows,p+rows+1,p+1)
                    faces.append(face if bank>0 else tuple(reversed(face)))
            obj = mesh('Eroded floodbank',verts,faces,mat)
            for f in obj.data.polygons:
                f.use_smooth = True
    finish('Riverbanks')

    for y in (-122,122):
        box('Water-stained pile',(0,y,-215),(76,76,390),'Concrete',8)
        box('Dark tide mark',(0,y,-213),(79,79,18),'Silt',2)
        box('Pile shoe',(0,y,-378),(94,94,36),'Dark',3)
    box('Concrete cap',(0,0,-35),(115,348,70),'Concrete',7)
    for y in (-105,105):
        box('Elastomer pad',(0,y,-4),(79,58,8),'Dark',1)
    finish('PierBent')
    for x in (-143,143):
        box('Shoe',(x,0,3),(20,20,6),'Steel',1)
        cyl('Galvanised upright',(x,0,57),4,108,'Paint','Z',12)
    for z,r in ((55,3.2),(108,4.5)):
        cyl('Rail',(0,0,z),r,300,'Paint' if z<100 else 'Pale','X',12)
    box('Toe plate',(0,0,8),(300,5,14),'Dark',1)
    finish('PipeRail')
    # Engraved physical radial chart with a single amber bearing at 120 degrees.
    box('Instrument back',(0,0,0),(11,235,156),'Dark',4)
    box('Printed chart stock',(7,0,0),(3,221,144),'Pale',1)
    for radius in (20,39,56):
        tube('Calibration ring',[(10,radius*math.sin(t*math.tau/48),radius*math.cos(t*math.tau/48))
                                 for t in range(49)],1.1,'Paint',6)
    for t in range(12):
        a=t*math.tau/12
        beam('Bearing graduation',(10,63*math.sin(a),63*math.cos(a)),(10,55*math.sin(a),55*math.cos(a)),2,2,'Steel')
    beam('Marked vector',(12,0,0),(12,51,-29),4,4,'Amber')
    finish('ArchiveChart')
    # Survey launch: hard-chine hull, raised sheer and a raked pilot house on the aft half.
    # Waterline z=0, local +X is the bow. Structural members are welded to the deck and cabin.
    sections=[(-431,99,84),(-389,125,83),(-250,136,80),(-65,138,81),(135,132,86),
              (252,109,94),(334,73,107),(393,32,123),(425,2,141)]
    for side in (-1,1):
        previous=None
        for scale,z,mat in ((.10,-64,'Dark'),(.75,-46,'Rust'),(.95,-9,'Rust'),
                            (.975,6,'Dark'),(1,.74,'Paint'),(1.01,.82,'Pale'),(1,1,'Paint')):
            row=[(x,side*w*scale,zz*z if 0<z<=1 else z) for x,w,zz in sections]
            if previous:
                vs=previous+row
                n=len(sections)
                faces=[(i,i+n,i+n+1,i+1) for i in range(n-1)]
                mesh('Riveted hull course',vs,faces if side==1 else [f[::-1] for f in faces],mat)
            previous=row
        tube('Rub rail',[(x,side*w,zz+1) for x,w,zz in sections],4.2,'Dark')
        for x in (-390,-311,-231,-145,-63,23,103,183):
            w=127 if x<150 else 119
            box('Welded repair strap',(x,side*w,46),(12,5,44),'Rust',1)
        for x in (197,236):
            beam('Survey stripe',(x,side*122,44),(x+16,side*117,68),6,5,'Amber')
    n=len(sections)
    vs=[(x,side*w,zz-2) for side in (-1,1) for x,w,zz in sections]
    mesh('Continuous weather deck',vs,[(i,i+1,n+i+1,n+i) for i in range(n-1)],'Wood')
    mesh('Flat stern transom',[(-431,-99,84),(-431,99,84),(-431,76,-46),(-431,-76,-46)],[(0,1,2,3)],'Paint')
    for y in range(-99,100,22):
        box('Aft deck seam',(-309,y,83),(239,2,3),'Dark',.5)
    box('Wheelhouse coaming',(-72,0,105),(304,191,48),'Paint',7)
    box('Pilot house lower panels',(-72,0,144),(289,189,62),'Pale',7)
    cabin=[(-213,-94,166), (75,-94,166),(75,94,166),(-213,94,166),
           (-202,-84,247),(48,-84,247),(48,84,247),(-202,84,247)]
    mesh('Four glazed wheelhouse sides',cabin,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'Glass')
    for i in range(4):
        beam('Window corner frame',cabin[i],cabin[i+4],8,9,'Pale')
    for y in (-92,92):
        for x in (-127,-39):
            beam('Cabin mullion',(x,y,165),(x+2,y*.92,247),7,8,'Pale')
    beam('Centre glazing bar',(74,0,165),(48,0,247),7,8,'Pale')
    box('Overhung canopy',(-77,0,251),(290,199,14),'Paint',6)
    box('Wheelhouse skylight',(-103,0,262),(86,65,14),'Steel',4)
    for y in (-117,117):
        tube('Forward pulpit',[(90,y,89),(90,y,149),(131,y,154),(242,y*.85,159),
                               (324,y*.57,169),(368,y*.32,171),(379,y*.25,131)],4,'Pale')
        for x,w,h in ((165,114,88),(258,92,98),(327,64,107)):
            cyl('Stanchion',(x,w*(1 if y>0 else -1),h+31),3.3,62,'Steel','Z',12)
    cyl('Reel barrel',(-319,0,146),31,96,'Dark','Y',28)
    for y in (-54,54):
        cyl('Reel flange',(-319,y,146),48,8,'Rust','Y',28)
        box('Reel pedestal',(-319,y*1.15,112),(37,16,58),'Paint',3)
    for y in range(-42,43,9):
        cyl('Wound survey wire',(-319,y,146),37,5,'Steel','Y',24)
    tube('Damaged mast',[(-158,0,259),(-158,0,365),(-178,8,409),(-208,13,468)],6,'Pale')
    tube('Whip',[(-209,13,468),(-221,15,496),(-238,17,515)],2.4,'Dark')
    beam('Signal spar',(-178,-73,406),(-178,65,412),6,7,'Steel')
    cyl('Signal lantern',(-179,62,418),10,14,'Amber','Z',16)
    for y in (-83,83):
        tube('Shroud',[(-359,y,88),(-245,y*.42,230),(-178,8,409)],2.3,'Dark')
    for x,y,z in ((315,-56,111),(-389,-75,85),(310,56,112),(-389,75,85)):
        cyl('Bollard',(x,y,z+9),7,19,'Steel','Z',14)
        box('Horn cleat',(x,y,z+19),(29,12,8),'Steel',2)
    finish('SurveyLaunch')
    assert manifest.keys() == ART and all(row['triangles'] < 25000 for row in manifest.values())
    if blend_only or launch_source:
        source=json.loads((EXPORT/'art.json').read_text())
        for name in BASE_ART:
            assert abs(manifest[name]['triangles']-source[name]['triangles'])==0, name
            assert max(abs(a-b) for a,b in zip(manifest[name]['dimensions'],source[name]['dimensions']))<.01, name
        (OUT/'before-blend-sha256.json').write_text(json.dumps(echo_output_hashes(),indent=2))
        (EXPORT/'launch-art.json').write_text(json.dumps({'SurveyLaunch':manifest['SurveyLaunch']},indent=2))
        BLEND.parent.mkdir(parents=True,exist_ok=True)
        bpy.context.preferences.filepaths.save_version=0
        # Each asset keeps its native origin. Showing one named collection at a time avoids
        # the valley's forty-thousand-centimeter bounds hiding the tabletop and machinery parts.
        for name in sorted(ART):
            obj=bpy.data.objects['SM_CR02_'+name]
            obj.hide_set(False)
            group=bpy.data.collections.new(name)
            scene.collection.children.link(group)
            old=list(obj.users_collection)
            group.objects.link(obj)
            for c in old:
                c.objects.unlink(obj)
            group.hide_viewport=name!='SurveyLaunch'
            obj['Source']='Original Echo Crossing geometry, centimeters'
            obj['Export_name']=obj.name+'.fbx'
        launch=bpy.data.objects['SM_CR02_SurveyLaunch']
        bpy.context.view_layer.objects.active=launch
        launch.select_set(True)
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type=='VIEW_3D':
                    s=area.spaces.active
                    s.region_3d.view_distance=1360
                    s.region_3d.view_location=(0,0,160)
                    s.shading.color_type='MATERIAL'
        bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    else:
        (EXPORT/'art.json').write_text(json.dumps(manifest,indent=2))
    print('CR02_ECHO_SOURCE PASS', manifest)


def echo_output_hashes():
    files=[EXPORT/('SM_CR02_'+name+'.fbx') for name in BASE_ART]
    content=PROJECT/'Content/Generated/Chapter02'
    files += [p for p in content.rglob('*.uasset') if p.stem!='SM_CR02_SurveyLaunch']+list(content.rglob('*.umap'))
    assert len(files)==20,(len(files),files)
    return {str(p.relative_to(PROJECT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def verify_blend():
    import bpy
    assert Path(bpy.data.filepath).resolve()==BLEND.resolve()
    source=json.loads((EXPORT/'art.json').read_text())
    if (EXPORT/'launch-art.json').is_file():
        source.update(json.loads((EXPORT/'launch-art.json').read_text()))
    actual={}
    for obj in bpy.context.scene.objects:
        key=obj.name.removeprefix('SM_CR02_')
        assert key in ART and obj.type=='MESH' and len(obj.users_collection)==1 and obj.users_collection[0].name==key,obj
        assert obj.location.length<.001 and obj.rotation_euler.to_matrix().is_identity and all(abs(i-1)<.0001 for i in obj.scale),key
        obj.data.calc_loop_triangles()
        tri=len(obj.data.loop_triangles)
        dim=list(obj.dimensions)
        slots=[m.name for m in obj.data.materials]
        assert tri==source[key]['triangles'] and max(abs(a-b) for a,b in zip(dim,source[key]['dimensions']))<.01,key
        assert slots and all(n.startswith('Echo_') and n[5:] in PALETTE for n in slots),key
        actual[key]=dict(triangles=tri,dimensions_cm=dim,material_slots=slots)
    assert set(actual)==ART and len(actual)==8
    hashes=echo_output_hashes()
    before=json.loads((OUT/'before-blend-sha256.json').read_text())
    # The additive placement subsequently changes the map alone. Preserve its pre-placement receipt.
    stable=[key for key,digest in hashes.items() if before.get(key)==digest]
    assert all(key in stable for key in hashes if not key.endswith('.umap'))
    (OUT/'blend-verified.json').write_text(json.dumps(dict(native=str(BLEND),meshes=actual,
                                                 unchanged_fbx_and_unreal=len(stable)),indent=2))
    print('CR02_ECHO_BLEND_REOPEN PASS',len(actual),'meshes;',len(stable),'unchanged content files')


def editor_assets(u, apply, keys=ART):
    library = u.EditorAssetLibrary
    tools = u.AssetToolsHelpers.get_asset_tools()
    edit = u.MaterialEditingLibrary

    def mat(name):
        path = ROOT+'/Materials/'+name
        if library.does_asset_exist(path):
            result = library.load_asset(path)
            assert library.get_metadata_tag(result,'CR.Owner') == TAG, path
            return result, False
        assert apply, path
        result = tools.create_asset(name, ROOT+'/Materials',u.Material,u.MaterialFactoryNew())
        assert result, path
        library.set_metadata_tag(result,'CR.Owner',TAG)
        return result, True

    def scalar(m,value,prop):
        n=edit.create_material_expression(m,u.MaterialExpressionConstant)
        n.set_editor_property('r',value)
        assert edit.connect_material_property(n,'',prop)

    palette={k:library.load_asset('/Game/Generated/Phase052/Materials/MI_CR052_'+k)
             for k in ('Dark','Steel','Paint','Pale','Amber','Concrete','Wood','Rust','Glass')}
    for key in ('Clay','Reed','Silt','Signal'):
        m, fresh = mat('M_Echo'+key)
        if fresh:
            n=edit.create_material_expression(m,u.MaterialExpressionConstant3Vector)
            n.set_editor_property('constant',u.LinearColor(*PALETTE[key],1))
            colour=n
            if key!='Signal':
                # Low-frequency depositional bands follow world space across the long shoreline mesh.
                wp=edit.create_material_expression(m,u.MaterialExpressionWorldPosition)
                band=edit.create_material_expression(m,u.MaterialExpressionCustom)
                pin=u.CustomInput()
                pin.set_editor_property('input_name','P')
                band.set_editor_property('inputs',[pin])
                band.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT1)
                band.set_editor_property('code','return .85+.15*sin(P.y*.021+sin(P.x*.0018)*2.3)'
                                          '+.10*sin(P.x*.0048+P.y*.0028)+.065*sin(P.z*.092+P.y*.018);')
                assert edit.connect_material_expressions(wp,'',band,'P')
                colour=edit.create_material_expression(m,u.MaterialExpressionMultiply)
                assert edit.connect_material_expressions(n,'',colour,'A') and edit.connect_material_expressions(band,'',colour,'B')
            assert edit.connect_material_property(colour,'',u.MaterialProperty.MP_BASE_COLOR)
            scalar(m,.36 if key=='Signal' else .93,u.MaterialProperty.MP_ROUGHNESS)
            if key=='Signal':
                assert edit.connect_material_property(n,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
            edit.recompile_material(m)
            assert library.save_loaded_asset(m)
        palette[key]=m
    water,fresh=mat('M_EchoFloodwater')
    if fresh:
        pos=edit.create_material_expression(water,u.MaterialExpressionWorldPosition)
        time=edit.create_material_expression(water,u.MaterialExpressionTime)
        normal=edit.create_material_expression(water,u.MaterialExpressionCustom)
        pins=[]
        for key in ('P','T'):
            pin=u.CustomInput()
            pin.set_editor_property('input_name',key)
            pins.append(pin)
        normal.set_editor_property('inputs',pins)
        normal.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3)
        normal.set_editor_property('code',
            'float2 q=P.xy; float r=sin(dot(q,float2(.032,.017))+T*1.1); '
            'float s=cos(dot(q,float2(.011,-.045))-T*.74); '
            'float t=sin(dot(q,float2(.002,.003))+T*.24); '
            'return normalize(float3(r*.105+s*.035+t*.055,s*.105+r*.033,1));')
        assert edit.connect_material_expressions(pos,'',normal,'P') and edit.connect_material_expressions(time,'',normal,'T')
        assert edit.connect_material_property(normal,'',u.MaterialProperty.MP_NORMAL)
        c=edit.create_material_expression(water,u.MaterialExpressionConstant3Vector)
        c.set_editor_property('constant',u.LinearColor(.034,.105,.113,1))
        assert edit.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
        scalar(water,.235,u.MaterialProperty.MP_ROUGHNESS)
        scalar(water,.40,u.MaterialProperty.MP_METALLIC)
        edit.recompile_material(water)
        assert library.save_loaded_asset(water)
    palette['Water']=water
    assert all(palette.values())
    kit={}
    for key in sorted(keys):
        name='SM_CR02_'+key
        path=ROOT+'/Meshes/'+name
        result=library.load_asset(path) if library.does_asset_exist(path) else None
        if result:
            assert library.get_metadata_tag(result,'CR.Owner')==TAG, path
        if apply:
            fbx=EXPORT/(name+'.fbx')
            digest=hashlib.sha256(fbx.read_bytes()).hexdigest()
            if not result or library.get_metadata_tag(result,'CR.FBX')!=digest:
                ui=u.FbxImportUI()
                ui.automated_import_should_detect_type=False
                ui.import_mesh=True
                ui.import_as_skeletal=False
                ui.import_animations=False
                ui.import_materials=False
                ui.import_textures=False
                ui.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH
                options=ui.static_mesh_import_data
                options.combine_meshes=True
                options.auto_generate_collision=key=='PipeRail'
                options.convert_scene=True
                options.convert_scene_unit=True
                task=u.AssetImportTask()
                task.filename=str(fbx)
                task.destination_path=ROOT+'/Meshes'
                task.destination_name=name
                task.options=ui
                task.automated=True
                task.replace_existing=result is not None
                task.replace_existing_settings=True
                task.save=False
                tools.import_asset_tasks([task])
                result=library.load_asset(path)
                assert result, path
                slots=list(result.get_editor_property('static_materials'))
                for slot in slots:
                    label=str(slot.get_editor_property('imported_material_slot_name'))
                    assert label.startswith('Echo_'), label
                    slot.set_editor_property('material_interface',palette[label.removeprefix('Echo_')])
                result.set_editor_property('static_materials',slots)
                library.set_metadata_tag(result,'CR.Owner',TAG)
                library.set_metadata_tag(result,'CR.FBX',digest)
                assert library.save_loaded_asset(result)
        assert result, path
        kit[key]=result
    return kit,palette


def run_editor():
    import unreal as u
    OUT.mkdir(parents=True,exist_ok=True)
    levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
    actors=u.get_editor_subsystem(u.EditorActorSubsystem)
    subsystem=u.get_editor_subsystem(u.UnrealEditorSubsystem)
    lib=u.EditorAssetLibrary
    flags=u.SystemLibrary.get_command_line().lower()
    if '-cr02echoviews' in flags:
        capture_views(u,levels,actors)
        return
    if '-cr02moorlaunch' in flags or '-cr02checkmooring' in flags:
        author_mooring(u,levels,actors,subsystem,'-cr02moorlaunch' in flags)
        return
    apply='-cr02authorecho' in flags
    kit,pal=editor_assets(u,apply)
    if lib.does_asset_exist(MAP):
        assert levels.load_level(MAP)
        assert any(a.get_actor_label()=='Echo_Spawn' and TAG in [str(t) for t in a.tags]
                   for a in actors.get_all_level_actors()), 'Existing map has no ownership marker'
    else:
        assert apply
        lib.make_directory(ROOT+'/Maps')
        assert levels.new_level(MAP,False)
        marker=actors.spawn_actor_from_class(u.PlayerStart,u.Vector(-1250,0,105))
        assert marker
        marker.set_actor_label('Echo_Spawn')
        marker.tags=[TAG]
        assert levels.save_current_level()
    world=subsystem.get_editor_world()
    existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
    built=set()
    cube=lib.load_asset('/Engine/BasicShapes/Cube')
    cylinder=lib.load_asset('/Engine/BasicShapes/Cylinder')

    def entity(name,cls,pos,rot=(0,0,0)):
        label='Echo_'+name
        a=existing.get(label)
        if a:
            assert isinstance(a,cls) and TAG in [str(t) for t in a.tags],label
        else:
            a=actors.spawn_actor_from_class(cls,u.Vector(*pos))
            assert a,label
            a.set_actor_label(label)
            a.tags=[TAG]
            existing[label]=a
        assert label not in built,label
        built.add(label)
        a.modify()
        a.set_actor_location(u.Vector(*pos),False,False)
        a.set_actor_rotation(u.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]),False)
        return a

    def prop(name,mesh,pos,scale=(1,1,1),rot=(0,0,0),material=None,solid=False):
        a=entity(name,u.StaticMeshActor,pos,rot)
        a.set_actor_scale3d(u.Vector(*scale))
        c=a.static_mesh_component
        c.set_static_mesh(mesh)
        if material:
            c.set_material(0,pal[material])
        c.set_collision_profile_name('BlockAll' if solid else 'NoCollision')
        c.set_editor_property('can_ever_affect_navigation',False)
        a.set_actor_enable_collision(solid)
        return a

    def block(name,pos,size,material='Concrete',solid=True,rot=(0,0,0)):
        return prop(name,cube,pos,tuple(v/100 for v in size),rot,material,solid)

    def deck(name,left,right,south,north,top=0,material='Concrete',depth=40):
        return block(name,((left+right)/2,(south+north)/2,top-depth/2),(right-left,north-south,depth),material)

    def incline(name,start,end,y,width,low,high,material='Steel'):
        slope=math.degrees(math.atan2(high-low,end-start))
        return block(name,((start+end)/2,y,(low+high)/2-14/math.cos(math.radians(slope))),
                     (math.hypot(end-start,high-low)+8,width,28),material,True,(slope,0,0))

    def rail(name,start,end):
        dx,dy,dz=(end[i]-start[i] for i in range(3))
        length=math.sqrt(dx*dx+dy*dy+dz*dz)
        count=max(1,round(length/300))
        yaw=math.degrees(math.atan2(dy,dx))
        pitch=math.degrees(math.atan2(dz,math.hypot(dx,dy)))
        for i in range(count):
            p=tuple(start[j]+(end[j]-start[j])*(i+.5)/count for j in range(3))
            prop(f'{name}Rail{i}',kit['PipeRail'],p,(length/count/300,1,1),(pitch,yaw,0),solid=True)

    def rod(name,start,end,width,depth,mat='Steel'):
        dx,dy,dz=(end[i]-start[i] for i in range(3))
        pitch=math.degrees(math.atan2(dz,math.hypot(dx,dy)))
        yaw=math.degrees(math.atan2(dy,dx))
        p=tuple((start[i]+end[i])/2 for i in range(3))
        return block(name,p,(math.dist(start,end),width,depth),mat,False,(pitch,yaw,0))

    def model(path):
        a=lib.load_asset('/Game/Generated/'+path)
        assert a,path
        return a

    def sign(name,words,pos,yaw,width,size=19):
        x,y,z=pos
        r=math.radians(yaw)
        back=(x-3.5*math.cos(r),y-3.5*math.sin(r),z)
        block(name+'Back',back,(6,width,size*2.85),'Dark',False,(0,yaw,0))
        a=entity(name,u.TextRenderActor,pos,(0,yaw,0))
        t=a.text_render
        t.set_text(words)
        t.set_world_size(size)
        t.set_text_render_color(u.Color(240,220,167,255))
        t.set_horizontal_alignment(u.HorizTextAligment.EHTA_CENTER)
        t.set_vertical_alignment(u.VerticalTextAligment.EVRTA_TEXT_CENTER)

    def lamp(name,pos,color,lumens,radius):
        a=entity(name,u.PointLight,pos)
        c=a.light_component
        c.set_mobility(u.ComponentMobility.MOVABLE)
        c.set_intensity_units(u.LightUnits.LUMENS)
        c.set_light_color(u.LinearColor(*color,1))
        c.set_intensity(lumens)
        c.set_attenuation_radius(radius)
        c.set_editor_property('cast_shadows',False)

    if apply:
        world.get_world_settings().modify()
        world.get_world_settings().set_editor_property('default_game_mode',u.load_class(None,MODE))
        entity('Spawn',u.PlayerStart,(-1250,0,105))
        # The surrounding silt bed is recoverable by either signed flood ladder.
        deck('RiverBed',-3600,10000,-2800,2800,-245,'Silt',80)
        block('Floodwater',(5500,0,-173),(46000,28000,12),'Water',False)
        prop('Valley',kit['Riverbanks'],(0,0,0))
        for name,left,right,south,north,top,mat in (
                ('ReceivingPier',-1860,-475,-550,550,0,'Concrete'),('InletWalk',-485,535,-185,185,0,'Steel'),
                ('IntakeApron',510,2020,-560,600,0,'Concrete'),('ShortCrossing',2000,3920,-445,-95,0,'Steel'),
                ('SurveyWalk',2000,3920,290,570,0,'Steel'),('GaugeBay',2540,3400,550,1040,0,'Concrete'),
                ('ArchivePier',3840,5860,-740,740,0,'Concrete'),('TowerBase',5540,5980,-360,360,0,'Steel'),
                ('HighPlatform',7220,8600,-650,650,420,'Steel')):
            deck(name,left,right,south,north,top,mat)
        incline('TowerRamp',5820,7220,0,370,0,420)
        incline('IntakeRecovery',-98,525,-423,150,-245,0)
        incline('ArchiveRecovery',3220,3850,-580,160,-245,0)
        for name,p,q in (
                ('ArrivalBack',(-1840,-525,0),(-1840,525,0)),('ArrivalS',(-1840,-535,0),(-485,-535,0)),
                ('ArrivalN',(-1840,535,0),(-485,535,0)),('ApproachS',(-485,-176,0),(520,-176,0)),
                ('ApproachN',(-485,176,0),(520,176,0)),('IntakeN',(520,587,0),(1996,587,0)),
                ('IntakeS',(530,-545,0),(1996,-545,0)),('ShortcutSouth',(2010,-439,0),(3850,-439,0)),
                ('ShortcutNorth',(2010,-102,0),(3850,-102,0)),('SurveySouth',(2010,298,0),(3850,298,0)),
                ('SurveyOuterA',(2010,562,0),(2540,562,0)),('SurveyOuterB',(3400,562,0),(3850,562,0)),
                ('GaugeSideA',(2550,565,0),(2550,1028,0)),('GaugeSideB',(3390,565,0),(3390,1028,0)),
                ('GaugeOuter',(2550,1029,0),(3390,1029,0)),('ArchiveSouth',(3850,-730,0),(5840,-730,0)),
                ('ArchiveNorth',(3850,730,0),(5840,730,0)),('RampN',(5810,177,0),(7225,177,420)),
                ('RampS',(5810,-177,0),(7225,-177,420)),('UpperNorth',(7210,637,420),(8590,637,420)),
                ('UpperSouth',(7210,-637,420),(8590,-637,420)),('UpperEnd',(8590,-637,420),(8590,637,420)),
                ('UpperBackN',(7200,188,420),(7200,637,420)),('UpperBackS',(7200,-637,420),(7200,-188,420))):
            rail(name,p,q)
        for i,(x,y,scale_y) in enumerate(((-1200,0,2.5),(-230,0,1),(390,0,1),(720,0,2.7),
                (1750,0,2.7),(2350,-270,1),(3270,-270,1),(2350,430,.9),(3290,430,.9),(2990,870,1),
                (4040,200,2.8),(4930,-120,3.3),(5550,100,2.9))):
            prop('PierBent'+str(i),kit['PierBent'],(x,y,-36),(1,scale_y,1))
        for x in (5970,6440,6950,7360,8160,8480):
            z=max(0,min(420,(x-5820)*.3))
            for y in ((-137,137) if x<7200 else (-528,528)):
                h=z+250
                block(f'TowerChassis{x}_{y}',(x,y,-245+h/2),(55,55,h),'Paint',False)
                block(f'TowerFoot{x}_{y}',(x,y,-222),(124,124,46),'Concrete',False)
        for x0,x1 in ((7360,8160),(8160,8480)):
            for y in (-528,528):
                rod(f'TowerBrace{x0}_{y}',(x0,y,-175),(x1,y,376),25,25,'Steel')
                rod(f'TowerBraceBack{x0}_{y}',(x0,y,376),(x1,y,-175),25,25,'Steel')
        # Separate headworks, elevated forebay pipes and a visible two-bridge decision.
        for i,y in enumerate((-490,-419,-348)):
            prop('IntakeBarrel'+str(i),cylinder,(1040,y,86),(1,1,9),(90,0,0),'Paint')
            for x in (675,1060,1390):
                prop(f'IntakeFlange{i}_{x}',cylinder,(x,y,86),(1.14,1.14,.15),(90,0,0),'Steel')
        prop('IntakeDrive',model('Phase06/Meshes/ServiceCircuit/SM_CR06_CircuitDynamometer'),(1240,-351,0),(.64,.64,.64))
        for i,x in enumerate((910,1380,1750)):
            prop('IntakeCabinet'+str(i),model('Phase052/Meshes/SM_CR052_UtilityBox'),(x,535,0),(.72,.72,.72))
        for i,x in enumerate((-875,1360,4230)):
            for y in ((-588,585) if i==2 else (-488,485)):
                block(f'CarrierMast{i}_{y}',(x,y,308),(22,25,616),'Paint')
                block(f'MastCollar{i}_{y}',(x,y,485),(30,32,16),'Amber',False)
                rod(f'MastStay{i}_{y}',(x,y,450),(x+163,y,7),7,7)
            block('CarrierArm'+str(i),(x,0,600),(30,1010,21),'Paint',False)
            if i<2:
                nx=(1360,4230)[i]
                for line_y in (-365,365):
                    line=[(x+(nx-x)*k/5,line_y,601-4*125*(k/5)*(1-k/5)) for k in range(6)]
                    for k in range(5):
                        rod(f'SlungCable{i}_{line_y}_{k}',line[k],line[k+1],4,4,'Dark')
        sign('InletTitle','ECHO CROSSING',(1328,0,603),180,309,22)
        prop('ArrivingSupplies',model('Phase052/Meshes/SM_CR052_ServiceCrate'),(-1140,331,0))
        prop('JettyReel',model('Phase052/Meshes/SM_CR052_CableSpool'),(-1360,-301,0))
        lamp('IncomingDaymark',(1510,255,240),(.52,.9,1),370,390)
        for i,(lo,hi) in enumerate(((-560,-430),(-110,270),(580,600))):
            block('BoomCheek'+str(i),(1950,(lo+hi)/2,62),(114,hi-lo,124),'Concrete')
        block('BoomHinge',(1915,-430,76),(78,58,152),'Paint')
        catch=entity('BridgeCatch',u.CREchoBridgeCatch,(1915,-270,0))
        boom=catch.get_editor_property('boom')
        boom.set_static_mesh(kit['BreakawayArm'])
        # Keep the free end over the south span for either FBX handedness convention.
        boom.set_relative_scale3d(u.Vector(1,1 if kit['BreakawayArm'].get_bounds().origin.y>0 else -1,1))
        catch.get_editor_property('witness').set_static_mesh(kit['PorcelainCatch'])
        sign('BridgeInstructions','SHORT BRIDGE   /   FIRE AT AMBER CATCH\nSURVEY WALK   /   OPEN TO YOUR RIGHT', (1890,92,102),180,352,16)
        sign('GaugeMark','FLOOD GAUGE   /   FIELD NOTES',(3000,1010,107),-90,270,17)
        # An enclosed archive with two entrances, clerestory lighting and a protected chart room.
        for side in (-1,1):
            y=side*656
            block('ArchiveSill'+str(side),(4750,y,87),(1540,34,174),'Concrete')
            block('ArchiveEaves'+str(side),(4750,y,400),(1540,39,74),'Paint')
            for i,x in enumerate((3990,4300,4600,4900,5200,5510)):
                block(f'ArchivePost{side}_{i}',(x,y,261),(28,43,218),'Steel')
            for i,x in enumerate((4140,4445,4750,5050,5350)):
                block(f'ArchiveWindowMullion{side}_{i}',(x,y,268),(10,18,192),'Steel',False)
            # A low continuous rail keeps the equipment rack and cabinet line separated from the glass opening.
            block('ArchiveWindowRail'+str(side),(4750,y,285),(1520,19,12),'Pale',False)
        for name,x,segments in (('West',3980,((-650,-435),(-105,260),(598,650))),
                                 ('East',5510,((-650,-180),(180,650)))):
            for i,(a,b) in enumerate(segments):
                block(f'Archive{name}{i}',(x,(a+b)/2,209),(35,b-a,418),'Paint')
            block('ArchiveLintel'+name,(x,0,369),(44,1310,108),'Steel')
        roof=model('Phase06/Meshes/ServiceArchitecture/SM_CR06_SignalStoreRoof')
        prop('ChartHallRoof',roof,(4745,0,420),(.99,1.72,.87),(0,90,0))
        for x in (4000,4500,5000,5500):
            block('InteriorTie'+str(x),(x,0,394),(24,1310,19),'Steel',False)
        for i,x in enumerate((4200,4540,5260)):
            prop('PlanShelving'+str(i),model('Phase054/Meshes/SM_CR054_ServiceShelf'),(x,-575,0),(.75,.67,.82))
        prop('ChartBoard',kit['ArchiveChart'],(4960,-549,218),(1,1,1),(0,90,0))
        block('ChartWall',(4960,-576,173),(385,34,346),'Paint')
        sign('ChartKey','REFERENCE STRIP   /   120 DEG',(4960,-525,327),90,307,17)
        for i,x in enumerate((4310,4850,5300)):
            prop('ArchiveCeilingLamp'+str(i),model('Phase05/Meshes/SM_CR05_CagedLamp'),(x,0,355))
            lamp('ArchiveTaskLight'+str(i),(x,10,290),(1,.77,.46),740,620)
        sign('ArchiveTitle','ECHO CROSSING   /   CHART ROOM',(3956,70,257),180,285,18)
        sign('TowerExit','AERIAL DECK',(5485,295,244),180,210,18)
        # A second mass at the far end anchors the transmitter deck in silhouette.
        block('TowerDrumBase',(7670,-345,455),(205,180,70),'Concrete')
        prop('AzimuthPedestal',cylinder,(7670,-345,520),(.99,.99,1.34),(0,0,0),'Steel')
        for x in (8070,8510):
            for y in (-572,-345):
                block(f'CanopyPost{x}_{y}',(x,y,632),(18,18,423),'Paint')
        block('TransmitterCanopy',(8290,-459,847),(510,305,29),'Steel',False,(0,0,-7))
        prop('TransmitRack',model('Phase05/Meshes/SM_CR05_ControlRack'),(8370,-434,420),(.8,.8,.8))
        prop('TransmitRackTwin',model('Phase05/Meshes/SM_CR05_ControlRack'),(8140,-434,420),(.8,.8,.8))
        lamp('TransmitGlow',(8330,210,648),(.52,.86,1),445,340)
        for index,name,pos,yaw in STATIONS:
            station=entity(name,u.CREchoStation,pos,(0,yaw,0))
            station.set_editor_property('station_index',index)
            panel=station.get_editor_property('panel')
            panel.set_static_mesh(model('Phase06/Meshes/SM_CR06_DiagnosticPanel'))
            panel.set_relative_scale3d(u.Vector(1,2.6 if index==2 else 1.45,1))
            station.get_editor_property('display').set_text({
                0:'LINE TAP / OPEN CIRCUIT',1:'CHART ARCHIVE / REFERENCE STRIP',2:'AERIAL / 000 DEG',
                3:'EAST TRANSMITTER',4:"OBSERVER'S FIELD LOG"}[index])
            x,y,z=pos
            block(name+'Stand',(x,y,z-81),(36,59,89),'Paint',True,(0,yaw,0))
            block(name+'Plinth',(x,y,z-119),(68,92,12),'Dark',True,(0,yaw,0))
            rad=math.radians(yaw)
            block(name+'Readout',(x+21*math.cos(rad),y+21*math.sin(rad),z+62),
                  (7,205,43),'Dark',False,(0,yaw,0))
            block(name+'ReadoutBracket',(x+13*math.cos(rad),y+13*math.sin(rad),z+44),
                  (17,35,18),'Steel',False,(0,yaw,0))
            if index==2:
                station.get_editor_property('rotor').set_static_mesh(kit['AerialDish'])
        # Practical lights, atmospheric dawn and a stable exposure envelope for crossing between zones.
        sun=entity('Sun',u.DirectionalLight,(0,0,3200),(-28,125,0)).light_component
        sun.set_mobility(u.ComponentMobility.MOVABLE)
        sun.set_intensity(7.5)
        sun.set_light_color(u.LinearColor(1,.83,.66,1))
        sun.set_editor_property('atmosphere_sun_light',True)
        entity('Sky',u.SkyAtmosphere,(0,0,0))
        sky=entity('SkyFill',u.SkyLight,(0,0,1200)).light_component
        sky.set_mobility(u.ComponentMobility.MOVABLE)
        sky.set_editor_property('real_time_capture',True)
        sky.set_intensity(.98)
        haze=entity('RiverMist',u.ExponentialHeightFog,(0,0,-100)).get_component_by_class(u.ExponentialHeightFogComponent)
        haze.set_editor_property('fog_density',.016)
        haze.set_editor_property('fog_height_falloff',.24)
        haze.set_editor_property('start_distance',1300)
        wind=entity('FloodplainWind',u.AmbientSound,(3000,0,0)).audio_component
        wind.set_sound(model('Phase055/Audio/S_CR055_AmbYard'))
        wind.set_volume_multiplier(.35)
        wind.set_editor_property('auto_activate',True)
        hum=entity('ChartRoomVent',u.AmbientSound,(4780,-530,210)).audio_component
        hum.set_sound(model('Phase055/Audio/S_CR055_AmbWorkshop'))
        hum.set_editor_property('attenuation_settings',model('Phase055/Audio/ATT_CR055_Spatial'))
        hum.set_volume_multiplier(.32)
        hum.set_editor_property('auto_activate',True)
        volume=entity('Exposure',u.PostProcessVolume,(0,0,0))
        volume.set_editor_property('unbound',True)
        settings=volume.get_editor_property('settings')
        for key,val in (('auto_exposure_min_brightness',-.5),('auto_exposure_max_brightness',3.8),
                        ('auto_exposure_bias',.55)):
            settings.set_editor_property('override_'+key,True)
            settings.set_editor_property(key,val)
        volume.set_editor_property('settings',settings)
        assert levels.save_current_level()
    assert levels.load_level(MAP)
    validate_map(u,subsystem.get_editor_world(),actors,kit,apply)
    if apply:
        author_mooring(u,levels,actors,subsystem,True)


def author_mooring(u,levels,actors,subsystem,apply):
    import random
    moor_tag=TAG+'_Mooring'
    assert levels.load_level(MAP)
    lib=u.EditorAssetLibrary
    assert any(a.get_actor_label()=='Echo_Spawn' and TAG in [str(t) for t in a.tags]
               for a in actors.get_all_level_actors())
    base,palette=editor_assets(u,False,BASE_ART)
    new,_=editor_assets(u,apply,{'SurveyLaunch'})
    launch_mesh=new['SurveyLaunch']
    native_dim=launch_mesh.get_bounds().box_extent*2
    assert math.dist((native_dim.x,native_dim.y,native_dim.z),(861.08,284.40,580.61))<1,native_dim
    scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
    banks=scene['Echo_Valley']
    reed_ground=lib.load_asset('/Game/Generated/Phase052/Materials/MI_CR052_Leaf')
    assert reed_ground and not banks.get_actor_enable_collision()
    slots=base['Riverbanks'].get_editor_property('static_materials')
    ground_slot=next(i for i,slot in enumerate(slots)
                     if str(slot.get_editor_property('imported_material_slot_name'))=='Echo_Reed')
    if apply:
        banks.modify()
        banks.static_mesh_component.modify()
        banks.static_mesh_component.set_material(ground_slot,reed_ground)
    def protected():
        result={}
        for a in actors.get_all_level_actors():
            tags=[str(t) for t in a.tags]
            if TAG not in tags or moor_tag in tags:
                continue
            p,r,s=a.get_actor_location(),a.get_actor_rotation(),a.get_actor_scale3d()
            result[a.get_actor_label()]=(a.get_class().get_path_name(),a.get_actor_enable_collision(),
                                          tuple(round(n,3) for n in (p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z)))
        return result
    old=protected()
    assert len(old)>=330
    old_hashes=echo_output_hashes()
    cube=lib.load_asset('/Engine/BasicShapes/Cube')
    tuft=lib.load_asset('/Game/Generated/Phase052/Meshes/SM_CR052_WeedTuft')
    assert cube and tuft
    expected={}

    def piece(name,mesh,pos,sc=(1,1,1),pitch=0,yaw=0,mat=None):
        label='Echo_Mooring_'+name
        assert label not in expected,label
        expected[label]=pos
        if not apply:
            return
        a=scene.get(label)
        if a:
            assert moor_tag in [str(t) for t in a.tags] and isinstance(a,u.StaticMeshActor),label
        else:
            a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*pos))
            a.set_actor_label(label)
            a.tags=[TAG,moor_tag]
        a.modify()
        a.set_actor_location(u.Vector(*pos),False,False)
        a.set_actor_rotation(u.Rotator(pitch=pitch,yaw=yaw),False)
        a.set_actor_scale3d(u.Vector(*sc))
        c=a.static_mesh_component
        c.set_static_mesh(mesh)
        if mat:
            c.set_material(0,palette[mat])
        c.set_collision_profile_name('NoCollision')
        c.set_editor_property('can_ever_affect_navigation',False)
        a.set_actor_enable_collision(False)

    bx,by,bz=2200,1080,-167
    heading=18
    piece('SurveyLaunch',launch_mesh,(bx,by,bz),yaw=heading)
    rad=math.radians(heading)
    for index,(cleat,dock) in enumerate((((315,-56,129),(2560,1028,12)),((-389,-75,105),(1975,584,12)))):
        x,y,z=cleat
        start=(bx+x*math.cos(rad)-y*math.sin(rad),by+x*math.sin(rad)+y*math.cos(rad),bz+z)
        rope=[]
        for k in range(5):
            f=k/4
            rope.append(tuple(start[i]+(dock[i]-start[i])*f-(13*4*f*(1-f) if i==2 else 0) for i in range(3)))
        for k,(p,q) in enumerate(zip(rope,rope[1:])):
            dx,dy,dz=(q[i]-p[i] for i in range(3))
            piece(f'Line{index}_{k}',cube,tuple((p[i]+q[i])/2 for i in range(3)),(math.dist(p,q)/100,.046,.046),
                  math.degrees(math.atan2(dz,math.hypot(dx,dy))),math.degrees(math.atan2(dy,dx)),'Dark')
        piece('PierBollard'+str(index),cube,(dock[0],dock[1],7),(.16,.20,.14),mat='Steel')
        piece('PierHorn'+str(index),cube,(dock[0],dock[1],12),(.35,.15,.065),mat='Amber')

    # Seed separate, irregular reed beds on the actual sloping bank triangles outside the playable piers.
    flip=1 if base['BreakawayArm'].get_bounds().origin.y>0 else -1
    def bank_vertex(i,j,b):
        x=-19000+i*580
        shore=2150+410*math.sin(x*.0007+b*2)+180*math.sin(x*.0017)
        wave=math.sin(x*.0012+j*.71)*.54+math.sin(x*.00046+b+j)*.46
        y=b*(shore+[-140,0,110,230,420,840,1600,3300,6300][j]+wave*(j*j*8))
        z=[-260,-206,-180,-127,-55,100,365,870,1190][j]+wave*(8+j*j*7)
        return x,y*flip,z
    rng=random.Random(82119)
    for patch,(i,b,total) in enumerate(((35,flip,11),(37,flip,10),(39,-flip,9))):
        p=bank_vertex(i,3,b)
        q=bank_vertex(i+1,3,b)
        r=bank_vertex(i,4,b)
        for k in range(total):
            f=rng.uniform(.03,.94)
            g=rng.uniform(.02,.85)*(1-f)
            pos=tuple(p[k]+(q[k]-p[k])*f+(r[k]-p[k])*g-(5 if k==2 else 0) for k in range(3))
            h=rng.uniform(1.8,3.1)
            piece(f'ShoreReeds{patch}_{k}',tuft,pos,(h*1.1,h*.81,h),yaw=rng.uniform(-160,160))
    if apply:
        assert levels.save_current_level()
    assert levels.load_level(MAP)
    actual={a.get_actor_label():a for a in actors.get_all_level_actors() if moor_tag in [str(t) for t in a.tags]}
    assert set(actual)==set(expected)
    for label,a in actual.items():
        p=a.get_actor_location()
        assert math.dist((p.x,p.y,p.z),expected[label])<.1 and not a.get_actor_enable_collision(),label
        assert str(a.static_mesh_component.get_collision_profile_name())=='NoCollision',label
    assert actual['Echo_Mooring_SurveyLaunch'].static_mesh_component.static_mesh==launch_mesh
    bank=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Echo_Valley')
    assert not bank.get_actor_enable_collision() and bank.static_mesh_component.get_material(ground_slot)==reed_ground
    assert old==protected()
    now=echo_output_hashes()
    assert all(now[k]==digest for k,digest in old_hashes.items() if not k.endswith('.umap'))
    validate_map(u,subsystem.get_editor_world(),actors,base,False)
    result=dict(applied=apply,additions=len(expected),protected_actors=len(old),preserved_source_and_native_assets=len(now)-1,
                bank_ground_override=reed_ground.get_path_name(),launch_dimensions_cm=[native_dim.x,native_dim.y,native_dim.z],
                launch_triangles=9018,actor_location=[bx,by,bz])
    (OUT/('native-mooring-author.json' if apply else 'native-mooring-verify.json')).write_text(json.dumps(result,indent=2))
    u.log('CR02_MOORING PASS '+str(result))


def validate_map(u,world,actors,kit,apply):
    assert world.get_world_settings().get_editor_property('default_game_mode').get_path_name()==MODE
    level=[a for a in actors.get_all_level_actors() if TAG in [str(t) for t in a.tags]]
    scene={a.get_actor_label():a for a in level}
    assert len(scene)==len(level)>140
    assert len([a for a in level if isinstance(a,u.PlayerStart)])==1
    for index,name,loc,yaw in STATIONS:
        a=scene['Echo_'+name]
        assert isinstance(a,u.CREchoStation) and a.get_editor_property('station_index')==index
        p=a.get_actor_location()
        assert math.dist((p.x,p.y,p.z),loc)<.02 and a.get_editor_property('panel').static_mesh
        if index==2:
            assert a.get_editor_property('rotor').static_mesh==kit['AerialDish']
    catch=scene['Echo_BridgeCatch']
    assert isinstance(catch,u.CREchoBridgeCatch)
    assert catch.get_editor_property('boom').static_mesh==kit['BreakawayArm']
    assert catch.get_editor_property('witness').static_mesh==kit['PorcelainCatch']
    objects=[u.ObjectTypeQuery.OBJECT_TYPE_QUERY1,u.ObjectTypeQuery.OBJECT_TYPE_QUERY2]
    def sample(points):
        count=0
        for p,q in zip(points,points[1:]):
            divisions=max(1,math.ceil(math.dist(p,q)/75))
            for k in range(divisions+1):
                x,y=(p[i]+(q[i]-p[i])*k/divisions for i in range(2))
                z=min(420,max(0,(x-5820)*.3))
                floor=u.SystemLibrary.sphere_overlap_actors(world,u.Vector(x,y,z-3),9,objects,u.StaticMeshActor,[])
                assert floor,(p,q,x,y,z,'missing floor')
                body=u.SystemLibrary.capsule_overlap_actors(world,u.Vector(x,y,z+100),42,92,objects,u.StaticMeshActor,[])
                assert not body,(p,q,x,y,[a.get_actor_label() for a in body])
                count+=1
        return count
    north=sample(ROUTE)
    south=sample([(1400,250),(1560,-120),(1610,-270),(2110,-270),(3600,-270),(4150,-270),(4580,-235)])
    receipt=dict(map=MAP,game_mode=MODE,applied=apply,actors=len(level),route_samples=north,short_bridge_floor_samples=south,
                 stations=STATIONS,spawn=[-1250,0,105],upper_deck_cm=420,short_bridge_requires_release=True)
    (OUT/('native-author.json' if apply else 'native-verify.json')).write_text(json.dumps(receipt,indent=2))
    u.log('CR02_ECHO_MAP PASS '+str(receipt))


def capture_views(u,levels,actors):
    import time
    import traceback
    assert levels.load_level(MAP)
    out=OUT/'views'
    out.mkdir(parents=True,exist_ok=True)
    shots=[
        ('01-intake-approach',(-950,0,168),(1540,95,160)),
        ('02-two-river-crossings',(1580,0,170),(5120,90,160)),
        ('03-floodplain-overlook',(3280,964,169),(7000,1440,176)),
        ('04-chart-room',(4310,376,164),(5010,-400,176)),
        ('05-transmitter-deck',(7240,75,588),(7760,-330,756)),
        ('06-river-from-tower',(8120,358,589),(3150,30,50))]
    flags=u.SystemLibrary.get_command_line().lower()
    receipt='frames.json'
    for flag,label in (('-cr02beforemooring','before'),('-cr02aftermooring','after')):
        if flag in flags:
            shots=[(label+'-berth',(2910,898,167),(2280,1130,90)),
                   (label+'-intake',(1030,40,165),(2380,682,126))]
            receipt=label+'-mooring.json'
            break
    if '-cr02echovista' in flags:
        shots=[('07-open-river-vista',(3280,964,169),(7000,1440,176))]
        receipt='vista.json'
    camera=actors.spawn_actor_from_class(u.CameraActor,u.Vector(*shots[0][1]))
    camera.camera_component.set_field_of_view(83)
    actors.clear_actor_selection_set()
    prefs=u.get_default_object(u.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
    throttle=prefs.get_editor_property('bThrottleCPUWhenNotForeground')
    prefs.set_editor_property('bThrottleCPUWhenNotForeground',False)
    state=dict(index=0,task=None,started=time.monotonic(),placed=0,frames=[])

    def aim():
        _,p,target=shots[state['index']]
        camera.set_actor_location(u.Vector(*p),False,False)
        dx,dy,dz=(target[i]-p[i] for i in range(3))
        camera.set_actor_rotation(u.Rotator(pitch=math.degrees(math.atan2(dz,math.hypot(dx,dy))),
                                             yaw=math.degrees(math.atan2(dy,dx))),False)
        state['placed']=time.monotonic()

    def finish(error=None):
        (out/receipt).write_text(json.dumps(dict(frames=state['frames'],error=error),indent=2))
        prefs.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
        u.unregister_slate_post_tick_callback(handle)
        u.SystemLibrary.quit_editor()

    def tick(delta):
        try:
            assert time.monotonic()-state['started']<190,'Viewport capture timed out'
            name=shots[state['index']][0]
            path=out/(name+'.png')
            task=state['task']
            if task and task.is_task_done():
                assert path.exists() and path.stat().st_size>15000,path
                state['frames'].append(name)
                state['index']+=1
                state['task']=None
                if state['index']==len(shots):
                    finish()
                else:
                    aim()
            elif task is None and time.monotonic()-state['placed']>4:
                state['task']=u.AutomationLibrary.take_high_res_screenshot(1600,900,str(path),camera=camera,force_game_view=True)
                assert state['task'] and state['task'].is_valid_task()
        except Exception:
            finish(traceback.format_exc())
    u.EditorPythonScripting.set_keep_python_script_alive(True)
    aim()
    handle=u.register_slate_post_tick_callback(tick)


if __name__ == '__main__':
    try:
        import unreal
    except ImportError:
        if '--verify-blend' in sys.argv:
            verify_blend()
        else:
            model_kit()
    else:
        run_editor()
