"""Calendario de Shorts v3: 4 por día del 25 al 27/11/2026 y 3 por día desde el 28/11 (13, 19 y 22 h de Argentina).

Reglas (ver análisis en el historial del canal):
- 4 horarios fijos, hora de Argentina: 10:00, 13:00, 19:00 y 22:00 (México 7, 10, 16 y 19 h).
- Cada día: 1 short del grupo A (gastos cotidianos con personaje), 1 del grupo B (deudas, tarjeta, inflación,
  ahorro) y 2 de exploración (nichos nuevos) durante los primeros 6 días.
- La exploración rota de horario para que ningún nicho quede siempre en la mejor hora.
- El grupo C (conceptos abstractos de inversión) no se publica. Ver DESCARTADOS en shorts_data.py.
- Desde el día 7 el calendario es provisorio: los nichos que ganen la exploración van a ocupar 1-2 lugares por día.
Uso: python3 calendario.py [--zip]   (--zip copia los MP4 y arma un zip por semana)
"""
import csv, datetime as dt, json, os, re, shutil, sys, unicodedata, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shorts_data import DESCARTADOS, EXPLORACION

VID = os.path.join(HERE, "video", "out")
START = dt.date(2026, 11, 25)
DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
DIAS_LARGO = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
SLOTS = ["10:00", "13:00", "19:00", "22:00"]   # hasta el 27/11
SLOTS3 = ["13:00", "19:00", "22:00"]          # desde el 28/11: 3 por día
# Títulos reescritos con lo que mostraron los datos del 25-27/11: número concreto + conflicto en primera persona
# ("Gasté $20 más para ahorrarme $5" y "Por qué todo cuesta $9,99" fueron los que más retuvieron).
TITULO_NUEVO = {
    88: "Pagué el mínimo de la tarjeta: 6 años y casi el doble 😱",
    89: "Las cuotas sin interés no son tan gratis 💳",
    60: "El cajero me cobra $144 al año por sacar MI plata",
    54: "El 2x1 me hizo gastar el 100 %",
    5: "La regla para que la tarjeta no me cobre intereses 💳",
    58: "7 cuotas “chiquitas” = $210 por mes",
    13: "Le presté $100 a mi primo y… 🫠",
    15: "Salí de deudas… y casi vuelvo a caer",
}
PUBLICADOS = [66, 51, 1, 81, 26, 2, 97, 52, 3, 67, 27, 4]  # subidos entre el 21 y el 24/11

# Grupo A: gastos de todos los días con el gasto como personaje (el formato que más retuvo: 52 % vs. 19-24 %)
A = [53, 55, 61, 63, 60, 54, 24, 57, 21, 58, 65, 62, 64, 56, 59, 68, 22, 19, 9, 16, 25, 94, 78]
# Grupo B: deudas, tarjeta, inflación y ahorro, rehechos con el arranque nuevo (2 personajes, sin "Cap. N")
B = [6, 11, 12, 88, 89, 5, 7, 10, 13, 20, 15, 70, 79, 17, 18, 23, 83, 85, 87, 92, 91, 96, 100, 14, 8, 76, 69, 29,
     36, 37, 39, 43, 47, 50]
# Exploración, fase 1: 6 nichos × 2. Orden pensado para que cada nicho caiga en días y horarios distintos.
E_FASE1 = [(101, "10:00"), (103, "19:00"),   # día 1: negocios por dentro · trucos de precios
           (105, "13:00"), (107, "22:00"),   # día 2: historias de empresas · acciones
           (109, "10:00"), (111, "19:00"),   # día 3: cuánto gana un negocio · plata de famosos
           (102, "13:00"), (104, "22:00"),   # día 4
           (106, "10:00"), (108, "19:00"),   # día 5
           (110, "13:00"), (112, "22:00")]   # día 6
NICHO = {101: "Negocios por dentro", 102: "Negocios por dentro", 103: "Trucos de precios", 104: "Trucos de precios",
         105: "Historias de empresas", 106: "Historias de empresas", 107: "Acciones", 108: "Acciones",
         109: "Cuánto gana un negocio", 110: "Cuánto gana un negocio", 111: "Plata de famosos", 112: "Plata de famosos"}

data = json.load(open(os.path.join(HERE, "shorts.json"), encoding="utf-8"))
by_n = {s["n"]: s for s in data["shorts"]}
todos = set(A) | set(B) | set(EXPLORACION) | set(PUBLICADOS) | DESCARTADOS
assert len(A) == 23 and len(B) == 34 and not (set(A) & set(B)), (len(A), len(B))
assert todos == set(by_n), sorted(set(by_n) - todos)
assert sorted(n for n, _ in E_FASE1) == EXPLORACION

