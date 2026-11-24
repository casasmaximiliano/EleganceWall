"""Arma recopilaciones, textos de publicación y zips por semana (videos largos + shorts).

Uso: python3 package_long.py CARPETA_VIDEOS CARPETA_MINIATURAS CARPETA_ZIPS es|en
"""
import csv
import datetime as dt
import glob
import io
import json
import os
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from episode import EPISODES, EXTRAS, srt_time, wrap2  # noqa: E402
from thumbs import COMPS  # noqa: E402

vids, thumbs, out, lang = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
EN = lang == "en"
TAG = "EN" if EN else "ES"
os.makedirs(out, exist_ok=True)
D = dt.date

# ------------------------------------------------------------------ calendario
EP_DATES = {1: (D(2026, 11, 24), "18:00"), 2: (D(2026, 11, 24), "18:10"), 3: (D(2026, 11, 24), "18:20"),
            4: (D(2026, 11, 27), "17:00"), 5: (D(2026, 12, 1), "17:00"), 6: (D(2026, 12, 4), "17:00"),
            7: (D(2026, 12, 8), "17:00"), 8: (D(2026, 12, 11), "17:00"), 9: (D(2026, 12, 15), "17:00"),
            10: (D(2026, 12, 18), "17:00"), 11: (D(2026, 12, 22), "17:00"), 12: (D(2026, 12, 25), "17:00"),
            13: (D(2026, 12, 29), "17:00")}
COMP_DATES = {"C1": (D(2026, 11, 29), "09:00"), "C2": (D(2026, 12, 6), "09:00"), "C3": (D(2026, 12, 13), "09:00"),
              "C4": (D(2026, 12, 20), "09:00"), "C5": (D(2026, 12, 27), "09:00"), "C6": (D(2026, 12, 31), "10:00")}
# shorts: uno por día a las 12:30, a partir del día siguiente a su episodio
SHORT_DATES, used = {}, set()
for n in sorted(EPISODES):
    for k in range(len(EPISODES[n]["shorts"])):
        d = EP_DATES[n][0] + dt.timedelta(days=1)
        while d in used:
            d += dt.timedelta(days=1)
        used.add(d)
        SHORT_DATES[(n, k)] = (d, "12:30")
WEEKS = [("Semana1_24-29nov", D(2026, 11, 24), D(2026, 11, 29)), ("Semana2_30nov-6dic", D(2026, 11, 30), D(2026, 12, 6)),
         ("Semana3_7-13dic", D(2026, 12, 7), D(2026, 12, 13)), ("Semana4_14-20dic", D(2026, 12, 14), D(2026, 12, 20)),
         ("Semana5_21-27dic", D(2026, 12, 21), D(2026, 12, 27)), ("Semana6_28-31dic", D(2026, 12, 28), D(2027, 1, 3))]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

SHOW = "Bombolín & Friends" if EN else "Bombolín y sus amigos"
SUFFIX = "Cartoons for Kids" if EN else "Dibujos animados para niños"
CATEGORY = "Film & Animation (Cine y animación)" if EN else "Cine y animación"
BASE_TAGS_ES = ["Bombolín", "Bombolín y sus amigos", "dibujos animados", "dibujos animados para niños", "caricaturas",
                "videos para niños", "cuentos infantiles", "episodios completos", "dinosaurio", "animales para niños",
                "aprender jugando", "canciones infantiles", "preescolar", "niños de 3 a 8 años"]
BASE_TAGS_EN = ["Bombolín", "Bombolín and Friends", "cartoons for kids", "kids cartoon", "kids shows", "full episodes",
                "preschool", "toddler videos", "baby dinosaur", "animals for kids", "learning for kids", "kids songs",
                "stories for kids", "ages 3 to 8"]


def fmt_t(s):
    s = int(s)
    return f"{s // 60}:{s % 60:02d}" if s < 3600 else f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def ep_file(n):
    return [p for p in glob.glob(os.path.join(vids, f"Bombolin_E{n:02d}_*_{TAG}.mp4")) if "_Short" not in p][0]


def ep_meta(n):
    return json.load(open(ep_file(n)[:-4] + ".json"))


