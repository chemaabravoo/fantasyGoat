// energia.mjs · ¿esto se ve animado, o sólo se mueve?
//
//   node ../../motor/energia.mjs pieza.html
//
// Muestrea la pieza cada 0,25 s y mide CUÁNTO cambia la escena de una muestra a la
// siguiente, sin contar el cielo. Da dos números:
//
//   energía media   por debajo de 15 la pieza se siente plana; 25-35 es lo normal
//                   en el estilo de la casa; por encima de 45, probablemente marea.
//   tramos flojos   los segundos en los que casi nada se mueve. Más de un tercio de
//                   la pieza en flojo y se va a notar, aunque cada fotograma suelto
//                   esté bien compuesto.
//
// POR QUÉ NO VALE «¿hay dos fotogramas idénticos?»: la cámara respira, así que nunca
// los hay. Medido el 8 sep 2026 sobre dos versiones del mismo anuncio: por esa cuenta
// las dos daban 0 % de fotogramas repetidos, y una de las dos era claramente cutre.
// Lo que el ojo lee como «se mueve» es la MAGNITUD del cambio, no que cambie algo.
//
//   la cutre  ·  energía 12,4  ·  41 s de 56 en flojo (73 %)
//   la buena  ·  energía 28,3  ·  21,5 s de 56 (38 %)
import puppeteer from "puppeteer-core";
import { exigirChrome } from "./chrome.mjs";
import { resolve } from "node:path";
const b = await puppeteer.launch({executablePath:exigirChrome(),headless:"new",
  args:["--allow-file-access-from-files"],defaultViewport:{width:1080,height:1920}});
const pg = await b.newPage();
await pg.goto("file://"+resolve(process.argv[2]),{waitUntil:"networkidle0"});
await pg.evaluate(()=>document.fonts.ready); await new Promise(r=>setTimeout(r,500));
const dur = await pg.evaluate(()=>window.DURACION);
const muestras=[];
for(let t=0;t<=dur;t+=0.25){
  muestras.push(await pg.evaluate(tt=>{ window.seek(tt);
    const reel=document.getElementById('reel'); const m=new Map();
    let i=0;
    for(const e of reel.querySelectorAll('*')){
      const cls=(typeof e.className==='string'?e.className:'')+' '+(e.id||'');
      if(/cielo|banda|bruma|grano|mota|\bb[1-4]\b/.test(cls)) continue;
      const s=getComputedStyle(e), r=e.getBoundingClientRect();
      if(r.width<3||r.height<3||+s.opacity<0.04) continue;
      m.set((e.id||e.tagName)+'#'+(i++), [r.left,r.top,r.width,r.height,+s.opacity*100]);
    } return [...m]; }, +t.toFixed(2)));
}
const energias=[];
for(let i=1;i<muestras.length;i++){
  const a=new Map(muestras[i-1]), b2=new Map(muestras[i]); let d=0, n=0;
  for(const [k,v] of b2){ const w=a.get(k); if(!w) { d+=60; n++; continue; }
    d+=Math.abs(v[0]-w[0])+Math.abs(v[1]-w[1])+Math.abs(v[2]-w[2])+Math.abs(v[3]-w[3])+Math.abs(v[4]-w[4]); n++; }
  energias.push(n?d/n:0);
}
const media=energias.reduce((a,b)=>a+b,0)/energias.length;
const flojos=energias.filter(e=>e<3).length;
const pct=100*flojos/energias.length;
const juicio = media<15 ? "PLANA · mírala con contactos.mjs: seguro que hay tramos donde sólo se mueve la cámara"
            : media<22 ? "justa · funciona, pero le falta una capa"
            : media<45 ? "bien · en el rango del estilo de la casa"
                       : "muy alta · comprueba que no sea ruido";
console.log(`${(process.argv[3]||"pieza")}  ${dur.toFixed(1)} s`);
console.log(`  energía media  ${media.toFixed(1)}   → ${juicio}`);
console.log(`  tramos flojos  ${(flojos*0.25).toFixed(1)} s de ${dur.toFixed(1)} (${pct.toFixed(0)} %)`
  + (pct>45 ? "   ← más de un tercio en flojo: ahí está lo que se ve cutre" : ""));
await b.close();
