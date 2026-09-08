---
name: marca-desde-web
description: >
  Monta la marca de un cliente para el taller de reels, desde su web —mide
  colores por área y por papel, tipografías, logotipo, contacto— o desde su
  manual (PDF, capturas, colores sueltos). Deja taller/<marca>/marca.css con
  los contrastes medidos, los activos en taller/<marca>/marca/ y la skill de
  la marca en .claude/skills/<marca>/SKILL.md, con su voz de ElevenLabs.
  Úsala en el paso 2 de CLAUDE.md, cuando el usuario dé una URL o un manual,
  o cuando quiera añadir otra marca al taller.
---

# La marca, desde su web o su manual

Se hace **una vez por marca**. Si esto sale mal, se nota en todas las piezas.
Las reglas de qué es cada token y cómo se decide están en
`../reel-motor/marca.md`: esto es el procedimiento.

## 1 · Recoger

### Si hay web

```bash
node motor/marca-desde-web.mjs https://su-web.com taller/<slug>
```

Imprime un resumen y deja en `taller/<slug>/marca/`: `web.json` (todo lo
medido), `captura.png`, `captura-entera.png`, `captura-movil.png` y el
`logo.*` si lo encontró.

**Mira las capturas** con Read, las tres. El estilo no está en los números:
¿minimalista o cargada? ¿cálida o técnica? ¿fotos o ilustración? ¿qué vende,
a quién, con qué tono? Eso va a la skill de la marca y decide la personalidad
de movimiento.

Si la web no carga (bloquea navegadores sin cabeza, o pide login), dilo y pasa
al manual, o pide capturas.

### Si hay manual

Léelo entero (PDF con Read; capturas con Read). Saca los mismos tokens que
saca el script: fondo, tinta, acento, tipografías, logotipo, nombre, web.

### Si sólo hay Instagram

Instagram bloquea a los navegadores sin cabeza, así que el script no entra.
Pídele **dos o tres capturas**: el perfil entero y un par de posts o de
stories. Léelas con Read y saca de ahí lo mismo: los dos colores que repite,
si el logo va sobre claro o sobre oscuro, qué tipografía usa en los textos de
las piezas, y sobre todo **el tono**. Un feed dice más del tono que una web.

### Si no hay ni web ni manual

Cuatro respuestas cortas, una pregunta cada vez: **nombre**, **qué vende y a
quién**, **dos colores** —y si dice «no sé, elige tú», propónle tres parejas
con su carácter, no una lista de hex— y **cómo quiere sonar** (cercano, serio,
gamberro, caro). **No inventes una marca**: una paleta inventada hay que
rehacerla entera.

## 2 · Decidir los tokens

- **El fondo tampoco se decide a ojo: se mide.** El script saca el fondo
  dominante de su web por área y escribe **las dos pieles enteras** —clara y
  oscura— con su fondo, su tinta derivada y su cielo. Lo que NO cambia es el
  material (cristal, filete, bisel, desenfoque): eso es lo que hace que sus
  piezas se vean de la misma casa aunque cada marca traiga su color.
  Hasta el 8 sep 2026 el fondo era una perla fija y todas las marcas salían
  iguales; ya no. **Tú no eliges la piel: se le enseñan las dos en la prueba**
  (paso 4 de `CLAUDE.md`) y elige él.
- **El cielo** (`--cielo-*`, `--mancha-*`) sale de su acento: cuatro manchas de
  la misma familia, con el tono girado poco. No lo toques a mano salvo que la
  marca sea de un solo color muy sobrio: entonces baja `--manchas` a 0,6.
- **`--acento`**: el color vivo que la web usa en botones. **Casi nunca vale
  como texto**, y el script lo dice: el acento subraya, rellena, enmarca; el
  texto va en `--tinta`.
- **`--titular` y `--dato`**: el script las escribe solo y **mete la fuente
  dentro del CSS**, en un `@import` de Google Fonts que comprueba con un fetch
  antes de ponerlo. Para `--dato`, una mono: JetBrains Mono o IBM Plex Mono.

