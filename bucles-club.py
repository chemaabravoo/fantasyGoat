"""Tres camas con pulso de club: orquesta encima, bombo debajo.
Orquesta encima, bombo debajo.

  python3 bucles-club.py carpeta [energia-orquesta energia-eco energia-piano energia-palmas]

Lo que estas tres tienen y las diez cinematográficas no: bombo a cuatro por
tiempo, **sidechain** (todo se agacha en cada bombo: es el bombeo del género),
supersaws, plucks con caída de filtro, subidas y un golpe de caída. La forma es
la del género: 4 compases de aire, 4 de subida y 8 de caída, y al volver al
principio del bucle se cae otra vez al aire — que es justo como suenan estos
temas en bucle.

energia-orquesta · F# menor · 130 · orquesta y techno: ostinato de cuerdas, bajo rodando
         a contratiempo, metales a golpes. Oscuro y sin melodía.
energia-eco · Si menor · 128 · melodía y hueco: pluck con eco, mucho silencio,
         reverb enorme y un lead de supersaw que dobla la melodía en la caída.
energia-piano · Re MAYOR · 126 · piano y euforia: acordes de piano sincopados, palmas,
         y un pluck cantando la melodía sobre acordes de supersaw.
"""
import numpy as np, wave, sys, pathlib
SR = 44100; rng = np.random.default_rng(23)
f_of = lambda n: 440.0*2**((n-69)/12)
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
PEDIDOS = sys.argv[2:]          # vacío = todas las de RECETAS

class Ctx:
    def __init__(s, bpm, nbars):
        s.bpm=bpm; s.beat=60/bpm; s.bar=4*s.beat; s.step=s.bar/16; s.nbars=nbars
        s.L=int(round(nbars*s.bar*SR)); s.T=s.L/SR
    def new(s): return np.zeros((2, 2*s.L))
    def at(s, bar, step=0.0): return int(round((bar*s.bar + step*s.step)*SR))
    def fold(s, b): return b[:, :s.L] + b[:, s.L:2*s.L]

def env(n,a,r,curve=1.5):
    e=np.ones(n); na=min(n,int(a*SR)); nr=min(n,int(r*SR))
    if na>0: e[:na]=np.linspace(0,1,na)**curve
    if nr>0: e[-nr:]*=np.linspace(1,0,nr)**curve
    return e
def additive(freq,n,harm,detune=0.0,rand_phase=True,vib=0.0,vrate=5.5):
    t=np.arange(n)/SR
    ph=2*np.pi*np.cumsum(freq*(1+detune)*(1+vib*np.sin(2*np.pi*vrate*t)))/SR if vib else 2*np.pi*freq*(1+detune)*t
    out=np.zeros(n)
    for k,a in enumerate(harm,1):
        if freq*k*(1+detune)>SR*0.45: break
        out+=a*np.sin(k*ph+(rng.uniform(0,2*np.pi) if rand_phase else 0.0))
    return out
def saw_harm(f,fc=5000): return [1/k for k in range(1,max(1,int(min(fc,SR*0.45)/f))+1)]
def sq_harm(f,fc=5000): return [(1/k if k%2 else 0.0) for k in range(1,max(1,int(min(fc,SR*0.45)/f))+1)]
def lowpass(x,fc,order=2):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); return np.fft.irfft(X/np.sqrt(1+(f/fc)**(2*order)),n=len(x))
def highpass(x,fc,order=2):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); return np.fft.irfft(X*(1-1/np.sqrt(1+(f/fc)**(2*order))),n=len(x))
def place(buf,start,sig,pan=0.5):
    n=min(len(sig),buf.shape[1]-start)
    if n>0: buf[0,start:start+n]+=sig[:n]*np.sqrt(1-pan); buf[1,start:start+n]+=sig[:n]*np.sqrt(pan)
def delay_circ(x,L,d,g,taps=4):
    y=x.copy()
    for k in range(1,taps+1): y[:,:L]+=np.roll(x[:,:L],d*k,axis=1)*g**k
    return y

# ── la percusión ──────────────────────────────────────────────────────────
def kick(dur=0.42, f0=155, f1=47, tp=0.055, td=0.115):
    n=int(dur*SR); t=np.arange(n)/SR
    f=f1+(f0-f1)*np.exp(-t/tp)                       # la caída de tono es el bombo
    cuerpo=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/td)
    click=highpass(rng.normal(size=n),1800)*np.exp(-t/0.0018)*0.45
    return np.tanh((cuerpo+click)*1.5)*0.95
