"""Export native campaign frames and the same session's Soundtrack.wav to an MP4.

python export_campaign_film.py --capture Saved/Campaign/Opening --ffmpeg <exe> --output Opening.mp4
"""

import argparse
from array import array
from bisect import bisect_right
from fractions import Fraction
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile


NATIVE_DURATIONS = {"Opening": 18, "Handoff": 24, "Select": 24}
AUDIO_RATE = 16000
PIXELS = 96 * 48
PROJECT = Path(__file__).resolve().parents[1]


def collect_frames(directory):
    frames = sorted((int(p.stem), p) for p in directory.glob("*.png") if p.stem.isascii() and p.stem.isdigit())
    if len(frames) < 2:
        raise ValueError(f"Need at least two numeric millisecond PNGs in {directory}")
    if len({t for t, _ in frames}) != len(frames):
        raise ValueError("Two PNG filenames describe the same millisecond")
    return frames


def timeline(stamps, audio_start, audio_length, fps, natural):
    """Use only captured picture/sound overlap, on the native film clock (seconds)."""
    start = max(Fraction(stamps[0], 1000), audio_start)
    stop = min(Fraction(stamps[-1], 1000) + Fraction(1, fps), audio_start + audio_length)
    if natural is not None:
        stop = min(stop, natural)
    count = math.floor((stop - start) * fps)
    if count < 2:
        raise ValueError("The native recording and captured pictures have insufficient overlap")
    indices = [bisect_right(stamps, (start + Fraction(i, fps)) * 1000) - 1 for i in range(count)]
    if indices[0] == indices[-1]:
        raise ValueError("The overlapping audio contains only one captured picture")
    return start, indices


def score_for(capture):
    """Original illustrated-film cue sheet, retained for archived capture diagnostics."""
    if capture.name == "Opening":
        shot_time = Fraction("5.6")
        events = [("BusEnergize", .58), ("FeedIn", .76), ("HoistLift", .65), ("InterlockTravel", .74)]
    elif capture.name in ("Handoff", "Select"):
        shot_time = Fraction("5.1")
        events = [("HoistLift", .78), ("FeedIn", .92), ("BusEnergize", .92), ("Confirm", .77)]
    else:
        raise ValueError("Use an archived Opening or Handoff capture folder for the illustrated-film mix")
    cues = []
    for i, (name, rate) in enumerate(events):
        files = list((PROJECT / "ArtSource/Audio").rglob(f"S_CR*_{name}.wav"))
        if len(files) != 1:
            raise ValueError(f"Expected one original source WAV for {name}, found {files}")
        cues.append({"name": name, "source": files[0].relative_to(PROJECT).as_posix(), "pitch": float(rate),
                     "gain": .55, "start_seconds": float(i * shot_time)})
    return shot_time, cues


def full_picture(stamps, shot_time, fps):
    end_ms = int(shot_time * 4 * 1000)
    if stamps[0] != 0 or not 0 <= end_ms - stamps[-1] <= 250:
        raise ValueError(f"Full film needs a frame at zero and one within 250 ms of {end_ms}; saw {stamps[0]}..{stamps[-1]}")
    per_shot = [sum(i*shot_time*1000 <= t < (i+1)*shot_time*1000 for t in stamps) for i in range(4)]
    largest_gap = max(b-a for a,b in zip(stamps, stamps[1:]))
    if min(per_shot) < 3 or largest_gap > shot_time * 1000 / 3:
        raise ValueError(f"Native pictures do not cover every cut: {per_shot}, largest gap {largest_gap} ms")
    indices = [bisect_right(stamps, Fraction(i * 1000, fps)) - 1 for i in range(round(shot_time * 4 * fps))]
    return indices, per_shot, largest_gap


def render_score(ffmpeg, output, shot_time, cues):
    rate = 48000
    samples = int(shot_time * rate)
    args = [ffmpeg, "-hide_banner", "-loglevel", "error", "-n"]
    filters = []
    for i, cue in enumerate(cues):
        args += ["-i", PROJECT / cue["source"]]
        pitched_rate = round(rate * cue["pitch"])
        filters.append(f"[{i}:a]aresample={rate},asetrate={pitched_rate},aresample={rate},"
                       f"aformat=channel_layouts=stereo,volume={cue['gain']},apad=whole_len={samples},"
                       f"atrim=end_sample={samples},asetpts=N/SR/TB[shot{i}]")
    filters.append("[shot0][shot1][shot2][shot3]concat=n=4:v=0:a=1[mix]")
    subprocess.run(args + ["-filter_complex", ";".join(filters), "-map", "[mix]", "-c:a", "pcm_s24le", output],
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)


