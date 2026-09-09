"""Sonido para cualquier pieza, desde lo que declara el propio HTML.

  python3 ../../motor/sonar-generico.py salida/pieza.mp4 audios/pieza-seco.mp3
  python3 ../../motor/sonar-generico.py salida/pieza.mp4                        (sin voz)
  python3 ../../motor/sonar-generico.py salida/pieza.mp4 audios/v.mp3 tension-reloj       (una cama, toda la pieza)
  python3 ../../motor/sonar-generico.py salida/pieza.mp4 audios/v.mp3 tension-reloj 0.15

Come del `.marcas.json` que escribe shoot-par.mjs al lado del mp4:

  SFX     [tipo, segundo, ganancia, tono?]                  los efectos
  MUSICA  [cama, desde, nivel?, transicion?, desdeCama?]    la música POR TRAMOS

La música va por tramos: cada entrada arranca una cama en `desde` y dura
hasta la siguiente (o hasta el final). `cama` es un nombre del catálogo
(musica/INDICE.md) o una ruta a un mp3/wav. `nivel` por defecto 0,15 (las de
energía, 0,18). `transicion` dice cómo se entra en esa cama:
  fundido   cruce de 1,2 s con la anterior (por defecto)
  sube      una subida de 1,6 s que acaba justo en `desde`, y cruce corto
  corte     subida + golpe en `desde`; la anterior se corta en seco. El giro.
`desdeCama` = segundo de la cama por el que empezar (p. ej. 25 en emocion-amanecer).
La cama `silencio` es un tramo sin música a propósito: el contraste antes del golpe.
Si el HTML no declara MUSICA, vale el tercer argumento como cama única.

Musica: las 11 grabadas de musica/pixabay/ y las 25 sintetizadas de musica/largos/.
Efectos: los 74 de motor/sonidos/ (INDICE.md), por nombre; si taller/<marca>/sonidos/
tiene uno con el mismo nombre (p. ej. generado con ElevenLabs), manda el de la marca. El cuarto valor cambia
el tono (>1 agudiza y acorta). Los que tienen ancla —subida, redoble, cuenta-atras…—
no empiezan en su segundo: acaban o golpean en él (anclas.json).
"""
import json, pathlib, subprocess, sys, tempfile
import numpy as np

SR = 44100
AQUI = pathlib.Path(__file__).resolve().parent
# dónde están los efectos y la música: al lado del script (el pack), o en la skill global

HOME = pathlib.Path.home()
RAICES_SONIDOS = [AQUI / "sonidos"]
RAICES_MUSICA = [AQUI.parent / "musica" / "largos", AQUI.parent / "musica" / "pixabay"]
# red de seguridad: si algún día falta un .wav con ese nombre, suena el pariente
ALIAS = {"abrir": "swipe", "datos": "blip", "dinero": "monedas", "engranaje": "reloj", "seleccionar": "toggle", "camara": "clic"}
S = next((c for c in RAICES_SONIDOS if c.is_dir()), RAICES_SONIDOS[0])          # sólo para el aviso de «no hay efectos»
rnd = np.random.default_rng(3)

