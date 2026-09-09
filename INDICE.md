# Las camas musicales

Veinticinco bucles sintetizados en local con numpy, **en cinco familias de
cinco**: sin derechos, sin plan de pago, sin buscar nada fuera. Cada uno es un
**bucle perfecto** y en `largos/` está ya repetido hasta ~95 s. Se generan una
vez con `bash musica/generar.sh` (lo hace `requisitos.sh`).

Los nombres son genéricos, `<familia>-<instrumento>`: se elige por lo que
hace falta en ese tramo, no por a qué se parece.

## La regla: la música va por tramos

**Una sola cama de fondo para todo el vídeo es lo que se evita.** La música
acompaña lo que pasa: tensión mientras se abre el bucle, emoción en el giro,
energía en el remate. Se declara en el HTML, con los mismos compases que
mueven la imagen:

```js
const MUSICA=[
  ['tension-reloj',    0],                          // el gancho: se abre la pregunta
  ['emocion-cuerdas',  T.giro[0],   0.15, 'corte'], // el giro: subida + golpe, cambio en seco
  ['energia-himno',    T.prueba[0], 0.18, 'sube'],  // la prueba: subida y entra con pulso
];
window.MARCAS=Object.assign({},T,{SFX,MUSICA,fin:window.DURACION});
```

`[cama, desde, nivel?, transicion?, desdeCama?]`: la cama arranca en `desde`
y dura hasta la siguiente. `nivel` 0,15 por defecto (energía, 0,18).
`transicion` es cómo entra: **fundido** (cruce de 1,2 s, por defecto), **sube**
(una subida de 1,6 s que acaba justo en `desde`) o **corte** (subida + golpe,
la anterior se corta en seco: el giro). `desdeCama` es por qué segundo de la
cama empezar.

Reglas que funcionan:

- **Dos o tres tramos**, no seis. Un cambio cada 8-15 s se nota; cada 3 s
  marea.
- **El cambio cae en un compás de la pieza** (`T.giro[0]`), nunca en un
  segundo suelto: así suena a que la imagen lo provoca.
- **Sube de energía hacia el final**, o baja a propósito para la cuña emotiva.
  Lo que no vale es ir a saltos.
- **Con voz densa, baja un peldaño** de energía en ese tramo.
- El corte en seco (`corte`) se usa **una vez** por pieza, en el giro.
- Apunta en la skill de la marca qué camas llevó cada pieza, para no repetir.

## Qué familia para qué tramo

| Tramo de la pieza (estructura.md) | Familia |
|---|---|
| El gancho, el bucle que se abre, la cuenta atrás, «esto es lo que pasaría si…» | **tensión** |
| El desarrollo, «cómo funciona», la lista, la explicación | **neutra** |
| La escala, el experimento, la metáfora, la multitud | **épica** |
| El giro, la cuña emotiva, «por eso lo hicimos», el final que acaba bien | **emoción** |
| El remate con fuerza, el reto que abre a lo grande, la dopamina visual | **energía** |

Partituras que salen solas, por armazón:

| Armazón | Tramos |
|---|---|
| La contradicción | tensión (0) → neutra (por qué está mal) → **corte** a épica o energía (la prueba) |
| El problema agitado | tensión (el problema) → silencio o tensión-drone (el beat vacío) → emoción o energía (la solución) |
| La lista que se tacha | neutra (0) → **corte** a energía en el cuarto, el que no se tacha |
| El corte único | tensión-drone (antes) → **corte** a emoción o energía (después) |
| El arco de historia | épica (el final adelantado) → neutra (el contexto) → tensión (qué pasó) → emoción (la lección) |
| El debate abierto | neutra todo el tramo; **sube** a tensión en el dato que complica |
| La metáfora / el experimento | épica u órgano (0) → tensión (el resultado) → emoción o energía en la cuña |

## Tensión

| Cama | Suena a | Tono · tempo | Energía | Pega con | No pega con |
|---|---|---|---|---|---|
| `tension-reloj` | tic de semicorcheas, pizzicatos, chelos en staccato | Re m · 72 | 4 | retos con reloj, cuenta atrás, ráfagas | cuñas emotivas |
| `tension-marcha` | bajo distorsionado, bombo, cuerdas a golpes | Fa m · 120 | 5 | retos, cortes duros, lo que aprieta | texto largo en pantalla |
| `tension-drone` | drone, metales lentos, campana suelta, **sin pulso** | Fa♯ m · 50 | 1 | el silencio, lo oscuro, mucha voz encima, el beat vacío | nada que necesite ritmo |
| `tension-latido` | un corazón que se acelera, tic, trémolo que sube | La m · 92 | 3 | la espera, «¿y ahora qué?», el gancho que abre una pregunta | humor |
| `tension-tremolo` | violines temblando, chelos a golpes, redobles | Sol m · 110 | 4 | anunciar algo, la subida antes del giro | cuñas emotivas |

