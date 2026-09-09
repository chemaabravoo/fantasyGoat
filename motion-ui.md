# El estilo de la casa: motion UI

**Desde el 6 de septiembre de 2026 las piezas se animan así.** El autor lo
vio en un vídeo de motion de interfaz al estilo Apple (isla dinámica, listas,
cursor, ruta) y pidió lo mismo en HTML. Palabras suyas sobre la primera
prueba: *«me gusta el estilo de animación, cómo se mueven las cosas, cómo se
ven, el dinamismo sobre todo»*; y sobre la tercera: *«esto me gusta más que
reel-motor para crear un vídeo, mucho más dinámico como se anima todo, me
encanta»*. No es una skill aparte: es **cómo se mueve todo** en este motor, para
cualquier marca. El motor antiguo está guardado en
`(el motor anterior, ya retirado)`.

Las tres piezas de referencia, de menos a más:

| Pieza | Qué enseña |
|---|---|
| `ejemplos/pieza-01-reproductor.html` | La demo neutra, 1:1: isla que muta, lista en escalera, cursor, trazo, cuentakilómetros |
| `ejemplos/pieza-04-antes-despues.html` | El estilo sobre la app real de una marca (17,5 s, muda) |
| `ejemplos/pieza-03-sabias.html` | La de lucirse: 44,6 s cuadrados palabra a palabra con una locución, cámara, lluvia de 72, fichas, barras, giro 3D, tipografía cinética |

## Las siete leyes del estilo

1. **Todo entra de borroso a nítido y sale al revés.** `filter:blur()` de 14-16
   px a 0, con un poco de desplazamiento y escala 0,94→1. Nada aparece por
   opacidad seca. La salida es el mismo gesto al revés (`fuera()`), y si sale
   deprisa lleva desenfoque proporcional a la velocidad (`pulso(k)*10px`).
2. **Un objeto que muta, no cortes.** La isla es círculo, luego píldora, luego
   cuadrado, luego lista. El papel del ticket se vuelve la hoja de cuentas. Se
   cambian ancho, radio y color del **mismo** elemento; el siguiente estado
   nace del anterior.
3. **Lo que aterriza lleva muelle.** `spring(k)` con sobrepaso: la píldora se
   pasa de ancha y vuelve, el sello llega girado y grande y se asienta, la barra
   se pasa del marcador. `easeOut` para lo que entra; `spring` para lo que pesa.
4. **Escalera de 60-90 ms.** Ítems, palabras, fichas, filas: nunca a la vez.
   `palabras()` para los textos, `i*0.09` para las filas.
5. **La cámara existe y tiene profundidad de campo.** Entra en lo que importa
   (`camara()` a 2,4×), lo que no está en foco se desenfoca y se apaga al 30 %,
   y el desplazamiento entre dos focos lleva desenfoque direccional
   (`scaleX(1+vel*0.16)` + blur). Un temblor corto (`shake()`) en los golpes.
6. **Siempre hay una cifra rodando.** El cuentakilómetros (`odo()`): cada
   dígito rueda solo cuando cambia, con desenfoque mientras rueda. Y las
   cifras corren por sumas reales (`odoPasos()`), nunca interpolando céntimos
   que no existen.
7. **Los objetos son los de la marca, no píldoras genéricas.** Fue el primer
   rechazo: «no has usado la tipografía ni los recursos de la app». En la app de cuentas
   son las piezas reales de la app (filas de comanda con «✓ 1 de 6», barra
   LO TUYO, hoja de cuentas, ticket de papel, portada «Sube la foto del
   ticket»). En el entrenador, las tarifas, el calendario, los muñecos y el
   teléfono. En el alquiler de baterías, la máquina y la batería. Se copian de las
   capturas reales, con la tipografía de la marca.

## El vocabulario

Cada movimiento, para qué sirve y con qué se hace. Los ayudantes están en
`../motor/base.html`.

