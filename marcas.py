"""Imprime el objeto M de una pieza desde audios/<pieza>/marcas.json (lo escribe toma.py).
   python3 ../../motor/marcas.py <pieza> [desplazamiento] [palabra palabra …]
   · desplazamiento: segundos que la voz empieza más tarde que la pieza (0 si habla desde el 0)
   · palabras: las que disparan algo en la pieza; salen con su segundo (la primera aparición
     después de la frase anterior). Siempre salen f1, f2… (el inicio de cada frase) y fin."""
import json,sys,unicodedata
if len(sys.argv)<2: sys.exit(__doc__)
vid=sys.argv[1]; C0=float(sys.argv[2]) if len(sys.argv)>2 else 0.0
pedidas=sys.argv[3:]
d=json.load(open(f'audios/{vid}/marcas.json',encoding='utf-8'))
def norm(s):
    s=unicodedata.normalize('NFD',s.lower()); return ''.join(c for c in s if unicodedata.category(c)!='Mn' and c.isalnum())
W=[(t,norm(w)) for t,w in d['palabras']]
M={f"f{m['n']+1}":m['ini'] for m in d['frases']}
pos=0.0
for pal in pedidas:
    n=norm(pal); t=next((t for t,w in W if t>=pos and w==n),None)
    if t is None: sys.exit(f'no está «{pal}» después del segundo {pos:.2f}')
    M[n]=t; pos=t
M['fin']=d['dur']
print('const M={'+', '.join(f'{k}:{round(v+C0,3)}' for k,v in M.items())+'};')
