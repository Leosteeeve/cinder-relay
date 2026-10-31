"""Offline summary of the opt-in combat route; never starts or repeats a run."""
import csv,json,statistics,sys
from pathlib import Path
root,out=map(Path,sys.argv[1:3])
frames=list(csv.DictReader((root/'frames.csv').open(encoding='utf-8-sig')))
memory=list(csv.DictReader((root/'memory.csv').open(encoding='utf-8-sig')))
def metrics(rows):
    result={}
    for key in ['frame_ms','game_thread_ms','render_thread_ms','gpu_ms']:
        values=sorted(float(r[key]) for r in rows if float(r[key])>0)
        if values:
            result[key]=dict(n=len(values),median=statistics.median(values),p95=values[int((len(values)-1)*.95)],p99=values[int((len(values)-1)*.99)],maximum=max(values),over_50ms=sum(v>50 for v in values))
    return result
groups=dict(all_recorded=frames,combat=[r for r in frames if r['stage']=='fight'],ai_navigation=[r for r in frames if r['scenario']=='0' and r['stage'] in ['walk','receive','hidden']],post_combat_traversal=[r for r in frames if r['scenario']=='1' and r['stage']=='walk'])
if any(r['stage'].startswith('03_') for r in frames):
    groups.update(assembly=[r for r in frames if r['stage']=='03_full'],return_to_gameplay=[r for r in frames if r['stage'] in ('03_ads','03_fire','03_reload')],optional_bypass=[r for r in frames if r['scenario']=='3' and r['stage']=='walk'])
result=dict(acceptance=json.loads((root/'acceptance.json').read_text(encoding='utf-8-sig')),frames={k:metrics(v) for k,v in groups.items()},frame_count=len(frames),duration_seconds=float(frames[-1]['elapsed']) if frames else 0,process_memory_peak={k:max(int(r[k]) for r in memory) for k in ['working_set_bytes','private_commit_bytes']} if memory else {},settings=(root/'settings.txt').read_text(encoding='utf-8-sig'),limits=['Native thread/GPU counters refer to previous engine frame and cannot be added together.','Automated route is not human feel acceptance; combat segment length is reported, not padded.','Process commit/working set are not dedicated VRAM.','Trace settings and external conditions must be reported separately.'])
fight=groups['combat']
result['segments']={k:dict(rows=len(v),recorded_frame_seconds=sum(float(r['frame_ms']) for r in v)/1000) for k,v in groups.items()}
result['memory_samples_at_stage_boundaries']=[r for i,r in enumerate(memory) if i==0 or i==len(memory)-1 or r['stage']!=memory[i-1]['stage']]
result['combat_duration_seconds']=sum(float(r['frame_ms']) for r in fight)/1000
# Separate encounters may span restarts and a cinematic; that gap is not combat time.
result['combat_elapsed_span_seconds']=float(fight[-1]['elapsed'])-float(fight[0]['elapsed']) if fight else 0
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['settings','limits']},indent=2))