def carga(r):
    raw = subprocess.run(["ffmpeg","-v","error","-i",str(r),"-f","f32le","-ac","1",
                          "-ar",str(SR),"-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)

def recorta(x, ini=0, largo=None, fade=20):
    a = int(ini*SR/1000); b = len(x) if largo is None else a+int(largo*SR/1000)
    y = x[a:min(b,len(x))].copy(); n = int(fade*SR/1000)
    if 0 < n < len(y): y[-n:] *= np.linspace(1,0,n)
    pk = np.abs(y).max()
    return y/pk if pk else y

def tono(x,k):
    return np.interp(np.linspace(0,len(x)-1,int(len(x)/k)), np.arange(len(x)), x)

ANCLAS = {}
def carga_anclas(carpetas):
    """Los anclas.json de todas las carpetas; las primeras (la marca) mandan sobre las últimas (el motor)."""
    for c in reversed(carpetas):
        a = c/"anclas.json"
        if a.exists(): ANCLAS.update(json.loads(a.read_text()))
_efectos = {}
CARPETAS = []      # dónde se buscan los efectos, en orden: los de la marca mandan sobre los del motor
def ruta_efecto(nombre):
    for c in CARPETAS:
        for ext in (".mp3", ".wav"):
            r = c/f"{nombre}{ext}"
            if r.exists(): return r
    return None
def hay_efectos():
    return {x.stem for c in CARPETAS for x in list(c.glob("*.wav"))+list(c.glob("*.mp3")) if not x.stem.startswith("DEMO")}
def efecto(nombre, k=1.0):
    """Un efecto por su nombre: primero taller/<marca>/sonidos/, luego motor/sonidos/. k cambia el tono."""
    if nombre not in _efectos:
        r = ruta_efecto(nombre)
        if r is None and nombre in ALIAS: r = ruta_efecto(ALIAS[nombre])
        if r is None:
            hay = sorted(hay_efectos())
            sys.exit(f"el efecto «{nombre}» no existe · los que hay ({len(hay)}): {', '.join(hay) or 'ninguno · falta motor/sonidos/: vuelve a descomprimir el zip'}")
        x = carga(r); pk = np.abs(x).max(); _efectos[nombre] = x/pk if pk else x
    x = _efectos[nombre]
    return tono(x, 1/max(k, 0.2)) if k != 1.0 else x
def ancla(nombre, k=1.0):
    return ANCLAS.get(nombre, 0.0)/max(k, 0.2)

def pon(buf,x,t,g):
    i = int(t*SR)
    if i < 0: x = x[-i:]; i = 0
    n = min(len(x), len(buf)-i)
    if n > 0: buf[i:i+n] += x[:n]*g

# ── la música por tramos ────────────────────────────────────────────
def cama_ruta(nombre):
    p = pathlib.Path(str(nombre))
    if p.suffix and p.exists(): return p
    for raiz in RAICES_MUSICA:
        for cand in (raiz/f"{nombre}-largo.mp3", raiz/f"{nombre}.mp3", raiz/f"{nombre}.wav"):
            if cand.exists(): return cand
    hay = sorted({x.stem.replace("-largo","") for r in RAICES_MUSICA if r.is_dir() for x in r.glob("*.mp3")})
    sys.exit(f"no encuentro la cama «{nombre}» · las que hay: {', '.join(hay) or 'ninguna (bash musica/generar.sh)'}")

_cache = {}
def cama_audio(nombre):
    r = cama_ruta(nombre)
    if r not in _cache:
        x = carga(r); pk = np.abs(x).max(); _cache[r] = x/pk if pk else x
    return _cache[r]

def rampa(n, sube=True):
    if n <= 0: return np.zeros(0)
    r = np.sin(np.linspace(0, np.pi/2, n))**2          # cruce a potencia constante
    return r if sube else r[::-1]

def monta_musica(tramos, n_total, fin_s):
    """Suma las camas en su tramo con sus fundidos, y devuelve (música, efectos de transición)."""
    mus = np.zeros(n_total); ef = np.zeros(n_total); resumen = []
    T = []
    for i, tr in enumerate(tramos):
        cama = tr[0]; desde = float(tr[1])
        nivel = float(tr[2]) if len(tr) > 2 and tr[2] is not None else (0.18 if str(cama).startswith("energia") else 0.15)
        trans = (tr[3] if len(tr) > 3 and tr[3] else ("fundido" if i else "entra"))
        off = float(tr[4]) if len(tr) > 4 and tr[4] else 0.0
        T.append((cama, desde, nivel, trans, off))
    for i, (cama, desde, nivel, trans, off) in enumerate(T):
        hasta = T[i+1][1] if i+1 < len(T) else fin_s
        sig = T[i+1][3] if i+1 < len(T) else "fin"
        if str(cama) == "silencio":                       # un tramo sin música, a propósito
            resumen.append(f"{desde:5.1f}s → {hasta:5.1f}s  silencio"); continue
        if i+1 < len(T) and str(T[i+1][0]) == "silencio": sig = "silencio"
        # cómo entra ésta y cómo sale (la salida la decide la transición de la SIGUIENTE)
        ent = {"entra":0.6, "fundido":1.2, "sube":0.35, "corte":0.0}[trans]
        sal = {"fundido":1.2, "sube":0.5, "corte":0.06, "fin":1.2, "silencio":0.3}[sig]
        a = desde - (ent/2 if trans == "fundido" else 0.0)
        b = hasta + (sal/2 if sig == "fundido" else 0.0)
        a = max(0.0, a); b = min(fin_s, b)
        ia, ib = int(a*SR), int(b*SR); n = ib - ia
        if n <= 0: continue
        x = cama_audio(cama); io = int(off*SR)
        seg = x[io:io+n]
        if len(seg) < n: seg = np.pad(seg, (0, n-len(seg)))
        seg = seg.copy()
        ne, ns = int(ent*SR), int(sal*SR)
        if ne > 0: seg[:ne] *= rampa(ne, True)
        if ns > 0: seg[-ns:] *= rampa(ns, False)
        mus[ia:ib] += seg*nivel
        if trans in ("sube", "corte"): pon(ef, efecto("subida"), desde-ancla("subida"), 0.30)
        if trans == "corte": pon(ef, efecto("impacto"), desde, 0.45)
        resumen.append(f"{desde:5.1f}s → {hasta:5.1f}s  {cama}  ({nivel:.2f}{', '+trans if i else ''}{', desde '+str(off)+'s' if off else ''})")
    return mus, ef, resumen

# ── la pieza ────────────────────────────────────────────────────────
if len(sys.argv) < 2:
    sys.exit("uso: sonar-generico.py <pieza.mp4> [voz.mp3] [cama|musica.mp3] [nivel]")
video = pathlib.Path(sys.argv[1]).resolve()
voz_src = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv) > 2 and sys.argv[2] not in ("-", "") else None
mus_arg = sys.argv[3] if len(sys.argv) > 3 else None
mus_niv = float(sys.argv[4]) if len(sys.argv) > 4 else None
marcas_json = pathlib.Path(str(video)[:-4] + ".marcas.json")
if not marcas_json.exists():
    sys.exit(f"falta {marcas_json.name} al lado del mp4: lo escribe shoot-par.mjs al empezar el render")
m = json.loads(marcas_json.read_text())
dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
      "-of","default=nw=1:nk=1",str(video)], capture_output=True, text=True, check=True).stdout)