def clap(dur=0.42):
    n=int(dur*SR); t=np.arange(n)/SR
    cuerpo=highpass(lowpass(rng.normal(size=n),7000),700)
    e=np.exp(-t/0.075)
    y=cuerpo*e
    for k,(r,g) in enumerate(zip((0.010,0.021,0.031),(0.7,0.5,0.35))):   # los tres rebotes del aplauso
        d=int(r*SR); y[d:]+=cuerpo[:-d]*np.exp(-t[:-d]/0.012)*g
    return y*0.8
def hat(abierto=False):
    dur=0.20 if abierto else 0.055; n=int(dur*SR); t=np.arange(n)/SR
    y=highpass(rng.normal(size=n),7500)
    return y*np.exp(-t/(0.075 if abierto else 0.011))*0.55

# ── los sintes ────────────────────────────────────────────────────────────
def supersaw(f,n,voces=7,det=0.14,fc=6500):
    """El acorde-lead del género: siete sierras desafinadas repartidas en estéreo."""
    out=np.zeros(n)
    for i in range(voces):
        d=det*((i-(voces-1)/2)/max(1,(voces-1)/2))*0.01
        out+=additive(f,n,saw_harm(f*(1+d),fc),detune=d)
    return lowpass(out/voces,fc)
def pluck_syn(f,n,brillo=4200,tau=0.16):
    """Sierra con caída de filtro, hecha cruzando una copia clara y una oscura."""
    raw=additive(f,n,saw_harm(f,brillo),rand_phase=False)+0.45*additive(f,n,sq_harm(f,brillo),rand_phase=False,detune=0.004)
    t=np.arange(n)/SR; claro=lowpass(raw,brillo); oscuro=lowpass(raw,420)
    y=oscuro+(claro-oscuro)*np.exp(-t/0.085)
    return y*np.exp(-t/tau)*np.minimum(1,t/0.002)
def bajo(f,n,fc=900):
    t=np.arange(n)/SR
    raw=additive(f,n,saw_harm(f,2400),rand_phase=False)+0.5*additive(f,n,sq_harm(f,2400),rand_phase=False,detune=0.004)
    return (lowpass(raw,fc)+0.8*np.sin(2*np.pi*f*t))*env(n,0.004,0.03)
def sub(f,n):
    t=np.arange(n)/SR
    return (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t))*env(n,0.012,0.05)
def cuerdas(f,n,vib=0.005):
    sig=sum(additive(f,n,saw_harm(f,3600),detune=d,vib=vib) for d in (-0.005,0,0.005))/3
    return lowpass(sig,2400)
def spicc(f,n,tau=0.085):
    t=np.arange(n)/SR
    sig=sum(additive(f,n,saw_harm(f,3600),detune=d) for d in (-0.005,0,0.005))/3
    return highpass(sig,180)*np.exp(-t/tau)*np.minimum(1,t/0.010)
def metal(f,n):
    """Metales: sierras apiladas, filtro bajo y ataque lento. Peso."""
    y=sum(additive(f,n,saw_harm(f,2200),detune=d) for d in (-0.004,0.0,0.004))/3
    return np.tanh(lowpass(y,850)*1.5)*env(n,0.10,0.30)
def piano(f,n=int(3.0*SR)):
    t=np.arange(n)/SR; out=np.zeros(n)
    for k,a in enumerate([1,0.55,0.32,0.2,0.11,0.07,0.04],1):
        fk=f*k*np.sqrt(1+0.0004*k*k); out+=a*np.sin(2*np.pi*fk*t+rng.uniform(0,6.28))*np.exp(-t*(0.75+0.45*k))
    return (out+lowpass(rng.normal(size=n)*np.exp(-t/0.004),1800)*0.35)*np.minimum(1,t/0.003)
def subida(dur):
    """El riser: acaba EXACTAMENTE donde se le pone, así que se coloca restando."""
    n=int(dur*SR); t=np.arange(n)/SR
    f=180*(2600/180)**((t/dur)**1.8)
    ton=np.sin(2*np.pi*np.cumsum(f)/SR)
    rui=highpass(rng.normal(size=n),600)*(0.4+0.6*(t/dur))
    return (ton*0.35+rui*0.65)*(t/dur)**2.2
