"""Original CINDER RELAY mechanical audio. No recordings, samples, voice or music.

Deterministic offline synthesis authored for the fictional game. Short filtered
noise transients, inharmonic resonances and bounded reflections replace the old
single-tone prototype cues. This is sound design, not a firearm simulation.
Run with the bundled NumPy Python. Existing outputs require an explicit
--replace-owned flag and matching hashes from this script's previous manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import wave
from pathlib import Path

import numpy as np

RATE = 48000
ROOT = Path(__file__).resolve().parent
OWNER = "CinderRelay.Phase055.OriginalAudio.v1"
TAU = 2 * math.pi


def spectral_filter(raw: np.ndarray, lo: float = 0, hi: float = 10000) -> np.ndarray:
    frequency = np.fft.rfftfreq(len(raw), 1 / RATE)
    response = 1 / np.sqrt(1 + (frequency / hi) ** 4)
    if lo > 0:
        response *= (frequency / lo) ** 2 / np.sqrt(1 + (frequency / lo) ** 4)
    return np.fft.irfft(np.fft.rfft(raw) * response, len(raw))


def noise(n: int, seed: int, lo: float = 35, hi: float = 10000) -> np.ndarray:
    raw = np.random.default_rng(seed).normal(0, 1, n)
    return spectral_filter(raw, lo, hi)


def time(seconds: float) -> np.ndarray:
    return np.arange(round(seconds * RATE), dtype=np.float64) / RATE


def envelope(t: np.ndarray, decay: float, attack: float = .0008) -> np.ndarray:
    return (1 - np.exp(-t / attack)) * np.exp(-t / decay)


def contact(seconds: float, seed: int, weight: float = .5, metal: float = .4) -> np.ndarray:
    t = time(seconds)
    x = noise(len(t), seed, 90, 7800) * envelope(t, .013) * .65
    x += noise(len(t), seed + 1, 35, 600) * envelope(t, .035) * weight
    for i, hz in enumerate((327, 719, 1249, 2153, 3719)):
        x += metal * .14 / (1 + i * .25) * np.sin(TAU * hz * t) * envelope(t, .018 + .008 * i)
    return x


def place(target: np.ndarray, source: np.ndarray, at: float, gain: float = 1) -> None:
    start = round(at * RATE)
    count = min(len(source), len(target) - start)
    if count > 0:
        target[start:start + count] += source[:count] * gain


def clicks(seconds: float, seed: int, beats: list[tuple[float, float]], metal: float = .4) -> np.ndarray:
    x = np.zeros(len(time(seconds)))
    for i, (at, gain) in enumerate(beats):
        place(x, contact(.15, seed + i * 13, .55, metal), at, gain)
    return x


def shot(environment: str, variant: int) -> np.ndarray:
    t = time(.92 if environment == "Outdoor" else .78)
    seed = 55000 + variant * 139
    report = noise(len(t), seed, 120, 10500) * envelope(t, .025) * .75
    report += noise(len(t), seed + 1, 45, 1700) * envelope(t, .067) * .9
    report += .22 * np.sin(TAU * (112 * t - 155 * t * t)) * envelope(t, .048)
    place(report, contact(.12, seed + 2, .65, .35), .003, .25)
    left, right = report.copy(), report.copy()
    settings = {
        "Outdoor": [(0.072, .10), (.147, .06), (.259, .025)],
        "Workshop": [(.019, .22), (.041, .15), (.073, .09), (.117, .045)],
        "Bunker": [(.012, .20), (.026, .16), (.049, .095), (.083, .04)],
    }
    for i, (delay, gain) in enumerate(settings[environment]):
        reflection = spectral_filter(report, hi=3100 if environment == "Outdoor" else 5700)
        place(left, reflection, delay, gain)
        place(right, reflection, delay + .0025 + i * .0007, gain * .93)
    tail = noise(len(t), seed + 30, 100, 2700) * envelope(t, .13 if environment == "Outdoor" else .095, .025)
    left += tail * .06
    right += np.roll(tail, 117) * .06
    return np.column_stack((left, right))


def foot(surface: str, variant: int) -> np.ndarray:
    t = time(.38)
    seed = 55100 + variant * 71 + ("Concrete", "Metal", "Gravel", "Industrial").index(surface) * 1000
    x = noise(len(t), seed, 35, 570) * envelope(t, .045) * .8
    x += noise(len(t), seed + 1, 350, 5200) * envelope(t, .025) * .15
    if surface == "Metal":
        x += contact(.38, seed + 2, .2, 1.2) * .4
    elif surface == "Gravel":
        for i, at in enumerate((.012, .026, .045, .072, .097)):
            place(x, contact(.1, seed + 17 + i, .1, .01), at, .13 - i * .017)
        x += noise(len(t), seed + 8, 1800, 8500) * envelope(t, .065) * .17
    elif surface == "Industrial":
        x += contact(.38, seed + 2, .4, .26) * .28
        place(x, contact(.18, seed + 4, .2, .14), .042, .11)
    else:
        x += noise(len(t), seed + 8, 850, 4000) * envelope(t, .04) * .12
    return x


def periodic_noise(seconds: float, seed: int, lo: float, hi: float) -> np.ndarray:
    """Band-shaped periodic noise; FFT bins ensure a seamless circular domain."""
    n = round(seconds * RATE)
    freq = np.fft.rfftfreq(n, 1 / RATE)
    rng = np.random.default_rng(seed)
    shape = (1 - np.exp(-(freq / lo) ** 3)) / (1 + (freq / hi) ** 4)
    spectrum = (rng.normal(size=len(freq)) + 1j * rng.normal(size=len(freq))) * shape
    spectrum[0] = 0
    x = np.fft.irfft(spectrum, n)
    return x / max(1e-9, np.std(x))


def ambience(zone: str) -> np.ndarray:
    seconds = 16
    t = time(seconds)
    if zone == "Yard":
        x = periodic_noise(seconds, 55301, 35, 740) * (.38 + .10 * np.cos(TAU * t / seconds))
        x += periodic_noise(seconds, 55302, 1500, 4200) * .025
        # Rare distant structure creak: many weak inharmonic modes, no siren.
        for hz in (213.25, 341.5, 587.75):
            x += .025 * np.sin(TAU * hz * t) * np.maximum(0, np.sin(TAU * t / seconds)) ** 16
    elif zone == "Workshop":
        x = periodic_noise(seconds, 55311, 40, 950) * .13
        for hz, gain in ((60, .22), (120, .035), (241, .016), (903, .006)):
            x += gain * np.sin(TAU * hz * t) * (1 + .06 * np.cos(TAU * t * 2 / seconds))
        for at in (3.4, 11.9):
            place(x, contact(.35, int(at * 100), .2, .3), at, .055)
    else:
        x = periodic_noise(seconds, 55321, 28, 650) * .16
        for hz, gain in ((47, .15), (94, .03), (187, .015)):
            x += gain * np.sin(TAU * hz * t)
        x += periodic_noise(seconds, 55322, 1600, 4700) * .018 * (1 + np.cos(TAU * t * 3 / seconds))
    return x


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replace-owned", action="store_true")
    opt = ap.parse_args()
    dest = ROOT / "Waves"
    dest.mkdir(exist_ok=True)
    old_manifest = ROOT / "manifest.json"
    old = json.loads(old_manifest.read_text()) if old_manifest.exists() else {}
    old_hashes = {x["file"]: x["sha256"] for x in old.get("sounds", [])}
    manifest = []

    def emit(name: str, x: np.ndarray, peak_db: float, group: str, usage: str, loop: bool = False) -> None:
        name = "S_CR055_" + name
        path = dest / (name + ".wav")
        rel = "Waves/" + path.name
        if path.exists():
            assert opt.replace_owned and old.get("owner") == OWNER, f"Refusing overwrite: {path}"
            assert hashlib.sha256(path.read_bytes()).hexdigest() == old_hashes.get(rel), f"Source changed: {path}"
        x = x - np.mean(x, axis=0)
        if not loop:
            fade = np.minimum(1, np.arange(len(x)) / (RATE * .0005)) * np.minimum(1, (len(x) - 1 - np.arange(len(x))) / (RATE * .012))
            x *= fade[:, None] if x.ndim == 2 else fade
        x *= 10 ** (peak_db / 20) / max(1e-9, np.max(np.abs(x)))
        pcm = np.rint(x * 32767).astype("<i2")
        with wave.open(str(path), "wb") as w:
            w.setnchannels(2 if x.ndim == 2 else 1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(pcm.tobytes())
        rms = np.sqrt(np.mean(x * x))
        manifest.append({"name": name, "file": rel, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size,
                         "seconds": len(x) / RATE, "sample_rate": RATE, "channels": 2 if x.ndim == 2 else 1, "format": "PCM signed16 little-endian",
                         "peak_dbfs": round(float(20 * np.log10(np.max(np.abs(x)))), 3), "rms_dbfs": round(float(20 * np.log10(rms)), 3),
                         "endpoint_delta": round(float(np.max(np.abs(x[-1] - x[0]))), 7), "clipped_samples": int(np.sum(np.abs(pcm) >= 32767)),
                         "loop": loop, "sound_class": group, "usage": usage,
                         "source_url": "https://github.com/Leosteeeve/cinder-relay/blob/phase-05-5-ui-audio-inventory/CinderRelay/ArtSource/Audio/Phase055/author_audio.py",
                         "author": "CINDER RELAY project; original deterministic sound design", "license": "Original project source; no new standalone asset license granted",
                         "attribution": "Original CINDER RELAY sound design", "public_repository_redistribution": "Authorized original project source; no external recordings/samples",
                         "modifications": "Filtered noise, inharmonic resonances, timed transient layers, environment reflections, gain and bounded fades"})

    for env in ("Outdoor", "Workshop", "Bunker"):
        for v in range(1, 4):
            emit("Rook" + env + str(v), shot(env, v), -5.5, "Weapons", "Accepted shot: one composite report with mechanical onset and environment-specific tail")
    cues = [
        ("Cycle", .30, [(0, .7), (.075, .5), (.17, .4)], .65, -16, "Weapons", "Once per accepted shot montage cycle marker"),
        ("Case", .34, [(.02, .45), (.13, .22), (.24, .10)], .9, -23, "Weapons", "Once per consumed EjectCase token; cosmetic only"),
        ("Dry", .14, [(0, .8), (.025, .25)], .4, -20, "Weapons", "Existing dry-fire cooldown cue"),
        ("ReloadStart", .24, [(0, .6), (.07, .25)], .2, -19, "Weapons", "Reload accepted onset only; no full reload timeline"),
        ("FeedOut", .35, [(0, .4), (.07, .6), (.18, .25)], .3, -18, "Weapons", "Existing FeedOut animation notify; montage-instance deduplicated"),
        ("FeedIn", .30, [(0, .6), (.055, .4)], .45, -17, "Weapons", "Existing FeedIn animation notify; montage-instance deduplicated"),
        ("ReloadComplete", .28, [(0, .65), (.08, .3)], .5, -20, "Weapons", "Native successful reload transfer only"),
        ("UISelect", .11, [(0, .6)], .05, -26, "UI", "Keyboard focus or pointer hover transition, rate limited"),
        ("UIConfirm", .22, [(0, .55), (.065, .24)], .18, -23, "UI", "Accepted menu action"),
        ("UICancel", .19, [(0, .42)], .08, -25, "UI", "Back/close"),
        ("UIError", .25, [(0, .45), (.11, .32)], .02, -25, "UI", "Unavailable action; never repeated on refresh"),
        ("Collect", .30, [(0, .55), (.10, .25)], .28, -21, "UI", "Actual item or ammo collection"),
        ("Confirm", .38, [(0, .5), (.09, .3), (.18, .16)], .32, -23, "UI", "Upgrade, objective, native saved/restored checkpoint feedback"),
        ("Hit", .15, [(0, .7)], .05, -21, "UI", "Confirmed enemy hit"),
        ("Kill", .26, [(0, .55), (.07, .3)], .05, -20, "UI", "Confirmed enemy defeat"),
        ("Impact", .25, [(0, .7), (.038, .17)], .65, -15, "Weapons", "Spatial solid-surface shot impact"),
    ]
    for index, (name, duration, beats, metal, peak, group, usage) in enumerate(cues):
        emit(name, clicks(duration, 55400 + index * 37, beats, metal), peak, group, usage)
    t = time(.32)
    emit("Damage", noise(len(t), 55510, 35, 1000) * envelope(t, .07), -16, "Foley", "Player damage; no synthesized voice")
    for surface in ("Concrete", "Metal", "Gravel", "Industrial"):
        for v in range(1, 4):
            emit("Foot" + surface + str(v), foot(surface, v), -20 if surface != "Metal" else -21, "Foley", "Grounded displacement step; actual surface with explicit zone fallback")
    t = time(.3)
    emit("SlideStart", noise(len(t), 55600, 90, 6700) * envelope(t, .055, .006), -21, "Foley", "Accepted slide start")
    t = time(1)
    emit("SlideLoop", periodic_noise(1, 55601, 160, 4300) * (.75 + .08 * np.cos(TAU * t * 3)), -26, "Foley", "Owned loop; stop/fade on slide end/pause/death/travel", True)
    t = time(.24)
    emit("SlideEnd", noise(len(t), 55602, 70, 3200) * envelope(t, .06, .006), -24, "Foley", "Slide stop, except silent travel/endplay cleanup")
    for zone in ("Yard", "Workshop", "Bunker"):
        emit("Amb" + zone, ambience(zone), -22 if zone == "Yard" else -26, "Ambience", "Quiet streamed zone loop with16s period; no music or voice", True)
    result = {"owner": OWNER, "date": "2026-11-01", "generator": "author_audio.py", "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "original_samples_only": True, "external_samples": [], "recorded_voice": False, "music": False,
              "qa_boundary": "Numerical PCM/loop checks are not human auditory acceptance. Requires actual audible engine capture and stereo-headphone review.", "sounds": manifest}
    old_manifest.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"sounds": len(manifest), "bytes": sum(s["bytes"] for s in manifest), "clipped_samples": sum(s["clipped_samples"] for s in manifest), "manifest": str(old_manifest)}))


if __name__ == "__main__":
    main()
