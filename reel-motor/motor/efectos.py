"""Las recetas sintetizadas, por si alguna vez quieres una variante.

Los efectos que usa el motor son grabaciones y ya vienen en motor/sonidos/
(INDICE.md): esto NO los toca. Escribe versiones sintetizadas con numpy en
motor/sonidos/_sintetizados/, que el mezclador no mira. Si una te gusta más
que la grabada, cópiala a motor/sonidos/ con el mismo nombre.

  python3 motor/efectos.py                 → motor/sonidos/_sintetizados/*.wav
  python3 motor/efectos.py boom pop        → sólo esos

Cada efecto se usa por su nombre en el SFX de la pieza:
  ['boom', T.giro[0], 0.5]           [nombre, segundo, ganancia, tono?]
Los que tienen «ancla» (subida, redoble, cuenta-atras…) no empiezan en su
segundo: ACABAN o GOLPEAN en él. sonar-generico.py lo sabe por anclas.json.
"""
import json, pathlib, sys, wave
import numpy as np

SR = 44100
OUT = pathlib.Path(__file__).resolve().parent / "sonidos" / "_sintetizados"
rng = np.random.default_rng(7)

# ── utilidades ─────────────────────────────────────────────────────
T = lambda d: np.arange(int(d*SR))/SR
def lp(x, fc, o=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR); return np.fft.irfft(X/np.sqrt(1+(f/fc)**(2*o)), n=len(x))
def hp(x, fc, o=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR); return np.fft.irfft(X*(1-1/np.sqrt(1+(f/fc)**(2*o))), n=len(x))
def bp(x, lo, hi): return lp(hp(x, lo), hi)
def noise(d): return rng.standard_normal(int(d*SR))
def sweep(f0, f1, d, curva=1.0):
    t = T(d); f = f0*(f1/f0)**((t/d)**curva); return np.sin(2*np.pi*np.cumsum(f)/SR)
def exp_(d, tau): return np.exp(-T(d)/tau)
def ataque(x, ms=2.0):
    n = min(len(x), int(ms*SR/1000)); x = x.copy(); x[:n] *= np.linspace(0, 1, n); return x
def cola(x, ms=12.0):
    n = min(len(x), int(ms*SR/1000)); x = x.copy(); x[-n:] *= np.linspace(1, 0, n); return x
def reverb(x, seg=0.9, tau=0.28, mezcla=0.3):
    ir = noise(seg)*exp_(seg, tau); ir[:int(0.004*SR)] = 0
    n = len(x)+len(ir)
    y = np.fft.irfft(np.fft.rfft(x, n)*np.fft.rfft(ir, n), n)
    y = y/(np.abs(y).max()+1e-9)*np.abs(x).max()
    return np.concatenate([x, np.zeros(len(ir))]) + y*mezcla
def pon(buf, x, t, g=1.0):
    i = int(t*SR); n = min(len(x), len(buf)-i)
    if n > 0: buf[i:i+n] += x[:n]*g
def lienzo(d): return np.zeros(int(d*SR))
def sierra(f, d, fc=3000):
    t = T(d); y = np.zeros_like(t)
    for k in range(1, int(min(fc, SR*0.45)/f)+1): y += np.sin(2*np.pi*f*k*t)/k
    return y
def campanita(f, d, tau=0.35, parciales=((1, 1.0), (2.76, 0.5), (5.4, 0.25), (8.9, 0.1))):
    t = T(d); return sum(a*np.sin(2*np.pi*f*r*t)*np.exp(-t/(tau/(1+0.6*i))) for i, (r, a) in enumerate(parciales))
def click(f=2600, d=0.05, tau_n=0.0018, tau_p=0.009):
    t = T(d); return hp(noise(d), 2500)*np.exp(-t/tau_n)*0.6 + np.sin(2*np.pi*f*t)*np.exp(-t/tau_p)