def reves(dur=1.6):
    n=int(dur*SR); t=np.arange(n)/SR
    y=highpass(rng.normal(size=n),4000)*np.exp(-t/0.55)
    return y[::-1]*0.7
def impacto(f,dur=2.4):
    n=int(dur*SR); t=np.arange(n)/SR
    fr=110*(32/110)**(t/0.9)
    grave=np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-t*2.0)
    crash=lowpass(rng.normal(size=n),9000)*np.exp(-t*2.6)*0.5
    return np.tanh((grave+crash)*1.2)

def por_tramos(c, buf, gan):
    """Ganancia por compás sobre una capa: es lo que hace que la caída caiga."""
    g=np.concatenate([np.repeat([gan[b] for b in range(c.nbars)], 1)]*2)
    curva=np.zeros(2*c.L)
    for i,gg in enumerate(g):
        a=i*c.L//c.nbars if i<c.nbars else c.L+(i-c.nbars)*c.L//c.nbars
        b_=a+c.L//c.nbars
        curva[a:b_]=gg
    # suaviza los saltos para que no chasqueen
    k=int(0.02*SR); curva=np.convolve(curva,np.ones(k)/k,mode="same")
    return buf*curva

def bombeo(L, golpes, prof=0.72, tau=0.15):
    """El sidechain: en cada bombo todo se agacha y vuelve. Da la vuelta al bucle."""
    g=np.ones(L); idx=np.arange(L)
    for h in golpes:
        d=((idx-h)%L)/SR
        g=np.minimum(g,1-prof*np.exp(-d/tau))
    return g

# ── las tres recetas ──────────────────────────────────────────────────────
# cada acorde: (raíz midi, tercera 3=menor/4=mayor)
def r_hibell():
    c=Ctx(130,16)
    P=[(30,3),(30,3),(26,4),(26,4),(33,4),(33,4),(28,4),(28,4)]*2      # F#m D A E
    K=[c.at(b,s) for b in range(4,16) for s in (0,4,8,12)]              # bombo desde el compás 4
    bat=c.new(); baj=c.new(); ost=c.new(); pad=c.new(); mtl=c.new(); ef=c.new()
    for k in K: place(bat,k,kick(),0.5)
    for b in range(8,16):
        for s in (4,12): place(bat,c.at(b,s),clap(),0.5)
    for b in range(4,16):
        for s in range(2,16,4): place(bat,c.at(b,s),hat(s%8==6),0.44 if s%8==2 else 0.56)
    for b,(r,t3) in enumerate(P):
        # bajo rodando a contratiempo, sólo en la caída
        if b>=8:
            for s in range(2,16,4): place(baj,c.at(b,s),bajo(f_of(r+12),int(c.step*1.7*SR)),0.5)
        place(baj,c.at(b),sub(f_of(r),int(c.bar*1.02*SR))*(0.9 if b>=8 else 0.55),0.5)
        # ostinato de cuerdas en semicorcheas: es la firma
        PAT=[0,7,12,7,0,7,12,t3+12,0,7,12,7,t3+12,12,7,0]
        for s in range(16):
            g=1.0 if b>=8 else (0.55 if b>=4 else 0.40)
            acc=1.0 if s%4==0 else (0.72 if s%2 else 0.85)
            place(ost,c.at(b,s),spicc(f_of(r+36+PAT[s]),int(c.step*2.2*SR))*g*acc,0.5+0.22*np.sin(2*np.pi*s/16))
        n=int((c.bar+0.7)*SR)
        for iv,g in [(24,1.0),(24+t3,0.75),(31,0.8),(36,0.5)]:
            for ch,d in enumerate((-0.005,0.005)):
                s0=c.at(b); pad[ch,s0:s0+n]+=cuerdas(f_of(r+iv)*(1+d),n)*g*env(n,0.5,0.7)*(1.0 if b>=8 else 0.6)
        if b>=8 and b%2==0:                                            # metales a golpes en la caída
            place(mtl,c.at(b),metal(f_of(r+12),int(c.beat*2.2*SR)),0.5)
    place(ef,c.at(8)-int(2.6*SR),subida(2.6),0.5)
    place(ef,c.at(8)-int(1.6*SR),reves(1.6),0.5)
    place(ef,c.at(8),impacto(f_of(30)),0.5)
    GAN=[0.55]*4+[0.75]*4+[1.0]*8
    pad,baj=(por_tramos(c,z,GAN) for z in (pad,baj))
    L=dict(bat=bat,baj=baj,ost=ost,pad=pad,mtl=mtl,ef=ef)
    G=dict(bat=(0.95,0.10),baj=(0.75,0.05),ost=(0.62,0.35),pad=(0.45,0.35),mtl=(0.55,0.30),ef=(0.5,0.45))
    return c,L,G,K,1.5,{"baj","ost","pad","mtl"}

