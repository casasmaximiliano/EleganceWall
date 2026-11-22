"""Arma largos.json (fechas, horarios, descripciones) y la lista de miniaturas para thumbs.js."""
import datetime as dt, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from largos_data import V

shorts = {s["n"]: s for s in json.load(open(os.path.join(HERE, "..", "shorts.json"), encoding="utf-8"))["shorts"]}
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dates = []
d = dt.date(2026, 11, 25)
while len(dates) < len(V):
    if d.weekday() in (2, 6):
        dates.append(d)
    d += dt.timedelta(days=1)

def shift(h, k):
    t = dt.datetime(2000, 1, 1, *map(int, h.split(":"))) + dt.timedelta(hours=k)
    return t.strftime("%H:%M")

PLAYLIST = {"Historia": "Historias del dinero", "Simulación": "Simulaciones de Moni", "Telenovela": "Telenovela del dinero (películas)", "Guía": "Guías de finanzas personales"}
out = []
for i, (v, day) in enumerate(zip(V, dates), 1):
    hora = "18:00" if day.weekday() == 2 else "11:00"
    caps = "\n".join(f"{c[0]} {c[1]}" for c in v["caps"])
    desc = (f"{v['gancho'].split('. ')[0]}. En este video: {v['titulo'].lower() if v['tipo']=='Guía' else 'la historia completa, explicada con Moni'}.\n\n"
            f"⏱️ Capítulos\n{caps}\n\n"
            f"📺 Más de Moni Finanzas: un short nuevo cada día y videos largos los miércoles y domingos.\n\n"
            f"📚 Fuentes y supuestos: {v['fuentes']}\n\n"
            f"Contenido educativo. No es asesoramiento financiero. Personajes animados y voces creados con herramientas digitales.\n\n"
            f"#finanzaspersonales #educacionfinanciera #monifinanzas")
    out.append(dict(n=i, fecha=day.isoformat(), dia=DIAS[day.weekday()], semana=(i + 1) // 2, hora_ar=hora,
                    hora_co=shift(hora, -2), hora_mx=shift(hora, -3), hora_es=shift(hora, 4),
                    playlist=PLAYLIST[v["tipo"]], descripcion=desc, thumb_file=f"miniatura_{i:02d}.png",
                    shorts_rel=[dict(n=n, titulo=shorts[n]["titulo"]) for n in v["shorts"]], **v))
json.dump(out, open(os.path.join(HERE, "largos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for o in out:
    print(o["n"], o["fecha"], o["dia"][:3], o["hora_ar"], o["tipo"], "|", o["titulo"], len(o["titulo"]))
