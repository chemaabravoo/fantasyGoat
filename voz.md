# La voz y el sonido

**Esto va en todas las piezas, no sólo en las que "llevan locución".** Una pieza
sin voz y sin efectos no está terminada: está a medio render. Ver la ley 4 de
[SKILL.md](../SKILL.md).

## 1 · La voz es UNA toma, y los tiempos los da Scribe

**No se trocea la voz.** Se genera el guion entero en **una sola llamada** a ElevenLabs
(`eleven_multilingual_v2`, una línea por frase) y los tiempos de cada frase y de cada
palabra salen de la transcripción con marcas de tiempo (Scribe). Así la voz suena a
una persona hablando seguido, y la animación se cuelga de la palabra exacta:

```bash
# desde taller/<marca>/ · guiones/<pieza>.txt tiene una frase por línea
export ELEVENLABS_API_KEY=sk_…
python3 ../../motor/toma.py <pieza>             # → audios/<pieza>/toma.mp3 + marcas.json
python3 ../../motor/marcas.py <pieza> 0         # → el objeto M para pegar en la pieza (0 = la voz empieza en el segundo 0)
```

`marcas.py` imprime `const M={f1:…, f2:…, esto:…, carpeta:…}`: el segundo en que empieza
cada frase (`f1`, `f2`…) y las palabras clave. **Los compases cuelgan de M, nunca de
segundos a mano**, y la imagen empieza 0,05-0,15 s antes de la palabra.

- **Qué voz**: la que diga la skill de la marca. Si no tiene, que la persona elija en
  ElevenLabs → Voices → Library (las voces públicas se añaden a cualquier cuenta) y te
  pase el id; anótalo en su skill. Se pasa con `--voz`.
- **Qué modelo**: `eleven_multilingual_v2` de serie, que es estable y barato.
  **`--modelo eleven_v3` entona de verdad** —es la diferencia entre un locutor y alguien
  contando algo—. Cómo se le dirige, abajo, en «§1b · dirigir a v3».
- **Es una toma**: se puede repetir. Recuadrar contra otra toma es barato antes de
  animar y caro después.
- Si la cabeza va muda y la voz entra más tarde, se rellena con silencio delante
  (`ffmpeg -f lavfi -t 11 -i anullsrc…`) y a `marcas.py` se le pasa ese desplazamiento.

**Por qué no se trocea.** Pedir una llamada por frase y pegarlas suena a trozos: cada
frase sale con un tono distinto y las juntas se notan. Con la toma única eso desaparece,
y además los tiempos vienen medidos en vez de deducidos.

## 1b · Dirigir a v3 · las etiquetas entre corchetes

`eleven_v3` es el único modelo que **actúa**: se le dan acotaciones dentro del propio
guion y las interpreta sin decirlas. Van entre **corchetes**, `[así]` — no entre comillas
ni entre paréntesis, que ésos sí se leen. `toma.py` las limpia antes de buscar las
palabras, así que no descuadran los tiempos (`re.sub(r'\[[^\]]*\]', ...)`).

```
[curious] Esto es una carpeta. Le pegas la web de tu negocio... [excited] y ya sabe
cómo tienen que verse tus vídeos.
```

**Las que se usan aquí**, por lo que hace la pieza en ese momento:

| Momento de la pieza | Etiqueta | Qué hace |
|---|---|---|
| El gancho, la pregunta que abre | `[curious]` · `[thoughtful]` | sube al final, deja aire |
| La revelación, el dato que sorprende | `[excited]` · `[surprised]` | acelera y sube |
| El argumento, la parte seria | `[serious]` · `[confident]` | baja el tono, ralentiza |
| El susurro antes del giro | `[whispers]` | volumen abajo; funciona con silencio detrás |
| El cierre, la mano tendida | `[warm]` · `[reassuring]` | suaviza el final |
| La broma | `[laughs]` · `[sighs]` | **suenan de verdad**: son sonido, no tono |

**Las cinco reglas que se han pagado:**

1. **Una etiqueta por bloque, no por frase.** Etiquetar cada frase da una locución
   maníaca que cambia de humor cada tres segundos. Se etiqueta cuando **cambia el acto**.
2. **La etiqueta va delante de lo que tiñe**, pegada. Al final de la frase no hace nada.
3. **`[laughs]`, `[sighs]`, `[clears throat]` son sonidos**, no tonos: ocupan tiempo real
   y aparecen en el mapa como un hueco. Úsalos sólo si la pieza los aprovecha.
4. **Los puntos suspensivos son una etiqueta más.** `...` le hace parar de verdad, y
   suele funcionar mejor que `[pause]`, que a veces se lee.
