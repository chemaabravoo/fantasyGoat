"""La voz de una pieza en UNA toma (sin juntas) y sus marcas por palabra.
   Desde taller/<marca>/ :   python3 ../../motor/toma.py <pieza> [--voz <id>] [--modelo <id>]
   Con --modelo eleven_v3 la voz entona de verdad y acepta etiquetas entre corchetes
   ([curious], [excited]…) dentro del guion: el modelo las interpreta y no las dice.
   Lee guiones/<pieza>.txt (una frase por línea) y deja audios/<pieza>/toma.mp3,
   toma.scribe.json y marcas.json. Luego marcas.py imprime el objeto M para la pieza.
   Hace falta ELEVENLABS_API_KEY en el entorno (LEEME-elevenlabs.md)."""
import json,sys,subprocess,pathlib,re,unicodedata,os
argv=sys.argv[1:]
VOZ='gD1IexrzCvsXPHUuT0s3'   # una voz pública de la Voice Library de ElevenLabs (español, mujer). Cámbiala por la de la marca.
MODELO='eleven_multilingual_v2'
if '--voz' in argv: i=argv.index('--voz'); VOZ=argv[i+1]; del argv[i:i+2]
if '--modelo' in argv: i=argv.index('--modelo'); MODELO=argv[i+1]; del argv[i:i+2]
if not argv: sys.exit('uso: toma.py <pieza> [--voz <voice_id>]')
vid=argv[0]; KEY=os.environ.get('ELEVENLABS_API_KEY','').strip()
if not KEY: sys.exit('falta ELEVENLABS_API_KEY en el entorno · ver LEEME-elevenlabs.md')
out=pathlib.Path('audios')/vid; out.mkdir(parents=True,exist_ok=True)
lineas=[l.strip() for l in open(f'guiones/{vid}.txt',encoding='utf-8') if l.strip()]
txt='\n'.join(lineas)
body={'text':txt,'model_id':MODELO,'language_code':'es',
      'voice_settings':{'stability':0.5,'similarity_boost':0.85,'style':0.0,'use_speaker_boost':True}}
if MODELO=='eleven_v3': body['voice_settings']={'stability':0.5,'similarity_boost':0.85}
pathlib.Path('/tmp/b.json').write_text(json.dumps(body))
if (out/'toma.scribe.json').exists() and (out/'toma.mp3').exists(): code='ya'
else: code=subprocess.run(['curl','-s','-o',str(out/'toma.mp3'),'-w','%{http_code}','-X','POST',
  f'https://api.elevenlabs.io/v1/text-to-speech/{VOZ}?output_format=mp3_44100_128',
  '-H',f'xi-api-key: {KEY}','-H','Content-Type: application/json','--data','@/tmp/b.json'],
  capture_output=True,text=True).stdout
if code not in('200','ya'): sys.exit(f'{vid}: tts {code} · {(out/"toma.mp3").read_text(errors="ignore")[:200]}')
if code=='ya': pass
else: code=subprocess.run(['curl','-s','-X','POST','https://api.elevenlabs.io/v1/speech-to-text',
  '-H',f'xi-api-key: {KEY}','-F',f'file=@{out/"toma.mp3"}','-F','model_id=scribe_v1',
  '-F','language_code=spa','-F','timestamps_granularity=word','-o',str(out/'toma.scribe.json'),
  '-w','%{http_code}'],capture_output=True,text=True).stdout
if code not in('200','ya'): sys.exit(f'{vid}: stt {code}')
d=json.load(open(out/'toma.scribe.json',encoding='utf-8'))
ws=[w for w in d['words'] if w.get('type')=='word']
def norm(s):
    s=unicodedata.normalize('NFD',s.lower()); return ''.join(c for c in s if unicodedata.category(c)!='Mn' and c.isalnum())
# cada línea: se busca su primera palabra "de peso" (≥3 letras) a partir de donde acabó la anterior
i=0; marcas=[]
for n,fr in enumerate(lineas):
    fr_limpia=re.sub(r'\[[^\]]*\]',' ',fr)     # las etiquetas de v3 no se dicen: no se buscan
    toks=[norm(x) for x in re.findall(r"[\wáéíóúñü]+",fr_limpia,flags=re.I)]
    firma=toks[:2]
    def busca(firma):
        j=i
        while j<len(ws)-len(firma)+1:
            if all(norm(ws[j+k]['text'])==firma[k] for k in range(len(firma))): return j
            j+=1
        return None
    j=busca(firma)
    if j is None: j=busca(firma[:1]); firma=firma[:1]   # Scribe oyó otra segunda palabra («muchón»): vale con la primera
    if j is None: sys.exit(f'{vid}: no encuentro «{fr}» a partir de la palabra {i}')
    ini=ws[j]['start']
    marcas.append({'n':n,'frase':fr,'ini':round(max(0,ini),3)}); i=j+len(firma)
dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(out/'toma.mp3')],capture_output=True,text=True).stdout)
pal={norm(w['text'])+'@'+str(k):round(w['start'],3) for k,w in enumerate(ws)}
json.dump({'dur':round(dur,3),'frases':marcas,'palabras':[[round(w['start'],3),w['text']] for w in ws]},open(out/'marcas.json','w'),ensure_ascii=False,indent=1)
print(f'{vid} · {dur:.2f} s')
for m in marcas: print(f"  {m['ini']:7.3f}  {m['frase']}")
print('  '+' | '.join(f"{w['start']:.2f} {w['text']}" for w in ws))
