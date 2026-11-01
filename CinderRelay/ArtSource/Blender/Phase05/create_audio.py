"""Original deterministic synthesis; no samples/voices/music from external sources.
Exports mono PCM for native Unreal attenuation/Sequencer. Generated WAVs are intermediates.
"""
import math,random,wave,array,json,argparse
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--export-dir',required=True);ap.add_argument('--only-loops',action='store_true');opt=ap.parse_args();out=Path(opt.export_dir);out.mkdir(parents=True,exist_ok=True)
rate=32000;rng=random.Random(211805);manifest=[]
def noise(n,smooth=.8):
 v=0;a=[]
 for i in range(n):v=v*smooth+rng.uniform(-1,1)*(1-smooth);a.append(v)
 return a
def emit(name,duration,fn,loop=False):
 if opt.only_loops and not loop:return
 cross=int(.2*rate) if loop else 0
 n=round(duration*rate)+cross;raw=noise(n,.87);fine=noise(n,.12);a=[fn(i/rate,raw[i],fine[i]) for i in range(n)]
 if loop:
  # Blend the tail into the discarded prefix, then remove that prefix. The last
  # sample and first retained sample are now adjacent samples of the same signal.
  for i in range(cross):u=i/(cross-1);a[n-cross+i]=a[n-cross+i]*(1-u)+a[i]*u
  a=a[cross:]
 else:
  for i in range(n):a[i]*=min(1,i/(rate*.002),(n-1-i)/(rate*.012))
 peak=max(abs(x) for x in a) or 1;a=[x*.7/peak for x in a]
 path=out/('S_CR05_'+name+'.wav')
 with wave.open(str(path),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(array.array('h',(int(x*32767) for x in a)).tobytes())
 manifest.append({'name':path.stem,'seconds':duration,'loop':loop,'sample_rate':rate,'peak':.7,'source':'Original deterministic synthesis, create_audio.py, seed 211805','license':'Original project source; no third-party sample license'})
tau=2*math.pi
emit('YardWind',8,lambda t,n,h:n*(.5+.15*math.sin(t*tau/8))+.025*math.sin(t*tau*127)*(math.sin(t*tau/4)**8),True)
emit('WorkshopHum',8,lambda t,n,h:.13*math.sin(t*tau*60)+.04*math.sin(t*tau*120)+n*.06,True)
emit('BunkerHum',8,lambda t,n,h:.14*math.sin(t*tau*45)+.03*math.sin(t*tau*89)+n*.08*(.8+.2*math.sin(t*tau/8)),True)
emit('RookShot',.65,lambda t,n,h:h*math.exp(-t*35)+.6*math.sin(t*tau*(145-70*t))*math.exp(-t*18)+n*.22*math.exp(-t*8))
emit('Impact',.35,lambda t,n,h:h*math.exp(-t*45)+.18*math.sin(t*tau*830)*math.exp(-t*15))
emit('Reload',2.4,lambda t,n,h:sum((h*.5+math.sin(t*tau*430)*.2)*math.exp(-(t-b)*45) if t>=b else 0 for b in(.08,.65,1.6,2.15)))
emit('FootYard',.24,lambda t,n,h:n*math.exp(-t*23)+h*.2*math.exp(-t*45))
emit('FootMetal',.28,lambda t,n,h:n*math.exp(-t*30)+.2*math.sin(t*tau*260)*math.exp(-t*22))
emit('PowerRise',4,lambda t,n,h:(n*.12+math.sin(t*tau*(42+3*t))*.2)*min(1,t)*min(1,4-t)+sum(h*.15*math.exp(-(t-b)*40) if t>=b else 0 for b in(.1,1.1,2.3)))
emit('SignalEnding',8,lambda t,n,h:(n*.12+math.sin(t*tau*420)*.08*(.3+.7*math.sin(t*tau*1.7)**2))*min(1,t)*min(1,8-t))
emit('Calibration',.8,lambda t,n,h:math.sin(t*tau*(660 if t<.24 else 880))*math.exp(-t*4))
if opt.only_loops:
 prior=json.loads((out/'audio-manifest.json').read_text());names={s['name'] for s in manifest};manifest += [s for s in prior if s['name'] not in names]
(out/'audio-manifest.json').write_text(json.dumps(manifest,indent=2));print('CR05_AUDIO_SOURCE_PASS',len(manifest))
