"""Summarize the completed Phase05 low-overhead route; never launch gameplay."""
import csv
import json
import math
import re
import statistics
import sys
from pathlib import Path

saved, evidence = map(Path, sys.argv[1:3])

def stats(values):
    values = sorted(values)
    if not values:
        return None
    return {'n': len(values), 'p50': statistics.median(values),
            'p95': values[math.ceil(len(values)*.95)-1],
            'p99': values[math.ceil(len(values)*.99)-1], 'max': values[-1]}

def metrics(rows):
    return {key: stats([float(row[key]) for row in rows if float(row[key]) > 0])
            for key in ('frame_ms', 'game_ms', 'render_ms', 'gpu_ms')}

report = {'conditions': [
    'Median p50 and nearest-rank p95/p99; small save/restore samples are not population estimates.',
    'Windows Development, 1920x1080, Epic groups 3, ScreenPercentage100, native rendering; no frame generation.',
    'No requested Insights/allocation trace; native previous-frame counters and 1Hz process memory.',
    'Enhanced Input route automation, lifecycle faults and pause remain measurement overhead.',
    'No repeated screenshots during samples; each route requests one final receipt screenshot.',
    'Menu/held bootstrap/travel are absent from CSV; native SafeControl logs report reconstruction separately.',
    'Position-based zone samples include movement and changing visibility, not isolated fixed-camera GPU benchmarks.',
    'GT/RT/GPU counters are not additive. Process memory is not dedicated VRAM or proof of leak freedom.',
    'Automated route durations are not first-time human pacing. No 12-16 minute acceptance is claimed.'
], 'routes': {}, 'processes': json.loads((evidence/'process-results.json').read_text(encoding='utf-8-sig'))}
for route in (1, 2, 3):
    root = saved/'Phase04'/str(route)
    rows = list(csv.DictReader((root/'frames.csv').open(encoding='utf-8-sig')))
    memory = list(csv.DictReader((root/'memory.csv').open(encoding='utf-8-sig')))
    log = (evidence/f'packaged-route{route}.log').read_text(encoding='utf-8-sig', errors='replace')
    groups = {'all_recorded': rows,
              'yard': [r for r in rows if float(r['x']) < 1600],
              'workshop': [r for r in rows if 1600 <= float(r['x']) < 3600],
              'bunker': [r for r in rows if float(r['x']) >= 3600],
              'assembly': [r for r in rows if r['stage'] == 'bench_full'],
              'normal_traversal': [r for r in rows if r['stage'] == 'walk'],
              'ending': [r for r in rows if r['stage'] == 'ending']}
    report['routes'][route] = {
        'acceptance': json.loads((root/'acceptance.json').read_text()),
        'settings': (root/'settings.txt').read_text(),
        'frames': {key: metrics(value) for key, value in groups.items()},
        'over_50ms': [r for r in rows if float(r['frame_ms']) > 50],
        'serialize_ms': stats([float(v) for v in re.findall(r'CR04_SAVE SerializeDispatch ms=([\d.]+)', log)]),
        'save_callback_ms': stats([float(v) for v in re.findall(r'CR04_SAVE WriteCompleted.*?latency_ms=([\d.]+)', log)]),
        'safe_control_ms': stats([float(v) for v in re.findall(r'CR04_RESTORE SafeControl.*?reconstruction_ms=([\d.]+)', log)]),
        'safe_control_events': [line for line in log.splitlines() if 'CR04_RESTORE SafeControl' in line],
        'streaming_timeline': [line for line in log.splitlines() if 'CR_STREAM ' in line or 'CR_GATE ' in line],
        'unloads': {z: len(re.findall(r'CR_STREAM '+z+r' Unloaded ', log)) for z in 'ABC'},
        'memory_peak_bytes': {k: max(int(r[k]) for r in memory) for k in ('working_set', 'private_commit')} if memory else {},
        'memory_boundaries': [r for i, r in enumerate(memory) if i == 0 or i == len(memory)-1 or r['stage'] != memory[i-1]['stage']],
    }
(evidence/'polish-summary.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k: {'acceptance': r['acceptance'], 'frames': r['frames'], 'spikes_over_50ms': len(r['over_50ms']),
    'serialize_ms': r['serialize_ms'], 'save_callback_ms': r['save_callback_ms'], 'safe_control_ms': r['safe_control_ms'],
    'unloads': r['unloads'], 'memory_peak_bytes': r['memory_peak_bytes']} for k, r in report['routes'].items()}, indent=2))
