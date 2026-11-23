# Pipeline técnico

## Archivos
```
estudio-moni/
  video/renderer.html      personajes (charSVG), estilos y renderizador de Shorts 1080x1920
  video/build_audio.py     VOICES, TTS (Kokoro), música (Karplus-Strong), efectos y Shorts
  video/render.js          render de Shorts
  largos/largos_data.py    plan de los videos largos (fuente de verdad)
  largos/build.py          genera largos.json (fechas, horarios, descripciones base)
  largos/guiones/NN.txt    guiones en formato de escenas
  largos/build_long.py     voz + música + efectos + timeline + .srt + descripción con capítulos reales
  largos/long.js           capa 16:9 que se inyecta sobre renderer.html (window.setupLong / frameLong)
  largos/motion.js         capa de movimiento: íconos por palabra clave, cámara viva, partículas, lluvia de monedas, barridos, palabras resaltadas, cameos
  largos/broll.js          b-roll animado: mapas con zoom (d3-geo + world-atlas), gráficos que suben/caen, dona de %, línea de tiempo de años, listas que se tildan, objetos que cruzan
  largos/render_long.js    render a MP4 (24 fps, 1920x1080, x264 crf 21, AAC con loudnorm −14 LUFS)
  largos/thumbs.js         miniaturas 1280x720
  largos/out/              audio, timeline, srt, mp4 y stills (no se versiona en git)
```

## Preparar el entorno (sesión nueva)
```bash
pip install kokoro-onnx soundfile numpy
mkdir -p /home/user/tts && cd /home/user/tts
curl -sSL -o kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -sSL -o voices-v1.0.bin  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```
- La ruta del modelo está fija en `video/build_audio.py` (`/home/user/tts/...`).
- Hugging Face y los servicios de voz online estaban bloqueados por la red. GitHub Releases y PyPI funcionan.
- Playwright y Chromium ya vienen instalados. ffmpeg también.

## Dependencias de npm (b-roll)
```bash
cd estudio-moni/largos && npm install   # d3-array, d3-geo, topojson-client, world-atlas (package.json)
```

## Comandos
```bash
cd estudio-moni/largos
python3 build.py                                   # después de tocar largos_data.py
python3 build_long.py 7                            # audio y timeline del video 7
node render_long.js --workers 1 --stills 1,40,120 7   # fotogramas de control en out/stills/
node render_long.js --workers 2 --out-motion 7 8   # render con movimiento y b-roll → out/mp4_motion/ (estándar actual)
# --no-motion / --no-broll desactivan capas; sin --out-motion escribe en out/mp4/
node thumbs.js 7                                   # miniatura
python3 zip_subida.py                              # zip de subida: descripción completa + .srt + miniatura por video
# Producción en lote: el render espera a que el audio de cada video esté listo
nohup python3 -u build_long.py $(seq 1 24) > out/audio.log 2>&1 &
nohup node render_long.js --watch --workers 2 > out/render.log 2>&1 &
nohup node render_long.js --watch --desc --workers 1 > out/render2.log 2>&1 &   # 3er worker desde el final, cuando termina el audio
```

Contador de palabras habladas (usar antes de generar el audio):
```bash
python3 -c "import build_long as B; m,it=B.parse('guiones/07.txt'); print(sum(len(i['text'].split()) for i in it if i['type']=='line'))"
```

## Parámetros (build_long.py)
`SPEED = 0.84` (narración más pausada que en los Shorts) · `GAP = 0.85` s entre líneas · `CARD = 2.6` s · `OUTRO = 20` s.
Música más baja bajo la voz (0,075) y más alta en las placas y la pantalla final (0,16).

## Tiempos de referencia (4 núcleos)
- TTS: entre 3 y 5 minutos por video de 8 minutos. Hay caché por línea en `video/out/tts_cache`, y si cambia la velocidad se regenera todo.
- Render: entre 20 y 30 minutos por video con un worker. Dos workers en paralelo con el TTS andan bien.

## Problemas conocidos y soluciones
- **Personajes oscuros o marrones**: había ids de gradiente duplicados entre instancias ocultas. `long.js` usa `charU()` para dar ids únicos. Si agregás instancias nuevas, usá `charU`.
- **Subtítulos cortados abajo**: con líneas de más de ~200 caracteres. `long.js` achica la letra y sube el subtítulo hasta que entra (desde la v2). Igual conviene que ninguna línea del guion pase de ~220 caracteres: mejor partirla en dos.
- **Verificación**: `bash verify.sh NN` muestra formato, duración, loudness y silencios, y arma una hoja de fotogramas en `out/check/NN.jpg`. Mirala siempre.
- **Duración corta**: casi siempre falta texto. Revisá con el contador, no con `wc`, porque las líneas `P:` no cuentan.
- **Emojis**: se ven con Noto Color Emoji. **Nunca uses 📅**: muestra “July 17” en inglés. Usá 🗓️.
- **Miniaturas**: no pongas nada abajo a la derecha, porque YouTube tapa esa zona con la duración.
- No se puede escuchar el audio en el entorno: siempre pedile al usuario que escuche una muestra.

## Capas de movimiento (estándar desde el video 1 aprobado)
- El usuario pidió **mucho movimiento**: algo nuevo en pantalla cada 2-5 s, ligado a lo que se dice.
- `motion.js`: diccionario `KW` (raíz sin tildes → emoji + etiqueta). Para sumar palabras, agregalas ahí. `STOP` evita falsos positivos (p. ej. “interesante” ≠ interés).
- `broll.js`: `COUNTRIES` (regex → id ISO numérico de world-atlas), `UP`/`DOWN` (verbos de suba/baja), `CROSS` (vehículos), `CAMEO` (palabra → personaje).
- Ritmo actual en el video 1: ~11 íconos por minuto + 1-2 widgets (mapa/gráfico) por minuto.
- Ayuda al guion: nombrar países, años, objetos concretos y verbos de suba/baja dispara b-roll automáticamente. Escribí pensando en lo que se va a ver.
- No hay fotos ni videos de stock: la red los bloquea y además tienen derechos. Todo es animación propia.
