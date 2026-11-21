"""Arma el calendario de publicación (2-3 shorts por día) y reempaqueta los videos por semana.

Reglas:
- Telenovela: 1 capítulo por día, en orden, en el horario de mayor audiencia (el cierre dice "Próximo capítulo mañana").
- Primera semana: los ganchos más fuertes.
- El mismo día no se repite formato.
- Lunes a viernes: 3 shorts (13:00, 19:00, 22:00). Sábado y domingo: 2 (12:00, 21:00). Hora de Argentina (UTC-3).
"""
import csv, datetime as dt, json, os, re, shutil, unicodedata, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
VID = os.path.join(HERE, "video", "out")
START = dt.date(2026, 11, 23)  # lunes
DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
DIAS_LARGO = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
WEEKDAY_SLOTS = ["13:00", "19:00", "22:00"]
WEEKEND_SLOTS = ["12:00", "21:00"]
PRIME = {"22:00", "21:00"}
TOP = [66, 51, 81, 26, 97, 52, 67, 27, 88, 70, 82, 53]  # ganchos más fuertes al principio

data = json.load(open(os.path.join(HERE, "shorts.json"), encoding="utf-8"))
by_n = {s["n"]: s for s in data["shorts"]}
novela = [s["n"] for s in data["shorts"] if s["fmt"] == "novela"]

# resto: primero los TOP, después intercalado ponderado por formato
rest_fmts = {}
for s in data["shorts"]:
    if s["fmt"] != "novela" and s["n"] not in TOP:
        rest_fmts.setdefault(s["fmt"], []).append(s["n"])
inter = []
for fmt, ns in rest_fmts.items():
    for k, n in enumerate(ns):
        inter.append(((k + 0.5) / len(ns), fmt, n))
inter.sort()
others = TOP + [n for _, _, n in inter]

def shift(hhmm, h):
    t = dt.datetime(2000, 1, 1, *map(int, hhmm.split(":"))) + dt.timedelta(hours=h)
    return t.strftime("%H:%M")

plan = []
day = 0
while novela or others:
    date = START + dt.timedelta(days=day)
    slots = WEEKEND_SLOTS if date.weekday() >= 5 else WEEKDAY_SLOTS
    used_fmts = set()
    todays = []
    for slot in slots:
        n = None
        if slot in PRIME and novela:
            n = novela.pop(0)
        else:
            for i, cand in enumerate(others):
                if by_n[cand]["fmt"] not in used_fmts:
                    n = others.pop(i)
                    break
            if n is None and others:
                n = others.pop(0)
            if n is None and novela and slot in PRIME:
                n = novela.pop(0)
        if n is None:
            continue
        used_fmts.add(by_n[n]["fmt"])
        todays.append((slot, n))
    for slot, n in todays:
        plan.append(dict(fecha=date.isoformat(), semana=day // 7 + 1, dia_semana=DIAS_LARGO[date.weekday()],
                         hora_ar=slot, hora_co=shift(slot, -2), hora_mx=shift(slot, -3), hora_es=shift(slot, 4), n=n))
    day += 1

def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-")[:50]

for i, p in enumerate(plan, 1):
    s = by_n[p["n"]]
    d = dt.date.fromisoformat(p["fecha"])
    p.update(orden=i, formato=s["formato"], serie=s["serie"], titulo=s["titulo"],
             descripcion=f"{s['desc']}\n\nContenido educativo, no es asesoramiento financiero.\n\n{s['tags']} #shorts",
             archivo=f"{i:03d}_{d.strftime('%m-%d')}_{DIAS[d.weekday()]}_{p['hora_ar'].replace(':', 'h')}_{slug(s['titulo'])}.mp4")

json.dump(plan, open(os.path.join(HERE, "calendario.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, "calendario.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Orden", "Semana", "Fecha", "Día", "Hora Argentina/Uruguay/Chile", "Hora Colombia/Perú", "Hora México", "Hora España",
                "Archivo", "Formato", "Serie", "Título", "Descripción"])
    for p in plan:
        w.writerow([p["orden"], p["semana"], p["fecha"], p["dia_semana"], p["hora_ar"], p["hora_co"], p["hora_mx"], p["hora_es"],
                    p["archivo"], p["formato"], p["serie"], p["titulo"], p["descripcion"]])

# reempaquetar por semana
dest = os.path.join(VID, "calendario")
if os.path.isdir(dest):
    shutil.rmtree(dest)
os.makedirs(dest)
weeks = {}
for p in plan:
    src = os.path.join(VID, "mp4", f"{p['n']:03d}.mp4")
    shutil.copyfile(src, os.path.join(dest, p["archivo"]))
    weeks.setdefault(p["semana"], []).append(p)
for wk, items in weeks.items():
    first, last = items[0]["fecha"], items[-1]["fecha"]
    zp = os.path.join(VID, f"Moni_semana{wk}_{first[5:]}_a_{last[5:]}.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
        for p in items:
            z.write(os.path.join(dest, p["archivo"]), p["archivo"])
        z.write(os.path.join(HERE, "calendario.csv"), "calendario.csv")
    print(os.path.basename(zp), len(items), "videos", round(os.path.getsize(zp) / 1e6, 1), "MB")
print("días:", day, "· último:", plan[-1]["fecha"], "· total:", len(plan))
