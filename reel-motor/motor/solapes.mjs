// Busca dos capas encendidas ocupando el mismo sitio.
// Recorre la pieza, mide la caja real de cada elemento con id y avisa de los
// pares que se pisan sin ser uno padre del otro.
//   node ../../motor/solapes.mjs pieza.html [paso]
//
// Qué mira: todo elemento con `id`, visible (opacidad heredada > 0,06) y de
// más de 8 px. Qué salta: dos que se pisan más de un 28 % del menor.
//
// Lo que SÍ puede pisarse porque es la misma cosa se marca en el HTML con el
// mismo `data-grupo` —una fila con su cara y su importe, una tarjeta con sus
// partes— y se ignora. Un contenedor que sólo agrupa lleva `data-solapes="no"`.
// El telón del cierre (#scrim, #cierre) tapa a propósito y nunca cuenta.
import puppeteer from "puppeteer-core";
import { resolve } from "node:path";
import { exigirChrome } from "./chrome.mjs";

const CHROME = exigirChrome();
const [html, paso = "0.5"] = process.argv.slice(2);
if (!html) { console.error("uso: node solapes.mjs <pieza.html> [paso]"); process.exit(1); }

const b = await puppeteer.launch({ executablePath: CHROME, headless: "new",
  args: ["--allow-file-access-from-files"], defaultViewport: { width: 1080, height: 1920 } });
const pg = await b.newPage();
pg.on("pageerror", e => console.log("JS ERROR:", e.message));
await pg.goto("file://" + resolve(html), { waitUntil: "networkidle0" });
const dur = await pg.evaluate(() => window.DURACION);
const vistos = new Map();
for (let t = 0; t <= dur; t += parseFloat(paso)) {
  const pares = await pg.evaluate(tt => {
    window.seek(tt);
    const SIEMPRE_FUERA = new Set(["reel", "escena", "halo", "halo2", "grano", "scrim", "cierre"]);
    const op = e => { let o = 1, n = e; while (n && n !== document.body) { o *= parseFloat(getComputedStyle(n).opacity); n = n.parentElement; } return o; };
    const grupo = e => e.dataset.grupo || e.closest("[data-grupo]")?.dataset.grupo || e.id;
    const els = [...document.querySelectorAll("[id]")].filter(e => {
      if (SIEMPRE_FUERA.has(e.id)) return false;
      if (e.dataset.solapes === "no") return false;
      if (e.closest("#cierre, #scrim")) return false;
      const r = e.getBoundingClientRect();
      return r.width > 8 && r.height > 8 && op(e) > 0.06;
    }).map(e => ({ id: e.id, g: grupo(e), r: e.getBoundingClientRect().toJSON(), e }));
    const out = [];
    for (let i = 0; i < els.length; i++) for (let j = i + 1; j < els.length; j++) {
      const A = els[i], B = els[j];
      if (A.e.contains(B.e) || B.e.contains(A.e)) continue;
      if (A.g === B.g) continue;
      const x = Math.max(0, Math.min(A.r.right, B.r.right) - Math.max(A.r.left, B.r.left));
      const y = Math.max(0, Math.min(A.r.bottom, B.r.bottom) - Math.max(A.r.top, B.r.top));
      const inter = x * y; if (!inter) continue;
      const menor = Math.min(A.r.width * A.r.height, B.r.width * B.r.height);
      if (inter / menor > 0.28) out.push([A.id, B.id, +(inter / menor).toFixed(2)]);
    }
    return out;
  }, +t.toFixed(2));
  for (const [a, c, f] of pares) {
    const k = a + " ↔ " + c;
    if (!vistos.has(k)) vistos.set(k, { de: +t.toFixed(1), a: +t.toFixed(1), max: f });
    else { const v = vistos.get(k); v.a = +t.toFixed(1); v.max = Math.max(v.max, f); }
  }
}
await b.close();
if (!vistos.size) console.log("✓ ningún solape por encima del 28%");
for (const [k, v] of [...vistos].sort((x, y) => x[1].de - y[1].de))
  console.log(`${String(v.de).padStart(5)}s → ${String(v.a).padStart(5)}s   ${k}   (hasta ${Math.round(v.max * 100)}% del menor)`);
