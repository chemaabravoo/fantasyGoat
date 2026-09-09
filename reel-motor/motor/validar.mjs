// validar.mjs · comprueba una pieza antes del vistazo, y la entrega antes de darla.
//
//   node validar.mjs pieza.html [--muda] [--sin-musica]     la pieza: se niega si falla lo medible
//   node validar.mjs pieza-son.mp4 [--muda]                 la entrega: audio, 1080×1920, que no sea el vistazo
//
// Lo que comprueba aquí NO hace falta recordarlo ni contarlo en las referencias:
// es la forma de que los agujeros mecánicos no salgan, en vez de taparlos uno a uno.
// ✗ = se niega (exit 1) · ⚠ = míralo con criterio.
import puppeteer from "puppeteer-core";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { execSync } from "node:child_process";
import { buscarChrome } from "./chrome.mjs";

const args = process.argv.slice(2);
const flags = new Set(args.filter(a => a.startsWith("--")));
const [target] = args.filter(a => !a.startsWith("--"));
if (!target) { console.error("uso: node validar.mjs <pieza.html|entrega.mp4> [--muda] [--sin-musica]"); process.exit(2); }
const X = [], W = [];
const fail = m => X.push(m), warn = m => W.push(m);
const MUDA = flags.has("--muda");

function informe() {
  for (const m of X) console.log("✗ " + m);
  for (const m of W.slice(0, 14)) console.log("⚠ " + m);
  if (W.length > 14) console.log(`⚠ … y ${W.length - 14} avisos más del mismo tipo`);
  if (!X.length && !W.length) console.log("✓ todo en verde");
  else console.log(`${X.length} que se niegan · ${W.length} para mirar`);
  process.exit(X.length ? 1 : 0);
}

/* ── la entrega ─────────────────────────────────────────────────── */
if (target.endsWith(".mp4")) {
  const probe = JSON.parse(execSync(`ffprobe -v error -print_format json -show_streams -show_format "${resolve(target)}"`).toString());
  const v = probe.streams.find(s => s.codec_type === "video"), a = probe.streams.find(s => s.codec_type === "audio");
  if (!v) fail("no hay pista de vídeo");
  else if (!(v.width === 1080 && v.height === 1920)) warn(`resolución ${v.width}×${v.height}: la entrega es 1080×1920 (el vistazo va a 540×960 y no se publica)`);
  if (!a && !MUDA) fail("el mp4 NO tiene pista de audio: no es el archivo que se entrega (falta sonar-generico.py, o pasa --muda si la pidió muda)");
  if (/\/tmp\/ver|BORRADOR/i.test(target)) warn("parece un vistazo, no una entrega");
  if (!/-son\.mp4$/.test(target) && !MUDA) warn("no se llama -son.mp4: ¿es el mudo?");
  informe();
}

