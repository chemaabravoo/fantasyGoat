# La piel: cristal

Todas las piezas del taller comparten **un solo material**, y por eso se ven de la misma
casa aunque cada marca lleve sus colores. Está en `motor/cristal.css`; la marca no lo
cambia, lo **rellena**.

## Las tres capas del material

| Capa | Qué es | Token |
|---|---|---|
| **El fondo** | **El de su web**, medido. Claro o carbón según lo que traiga; lo escribe `marca-desde-web` | `--fondo` |
| **El cielo** | Cuatro manchas de color desenfocadas que no paran (`cieloSeek(t)` en `comun.js`) y una banda de luz que barre. **Salen de su acento**, no son fijas. Es lo único que el cristal tiene que refractar: sin cielo, un `backdrop-filter` es un gris plano | `--cielo-*`, `--mancha-*`, `CIELO_HTML` |
| **El cristal** | Un velo translúcido con filete de un píxel, bisel por dentro y desenfoque de lo de detrás. En la piel clara es blanco al 55-85 %; en la oscura, luz al 6-13 % con el bisel invertido | `--cristal*`, `--filete`, `--bisel`, `--desenfoque` |

Una tarjeta se escribe así, siempre igual:

```css
.tarjeta{background:var(--cristal-alto);border:1px solid var(--filete);
  box-shadow:var(--bisel),var(--flota-alta);
  -webkit-backdrop-filter:var(--desenfoque);backdrop-filter:var(--desenfoque)}
```

Lo interactivo va en píldora (`border-radius:var(--r2)`); las sombras son las tres del
material (`--flota`, `--flota-alta`, `--flota-dock`), ninguna inventada.

## Las ranuras de la marca

Lo que cambia entre marcas. Lo escribe `marca-desde-web` en **dos archivos completos**,
`taller/<marca>/marca-clara.css` y `marca-oscura.css`; `marca.css` es una línea que
importa la elegida. La prueba del paso 4 se enseña en las dos y la persona decide:

| Ranura | Qué pone la marca | Regla |
|---|---|---|
| `--fondo` | Su lienzo | El fondo dominante de su web, medido por área. La otra piel es la misma marca en el otro extremo |
| `--acento` | Su color vivo | Rellena botones, barras, anillos, la píldora activa. **Casi nunca es texto**: `validar.mjs` avisa con el número exacto |
| `--cielo-*` · `--mancha-*` | Su fondo vivo | Cuatro manchas de la familia de su acento (el tono gira poco: +34, −38, +96). `--manchas` de 0,55 a 1,05 |
| `--titular` | Su tipografía de titulares | La de su web. **Viaja dentro de `marca.css`**, en un `@import` de Google Fonts ya comprobado: no hay que tocar el `<link>` de la pieza |
| `--dato` | Una monoespaciada | Para cifras, etiquetas y la línea de comando. JetBrains Mono si no tiene |

La tinta (`--tinta`, `--tinta-baja`) tampoco se inventa: se deriva del fondo y **se mide**.
Por debajo de 7:1 y 4,5:1, `validar.mjs` se niega a dejar pasar la pieza.

## Los objetos que ya existen en este estilo

Los seis `ejemplos/` traen dibujados —y animados— un reproductor de música, un mapa con
ruta, un botón que demuestra desenfoque, muelle y cámara, una landing partida en antes y
después, un checkout con tarjeta, y una carpeta que se abre. Se **copia la técnica, no el
plano** ([forma.md](forma.md)): el objeto de cada pieza es el de la marca.

## Lo que este estilo no hace

- Fotos. Anima interfaces, texto, cifras y objetos dibujados.
- Colores a fuego en la pieza. Todo sale de tokens: un `#fff` escrito a mano es invisible
  en la piel clara y un borrón en la oscura (le pasó a la píldora de `prueba.html`).
- Rebotes grandes: la personalidad es «cara» (`movimiento.md`), muelle corto.
