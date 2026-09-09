#!/usr/bin/env bash
# Sintetiza el catálogo de camas musicales con numpy y las deja repetidas
# hasta ~95 s en musica/largos/, que es lo que come sonar-generico.py
# (no repite la música por sí solo). Sin derechos: todo sale de las recetas.
#   bash musica/generar.sh                   las 25
#   bash musica/generar.sh tension-latido    una sola (las de bucles.py)
set -e
cd "$(dirname "$0")"
mkdir -p wav largos
if [ $# -gt 0 ]; then
  python3 bucles.py wav "$@"
else
  python3 sintetizar.py wav            # el órgano épico, suave y fuerte
  mv wav/nolan-suave.wav wav/epica-organo-suave.wav
  mv wav/nolan-fuerte.wav wav/epica-organo.wav
  python3 bucles.py wav                # tensión · emoción · épica · neutra (16)
  python3 bucles-club.py wav           # energía (4)
  python3 bucles-esperanza.py wav      # emoción-organo · emoción-amanecer · energía-himno
fi
for w in wav/*.wav; do
  n=$(basename "$w" .wav)
  ffmpeg -v error -y -stream_loop 4 -i "$w" -t 95 -c:a libmp3lame -b:a 160k "largos/$n-largo.mp3"
done
rm -rf wav __pycache__          # los wav pesan y ya están en los mp3
ls largos
