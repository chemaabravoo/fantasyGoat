# Las trampas

Fallos ya pagados. Cada uno costó un render. Se lee **antes de dar una pieza por buena**,
no después.

## 1 · La pantalla arranca vacía

El más caro de todos y no es técnico. La pieza empieza en negro, algo entra con una curva
preciosa, y para entonces ya la han pasado. **El primer compás va en tiempo negativo**
([gancho.md](../guion/gancho.md)). Compruébalo siempre: `node mirar.mjs pieza.html 0`.

## 2 · Animar `font-size` es animar el maquetado

Una cifra que crece de 150 px a 214 px de `font-size` da **catorce anchos distintos en 36
fotogramas**: cada tamaño intermedio recompone la tipografía y la ajusta a la rejilla de
píxeles, así que los palos de los dígitos engordan y adelgazan solos. En un fotograma
suelto no se ve; al medirlo, sí.

Caja fija y `scale`. Vale igual para `width`, `height`, `top`, `margin` y `padding`.
La única excepción es el morph de un contenedor sin texto en flujo dentro
([motor.md](../animacion/motor.md), segunda regla).

## 3 · Un ancho variable dentro de un flex recoloca la fila entera

Un botón que pasa de «Pagar 0,00 €» a «Pagar 18,96 €» crece, y lo que tiene al lado se
mueve **en cada fotograma**. Ancho fijo (`min-width` o `flex:0 0 <px>`),
`text-align:center` y `tabular-nums`.

Y comprueba que lo que has fijado **cabe**: si se sale, lo recorta el `overflow`.

## 4 · Medir, no mirar

Un fotograma quieto no enseña un temblor. `offsetWidth` es medida de **maquetado**: la
transformación de la cámara no la toca. `getBoundingClientRect` sí la lleva encima, y
entonces mides el zoom, no el layout.

```bash
node medir.mjs pieza.html <id> <fDesde> <fHasta>
```

Un solo valor = estable. Cuarenta valores = ahí está tu temblor.

## 5 · Un absoluto sin `top` no empieza donde crees

Un `position:absolute` sin `top` ni `bottom` se coloca en su **posición estática**: donde
le tocaría en el flujo. Ponle `top:0` explícito.

## 6 · Lo que se recorta y lo que no

Para que un barrido se quede dentro de una pieza hace falta un contenedor con
`overflow:hidden`. **La sombra va en el contenedor, no en la pieza**: `box-shadow` no lo
recorta su propio `overflow`, así que dentro desaparece.

## 7 · Color sobre el mismo color es invisible

Un rótulo en `--tinta` sobre un papel del mismo crema está ahí, perfectamente renderizado,
y no se ve. Al comprobar solapes **mira el color, no sólo la posición**. Y con el acento,
mídelo ([marca.md](../marca.md)).

## 8 · Un SVG ajeno trae su propio color

Un logotipo de otra marca **no se recolorea**: se le pone **su fondo de marca** detrás. En
el código no se ve; en un fotograma, sí.

## 9 · Fundir dos pantallas enteras no deja ninguna legible

Cruzar opacidades enseña las dos al 50 % durante medio segundo, y ahí no se lee ninguna:
se lee una sopa. **Deslizar**, con la capa opaca desde el primer fotograma. Cuesta lo
mismo.

## 10 · Los valores heredados de una maqueta anterior

Un `translateY` de +700 px que venía de cuando el elemento estaba en otro sitio. Al mover
algo, busca los desplazamientos que apuntaban a su posición vieja.

## 11 · Lo que entra y sale del flujo pega saltos

Un elemento que aparece cambia el alto de su contenedor y todo lo de encima da un brinco.
Que ocupe sitio siempre con `opacity:0`, o sácalo del flujo.

## 12 · Una capa sin gatear enseña un estado que aún no ha pasado

Si algo existe en el maquetado desde el fotograma 0, se ve por detrás contando algo que
todavía no ha ocurrido. Cada capa se enciende **cuando le toca en el guion**, no cuando
está montada.

## 13 · El atrezo que se queda quieto tapa el plano siguiente

Un objeto se posa en el centro y ahí se queda; tres compases después, lo importante
aparece **debajo**. Al montar un plano nuevo, mira qué hay encima de esa zona del plano
anterior y apártalo.

## 14 · El rótulo de abajo y la cámara acercándose se cruzan

Los rótulos van fuera de `.escena`, así que la cámara no los mueve — pero sí mueve lo de
dentro, que acaba detrás del texto. Hace falta un **velo en degradado**. Y que el velo dure
**todo el tramo**, no lo que dura cada rótulo: si se enciende y apaga con cada uno,
parpadea en los huecos.