| Movimiento | Para qué | Cómo |
|---|---|---|
| **Blur-in / blur-out** | Toda entrada y salida | `blurIn(el,k)` · `palabras(spans,t,a,paso,dur,sal)` |
| **Morph** | Un estado que se vuelve el siguiente | Un solo elemento: `width/height/borderRadius/background` con `mix` y `lerpCol` |
| **Muelle** | Lo que aterriza y pesa | `spring(k, z=0.42, w=13)`; para barras que se pasan, `spring(k,0.35,11)` |
| **Escalera** | Listas, palabras, fichas | `a + i*0.09` |
| **Cursor con estela** | Un toque que se ve venir | `cursor(...)`: dos fantasmas donde estaba hace uno y dos fotogramas, anillo ámbar al tocar, `scale(.85)` al pulsar |
| **Trazo + moneda** | Algo que va de A a B y se ve el camino | `stroke-dashoffset` para dibujarlo, `getPointAtLength` para que algo lo recorra |
| **Fichas que vuelan** | Un importe que se reparte o se junta | `vuela(el,t,a,b,desde,hasta,alto)`: arco, estiramiento por velocidad y giro leve; al llegar, un `pop` y el contador de destino suma |
| **Cuentakilómetros** | Cualquier cifra que cambia | `odo(node,'10,40 €','14,25 €',k,H)` · `odoPasos(node,[[t,'…'],…],t,H)` |
| **Lluvia con gravedad** | Muchos que llegan (72 desconocidos) | `easeCae` en la caída, `spring` en el aterrizaje (aplasta y vuelve), `hash(i)` para la dispersión |
| **Divisor / dos mundos** | Dos condiciones frente a frente | Línea que crece con `scaleY`; los anillos de un lado se parten en trazos (`stroke-dasharray`), los del otro se sueldan y se rellenan |
| **Cámara + profundidad** | Entrar en una mesa, una fila, un dato | `camara()`; lo no enfocado: `blur(7px)` y opacidad 0,3; entre focos, desenfoque direccional |
| **Control real** | La app haciendo lo suyo | La fila se abre con muelle y aparecen sus controles de verdad (un «− 1 +», un botón); el cursor los toca |
| **Filas fantasma** | «Los otros cinco piensan lo mismo» | Cinco copias apiladas detrás con `translateY(-24·i) scale(1-.035·i)` y opacidad decreciente |
| **Barras con muelle y sello** | El dato que remata | La barra se pasa del marcador (`spring` 1,15) y vuelve; el sello entra `rotate(-16→-4) scale(2.2→1)` con un arco que se dibuja alrededor y `shake()` |
| **Giro 3D** | Un objeto que vuelve con otro valor | `perspective(1400px) rotateX(-80→0deg)` con `transform-origin` abajo |
| **Tipografía cinética** | Las frases del giro y el remate | Palabra a palabra; la que importa cae `scale(2.4→1)` con blur y temblor; lo que se niega se tacha con una línea que crece (`scaleX`) medida sobre el texto |
| **Destello** | El botón del cierre | Un brillo que recorre el botón (`skewX(-20deg)` y `translateX`) una sola vez |
| **Rayos de luz** | El primer segundo | Dos barras largas desenfocadas cruzando en diagonal, y se van |
| **Capa ambiente** | Que nada esté quieto | `respira()` en la isla, el glow late, el reloj gira, la moneda gira |

## Cuadrar con la voz, palabra a palabra

Este estilo se sincroniza **por palabra, no por frase**: el sello cae en la cifra
que la voz dice, la ficha sale en el verbo, la tachadura en la palabra que niega. El
mapa lo da `marcas.py` desde la transcripción con tiempos de la toma (`toma.py`), como
un objeto `M` con el segundo de cada frase y de las palabras que disparan algo:

```js
const M={f1:0.10, f2:3.28, precio:21.04, gratis:30.94, fin:41.2};
```

Los compases cuelgan de `V`, nunca de segundos a mano. **La imagen no espera a
la voz**: lo que acompaña a una palabra empieza 0,05-0,15 s antes de que suene.

## El sonido

Vale lo de siempre ([voz.md](../sonido/voz.md)): voz frase a frase, efectos en `SFX`,
música por tramos. Dos matices de este estilo:

- **Si la pieza usa un audio ya publicado** (voz + cama mezcladas), se le pasa
  a `sonar-generico.py` como voz, sin `MUSICA`, y sólo se añaden efectos a
  0,25-0,5 de ganancia: la cama ya va dentro.
- **Muda sólo si el cliente lo pide para esa pieza.**

## Dónde chocaba con el motor de antes, y qué manda

Revisado el 6 sep 2026 contra todas las referencias. Cinco choques, los cinco resueltos
en el sitio donde estaba la regla vieja:

| La regla de antes | Lo que hace este estilo | Queda así |
|---|---|---|
| «Se animan `transform` y `opacity`, nada más» | El morph cambia `width`, `height` y `border-radius`; y anima `filter:blur` | El morph vale si dentro no hay texto en flujo; el blur no es maquetado ([motor.md](motor.md)) |
| Personalidad «seca» = sin rebote (la app de cuentas, el alquiler de baterías) | Muelle en todo lo que aterriza, y a él le encantó en la app de cuentas | «Seca» pasa a ser muelle corto, `spring(k,0.60)`; la tabla nueva en [movimiento.md](movimiento.md) |
| «No arranques una entrada por debajo de 0,88 de escala» | Fichas que nacen a 0,4, sellos que caen desde 2,2 | Lo que **llega** sigue a 0,94→1; lo que **nace** de otro objeto puede nacer ([motor.md](motor.md)) |
| «Ninguna curva con rebote en la cámara» | `shake()` sobre la cámara en los golpes | El temblor no es rebote: tres décimas que se apagan solas, una o dos veces por pieza ([movimiento.md](movimiento.md)) |
| «Nunca abras una pieza anterior» | Aquí se citan tres piezas de referencia | Se abren para ver la técnica; el ayudante está en `base.html`; el plano no se trae ([forma.md](forma.md)) |