/* ── la pieza ───────────────────────────────────────────────────── */
const src = readFileSync(resolve(target), "utf8");
if (/@keyframes/.test(src)) fail("hay @keyframes: la animación tiene que colgar de seek(t) (motor.md)");
if (/(^|[^-\w])transition\s*:/m.test(src)) fail("hay transition: en el CSS: se captura a saltos (motor.md)");
if (/setTimeout\s*\(/.test(src)) warn("hay setTimeout: si toca la escena, el fotograma dependerá del reloj");
if (/requestAnimationFrame/.test(src) && !/navigator\.webdriver/.test(src)) fail("hay un reproductor con requestAnimationFrame sin parar bajo captura: añade `let playing=!navigator.webdriver` y `transform:none` bajo webdriver (motion-ui.md)");

const browser = await puppeteer.launch({ executablePath: buscarChrome(), headless: "new",
  args: ["--font-render-hinting=none", "--force-color-profile=srgb", "--hide-scrollbars", "--allow-file-access-from-files"],
  defaultViewport: { width: 1080, height: 1920, deviceScaleFactor: 1 } });
const page = await browser.newPage();
const jsErr = []; page.on("pageerror", e => jsErr.push(e.message));
await page.goto("file://" + resolve(process.cwd(), target), { waitUntil: "networkidle0" });
await page.evaluate(() => document.fonts.ready); await new Promise(r => setTimeout(r, 400));
for (const e of jsErr) fail("error de JavaScript: " + e);

const meta = await page.evaluate(() => {
  const cs = getComputedStyle(document.documentElement);
  const lee = v => cs.getPropertyValue(v).trim().replace(/^["']|["']$/g, "");
  return { seek: typeof window.seek === "function", fps: window.FPS, dur: window.DURACION,
    marcas: !!window.MARCAS, sfx: (window.MARCAS && window.MARCAS.SFX || []).length, musica: (window.MARCAS && window.MARCAS.MUSICA || []).length,
    marca: lee("--marca"), usaMarcaCss: !!document.querySelector('link[href*="marca"][href$=".css"]'),
    reel: !!(document.getElementById("reel") || document.querySelector(".reel")),
    /* los colores de la piel, resueltos a rgb por el propio navegador: el token puede
       venir en hex, en rgb() o en color-mix y aquí hay que compararlos de verdad */
    piel: (() => { const d = document.createElement("div"); document.body.appendChild(d);
      const r = n => { d.style.color = `var(${n})`; const c = getComputedStyle(d).color.match(/[\d.]+/g); return c ? c.slice(0, 3).map(Number) : null; };
      const v = { fondo: r("--fondo"), tinta: r("--tinta"), tintaBaja: r("--tinta-baja"), acento: r("--acento") };
      d.remove(); return v; })() };
});
if (!meta.seek) fail("la página no expone window.seek(t)");
if (!(meta.fps > 0)) fail("falta window.FPS");
if (!(meta.dur > 0)) fail("falta window.DURACION");
if (!meta.reel) fail("no hay #reel: es lo que capturan shoot-par.mjs y mirar.mjs");
if (meta.usaMarcaCss && (!meta.marca || meta.marca === "SIN DEFINIR")) fail("marca sin definir en marca.css (--marca)");
/* el contraste de la piel · desde el 8 sep 2026 cada marca trae su fondo (marca-desde-web),
   así que ya no está garantizado por diseño: se mide aquí o sale una pieza ilegible */
if (meta.piel && meta.piel.fondo && meta.piel.tinta) {
  const L = c => { const [r, g, b] = c.map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
  const cr = (a, b) => { const [x, y] = [L(a), L(b)].sort((p, q) => q - p); return +((x + 0.05) / (y + 0.05)).toFixed(2); };
  const F = meta.piel.fondo, hex = c => "#" + c.map(v => Math.round(v).toString(16).padStart(2, "0")).join("");
  const cT = cr(meta.piel.tinta, F);
  if (cT < 7) fail(`la tinta no se lee sobre el fondo: ${hex(meta.piel.tinta)} sobre ${hex(F)} da ${cT}:1 y hace falta 7:1 · arréglalo en marca.css, no en la pieza`);
  if (meta.piel.tintaBaja) { const cB = cr(meta.piel.tintaBaja, F);
    if (cB < 4.5) fail(`la tinta-baja no se lee: ${hex(meta.piel.tintaBaja)} sobre ${hex(F)} da ${cB}:1 y hace falta 4,5:1`); }
  if (meta.piel.acento) { const cA = cr(meta.piel.acento, F);
    if (cA < 1.6) warn(`el acento casi no se distingue del fondo (${cA}:1): las barras y las píldoras se van a perder`);
    else if (cA < 4.5) warn(`el acento da ${cA}:1 sobre el fondo: rellena y subraya, pero NO lo uses como texto`); }
}
if (!meta.marcas) fail("falta window.MARCAS: sin él no hay sonido ni mapa de tiempos");
else {
  if (!meta.sfx && !MUDA) fail("MARCAS.SFX está vacío: ninguna pieza se entrega muda (voz.md); si la pidió muda, --muda");
  if (!meta.musica && !MUDA && !flags.has("--sin-musica")) warn("MARCAS.MUSICA vacío: la música va por tramos (voz.md §8); con un audio ya mezclado, --sin-musica");
}
if (X.length) { await browser.close(); informe(); }

/* lo que se ve: recorrer la pieza cada medio segundo */
const DUR = meta.dur, PASO = 0.5;
const abajo = new Map(), arriba = new Map(), lados = new Map(), pisan = new Map(), mayus = new Map(); const firmas = [];
/* las franjas tapadas de Reels y TikTok (encuadre.md, 6 sep 2026): las letras no van por encima de 250, por debajo de 1520 ni más allá de 910 */
const Z = { x0: 100, x1: 910, y0: 250, y1: 1520 };   // la columna de botones empieza hacia 940; 910 deja aire
for (let t = 0; t <= DUR + 1e-6; t += PASO) {
  const r = await page.evaluate(t => {
    window.seek(t);
    const reel = document.getElementById("reel") || document.querySelector(".reel");
    const R = reel.getBoundingClientRect();
    const opac = el => { let o = 1; for (let e = el; e && e !== document.body; e = e.parentElement) { const s = getComputedStyle(e); if (s.display === "none" || s.visibility === "hidden") return 0; o *= +s.opacity; if (o < 0.02) return 0; } return o; };
    const hojas = [];
    for (const el of reel.querySelectorAll("*")) {
      const txt = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join("").trim();
      if (!txt) continue;
      const o = opac(el); if (o < 0.3) continue;
      const b = el.getBoundingClientRect(); if (b.width < 2 || b.height < 2) continue;
      const s = getComputedStyle(el);
      /* las letras de verdad, no la caja: un rótulo centrado en una caja ancha vale si sus letras caen dentro */
      let g = b; try { let L = Infinity, T = Infinity, Rr = -Infinity, B = -Infinity;
        for (const n of el.childNodes) { if (n.nodeType !== 3 || !n.textContent.trim()) continue; const rg = document.createRange(); rg.selectNodeContents(n);
          for (const r of rg.getClientRects()) { if (r.width < 1 || r.height < 1) continue; L = Math.min(L, r.left); T = Math.min(T, r.top); Rr = Math.max(Rr, r.right); B = Math.max(B, r.bottom); } }
        if (isFinite(L)) g = { left: L, top: T, width: Rr - L, height: B - T }; } catch (e) {}
      hojas.push({ id: el.id || el.className || el.tagName.toLowerCase(), txt: txt.slice(0, 40), x: b.left - R.left, y: b.top - R.top, w: b.width, h: b.height, gx: g.left - R.left, gy: g.top - R.top, gw: g.width, gh: g.height, o, mono: /courier|mono/i.test(s.fontFamily), el });
    }
    /* quién contiene a quién: un texto y su propio hijo no se pisan */
    const cont = hojas.map((h, i) => hojas.map((g, j) => i !== j && h.el.contains(g.el)).map(Number));
    hojas.forEach((h, i) => { h.cont = cont[i]; delete h.el; });
    const AMBIENTE = /^(halo|grano|bg|glow|scrim|reel|escena|hud|mundo|velo)/i;
    let vivos = 0; const partes = [];
    for (const el of reel.querySelectorAll("*")) {
      const nombre = el.id || (typeof el.className === "string" ? el.className : "");
      const o = opac(el); if (o < 0.05) continue;
      const b = el.getBoundingClientRect(); if (b.width < 4 || b.height < 4) continue;
      const s = getComputedStyle(el);
      const conFondo = s.backgroundColor !== "rgba(0, 0, 0, 0)" || (s.backgroundImage !== "none" && !AMBIENTE.test(nombre)) || s.borderTopWidth !== "0px";
      const conTexto = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
      if (!AMBIENTE.test(nombre) && (conTexto || conFondo) && o > 0.15) vivos++;
      /* la firma del fotograma: TODO lo visible, con o sin texto; si dos fotogramas seguidos dan la misma, nada se ha movido */
      partes.push(`${Math.round(b.left)},${Math.round(b.top)},${Math.round(b.width)},${Math.round(o * 20)}`);
    }
    const firma = partes.join("|");
    return { hojas, vivos: vivos.length, firma };
  }, +t.toFixed(3));
  if (t === 0 && r.vivos === 0) fail("fotograma 0 vacío: en el segundo 0 ya tiene que haber algo a medio moverse (gancho.md)");
  for (const h of r.hojas) {
    if (h.w * h.h < 2500 || h.txt.length < 3) { /* iniciales y fichas: se ven en contactos */ }
    else { if (h.gy + h.gh > Z.y1 + 10 && h.gy < 1900) abajo.set(h.id + "·" + h.txt, t);
           if (h.gy < Z.y0 - 10) arriba.set(h.id + "·" + h.txt, t);
           if (h.gx < Z.x0 - 10 || h.gx + h.gw > Z.x1 + 10) lados.set(h.id + "·" + h.txt, [t, Math.round(h.gx), Math.round(h.gx + h.gw)]); }
    if (h.mono && /^[A-ZÁÉÍÓÚÜÑ0-9 ·.\/%€,+\-–]{4,}$/.test(h.txt) && /[A-ZÁÉÍÓÚÑ]{3}/.test(h.txt)) mayus.set(h.txt, 1);
  }
  const hs = r.hojas;
  for (let i = 0; i < hs.length; i++) for (let j = i + 1; j < hs.length; j++) {
    const a = hs[i], b = hs[j]; if (a.txt === b.txt) continue;
    if (a.cont[j] || b.cont[i]) continue;                         // un texto y su propio hijo
    if (a.w * a.h < 2500 || b.w * b.h < 2500) continue;             // iniciales y fichas al vuelo: se ven en contactos
    const ix = Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)), iy = Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
    const inter = ix * iy, min = Math.min(a.w * a.h, b.w * b.h);
    if (min > 0 && inter / min > 0.5) pisan.set(`«${a.txt}» y «${b.txt}»`, t);
  }
  firmas.push([t, r.firma]);
}
await browser.close();
/* los textos fuera de la zona segura se niegan: el mismo mp4 va a Reels y a TikTok (encuadre.md); --sin-zonas lo deja en aviso */
const zona = flags.has("--sin-zonas") ? warn : fail;
for (const [k, t] of abajo) zona(`por debajo de ${Z.y1} (caption y botones de Reels/TikTok) en ${t.toFixed(1)} s: ${k}`);
for (const [k, t] of arriba) zona(`por encima de ${Z.y0} (el título de Reels y las pestañas de TikTok) en ${t.toFixed(1)} s: ${k}`);
for (const [k, [t, x0, x1]] of lados) zona(`fuera de x ${Z.x0}–${Z.x1} (los botones de la derecha) en ${t.toFixed(1)} s, x ${x0}–${x1}: ${k}`);
for (const [k, t] of pisan) warn(`se pisan en ${t.toFixed(1)} s: ${k}`);
if (mayus.size) warn(`${mayus.size} etiquetas mono en mayúsculas: ${[...mayus.keys()].slice(0, 8).join(" · ")}${mayus.size > 8 ? " …" : ""} — ¿estarían impresas en el papel?`);
let quieto = 0, desde = null;
for (let i = 1; i < firmas.length; i++) {
  if (firmas[i][1] === firmas[i - 1][1] && firmas[i][1]) { if (desde === null) desde = firmas[i - 1][0]; quieto++; }
  else { if (quieto >= 2) warn(`nada se mueve entre ${desde.toFixed(1)} y ${firmas[i - 1][0].toFixed(1)} s (la capa ambiente no para nunca · movimiento.md)`); quieto = 0; desde = null; }
}
if (quieto >= 2) warn(`nada se mueve entre ${desde.toFixed(1)} y ${firmas.at(-1)[0].toFixed(1)} s`);
informe();
