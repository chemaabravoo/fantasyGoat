"""Bucle instrumental de órgano épico, sintetizado desde cero con numpy.
Si menor, 63 BPM (pulso de dieciseisavos a 252), 8 compases = 30,48 s.
El bucle es perfecto: las colas de las notas y la reverb se pliegan sobre el
principio (convolución circular), así que no hay corte al repetir.
Saca dos versiones alineadas (misma longitud y compás): suave y fuerte."""
import numpy as np, wave, sys, pathlib
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
SR = 44100
BPM = 63.0; BEAT = 60/BPM; BAR = 4*BEAT; NBARS = 8; STEP = BAR/16
L = int(round(NBARS*BAR*SR)); T = L/SR
rng = np.random.default_rng(11)
f_of = lambda n: 440.0*2**((n-69)/12)

# nombre, raíz (midi, octava 1-2), tercera (3 menor / 4 mayor)
PROG = [('Bm',35,3),('G',31,4),('D',38,4),('A',33,4),('Bm',35,3),('G',31,4),('Em',40,3),('F#',30,4)]

def env(n, a, r, curve=1.5):
    e = np.ones(n); na = min(n, int(a*SR)); nr = min(n, int(r*SR))
    if na > 0: e[:na] = np.linspace(0,1,na)**curve
    if nr > 0: e[-nr:] *= np.linspace(1,0,nr)**curve
    return e

def additive(freq, n, harm, detune=0.0, rand_phase=True):
    t = np.arange(n)/SR; out = np.zeros(n)
    for k, a in enumerate(harm, 1):
        f = freq*k*(1+detune)
        if f > SR*0.45: break
        ph = rng.uniform(0, 2*np.pi) if rand_phase else 0.0
        out += a*np.sin(2*np.pi*f*t + ph)
    return out

def saw_harm(freq, fc=4500):
    kmax = max(1, int(min(fc, SR*0.45)/freq)); return [1/k for k in range(1, kmax+1)]

def lowpass(x, fc, order=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR)
    return np.fft.irfft(X/np.sqrt(1+(f/fc)**(2*order)), n=len(x))
def highpass(x, fc, order=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR)
    return np.fft.irfft(X*(1-1/np.sqrt(1+(f/fc)**(2*order))), n=len(x))

def new(): return np.zeros((2, 2*L))
def place(buf, start, sig, pan=0.5):
    n = min(len(sig), buf.shape[1]-start)
    buf[0, start:start+n] += sig[:n]*np.sqrt(1-pan); buf[1, start:start+n] += sig[:n]*np.sqrt(pan)
def fold(buf): return buf[:, :L] + buf[:, L:2*L]
def at(bar, step=0.0): return int(round((bar*BAR + step*STEP)*SR))

# ---- 1. órgano en pulso --------------------------------------
ORGAN_H = [1, 0.6, 0.45, 0.28, 0.16, 0.09, 0.05]
ARP = [0,7,12,7, 0,7,12,7, 0,7,12,7, 0,7,12,'3']
organ = new()
for b, (_, root, third) in enumerate(PROG):
    for s in range(16):
        iv = ARP[s]; iv = third+12 if iv == '3' else iv
        f = f_of(root+36+iv); n = int(STEP*0.95*SR)
        sig = additive(f, n, ORGAN_H, rand_phase=False) + 0.7*additive(f, n, ORGAN_H, detune=0.0035)
        sig *= env(n, 0.006, 0.07)
        acc = 1.0 if s % 4 == 0 else (0.72 if s % 2 else 0.85)
        place(organ, at(b, s), sig*acc, pan=0.5+0.18*np.sin(2*np.pi*(s+0.5)/16))
organ = np.stack([lowpass(c, 2600) for c in organ])

# ---- 2. cuerdas (pad de sierras desafinadas) --------------------------------
pad = new()
for b, (_, root, third) in enumerate(PROG):
    n = int((BAR+0.9)*SR); e = env(n, 0.55, 0.85)*np.linspace(0.75, 1.0, n)
    for iv, g in [(24,1.0),(24+third,0.8),(31,0.8),(36,0.55),(36+third,0.45)]:
        f = f_of(root+iv)
        for c, dets in enumerate([(-0.006,-0.002,0.003),(-0.003,0.002,0.006)]):
            sig = sum(additive(f, n, saw_harm(f, 3800), detune=d) for d in dets)/3
            buf = np.zeros(n); buf += sig*e*g
            pad[c, at(b):at(b)+n] += buf
pad = np.stack([highpass(lowpass(c, 2100), 140) for c in pad])

# ---- 3. sub / drone ---------------------------------------------------------
sub = new()
for b, (_, root, _) in enumerate(PROG):
    n = int((BAR+0.6)*SR); t = np.arange(n)/SR; f = f_of(root)
    sig = np.sin(2*np.pi*f*t) + 0.35*np.sin(2*np.pi*2*f*t) + 0.25*lowpass(additive(2*f, n, saw_harm(2*f, 900)), 320)
    sig *= env(n, 0.35, 0.6)
    place(sub, at(b), sig, 0.5)

