"""Read sealed local CSV snapshots; no gameplay, cache changes or benchmark reruns."""
import csv,json,math,statistics
from pathlib import Path
root=Path(__file__).resolve().parents[2]/'.environment-local/phase-05-4'
def stats(rows):
    result={'frames':len(rows),'over_50ms':sum(float(r['frame_ms'])>50 for r in rows)}
    for key in ['frame_ms','game_ms','render_ms','gpu_ms']:
        v=sorted(float(r[key]) for r in rows if float(r[key])>0)
        result[key]=dict(p50=statistics.median(v),p95=v[math.ceil(len(v)*.95)-1],p99=v[math.ceil(len(v)*.99)-1],maximum=v[-1]) if v else None
    return result
report={'conditions':'1080p Epic3 ScreenPercentage100 native; no frame generation/recording/requested trace. Native previous-frame counters and1Hz process sampler; uncontrolled desktop/power/temperature. Small samples, not guarantees.','runs':{}}
for label,folder in [('before','baseline-performance'),('after','packaged-acceptance')]:
    rows={i:list(csv.DictReader((root/folder/'SavedPhase04'/str(i)/'frames.csv').open(encoding='utf-8-sig'))) for i in [1,2,3]}
    groups={
        'Combat': [r for r in rows[1] if r['stage']=='fight'],
        'Yard traversal':[r for r in rows[1] if r['stage']=='walk' and float(r['x'])<1600],
        'Slide and hip fire':[r for r in rows[1] if r['stage']=='slide_active'],
        'Reload after slide':[r for r in rows[1] if r['stage']=='slide_reload'],
        'Workshop assembly':[r for r in rows[2] if r['stage']=='bench_full'],
        'Workshop movement':[r for r in rows[2] if r['stage']=='walk' and 1600<=float(r['x'])<3600],
        'Bunker':[r for r in rows[3] if float(r['x'])>=3600],
        'Streaming traversal':[r for r in rows[3] if r['stage']=='walk']}
    report['runs'][label]={'groups':{n:stats(r) for n,r in groups.items()},'spikes':[dict(route=i,**r) for i,rr in rows.items() for r in rr if float(r['frame_ms'])>50]}
(root/'performance-comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
lines=['| Sample | Frames | Before p95 ms | After p50 / p95 / p99 ms | GT / RT / GPU p95 ms | >50ms |','|---|---:|---:|---|---|---:|']
for name,after in report['runs']['after']['groups'].items():
    before=report['runs']['before']['groups'][name]['frame_ms'];f=after['frame_ms']
    if not f:continue
    old=f"{before['p95']:.3f}" if before else 'n/a'
    times=' / '.join(f"{f[k]:.3f}" for k in ['p50','p95','p99'])
    counters=' / '.join(f"{after[k]['p95']:.3f}" if after[k] else 'n/a' for k in ['game_ms','render_ms','gpu_ms'])
    lines.append(f"| {name} | {after['frames']} | {old} | {times} | {counters} | {after['over_50ms']} |")
(root/'performance-table.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines))