def r_walker():
    c=Ctx(128,16)
    P=[(35,3),(35,3),(31,4),(31,4),(38,4),(38,4),(33,4),(33,4)]*2      # Bm G D A
    K=[c.at(b,s) for b in list(range(4,8))+list(range(8,16)) for s in (0,4,8,12)]
    MEL=[(0,0,78,4),(0,4,76,2),(0,6,74,2),(0,8,71,4),(0,12,74,4),
         (2,0,74,4),(2,4,71,4),(2,8,69,6),(2,14,71,2),
         (4,0,78,4),(4,4,81,2),(4,6,78,2),(4,8,76,4),(4,12,74,4),
         (6,0,76,4),(6,4,74,4),(6,8,71,8)]
    MEL=MEL+[(b+8,s,n,d) for b,s,n,d in MEL]
    bat=c.new(); baj=c.new(); mel=c.new(); lead=c.new(); pad=c.new(); ef=c.new()
    for k in K: place(bat,k,kick(f0=145,f1=45,td=0.13),0.5)
    for b in range(8,16):
        for s in (4,12): place(bat,c.at(b,s),clap(),0.5)
    for b in range(6,16):
        for s in range(2,16,4): place(bat,c.at(b,s),hat(),0.45 if s%8==2 else 0.55)
    for b,(r,t3) in enumerate(P):
        if b>=8:
            for s in range(2,16,4): place(baj,c.at(b,s),bajo(f_of(r+12),int(c.step*1.6*SR),fc=700),0.5)
        place(baj,c.at(b),sub(f_of(r),int(c.bar*1.02*SR))*(0.85 if b>=8 else 0.5),0.5)
        n=int((c.bar+0.9)*SR)
        for iv,g in [(24,1.0),(24+t3,0.7),(31,0.75)]:
            for ch,d in enumerate((-0.004,0.004)):
                s0=c.at(b); pad[ch,s0:s0+n]+=cuerdas(f_of(r+iv)*(1+d),n)*g*env(n,0.6,0.8)
    for b,s,nota,dur in MEL:
        largo=int(dur*c.step*SR*1.9)
        place(mel,c.at(b,s),pluck_syn(f_of(nota),largo,brillo=5200,tau=0.19)*0.9,0.5)
        if b>=8: place(lead,c.at(b,s),supersaw(f_of(nota),int(dur*c.step*SR*1.05))*env(int(dur*c.step*SR*1.05),0.012,0.05),0.5)
    mel=delay_circ(mel,c.L,int(3*c.step*SR),0.34)                      # el eco a tresillo, marca de la casa
    place(ef,c.at(8)-int(2.2*SR),subida(2.2),0.5)
    place(ef,c.at(8),impacto(f_of(35)),0.5)
    GAN=[0.42]*4+[0.68]*4+[1.0]*8
    mel,pad,baj=(por_tramos(c,z,GAN) for z in (mel,pad,baj))
    L=dict(bat=bat,baj=baj,mel=mel,lead=lead,pad=pad,ef=ef)
    G=dict(bat=(0.9,0.12),baj=(0.7,0.05),mel=(0.5,0.5),lead=(0.42,0.4),pad=(0.5,0.45),ef=(0.45,0.5))
    return c,L,G,K,2.2,{"baj","mel","lead","pad"}

