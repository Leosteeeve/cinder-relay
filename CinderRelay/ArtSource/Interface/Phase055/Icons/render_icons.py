"""Original industrial-field item symbols; no external image or game artwork.

Schematic silhouettes describe approved chapter items, not new mechanics.
Transparent512x256 PNGs use a shared constrained palette. Editable source retained.
"""
from pathlib import Path
import hashlib, json
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
S = 2
WHITE = '#E8E3D8'
OLIVE = '#8E978B'
STEEL = '#364542'
DEEP = '#182423'
AMBER = '#C99553'
CYAN = '#77B6B0'


class Symbol:
    def __init__(self):
        self.im = Image.new('RGBA', (512*S, 256*S))
        self.d = ImageDraw.Draw(self.im)
    def box(self, r, fill, outline=None, width=2):
        self.d.rectangle(tuple(round(v*S) for v in r), fill, outline, width=width*S)
    def poly(self, points, fill, outline=None):
        pts=[(round(x*S),round(y*S)) for x,y in points]
        self.d.polygon(pts,fill)
        if outline:self.d.line(pts+[pts[0]],outline,3*S,joint='curve')
    def line(self, points, color=OLIVE, width=2):
        self.d.line([(round(x*S),round(y*S)) for x,y in points],color,width*S,joint='curve')
    def ellipse(self, r, fill, outline=None, width=2):
        self.d.ellipse(tuple(round(v*S) for v in r),fill,outline,width*S)
    def save(self, name):
        p=OUT/('CR055_Icon'+name+'.png')
        self.im.resize((512,256),Image.Resampling.LANCZOS).save(p,optimize=True)
        return p


def rook():
    s=Symbol()
    s.poly([(36,110),(104,110),(119,89),(286,89),(308,106),(471,106),(471,124),(308,124),(278,150),(217,150),(195,201),(174,195),(178,150),(106,142),(36,174)],STEEL,OLIVE)
    s.box((128,98,148,128),DEEP)
    for x in (164,174,184):s.line([(x,105),(x,132)],OLIVE)
    s.line([(310,112),(463,112)],WHITE,1)
    s.line([(56,120),(95,120),(109,131)],AMBER,3)
    s.line([(233,90),(233,78),(266,78),(266,90)],OLIVE,3)
    s.box((220,48,278,77),DEEP,OLIVE,3)
    s.ellipse((259,51,281,73),CYAN,WHITE,2)
    return s.save('Rook')


def optic():
    s=Symbol()
    s.poly([(158,95),(180,73),(328,73),(349,95),(349,158),(327,177),(178,177),(158,158)],STEEL,OLIVE)
    s.box((184,89,310,160),DEEP)
    s.ellipse((286,87,349,164),DEEP,OLIVE,3)
    s.ellipse((297,99,338,152),'#426F6A',CYAN,3)
    s.line([(304,111),(318,103)],WHITE,2)
    s.box((201,177,226,197),DEEP,OLIVE,2);s.box((283,177,309,197),DEEP,OLIVE,2)
    s.line([(178,91),(178,158)],AMBER,4)
    return s.save('Optic')


def ammo():
    s=Symbol()
    s.box((139,162,374,204),DEEP,OLIVE,3)
    for x in (154,198,242,286,330):
        s.poly([(x,157),(x,90),(x+7,67),(x+13,56),(x+20,67),(x+27,90),(x+27,157)],STEEL,OLIVE)
        s.line([(x+3,94),(x+24,94)],AMBER,4)
        s.box((x-2,155,x+29,165),AMBER)
        s.line([(x+8,103),(x+8,143)],WHITE,1)
    s.line([(159,184),(354,184)],OLIVE)
    return s.save('Ammo')


def module():
    s=Symbol()
    s.poly([(173,60),(316,60),(354,88),(354,193),(191,193),(157,164),(157,87)],STEEL,OLIVE)
    s.poly([(191,93),(354,88),(316,60),(173,60)],'#56625A',OLIVE)
    s.line([(191,93),(191,193)],OLIVE,3)
    s.box((212,113,333,165),DEEP,OLIVE,2)
    s.box((224,127,278,137),CYAN)
    s.box((224,145,264,149),OLIVE)
    s.box((305,122,320,151),AMBER)
    s.line([(222,60),(222,40),(286,40),(286,60)],OLIVE,7)
    s.line([(164,103),(178,113),(178,158)],AMBER,4)
    for x,y in ((204,104),(341,101),(204,181),(340,180)):s.ellipse((x-3,y-3,x+3,y+3),WHITE)
    return s.save('PowerModule')


if __name__ == '__main__':
    files=[rook(),optic(),ammo(),module()]
    (OUT/'manifest.json').write_text(json.dumps({'author':'Cinder Relay project / Phase055 original UI symbols','source':'render_icons.py','external_images':False,'format':'RGBA PNG512x256','public_repository_redistribution':'Original project source; no separate asset license granted','files':[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files]},indent=2)+'\n')
