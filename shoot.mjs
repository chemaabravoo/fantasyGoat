// Captura una pieza animada a vídeo 9:16, fotograma a fotograma, en un solo Chrome.
//   node ../../motor/shoot.mjs pieza-loquesea.html salida/loquesea.mp4
//
// El HTML manda: expone window.FPS, window.DURACION y una window.seek(t)
// que es función pura del tiempo. Aquí sólo se avanza el reloj a mano y se
// fotografía. Se renderiza al doble y se baja a 1080 con lanczos: el texto
// fino se rompe si se captura a 1x.
//
// Para el día a día usa shoot-par.mjs, que reparte entre varios Chromes.
import puppeteer from "puppeteer-core";
import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import { join, resolve, dirname } from "node:path";
import { tmpdir } from "node:os";
import { execFileSync } from "node:child_process";
import { exigirChrome } from "./chrome.mjs";

const CHROME = exigirChrome();
const [htmlArg, outArg] = process.argv.slice(2);
if (!htmlArg || !outArg) {
  console.error("uso: node shoot.mjs <pieza.html> <salida.mp4>");
  process.exit(1);
}
const SRC = "file://" + resolve(process.cwd(), htmlArg);
const OUT = resolve(process.cwd(), outArg);
mkdirSync(dirname(OUT), { recursive: true });
const TMP = join(tmpdir(), "reel-" + Date.now());
mkdirSync(TMP, { recursive: true });

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: "new",
  args: ["--font-render-hinting=none", "--force-color-profile=srgb",
         "--hide-scrollbars", "--allow-file-access-from-files"],
  defaultViewport: { width: 1080, height: 1920, deviceScaleFactor: 2 },
});
const page = await browser.newPage();
page.on("pageerror", e => console.log("JS ERROR:", e.message));
await page.goto(SRC, { waitUntil: "networkidle0" });
await page.evaluate(() => document.fonts.ready);
await new Promise(r => setTimeout(r, 900));

const { fps, dur } = await page.evaluate(() => ({ fps: window.FPS, dur: window.DURACION }));
const marcas = await page.evaluate(() => window.MARCAS || null);
if (marcas) {
  writeFileSync(OUT.replace(/\.mp4$/, "") + ".marcas.json", JSON.stringify(marcas));
  console.log("marcas: " + Object.keys(marcas).join(", "));
}
const total = Math.round(fps * dur);
console.log(`${dur}s · ${fps} fps · ${total} fotogramas`);

const el = await page.$("#reel");
for (let i = 0; i < total; i++) {
  await page.evaluate(t => window.seek(t), i / fps);
  await el.screenshot({ path: join(TMP, String(i).padStart(4, "0") + ".png") });
  if (i % 60 === 0) process.stdout.write(`  ${i}/${total}\r`);
}
await browser.close();

execFileSync("ffmpeg", [
  "-y", "-framerate", String(fps),
  "-i", join(TMP, "%04d.png"),
  "-vf", "scale=1080:1920:flags=lanczos",
  "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "18",
  "-r", String(fps), "-movflags", "+faststart",
  OUT,
], { stdio: ["ignore", "ignore", "inherit"] });

rmSync(TMP, { recursive: true, force: true });
console.log(`✓ ${OUT}`);