def decoded(ffmpeg, filename, options):
    return subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-i", filename, *options, "pipe:1"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout


def measure_audio(ffmpeg, filename, shot_time=None):
    pcm = decoded(ffmpeg, filename, ["-map", "0:a:0", "-vn", "-ac", "2", "-ar", str(AUDIO_RATE), "-f", "s16le"])
    samples = array("h")
    samples.frombytes(pcm)
    if sys.byteorder != "little":
        samples.byteswap()
    if not samples:
        raise ValueError(f"Empty audio stream in {filename}")
    peak = max(abs(i) for i in samples) / 32768
    rms = math.sqrt(sum(i * i for i in samples) / len(samples)) / 32768
    if peak < .0002 or rms < .00001:
        raise ValueError(f"No measurable waveform in {filename} (peak {peak:.7f}, RMS {rms:.7f})")
    shot_peaks = []
    if shot_time:
        width = int(shot_time * AUDIO_RATE * 2)
        for i in range(4):
            part = samples[i*width:(i+1)*width]
            value = max((abs(s) for s in part), default=0) / 32768
            if value < .0002:
                raise ValueError(f"No decoded audio cue at cut {i+1} in {filename}")
            shot_peaks.append(round(value, 6))
    return Fraction(len(samples), AUDIO_RATE * 2), peak, rms, shot_peaks