def tags_for(extra):
    base = BASE_TAGS_EN if EN else BASE_TAGS_ES
    tags, total = [], 0
    for t in extra + base:
        if t not in tags and total + len(t) + 2 < 480:
            tags.append(t)
            total += len(t) + 2
    return ", ".join(tags)


def settings_txt():
    if EN:
        return ("SETTINGS: Audience: Yes, it's made for kids · Altered/synthetic content: No (animated cartoon) · "
                "Category: Film & Animation · Video language: English · Captions: upload the .srt file · "
                "License: Standard YouTube License · Paid promotion: No · Comments: disabled automatically (made for kids)")
    return ("CONFIGURACIÓN: Audiencia: Sí, es contenido creado para niños · Contenido alterado o sintético: No (dibujo animado) · "
            "Categoría: Cine y animación · Idioma del video: Español (Latinoamérica) · Subtítulos: subir el archivo .srt · "
            "Licencia: Licencia estándar de YouTube · Promoción pagada: No · Comentarios: se desactivan solos (contenido para niños)")


rows = []

# ------------------------------------------------------------------ episodios
for n, ep in EPISODES.items():
    m = ep_meta(n)
    title = f"{ep['ten'] if EN else ep['tes']} | {SHOW} | {SUFFIX}"
    mini, song, game = EXTRAS[n]
    if EN:
        desc = (f"{ep['sum_en']}\n\nIn this episode:\n🦕 A brand-new story with Bombolín and his friends\n"
                f"🎵 A song to sing along\n🎲 A \"Myth or truth?\" game with a countdown\n💡 A real fact: {ep['dato_en']}\n\n"
                f"Today we learned that {ep['len']}!\n\n{SHOW} is a cartoon for kids ages 3 to 8: short stories, songs, games "
                f"and real facts about animals, dinosaurs and nature. New episodes every Tuesday and Friday!\n\n"
                f"Source of the fact: {ep['fuente']}\n\n#Bombolin #CartoonsForKids #KidsShows")
    else:
        desc = (f"{ep['sum_es']}\n\nEn este episodio:\n🦕 Una historia nueva de Bombolín y sus amigos\n"
                f"🎵 Una canción para cantar juntos\n🎲 Un juego de «¿Mito o verdad?» con cuenta regresiva\n💡 Un dato real: {ep['dato_es']}\n\n"
                f"¡Hoy aprendimos que {ep['les']}!\n\n{SHOW} es un dibujo animado para niños de 3 a 8 años: historias cortas, "
                f"canciones, juegos y datos reales sobre animales, dinosaurios y la naturaleza. ¡Episodios nuevos todos los martes y viernes!\n\n"
                f"Fuente del dato: {ep['fuente']}\n\n#Bombolin #DibujosAnimados #VideosParaNiños")
    extra_tags = ([ep["ten"], ep["thumb"]["t1_en"].strip("!?¡¿ ").lower()] if EN else [ep["tes"], ep["thumb"]["t1_es"].strip("!?¡¿ ").lower()])
    d, h = EP_DATES[n]
    rows.append(dict(fecha=d, hora=h, tipo="Episodio" if not EN else "Episode", archivo=os.path.basename(ep_file(n)),
                     srt=os.path.basename(ep_file(n))[:-4] + ".srt", duracion=fmt_t(m["duration"]), titulo=title,
                     descripcion=desc, etiquetas=tags_for(extra_tags),
                     playlist=("Season 1 – Full Episodes" if EN else "Temporada 1 – Episodios completos"),
                     miniaturas=" / ".join(f"E{n:02d}_{TAG}_miniatura{k}.jpg" for k in (1, 2, 3)),
                     paths=[ep_file(n), ep_file(n)[:-4] + ".srt"] + [os.path.join(thumbs, f"E{n:02d}_{TAG}_miniatura{k}.jpg") for k in (1, 2, 3)]))

