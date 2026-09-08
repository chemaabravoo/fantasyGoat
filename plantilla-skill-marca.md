---
name: reel-{{slug}}
description: >
  La marca {{Nombre}} ({{web}}): {{qué es, en una frase: «la clínica dental de
  Málaga que…», «la app para…»}}. Su identidad —{{fondo y acento en palabras}},
  {{tipografía}}—, sus datos reales, su tono, su voz de ElevenLabs y la lista
  de formas ya usadas. Úsala SIEMPRE que se pida un reel, una animación, un
  guion, un post o ideas de {{Nombre}}, o cuando se nombre la marca. Para
  vídeo se carga junto a `reel-motor`, que pone el motor, el ritmo, la voz y
  el render: aquí está el qué, allí el cómo.
---

# {{Nombre}}

## Qué es

{{Dos o tres frases: qué vende, a quién, dónde, desde cuándo. Sacado de la
web o del manual. Lo que no se sepa, «por confirmar».}}

## Quién lo ve

{{El público: edad, situación, qué le duele, en qué red está. Si no se sabe,
lo que se deduce de la web, dicho como deducción.}}

## La identidad

Los tokens viven en `taller/{{slug}}/marca.css`. Medidos, no mirados:

| Token | Valor | Contraste con el fondo |
|---|---|---|
| `--fondo` | `{{#…}}` | — |
| `--tinta` | `{{#…}}` | {{x,x}}:1 |
| `--tinta-baja` | `{{#…}}` | {{x,x}}:1 |
| `--acento` | `{{#…}}` | {{x,x}}:1 · {{vale / NO vale}} como texto |
| `--acento-2` | `{{…}}` | — |

- **Tipografías**: titulares `{{familia}}` {{peso}}; datos y cifras
  `{{mono}}`. El `<link>` de Google Fonts para cada pieza:
  `{{https://fonts.googleapis.com/css2?family=…}}`
- **Personalidad de movimiento**: `{{nerviosa | segura | cara | seca}}` —
  {{por qué, en media línea}}.
- **Activos**: `taller/{{slug}}/marca/logo.{{ext}}` ({{descripción: wordmark
  claro sobre oscuro, símbolo…}}); capturas de la web en la misma carpeta.
  {{Si hay producto o app: dónde están las capturas reales.}}
- **Lo que la web hace y el vídeo hereda**: {{dos o tres rasgos: «botones
  redondos», «fotos desaturadas», «mucho blanco», «cursivas en los
  titulares»…}}

## Los datos reales

{{Lo que se puede decir con cifra porque está en la web o lo dijo el cliente:
precios, años, número de clientes, reseñas, horarios, ciudad. Tal cual, sin
redondear. Si no hay ninguno: «no hay cifras confirmadas; se piden antes de
usar una».}}

- Web: {{web}}
- Contacto: {{teléfono / WhatsApp / mail, si están en la web}}
- Redes: {{@…}}

## El tono

{{Cómo habla la marca: tú o usted, cercano o técnico, con humor o sin él,
frases largas o cortas. Dos ejemplos de frases suyas, entrecomilladas, sacadas
de la web.}}

## El cierre

- La frase que se puede citar: «{{una, corta; si la web tiene un lema, ése}}»
- La marca: **{{Nombre}}** · el pie: `{{web}}`
- La acción, si la hay: «{{una sola palabra o frase: «Reserva», «Pide
  cita», «Escríbenos»}}»

## La voz

`{{nombre de la voz}}` · id `{{id de ElevenLabs}}` · `eleven_v3` · `es`.
{{Por qué esa: masculina/femenina, registro. Si es la de por defecto, dilo.}}
Se elige una vez y no se cambia entre piezas.

## Lo que no se puede decir

{{Promesas que el sector no permite (salud: resultados clínicos; fitness:
antes-y-después; finanzas: rentabilidades), y lo que el cliente haya pedido
no decir. Si no hay nada: «nada especial, por ahora».}}

## Formas ya usadas

Cada pieza apunta aquí su forma en una frase, para no repetirla:

| Fecha | Pieza | La forma, en una frase | Cama |
|---|---|---|---|
| {{AAAA-MM-DD}} | `pieza-prueba` | el nombre aterriza, una barra se descubre, tres chips, un contador | — |
