"""Genera el calendario y los guiones semana por semana de «Bombolín y sus amigos».

Uso: python3 plan-shorts/bombolin/src/build.py
Escribe: plan-shorts/bombolin/calendario.csv y plan-shorts/bombolin/semana-1.md … semana-5.md
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from data_a import A  # noqa: E402
from data_bc import B, C  # noqa: E402
from data_def import D, E, F  # noqa: E402

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STYLE = ("Soft 3D animated-film style, rounded plush-toy shapes, bright saturated colors, "
         "warm soft lighting, cheerful and safe for preschoolers, vertical 9:16, no text, no logos.")
CHAR = {
 "PIPO": ("PIPO: a baby dinosaur, mint-green (#7ED9A6), chubby round body and big round head, huge round "
          "brown eyes with white sparkles, small rounded teeth in a wide smile, soft yellow belly with three "
          "darker green spots, three small rounded orange spikes on his back, short tail, little orange "
          "sneakers, wearing the top half of his white eggshell with blue spots as a little hat."),
 "TOTO": ("TOTO: a round fluffy orange (#FF9A3C) furball monster the same height as Bombolín, messy fur with "
          "a striped sock stuck on it, two tiny purple horns, big goofy grin with one front tooth, big "
          "clumsy feet, always slightly off-balance."),
 "LULA": ("LULA: a small soft cloud girl, sky-blue (#8FD3F4) when calm, rosy cheeks, big gentle eyes "
          "with long lashes, tiny cloud hands; her color changes with her feelings (grey when sad, soft red "
          "when angry, pink when shy, rainbow-striped when happy)."),
 "ZUMBI": ("ZUMBI: a tiny round bumblebee boy, yellow (#FFD23F) and black stripes, oversized sparkly "
           "wings, antennae tipped with little hearts, six legs with tiny red sneakers, often with "
           "speed lines."),
 "ABU": ("ABU TORTU: a kind grandmother tortoise, twice Bombolín's height, green patchwork-quilt shell, "
         "round golden glasses, lavender knitted scarf, a walking cane shaped like a leaf, warm smile."),
}
FMT = {"A": "A. Serie", "B": "B. Pizarra", "C": "C. Comedia", "D": "D. ¿Y si…?",
       "E": "E. Juego con cuenta regresiva", "F": "F. Canción"}
TAG_ES = {"A": "#cuentosinfantiles", "B": "#curiosidadesparaniños", "C": "#humorinfantil",
          "D": "#ysi", "E": "#juegosparaniños", "F": "#cancionesinfantiles"}
TAG_EN = {"A": "#kidsstories", "B": "#funfactsforkids", "C": "#funnykids",
          "D": "#whatif", "E": "#kidsquiz", "F": "#kidssongs"}
NAME = {"PIPO": "Bombolín", "TOTO": "Toto", "LULA": "Lula", "ZUMBI": "Zumbi", "ABU": "Abu Tortu"}
JINGLE_ES = "¡Un, dos, tres, a descubrir otra vez!"
JINGLE_EN = "One, two, three, come discover with me!"
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

by_id = {x["id"]: x for x in A + B + C + D + E + F}
assert len(by_id) == 90, len(by_id)

# ---------- Calendario ----------
F_wd = ["F01", "F02", "F04", "F05", "F06", "F08", "F09", "F11", "F12", "F14", "F15"]
F_we = ["F03", "F07", "F13", "F10"]
E_wd = ["E04", "E01", "E06", "E07", "E08", "E09", "E10", "E11", "E12", "E14", "E05"]
E_we = ["E02", "E13", "E03"]
B_q = ["B01", "B04", "B02", "B03", "B08", "B09", "B05", "B06", "B10", "B07", "B11"]
C_wd = ["C01", "C03", "C06", "C10", "C12", "C07", "C09", "C13", "C16", "C08", "C17"]
C_we = ["C02", "C04", "C05", "C11", "C14", "C15", "C18"]
D_q = ["D09", "D01", "D05", "D08", "D02", "D10", "D03", "D07", "D06", "D04"]
A_q = [x["id"] for x in A]

sched = []  # (día, nombre del día, hora, franja, id)
wd_i = 0
for day in range(1, 31):
    dow = (day - 1) % 7
    if dow < 5:
        m = F_wd.pop(0) if wd_i % 2 == 0 else E_wd.pop(0)
        ev = B_q.pop(0) if wd_i % 2 == 0 else C_wd.pop(0)
        sched += [(day, dow, "07:30", "Mañana", m), (day, dow, "17:00", "Tarde", A_q.pop(0)),
                  (day, dow, "19:30", "Noche (tranquilo)", ev)]
        wd_i += 1
    elif dow == 5:
        last = D_q.pop(0) if day == 27 else C_we.pop(0)
        sched += [(day, dow, "09:00", "Mañana", F_we.pop(0)), (day, dow, "12:30", "Mediodía", D_q.pop(0)),
                  (day, dow, "18:00", "Tarde", last)]
    else:
        mid = D_q.pop(0) if day == 28 else E_we.pop(0)
        sched += [(day, dow, "09:00", "Mañana", D_q.pop(0)), (day, dow, "12:30", "Mediodía", mid),
                  (day, dow, "18:00", "Tarde", C_we.pop(0))]
for q in (F_wd, F_we, E_wd, E_we, B_q, C_wd, C_we, D_q, A_q):
    assert not q, q
ids = [s[4] for s in sched]
assert len(ids) == 90 and len(set(ids)) == 90

for x in by_id.values():
    for k in ("tes", "ten"):
        assert len(x[k]) <= 60, (x["id"], k, len(x[k]), x[k])


def hashtags(x, lang):
    if lang == "es":
        return f"#Bombolin #dibujosanimados #videosinfantiles {x['tag']} {TAG_ES[x['f']]}"
    return f"#Bombolin #kidscartoon #kidsvideos #learnwithbombolin {TAG_EN[x['f']]}"


def cierre(x):
    l = x["l"]
    if x["f"] == "F":
        return (f"Todos cantan el estribillo completo una vez más. Abu Tortu: «¡Hoy aprendimos que {l}! "
                f"¡Cántala otra vez!»")
    if x["f"] == "A":
        return f"Abu Tortu: «¡Hoy aprendimos que {l}! {x['cliff']}» Todos: «{JINGLE_ES}»"
    if x["f"] == "E":
        return f"Abu Tortu: «¡Hoy aprendimos que {l}! ¡Juega otra vez!» Todos: «{JINGLE_ES}»"
    return f"Abu Tortu: «¡Hoy aprendimos que {l}!» Todos: «{JINGLE_ES}»"


TIMES = ["0–4 s", "4–11 s", "11–18 s", "18–25 s", "25–33 s"]


def render(x, day, dow, hora, franja):
    out = []
    serie = f" · Serie «{x['serie']}», cap. {x['cap']}" if x["f"] == "A" else ""
    out.append(f"### Día {day} ({DIAS[dow]}) · {hora} · `{x['id']}` · {FMT[x['f']]}{serie}\n")
    out.append(f"**Franja:** {franja}\n")
    out.append(f"**Título**\n- ES: {x['tes']}\n- EN: {x['ten']}\n")
    out.append(f"**Descripción**\n- ES: {x['des']} {hashtags(x, 'es')}\n- EN: {x['den']} {hashtags(x, 'en')}\n")
    v0, l0 = [p.strip() for p in x["s"][0].split("|", 1)]
    out.append(f"**Gancho (segundo 0):** {v0}. Texto grande: **{x['hes']}** / **{x['hen']}**. "
               f"Primera frase: {l0}\n")
    out.append("**Guion**\n\n| # | Tiempo | Qué se ve | Quién habla y qué dice |\n|---|---|---|---|")
    for i, sc in enumerate(x["s"]):
        vis, line = [p.strip() for p in sc.split("|", 1)]
        out.append(f"| {i+1} | {TIMES[i]} | {vis} | {line} |")
    out.append(f"| 5 | {TIMES[4]} | Todos juntos, con la misma toma del inicio para que el video vuelva a empezar solo | {cierre(x)} |\n")
    if x["f"] == "F":
        es, en = x["song"]
        out.append(f"**Canción (se repite 2 veces)**\n- ES: *{es.replace(' | ', ' / ')}*\n- EN: *{en.replace(' | ', ' / ')}*\n")
    else:
        out.append(f"**Rima del canal:** *{JINGLE_ES}* / *{JINGLE_EN}*\n")
    out.append(f"**Dato clave:** {x['dato']}  \n**Fuente o supuesto:** {x['fuente']}\n")
    out.append(f"**Aprendizaje (ES):** ¡Hoy aprendimos que {x['l']}!\n")
    out.append("**Voces:** " + ", ".join(NAME[c] for c in x["ch"]) +
               (", Abu Tortu (narradora)" if "ABU" not in x["ch"] else "") + ". Ver `voces.md`.\n")
    blocks = "\n".join(CHAR[c] for c in x["ch"])
    out.append("**Prompt visual (escena principal)**\n```\n" + STYLE + "\n" + blocks + "\nScene: " + x["p"] + "\n```\n")
    out.append("---\n")
    return "\n".join(out)


weeks = {}
for day, dow, hora, franja, sid in sched:
    w = (day - 1) // 7 + 1
    weeks.setdefault(w, []).append(render(by_id[sid], day, dow, hora, franja))

for w, parts in weeks.items():
    first, last = (w - 1) * 7 + 1, min(w * 7, 30)
    head = (f"# Bombolín y sus amigos · Semana {w} (días {first} a {last})\n\n"
            "> Generado con `src/build.py`. Para cambiar un guion, edita `src/data_*.py` y vuelve a correr el script.\n"
            "> Los horarios son la hora local del público principal de cada canal (ver `README.md`).\n\n---\n")
    with open(os.path.join(OUT, f"semana-{w}.md"), "w", encoding="utf-8") as fh:
        fh.write(head + "\n".join(parts))

with open(os.path.join(OUT, "calendario.csv"), "w", newline="", encoding="utf-8") as fh:
    wr = csv.writer(fh)
    wr.writerow(["dia", "dia_semana", "hora", "franja", "id", "formato", "serie", "capitulo",
                 "titulo_es", "titulo_en", "descripcion_es", "descripcion_en", "playlist"])
    PL = {"A": "Series de Bombolín", "B": "Bombolín explica", "C": "Bombolín y sus amigos",
          "D": "¿Y si…? con Bombolín", "E": "Juega con Bombolín", "F": "Canciones de Bombolín"}
    for day, dow, hora, franja, sid in sched:
        x = by_id[sid]
        wr.writerow([day, DIAS[dow], hora, franja, sid, FMT[x["f"]], x.get("serie", ""), x.get("cap", ""),
                     x["tes"], x["ten"], f"{x['des']} {hashtags(x, 'es')}", f"{x['den']} {hashtags(x, 'en')}",
                     PL[x["f"]] + (f" · {x['serie']}" if x["f"] == "A" else "")])

# Resumen del calendario en markdown (para el README)
rows = ["| Día | Hora | ID | Formato | Título (ES) |", "|---|---|---|---|---|"]
for day, dow, hora, franja, sid in sched:
    x = by_id[sid]
    rows.append(f"| {day} {DIAS[dow][:3]} | {hora} | `{sid}` | {FMT[x['f']]} | {x['tes']} |")
with open(os.path.join(OUT, "calendario.md"), "w", encoding="utf-8") as fh:
    fh.write("# Calendario del mes: 90 shorts (3 por día)\n\n"
             "> El día 1 es un **lunes**. Los horarios son la hora local del público de cada canal.\n"
             "> El mismo calendario, con descripciones y playlists, está en `calendario.csv`.\n\n"
             + "\n".join(rows) + "\n")

from collections import Counter  # noqa: E402
print("OK", Counter(by_id[i]["f"] for i in ids))