Lo demás no chocaba: el `seek(t)` puro, las curvas, la capa ambiente, el latido, el
gancho en negativo, las zonas seguras, la voz frase a frase, el render y el vistazo son
los mismos. El estilo cambia **cómo se mueven las cosas**, no el oficio de sacarlas.

## Cuánto movimiento es suficiente · `energia.mjs`

Las siete leyes dicen **cómo** se mueve cada cosa. Esto dice **cuánto**, que es lo que
separa una pieza que funciona de una que el autor llama «cutre» aunque cada fotograma
suelto esté bien compuesto.

```bash
node ../../motor/energia.mjs pieza-<nombre>.html
```

Muestrea cada 0,25 s y mide **cuánto cambia la escena** de una muestra a la siguiente,
sin contar el cielo. Dos números:

| | |
|---|---|
| **energía media** | por debajo de 15 la pieza se siente plana · 25-35 es el estilo de la casa · por encima de 45, probablemente marea |
| **tramos flojos** | los segundos en que casi nada se mueve. **Más de un tercio de la pieza en flojo y se nota** |

### Por qué no vale «¿hay dos fotogramas iguales?»

Fue el primer intento y **no sirve**: la cámara respira, así que nunca hay dos fotogramas
idénticos. Medido el 8 sep 2026 sobre dos versiones del mismo anuncio, esa cuenta daba
**0 % de fotogramas repetidos en las dos**, y una de las dos era claramente floja. Lo que
el ojo lee como «se mueve» es la **magnitud** del cambio, no que cambie algo.

    la floja  ·  energía 12,4  ·  41 s de 56 en flojo (73 %)
    la buena  ·  energía 28,3  ·  21,5 s de 56 (38 %)

### De dónde sale la diferencia, por orden de impacto

1. **Quitar tiempo muerto pesa más que añadir efectos.** La mitad de la mejora fueron dos
   huecos de cuatro segundos en los que sólo había un elemento entrando. No se arreglan
   animando más ese elemento: se arreglan **poniendo algo que ya esté pasando** —en aquel
   caso, una ruleta de marcas girando detrás que frena y para en el golpe.
2. **Lo que aterriza no se queda quieto.** Un `spring` que termina y ya está deja el
   elemento congelado hasta que salga. Después del muelle va una oscilación pequeña que no
   para (`Math.sin(t*…)` sobre la altura, `respira()` sobre el giro). Ahí se pasó de una
   llamada a `respira` a nueve, y es lo que mata los «once segundos congelados».
3. **Más cosas a la vez, escalonadas.** De 12 elementos animándose a 28. Un compás nuevo
   cada 1,5 s dentro del mismo plano —una fila de chips, un titular, una cifra que
   rueda— en vez de un plano con una sola cosa.
4. **Muelle en vez de fundido.** Si casi todo entra con `easeOut`, la pieza «aparece» en
   vez de moverse. De 5 `spring` a 12.

### Cuándo se pasa

**Antes del vistazo, siempre**, junto a `validar.mjs` y `contactos.mjs`. Y las tres cosas
se miran en este orden, porque cada una ve algo que las otras no:

    validar.mjs    lo que está roto o se sale del encuadre
    energia.mjs    si la pieza se mueve lo suficiente, y dónde no
    contactos.mjs  qué es exactamente lo que está quieto — se ve en la fila, no en el fotograma

## Las trampas de este estilo

- **El reproductor de la página pisa `seek(t)` bajo Puppeteer.** Las piezas
  llevan un player con `requestAnimationFrame` para verlas en el navegador;
  bajo captura tiene que arrancar parado: `let playing=!navigator.webdriver`.
- **El `fit()` que escala el lienzo al navegador rompe la captura.** Bajo
  `navigator.webdriver`, `transform:none` en `#reel`, o shoot-par saca
  523×930 en vez de 540×960.
- **El cuentakilómetros con cifras de distinta longitud.** «5,65 €» contra
  «21,40 €»: se rellenan por la izquierda con `padStart` o las columnas se
  desalinean y sale «5,€5 €».
- **El relleno de una barra necesita `width:100%`** si es un `<i>` absoluto;
  si no, `scaleX` no enseña nada.
- **Las fichas aterrizan fuera del anillo** (`asiento(m,j,1.62)`), no encima
  de la inicial.
- **Un rótulo encima de otro.** El título de dos líneas pisaba el primer ítem
  de la lista; se mide con `contactos.mjs`, no se supone.
- **Los scripts se llaman siempre del motor** (`node ../../motor/…`), no se copian a la carpeta de la marca: las copias envejecen.