"""Empaqueta los programas diarios: un zip por día con el programa, sus subtítulos, 3 miniaturas,
2 shorts y los textos de publicación (título, descripción, etiquetas, categoría, horario y configuración).

Uso: python3 package_prog.py CARPETA_VIDEOS CARPETA_MINIATURAS CARPETA_ZIPS 1,2,3
"""
import csv
import datetime as dt
import glob
import io
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from episode import EPISODES  # noqa: E402
from extras_s1 import SHORTS  # noqa: E402

vids, thumbs, out, dias = sys.argv[1], sys.argv[2], sys.argv[3], [int(x) for x in sys.argv[4].split(",")]
os.makedirs(out, exist_ok=True)
START = dt.date(2026, 11, 26)
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
SHOW = "Bombolín y sus amigos"
TAGS = ["Bombolín", "Bombolín y sus amigos", "dibujos animados", "dibujos animados para niños", "caricaturas",
        "videos para niños", "cuentos infantiles", "canciones infantiles", "programa infantil", "dinosaurio",
        "animales para niños", "aprender jugando", "preescolar", "niños de 3 a 8 años", "episodio completo"]
CONFIG = ("CONFIGURACIÓN ANTES DE PUBLICAR\n"
          "· Audiencia: Sí, es contenido creado para niños\n"
          "· Contenido alterado o sintético: No (dibujo animado)\n"
          "· Categoría: Cine y animación\n"
          "· Idioma del video y de título/descripción: Español (Latinoamérica)\n"
          "· Subtítulos: Subtítulos > Agregar idioma > Español > Subir archivo > Con sincronización > el .srt\n"
          "· Licencia: Licencia estándar de YouTube · Permitir insertar: Sí\n"
          "· Promoción pagada: No · Restricción de edad: No\n"
          "· Miniatura: subir miniatura1 (a los 3 días, si el CTR está bajo, cambiar por la 2 y después por la 3)\n"
          "· Playlist: Bombolín y sus amigos – Programas completos\n"
          "· Visibilidad: Programar con la fecha y hora de arriba\n")


def hora_prog(d, n):
    if n == 1:
        return "18:00"
    return "09:00" if d.weekday() >= 5 else "17:00"


def fmt(s):
    s = int(s)
    return f"{s // 60}:{s % 60:02d}"


tags_txt = lambda extra: ", ".join(extra + TAGS)  # noqa: E731
rows_all = []
for n in dias:
    ep = EPISODES[n]
    d = START + dt.timedelta(days=n - 1)
    prog = glob.glob(os.path.join(vids, f"Bombolin_Dia{n:02d}_*.mp4"))
    prog = [p for p in prog if "_Short" not in p][0]
    meta = json.load(open(prog[:-4] + ".json"))
    ch = [(t, lab) for t, lab in meta["chapters"] if lab not in ("¡Empieza!", "Presentación")]
    ch = [(0.0, f"La historia: {ep['tes']}")] + ch
    ch = [c for i, c in enumerate(ch) if i == len(ch) - 1 or ch[i + 1][0] - c[0] >= 10]
    chapters = "\n".join(f"{fmt(t)} {lab}" for t, lab in ch)
    title = f"{ep['tes']} | {SHOW} | Dibujos animados para niños"
    desc = (f"{ep['sum_es']}\n\n"
            f"En el programa de hoy:\n🦕 Una aventura nueva de Bombolín y sus amigos\n💡 ¿Sabías qué?: datos reales de animales\n"
            f"🎵 Canciones para cantar juntos\n🎲 Juegos de «¿Mito o verdad?»\n📚 Cuentos cortitos\n"
            + ("⭐ ¡Otra aventura! (la historia de ayer)\n" if n > 1 else "")
            + f"\n¡Hoy aprendimos que {ep['les']}!\n\nDato del día: {ep['dato_es']}\nFuente: {ep['fuente']}\n\n"
            f"Capítulos:\n{chapters}\n\n"
            f"{SHOW} es un programa de dibujos animados para niños de 3 a 8 años. ¡Un programa nuevo todos los días!\n\n"
            f"#Bombolin #DibujosAnimados #VideosParaNiños")
    rows = [dict(fecha=d, hora=hora_prog(d, n), tipo="Programa", archivo=os.path.basename(prog), duracion=fmt(meta["duration"]),
                 titulo=title, descripcion=desc, etiquetas=tags_txt([ep["tes"], ep["thumb"]["t1_es"].strip("¡!¿? ").lower()]),
                 playlist="Bombolín y sus amigos – Programas completos",
                 extra=[prog, prog[:-4] + ".srt"] + [os.path.join(thumbs, f"E{n:02d}_ES_miniatura{k}.jpg") for k in (1, 2, 3)])]
    for k, (a, b, hook) in enumerate(SHORTS[n]):
        f = os.path.join(vids, f"Bombolin_Dia{n:02d}_Short{k + 1}.mp4")
        hk = hook.capitalize() if hook.isupper() else hook
        hora = ("19:00", "20:00")[k] if n == 1 else ("12:30", "20:00")[k]
        rows.append(dict(fecha=d, hora=hora, tipo="Short", archivo=os.path.basename(f), duracion="",
                         titulo=f"{hk} {ep['thumb']['em']} | {SHOW} #Shorts",
                         descripcion=(f"Un momento del programa «{ep['tes']}». ¡Mira el programa completo en el canal!\n\n"
                                      f"#Bombolin #DibujosAnimados #Shorts"),
                         etiquetas=tags_txt([]), playlist="Shorts", extra=[f]))
    zp = os.path.join(out, f"Bombolin_Dia{n:02d}_{d.strftime('%d-%m')}.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["fecha", "dia", "hora", "tipo", "archivo", "duracion", "titulo", "descripcion", "etiquetas",
                     "categoria", "playlist", "audiencia"])
        for r in rows:
            for p in r["extra"]:
                if os.path.exists(p):
                    z.write(p, os.path.basename(p))
            txt = (f"PUBLICAR: {DIAS[r['fecha'].weekday()]} {r['fecha'].strftime('%d/%m/%Y')} a las {r['hora']}\n"
                   f"TIPO: {r['tipo']}\nARCHIVO: {r['archivo']}\n" + (f"DURACIÓN: {r['duracion']}\n" if r["duracion"] else "")
                   + f"\nTÍTULO:\n{r['titulo']}\n\nDESCRIPCIÓN:\n{r['descripcion']}\n\nETIQUETAS:\n{r['etiquetas']}\n\n"
                   f"CATEGORÍA: Cine y animación\nPLAYLIST: {r['playlist']}\n\n"
                   + (CONFIG if r["tipo"] == "Programa" else
                      "CONFIGURACIÓN: Audiencia: Sí, es contenido creado para niños · Contenido alterado: No · "
                      "La portada del short se elige en la app de YouTube\n"))
            z.writestr(r["archivo"][:-4] + ".txt", txt)
            w.writerow([r["fecha"].isoformat(), DIAS[r["fecha"].weekday()], r["hora"], r["tipo"], r["archivo"], r["duracion"],
                        r["titulo"], r["descripcion"], r["etiquetas"], "Cine y animación", r["playlist"], "Creado para niños"])
        z.writestr("PUBLICAR.csv", "\ufeff" + buf.getvalue())
    rows_all += rows
    print(zp, round(os.path.getsize(zp) / 1e6, 1), "MB")