# ------------------------------------------------------------------ recopilaciones (concat sin recodificar)
for cid, eps in COMPS:
    name = f"Bombolin_{cid}_Recopilacion_E{eps[0]:02d}-E{eps[-1]:02d}_{TAG}"
    mp4 = os.path.join(vids, name + ".mp4")
    lst = os.path.join(vids, name + ".txt")
    open(lst, "w").write("".join(f"file '{ep_file(n)}'\n" for n in eps))
    if not os.path.exists(mp4):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                        "-movflags", "+faststart", mp4], check=True)
    os.remove(lst)
    off, chapters, srt, idx = 0.0, [], [], 1
    for n in eps:
        m = ep_meta(n)
        chapters.append(f"{fmt_t(off)} {EPISODES[n]['ten'] if EN else EPISODES[n]['tes']}")
        for (t0, du, text) in m["srt"]:
            srt.append(f"{idx}\n{srt_time(off + t0)} --> {srt_time(off + t0 + du + 0.2)}\n{wrap2(text)}\n")
            idx += 1
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    ep_file(n)], capture_output=True, text=True).stdout)
        off += dur
    open(mp4[:-4] + ".srt", "w", encoding="utf-8").write("\n".join(srt))
    if cid == "C6":
        t_es, t_en = "¡Temporada 1 completa! Todos los episodios", "Full Season 1! All Episodes"
    elif cid in ("C4", "C5"):
        t_es, t_en = f"Especial Navidad: episodios {eps[0]} al {eps[-1]}", f"Christmas Special: Episodes {eps[0]}–{eps[-1]}"
    else:
        t_es, t_en = f"Episodios {eps[0]} al {eps[-1]}", f"Episodes {eps[0]}–{eps[-1]}"
    title = f"{t_en if EN else t_es} ({fmt_t(off).split(':')[0]} min) | {SHOW} | {SUFFIX}" if off < 3600 else \
        f"{t_en if EN else t_es} | {SHOW} | {SUFFIX}"
    chap = "\n".join(chapters)
    if EN:
        desc = (f"{len(eps)} full episodes of {SHOW} in a row: stories, songs and games for kids ages 3 to 8.\n\n"
                f"Episodes:\n{chap}\n\nNew episodes every Tuesday and Friday!\n\n#Bombolin #CartoonsForKids #FullEpisodes")
    else:
        desc = (f"{len(eps)} episodios completos de {SHOW}, uno detrás del otro: historias, canciones y juegos para niños de 3 a 8 años.\n\n"
                f"Episodios:\n{chap}\n\n¡Episodios nuevos todos los martes y viernes!\n\n#Bombolin #DibujosAnimados #EpisodiosCompletos")
    d, h = COMP_DATES[cid]
    rows.append(dict(fecha=d, hora=h, tipo="Compilation" if EN else "Recopilación", archivo=os.path.basename(mp4),
                     srt=os.path.basename(mp4)[:-4] + ".srt", duracion=fmt_t(off), titulo=title, descripcion=desc,
                     etiquetas=tags_for(["full episodes compilation", "1 hour cartoons" if cid == "C6" else "cartoon marathon"]
                                        if EN else ["recopilación", "1 hora de dibujos" if cid == "C6" else "maratón de dibujos"]),
                     playlist=("Compilations" if EN else "Recopilaciones"),
                     miniaturas=" / ".join(f"{cid}_{TAG}_miniatura{k}.jpg" for k in (1, 2, 3)),
                     paths=[mp4, mp4[:-4] + ".srt"] + [os.path.join(thumbs, f"{cid}_{TAG}_miniatura{k}.jpg") for k in (1, 2, 3)]))

# ------------------------------------------------------------------ shorts
for n, ep in EPISODES.items():
    for k, sh in enumerate(ep["shorts"]):
        f = os.path.join(vids, f"Bombolin_E{n:02d}_Short{k + 1}_{TAG}.mp4")
        hook = sh[3] if EN else sh[2]
        hook_t = hook.capitalize() if hook.isupper() else hook
        title = f"{hook_t} {ep['thumb']['em']} | {SHOW} #Shorts"
        if EN:
            desc = (f"A moment from the episode \"{ep['ten']}\". Watch the full episode on the channel!\n\n"
                    f"#Bombolin #KidsCartoon #Shorts")
        else:
            desc = (f"Un momento del episodio «{ep['tes']}». ¡Mira el episodio completo en el canal!\n\n"
                    f"#Bombolin #DibujosAnimados #Shorts")
        d, h = SHORT_DATES[(n, k)]
        rows.append(dict(fecha=d, hora=h, tipo="Short", archivo=os.path.basename(f), srt="", duracion="",
                         titulo=title, descripcion=desc, etiquetas=tags_for([]), playlist="Shorts",
                         miniaturas="(se elige un fotograma dentro de YouTube)" if not EN else "(pick a frame in YouTube)",
                         paths=[f]))