# ---- 4. el tic del reloj (cada corchea) -------------------------------------
tick = new()
for e in range(NBARS*8):
    n = int(0.05*SR); t = np.arange(n)/SR
    click = highpass(rng.normal(size=n)*np.exp(-t/0.0022), 2800)*0.6
    ping = np.sin(2*np.pi*3150*t)*np.exp(-t/0.011) + 0.5*np.sin(2*np.pi*5200*t)*np.exp(-t/0.006)
    sig = (click+ping)*np.minimum(1, t/0.0008)
    acc = 1.0 if e % 8 == 0 else (0.8 if e % 2 == 0 else 0.6)
    place(tick, at(e//8, (e%8)*2), sig*acc, 0.42 if e % 2 else 0.58)

# ---- 5. el hinchazón grave (bras) al principio de cada frase ----------------
swell = new()
for b in (0, 4):
    root = PROG[b][1]; n = int(BAR*1.15*SR); t = np.arange(n)/SR
    sig = np.zeros(n)
    for iv, d in [(0,-0.004),(0,0.004),(7,0.0),(12,-0.003)]:
        f = f_of(root+iv); sig += additive(f, n, saw_harm(f, 2000), detune=d)*(0.6 if iv else 1.0)
    e = np.minimum(1, (t/1.5)**2)*np.exp(-np.maximum(0, t-1.5)/1.4)
    sig = np.tanh(lowpass(sig*e, 650)*1.6)
    place(swell, at(b), sig, 0.5)

# ---- 6. piano de fieltro: melodía en la segunda mitad -----------------------
def piano(freq, n=int(3.2*SR)):
    t = np.arange(n)/SR; out = np.zeros(n)
    for k, a in enumerate([1,0.55,0.32,0.2,0.11,0.07,0.04], 1):
        fk = freq*k*np.sqrt(1+0.0004*k*k)
        out += a*np.sin(2*np.pi*fk*t + rng.uniform(0, 6.28))*np.exp(-t*(0.75+0.45*k))
    thump = lowpass(rng.normal(size=n)*np.exp(-t/0.004), 1800)*0.35
    return (out+thump)*np.minimum(1, t/0.003)
MEL = [(4,0,78),(4,2,74),(4,3,76), (5,0,74),(5,3,71), (6,0,76),(6,2,79), (7,0,78),(7,2,73)]
pno = new()
for bar, beat, n in MEL:
    place(pno, at(bar, beat*4), piano(f_of(n))*(1.0 if beat == 0 else 0.8), 0.5+0.12*np.sign(n-75))
pno = np.stack([lowpass(c, 5000) for c in pno])

# ---- reverb circular: la cola se pliega sobre el principio -----------------
def ir(seconds=3.2, tau=1.0):
    n = int(seconds*SR); t = np.arange(n)/SR; out = np.zeros((2, n))
    for c in range(2):
        nz = lowpass(rng.normal(size=n), 5500); out[c] = nz*np.exp(-t/tau)*np.minimum(1, t/0.02)
    pre = int(0.028*SR); out = np.concatenate([np.zeros((2, pre)), out], 1)
    return out/np.sqrt((out**2).sum(1)).max()
IR = ir()
def verb(x):
    return np.stack([np.fft.irfft(np.fft.rfft(x[c], n=L)*np.fft.rfft(IR[c], n=L), n=L) for c in range(2)])

layers = {k: fold(v) for k, v in dict(organ=organ, pad=pad, sub=sub, tick=tick, swell=swell, pno=pno).items()}
MIX = {
  'suave':  dict(organ=(0.55,0.35), pad=(0.30,0.30), sub=(0.45,0.0), tick=(0.75,0.25), swell=(0.0,0.0), pno=(0.0,0.0)),
  'fuerte': dict(organ=(0.62,0.35), pad=(0.58,0.28), sub=(0.55,0.0), tick=(0.85,0.25), swell=(0.55,0.45), pno=(0.62,0.5)),
}
def write(path, y):
    y = np.clip(y, -1, 1); data = (y.T*32767).astype('<i2').tobytes()
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data)

for name, g in MIX.items():
    dry = sum(layers[k]*g[k][0] for k in layers)
    send = sum(layers[k]*g[k][0]*g[k][1] for k in layers)
    y = dry + verb(send)*1.1
    y = np.stack([highpass(lowpass(c, 16000), 28) for c in y])
    y /= np.abs(y).max()
    y = np.tanh(y*1.25)/np.tanh(1.25)          # pegamento suave, sin aplastar
    y *= 0.891/np.abs(y).max()                 # pico a -1 dBFS
    rms = 20*np.log10(np.sqrt((y**2).mean()))
    write(OUT/f"nolan-{name}.wav", y)
    print("  capas (pico dBFS en la mezcla):", {k: round(float(20*np.log10(np.abs(layers[k]*g[k][0]).max()+1e-9)),1) for k in layers})
    print(f"{name}: {T:.2f} s, pico {np.abs(y).max():.2f}, RMS {rms:.1f} dBFS, salto en el bucle L/R: {abs(y[0,0]-y[0,-1]):.4f} {abs(y[1,0]-y[1,-1]):.4f}")
print("bucle:", T, "s ;", NBARS, "compases a", BPM, "BPM")
