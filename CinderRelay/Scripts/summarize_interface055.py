"""Summarize sealed Phase055 evidence; never launch gameplay or change source evidence.

Example (run from the repository root after sealing both runs):
    python CinderRelay/Scripts/summarize_interface055.py
    python CinderRelay/Scripts/summarize_interface055.py --timer-csv path/to/timers.csv

Only performance-comparison.json and table.md under --root are written.
Exit 0 means the paired input gates passed, not performance or human acceptance.
"""

import argparse
import csv
import json
import math
import re
import statistics
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2] / ".environment-local/phase-05-5"
COUNTERS = ("frame_ms", "game_ms", "render_ms", "gpu_ms")
QUALITY_GROUPS = (
    "ViewDistance", "AntiAliasing", "Shadow", "GlobalIllumination", "Reflection",
    "PostProcess", "Texture", "Effects", "Foliage", "Shading",
)
EXPECTED_SETTINGS = {
    "viewport": "1920x1080", "r.ScreenPercentage": "100",
    "r.DynamicRes.OperationMode": "0", "r.VSync": "0", "t.MaxFPS": "0",
    **{f"sg.{name}Quality": "3" for name in QUALITY_GROUPS},
}
LIMITATIONS = [
    "Uncontrolled desktop workload, power state and temperature; small route samples.",
    "Whole-game counters are native previous-frame counters, not an attribution of UI or audio cost.",
    "Paired observations do not establish attributable causality or guarantee a 60 FPS target.",
    "No human visual, auditory or gameplay acceptance is established by this report.",
    "Trace recordings are separate diagnostics and must not be compared as untraced gameplay runs.",
    "CR055_HUDUpdate measures SetCombat; CR055_HUDTransient covers active transient updates only.",
    "CR055 UI/game audio scopes measure dispatch, not complete mixer, decoding or device cost.",
    "Engine audio scopes can overlap or nest; their totals must not be summed as a full mixer cost.",
    "Groups overlap and cannot be summed; nonpositive counter samples are excluded from percentiles.",
    "No trace or recording is requested by the paired command lines; external recording is not detectable.",
]


def stats(rows):
    """Use the same median / nearest-rank percentile policy as Phase054."""
    result = {
        "frames": len(rows),
        "over_50ms": sum(float(row["frame_ms"]) > 50 for row in rows),
    }
    for key in COUNTERS:
        values = sorted(float(row[key]) for row in rows if float(row[key]) > 0)
        result[key] = {
            "samples": len(values),
            "p50": statistics.median(values),
            "p95": values[math.ceil(len(values) * .95) - 1],
            "p99": values[math.ceil(len(values) * .99) - 1],
            "maximum": values[-1],
        } if values else None
    return result


def groups(rows):
    """Keep the existing Phase054 route and stage boundaries unchanged."""
    return {
        "Combat": [r for r in rows[1] if r["stage"] == "fight"],
        "Yard traversal": [r for r in rows[1] if r["stage"] == "walk" and float(r["x"]) < 1600],
        "Slide and hip fire": [r for r in rows[1] if r["stage"] == "slide_active"],
        "Reload after slide": [r for r in rows[1] if r["stage"] == "slide_reload"],
        "Workshop assembly": [r for r in rows[2] if r["stage"] == "bench_full"],
        "Workshop movement": [r for r in rows[2] if r["stage"] == "walk" and 1600 <= float(r["x"]) < 3600],
        "Bunker": [r for r in rows[3] if float(r["x"]) >= 3600],
        "Streaming traversal": [r for r in rows[3] if r["stage"] == "walk"],
    }


