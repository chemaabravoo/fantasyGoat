# La entrega: validar, mirar, vistazo, render, sonido

Todo lo que pasa entre «el HTML está escrito» y «el mp4 está en su carpeta». Es el
**único** sitio donde se explica; el resto enlaza aquí.

## 0 · Validar antes de nada

```bash
node validar.mjs pieza-<nombre>.html            # [--muda] [--sin-musica]
```

Comprueba lo que se puede medir y **se niega** si falla algo que rompería la pieza:
`seek(t)` y `DURACION` expuestos, nada de `transition`/`@keyframes`, el reproductor
parado bajo captura, `#reel` presente, marca definida, efectos declarados, fotograma 0 con
algo puesto. Y avisa de lo que hay que mirar con criterio: texto por debajo de 1560 o
por encima de 180, dos textos que se pisan, etiquetas mono en mayúsculas (¿estarían
impresas en el papel?), tramos de un segundo en que nada se mueve. **Lo que comprueba el
validador no hace falta recordarlo ni contarlo**: por eso las trampas mecánicas ya no
están en las referencias.

Sobre un `-son.mp4` comprueba la entrega: pista de audio, 1080×1920, que no sea el
vistazo. `shoot-par.mjs` lo lanza solo antes de capturar; `--sin-validar` lo salta.

## 1 · Hojas de contactos, no cuatro fotogramas

```bash
node contactos.mjs pieza-<nombre>.html      # del HTML, ~15 s · o de un mp4
```

El gancho a cuatro fotogramas por segundo, el resto a dos, en tandas de treinta. **Se
miran todas, con Read, antes del vistazo.** Es lo único que enseña un rótulo que se queda
cuatro segundos de más, dos textos que dicen lo mismo, un tramo sin movimiento, un número
que salta antes de que la voz lo diga.

Los fotogramas sueltos van **después**, para confirmar un detalle:

```bash
node mirar.mjs pieza.html 0 0.4 1.2 2.8      # → carpeta temporal del sistema
node medir.mjs pieza.html <id> <fA> <fB>     # ¿tiembla el maquetado? un solo valor = no
node solapes.mjs pieza.html 0.3              # dos capas coincidiendo, barrido entero
```

## 1b · Antes del vistazo, tres medidas

```bash
node ../../motor/validar.mjs   pieza-<nombre>.html     # lo roto y lo que se sale
node ../../motor/energia.mjs   pieza-<nombre>.html     # ¿se mueve lo suficiente?
node ../../motor/contactos.mjs pieza-<nombre>.html     # y dónde no · se leen TODAS las hojas
```

Las tres, siempre, y ninguna sustituye a otra: `validar` no sabe si la pieza es aburrida,
`energia` no sabe dónde, y `contactos` no sabe si algo se sale del encuadre. El umbral y
el porqué, en [motion-ui.md](../animacion/motion-ui.md).

## 2 · El vistazo se ENSEÑA; el render bueno, después

> El primer archivo que sale de una pieza es el vistazo, con voz, y se le manda. El
> render de calidad no se hace hasta que él lo ve.

```bash
node shoot-par.mjs pieza-<nombre>.html /tmp/ver.mp4 10 0.5 30       # medio de 60
python3 sonar-generico.py /tmp/ver.mp4 ../audios/<pieza>-seco.mp3   # < 1 s
```

Los dos últimos números son la **escala** y los **fps**. **Las piezas se animan a 60**
(`window.FPS`), que es lo que hace que un barrido rápido o una cifra que rueda no salgan a
tirones; el `[fps]` que se pide aquí sólo puede bajar de ahí. `0.5` y `30` es el vistazo:
540×960 y la mitad de fotogramas, se lee todo y el ritmo se juzga igual porque `seek(t)` es
puro. Si lo que se está corrigiendo es la fluidez misma, el vistazo va a `0.5` y `60`.
El vistazo se avisa a sí mismo: `⚠ BORRADOR, no se publica`. Lleva voz porque la mitad
de lo que se corrige es si la imagen va cuadrada con la locución; un vistazo mudo no vale.

Sólo cuando lo ha visto y ha dicho que sí:

```bash
node shoot-par.mjs pieza-<nombre>.html salida.mp4                   # escala 2, 60 fps
python3 sonar-generico.py salida.mp4 ../audios/<pieza>-seco.mp3      # → salida-son.mp4
node validar.mjs salida-son.mp4
```

`shoot-par.mjs` reparte los fotogramas entre diez Chrome (uno por obrero, no pestañas;
las tipografías se descargan una vez y se sirven de caché). Medido en un Mac de 10
núcleos: **a 60 fps una pieza de 13 s son 774 fotogramas y el vistazo (escala 0,5) tarda
29 s de captura**. Las cifras viejas eran a 30 fps —1467 fotogramas en 194 s a escala 2,
63 s a escala 1—: **al doblar los fps, se doblan los fotogramas y el tiempo**. Por eso el
vistazo baja a 30 y el bueno va a 60. Sale el mp4 **mudo** y su `.marcas.json` al lado.
`shoot.mjs` sigue ahí para renderizar de uno en uno.

## 3 · El sonido

`sonar-generico.py` pega la voz (la toma única de `toma.py`, apretada con `secar.py`), los
efectos que declara el HTML en `MARCAS.SFX` y la música por tramos de `MARCAS.MUSICA`.
Cómo se pide la voz, cómo se sacan los tiempos y qué efectos hay: [../sonido/voz.md](../sonido/voz.md).
Con un audio ya publicado (voz y cama mezcladas) se pasa como voz, sin `MUSICA`, y los
efectos van a 0,25-0,5. Muda **sólo** si él lo pide para esa pieza, y entonces `--muda`.

## 4 · Entregar

El `-son.mp4` (nunca el mudo), el mudo por si lo quiere montar él, el mapa de tiempos y
**qué elegiste y por qué**: el armazón, el gancho, la forma. Sin eso no se puede corregir.
Dónde se archiva y cómo entra en el panel de Instagram lo dice la skill de cada marca.