## Emoción

| Cama | Suena a | Tono · tempo | Energía | Pega con | No pega con |
|---|---|---|---|---|---|
| `emocion-piano` | piano de fieltro, cuerdas lentas, reloj a negras | La m · 60 | 2 | la cuña emotiva, la amistad, «por eso lo hicimos» | retos, cortes duros |
| `emocion-cuerdas` | acordes que se abren, un chelo que canta, sin pulso | Do M · 64 | 2 | el giro, la resolución, lo que se entiende al final | ráfagas |
| `emocion-guitarra` | arpegio punteado en mayor, campana de vez en cuando | Sol M · 80 | 2 | lo cercano, lo cotidiano que acaba bien, gente | épica |
| `emocion-organo` | órgano en corcheas, cuerdas que se suman, coro al final. Sin batería | Re M (lidio) · 92 | 3 | emocionar sin ponerse triste; el cierre de marca | retos y cortes |
| `emocion-amanecer` | la misma melodía dos veces: primero oscura, luego en mayor con coro. **Gira a los 25 s** | Si m → Re M · 76 | 2 | la cuña emotiva, el giro que acaba bien (`desdeCama` 25 si el vídeo es corto) | nada con prisa |

## Épica

| Cama | Suena a | Tono · tempo | Energía | Pega con | No pega con |
|---|---|---|---|---|---|
| `epica-organo` | órgano en pulso, tic, cuerdas, sub, piano en la 2ª mitad | Si m · 63 | 3 | metáforas y experimentos serios, «¿sabías que…?». **El comodín** | humor ligero |
| `epica-organo-suave` | la misma, más baja | Si m · 63 | 2 | lo mismo con la voz densa | — |
| `epica-cuerdas` | ostinato de violines, chelos, timbales, línea aguda | Sol m · 66 | 4 | escala, multitudes, «esto es lo que pasaría si…» | humor |
| `epica-coro` | voces, taikos, campana, drone | Do m · 56 | 3 | lo solemne y lo ritual, el silencio antes de algo | cómo funciona |
| `epica-tambores` | taikos a negras, golpes graves, ostinato que crece | Re m · 100 | 4 | la prueba, el resultado grande, el experimento que sale | cuñas emotivas |

## Energía

Bombo a cuatro, sidechain, supersaws y una caída de verdad: 4 compases de
aire, 4 de subida y 8 de caída. Van a **0,18-0,20**.

| Cama | Suena a | Tono · tempo | Energía | Pega con | No pega con |
|---|---|---|---|---|---|
| `energia-orquesta` | orquesta y techno: ostinato, metales, bombo | Fa♯ m · 130 | 5 | la pieza que quiere sonar a tráiler; lo que abre fuerte | narración densa |
| `energia-eco` | pluck con eco a tresillo, lead ancho, mucho hueco | Si m · 128 | 4 | melancolía con pulso, stories | explicaciones con cifras |
| `energia-piano` | piano sincopado, palmas, pluck cantando | Re M · 126 | 4 | finales felices con energía | ganchos oscuros |
| `energia-palmas` | bombo, palmas, plucks brillantes, melodía en mayor | Do M · 124 | 4 | el remate que sale bien, la lista que acaba, humor con fuerza | tensión |
| `energia-himno` | el pulso de club debajo de un himno que sube | Mi M · 122 | 4 | esperanza con energía: el puente entre lo emotivo y lo de club | narración muy densa |

## Neutra

| Cama | Suena a | Tono · tempo | Energía | Pega con | No pega con |
|---|---|---|---|---|---|
| `neutra-marimba` | marimba en ostinato, pad cálido | La M · 84 | 3 | explicaciones sin drama, listas, cómo funciona | tensión |
| `neutra-sintes` | bajo de sinte, arpegio con delay, pad ancho | Mi m · 100 | 4 | cómo funciona, pantallas de una app, tecnología | experimentos de época |
| `neutra-cristal` | rhodes, campanas de cristal, cuerdas suaves | Mi♭ M · 76 | 2 | el alivio, lo amable, finales tranquilos | ganchos de tensión |
| `neutra-pulso` | tic suave, bajo redondo, arpegio discreto | La M · 96 | 3 | explicar con pulso, pasos, la parte que cuenta cosas | drama |
| `neutra-teclas` | piano eléctrico a negras, bajo suave, shaker | Fa M · 88 | 2 | lo cotidiano, hablar tranquilo, humor amable | épica |

**Cortes a compás:** si la pieza corta por B, que B sea múltiplo de 60/BPM
de la cama de ese tramo (reloj 0,83 s · marcha 0,5 · piano 1,0 · cuerdas 0,91
· coro 1,07 · marimba 0,71 · sintes 0,6 · latido 0,65 · tambores 0,6).
