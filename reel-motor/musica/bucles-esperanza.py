"""Las camas que tienen que hacer sentir algo: esperanza.

  python3 bucles-esperanza.py carpeta [emocion-organo emocion-amanecer energia-himno]

La esperanza en música no es suerte, son cuatro recursos concretos, y aquí se
usan a propósito:

1. **La melodía sube.** Cada frase remata más arriba que la anterior y la pieza
   llega a su nota más alta cerca del final. Bajar es resignación; subir es
   esperanza. El script lo comprueba e imprime los picos.
2. **El cuarto grado sostenido** (modo lidio): el sonido de «asombro» de
   el cine de aventuras. Va como nota de paso en la melodía, no en
   el acorde.
3. **Suspensiones que resuelven**: el acorde llega con la cuarta y baja a la
   tercera. Es una promesa cumplida, en pequeño, cada dos compases.
4. **Menor que se vuelve mayor**: la misma melodía, primero armonizada oscura y
   después con luz. Es el recurso entero de `amanecer`.

Se apoya en el banco de instrumentos de `bucles-club.py` (órgano, cuerdas,
piano, supersaw, bombo, sidechain) para no repetirlo.

emocion-organo · Re MAYOR (lidio) · 92  · órgano en corcheas y cuerdas que se suman.
            Sin batería.
amanecer  · Si m → Re MAYOR · 76 · la misma melodía dos veces: la segunda con
            luz. La más lenta y la más emotiva.
faro      · Mi MAYOR · 122 · esperanza con pulso: el bombo y el sidechain de
            club debajo de un himno que sube. El puente entre las dos cosas.
"""
import importlib.util, pathlib, sys
import numpy as np

AQUI = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("club", AQUI/"bucles-club.py")
club = importlib.util.module_from_spec(spec); sys.modules["club"] = club
ARGV = list(sys.argv)                                   # el mío, antes de pisarlo
sys.argv = [sys.argv[0], str(AQUI)]                    # que club no renderice al importarlo
spec.loader.exec_module(club)

SR=club.SR; f_of=club.f_of; Ctx=club.Ctx
env=club.env; additive=club.additive; saw_harm=club.saw_harm
lowpass=club.lowpass; highpass=club.highpass; place=club.place; delay_circ=club.delay_circ
cuerdas=club.cuerdas; spicc=club.spicc; piano=club.piano; metal=club.metal
supersaw=club.supersaw; pluck_syn=club.pluck_syn; bajo=club.bajo; sub=club.sub
kick=club.kick; clap=club.clap; hat=club.hat; subida=club.subida; reves=club.reves
por_tramos=club.por_tramos; bombeo=club.bombeo
rng=club.rng

ORGANO=[1,0.6,0.45,0.28,0.16,0.09,0.05]
def organo(f,n):
    return (additive(f,n,ORGANO,rand_phase=False)+0.7*additive(f,n,ORGANO,detune=0.0035))*env(n,0.006,0.07)
def coro(f,n):
    """Voces: da el «algo grande» sin sonar a iglesia si va bajo."""
    kmax=int(min(4200,SR*0.45)/f)
    F=lambda x: 0.04+np.exp(-0.5*((x-640)/110)**2)+np.exp(-0.5*((x-1120)/150)**2)+0.5*np.exp(-0.5*((x-2600)/260)**2)
    harm=[float(F(f*k))/k**0.6 for k in range(1,kmax+1)]
    sig=sum(additive(f,n,harm,detune=d,vib=0.005,vrate=4.6+rng.uniform(-0.3,0.3)) for d in (-0.006,-0.002,0.003,0.007))/4
    return lowpass(sig,4200)*env(n,0.9,1.0)

def sus_pad(c, buf, b, root, tercera, n, g=1.0, sus=True):
    """El acorde con la cuarta que baja a la tercera: la promesa que se cumple."""
    t=np.arange(n)/SR
    cambio=np.clip((t-c.bar*0.45)/0.25,0,1) if sus else np.ones(n)
    for iv,gg in [(24,1.0),(31,0.8),(36,0.5)]:
        for ch,d in enumerate((-0.005,0.005)):
            s0=c.at(b); buf[ch,s0:s0+n]+=cuerdas(f_of(root+iv)*(1+d),n)*gg*g*env(n,0.5,0.7)
    for ch,d in enumerate((-0.004,0.004)):
        s0=c.at(b)
        cuarta=cuerdas(f_of(root+29)*(1+d),n)*env(n,0.4,0.6)      # la 4ª
        terc  =cuerdas(f_of(root+24+tercera)*(1+d),n)*env(n,0.4,0.6)
        buf[ch,s0:s0+n]+=(cuarta*(1-cambio)+terc*cambio)*0.75*g