# ── TRANSICIONES ───────────────────────────────────────────────────
def whoosh():
    d = 0.5; t = T(d); e = np.sin(np.pi*t/d)**1.6
    return bp(noise(d), 300, 3200)*e + sweep(400, 1400, d)*e*0.12
def whoosh_largo():
    d = 1.0; t = T(d); e = np.sin(np.pi*t/d)**1.4
    return bp(noise(d), 200, 2600)*e + sweep(250, 1100, d)*e*0.1
def barrido():
    d = 0.6; t = T(d); f = 520 + 980*(t/d)
    return (np.sin(2*np.pi*np.cumsum(f)/SR) + noise(d)*0.22)*np.sin(np.pi*t/d)**1.4
def swipe():
    d = 0.22; t = T(d)
    return hp(noise(d), 1500)*np.exp(-t/0.05)*np.minimum(1, t/0.004) + sweep(2200, 600, d)*np.exp(-t/0.06)*0.3
def subida():
    d = 1.6; t = T(d)
    return (sweep(180, 2600, d, 1.8)*0.35 + hp(noise(d), 600)*(0.4+0.6*t/d)*0.65)*(t/d)**2.2
def subida_larga():
    d = 3.0; t = T(d)
    return (sweep(120, 3200, d, 1.6)*0.3 + hp(noise(d), 400)*(0.3+0.7*t/d)*0.7)*(t/d)**2.4
def rebobinar():
    d = 1.2; t = T(d)
    y = (sweep(2400, 200, d)*0.4 + hp(noise(d), 800)*0.6)*np.exp(-t/0.35)
    return y[::-1]
def freno():
    """Parada de cinta: todo baja de tono hasta cero."""
    d = 0.85; t = T(d); k = (1-t/d)**1.4
    y = np.zeros_like(t)
    for f in (220, 330, 440): y += np.sin(2*np.pi*np.cumsum(f*k)/SR)/3
    return lp(y, 2500)*k**0.5 + bp(noise(d), 300, 1800)*k*0.15
def glitch():
    d = 0.45; y = lienzo(d); p = 0.0
    while p < d-0.02:
        largo = rng.uniform(0.012, 0.06); f = rng.choice([220, 440, 880, 1760])
        tt = T(largo); pon(y, np.sign(np.sin(2*np.pi*f*tt))*0.5 + hp(noise(largo), 2000)*0.5, p)
        p += largo + rng.uniform(0.0, 0.03)
    return lp(y, 6000)*np.sin(np.pi*T(len(y)/SR)/d)**0.3
def corte():
    d = 0.14; t = T(d)
    return click(3200, d, 0.0015, 0.006) + lp(noise(d), 2000)*np.exp(-t/0.02)*0.5

# ── GOLPES ─────────────────────────────────────────────────────────
def golpe():
    d = 0.58; t = T(d); f = 94*(48/94)**(t/d)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*5.6)
def impacto():
    d = 2.0; t = T(d); fr = 110*(32/110)**(np.minimum(t, 0.9)/0.9)
    return np.tanh((np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-t*2.0) + noise(d)*np.exp(-t*2.6)*0.35)*1.2)
def boom():
    """El boom grave con cola larga: el momento en que algo cae de golpe."""
    d = 1.4; t = T(d); f = 62*(36/62)**(np.minimum(t, 0.5)/0.5)
    y = np.tanh(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*2.2)*2.0) + lp(noise(d), 900)*np.exp(-t/0.05)*0.6
    return reverb(y, 1.4, 0.45, 0.45)
def bombo():
    d = 0.42; t = T(d); f = 47+(155-47)*np.exp(-t/0.055)
    return np.tanh((np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.115) + hp(noise(d), 1800)*np.exp(-t/0.0018)*0.45)*1.5)
def caida():
    """La caída de graves: el bajón, el «se acabó»."""
    d = 1.3; t = T(d)
    return np.tanh(sweep(240, 28, d, 0.7)*np.exp(-t*1.4)*1.8)
