#!/usr/bin/env bash
# Pasa un Reel Motor v1 a v2, sin perder nada tuyo.
#
#   bash actualizar-pack.sh ~/Downloads/reel-motor          ← la carpeta vieja
#   bash actualizar-pack.sh                                 ← la busca al lado
#
# Se pasa DESDE la carpeta nueva (ésta) apuntando a la vieja. Lo que hace:
#
#   TRAE de la nueva   el motor entero, los 74 efectos grabados, las 11 camas,
#                      los ejemplos, las skills y los textos.
#   RESPETA de la vieja  taller/ (tus marcas, guiones, audios y salidas),
#                      node_modules, .instalado y las skills de tus marcas.
#   BORRA lo que ya no vale  motor/INDICE.md (se mudó a motor/sonidos/INDICE.md),
#                      los efectos sintetizados sueltos y anclas.json viejos.
#
# Antes de tocar nada hace una copia de seguridad de la vieja al lado.
set -e
NUEVA="$(cd "$(dirname "$0")" && pwd)"

# ── ¿cuál es la vieja? ─────────────────────────────────────────────
VIEJA="$1"
if [ -z "$VIEJA" ]; then
  for c in "$(dirname "$NUEVA")"/reel-motor "$(dirname "$NUEVA")"/reel-motor-pack \
           "$HOME/Downloads/reel-motor" "$HOME/Descargas/reel-motor"; do
    [ -d "$c" ] && [ "$c" != "$NUEVA" ] && [ -f "$c/CLAUDE.md" ] && { VIEJA="$c"; break; }
  done
fi
[ -n "$VIEJA" ] || { echo "uso: bash actualizar-pack.sh <carpeta del Reel Motor viejo>"; exit 1; }
VIEJA="$(cd "$VIEJA" && pwd)"

[ -f "$VIEJA/CLAUDE.md" ] || { echo "✗ $VIEJA no parece un Reel Motor (no hay CLAUDE.md)"; exit 1; }
[ "$VIEJA" = "$NUEVA" ] && { echo "✗ esa es esta misma carpeta"; exit 1; }

# ── ¿ya está actualizada? ──────────────────────────────────────────
if [ -f "$VIEJA/motor/energia.mjs" ] && [ -d "$VIEJA/musica/pixabay" ]; then
  echo "✓ $VIEJA ya es v2. No hay nada que hacer."; exit 0
fi

echo "Vieja:  $VIEJA"
echo "Nueva:  $NUEVA"
echo

# ── copia de seguridad ─────────────────────────────────────────────
COPIA="$VIEJA-antes-de-v2-$(date +%Y%m%d-%H%M)"
echo "1/5 · copia de seguridad en $COPIA"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --exclude 'node_modules' "$VIEJA/" "$COPIA/"
else
  mkdir -p "$COPIA"; (cd "$VIEJA" && tar cf - --exclude node_modules .) | (cd "$COPIA" && tar xf -)
fi

# ── lo que se trae de la nueva ─────────────────────────────────────
echo "2/5 · trayendo el motor, los sonidos, la música y el oficio"
copia_dir(){   # copia_dir <sub> [--borrando]
  local sub="$1" del=""
  [ "$2" = "--borrando" ] && del="--delete"
  mkdir -p "$VIEJA/$sub"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a $del "$NUEVA/$sub/" "$VIEJA/$sub/"
  else
    rm -rf "$VIEJA/$sub"; mkdir -p "$VIEJA/$sub"; cp -R "$NUEVA/$sub/." "$VIEJA/$sub/"
  fi
}
# el motor entero, borrando lo que sobra (los sintetizados sueltos de v1 se van con él)
copia_dir motor --borrando
copia_dir ejemplos
copia_dir piezas
copia_dir musica/pixabay
copia_dir .claude/skills/reel-motor --borrando
copia_dir .claude/skills/marca-desde-web --borrando
for f in CLAUDE.md LEEME.md LEEME-elevenlabs.md CREDITOS.md LICENCIA.md \
         requisitos.sh nueva-marca.sh actualizar-pack.sh package.json .gitignore; do
  [ -f "$NUEVA/$f" ] && cp "$NUEVA/$f" "$VIEJA/$f"