def picos(MEL):
    """Comprueba que la melodía sube: el pico de cada frase, en orden."""
    fr={}
    for b,s,n,d in MEL: fr.setdefault(b//4,[]).append(n)
    return [max(v) for k,v in sorted(fr.items())]

# ── 14 · emocion-organo · Re mayor lidio, órgano y cuerdas, sin batería ─────────
def r_cornfield():
    c=Ctx(92,16)
    P=[(38,4),(38,4),(33,4),(33,4),(35,3),(35,3),(31,4),(31,4),
       (38,4),(38,4),(33,4),(33,4),(31,4),(31,4),(33,4),(33,4)]     # D A Bm G · D A G A
    ARP=[0,7,12,16,12,7,12,16]                                       # corcheas, como el maíz
    org=c.new(); pad=c.new(); mel=c.new(); bajo_=c.new(); vo=c.new()
    for b,(r,t3) in enumerate(P):
        for e8 in range(8):
            g=0.55 if b<4 else (0.8 if b<8 else 1.0)
            acc=1.0 if e8%4==0 else 0.75
            place(org,c.at(b,e8*2),organo(f_of(r+36+ARP[e8]),int(c.step*1.9*SR))*g*acc,0.5+0.16*np.sin(2*np.pi*e8/8))
        n=int((c.bar+0.8)*SR)
        if b>=4: sus_pad(c,pad,b,r,t3,n,g=0.7 if b<8 else 1.0)
        place(bajo_,c.at(b),sub(f_of(r),int(c.bar*1.02*SR))*(0.6 if b<8 else 0.9),0.5)
        if b>=12:
            for ch,d in enumerate((-0.004,0.004)):
                s0=c.at(b); vo[ch,s0:s0+n]+=coro(f_of(r+36)*(1+d),n)*0.5
    # la melodía sube y toca el 4º sostenido (sol#) de paso: el «asombro»
    MEL=[(8,0,78,8),(8,8,81,8), (9,0,80,4),(9,4,81,12),
         (10,0,83,8),(10,8,81,8), (11,0,78,16),
         (12,0,81,8),(12,8,83,8), (13,0,86,16),
         (14,0,85,8),(14,8,83,8), (15,0,81,8),(15,8,78,8)]
    for b,s,nota,dur in MEL:
        n=int(dur*c.step*SR*1.25)
        place(mel,c.at(b,s),cuerdas(f_of(nota),n)*env(n,0.18,0.35)*0.9,0.5)
        place(mel,c.at(b,s),piano(f_of(nota+12))*0.35,0.5)
    L=dict(org=org,pad=pad,mel=mel,baj=bajo_,vo=vo)
    G=dict(org=(0.6,0.4),pad=(0.55,0.4),mel=(0.6,0.5),baj=(0.5,0.0),vo=(0.4,0.5))
    return c,L,G,[],2.2,set(),MEL

# ── 15 · amanecer · la misma melodía, primero en menor y después en mayor ──
def r_amanecer():
    c=Ctx(76,16)
    OSCURO=[(35,3),(35,3),(31,4),(31,4),(40,3),(40,3),(35,3),(35,3)]   # Bm G Em Bm
    LUZ   =[(38,4),(38,4),(33,4),(33,4),(31,4),(31,4),(38,4),(38,4)]   # D  A G  D
    P=OSCURO+LUZ
    # una sola melodía; se repite igual en los dos tramos y es la armonía la que cambia
    MOTIVO=[(0,0,74,8),(0,8,76,8), (1,0,78,8),(1,8,76,8), (2,0,74,16),
            (3,0,71,8),(3,8,74,8), (4,0,76,16), (5,0,78,8),(5,8,81,8),
            (6,0,78,16), (7,0,74,16)]
    MEL=MOTIVO+[(b+8,s,n,d) for b,s,n,d in MOTIVO]
    pad=c.new(); mel=c.new(); pia=c.new(); baj=c.new(); vo=c.new(); mtl=c.new()
    for b,(r,t3) in enumerate(P):
        n=int((c.bar+1.0)*SR)
        sus_pad(c,pad,b,r,t3,n,g=0.75 if b<8 else 1.0)
        place(baj,c.at(b),sub(f_of(r),int(c.bar*1.02*SR))*(0.7 if b<8 else 0.95),0.5)
        for s in (0,8): place(pia,c.at(b,s),piano(f_of(r+24))*(0.5 if b<8 else 0.75),0.5)
        if b>=8:
            for ch,d in enumerate((-0.004,0.004)):
                s0=c.at(b); vo[ch,s0:s0+n]+=coro(f_of(r+36)*(1+d),n)*0.55
        if b in (12,14): place(mtl,c.at(b),metal(f_of(r+12),int(c.bar*0.9*SR)),0.5)
    for b,s,nota,dur in MEL:
        n=int(dur*c.step*SR*1.3); alto=b>=8
        place(mel,c.at(b,s),cuerdas(f_of(nota+(12 if alto else 0)),n)*env(n,0.22,0.4)*(0.8 if not alto else 1.0),0.5)
        place(mel,c.at(b,s),piano(f_of(nota+12))*(0.3 if not alto else 0.45),0.5)
    # el tramo oscuro va más abajo y sin brillo: la luz tiene que notarse en el
    # cuerpo, no sólo en la armonía
    GAN=[0.5]*4+[0.62]*4+[1.0]*8
    pad,mel,pia,baj=(por_tramos(c,z,GAN) for z in (pad,mel,pia,baj))
    L=dict(pad=pad,mel=mel,pia=pia,baj=baj,vo=vo,mtl=mtl)
    G=dict(pad=(0.55,0.45),mel=(0.6,0.5),pia=(0.45,0.5),baj=(0.5,0.0),vo=(0.45,0.55),mtl=(0.4,0.4))
    return c,L,G,[],2.6,set(),MEL

# ── 16 · faro · el pulso de club debajo de un himno que sube ─────────────
def r_faro():
    c=Ctx(122,16)
    P=[(40,4),(40,4),(35,4),(35,4),(37,3),(37,3),(33,4),(33,4)]*2      # E B C#m A
    K=[c.at(b,s) for b in range(4,16) for s in (0,4,8,12)]
    MEL=[(8,0,76,6),(8,6,80,2),(8,8,83,8), (9,0,80,8),(9,8,83,8),
         (10,0,85,6),(10,6,83,2),(10,8,80,8), (11,0,83,16),
         (12,0,80,6),(12,6,83,2),(12,8,85,8), (13,0,83,8),(13,8,88,8),
         (14,0,87,8),(14,8,85,8), (15,0,83,16)]
    bat=c.new(); baj=c.new(); pad=c.new(); mel=c.new(); acor=c.new(); pia=c.new(); ef=c.new()
    for k in K: place(bat,k,kick(f0=155,f1=48,td=0.11),0.5)
    for b in range(8,16):
        for s in (4,12): place(bat,c.at(b,s),clap(),0.5)
    for b in range(6,16):
        for s in range(2,16,4): place(bat,c.at(b,s),hat(s%8==6),0.45 if s%8==2 else 0.55)
    for b,(r,t3) in enumerate(P):
        n=int((c.bar+0.8)*SR)
        sus_pad(c,pad,b,r,t3,n,g=0.6 if b<8 else 1.0)
        place(baj,c.at(b),sub(f_of(r),int(c.bar*1.02*SR))*(0.55 if b<8 else 0.9),0.5)
        if b>=8:
            for s in range(2,16,4): place(baj,c.at(b,s),bajo(f_of(r+12),int(c.step*1.6*SR)),0.5)
            nn=int(c.beat*0.95*SR)
            for s in (0,4,8,12):
                for iv in (24,24+t3,31):
                    place(acor,c.at(b,s),supersaw(f_of(r+iv),nn)*env(nn,0.010,0.10)*0.45,0.5)
        for s in (0,6,10):
            place(pia,c.at(b,s),piano(f_of(r+24))*(0.5 if b<8 else 0.35),0.5)
    for b,s,nota,dur in MEL:
        n=int(dur*c.step*SR*1.2)
        place(mel,c.at(b,s),cuerdas(f_of(nota),n)*env(n,0.10,0.25)*0.85,0.5)
        place(mel,c.at(b,s),supersaw(f_of(nota),n)*env(n,0.012,0.10)*0.30,0.5)
    place(ef,c.at(8)-int(2.4*SR),subida(2.4),0.5)
    place(ef,c.at(8)-int(1.5*SR),reves(1.5),0.5)
    GAN=[0.55]*4+[0.78]*4+[1.0]*8
    pad,baj=(por_tramos(c,z,GAN) for z in (pad,baj))
    L=dict(bat=bat,baj=baj,pad=pad,mel=mel,acor=acor,pia=pia,ef=ef)
    G=dict(bat=(0.85,0.12),baj=(0.65,0.05),pad=(0.5,0.45),mel=(0.62,0.45),acor=(0.38,0.4),pia=(0.4,0.45),ef=(0.4,0.45))
    return c,L,G,K,1.9,{"baj","pad","acor","pia"},MEL

RECETAS={"emocion-organo":r_cornfield,"emocion-amanecer":r_amanecer,"energia-himno":r_faro}   # nombres genéricos
PEDIDOS=[a for a in ARGV[1:] if a in RECETAS] or list(RECETAS)
DEST=pathlib.Path(ARGV[1]) if len(ARGV)>1 and ARGV[1] not in RECETAS else AQUI

for nombre in PEDIDOS:
    receta=RECETAS[nombre]
    MEL=receta()[-1]
    y=club.render(nombre, receta=lambda r=receta: r()[:-1], OUT=DEST)
    print(f"          picos de cada frase: {picos(MEL)}  ({'sube' if picos(MEL)[-1]>picos(MEL)[0] else 'NO SUBE'})")