def estampido():
    d = 0.35; t = T(d)
    return lp(noise(d), 4000)*np.exp(-t/0.06) + np.sin(2*np.pi*70*t)*np.exp(-t/0.09)*0.8
def portazo():
    d = 0.5; t = T(d)
    y = lp(noise(d), 700)*np.exp(-t/0.10) + np.sin(2*np.pi*88*t)*np.exp(-t/0.14)*0.7
    return reverb(np.tanh(y*1.5), 0.5, 0.15, 0.25)

# ── INTERFAZ ───────────────────────────────────────────────────────
def tecla():
    return click(3100, 0.08, 0.0022, 0.011)
def teclado():
    y = lienzo(0.7); p = 0.0
    for i in range(7):
        pon(y, click(2600+rng.uniform(-500, 700), 0.06, 0.002, 0.009), p, 0.7+rng.uniform(0, 0.3)); p += rng.uniform(0.055, 0.1)
    return y
def clic():
    return click(1400, 0.035, 0.0012, 0.006)
def blip():
    d = 0.07; t = T(d)
    return (np.sin(2*np.pi*1180*t) + 0.4*np.sin(2*np.pi*2360*t))*np.exp(-t/0.02)*np.minimum(1, t/0.002)
def notificacion():
    y = lienzo(0.5)
    for i, f in enumerate((880, 1320)):
        d = 0.16; t = T(d); pon(y, (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t))*np.exp(-t/0.06)*np.minimum(1, t/0.003), i*0.1)
    return y
def mensaje():
    y = lienzo(0.55)
    for i, f in enumerate((660, 880, 1108)):
        d = 0.25; t = T(d); pon(y, (np.sin(2*np.pi*f*t)+0.25*np.sin(2*np.pi*3*f*t)*np.exp(-t*20))*np.exp(-t/0.09)*np.minimum(1, t/0.003), i*0.08, 0.8)
    return y
def pop():
    d = 0.12; t = T(d)
    return sweep(900, 280, d, 0.6)*np.exp(-t/0.03)*np.minimum(1, t/0.0015)
def burbuja():
    d = 0.16; t = T(d)
    return sweep(320, 1400, d, 1.4)*np.sin(np.pi*t/d)**1.2
def toggle():
    y = lienzo(0.12); pon(y, click(1800, 0.04, 0.001, 0.005), 0); pon(y, click(1200, 0.04, 0.001, 0.006), 0.045, 0.8); return y
def error():
    d = 0.32; t = T(d)
    sq = np.sign(np.sin(2*np.pi*110*t)) + 0.5*np.sign(np.sin(2*np.pi*165*t))
    return np.convolve(sq, np.ones(40)/40, mode="same")*np.sin(np.pi*t/d)**0.6
def acierto():
    y = lienzo(0.6)
    for t0, f in ((0.0, 660), (0.14, 990)):
        d = 0.45; t = T(d); pon(y, (np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*2*f*t))*np.exp(-t*7)*np.minimum(1, t/0.004), t0, 0.7)
    return y
def campana():
    return campanita(880, 1.6, 0.6)*0.5
def caja():
    """La caja registradora: el ka-ching y el cajón."""
    y = lienzo(0.95)
    pon(y, campanita(2900, 0.5, 0.25)*0.6, 0.0); pon(y, campanita(3400, 0.45, 0.22)*0.5, 0.07)
    pon(y, hp(noise(0.25), 3000)*exp_(0.25, 0.03)*0.35, 0.0)
    pon(y, lp(noise(0.3), 400)*exp_(0.3, 0.05)*0.8 + np.sin(2*np.pi*120*T(0.3))*exp_(0.3, 0.08)*0.5, 0.26)
    return y
def monedas():
    y = lienzo(0.75); p = 0.0
    for i in range(6):
        f = rng.uniform(3000, 5400)
        pon(y, campanita(f, 0.28, 0.08, ((1, 1.0), (1.41, 0.6), (2.3, 0.35), (3.7, 0.15)))*0.6, p); p += rng.uniform(0.045, 0.085)
    return y
