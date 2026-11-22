# Generador de videos de «Bombolín y sus amigos»

Convierte los 90 guiones (`../src/data_*.py`) en shorts verticales 1080x1920 con voces, música, efectos y subtítulos palabra por palabra.

| Archivo | Qué hace |
|---|---|
| `characters.py` | Dibuja los personajes originales: Bombolín, Toto, Lula, Zumbi y Abu Tortu, con boca abierta o cerrada, parpadeo y los estados de ánimo de Lula |
| `render.py` | Arma cada short: voces, música, efectos, escenarios, emojis de animales y objetos, cuenta regresiva, rebobinado, cámara y subtítulos |
| `package.py` | Crea un zip por semana con los videos, `PUBLICAR.csv` y un `.txt` por video |

## Requisitos
- `ffmpeg`, Python 3 con `numpy` y `Pillow`, y `pip install piper-tts`.
- Voces de Piper (descargar de huggingface.co/rhasspy/piper-voices): `es_MX-claude-high`, `es_MX-ald-medium` y `es_AR-daniela-high`.
- La fuente Noto Color Emoji (`/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf`).

## Uso
```bash
python3 render.py --voices DIR_VOCES --out DIR_VIDEOS --jobs 4            # los 90
python3 render.py --voices DIR_VOCES --out DIR_VIDEOS --only A1-1,F03      # algunos
python3 package.py DIR_VIDEOS DIR_ZIPS
```

## Voces (tono y velocidad sobre Piper)
| Personaje | Modelo | Tono | Velocidad |
|---|---|---|---|
| Bombolín | es_AR-daniela-high | ×1,30 | normal |
| Toto | es_MX-ald-medium | ×0,86 | más lento |
| Lula | es_MX-claude-high | ×1,20 | un poco más lento |
| Zumbi | es_AR-daniela-high | ×1,45 | rápido |
| Abu Tortu | es_MX-claude-high | ×0,93 | lento |
| Todos | coro de Bombolín, Toto, Lula y Zumbi | | |

Son voces sintéticas: suenan más robóticas que una voz de IA comercial o un actor. Para mejorar la calidad, se puede regrabar cada personaje con las descripciones de `../voces.md` y volver a generar los videos.
