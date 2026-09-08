# Los efectos de sonido

Setenta y cuatro efectos, ya dentro de la carpeta: son **grabaciones**, no
sintetizadores, elegidas midiendo ataque, pico, cola y brillo. Se usan por su nombre
en el `SFX` de la pieza: `['boom', T.giro[0], 0.5]` →
`[nombre, segundo, ganancia, tono?]`. El cuarto valor cambia el tono: >1 agudiza y
acorta, <1 agrava y alarga.

**Ancla**: los que la tienen no empiezan en su segundo, acaban o golpean en él
(`subida` llega al pico, `abrir` termina de abrir, `cuenta-atras` acaba de contar).
Están medidas en `anclas.json`; el mezclador las lee solo.

Un golpe visual sin su efecto es medio golpe; y un efecto sin golpe visual es ruido.
Uno cada 0,7 s es lo medido en la pieza de referencia: no tengas miedo de poner muchos,
pero que cada uno tenga su porqué en pantalla.

Si te falta uno, `motor/efectos-eleven.py` lo pide a ElevenLabs con tu cuenta y lo deja
en `taller/<marca>/sonidos/`, que manda sobre éstos para ese nombre.

## Transiciones

| Efecto | Dura | Para qué |
|---|---|---|
| `whoosh` | 0.70 s | algo sale disparado o se envía; un cambio de plano |
| `whoosh-largo` | 1.60 s | un cambio de plano grande, la cámara que viaja |
| `barrido` | 0.88 s | una hoja que sube, un plano que entra |
| `swipe` | 0.50 s | pasar una tarjeta, un gesto rápido |
| `estirar` | 1.10 s | el objeto que muta y se estira: el morph del motion UI |
| `subida` | 3.45 s · ancla 2.12 s | anuncia lo que viene; el pico cae en su segundo |
| `subida-larga` | 3.30 s · ancla 2.95 s | tres segundos de subida antes del giro grande |
| `bajada` | 2.00 s | al revés que la subida: algo se va, un plano que se cierra |
| `rebobinar` | 1.20 s · ancla 1.20 s | volver atrás, deshacer; acaba en su segundo |
| `freno` | 0.58 s | parada de cinta: se para todo, el «espera» |
| `glitch` | 0.50 s | fallo digital, corte brusco, lo que se rompe |
| `corte` | 0.34 s | el corte seco entre dos planos |

## Golpes

| Efecto | Dura | Para qué |
|---|---|---|
| `golpe` | 2.31 s | algo con peso que aterriza: una tarjeta, el móvil, el cierre |
| `impacto` | 2.95 s | el golpe con cola grave: el giro, la caída |
| `boom` | 2.97 s | el boom grave con cola larga: algo que cae de golpe, el remate |
| `bombo` | 0.50 s | un bombo seco a compás; para marcar cortes |
| `caida` | 1.05 s | la caída de graves: el bajón, el «se acabó» |
| `estampido` | 0.58 s | un golpe corto y seco: algo se estampa |
| `portazo` | 1.18 s | una puerta, algo que se cierra de golpe |

## Interfaz