def encode(ffmpeg, frames, indices, wav, audio_offset, fps, output):
    # image2pipe fixes frame time exactly at 1/fps. Selecting the most recent PNG
    # on the original millisecond clock avoids concat's per-image time-base rounding.
    length = len(indices) / fps
    args = [ffmpeg, "-hide_banner", "-loglevel", "error", "-n", "-f", "image2pipe",
            "-framerate", str(fps), "-c:v", "png", "-i", "pipe:0",
            "-ss", f"{float(audio_offset):.9f}", "-i", wav, "-map", "0:v:0", "-map", "1:a:0",
            "-t", f"{length:.9f}", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", output]
    with tempfile.TemporaryFile() as errors, subprocess.Popen(args, stdin=subprocess.PIPE, stderr=errors) as proc:
        try:
            previous = None
            for index in indices:
                if previous != index:
                    data = frames[index][1].read_bytes()
                    previous = index
                proc.stdin.write(data)
            proc.stdin.close()
        except BrokenPipeError:
            pass
        if proc.wait():
            errors.seek(0)
            raise ValueError("FFmpeg encode failed: " + errors.read().decode(errors="replace").strip())


def verify_motion(ffmpeg, output, start, fps, count, natural, require_all=False):
    # Exclude the header, skip control and subtitle area. Count movement inside
    # shots separately from scene cuts and the intentional dips to black.
    raw = decoded(ffmpeg, output, ["-map", "0:v:0", "-an", "-vf",
                  "crop=iw*0.9:ih*0.52:iw*0.05:ih*0.14,scale=96:48,format=gray",
                  "-fps_mode", "passthrough", "-f", "rawvideo"])
    if len(raw) != count * PIXELS:
        raise ValueError(f"Decoded {len(raw) // PIXELS} video frames, expected {count}")
    frames = memoryview(raw)
    stride = max(1, fps // 5)
    measured = 0
    per_shot = [0, 0, 0, 0]
    for i in range(stride, count, stride):
        if natural:
            shot = float(natural) / 4
            phase = (float(start) + i / fps) % shot
            if not .35 + stride / fps <= phase <= shot - .35:
                continue
        prev = frames[(i - stride)*PIXELS:(i - stride + 1)*PIXELS]
        curr = frames[i*PIXELS:(i + 1)*PIXELS]
        changed = sum(abs(a - b) >= 6 for a, b in zip(prev, curr)) / PIXELS
        if .003 <= changed <= .65:
            measured += 1
            if natural:
                per_shot[min(3, int((float(start) + i / fps) / shot))] += 1
    if measured < 2:
        raise ValueError("Insufficient within-shot motion in the decoded picture area")
    if require_all and min(per_shot) < 2:
        raise ValueError(f"Missing sustained decoded picture motion inside one of four cuts: {per_shot}")
    return measured, per_shot


def export(args):
    capture = args.capture.resolve()
    frames = collect_frames(capture / "frames")
    wav = capture / "Soundtrack.wav"
    if not args.authored_audio and not wav.is_file():
        raise ValueError(f"Could not find {wav}")
    output = args.output.resolve()
    if output.suffix.lower() != ".mp4":
        raise ValueError("The output must have the .mp4 extension")
    if output.exists():
        raise ValueError(f"Choose a new output file; already exists: {output}")
    if args.report and (args.report.exists() or args.report.resolve() == output):
        raise ValueError("Choose a separate new report filename")
    duration = args.natural_duration if args.natural_duration is not None else NATIVE_DURATIONS.get(capture.name)
    natural = Fraction(str(duration)) if duration is not None else None
    if natural is not None and natural <= 0:
        raise ValueError("Expected natural duration must be positive")
    audio_start = Fraction(args.audio_start_ms, 1000)
    stamps = [ms for ms, _ in frames]
    details = {}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix=".film-") as scratch:
        draft = Path(scratch) / "encode.mp4"
        shot_time = None
        if args.authored_audio:
            if args.audio_start_ms != 0:
                raise ValueError("The authored cue sheet begins at native film time zero")
            shot_time, cues = score_for(capture)
            if args.natural_duration is not None and natural != 4*shot_time:
                raise ValueError("The supplied duration disagrees with the authored native cuts")
            natural = 4*shot_time
            indices, samples_per_shot, gap = full_picture(stamps, shot_time, args.fps)
            start = Fraction(0)
            wav = Path(scratch) / "AuthoredScore.wav"
            render_score(args.ffmpeg, wav, shot_time, cues)
            details = {"audio_mode": "offline authored cue mix from original project WAV files",
                       "audio_cues": cues, "native_pictures_per_shot": samples_per_shot, "largest_native_gap_ms": gap,
                       "final_native_picture_hold_ms": int(natural*1000) - stamps[-1]}
        else:
            details["audio_mode"] = "native packaged mixer recording"
        audio_length, source_peak, _, _ = measure_audio(args.ffmpeg, wav, shot_time)
        if not args.authored_audio:
            start, indices = timeline(stamps, audio_start, audio_length, args.fps, natural)
        length = Fraction(len(indices), args.fps)
        encode(args.ffmpeg, frames, indices, wav, start - audio_start, args.fps, draft)
        motion, shot_motion = verify_motion(args.ffmpeg, draft, start, args.fps, len(indices), natural, args.authored_audio)
        mixed_length, peak, rms, shot_peaks = measure_audio(args.ffmpeg, draft, shot_time)
        if args.authored_audio:
            details["decoded_motion_intervals_per_shot"] = shot_motion
            details["decoded_audio_peak_per_shot"] = shot_peaks
        if abs(mixed_length - length) > Fraction(1, 10):
            raise ValueError("Decoded MP4 audio and timed video differ by more than 0.1 seconds")
        if output.exists():
            raise ValueError(f"Output already exists: {output}")
        draft.rename(output)
    result = {"output": str(output), **details, "source_pngs": len(frames), "used_pngs": len(set(indices)),
              "first_capture_ms": stamps[0], "last_capture_ms": stamps[-1], "fps": args.fps,
              "frames": len(indices), "source_audio_seconds": round(float(audio_length), 4),
              "audio_start_on_film_ms": args.audio_start_ms, "export_start_on_film_s": round(float(start), 4),
              "export_end_on_film_s": round(float(start+length), 4), "export_duration_s": round(float(length), 4),
              "natural_film_duration_s": float(natural) if natural else None,
              "uncaptured_end_s": round(max(0., float(natural-start-length)), 4) if natural else None,
              "motion_intervals_in_picture": motion, "source_audio_peak": round(source_peak, 6),
              "decoded_audio_peak": round(peak, 6), "decoded_audio_rms": round(rms, 6)}
    receipt = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("x", encoding="utf-8") as f:
            f.write(receipt + "\n")
    print(receipt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True, help="Folder with frames/ and Soundtrack.wav")
    parser.add_argument("--ffmpeg", required=True, help="Local FFmpeg executable")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fps", type=int, choices=(24, 30), default=30)
    parser.add_argument("--natural-duration", type=float, help="Authored full runtime in seconds (recognized for native capture folders)")
    parser.add_argument("--audio-start-ms", type=int, default=0, help="Film time of first WAV sample (native capture starts with the film)")
    parser.add_argument("--report", type=Path, help="Optional JSON verification receipt")
    parser.add_argument("--authored-audio", action="store_true",
                        help="Recreate the archived illustrated-film mix. Current Blender films contain their own audio.")
    try:
        export(parser.parse_args())
    except subprocess.CalledProcessError as error:
        parser.exit(1, f"FFmpeg decode failed: {error.stderr.decode(errors='replace').strip()}\n")
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")