def timbre():
    y = lienzo(1.3); pon(y, campanita(659, 0.8, 0.35)*0.6, 0.0); pon(y, campanita(523, 1.0, 0.45)*0.6, 0.38); return y
def alarma():
    d = 0.7; t = T(d); tono = lp(np.sign(np.sin(2*np.pi*880*t)), 4000)
    puls = (np.sin(2*np.pi*8*t) > 0).astype(float); puls = np.convolve(puls, np.ones(60)/60, mode="same")
    return tono*puls*0.7
def camara():
    y = lienzo(0.28)
    pon(y, click(1600, 0.05, 0.0015, 0.008) + lp(noise(0.05), 2500)*exp_(0.05, 0.01)*0.4, 0.0)
    pon(y, click(2200, 0.06, 0.0015, 0.007) + lp(noise(0.06), 3000)*exp_(0.06, 0.012)*0.5, 0.09, 0.9)
    return y
def cuenta_atras():
    """Tres pitidos y el largo: el largo cae en el segundo declarado (ancla 1,5 s)."""
    y = lienzo(1.95)
    for i in range(3):
        d = 0.09; t = T(d); pon(y, np.sin(2*np.pi*1000*t)*np.sin(np.pi*t/d)**0.4, i*0.5, 0.7)
    d = 0.42; t = T(d); pon(y, (np.sin(2*np.pi*1500*t)+0.3*np.sin(2*np.pi*3000*t))*np.sin(np.pi*t/d)**0.3, 1.5, 0.8)
    return y

# ── DRAMÁTICOS ─────────────────────────────────────────────────────
def latido():
    d = 0.55; n = int(d*SR); t = T(d); y = np.zeros(n)
    for t0, g in ((0.0, 1.0), (0.16, 0.65)):
        i = int(t0*SR); tt = t[:n-i]; f = 140*(45/140)**(np.minimum(tt, 0.12)/0.12)
        y[i:] += np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*14)*g
    return np.tanh(y*1.4)
def reloj():
    y = lienzo(2.0)
    for i in range(4): pon(y, click(2600 if i % 2 == 0 else 1900, 0.06, 0.002, 0.012), i*0.5, 0.8 if i % 2 == 0 else 0.6)
    return y
def dun_dun_dun():
    """Tres golpes de metales que bajan. El drama, en broma o en serio."""
    y = lienzo(2.6)
    for i, (t0, f, d) in enumerate(((0.0, 146.8, 0.42), (0.45, 138.6, 0.42), (0.9, 130.8, 1.6))):
        t = T(d); s = (sierra(f, d, 2400) + sierra(f*1.005, d, 2400)*0.7 + sierra(f/2, d, 1200)*0.6)
        pon(y, np.tanh(lp(s, 900)*1.4)*np.minimum(1, t/0.02)*np.exp(-t/(0.3 if i < 2 else 0.9)), t0)
    return reverb(y, 1.2, 0.4, 0.35)
def tension():
    d = 2.6; t = T(d); k = (t/d)**1.6
    y = (sierra(55, d, 1200) + sierra(55.4, d, 1200) + sierra(82.5, d, 1200)*0.5)/2.5*k + hp(noise(d), 1200)*k**2*0.35
    return lp(np.tanh(y*1.4), 3000)
def revelacion():
    """La revelación: un arpegio que sube y brilla. Para el dato que lo cambia todo."""
    y = lienzo(1.8); notas = [523, 659, 784, 1047, 1319, 1568, 2093, 2637]
    for i, f in enumerate(notas): pon(y, campanita(f, 1.0, 0.4, ((1, 1.0), (2, 0.3), (3, 0.12)))*0.35, i*0.075)
    pon(y, hp(noise(0.9), 3000)*(T(0.9)/0.9)**2*0.25, 0.0)
    return reverb(y, 1.0, 0.35, 0.4)