## 15 · Un parpadeo que no cuadra con la rejilla tartamudea

`Math.floor(t*7)` es función pura de `t` y aun así se ve mal: a 60 fps un periodo de 1/7 s
son 8,57 fotogramas, o sea que cada destello dura ocho o nueve según le toque. El ojo lee
eso como un tropiezo.

**Determinista no es lo mismo que estable.** Lo que parpadee, cuéntalo en fotogramas:

```js
s.style.color=(Math.floor(frame(t)/8+i*1.7)%3===0)?'var(--acento)':'var(--tinta-baja)';
```

**Y si cambias los fps, recalibra lo que cuente fotogramas.** El día que el taller pasó de
30 a 60 (8 sep 2026), los dos cursores de `ejemplos/` (`frame(t)%20<11`) empezaron a
parpadear al doble de rápido hasta que pasaron a `%40<21`. Un `%N` en fotogramas es una
duración disfrazada.

## 16 · La capa ambiente apagada en el tramo largo

Se monta `respira()` para el principio y luego se multiplica por un progreso que la va
apagando. Resultado: en el tramo explicativo, que es el más largo, la imagen está
literalmente congelada. **La capa ambiente no se multiplica por nada del guion.**

## 17 · Un arco con el mismo progreso que el movimiento

`translate(mix(0,-74,k)px, mix(0,-1180,k)px)` no es un arco: es una diagonal recta. El eje
secundario tiene que ir con **otra función** — `arco(k,alto)` ([movimiento.md](../animacion/movimiento.md)).

## 18 · El bucle que no cierra por un píxel

Si la pieza busca bucle perfecto, `seek(DURACION)` tiene que dar exactamente `seek(0)`.
Una opacidad en 0,98 en vez de 1 se ve como un parpadeo en cada repetición.

```bash
node mirar.mjs pieza.html 0 <DURACION>
```

## 19 · La paleta de otro cliente

Arrancar copiando el `marca.css` del cliente anterior. La pieza sale bien, se ve bien, y
lleva la identidad de otro. Se copia **siempre** de `marca-PLANTILLA.css`, que es magenta a
propósito, y se rellena desde el manual ([marca.md](../marca.md)).

Si ves una pieza con banda roja o con acento magenta, es que este paso no se hizo.

## 20 · La tipografía que no carga en `file://`

El render corre sobre `file://`. Una fuente local con ruta relativa mal puesta no carga y
Chrome sustituye por Helvetica sin avisar: la pieza sale entera, bien maquetada, y con otra
tipografía. Míralo en un fotograma antes de renderizar.

Y recuerda que van en **dos** sitios: los tokens `--titular`/`--dato` de `marca.css` y el
`<link>` de Google Fonts de `base.html`. Cambiar uno y no el otro da exactamente este
fallo.


<!-- fundido desde las tres marcas · 25 ago 2026 -->

## 21 · 4 · Los contadores no interpolan sumandos


Si el total sube multiplicando cada línea por lo encendida que está su tarjeta,
enseña céntimos que no son de nadie —2,22 €, 7,83 €— y parece que se ha roto.
Ve de un importe real al siguiente. La receta está en [movimiento.md](../animacion/movimiento.md).

## 22 · 16 · El velo de titular tapa lo que está dentro de la escena


`.velo-tit` va **fuera** de `.escena` y después en el DOM, así que se pinta
encima de todo lo que la escena contiene. Existe para proteger un rótulo que
vive todavía más arriba en el árbol; si el titular de la pieza está dentro de
`.escena` —como el gancho de `amedias`— el velo se lo come y lo que ves es un
texto apagado que no entiendes por qué no brilla. O sacas el titular de la
escena, o apagas el velo.

## 23 · 17 · Un contenedor `flex` se traga el espacio antes de un `<span>`


`<div style="display:flex">nunca es <i>el de la caña</i></div>` pierde el
espacio: en un contenedor flex los nodos de texto se recortan y el hijo se pega
a la palabra anterior. Sale «nunca esel de la caña» y en el código no se ve.
Con `&nbsp;` antes de la etiqueta. Pasó dos veces —`CADA UNOLO SUYO` y
`nunca esel de la caña`—, así que revísalo siempre que mezcles texto y un
`<i>`/`<b>` dentro de un flex.

## 24 · 15 · Un `<video>` no se puede posicionar fotograma a fotograma


