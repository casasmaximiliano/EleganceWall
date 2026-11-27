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
- **Entrega al teléfono**: los MP4 de ~100 MB no se pueden bajar desde la app; hasta ~60 MB sí. Antes de mandarlos, comprimí a `out/mp4_movil/` (≈45 MB, misma calidad visual):
  `ffmpeg -i out/mp4_motion/NN.mp4 -c:v libx264 -preset slow -tune animation -crf 27 -maxrate 1200k -bufsize 2400k -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/mp4_movil/NN.mp4`

## Capas de movimiento (estándar desde el video 1 aprobado)
- El usuario pidió **mucho movimiento**: algo nuevo en pantalla cada 2-5 s, ligado a lo que se dice.
- `motion.js`: diccionario `KW` (raíz sin tildes → emoji + etiqueta). Para sumar palabras, agregalas ahí. `STOP` evita falsos positivos (p. ej. “interesante” ≠ interés).
- `broll.js`: `COUNTRIES` (regex → id ISO numérico de world-atlas), `UP`/`DOWN` (verbos de suba/baja), `CROSS` (vehículos), `CAMEO` (palabra → personaje).
- Ritmo actual en el video 1: ~11 íconos por minuto + 1-2 widgets (mapa/gráfico) por minuto.
- Ayuda al guion: nombrar países, años, objetos concretos y verbos de suba/baja dispara b-roll automáticamente. Escribí pensando en lo que se va a ver.
- No hay fotos ni videos de stock: la red los bloquea y además tienen derechos. Todo es animación propia.

## Lo que aprendimos con los primeros datos (noviembre 2026) — aplicar siempre
- **Datos de los primeros 9 Shorts**: la sitcom (2 personajes, living cálido, objeto + precio) retuvo 52 % "se quedaron a mirar" contra 19-24 % de Moni sola con un cartel sobre fondo oscuro. Lo que falla es el primer segundo, no el contenido.
- **Shorts**: 2 personajes desde el primer cuadro (`build_audio.py`: `SIDEKICK` si el guion no tiene un segundo personaje), zoom de entrada, aviso legal solo al final, sin "Cap. N"/"Ep. N" (cada short se entiende solo), telenovela en escena cálida.
- **Videos largos**:
  - Arranque en frío: el primer capítulo no tiene placa (`build_long.py`). La primera línea es el gancho con número sorpresa.
  - Nunca Moni sola: `SIDEKICK` en `build_long.py` agrega un compañero por video (Peso en pareja, Infla en inflación, Capricho en trampas, Tarjetín en tarjeta, Centavito por defecto) que reacciona a números y preguntas.
  - Fondos variados: `ROOMS` elige por capítulo cocina, oficina, súper, banco, calle, parque o living según de qué se habla, sin repetir dos seguidos (CSS en `long.js`, clases `r-*`).
  - Si el título del capítulo ya trae número (Paso 1, Episodio 2, Trampa 3), la placa no dice "Capítulo N".
  - Carteles con número: el número grande en el cartel y el rubro abajo en chico (`P: $40 → $10 | suscripciones`), si no se corta feo.
  - Mejor que reescribir: en las simulaciones, un personaje que reaccione en cada etapa (ver guion 21 con Cafecito).
