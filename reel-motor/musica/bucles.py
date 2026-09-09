"""Cinco bucles cinematográficos más, cada uno con su paleta de instrumentos,
su tonalidad y su tempo, todos con el mismo cierre perfecto de bucle que
epica-organo*.wav (colas y reverb plegadas sobre el principio, convolución circular).

  python3 bucles.py carpeta [reloj piano sintes cuerdas coro]

reloj   · tic de semicorcheas, pizzicatos, chelos en staccato   · Re m · 72
piano   · piano de fieltro en corcheas, cuerdas lentas    · La m · 60
sintes  · bajo de sinte, arpegio con delay, pad ancho · Mi m · 100
cuerdas · ostinato de violines, chelos, timbales, línea aguda     · Sol m · 66
coro    · voces sintéticas, taikos, campana, drone                  · Do m · 56
lluvia  · luminoso, en mayor: rhodes, campanas de cristal, cuerdas suaves  · Mi♭ M · 76
marcha  · bajo distorsionado, bombo, cuerdas a golpes, tic         · Fa m · 120
marimba · minimalista: marimba en ostinato, pad cálido                    · La M · 84
nocturno· drone, metales lentos, campana suelta, sin pulso  · Fa# m · 50"""
import numpy as np, wave, sys, pathlib
SR = 44100; rng = np.random.default_rng(5)
f_of = lambda n: 440.0*2**((n-69)/12)
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
PEDIDOS = sys.argv[2:]          # vacío = todas las de RECETAS (al final del archivo)

class Ctx:
    def __init__(s, bpm, nbars):
        s.bpm = bpm; s.beat = 60/bpm; s.bar = 4*s.beat; s.step = s.bar/16; s.nbars = nbars
        s.L = int(round(nbars*s.bar*SR)); s.T = s.L/SR
    def new(s): return np.zeros((2, 2*s.L))
    def at(s, bar, step=0.0): return int(round((bar*s.bar + step*s.step)*SR))
    def fold(s, b): return b[:, :s.L] + b[:, s.L:2*s.L]

def env(n, a, r, curve=1.5):
    e = np.ones(n); na = min(n, int(a*SR)); nr = min(n, int(r*SR))
    if na > 0: e[:na] = np.linspace(0,1,na)**curve
    if nr > 0: e[-nr:] *= np.linspace(1,0,nr)**curve
    return e
def additive(freq, n, harm, detune=0.0, rand_phase=True, vib=0.0, vrate=5.5):
    t = np.arange(n)/SR; out = np.zeros(n)
    ph = 2*np.pi*np.cumsum(freq*(1+detune)*(1+vib*np.sin(2*np.pi*vrate*t)))/SR if vib else 2*np.pi*freq*(1+detune)*t
    for k, a in enumerate(harm, 1):
        if freq*k*(1+detune) > SR*0.45: break
        out += a*np.sin(k*ph + (rng.uniform(0, 2*np.pi) if rand_phase else 0.0))
    return out
def saw_harm(freq, fc=4500): return [1/k for k in range(1, max(1, int(min(fc, SR*0.45)/freq))+1)]
def sq_harm(freq, fc=4500): return [(1/k if k % 2 else 0.0) for k in range(1, max(1, int(min(fc, SR*0.45)/freq))+1)]
def lowpass(x, fc, order=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR); return np.fft.irfft(X/np.sqrt(1+(f/fc)**(2*order)), n=len(x))
def highpass(x, fc, order=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR); return np.fft.irfft(X*(1-1/np.sqrt(1+(f/fc)**(2*order))), n=len(x))
def place(buf, start, sig, pan=0.5):
    n = min(len(sig), buf.shape[1]-start)
    if n > 0: buf[0, start:start+n] += sig[:n]*np.sqrt(1-pan); buf[1, start:start+n] += sig[:n]*np.sqrt(pan)
def delay_circ(x, L, d, g, taps=3):
    """Delay con realimentación que da la vuelta al bucle: sigue siendo perfecto."""
    y = x.copy()
    for k in range(1, taps+1): y[:, :L] += np.roll(x[:, :L], d*k, axis=1)*g**k
    return y

# ---- instrumentos ---------------------------------------------------------------
ORGAN_H = [1, 0.6, 0.45, 0.28, 0.16, 0.09, 0.05]
def pluck(f, n):
    t = np.arange(n)/SR; out = np.zeros(n)
    for k in range(1, 13):
        if f*k > SR*0.45: break
        out += np.sin(2*np.pi*f*k*t + rng.uniform(0, 6.28))/k*np.exp(-t*(5+3.5*k))
    return (out + lowpass(rng.normal(size=n), 4000)*np.exp(-t/0.003)*0.25)*np.minimum(1, t/0.002)
def spicc(f, n, tau=0.09):
    t = np.arange(n)/SR
    sig = sum(additive(f, n, saw_harm(f, 3500), detune=d) for d in (-0.005, 0, 0.005))/3
    return highpass(sig, 180)*np.exp(-t/tau)*np.minimum(1, t/0.012)
def legato(f, n):
    sig = sum(additive(f, n, saw_harm(f, 3000), detune=d, vib=0.006, vrate=5.2) for d in (-0.004, 0, 0.004))/3
    return lowpass(sig, 2200)*env(n, 0.35, 0.4)
