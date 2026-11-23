---
name: moni-videos-largos
description: Producir videos largos (8-12 min, 16:9) del canal Moni Finanzas con los mismos personajes, voces, música y estilo que los Shorts. Usar cuando haya que planificar, escribir guiones, generar voz, renderizar, hacer miniaturas o preparar la subida de videos largos de Moni Finanzas (@moni.finanzas).
---

# Videos largos de Moni Finanzas

Canal de educación financiera animado, en español rioplatense (voseo), dirigido a Latinoamérica.
Protagonista: **Moni**, una moneda dorada con un brote verde. Frase: “Plata que duerme, plata que pierde.”
Todo el código vive en el repo `casasmaximiliano/EleganceWall`, carpeta `estudio-moni/`.

Antes de empezar, leé según lo que vayas a hacer:
- `references/canal.md`: marca, personajes y reglas de continuidad.
- `references/guiones.md`: formato del guion y reglas de escritura.
- `references/youtube.md`: horarios, configuración de subida y descripción.
- `references/pipeline.md`: preparación del entorno, comandos, tiempos y problemas conocidos.

## Flujo completo (resumen)

1. **Plan**: elegí el tema y el tipo. Los miércoles a las 18:00 (hora de Argentina) va una historia o simulación entretenida. Los domingos a las 11:00, una guía práctica de las que se buscan. Cargalo en `estudio-moni/largos/largos_data.py`: título, título alternativo, miniatura, gancho, capítulos, Shorts relacionados, fuentes y etiquetas. Después corré `python3 build.py`.
2. **Guion**: escribí `estudio-moni/largos/guiones/NN.txt` con el formato de `references/guiones.md`. Tienen que ser **1.230 palabras habladas o más**, que dan unos 8 minutos y habilitan anuncios a mitad del video. Medilo con el contador de `references/pipeline.md`. Verificá cada número con Python antes de escribirlo.
3. **Audio**: `python3 build_long.py NN` genera voces, música, efectos, la línea de tiempo, el `.srt` y la descripción con los capítulos reales.
4. **Revisión visual**: `node render_long.js --workers 1 --stills 1,30,90,200 NN` y mirá los fotogramas en `out/stills/`.
5. **Render**: `node render_long.js --workers 2 --out-motion NN` genera el MP4 1920×1080 a 24 fps (−14 LUFS) con las capas de movimiento y b-roll (`motion.js`, `broll.js`) en `out/mp4_motion/`. Es el estándar: el usuario quiere movimiento constante ligado a lo que se dice.
6. **Miniatura**: `node thumbs.js NN` genera `miniaturas/miniatura_NN.png` en 1280×720.
7. **Entrega**: MP4, miniatura, `.srt` y la descripción final (está en `out/timeline/NN.json`, campo `descripcion`). Avisá al usuario que **escuche** el resultado: el TTS puede pronunciar mal alguna palabra y desde el entorno no se puede escuchar.

## Reglas que no se negocian

- Mismos personajes, voces y estilo visual (3D suave). No cambiar colores ni voces sin pedido explícito.
- Movimiento constante: íconos, cámara viva, mapas, gráficos, línea de tiempo y cameos (ver `pipeline.md`). Nunca más de ~5 s sin que aparezca algo nuevo.
- Cada dato numérico se calcula y se aclaran los supuestos en pantalla o en la voz (“ejemplo ilustrativo”).
- Fuentes reales en la descripción. Nada de cifras virales sin fuente: si una cifra famosa es un mito, se dice.
- Al final de cada video va “Contenido educativo. No es asesoramiento financiero.” El renderizador lo agrega solo.
- Contenido original: guion propio, investigación, al menos un 60 % de material nuevo si se reutilizan Shorts. Así se evita la política de “contenido no auténtico” de YouTube.
- Sin política partidaria ni recomendaciones de instrumentos puntuales. Se enseña a pensar, no qué comprar.
- Continuidad: Centavito es **primo** de Moni. Peso es su **pareja**. Tarjetín es el villano de la temporada 1 e Infla el de la 2. Ver `references/canal.md`.
