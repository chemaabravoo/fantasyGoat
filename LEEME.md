# Reel Motor

Una carpeta que abres con Claude Code y hace vídeos verticales animados con tu marca:
guion, animación en el estilo motion UI sobre cristal, voz, efectos y música, en mp4
1080 × 1920 listo para Reels, TikTok o Shorts.

## ¿Ya tenías Reel Motor?

No empieces de cero: se actualiza tu carpeta y no pierdes ni una marca ni un vídeo.
Abre ésta con Claude Code y dile «ya tenía Reel Motor, está en <la ruta>». Los detalles,
en [ACTUALIZAR.md](ACTUALIZAR.md).

## Cómo se empieza

1. Descomprime esta carpeta donde quieras.
2. Abre una terminal dentro y escribe `claude` (o arrastra la carpeta a la app de Claude Code).
3. Di **«hola»**.

A partir de ahí te guía él. La primera vez son cuatro pasos y unos diez minutos, y casi
todo es esperar:

- **Te cuenta qué se va a instalar** en tu ordenador y te pide permiso antes de tocar nada.
- **Comprueba tu equipo** y, si falta algo, te da el comando exacto para instalarlo.
- **Te pregunta si quieres voz** en los vídeos, y si dices que sí te guía para conectar tu
  cuenta de ElevenLabs (`LEEME-elevenlabs.md`).
- **Te pide tu marca**: tu web, tu manual, unas capturas de tu Instagram, o los colores a
  mano si no tienes nada de eso. Con eso monta tu paleta y tus tipografías.
- **Te enseña una prueba** con tu marca moviéndose, para que veas que todo funciona.

Y ya está montado. Desde ese momento, cada vídeo es una frase:

> reel motor: un reel contando que abrimos los domingos

Te hace primero un **vistazo** de veinte segundos. Si te gusta, dices «renderízalo» y te
lo devuelve entero en máxima calidad. Si no, le dices qué cambiar.

## Lo que hace falta en tu equipo

Claude te lo comprueba y te dice qué falta: **Claude Code** con tu cuenta, **Google
Chrome**, **Node.js 18** o más, **ffmpeg** y **Python 3 con numpy**. Para la voz, una
cuenta de **ElevenLabs**.

## Qué se instala, y qué no

Al preparar la carpeta, dentro de ella y en ningún otro sitio:

| Qué | Dónde | De dónde sale |
|---|---|---|
| 25 paquetes de Node (`puppeteer-core` y sus dependencias, ~35 MB) | `node_modules/` | `registry.npmjs.org` |
| 25 camas musicales | `musica/largos/` | **se sintetizan en tu equipo** (4-8 min, una vez) |

Los **74 efectos de sonido** no hay que crearlos: vienen dentro, en `motor/sonidos/`.

**No se descarga ningún repositorio de GitHub**, no se toca tu sistema fuera de esta
carpeta y no se sube nada tuyo a ningún servidor mío: aquí no hay servidor mío. Trabajando,
el taller sale a internet sólo para las tipografías (`fonts.googleapis.com`), para medir
tu web una vez, y para ElevenLabs si has pedido voz.

## Qué hay dentro

```
CLAUDE.md                  ← lo que Claude lee al abrir la carpeta: el taller entero
motor/                     ← el motor y las herramientas
  base.html                ← el esqueleto de una pieza
  comun.js · comun.css     ← las curvas, los ayudantes, el cielo
  cristal.css              ← la piel (clara); marca-PLANTILLA.css y -oscura.css se rellenan
  marca-desde-web.mjs      ← mide su web y escribe su marca en las dos pieles
  toma.py · marcas.py      ← la voz en una toma y sus tiempos por palabra
  shoot-par.mjs            ← la captura a mp4 · mirar.mjs, contactos.mjs, validar.mjs
  sonar-generico.py        ← voz + efectos + música por tramos
  sonidos/                 ← 74 efectos de sonido, grabados · INDICE.md dice para qué es cada uno
.claude/skills/            ← el oficio (reel-motor) y cómo montar una marca (marca-desde-web)
piezas/                    ← 31 piezas de interfaz en PNG para montar escenas
musica/                    ← 11 camas grabadas (pixabay/) + 25 sintetizadas (largos/)
ejemplos/                  ← seis piezas completas del estilo, con su guion
taller/                    ← aquí van tus marcas (se crea sola)
```

## Lo que no hace

No graba ni genera personas. Anima interfaces, texto, cifras y objetos dibujados. Y no es
una aplicación con botones: se maneja escribiendo, dentro de Claude Code.

## Lo que puedes y no puedes hacer con esto

Es tuyo para usarlo en tus marcas y en las de tus clientes, sin límite de vídeos y sin
tener que citarme. Lo que no se puede es repartir, revender o publicar la carpeta —ni
entera ni a trozos—. Está todo en `LICENCIA.md`, en media página.

## Si algo no arranca

Escribe a hola@reelmotor.io con el error tal cual, copiado y pegado. Sistema probado:
macOS. Linux debería ir igual; Windows con WSL o Git Bash, menos probado.

**reelmotor.io**
