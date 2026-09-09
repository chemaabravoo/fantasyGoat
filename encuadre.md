# El encuadre

# El encuadre

## El lienzo


1080 × 1920 a 60 fps. Fondo `#141010` con el resplandor cálido:

```css
background-image:radial-gradient(60% 36% at 50% 46%,rgba(232,176,75,.11),transparent 72%)
```

**Zonas seguras (6 sep 2026).** El autor pasó las dos referencias (Reels: 250 arriba,
350 abajo, 100 izquierda, 200 derecha; TikTok: el carril de botones a la derecha y el
caption abajo) y, tras dos pasadas mal entendidas, lo dejó dicho así:

> «Quiero que todo mantenga su tamaño, simplemente que las partes de foco no sean justo
> las partes donde están las zonas no seguras. Los textos, que no estén arriba del todo,
> y por abajo igual, y que no pase nada en el lateral derecho, que es donde se tapa con
> los botones de me gusta. NO ES HACERLO MÁS PEQUEÑO, al igual que no es poner las frases
> centradas en la zona segura, porque entonces se ven visualmente descentradas.»

Las tres reglas que salen de ahí, en este orden:

1. **Nada cambia de tamaño ni de centro.** El lienzo sigue siendo 1080 y todo se centra
   en **540**: los rótulos, la mesa, los paneles, la tarjeta del cierre. Una frase
   centrada en 490 «para caber» se nota corrida a la izquierda y es peor que el problema.
   Tampoco se encoge nada: el escenario (mesa de 1000, paneles de 960, resplandor) se
   mete por los lados no seguros con toda naturalidad.
2. **Lo que se lee y lo que pasa, fuera de las franjas tapadas.** Las franjas son: arriba
   hasta **250** (el título «Reels», las pestañas de TikTok), abajo desde **1520** (caption,
   nombre, música, navegación) y **la columna de la derecha desde x 910** (corazón,
   comentarios, compartir; en la app empiezan hacia 940). El margen izquierdo no tapa
   nada importante. Ahí no van rótulos, cifras, sellos, bocadillos, ni la acción (una
   ficha que aterriza, una silla que se levanta). Un borde de mesa o un muñeco de
   relleno sí pueden estar.
3. **Si una frase no cabe centrada sin llegar a la columna, se acorta la frase**, no la
   letra, y no se corre el centro. A 60 px caben unos 24-26 caracteres por línea
   (740 px, de 170 a 910). Dos líneas cortas, no tres.

Números que se han quedado fijos con esa regla:

- Rótulos entre **254 y 380**, a su tamaño, en una caja centrada de 960 (60→1020).
- Seis sillas a 128 px, centradas: `MX=[220,348,476,604,732,860]`; el último importe
  (chip de 118) acaba en 919. La mesa, de 40 a 1040.
- Paneles anchos (60→1020) con relleno a la derecha para que su última cifra acabe
  antes de 910; la barra LO TUYO de 100 a 980 con el botón terminando en 880.
- Nada que se lea por debajo de 1520.
- La cámara no acerca más de 1,1: lo que estaba en el borde se sale.

`validar.mjs` mide **las letras** (los rectángulos de los nodos de texto, no la caja del
elemento) contra x 100–910 e y 250–1520, con 10 px de tolerancia para el sobrepaso de un
muelle, y **se niega** si un texto se sale (`--sin-zonas` lo deja en aviso). Una caja ancha
con el texto centrado vale; un botón con un destello que se sale, también.

**Si la pieza va a promocionarse en TikTok (anuncio / Spark Ads)**, la referencia es más
dura: el bloque con el botón de descarga come la mitad inferior. Ahí el corazón de la
pieza —la cifra que importa, la frase citable— va además dentro de **x 80–900, y 430–1250**.

Referencias: la de Reels (It's Deb's media) y la captura orgánica de TikTok en
[zonas-seguras-tiktok.png](zonas-seguras-tiktok.png).

## La cámara


```js
const camara=(s,wx,wy,sx,sy)=>
  'translate('+(sx-s*wx)+'px,'+(sy-s*wy)+'px) scale('+s+')';
```

