"""Original deterministic seamless surface masks/normals; no photo or external texture."""
import bpy,numpy as np,json
from pathlib import Path
root=Path(__file__).resolve().parent; size=512;rng=np.random.default_rng(2118)
def smooth(a,n):
 for _ in range(n):a=(a+np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1))/5
 return a
coarse=smooth(rng.random((size,size)),90);coarse=(coarse-coarse.min())/(coarse.max()-coarse.min())
fine=rng.random((size,size));medium=smooth(fine,5);medium=(medium-medium.min())/(medium.max()-medium.min())
noise=.62*coarse+.30*medium+.08*fine
streak=smooth(rng.random((size,size)),5)
for _ in range(32):streak=(streak+np.roll(streak,1,0)+np.roll(streak,-1,0))/3
streak=(streak-streak.min())/(streak.max()-streak.min())
def save(name,pixels):
 img=bpy.data.images.new(name,width=size,height=size,alpha=True);img.colorspace_settings.name='Non-Color';img.pixels.foreach_set(pixels.astype(np.float32).ravel());img.filepath_raw=str(root/(name+'.png'));img.file_format='PNG';img.save()
mask=np.ones((size,size,4));mask[:,:,0]=noise;mask[:,:,1]=streak;mask[:,:,2]=medium;save('T_CR05_SurfaceMask',mask)
height=.75*medium+.25*fine;gx=(np.roll(height,-1,1)-np.roll(height,1,1))*.28;gy=(np.roll(height,-1,0)-np.roll(height,1,0))*.28
normal=np.stack((-gx,-gy,np.ones_like(gx)),axis=2);normal/=np.linalg.norm(normal,axis=2,keepdims=True)
rgba=np.ones((size,size,4));rgba[:,:,:3]=normal*.5+.5;save('T_CR05_SurfaceNormal',rgba)
(root/'surface-provenance.json').write_text(json.dumps({'author':'Cinder Relay original mathematical synthesis','seed':2118,'size':size,'channels':{'mask':'R macro/micro noise; G directional wear; B fine height','normal':'RGB tangent normal'},'third_party_samples':False},indent=2),encoding='utf-8')
print('CR05_SURFACES_PASS',size)