- **Orden de publicación**: `ORDEN` en `build.py` (el número de video es un identificador fijo; las fechas salen del orden). Primero temas cotidianos e historias; guías después; las de temporada (diciembre, plan anual, San Valentín) en su fecha.
- **Miniaturas**: 3 por video (`THUMBS_BC` en `largos_data.py`, `thumbs.js` genera `_B` y `_C`) para "Probar y comparar" de YouTube (solo videos largos, desde la computadora, con funciones avanzadas activadas). Usar espacio no separable (` `) entre número y % para que no se corte.
- **Calendario**: `calendario.py` arma 4 shorts por día (10, 13, 19 y 22 h de Argentina) con grupos A (gastos), B (deudas/inflación/ahorro) y exploración. `calendario_artifact.py` genera `cal_art/plan.json` para el artefacto "Calendario Moni Finanzas" (https://claude.ai/artifact/SPLppXuGb86ztkgUvsncoA): por día, video del short (asset subido), título, descripción, etiquetas, categoría, lista, video relacionado (el largo del tema ya publicado), comentario fijado y check de subido (db `subidos`).
- **Entrega**: el usuario descarga en la compu; mandar los MP4 en calidad original (`out/mp4_motion`) y el zip de `zip_subida.py` (descripción, subtítulos y miniaturas A/B/C por video).

## Mundo 3D (estilo nuevo de los largos, desde noviembre 2026)

Carpeta `estudio-moni/mundo3d/`. Usa el mismo audio y timeline de `build_long.py`; solo cambia la imagen.

- `core.js` (toon + contornos, cara con expresiones, brazos y piernas), `personajes.js` (Moni, Centavito, Tarjetín, Cafecito, Delivy, zombis, Infla y extras), `props.js` (celular, cuaderno, resumen, calendario, alcancía, pizarrón; `M3.insert()` para planos de detalle), `lugares.js` (depto, calle, cafeteria, banco: spots con altura de asiento y cámaras con nombre), `director.js` (planos, gestos por palabras, el que escucha mira y asiente, subtítulos de 2-4 palabras).
- Guion de planos: `planos/NN.js` → `{índiceDeEscena: [[fracciónFin, plano], ...]}`. Un plano lleva `loc`, `cam` (nombre o `'close:<kind>'` con `camOpt {angle, dist, fov}`), `cast {kind: spot}`, y opcionales `insert`, `title`, `gesture`, `enter`, `push`, `propSet`.
- Pruebas: `node render3d.js NN --stills 120,300` → `largos/out/stills3d/`. Revisá siempre: personajes tapados, gente flotando o en el piso, árboles/faroles delante de la cámara, texto cortado en cuadernos (máx. ~26 letras por renglón).
- Render: `node render3d.js NN --workers 3 --out ../largos/out/mp4_3d/NN_3d.mp4` (~1 fps por worker: 8 min de video ≈ 70-80 min).
- Miniaturas 3D: `node thumb3d.js NN` (variantes A/B/C configuradas dentro del script) → `largos/miniaturas/miniatura_NN_3D_X.png`; reescalar a 1280×720.
- Trabajo semanal: guiones listos con anticipación, pero el 3D se arma y renderiza por semana, corrigiendo con stills.

### Mundo 3D · reglas de calidad (27/11/2026)

- **Datos en pantalla:** los `insert` de `cuaderno` y `resumen` ya no cortan a la mesa. `render3d.js` los convierte en un panel que entra por la derecha encima del último plano con personajes, con los renglones apareciendo de a uno, y corre la escena a la izquierda (`setViewOffset`). El celular, la alcancía y el calendario siguen como planos de detalle. `--sin-paneles` vuelve al comportamiento viejo.
- **Primeros planos:** `close:<kind>` prueba ángulos y distancias y elige uno sin árboles o faroles delante y sin otro personaje cortado por el borde (o lo deja entero, o lo saca). `camOpt.fixed: true` fuerza el ángulo pedido. `DBG=1` imprime el puntaje.
- **Calle:** la gente camina sobre la vereda (alto .3) y pasa por detrás de los personajes. Los autos van por los carriles z 1,0 y 3,1; la mitad del fondo es para estacionar. Autito usa el spot `cordon` (en la calle) con Moni en `veredaAuto`, cámara `autoTwo`.
- **Lugares nuevos:** `videoclub` (spots `pasillo`, `mostrador` para Centavito arriba del mostrador, `junto`; cámaras `two`, `wide`, `est`, `estantes`, `tele`) y `sala` de reuniones (cámaras `mesa`, `risa`, `fundadores`, `atril`; `fx: {laugh: 1}` hace reír a los ejecutivos).
- **Cámara a medida:** `cam` también acepta un objeto `{p, look, fov}`.
- **Short vertical en 3D:** `node render3d.js NN --short` usa `video/out/timeline/NNN.json`, `video/out/audio/NNN.wav` y `planos/short_NNN.js`, a 1080×1920. Muestra el `panel.big` de cada frase arriba y el aviso legal al final. En vertical, primeros planos con `dist` ≈ 8,6 y `fov` 44.
- **Guiones largos:** que Moni nunca esté sola: un compañero que pregunta lo que pensaría el espectador (Centavito no conoce un videoclub, etc.). Gancho con el número en la primera frase y un "quedate hasta el final porque…" que se paga en el último tercio.

### Lo que dicen los datos de Shorts (25-27/11/2026)

| Short | Duración | Se quedaron | % visto | Me gusta | Suscriptores |
| --- | --- | --- | --- | --- | --- |
| Gasté $20 más para ahorrarme $5 de envío | 13 s | 61,8 % | 106,9 % | 26 | 0 |
| Por qué todo cuesta $9,99 | 18 s | 56,3 % | 74,4 % | 14 | 2 |
| Si tenés una acción de Coca-Cola | 22 s | 41,3 % | 59 % | 11 | 0 |
| La suscripción que vive en mi sillón | 12 s | 33,6 % | 97 % | 7 | 0 |

- Lo que decide si se quedan es el primer cuadro y el título: un número concreto y un conflicto en primera persona ("Gasté $20 más…"). "DESDE MARZO" como primer cartel no engancha.
- Los de 12-14 s se ven enteros o se repiten; los de 20 s o más pierden la mitad. Apuntar a 12-16 s.
- Casi todo el tráfico es el feed de Shorts (98-99 %): la búsqueda no trae nada todavía.
- Títulos reescritos con este criterio en `calendario.py` (`TITULO_NUEVO`).
