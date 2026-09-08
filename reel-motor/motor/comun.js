/* ═══ lo común a los cinco vídeos · curvas, ayudantes, el cielo y el reproductor ═══ */
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const p=(t,a,b)=>clamp((t-a)/(b-a),0,1);
const mix=(a,b,k)=>a+(b-a)*k;
function bez(x1,y1,x2,y2){
  const cx=3*x1,bx=3*(x2-x1)-cx,ax=1-cx-bx, cy=3*y1,by=3*(y2-y1)-cy,ay=1-cy-by;
  return x=>{ if(x<=0)return 0; if(x>=1)return 1; let u=x;
    for(let i=0;i<8;i++){ const e=((ax*u+bx)*u+cx)*u-x; if(Math.abs(e)<1e-7)break;
      const d=(3*ax*u+2*bx)*u+cx; if(Math.abs(d)<1e-7)break; u-=e/d; }
    return ((ay*u+by)*u+cy)*u; };
}
const easeOut=bez(.23,1,.32,1), easeInOut=bez(.77,0,.175,1), easeCae=bez(.5,0,.85,.45);
const arco=(k,alto)=>Math.sin(k*Math.PI)*alto;
const respira=(t,amp,hz,fase)=>Math.sin(t*(hz||0.12)*6.283185+(fase||0))*amp;
const pulso=k=>(k>0&&k<1)?Math.sin(k*Math.PI):0;
const spring=(k,z=0.42,w=13)=>k<=0?0:k>=1?1:1-Math.exp(-z*w*k)*Math.cos(w*Math.sqrt(1-z*z)*k);
const shake=(t,t0,amp)=>t<t0?0:amp*Math.exp(-(t-t0)*9)*Math.sin((t-t0)*70);
const hash=n=>{const x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x);};
const frame=t=>Math.round(t*window.FPS);
const lerpCol=(a,b,k)=>{const h=c=>[parseInt(c.slice(1,3),16),parseInt(c.slice(3,5),16),parseInt(c.slice(5,7),16)];
  const A=h(a),B=h(b);return`rgb(${A.map((v,i)=>Math.round(mix(v,B[i],k))).join(',')})`;};
const blurIn=(n,k,dy=24)=>{n.style.opacity=k;n.style.filter=`blur(${mix(14,0,k)}px)`;n.style.transform=`translateY(${mix(dy,0,k)}px)`;};
const palabras=(sp,t,a,paso,dur,sal=1,dy=26)=>sp.forEach((s,i)=>{
  const k=easeOut(p(t,a+i*paso,a+i*paso+dur));s.style.opacity=k*sal;
  s.style.filter=`blur(${mix(16,0,k)}px)`;
  s.style.transform=`translateY(${mix(dy,0,k)}px) scale(${mix(0.94,1,k)})`;});
function odo(node,viejo,nuevo,k,H){
  const L=Math.max(viejo.length,nuevo.length); viejo=viejo.padStart(L,' '); nuevo=nuevo.padStart(L,' ');
  let h='';
  for(let c=0;c<L;c++){const ch=nuevo[c],old=viejo[c];const ref=(k<=0?old:ch)!==' '?(k<=0?old:ch):(ch!==' '?ch:old);
    const cls=(ref===','||ref==='.'||ref===':'||ref===' ')?'col s':ref==='€'?'col e':'col';
    if(ch===old||k>=1||k<=0){h+=`<div class="${cls}"><span>${k<=0?old:ch}</span></div>`;}
    else{const y=mix(0,-H,k),bl=pulso(k)*6;h+=`<div class="${cls}" style="filter:blur(${bl}px)"><span style="transform:translateY(${y}px)">${old}</span><span style="transform:translateY(${y+H}px)">${ch}</span></div>`;}}
  node.innerHTML=h;
}
function odoPasos(node,pasos,t,H,dur=0.45){let i=0;for(let n=0;n<pasos.length;n++) if(t>=pasos[n][0]) i=n;
  const prev=pasos[Math.max(0,i-1)][1],cur=pasos[i][1];
  const k=i===0?1:easeOut(p(t,pasos[i][0],pasos[i][0]+dur));odo(node,prev,cur,k,H);}
