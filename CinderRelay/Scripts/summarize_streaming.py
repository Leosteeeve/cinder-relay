"""Summarize the bounded Development route; does not launch/repeat a test.

Usage: python summarize_streaming.py <Saved/Phase01B> <game-log> <output.json>
Raw CSV and Insights trace remain separate local evidence, never budget claims.
"""
import csv
import datetime as dt
import json
from pathlib import Path
import re
import statistics
import sys

root, log, output = map(Path, sys.argv[1:4])
frames = list(csv.DictReader((root / 'frames.csv').open(encoding='utf-8-sig')))
memory = list(csv.DictReader((root / 'memory.csv').open(encoding='utf-8-sig')))


def distribution(values):
    values = sorted(values)
    if not values:
        return None
    def p(q):
        return values[min(len(values)-1, int((len(values)-1)*q))]
    return dict(n=len(values), median=p(.5), p95=p(.95), p99=p(.99), maximum=max(values), over_50ms=sum(v>50 for v in values))


cycle_start = next((i+1 for i in range(len(frames)-1) if frames[i]['stage']=='relay_result' and frames[i+1]['stage']=='walk'), len(frames))
cycle_end = max((i+1 for i, r in enumerate(frames) if r['stage']=='bunker_checkpoint' and r['cycle']=='3'), default=cycle_start)
segments = {
    'all_recorded': frames,
    'three_cycles': frames[cycle_start:cycle_end],
    'walking': [r for r in frames if r['stage'] == 'walk'],
}
metrics = {name: {field: distribution([float(r[field]) for r in rows if float(r[field]) > 0])
                  for field in ('frame_ms','game_thread_ms','render_thread_ms','gpu_ms')}
           for name, rows in segments.items()}
pattern = re.compile(r'\[([\d.\-:]+)\].*CR_STREAM ([ABC]) (\w+) t=([\d.]+) request=(\d+).*loaded=(\d) visible=(\d).*witness_valid=(\d)')
timeline, requested, latency = [], {}, []
for line in log.read_text(encoding='utf-8-sig', errors='replace').splitlines():
    match = pattern.search(line)
    if not match:
        continue
    stamp, zone, event, game_t, request, loaded, visible, witness = match.groups()
    clock = dt.datetime.strptime(stamp, '%Y.%m.%d-%H.%M.%S:%f').timestamp()
    row = dict(timestamp=stamp, zone=zone, event=event, game_time=float(game_t), request=int(request), loaded=int(loaded), visible=int(visible), witness_valid=int(witness))
    timeline.append(row)
    key = (zone, request)
    if event == 'LoadRequested': requested[key] = clock
    if event == 'Ready' and key in requested:
        # Veto/cancel/retry B requests 1-4 belong to the explicit fault scenario.
        latency.append(dict(zone=zone, request=int(request), wall_ms=round((clock-requested.pop(key))*1000, 3), fault_scenario=zone=='B' and int(request)<=4))
checkpoints = {}
for cycle in ('1','2','3'):
    rows = [r for r in memory if r['stage']=='bunker_checkpoint' and r['cycle']==cycle]
    if rows:
        checkpoints[cycle] = {k: statistics.median(int(r[k]) for r in rows) for k in ('working_set_bytes','private_commit_bytes')}
result = dict(
    acceptance=json.loads((root/'acceptance.json').read_text(encoding='utf-8-sig')),
    frames=metrics, frame_count=len(frames), duration_seconds=float(frames[-1]['elapsed']) if frames else None,
    process_memory_peak={k:max(int(r[k]) for r in memory) for k in ('working_set_bytes','private_commit_bytes')} if memory else {},
    same_bunker_checkpoints=checkpoints,
    checkpoint_private_delta_bytes=checkpoints.get('3',{}).get('private_commit_bytes',0)-checkpoints.get('1',{}).get('private_commit_bytes',0),
    load_ready_wall_ms=latency, unloaded_events={z:sum(r['zone']==z and r['event']=='Unloaded' for r in timeline) for z in 'ABC'},
    streaming_timeline=timeline,
    limitations=['Frame counters are previous engine frame samples; zero GPU/GT samples are unavailable, not zero cost.',
                 'Memory/CPU traces and opt-in route instrumentation add overhead; this is diagnostic greybox evidence.',
                 'Startup before actor creation is in the game log/trace, not frames.csv.',
                 'Process working set and private commit are distinct; neither is dedicated VRAM.'])
output.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('streaming_timeline','load_ready_wall_ms')}, indent=2))
