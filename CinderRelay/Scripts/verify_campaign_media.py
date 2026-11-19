"""Compare the decoded release movies with a packaged Opening or Handoff recording.

Use run_campaign_acceptance.ps1 first. The --capture directory contains frames/*.png
and Soundtrack.wav from that same run. Without --capture, check just the mastered film.
"""

import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image


SPECS = {
    "CR_Opening3D": (432, [1, 121, 217, 313], [2.1, 8.38, 12.08]),
    "CR_Recap3D": (576, [1, 97, 205, 301, 403, 505], [7.29, 11.08, 15.25]),
}
WIDTH, HEIGHT = 96, 54


def decode(ffmpeg, source, args):
    return subprocess.run([ffmpeg, "-nostdin", "-v", "error", "-i", source, *args, "-f", "rawvideo", "-"],
                          stdout=subprocess.PIPE, check=True).stdout


def audio(ffmpeg, path):
    raw = subprocess.run([ffmpeg, "-nostdin", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", "4000",
                          "-f", "f32le", "-"], stdout=subprocess.PIPE, check=True).stdout
    return np.frombuffer(raw, dtype="<f4").astype(float)


def center(array):
    # Ignore captions, the Skip control and the letterbox edges.
    return array[..., 9:43, 8:88].reshape(array.shape[:-2] + (-1,)).astype(np.float32)


def normalized(values):
    x = values - values.mean(axis=-1, keepdims=True)
    return x / np.maximum(.001, np.linalg.norm(x, axis=-1, keepdims=True))


def find_sound(recording, excerpt):
    """Normalized time-domain correlation via FFT, with allowance for variable recording start."""
    width = len(excerpt)
    if len(recording) < width:
        return 0, 0
    excerpt = excerpt - excerpt.mean()
    n = 1 << (len(recording) + width - 2).bit_length()
    corr = np.fft.irfft(np.fft.rfft(recording, n) * np.fft.rfft(excerpt[::-1], n), n)
    energy = np.r_[0, np.cumsum(recording ** 2)]
    norm = np.sqrt(np.maximum(1e-12, energy[width:] - energy[:-width])) * np.linalg.norm(excerpt)
    coeff = corr[width - 1:len(recording)] / np.maximum(1e-9, norm)
    where = int(np.argmax(coeff))
    return round(where / 4000, 3), round(float(coeff[where]), 3)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ffmpeg", required=True)
    parser.add_argument("--movie", type=Path, required=True)
    parser.add_argument("--capture", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    frames, cuts, cue_seconds = SPECS[args.movie.stem]
    video = np.frombuffer(decode(args.ffmpeg, args.movie, ["-an", "-vf", f"scale={WIDTH}:{HEIGHT}",
                                                           "-pix_fmt", "gray"]), dtype=np.uint8)
    pictures = center(video.reshape(-1, HEIGHT, WIDTH))
    soundtrack = audio(args.ffmpeg, args.movie)
    if len(pictures) != frames or abs(len(soundtrack) / 4000 - frames / 24) > .06:
        raise ValueError("Decoded picture or audio length disagrees with the Blender timeline")
    report = {"movie": args.movie.name, "decoded_frames": frames, "seconds": frames / 24,
              "audio_seconds": len(soundtrack) / 4000, "shot_frame_changes": []}
    passed = True
    for first, next_cut in zip(cuts, cuts[1:] + [frames + 1]):
        shot = pictures[first - 1:next_cut - 1]
        changed = int(np.count_nonzero(np.abs(np.diff(shot, axis=0)).mean(axis=1) > .025))
        report["shot_frame_changes"].append(changed)
        passed &= changed > .30 * (len(shot) - 1)
    if args.capture:
        source = normalized(pictures)
        matches = []
        for file in sorted((args.capture / "frames").glob("*.png")):
            stamp = int(file.stem) / 1000
            if stamp < .12 or stamp >= frames / 24 - .10:
                continue
            with Image.open(file) as shot:
                pixel = np.asarray(shot.convert("L").resize((WIDTH, HEIGHT), Image.Resampling.BOX))
            # RHI display and screenshot requests each introduce some frame latency.
            lo = max(0, int(24 * (stamp - 1.25)))
            hi = min(frames, int(24 * (stamp + 1.25)) + 1)
            if lo >= hi:
                continue
            score = source[lo:hi] @ normalized(center(pixel))
            index = int(score.argmax())
            matches.append([stamp, round((lo + index) / 24, 2), round(float(score[index]), 3)])
        report["screenshot_matches_native_s_master_s_correlation"] = matches
        passed &= len([m for m in matches if m[2] > .78]) >= (1 if args.capture.name == "Select" else 4)
        if args.capture.name != "Select":
            recording = audio(args.ffmpeg, args.capture / "Soundtrack.wav")
            sounds = []
            for start in cue_seconds:
                first = int(4000 * start)
                at, coeff = find_sound(recording, soundtrack[first:first + 2048])
                sounds.append([start, at, coeff])
            report["sound_matches_master_s_native_s_correlation"] = sounds
            passed &= sum(m[2] > .33 for m in sounds) >= 2
    report["passed"] = bool(passed)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit(f"Media check failed. See {args.report}")
    print(f"{args.movie.name} verified. {args.report}")


if __name__ == "__main__":
    main()