5. **v3 respira de más**: mete pausas de párrafo de más de un segundo. Eso lo arregla
   `secar.py` (§2), y no es opcional.

**Lo que NO se le mete**: nombres de dominio ni marcas en inglés. Ningún modelo dice
bien una web: en una toma real se comió tres de tres, y de una marca acabada en *-home*
salió algo que no se parecía. **Los dominios se enseñan en pantalla, no se locutan**; y si
uno tiene que sonar, se escribe como suena en castellano (`Ril Mótor, punto i o`).

**Los ajustes**: `stability` 0,4 deja actuar (a 0,8 se aplana y las etiquetas casi no se
notan); `style` 0,3-0,4 sube la interpretación. Por encima de 0,5 de `style` empieza a
sobreactuar.

## 2 · Apretar la toma · `secar.py`

ElevenLabs respira de más entre frases, y en un vídeo de 30 s eso se nota como
lentitud. Un guion de 26 s se va a 46 s de audio sin que sobre una palabra.

```bash
python3 ../../motor/secar.py <pieza>          # deja el hueco entre frases en 0,30 s
python3 ../../motor/secar.py <pieza> 0.18     # más apretado, si la pieza va lenta
```

Qué hace, y por qué es exacto:

- Busca los silencios con `silencedetect` y **corta por dentro del propio silencio**:
  un corte en silencio no se oye, así que no hay tijeretazo.
- La toma original se guarda como `toma-crudo.mp3`. Se puede repetir cuantas veces
  quieras cambiando el hueco.
- **Recoloca cada tiempo de `marcas.json`** restando lo que ha quitado antes de él. Es
  aritmética, no una estimación: **no hay que volver a transcribir**, que es lo que
  cuesta dinero.

Baja las tomas un 12-20 %. Pásalo siempre antes de `marcas.py`; si la voz te parece
apurada, sube el hueco y vuelve a pasarlo.

**El hueco no es sagrado.** Una pieza con cifras que hay que leer quiere 0,5 s entre
frases; una de humor, 0,18. Si la skill de la marca fija uno, manda esa.

## 2b · Los compases se cuelgan del mapa, nunca se escriben a mano

**Ésta es la que hace que corregir salga barato.** `marcas.py` imprime `M` y de `M`
tiene que colgar **todo** el guion de la pieza:

```js
const M={f1:0.100,f2:2.180,esto:4.900,…,fin:47.345};   // pegado tal cual

const T = guion([
  ['tit1',  M.f1-0.15,   0.42],
  ['tira',  M.esto+0.09, 0.62],
  ['card',  M.f7+0.51,   0.95],
]);
window.DURACION=+(M.fin+1.10).toFixed(2);
```

Y lo mismo para lo que no vive en `T`: los gestos, los toques y los tramos de cámara.
Si ves un `p(t,15.30,16.10)` con números crudos, está mal.

**El porqué:** al regenerar una sola frase se desplazan todas las de detrás. Con los
compases pinchados a mano, cambiar una palabra obliga a repinchar la pieza entera;
colgados de `M`, corregir es regenerar la toma, volver a pasar `secar.py` y `marcas.py`,
pegar la línea `M` nueva — y la animación se recoloca sola. **La persona corrige siempre
después del primer vistazo**, así que esto no es higiene: es la diferencia entre que su
corrección cueste un minuto o media hora.

**Y si cambias la toma sin querer rehacer la animación**, hay atajo: guarda los inicios
de frase viejos (`V0`) y los nuevos (`V1`) y remapea el reloj —`seek(t)` llama a
`_seek(aViejo(t))`—. Por dentro la pieza sigue en sus tiempos y se estira sola. Los
`SFX` y la `MUSICA` se mapean al revés, porque los lee `sonar-generico.py`.

## 3 · El ritmo se comprime


[movimiento.md](../animacion/movimiento.md) está medido para piezas mudas, donde la imagen tiene que
explicarse sola. **Con voz, la voz explica y la imagen sólo confirma**, así que
se puede ir bastante más rápido sin perder a nadie:

| | Muda | Con voz |
|---|---|---|
| Hueco de cascada | 0,16 s | **0,085 s** |
| Entrada de cada elemento | 0,36 s | **0,30 s** |
| Entre toque y toque | 0,95 s | **0,32 s** |
| Planos que caben en 17 s | 6 | **10** |

Lo que **no** se comprime: nada por debajo de **0,45 s** se lee, por mucha voz
que haya. Y un plano sigue necesitando 2 s si es la primera vez que se ve.

