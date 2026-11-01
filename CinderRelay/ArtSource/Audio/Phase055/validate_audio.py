"""Read-only source validation; writes only explicitly requested local evidence.
This validates PCM and loop continuity, not subjective auditory quality.
"""
import argparse
import hashlib
import json
from pathlib import Path
import wave

import numpy as np

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--evidence", required=True)
args = parser.parse_args()
evidence = Path(args.evidence).resolve()
evidence.mkdir(parents=True, exist_ok=True)
manifest = json.loads((root / "manifest.json").read_text())
results = []
for item in manifest["sounds"]:
    path = root / item["file"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with wave.open(str(path), "rb") as audio:
        assert audio.getframerate() == 48000 and audio.getsampwidth() == 2
        assert audio.getnchannels() == item["channels"]
        values = np.frombuffer(audio.readframes(audio.getnframes()), dtype="<i2").reshape((-1, audio.getnchannels())) / 32768.0
    checks = {"hash": digest == item["sha256"], "finite": bool(np.isfinite(values).all()),
              "not_silent": float(np.sqrt(np.mean(values * values))) > .00001,
              "headroom": float(np.max(np.abs(values))) < .75,
              "duration": abs(len(values) / 48000 - item["seconds"]) < .00001}
    if item["loop"]:
        differences = np.max(np.abs(np.diff(values, axis=0)), axis=1)
        seam = float(np.max(np.abs(values[-1] - values[0])))
        p995 = float(np.percentile(differences, 99.5))
        checks["loop_seam_within_normal_derivative"] = seam <= max(p995, 1 / 32768)
        seam_info = {"seam_delta": seam, "ordinary_derivative_p995": p995}
    else:
        checks["zero_endpoints"] = bool(np.max(np.abs(values[[0, -1]])) == 0)
        seam_info = {}
    results.append({"name": item["name"], "passed": all(checks.values()), "checks": checks, **seam_info})
report = {"passed": all(r["passed"] for r in results), "assets": len(results), "results": results,
          "boundary": "PCM decode, hashes, headroom and loop continuity only. Not actual engine playback or human auditory acceptance."}
(evidence / "source-validation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"passed": report["passed"], "assets": len(results), "evidence": str(evidence / "source-validation.json")}))
raise SystemExit(0 if report["passed"] else 1)
