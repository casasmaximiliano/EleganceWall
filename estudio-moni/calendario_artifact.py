"""Arma los datos del artefacto 'Calendario Moni Finanzas': cal_art/plan.json y las miniaturas en cal_art/mini/.
Uso: python3 calendario_artifact.py [assets.json]   (assets.json: {"short_NNN": "url del video subido"})"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cal_art")
cal = json.load(open(os.path.join(HERE, "calendario.json"), encoding="utf-8"))
largos = json.load(open(os.path.join(HERE, "largos", "largos.json"), encoding="utf-8"))
shorts = {s["n"]: s for s in json.load(open(os.path.join(HERE, "shorts.json"), encoding="utf-8"))["shorts"]}
assets = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
items = []
for r in cal:
    items.append(dict(id=f"s{r['n']}", tipo="short", fecha=r["fecha"], hora=r["hora_ar"], hora_mx=r["hora_mx"], hora_co=r["hora_co"],
                      titulo=r["titulo"], descripcion=r["descripcion"], comentario=r["comentario_fijado"], archivo=r["archivo"],
                      grupo=r["grupo"], nicho=r["nicho"], provisorio=r["provisorio"], video=assets.get(f"short_{r['n']:03d}", ""),
                      formato=r["formato"]))
for v in largos:
    n = v["n"]; tl = json.load(open(os.path.join(HERE, "largos", "out", "timeline", f"{n:02d}.json"), encoding="utf-8"))
    desc = tl["descripcion"].replace("un short nuevo cada día", "shorts nuevos todos los días")
    if v["tipo"] == "Guía":
        desc = desc.replace(f"En este video: {v['titulo'].lower()}.", "En este video: la guía completa, paso a paso, con números de ejemplo.")
    dur = tl["total"]; thumbs = []
    for suf in ["", "_B", "_C"]:
        src = os.path.join(HERE, "largos", "miniaturas", f"miniatura_{n:02d}{suf}.png")
        dst = os.path.join(OUT, "mini", f"m{n:02d}{suf or '_A'}.jpg")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-q:v", "3", dst], check=True)
        thumbs.append(f"mini/m{n:02d}{suf or '_A'}.jpg")
    items.append(dict(id=f"l{n}", tipo="largo", fecha=v["fecha"], hora=v["hora_ar"], hora_mx=v["hora_mx"], hora_co=v["hora_co"],
                      titulo=v["titulo"], alt=v["alt"], descripcion=desc, etiquetas=v["tags"], lista=v["playlist"],
                      shorts_rel=[f"{s['titulo']}" for s in v["shorts_rel"]], duracion=f"{int(dur // 60)}:{int(dur % 60):02d}",
                      archivo=f"video {n:02d} (mp4 original que te mandé por el chat)", subtitulos=f"subtitulos_{n}.srt",
                      thumbs=thumbs, comentario="¿Y a vos qué te pasó con esto? Te leo en los comentarios 👇", n=n))
items.sort(key=lambda x: (x["fecha"], x["hora"]))
json.dump(items, open(os.path.join(OUT, "plan.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(len(items), "items ·", sum(1 for i in items if i["tipo"] == "short"), "shorts ·", sum(1 for i in items if i["tipo"] == "largo"), "largos ·",
      os.path.getsize(os.path.join(OUT, "plan.json")) // 1024, "KB")
