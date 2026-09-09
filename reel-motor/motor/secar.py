# -*- coding: utf-8 -*-
"""Aprieta los silencios de una toma única y recoloca sus marcas sin volver a pagar Scribe.

   Desde taller/<marca>/ :  python3 ../../motor/secar.py <pieza> [hueco]
   (el hueco que se deja entre frases; 0,30 s por defecto)

La toma de ElevenLabs respira de más entre frases y eso frena el vídeo (sonido/voz.md).
Se cortan los silencios **por dentro del propio silencio** —los cortes en silencio no
se oyen— y cada tiempo de marcas.json se desplaza por lo que se ha quitado antes de él,
que es exacto: no hace falta transcribir otra vez.
"""
import json, pathlib, re, subprocess, sys

vid   = sys.argv[1]
HUECO = float(sys.argv[2]) if len(sys.argv) > 2 else 0.30
ENTRADA = 0.10                      # el silencio de cabecera se deja en una décima
d   = pathlib.Path("audios")/vid
src = d/"toma-crudo.mp3"
if not src.exists(): (d/"toma.mp3").rename(src)

dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
      "-of","default=nw=1:nk=1",str(src)],capture_output=True,text=True).stdout)
log = subprocess.run(["ffmpeg","-v","info","-i",str(src),"-af",
      "silencedetect=noise=-34dB:d=0.12","-f","null","-"],capture_output=True,text=True).stderr
sil = []
ini = None
for m in re.finditer(r"silence_(start|end): (-?[\d.]+)", log):
    if m.group(1) == "start": ini = float(m.group(2))
    elif ini is not None: sil.append((ini, float(m.group(2)))); ini = None
if ini is not None: sil.append((ini, dur))

cortes = []                                            # (desde, hasta) de lo que se quita
for a, b in sil:
    tope = ENTRADA if a <= 0.02 else HUECO
    if b - a <= tope + 0.02: continue
    sobra = (b - a) - tope
    if a <= 0.02: cortes.append((0.0, sobra))          # la cabecera se quita por delante
    else:
        c = a + tope/2
        cortes.append((round(c,3), round(c+sobra,3)))
if not cortes:
    print("nada que apretar"); sys.exit(0)

# los trozos que se quedan
trozos, pos = [], 0.0
for a, b in cortes:
    if a > pos: trozos.append((pos, a))
    pos = b
if pos < dur: trozos.append((pos, dur))

filtro = ";".join(f"[0]atrim=start={a}:end={b},asetpts=N/SR/TB[t{i}]" for i,(a,b) in enumerate(trozos))
filtro += ";" + "".join(f"[t{i}]" for i in range(len(trozos))) + f"concat=n={len(trozos)}:v=0:a=1[out]"
subprocess.run(["ffmpeg","-y","-v","error","-i",str(src),"-filter_complex",filtro,
                "-map","[out]","-c:a","libmp3lame","-b:a","128k",str(d/"toma.mp3")],check=True)

quitado = sum(b-a for a,b in cortes)
def nuevo(t):
    q = sum(min(b,t)-a for a,b in cortes if a < t)
    return round(max(0.0, t-q), 3)

M = json.load(open(d/"marcas.json", encoding="utf-8"))
for fr in M["frases"]: fr["ini"] = nuevo(fr["ini"])
M["palabras"] = [[nuevo(t), w] for t, w in M["palabras"]]
M["dur"] = round(dur - quitado, 3)
json.dump(M, open(d/"marcas.json","w"), ensure_ascii=False, indent=1)
print(f"{vid} · {dur:.2f} → {M['dur']:.2f} s · {len(cortes)} silencios apretados a {HUECO}s")
for fr in M["frases"]: print(f"  {fr['ini']:7.3f}  {fr['frase']}")
