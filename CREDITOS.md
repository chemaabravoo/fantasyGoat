# Créditos

## El taller

Motor, herramientas, referencias, piel de cristal, recetas musicales y ejemplos:
**Alejandro Lozano · reelmotor.io**. Hecho reel a reel; las «trampas» de la skill son
fallos reales, cada uno pagado con un render.

## Lo que usa, de otros

| Qué | De quién | Licencia | Cómo se usa |
|---|---|---|---|
| Chrome | Google | propietaria | ya instalado en tu equipo; no se distribuye |
| puppeteer-core | Google (Puppeteer) | Apache-2.0 | `npm install`, en `node_modules/` |
| ffmpeg | FFmpeg team | LGPL / GPL | ya instalado en tu equipo; se invoca, no se incluye |
| numpy | NumPy developers | BSD-3 | `pip install`, en tu Python |
| Node.js | OpenJS Foundation | MIT | ya instalado en tu equipo |
| Google Fonts (Inter, JetBrains Mono, Space Grotesk, Instrument Serif y las de cada marca) | sus autores | SIL OFL 1.1 | se cargan al renderizar |
| ElevenLabs (voz, transcripción, efectos opcionales) | ElevenLabs | servicio, con tu cuenta | `toma.py`, `efectos-eleven.py`; ver `LEEME-elevenlabs.md` |
| Claude Code | Anthropic | servicio, con tu cuenta | el taller corre dentro |
| Los 74 efectos de sonido | Pixabay y un pack de efectos | uso libre, sin atribución | en `motor/sonidos/`, ya dentro |
| Las 11 camas musicales grabadas | Pixabay | uso libre, sin atribución | en `musica/pixabay/`, ya dentro |

Los **74 efectos de `motor/sonidos/`** son grabaciones de uso libre —el grueso, de
Pixabay (licencia de contenido de Pixabay: uso libre, sin atribución obligatoria); el
resto, de un pack de efectos de licencia libre—, elegidas una a una midiendo ataque,
pico, cola y brillo. Vienen dentro de la carpeta y **no tienes que atribuir nada** en tus
vídeos. Sólo `dun-dun-dun` sigue sintetizado. Las **25 camas musicales de `musica/`** sí
se sintetizan en tu ordenador desde las recetas del taller —y además vienen **once camas
grabadas** en `musica/pixabay/`, también de Pixabay y también sin atribución—, y
`motor/efectos.py` guarda
en `motor/sonidos/_sintetizados/` una versión sintetizada de casi todos, por si quieres
una variante. Los ejemplos van sin voz: la generas tú, con tu cuenta.

## Las piezas de interfaz

Los 31 PNG de `piezas/` son **atrezo para animar**: carpetas, notas, ventanas, cursores,
listas, controles. Varios **reproducen elementos de interfaz de escritorio y de móvil**
que reconocerás. Se incluyen para que los muevas dentro de tus piezas, igual que se
enseña la pantalla de una app en un anuncio.

Con ellos, dos reglas:

- **No los publiques sueltos** ni como si fueran material oficial de nadie, y no los
  revendas: no forman parte de lo que se te licencia para redistribuir (`LICENCIA.md`).
- Si tu vídeo va a decir o dar a entender que una marca ajena respalda lo tuyo, cambia la
  pieza. El atrezo ambienta; no acredita.

Si prefieres no usarlos, borra la carpeta `piezas/`: el taller funciona igual y dibuja sus
objetos en CSS.
