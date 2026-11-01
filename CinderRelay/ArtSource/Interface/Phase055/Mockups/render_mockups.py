"""Original Phase055 layout studies. Pillow; no borrowed visual assets.

Run with the bundled Python. Output is a design mockup, never Unreal evidence.
The schematic environment intentionally does not assert new story canon.
"""
from pathlib import Path
import math, json, hashlib
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
FONT=ROOT.parent/'Fonts'
C={'deep':'#0B1012','steel':'#151B1D','white':'#E8E3D8','amber':'#C99553','cyan':'#77B6B0','olive':'#8E978B','red':'#BE6959','line':'#3B4545'}

class Canvas:
    def __init__(self,w,h):
        self.w,self.h=w,h
        self.s=w/1920
        self.H=h/self.s
        self.im=Image.new('RGB',(w,h),C['deep']); self.d=ImageDraw.Draw(self.im)
    def box(self,b,fill,outline=None,width=1):
        self.d.rectangle(tuple(round(v*self.s) for v in b),fill=fill,outline=outline,width=max(1,round(width*self.s)))
    def line(self,pts,fill,width=1):
        self.d.line([(round(x*self.s),round(y*self.s)) for x,y in pts],fill=fill,width=max(1,round(width*self.s)),joint='curve')
    def poly(self,pts,fill): self.d.polygon([(round(x*self.s),round(y*self.s)) for x,y in pts],fill=fill)
    def ellipse(self,b,fill=None,outline=None,width=1): self.d.ellipse(tuple(round(v*self.s) for v in b),fill=fill,outline=outline,width=max(1,round(width*self.s)))
    def text(self,xy,t,size=24,color='white',kind='body',anchor='lt'):
        name='BarlowCondensed-SemiBold.ttf' if kind=='title' else 'Barlow-Medium.ttf' if kind=='medium' else 'Barlow-Regular.ttf'
        self.d.text(tuple(round(v*self.s) for v in xy),t,font=ImageFont.truetype(str(FONT/name),round(size*self.s)),fill=C.get(color,color),anchor=anchor,stroke_width=0)
    def relay(self,x,y,size=48):
        s=size/48
        self.line([(x,y+40*s),(x,y+8*s),(x+18*s,y+8*s),(x+18*s,y+40*s)],C['amber'],4*s)
        self.line([(x+29*s,y),(x+29*s,y+32*s),(x+47*s,y+32*s),(x+47*s,y)],C['cyan'],4*s)
        self.line([(x+8*s,y+24*s),(x+39*s,y+16*s)],C['white'],2*s)
    def environment(self):
        # Original graphic blockout used only to evaluate information hierarchy.
        for y in range(self.h):
            v=y/self.h
            fog=math.exp(-((v-.46)/.23)**2)
            self.d.line((0,y,self.w,y),fill=(int(15+36*fog),int(23+41*fog),int(25+40*fog)))
        horizon=self.H*.55
        for x,ht,ww in [(680,90,100),(780,160,90),(900,140,150),(1140,245,92),(1400,120,120),(1510,210,160),(1700,160,110)]:
            self.box((x,horizon-ht,x+ww,horizon+20),'#384545')
            for a in range(int(x+12),int(x+ww-6),22): self.box((a,horizon-ht+20,a+5,horizon-ht+45),'#435151')
        self.box((1370,horizon-350,1380,horizon+80),'#3C4948'); self.box((1570,horizon-300,1580,horizon+80),'#3C4948')
        self.line([(1300,horizon-260),(1640,horizon-260)],'#3C4948',7)
        self.line([(1368,horizon-350),(1590,horizon-310)],'#3C4948',4)
        self.box((0,horizon,1920,self.H),'#222A29')
        self.poly([(1120,horizon+15),(1250,horizon-150),(1430,horizon-140),(1490,horizon-95),(1670,horizon-110),(1770,horizon+15)],'#1B2525')
        self.box((1180,horizon+10,1760,horizon+210),'#202A29')
        self.box((1244,horizon+45,1350,horizon+210),'#0F1919')
        self.box((1450,horizon+45,1640,horizon+125),'#111B1B')
        for x in range(1450,1641,38): self.line([(x,horizon+45),(x,horizon+125)],'#3E4841',3)
        self.box((1257,horizon+43,1336,horizon+50),C['amber'])
        self.poly([(1257,horizon+50),(1336,horizon+50),(1420,horizon+260),(1150,horizon+260)],'#363326')
        self.box((1258,horizon+50,1335,horizon+210),'#302F24')
        self.line([(1110,horizon+16),(1270,horizon-158),(1420,horizon-146)],'#66706A',3)
        self.line([(1490,horizon-95),(1660,horizon-116),(1774,horizon+12)],'#66706A',3)
        for x in [1170,1360,1500,1710]:self.line([(x,horizon+10),(x,horizon+220)],'#51594F',4)
        self.text((1210,horizon-23),'RELAY NINE',20,'olive','medium')
        vanish=(1150,horizon+110)
        for x in [680,790,1390,1500]: self.line([vanish,(x,self.H)],'#788076',3)
        for y in range(int(horizon+125),int(self.H),32):
            z=(y-vanish[1])/(self.H-vanish[1]); self.line([(1150-520*z,y),(1150+400*z,y)],'#4A4C40',max(2,5*z))
        # Damaged signalling fixture.
        self.line([(1720,self.H+10),(1690,horizon+20)],'#0D1415',18)
        self.poly([(1642,horizon-118),(1715,horizon-112),(1740,horizon+25),(1650,horizon+28)],'#0B1314')
        self.ellipse((1667,horizon-87,1703,horizon-51),fill='#263330',outline='#596053',width=4)
        self.ellipse((1677,horizon-27,1713,horizon+9),fill='#7C6240',outline='#9E804E',width=4)
        self.line([(1690,horizon-125),(1724,horizon-151)],'#151F20',9)
        self.ellipse((1387,horizon-247,1393,horizon-241),fill=C['cyan'])
        # Quiet left column, original graphics not a borrowed game screenshot.
        overlay=Image.new('RGBA',self.im.size)
        od=ImageDraw.Draw(overlay)
        for x in range(self.w):
            a=int(220*max(0,1-x/(self.w*.65))**.8)
            od.line((x,0,x,self.h),fill=(7,12,14,a))
        self.im=Image.alpha_composite(self.im.convert('RGBA'),overlay).convert('RGB'); self.d=ImageDraw.Draw(self.im)
    def note(self,screen):
        self.text((48,28),'CINDER RELAY   /   INDUSTRIAL FIELD INTERFACE',16,'olive','medium')
        self.text((1872,28),f'{screen.upper()}  •  DESIGN STUDY  /  NOT ENGINE CAPTURE',16,'olive',anchor='rt')
    def save(self,name):
        path=ROOT/f'{name}_{self.w}x{self.h}.png'; self.im.save(path,optimize=True); return path

