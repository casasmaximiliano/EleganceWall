"""Arma los zip por semana: videos + PUBLICAR.csv + un .txt por video con título y descripción.

Uso: python3 package.py VIDEOS_DIR ZIP_OUT_DIR
"""
import csv
import glob
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
vids, out = sys.argv[1], sys.argv[2]
LANG = sys.argv[3] if len(sys.argv) > 3 else "es"
EN = LANG == "en"
os.makedirs(out, exist_ok=True)
cal = list(csv.DictReader(open(os.path.join(HERE, "..", "calendario.csv"), encoding="utf-8")))
files = {os.path.basename(p).split("_")[2]: p for p in glob.glob(os.path.join(vids, "*.mp4"))}

LEEME = """EL MUNDO DE PIPO: videos listos para publicar (versión en {idioma})
=====================================================================

Cada video es vertical 1080x1920, de 20 a 35 segundos, con voces, música y subtítulos.
El nombre del archivo dice el DÍA del calendario, la HORA y el código del short.
  Ejemplo: {pre}01_0730_F01_... = día 1 (lunes), a las 07:30.

PUBLICAR.csv (se abre con Excel o Google Sheets) tiene, para cada video:
  día, hora, título, descripción con hashtags y playlist.
Cada video tiene además un .txt con el título y la descripción listos para copiar.

Al subirlo a YouTube:
  1. Título y descripción: cópialos del .txt.
  2. Audiencia: "Sí, es contenido creado para niños".
  3. Agrégalo a la playlist que indica el .txt.
  4. Prográmalo para el día y la hora del calendario (el día 1 es un lunes).

Las voces son sintéticas (Piper TTS, modelos abiertos) y la música y los efectos
se generaron por programa: no usan material con derechos de terceros.
"""

PL_EN = {"Series de Pipo": "Pipo's Series", "Pipo explica": "Pipo Explains", "Pipo y sus amigos": "Pipo and Friends",
         "¿Y si…? con Pipo": "What If…? with Pipo", "Juega con Pipo": "Play with Pipo", "Canciones de Pipo": "Pipo's Songs",
         "El huevo misterioso": "The Mystery Egg", "Lula perdió su arcoíris": "Lula Lost Her Rainbow",
         "La gran carrera de Zumbi": "Zumbi's Big Race", "El cumpleaños de Abu Tortu": "Grandma Tortu's Birthday",
         "La cueva de los ecos": "The Echo Cave"}
by_week = {}
for r in cal:
    w = (int(r["dia"]) - 1) // 7 + 1
    by_week.setdefault(w, []).append(r)

for w, rows in by_week.items():
    tag = "EN_Week" if EN else "Semana"
    zp = os.path.join(out, f"Pipo_{tag}{w}_dias{rows[0]['dia']}-{rows[-1]['dia']}.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
        z.writestr("LEEME.txt", LEEME.format(idioma="inglés" if EN else "español", pre="Day" if EN else "Dia")
                   + ("\nCanal en inglés: programa los horarios en hora del este de EE. UU. (ET).\n" if EN else ""))
        buf = [["archivo", "dia", "dia_semana", "hora", "titulo", "descripcion", "playlist", "audiencia"]]
        for r in rows:
            p = files.get(r["id"])
            if not p:
                print("FALTA", r["id"])
                continue
            name = os.path.basename(p)
            tit = r["titulo_en"] if EN else r["titulo_es"]
            desc = r["descripcion_en"] if EN else r["descripcion_es"]
            pl = r["playlist"]
            if EN:
                for a, b in PL_EN.items():
                    pl = pl.replace(a, b)
            z.write(p, name)
            z.writestr(name[:-4] + ".txt",
                       f"TÍTULO:\n{tit}\n\nDESCRIPCIÓN:\n{desc}\n\n"
                       f"PLAYLIST: {pl}\nPUBLICAR: día {r['dia']} ({r['dia_semana']}) a las {r['hora']}\n"
                       f"AUDIENCIA: Sí, es contenido creado para niños\n")
            buf.append([name, r["dia"], r["dia_semana"], r["hora"], tit, desc, pl, "Creado para niños"])
        import io
        s = io.StringIO()
        csv.writer(s).writerows(buf)
        z.writestr("PUBLICAR.csv", "\ufeff" + s.getvalue())
    print(zp, round(os.path.getsize(zp) / 1e6, 1), "MB")
