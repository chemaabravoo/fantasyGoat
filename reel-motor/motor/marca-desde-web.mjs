// Saca la marca de una web: colores medidos por área y por papel, tipografías,
// logotipo, nombre, datos de contacto y una captura. Y propone los tokens de
// marca.css con el contraste ya medido.
//
//   node motor/marca-desde-web.mjs https://ejemplo.com taller/ejemplo
//
// Deja en taller/ejemplo/marca/: web.json (todo), captura.png (arriba),
// captura-entera.png (la página), captura-movil.png y logo.* si lo encontró.
// Lo que imprime es un resumen para decidir; la decisión final es de quien
// monta la marca (referencias/marca.md).
import puppeteer from "puppeteer-core";
import { mkdirSync, writeFileSync, readFileSync } from "node:fs";
import { resolve, join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { exigirChrome } from "./chrome.mjs";

const CHROME = exigirChrome();
let [url, destArg] = process.argv.slice(2);
if (!url) { console.error("uso: node marca-desde-web.mjs <url> [carpeta-de-la-marca]"); process.exit(1); }
if (!/^https?:\/\//.test(url)) url = "https://" + url;
const host = new URL(url).hostname.replace(/^www\./, "");
const slug = host.split(".")[0].toLowerCase().replace(/[^a-z0-9]+/g, "-");
const DEST = resolve(process.cwd(), destArg || join("taller", slug));
const MARCA = join(DEST, "marca");
mkdirSync(MARCA, { recursive: true });

// ── color: utilidades ──────────────────────────────────────────────
const hex2rgb = h => [0, 2, 4].map(i => parseInt(h.slice(1).substr(i, 2), 16));
const rgb2hex = ([r, g, b]) => "#" + [r, g, b].map(v => Math.round(Math.max(0, Math.min(255, v))).toString(16).padStart(2, "0")).join("");
const lum = h => { const [r, g, b] = hex2rgb(h).map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
const contraste = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return +((x + 0.05) / (y + 0.05)).toFixed(2); };
const sat = h => { const [r, g, b] = hex2rgb(h).map(v => v / 255); const mx = Math.max(r, g, b), mn = Math.min(r, g, b); return mx === 0 ? 0 : (mx - mn) / mx; };
const mezcla = (a, b, k) => rgb2hex(hex2rgb(a).map((v, i) => v + (hex2rgb(b)[i] - v) * k));
const croma = h => { const c = hex2rgb(h); return Math.max(...c) - Math.min(...c); };   // 0..255
const gris = h => croma(h) < 40;   // un marrón muy oscuro tiene saturación alta y no es un color de marca
// gira el tono del acento sin tocar su viveza: de ahí salen las otras tres manchas del cielo
const rgb2hsl = h => { const [r, g, b] = hex2rgb(h).map(v => v / 255); const mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
  let hh = 0; if (d) hh = mx === r ? ((g - b) / d + (g < b ? 6 : 0)) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
  const l = (mx + mn) / 2; return [hh * 60, d ? d / (1 - Math.abs(2 * l - 1)) : 0, l]; };
const hsl2rgb = ([hh, s, l]) => { hh = ((hh % 360) + 360) % 360; const c = (1 - Math.abs(2 * l - 1)) * s, x = c * (1 - Math.abs((hh / 60) % 2 - 1)), m = l - c / 2;
  const [r, g, b] = hh < 60 ? [c, x, 0] : hh < 120 ? [x, c, 0] : hh < 180 ? [0, c, x] : hh < 240 ? [0, x, c] : hh < 300 ? [x, 0, c] : [c, 0, x];
  return rgb2hex([(r + m) * 255, (g + m) * 255, (b + m) * 255]); };

// ── la página ──────────────────────────────────────────────────────
const b = await puppeteer.launch({ executablePath: CHROME, headless: "new",
  args: ["--force-color-profile=srgb", "--hide-scrollbars"],
  defaultViewport: { width: 1280, height: 900, deviceScaleFactor: 1 } });
const pg = await b.newPage();
await pg.setUserAgent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36");
try { await pg.goto(url, { waitUntil: "networkidle2", timeout: 60000 }); }
catch (e) { console.error("no cargó: " + e.message); process.exit(1); }
await pg.evaluate(() => document.fonts.ready);
await new Promise(r => setTimeout(r, 1200));

// El aviso de cookies tapa la captura: se intenta rechazar (lo mínimo) o cerrar.
await pg.evaluate(() => {
  const btns = [...document.querySelectorAll("button, a, [role=button]")];
  const busca = re => btns.find(x => re.test((x.textContent || "").trim()) && x.getBoundingClientRect().width > 0);
  const el = busca(/^(rechazar|rechazar todo|rechazar todas|solo necesarias|sólo necesarias|reject all|reject|decline|only necessary)$/i)
          || busca(/^(ahora no|no, gracias|no gracias|más tarde|omitir|saltar|not now|skip|later|cerrar|close|✕|×)$/i);
  if (el) el.click();
});
await new Promise(r => setTimeout(r, 600));
// un paseo por la página para que cargue lo perezoso, y vuelta arriba
await pg.evaluate(async () => { for (let y = 0; y < Math.min(document.body.scrollHeight, 6000); y += 700) { scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } scrollTo(0, 0); });
await new Promise(r => setTimeout(r, 500));

const datos = await pg.evaluate(() => {
  const W = innerWidth, H = Math.max(1, Math.min(document.documentElement.scrollHeight, 6000));
  const norm = c => { const m = (c || "").match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(/[\s,\/]+/).filter(Boolean).map(Number); if (p.length > 3 && p[3] < 0.5) return null;
    return "#" + p.slice(0, 3).map(v => Math.round(v).toString(16).padStart(2, "0")).join(""); };
  const vis = (e, s, r) => r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none" && parseFloat(s.opacity) > 0;
  const colores = {}, fuentes = {};
  const addC = (c, peso, rol) => { if (!c) return; const e = colores[c] || (colores[c] = { color: c, peso: 0, roles: {} }); e.peso += peso; e.roles[rol] = (e.roles[rol] || 0) + peso; };
  const addF = (f, peso, rol, w) => { f = (f || "").split(",")[0].replace(/["']/g, "").trim(); if (!f) return;
    const e = fuentes[f] || (fuentes[f] = { familia: f, peso: 0, roles: {}, grosores: {} }); e.peso += peso; e.roles[rol] = (e.roles[rol] || 0) + peso; e.grosores[w] = (e.grosores[w] || 0) + 1; };
  for (const e of document.querySelectorAll("body *")) {
    const s = getComputedStyle(e), r = e.getBoundingClientRect();
    if (!vis(e, s, r)) continue;
    const tag = e.tagName.toLowerCase();
    if (["script", "style", "noscript", "svg", "path"].includes(tag)) continue;
    const top = r.top + scrollY; if (top > H) continue;
    const area = (Math.min(r.width, W) * Math.min(r.height, H)) / (W * H);   // fracción de la página
    const bg = norm(s.backgroundColor);
    const esBoton = tag === "button" || (tag === "a" && bg && r.width < 600 && r.height < 120 && r.height > 24);
    if (bg) addC(bg, area * 100 + (esBoton ? 4 : 0), esBoton ? "boton-fondo" : "fondo");
    const conTexto = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (conTexto) {
      const fs = parseFloat(s.fontSize) || 16;
      const rol = /^h[1-3]$/.test(tag) ? "titular" : esBoton ? "boton-texto" : "texto";
      const peso = (fs / 16) * Math.max(0.02, Math.min(area * 100, 2)) + (rol === "titular" ? 1.5 : 0);
      addC(norm(s.color), peso, rol);
      addF(s.fontFamily, peso * (rol === "titular" ? 3 : 1), rol, s.fontWeight);
      if (rol === "titular" && s.fontStyle === "italic") addF(s.fontFamily, 0, "cursiva", s.fontWeight);
    }
    const bc = norm(s.borderTopColor);
    if (bc && parseFloat(s.borderTopWidth) > 0 && bc !== bg) addC(bc, 0.3, "borde");
  }
  const meta = n => document.querySelector(`meta[name="${n}"], meta[property="${n}"]`)?.content || "";
  const abs = u => { try { return new URL(u, location.href).href; } catch { return ""; } };
  const logos = [...document.querySelectorAll("img, svg")].map(e => {
    const r = e.getBoundingClientRect(); if (r.width < 16 || r.height < 8) return null;
    const pista = [e.className && e.className.baseVal !== undefined ? e.className.baseVal : e.className, e.id, e.getAttribute("alt"), e.getAttribute("aria-label"), e.getAttribute("src"), e.closest("a")?.getAttribute("aria-label"), e.closest("a")?.getAttribute("title")].join(" ");
    const enCabecera = !!e.closest("header, nav, [class*=header], [class*=navbar], [class*=nav-], [id*=header], [id*=nav]") || (r.top + scrollY) < 160;
    const dice = /logo|brand|marca|wordmark/i.test(pista);
    if (!dice && !enCabecera) return null;
    if (r.height > r.width * 1.6) return null;          // un logotipo es ancho o cuadrado; esto es un mockup o una foto
    return { tipo: e.tagName.toLowerCase(), src: e.tagName === "IMG" ? abs(e.currentSrc || e.src) : null,
      svg: e.tagName === "svg" ? e.outerHTML.slice(0, 200000) : null, alt: e.getAttribute("alt") || "", ancho: Math.round(r.width), alto: Math.round(r.height), enCabecera, dice };
  }).filter(Boolean).sort((a, c) => (c.dice - a.dice) || (c.enCabecera - a.enCabecera) || (c.ancho * c.alto - a.ancho * a.alto));
  const texto = document.body.innerText || "";
  const tel = [...new Set([...document.querySelectorAll('a[href^="tel:"]')].map(a => a.getAttribute("href").replace("tel:", "").trim()))];
  const mail = [...new Set([...document.querySelectorAll('a[href^="mailto:"]')].map(a => a.getAttribute("href").replace("mailto:", "").split("?")[0]))];
  const wa = [...new Set([...document.querySelectorAll('a[href*="wa.me"], a[href*="whatsapp"]')].map(a => a.href))];
  const redes = [...new Set([...document.querySelectorAll('a[href*="instagram.com"], a[href*="tiktok.com"], a[href*="facebook.com"], a[href*="youtube.com"], a[href*="linkedin.com"]')].map(a => a.href))];
  const nav = [...new Set([...document.querySelectorAll("nav a, header a")].map(a => a.textContent.trim()).filter(t => t && t.length < 30))].slice(0, 14);
  const h1 = [...document.querySelectorAll("h1")].map(e => e.innerText.trim()).filter(Boolean).slice(0, 3);
  const h2 = [...document.querySelectorAll("h2")].map(e => e.innerText.trim()).filter(Boolean).slice(0, 8);
  const cifras = [...new Set((texto.match(/\b\d[\d.,]*\s?(%|€|\$|años|clientes|reseñas|opiniones|estrellas|min|h)\b/gi) || []).map(x => x.trim()))].slice(0, 12);
  const gfonts = [...document.querySelectorAll('link[href*="fonts.googleapis.com"]')].map(l => l.href);
  const fontfaces = [...new Set([...document.fonts].map(f => f.family.replace(/["']/g, "")))];
  return {
    titulo: document.title, descripcion: meta("description") || meta("og:description"),
    nombre: meta("og:site_name") || meta("application-name") || "", ogImage: abs(meta("og:image")),
    themeColor: meta("theme-color"), lang: document.documentElement.lang,
    favicon: abs(document.querySelector('link[rel*="icon"]')?.getAttribute("href") || "/favicon.ico"),
    h1, h2, nav, cifras, tel, mail, wa, redes, gfonts, fontfaces,
    colores: Object.values(colores).sort((a, c) => c.peso - a.peso).slice(0, 24),
    fuentes: Object.values(fuentes).sort((a, c) => c.peso - a.peso).slice(0, 8),
    logos: logos.slice(0, 6),
  };
});

// ── capturas ───────────────────────────────────────────────────────
await pg.screenshot({ path: join(MARCA, "captura.png") });
await pg.screenshot({ path: join(MARCA, "captura-entera.png"), fullPage: true, captureBeyondViewport: true }).catch(() => {});
await pg.setViewport({ width: 390, height: 844, deviceScaleFactor: 1 });
await new Promise(r => setTimeout(r, 500));
await pg.screenshot({ path: join(MARCA, "captura-movil.png") });

// ── el logotipo ────────────────────────────────────────────────────
let logoRuta = null;
for (const l of datos.logos) {
  try {
    if (l.svg) { logoRuta = join(MARCA, "logo.svg"); writeFileSync(logoRuta, l.svg); break; }
    if (l.src) {
      const res = await pg.goto(l.src, { timeout: 20000 });
      if (!res || !res.ok()) continue;
      const tipo = (res.headers()["content-type"] || "").split(";")[0];
      const ext = tipo.includes("svg") ? "svg" : tipo.includes("png") ? "png" : tipo.includes("webp") ? "webp" : tipo.includes("jpeg") ? "jpg" : (l.src.match(/\.(svg|png|webp|jpe?g)/i) || [, "png"])[1];
      logoRuta = join(MARCA, "logo." + ext); writeFileSync(logoRuta, await res.buffer()); break;
    }
  } catch { /* el siguiente candidato */ }
}
await b.close();

// ── la propuesta de tokens ─────────────────────────────────────────
const C = datos.colores;
const fondos = C.filter(c => c.roles.fondo).sort((a, c) => c.roles.fondo - a.roles.fondo);
const fondoWeb = fondos[0]?.color || "#ffffff";
const webOscura = lum(fondoWeb) < 0.25;
const vivos = C.filter(c => !gris(c.color)).map(c => ({ ...c,
  puntos: c.peso + 6 * (c.roles["boton-fondo"] || 0) + 2 * (c.roles.titular || 0) + (c.roles.borde || 0) }))
  .sort((a, c) => c.puntos - a.puntos);
const acento = vivos[0]?.color || datos.themeColor || "#ff00ff";
const acento2 = vivos.find(v => v.color !== acento && contraste(v.color, acento) > 1.4)?.color || null;

const fondoOscuro = webOscura ? fondoWeb : mezcla("#0e0e0e", acento, 0.06);
const fondoClaro = webOscura ? mezcla("#f7f7f5", acento, 0.04) : fondoWeb;
const proponeTinta = fondo => {
  const esOscuro = lum(fondo) < 0.25;
  const candidatos = C.filter(c => c.roles.texto || c.roles.titular).map(c => c.color);
  const base = esOscuro ? "#ffffff" : "#111111";
  const t = candidatos.find(c => contraste(c, fondo) >= 7) || (esOscuro ? mezcla("#ffffff", acento, 0.04) : mezcla("#111111", acento, 0.08));
  let baja = mezcla(t, fondo, 0.42); let n = 0;
  while (contraste(baja, fondo) < 4.5 && n++ < 10) baja = mezcla(baja, t, 0.15);
  return { tinta: t, tintaBaja: baja, tintaBase: base };
};
const propuesta = fondo => { const { tinta, tintaBaja } = proponeTinta(fondo); return {
  fondo, tinta, tintaBaja, acento, acento2: acento2 || acento,
  contraste: { tinta: contraste(tinta, fondo), tintaBaja: contraste(tintaBaja, fondo), acento: contraste(acento, fondo) },
  acentoValeComoTexto: contraste(acento, fondo) >= 4.5 }; };

// Next.js y compañía sirven las fuentes con el nombre destrozado (__Plus_Jakarta_Sans_380412).
// Si eso entra en --titular, Chrome no la encuentra y la pieza sale con la tipografía equivocada.
const limpiaFuente = f => f ? f.replace(/^_+/, "").replace(/_+[0-9a-f]{4,}$/i, "").replace(/_+(Fallback|fallback)$/, "").replace(/_+/g, " ").trim() : f;
const F = datos.fuentes.map(f => ({ ...f, familia: limpiaFuente(f.familia), familiaCruda: f.familia }));
const titular = F.slice().sort((a, c) => (c.roles.titular || 0) - (a.roles.titular || 0))[0]?.familia || null;
const texto = F.slice().sort((a, c) => (c.roles.texto || 0) - (a.roles.texto || 0))[0]?.familia || null;
const mono = F.find(f => /mono|code|courier/i.test(f.familia))?.familia || null;
const sistema = f => !f || /^(-apple-system|system-ui|ui-sans-serif|ui-monospace|ui-serif|ui-rounded|blinkmacsystemfont|segoe ui|helvetica|arial|roboto|sans-serif|sans|serif|monospace|mono|times|georgia|courier|courier new)$/i.test(f);

const salida = {
  url, host, slug, nombre: datos.nombre || datos.titulo.split(/[|·–—-]/)[0].trim(), titulo: datos.titulo,
  descripcion: datos.descripcion, lang: datos.lang, h1: datos.h1, h2: datos.h2, nav: datos.nav, cifras: datos.cifras,
  contacto: { tel: datos.tel, mail: datos.mail, whatsapp: datos.wa, redes: datos.redes },
  webOscura, fondoWeb, themeColor: datos.themeColor,
  colores: C.slice(0, 14).map(c => ({ color: c.color, peso: +c.peso.toFixed(2), roles: Object.fromEntries(Object.entries(c.roles).map(([k, v]) => [k, +v.toFixed(2)])), saturacion: +sat(c.color).toFixed(2) })),
  fuentes: F.map(f => ({ familia: f.familia, peso: +f.peso.toFixed(2), roles: Object.fromEntries(Object.entries(f.roles).map(([k, v]) => [k, +v.toFixed(2)])), grosores: f.grosores, deSistema: sistema(f.familia) })),
  googleFonts: datos.gfonts, fontFaces: datos.fontfaces,
  logo: logoRuta ? logoRuta.replace(process.cwd() + "/", "") : null, logosVistos: datos.logos.map(l => ({ tipo: l.tipo, src: l.src, alt: l.alt, ancho: l.ancho, alto: l.alto, enCabecera: l.enCabecera })),
  ogImage: datos.ogImage, favicon: datos.favicon,
  propuesta: {
    tipografia: { titular, texto, dato: mono || "JetBrains Mono (no la usa la web; una mono para cifras)", titularDeSistema: sistema(titular) },
    oscura: propuesta(fondoOscuro), clara: propuesta(fondoClaro),
    recomendada: webOscura ? "oscura" : "clara",
    nota: webOscura
      ? "La web es oscura: la piel oscura hereda su fondo tal cual; la clara es la alternativa por si el vídeo lo quiere luminoso."
      : "La web es clara: la piel clara hereda su fondo tal cual; la oscura es el mismo acento sobre carbón, que es lo habitual en reels. Se le enseñan las dos y elige.",
  },
  capturas: ["captura.png", "captura-entera.png", "captura-movil.png"].map(c => join(MARCA, c).replace(process.cwd() + "/", "")),
};
writeFileSync(join(MARCA, "web.json"), JSON.stringify(salida, null, 2));

// ── las dos pieles, escritas · el candado del fondo se quitó el 8 sep 2026 ──
// La web manda: de aquí salen marca-clara.css y marca-oscura.css con SU fondo,
// SU cielo y SU acento. La prueba se le enseña en las dos y elige (CLAUDE.md paso 4).
const MOTOR = dirname(fileURLToPath(import.meta.url));   // fileURLToPath y no .pathname: con espacios en la ruta, .pathname viene con %20
const pon = (css, token, valor) => css.replace(new RegExp(`(--${token}\\s*:)[^;]*;`), `$1${valor};`);
// EL CIELO SON LOS COLORES DE SU WEB. Se cogen los vivos que ya midió la página, por
// peso, quitando los que repiten tono (#0079ce y #006cb8 son el mismo azul), y sólo si
// no llegan a cuatro se rellena girando el acento (+34, -38, +96). Los tonos son suyos;
// la viveza y el brillo se igualan para que sean manchas de cielo y no rellenos planos.
// Girar 150° y saturar a tope daba un arcoíris de feria en cuanto el acento era vivo.
const tonosWeb = (() => { const out = [];
  for (const v of vivos) { const [h] = rgb2hsl(v.color);
    if (out.every(x => Math.min(Math.abs(x - h), 360 - Math.abs(x - h)) > 18)) out.push(h);
    if (out.length === 4) break; }
  return out; })();
const familiaCielo = claro => { const [hA, sA] = rgb2hsl(acento);
  const S = Math.min(Math.max(sA, 0.42), claro ? 0.80 : 0.86);
  const L = claro ? 0.66 : 0.52;
  const tonos = tonosWeb.slice();
  for (const d of [34, -38, 96]) { if (tonos.length >= 4) break;
    const h = hA + d; if (tonos.every(x => Math.min(Math.abs(((x - h) % 360 + 360) % 360), 360 - Math.abs(((x - h) % 360 + 360) % 360)) > 18)) tonos.push(h); }
  while (tonos.length < 4) tonos.push(hA + 34 * tonos.length);
  return tonos.slice(0, 4).map(h => hsl2rgb([h, S, L])); };
const fuerzaManchas = +Math.max(0.55, Math.min(1.05, 0.45 + sat(acento) * 0.6)).toFixed(2);
const titularCss = titular && !sistema(titular) ? `"${titular}",sans-serif` : null;
const datoCss = mono && !sistema(mono) ? `"${mono}",ui-monospace,monospace` : null;

// LAS TIPOGRAFÍAS VAN EN DOS SITIOS y es la trampa 19: si --titular dice una y el <link>
// carga otra, Chrome sustituye sin avisar y la pieza sale entera con la letra equivocada.
// Aquí se acaba: la fuente viaja DENTRO de marca.css, en un @import que se comprueba de
// verdad antes de escribirlo. Si Google no la tiene, no se pone y se dice en el resumen.
const pruebaGoogle = async (fam, intento = 0) => {
  const q = fam.trim().replace(/\s+/g, "+");
  for (const ejes of ["ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400", "wght@300;400;500;600;700;800", "wght@400;700", ""]) {
    const u = `https://fonts.googleapis.com/css2?family=${q}${ejes ? ":" + ejes : ""}&display=swap`;
    try { const r = await fetch(u, { headers: { "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36" } });
      if (r.ok && /@font-face/.test(await r.text())) return u; } catch { /* sin red: se sigue sin @import */ }
  }
  // un parpadeo de red deja la marca sin su tipografía y no se entera nadie: se reintenta
  if (intento === 0) { await new Promise(r => setTimeout(r, 900)); return pruebaGoogle(fam, 1); }
  return null;
};
const imports = [];
const faltan = [];
if (datos.gfonts.length) imports.push(...datos.gfonts);          // las suyas, tal cual las carga su web
else for (const fam of [titular, mono].filter(f => f && !sistema(f))) {
  const u = await pruebaGoogle(fam);
  if (u) imports.push(u); else faltan.push(fam);
}
const cabeceraImports = imports.map(u => `@import url("${u}");`).join("\n") + (imports.length ? "\n" : "");

const pieles = {};
for (const modo of ["clara", "oscura"]) {
  const q = salida.propuesta[modo];                       // P se declara más abajo, en el resumen
  const plantilla = readFileSync(join(MOTOR, modo === "clara" ? "marca-PLANTILLA.css" : "marca-PLANTILLA-oscura.css"), "utf8");
  const claro = modo === "clara";
  let css = plantilla;
  css = pon(css, "marca", `"${salida.nombre.replace(/"/g, "")}"`);
  css = pon(css, "acento", q.acento);
  css = pon(css, "fondo", q.fondo);
  css = pon(css, "tinta", q.tinta);
  css = pon(css, "tinta-baja", q.tintaBaja);
  // el cielo se tiñe del fondo medido: dos pasos hacia el acento y hacia la segunda mancha
  const [m1, m2, m3, m4] = familiaCielo(claro);
  css = pon(css, "cielo-a", mezcla(q.fondo, m1, claro ? 0.14 : 0.10));
  css = pon(css, "cielo-b", q.fondo);
  css = pon(css, "cielo-c", mezcla(q.fondo, m2, claro ? 0.12 : 0.09));
  css = pon(css, "mancha-1", m1); css = pon(css, "mancha-2", m2);
  css = pon(css, "mancha-3", m3); css = pon(css, "mancha-4", m4);
  css = pon(css, "manchas", claro ? fuerzaManchas : (fuerzaManchas * 0.72).toFixed(2));
  if (titularCss) css = pon(css, "titular", titularCss);
  if (datoCss) css = pon(css, "dato", datoCss);
  const ruta = join(DEST, `marca-${modo}.css`);
  writeFileSync(ruta, cabeceraImports + css);   // el @import va el primero o el navegador lo ignora
  pieles[modo] = ruta.replace(process.cwd() + "/", "");
}
// marca.css apunta a la recomendada: cuando elija en la prueba, se cambia esta línea
const elegida = salida.propuesta.recomendada === "clara" ? "clara" : "oscura";
writeFileSync(join(DEST, "marca.css"),
  `/* La piel elegida. Para cambiarla, cambia el nombre de esta línea:\n` +
  `   marca-clara.css  ·  marca-oscura.css  (las dos están escritas y medidas) */\n` +
  `@import url("marca-${elegida}.css");\n`);

// ── resumen ────────────────────────────────────────────────────────
const P = salida.propuesta;
console.log(`\n${salida.nombre}  ·  ${host}  ·  web ${webOscura ? "oscura" : "clara"} (fondo ${fondoWeb})`);
if (salida.h1.length) console.log(`H1: ${salida.h1[0]}`);
console.log(`\nColores (por peso; ★ = vivo):`);
for (const c of salida.colores.slice(0, 10)) console.log(`  ${c.color}  ${String(c.peso).padStart(6)}  ${gris(c.color) ? " " : "★"}  ${Object.entries(c.roles).map(([k, v]) => `${k} ${v}`).join(" · ")}`);
console.log(`\nTipografías:`);
for (const f of salida.fuentes.slice(0, 5)) console.log(`  ${f.familia}${f.deSistema ? " (de sistema)" : ""}  ${Object.entries(f.roles).map(([k, v]) => `${k} ${v}`).join(" · ")}  grosores ${Object.keys(f.grosores).join("/")}`);
if (salida.googleFonts.length) console.log(`  Google Fonts: ${salida.googleFonts.join("\n                ")}`);
console.log(`\nPropuesta (${P.recomendada}):`);
for (const v of ["oscura", "clara"]) { const q = P[v];
  console.log(`  ${v.padEnd(7)} fondo ${q.fondo} · tinta ${q.tinta} (${q.contraste.tinta}:1) · tinta-baja ${q.tintaBaja} (${q.contraste.tintaBaja}:1) · acento ${q.acento} (${q.contraste.acento}:1${q.acentoValeComoTexto ? ", vale como texto" : ", NO vale como texto"})`); }
console.log(`  titular ${titular || "?"}${sistema(titular) ? " (de sistema → elegir una grotesca en Google Fonts)" : ""} · texto ${texto || "?"} · dato ${P.tipografia.dato}`);
console.log(`\nLogo: ${salida.logo || "no encontrado (mira las capturas)"}`);
console.log(`Contacto: ${[...salida.contacto.tel, ...salida.contacto.mail, ...salida.contacto.whatsapp].join("  ") || "—"}`);
console.log(`\nLas dos pieles, ya escritas y medidas:`);
console.log(`  ${pieles.clara}\n  ${pieles.oscura}`);
console.log(`  marca.css → marca-${elegida}.css (la recomendada; se cambia tras la prueba)`);
console.log(`\nCómo escribe (la muestra para el tono · guion/tono.md):`);
for (const h of [...salida.h1, ...salida.h2].slice(0, 6)) console.log(`  «${h.replace(/\s+/g, " ").slice(0, 96)}»`);
if (salida.descripcion) console.log(`  meta: «${salida.descripcion.slice(0, 110)}»`);
if (salida.nav.length) console.log(`  sus palabras (menú): ${salida.nav.join(" · ")}`);
console.log(`  cielo: ${tonosWeb.length} tono${tonosWeb.length === 1 ? "" : "s"} sacado${tonosWeb.length === 1 ? "" : "s"} de su web${tonosWeb.length < 4 ? ` + ${4 - tonosWeb.length} girando el acento (su web no tiene más colores)` : ""}`);
console.log(imports.length
  ? `  tipografías dentro del CSS (${imports.length} @import comprobados): ya no hay que tocar el <link> de la pieza`
  : `  sin @import de tipografías${faltan.length ? ` · Google no tiene ${faltan.join(", ")}: elige una parecida y ponla en el <link>` : " · la web usa fuentes de sistema: elige una grotesca"}`);
console.log(`Capturas: ${salida.capturas.join("  ")}`);
console.log(`Todo: ${join(MARCA, "web.json").replace(process.cwd() + "/", "")}\n`);
