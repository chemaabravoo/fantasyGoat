# Emojis, iconos y logotipos

Lo que separa una pieza que parece hecha por alguien de una que parece hecha por un
programa suele ser esto: **símbolos de verdad en vez de círculos de colores**. Un emoji
del sistema, un icono con peso y un logo vectorial cuestan una línea cada uno y se notan
en el primer vistazo.

Tres cosas distintas y no se mezclan:

| | Qué es | De dónde sale |
|---|---|---|
| **Emoji** | El dibujo a color, con volumen | La fuente del sistema. En macOS, **los de Apple** |
| **Icono** | El símbolo plano de una acción o un objeto | Material Symbols, por Google Fonts |
| **Logotipo** | La marca de una empresa | Su web (el del cliente) o `motor/logo.mjs` (los de terceros) |

---

## 1 · Emoji · sale el de Apple y no hay que hacer nada

Un emoji escrito en el HTML lo dibuja la fuente del sistema. **En un Mac eso es Apple
Color Emoji**, que es el que la gente reconoce y el que da el aire de captura de iPhone.
Comprobado el 8 sep 2026 renderizando con el propio Chrome de la captura: la batería, el
rayo, el iPhone, las máscaras de teatro y el check verde salen los de Apple, con su
volumen y su sombra.

```html
<span class="emj">🔋</span>
```
```css
.emj{font-size:96px;line-height:1;
  /* que no lo pise la tipografía de la marca */
  font-family:"Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif}
```

**Las cuatro reglas:**

1. **Uno, grande, y por algo.** Un emoji de 96-140 px como objeto de la escena. Tres
   emojis pequeños en fila son una lista de la compra, no una pieza.
2. **No sustituye a un icono en una interfaz.** Dentro de una tarjeta que imita una app,
   va un icono plano. El emoji es el objeto del que habla la voz.
3. **Se anima como cualquier objeto**: entra con muelle, respira, gira un poco. Un emoji
   quieto es una pegatina.
4. **`filter` no lo tiñe**: es un dibujo a color y así se queda. Si lo quieres del color
   de la marca, no es un emoji, es un icono.

**En Windows y Linux salen otros** (Segoe UI Emoji, Noto). Cambia el dibujo, no la
maqueta. Si la pieza depende de que se vea el de Apple, se renderiza en un Mac.

**Y son de Apple.** Aparecen en el vídeo igual que aparecen en cualquier captura de un
móvil; lo que no se hace es sacarlos de la pantalla y venderlos como arte propio.

---

## 2 · Iconos · Material Symbols, y se tiñen con el acento

Para lo plano —lo que va dentro de una app dibujada, lo que acompaña a un texto— hacen
falta iconos de verdad, con la misma familia y el mismo peso. Se cargan como una fuente
más, con el `<link>` que ya lleva la pieza:

```html
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,500,1,0&display=swap" rel="stylesheet">
<span class="ic">bolt</span>
```
```css
.ic{font-family:"Material Symbols Rounded";font-size:64px;line-height:1;
  color:var(--acento);                         /* se tiñe: es texto */
  font-variation-settings:'FILL' 1,'wght' 500} /* relleno y grosor, a juego con la marca */
```

- **Se tiñe con `color`** y escala con `font-size`, como cualquier letra. Eso es lo que un
  emoji no puede hacer.
- Tres cortes: `Material Symbols Rounded` (redondeado, lo que mejor casa con el cristal),
  `Outlined` (línea) y `Sharp` (recto). **Uno por pieza**, no se mezclan.
- El eje `FILL` de 0 a 1 sirve para animar: un icono que se rellena al activarse
  (`font-variation-settings` interpolado desde `seek(t)`).
- Nombres en <https://fonts.google.com/icons>. Licencia **Apache 2.0**: se usan sin pedir
  permiso y sin atribuir.

**Los de Apple (SF Symbols) NO se pueden usar.** Su licencia los limita a apps de las
plataformas de Apple: no valen para un vídeo, ni se pueden redistribuir. Si lo que buscas
es ese aire, es `Rounded` con `wght` 500-600, que es lo más parecido que hay libre.

---

## 3 · Logotipos · vectoriales, nunca una captura

```bash
node ../../motor/logo.mjs spotify instagram tiktok
```

Deja los SVG en `marca/logos/`. Salen de **simple-icons** (paquete CC0, unos 3.300 logos):
un solo trazo, sin fondo, así que se tiñen con `fill` y escalan sin pixelarse — que es lo
que hace falta en un lienzo de 1080×1920 capturado al doble.

```html
<svg viewBox="0 0 24 24" class="lg"><path d="…"/></svg>
```
```css
.lg{width:96px;height:96px;fill:var(--tinta)}
```

**El logo del cliente no sale de ahí**: lo baja `marca-desde-web.mjs` de su propia web y
queda en `marca/logo.*`. `logo.mjs` es para los de terceros que aparecen en la pieza
—«funciona en Instagram y TikTok», «pagas con Bizum»—.

**Un PNG de Google Imágenes no vale.** Se ve el borde a 1080×1920, casi siempre lleva
fondo blanco pegado, y la mitad de las veces es una versión antigua del logo. Si
simple-icons no lo tiene, se pide el vectorial a la marca o se resuelve con texto.

### Lo que se puede y lo que no

- **Se puede nombrar a una empresa con su logo.** «Funciona en Instagram» con el logo de
  Instagram al lado es uso nominativo y es legítimo.
- **No se puede dar a entender que te patrocinan.** Su logo junto al tuyo, del mismo
  tamaño, en un cierre de marca, dice «colaboramos». Si no es verdad, fuera.
- **No se recolorea un logo ajeno** salvo a un solo color plano cuando el fondo lo obliga
  —y aun así, nunca al color de TU marca, que es exactamente lo que sugiere patrocinio—.
- **No se deforma, no se gira, no se le añaden efectos.**
- El paquete es CC0, pero **los logos siguen siendo marcas registradas de sus dueños**.
  Lo que es libre es el archivo, no el derecho a usar la marca como te apetezca.

---

## Cuál de los tres, en una línea

- ¿Es **el objeto del que habla la voz**? Emoji, grande.
- ¿Está **dentro de una interfaz** dibujada, o acompaña a un texto? Icono, teñido.
- ¿Es **una empresa concreta**? Logotipo vectorial, sin tocar.
