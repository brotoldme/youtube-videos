import json, subprocess, numpy as np, wave, sys
from scipy.io import wavfile
from scipy.signal import butter, lfilter
from scipy.ndimage import uniform_filter1d
SR = 44100
SENT = json.load(open('/home/claude/w/v8/voix_sent.json'))
ST = {i + 1: x['start'] for i, x in enumerate(SENT)}
F0 = ST[35] - 2.02
TOT = F0 + 9.6
N = int(TOT * SR) + SR
sr, v = wavfile.read('/home/claude/w/v8/voix.wav'); assert sr == SR
v = v.astype(float) / 32768
# gain voix -> -21.3 LUFS integre
out = subprocess.run(['ffmpeg', '-hide_banner', '-i', '/home/claude/w/v8/voix.wav', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = float([l for l in out.splitlines() if l.strip().startswith('I:')][-1].split()[1])
g = 10 ** ((-21.3 - I) / 20); print('voix LUFS', I, 'gain dB', round(20 * np.log10(g), 2))
vo = np.zeros(N); vo[:len(v)] = v * g
# fond sonore : cordes douces + pulsation grave, do majeur ~88 bpm
def mid(m): return 440 * 2 ** ((m - 69) / 12)
def lp(x, fc, o=2):
    b, a = butter(o, fc / (SR / 2)); return lfilter(b, a, x)
def strings(notes, d):
    n = int(SR * d); t = np.arange(n) / SR; x = np.zeros(n)
    for m in notes:
        f = mid(m)
        for det in (-0.006, -0.002, 0.002, 0.006): x += (2 * ((f * (1 + det) * t + det * 37) % 1) - 1) * 0.07
    return lp(x, 1300) * np.minimum(t / 0.9, 1) * np.minimum((d - t) / 0.9, 1)
def trio(r, minor): return [r, r + 7, r + 12 + (3 if minor else 4)]
bed = np.zeros(N)
prog = [(48, False), (45, True), (41, False), (43, False)]
t = 0.0; k = 0
while t < TOT + 2:
    r, mn = prog[k % 4]; s = strings(trio(r, mn), 6.5); i = int(t * SR); j = min(i + len(s), N)
    bed[i:j] += s[:j - i]; t += 5.5; k += 1
beat = 60 / 88; tt = np.arange(int(0.5 * SR)) / SR
thump = np.sin(2 * np.pi * 55 * tt) * np.exp(-tt / 0.09) * 0.25
t = 0.0
while t < TOT:
    i = int(t * SR); j = min(i + len(thump), N); bed[i:j] += thump[:j - i] * (1.0 if int(t / beat) % 4 == 0 else 0.6); t += beat
bed /= np.sqrt(np.mean(bed ** 2))
env = uniform_filter1d(np.abs(vo), int(0.12 * SR)); act = (env > 0.012).astype(float)
act = uniform_filter1d(act, int(0.5 * SR)); act = np.clip(act * 1.0, 0, 1)
base = 10 ** (-31.5 / 20) * np.sqrt(np.mean(vo[:int(F0 * SR)][env[:int(F0 * SR)] > 0.012] ** 2))
bedg = base * (1 + (10 ** (3 / 20) - 1) * (1 - act))
fade = np.ones(N); nf = int(3 * SR); e = int(TOT * SR); fade[e - nf:e] = np.linspace(1, 0, nf); fade[e:] = 0
bed = bed * bedg * fade
sr2, st = wavfile.read('/home/claude/w/snd/B_laiton_lourd.wav'); st = st.astype(float) / 32768; st = st / np.abs(st).max() * 0.30
fx = np.zeros(N); i = int((F0 + 1.5) * SR); fx[i:i + len(st)] = st
mix = vo + bed + fx
pk = np.abs(mix).max(); print('crête', round(pk, 3))
if pk > 0.95: mix *= 0.95 / pk
mix = mix[:int(TOT * SR)]
wavfile.write('/home/claude/w/v8/mix.wav', SR, (mix * 32767).astype('<i2'))
out = subprocess.run(['ffmpeg', '-hide_banner', '-i', '/home/claude/w/v8/mix.wav', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
print([l.strip() for l in out.splitlines() if l.strip().startswith(('I:', 'Peak:'))][-2:])
print('bed vs voix dB', round(20 * np.log10(np.sqrt(np.mean(bed[:int(F0 * SR)][act[:int(F0 * SR)] > 0.99] ** 2)) / np.sqrt(np.mean(vo[:int(F0 * SR)][act[:int(F0 * SR)] > 0.99] ** 2))), 1))
