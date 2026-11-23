# EleganceWall · Estudio Moni Finanzas

Este repo contiene la producción del canal animado de finanzas **Moni Finanzas** (@moni.finanzas), en `estudio-moni/`.
El resto del repo (`src/`, `public/`) es una app de Create React App sin relación con el canal.

- Videos largos: usar la skill `.claude/skills/moni-videos-largos/`. Tiene la marca, los personajes, el formato de guion, el pipeline y la configuración de YouTube.
- Shorts verticales: `estudio-moni/video/` (`build_audio.py` + `render.js`), con los datos de `estudio-moni/shorts_data.py` y `shorts_pantalla.py`.
- Calendario de Shorts: `estudio-moni/calendario.py`. Plan de largos: `estudio-moni/largos/largos_data.py`.
- Kit de marca: `estudio-moni/marca/`.
- Los renders (`*/out/`) no se versionan: son pesados y se regeneran con los scripts.
- Idioma del canal: español rioplatense con voseo. Montos en dólares. Cada dato numérico se verifica con Python y lleva su fuente.
- Continuidad: Centavito es primo de Moni. Peso es su pareja.