def menu(w,h):
    c=Canvas(w,h);c.environment();c.note('Main menu')
    y=c.H*.19
    c.relay(96,y,58)
    c.text((96,y+94),'CINDER',92,'white','title');c.text((96,y+181),'RELAY',92,'white','title')
    c.text((99,y+290),'T H E   L A S T   S I G N A L',22,'amber','medium')
    start=y+376
    for i,label in enumerate(['Continue','New Game','Settings','Credits','Exit Game']):
        yy=start+i*60
        if i==0:
            c.box((80,yy-10,480,yy+40),'#263333');c.box((80,yy-10,84,yy+40),C['amber'])
        c.text((104,yy),label,27,'white' if i==0 else 'olive','medium')
        if i==0:c.text((450,yy+1),'›',30,'amber',anchor='rt')
    c.text((96,c.H-100),'THE DEAD STATION',18,'white','medium')
    c.text((96,c.H-67),'Continue from your last saved checkpoint.',19,'olive')
    c.text((1872,c.H-67),'Original environment blockout • final cinematic art pending',16,'olive',anchor='rt')
    return c.save('MainMenu')

def hud(w,h):
    c=Canvas(w,h);c.environment();c.note('Gameplay HUD')
    c.box((48,88,472,177),C['deep']);c.box((48,88,51,177),C['amber'])
    c.text((72,104),'CURRENT OBJECTIVE',16,'amber','medium')
    c.text((72,138),'Reach the maintenance workshop.',23)
    # A spare crosshair, not present in valid optic ADS.
    x,y=960,c.H*.5
    for a,b in [((x-11,y),(x-5,y)),((x+5,y),(x+11,y)),((x,y-11),(x,y-5)),((x,y+5),(x,y+11))]:c.line([a,b],C['white'],1)
    by=c.H-144
    c.box((48,by,288,c.H-48),C['deep']);c.text((72,by+17),'VITALS',16,'olive','medium')
    c.text((72,by+45),'100',37,'white','title');c.text((146,by+60),'HEALTH',16,'olive','medium')
    c.box((72,c.H-64,264,c.H-60),'#37423E');c.box((72,c.H-64,264,c.H-60),C['cyan'])
    c.box((1640,by,1872,c.H-48),C['deep']);c.text((1664,by+17),'ROOK-5',18,'olive','medium')
    c.text((1663,by+40),'04',49,'white','title');c.text((1744,by+62),'/  25',26,'olive','medium')
    c.text((1848,by+20),'•',18,'cyan',anchor='rt')
    c.box((557,c.H-174,1363,c.H-112),C['deep'])
    c.text((960,c.H-152),'ELIAS: Workshop lights. There may be a way to bring the relay back.',24,'white',anchor='mt')
    c.text((960,c.H-66),'SCHEMATIC SCENE  /  MOCKUP VALUES ONLY',16,'olive',anchor='mt')
    return c.save('GameplayHUD')

