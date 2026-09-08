# La voz · conectar ElevenLabs

Los vídeos pueden salir **con voz** o **sólo con música y efectos**. Si los quieres con
voz, hace falta una cuenta de ElevenLabs, que es **tuya, no mía**: el taller la usa con tu
clave y desde tu ordenador.

El taller la usa para dos cosas. Genera la locución del guion en **una sola toma** (sin
trozos pegados, por eso suena natural) y luego **transcribe esa misma toma** para saber en
qué segundo cae cada palabra. De ahí sale que la imagen vaya clavada con lo que se dice:
los golpes de animación cuelgan de las palabras, no de tiempos puestos a mano.

Claude te guía por esto la primera vez. Aquí está por escrito, por si lo quieres a mano.

## 1 · La cuenta

Crea una cuenta en <https://elevenlabs.io>.

| | Gratis | Starter (~5 $/mes) |
|---|---|---|
| Voz al mes | ~10 minutos · **entre tres y seis reels** | ~30 minutos, y se amplía |
| Voces | las del catálogo público (hay castellano de sobra) | las mismas **+ clonar tu voz** o la de tu marca |
| **Uso comercial** | **no lo permite** | **sí** |

Con el plan gratuito se prueba el taller entero y se ve cómo queda. **Si los vídeos son
para vender algo —tu negocio, un cliente—, hace falta el de pago**: no es un capricho mío,
son las condiciones de ElevenLabs.

## 2 · La clave

Tu perfil, arriba a la derecha → **API Keys** → **Create API Key**. Empieza por `sk_`.

**Trátala como una contraseña.** Quien la tenga gasta tu saldo.

- No la pegues en el chat de Claude, ni aquí ni en ningún sitio.
- No la escribas dentro de un archivo de esta carpeta.
- Si se te escapa en algún sitio, bórrala en el panel de ElevenLabs y saca otra. Se tarda
  diez segundos y la vieja deja de servir.

Se la das al taller por **una variable de entorno**, que es la forma de que la vean los
programas de tu ordenador sin que quede escrita en el proyecto. En Mac (`~/.zshrc`) o
Linux (`~/.bashrc`), en **tu Terminal**, no en Claude:

```bash
echo 'export ELEVENLABS_API_KEY=sk_TU_CLAVE' >> ~/.zshrc && source ~/.zshrc
```

En Windows con Git Bash, lo mismo cambiando `~/.zshrc` por `~/.bashrc`.

**Cierra Claude Code y vuelve a abrirlo desde esa misma terminal**, o no la verá.
Para comprobar que está:

```bash
echo $ELEVENLABS_API_KEY        # tiene que salir tu clave
bash requisitos.sh --sin-musica # y aquí, la línea verde de ELEVENLABS_API_KEY
```

## 3 · La voz de tu marca

De fábrica viene una voz castellana del catálogo público. Para cambiarla:

1. En ElevenLabs → **Voices** → **Library**, escucha y elige (puedes filtrar por idioma).
2. Añádela a tu cuenta y copia su **Voice ID**.
3. Dísela a Claude: «la voz de mi marca es este id: …». Queda anotada en la skill de tu
   marca y ya se usa siempre.

A mano, si lo prefieres: `python3 ../../motor/toma.py <pieza> --voz <voice_id>`.

Con el plan de pago puedes **clonar tu propia voz** (te graba leyendo un rato) y usarla en
todos los vídeos. Es lo que hace que una cuenta suene a una persona y no a un locutor de
stock.

## 4 · Que la voz actúe · el modelo v3

Hay dos modelos y la diferencia se oye. `eleven_multilingual_v2` es un locutor correcto:
lee. **`eleven_v3` actúa**, y además le puedes dar acotaciones dentro del guion, **entre
corchetes**:

```
[curious] Esto es una carpeta. Le pegas la web de tu negocio...
[excited] y ya sabe cómo tienen que verse tus vídeos.
```

El modelo las interpreta y **no las dice**. Las que más se usan: `[curious]` para la
pregunta que abre, `[excited]` para el dato que sorprende, `[serious]` o `[confident]`
para el argumento, `[whispers]` antes de un giro, `[warm]` para el cierre. Ojo con
`[laughs]` y `[sighs]`: ésos **suenan de verdad** y ocupan tiempo.

Tres cosas que conviene saber:

- **Corchetes, no comillas ni paréntesis.** Los otros se leen en voz alta.
- **Una etiqueta por bloque**, no por frase, o la locución cambia de humor cada tres
  segundos.
- **Los dominios no se locutan.** Ningún modelo dice bien una web en inglés: se enseñan
  en pantalla. Claude ya lo sabe y te lo propondrá así.

No tienes que escribirlas tú: dile a Claude **cómo quieres que suene** («que empiece con
curiosidad y acabe cercano») y las pone él. Esto es lo que hay debajo.

## Si no quieres voz

No pasa nada: dilo y las piezas se entregan con **música y efectos**, que ya llevan el
ritmo. La voz se puede añadir cualquier día; el taller no se toca.
