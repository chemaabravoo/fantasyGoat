# Piezas de interfaz

PNG con transparencia, recortados a su contenido (lado mayor ≤ 1600 px), para animar sobre `cristal.css`.
Se colocan con `<img>` y se mueven con los ayudantes del motor (`blurIn`, `spring`, `vuela`).

| Archivo | Qué es | Tamaño |
|---|---|---|
| `barra-busqueda.png` | Campo de busqueda con lupa y cursor | 1511×384 |
| `barra-carga.png` | Barra de carga clasica con 'Loading...' | 1475×402 |
| `barra-herramientas.png` | Barra de navegacion: atras, adelante, pestanas, mas | 1446×212 |
| `burbujas-chat.png` | Dos burbujas de mensaje: azul enviada, oscura recibida | 1463×612 |
| `capas-timeline.png` | Cuatro pistas de linea de tiempo de colores | 1310×1474 |
| `carpeta-amarilla.png` | Carpeta de macOS, amarilla | 1426×1154 |
| `carpeta-azul.png` | Carpeta de macOS, azul | 1426×1155 |
| `carpeta-magenta.png` | Carpeta de macOS, magenta | 1426×1154 |
| `carpeta-verde.png` | Carpeta de macOS, verde | 1426×1154 |
| `chinchetas.png` | Dos chinchetas clavadas: azul y rosa | 1470×834 |
| `correo-nuevo.png` | Ventana de mensaje nuevo: Para, Asunto, Enviar | 1463×1393 |
| `cursor-mano.png` | Mano de puntero, contorno negro | 1036×1105 |
| `cursor-pixel.png` | Flecha de raton pixelada, estilo clasico | 849×1444 |
| `focos.png` | Selector de modos de concentracion: Personal / Trabajo / + | 1478×1168 |
| `hud-brillo-volumen.png` | Los dos HUD verticales: brillo y volumen | 1212×1178 |
| `icono-mensajes.png` | Icono de la app Mensajes, verde | 1600×1600 |
| `interruptores.png` | Interruptor encendido (verde) y apagado | 1456×362 |
| `lista-clara.png` | Lista clara de cinco filas con estrellas (la ultima roja) | 1405×1319 |
| `lista-oscura.png` | Lista oscura de cinco filas con estrellas (la ultima roja) | 1358×1310 |
| `llamada-botones.png` | Boton verde de descolgar y boton rojo de colgar | 1470×569 |
| `marco-escaneo.png` | Marco de escaneo: cuatro esquinas amarillas | 1345×1268 |
| `menu-editar.png` | Menu contextual Cortar / Copiar / Pegar, claro y oscuro | 1474×516 |
| `nota-amarilla.png` | Nota adhesiva amarilla | 1450×862 |
| `nota-azul.png` | Nota adhesiva azul | 1314×863 |
| `nota-rosa.png` | Nota adhesiva rosa | 1314×863 |
| `notificacion-mensajes.png` | Notificacion de Mensajes, clara, con 'ahora' | 1484×462 |
| `postits-tres.png` | Tres pósits apilados: rosa, naranja, amarillo | 539×1567 |
| `reproductor.png` | Reproductor con caratula, tiempos y controles | 1516×925 |
| `seleccion-tiradores.png` | Rectangulo de seleccion con ocho tiradores | 922×1252 |
| `ventana-mac.png` | Ventana de macOS con los tres semaforos | 1393×1356 |
| `ventana-mac-vacia.png` | Ventana de macOS vacia, mas ancha | 1429×738 |

## Cómo se usan

```html
<img class="pz" src="../../piezas/carpeta-amarilla.png" alt="">
```

Se colocan como cualquier elemento de la pieza y se mueven con los ayudantes del motor
(`blurIn`, `spring`, `vuela`). Van bien como **objeto que muta**: la carpeta que se abre y
suelta lo que hay dentro, la nota que aterriza, la ventana que se acerca.

## Aviso

Varias **reproducen elementos de interfaz de escritorio y de móvil** que reconocerás. Son
atrezo: se mueven dentro de tus piezas, **no se publican sueltas**, no se presentan como
material oficial de nadie y no se revenden (`LICENCIA.md`). Si el vídeo puede dar a
entender que una marca ajena respalda lo tuyo, cambia la pieza.

Si prefieres no usarlas, borra esta carpeta: el taller funciona igual.
