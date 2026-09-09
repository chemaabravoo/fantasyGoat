# El gancho · los tres primeros segundos

Todo lo demás de esta skill sirve para que alguien que ya se ha parado siga mirando. Esto
es lo que hace que se pare. Si esto falla, lo otro no se llega a ver.

## El reparto real de esos tres segundos

| Tramo | Qué tiene que estar hecho |
|---|---|
| **0,0 – 0,3 s** | El pulgar frena. Aquí sólo manda el **movimiento**, no el texto: nadie ha leído nada todavía |
| **0,3 – 1,2 s** | Se lee el titular. Cinco palabras, siete como mucho |
| **1,2 – 3,0 s** | Se abre el bucle: queda algo sin resolver que obliga a seguir |

Los tres son distintos y hacen falta los tres. Un titular buenísimo sobre una pantalla
quieta no para a nadie, porque en el medio segundo en que se decide todo el titular aún no
se ha leído.

## Ley 1 · En el fotograma 0 ya hay algo a medio moverse

**Es el error más caro y el más común.** La pieza empieza con la pantalla vacía, algo
entra desde abajo con una curva preciosa… y para cuando ha entrado, el vídeo ya lo han
pasado.

La solución es del motor: **el primer compás arranca en tiempo negativo.**

```js
const T = guion([
  ['abre', -0.09, 0.62],   // en t=0 va por la mitad del recorrido
  ...
]);
```

`p(t,a,b)` acepta una ventana que empiece antes de cero sin tocar nada.

**Cuidado con cuánto adelantas, que aquí está el error fino.** `easeOut` va tan cargada al
principio que gasta el movimiento enseguida: al 20 % de la ventana el elemento ya ha
recorrido el 68 %, y al 40 % está en el 93 % — o sea, quieto.

| Ventana consumida en t=0 | Recorrido real | Se ve |
|---|---|---|
| 10 % | 40 % | **En pleno vuelo. Esto es lo que se busca** |
| 15 % | 56 % | Bien, ya frenando |
| 25 % | 78 % | Justo, casi puesto |
| 40 % o más | 93 % + | **Quieto. El gancho está roto** |

Regla: **adelanta entre el 10 % y el 15 % de la duración de la entrada**, no más. Para una
entrada de 0,62 s eso son 0,07–0,09 s en negativo. Un adelanto grande no te da «más
movimiento»: te da un elemento que ya llegó.

**Comprueba siempre el fotograma 0 con `mirar.mjs pieza.html 0`.** Si sale una pantalla
vacía o un elemento entero y quieto, el gancho está roto por muy bueno que sea el copy.

Y sirve doble: ese fotograma 0 es la **portada** en la parrilla del perfil.

## Ley 2 · Los tres ganchos son simultáneos

```
[GANCHO VISUAL] + [GANCHO DE TEXTO] + [GANCHO SONORO]
```

- **Visual** — un movimiento que no se sabe a dónde va. Algo rompiéndose, algo
  multiplicándose, algo que va al revés de lo esperado, una escala imposible.
- **Texto** — el titular en pantalla. Se lee aunque el vídeo vaya en silencio, que es como
  lo ve más de la mitad de la gente.
- **Sonoro** — un golpe seco en el fotograma 0 o muy cerca. Sin esto la pieza empieza
  «apagada» aunque se vea bien.

Los tres tienen que decir lo mismo. Si el texto promete una cosa y la imagen enseña otra,
no se lee ninguna.

## Ley 3 · Se abre un bucle y no se cierra

Un bucle abierto es **una pregunta que la propia imagen plantea y no responde**. La gente
no se queda por interés: se queda porque le molesta no saber.

Formas que funcionan, en animación:

- **El número tapado.** Un total con los dígitos ocultos, un contador que sube y se corta
- **Lo roto sin explicar.** Algo se parte en el segundo 1 y no se dice por qué
- **La cuenta atrás.** Un reloj corriendo desde el principio y ya se ve que no llega
- **El resultado primero.** Se enseña el final y se retrocede
- **El que falta.** Cinco huecos, cuatro llenos

Regla: **el bucle se cierra en el último tercio, nunca antes.** Si en el segundo 6 ya se
ha resuelto, el resto del vídeo no tiene por qué verse.

## Ley 4 · Cada segundo, una animación DISTINTA (no la misma moviéndose)

El autor, 2 sep 2026, viendo una pieza cuyo gancho estaba «bien»:

> «No se anima nada durante los primeros siete segundos. Y no digo animar de que
> se muevan un poco, si no animar de dinámico, de aparecer, desaparecer, otra
> animación, ¿sabes? Es lo más llamativo. Los primeros segundos son cruciales:
> **no puede haber un segundo sin animación diferente.**»

Lo que estaba mal no era que la pantalla estuviera quieta —había deriva de
cámara, respiración, un halo moviéndose—: era que **el tipo de movimiento no
cambiaba**. El ojo se acostumbra a un movimiento continuo en menos de un
segundo y deja de leerlo como información.

**La regla práctica: en los primeros cinco o seis segundos tiene que haber un
gesto nuevo cada segundo, y de familias distintas.** Familias que valen:

