# El motor

## La regla que sostiene todo

**Nada de animaciones CSS. Todo cuelga de `window.seek(t)`, que es función pura del
tiempo.** No hay `transition`, no hay `@keyframes`, no hay estado que dependa del
fotograma anterior.

El motivo no es purismo: el vídeo se captura fotografiando la página una vez por
fotograma, y una animación CSS avanza con el reloj del navegador, que no va al mismo ritmo
que las capturas. Con `seek(t)` el fotograma 137 sale igual lo captures cuando lo
captures. Sin eso, el vídeo tiembla.

Si te ves escribiendo `setTimeout`, `requestAnimationFrame` o una variable que acumula,
párate. Todo se calcula desde `t`.

## La segunda regla: se animan `transform` y `opacity`, nada más

`font-size`, `width`, `height`, `top`, `margin` y `padding` son propiedades de
**maquetado**: cambiarlas obliga al navegador a recomponer la página. Aquí eso hace que la
tipografía **hierva** de un fotograma al siguiente y que todo lo que comparte columna se
recoloque.

Si algo tiene que crecer, se dibuja **ya al tamaño final**, se le fija la caja, y se anima
`scale`:

```css
.cifra{font-size:214px; height:226px;   /* la caja no se mueve nunca */
       display:flex; align-items:center; justify-content:center}
```
```js
el.cifra.style.transform='scale('+mix(150/214,1,k)+')';
```

**La excepción, desde el 6 sep 2026: el morph.** En [motion-ui.md](motion-ui.md) un
mismo contenedor pasa de círculo a píldora a cuadrado cambiando `width`, `height` y
`border-radius`. Vale **sólo** si dentro no hay texto en flujo: sus hijos van en
`position:absolute` (o están apagados mientras muta), así que nada se recompone. Un
texto dentro de una caja que cambia de ancho sigue hirviendo, y `font-size` sigue sin
animarse nunca. `filter:blur()` no es maquetado: se anima sin miedo.

## Lo que la página expone

```js
window.FPS = 60;
window.DURACION = 18.4;      // segundos
window.seek = function (t) { ... };
window.MARCAS = { ... };     // el mapa de compases, para el sonido
```

`shoot.mjs` escribe `MARCAS` en un `.marcas.json` al lado del mp4, para poder pegar los
efectos de sonido fotograma a fotograma en vez de a ojo.

## Los ayudantes

Van en `base.html`, listos.

```js
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const p=(t,a,b)=>clamp((t-a)/(b-a),0,1);   // progreso 0..1 · admite ventanas negativas
const mix=(a,b,k)=>a+(b-a)*k;
const fuera=(t,a,b)=>1-easeOut(p(t,a,b));  // una salida también lleva curva
const frame=t=>Math.round(t*window.FPS);   // el fotograma exacto, para lo que parpadea
```

Y los tres del oficio ([movimiento.md](movimiento.md)):

```js
const arco   =(k,alto)=>Math.sin(k*Math.PI)*alto;          // curva la trayectoria
const respira=(t,amp,hz,fase)=>Math.sin(t*hz*6.283+fase)*amp;  // capa ambiente, no para nunca
const pulso  =k=>(k>0&&k<1)?Math.sin(k*Math.PI):0;         // un destello de ida y vuelta
```

## Las curvas

`bez()` resuelve una `cubic-bezier` de CSS como función pura de x, por Newton-Raphson, que
es lo que hace el navegador por dentro. Curvas buenas, sin librería, sin perder el
determinismo.

| Curva | `cubic-bezier` | Para qué |
|---|---|---|
| `easeOut` | `.23, 1, .32, 1` | **El de por defecto.** Todo lo que entra o sale |
| `easeInOut` | `.77, 0, .175, 1` | La cámara y lo que se desplaza por la pantalla |
| `easeHoja` | `.32, .72, 0, 1` | Lo que sube desde abajo: hojas, barras, sábanas |
| `easeBack` | *overshoot 1.5* | Lo que **aterriza** y pesa |
| `easeAntes` | *undershoot 1.7* | Lo que **sale disparado**: retrocede antes |

`.23,1,.32,1` sale disparada y frena en seco. Es lo que hace que un rótulo se sienta rápido
sin acortarle una décima. Las cúbicas normales de CSS arrancan flojas y hacen que la pieza
parezca lenta aunque los números sean los mismos.

`easeBack` y `easeAntes` son pareja: uno se pasa al llegar, el otro coge carrerilla al
salir. **Ninguno de los dos en la cámara**: una cámara que rebota marea. Y no arranques
una entrada por debajo de **0,88 de escala**: más pequeño no parece que llega, parece que
nace. **Salvo que nazca a propósito**: una ficha que se desprende de un precio, un sello
que se estampa (2,2→1), una píldora que brota de un icono. Esos vienen de otro objeto o
caen de arriba, y el muelle lo cuenta ([motion-ui.md](motion-ui.md)). Lo que **llega**
—un rótulo, una tarjeta, una fila— sigue entrando a 0,94→1 con desenfoque.