El aparejo adelanta el reloj y fotografía; un `<video>` avanza con el suyo, así
que sale congelado en el primer fotograma o desincronizado. El metraje real se
mete como **secuencia de imágenes precargadas** —`./secuencia.sh`, ver
la skill de la marca— nunca como vídeo.

## 25 · 16 · La sombra que se cuela


Esta marca tiene **una sola sombra** y es la que sostiene la máquina en una
foto. En cuanto una pieza lleva tarjetas, es facilísimo ponerles un
`box-shadow` «para separarlas». Si algo no se separa del fondo, el fondo está
mal: cámbiale la superficie.

## 26 · 17 · El peso 700 se cuela por costumbre


Satoshi tiene Bold y Black y el navegador los da sin rechistar. Los titulares de
esta marca van en **600**, y el 500 no existe. Un `font-weight:bold` heredado de
un `<b>` o un `<strong>` es 700: decláralo.

```css
b,strong{font-weight:600}
```

## 27 · 14 · Un antes-y-después tumba el anuncio


Meta rechaza la publicidad que compara cuerpos o que da a entender un cambio
físico personal. Da igual que las fotos sean reales y con permiso: el formato
es el problema. Enseña el trabajo, la constancia o el sitio donde pasa, no dos
cuerpos uno al lado del otro.

Y por lo mismo: «readaptación de lesiones» es lo que dice la web y es lo que
se puede decir. «Te quito el dolor de espalda» es una promesa clínica. La
reseña de Manuel cuenta lo de su protrusión discal **en su boca**, y así es
como puede salir: como reseña, entrecomillada y con su nombre.

## 28 · 15 · El € se come al dígito en la cifra grande


Montserrat 900 cursiva con `letter-spacing:-.03em` es lo que hace que un
titular parezca de la marca, pero a 130 px el euro se monta
encima del último número: «35€» sale con el rabo del 5 cruzando el €. En texto
corrido el euro va pegado, como en la web; **en una cifra de más de 90 px va
en su propio `<i>`**, a `.66em` y con `margin-left:.20em`, alineado a la línea
base. Se sigue leyendo como una unidad y deja de pisarse.

## 29 · 16 · La última palabra del cierre se queda huérfana


La frase del cierre parte donde le toca al ancho, y «…a tu **casa**.» se cayó
sola a la segunda línea. `text-wrap:balance` en `.cierre .frase` reparte las
dos líneas y se acabó. La plantilla ya lo trae.

## 30 · 17 · Un velo al 0,986 no tapa


Un cierre que baja el telón con `opacity` 0,986 deja pasar un 1,4 %. Sobre
tarjetas con borde y resplandor, ese 1,4 % se ve: detrás
del logotipo se leía la tarjeta del precio. Aquí el scrim va a **1**.

## 31 · 18 · La cursiva se pierde si la fuente no ha cargado


Los titulares son Montserrat 900 **italic**. Si la fuente no ha terminado de
cargar cuando se dispara la captura, Chrome sintetiza una cursiva inclinando
la de sistema y el fotograma sale con otra letra. `shoot.mjs` espera a
`document.fonts.ready` y 900 ms más, pero si añades una fuente nueva a la
pieza, compruébalo en un fotograma antes de gastar el render.

## 32 · 19 · Un miembro centrado no existe


Los brazos del muñeco estaban a `left:52`, o sea justo encima del torso, que
va de 31 a 89. Renderizados, con su color, invisibles: cuatro planos de gente
andando sin brazos. Van **a los lados**, `left:20` y `left:84`. Lo mismo vale
para cualquier pieza que se solape con otra del mismo color: si no asoma, no
está. Ver la skill de la marca.

## 33 · 20 · Al escalar el mundo, el cuadro se estrecha


Con `.mundo` al 1,35 el lienzo sólo enseña del x=140 al x=940 del mundo. Una
figura colocada en 868 —que en el maquetado parecía céntrica— salía cortada
por la derecha, y una fila de material se salía entera. La cuenta es
`x_pantalla = 540 + (x_mundo - 540) * escala`, y **se hace antes de colocar
nada**, no después de mirar el fotograma.

## 34 · 21 · Dos capas encendidas al mismo tiempo no dejan leer ninguna


La barra de la hora entró encima del sofá y los relojes encima de los dos
muñecos: tres veces el mismo fallo en la misma pieza. Cuando entra un gráfico
que manda, **el mundo se baja al 0,26–0,34**; y cuando el plano cambia de
verdad —él se levanta del sofá— el mueble se va del todo en vez de quedarse
detrás estorbando. Un plano, una cosa que manda.