def shift(hhmm, h):
    t = dt.datetime(2000, 1, 1, *map(int, hhmm.split(":"))) + dt.timedelta(hours=h)
    return t.strftime("%H:%M")

a, b = list(A), list(B)
plan = []
for d in range(3):  # 25 al 27/11 (ya publicados o programados): A + B + 2 de exploración, 4 por día
    e = dict((slot, n) for n, slot in E_FASE1[2 * d: 2 * d + 2])
    free = [s for s in SLOTS if s not in e]
    first, second = (a, b) if d % 2 == 0 else (b, a)
    e[free[0]] = first.pop(0); e[free[1]] = second.pop(0)
    for slot in SLOTS:
        plan.append((d, slot, e[slot], "exploración" if e[slot] in EXPLORACION else ("A" if e[slot] in A else "B")))
# Desde el 28/11: 3 por día (se saca las 10:00, que en México son las 7). Un short de exploración por día hasta
# terminar los 6 que faltan, rotando de horario; el resto alterna A y B.
expl = [n for n, _ in E_FASE1[6:]]
d = 3
while a or b or expl:
    hoy = []
    if expl: hoy.append(expl.pop(0))
    while len(hoy) < len(SLOTS3):
        src = (a if (len(hoy) + d) % 2 == 0 else b) if (a and b) else (a or b)
        if not src: break
        hoy.append(src.pop(0))
    k = d % len(SLOTS3)  # la exploración rota de horario
    hoy = hoy[-k:] + hoy[:-k] if k else hoy
    for slot, n in zip(SLOTS3, hoy):
        plan.append((d, slot, n, "exploración" if n in EXPLORACION else ("A" if n in A else "B")))
    d += 1

def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-")[:50]

rows = []
for i, (d, slot, n, grupo) in enumerate(plan, 1):
    s = by_n[n]; date = START + dt.timedelta(days=d)
    rows.append(dict(orden=i, dia=d + 1, fecha=date.isoformat(), dia_semana=DIAS_LARGO[date.weekday()], hora_ar=slot,
                     hora_co=shift(slot, -2), hora_mx=shift(slot, -3), hora_es=shift(slot, 4), n=n, grupo=grupo,
                     nicho=NICHO.get(n, ""), provisorio=d >= 6, formato=s["formato"], titulo=TITULO_NUEVO.get(n, s["titulo"]),
                     descripcion=f"{s['desc']}\n\n{('Fuente: ' + s['dato'] + chr(10) + chr(10)) if n in EXPLORACION else ''}"
                                 f"Contenido educativo, no es asesoramiento financiero.\n\n{s['tags']} #shorts",
                     comentario_fijado=f"¿Y a vos te pasó? Contame en los comentarios 👇",
                     archivo=f"{i:03d}_{date.strftime('%m-%d')}_{DIAS[date.weekday()]}_{slot.replace(':', 'h')}_{slug(s['titulo'])}.mp4"))

json.dump(rows, open(os.path.join(HERE, "calendario.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, "calendario.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Orden", "Día", "Fecha", "Día de la semana", "Hora Argentina", "Hora Colombia/Perú", "Hora México", "Hora España",
                "Grupo", "Nicho", "Provisorio", "Archivo", "Título", "Descripción", "Comentario para fijar"])
    for r in rows:
        w.writerow([r["orden"], r["dia"], r["fecha"], r["dia_semana"], r["hora_ar"], r["hora_co"], r["hora_mx"], r["hora_es"],
                    r["grupo"], r["nicho"], "sí" if r["provisorio"] else "", r["archivo"], r["titulo"], r["descripcion"],
                    r["comentario_fijado"]])

if "--zip" in sys.argv:  # un zip por semana (28 shorts)
    dest = os.path.join(VID, "calendario")
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    bloques = {}
    for r in rows:
        shutil.copyfile(os.path.join(VID, "mp4", f"{r['n']:03d}.mp4"), os.path.join(dest, r["archivo"]))
        bloques.setdefault((r["dia"] - 1) // 7, []).append(r)
    for k, items in bloques.items():
        zp = os.path.join(VID, f"Moni_shorts_{items[0]['fecha'][5:]}_a_{items[-1]['fecha'][5:]}.zip")
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
            for r in items:
                z.write(os.path.join(dest, r["archivo"]), r["archivo"])
            z.write(os.path.join(HERE, "calendario.csv"), "calendario.csv")
        print(os.path.basename(zp), len(items), "videos", round(os.path.getsize(zp) / 1e6, 1), "MB")
print("total:", len(rows), "· último día:", rows[-1]["fecha"], "· fase 1 hasta:", rows[23]["fecha"])
for r in rows[:24]:
    print(r["fecha"], r["hora_ar"], r["grupo"][:5], r["n"], r["titulo"][:60])
