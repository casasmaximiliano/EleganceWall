# Notas del proyecto (memoria para Claude)

Este repositorio tiene una app React (wallpapers) y, en `plan-shorts/`, el proyecto de un **canal infantil de shorts animados**. Conversar con el usuario en **español** (tuteo con «tú»).

## Canal infantil: decisiones tomadas
- **Nombre del canal:** **«Bombolín y sus amigos»** (español) y **«Bombolín & Friends»** (inglés). Son dos canales separados, uno por idioma, en YouTube, Instagram y TikTok.
- **Usuarios sugeridos:** @BombolinYSusAmigos y @BombolinAndFriends (sin tilde en el usuario; con tilde en el nombre visible).
- **Protagonista:** **Bombolín**, un dinosaurio bebé verde menta que usa medio cascarón con lunares azules como gorrito. Es curioso, risueño y valiente.
- **Amigos:** Toto (monstruito naranja del desorden, «¡Uy, uy, uy!»), Lula (nubecita que cambia de color con las emociones), Zumbi (abejita apurada, «¡Zzzí!») y Abu Tortu (abuela tortuga, narradora; en inglés, «Grandma Tortu»).
- **Rima del canal:** «¡Un, dos, tres, a descubrir otra vez!» / «One, two, three, come discover with me!».
- **Público:** niños de 3 a 8 años. En YouTube se marca como «contenido creado para niños». En Instagram y TikTok los textos se dirigen a las familias (son redes para mayores de 13).
- **Nombres descartados** porque ya están usados: El mundo de Pipo, Pipo's World y todo lo que contenga «Pipo» (existe el Capitán Pipo de El Reino Infantil), Cascarín/Cascarón y sus amigos, Dino Mimo/DinoMimi, todo lo que empiece con «Dino», Pompón, Tuti (TuTiTu), Dudú (Dudu Dada), Chimpún, Bumbú, Pumpi y todo lo que empiece con «Huevo» (Huevocartoon).
- **Ritmo (desde el 24/11/2026, decisión final):** **solo en español**, **un programa por día de 10 a 12 minutos**, 1920x1080 a **60 fps**, más **2 shorts por programa** (1080x1920, 60 fps). Los programas salen de lunes a viernes a las 17:00 y sábados y domingos a las 09:00; los shorts, a las 12:30 y 20:00. Del 24/11 al 31/12 son 38 programas. El canal en inglés quedó en pausa. Plan completo y calendario de historias: `plan-shorts/bombolin/plan-videos-largos.md`.
- **Estructura del programa:** gancho, presentación, historia nueva del día (unos 3 min), bloques de la biblioteca (¿Sabías qué?, canciones, juegos y cuentos cortitos, que rotan), «¡Otra aventura!» (la historia de ayer) y el Libro de Descubrimientos con «Mañana: …».
- **Avance de la producción:** la semana 1 (días 1 a 7, del 24 al 30/11) está producida. Los días 8 a 38 faltan: hay que escribir las historias nuevas (o alargar las existentes) en `episodios/` y sumarlas a `EPISODES`, `EXTRA` y `SHORTS`.
- **Episodios autoconclusivos con un hilo suave:** el Libro de Descubrimientos (una figurita por episodio) y el anticipo del próximo. Bloques fijos en cada episodio: «¿Sabías qué?» o un cuento, «¡Hora de cantar!» y «¡Hora de jugar!».
- **YouTube «para niños» no permite la prueba A/B de miniaturas:** se hacen 3 miniaturas por video y se rotan a mano cada 3 días según el porcentaje de clics (CTR).
- El plan anterior de 90 shorts (3 por día) quedó como biblioteca: sus canciones, juegos y explicaciones se reutilizan dentro de los episodios.

## Dónde está cada cosa (`plan-shorts/bombolin/`)
- `src/data_a.py`, `data_bc.py`, `data_def.py`: los 90 guiones en español (formatos A a F). `src/data_en.py`: los diálogos en inglés.
- `src/build.py`: genera `calendario.csv/.md` y `semana-1..5.md`.
- `video/render.py`: genera los videos (`--lang es|en`). `video/characters.py`: dibuja a los personajes. `video/package.py`: arma los zips por semana con PUBLICAR.csv y un .txt por video.
- `branding/branding.py`: logo, banners de YouTube, marca de agua y portadas de historias destacadas de Instagram (tipografía Fredoka, licencia OFL, en `branding/fonts`). `branding/horarios.py`: horarios día por día por plataforma (por defecto empieza el lunes 2026-11-30).
- `canal.md`: nombre, descripciones de YouTube, Instagram y TikTok, y ajustes de cada red. `voces.md`: la voz de cada personaje.
- `plan-shorts/moni-plan-12-shorts.md`: el plan viejo de «Moni» (ahorro), ya descartado.

- `episodios/`: la temporada 1 de videos largos. `eps_*.py` son los guiones ES/EN, `episode.py` genera los episodios 1920x1080 con `.srt` y los shorts verticales, `thumbs.py` las miniaturas y `package_long.py` las recopilaciones, los textos de publicación y los zips por semana.

## Cómo regenerar
- Voces: Piper TTS (`pip install piper-tts`), con los modelos `es_MX-claude-high`, `es_MX-ald-medium`, `es_AR-daniela-high`, `en_US-amy-medium`, `en_US-ryan-high` y `en_US-hfc_female-medium`, que se descargan de huggingface.co/rhasspy/piper-voices (el entorno ya tiene permitido huggingface.co y su CDN).
- `python3 video/render.py --voices DIR --out DIR [--lang en] [--only ID,...] --jobs 4` y después `python3 video/package.py VIDEOS ZIPS [en]`.
- El coro («Todos») sale de una sola locución base con el tono cambiado para cada personaje, para que las voces vayan sincronizadas. No volver a generar una locución por personaje.
- Programas diarios: `python3 episodios/programa.py --voices DIR --out DIR --dias 1,2,3 --jobs 4`; después `python3 episodios/package_prog.py VIDEOS MINIS ZIPS 1,2,3`.
- Videos largos (formato anterior, de 3 min): `python3 episodios/episode.py --voices DIR --out DIR --lang es|en --jobs 4`; después `python3 episodios/thumbs.py MINIS` y `python3 episodios/package_long.py VIDEOS MINIS ZIPS es|en`.
- Los videos y zips generados no se suben a git (`descargas/` está en `.gitignore`).
