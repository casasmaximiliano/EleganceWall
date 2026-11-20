"""Genera shorts.json, shorts.csv y plan-100-shorts.html a partir de shorts_data.py."""
import csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from shorts_data import S, F

HERE = os.path.dirname(os.path.abspath(__file__))

MONI = ("Moni: moneda dorada redonda con canto grueso, pequeño signo $ grabado arriba, brote verde de dos hojas en la cabeza, "
        "ojos grandes blancos con pupilas negras, cejas marrones, mejillas rosadas, sonrisa roja, brazos y piernas finos marrones, zapatos negros")
CAST = {
 "Tarjetín": "Tarjetín: tarjeta de crédito rojo frambuesa con chip dorado, ojos entrecerrados y sonrisa pícara, brazos y piernas finos",
 "Cafecito": "Cafecito: taza de café de cartón color crema con franja marrón y tapa, vapor saliendo, cara tierna",
 "Infla": "Infla: fantasma verde translúcido, simpático pero travieso, con signo % en la panza",
 "Préstamín": "Préstamín: billete verde con traje brillante y sonrisa de vendedor",
 "Centavito": "Centavito: moneda cobre pequeña, primo de Moni, ojos de cachorro",
 "Ofertín": "Ofertín: etiqueta de precio amarilla con megáfono",
 "Delivy": "Delivy: bolsa de delivery de papel con cara y gorra",
 "Capricho": "Capricho: moño de regalo rosa con cuernitos de diablito",
 "Cuotín": "Cuotín: cuadradito celeste con número de cuota en la panza",
 "Fomito": "Fomito: personaje redondo violeta con ojos en espiral y cohete de cartón",
 "Botellín": "Botellín: botella de agua con anteojos de sol",
 "Celulín": "Celulín: celular con bastón y barba falsa",
 "Snacky": "Snacky: paquete de papas fritas con cara",
 "Autito": "Autito: auto pequeño redondeado con faros como ojos",
 "zombie": "Zombis: zombies caricaturescos y tiernos, nada aterradores",
}
STYLES = {
 "soft": "animación 3D suave estilo película familiar, iluminación cálida, texturas lisas",
 "flat": "ilustración 2D plana con contornos limpios y colores sólidos",
 "doodle": "dibujo a mano con marcador negro y colores pastel, líneas temblorosas",
}

def cast_for(text):
    out = []
    low = text.lower()
    for k, v in CAST.items():
        if k.lower() in low and v not in out:
            out.append(v)
    return out

# orden de publicación: reparto ponderado para alternar formatos
order = []
by = {}
for i, s in enumerate(S):
    by.setdefault(s["fmt"], []).append(i)
for fmt, idxs in by.items():
    n = len(idxs)
    for k, i in enumerate(idxs):
        order.append(((k + 0.5) / n, list(F).index(fmt), i))
order.sort()
day_of = {i: d + 1 for d, (_, _, i) in enumerate(order)}

rows = []
for i, s in enumerate(S):
    text = " ".join([s["escena"], s["gancho"]] + s["guion"])
    r = dict(s)
    r["n"] = i + 1
    r["dia"] = day_of[i]
    r["formato"] = F[s["fmt"]]
    r["reparto"] = cast_for(text)
    rows.append(r)

data = dict(moni=MONI, styles=STYLES, formats=F, shorts=rows)
with open(os.path.join(HERE, "shorts.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

with open(os.path.join(HERE, "shorts.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["N°", "Día de publicación", "Formato", "Serie", "Título", "Descripción", "Hashtags",
                "Gancho (segundo 0)", "Guion", "Dato verificable", "Cierre", "Prompt visual (3D suave)"])
    for r in sorted(rows, key=lambda r: r["dia"]):
        prompt = f"{MONI}. " + " ".join(c + "." for c in r["reparto"]) + f" Escena: {r['escena']}. Estilo: {STYLES['soft']}. Vertical 9:16, sin texto."
        w.writerow([r["n"], r["dia"], r["formato"], r["serie"], r["titulo"], r["desc"], r["tags"], r["gancho"],
                    "\n".join(r["guion"]), r["dato"], r["cierre"], prompt])

tpl = open(os.path.join(HERE, "plan_template.html"), encoding="utf-8").read()
payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
open(os.path.join(HERE, "plan-100-shorts.html"), "w", encoding="utf-8").write(tpl.replace("__DATA__", payload))
print("ok", len(rows), "shorts; html bytes", len(tpl) + len(payload))
