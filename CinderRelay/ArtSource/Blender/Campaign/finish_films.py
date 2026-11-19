"""Mix and master the two Blender edits. Requires NumPy and FFmpeg with libass.

python finish_films.py opening --frames /path/to/numbered-jpegs --ffmpeg /path/to/ffmpeg --work /path/to/temp
"""

import argparse
import math
from pathlib import Path
import shutil
import subprocess
import wave

import numpy as np


PROJECT = Path(__file__).resolve().parents[3]
SOUNDS = PROJECT / "ArtSource/Audio"
FONTS = PROJECT / "ArtSource/Interface/Phase055/Fonts"
MOVIES = PROJECT / "Content/Movies"
RATE = 48000
FPS = 24
LENGTH = {"opening": 18, "recap": 24}
FILENAMES = {"opening": "CR_Opening3D", "recap": "CR_Recap3D"}


class Mix:
    def __init__(self, seconds):
        self.stereo = np.zeros((RATE * seconds, 2), dtype=np.float32)

    def put(self, data, start, gain, pan=0):
        offset = round(start * RATE)
        size = min(len(data), len(self.stereo) - offset)
        angle = (1 + pan) * math.pi / 4
        channels = np.array([math.cos(angle), math.sin(angle)])
        self.stereo[offset:offset + size] += data[:size, None] * channels * gain

    def sound(self, name, start, gain, pan=0, speed=1, length=None):
        files = list(SOUNDS.rglob(f"*_{name}.wav"))
        if len(files) != 1:
            raise ValueError(f"Expected one original sound named {name}, found {files}")
        with wave.open(str(files[0])) as source:
            assert (source.getnchannels(), source.getsampwidth(), source.getframerate()) == (1, 2, RATE)
            data = np.frombuffer(source.readframes(source.getnframes()), dtype="<i2") / 32768
        if speed != 1:
            positions = np.arange(0, len(data) - 1, speed)
            data = np.interp(positions, np.arange(len(data)), data)
        if length and len(data) > round(length * RATE):
            data = data[:round(length * RATE)].copy()
            tail = min(round(RATE * .1), len(data))
            data[-tail:] *= np.linspace(1, 0, tail)
        self.put(data, start, gain, pan)

    def bed(self, name, start, stop, gain, pan=0):
        file = next(SOUNDS.rglob(f"*_{name}.wav"))
        with wave.open(str(file)) as source:
            data = np.frombuffer(source.readframes(source.getnframes()), dtype="<i2") / 32768
        count = round((stop - start) * RATE)
        fade = min(RATE, count // 3)
        for side, offset in ((-.85, 0), (.85, RATE * 7)):
            loop = np.take(data, np.arange(count) + offset, mode="wrap")
            loop[:fade] *= np.linspace(0, 1, fade)
            loop[-fade:] *= np.linspace(1, 0, fade)
            self.put(loop, start, gain, np.clip(side + pan, -1, 1))

    def resonance(self, start, length, hz, gain, pan, decay, wobble=0):
        t = np.arange(round(length * RATE)) / RATE
        phase = 2 * np.pi * hz * t + wobble * np.sin(2 * np.pi * 4.3 * t)
        # The two overtones keep the receiver audible on small speakers.
        signal = .72 * np.sin(phase) + .2 * np.sin(2 * phase + .2) + .08 * np.sin(3 * phase)
        envelope = (1 - np.exp(-t * 125)) * np.exp(-t * decay)
        envelope[-960:] *= np.linspace(1, 0, 960)
        self.put(signal * envelope, start, gain, pan)

    def write(self, file):
        fade = int(RATE * .10)
        self.stereo[:fade] *= np.linspace(0, 1, fade)[:, None]
        self.stereo[-fade:] *= np.linspace(1, 0, fade)[:, None]
        rms = np.sqrt(np.mean(self.stereo ** 2))
        self.stereo *= min(.053 / max(1e-8, rms), .87 / max(1e-8, np.abs(self.stereo).max()))
        with wave.open(str(file), "wb") as dest:
            dest.setparams((2, 2, RATE, 0, "NONE", "not compressed"))
            dest.writeframes(np.round(self.stereo * 32767).astype("<i2").tobytes())


def opening_sound():
    mix = Mix(18)
    mix.bed("AmbYard", 0, 18, 1.35)
    for index, beat in enumerate((.55, 1.32, 2.09, 2.86, 3.63, 4.40, 5.17, 5.95, 6.74, 7.54, 8.38)):
        surface = "Gravel" if beat < 6 else "Metal"
        mix.sound(f"Foot{surface}{index % 3 + 1}", beat, .85 + .12 * index, -.40 + .06 * index,
                  speed=.87 + .04 * (index % 3))
    mix.resonance(3.78, .95, 280, .039, -.64, 3.4)
    mix.sound("SlideLoop", 10.82, 2.0, .17, speed=.76, length=.57)
    mix.sound("Secure", 12.08, 1.9, .17, speed=1.12)
    mix.resonance(12.11, .8, 197, .043, .20, 6.0)
    mix.bed("AmbWorkshop", 13.05, 18, .72, .1)
    return mix


def recap_sound():
    mix = Mix(24)
    mix.bed("AmbBunker", 0, 21.6, 1.2)
    mix.sound("FootIndustrial2", 2.52, 1.1, -.16, speed=.85)
    mix.sound("SlideLoop", 5.52, 1.3, .09, speed=.78, length=.55)
    mix.sound("FeedIn", 6.89, 1.45, .11, speed=.78)
    mix.sound("Seat", 7.29, 3.1, .12)
    mix.resonance(7.31, .85, 135, .09, .10, 5.1)
    mix.sound("InterlockTravel", 9.56, .48, .19, length=1.24)
    mix.sound("Secure", 10.79, 2.8, .19, speed=.78)
    mix.sound("BusEnergize", 11.08, .57, .02)
    mix.sound("RelayWake", 11.31, .22, -.18, length=1.65)
    mix.resonance(13.08, .85, 636, .18, .25, 4.9, .16)
    mix.resonance(15.25, 1.40, 744, .23, -.12, 3.4, .48)
    mix.resonance(15.56, .78, 702, .065, .23, 5.2, .7)
    mix.sound("FootMetal3", 18.18, .89, -.32, speed=.81)
    mix.bed("AmbYard", 20.45, 24, 1.30)
    mix.resonance(21.35, 2.15, 173, .06, .41, 1.9)
    return mix


def on_screen_text(film):
    # PlayRes is a design coordinate system. libass scales to the actual print resolution.
    heading = """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
ScaledBorderAndShadow: yes
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Kicker,Barlow Condensed SemiBold,23,&H00A5CAEC,&H00FFFFFF,&HA0151511,&H900F1110,0,0,0,0,100,100,3,0,1,1,1,7,55,55,42,1
Style: Caption,Barlow Medium,32,&H00FAF5EA,&H00FFFFFF,&H50151310,&H70131311,0,0,0,0,100,100,0,0,1,2.1,1.1,2,60,60,39,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    if film == "opening":
        events = [
            ("0:00:00.60", "0:00:04.74", "Kicker", "2118   /   THE RAIL YARD"),
            ("0:00:00.80", "0:00:04.85", "Caption", "Decades ago, the Quieting brought the world's infrastructure to a halt."),
            ("0:00:05.30", "0:00:08.70", "Kicker", "ELIAS VENN   /   MECHANIC"),
            ("0:00:13.60", "0:00:17.40", "Caption", "The workshop still has a light."),
        ]
    else:
        events = [
            ("0:00:00.50", "0:00:03.77", "Kicker", "RELAY NINE   /   UNDERGROUND STATION"),
            ("0:00:03.98", "0:00:07.06", "Caption", "The workshop had one replacement module."),
            ("0:00:13.22", "0:00:14.65", "Caption", "[Carrier test tone]"),
            ("0:00:15.49", "0:00:17.08", "Caption", "[A broken tone returns]"),
            ("0:00:21.23", "0:00:23.85", "Kicker", "CHAPTER 02   /   ECHO CROSSING"),
        ]
    return heading + "".join(f"Dialogue: 0,{a},{b},{style},,0,0,0,,{{\\fad(170,180)}}{line}\n"
                             for a, b, style, line in events)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("film", choices=LENGTH)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--frames", type=Path)
    parser.add_argument("--ffmpeg", type=Path)
    parser.add_argument("--sound-only", action="store_true")
    args = parser.parse_args()
    name = FILENAMES[args.film]
    work = args.work.resolve() / name
    work.mkdir(parents=True, exist_ok=True)
    wav = work / "mix.wav"
    (opening_sound if args.film == "opening" else recap_sound)().write(wav)
    if args.sound_only:
        return
    if not args.frames or not args.ffmpeg:
        parser.error("--frames and --ffmpeg are required to master picture")
    frames = args.frames.resolve()
    expected = [f"{frame:04d}.jpg" for frame in range(1, LENGTH[args.film] * FPS + 1)]
    if sorted(p.name for p in frames.glob("[0-9][0-9][0-9][0-9].jpg")) != expected:
        raise ValueError(f"Expected the complete sequence {expected[0]} through {expected[-1]} in {frames}")
    font_dir = work / "fonts"
    font_dir.mkdir(exist_ok=True)
    for font in ("Barlow-Medium.ttf", "BarlowCondensed-SemiBold.ttf"):
        shutil.copyfile(FONTS / font, font_dir / font)
    (work / "captions.ass").write_text(on_screen_text(args.film), encoding="utf-8")
    MOVIES.mkdir(parents=True, exist_ok=True)
    movie = MOVIES / (name + ".mp4")
    temporary = work / (name + ".mp4")
    subprocess.run([str(args.ffmpeg.resolve()), "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                    "-framerate", str(FPS), "-start_number", "1", "-i", str(frames / "%04d.jpg"),
                    "-i", str(wav), "-map", "0:v", "-map", "1:a", "-vf",
                    "scale=in_color_matrix=bt601:out_color_matrix=bt709:in_range=full:out_range=tv,"
                    "curves=all='0/0 0.22/0.18 0.5/0.50 0.78/0.81 1/1',vignette=PI/9,"
                    "format=yuv420p,ass=captions.ass:fontsdir=fonts",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                    "-g", "48", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-c:a", "aac", "-b:a", "192k", "-ar", str(RATE), "-movflags", "+faststart",
                    str(temporary)], cwd=work, check=True)
    shutil.copyfile(temporary, movie)
    print(movie)


if __name__ == "__main__":
    main()
