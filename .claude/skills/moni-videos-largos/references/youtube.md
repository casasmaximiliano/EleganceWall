# Publicación en YouTube

## Calendario
- Videos largos: **miércoles 18:00** (historia o simulación) y **domingos 11:00** (guía práctica), hora de Argentina (UTC−3). Colombia −2 h, México −3 h, España +4 h.
- Shorts: lunes a viernes 13:00, 19:00 y 22:00. Sábados y domingos 12:00 y 21:00. La telenovela va a las 22:00 y sale un capítulo por día.
- El plan de los 24 primeros videos largos (del 25/11/2026 al 14/02/2027) está en `estudio-moni/largos/largos.json` y en la planilla `videos_largos.csv`.

## Configuración al subir un video largo
- Título del plan. Usá “Probar y comparar” con el título alternativo y una segunda miniatura.
- Descripción: la del campo `descripcion` de `out/timeline/NN.json`, que ya trae los capítulos con los tiempos reales. El primer capítulo arranca en 00:00, hay 3 o más y cada uno dura 10 s o más.
- Miniatura 1280×720 de `miniaturas/`. Requiere tener el canal verificado con el teléfono.
- Listas: Historias del dinero · Guías de finanzas personales · Simulaciones de Moni · Telenovela del dinero (películas).
- Público: **No es contenido creado para niños**. Restricción de edad: no. Promoción pagada: no, salvo que haya un auspicio.
- Contenido alterado o sintético: **No**, porque es animación claramente no realista. Marcar **Sí** si se usa una voz clonada de una persona real, aunque sea la del dueño del canal.
- Categoría: **Educación**. Idioma: Español (Latinoamérica).
- Subtítulos: subir el `.srt` de `out/srt/NN.srt`.
- Licencia estándar. Permitir insertar: sí. Publicar en el feed y notificar: sí. Permitir remezclas de Shorts: sí.
- Comentarios con moderación básica, ordenados por “Principales”. Responder durante la primera hora.
- Pantalla final: el video renderizado deja 20 s con dos recuadros vacíos (izquierda y derecha) y a Moni en el centro. Poner el video siguiente, una lista y el botón de suscripción.
- Anuncios (con el Programa de Socios): 8 minutos o más, en los cortes de capítulo, no más de uno cada 3 o 4 minutos.
- Programar la publicación con al menos un día de anticipación.
- Después de publicar: en cada Short relacionado (lista `shorts` del plan), ir a Detalles → “Video relacionado” y elegir este video.

## Instagram y TikTok
- Mismos videos verticales (Shorts). En TikTok, activar la etiqueta “Contenido generado por IA”.
- Bio de Instagram y TikTok, logo y portadas: `estudio-moni/marca/kit-de-marca.html`.