## 35 · 22 · Un `const` usado antes de su línea rompe el `seek` entero


`apagaCasa` se declaraba en el bloque del salón pero se usaba en el bloque del
protagonista, que va veinte líneas antes: `Cannot access 'apagaCasa' before
initialization`, y la pieza entera en negro. Es la hermana de la trampa 8 de
otra marca (los nombres colisionando): dentro de `seek()` **todo lo que use
más de un bloque se calcula al principio de la función**.

Y su prima, que costó un render: si la posición de un muñeco se decide con un
`if/else if` por tramos, **un hueco entre dos tramos lo hace desaparecer**. El
protagonista se esfumaba entre el segundo 17,6 y el 19,2 porque ningún tramo
cubría ese hueco. Recorre los tramos en orden y comprueba que se tocan.

## 37 · Dos capas encendidas a la vez no salen en un fotograma suelto


Es la hermana mayor de la 13 y la 34, y la más cara de encontrar a ojo: **cada
capa por separado está bien**. El fallo sólo existe en los instantes en que las
dos están encendidas, y si no muestreas justo ese segundo no lo ves.

El 26 ago 2026, en `reel-vino`, pasó **dos veces en la misma pieza**: la carta
del bar y el contador del precio ocupaban la misma caja durante 2,1 s, y los
seis trozos de la cuenta bajaban por el mismo carril y se montaban unos encima
de otros a mitad de vuelo. Ninguno de los dos salía en los fotogramas que había
mirado, porque los había pedido en otros segundos.

No se busca a ojo: se mide.

```bash
node solapes.mjs pieza.html 0.3
```

Recorre la pieza entera, mide la caja real de cada elemento con `id` cuya
opacidad heredada pase de 0,06, y lista los pares que se pisan más de un 28 %
sin ser uno parte del otro, con el tramo de segundos en que ocurre. Agrupa lo
que **sí** puede solaparse —una fila con su cara y su importe, una banda con su
etiqueta, la comanda con sus partes— para que sólo salte lo que es un fallo.

Si añades una familia de elementos nueva, métela en su `grupo()` o te llenará
la salida de ruido. Y lee lo que quede: hay solapes buenos —el objeto que
aterriza sobre su destino, dos hilos que se cruzan a propósito— y el que decide
cuál es cuál eres tú.

## 36 · 13 · El wordmark pequeño es una mancha


El logotipo es 1216×142 — ocho veces y media más ancho que alto. Por debajo de
~420 px de ancho en el lienzo de 1080, las letras se cierran al bajar a 1080 y
lo que queda es un borrón. Para el cierre, 520–620 px.

## 38 · El `.marcas.json` se escribe al EMPEZAR el render, no al acabar


`shoot-par.mjs` lo escribe en cuanto lee `window.MARCAS` de la página —línea 78,
antes del primer fotograma—, así que durante todo el render ese archivo está
solo en la raíz de la marca. Si algo archiva mientras tanto (`ordenar-reels.sh`,
otra sesión sobre el mismo repo, un watcher), se lo lleva a `Reels/<pieza>/` y
**el paso de sonido peta con `FileNotFoundError` después de haber gastado el
render entero**.

Pasó el 4 sep 2026 en un lote de tres: `cara` y `confianza` salieron enteras y
`aguja`, que tardó 199 s, se quedó muda. El arreglo es de dos segundos —copiar
el json de vuelta al lado del mp4 y volver a llamar a `sonar-generico.py`— pero
sólo si te das cuenta; el `✓` del render ya había salido.

Dos reglas:

- **En un lote, monta el sonido de cada pieza antes de archivar ninguna**, y
  archiva todas al final de una sola pasada.
- **No encadenes render y sonido con `| tail -2` y `set -e`**: el `tail` se come
  el código de salida del python y el lote sigue como si nada. Si quieres que
  pare, comprueba el `-son.mp4` con `ffprobe` antes de seguir.


## 39 · Un `clip-path` recorta DESPUÉS del `filter`

Un cono de luz hecho con `clip-path:polygon(...)` y `filter:blur(18px)` en el **mismo**
elemento sale con los bordes duros: el recorte se aplica a la imagen ya desenfocada, así
que el desenfoque se corta en seco y lo que se ve es un triángulo plano de presentación.

El desenfoque va en **el padre**, y el recorte en el hijo:

```css
.conoW{filter:blur(19px);mix-blend-mode:screen}   /* el padre difumina */
.cono {clip-path:polygon(47.6% 0,52.4% 0,100% 96%,0 96%)}   /* el hijo recorta */
```

