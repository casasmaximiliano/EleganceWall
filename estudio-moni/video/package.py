"""Copia los MP4 con nombre por día de publicación, arma la planilla de subida y los zips por tandas."""
import csv, json, os, re, shutil, unicodedata, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out")
DEST = os.path.join(OUT, "listos")
os.makedirs(DEST, exist_ok=True)

def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-")[:60]

data = json.load(open(os.path.join(ROOT, "shorts.json"), encoding="utf-8"))
rows = sorted(data["shorts"], key=lambda s: s["dia"])
missing = []
with open(os.path.join(DEST, "subida.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Día", "Archivo", "Título", "Descripción", "Formato", "Serie"])
    for s in rows:
        src = os.path.join(OUT, "mp4", f"{s['n']:03d}.mp4")
        name = f"Dia{s['dia']:03d}_{slug(s['titulo'])}.mp4"
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(DEST, name))
        else:
            missing.append(s["n"])
        w.writerow([s["dia"], name, s["titulo"], f"{s['desc']}\n\nContenido educativo, no es asesoramiento financiero.\n\n{s['tags']} #shorts",
                    s["formato"], s["serie"]])

# zips de 25 videos en orden de publicación
files = sorted(x for x in os.listdir(DEST) if x.endswith(".mp4"))
for b in range(0, len(files), 25):
    part = files[b:b + 25]
    zp = os.path.join(OUT, f"Moni_shorts_dias_{b + 1:03d}-{b + len(part):03d}.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
        for x in part:
            z.write(os.path.join(DEST, x), x)
        z.write(os.path.join(DEST, "subida.csv"), "subida.csv")
    print(os.path.basename(zp), round(os.path.getsize(zp) / 1e6, 1), "MB")
print("faltan:", missing)
