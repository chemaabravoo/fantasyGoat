# ¿Ya tenías Reel Motor? Esto lo actualiza

Si compraste la versión anterior y tienes ahí tus marcas y tus vídeos, **no empieces de
cero**. Se actualiza tu carpeta y no pierdes nada.

## Lo más fácil: díselo

Descomprime esta carpeta, ábrela con Claude Code y escribe:

> ya tenía Reel Motor, está en ~/Downloads/reel-motor

Él lo comprueba, te pregunta y lo hace. Nada más.

## A mano, si lo prefieres

```bash
bash actualizar-pack.sh ~/Downloads/reel-motor
```

O sin ruta, y busca la carpeta vieja al lado:

```bash
bash actualizar-pack.sh
```

## Qué toca y qué no

| | |
|---|---|
| **Se queda como está** | `taller/` entero: tus marcas, guiones, audios, piezas y vídeos. También `node_modules` y las skills de tus marcas |
| **Se actualiza** | el motor, los efectos, la música, los ejemplos, las piezas de interfaz, el oficio y los textos |
| **Se quita** | lo que la versión anterior dejaba y ya no sirve (`motor/INDICE.md`, los efectos sintetizados sueltos) |
| **Se cambia en tus piezas** | `window.FPS` de 30 a 60. Es lo único que se toca de lo tuyo |

**Antes de nada hace una copia de seguridad** de tu carpeta al lado, en
`…-antes-de-v2-<fecha>`. Cuando compruebes que va, la borras.

## Lo único que se puede romper

Si alguna pieza tuya hace parpadear algo **contando fotogramas** —un cursor, un texto que
titila—, así:

```js
el.cursor.style.opacity = frame(t)%20<11 ? 1 : 0;
```

a 60 fps parpadeará **al doble de rápido**. Se arregla doblando el número:

```js
el.cursor.style.opacity = frame(t)%40<21 ? 1 : 0;
```

Un `%N` en fotogramas es una duración disfrazada. Nada más se ve afectado: todo lo demás
cuelga de `seek(t)`, que va en segundos.

## Qué ganas

- **74 efectos grabados** dentro de la carpeta, en vez de sintetizarlos al instalar.
- **11 camas musicales grabadas**, una por familia. Las 25 sintetizadas siguen de respaldo.
- **La marca sale de la web del cliente en dos pieles**, clara y oscura, con su fondo, su
  cielo y sus letras medidos —no una perla fija para todos—, y la tipografía dentro del CSS.
- **60 fps.**
- **`reel motor <una-web>`** te monta la skill de esa marca. Puedes tener las que quieras.
- **`nueva-marca.sh`** saca un taller entero aparte para un cliente.
- **`motor/energia.mjs`**, que te dice si una pieza se ve animada o sólo se mueve.
- **`motor/logo.mjs`**, logos de empresas en vectorial.
- **Emojis, iconos y logotipos**, en `.claude/skills/reel-motor/animacion/simbolos.md`.
- **`validar.mjs` se niega** si el texto no se lee sobre el fondo de la marca.

Cuando termine, cierra Claude Code y ábrelo desde **tu** carpeta, que es la que está al día.