def piano(f, n=int(3.2*SR)):
    t = np.arange(n)/SR; out = np.zeros(n)
    for k, a in enumerate([1,0.55,0.32,0.2,0.11,0.07,0.04], 1):
        fk = f*k*np.sqrt(1+0.0004*k*k); out += a*np.sin(2*np.pi*fk*t + rng.uniform(0, 6.28))*np.exp(-t*(0.75+0.45*k))
    return (out + lowpass(rng.normal(size=n)*np.exp(-t/0.004), 1800)*0.35)*np.minimum(1, t/0.003)
def synth_bass(f, n):
    t = np.arange(n)/SR; raw = additive(f, n, saw_harm(f, 2500), rand_phase=False) + 0.5*additive(f, n, sq_harm(f, 2500), rand_phase=False, detune=0.003)
    dark, bright = lowpass(raw, 260), lowpass(raw, 1900)
    return (dark + (bright-dark)*np.exp(-t/0.12) + 0.6*np.sin(2*np.pi*f*t))*env(n, 0.003, 0.03)
def synth_arp(f, n):
    t = np.arange(n)/SR; raw = additive(f, n, saw_harm(f, 5000)) + 0.4*additive(f, n, sq_harm(f, 5000), detune=0.004)
    return lowpass(raw, 3200)*np.exp(-t/0.13)*np.minimum(1, t/0.002)
def formant(F, picos, anchos):
    return 0.04 + sum(np.exp(-0.5*((F-p)/w)**2) for p, w in zip(picos, anchos))
def choir(f, n, picos=(650, 1100, 2650, 3400), anchos=(110, 140, 240, 300)):
    kmax = int(min(5000, SR*0.45)/f); harm = [float(formant(f*k, picos, anchos))/k**0.6 for k in range(1, kmax+1)]
    sig = sum(additive(f, n, harm, detune=d, vib=0.005, vrate=4.8+rng.uniform(-0.4, 0.4)) for d in (-0.006, -0.002, 0.003, 0.007))/4
    return lowpass(sig, 4500)*env(n, 0.8, 0.9)
def taiko(n):
    t = np.arange(n)/SR; f = 95*(45/95)**(t/0.5)
    body = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*5.0)
    slap = lowpass(rng.normal(size=n), 3000)*np.exp(-t/0.02)*0.5
    return np.tanh((body + slap)*1.4)
def timpani(f, n):
    t = np.arange(n)/SR; out = np.zeros(n); fd = f*(1-0.03*np.exp(-t/0.3))
    for k, (r, a) in enumerate(zip((1, 1.5, 1.98, 2.44, 2.9), (1, 0.5, 0.35, 0.25, 0.15))):
        out += a*np.sin(2*np.pi*np.cumsum(fd*r)/SR)*np.exp(-t*(2.2+1.2*k))
    return out + lowpass(rng.normal(size=n), 2500)*np.exp(-t/0.012)*0.4
def bell(f, n):
    t = np.arange(n)/SR
    return (np.sin(2*np.pi*f*t) + 0.5*np.sin(2*np.pi*f*2.76*t) + 0.3*np.sin(2*np.pi*f*5.4*t)*np.exp(-t*3))*np.exp(-t/0.6)*0.5
def organ(f, n):
    return (additive(f, n, ORGAN_H, rand_phase=False) + 0.7*additive(f, n, ORGAN_H, detune=0.0035))*env(n, 0.006, 0.07)

# ---- capas comunes --------------------------------------------------------------
def capa_pad(c, prog, bright=False, fc=2100):
    pad = c.new()
    for b, (root, third) in enumerate(prog):
        n = int((c.bar+0.9)*SR); e = env(n, 0.55, 0.85)*np.linspace(0.8, 1.0, n)
        voces = [(24,1.0),(24+third,0.8),(31,0.8),(36,0.55),(36+third,0.45)] + ([(43,0.35),(48,0.3)] if bright else [])
        for iv, g in voces:
            f = f_of(root+iv)
            for ch, dets in enumerate([(-0.006,-0.002,0.003),(-0.003,0.002,0.006)]):
                sig = sum(additive(f, n, saw_harm(f, 3800), detune=d) for d in dets)/3
                s0 = c.at(b); pad[ch, s0:s0+n] += sig*e*g
    return np.stack([highpass(lowpass(x, fc), 140) for x in pad])
def capa_sub(c, prog):
    sub = c.new()
    for b, (root, _) in enumerate(prog):
        n = int((c.bar+0.6)*SR); t = np.arange(n)/SR; f = f_of(root)
        sig = np.sin(2*np.pi*f*t) + 0.35*np.sin(2*np.pi*2*f*t) + 0.25*lowpass(additive(2*f, n, saw_harm(2*f, 900)), 320)
        place(sub, c.at(b), sig*env(n, 0.35, 0.6))
    return sub