Coloca el punto del mundo `(wx,wy)` en el punto del cuadro `(sx,sy)` a escala
`s`. Con `transform-origin:0 0` sale una traslación limpia y **el punto
enfocado no se mueve aunque cambie la escala** — por eso lo que enfocas no
baila al acercarse.

Se aplica al contenedor `.escena`, que lleva dentro todo lo que viaja con el
plano. Los rótulos van **fuera**: en un anuncio los títulos no se mueven con
la cámara.

Reglas que costaron caro:

- **Muévela sólo cuando lo que importa está dentro de algo pequeño** —el
  móvil, una fila, una esquina del ticket—. Si el protagonista es una pieza
  flotando, que la escala de la pieza haga el trabajo y la cámara se esté
  quieta.
- **Nunca multipliques la escala de una pieza por la de la cámara.** Una fila
  a 2× con la cámara a 1,42 son 2,8×: se sale del cuadro por los lados.
- `easeInOut` siempre, 0,70–1,10 s.
- Antes de subir el zoom, comprueba que lo ancho sigue cabiendo. El tope
  práctico con una barra de 800 px en la pantalla es **1,26**.

### El velo de titular

Cuando la cámara se acerca, el contenido del móvil sube hasta donde vive el
rótulo y se pisan. Hace falta una protección, encendida con el mismo factor
que la cámara:

```css
.velo-tit{position:absolute;top:0;left:0;right:0;height:560px;opacity:0;
  background:linear-gradient(to bottom,#141010 0,#141010 300px,
    rgba(20,16,13,.78) 410px,rgba(20,16,13,0) 100%)}
```

## El foco


Cuando una pieza se despega del móvil para verse de cerca, **lo demás se apaga
al 0,95**. Un velo `#0a0806` entre el móvil y la pieza.

No es estética: las piezas de `sin-fondo/` tienen el relleno translúcido —en
la interfaz es un acento al 8 %—, así que si detrás se ve la app, la fila se lee dos
veces y no se entiende cuál manda.

## El velo de titular


Cuando la cámara se acerca, el contenido sube hasta donde vive el rótulo y se
pisan. Hace falta una protección, encendida con el mismo factor que la cámara, y
que dure **todo el tramo explicativo** — no lo que dura cada rótulo, o parpadea
en los huecos.

```css
.velo-tit{position:absolute;top:0;left:0;right:0;height:560px;opacity:0;
  background:linear-gradient(to bottom,#101210 0,#101210 300px,
    rgba(16,18,16,.78) 410px,rgba(16,18,16,0) 100%)}
```

Ojo: **esto no contradice el «sin degradados»** del manual. Aquel prohíbe el
degradado como decoración de fondo; esto es una máscara de legibilidad, igual
que la banda sólida que el manual exige debajo de un texto sobre foto.

## Texto sobre foto


El manual es tajante: **sobre foto no hay contraste que se pueda garantizar**.
Si un texto cae encima de una foto de bar, o va sobre una banda sólida, o va
sobre un velo que llegue a `rgba(16,18,16,.78)` como mínimo en la zona del
texto. Medirlo, no mirarlo.

## Las fotos, encuadradas


Una foto de alguien entrenando es un plano horizontal metido en un cuadro
vertical: siempre vas a recortar. Dos maneras que funcionan:

- **A sangre**, ocupando el lienzo entero con el degradado del negro por
  arriba y por abajo, y el texto en la franja de abajo (por encima de 1560).
- **En ventana**, 840 × 620 centrada con radio 32, sobre el negro. Deja sitio
  para un rótulo arriba y una cifra debajo, y perdona mucho más el recorte.

`background-position` por defecto a `center`; si la cabeza se va, súbelo a
`center 30%` y **míralo en un fotograma**, no lo supongas.

## El móvil entero


No se dibuja: es un iPhone real recortado, de `../motor/moviles/`, con la app
montada en el hueco de la pantalla y la muesca o la isla tapándola por arriba.
Cómo se monta, la geometría de los dos que hay y el script que recorta otro:
[cristal.md](cristal.md).