def rifle(c,x,y,s=1):
    def P(ps):return [(x+a*s,y+b*s) for a,b in ps]
    c.poly(P([(0,20),(70,20),(78,0),(220,0),(242,12),(390,12),(390,31),(240,31),(225,52),(165,52),(145,92),(123,89),(127,50),(69,47),(0,75)]),'#404C49')
    c.line(P([(0,20),(70,20),(78,0),(220,0),(242,12),(390,12)]),C['olive'],2)
    c.box((x+200*s,y-38*s,x+246*s,y-10*s),'#2A3B3B',C['cyan'],2)
    c.line(P([(207,-10),(207,0),(237,0),(237,-10)]),C['olive'],2)
    c.ellipse((x+235*s,y-31*s,x+248*s,y-18*s),fill=C['cyan'])
    for a in range(90,120,8):c.line(P([(a,14),(a,36)]),'#748073',2)

def pack(w,h):
    c=Canvas(w,h);c.environment()
    shade=Image.new('RGBA',(w,h),(7,12,14,216)); c.im=Image.alpha_composite(c.im.convert('RGBA'),shade).convert('RGB');c.d=ImageDraw.Draw(c.im)
    c.note('Field Pack')
    top=112; bottom=c.H-112
    c.relay(64,top,36);c.text((128,top-8),"ELIAS'S FIELD PACK",54,'white','title')
    c.text((128,top+52),'FIELD EQUIPMENT  /  THE DEAD STATION',18,'olive','medium')
    c.text((1856,top+27),'PAUSED',18,'cyan','medium',anchor='rt')
    c.line([(64,top+104),(1856,top+104)],C['line'])
    ltop=top+152
    for i,label in enumerate(['Equipment','Supplies','Components','Mission Items']):
        yy=ltop+i*66
        if i==0:c.box((64,yy-16,336,yy+36),'#263333');c.box((64,yy-16,68,yy+36),C['amber'])
        c.text((88,yy),label,25,'white' if i==0 else 'olive','medium')
    c.text((88,bottom-68),'INSPECTION',16,'olive','medium')
    c.text((88,bottom-40),'Your chapter equipment.',20,'olive')
    c.line([(368,ltop-16),(368,bottom-16)],C['line'])
    c.text((408,ltop-13),'EQUIPMENT',18,'olive','medium')
    c.box((408,ltop+34,816,ltop+150),'#263333');c.box((408,ltop+34,412,ltop+150),C['cyan'])
    c.text((436,ltop+60),'ROOK-5',31,'white','title');c.text((436,ltop+105),'EQUIPPED',17,'cyan','medium')
    c.text((780,ltop+90),'01',22,'olive',anchor='rt')
    c.box((408,ltop+166,816,ltop+282),'#182123')
    c.text((436,ltop+193),'Survey Optic',27,'white','title');c.text((436,ltop+238),'INSTALLED',17,'olive','medium')
    c.text((780,ltop+222),'01',22,'olive',anchor='rt')
    c.box((864,ltop-16,1856,bottom-16),'#182123')
    c.text((904,ltop+21),'ROOK-5',48,'white','title');c.text((1816,ltop+32),'EQUIPPED',18,'cyan','medium',anchor='rt')
    rifle(c,1040,ltop+166,1.55)
    c.line([(904,ltop+352),(1816,ltop+352)],C['line'])
    c.text((904,ltop+382),'MAGAZINE',18,'olive','medium');c.text((1160,ltop+382),'RESERVE',18,'olive','medium');c.text((1440,ltop+382),'SURVEY OPTIC',18,'olive','medium')
    c.text((904,ltop+421),'04 / 05',33,'white','title');c.text((1160,ltop+421),'25',33,'white','title');c.text((1440,ltop+427),'Installed',25,'cyan')
    c.text((904,ltop+492),'A manually cycled carbine. The Survey Optic provides',24,'white')
    c.text((904,ltop+526),'a closer sight picture after workshop calibration.',24,'white')
    c.line([(64,bottom+20),(1856,bottom+20)],C['line'])
    c.text((64,bottom+52),'I / ESC   Close',21,'white','medium');c.text((320,bottom+52),'UP / DOWN   Select',21,'olive');c.text((640,bottom+52),'LEFT / RIGHT   Category',21,'olive')
    c.text((1856,bottom+54),'Illustrative state • runtime uses real chapter progress',18,'olive',anchor='rt')
    return c.save('EliasFieldPack')

if __name__=='__main__':
    files=[]
    for resolution in [(1920,1080),(2560,1600)]:
        for fn in [menu,hud,pack]: files.append(fn(*resolution))
    data={'purpose':'Original UI layout mockups, not Unreal captures','resolutions':[[1920,1080],[2560,1600]],'source':'render_mockups.py','fonts':'../Fonts (SIL OFL 1.1)','background':'Original procedural graphic blockout; no borrowed game pixels','files':[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files]}
    (ROOT/'manifest.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))
