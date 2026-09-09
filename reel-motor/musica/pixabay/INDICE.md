# Las once camas grabadas

Grabaciones de **Pixabay** (licencia de contenido de Pixabay: uso libre, sin atribución
obligatoria), una por familia. Vienen dentro de la carpeta: no hay que generarlas.

Se llaman por su nombre en el `MUSICA` de la pieza, sin extensión:

```js
const MUSICA=[
  ['px-corporativo-upbeat-tech', 0,               0.15],
  ['px-tension-building',        T.giro[0]-0.40,  0.17],
  ['px-epica-trailer-inspirador',T.remate[0]-0.20,0.16],
];
```

| Cama | Dura | Para qué |
|---|---|---|
| `px-corporativo-upbeat-tech` | 144 s | tecnología que avanza; el arranque de una demo |
| `px-corporativo-the-tech` | 164 s | lo mismo, más contenido: debajo de una explicación |
| `px-corporativo-inspiring-minimal` | 154 s | piano y aire; el cierre que quiere sonar honesto |
| `px-tension-building` | 90 s | el argumento que se aprieta antes del giro |
| `px-epica-trailer-inspirador` | 184 s | la resolución, el remate que levanta |
| `px-epica-trailer-dramatico` | 162 s | el giro grande, la cifra que sorprende |
| `px-emocion-piano-violin` | 132 s | la cuña emotiva, el testimonio |
| `px-energia-elevating` | 137 s | subida sostenida; una lista que se llena |
| `px-alegre-happy-upbeat` | 85 s | consumo, humor, algo que se disfruta |
| `px-lofi-jazzy` | 119 s | cotidiano, tranquilo; un «mientras tanto» |
| `px-funk-groove` | 86 s | con chispa; producto joven, ritmo marcado |

**Cómo se elige**: por lo que pasa en la pieza, no por gusto. Si la voz lleva mucho texto,
baja un peldaño de energía. Nivel bajo la voz: **0,15** (a 0,30 tapa). Y **la música va por
tramos**: una por acto, con `fundido` o `corte` entre ellos. Una sola cama de principio a
fin es lo que hace que una pieza de 50 s se sienta larga.

Las **25 sintetizadas** de `../largos/` siguen ahí: se generan al instalar y sirven cuando
ninguna de éstas pega. Su índice, en `../INDICE.md`.
