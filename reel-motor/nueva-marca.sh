#!/usr/bin/env bash
# Un Reel Motor para una marca, sin tocar éste.
#
#   bash nueva-marca.sh https://tu-cliente.com           → ../reel-tu-cliente
#   bash nueva-marca.sh https://tu-cliente.com ~/Clientes → ~/Clientes/reel-tu-cliente
#   bash nueva-marca.sh --manual mi-marca                → copia en blanco, la marca a mano
#
# Qué hace: copia esta carpeta entera al lado, le mide la web y le deja la marca puesta.
# A partir de ahí son dos talleres independientes: éste se queda **siempre igual** y la
# copia es de esa marca. Puedes tener los que quieras.
#
# Lo que NO se copia: taller/ (las piezas de otras marcas), node_modules (se reinstala
# solo), .git y las salidas. Lo que SÍ: el motor, los 74 efectos, la música, los
# ejemplos, las piezas y el oficio.
#
# El precio de tener copias es que envejecen: si mejoras el motor aquí, allí no cambia.
# Por eso cada copia sale con su `actualizar.sh`, que trae el motor y el oficio de vuelta
# sin tocar la marca ni las piezas.
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
cd "$AQUI"

URL="$1"; DONDE="$2"
if [ -z "$URL" ]; then
  echo "uso: bash nueva-marca.sh <url>            → ../reel-<marca>"
  echo "     bash nueva-marca.sh <url> <carpeta>  → <carpeta>/reel-<marca>"
  echo "     bash nueva-marca.sh --manual <slug>  → copia en blanco"
  exit 1
fi

# ── el nombre de la copia ──────────────────────────────────────────
if [ "$URL" = "--manual" ]; then
  SLUG="$(echo "$DONDE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]\+/-/g;s/^-//;s/-$//')"
  DONDE=""
  [ -n "$SLUG" ] || { echo "✗ dime el nombre: bash nueva-marca.sh --manual mi-marca"; exit 1; }
else
  case "$URL" in http://*|https://*) ;; *) URL="https://$URL";; esac
  HOST="$(echo "$URL" | sed -E 's#^https?://##; s#/.*##; s#^www\.##')"
  SLUG="$(echo "$HOST" | cut -d. -f1 | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]\+/-/g')"
fi
BASE="${DONDE:-$(dirname "$AQUI")}"
DEST="$BASE/reel-$SLUG"

[ -e "$DEST" ] && { echo "✗ ya existe $DEST · bórralo o dale otra carpeta"; exit 1; }
mkdir -p "$BASE"

# ── la copia ───────────────────────────────────────────────────────
echo "Copiando el taller a $DEST"
if command -v rsync >/dev/null 2>&1; then
  rsync -a \
    --exclude 'taller/' --exclude 'node_modules' --exclude '.git' \
    --exclude '.instalado' --exclude '.DS_Store' --exclude '__pycache__/' \
    --exclude '*.pyc' \
    "$AQUI/" "$DEST/"
else
  mkdir -p "$DEST"
  for f in *; do
    case "$f" in taller|node_modules|.git) continue;; esac
    cp -R "$f" "$DEST/"
  done
  cp -R .claude "$DEST/" 2>/dev/null || true
  cp .gitignore "$DEST/" 2>/dev/null || true
  rm -rf "$DEST/node_modules" "$DEST/taller"
fi
mkdir -p "$DEST/taller"

# ── de dónde viene, para poder actualizarla ────────────────────────
cat > "$DEST/ORIGEN.md" <<EOF
# De dónde sale esta carpeta

Copia de **Reel Motor** hecha el $(date +%F) para la marca \`$SLUG\`.

    origen: $AQUI

El original se queda como está: éste es el taller de esta marca y sólo de esta marca.

## Si el original mejora

    bash actualizar.sh

Trae el motor (\`motor/\`) y el oficio (\`.claude/skills/reel-motor\`) desde el origen.
**No toca** tu marca, tus piezas, tus guiones ni tus salidas. Si has cambiado algo del
motor a mano, se pierde: los retoques de una marca van en su carpeta, no en el motor.
EOF

# ── el actualizador ────────────────────────────────────────────────
cat > "$DEST/actualizar.sh" <<'EOF'
#!/usr/bin/env bash
# Trae el motor y el oficio del Reel Motor original. No toca la marca ni las piezas.
set -e
cd "$(dirname "$0")"
ORIGEN="$(sed -n 's/^    origen: //p' ORIGEN.md | head -1)"
[ -d "$ORIGEN" ] || { echo "✗ no encuentro el original en $ORIGEN · edita ORIGEN.md"; exit 1; }
echo "Trayendo motor y oficio de $ORIGEN"
rsync -a --delete "$ORIGEN/motor/" motor/
rsync -a --delete "$ORIGEN/.claude/skills/reel-motor/" .claude/skills/reel-motor/
rsync -a --delete "$ORIGEN/.claude/skills/marca-desde-web/" .claude/skills/marca-desde-web/
rsync -a "$ORIGEN/ejemplos/" ejemplos/
for f in CLAUDE.md LEEME.md LEEME-elevenlabs.md CREDITOS.md LICENCIA.md requisitos.sh nueva-marca.sh; do
  [ -f "$ORIGEN/$f" ] && cp "$ORIGEN/$f" .
done
echo "✓ al día. Tu marca, tus piezas y tus salidas siguen como estaban."
EOF
chmod +x "$DEST/actualizar.sh"

# ── la marca, ya medida ────────────────────────────────────────────
if [ "$URL" != "--manual" ]; then
  echo "Midiendo $URL"
  ( cd "$DEST" && node motor/marca-desde-web.mjs "$URL" "taller/$SLUG" ) || {
    echo "⚠ la web no se dejó medir. La copia está hecha: monta la marca a mano dentro."; }
fi
[ -f "$AQUI/.instalado" ] && cp "$AQUI/.instalado" "$DEST/" || true

echo
echo "✓ $DEST"
echo "  Ábrelo con Claude Code desde ahí y sigue. Este taller no se ha tocado."
