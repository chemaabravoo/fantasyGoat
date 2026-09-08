// Captura una pieza a vídeo 9:16 repartiendo los fotogramas entre varios
// navegadores que trabajan a la vez.
//
//   node ../../motor/shoot-par.mjs pieza.html salida/pieza.mp4 [obreros] [escala] [fps]
//
// La escala es lo que se captura por píxel de lienzo:
//   2     entrega · nítido, lo que se publica
//   1     borrador · para ver la animación, ~4x menos píxeles
//   0.5   vistazo  · legible y rápido; con [fps] 20, doce veces menos trabajo
//
// Y los fps: las piezas se animan a 60 (window.FPS), que es lo que hace que un
// barrido rápido no salga a tirones. La pieza dura lo mismo capturando 20 en vez
// de 60, porque seek(t) es puro y se le piden un tercio de instantes. El
// movimiento se ve a saltos, pero el RITMO —que es lo que se juzga en un
// preview— se juzga igual. El [fps] que se pide sólo puede BAJAR de 60: los
// fotogramas que no se capturan no existen.
// El movimiento, los tiempos y el encuadre son IDÉNTICOS en los tres:
// lo único que cambia es la nitidez del texto fino.
//
// Se puede porque window.seek(t) es función PURA del tiempo: el fotograma 900
// no depende del 899, así que da igual quién lo dibuje ni en qué orden. Cada
// obrero abre su propio Chrome —no una pestaña más del mismo— porque un
// navegador tiene un solo proceso de GPU y las capturas harían cola en él.
//
// El reparto es intercalado (obrero w hace los fotogramas w, w+N, w+2N…) para
// que un tramo pesado no le caiga entero a uno solo.
import puppeteer from "puppeteer-core";
import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join, resolve, dirname } from "node:path";
import { tmpdir, cpus } from "node:os";
import { fileURLToPath } from "node:url";
import { exigirChrome } from "./chrome.mjs";

const CHROME = exigirChrome();
const FLAGS = process.argv.slice(2).filter(a => a.startsWith("--"));   // --sin-validar · --muda · --sin-musica
const [htmlArg, outArg, nArg, escArg, fpsArg] = process.argv.slice(2).filter(a => !a.startsWith("--"));
if (!htmlArg || !outArg) {
  console.error("uso: node shoot-par.mjs <archivo.html> <salida.mp4> [obreros] [escala] [fps]");
  process.exit(1);
}
const SRC = "file://" + resolve(process.cwd(), htmlArg);
const OUT = resolve(process.cwd(), outArg);
mkdirSync(dirname(OUT), { recursive: true });
/* validar antes de capturar: lo mecánico no se recuerda, se comprueba (entrega/render.md) */
if (!FLAGS.includes("--sin-validar")) {
  try { execFileSync("node", [join(dirname(fileURLToPath(import.meta.url)), "validar.mjs"), htmlArg, ...FLAGS.filter(f => f !== "--sin-validar")], { stdio: "inherit" }); }
  catch (e) { console.error("validar.mjs se ha negado: corrige la pieza, o --sin-validar si sabes lo que haces"); process.exit(1); }
}
// Medido en un Mac de 10 núcleos con una pieza de 1467 fotogramas:
//   escala 1 →  6 obreros 78,6s · 10 obreros 63,4s · 14 obreros 62,7s
//   escala 2 →  3 obreros 414s · 6 obreros 245s · 10 obreros 194s
// Diez es el codo. En un equipo con menos núcleos se usa lo que haya.
const N   = Math.max(1, parseInt(nArg || "0", 10) || Math.min(10, Math.max(4, cpus().length)));
const TMP = join(tmpdir(), "reel-par-" + Date.now());
mkdirSync(TMP, { recursive: true });

const ARGS = ["--font-render-hinting=none", "--force-color-profile=srgb",
              "--hide-scrollbars", "--allow-file-access-from-files"];
const ESC = Math.max(0.5, Math.min(2, parseFloat(escArg || "2") || 2));
const BORRADOR = ESC < 2;
const VIEW = { width: 1080, height: 1920, deviceScaleFactor: ESC };

const t0 = Date.now();

// ── el primero abre solo, para leer el guion y las marcas ──
const jefe = await puppeteer.launch({ executablePath: CHROME, headless: "new",
  args: ARGS, defaultViewport: VIEW });