def r_avicii():
    c=Ctx(126,16)
    P=[(38,4),(38,4),(33,4),(33,4),(35,3),(35,3),(31,4),(31,4)]*2      # D A Bm G
    K=[c.at(b,s) for b in range(4,16) for s in (0,4,8,12)]
    MEL=[(8,0,78,3),(8,3,81,3),(8,6,83,2),(8,8,81,4),(8,12,78,4),
         (10,0,76,3),(10,3,78,3),(10,6,81,2),(10,8,78,4),(10,12,73,4),
         (12,0,74,3),(12,3,78,3),(12,6,81,2),(12,8,83,4),(12,12,81,4),
         (14,0,78,4),(14,4,76,4),(14,8,74,8)]
    PIA=[(0,0),(0,6),(0,10),(1,0),(1,6),(1,10)]                        # el patrón sincopado del piano
    bat=c.new(); baj=c.new(); pia=c.new(); mel=c.new(); acor=c.new(); pad=c.new(); ef=c.new()
    for k in K: place(bat,k,kick(f0=160,f1=50,td=0.10),0.5)
    for b in range(8,16):
        for s in (4,12): place(bat,c.at(b,s),clap(),0.5)
    for b in range(4,16):
        for s in range(2,16,4): place(bat,c.at(b,s),hat(s%8==6),0.45 if s%8==2 else 0.55)
    for b,(r,t3) in enumerate(P):
        if b>=8:
            for s in range(2,16,4): place(baj,c.at(b,s),bajo(f_of(r+12),int(c.step*1.6*SR)),0.5)
        place(baj,c.at(b),sub(f_of(r),int(c.bar*1.02*SR))*(0.9 if b>=8 else 0.5),0.5)
        for bb,ss in PIA:                                              # piano en todo el bucle
            if bb!=b%2: continue
            for iv in (12,24,24+t3,31):
                place(pia,c.at(b,ss),piano(f_of(r+iv))*(0.55 if b<8 else 0.4),0.5)
        if b>=8:                                                       # acordes de supersaw en la caída
            n=int(c.beat*0.9*SR)
            for s in (0,4,8,12):
                for iv in (24,24+t3,31,36):
                    place(acor,c.at(b,s),supersaw(f_of(r+iv),n)*env(n,0.008,0.10)*0.5,0.5)
        n=int((c.bar+0.8)*SR)
        for iv,g in [(24,0.9),(31,0.7)]:
            for ch,d in enumerate((-0.004,0.004)):
                s0=c.at(b); pad[ch,s0:s0+n]+=cuerdas(f_of(r+iv)*(1+d),n)*g*env(n,0.55,0.75)
    for b,s,nota,dur in MEL:
        place(mel,c.at(b,s),pluck_syn(f_of(nota),int(dur*c.step*SR*2.1),brillo=6000,tau=0.17),0.5)
    place(ef,c.at(8)-int(2.4*SR),subida(2.4),0.5)
    place(ef,c.at(8)-int(1.4*SR),reves(1.4),0.5)
    place(ef,c.at(8),impacto(f_of(38)),0.5)
    GAN=[0.48]*4+[0.72]*4+[1.0]*8
    pad,baj=(por_tramos(c,z,GAN) for z in (pad,baj))
    pia=por_tramos(c,pia,[0.62]*4+[0.85]*4+[1.0]*8)
    L=dict(bat=bat,baj=baj,pia=pia,mel=mel,acor=acor,pad=pad,ef=ef)
    G=dict(bat=(0.92,0.10),baj=(0.7,0.05),pia=(0.5,0.4),mel=(0.55,0.4),acor=(0.4,0.35),pad=(0.4,0.4),ef=(0.45,0.45))
    return c,L,G,K,1.8,{"baj","pia","mel","acor","pad"}

