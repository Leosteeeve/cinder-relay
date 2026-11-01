"""Read sealed local Phase04 evidence; never launches/repeats gameplay or mutates saves."""
import csv
import json
import re
import statistics
import sys
from pathlib import Path

saved, evidence = map(Path, sys.argv[1:3])
def stats(values):
    v = sorted(values)
    return dict(n=len(v), median=statistics.median(v), p95=v[int((len(v)-1)*.95)], maximum=max(v)) if v else None

result = {'routes': {}, 'limits': [
    'CSV frame counters exclude menu/held bootstrap and travel; bootstrap durations are separate native logs.',
    'Counters are previous-frame engine measurements; GT/RT/GPU cannot be added.',
    'Pause, injected faults, input automation and cpu/gpu/frame/bookmark/loadtime traces add overhead.',
    'Working set/private commit are process residency, not dedicated VRAM or proof of leak freedom.',
    'Three recovery cycles are bounded observations, not an endurance benchmark.',
]}
for route in (1,2,3):
    root = saved/'Phase04'/str(route)
    frames = list(csv.DictReader((root/'frames.csv').open(encoding='utf-8-sig')))
    memory = list(csv.DictReader((root/'memory.csv').open(encoding='utf-8-sig')))
    log = (evidence/f'packaged-route{route}.log').read_text(encoding='utf-8-sig',errors='replace')
    groups = {'recorded':frames,'traversal':[r for r in frames if r['stage']=='walk'],
              'assembly':[r for r in frames if r['stage']=='bench_full'],
              'save_windows':[r for r in frames if r['stage'] in ('wait_cp00','wait_cp01','wait_cp02')],
              'restored_frames':[r for r in frames if r['stage']=='restore_values']}
    data = dict(acceptance=json.loads((root/'acceptance.json').read_text(encoding='utf-8-sig')),
                frames={name:{key:stats([float(r[key]) for r in rows if float(r[key])>0]) for key in ('frame_ms','game_ms','render_ms','gpu_ms')} for name,rows in groups.items()},
                serialize_ms=stats([float(v) for v in re.findall(r'CR04_SAVE SerializeDispatch ms=([\d.]+)',log)]),
                save_callback_ms=stats([float(v) for v in re.findall(r'CR04_SAVE WriteCompleted.*?latency_ms=([\d.]+)',log)]),
                scan_ms=stats([float(v) for v in re.findall(r'CR04_SAVE ScanComplete.*?latency_ms=([\d.]+)',log)]),
                reconstruction_ms=stats([float(v) for v in re.findall(r'CR04_RESTORE SafeControl.*?reconstruction_ms=([\d.]+)',log)]),
                safe_control_events=[line for line in log.splitlines() if 'CR04_RESTORE SafeControl' in line],
                unloads={z:len(re.findall(r'CR_STREAM '+z+r' Unloaded ',log)) for z in 'ABC'},
                memory_peak={key:max(int(r[key]) for r in memory) for key in ('working_set','private_commit')} if memory else {},
                memory_boundaries=[r for i,r in enumerate(memory) if i==0 or i==len(memory)-1 or r['stage']!=memory[i-1]['stage']],
                settings=(root/'settings.txt').read_text(encoding='utf-8-sig'))
    result['routes'][route] = data
result['processes'] = json.loads((evidence/'process-results.json').read_text(encoding='utf-8-sig'))
(evidence/'packaged-summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:{key:v for key,v in r.items() if key not in ('memory_boundaries','settings','safe_control_events')} for k,r in result['routes'].items()},indent=2))