def read_run(folder):
    issues, processes, settings, routes = [], [], {}, {}
    process_path = folder / "process-results.json"
    try:
        processes = json.loads(process_path.read_text(encoding="utf-8-sig"))
        if not isinstance(processes, list) or not all(isinstance(p, dict) for p in processes):
            raise ValueError("expected an array of process receipts")
    except (OSError, ValueError) as error:
        issues.append(f"{process_path}: {error}")
        processes = []

    for route in (1, 2, 3):
        matches = [p for p in processes if p.get("route") == route]
        if len(matches) != 1:
            issues.append(f"Route {route}: expected exactly one process receipt; found {len(matches)}")
        for process in matches:
            for key in ("launcher_exit", "native_exit"):
                if process.get(key) != 0:
                    issues.append(f"Route {route}: {key}={process.get(key)!r}; expected 0")
            if process.get("forced_stop") is not False:
                issues.append(f"Route {route}: forced_stop must be explicitly false")
            acceptance = process.get("acceptance")
            if not isinstance(acceptance, dict) or acceptance.get("passed") is not True:
                issues.append(f"Route {route}: native acceptance did not pass")
            elif acceptance.get("route") != route:
                issues.append(f"Route {route}: native acceptance route mismatch")
            arguments = process.get("arguments", "")
            if not isinstance(arguments, str) or not arguments.strip():
                issues.append(f"Route {route}: missing command-line evidence")
            elif re.search(r"(?:^|\s)-(?:trace(?:=|\s|$)|tracefile=|CR055InterfaceCheck=)", arguments, re.I):
                issues.append(f"Route {route}: traced or interface-recording run cannot be the low-overhead pair")

        directory = folder / "SavedPhase04" / str(route)
        try:
            values = dict(line.split("=", 1) for line in
                          (directory / "settings.txt").read_text(encoding="utf-8-sig").splitlines() if "=" in line)
            settings[str(route)] = values
            for key, expected in EXPECTED_SETTINGS.items():
                if values.get(key) != expected:
                    issues.append(f"Route {route}: {key}={values.get(key)!r}; expected {expected}")
        except (OSError, ValueError) as error:
            issues.append(f"{directory / 'settings.txt'}: {error}")

        try:
            with (directory / "frames.csv").open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            if not rows:
                raise ValueError("no frame rows")
            for row in rows:
                if not row.get("stage"):
                    raise ValueError("missing frame stage")
                if not all(math.isfinite(float(row[key])) for key in (*COUNTERS, "x")):
                    raise ValueError("non-finite frame or position counter")
            routes[route] = rows
        except (OSError, ValueError, KeyError, TypeError) as error:
            issues.append(f"{directory / 'frames.csv'}: {error}")
            routes[route] = []

    if len(processes) != 3:
        issues.append(f"Expected three process receipts, found {len(processes)}")
    grouped = {name: stats(rows) for name, rows in groups(routes).items()}
    for name, sample in grouped.items():
        if not sample["frame_ms"]:
            issues.append(f"{name}: no positive frame-time samples")
    return {
        "source": str(folder), "input_gate_passed": not issues, "issues": issues,
        "process_results": processes, "recorded_settings": settings, "groups": grouped,
        "spikes": [dict(route=route, **row) for route, rows in routes.items()
                   for row in rows if float(row["frame_ms"]) > 50],
    }


def read_timers(path, explicitly_requested):
    result = {
        "source": str(path), "status": "unavailable", "issues": [],
        "project_scopes": [], "engine_audio_scopes": [],
        "coverage": "Selected CPU scope statistics only; not total HUD or audio mixer overhead.",
    }
    if not path.is_file():
        if explicitly_requested:
            result["issues"].append("Explicit timer CSV does not exist")
        return result
    required = ("Name", "Count", "I.Avg", "I.Max", "E.Avg", "E.Max")
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or any(key not in reader.fieldnames for key in required):
                raise ValueError(f"Expected TimingInsights columns: {', '.join(required)}")
            for row in reader:
                name = row["Name"]
                is_project = name.startswith("CR055_")
                is_engine_audio = not is_project and bool(re.search(
                    r"(?:Audio|FMixer|SoundMix|SoundClass|SoundSource)", name, re.I))
                if not (is_project or is_engine_audio):
                    continue
                values = [float(row[key]) for key in required[2:]]
                if not all(math.isfinite(value) and value >= 0 for value in values):
                    raise ValueError(f"Invalid timing values for {name}")
                item = {
                    "name": name, "count": int(row["Count"]),
                    "inclusive_average_ms": values[0] * 1000,
                    "inclusive_maximum_ms": values[1] * 1000,
                    "exclusive_average_ms": values[2] * 1000,
                    "exclusive_maximum_ms": values[3] * 1000,
                }
                result["project_scopes" if is_project else "engine_audio_scopes"].append(item)
        result["status"] = "available" if result["project_scopes"] else "no_project_scopes"
        if not result["project_scopes"]:
            result["issues"].append("No CR055_* rows found; absence is not zero overhead")
        for key in ("project_scopes", "engine_audio_scopes"):
            result[key].sort(key=lambda item: item["name"])
    except (OSError, ValueError, KeyError, TypeError) as error:
        result["status"] = "invalid"
        result["issues"].append(str(error))
    return result


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def number(sample, key):
    return f"{sample[key]:.3f}" if sample else "n/a"