N = int(dur*SR)
buf = np.zeros(N)

if not m.get("SFX"):
    sys.exit("la pieza no declara SFX en window.MARCAS · ver referencias/voz.md")
# los efectos de la marca (taller/<marca>/sonidos/) tapan a los del motor con el mismo nombre
_vistas = set()
CARPETAS[:] = [c for c in [video.parent.parent/"sonidos"] + RAICES_SONIDOS if c.is_dir() and not (c.resolve() in _vistas or _vistas.add(c.resolve()))]
carga_anclas(CARPETAS)
HAY = hay_efectos()
if not HAY:
    sys.exit("no hay efectos en motor/sonidos/ · la descarga está a medias: vuelve a descomprimir el zip")
malos = sorted({ev[0] for ev in m["SFX"] if ev[0] not in HAY and ALIAS.get(ev[0]) not in HAY})
if malos:
    sys.exit(f"efectos que no existen: {', '.join(malos)} · los que hay: {', '.join(sorted(HAY))}")

for ev in m["SFX"]:
    tipo, t0, g = ev[0], float(ev[1]), float(ev[2])
    k = float(ev[3]) if len(ev) > 3 else 1.0
    pon(buf, efecto(tipo, k), t0 - ancla(tipo, k), g)

tramos = m.get("MUSICA") or ([[mus_arg, 0, mus_niv]] if mus_arg else [])
mus, ef_mus, resumen = (monta_musica(tramos, N, dur) if tramos else (np.zeros(N), np.zeros(N), []))

if voz_src is None:
    # pieza sin voz: los efectos van solos y mandan, sin agacharse ante nadie
    seco = buf*1.7 + ef_mus*1.5 + mus*2.2
    mez = np.tanh(seco)*0.88
else:
    voz = carga(voz_src)
    voz = np.pad(voz, (0, max(0, N-len(voz))))[:N]
    pk = np.abs(voz).max()
    voz = voz/pk*0.92 if pk else voz
    env = np.convolve(np.abs(voz), np.ones(int(0.06*SR))/int(0.06*SR), mode="same")
    env = env/(env.max() or 1)
    duck = 1 - 0.49*np.clip(env*4.0, 0, 1)            # la música se aparta donde se habla
    seco = voz + buf*0.42*(1-0.62*np.clip(env*4.0,0,1)) + ef_mus*0.9 + mus*duck
    mez = np.tanh(seco*1.25)*0.90

print(f"{len(mez)/SR:.2f}s · {len(m['SFX'])} efectos · pico {np.abs(mez).max():.3f}")
for r in resumen: print("  música  " + r)
if not resumen: print("  sin música")

wav = pathlib.Path(tempfile.gettempdir())/(video.stem+".wav")
subprocess.run(["ffmpeg","-v","error","-y","-f","f32le","-ar",str(SR),"-ac","1","-i","-",str(wav)],
               input=mez.astype(np.float32).tobytes(), check=True)
out = video.with_name(video.stem+"-son.mp4")
subprocess.run(["ffmpeg","-v","error","-y","-i",str(video),"-i",str(wav),"-c:v","copy","-c:a","aac",
                "-b:a","192k","-ar","44100","-movflags","+faststart","-shortest",str(out)], check=True)
wav.unlink(); print("✓", out)
