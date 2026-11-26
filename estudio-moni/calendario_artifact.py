"""Arma los datos del artefacto 'Calendario Moni Finanzas': cal_art/plan.json y las miniaturas en cal_art/mini/.
Uso: python3 calendario_artifact.py [assets.json]   (assets.json: {"short_NNN": "url del video subido"})"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cal_art")
cal = json.load(open(os.path.join(HERE, "calendario.json"), encoding="utf-8"))
largos = json.load(open(os.path.join(HERE, "largos", "largos.json"), encoding="utf-8"))
shorts = {s["n"]: s for s in json.load(open(os.path.join(HERE, "shorts.json"), encoding="utf-8"))["shorts"]}
assets = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
CATEGORIA = "Educación"
BASE_TAGS = ["moni finanzas", "finanzas personales", "educación financiera", "plata", "ahorro", "shorts"]
LISTA = {"Sitcom": "Gastos hormiga (Shorts)", "Telenovela del dinero": "Telenovela del dinero (Shorts)", "Mito o verdad": "Mito o verdad",
         "¿Y si…? Simulador": "Simulaciones de Moni", "Pizarra express": "Moni explica en 15 segundos"}
# Video largo relacionado por tema (en orden de preferencia); se usa el primero que ya esté publicado a la hora del short.
TEMAS = [(r"tarjet|cuota|m[ií]nimo|adelanto", [4, 13, 16, 25]), (r"inflaci|infla|fantasma|reduflaci|colch[oó]n|aumentaron", [18, 23, 11, 21]),
         (r"pr[eé]stamo|deuda|presté|endeudar", [16, 4, 25]), (r"emergencia|imprevist|se me rompi|heladera", [14, 25]),
         (r"cripto|amigo me jur|fomo", [19, 3, 25]), (r"acci[oó]n|coca-cola|bolsa", [22, 12, 15, 25]),
         (r"blockbuster|kodak|mcdonald|netflix|empresa", [15, 25]), (r"messi|taylor|gira", [1, 15, 25]),
         (r"kiosco|chofer|negocio", [15, 25, 21]), (r"s[uú]per|oferta|precio|pochoclo|9,99|black friday|2x1|env[ií]o", [9, 17, 21]),
         (r"merezco|invito yo|capricho", [17, 21]), (r"auto\b|celular|remera|agua|cajero|gimnasio|suscrip|zombie|delivery|caf[eé]|cafecito", [21, 25]),
         (r".", [25, 21])]
import datetime as dt, re
LARGO_PUB = {v["n"]: dt.datetime.fromisoformat(f"{v['fecha']}T{v['hora_ar']}") for v in largos}
TIT = {v["n"]: v["titulo"] for v in largos}
def relacionado(titulo, desc, fecha, hora):
    when = dt.datetime.fromisoformat(f"{fecha}T{hora}"); low = (titulo + " " + desc).lower()
    for rx, ns in TEMAS:
        if re.search(rx, low):
            for n in ns:
                if LARGO_PUB[n] <= when:
                    return f"{TIT[n]} (video largo {n})"
    pub = [n for n in LARGO_PUB if LARGO_PUB[n] <= when]
    if pub:
        n = max(pub, key=lambda k: LARGO_PUB[k]); return f"{TIT[n]} (video largo {n})"
    return "Todavía no hay video largo publicado: dejalo vacío y agregá “¿Qué pasa si ahorrás el cafecito toda tu vida?” después del miércoles 25 a las 18:00."
items = []
for r in cal:
    items.append(dict(id=f"s{r['n']}", tipo="short", fecha=r["fecha"], hora=r["hora_ar"], hora_mx=r["hora_mx"], hora_co=r["hora_co"],
                      titulo=r["titulo"], descripcion=r["descripcion"], comentario=r["comentario_fijado"], archivo=r["archivo"],
                      grupo=r["grupo"], nicho=r["nicho"], provisorio=r["provisorio"], video=assets.get(f"short_{r['n']:03d}", ""),
                      formato=r["formato"], categoria=CATEGORIA,
                      etiquetas=", ".join([t.lstrip("#") for t in shorts[r["n"]]["tags"].split() if t.lstrip("#") not in ("moni", "shorts")] + BASE_TAGS),
                      lista=(r["nicho"] + " (exploración)") if r["grupo"] == "exploración" else LISTA.get(r["formato"], "Shorts de Moni"),
                      relacionado=relacionado(r["titulo"], shorts[r["n"]]["desc"], r["fecha"], r["hora_ar"])))
# Videos ya publicados que se reemplazan por la versión 3D: n → (fecha, hora AR, aviso)
REEMPLAZOS = {21: ("2026-11-26", "18:00", "REEMPLAZO EN 3D: 1) En YouTube Studio borrá el video “¿Qué pasa si ahorrás el cafecito toda tu vida?” publicado el 25/11. "
                   "2) Subí este video en 3D con estos mismos datos y programalo para hoy a las 18:00. 3) Cargá las 3 miniaturas en Probar y comparar. "
                   "4) En los shorts ya publicados que tenían este video como relacionado, volvé a elegirlo (el enlace cambia).")}
for v in largos:
    n = v["n"]; tl = json.load(open(os.path.join(HERE, "largos", "out", "timeline", f"{n:02d}.json"), encoding="utf-8"))
    desc = tl["descripcion"].replace("un short nuevo cada día", "shorts nuevos todos los días")
    if v["tipo"] == "Guía":
        desc = desc.replace(f"En este video: {v['titulo'].lower()}.", "En este video: la guía completa, paso a paso, con números de ejemplo.")
    dur = tl["total"]; thumbs = []
    tres_d = os.path.exists(os.path.join(HERE, "largos", "miniaturas", f"miniatura_{n:02d}_3D_A.png"))
    for suf in ["", "_B", "_C"]:
        src = os.path.join(HERE, "largos", "miniaturas", f"miniatura_{n:02d}_3D_{suf[1:] or 'A'}.png" if tres_d else f"miniatura_{n:02d}{suf}.png")
        dst = os.path.join(OUT, "mini", f"m{n:02d}{suf or '_A'}.jpg")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-q:v", "3", dst], check=True)
        thumbs.append(f"mini/m{n:02d}{suf or '_A'}.jpg")
    items.append(dict(id=f"l{n}", tipo="largo", fecha=v["fecha"], hora=v["hora_ar"], hora_mx=v["hora_mx"], hora_co=v["hora_co"],
                      titulo=v["titulo"], alt=v["alt"], descripcion=desc, etiquetas=v["tags"], lista=v["playlist"],
                      shorts_rel=[f"{s['titulo']}" for s in v["shorts_rel"]], duracion=f"{int(dur // 60)}:{int(dur % 60):02d}",
                      archivo=f"video {n:02d} {'en 3D ' if tres_d else ''}(mp4 original que te mandé por el chat)", subtitulos=f"subtitulos_{n}.srt",
                      thumbs=thumbs, categoria=CATEGORIA, comentario="¿Y a vos qué te pasó con esto? Te leo en los comentarios 👇", n=n))
    if n in REEMPLAZOS:  # el video ya publicado se reemplaza por la versión 3D: tarjeta aparte en el día del reemplazo
        f, h, aviso = REEMPLAZOS[n]
        items.append(dict(items[-1], id=f"l{n}r", fecha=f, hora=h, hora_mx=f"{int(h[:2]) - 3:02d}{h[2:]}", hora_co=f"{int(h[:2]) - 2:02d}{h[2:]}", aviso=aviso))
        items[-2]["aviso"] = f"Esta versión se reemplaza el {f[8:]}/{f[5:7]} por la versión 3D (mirá ese día)."
items.sort(key=lambda x: (x["fecha"], x["hora"]))
json.dump(items, open(os.path.join(OUT, "plan.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(len(items), "items ·", sum(1 for i in items if i["tipo"] == "short"), "shorts ·", sum(1 for i in items if i["tipo"] == "largo"), "largos ·",
      os.path.getsize(os.path.join(OUT, "plan.json")) // 1024, "KB")
