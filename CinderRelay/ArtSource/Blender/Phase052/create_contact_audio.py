"""Original synthesized, quiet fictional calibration Foley; no downloaded samples."""
import json,math,random,struct,wave
from pathlib import Path
dest=Path(__file__).resolve().parents[2]/'Audio/Phase052'
dest.mkdir(parents=True,exist_ok=True);rate=48000;receipt=[]
for name,duration,beats in [('Seat',.26,[(0,.17,480),(.065,.075,720)]),('Secure',.38,[(0,.09,650),(.09,.08,740),(.19,.11,520)])]:
    rng=random.Random(5202);samples=[];filtered=0
    for i in range(round(duration*rate)):
        t=i/rate;filtered=.68*filtered+.32*rng.uniform(-1,1);v=0
        for start,amp,hz in beats:
            dt=t-start
            if dt>=0:v+=amp*math.exp(-dt*68)*(math.sin(math.tau*hz*dt)*.55+filtered*.45)*(1-math.exp(-dt*1700))
        samples.append(max(-32767,min(32767,round(v*32767))))
    path=dest/('S_CR052_'+name+'.wav')
    with wave.open(str(path),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(struct.pack('<'+'h'*len(samples),*samples))
    receipt.append({'file':path.name,'seconds':duration,'sample_rate':rate,'authorship':'Original deterministic additive/noise synthesis','external_samples':False,'usage':'Quiet fictional exterior calibration cue; not recorded voice or real firearm operation'})
(dest/'provenance.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