def suspenso():
    d = 0.75; t = T(d); trem = 0.55+0.45*np.sin(2*np.pi*13*t)
    y = (sierra(440, d, 3500) + sierra(659, d, 3500)*0.7 + sierra(220, d, 2000)*0.5)*trem
    return bp(y, 180, 3200)*np.minimum(1, t/0.03)*np.where(t < d-0.05, 1, 0)*0.5
def disco_rayado():
    """El vinilo que se frena: el «espera, ¿qué?»."""
    d = 0.5; t = T(d); vaiven = np.sin(2*np.pi*4.2*t)
    f = 700*2**(vaiven*1.4)
    y = bp(noise(d), 700, 5000)*(0.6+0.4*np.abs(vaiven)) + np.sin(2*np.pi*np.cumsum(f)/SR)*0.3
    return y*np.sin(np.pi*t/d)**0.5
def silbato():
    """El silbato que baja: la caída de dibujos animados, el fracaso con gracia."""
    d = 0.8; t = T(d); vib = 1+0.02*np.sin(2*np.pi*6*t)
    return sweep(1900, 480, d, 0.9)*vib*np.sin(np.pi*t/d)**0.4*0.8 + bp(noise(d), 1500, 5000)*0.08*np.sin(np.pi*t/d)
def muelle():
    d = 0.7; t = T(d); wob = 1+0.35*np.sin(2*np.pi*(14-10*t/d)*t)*np.exp(-t*2)
    return np.sin(2*np.pi*np.cumsum(230*wob)/SR)*np.exp(-t*4)*np.minimum(1, t/0.003)
def aplauso():
    y = lienzo(2.4)
    for i in range(160):
        p = rng.uniform(0, 2.2); dens = np.sin(np.pi*min(1, p/1.8))**0.5 if p < 1.8 else max(0, 1-(p-1.8)/0.5)
        if rng.uniform() > dens: continue
        d = 0.03; pon(y, bp(noise(d), 900, 6000)*exp_(d, 0.008), p, rng.uniform(0.3, 1.0))
    return reverb(y, 0.7, 0.25, 0.3)
def redoble():
    """El redoble de tambor y el platillo: el platillo cae en el segundo declarado (ancla 1,45 s)."""
    y = lienzo(2.6); p = 0.0
    while p < 1.42:
        d = 0.12; t = T(d); pon(y, (hp(lp(noise(d), 6000), 900)*np.exp(-t/0.03) + np.sin(2*np.pi*190*t)*np.exp(-t/0.04)*0.4), p, 0.35+0.65*(p/1.42)); p += 0.046
    d = 1.1; t = T(d); pon(y, hp(noise(d), 2500)*np.exp(-t/0.35)*0.9 + lp(noise(d), 500)*np.exp(-t/0.08)*0.8, 1.45)
    return y
def grillo():
    """Los grillos: el silencio incómodo."""
    y = lienzo(1.6)
    for i in range(4):
        d = 0.13; t = T(d); puls = (np.sin(2*np.pi*42*t) > 0.2).astype(float)
        pon(y, np.sin(2*np.pi*4300*t)*puls*np.sin(np.pi*t/d)**0.5, i*0.38, 0.5)
    return lp(y, 8000)
def zap():
    d = 0.2; t = T(d)
    return np.sign(sweep(2400, 180, d, 0.8))*0.4*np.exp(-t/0.07) + sweep(2400, 180, d, 0.8)*np.exp(-t/0.09)*0.5
def brillo():
    d = 0.42; t = T(d)
    return (np.sin(2*np.pi*1080*t)+0.5*np.sin(2*np.pi*1620*t))*np.exp(-t*11)
def fiesta():
    """Pops y brillo: la celebración."""
    y = lienzo(1.2)
    for i in range(7): pon(y, pop(), rng.uniform(0, 0.5), rng.uniform(0.5, 1.0))
    pon(y, revelacion()[:int(1.0*SR)], 0.1, 0.5)
    return y