def capa_tick(c, cada=2, brillo=1.0):
    """cada = pasos de semicorchea entre tics: 1 semicorchea, 2 corchea, 4 negra."""
    tick = c.new(); k = 0
    while k*cada < c.nbars*16:
        n = int(0.05*SR); t = np.arange(n)/SR
        click = highpass(rng.normal(size=n)*np.exp(-t/0.0022), 2800)*0.6
        ping = np.sin(2*np.pi*3150*brillo*t)*np.exp(-t/0.011) + 0.5*np.sin(2*np.pi*5200*brillo*t)*np.exp(-t/0.006)
        pos = k*cada; acc = 1.0 if pos % 16 == 0 else (0.8 if pos % 4 == 0 else (0.62 if pos % 2 == 0 else 0.5))
        place(tick, c.at(pos//16, pos % 16), (click+ping)*np.minimum(1, t/0.0008)*acc, 0.42 if k % 2 else 0.58)
        k += 1
    return tick
def capa_swell(c, prog, bars):
    sw = c.new()
    for b in bars:
        root = prog[b][0]; n = int(c.bar*1.15*SR); t = np.arange(n)/SR; sig = np.zeros(n)
        for iv, d in [(0,-0.004),(0,0.004),(7,0.0),(12,-0.003)]:
            f = f_of(root+iv); sig += additive(f, n, saw_harm(f, 2000), detune=d)*(0.6 if iv else 1.0)
        e = np.minimum(1, (t/1.5)**2)*np.exp(-np.maximum(0, t-1.5)/1.4)
        place(sw, c.at(b), np.tanh(lowpass(sig*e, 650)*1.6))
    return sw
def arp_layer(c, prog, patron, iv_base, instr, dur_steps=0.95, pan_w=0.18, acc=(1.0, 0.85, 0.72)):
    """Un instrumento tocando el patrón en semicorcheas, un acorde por compás."""
    buf = c.new()
    for b, (root, third) in enumerate(prog):
        for s in range(16):
            iv = patron[s % len(patron)]; iv = third+12 if iv == '3' else (third if iv == 't' else iv)
            if iv is None: continue
            n = int(c.step*dur_steps*SR*(3.5 if instr in (pluck, piano) else 1))
            a = acc[0] if s % 4 == 0 else (acc[1] if s % 2 == 0 else acc[2])
            place(buf, c.at(b, s), instr(f_of(root+iv_base+iv), n)*a, 0.5+pan_w*np.sin(2*np.pi*(s+0.5)/16))
    return buf

# ---- las cinco recetas -------------------------------------------------------------
def r_reloj():
    c = Ctx(72, 8); P = [(38,3),(34,4),(41,4),(36,4),(38,3),(34,4),(31,3),(33,4)]   # Dm Bb F C Dm Bb Gm A
    L = dict(
        tick=capa_tick(c, 1, 1.15),
        pluck=arp_layer(c, P, [0,7,12,7,0,7,12,'3',0,7,12,7,0,7,'3',12], 36, pluck),
        cello=arp_layer(c, P, [0,None,0,None]*4, 12, spicc, acc=(1.0,0.8,0.8)),
        pad=capa_pad(c, P), sub=capa_sub(c, P), swell=capa_swell(c, P, (0,4)))
    G = dict(tick=(0.8,0.2), pluck=(0.55,0.35), cello=(0.75,0.25), pad=(0.22,0.3), sub=(0.45,0), swell=(0.35,0.4))
    return c, L, G, 0.8
def r_piano():
    c = Ctx(60, 8); P = [(33,3),(29,4),(36,4),(31,4),(33,3),(29,4),(38,3),(40,4)]   # Am F C G Am F Dm E
    pat = [0,None,7,None,12,None,'3',None,19,None,'3',None,12,None,7,None]
    pno = arp_layer(c, P, pat, 24, piano, pan_w=0.12, acc=(1.0,0.75,0.75))
    for b, (root, _) in enumerate(P): place(pno, c.at(b), piano(f_of(root+12))*0.8, 0.5)
    mel = c.new()
    for bar, beat, n in [(4,0,76),(4,2,74),(5,0,72),(6,0,74),(6,2,76),(7,0,71)]:
        place(mel, c.at(bar, beat*4), piano(f_of(n))*0.55, 0.5+0.12*np.sign(n-74))
    L = dict(pno=np.stack([lowpass(x, 5000) for x in pno]), mel=mel, tick=capa_tick(c, 4, 0.9), pad=capa_pad(c, P), sub=capa_sub(c, P))
    G = dict(pno=(0.6,0.5), mel=(0.6,0.55), tick=(0.35,0.3), pad=(0.42,0.3), sub=(0.42,0))
    return c, L, G, 1.3
def r_sintes():
    c = Ctx(100, 16); P = [(40,3),(36,4),(31,4),(38,4)]*2 + [(40,3),(36,4),(33,3),(35,4)]*2   # Em C G D ×2 · Em C Am B ×2
    bass = c.new()
    for b, (root, _) in enumerate(P):
        for e8 in range(8):
            iv = 12 if (b % 2 == 1 and e8 == 7) else 0
            n = int(c.step*1.8*SR); a = 1.0 if e8 % 2 == 0 else 0.8
            place(bass, c.at(b, e8*2), synth_bass(f_of(root+iv), n)*a, 0.5)
    arp = arp_layer(c, P, [0,7,12,19,12,7,0,'3',0,7,12,19,12,'3',7,0], 24, synth_arp, pan_w=0.3)
    arp = delay_circ(arp, c.L, int(3*c.step*SR), 0.38)
    L = dict(bass=bass, arp=arp, pad=capa_pad(c, P, fc=1500), tick=capa_tick(c, 2, 1.4), sub=capa_sub(c, P), swell=capa_swell(c, P, (0,8)))
    G = dict(bass=(0.6,0.05), arp=(0.5,0.4), pad=(0.38,0.35), tick=(0.6,0.25), sub=(0.3,0), swell=(0.4,0.4))
    return c, L, G, 0.9
def r_cuerdas():
    c = Ctx(66, 8); P = [(31,3),(39,4),(34,4),(41,4),(31,3),(39,4),(36,3),(38,4)]   # Gm Eb Bb F Gm Eb Cm D
    viol = arp_layer(c, P, [0,0,7,7,12,12,7,7,0,0,'3','3',7,7,12,12], 36, spicc, pan_w=0.25, acc=(1.0,0.85,0.7))
    cello = arp_layer(c, P, [0,None,0,None]*4, 12, spicc, acc=(1.0,0.8,0.8))
    line = c.new()
    for bar, beat, n, beats in [(4,0,74,4),(5,0,75,2),(5,2,74,2),(6,0,72,4),(7,0,69,2),(7,2,66,2)]:
        place(line, c.at(bar, beat*4), legato(f_of(n), int(beats*c.beat*1.05*SR)), 0.5)
    timp = c.new()
    for b, (root, _) in enumerate(P):
        place(timp, c.at(b), timpani(f_of(root+12), int(1.4*SR)), 0.5)
        if b in (3, 7):
            for s in (14, 15): place(timp, c.at(b, s), timpani(f_of(root+12), int(0.6*SR))*0.5, 0.5)
    L = dict(viol=viol, cello=cello, line=line, timp=timp, pad=capa_pad(c, P, bright=True), sub=capa_sub(c, P), tick=capa_tick(c, 4, 0.9))
    G = dict(viol=(0.85,0.35), cello=(0.7,0.3), line=(0.55,0.45), timp=(0.5,0.35), pad=(0.3,0.3), sub=(0.45,0), tick=(0.28,0.25))
    return c, L, G, 1.1
def r_coro():
    c = Ctx(56, 8); P = [(36,3),(32,4),(39,4),(34,4),(36,3),(32,4),(29,3),(31,4)]   # Cm Ab Eb Bb Cm Ab Fm G
    voces = c.new(); bajo = c.new(); camp = c.new(); tk = c.new()
    for b, (root, third) in enumerate(P):
        n = int((c.bar+1.0)*SR)
        for iv, g in [(24,1.0),(24+third,0.8),(31,0.8),(36,0.6)]:
            for ch, d in enumerate((-0.004, 0.004)):
                s0 = c.at(b); sig = choir(f_of(root+iv)*(1+d), n)*g; voces[ch, s0:s0+n] += sig
        place(bajo, c.at(b), choir(f_of(root+12), n, picos=(450, 800, 2400), anchos=(90, 120, 250)), 0.5)
        place(camp, c.at(b), bell(f_of(root+55), int(2.2*SR))*(1.0 if b % 4 == 0 else 0.6), 0.5)
        for s in (0, 8): place(tk, c.at(b, s), taiko(int(0.8*SR))*(1.0 if s == 0 else 0.75), 0.5)
        if b in (3, 7):
            for s in (13, 14, 15): place(tk, c.at(b, s), taiko(int(0.4*SR))*0.6, 0.5)
    L = dict(voces=voces, bajo=bajo, camp=camp, taiko=tk, sub=capa_sub(c, P), pad=capa_pad(c, P), tick=capa_tick(c, 2, 0.85), swell=capa_swell(c, P, (0,4)))
    G = dict(voces=(0.7,0.45), bajo=(0.4,0.2), camp=(0.5,0.5), taiko=(0.7,0.3), sub=(0.45,0), pad=(0.28,0.3), tick=(0.22,0.2), swell=(0.45,0.4))
    return c, L, G, 1.4


def rhodes(f, n):
    t = np.arange(n)/SR
    tono = np.sin(2*np.pi*f*t) + 0.35*np.sin(2*np.pi*2*f*t + 0.5)*np.exp(-t*3) + 0.12*np.sin(2*np.pi*3*f*t)*np.exp(-t*6)
    trem = 1 - 0.12*(1-np.cos(2*np.pi*4.5*t))/2
    tine = lowpass(rng.normal(size=n), 5000)*np.exp(-t/0.003)*0.2
    return (tono*np.exp(-t/1.1)*trem + tine)*np.minimum(1, t/0.003)
def marimba(f, n):
    t = np.arange(n)/SR
    y = np.sin(2*np.pi*f*t)*np.exp(-t/0.28) + 0.5*np.sin(2*np.pi*4*f*t)*np.exp(-t/0.06) + 0.2*np.sin(2*np.pi*10.1*f*t)*np.exp(-t/0.03)
    return (y + lowpass(rng.normal(size=n), 3000)*np.exp(-t/0.002)*0.3)*np.minimum(1, t/0.0015)
def kick(n):
    t = np.arange(n)/SR; f = 150*(48/150)**(np.minimum(t, 0.12)/0.12)
    return np.tanh((np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9) + lowpass(rng.normal(size=n), 2500)*np.exp(-t/0.006)*0.5)*1.5)
def snare(n):
    t = np.arange(n)/SR
    return (highpass(lowpass(rng.normal(size=n), 6000), 900)*np.exp(-t/0.06) + np.sin(2*np.pi*190*t)*np.exp(-t/0.05)*0.5)
def dist_bass(f, n):
    t = np.arange(n)/SR; raw = additive(f, n, saw_harm(f, 3000), rand_phase=False) + 0.5*additive(f, n, saw_harm(f, 3000), rand_phase=False, detune=0.005)
    return lowpass(np.tanh(raw*3.0), 1400)*env(n, 0.004, 0.04) + 0.5*np.sin(2*np.pi*f*t)*env(n, 0.004, 0.04)
def capa_swell_lento(c, prog, bars, ataque=2.5, fc=900):
    sw = c.new()
    for b in bars:
        root, third = prog[b]; n = int(min(c.bar*1.6, ataque+2.5)*SR); t = np.arange(n)/SR; sig = np.zeros(n)
        for iv, d in [(0,-0.004),(0,0.004),(7,0.0),(12,-0.003),(12+third,0.002)]:
            f = f_of(root+iv); sig += additive(f, n, saw_harm(f, 2500), detune=d)*(0.6 if iv else 1.0)
        e = np.minimum(1, (t/ataque)**2)*np.exp(-np.maximum(0, t-ataque)/1.6)
        place(sw, c.at(b), np.tanh(lowpass(sig*e, fc)*1.4))
    return sw

def r_lluvia():
    c = Ctx(76, 8); P = [(39,4),(36,3),(32,4),(34,4),(39,4),(31,3),(32,4),(34,4)]   # Eb Cm Ab Bb Eb Gm Ab Bb
    rh = arp_layer(c, P, [0,None,7,None,12,None,'3',None,7,None,12,None,'3',None,19,None], 24, rhodes, pan_w=0.15, acc=(1.0,0.8,0.8))
    camp = c.new()
    for b, (root, third) in enumerate(P):
        for beat, iv in ((0, 43), (2, 36+third)):
            if (b + beat//2) % 2 == 0: place(camp, c.at(b, beat*4), bell(f_of(root+iv+12), int(2.0*SR))*0.7, 0.5+0.15*(1 if beat else -1))
    L = dict(rh=np.stack([lowpass(x, 6000) for x in rh]), camp=camp, pad=capa_pad(c, P), sub=capa_sub(c, P), tick=capa_tick(c, 2, 0.85))
    G = dict(rh=(0.6,0.45), camp=(0.6,0.55), pad=(0.34,0.3), sub=(0.4,0), tick=(0.2,0.25))
    return c, L, G, 1.4
def r_marcha():
    c = Ctx(120, 16); P = [(29,3),(37,4),(32,4),(39,4)]*2 + [(29,3),(37,4),(34,3),(36,4)]*2   # Fm Db Ab Eb ×2 · Fm Db Bbm C ×2
    bass = c.new(); perc = c.new()
    for b, (root, _) in enumerate(P):
        for e8 in range(8):
            place(bass, c.at(b, e8*2), dist_bass(f_of(root), int(c.step*1.7*SR))*(1.0 if e8 % 2 == 0 else 0.8), 0.5)
        if b % 2 == 1:
            for s in (14, 15): place(bass, c.at(b, s), dist_bass(f_of(root+12), int(c.step*0.9*SR))*0.7, 0.5)
        for s in (0, 8): place(perc, c.at(b, s), kick(int(0.35*SR)), 0.5)
        if b % 2 == 1: place(perc, c.at(b, 14), kick(int(0.3*SR))*0.7, 0.5)
        for s in (4, 12): place(perc, c.at(b, s), snare(int(0.2*SR))*0.5, 0.5)
    viol = arp_layer(c, P, [0,None,0,None,7,None,0,None,0,None,12,None,7,None,'3',None], 36, spicc, pan_w=0.25, acc=(1.0,0.8,0.7))
    L = dict(bass=bass, perc=perc, viol=viol, tick=capa_tick(c, 1, 1.3), pad=capa_pad(c, P, fc=1500), sub=capa_sub(c, P), swell=capa_swell(c, P, (0,8)))
    G = dict(bass=(0.55,0.05), perc=(0.7,0.15), viol=(0.55,0.3), tick=(0.5,0.2), pad=(0.3,0.3), sub=(0.3,0), swell=(0.4,0.4))
    return c, L, G, 0.7
def r_marimba():
    c = Ctx(84, 8); P = [(33,4),(30,3),(38,4),(40,4),(33,4),(37,3),(38,4),(40,4)]   # A F#m D E A C#m D E
    mar = arp_layer(c, P, [0,'t',7,12,7,'t',0,'t',0,'t',7,12,19,12,7,'t'], 36, marimba, pan_w=0.3, acc=(1.0,0.8,0.65))
    grave = arp_layer(c, P, [0,None,None,None,None,None,None,None,7,None,None,None,None,None,None,None], 24, marimba, acc=(1.0,0.8,0.8))
    camp = c.new()
    for b in (3, 7): place(camp, c.at(b, 8), bell(f_of(P[b][0]+55), int(2.0*SR))*0.6, 0.5)
    L = dict(mar=mar, grave=grave, camp=camp, pad=capa_pad(c, P), sub=capa_sub(c, P), tick=capa_tick(c, 4, 0.9))
    G = dict(mar=(0.7,0.4), grave=(0.6,0.3), camp=(0.55,0.5), pad=(0.3,0.3), sub=(0.42,0), tick=(0.2,0.25))
    return c, L, G, 1.0
def r_nocturno():
    c = Ctx(50, 8); P = [(30,3),(38,4),(33,4),(40,4),(30,3),(38,4),(35,3),(37,4)]   # F#m D A E F#m D Bm C#
    bajo = c.new(); camp = c.new(); linea = c.new()
    for b, (root, third) in enumerate(P):
        n = int((c.bar+1.2)*SR)
        place(bajo, c.at(b), choir(f_of(root+12), n, picos=(420, 750, 2300), anchos=(90, 120, 250)), 0.5)
    for bar, step, iv, g in [(0,4,55,0.8),(1,10,48,0.5),(3,12,52,0.6),(4,4,55,0.8),(5,10,48,0.5),(6,6,50,0.6),(7,12,52,0.7)]:
        place(camp, c.at(bar, step), bell(f_of(P[bar][0]+iv), int(3.0*SR))*g, 0.5+0.2*(1 if step % 8 else -1))
    for bar, beat, n, beats in [(4,0,66,4),(5,0,69,4),(6,0,71,2),(6,2,69,2),(7,0,68,4)]:
        place(linea, c.at(bar, beat*4), legato(f_of(n-12), int(beats*c.beat*1.05*SR)), 0.5)
    L = dict(bajo=bajo, camp=camp, linea=linea, swell=capa_swell_lento(c, P, (0,2,4,6)), pad=capa_pad(c, P, fc=900), sub=capa_sub(c, P), tick=capa_tick(c, 4, 0.8))
    G = dict(bajo=(0.45,0.3), camp=(0.45,0.6), linea=(0.45,0.5), swell=(0.6,0.45), pad=(0.4,0.35), sub=(0.55,0), tick=(0.25,0.3))
    return c, L, G, 2.0

# ---- las familias nuevas: tensión, emoción, épica, neutra ---------------------------------
def r_tension_latido():
    """Latido: un corazón grave que se acelera en la segunda mitad, tic de corcheas y un
    trémolo de cuerdas que va subiendo. Para la cuenta atrás y el «¿y ahora qué?»."""
    c = Ctx(92, 8); P = [(33,3),(33,3),(29,4),(28,4),(33,3),(33,3),(34,4),(28,4)]   # Am Am F E · Am Am Bb E
    lat = c.new(); trem = c.new()
    for b, (root, third) in enumerate(P):
        cada = 8 if b < 4 else 4                        # el corazón se acelera
        for s in range(0, 16, cada):
            place(lat, c.at(b, s), kick(int(0.28*SR))*0.9, 0.5)
            place(lat, c.at(b, s+1), kick(int(0.22*SR))*0.6, 0.5)
        g = 0.25 + 0.75*(b/7)
        for s in range(16):
            iv = 36 if s % 4 != 3 else 36+third
            place(trem, c.at(b, s), spicc(f_of(root+iv), int(c.step*1.6*SR), tau=0.06)*g*(1.0 if s % 4 == 0 else 0.7), 0.5+0.2*np.sin(2*np.pi*s/16))
    L = dict(lat=lat, trem=trem, tick=capa_tick(c, 2, 1.0), pad=capa_pad(c, P, fc=1200), sub=capa_sub(c, P), swell=capa_swell(c, P, (3,7)))
    G = dict(lat=(0.8,0.1), trem=(0.6,0.35), tick=(0.45,0.25), pad=(0.3,0.3), sub=(0.5,0), swell=(0.4,0.4))
    return c, L, G, 0.9
def r_tension_tremolo():
    """Trémolo: violines temblando, chelos a golpes y redobles de caja que anuncian algo."""
    c = Ctx(110, 8); P = [(31,3),(31,3),(36,3),(38,4),(31,3),(31,3),(27,4),(38,4)]   # Gm Gm Cm D · Gm Gm Eb D
    viol = c.new(); cello = c.new(); caja = c.new()
    for b, (root, third) in enumerate(P):
        for s in range(16):
            iv = [0,7,12,7][s % 4] + 36
            place(viol, c.at(b, s), spicc(f_of(root+iv), int(c.step*1.4*SR), tau=0.05)*(0.9 if s % 4 == 0 else 0.65), 0.5+0.25*np.sin(2*np.pi*s/16))
        for s in (0, 6, 8, 14):
            place(cello, c.at(b, s), spicc(f_of(root+12), int(c.step*2.5*SR), tau=0.12)*(1.0 if s in (0, 8) else 0.75), 0.5)
        if b % 2 == 1:
            for s in range(12, 16): place(caja, c.at(b, s), snare(int(0.15*SR))*(0.35+0.15*(s-12)), 0.5)
        if b in (3, 7): place(caja, c.at(b, 0), taiko(int(0.7*SR))*0.8, 0.5)
    L = dict(viol=viol, cello=cello, caja=caja, tick=capa_tick(c, 2, 1.2), pad=capa_pad(c, P, fc=1600), sub=capa_sub(c, P), swell=capa_swell(c, P, (0,4)))
    G = dict(viol=(0.7,0.35), cello=(0.7,0.3), caja=(0.6,0.3), tick=(0.4,0.2), pad=(0.28,0.3), sub=(0.45,0), swell=(0.4,0.4))
    return c, L, G, 1.0
def r_emocion_cuerdas():
    """Cuerdas lentas: acordes que se abren, un chelo que canta, sin pulso. Para el giro."""
    c = Ctx(64, 8); P = [(36,4),(31,4),(33,3),(29,4),(36,4),(31,4),(29,4),(31,4)]   # C G Am F · C G F G
    cel = c.new(); alto = c.new()
    for bar, beat, n, beats in [(0,0,60,4),(1,0,62,2),(1,2,64,2),(2,0,64,4),(3,0,62,4),(4,0,67,4),(5,0,65,2),(5,2,64,2),(6,0,62,4),(7,0,60,4)]:
        place(cel, c.at(bar, beat*4), legato(f_of(n-12), int(beats*c.beat*1.08*SR)), 0.5)
    for b, (root, third) in enumerate(P):
        n = int((c.bar+1.2)*SR)
        for iv, g in [(36,0.8),(36+third,0.7),(43,0.6),(48,0.45)]:
            for ch, d in enumerate((-0.004, 0.004)):
                s0 = c.at(b); alto[ch, s0:s0+n] += legato(f_of(root+iv)*(1+d), n)*g*0.5
    L = dict(cel=cel, alto=alto, pad=capa_pad(c, P, bright=True, fc=2600), sub=capa_sub(c, P), swell=capa_swell_lento(c, P, (0,4), ataque=3.0, fc=1200))
    G = dict(cel=(0.65,0.5), alto=(0.5,0.5), pad=(0.4,0.4), sub=(0.4,0), swell=(0.4,0.5))
    return c, L, G, 1.8
def r_emocion_guitarra():
    """Guitarra: arpegio punteado en mayor, un pad debajo, una campana de vez en cuando. Cercana."""
    c = Ctx(80, 8); P = [(31,4),(38,4),(28,3),(36,4),(31,4),(38,4),(36,4),(38,4)]   # G D Em C · G D C D
    gui = arp_layer(c, P, [0,7,12,'3',19,'3',12,7,0,7,12,'3',19,12,'3',7], 24, pluck, pan_w=0.2, acc=(1.0,0.7,0.6))
    bajo = arp_layer(c, P, [0]+[None]*7+[7]+[None]*7, 12, pluck, acc=(1.0,0.8,0.8))
    camp = c.new()
    for b in (1, 3, 5, 7): place(camp, c.at(b, 8), bell(f_of(P[b][0]+48), int(2.0*SR))*0.5, 0.5)
    L = dict(gui=np.stack([lowpass(x, 5500) for x in gui]), bajo=bajo, camp=camp, pad=capa_pad(c, P, fc=1800), sub=capa_sub(c, P), tick=capa_tick(c, 4, 0.8))
    G = dict(gui=(0.7,0.4), bajo=(0.6,0.2), camp=(0.5,0.5), pad=(0.3,0.35), sub=(0.35,0), tick=(0.15,0.2))
    return c, L, G, 1.2
def r_epica_tambores():
    """Tambores: taikos a negras, golpes graves de cuerda, ostinato de violines que crece. Escala."""
    c = Ctx(100, 8); P = [(38,3),(34,4),(36,4),(33,4),(38,3),(34,4),(29,4),(33,4)]   # Dm Bb C A · Dm Bb F A
    tk = c.new(); ost = c.new(); gol = c.new()
    for b, (root, third) in enumerate(P):
        for s in (0, 4, 8, 12): place(tk, c.at(b, s), taiko(int(0.7*SR))*(1.0 if s == 0 else 0.7), 0.5)
        for s in (6, 14): place(tk, c.at(b, s), taiko(int(0.4*SR))*0.5, 0.5)
        if b in (3, 7):
            for s in (13, 14, 15): place(tk, c.at(b, s), taiko(int(0.4*SR))*0.7, 0.5)
        PAT = [0,0,7,7,12,12,7,7,0,0,third+12,third+12,7,7,12,12]
        for s in range(16):
            place(ost, c.at(b, s), spicc(f_of(root+36+PAT[s]), int(c.step*2.0*SR))*(0.5+0.5*(b/7))*(1.0 if s % 4 == 0 else 0.75), 0.5+0.22*np.sin(2*np.pi*s/16))
        if b >= 4 and b % 2 == 0:
            for iv in (12, 19): place(gol, c.at(b), spicc(f_of(root+iv), int(c.beat*1.2*SR), tau=0.35)*0.8, 0.5)
    L = dict(tk=tk, ost=ost, gol=gol, pad=capa_pad(c, P, bright=True), sub=capa_sub(c, P), tick=capa_tick(c, 2, 1.1), swell=capa_swell(c, P, (0,4)))
    G = dict(tk=(0.8,0.3), ost=(0.6,0.35), gol=(0.5,0.35), pad=(0.3,0.3), sub=(0.45,0), tick=(0.3,0.2), swell=(0.4,0.4))
    return c, L, G, 1.3
def r_neutra_pulso():
    """Pulso: tic suave, bajo redondo a corcheas, arpegio de sinte discreto. Para explicar."""
    c = Ctx(96, 8); P = [(33,4),(38,4),(30,3),(36,4),(33,4),(38,4),(36,4),(38,4)]   # A E F#m D · A E D E
    bass = c.new()
    for b, (root, _) in enumerate(P):
        for e8 in range(8): place(bass, c.at(b, e8*2), synth_bass(f_of(root), int(c.step*1.6*SR))*(1.0 if e8 % 2 == 0 else 0.7), 0.5)
    arp = arp_layer(c, P, [0,None,7,None,12,None,'3',None,7,None,12,None,'3',None,19,None], 36, synth_arp, pan_w=0.25, acc=(0.9,0.7,0.7))
    arp = delay_circ(arp, c.L, int(3*c.step*SR), 0.3)
    L = dict(bass=bass, arp=arp, pad=capa_pad(c, P, fc=1600), tick=capa_tick(c, 2, 0.9), sub=capa_sub(c, P))
    G = dict(bass=(0.5,0.05), arp=(0.45,0.4), pad=(0.4,0.35), tick=(0.35,0.25), sub=(0.3,0))
    return c, L, G, 0.9
def r_neutra_teclas():
    """Teclas: acordes de piano eléctrico, un bajo suave, shaker. Amable, sin drama."""
    c = Ctx(88, 8); P = [(29,4),(33,3),(31,4),(36,4),(29,4),(33,3),(38,3),(31,4)]   # F Am G C · F Am Dm G
    rh = c.new(); shk = c.new()
    for b, (root, third) in enumerate(P):
        for s in (0, 6, 8, 12):
            for j, iv in enumerate((24, 24+third, 31, 36)):
                place(rh, c.at(b, s), rhodes(f_of(root+iv), int(c.beat*1.6*SR))*(0.55 if s in (0, 8) else 0.4), 0.4+0.07*j)
        for s in range(2, 16, 4):
            n = int(0.06*SR); t = np.arange(n)/SR
            place(shk, c.at(b, s), highpass(rng.normal(size=n), 5000)*np.exp(-t/0.02)*0.5, 0.5+0.15*(1 if s % 8 == 2 else -1))
    bajo = arp_layer(c, P, [0]+[None]*5+[0]+[None]*3+[7]+[None]*5, 12, pluck, acc=(1.0,0.8,0.8))
    L = dict(rh=np.stack([lowpass(x, 6000) for x in rh]), shk=shk, bajo=bajo, pad=capa_pad(c, P, fc=1400), sub=capa_sub(c, P))
    G = dict(rh=(0.6,0.4), shk=(0.35,0.2), bajo=(0.55,0.15), pad=(0.3,0.3), sub=(0.35,0))
    return c, L, G, 1.1

# nombres genéricos por familia: <familia>-<instrumento>. Nada de nombres propios.
RECETAS = {"tension-reloj": r_reloj, "tension-marcha": r_marcha, "tension-drone": r_nocturno,
           "tension-latido": r_tension_latido, "tension-tremolo": r_tension_tremolo,
           "emocion-piano": r_piano, "emocion-cuerdas": r_emocion_cuerdas, "emocion-guitarra": r_emocion_guitarra,
           "epica-cuerdas": r_cuerdas, "epica-coro": r_coro, "epica-tambores": r_epica_tambores,
           "neutra-sintes": r_sintes, "neutra-cristal": r_lluvia, "neutra-marimba": r_marimba,
           "neutra-pulso": r_neutra_pulso, "neutra-teclas": r_neutra_teclas}

def ir(seconds, tau):
    n = int(seconds*SR); t = np.arange(n)/SR; out = np.zeros((2, n))
    for ch in range(2): out[ch] = lowpass(rng.normal(size=n), 5500)*np.exp(-t/tau)*np.minimum(1, t/0.02)
    out = np.concatenate([np.zeros((2, int(0.028*SR))), out], 1); return out/np.sqrt((out**2).sum(1)).max()
def write(path, y):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1).T*32767).astype('<i2').tobytes())

for name in (PEDIDOS or list(RECETAS)):
    c, L, G, tau = RECETAS[name]()
    L = {k: c.fold(v) for k, v in L.items()}
    IR = ir(min(3.5, c.T-1), tau)
    dry = sum(L[k]*G[k][0] for k in L); send = sum(L[k]*G[k][0]*G[k][1] for k in L)
    wet = np.stack([np.fft.irfft(np.fft.rfft(send[ch], n=c.L)*np.fft.rfft(IR[ch], n=c.L), n=c.L) for ch in range(2)])
    y = dry + wet*1.1
    y = np.stack([highpass(lowpass(x, 16000), 28) for x in y])
    y /= np.abs(y).max(); y = np.tanh(y*1.25)/np.tanh(1.25); y *= 0.891/np.abs(y).max()
    write(OUT/f"{name}.wav", y)
    picos = {k: round(float(20*np.log10(np.abs(L[k]*G[k][0]).max()+1e-9)), 1) for k in L}
    print(f"{name:8s} {c.T:5.2f} s · {c.nbars} compases a {c.bpm} BPM · RMS {20*np.log10(np.sqrt((y**2).mean())):.1f} dBFS · picos {picos}")