function cursor(c,g0,g1,g2,an,t,a,b,x0,y0,x1,y1,tap,sal=1){
  const f=tt=>easeOut(p(tt,a,b)); const k=f(t);
  const cx=k=>mix(x0,x1,k)+arco(k,-50), cy=k=>mix(y0,y1,k);
  c.style.opacity=(t>=a?1:0)*sal; c.style.transform=`translate(${cx(k)}px,${cy(k)}px)`;
  const k1=f(t-1/60),k2=f(t-2/60),gh=(k>0&&k<1)?1:0;
  g1.style.transform=`translate(${cx(k1)-cx(k)}px,${cy(k1)-cy(k)}px)`;
  g2.style.transform=`translate(${cx(k2)-cx(k)}px,${cy(k2)-cy(k)}px)`;
  g1.style.opacity=gh*0.35; g2.style.opacity=gh*0.18;
  const kt=p(t,tap,tap+0.32); an.style.opacity=pulso(kt)*0.9; an.style.transform=`scale(${mix(0.5,1.9,easeOut(kt))})`;
  g0.style.transform=`scale(${1-pulso(p(t,tap,tap+0.14))*0.15})`;
}
const camara=(s,wx,wy,sx,sy)=>'translate('+(sx-s*wx)+'px,'+(sy-s*wy)+'px) scale('+s+')';
function guion(lista){ const T={}; let ini=0,fin=0;
  for(const [k,pos,dur=0] of lista){ const s=String(pos);
    const a = s==='<'?ini : s[0]==='<'?ini+parseFloat(s.slice(1))
            : s.slice(0,2)==='+='?fin+parseFloat(s.slice(2)) : parseFloat(s);
    T[k]=[+a.toFixed(3),+(a+dur).toFixed(3)]; ini=a; fin=a+dur; }
  return T; }
const caja=(n,L,Tp,W,H,R)=>{n.style.left=L+'px';n.style.top=Tp+'px';n.style.width=W+'px';
  n.style.height=H+'px';n.style.borderRadius=R+'px';};
const $=id=>document.getElementById(id);
Object.assign(window,{clamp,p,mix,easeOut,easeInOut,easeCae,arco,respira,pulso,spring,shake,hash,
  frame,lerpCol,blurIn,palabras,odo,odoPasos,cursor,camara,guion,caja,$});

/* el cielo: se pinta una vez y late siempre */
const CIELO_HTML=`<div class="cielo" id="cielo"><i class="b b1" id="b1"></i><i class="b b2" id="b2"></i>
<i class="b b3" id="b3"></i><i class="b b4" id="b4"></i><i class="banda" id="banda"></i></div><div class="bruma"></div>`;
function cieloSeek(t){
  const c=$('cielo');
  $('b1').style.transform=`translate(${respira(t,120,0.033)}px,${respira(t,84,0.047,1.1)}px) scale(${1+respira(t,0.13,0.029,0.4)})`;
  $('b2').style.transform=`translate(${respira(t,-140,0.026,2.2)}px,${respira(t,110,0.038,0.3)}px) scale(${1+respira(t,0.15,0.023,1.9)})`;
  $('b3').style.transform=`translate(${respira(t,96,0.041,4.1)}px,${respira(t,-130,0.031,2.7)}px) scale(${1+respira(t,0.17,0.036,3.3)})`;
  $('b4').style.transform=`translate(${respira(t,-110,0.036,1.4)}px,${respira(t,92,0.024,5.0)}px) scale(${1+respira(t,0.14,0.043,2.1)})`;
  $('banda').style.transform=`translateX(${((t*126)%2400)-300}px) rotate(${14+respira(t,7,0.018)}deg)`;
  $('banda').style.opacity=0.20+0.16*Math.sin(t*0.34);
  c.style.transform=`rotate(${respira(t,2.2,0.012)}deg) scale(${1+respira(t,0.05,0.017,2.4)})`;
}
const CURSOR_HTML=`<div class="cur" id="cur"><span class="g" id="cg2"></span><span class="g" id="cg1"></span><span class="p" id="cg0"></span><span class="an" id="can"></span></div>`;
Object.assign(window,{CIELO_HTML,cieloSeek,CURSOR_HTML});

/* el reproductor de la página · bajo captura arranca parado */
function arrancar(){
  window.seek(0);
  let playing=!navigator.webdriver, t0=performance.now();
  (function bucle(){requestAnimationFrame(bucle);
    if(!playing)return; const t=((performance.now()-t0)/1000)%window.DURACION; window.seek(t);})();
  document.addEventListener('keydown',e=>{if(e.code==='Space'){playing=!playing;t0=performance.now();}});
}
window.arrancar=arrancar;
