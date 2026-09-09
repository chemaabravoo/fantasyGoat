# El movimiento

Aquí está lo que separa una animación que parece hecha por un programa de una que parece
hecha por alguien. Es `motion-design` (LottieFiles) filtrado: lo que sirve para vídeo
vertical, y lo que hay que tirar porque es de otra escala.

---

## Primero, lo que NO se coge de motion-design

Importa más que lo demás, porque esa skill viene con tablas muy convincentes y **están
pensadas para interfaz en la mano, no para vídeo**.

- **Su tabla de duraciones** (*card enter 200–350 ms*, *modal 300–400 ms*) es de un
  elemento de 300 px que responde a un dedo. Aquí un elemento ocupa media pantalla y
  recorre 1000 px. Por su propia regla —*distance scales duration*— las duraciones
  correctas son las de más abajo, casi el doble.
- **Su tabla de curvas** son las de Material `(0.2,0,0,1)` y Apple `(0.25,0.1,0.25,1)`.
  Arrancan flojas y hacen que la pieza parezca lenta aunque los tiempos sean los mismos.
  Las de este motor salen disparadas y frenan en seco, que es lo que hace que un rótulo se
  sienta rápido sin quitarle una décima.
- **Su regla de 1/3 de elementos en movimiento** es para no distraer a alguien que está
  intentando usar algo. Aquí distraer *es el objetivo*.

Lo que sí se coge son las tres ideas de abajo, y son las tres que más se notan.

---

## 1 · Las tres capas

Una animación plana es siempre lo mismo: **le falta una capa**.

| Capa | Qué es | Cuándo se mueve |
|---|---|---|
| **Principal** | La acción que sigue el ojo | En su compás |
| **Secundaria** | Lo que la acompaña: la sombra, el contenido de dentro, lo de al lado | 0,05–0,12 s **después** de la principal |
| **Ambiente** | El fondo vivo: un degradado que gira, algo que respira, grano | **Siempre. Nunca se para** |

**La capa ambiente es obligatoria en esta skill.** Es literalmente lo que pide el encargo
de que no haya un segundo estático: entre compás y compás, la capa principal está quieta y
lo único que impide que el fotograma esté congelado es el ambiente.

```js
// respira() nunca se apaga: vive fuera del guion
el.fondo.style.transform = 'translate('+respira(t,4,0.13)+'px,'+respira(t,3,0.11,1.7)+'px)';
el.halo.style.opacity    = 0.5 + respira(t,0.06,0.09);
```

Amplitudes: **2–5 px** de desplazamiento, **±0,06** de opacidad, **±0,015** de escala. Más
que eso ya no es ambiente, es un elemento más y compite con la acción.

**El desfase secundario** es la mitad del efecto «caro» y cuesta una línea:

```js
const kCard = easeOut(p(t, T.card[0], T.card[1]));
const kTxt  = easeOut(p(t, T.card[0]+0.09, T.card[1]+0.09));   // el contenido llega después
```

## 2 · Los arcos

**Nada cae en línea recta.** Es el principio de Disney que más se nota y el que casi
siempre falta: un objeto que baja recto parece un `div`; uno que describe una curva parece
que pesa.

Un arco es cruzar el eje secundario con **otra función**, no con el mismo progreso:

```js
const k = easeOut(p(t, T.cae[0], T.cae[1]));
el.x.style.transform =
  'translate('+ (mix(0,-74,k) + arco(k,46)) +'px,'+ mix(-380,0,k) +'px)';
```

`arco(k, alto)` es una campana: 0 al empezar, `alto` en el medio, 0 al llegar. La pieza
sale y llega donde tenía que llegar, pero por el camino se ha ido de paseo.

Alturas: **30–60 px** para un objeto que cruza la pantalla, **12–20 px** para algo
pequeño. Un objeto pesado arquea poco; uno ligero, mucho.

Mover dos ejes con el **mismo** `k` no es un arco: es una diagonal recta.

## 3 · La anticipación

Antes de salir disparado, se retrocede. Es lo que anuncia el movimiento y hace que se lea
como una decisión y no como un teletransporte.

```js
const k = easeAntes(p(t, T.sale[0], T.sale[1]));   // se mete por debajo de 0 al principio
```

`easeAntes` retrocede un poco antes de arrancar. Para lo que **sale disparado, salta o
golpea**. Su pareja es `easeBack`, que se pasa de largo y vuelve, y sirve para lo que
**aterriza y pesa**.

