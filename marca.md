# El manual de marca → tokens

Se hace **una vez por cliente**. El resultado es un `marca.css` que todas sus piezas
importan. Si esto se hace mal, se nota en todas.

## Lo que hay que sacar, venga como venga

Da igual si llega un PDF de 40 páginas, tres capturas de la web, una URL o un mensaje que
dice «los colores son negro y naranja». Lo que hace falta es siempre esto:

| Token | Qué es | Cómo se decide |
|---|---|---|
| `--fondo` | El lienzo | **El suyo**, medido de su web. Lo escribe `marca-desde-web` en las dos pieles |
| `--tinta` / `--tinta-baja` | El texto | Se derivan del fondo con el contraste medido: **7:1 y 4,5:1 como mínimo**, o `validar.mjs` se niega |
| `--cielo-*` / `--mancha-*` | El fondo vivo | Cuatro manchas de la familia de su acento. `--manchas` sube o baja su fuerza |
| `--acento` | El color de marca | El que la gente asocia a la marca. Rellena; nunca es texto |
| `--titular` | Tipografía de titulares | La de la marca. Si no hay, una grotesca de peso alto |
| `--dato` | Monoespaciada | Para cifras, pies, etiquetas. Da sensación de dato |

## La regla que más veces se ha fallado

> **El color de marca casi nunca vale como tinta de texto.**

Un naranja de marca sobre negro puede quedar en 3,8:1: perfectamente renderizado y
perfectamente ilegible en un móvil a pleno sol. El acento sirve para **subrayar, rellenar,
enmarcar y llamar la atención**; el texto va en `--tinta`.

Y esto **no se decide mirando**. Se mide:

```bash
node -e '
const hex=h=>{h=h.replace("#","");return [0,2,4].map(i=>parseInt(h.substr(i,2),16)/255)};
const L=c=>{const [r,g,b]=hex(c).map(v=>v<=0.03928?v/12.92:((v+0.055)/1.055)**2.4);
  return 0.2126*r+0.7152*g+0.0722*b};
const R=(a,b)=>{const [x,y]=[L(a),L(b)].sort((p,q)=>q-p);return ((x+0.05)/(y+0.05)).toFixed(2)};
const F="#141010";
for(const c of ["#f4ece0","#e8b04b","#8b7f70"]) console.log(c, R(c,F));
'
```

Cambia `F` por el fondo y la lista por los colores candidatos. Menos de 4,5 no es texto.

## Cuando el manual no lo dice todo

Casi nunca lo dice. Lo que falta se completa así:

- **No hay tipografía**: una grotesca de peso 600–700 para titulares (Space Grotesk, Inter
  Tight, Archivo) y una mono para datos (JetBrains Mono, IBM Plex Mono). Vía Google Fonts,
  que es lo único que carga limpio en el render.
- **No hay color de fondo**: `--fondo` a un neutro muy oscuro **teñido con el acento** — no
  negro puro. Un negro con un 4 % del acento dentro es lo que hace que la pieza «sea de la
  marca» sin que se sepa por qué.
- **Sólo hay un color**: `--acento-2` = el mismo con `opacity .35`, o su versión clara.
- **El manual es para papel**: sus colores estarán en CMYK y saldrán apagados en pantalla.
  Súbeles la saturación un 10–15 % o el vídeo parecerá desteñido.

## El fondo no es un color plano

Un `background` liso se lee como plantilla. El fondo lleva **siempre** al menos una de
estas dos, con el acento a muy baja opacidad:

```css
.reel{
  background:var(--fondo);
  background-image:radial-gradient(60% 36% at 50% 46%,
    color-mix(in srgb, var(--acento) 11%, transparent), transparent 72%);
}
```

Y ese halo es de la **capa ambiente** ([movimiento.md](animacion/movimiento.md)): se mueve despacio
durante toda la pieza, no se queda fijo.

## Lo que se escribe

El motor **no tiene paleta por defecto**. Trae `marca-PLANTILLA.css` con valores de relleno
deliberadamente feos —magenta, `system-ui`— y un centinela:

```css
--marca:"SIN DEFINIR";
```

