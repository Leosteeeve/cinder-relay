"""Shared campaign-film character. Metres, Z up, local -Y forward. No external geometry."""
import math
import bpy
from mathutils import Vector, Quaternion, Euler

V=Vector


def _material(name,rgb,metal=0,rough=.76):
    name='Elias / '+name
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*rgb,1)
    bs.inputs['Metallic'].default_value=metal
    bs.inputs['Roughness'].default_value=rough
    return m


def build_elias(name='Elias'):
    """Create an original weighted mesh and an editable native Armature at the origin."""
    bones={}
    def bone(n,h,t,parent=None): bones[n]=(V(h),V(t),parent)
    for n,lo,hi,parent in [('pelvis',.92,1.015,None),('spine',1.015,1.235,'pelvis'),
            ('chest',1.235,1.427,'spine'),('neck',1.427,1.51,'chest'),('head',1.51,1.76,'neck')]:
        bone(n,(0,0,lo),(0,0,hi),parent)
    sides=(('L',-1),('R',1))
    for side,s in sides:
        suf='.'+side
        shoulder=(s*.206,0,1.410); elbow=(s*.270,.020,1.116); wrist=(s*.289,-.031,.857)
        bone('upper_arm'+suf,shoulder,elbow,'chest')
        bone('forearm'+suf,elbow,wrist,'upper_arm'+suf)
        bone('hand'+suf,wrist,(s*.289,-.043,.762),'forearm'+suf)
        for d in range(4):
            x=s*(.255+.019*d)
            bone('finger'+str(d)+suf,(x,-.045,.780),(x,-.060,.724+abs(d-1)*.008),'hand'+suf)
        bone('thumb'+suf,(s*.251,-.049,.815),(s*.223,-.077,.765),'hand'+suf)
        bone('thigh'+suf,(s*.105,0,.92),(s*.105,-.018,.507),'pelvis')
        bone('shin'+suf,(s*.105,-.018,.507),(s*.109,.004,.104),'thigh'+suf)
        bone('foot'+suf,(s*.109,.004,.104),(s*.109,-.185,.068),'shin'+suf)
    arm=bpy.data.armatures.new(name+' Skeleton')
    rig=bpy.data.objects.new(name,arm)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active=rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for n,(h,t,p) in bones.items():
        b=arm.edit_bones.new(n); b.head=h; b.tail=t
        if p: b.parent=arm.edit_bones[p]
    bpy.ops.object.mode_set(mode='OBJECT')
    rig.show_in_front=False
    arm.display_type='STICK'
    for b in rig.pose.bones: b.rotation_mode='QUATERNION'
    colors={'coat':(.065,.145,.15),'panel':(.10,.205,.197),'seam':(.035,.069,.068),'edge':(.247,.319,.281),
            'amber':(.68,.287,.061),'brass':(.42,.287,.132),'pants':(.105,.127,.122),'leather':(.19,.119,.063),
            'rubber':(.04,.045,.041),'glove':(.285,.198,.106),'pad':(.102,.087,.064),'skin':(.54,.306,.196),
            'warm':(.45,.218,.15),'lip':(.39,.155,.121),'hair':(.065,.045,.038),'iris':(.13,.125,.069),
            'white':(.59,.55,.45),'pupil':(.021,.023,.022),'metal':(.28,.343,.33),'patch':(.646,.566,.381)}
    mats={k:_material(k,rgb,.55 if k in ('brass','metal') else 0,.46 if k in ('pupil','metal') else .78)
          for k,rgb in colors.items()}
    keys=list(mats)
    verts=[]; faces=[]; slots=[]; smooth=[]; weights={}
    def geometry(n,points,polys,mat,soft=False):
        start=len(verts); verts.extend([tuple(p) for p in points])
        weights.setdefault(n,[]).extend(range(start,len(verts)))
        faces.extend([tuple(start+i for i in f) for f in polys])
        slots.extend([keys.index(mat)]*len(polys));smooth.extend([soft]*len(polys))
    def rings(n,rows,mat,segments=16,soft=True):
        points=[]
        for x,y,z,rx,ry in rows:
            for i in range(segments):
                a=2*math.pi*i/segments
                points.append((x+rx*math.cos(a),y+ry*math.sin(a),z))
        polys=[tuple(reversed(range(segments)))]
        for j in range(len(rows)-1):
            for i in range(segments):
                a=j*segments+i;b=j*segments+(i+1)%segments
                polys.append((a,b,b+segments,a+segments))
        polys.append(tuple(range(len(points)-segments,len(points))))
        geometry(n,points,polys,mat,soft)
    def oval(n,c,rad,mat):
        x,y,z=c;rx,ry,rz=rad
        rows=[]
        for i in range(9):
            a=-math.pi/2+i*math.pi/8
            rows.append((x,y,z+rz*math.sin(a),rx*max(.025,math.cos(a)),ry*max(.025,math.cos(a))))
        rings(n,rows,mat)
    def link(n,a,b,ra,rb,mat,segments=10):
        a,b=V(a),V(b)
        diff=(b-a).normalized()
        cat=V((1,0,0)) if abs(diff.x)<.8 else V((0,1,0))
        u=diff.cross(cat).normalized();v=diff.cross(u)
        p=[]
        for at,r in ((a,ra),(b,rb)):
            for i in range(segments):
                t=i*math.tau/segments;p.append(at+r*(u*math.cos(t)+v*math.sin(t)))
        f=[tuple(reversed(range(segments))),tuple(range(segments,segments*2))]
        f += [(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)]
        geometry(n,p,f,mat,True)
    def block(n,c,size,mat):
        x,y,z=c;a,b,k=(v/2 for v in size)
        points=[(x+dx*a,y+dy*b,z+dz*k) for dz in (-1,1) for dy in (-1,1) for dx in (-1,1)]
        geometry(n,points,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mat)
    def cloth(n,rows,mat): rings(n,[(0,y,z,xr,yr) for z,xr,yr,y in rows],mat,24)
    cloth('pelvis',[(.84,.158,.111,.01),(.90,.186,.127,.012),(.998,.164,.123,.008)],'pants')
    cloth('spine',[(.91,.196,.14,.006),(.938,.211,.153,.009),(1.04,.184,.136,.012),
                   (1.15,.194,.145,.009),(1.255,.216,.149,.010)],'coat')
    cloth('chest',[(1.205,.195,.137,.013),(1.258,.217,.154,.012),
                   (1.352,.234,.149,.008),(1.408,.205,.12,.008),(1.45,.109,.102,.006)],'panel')
    cloth('pelvis',[(.963,.186,.142,.007),(.992,.19,.146,.007),(1.013,.183,.14,.007)],'leather')
    block('pelvis',(0,-.142,.988),(.075,.019,.048),'brass')
    for s in (-1,1):
        oval('pelvis',(s*.173,.04,.933),(.068,.079,.080),'leather')
        block('pelvis',(s*.179,-.019,.951),(.088,.027,.039),'pad')
        link('chest',(s*.092,-.106,1.445),(s*.045,-.151,1.364),.018,.013,'edge')
        block('chest',(s*.117,-.141,1.304),(.102,.024,.067),'coat')
        block('chest',(s*.116,-.157,1.326),(.117,.015,.022),'edge')
        oval('chest',(s*.117,-.168,1.324),(.008,.005,.008),'brass')
    for n,low,high,y in [('spine',.998,1.244,-.132),('chest',1.244,1.39,-.143)]:
        link(n,(0,y,low),(0,y-.004,high),.007,.007,'brass',8)
    link('chest',(-.162,-.083,1.411),(.168,-.119,1.245),.022,.020,'leather')
    block('chest',(.11,-.154,1.276),(.044,.017,.026),'brass')
    rings('neck',[(0,.007,1.413,.061,.064),(0,.003,1.527,.064,.065)],'skin')
    cloth('chest',[(1.429,.107,.094,.004),(1.473,.092,.083,.005)],'seam')
    cloth('chest',[(1.462,.094,.087,.004),(1.470,.093,.085,.005)],'edge')
    # Narrow chin, nose bridge, modeled eyes and brows under a separate knitted cap.
    rings('head',[(0,-.008,1.49,.040,.047),(0,-.016,1.508,.060,.075),
                  (0,-.005,1.545,.081,.095),(0,.006,1.594,.092,.101),
                  (0,.010,1.642,.093,.102),(0,.014,1.688,.088,.100),(0,.019,1.724,.071,.078)],
                  'skin',28)
    for s in (-1,1):
        oval('head',(s*.090,.005,1.595),(.018,.025,.035),'warm')
        oval('head',(s*.096,-.003,1.599),(.012,.017,.026),'skin')
        def face_y(x,z):
            t=max(0,min(1,(z-1.594)/.048))
            return .006+.004*t-(.101+.001*t)*math.sqrt(max(0,1-(x/(.092+.001*t))**2))
        def eye_patch(rx,rz,offset,mat,almond=False):
            cx=s*.038;cz=1.617
            pts=[(cx,face_y(cx,cz)-offset-.0007,cz)]
            for j in range(24):
                a=math.tau*j/24
                x=cx+rx*math.cos(a)
                z=cz+rz*math.sin(a)*(.72+.28*abs(math.sin(a)) if almond else 1)
                pts.append((x,face_y(x,z)-offset,z))
            geometry('head',pts,[(0,j+1,(j+1)%24+1) for j in range(24)],mat,True)
        eye_patch(.021,.0062,.0017,'white',True)
        eye_patch(.0064,.0058,.0027,'iris')
        eye_patch(.0031,.0039,.0037,'pupil')
        for upper in (False,True):
            pts=[]
            for j in range(8):
                t=j/7
                x=s*(.017+.042*t)
                z=1.617+(.0069 if upper else -.0056)*math.sin(t*math.pi)
                pts.append((x,face_y(x,z)-.0021,z))
            for a,b in zip(pts,pts[1:]):
                link('head',a,b,.00175,.00175,'warm' if upper else 'skin',7)
        for q in range(4):
            x1=s*(.017+.011*q);x2=s*(.028+.011*q)
            z1=1.632+.0035*math.sin(q*.68);z2=1.632+.0035*math.sin((q+1)*.68)
            link('head',(x1,face_y(x1,z1)-.0016,z1),(x2,face_y(x2,z2)-.0013,z2),
                 .0038-.00055*q,.0034-.00055*q,'hair',8)
    rings('head',[(0,-.099,1.572,.014,.009),(0,-.109,1.583,.017,.017),
                  (0,-.100,1.601,.010,.013),(0,-.087,1.635,.012,.011)],'skin',14)
    for s in (-1,1): oval('head',(s*.015,-.105,1.581),(.009,.011,.007),'warm')
    link('head',(-.026,-.093,1.551),(0,-.103,1.55),.0025,.003,'lip')
    link('head',(0,-.103,1.55),(.026,-.093,1.551),.003,.0025,'lip')
    oval('head',(0,-.094,1.543),(.018,.007,.005),'warm')
    rings('head',[(0,.013,1.653,.097,.106),(0,.012,1.685,.099,.112),
                  (0,.022,1.724,.092,.104),(0,.035,1.758,.071,.081),(0,.047,1.775,.025,.04)],'coat',28)
    rings('head',[(0,.005,1.648,.098,.112),(0,.008,1.678,.102,.113)],'seam',32)
    for i in range(23):
        t=i*math.tau/23
        link('head',(.099*math.cos(t),.008+.112*math.sin(t),1.652),
             (.101*math.cos(t),.008+.112*math.sin(t),1.674),.0018,.0018,'coat',5)
    block('head',(.064,-.075,1.671),(.025,.012,.021),'amber')
    for side,s in sides:
        suf='.'+side
        rings('upper_arm'+suf,[(s*.269,.018,1.093,.060,.064),(s*.26,.012,1.164,.067,.072),
              (s*.23,.004,1.303,.081,.078),(s*.211,.002,1.381,.084,.087),
              (s*.202,0,1.421,.069,.070)],'coat')
        oval('upper_arm'+suf,(s*.215,.001,1.384),(.084,.089,.065),'panel')
        rings('upper_arm'+suf,[(s*.240,.006,1.256,.078,.08),(s*.236,.004,1.28,.079,.08)],
              'amber' if side=='L' else 'seam')
        rings('forearm'+suf,[(s*.29,-.033,.851,.049,.052),(s*.287,-.025,.906,.067,.067),
              (s*.274,-.004,1.030,.072,.066),(s*.266,.02,1.125,.062,.063)],'panel')
        rings('forearm'+suf,[(s*.289,-.032,.852,.052,.055),(s*.287,-.026,.89,.057,.058)],'seam')
        oval('hand'+suf,(s*.287,-.039,.808),(.052,.038,.069),'glove')
        oval('hand'+suf,(s*.288,-.015,.810),(.045,.022,.044),'pad')
        for digit in range(4):
            n='finger'+str(digit)+suf;h,t,_=bones[n]
            link(n,h,t,.012,.009,'glove');oval(n,t,(.010,.010,.011),'pad')
        n='thumb'+suf;h,t,_=bones[n]
        link(n,h,t,.017,.013,'glove');oval(n,t,(.013,.014,.013),'pad')
        rings('thigh'+suf,[(s*.105,-.015,.493,.069,.078),(s*.104,-.006,.562,.08,.082),
              (s*.105,.006,.715,.094,.097),(s*.105,0,.89,.104,.107),(s*.101,0,.938,.090,.098)],'pants')
        block('thigh'+suf,(s*.18,.005,.73),(.045,.13,.114),'coat')
        rings('shin'+suf,[(s*.109,.003,.144,.056,.062),(s*.109,.015,.281,.063,.079),
              (s*.107,.008,.38,.084,.087),(s*.105,-.014,.506,.074,.078)],'pants')
        oval('shin'+suf,(s*.106,-.073,.471),(.066,.037,.068),'seam')
        rings('foot'+suf,[(s*.109,-.062,.013,.072,.145),(s*.109,-.064,.037,.073,.149),
              (s*.109,-.051,.067,.071,.142),(s*.109,-.018,.098,.062,.088),(s*.109,.001,.165,.061,.065)],
              'leather',20)
        rings('foot'+suf,[(s*.109,-.064,.003,.073,.147),(s*.109,-.064,.025,.075,.15)],'rubber',20)
    for n,orig in (('forearm.L',(-.286,-.09,.92)),('chest',(.12,-.16,1.304))):
        block(n,orig,(.043,.009,.012),'amber')
    data=bpy.data.meshes.new(name+' Field Clothing and Face')
    data.from_pydata(verts,[],faces);data.update()
    mesh=bpy.data.objects.new(name+' / field uniform and repair gloves',data)
    bpy.context.scene.collection.objects.link(mesh)
    for m in mats.values():data.materials.append(m)
    for p,mi,sm in zip(data.polygons,slots,smooth):
        p.material_index=mi;p.use_smooth=sm
    for n,ids in weights.items(): mesh.vertex_groups.new(name=n).add(ids,1.0,'REPLACE')
    mod=mesh.modifiers.new('Articulated field technician','ARMATURE');mod.object=rig
    mesh.parent=rig
    rig['Authoring convention']='Meters, +Z up, -Y facing, soles at Z zero'
    return rig