def cristal_roto():
    d = 0.9; t = T(d); y = hp(noise(d), 2500)*np.exp(-t/0.05)*0.8
    for i in range(7):
        f = rng.uniform(2800, 8500); tau = rng.uniform(0.08, 0.3); t0 = rng.uniform(0, 0.25)
        pon(y, campanita(f, 0.5, tau, ((1, 1.0), (1.37, 0.5), (2.1, 0.2)))*0.3, t0)
    for i in range(10): pon(y, click(rng.uniform(3000, 6000), 0.03, 0.001, 0.004), rng.uniform(0.15, 0.7), 0.4)
    return y

# ── COTIDIANO ──────────────────────────────────────────────────────
def loza():
    d = 0.28; t = T(d)
    return noise(d)*np.exp(-t*40)*0.5 + np.sin(2*np.pi*760*t)*np.exp(-t*26) + np.sin(2*np.pi*1900*t)*np.exp(-t*44)*0.4
def vaso():
    return campanita(2450, 0.5, 0.22, ((1, 1.0), (1.59, 0.5), (2.2, 0.3), (2.9, 0.15)))*0.6 + click(2450, 0.5, 0.001, 0.004)*0.3
def brindis():
    y = lienzo(0.75); pon(y, vaso(), 0.0); pon(y, campanita(2650, 0.5, 0.24, ((1, 1.0), (1.59, 0.5), (2.2, 0.3)))*0.55, 0.09); return y
def roce():
    d = 0.42; t = T(d); n = np.convolve(noise(d), np.ones(90)/90, mode="same")
    return n*np.exp(-t*7)*np.sin(np.pi*np.clip(t/d, 0, 1))**0.5
def hilo():
    d = 0.32; t = T(d); f = 460*(1020/460)**(t/d)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*t/d)**1.6
def papel():
    d = 0.3; t = T(d); e = np.sin(np.pi*t/d)**0.8
    return bp(noise(d), 1200, 7000)*e*0.7 + hp(noise(d), 4000)*(rng.uniform(size=len(t)) > 0.97)*e*0.5
def boligrafo():
    y = lienzo(0.16); pon(y, click(1900, 0.05, 0.001, 0.006), 0.0); pon(y, click(1500, 0.05, 0.001, 0.006), 0.085, 0.7); return y
def sello():
    d = 0.35; t = T(d)
    return lp(noise(d), 600)*np.exp(-t/0.05) + np.sin(2*np.pi*110*t)*np.exp(-t/0.07)*0.6 + hp(noise(d), 3000)*np.exp(-t/0.006)*0.4

