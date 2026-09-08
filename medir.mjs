// ¿Tiembla el maquetado? Un fotograma quieto no enseña un temblor.
//   node ../../motor/medir.mjs pieza.html cifra 40 120
//   (id del elemento, fotograma desde, fotograma hasta)
//
// offsetWidth/offsetHeight son medidas de MAQUETADO: la transformación de
// la cámara no las toca. getBoundingClientRect sí la lleva encima, y
// entonces mides el zoom, no el layout.
// UN SOLO VALOR = estable. Cuarenta valores = ahí está tu temblor.
import puppeteer from "puppeteer-core";
import { resolve } from "node:path";
import { exigirChrome } from "./chrome.mjs";

const CHROME = exigirChrome();
const [html, id, desde, hasta] = process.argv.slice(2);
if (!html || !id) {
  console.error("uso: node medir.mjs <pieza.html> <idElemento> [fDesde] [fHasta]");
  process.exit(1);
}

const browser = await puppeteer.launch({
  executablePath: CHROME, headless: "new",
  args: ["--font-render-hinting=none", "--allow-file-access-from-files"],
  defaultViewport: { width: 1080, height: 1920, deviceScaleFactor: 1 },
});
const page = await browser.newPage();
page.on("pageerror", e => console.log("JS ERROR:", e.message));
await page.goto("file://" + resolve(process.cwd(), html), { waitUntil: "networkidle0" });
await page.evaluate(() => document.fonts.ready);

const fps = await page.evaluate(() => window.FPS || 60);
const dur = await page.evaluate(() => window.DURACION || 10);
const a = desde !== undefined ? +desde : 0;
const b = hasta !== undefined ? +hasta : Math.round(fps * dur);

const anchos = new Set(), altos = new Set();
for (let f = a; f <= b; f++) {
  const m = await page.evaluate((tt, el) => {
    window.seek(tt);
    const e = document.getElementById(el);
    return e ? [e.offsetWidth, e.offsetHeight] : null;
  }, f / fps, id);
  if (!m) { console.error(`no existe #${id}`); process.exit(1); }
  anchos.add(m[0]); altos.add(m[1]);
}
await browser.close();

const ok = anchos.size === 1 && altos.size === 1;
console.log(`#${id} · fotogramas ${a}–${b}`);
console.log(`  ancho: ${anchos.size} valor(es) → ${[...anchos].slice(0, 12).join(" ")}${anchos.size > 12 ? " …" : ""}`);
console.log(`  alto : ${altos.size} valor(es) → ${[...altos].slice(0, 12).join(" ")}${altos.size > 12 ? " …" : ""}`);
console.log(ok ? "  ✓ estable" : "  ✗ TIEMBLA · caja fija y anima scale · ver trampas.md 2 y 3");