No uses ninguna de las dos en la cámara: una cámara que rebota marea. **Otra cosa es el
temblor** (`shake()`, [motion-ui.md](motion-ui.md)): tres décimas de vibración que se
apagan sola en un golpe —el sello, «más caro»—, una o dos veces por pieza. No es un
rebote de la cámara al moverse: es la cámara acusando un impacto.

---

## El latido

La regla operativa de «que no haya un segundo muerto».

> **Cada 1,2–2,0 s tiene que pasar un evento.**

Un evento es: un corte, algo que entra, algo que sale, un cambio de escala, un número que
salta, un color que cambia, la cámara que se mueve. Lo que no cuenta como evento: la capa
ambiente (esa es el suelo, no el latido) y algo que sigue moviéndose desde antes.

**El latido se acelera hacia el final.** No es constante:

| Tramo | Hueco entre eventos |
|---|---|
| Gancho (0–3 s) | 0,4 – 0,8 s |
| Desarrollo | 1,2 – 2,0 s |
| Clímax / prueba | 0,6 – 1,0 s |
| Remate | 1,5 – 2,5 s, y ahí sí se respira |

Una pieza con latido constante aburre aunque sea rápida. Lo que engancha es que **acelere**.

Para comprobarlo, escribe los compases de `MARCAS` en una columna y mira las diferencias.
Cualquier hueco por encima de 2,0 s fuera del remate es un sitio por donde se van.

## Las duraciones

Punto de partida, con las curvas de este motor:

| Qué | Cuánto |
|---|---|
| Un elemento entra (opacidad + desplazamiento) | 0,32 – 0,52 s |
| Una hoja que sube desde abajo, pantalla completa | 0,85 – 1,05 s |
| Un titular entra | 0,45 s · sale en 0,35 |
| Un movimiento de cámara | 0,65 – 1,00 s |
| Un contador que sube | 0,40 s |
| Un corte seco | **0 s.** No es una transición |
| El velo del cierre | 0,55 s, y la frase 0,35 s después |

**Nada tarda más de 1,1 s en entrar.** Si algo necesita más, es que está entrando mal, no
despacio.

Y antes de recortar décimas, **mira la curva**: una entrada de 0,42 s con `easeOut` se lee
más rápida que una de 0,30 s con una cúbica floja.

## Las cascadas

Varios elementos seguidos: **0,14 s de hueco, 0,34 s cada uno**. Cinco elementos caen en
poco más de un segundo y se leen como un golpe, no como una lista cargando.

Si dudas, ve más rápido. El error siempre ha sido por lento.

## La personalidad de la marca

Se elige **una** y se aplica a toda la pieza. Sale del manual de marca ([marca.md](../marca.md)).

| Personalidad | Curva por defecto | Duraciones | El muelle (`spring`) | Arcos |
|---|---|---|---|---|
| **Nerviosa** (consumo, humor, joven) | `easeOut` | ×0,85 | Largo: `spring(k,0.30,13)`, dos o tres rebotes | Altos |
| **Segura** (producto, servicio, SaaS) | `easeOut` | ×1,00 | El de casa: `spring(k,0.42,13)` | Medios |
| **Cara** (lujo, salud, financiero) | `easeInOut` | ×1,25 | Suave y lento: `spring(k,0.55,9)` | Largos y bajos |
| **Seca** (técnico, dato, institucional) | `easeOut` | ×0,90 | Corto: `spring(k,0.60,13)`, un solo sobrepaso | Casi rectos |

**Desde el 6 sep 2026 el muelle está en todas** ([motion-ui.md](motion-ui.md)): lo que
aterriza se pasa un poco y vuelve, también en las marcas «secas». Antes «seca» quería
decir *sin rebote*; ahora quiere decir *rebote corto*. Lo pidió él al ver la app de cuentas —una marca
seca— animada con muelle: «mucho más dinámico como se anima todo». Lo que sigue sin
rebotar es la cámara.

La personalidad es lo que hace que dos piezas con formas distintas se reconozcan como la
misma marca. Es tan de marca como el color, y no está en ningún manual: la eliges tú y la
anotas en `marca.css` para no cambiarla en la siguiente pieza.

## Lo que delata una animación mala

