#!/usr/bin/env bash
# Comprueba el equipo y deja la carpeta lista. Se pasa las veces que haga falta.
#   bash requisitos.sh              todo, música incluida (la primera vez tarda 4-8 min)
#   bash requisitos.sh --sin-musica sólo el equipo
cd "$(dirname "$0")" || exit 1
ok=1
v(){ printf "  \033[32m✓\033[0m %s\n" "$1"; }
x(){ printf "  \033[31m✗\033[0m %s\n" "$1"; ok=0; }
i(){ printf "  … %s\n" "$1"; }
echo "Reel Motor · requisitos"
echo "  Sólo toca esta carpeta. Si falta algo, crea:"
echo "    node_modules/      25 paquetes de npm (puppeteer-core y sus dependencias, ~35 MB)"
echo "    musica/largos/     25 camas .mp3, sintetizadas aquí (4-8 min, una sola vez)"
echo "  Los 74 efectos de sonido ya vienen en motor/sonidos/: no hay que generarlos."
echo

# ── node ≥ 18 ──
if command -v node >/dev/null 2>&1; then
  NV=$(node -v | sed 's/^v//'); NM=${NV%%.*}
  if [ "$NM" -ge 18 ] 2>/dev/null; then v "node $NV"; else x "node $NV es viejo: hace falta 18 o más → https://nodejs.org (LTS)"; fi
else x "node no está → https://nodejs.org (versión LTS)"; fi
command -v npm >/dev/null 2>&1 || x "npm no está (viene con node)"

# ── ffmpeg / ffprobe ──
for b in ffmpeg ffprobe; do
  if command -v $b >/dev/null 2>&1; then v "$b"
  else x "$b no está → Mac: brew install ffmpeg · Linux: sudo apt install ffmpeg · Windows: https://ffmpeg.org/download.html"; fi
done

# ── python3 + numpy ──
if command -v python3 >/dev/null 2>&1; then
  PV=$(python3 -c 'import sys;print("%d.%d"%sys.version_info[:2])'); v "python3 $PV"
  if python3 -c 'import numpy' 2>/dev/null; then v "numpy $(python3 -c 'import numpy;print(numpy.__version__)')"
  else x "numpy no está → python3 -m pip install numpy"; fi
else x "python3 no está → https://python.org"; fi

# ── Chrome ──
if command -v node >/dev/null 2>&1 && CH=$(node motor/chrome.mjs 2>/dev/null); then v "Chrome: $CH"
else x "Chrome no encontrado → https://www.google.com/chrome  (o dime dónde está: CHROME_PATH=/ruta/al/chrome bash requisitos.sh)"; fi

# ── la clave de ElevenLabs (para la voz; no hace falta para instalar) ──
if [ -n "${ELEVENLABS_API_KEY:-}" ]; then v "ELEVENLABS_API_KEY puesta (la voz)"; else i "sin ELEVENLABS_API_KEY: la voz esperará · ver LEEME-elevenlabs.md"; fi

# ── puppeteer-core, dentro de esta carpeta ──
if [ "$ok" = 1 ]; then
  if [ -d node_modules/puppeteer-core ]; then v "puppeteer-core"
  else i "instalando puppeteer-core en ./node_modules (una vez, ~20 s)"
    if npm install --no-audit --no-fund --loglevel=error >/dev/null 2>&1; then v "puppeteer-core"; else x "npm install falló · pásalo a mano: npm install"; fi
  fi
fi

# ── los efectos de sonido: vienen en la carpeta, sólo se cuentan ──
if [ "$ok" = 1 ]; then
  E=$(ls motor/sonidos/*.wav 2>/dev/null | wc -l | tr -d ' ')
  if [ "$E" -ge 74 ]; then v "efectos: $E grabaciones en motor/sonidos/"
  else x "faltan efectos en motor/sonidos/ (hay $E de 74) · la descarga se ha quedado a medias: vuelve a descomprimir el zip"; fi
fi

# ── la música, sintetizada en local ──
if [ "$ok" = 1 ] && [ "${1:-}" != "--sin-musica" ]; then
  N=$(ls musica/largos/*.mp3 2>/dev/null | wc -l | tr -d ' ')
  if [ "$N" -ge 25 ]; then v "música: $N camas en musica/largos/"
  else i "sintetizando las 25 camas musicales con numpy (4-8 min, una sola vez)"
    if bash musica/generar.sh >/dev/null 2>&1; then v "música: $(ls musica/largos/*.mp3 | wc -l | tr -d ' ') camas en musica/largos/"
    else x "la música no se generó · pásalo a mano y mira el error: bash musica/generar.sh"; fi
  fi
fi

echo
if [ "$ok" = 1 ]; then
  date +%F > .instalado
  echo "Todo listo. Lo siguiente es la marca."
else
  rm -f .instalado
  echo "Falta algo (las ✗). Instálalo y vuelve a pasar:  bash requisitos.sh"
  exit 1
fi
