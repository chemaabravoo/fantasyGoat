# La estructura · cómo se cuenta

Aquí sí hay plantillas, y a propósito. La narrativa es la parte del oficio que está
resuelta: se elige un armazón, se rellena y funciona. Lo que no se puede repetir es la
**forma visual** ([forma.md](../animacion/forma.md)), que es otra cosa.

## Cómo se elige el armazón

Por el **verbo** de lo que hay que contar, no por el formato:

| Si hay que… | Armazón |
|---|---|
| Desmontar una creencia | **La contradicción** |
| Enseñar que algo funciona | **El problema agitado** |
| Contar varias cosas de golpe | **La lista que se tacha** |
| Enseñar un cambio | **El corte único** |
| Contar algo que pasó | **El arco de historia** |
| Ganar comentarios | **El debate abierto** |

Y una regla que decide la longitud: **una sola cosa aguanta 12–16 s. Tres o más cosas se
van a 22–30 s. Pasados los 35 s siempre ha sobrado algo** — se quita lo más flojo, no se
acelera el resto.

---

## 1 · La contradicción · 14–20 s

El más fuerte para retención, porque el bucle se abre solo.

```
0,0 – 0,3   ya en movimiento. Lo esperado, montado y bien
0,3 – 1,2   el titular: «X está mal»
1,2 – 1,8   SE ROMPE. Corte seco, sin transición
1,8 – 4,0   por qué está mal. Un solo argumento, el más físico
4,0 – 9,0   qué es lo correcto. Aquí va la demostración
9,0 – 12,0  la prueba: el dato, el número, el resultado
12,0 – fin  remate + marca
```

**Dónde se rompe**: la ruptura del 1,2 tiene que ser *visual y brusca*. Si es un fundido,
se pierde. Ejemplos de ruptura: se tacha, se parte en dos, se cae de la mesa, se le pone
una cruz encima, cambia de color de golpe, se desordena.

## 2 · El problema agitado · 16–24 s

El clásico de producto. Funciona si el problema se **enseña**, no se cuenta.

```
0,0 – 3,0   el problema EN ACCIÓN, no descrito. Que se vea el dolor
3,0 – 6,0   se agrava. Repítelo, acumúlalo, que incomode
6,0 – 7,0   el silencio. Un beat vacío antes de la solución
7,0 – 14,0  la solución, paso a paso, rápido
14,0 – 18,0 el después. El mismo plano del principio, ya resuelto
18,0 – fin  remate + marca
```

**El silencio del 6,0 no se salta.** Es lo que hace que la solución se lea como alivio y
no como el siguiente punto de una lista. Es el único hueco de esta skill donde se permite
que no haya evento — y aun así la capa ambiente sigue viva.

## 3 · La lista que se tacha · 12–20 s

Para meter tres o cuatro ideas sin que parezca un tutorial.

```
0,0 – 1,5   los huecos VACÍOS ya visibles. Se ve que van a ser cuatro
1,5 – 3,0   entra el 1 · se resuelve · se tacha
3,0 – 4,5   entra el 2 · se resuelve · se tacha
4,5 – 6,0   entra el 3 · se resuelve · se tacha
6,0 – 8,5   el 4 NO se tacha. Ese es el que importa
8,5 – fin   remate + marca
```

El truco entero está en el último: se rompe el patrón que llevas tres repeticiones
enseñando. Y los huecos vacíos del principio son el bucle abierto — se sabe cuántos
faltan.

## 4 · El corte único · 10–14 s

El más corto y el que más se comparte. Una idea, sin argumentar.

```
0,0 – 4,5   el ANTES. Plano fijo, y dentro sólo se mueve una cosa
4,5 – 4,6   CORTE. Sin transición. Ni un fotograma de fundido
4,6 – 9,0   el DESPUÉS. Mismo encuadre exacto, misma escala
9,0 – fin   remate + marca
```

**Mismo encuadre exacto** es literal: si la cámara se mueve un píxel entre los dos, el
corte deja de leerse como comparación y se lee como escena nueva.

## 5 · El arco de historia · 22–32 s

Cuando hay algo que pasó de verdad.

```
0,0 – 3,0   el final, adelantado. Se enseña el resultado sin explicar
3,0 – 8,0   el contexto. Lo justo: quién y qué estaba en juego
8,0 – 18,0  qué pasó. Aquí va el latido más rápido de toda la pieza
18,0 – 24,0 la resolución, ya entendida
24,0 – fin  la lección + marca
```

## 6 · El debate abierto · 12–18 s

Diseñado para comentarios, no para guardados. Se elige a sabiendas.

```
0,0 – 2,0   la pregunta, ocupando el lienzo
2,0 – 8,0   los dos lados, con el mismo peso visual y el mismo tiempo
8,0 – 11,0  el dato que NO decide, sólo complica
11,0 – fin  «¿tú qué harías?» + marca
```

**No se resuelve.** Si la pieza toma partido, se acaba la conversación y con ella el
alcance. El único armazón de la lista donde el bucle se queda abierto al final.

---

## El bucle perfecto · operador, no armazón

Encima de cualquiera de los seis: que el último fotograma **encaje con el primero**, de
modo que al repetirse no se note el corte. Instagram y TikTok cuentan la repetición como
tiempo de visionado, así que una pieza de 12 s que engancha se ve como una de 30.

Se hace cuadrando el estado final de `seek(DURACION)` con `seek(0)`: misma posición, misma
escala, misma opacidad. Compruébalo:

```bash
node mirar.mjs pieza.html 0 <DURACION>
```

Las dos imágenes tienen que ser prácticamente la misma. Sólo funciona si la pieza no lleva
cierre de marca a pantalla completa — o si el cierre es un rótulo lateral en lugar de un
velo.

---

## El remate

Los últimos 2–3 segundos. Tres cosas, en este orden:

1. **La frase que se puede citar.** Una, corta, que resuma. Es lo que la gente escribe en
   el comentario
2. **La marca.** Ahora sí: al final, cuando ya ha valido la pena
3. **La acción**, si la hay. Una sola, con la palabra exacta que haya que usar

Lo que no va en el remate: dar las gracias, «síguenos para más», o resumir lo que se acaba
de ver.

## Cómo se escribe el guion

Para cada compás: **en qué segundo empieza, cuánto dura, qué pasa en pantalla, qué pone.**
Si al leerlo no sabrías decir en qué segundo pasa cada cosa, todavía no es un guion.

Los compases se declaran en relativo con `guion()` ([motor.md](../animacion/motor.md)), así que mover
uno recoloca los de detrás en vez de obligarte a reteclear la línea de tiempo entera.

## De dónde salen las palabras

De su web. Esta página pone el **orden y el tiempo**; con qué palabras se rellena está en
[tono.md](tono.md), y la muestra —sus titulares, su menú, sus cifras— ya está medida en
`taller/<marca>/marca/web.json`.

**No hay una voz de la casa.** Un armazón bien elegido con las palabras de otro hace que
todos los clientes suenen igual, que es el mismo fallo que tenía el fondo antes de que
cada marca trajese el suyo.