- **Si sustituyes una tipografía a mano, toca DOS líneas.** Cuando el resumen
  dice «sin @import de tipografías» —la web usa fuentes de sistema, o la suya no
  está en Google (SF Pro, WhatsApp Sans, cualquier fuente propia)— eliges una
  parecida y la pones en **las dos**:

  ```css
  @import url("https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700;800&display=swap");
  :root{ --titular:"Figtree",-apple-system,sans-serif; }
  ```

  **Cambiar sólo `--titular` es el fallo silencioso más caro que hay**: el token
  nombra una fuente que nadie ha cargado, Chrome sustituye sin decir nada y el
  vídeo sale entero, bien maquetado, con la letra equivocada. No se ve hasta que
  lo miras al 100 %. Pasó el 8 sep 2026 con `reel-whatsapp`: `WhatsApp Sans Var`
  no está en Google, se puso Figtree en el token y el `@import` se quedó sin
  poner. Y hay que hacerlo **en las dos pieles**, clara y oscura.

  Comprobar que la fuente existe antes de ponerla, no fiarse:

  ```bash
  curl -s -o /dev/null -w "%{http_code}\n" \
    "https://fonts.googleapis.com/css2?family=Figtree:wght@400;700&display=swap"
  ```

  200 es que sí; 400 es que ese nombre no está en Google Fonts.
- **`--personalidad`** (`movimiento.md`): nerviosa (consumo, humor, joven),
  segura (producto, servicio), cara (lujo, salud, financiero), seca (técnico,
  dato). Por lo que vende y cómo lo dice, no por el color.
- **Los colores del manual en papel** salen apagados en pantalla: súbeles la
  saturación un 10-15 %.

## 3 · Escribir

- `taller/<slug>/marca-clara.css` y `marca-oscura.css`: **con web los escribe
  el script**, enteros y medidos. Sin web, copia `motor/marca-PLANTILLA.css` y
  `motor/marca-PLANTILLA-oscura.css` y rellena las dos. **Nunca desde la
  marca.css de otra marca del taller.**
- `taller/<slug>/marca.css`: una línea, `@import url("marca-<piel>.css")`.
  Es lo que se cambia cuando elija en la prueba; no dupliques los tokens aquí.
- **Comprueba las dos antes de enseñarlas**: `node motor/validar.mjs` sobre
  cada prueba. Se niega si la tinta no llega a 7:1 sobre su fondo.
- `.claude/skills/reel-<slug>/SKILL.md`: desde `plantilla-skill-marca.md`, que está
  al lado de este archivo. Rellena todo lo que sepas; lo que no, **«por
  confirmar»**, no inventado. La descripción del frontmatter tiene que
  disparar cuando se nombre la marca.
- **La voz.** Por defecto la que trae `motor/toma.py`, castellana. Si la marca
  pide otra —otro género, otro acento, otro registro—, **no la elijas tú**:
  dile que entre en ElevenLabs → Voices → Library, escuche y te pase el
  **Voice ID**. Anótalo en la skill de la marca. Si todavía no tiene cuenta,
  deja la de por defecto y sigue: se cambia cuando quiera.
- Si hay logotipo, déjalo en `taller/<slug>/marca/logo.*` tal cual: **un
  logotipo ajeno no se recolorea**.

## 4 · Enseñar y confirmar

En un mensaje corto: la paleta con los contrastes en números, las
tipografías, la personalidad, la frase del cierre y la voz. Pide el visto
bueno. Si dice que un color no es el suyo, corrígelo: él conoce su marca
mejor que el script.

**La piel no se pregunta aquí, se enseña.** Preguntar «¿la quieres clara u
oscura?» sin nada delante no lo sabe contestar nadie. Va en la prueba (paso 4
de `CLAUDE.md`), con los dos vídeos hechos y una recomendación: la que tiene
su web.

## Lo que no se hace

- Recolorear un logotipo ajeno.
- Copiar `marca.css` de otra marca «para tener algo».
- Elegir tú la piel, o enseñar sólo una. Se hacen las dos y elige él.
- Tocar el material (cristal, bisel, filete, sombras) para «adaptarlo» a la
  marca. La marca entra por el fondo, el cielo, el acento y las letras.
- Sacar la paleta a ojo de la captura cuando el script ha medido.
- Inventar cifras, precios o testimonios para rellenar la skill.
