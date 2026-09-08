"""Los mismos 74 efectos del catálogo, pero generados con ElevenLabs en vez de
sintetizados: suenan a grabación, no a numpy. Se guardan en la carpeta de la
marca (taller/<marca>/sonidos/), que manda sobre motor/sonidos/ para los
nombres que tenga. Los que no generes siguen saliendo de los sintetizados.

  ELEVENLABS_API_KEY=sk_… python3 motor/efectos-eleven.py taller/<marca>            todos
  ELEVENLABS_API_KEY=sk_… python3 motor/efectos-eleven.py taller/<marca> boom caja  sólo esos

Cuesta créditos de tu cuenta (unos 40 por segundo de efecto; los 74 rondan los
3.200). Con el plan gratuito el uso es personal y con atribución; para vender
vídeos con ellos hace falta un plan de pago. Ver LEEME-elevenlabs.md.

Cada efecto se pide en inglés, que es como mejor entiende el modelo, se le
quita el silencio del principio —el golpe tiene que caer en su segundo— y se
mide dónde está su pico para los que llevan ancla.
"""
import json, os, pathlib, subprocess, sys, urllib.request, wave
import numpy as np

SR = 44100
API = "https://api.elevenlabs.io/v1/sound-generation"
KEY = os.environ.get("ELEVENLABS_API_KEY", "")

# nombre → (descripción en inglés, segundos, ancla: 0 | "pico")
CAT = {
 "whoosh":       ("Quick cinematic whoosh, swoosh transition", 0.5, 0),
 "whoosh-largo": ("Long airy cinematic whoosh transition, camera flying past", 1.0, 0),
 "barrido":      ("Fast airy sweep transition, rising", 0.6, 0),
 "swipe":        ("Very short UI swipe swish", 0.5, 0),
 "subida":       ("Cinematic tension riser sweep building up and ending at the peak", 1.6, "pico"),
 "subida-larga": ("Long cinematic riser, three seconds building up to a big hit at the end", 3.0, "pico"),
 "rebobinar":    ("Fast tape rewind sound, ending abruptly", 1.2, "pico"),
 "freno":        ("Tape stop, everything slows down and stops, pitch dropping", 0.9, 0),
 "glitch":       ("Short digital glitch, data corruption stutter", 0.5, 0),
 "corte":        ("Sharp camera shutter click, film cut", 0.5, 0),
 "golpe":        ("Deep cinematic hit, short low thud with a tight punch, minimal tail", 0.7, 0),
 "impacto":      ("Cinematic impact hit with reverb tail and low rumble", 2.0, 0),
 "boom":         ("Deep cinematic trailer boom with a long sub bass tail", 2.0, 0),
 "bombo":        ("Single punchy kick drum hit, dry", 0.5, 0),
 "caida":        ("Bass drop, sub bass falling down, cinematic", 1.3, 0),
 "estampido":    ("Short hard slam, something stamped down", 0.5, 0),
 "portazo":      ("Door slam, wooden door closing hard", 0.8, 0),
 "tecla":        ("Single phone screen tap click", 0.5, 0),
 "teclado":      ("Fast mechanical keyboard typing, several quick keystrokes, close mic", 1.0, 0),
 "clic":         ("Single mouse click", 0.5, 0),
 "blip":         ("Short clean digital blip, notification", 0.5, 0),
 "notificacion": ("Phone notification chime, two soft tones", 0.6, 0),
 "mensaje":      ("Incoming message sound, three ascending soft notes", 0.7, 0),
 "pop":          ("Soft bubble pop, a UI element appears", 0.5, 0),
 "burbuja":      ("Small bubble rising and popping, cartoonish", 0.5, 0),
 "toggle":       ("Light switch toggle click", 0.5, 0),
 "error":        ("Short error buzz, wrong answer, game show", 0.5, 0),
 "acierto":      ("Success chime, two ascending pleasant notes, achievement unlocked", 0.8, 0),
 "campana":      ("Single bright bell ring with a soft decay", 1.5, 0),
 "caja":         ("Cash register ka-ching with bell ring and drawer opening", 1.0, 0),
 "monedas":      ("A handful of coins dropping on a table", 0.9, 0),
 "timbre":       ("Doorbell ding dong", 1.2, 0),
 "alarma":       ("Short alarm beeping, urgent", 0.8, 0),
 "camara":       ("Camera shutter click with mirror clack, photo taken", 0.5, 0),
 "cuenta-atras": ("Countdown beeps speeding up and stopping at the end", 2.0, "pico"),
 "latido":       ("Single slow heartbeat, lub-dub, deep", 0.7, 0),
 "reloj":        ("Clock ticking, tick tock, four ticks", 2.0, 0),
 "dun-dun-dun":  ("Dramatic dun dun dun, three descending orchestral brass hits", 3.0, 0),
 "tension":      ("Rising tension drone, suspense build up that cuts off", 2.6, 0),
 "revelacion":   ("Magical reveal, ascending sparkling arpeggio with shimmer", 2.0, 0),
 "suspenso":     ("Sudden orchestral string stinger, suspense sting", 0.8, 0),
 "disco-rayado": ("Vinyl record scratch and stop", 0.8, 0),
 "silbato":      ("Cartoon slide whistle falling down", 0.9, 0),
 "muelle":       ("Cartoon spring boing", 0.7, 0),
 "aplauso":      ("Small crowd applause, clapping, two seconds", 2.4, 0),
 "redoble":      ("Drum roll building up ending with a cymbal crash", 2.4, "pico"),
 "grillo":       ("Crickets chirping at night, quiet awkward silence", 2.0, 0),
 "zap":          ("Short laser zap", 0.5, 0),
 "brillo":       ("Short magical shimmer chime, bright and glassy, UI reveal", 0.8, 0),
 "fiesta":       ("Party popper confetti burst with a small cheer", 1.2, 0),
 "cristal-roto": ("Glass shattering, window breaking", 1.0, 0),
 "loza":         ("Plates and cutlery clinking on a bar table", 0.6, 0),
 "vaso":         ("Single glass set down on a wooden table with a clink", 0.6, 0),
 "brindis":      ("Two glasses clinking together, toast", 0.8, 0),
 "roce":         ("Paper sliding across a table", 0.6, 0),
 "hilo":         ("Thin rising whistle tone, a line being drawn", 0.5, 0),
 "papel":        ("Page flip, paper turning", 0.5, 0),
 "boligrafo":    ("Ballpoint pen click", 0.5, 0),
 "sello":        ("Rubber stamp thump on paper, office stamp", 0.5, 0),
 # los quince del pack premium (PREMIUM.md); aquí van descritos por si hay que rehacerlos
 "estirar":         ("UI element stretching and morphing, elastic digital sweep", 1.1, 0),
 "bajada":          ("Cinematic downlifter, reverse riser falling away", 2.0, 0),
 "teclado-largo":   ("Continuous mechanical keyboard typing, several seconds", 2.5, 0),
 "clic-digital":    ("Digital UI click with body, app control", 0.5, 0),
 "seleccionar":     ("Granular UI select blip, option marked", 0.5, 0),
 "enviar":          ("UI enter confirm, message sent, deep short swell", 0.5, 0),
 "borrar":          ("UI backspace delete, something removed", 0.5, 0),
 "abrir":           ("UI panel opening, sheet sliding open and settling", 1.5, "pico"),
 "parpadeo":        ("Text glitch flicker, digital text appearing", 0.5, 0),
 "dinero":          ("Cinematic money sound, cash and coins with a low swell", 1.1, 0),
 "datos":           ("Digital data collect, numbers rolling and locking in", 1.0, 0),
 "datos-largo":     ("Long digital data processing, numbers computing", 2.6, 0),
 "cronometro":      ("Digital stopwatch counting, fast electronic ticking", 2.0, 0),
 "engranaje":       ("Mechanical gear turning, parts meshing", 0.7, 0),
 "engranaje-largo": ("Mechanism spinning up and clicking into place at the end", 1.3, "pico"),
}