done
# las recetas de la música sintetizada, sin pisar las que ya generó
for f in "$NUEVA"/musica/*.py "$NUEVA"/musica/*.sh "$NUEVA"/musica/INDICE.md; do
  [ -f "$f" ] && cp "$f" "$VIEJA/musica/"
done

# ── lo que ya no vale ──────────────────────────────────────────────
echo "3/5 · quitando lo que v1 dejaba y ya no sirve"
[ -f "$VIEJA/motor/INDICE.md" ] && { rm -f "$VIEJA/motor/INDICE.md"; echo "    − motor/INDICE.md (ahora en motor/sonidos/INDICE.md)"; }
rm -rf "$VIEJA/motor/__pycache__" "$VIEJA/motor/sonidos/_sintetizados"

# ── las piezas que ya tenía, a 60 fps ──────────────────────────────
echo "4/5 · tus piezas de taller/"
N=0
if [ -d "$VIEJA/taller" ]; then
  while IFS= read -r pz; do
    if grep -q "window.FPS=30;" "$pz" 2>/dev/null; then
      sed -i.bak 's/window\.FPS=30;/window.FPS=60;/' "$pz" && rm -f "$pz.bak"
      N=$((N+1))
    fi
  done < <(find "$VIEJA/taller" -name "*.html" -type f 2>/dev/null)
fi
if [ "$N" -gt 0 ]; then
  echo "    $N piezas pasadas de 30 a 60 fps"
  echo "    ⚠ si alguna cuenta fotogramas (frame(t)%N) hay que doblar la N: parpadeará al doble"
else
  echo "    ninguna que tocar"
fi
echo "    tus marcas, guiones, audios y salidas no se han tocado"

# ── comprobar ──────────────────────────────────────────────────────
echo "5/5 · comprobando"
E=$(ls "$VIEJA"/motor/sonidos/*.wav 2>/dev/null | wc -l | tr -d ' ')
C=$(ls "$VIEJA"/musica/pixabay/*.mp3 2>/dev/null | wc -l | tr -d ' ')
echo "    efectos grabados: $E (deben ser 74)"
echo "    camas grabadas:   $C (deben ser 11)"
[ -f "$VIEJA/motor/energia.mjs" ] && echo "    energia.mjs ✓" || echo "    energia.mjs ✗"
[ -f "$VIEJA/motor/marca-PLANTILLA-oscura.css" ] && echo "    piel oscura ✓" || echo "    piel oscura ✗"

cat > "$VIEJA/QUE-HA-CAMBIADO.md" <<'EOF'
# Has pasado a la v2

Tu carpeta se ha actualizado. Tus marcas, guiones, audios y vídeos **siguen donde estaban**,
en `taller/`. La copia de seguridad de cómo estaba antes está al lado, en una carpeta
`…-antes-de-v2-<fecha>`; cuando compruebes que todo va, bórrala.

## Lo que ahora tienes y antes no

- **74 efectos de sonido grabados**, dentro de `motor/sonidos/`. Antes se sintetizaban al
  instalar y sonaban a sintetizador. Ya no hay que generarlos.
- **11 camas musicales grabadas** en `musica/pixabay/`, una por familia, con su índice.
  Las 25 sintetizadas siguen en `musica/largos/` como respaldo.
- **La marca se mide de la web y sale en dos pieles**, clara y oscura, con el fondo, el
  cielo y las letras de tu cliente —no una perla fija para todos—. La tipografía viaja
  dentro del CSS, así que ya no se puede descuadrar con el `<link>` de la pieza.
- **60 fps** en vez de 30. Tus piezas se han cambiado solas.
- **`reel motor <una-web>`** te monta la skill de esa marca (`/reel-tu-cliente`) y puedes
  tener las que quieras. El taller no se toca.
- **`nueva-marca.sh`** saca un taller entero aparte para un cliente.
- **`motor/energia.mjs`** te dice si una pieza se ve animada o sólo se mueve.
- **`motor/logo.mjs`** baja logos de empresas en vectorial.
- **Emojis, iconos y logotipos** explicados en
  `.claude/skills/reel-motor/animacion/simbolos.md`.
- **`validar.mjs` se niega** si el texto no se lee sobre el fondo de la marca.

## Dos avisos

1. **Si alguna pieza tuya hace parpadear algo contando fotogramas** (`frame(t)%20<11`),
   ahora parpadeará al doble de rápido: dobla ese número (`%40<21`). Es lo único que el
   cambio de 30 a 60 fps puede romper.
2. **Las `marca.css` que ya tenías siguen valiendo** tal cual. Si quieres que esa marca
   tenga también su piel clara y oscura medidas, vuelve a pasarle su web:
   `node motor/marca-desde-web.mjs https://su-web.com taller/<slug>`.

Cuando quieras, cierra Claude Code y vuelve a abrirlo desde esta carpeta para que cargue
las skills nuevas.
EOF

echo
echo "✓ $VIEJA está en v2 · lee QUE-HA-CAMBIADO.md"
echo "  Copia de seguridad: $COPIA"
