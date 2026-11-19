"""Summarize sealed local captures; never launches gameplay or changes caches."""
import argparse, csv, json, math, statistics
from pathlib import Path

def read(path):
    with path.open(encoding='utf-8-sig') as source:
        return list(csv.DictReader(source))

def stats(rows):
    result={'frames':len(rows),'over_50ms':sum(float(r['frame_ms'])>50 for r in rows)}
    for key in ('frame_ms','game_ms','render_ms','gpu_ms'):
        values=sorted(float(r[key]) for r in rows if float(r[key])>0)
        result[key]=dict(p50=statistics.median(values),p95=values[math.ceil(len(values)*.95)-1],p99=values[math.ceil(len(values)*.99)-1],maximum=values[-1]) if values else None
    return result

def run(folder):
    rows=read(folder/'frames.csv')
    combat=[r for r in rows if r['stage']=='fight']
    first=float(combat[0]['elapsed']) if combat else -1
    groups={'all_active':rows,'combat':combat,'slide_all':[r for r in rows if r['stage'].startswith('slide_')],
            'slide_active':[r for r in rows if r['stage']=='slide_active'],
            'first_combat_second':[r for r in combat if float(r['elapsed'])<first+1],
            'walk':[r for r in rows if r['stage']=='walk']}
    result={'groups':{k:stats(v) for k,v in groups.items()},
            'spikes':[r for r in rows if float(r['frame_ms'])>50],
            'settings':(folder/'settings.txt').read_text(encoding='utf-8-sig'),
            'acceptance':json.loads((folder/'acceptance.json').read_text(encoding='utf-8-sig'))}
    memory=read(folder/'memory.csv')
    if memory:
        result['memory_MiB']={k:{'minimum':min(float(r[k]) for r in memory)/1048576,'maximum':max(float(r[k]) for r in memory)/1048576} for k in memory[0] if k not in ('elapsed','stage')}
    return result

parser=argparse.ArgumentParser()
parser.add_argument('--baseline',type=Path,required=True)
parser.add_argument('--candidate',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
report={'method':'Median p50, nearest-rank p95/p99; previous-frame GT/RT/GPU counters are not additive. Active-pawn samples exclude startup. World delta can cap at400ms; maxima are not necessarily full wall-clock stalls.',
        'limits':'Different content builds, same native1080p Epic route inputs. Manual doors change traversal; combat/slide are the closest paired segments. Existing caches retained; not cold shader caches. No human pacing or isolated UI/audio cost claim.',
        'baseline':run(args.baseline),'candidate':run(args.candidate)}
assert report['baseline']['settings']==report['candidate']['settings'],'Mismatched benchmark settings'
assert report['baseline']['acceptance']['passed'] and report['candidate']['acceptance']['passed']
args.output.write_text(json.dumps(report,indent=2),encoding='utf-8')
lines=['| Segment | Baseline frames / p95 ms | Candidate frames / p50 / p95 / p99 ms | Candidate GT / RT / GPU p95 ms | Candidate >50ms |','|---|---|---|---|---|']
for name,after in report['candidate']['groups'].items():
    before=report['baseline']['groups'][name]; frame=after['frame_ms']
    if not frame or not before['frame_ms']:continue
    times=' / '.join(f'{frame[k]:.3f}' for k in ('p50','p95','p99'))
    counters=' / '.join(f"{after[k]['p95']:.3f}" if after[k] else 'n/a' for k in ('game_ms','render_ms','gpu_ms'))
    lines.append(f"| {name} | {before['frames']} / {before['frame_ms']['p95']:.3f} | {after['frames']} / {times} | {counters} | {after['over_50ms']} |")
args.output.with_suffix('.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines))
