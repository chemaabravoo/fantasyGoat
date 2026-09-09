// Hojas de contactos de una pieza: TODOS los fotogramas que importan, en rejilla.
// Mirar cuatro sueltos es adivinar; esto enseña la pieza entera de golpe.
//
//   node ../../motor/contactos.mjs pieza-x.html            ← desde el HTML, sin renderizar (~15 s)
//   node ../../motor/contactos.mjs salida/pieza-son.mp4    ← desde un vídeo ya hecho
//   node ../../motor/contactos.mjs <lo que sea> <carpeta>  ← dónde dejarlas
//
// Saca: hoja A = los 6 primeros segundos a 4 fps (24 fotogramas: el gancho, uno a uno)
//       hojas B, C… = el resto a 2 fps, de 30 en 30 (15 s por hoja).
// Se miran TODAS. Una pieza de 45 s son cuatro hojas.
import { execFileSync } from "node:child_process";
import { mkdirSync, rmSync, readdirSync } from "node:fs";
import { resolve, basename, join } from "node:path";
import { tmpdir } from "node:os";

const [src, destArg] = process.argv.slice(2);
if (!src) { console.error("uso: node contactos.mjs <pieza.html | video.mp4> [carpeta]"); process.exit(1); }
const dest = destArg || join(tmpdir(), "contactos");
mkdirSync(dest, { recursive: true });
const nom = basename(src).replace(/\.[^.]+$/, "");
const FPS_A = 4, SEG_A = 6, FPS_B = 2, POR_HOJA = 30;

// ── 1 · los fotogramas: del vídeo (ffmpeg) o de la pieza (puppeteer) ──
const TMP = join(tmpdir(), "contactos-" + Date.now());
mkdirSync(join(TMP, "A"), { recursive: true }); mkdirSync(join(TMP, "B"), { recursive: true });
let dur;
if (/\.html?$/i.test(src)) {
  const puppeteer = (await import("puppeteer-core")).default;
  const { exigirChrome } = await import("./chrome.mjs");
  const b = await puppeteer.launch({ executablePath: exigirChrome(), headless: "new",
    args: ["--font-render-hinting=none", "--force-color-profile=srgb", "--hide-scrollbars", "--allow-file-access-from-files"],
    defaultViewport: { width: 1080, height: 1920, deviceScaleFactor: 0.5 } });
  const pg = await b.newPage();
  pg.on("pageerror", e => console.error("JS ERROR:", e.message));
  await pg.goto("file://" + resolve(process.cwd(), src), { waitUntil: "networkidle0" });
  await pg.evaluate(() => document.fonts.ready);
  await new Promise(r => setTimeout(r, 700));
  dur = await pg.evaluate(() => window.DURACION);
  const el = await pg.$("#reel");
  let i = 0;
  for (let t = 0; t < Math.min(SEG_A, dur); t += 1 / FPS_A, i++) {
    await pg.evaluate(v => window.seek(v), +t.toFixed(3));
    await el.screenshot({ path: join(TMP, "A", String(i).padStart(4, "0") + ".png") });
  }
  i = 0;
  for (let t = SEG_A; t < dur; t += 1 / FPS_B, i++) {
    await pg.evaluate(v => window.seek(v), +t.toFixed(3));
    await el.screenshot({ path: join(TMP, "B", String(i).padStart(4, "0") + ".png") });
  }
  await b.close();
} else {
  const v = resolve(src);
  dur = parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v]).toString());
  execFileSync("ffmpeg", ["-v", "error", "-t", String(SEG_A), "-i", v, "-vf", `fps=${FPS_A},scale=300:-1`, join(TMP, "A", "%04d.png")]);
  if (dur > SEG_A) execFileSync("ffmpeg", ["-v", "error", "-ss", String(SEG_A), "-i", v, "-vf", `fps=${FPS_B},scale=300:-1`, join(TMP, "B", "%04d.png")]);
}

// ── 2 · las hojas ──
const hojas = [];
const tile = (carpeta, desde, cuantas, cols, filas, salida) => execFileSync("ffmpeg",
  ["-v", "error", "-y", "-start_number", String(desde), "-i", join(TMP, carpeta, "%04d.png"),
   "-frames:v", String(cuantas), "-vf", `scale=300:-1,tile=${cols}x${filas}:margin=6:padding=6`, "-frames:v", "1", join(dest, salida)]);
const primero = readdirSync(join(TMP, "A")).length ? parseInt(readdirSync(join(TMP, "A")).sort()[0]) : 0;
tile("A", primero, FPS_A * SEG_A, 6, 4, `${nom}-A.png`);
hojas.push(`${nom}-A.png  ·  0 → ${Math.min(SEG_A, dur)} s  (${FPS_A} fps)`);
const nB = readdirSync(join(TMP, "B")).length;
const primeroB = nB ? parseInt(readdirSync(join(TMP, "B")).sort()[0]) : 0;
for (let h = 0; h * POR_HOJA < nB; h++) {
  const letra = String.fromCharCode(66 + h);
  const t0 = SEG_A + (h * POR_HOJA) / FPS_B, t1 = Math.min(dur, t0 + POR_HOJA / FPS_B);
  tile("B", primeroB + h * POR_HOJA, POR_HOJA, 6, 5, `${nom}-${letra}.png`);
  hojas.push(`${nom}-${letra}.png  ·  ${t0} → ${t1.toFixed(1)} s  (${FPS_B} fps)`);
}
rmSync(TMP, { recursive: true, force: true });
console.log(`${nom} · ${dur.toFixed(2)} s · ${hojas.length} hojas en ${dest}  — míralas TODAS`);
hojas.forEach(h => console.log("  " + h));