El presupuesto se hace al revés que sin voz: **la duración ya está dada** —la
del mp3 más ~1,1 s de cola— y lo que decides es qué cabe dentro. Suma lo que
va a costar cada cosa de tu guion y compáralo con los tramos que te dio
`silencedetect`. Órdenes de magnitud, medidos: un gesto suelto (algo entra,
algo se enciende) ronda 0,5 s; una acción con su reacción (tocas y pasa algo)
1,4–1,9 s; una escena que se monta entera —entra, hace lo suyo y se va— 2,5–2,7 s.

Si no cabe, **quita una cosa; no aceleres todo**. Comprimir por debajo de los
suelos de arriba no ahorra segundos, se los come de la legibilidad.

## 4 · El sonido


Ya no va aparte: está montado, y es el paso 7 del flujo. El único script es
`sonar-generico.py`, que **no sabe nada de tu pieza**: coge los efectos del array
`SFX` que el propio HTML declara dentro de `window.MARCAS`, así que cada pieza
pide los suyos sin escribir un script nuevo. Si le pasas la voz, la monta debajo;
si no, los efectos van solos y a volumen normal.

```bash
python3 sonar-generico.py ../<Marca>-<Nombre>.mp4 ~/Downloads/voz.mp3
```

Come del `.marcas.json` que escribe `shoot.mjs`, así que los efectos cuadran
fotograma a fotograma sin tocar nada. Escribe `<pieza>-son.mp4` al lado del mudo,
**y ése es el que se entrega**. Si alguna vez ves un `sonar-<nombre>.py` escrito a
mano para una pieza concreta, no lo reutilices: para eso está el genérico. Tres
cosas que costaron pasadas:

- La voz entra **sin desplazar**, con su silencio de entrada incluido.
- Los efectos al **0,42** y **agachados** donde se habla (envolvente de
  `np.abs(voz)` suavizada a 60 ms, hasta −62 %). Sin eso compiten con ella
  justo en los golpes, que es donde caen las dos cosas a la vez.
- `window.DURACION` = la voz + **~1,1 s de cola**, para que el cierre respire
  después de la última palabra.

## 5 · De una en una


**No hagas cinco piezas de golpe.** Se probó el 18 ago 2026 y salieron mal las
diez: las cinco primeras compartían plantilla y eran la misma con otros datos,
y las cinco siguientes, aun con formato propio cada una, se quedaron flojas.

El motivo es medible. Las piezas que funcionaron —entrevista, Belén, cobros,
voz alta, mesa— llevaron **entre seis y trece fotogramas mirados y tres o
cuatro pasadas de corrección** cada una: mirar, encontrar el fallo, arreglar,
volver a mirar. Las del lote llevaron dos o tres fotogramas y **ninguna pasada
de corrección**. El formato nuevo no salva una pieza sin iterar.

Si el encargo es de varias, dilo y hazlas de una en una, entregando cada una
antes de empezar la siguiente.

## 6 · Entregar


Los dos archivos: **el `-son.mp4` primero** —es la pieza— y el mudo detrás, por
si lo quiere montar él en su editor. Y el mapa de tiempos escrito, que es lo que le deja pedir cambios
concretos («el paso 3 entra tarde») en vez de en abstracto.

## Las pausas de la toma se aprietan


`eleven_v3` mete pausas de párrafo de más de un segundo, y esas pausas
**frenan el vídeo**. Antes de montar, recorta todo silencio entre frases a
**0,25–0,35 s** cortando sobre el propio silencio (atrim + concat: los cortes
en silencio no se oyen). Lo pidió el autor y es regla, no gusto. Y si la skill
de la marca dice otra medida, manda ella: la app de cuentas, formato cuenta, 0,4-0,65.

Y el corolario visual: **la imagen nunca espera a la voz**. Si entre dos
frases queda un hueco, algo tiene que estar moviéndose durante el hueco. Más
de 0,4 s sin voz y sin movimiento es un freno.

El presupuesto se hace al revés que sin voz: **la duración ya está dada** —la
del mp3 más ~1,1 s de cola— y lo que decides es qué cabe dentro. Si no cabe,
**quita una cosa; no aceleres todo**.

## 7 · Los efectos: la banda sale del guion


**Los declara el HTML**, con los mismos tiempos que mueven la imagen, dentro del
`window.MARCAS` que ya escribe la pieza:

```js
const SFX=[
  ["barrido", T.movil[0],      0.34],
  ["golpe",   T.movil[1]-0.06, 0.45],
  ["tecla",   T.tap[0],        0.70],
  ["brillo",  T.tap[0]+0.14,   0.24, 1.2],   // el 4º es el tono: >1 agudiza
  ["golpe",   T.cierre[0],     0.50, 0.7],   // grave: el cierre de marca
];
window.MARCAS=Object.assign({},T,{SFX,fin:window.DURACION});
```