# ── el catálogo: nombre → (función, grupo, para qué, ancla en segundos) ──
CAT = {
 # transiciones
 "whoosh":       (whoosh, "transiciones", "algo sale disparado o se envía; un cambio de plano", 0),
 "whoosh-largo": (whoosh_largo, "transiciones", "un cambio de plano grande, la cámara que viaja", 0),
 "barrido":      (barrido, "transiciones", "una hoja que sube, un plano que entra", 0),
 "swipe":        (swipe, "transiciones", "pasar una tarjeta, un gesto rápido", 0),
 "subida":       (subida, "transiciones", "anuncia lo que viene; acaba en su segundo", "fin"),
 "subida-larga": (subida_larga, "transiciones", "tres segundos de subida antes del giro grande; acaba en su segundo", "fin"),
 "rebobinar":    (rebobinar, "transiciones", "volver atrás, deshacer; acaba en su segundo", "fin"),
 "freno":        (freno, "transiciones", "parada de cinta: se para todo, el «espera»", 0),
 "glitch":       (glitch, "transiciones", "fallo digital, corte brusco, lo que se rompe", 0),
 "corte":        (corte, "transiciones", "el corte seco entre dos planos", 0),
 # golpes
 "golpe":        (golpe, "golpes", "algo con peso que aterriza: una tarjeta, el móvil, el cierre", 0),
 "impacto":      (impacto, "golpes", "el golpe con cola grave: el giro, la caída", 0),
 "boom":         (boom, "golpes", "el boom grave con cola larga: el momento en que algo cae de golpe, el remate cómico o serio", 0),
 "bombo":        (bombo, "golpes", "un bombo seco a compás; para marcar cortes", 0),
 "caida":        (caida, "golpes", "la caída de graves: el bajón, el «se acabó»", 0),
 "estampido":    (estampido, "golpes", "un golpe corto y seco: algo se estampa", 0),
 "portazo":      (portazo, "golpes", "una puerta, algo que se cierra de golpe", 0),
 # interfaz
 "tecla":        (tecla, "interfaz", "un toque en la pantalla", 0),
 "teclado":      (teclado, "interfaz", "escribir: una ráfaga de teclas", 0),
 "clic":         (clic, "interfaz", "un clic de ratón, un botón pequeño", 0),
 "blip":         (blip, "interfaz", "un aviso corto, algo que se recibe", 0),
 "notificacion": (notificacion, "interfaz", "llega una notificación", 0),
 "mensaje":      (mensaje, "interfaz", "llega un mensaje; tres notas que suben", 0),
 "pop":          (pop, "interfaz", "algo aparece: una burbuja, un icono, un chip", 0),
 "burbuja":      (burbuja, "interfaz", "algo sube o se infla", 0),
 "toggle":       (toggle, "interfaz", "un interruptor, activar algo", 0),
 "error":        (error, "interfaz", "lo que está mal, lo que se tacha", 0),
 "acierto":      (acierto, "interfaz", "lo que sale bien, lo que se resuelve", 0),
 "campana":      (campana, "interfaz", "algo se revela, un dato que suena a verdad", 0),
 "caja":         (caja, "interfaz", "la caja registradora: dinero, pagar, cobrar", 0),
 "monedas":      (monedas, "interfaz", "monedas que caen: ahorro, céntimos, propina", 0),
 "timbre":       (timbre, "interfaz", "ding-dong: alguien llega, un pedido", 0),
 "alarma":       (alarma, "interfaz", "una alarma, un aviso urgente", 0),
 "camara":       (camara, "interfaz", "una foto: el ticket, la captura", 0),
 "cuenta-atras": (cuenta_atras, "interfaz", "tres pitidos y el largo; el largo cae en su segundo", 1.5),
 # dramáticos
 "latido":       (latido, "dramaticos", "lub-dub: la espera, el silencio que incomoda", 0),
 "reloj":        (reloj, "dramaticos", "tic-tac, cuatro tics en dos segundos: el tiempo que corre", 0),
 "dun-dun-dun":  (dun_dun_dun, "dramaticos", "tres golpes de metales que bajan: el drama, en broma o en serio", 0),
 "tension":      (tension, "dramaticos", "un drone que sube y se corta: algo va a pasar", 0),
 "revelacion":   (revelacion, "dramaticos", "un arpegio que sube y brilla: el dato que lo cambia todo", 0),
 "suspenso":     (suspenso, "dramaticos", "un golpe de cuerdas en trémolo: el sobresalto", 0),
 "disco-rayado": (disco_rayado, "dramaticos", "el vinilo que se frena: «espera, ¿qué?»", 0),
 "silbato":      (silbato, "dramaticos", "el silbato que baja: la caída de dibujos, el fracaso con gracia", 0),
 "muelle":       (muelle, "dramaticos", "boing: algo rebota, lo cómico", 0),
 "aplauso":      (aplauso, "dramaticos", "aplausos: el logro, el final", 0),
 "redoble":      (redoble, "dramaticos", "redoble y platillo: el platillo cae en su segundo (la revelación)", 1.45),
 "grillo":       (grillo, "dramaticos", "grillos: el silencio incómodo, nadie contesta", 0),
 "zap":          (zap, "dramaticos", "un láser, algo que desaparece de golpe", 0),
 "brillo":       (brillo, "dramaticos", "algo se enciende, una cifra que remata", 0),
 "fiesta":       (fiesta, "dramaticos", "pops y brillo: la celebración", 0),
 "cristal-roto": (cristal_roto, "dramaticos", "algo se rompe de verdad", 0),
 # cotidiano
 "loza":         (loza, "cotidiano", "vajilla, mesa, bar", 0),
 "vaso":         (vaso, "cotidiano", "un vaso, una copa que se posa", 0),
 "brindis":      (brindis, "cotidiano", "dos copas que chocan", 0),
 "roce":         (roce, "cotidiano", "papel, tela, algo que se arrastra", 0),
 "hilo":         (hilo, "cotidiano", "una línea que se traza, algo que conecta", 0),
 "papel":        (papel, "cotidiano", "pasar una página, un ticket que se despliega", 0),
 "boligrafo":    (boligrafo, "cotidiano", "un bolígrafo: apuntar, firmar", 0),
 "sello":        (sello, "cotidiano", "un sello que cae: aprobado, pagado", 0),
}
GRUPOS = {"transiciones": "Transiciones", "golpes": "Golpes", "interfaz": "Interfaz", "dramaticos": "Dramáticos", "cotidiano": "Cotidiano"}