def table(report):
    lines = [
        "# Phase055 paired performance evidence", "",
        f"Paired input gate: {'PASS' if report['input_gate_passed'] else 'FAIL'}. This is not a performance acceptance gate.", "",
        report["conditions"], "",
        "| Run | Route | Launcher exit | Native exit | Forced stop | Native acceptance |",
        "|---|---:|---:|---:|---|---|",
    ]
    for label, run in report["runs"].items():
        for process in run["process_results"]:
            receipt = process.get("acceptance") or {}
            passed = receipt.get("passed") if isinstance(receipt, dict) else None
            lines.append("| " + " | ".join(cell(value) for value in (
                label, process.get("route"), process.get("launcher_exit"), process.get("native_exit"),
                process.get("forced_stop"), passed)) + " |")
    for label, run in report["runs"].items():
        lines.extend(f"\n- {label}: {cell(issue)}" for issue in run["issues"])
    lines.extend([
        "", "| Sample | Baseline / candidate frames | Baseline p95 ms | Candidate p50 / p95 / p99 ms | Candidate GT / RT / GPU p95 ms | Baseline / candidate >50ms |",
        "|---|---:|---:|---|---|---:|",
    ])
    for name, candidate in report["runs"]["candidate"]["groups"].items():
        baseline = report["runs"]["baseline"]["groups"][name]
        frame = candidate["frame_ms"]
        times = " / ".join(number(frame, key) for key in ("p50", "p95", "p99"))
        counters = " / ".join(number(candidate[key], "p95") for key in COUNTERS[1:])
        lines.append(f"| {name} | {baseline['frames']} / {candidate['frames']} | {number(baseline['frame_ms'], 'p95')} | {times} | {counters} | {baseline['over_50ms']} / {candidate['over_50ms']} |")
    scopes = report["scope_diagnostics"]
    lines.extend(["", f"Optional CPU scope diagnostics: {scopes['status']}. {scopes['coverage']}"])
    lines.extend(f"\n- {cell(issue)}" for issue in scopes["issues"])
    for key, label in (("project_scopes", "Project scopes"), ("engine_audio_scopes", "Engine audio scopes (name-filtered)")):
        lines.extend(["", label, "", "| Scope | Count | Inclusive average / max ms | Exclusive average / max ms |", "|---|---:|---|---|"])
        for scope in scopes[key]:
            lines.append(f"| {cell(scope['name'])} | {scope['count']} | {scope['inclusive_average_ms']:.6f} / {scope['inclusive_maximum_ms']:.6f} | {scope['exclusive_average_ms']:.6f} / {scope['exclusive_maximum_ms']:.6f} |")
    lines.extend(["", "Limitations", "", *[f"- {item}" for item in LIMITATIONS]])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Phase055 local evidence root")
    parser.add_argument("--timer-csv", type=Path, help="Optional TimingInsights CSV; relative paths use the current directory")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"Evidence root does not exist: {root}")
    runs = {label: read_run(root / f"performance-{label}") for label in ("baseline", "candidate")}
    timer_path = args.timer_csv.resolve() if args.timer_csv else root / "interface-trace/Write-timers.csv"
    report = {
        "report_format_version": 1,
        "conditions": "Paired native 1920x1080 Epic3 runs, ScreenPercentage100, dynamic resolution/VSync off, uncapped. Native previous-frame counters; no requested trace or interface recording in the paired runs.",
        "percentile_policy": "Median p50; nearest-rank ceil(n*p)-1 p95/p99 over positive samples, matching Phase054.",
        "input_gate_passed": all(run["input_gate_passed"] for run in runs.values()),
        "runs": runs, "scope_diagnostics": read_timers(timer_path, args.timer_csv is not None),
        "limitations": LIMITATIONS,
    }
    output = table(report)
    (root / "performance-comparison.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (root / "table.md").write_text(output, encoding="utf-8")
    print(output)
    return 0 if report["input_gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