**Las salidas también llevan curva.** `(1-p(t,a,b))` es una rampa recta y se nota: usa
`fuera(t,a,b)`.

## El guion, en relativo

Escribir los segundos a mano tiene un problema: mueves un compás y hay que reteclear todos
los de detrás. `guion()` deja declararlos unos respecto a otros y devuelve el mismo `T` de
siempre —pares `[entra, sale]` en segundos absolutos.

```js
const T = guion([
  ['abre',   -0.09,    0.62],   // NEGATIVO: en t=0 va a medio vuelo · ver gancho.md
  ['rompe',  '+=0.18', 0.30],   // 0,18 s después de que ACABE el anterior
  ['dato',   '<',      0.44],   // a la vez que el anterior
  ['prueba', '<0.18',  0.52],   // 0,18 s después de que EMPIECE el anterior
  ['cierre', '+=0.60', 0.55],
]);
```

`T.cierre` es un par, así que se lee `T.cierre[0]`.

**El primer compás casi siempre es negativo.** Es la ley 1 del gancho y el motor la
soporta sin tocar nada.

Pero **adelántalo poco: entre el 10 % y el 15 % de su duración.** `easeOut` gasta el
recorrido al principio —al 20 % de la ventana ya ha hecho el 68 % del camino—, así que un
adelanto grande no da más movimiento en el fotograma 0: da un elemento que ya ha llegado.
La tabla está en [gancho.md](../guion/gancho.md).

## Escribir un `seek`

Un bloque por elemento, en el orden en que aparecen en la pieza:

```js
window.seek=function(t){

  // ── la capa ambiente · fuera del guion, no para nunca ──
  el.halo.style.transform='translate('+respira(t,5,0.11)+'px,'+respira(t,4,0.09,1.7)+'px)';

  // ── la tarjeta cae, en arco ──
  const k=easeOut(p(t,T.cae[0],T.cae[1]));
  el.card.style.opacity=k;
  el.card.style.transform='translate('+(mix(-40,0,k)+arco(k,52))+'px,'+mix(-320,0,k)+'px)';

  // ── su contenido llega 0,09 s después · capa secundaria ──
  const kt=easeOut(p(t,T.cae[0]+0.09,T.cae[1]+0.09));
  el.cardTxt.style.opacity=kt;

  ...
};
```

## La cámara

Sólo si lo que importa está dentro de algo pequeño. `camara(escala, focoX, focoY, dondeX,
dondeY)` devuelve el `transform` de `.escena`. Lo que **no** debe moverse con la cámara
—rótulos, velos, el cierre— va **fuera** de `.escena`.

## El contador

Si un número sube, que vaya **de un importe real al siguiente**, nunca interpolando
fracciones de sus sumandos, o enseña cifras que no son de nadie:

```js
let v=0, desde=0;
for(let n=0;n<PASOS.length;n++){
  const hasta=desde+PASOS[n];
  const k=easeOut(p(t,marcas[n]+0.06,marcas[n]+0.46));
  if(k>0) v=mix(desde,hasta,k);
  desde=hasta;
}
```

## Cómo se captura

```bash
node mirar.mjs pieza.html 0 0.5 1.4 3.0      # fotogramas sueltos → /tmp/mirar
node medir.mjs pieza.html <id> <fA> <fB>     # ¿tiembla el maquetado?
node shoot.mjs pieza.html salida.mp4         # el mp4
```

`shoot.mjs` renderiza al doble y baja a 1080 con lanczos: el texto fino se rompe si se
captura a 1x.


<!-- fundido · 25 ago 2026 -->

## El gesto de tocar


El manual documenta un gesto y sólo uno: `transform: scale(0.96)` durante
**120 ms**. Lo lleva todo lo que se toca, y **lo que ese toque dispara empieza
0,06–0,08 s después**, no a la vez. Ese retardo minúsculo es lo que hace que
parezca causa y efecto en vez de dos cosas sueltas.

```js
el.boton.style.transform = 'scale(' + pulsa(t, T.toque[0]) + ')';
```

## Las fotos reales dentro de la pieza


Las fotos reales entran como `background-image` con `url('../recursos/fotos/…')`
—ruta relativa desde el HTML, que vive en `_generador/`— y **siempre con un
degradado del negro por encima**, o el texto no se lee sobre ellas:

```css
.foto{background-size:cover;background-position:center;filter:grayscale(.35) contrast(1.05)}
.foto::after{content:"";position:absolute;inset:0;
  background:linear-gradient(to top,#050505 0%,rgba(5,5,5,.55) 45%,rgba(5,5,5,.15) 100%)}
```

El `grayscale` parcial es de la web (las fotos de reseñas y del «sobre mí» van
desaturadas en algunas marcas): iguala fotos hechas con luces distintas y deja
que el color de acento sea lo único de color en el cuadro.

Puppeteer arranca con `--allow-file-access-from-files`, así que las rutas
locales cargan. Comprueba en un fotograma que la foto salió: si la ruta falla,
lo que ves es un rectángulo negro que parece intencionado.
