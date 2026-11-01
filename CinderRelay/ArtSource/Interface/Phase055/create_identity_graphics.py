"""Editable original relay monogram and title overlays; OFL type remains separate.

This is vector/UI authoring, not a copied logo or a raster generation prompt.
Raster exports are antialiased from the same explicit paths, with no external image.
"""
from pathlib import Path
from hashlib import sha256
import json
from PIL import Image, ImageDraw, ImageFont

OUT=Path(__file__).resolve().parent
FONTS=OUT/'Fonts'
S=4
STEEL='#151B1D';WHITE='#E8E3D8';AMBER='#C99553';CYAN='#77B6B0'
MARK='''<g fill="none" stroke="#E8E3D8" stroke-width="28" stroke-linecap="square" stroke-linejoin="miter">
 <path id="open-c" d="M 310,142 H 190 L 134,198 V 314 L 190,370 H 310"/>
 <path id="relay-r" d="M 245,370 V 208 H 310 L 350,246 L 310,284 H 245 M 292,284 L 350,370"/>
 </g><g stroke="#C99553" stroke-width="20" fill="none"><path id="signal-contact" d="M 350,174 V 142 H 382"/></g>
 <circle id="carrier-point" cx="350" cy="112" r="9" fill="#77B6B0"/>'''
(OUT/'CR055_RelayMark.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512"><title>Cinder Relay original open circuit CR monogram</title>'+MARK+'</svg>',encoding='utf-8')
(OUT/'CR055_GameIcon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512"><title>Cinder Relay game icon</title><rect width="512" height="512" fill="#151B1D"/>'+MARK+'</svg>',encoding='utf-8')

def draw_mark(im,offset=(0,0),scale=1):
    d=ImageDraw.Draw(im)
    def pts(values):return [((x*scale+offset[0])*S,(y*scale+offset[1])*S) for x,y in values]
    for p in [[(310,142),(190,142),(134,198),(134,314),(190,370),(310,370)],[(245,370),(245,208),(310,208),(350,246),(310,284),(245,284)],[(292,284),(350,370)]]:
        d.line(pts(p),fill=WHITE,width=round(28*S*scale),joint='curve')
    d.line(pts([(350,174),(350,142),(382,142)]),fill=AMBER,width=round(20*S*scale))
    cx,cy=pts([(350,112)])[0];r=9*scale*S;d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=CYAN)

for filename,background in [('CR055_GameIcon.png',STEEL),('CR055_RelayMark.png',(0,0,0,0))]:
    im=Image.new('RGBA',(512*S,512*S),background);draw_mark(im);im.resize((512,512),Image.Resampling.LANCZOS).save(OUT/filename)

title='''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="420" viewBox="0 0 1500 420">
 <title>CINDER RELAY — The Last Signal, editable title typography</title>
 <defs><style>@font-face{font-family:BarlowCondensed;src:url(Fonts/BarlowCondensed-SemiBold.ttf)}@font-face{font-family:Barlow;src:url(Fonts/Barlow-Medium.ttf)}</style></defs>
 <g transform="translate(-38,-40) scale(.82)">'''+MARK+'''</g>
 <text id="title" x="390" y="222" font-family="BarlowCondensed, sans-serif" font-size="190" letter-spacing="9" fill="#E8E3D8">CINDER RELAY</text>
 <path d="M 400,277 H 458" stroke="#C99553" stroke-width="5"/>
 <text id="subtitle" x="490" y="286" font-family="Barlow, sans-serif" font-size="30" letter-spacing="9" fill="#C99553">THE LAST SIGNAL</text>
</svg>'''
(OUT/'CR055_TitleTypography.svg').write_text(title,encoding='utf-8')