rows.sort(key=lambda r: (r["fecha"], r["hora"]))

LEEME = ("BOMBOLÍN — VIDEOS LARGOS ({idioma})\n=================================\n\n"
         "Cada carpeta de semana trae:\n"
         "  · Los episodios (horizontales, 1920x1080) con su archivo de subtítulos .srt.\n"
         "  · Las recopilaciones del domingo.\n"
         "  · Los shorts verticales que salen de cada episodio.\n"
         "  · 3 miniaturas por video largo (miniatura1, 2 y 3).\n"
         "  · Un .txt por video con título, descripción, etiquetas, categoría, playlist, fecha, hora y configuración.\n"
         "  · PUBLICAR.csv con todo junto (se abre con Excel o Google Sheets).\n\n"
         "MINIATURAS: YouTube no permite «Probar y comparar» en videos para niños. Sube la miniatura1;\n"
         "a los 3 días, si el video tiene menos vistas o menos porcentaje de clics que tus otros videos, cámbiala por la miniatura2;\n"
         "a los 3 días más, prueba la miniatura3. Quédate con la que mejor funcionó (YouTube Studio > Estadísticas > Alcance).\n\n"
         "Horarios: {zona}.\n")

for wname, d0, d1 in WEEKS:
    wk = [r for r in rows if d0 <= r["fecha"] <= d1]
    if not wk:
        continue
    zp = os.path.join(out, f"Bombolin_Largos_{TAG}_{wname}.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
        z.writestr("LEEME.txt", LEEME.format(idioma="inglés" if EN else "español",
                                             zona="hora del este de EE. UU. (ET)" if EN else "hora local del país principal del canal"))
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["fecha", "dia", "hora", "tipo", "archivo", "duracion", "titulo", "descripcion", "etiquetas",
                    "categoria", "playlist", "miniaturas", "subtitulos", "audiencia"])
        for r in wk:
            for p in r["paths"]:
                if os.path.exists(p):
                    z.write(p, os.path.basename(p))
            txt = (f"PUBLICAR: {DIAS[r['fecha'].weekday()]} {r['fecha'].isoformat()} a las {r['hora']}\nTIPO: {r['tipo']}\n"
                   f"ARCHIVO: {r['archivo']}\n" + (f"DURACIÓN: {r['duracion']}\n" if r["duracion"] else "") +
                   f"\nTÍTULO:\n{r['titulo']}\n\nDESCRIPCIÓN:\n{r['descripcion']}\n\nETIQUETAS:\n{r['etiquetas']}\n\n"
                   f"CATEGORÍA: {CATEGORY}\nPLAYLIST: {r['playlist']}\nMINIATURAS: {r['miniaturas']}\n"
                   + (f"SUBTÍTULOS: {r['srt']}\n" if r["srt"] else "") + f"\n{settings_txt()}\n")
            z.writestr(r["archivo"][:-4] + ".txt", txt)
            w.writerow([r["fecha"].isoformat(), DIAS[r["fecha"].weekday()], r["hora"], r["tipo"], r["archivo"], r["duracion"],
                        r["titulo"], r["descripcion"], r["etiquetas"], CATEGORY, r["playlist"], r["miniaturas"], r["srt"],
                        "Made for kids" if EN else "Creado para niños"])
        z.writestr("PUBLICAR.csv", "\ufeff" + buf.getvalue())
    print(zp, round(os.path.getsize(zp) / 1e6, 1), "MB", len(wk), "videos")

# calendario general (para el plan)
with open(os.path.join(out, f"calendario_largos_{TAG}.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["fecha", "dia", "hora", "tipo", "titulo", "duracion"])
    for r in rows:
        w.writerow([r["fecha"].isoformat(), DIAS[r["fecha"].weekday()], r["hora"], r["tipo"], r["titulo"], r["duracion"]])