| Se ve | Es | Se arregla |
|---|---|---|
| Robótica | Sin curva, o todo con la misma | Curvas distintas por función |
| Barata, plana | Falta secundaria y ambiente | Desfase de 0,09 s + `respira()` |
| Lenta, aunque los números sean cortos | Curva floja | `easeOut`, no una cúbica |
| De programa | Todo en línea recta | `arco()` |
| Aburrida a mitad | Latido por encima de 2 s | Métete un evento |
| Se salta | Algo cambió de tamaño con `font-size` o `width` | Caja fija y `scale` ([trampas.md](../entrega/trampas.md)) |


<!-- El tiempo medido: fundido de las tres marcas al partir las skills · 25 ago 2026 -->

## Toques


El efecto empieza **0,06–0,08 s después** de la marca del toque, no a la vez.
Ese retardo minúsculo es lo que hace que parezca causa y efecto en vez de dos
cosas sueltas.

Entre un toque y el siguiente, ~0,95 s. Menos y no da tiempo a leer lo que ha
cambiado; más y se hace pesado.

## Planos


Un plano aguanta entre 2 y 4 segundos. Pasado eso hace falta que algo entre,
que algo cambie o que se mueva la cámara. Si un tramo dura más de 4 s sin que
pase nada, sobra.

## Duración total


La duración sale del guion, no del formato: se suma lo que cuesta cada cosa y
eso es lo que dura. Lo medido hasta ahora, como vara:

- Una pieza que cuenta **una sola cosa** se sostiene en 10 – 14 s
- En cuanto hay **tres o más** cosas que contar, se va a 20 – 26 s
- Pasados los 30 s siempre ha sobrado algo. Quita lo más flojo, no aceleres
  el resto

## Contadores


Si un número sube, que vaya **de un importe real al siguiente**, nunca
interpolando fracciones de sus sumandos. Ver [trampas.md](../entrega/trampas.md), es el
fallo que más se nota.

```js
let v = 0, desde = 0;
for (let n = 0; n < PASOS.length; n++) {
  const hasta = desde + PASOS[n];
  const k = easeOut(p(t, marcas[n] + 0.06, marcas[n] + 0.46));
  if (k > 0) v = mix(desde, hasta, k);
  desde = hasta;
}
```

## Los primeros cinco segundos


**Es donde se va la gente, y no pueden ser dos líneas de texto quietas.** El 25
de agosto de 2026 él lo dijo así: «del segundo 1 al 5, que es lo más importante
para que no se vaya la gente, no hay nada de animación».

Lo que sí aguanta ese tramo, tal y como quedó en `amedias`:

| s | qué entra |
|---|---|
| 0,10 | la primera mitad de la frase, bajando desde arriba |
| 0,40 | **la frase entre comillas, en una burbuja que rebota** y se queda balanceándose |
| 1,10 | la segunda mitad, subiendo |
| 1,40 | **la palabra clave aterriza sola**, en el color de acento, con `easeBack` |
| 1,60 → 2,60 | **un objeto que se llena, crece o cuenta** — en `amedias`, una caña con su espuma subiendo |

Son cuatro entradas y un movimiento continuo en dos segundos y medio. La regla
detrás: **nunca más de ~0,6 s sin que algo entre o cambie**, y que al menos una
de esas cosas dure más de un segundo (el objeto que se llena) para que no sea
sólo texto apareciendo.

## La cámara no se para nunca


Una pieza donde la cámara está fija se ve plana aunque dentro pasen cosas.
Tres capas que se suman:

1. **Respiración de fondo**, siempre encendida: `1 + 0.014*Math.sin(t*0.62)`.
   No se ve; se nota.
2. **Un viaje motivado** por cada cosa que se nombra: acercarse a la mesa
   cuando la voz dice «con tus colegas», a tu columna cuando te nombra,
   abrirse cuando entra algo que no cabe. Se encadenan con `mix` sobre
   `camara()`, y cada tramo se abre y se cierra con `easeInOut` + `fuera`.
3. **Un golpe de escala** (+0,07) en el momento del giro o del reparto.

## Que el dinero se mueva de verdad


Un número que cambia solo no es una animación, es una actualización. Si el caso
dice que uno se ahorra y tres pagan, **eso tiene que verse cruzando la
pantalla**: en `amedias` salen tres trozos en arco de la columna alta a las tres
bajas mientras todas se igualan. La cifra confirma lo que ya has visto.

**Y el corolario, que él dijo en una frase:** si un rótulo no se mueve y no
cambia nada, sobra. La situación se cuenta hablando; los datos entran como
objetos —un ticket que cae, una caña que se llena, un trozo que vuela—, no como
texto quieto en una esquina.