def r_palmas():
    """Palmas: bombo, palmas a contratiempo, plucks brillantes y una melodía de supersaw en
    mayor. Alegre y con fuerza: el final que sale bien."""
    c=Ctx(124,16)
    P=[(36,4),(36,4),(31,4),(31,4),(33,3),(33,3),(29,4),(29,4)]*2      # C G Am F
    K=[c.at(b,s) for b in range(4,16) for s in (0,4,8,12)]
    MEL=[(8,0,76,2),(8,2,79,2),(8,4,81,4),(8,8,79,2),(8,10,76,2),(8,12,74,4),
         (10,0,72,2),(10,2,76,2),(10,4,79,4),(10,8,76,2),(10,10,74,2),(10,12,72,4),
         (12,0,76,2),(12,2,79,2),(12,4,81,4),(12,8,83,2),(12,10,81,2),(12,12,79,4),
         (14,0,76,4),(14,4,74,4),(14,8,72,8)]
    bat=c.new(); baj=c.new(); mel=c.new(); acor=c.new(); pad=c.new(); ef=c.new()
    for k in K: place(bat,k,kick(f0=150,f1=48,td=0.10),0.5)
    for b in range(4,16):
        for s in (4,12): place(bat,c.at(b,s),clap(),0.5)
        for s in range(2,16,4): place(bat,c.at(b,s),hat(s%8==6),0.45 if s%8==2 else 0.55)
    for b,(r,t3) in enumerate(P):
        if b>=8:
            for s in (2,6,10,14): place(baj,c.at(b,s),bajo(f_of(r+12),int(c.step*1.6*SR)),0.5)
        place(baj,c.at(b),sub(f_of(r),int(c.bar*1.02*SR))*(0.9 if b>=8 else 0.5),0.5)
        for s in (0,3,6,8,11,14):
            for iv in (24,24+t3,31):
                place(acor,c.at(b,s),pluck_syn(f_of(r+iv+12),int(c.step*2.4*SR),brillo=5600,tau=0.14)*(0.5 if b<8 else 0.7),0.5+0.1*np.sin(s))
        n=int((c.bar+0.8)*SR)
        for iv,g in [(24,0.9),(31,0.7)]:
            for ch,d in enumerate((-0.004,0.004)):
                s0=c.at(b); pad[ch,s0:s0+n]+=cuerdas(f_of(r+iv)*(1+d),n)*g*env(n,0.55,0.75)
    for b,s,nota,dur in MEL:
        n=int(dur*c.step*SR*1.05)
        place(mel,c.at(b,s),supersaw(f_of(nota),n)*env(n,0.01,0.06)*0.8,0.5)
    place(ef,c.at(8)-int(2.4*SR),subida(2.4),0.5)
    place(ef,c.at(8),impacto(f_of(36)),0.5)
    GAN=[0.5]*4+[0.72]*4+[1.0]*8
    pad,baj=(por_tramos(c,z,GAN) for z in (pad,baj))
    acor=por_tramos(c,acor,[0.6]*4+[0.85]*4+[1.0]*8)
    L=dict(bat=bat,baj=baj,mel=mel,acor=acor,pad=pad,ef=ef)
    G=dict(bat=(0.92,0.10),baj=(0.7,0.05),mel=(0.45,0.4),acor=(0.5,0.4),pad=(0.4,0.4),ef=(0.45,0.45))
    return c,L,G,K,1.6,{"baj","acor","pad","mel"}

# nombres genéricos por familia: nada de nombres propios
RECETAS={"energia-orquesta":r_hibell,"energia-eco":r_walker,"energia-piano":r_avicii,"energia-palmas":r_palmas}

def ir(seconds,tau):
    n=int(seconds*SR); t=np.arange(n)/SR; out=np.zeros((2,n))
    for ch in range(2): out[ch]=lowpass(rng.normal(size=n),6500)*np.exp(-t/tau)*np.minimum(1,t/0.02)
    out=np.concatenate([np.zeros((2,int(0.024*SR))),out],1); return out/np.sqrt((out**2).sum(1)).max()
def write(p,y):
    with wave.open(str(p),'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y,-1,1).T*32767).astype('<i2').tobytes())

def render(nombre, receta=None, OUT=OUT):
    c,LAY,G,K,tau,sc=(receta or RECETAS[nombre])()
    LAY={k:c.fold(v) for k,v in LAY.items()}
    duck=bombeo(c.L,K)                                                  # el bombeo, sobre las capas marcadas
    for k in sc: LAY[k]=LAY[k]*duck
    IR=ir(min(3.0,c.T-1),tau)
    seco=sum(LAY[k]*G[k][0] for k in LAY); env_=sum(LAY[k]*G[k][0]*G[k][1] for k in LAY)
    mojado=np.stack([np.fft.irfft(np.fft.rfft(env_[ch],n=c.L)*np.fft.rfft(IR[ch],n=c.L),n=c.L) for ch in range(2)])
    y=seco+mojado*1.0
    y=np.stack([highpass(lowpass(x,16500),26) for x in y])
    y/=np.abs(y).max(); y=np.tanh(y*1.35)/np.tanh(1.35); y*=0.891/np.abs(y).max()
    write(OUT/f"{nombre}.wav",y)
    db=lambda s:20*np.log10(np.sqrt((s**2).mean())+1e-9)
    tramos=" ".join(f"{db(y[:,c.at(b):c.at(b+4)]):.0f}" for b in (0,4,8,12))
    print(f"{nombre:9s} {c.T:5.2f} s · {c.nbars} compases a {c.bpm} BPM · RMS {db(y):.1f} dBFS · por tramos {tramos} dB")
    return y

if __name__ == "__main__":
    for nombre in (PEDIDOS or list(RECETAS)): render(nombre)
