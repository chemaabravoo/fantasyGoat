---
name: reel-motor
description: >
  El oficio de animar vídeos verticales 9:16 en el estilo motion UI de la casa —
  todo entra de borroso a nítido, un objeto que muta, muelle, cámara con profundidad,
  cifras que ruedan— sobre la piel de cristal. La pieza se escribe en HTML con una
  seek(t) determinista y se captura a mp4 con voz, efectos y música, y con la portada
  1080x1920 encuadrada al cuadrado central que se entrega con cada vídeo. Se usa siempre
  junto a la skill de la marca del cliente (.claude/skills/<marca>), que pone sus
  colores, sus datos y su tono. Úsala cuando alguien pida una animación, un reel, un
  vídeo, un mp4 o una pieza para Instagram, TikTok o Shorts, y también para retocar el
  ritmo, el encuadre o los tiempos de una ya hecha.
---

# El oficio de animar un reel

**Una idea + la marca del cliente → un mp4 9:16 donde no hay un segundo quieto y los tres
primeros deciden si alguien se queda.** Esta skill es el **cómo**. El **qué** —colores,
tipografías, producto, datos, tono— lo pone la skill de la marca, en
`.claude/skills/<marca>/SKILL.md`, que se monta con `marca-desde-web` la primera vez.

Si te ves escribiendo aquí un color, un dato o una frase de un negocio, va en su skill.
Si una regla de animación sirve para dos marcas, va aquí.

## Las cuatro partes

| Parte | Qué resuelve | Archivos |
|---|---|---|
| **Guion** | Qué se cuenta, en qué orden y **con qué palabras**: el gancho, el armazón, el tono de la marca | [guion/gancho.md](guion/gancho.md) · [guion/estructura.md](guion/estructura.md) · [guion/tono.md](guion/tono.md) |
| **Animación** | Cómo se mueve: el estilo motion UI, la piel de cristal, las curvas, la cámara, el encuadre | [animacion/motion-ui.md](animacion/motion-ui.md) · [cristal.md](animacion/cristal.md) · [movimiento.md](animacion/movimiento.md) · [motor.md](animacion/motor.md) · [forma.md](animacion/forma.md) · [encuadre.md](animacion/encuadre.md) |
| **Sonido** | La voz en una toma con tiempos por palabra, los efectos, la música por tramos | [sonido/voz.md](sonido/voz.md) |
| **Entrega** | Validar, mirar, el vistazo, el render, el archivo final | [entrega/render.md](entrega/render.md) · [entrega/trampas.md](entrega/trampas.md) (consulta, no lista) |

## Cómo funciona por dentro

Cada pieza es **una página web con una `seek(t)`**: dado un segundo, dibuja la pantalla en
ese instante. Un script le pide 30 instantes por segundo, los fotografía y los pega en un
mp4. Nada de `@keyframes`, `transition` ni `setTimeout`: el fotograma 137 sale igual
siempre. Los ayudantes, las curvas y el cielo están en `motor/comun.js` y
`motor/comun.css`; la piel en `motor/cristal.css`; el esqueleto de una pieza en
`motor/base.html`, que es el motor y no una plantilla: la escena se escribe entera cada vez.

## Las cuatro leyes

1. **Los tres primeros segundos.** En el fotograma 0 ya hay algo a medio moverse, se lee
   sin sonido en cinco palabras y se abre un bucle que no se cierra hasta el final.
   [guion/gancho.md](guion/gancho.md).
2. **Ni un segundo muerto.** Cada 1,2-2 s pasa algo, y por debajo siempre respira el cielo.
   Se retiene **transformando, no cortando**. [animacion/movimiento.md](animacion/movimiento.md).
3. **La marca se hereda, la película no.** Paleta, tipografías, encuadre y datos se
   repiten siempre; el objeto con el que se cuenta y el plano se inventan cada vez.
   [animacion/forma.md](animacion/forma.md).
4. **Ninguna pieza se entrega muda.** Voz en una toma, efectos declarados en el HTML con
   los mismos tiempos que mueven la imagen, música por tramos. [sonido/voz.md](sonido/voz.md).

## El estilo: motion UI sobre cristal