`shoot.mjs` lo escribe en el `.marcas.json` junto al mp4 y `sonar-generico.py` lo
monta. **Existen los setenta y cuatro de `../motor/sonidos/`** —grabaciones, con
su índice de para qué sirve cada uno en `../motor/sonidos/INDICE.md`—; los demás
nombres revientan el montaje con un error que te los lista. Lee el índice antes
de escribir el `SFX`. Los que tienen ancla (`subida`, `redoble`, `cuenta-atras`)
no empiezan en su segundo: acaban o golpean en él.

**Si te falta uno**, no lo sustituyas por el pariente más cercano y a correr: si
la persona tiene cuenta de ElevenLabs, genera el que haga falta con
`python3 ../../motor/efectos-eleven.py` (descripción en inglés) y déjalo con el
mismo nombre en `<marca>/sonidos/`, al lado de `salida/`: ese **manda sobre el
del motor**.
Recorta el silencio del principio o el golpe llega tarde (el script lo hace).

Los que más se usan, por lo que pasa en pantalla:

| Pasa en pantalla | Efecto |
|---|---|
| Algo con peso aterriza: una tarjeta, el móvil, el cierre | `golpe` · `boom` si es el remate |
| Un toque, un clic, escribir | `tecla` · `clic` · `teclado` |
| Llega algo: un aviso, un mensaje | `blip` · `notificacion` · `mensaje` |
| Algo aparece o se infla | `pop` · `burbuja` |
| Algo sale disparado o cambia el plano | `whoosh` · `swipe` · `barrido` |
| Algo se enciende, una cifra remata | `brillo` · `revelacion` si lo cambia todo |
| Lo que está mal / lo que sale bien | `error` · `acierto` |
| Dinero: pagar, cobrar, ahorrar | `caja` · `monedas` |
| Antes del giro, antes de la cifra | `subida` (acaba en su segundo) · `redoble` |
| El giro, la caída | `impacto` · `caida` · `freno` · `disco-rayado` |
| La espera, el silencio | `latido` · `reloj` · `grillo` |
| Bar, mesa, papel | `loza` · `vaso` · `brindis` · `papel` · `roce` |

```bash
python3 sonar-generico.py ../<Marca>-<Nombre>.mp4 ../audios/<pieza>-seco.mp3
python3 sonar-generico.py ../<Marca>-<Nombre>.mp4                 # sin voz, si él lo pidió así
python3 sonar-generico.py ../<Marca>-<Nombre>.mp4 ../audios/v.mp3 cama.mp3 0.24
```

El tercer argumento es la música y el cuarto su nivel: a 0,24 es cama de fondo y
por encima de 0,35 acompaña a la voz. ElevenLabs no la genera (plan gratuito):
sale del catálogo sintetizado de `musica/` (`INDICE.md`).
Pásale el `-largo.mp3` —este script **no repite** la música— y el nivel que
aprobó es **0,15**: a 0,30 le sonó fuerte.

Con voz, los efectos van al **0,42** y **agachados** donde se habla: la
envolvente de la voz los baja hasta un 62 %. Sin eso compiten con ella justo
en los golpes, que es donde caen las dos cosas a la vez.

## 8 · La música va por tramos, no de fondo

**Una cama de fondo para todo el vídeo es lo que se evita.** Se declara en el
HTML, colgada de los mismos compases que mueven la imagen, y
`sonar-generico.py` la monta con sus fundidos, subidas y golpes:

```js
const MUSICA=[
  ['tension-latido',   0],                          // el gancho
  ['emocion-cuerdas',  T.giro[0],   0.15, 'corte'], // el giro: subida + golpe, cambio en seco
  ['silencio',         T.antes[0]],                 // el contraste antes del remate
  ['energia-palmas',   T.remate[0], 0.18, 'corte'],
];
window.MARCAS=Object.assign({},T,{SFX,MUSICA,fin:window.DURACION});
```

`[cama, desde, nivel?, transicion?, desdeCama?]`; transiciones `fundido`
(defecto), `sube`, `corte`; `silencio` es un tramo sin música a propósito. Dos
o tres tramos, no seis; el cambio cae en un compás; el corte en seco, una vez.
Las camas, por familia, en `musica/INDICE.md` (con el mapa
de los nombres viejos). Si el HTML no declara `MUSICA`, el tercer argumento de
`sonar-generico.py` sigue valiendo como cama única —así siguen funcionando las
piezas viejas de la app de cuentas—, pero es la excepción.
