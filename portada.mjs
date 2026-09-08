// La portada del reel, del propio vídeo: 1080×1920 con todo lo legible dentro
// del cuadrado central (y 420 → 1500), que es lo que Instagram enseña en la parrilla.
//
//   node ../../motor/portada.mjs salida/pieza-son.mp4 salida/pieza-portada.png \
//        --cifra "1.000.000" --sub "de reproducciones · un solo vídeo" \
//        --frase "Y no lo animé <i>yo.</i>" --chip "TikTok + Instagram" --pie "Reel Motor"
//
// Los tres fotogramas de la tira salen del propio vídeo (15 %, 45 %, 75 %) salvo que
// se pidan otros con --fotogramas 7.2,19.4,31.2 (o de otro vídeo con --fuente otro.mp4).
// Se ejecuta DESDE la carpeta de la marca, porque la piel la pone su marca.css.
import puppeteer from "puppeteer-core";
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from "node:fs";
import { resolve, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";
import { exigirChrome } from "./chrome.mjs";

const AQUI = dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const opt = (n, d = "") => { const i = argv.indexOf("--" + n); if (i < 0) return d;
  const v = argv[i + 1]; argv.splice(i, 2); return v; };
const CIFRA = opt("cifra"), SUB = opt("sub"), FRASE = opt("frase");
const CHIP = opt("chip"), PIE = opt("pie"), FUENTE = opt("fuente");
const FOTOS = opt("fotogramas");
// una pieza puede llevar dentro la marca de otro (un caso de éxito, un cliente):
// con esto la portada se viste de esa marca sin tocar marca.css
const FONDO = opt("fondo"), TINTA = opt("tinta"), ACENTO = opt("acento"), TINTABAJA = opt("tinta-baja");
const [video, salida] = argv.filter(a => !a.startsWith("--"));
if (!video || !salida) {
  console.error("uso: node portada.mjs <video.mp4> <salida.png> [--cifra …] [--sub …] [--frase …] [--chip …] [--pie …]");
  process.exit(1);
}
if (!existsSync("marca.css")) { console.error("no hay marca.css en esta carpeta: la portada hereda la piel de la marca"); process.exit(1); }

const dur = +execFileSync("ffprobe", ["-v","error","-show_entries","format=duration",
  "-of","default=nw=1:nk=1", FUENTE || video]).toString().trim();
const tiempos = FOTOS ? FOTOS.split(",").map(Number) : [0.15, 0.45, 0.75].map(k => +(dur * k).toFixed(2));
const TMP = join(tmpdir(), "portada-" + Date.now()); mkdirSync(TMP, { recursive: true });
const imgs = tiempos.map((t, i) => {
  const f = join(TMP, `f${i}.jpg`);
  execFileSync("ffmpeg", ["-v","error","-y","-ss",String(t),"-i", FUENTE || video, "-frames:v","1", f]);
  return f;
});
const GIRO = [-3, 0, 3], IZQ = [145, 415, 685];
const tira = imgs.map((f, i) =>
  `<img src="file://${f}" style="left:${IZQ[i]}px;transform:rotate(${GIRO[i]}deg)">`).join("");

const html = readFileSync(join(AQUI, "portada.html"), "utf8")
  .replace("{{CHIP}}",  CHIP  ? `<span>${CHIP}</span>` : "")
  .replace("{{CIFRA}}", CIFRA || "")
  .replace("{{SUB}}",   SUB   || "")
  .replace("{{FRASE}}", FRASE || "")
  .replace("{{TIRA}}",  tira)
  .replace("{{PIE}}",   PIE ? `<u><b></b><span>${PIE}</span></u>` : "")
  .replace("</head>", (FONDO||TINTA||ACENTO||TINTABAJA
    ? `<style>:root{${FONDO?`--fondo:${FONDO};`:""}${TINTA?`--tinta:${TINTA};`:""}`
      + `${ACENTO?`--acento:${ACENTO};`:""}${TINTABAJA?`--tinta-baja:${TINTABAJA};`:""}}</style>`
    : "") + "</head>");
const tmpHtml = resolve("_portada-tmp.html");
writeFileSync(tmpHtml, html);

const browser = await puppeteer.launch({
  executablePath: exigirChrome(), headless: "new",
  args: ["--font-render-hinting=none","--force-color-profile=srgb","--hide-scrollbars",
         "--allow-file-access-from-files"],
  defaultViewport: { width: 1080, height: 1920, deviceScaleFactor: 1 },
});
const page = await browser.newPage();
page.on("pageerror", e => console.log("JS ERROR:", e.message));
await page.goto("file://" + tmpHtml, { waitUntil: "networkidle0" });
await page.evaluate(() => document.fonts.ready);
await new Promise(r => setTimeout(r, 500));
await (await page.$("#reel")).screenshot({ path: resolve(salida) });
// una copia con el cuadrado marcado, para revisar el encuadre antes de entregarla
await page.evaluate(() => { document.getElementById("guia").style.display = "block"; });
const guia = resolve(salida).replace(/\.png$/, "-guia.png");
await (await page.$("#reel")).screenshot({ path: guia });
await browser.close();
rmSync(tmpHtml, { force: true }); rmSync(TMP, { recursive: true, force: true });
console.log(`✓ ${salida}  ·  fotogramas ${tiempos.join(", ")} s`);
console.log(`  ${guia} ← míralo: todo lo que se lee tiene que caber en el cuadrado`);