def pide(texto, dur):
    datos = json.dumps({"text": texto, "duration_seconds": dur, "prompt_influence": 0.5}).encode()
    req = urllib.request.Request(API, data=datos, headers={"xi-api-key": KEY, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=120) as r: return r.read()

def carga_bytes(mp3):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "pipe:0", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], input=mp3, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)

def limpia(x):
    """Quita el silencio de los dos lados y normaliza: el golpe cae en su segundo."""
    pk = np.abs(x).max(); x = x/pk if pk else x
    ini = max(0, int(np.argmax(np.abs(x) > 0.03)) - int(0.004*SR))
    fin = len(x) - int(np.argmax(np.abs(x[::-1]) > 0.01))
    y = x[ini:fin].copy()
    n = min(len(y), int(0.002*SR)); y[:n] *= np.linspace(0, 1, n)
    m = min(len(y), int(0.01*SR)); y[-m:] *= np.linspace(1, 0, m)
    return y/np.abs(y).max()*0.89

if __name__ == "__main__":
    if not KEY: sys.exit("falta ELEVENLABS_API_KEY en el entorno · ver LEEME-elevenlabs.md")
    if len(sys.argv) < 2: sys.exit("uso: efectos-eleven.py taller/<marca> [efecto …]")
    dest = pathlib.Path(sys.argv[1])/"sonidos"; dest.mkdir(parents=True, exist_ok=True)
    pedidos = [a for a in sys.argv[2:] if a in CAT] or list(CAT)
    anclas = json.loads((dest/"anclas.json").read_text()) if (dest/"anclas.json").exists() else {}
    for nombre in pedidos:
        texto, dur, ancla = CAT[nombre]
        try: y = limpia(carga_bytes(pide(texto, dur)))
        except Exception as e: print(f"  ✗ {nombre}: {e}"); continue
        with wave.open(str(dest/f"{nombre}.wav"), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1)*32767).astype("<i2").tobytes())
        if ancla == "pico": anclas[nombre] = round(float(np.argmax(np.abs(y))/SR), 3)
        print(f"  ✓ {nombre:13s} {len(y)/SR:5.2f} s{'  · ancla ' + str(anclas[nombre]) if nombre in anclas else ''}")
    (dest/"anclas.json").write_text(json.dumps(anclas, indent=1))
    print(f"✓ {len(pedidos)} efectos en {dest} · mandan sobre motor/sonidos/ para estos nombres")
