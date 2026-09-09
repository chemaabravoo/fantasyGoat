// logo.mjs · el logotipo de una empresa, en vectorial
//
//   node ../../motor/logo.mjs spotify                 → marca/logos/spotify.svg
//   node ../../motor/logo.mjs "banco santander"       → busca el nombre suelto
//   node ../../motor/logo.mjs instagram tiktok youtube
//
// Saca los SVG de **simple-icons** (paquete CC0, unos 3.300 logos de marcas conocidas).
// Vectorial, un solo trazo, sin fondo: se tiñe con `fill` y escala sin pixelarse, que es
// justo lo que hace falta en un lienzo de 1080×1920 capturado al doble.
//
// EL LOGO DEL CLIENTE NO SALE DE AQUÍ: ése lo baja `marca-desde-web.mjs` de su propia web
// y queda en `marca/logo.*`. Esto es para logos de TERCEROS que aparecen en la pieza
// —«funciona en Instagram y TikTok», «pagas con Bizum»—.
//
// Antes de usar uno, lee la parte legal de `animacion/simbolos.md`. Resumen: nombrar a una
// empresa con su logo está bien; dar a entender que te patrocina, no. Y no se recolorean
// salvo a un solo color plano cuando el fondo lo exige.
import { mkdirSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const nombres = process.argv.slice(2).filter(a => !a.startsWith("--"));
if (!nombres.length) {
  console.error(`uso: node ../../motor/logo.mjs <marca> [otra] [otra]

  node ../../motor/logo.mjs spotify
  node ../../motor/logo.mjs instagram tiktok youtube`);
  process.exit(1);
}
const DEST = join("marca", "logos");
mkdirSync(DEST, { recursive: true });

const slug = s => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "")
  .replace(/\+/g, "plus").replace(/\./g, "dot").replace(/&/g, "and")
  .replace(/[^a-z0-9]/g, "");

let ok = 0;
for (const nombre of nombres) {
  const s = slug(nombre);
  const url = `https://cdn.jsdelivr.net/npm/simple-icons@13/icons/${s}.svg`;
  try {
    const r = await fetch(url);
    if (!r.ok) { console.log(`  ✗ ${nombre} · simple-icons no lo tiene como «${s}»`);
      console.log(`     míralo en https://simpleicons.org y pásame el nombre exacto,`);
      console.log(`     o si es el logo del cliente, sale de su web (marca/logo.*)`); continue; }
    const svg = await r.text();
    if (!/<svg/.test(svg)) { console.log(`  ✗ ${nombre} · lo que ha venido no es un SVG`); continue; }
    const ruta = join(DEST, `${s}.svg`);
    /* simple-icons trae el color oficial en el <title>; se deja el path limpio para teñirlo */
    writeFileSync(ruta, svg);
    const bytes = Buffer.byteLength(svg);
    console.log(`  ✓ ${ruta}  (${bytes} B)`);
    ok++;
  } catch (e) { console.log(`  ✗ ${nombre} · ${e.message}`); }
}
if (ok) {
  console.log(`
Cómo se usa en la pieza (inline, para poder teñirlo y animarlo):

  <div class="logo" id="lg"></div>
  const SVG = await (await fetch('marca/logos/spotify.svg')).text();   // o pégalo a mano

Más simple y sin fetch: abre el .svg, copia el <path> y mételo en la pieza:

  <svg viewBox="0 0 24 24" class="lg"><path d="…"/></svg>
  .lg{width:96px;height:96px;fill:var(--acento)}      /* un solo color, se tiñe */

Se anima como cualquier otra cosa: entra con muelle, el trazo se dibuja con
stroke-dashoffset si le pones stroke, y respira con el ambiente.`);
}