def escribe(path, y):
    y = cola(ataque(y, 0.8), 10); pk = np.abs(y).max(); y = y/pk*0.89 if pk else y
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1)*32767).astype("<i2").tobytes())
    return len(y)/SR

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    pedidos = [a for a in sys.argv[1:] if a in CAT] or list(CAT)
    anclas = {}; filas = {}
    for nombre in pedidos:
        fn, grupo, para, ancla = CAT[nombre]
        dur = escribe(OUT/f"{nombre}.wav", fn())
        a = dur if ancla == "fin" else float(ancla)
        if a: anclas[nombre] = round(a, 3)
        filas.setdefault(grupo, []).append((nombre, dur, para, a))
        print(f"  {nombre:14s} {dur:5.2f} s{'  · ancla ' + str(round(a, 2)) + ' s' if a else ''}")
    if len(pedidos) == len(CAT):
        (OUT/"anclas.json").write_text(json.dumps(anclas, indent=1))
        md = ["# Los efectos de sonido", "",
              f"{len(CAT)} efectos sintetizados con numpy. NO son los del motor: los que usa",
              "son grabaciones y están en `motor/sonidos/` (INDICE.md). Éstos son variantes; si",
              "alguna te gusta más, cópiala arriba con el mismo nombre. Se usan por su nombre en el",
              "`SFX` de la pieza: `['boom', T.giro[0], 0.5]` → `[nombre, segundo, ganancia, tono?]`.",
              "El cuarto valor cambia el tono: >1 agudiza y acorta, <1 agrava y alarga.", "",
              "**Ancla**: los que la tienen no empiezan en su segundo, acaban o golpean en él",
              "(`subida` acaba, `redoble` da el platillo, `cuenta-atras` da el pitido largo).", "",
              "Un golpe visual sin su efecto es medio golpe; y un efecto sin golpe visual es ruido.",
              "Uno cada 0,7 s es lo medido en la pieza de referencia: no tengas miedo de poner muchos,",
              "pero que cada uno tenga su porqué en pantalla.", ""]
        for g, titulo in GRUPOS.items():
            md += [f"## {titulo}", "", "| Efecto | Dura | Para qué |", "|---|---|---|"]
            for nombre, dur, para, a in filas.get(g, []):
                md.append(f"| `{nombre}` | {dur:.2f} s{' · ancla ' + format(a, '.2f') + ' s' if a else ''} | {para} |")
            md.append("")
        (OUT/"INDICE.md").write_text("\n".join(md))
        print(f"✓ {len(pedidos)} efectos en {OUT} · INDICE.md · anclas.json")
