"""Calendario de publicación por plataforma, con fechas reales.

Uso: python3 horarios.py [FECHA_INICIO_LUNES]   (por defecto 2026-11-30)
Escribe ../horarios_publicacion.csv y ../horarios_publicacion.md
"""
import csv
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
start = dt.date.fromisoformat(sys.argv[1] if len(sys.argv) > 1 else "2026-11-30")
assert start.weekday() == 0, "el día 1 tiene que ser lunes"
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["", "ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def plus(hhmm, minutes):
    h, m = map(int, hhmm.split(":"))
    t = h * 60 + m + minutes
    return f"{t // 60:02d}:{t % 60:02d}"


cal = list(csv.DictReader(open(os.path.join(HERE, "..", "calendario.csv"), encoding="utf-8")))
rows = []
for r in cal:
    d = start + dt.timedelta(days=int(r["dia"]) - 1)
    rows.append({
        "dia": r["dia"], "fecha": d.isoformat(), "dia_semana": DIAS[d.weekday()], "id": r["id"],
        "titulo_es": r["titulo_es"], "titulo_en": r["titulo_en"],
        "youtube": r["hora"], "tiktok": plus(r["hora"], 60), "instagram": plus(r["hora"], 90),
    })

with open(os.path.join(HERE, "..", "horarios_publicacion.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

md = [f"# Horarios de publicación: {len(rows)} shorts, 3 por día",
      "",
      f"> Empieza el **lunes {start.day} de {MESES[start.month]} de {start.year}**. Para cambiar la fecha de inicio: "
      "`python3 branding/horarios.py AAAA-MM-DD` (tiene que ser un lunes).",
      "> **Canal en español:** hora del país con más público (si no sabes cuál, usa la hora de México). "
      "**Canal en inglés:** los mismos horarios en hora del este de EE. UU. (ET).",
      "> Se sube el mismo short en las tres redes: primero en YouTube, 1 hora después en TikTok y 1 hora y media después en Instagram (Reels).",
      ""]
cur = None
for r in rows:
    if r["fecha"] != cur:
        cur = r["fecha"]
        d = dt.date.fromisoformat(cur)
        md += ["", f"### Día {r['dia']} · {r['dia_semana']} {d.day} de {MESES[d.month]}", "",
               "| YouTube | TikTok | Instagram | Short | Título (ES) | Título (EN) |", "|---|---|---|---|---|---|"]
    md.append(f"| {r['youtube']} | {r['tiktok']} | {r['instagram']} | `{r['id']}` | {r['titulo_es']} | {r['titulo_en']} |")
open(os.path.join(HERE, "..", "horarios_publicacion.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
print("ok", rows[0]["fecha"], "→", rows[-1]["fecha"])