font_records=[]
for p in sorted(FONTS.iterdir()):
    if p.is_file():
        folder='barlowcondensed' if 'Condensed' in p.name else 'barlow'
        font_records.append({'file':p.relative_to(OUT).as_posix(),'source_url':f'https://raw.githubusercontent.com/google/fonts/main/ofl/{folder}/{p.name}','author':'The Barlow Project Authors; principal designer Jeremy Tribby','license':'SIL Open Font License 1.1','public_repository_redistribution':True,'required_notice':'Retain copyright and OFL.txt with font copies. Font itself must remain OFL. Do not sell font by itself.','modifications':'None; unmodified TTF binaries.','sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
(OUT/'font-provenance.json').write_text(json.dumps({'verified_on':'2026-11-01','upstream':'https://github.com/jpt/barlow','license_url':'https://raw.githubusercontent.com/google/fonts/main/ofl/barlow/OFL.txt','files':font_records},indent=2),encoding='utf-8')
print(json.dumps({'created':['CR055_RelayMark.svg','CR055_GameIcon.svg','CR055_GameIcon.png','CR055_RelayMark.png','CR055_TitleTypography.svg','font-provenance.json']}))

# Promotional composites are optional; runtime always imports the title-free plate.
# The SVG above retains live text and the Blender source retains all scene objects.
def spaced(draw,xy,content,font,spacing,fill):
    x,y=xy
    for ch in content:
        draw.text((x,y),ch,font=font,fill=fill,stroke_width=0)
        x+=draw.textlength(ch,font=font)+spacing

exports=[]
for orientation in ('Landscape','Portrait'):
    source=OUT/f'CR055_KeyArt_{orientation}.png'
    if not source.exists():continue
    im=Image.open(source).convert('RGBA')
    overlay=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(overlay)
    portrait=orientation=='Portrait'
    x,y=(122,150) if portrait else (142,220)
    size=194 if portrait else 170
    face=ImageFont.truetype(str(FONTS/'BarlowCondensed-SemiBold.ttf'),size)
    sub=ImageFont.truetype(str(FONTS/'Barlow-Medium.ttf'),31 if portrait else 28)
    spaced(d,(x,y),'CINDER',face,8,WHITE)
    spaced(d,(x,y+size*.90),'RELAY',face,8,WHITE)
    d.line((x+4,y+size*2.04,x+72,y+size*2.04),fill=AMBER,width=4)
    spaced(d,(x+100,y+size*1.96),'THE LAST SIGNAL',sub,5,AMBER)
    im=Image.alpha_composite(im,overlay).convert('RGB')
    target=OUT/f'CR055_Cover_{orientation}.png';im.save(target)
    # An editable SVG per cover explicitly references its original plate and live type.
    w,h=im.size
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
 <defs><style>@font-face{{font-family:BarlowCondensed;src:url(Fonts/BarlowCondensed-SemiBold.ttf)}}@font-face{{font-family:Barlow;src:url(Fonts/Barlow-Medium.ttf)}}</style></defs>
 <image id="original-blender-plate" href="CR055_KeyArt_{orientation}.png" width="{w}" height="{h}"/>
 <g id="editable-title" fill="{WHITE}" font-family="BarlowCondensed" font-size="{size}" letter-spacing="8">
  <text x="{x}" y="{y+face.getmetrics()[0]}">CINDER</text><text x="{x}" y="{y+size*.90+face.getmetrics()[0]}">RELAY</text>
 </g><path d="M {x+4},{y+size*2.04} H {x+72}" stroke="{AMBER}" stroke-width="4"/>
 <text id="editable-tagline" x="{x+100}" y="{y+size*1.96+sub.getmetrics()[0]}" fill="{AMBER}" font-family="Barlow" font-size="{31 if portrait else 28}" letter-spacing="5">THE LAST SIGNAL</text>
</svg>'''
    (OUT/f'CR055_Cover_{orientation}.svg').write_text(svg,encoding='utf-8')
    exports.append({'file':target.name,'width':w,'height':h,'sha256':sha256(target.read_bytes()).hexdigest()})
if exports:
    print(json.dumps({'promotional_composites':exports}))