Todo entra de borroso a nítido, un objeto muta en vez de cortar, muelle en lo que
aterriza, escalera, cámara con profundidad de campo, siempre una cifra rodando, y **los
objetos son los de la marca** (su app, su web, su producto), nunca píldoras genéricas.
Las siete leyes y el vocabulario: [animacion/motion-ui.md](animacion/motion-ui.md). La
piel —el cielo vivo, el cristal, cómo entran los colores del cliente—:
[animacion/cristal.md](animacion/cristal.md). **Los emojis, los iconos y los logotipos
—que es la mitad de lo que hace que una pieza parezca profesional— en
[animacion/simbolos.md](animacion/simbolos.md)**: en un Mac los emojis salen los de Apple
sin hacer nada, los iconos van con Material Symbols y se tiñen con el acento, y los logos
de terceros se bajan en vectorial con `motor/logo.mjs`. Seis piezas completas para copiar la
técnica (no el plano): `ejemplos/`.

## El flujo, en ocho pasos

```bash
# 1 · la marca · la monta marca-desde-web en taller/<marca>/marca.css y .claude/skills/<marca>/
cd taller/<marca>
```

2. **El guion.** Armazón, gancho y **tono de la marca** ([guion/](guion/): las palabras
   son las suyas, no las del taller); una frase por línea en
   `guiones/<pieza>.txt`. **La voz se pide ya** (`toma.py`), se le aprietan los silencios
   (`secar.py`) y de ahí sale `M` (`marcas.py`): los compases cuelgan de las palabras,
   nunca de segundos a mano.
3. **La forma.** Tres formas de canteras distintas, se tira la primera
   ([animacion/forma.md](animacion/forma.md)). **Di la pieza en una frase** antes de tocar
   el HTML.
4. **El HTML.** `cp ../../motor/base.html pieza-<nombre>.html`. Un bloque por elemento
   dentro de `seek()`, con el vocabulario de motion-ui.md. `SFX` y `MUSICA` con los
   mismos compases.

```bash
# 5 · validar · se niega si algo medible falla
node ../../motor/validar.mjs pieza-<nombre>.html
# 6 · las hojas de contactos · se miran TODAS con Read
node ../../motor/contactos.mjs pieza-<nombre>.html
# 7 · el vistazo, con voz, y se le enseña · ~40 s · la MITAD de 60
node ../../motor/shoot-par.mjs pieza-<nombre>.html salida/ver.mp4 10 0.5 30
python3 ../../motor/sonar-generico.py salida/ver.mp4 audios/<pieza>/toma.mp3
# 8 · sólo cuando ha dicho que sí · ~10 min · a 60, que es como se anima
node ../../motor/shoot-par.mjs pieza-<nombre>.html salida/<pieza>.mp4 10 2 60
python3 ../../motor/sonar-generico.py salida/<pieza>.mp4 audios/<pieza>/toma.mp3
# 9 · la portada · SIEMPRE que hay render de calidad
node ../../motor/portada.mjs salida/<pieza>-son.mp4 salida/<pieza>-portada.png \
  --cifra "…" --frase "…" --pie "<marca>"
```

Se entrega el `-son.mp4`, **su portada**, el mapa de tiempos y **qué elegiste y por qué**.
[entrega/render.md](entrega/render.md).

**Ningún render de calidad se entrega sin portada.** Es 1080 × 1920, pero lo legible va
dentro del cuadrado central (`y 420`-`1500`), que es lo que se ve en la parrilla del perfil.

## Antes de dar una pieza por buena

1. **Fotograma 0**: ¿hay algo a medio moverse, o la pantalla arranca vacía?
2. **Segundo 3**: ¿se entiende la promesa sin sonido? ¿Hay un bucle abierto?
3. **El latido**: ¿algún hueco de más de 2 s sin evento? Las hojas de contactos lo delatan.
4. **¿Es motion UI?** Blur de entrada y salida, muelle, cámara, una cifra que rueda.
5. **¿Los objetos son los de la marca?** Una píldora que no existe en su web es genérica.
6. **¿`validar.mjs` en verde y las hojas de contactos miradas?** Todas.
7. **¿Suena?** Voz en una toma, efectos en cada golpe, música que cambia con la pieza.
8. **¿Ha visto el vistazo?** El render de calidad no se hace antes.
9. **¿Lo que se lee y lo que pasa está dentro de la zona segura** (x 100–910, y 250–1520)
   a su tamaño y centrado en 540? Si una frase no cabe, se acorta; no se encoge.

Si algo se ve raro y no sabes por qué, busca en [entrega/trampas.md](entrega/trampas.md).

## Sobre el lote

Las piezas van de una en una. Lo que hace buena una pieza son las tres o cuatro pasadas de
corrección, y en lote no se dan.
