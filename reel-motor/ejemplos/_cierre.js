/* ═══ el cierre de los ejemplos ═══════════════════════════════════════
   Los seis ejemplos se escribieron con una cola de venta compartida. Aquí
   la cola se sustituye por el cierre de marca del motor, con la misma
   interfaz: COLA.montar({M, cabeza}) → {seek(t), SFX, T, fin}.
   La cabeza se encoge en M.esto (la frase donde empezaba la cola) y entra
   el cierre. Así cada ejemplo es una pieza completa por sí sola.        */
window.COLA=(function(){
  const CSS=`
.x-scrim{position:absolute;inset:0;background:var(--fondo);opacity:0;z-index:50}
.x-cierre{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;opacity:0;z-index:51}
.x-cierre .frase{font-size:50px;font-weight:600;letter-spacing:-.022em;line-height:1.18;max-width:700px;text-wrap:balance}
.x-cierre .marca{font-size:46px;font-weight:600;letter-spacing:-.012em;margin-top:76px}
.x-cierre .marca i{font-style:normal;color:var(--acento)}`;
  const HTML=`<div class="x-scrim" id="xScrim"></div>
<div class="x-cierre" id="xCierre"><p class="frase">Tu producto, en movimiento.</p><p class="marca">Tu marca<i>.</i></p></div>`;
  function montar(opt){
    const M=opt.M, cabeza=document.getElementById(opt.cabeza||'cabeza'), reel=document.getElementById('reel'), escena=document.getElementById('escena');
    const st=document.createElement('style'); st.textContent=CSS; document.head.appendChild(st);
    reel.insertAdjacentHTML('beforeend',HTML);
    const S=document.getElementById('xScrim'), C=document.getElementById('xCierre');
    const T={ sale:[M.esto-0.10,M.esto+0.62], cierre:[M.esto+0.30,M.esto+0.85], movil:[M.esto+0.3,M.esto+0.9], suelta:[M.esto,M.esto+0.3], coge:[M.esto,M.esto+0.3] };
    function seek(t){
      const kS=easeInOut(p(t,T.sale[0],T.sale[1]));
      if(cabeza){ cabeza.style.opacity=1-kS; cabeza.style.filter=`blur(${kS*20}px)`; cabeza.style.transformOrigin='540px 900px'; cabeza.style.transform=`scale(${mix(1,0.6,kS)})`; }
      const v=easeOut(p(t,T.cierre[0],T.cierre[1]));
      S.style.opacity=v*0.78; escena.style.opacity=1-v;
      const kz=easeOut(p(t,T.cierre[0]+0.16,T.cierre[0]+0.78));
      C.style.opacity=kz; C.style.transform=`translateY(${mix(26,0,kz)}px)`; C.style.filter=`blur(${mix(14,0,kz)}px)`;
      return v;
    }
    const SFX=[['swipe',T.sale[0],0.22],['golpe',T.cierre[0],0.44,0.7]];
    return {seek,SFX,T,fin:T.cierre[1]+2.4};
  }
  return {montar};
})();