| Efecto | Dura | Para qué |
|---|---|---|
| `tecla` | 0.24 s | un toque en la pantalla |
| `teclado` | 1.00 s | escribir: una ráfaga de teclas |
| `teclado-largo` | 2.50 s | escribiendo de verdad, para debajo de una frase entera |
| `clic` | 0.09 s | un clic de ratón, un botón pequeño |
| `clic-digital` | 0.21 s | un clic con cuerpo: un control de la app |
| `seleccionar` | 0.21 s | marcar una opción, elegir de una lista |
| `blip` | 0.27 s | un aviso corto, algo que se recibe |
| `notificacion` | 1.70 s | llega una notificación |
| `mensaje` | 1.01 s | llega un mensaje; tres notas que suben |
| `enviar` | 0.45 s | se manda, se confirma, se acepta |
| `borrar` | 0.35 s | se borra, se quita, se deshace |
| `pop` | 0.25 s | algo aparece: una burbuja, un icono, un chip |
| `abrir` | 1.47 s · ancla 0.92 s | una hoja o un panel que se abre: acaba de abrirse en su segundo |
| `burbuja` | 0.95 s | algo sube o se infla |
| `toggle` | 0.52 s | un interruptor, activar algo |
| `parpadeo` | 0.40 s | un texto que entra parpadeando, un dato que titila |
| `error` | 1.00 s | lo que está mal, lo que se tacha |
| `acierto` | 1.37 s | lo que sale bien, lo que se resuelve |
| `campana` | 0.95 s | algo se revela, un dato que suena a verdad |
| `caja` | 1.02 s | la caja registradora: dinero, pagar, cobrar |
| `monedas` | 0.82 s | monedas que caen: ahorro, céntimos, propina |
| `dinero` | 1.10 s | el dinero de película: la cifra que aparece, lo que se ahorra |
| `timbre` | 1.30 s | ding-dong: alguien llega, un pedido |
| `alarma` | 0.80 s | una alarma, un aviso urgente |
| `camara` | 0.53 s | una foto: el ticket, la captura |
| `cuenta-atras` | 1.83 s · ancla 1.80 s | pitidos que se aceleran y acaban en su segundo |

## Datos y máquina

| Efecto | Dura | Para qué |
|---|---|---|
| `datos` | 0.96 s | cifras que ruedan, algo que se calcula en pantalla |
| `datos-largo` | 2.60 s | el cálculo que dura: el reparto que se resuelve solo |
| `cronometro` | 2.00 s | el reloj digital del reto: el tiempo corriendo en pantalla |
| `engranaje` | 0.67 s | un mecanismo que gira, las piezas que encajan |
| `engranaje-largo` | 1.27 s · ancla 1.15 s | el mecanismo que arranca y encaja en su segundo |

## Dramáticos

| Efecto | Dura | Para qué |
|---|---|---|
| `latido` | 0.90 s | lub-dub: la espera, el silencio que incomoda |
| `reloj` | 2.00 s | tic-tac de agujas: el tiempo que corre |
| `dun-dun-dun` | 3.80 s | tres golpes de metales que bajan: el drama, en broma o en serio |
| `tension` | 2.60 s | un drone que sube y se corta: algo va a pasar |
| `revelacion` | 2.80 s | un arpegio que sube y brilla: el dato que lo cambia todo |
| `suspenso` | 2.00 s | un golpe de cuerdas: el sobresalto |
| `disco-rayado` | 0.60 s | el vinilo que se frena: «espera, ¿qué?» |
| `silbato` | 1.05 s | el silbato que baja: la caída de dibujos, el fracaso con gracia |
| `muelle` | 0.51 s | boing: algo rebota, lo cómico |
| `aplauso` | 3.10 s | aplausos: el logro, el final |
| `redoble` | 1.52 s · ancla 1.47 s | el redoble acaba en su segundo (este no lleva platillo: el golpe lo pones tú con `bombo` o `campana`) |
| `grillo` | 1.60 s | grillos: el silencio incómodo, nadie contesta |
| `zap` | 0.19 s | un láser, algo que desaparece de golpe |
| `brillo` | 0.82 s | algo se enciende, una cifra que remata |
| `fiesta` | 0.62 s | pops y brillo: la celebración |
| `cristal-roto` | 1.17 s | algo se rompe de verdad |

## Cotidiano

| Efecto | Dura | Para qué |
|---|---|---|
| `loza` | 0.50 s | vajilla, mesa, bar |
| `vaso` | 0.48 s | un vaso, una copa que se posa |
| `brindis` | 0.60 s | dos copas que chocan |
| `roce` | 1.05 s | papel, tela, algo que se arrastra |
| `hilo` | 0.40 s | una línea que se traza, algo que conecta |
| `papel` | 0.60 s | pasar una página, un ticket que se despliega |
| `boligrafo` | 0.30 s | un bolígrafo: apuntar, firmar |
| `sello` | 0.54 s | un sello que cae: aprobado, pagado |
