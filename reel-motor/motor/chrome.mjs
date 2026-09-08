// Localiza un navegador con el que capturar: Chrome, Chromium, Edge o Brave,
// en Mac, Linux o Windows. Si tienes uno en otro sitio, CHROME_PATH manda.
//
//   node motor/chrome.mjs          → imprime la ruta, o sale con error
import { existsSync } from "node:fs";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";

const HOME = process.env.HOME || process.env.USERPROFILE || "";
const CANDIDATOS = {
  darwin: [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    `${HOME}/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`,
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
  ],
  win32: [
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    `${process.env.LOCALAPPDATA || ""}\\Google\\Chrome\\Application\\chrome.exe`,
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
  ],
  linux: [],   // en Linux se busca por nombre, abajo
};
const NOMBRES_LINUX = ["google-chrome", "google-chrome-stable", "chromium",
  "chromium-browser", "microsoft-edge", "brave-browser"];

export function buscarChrome() {
  if (process.env.CHROME_PATH && existsSync(process.env.CHROME_PATH)) return process.env.CHROME_PATH;
  for (const c of CANDIDATOS[process.platform] || []) if (c && existsSync(c)) return c;
  if (process.platform !== "win32") {
    for (const n of NOMBRES_LINUX) {
      try { const r = execSync(`command -v ${n}`, { stdio: ["ignore", "pipe", "ignore"] }).toString().trim(); if (r) return r; }
      catch { /* siguiente */ }
    }
  }
  return null;
}

export const CHROME = buscarChrome();

export function exigirChrome() {
  if (CHROME) return CHROME;
  console.error("No encuentro Chrome. Instálalo (https://www.google.com/chrome) o " +
    "di dónde está: CHROME_PATH=/ruta/al/chrome node …");
  process.exit(1);
}

if (import.meta.url === pathToFileURL(process.argv[1] || "").href) {
  const c = buscarChrome();
  if (c) { console.log(c); process.exit(0); }
  console.error("Chrome no encontrado");
  process.exit(1);
}