Pasó el 6 sep 2026 en la pieza del concierto de el alquiler de baterías y era justo lo que hacía
que la sala se viera «de vectores».

## 40 · Siluetas oscuras sobre fondo oscuro no existen

Un público en negro sobre una sala en negro está perfectamente renderizado y no se ve. No
se arregla aclarando las siluetas —dejan de ser siluetas— sino **poniendo luz detrás**:
una banda de niebla iluminada por cada plano de profundidad, contra la que se recortan.

Es el contraluz de cualquier foto de concierto, y es la diferencia entre una escena que
parece un gráfico y una que parece un sitio.

## 41 · El Python del sistema no llega a ElevenLabs

`urllib` con el Python 3.14 de python.org da `CERTIFICATE_VERIFY_FAILED: unable to get
local issuer certificate`: no trae el almacén de certificados del sistema. Para pedir la
voz por API, **`curl`**, que sí lo usa:

```bash
curl -sS -X POST "https://api.elevenlabs.io/v1/text-to-speech/<voz>?output_format=mp3_44100_128" \
  -H "xi-api-key: $KEY" -H "Content-Type: application/json" \
  -d '{"text":"...","model_id":"eleven_v3","language_code":"es",
       "voice_settings":{"stability":0.5,"similarity_boost":0.75,"speed":1.15}}' \
  -o audios/<pieza>/07-nombre.mp3
```

Y comprueba el resultado con `file`: si la API devuelve un error, escribe el JSON en el
mp3 tan contenta y el fallo aparece tres pasos después, al montar el sonido.

## 42 · El cuentakilómetros sin su clase apila las cifras

Un contador de dígitos que rueda necesita la clase `odo` **en su propio nodo**. Sin ella
las columnas no son flex: se apilan en vertical y sale un «47» donde debía poner «7».
Se ve en un fotograma y no se ve leyendo el código, porque el CSS que falta no da error.

Y dentro, `.odo{flex:none}`: si no, el flex aprieta las columnas y los dígitos se comen
unos a otros.

## 43 · Una chapa de ancho fijo con texto en mono no cabe casi nunca

La mono es ancha y el texto crece con cada palabra. El patrón bueno para una píldora
centrada y absoluta:

```css
left:0; right:0; width:max-content; margin:0 auto; padding:0 44px;
```

Así el relleno es real y el ancho lo pone el texto. Con `width:<px>` te queda un rótulo
que pisa sus propios bordes en la mitad de las piezas.

## 44 · `lerpCol` devuelve `rgb(…)`, así que no se encadena

Dos mezclas seguidas revientan: la segunda hace `parseInt('gb',16)`, sale `NaN`, el color
no se aplica y el elemento se queda con el gris del CSS —sin error en consola—. Si
necesitas encadenar, **mezcla en hexadecimal** y convierte una sola vez al final.

## 45 · `.cur` ya existe: es el cursor del ratón

En `comun.css`, `.cur` es el puntero (`position:absolute; left:0`). Si llamas igual al
cursor de escritura que va detrás de la última letra, se te va a la esquina de su caja y
no entiendes por qué. Los nombres de clase de una pieza no compiten con los del motor:
mira `comun.css` antes de bautizar algo corto.

## 46 · Un `re.sub` de una línea no mata una regla de dos

Parcheas el CSS de una pieza con una sustitución y «no hace nada». Lo que pasa es que la
regla vieja ocupaba dos líneas, sobrevivió al reemplazo y **gana por ser la última**. Si
un parche de CSS no surte efecto, busca la huérfana antes de volver a parchear.

## 47 · Scribe no oye las palabras inventadas

Una marca, un CTA en mayúsculas o un nombre raro salen transcritos como otra cosa
(«MOTION» → *Mocean*, *Muchon*; «Claude» → *Clot*). Entonces `marcas.py` no encuentra la
frase y se planta.

No repitas la toma: abre `audios/<pieza>/marcas.json`, mira **qué palabra oyó de verdad**
en ese punto y pásasela. Cuesta diez segundos; regrabar cuesta dinero.

## 48 · El texto que se sale de la zona segura mientras algo cruza

A veces un rótulo se sale del carril justo cuando otra cosa barre la pantalla, y el
validador se niega. No lo apagues con `--sin-zonas`: **bájale la opacidad por debajo de
0,3** en ese tramo. Lo que casi no se ve, el validador lo ignora — y si a esa opacidad se
sigue leyendo, es que estorbaba.