def pose_elias(rig,frame,*,root=(0,0,0),yaw=0.,walk=0.,stride=0.,look=(0.,0.),lean=0.,
               reach_l=None,reach_r=None,curl=.25,hand_dir_l=None,hand_dir_r=None):
    """Key a balanced pose. Look uses (yaw, upward pitch) degrees. Hand targets are world-space palm centers."""
    rad=math.radians
    R=Quaternion((0,0,1),rad(yaw))
    rise=.021*stride*math.cos(walk*2)
    root=V(root)+V((0,0,rise))
    rig.location=root;rig.rotation_euler=(0,0,rad(yaw))
    rig.keyframe_insert(data_path='location',frame=frame);rig.keyframe_insert(data_path='rotation_euler',frame=frame)
    dirs={};heads={}
    def head(n):
        b=rig.data.bones[n]
        if b.parent:
            parent=b.parent.name
            return heads[parent]+dirs[parent]@(b.head_local-b.parent.head_local)
        return b.head_local.copy()
    def rotate(n,delta):
        b=rig.data.bones[n];pb=rig.pose.bones[n]
        base=b.matrix_local.to_quaternion()
        parent=dirs[b.parent.name] if b.parent else Quaternion()
        result=base.inverted()@parent.inverted()@delta@base
        if pb.rotation_quaternion.dot(result)<0:result.negate()
        pb.rotation_quaternion=result
        pb.keyframe_insert(data_path='rotation_quaternion',frame=frame)
        heads[n]=head(n);dirs[n]=delta
    def aim(n,vec):
        b=rig.data.bones[n]
        parent=dirs[b.parent.name]
        d=(parent@(b.tail_local-b.head_local)).normalized()
        rotate(n,d.rotation_difference(vec.normalized())@parent)
    def pair(n1,n2,target,pole):
        a=head(n1);v=target-a;axis=v.normalized()
        l1=rig.data.bones[n1].length;l2=rig.data.bones[n2].length
        length=max(abs(l1-l2)+.001,min(v.length,l1+l2-.001))
        end=a+length*axis
        lateral=pole-axis*axis.dot(pole)
        if lateral.length<.0001:lateral=axis.cross(V((1,0,0)))
        along=(l1*l1-l2*l2+length*length)/(2*length)
        joint=a+axis*along+lateral.normalized()*math.sqrt(max(0,l1*l1-along*along))
        aim(n1,joint-a);aim(n2,end-joint)
    rotate('pelvis',Quaternion((0,0,1),.065*stride*math.sin(walk)))
    tilt=Quaternion((1,0,0),rad(lean))
    rotate('spine',Quaternion((1,0,0),rad(lean*.56)))
    rotate('chest',tilt@Quaternion((0,0,1),-.077*stride*math.sin(walk)))
    gaze=Quaternion((0,0,1),rad(look[0]))@Quaternion((1,0,0),rad(-look[1]))
    rotate('neck',tilt.slerp(gaze,.4));rotate('head',gaze)
    for side,s,target in (('L',-1,reach_l),('R',1,reach_r)):
        suf='.'+side
        phase=walk+(math.pi if s<0 else 0)
        foot=V((s*.11,.006-.24*stride*math.sin(phase),.104-rise+.095*stride*max(0,math.cos(phase))))
        pair('thigh'+suf,'shin'+suf,foot,V((s*.03,-1,0)))
        rotate('foot'+suf,Quaternion((1,0,0),.13*stride*math.cos(phase)))
        if target is not None:
            palm=R.inverted()@(V(target)-root)
            sh=head('upper_arm'+suf);direction=(palm-sh).normalized()
            finger_axis=hand_dir_l if side=='L' else hand_dir_r
            if finger_axis is not None:
                direction=(R.inverted()@V(finger_axis)).normalized()
            wrist=palm-direction*.063
        else:
            wrist=V((s*.291,-.061+.19*stride*math.sin(phase),.874+.035*stride*max(0,math.cos(phase))))
            direction=V((0,-.13,-1)).normalized()
        flat_contact=target is not None and (hand_dir_l if side=='L' else hand_dir_r) is not None
        elbow_plane=V((s*.07,.20,-1)) if flat_contact else V((s*.62,.60,-.65))
        pair('upper_arm'+suf,'forearm'+suf,wrist,elbow_plane)
        aim('hand'+suf,direction)
        for i in range(4):
            rotate('finger'+str(i)+suf,dirs['hand'+suf]@Quaternion((1,0,0),rad(-9-32*curl)))
        rotate('thumb'+suf,dirs['hand'+suf]@Quaternion((0,1,0),rad(s*(6+13*curl))))
    return rig