Mientras eso siga ahí, el guardián de `base.html` pinta una banda roja en **todos** los
fotogramas y lanza un error que `mirar.mjs` y `shoot.mjs` imprimen. No es un aviso
amable: es para que sea imposible entregar una pieza sin marca.

Con web, esto **no se escribe a mano**: `node motor/marca-desde-web.mjs <url> taller/<slug>`
deja los dos archivos enteros —`marca-clara.css` y `marca-oscura.css`— con su fondo, su
cielo, su acento y sus letras, y un `marca.css` de una línea que importa la elegida. Sin
web, se copia `motor/marca-PLANTILLA.css` (clara) o `marca-PLANTILLA-oscura.css` y se
rellenan las mismas ranuras:

```css
/* marca-oscura.css · <Cliente> */
@import url("https://fonts.googleapis.com/css2?family=<La+Suya>:wght@400;600;700&display=swap");
:root{
  --marca:"<Cliente>";        /* ← esto apaga el aviso */
  --fondo:#0d1b14;  --tinta:#f2f7f4;  --tinta-baja:#8fa398;   /* medidos: 7:1 y 4,5:1 mínimo */
  --acento:#0f9d58;
  --cielo-a:#12241a; --cielo-b:#0d1b14; --cielo-c:#101f22;
  --mancha-1:#3ec98a; --mancha-2:#3ec9c0; --mancha-3:#8ec93e; --mancha-4:#3e6ec9;
  --manchas:.8;
  --titular:"<la de la marca>",sans-serif;
  --dato:"<una mono>",monospace;

  /* personalidad de movimiento · ver movimiento.md */
  --personalidad:segura;      /* nerviosa · segura · cara · seca */
}
```

**La tipografía viaja dentro del CSS**, en ese `@import` de arriba. Antes iba en dos sitios
—el token y el `<link>` de la pieza— y si no cuadraban, Chrome sustituía sin avisar y la
pieza salía entera, bien maquetada, con la letra equivocada
([trampas.md](entrega/trampas.md) 19). El `@import` tiene que ser **la primera línea** del
archivo o el navegador lo ignora sin decir nada.

**Y si sustituyes la fuente a mano, cambia el `@import` Y el token, en las dos pieles.**
Tocar sólo `--titular` deja el nombre de una fuente que nadie ha cargado, y vuelve la
misma trampa por la puerta de atrás.

Anota la personalidad **aquí**, no en la cabeza. Es lo que hace que la pieza número 8 se
mueva como la 1.

## Nunca heredes la paleta de otro cliente

Copiar `marca.css` de un cliente anterior «para tener algo con lo que empezar» es lo que
hace que a la tercera pieza todos los clientes se parezcan entre sí — y en el peor caso,
que uno salga con la identidad de otro. **Se copia siempre de `marca-PLANTILLA.css`** (o de la
oscura), que por eso viene con `--marca:"SIN DEFINIR"`: para que dé rabia dejarla puesta.

## Los activos

| Qué | Dónde va | Cuidado |
|---|---|---|
| Logotipo | `marca/logo.svg` | **Un logotipo ajeno no se recolorea.** Si no contrasta, se le pone su fondo de marca detrás |
| Producto | `marca/producto/` | Capturas de la app o la web **reales**, no dibujadas de memoria |
| Fotos de gente | `marca/gente/` | Caras de verdad. Unas iniciales en un círculo se leen como maqueta |
| Tipografías propias | `marca/fuentes/` | `@font-face` con ruta local. El render corre en `file://` |

## Los datos reales

Si la marca da cifras, precios, nombres o testimonios, **se usan tal cual y cuadran entre
sí**. Una cifra rara cuenta una historia; una redonda parece inventada. 62,40 € se cree;
60 € no.

Si no hay datos reales, se piden. No se inventan cifras que parezcan de la empresa.

## Antes de dar la marca por montada

1. ¿Pasa `node motor/validar.mjs` en las dos pieles? (mide la tinta y avisa del acento)
2. ¿El cielo es de la familia de su acento, y no el azul-morado de la casa?
3. ¿La tipografía carga en `file://`? Renderiza un fotograma y míralo
4. ¿Está anotada la personalidad de movimiento?
5. ¿Hay logotipo, o el cierre va a ser sólo texto? (Sólo texto es una opción legítima)