| Familia | Ejemplo |
|---|---|
| Barrido | un `clip-path: inset()` que descubre el fondo o escribe un texto |
| Estampado | algo que entra a escala 2,4 y aterriza con `easeBack` |
| Ola discreta | veinte casillas que aparecen escalonadas, no un bloque que hace *fade* |
| Lluvia | partículas con su propio retardo por índice |
| Giro / volteo | una carta que se aplasta en `scaleX` y sale con otra cara |
| Trazo | una flecha o un tachón que se dibuja con `stroke-dashoffset` |
| Rotura | una hoja que se parte en tiras y cae |
| Conteo | un número que sube de verdad, con su unidad |

Dos gestos de la misma familia seguidos cuentan como uno solo.

**El error de implementación que lo rompe todo**, y que ha pasado dos veces: la
lluvia escalonada mal escalada. Si el reparto por partícula satura antes de que
acabe la ventana, TODAS llegan a la vez, desaparecen a la vez y no se ve nada.

```js
// mal: con easeOut la ventana se consume en el primer tercio
const pi = clamp(easeOut(k)*1.75 - retardo, 0, 1);
// bien: rampa LINEAL, retardo por índice, y cada una con su recorrido
const bruto = p(t, T.lluvia[0], T.lluvia[1]);          // lineal, 0→1
const pi = clamp((bruto*1.34 - (i%9)*0.062 - d*0.10) / 0.32, 0, 1);
```

Y se comprueba mirando **un fotograma en mitad de la ventana**, no el del final:
si ahí no hay nada volando, la lluvia no existe.

## Las fórmulas, traducidas a imagen

Esta tabla es **cómo se anima cada fórmula**. El texto de la columna del medio es el
esqueleto, no la frase: se reescribe con las palabras de la marca ([tono.md](tono.md))
antes de que entre en la pieza.

| Fórmula | El texto | Y en pantalla se hace así |
|---|---|---|
| **Contradicción** | «X está mal y todo el mundo lo hace» | Lo esperado, montado bien y completo. Y en el segundo 1,2 se **tacha, se rompe o se cae** |
| **Pregunta fuerte** | «¿Por qué nadie…?» | La pregunta ocupando el lienzo entero. El objeto entra **detrás**, empequeñecido |
| **Número primero** | «El 80 % de…» | La cifra ya está en pantalla en el fotograma 0, **subiendo**. Que arranque a media cuesta |
| **Antes/después** | sin texto | Un solo **corte seco** en el 0,8. Sin transición, sin fundido |
| **Interrupción de patrón** | mínimo | Empieza como otra cosa distinta —un chat, un marcador, un panel de aeropuerto— y a los 1,5 s se revela |
| **Confesión** | «Llevo dos años haciéndolo mal» | Plano cerrado en un detalle. La cámara **se aleja** y aparece el desastre |
| **Enumeración** | «Tres cosas que…» | Los tres huecos vacíos ya visibles. Se van llenando |

**Descarta la primera que se te ocurra.** Suele ser la más gastada del sector.

## El gancho se arregla en el guion, no en la animación

**6 sep 2026, el entrenador.** El autor rechazó dos arranques seguidos —«es una auténtica
basura», «¿no notas el cambio de ritmo?»— de una pieza cuya segunda mitad le parecía
buena. El fallo no estaba en la animación: estaba en que las frases del principio eran
largas («Pero primero, el tráfico», «Aparcar. Y cola en la máquina»), así que **los eventos
caían cada 1,5-2 s en el gancho y cada 0,5 s en el desarrollo** — justo al revés de la
tabla del latido.

Retocar la animación no lo arregla: los compases cuelgan de la voz. Lo que lo arregló fue
**reescribir el gancho como una ráfaga de palabras sueltas** —«Tráfico.» «Aparcar.»
«Cola.» «Vestuario.»— generadas una por llamada y montadas con **0,12 s de hueco**: cuatro
golpes en 2,1 s, cada uno con su objeto entrando de fuera del cuadro, su cifra saltando y
su temblor de cámara.

**La comprobación, antes de animar:** escribe los huecos del mapa de voz en una columna. Si
los del gancho son mayores que los del desarrollo, la pieza ya está rota y ninguna curva la
salva.

## Lo que mata un gancho

- **Un logotipo en el segundo 0.** Nadie se para por una marca que no conoce. El cierre
  va al final; el principio es para el conflicto
- **Construir contexto antes del conflicto.** «En un bar de Málaga…» — no. El conflicto
  primero, el contexto después, y sólo el que haga falta
- **Una entrada larga y elegante.** Elegante es de marca consolidada; aquí se busca que
  frenen. Entra en 0,4 s
- **Más de siete palabras en pantalla.** No da tiempo
- **Que el gancho sea sólo el texto.** Si al quitar el rótulo el primer segundo es una
  pantalla quieta, no hay gancho, hay un titular

## El test, en tres comprobaciones

```bash
node mirar.mjs pieza.html 0 0.5 1.4 3.0
```

1. **t=0** — ¿hay movimiento? ¿aguanta como portada?
2. **t=1,4** — sin leer nada, ¿se ve *que pasa algo*?
3. **t=3,0** — ¿queda algo por saber?

Si las tres son que sí, el resto de la pieza ya tiene a quién contárselo.
