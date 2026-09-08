// Fotografía instantes sueltos de una pieza, para comprobar encuadres.
//   node ../../motor/mirar.mjs pieza.html 0 0.5 1.4 3.0
// Un render tarda minutos; esto, ocho segundos. Casi todo lo de
// trampas.md se ve en un fotograma quieto. MIRA las imágenes de verdad.
import puppeteer from "puppeteer-core";
import { mkdirSync } from "node:fs";
import { resolve, join } from "node:path";
import { tmpdir } from "node:os";
import { exigirChrome } from "./chrome.mjs";

const CHROME = exigirChrome();
const [html, ...tiempos] = process.argv.slice(2);
if (!html || !tiempos.length) {
  console.error("uso: node mirar.mjs <pieza.html> <t1> [t2 ...]");
  process.exit(1);
}
const OUT = join(tmpdir(), "mirar");
mkdirSync(OUT, { recursive: true });

const browser = await puppeteer.launch({
  executablePath: CHROME, headless: "new",
  args: ["--font-render-hinting=none", "--force-color-profile=srgb",
         "--hide-scrollbars", "--allow-file-access-from-files"],
  defaultViewport: { width: 1080, height: 1920, deviceScaleFactor: 1 },
});
const page = await browser.newPage();
page.on("pageerror", e => console.log("JS ERROR:", e.message));
await page.goto("file://" + resolve(process.cwd(), html), { waitUntil: "networkidle0" });
await page.evaluate(() => document.fonts.ready);
await new Promise(r => setTimeout(r, 700));

const el = await page.$("#reel");
for (const t of tiempos) {
  await page.evaluate(v => window.seek(v), +t);
  await el.screenshot({ path: join(OUT, "t" + String(t).replace(".", "_") + ".png") });
}
console.log("ok →", OUT, tiempos.join(" "));
await browser.close();
