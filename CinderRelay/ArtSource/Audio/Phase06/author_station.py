"""Render project-original station machinery and receiver cues from oscillators and filtered noise."""
import array
import hashlib
import json
import math
import random
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RATE = 48000
TAU = math.tau


def strike(t, at, pitch):
    age = t - at
    if age < 0 or age > .48:
        return 0.
    return math.exp(-age*19) * (math.sin(TAU*pitch*age) + .32*math.sin(TAU*pitch*2.7*age))


def draw(name, duration, seed):
    rng = random.Random(seed)
    samples = []
    filtered = 0.
    phase = 0.
    for index in range(round(duration * RATE)):
        t = index / RATE
        u = t / duration
        noise = rng.uniform(-1, 1)
        filtered += .09*(noise-filtered)
        if name == 'HoistLift':
            phase += TAU*(48 + 37*math.sin(math.pi*u)**.55)/RATE
            ratchet = max(0., math.sin(phase*.18))**13
            value = .28*math.sin(phase) + .12*math.sin(phase*3) + (.14+ratchet)*filtered
            value += .34*(strike(t, .08, 161) + strike(t, duration-.22, 109))
        elif name == 'BusEnergize':
            value = .25*math.sin(TAU*60*t) + .14*math.sin(TAU*121*t) + .16*filtered
            value += .48*sum(strike(t, at, hz) for at, hz in ((.05, 313), (.21, 431), (.47, 542)))
        elif name == 'InterlockTravel':
            phase += TAU*(106 - 28*u)/RATE
            value = .19*math.sin(phase) + filtered*(.8 + .4*math.cos(phase*.2))
            value += .48*(strike(t, .08, 115) + strike(t, 1.07, 92) + strike(t, 1.19, 140))
        elif name == 'RelayWake':
            phase += TAU*(34 + 40*min(1., t*.55))/RATE
            value = (.12 + .21*min(1., t))*math.sin(phase) + .10*math.sin(phase*3)
            value += .1*filtered + .42*sum(strike(t, at, hz) for at, hz in ((.09, 145), (.62, 192), (1.24, 245)))
        else:
            # Broken carrier pulses gradually hold a stable interval.
            phase += TAU*(392 + 28*math.sin(2.9*t)*max(0., 1.-u*1.4))/RATE
            gate = min(1., max(0., (math.cos(9*t + math.sin(2.5*t)) + 1.55*u)*4))
            value = .12*filtered + gate*(.27*math.sin(phase) + .11*math.sin(phase*1.5))
        edge = min(1., t/.035, (duration-t)/(.32 if duration < 3 else .8))
        samples.append(value * max(0., edge))
    gain = .55 / max(abs(v) for v in samples)
    pcm = array.array('h', (round(v*gain*32767) for v in samples))
    if sys.byteorder != 'little':
        pcm.byteswap()
    path = ROOT / ('S_CR06_' + name + '.wav')
    with wave.open(str(path), 'wb') as output:
        output.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        output.writeframes(pcm.tobytes())
    return dict(event=name, file=path.name, seconds=duration, sha256=hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    cues = [('HoistLift', 2.3), ('BusEnergize', 1.35), ('InterlockTravel', 1.6),
            ('RelayWake', 4.), ('CarrierLock', 8.)]
    sounds = [draw(name, duration, 619 + i) for i, (name, duration) in enumerate(cues)]
    (ROOT / 'station-sounds.json').write_text(json.dumps(sounds, indent=2) + '\n', encoding='utf-8')