const pJefe = await jefe.newPage();
pJefe.on("pageerror", e => { console.error("JS ERROR:", e.message); process.exit(1); });
// Todo lo que venga de la red se guarda aquí una sola vez. Sin esto, cada
// obrero abre un Chrome con perfil nuevo y vuelve a descargar las tipografías
// de Google: diez descargas a la vez, y el `load` esperando a todas.
const CACHE = new Map();
pJefe.on("response", async (res) => {
  const u = res.url();
  if (!/^https?:/.test(u)) return;
  try {
    CACHE.set(u, { status: res.status(), headers: res.headers(),
                   body: await res.buffer() });
  } catch { /* una respuesta sin cuerpo no estorba */ }
});
await pJefe.goto(SRC, { waitUntil: "load", timeout: 120000 });
await pJefe.evaluate(() => document.fonts.ready);
const { fps, dur } = await pJefe.evaluate(() => ({ fps: window.FPS, dur: window.DURACION }));
if (!fps || !dur) { console.error("la pieza no expone window.FPS y window.DURACION"); process.exit(1); }
const marcas = await pJefe.evaluate(() => window.MARCAS || null);
if (marcas) {
  writeFileSync(OUT.replace(/\.mp4$/, "") + ".marcas.json", JSON.stringify(marcas));
  console.log("marcas: " + Object.keys(marcas).join(", "));
}
await jefe.close();

// se captura 1 de cada PASO fotogramas, y se renumeran para que ffmpeg los vea seguidos
const FPS_OUT = Math.max(5, Math.min(fps, parseInt(fpsArg || "0", 10) || fps));
const PASO = Math.max(1, Math.round(fps / FPS_OUT));
const total = Math.round(fps * dur);
const totalOut = Math.ceil(total / PASO);
console.log(`${dur}s · ${(fps/PASO).toFixed(0)} fps · ${totalOut} fotogramas · ${N} obreros · escala ${ESC}${BORRADOR ? "  ⚠ BORRADOR, no se publica" : ""}`);

let hechos = 0;
async function obrero(w) {
  // Escalonado: diez Chromes arrancando a la vez se pisan pidiendo las
  // tipografías y alguno se pasa del timeout de navegación.
  await new Promise(r => setTimeout(r, w * 220));
  const b = await puppeteer.launch({ executablePath: CHROME, headless: "new",
    args: ARGS, defaultViewport: VIEW });
  const pg = await b.newPage();
  pg.on("pageerror", e => console.error("JS ERROR:", e.message));
  // Nada sale a la red: lo externo se responde desde lo que trajo el jefe.
  await pg.setRequestInterception(true);
  pg.on("request", (req) => {
    const u = req.url();
    if (!/^https?:/.test(u)) return req.continue();
    const c = CACHE.get(u);
    return c ? req.respond(c) : req.abort();
  });
  await pg.goto(SRC, { waitUntil: "load", timeout: 60000 });
  await pg.evaluate(() => document.fonts.ready);
  await new Promise(r => setTimeout(r, 900));      // que carguen las tipografías
  const el = await pg.$("#reel");
  for (let j = w; j < totalOut; j += N) {
    await pg.evaluate(t => window.seek(t), (j * PASO) / fps);
    await el.screenshot({ path: join(TMP, String(j).padStart(4, "0") + ".png") });
    if (++hechos % 60 === 0) process.stdout.write(`  ${hechos}/${totalOut}\r`);
  }
  await b.close();
}
await Promise.all(Array.from({ length: N }, (_, w) => obrero(w)));
const seg = ((Date.now() - t0) / 1000).toFixed(1);
console.log(`  ${totalOut}/${totalOut} capturados en ${seg}s`);

// El vídeo sale SIEMPRE con proporción 9:16: la entrega a 1080x1920 con
// lanczos; el borrador se queda como se capturó, que se juzga igual.
execFileSync("ffmpeg", [
  "-y", "-framerate", String(fps / PASO),
  "-i", join(TMP, "%04d.png"),
  ...(BORRADOR ? [] : ["-vf", "scale=1080:1920:flags=lanczos"]),
  "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
  ...(BORRADOR ? ["-preset", "ultrafast", "-crf", "26"] : ["-crf", "18"]),
  "-r", String(fps / PASO), "-movflags", "+faststart",
  OUT,
], { stdio: ["ignore", "ignore", "inherit"] });

rmSync(TMP, { recursive: true, force: true });
console.log(`✓ ${OUT}  ·  ${((Date.now() - t0) / 1000).toFixed(1)}s en total`);
