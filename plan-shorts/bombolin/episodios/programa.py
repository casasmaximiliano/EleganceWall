"""Programa diario de «Bombolín y sus amigos»: 10 a 12 minutos, 1920x1080 a 60 fps, solo en español.

Cada programa = gancho + presentación + historia del día (4–5 min) + bloques de la biblioteca
(¿Sabías qué?, canciones, juegos, cuentos cortitos) + «¡Otra aventura!» (repite la historia del día anterior)
+ Libro de Descubrimientos + «¡Hoy aprendimos!» + anticipo de mañana. Además, 2 shorts verticales por programa.

Uso: python3 programa.py --voices DIR --out DIR --dias 1,2,3 [--what prog,short] [--jobs 4]
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import wave
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import episode as E  # noqa: E402
from extras_s1 import EXTRA, SHORTS  # noqa: E402
from staging import STAGE  # noqa: E402

E.FPS = 60
FPS = 60
R = E.R
SR = E.SR
START = dt.date(2026, 11, 26)
TARGET_MIN, TARGET_MAX = 630.0, 700.0  # contenido antes del cierre: 10:30 a 11:40 (con el cierre queda entre 11 y 12 min)

LIB = {
    "B": ["B01", "B04", "B02", "B03", "B08", "B09", "B05", "B06", "B10", "B07", "B11"],
    "F": ["F01", "F03", "F02", "F05", "F07", "F04", "F09", "F06", "F08", "F10", "F11", "F12", "F13", "F14", "F15"],
    "E": ["E01", "E02", "E04", "E03", "E05", "E06", "E07", "E08", "E09", "E10", "E11", "E12", "E13", "E14"],
    "C": ["C01", "C03", "C02", "C06", "C04", "C10", "C05", "C07", "C09", "C11", "C12", "C13", "C14", "C15", "C16",
          "C17", "C18", "D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08", "D09", "D10"],
}
LABEL = {"B": ("💡", "¿Sabías qué?"), "F": ("🎸", "¡Hora de cantar!"), "E": ("🎲", "¡Hora de jugar!"),
         "C": ("📚", "¡Un cuento cortito!"), "OTRA": ("⭐", "¡Otra aventura de Bombolín!")}
PATTERN = [("B", 1), ("F", 2), ("E", 2), ("C", 2), ("OTRA", 1), ("F", 2), ("E", 2), ("C", 2), ("B", 2), ("F", 2), ("E", 2), ("C", 2), ("F", 2), ("E", 2)]


def story(n):
    """Historia alargada del día n: escenas originales + escenas extra."""
    ep = E.EPISODES[n]
    base = list(ep["s"])
    extra = EXTRA.get(n, [])
    out = []
    for i, sc in enumerate(base):
        out.append(sc)
        out += [x for (k, x) in extra if k == i]
    return out


def scene_seg(sc, key=None):
    th, props, cast, lines = sc
    chars, guests, mood = E.parse_cast(cast)
    seg = dict(kind="scene", theme=th, props=props, chars=chars, guests=guests, mood=mood,
               lines=[(x[0].replace("_", " "), x[1]) for x in lines], idx=0)
    if E.STYLE2 and key in STAGE:
        seg["stage"] = [it for it in STAGE[key] if it["mode"] not in ("theme", "guest")]
        seg["guests"] = guests + [it["name"] for it in STAGE[key] if it["mode"] == "guest" and it["name"] not in guests]
        for it in STAGE[key]:
            if it["mode"] == "theme" and os.path.exists(os.path.join(E.BG3D_DIR or "", it["name"] + "_h.png")):
                seg["theme"] = it["name"]  # escenario más adecuado (p. ej. el baño) si ya está renderizado
    return seg


def lib_pick(kind, n, used):
    lst = LIB[kind]
    i = (n * 3) % len(lst)
    for k in range(len(lst)):
        cand = lst[(i + k) % len(lst)]
        if cand not in used:
            used.add(cand)
            return cand
    return lst[i]


def timeline(segs, vdir, cache):
    events, tt = [], 0.05
    for si, sg in enumerate(segs):
        sg["t0"] = tt if si else 0.0
        if sg["kind"] == "title":
            tt += 0.6
        for sp, text in sg["lines"]:
            if sp == "ALL":
                a = R.chorus(text, vdir, cache)
            elif sp.startswith("G:"):
                g = sp[2:]
                a = R.tts(R.GUESTS.get(g, (None, "GM"))[1], text, vdir, cache, echo=(g == "Eco"))
            else:
                a = R.tts(sp, text, vdir, cache)
            events.append(dict(t=tt, a=a, sp=sp, text=text, seg=si))
            tt += len(a) / SR + (0.45 if E.STYLE2 else 0.8)
        if sg["kind"] == "end":
            tt += 4.0
        elif sg["kind"] == "title":
            tt = max(tt, sg["t0"] + (3.6 if E.STYLE2 else 5.5))
        elif sg["kind"] == "bumper":
            tt = max(tt, sg["t0"] + 2.6)
        else:
            tt = max(tt, sg["t0"] + (2.4 if E.STYLE2 else 3.0)) + (0.7 if E.STYLE2 else 1.4)
        sg["t1"] = tt
    return events, tt + 0.3


def build_program(n, vdir, cache):
    ep = E.EPISODES[n]
    st = story(n)
    head = [scene_seg(st[0], (n, 0)),
            dict(kind="title", lines=[("ALL", "¡Bombolín y sus amigos!"), ("ABU", ep["tes"])])]
    head += [scene_seg(sc, (n, i + 1)) for i, sc in enumerate(st[1:])]
    # bloques de relleno (en orden), con su presentación
    used, blocks = set(), []
    for kind, count in PATTERN:
        icon, label = LABEL[kind]
        if kind == "OTRA":
            if n - 1 not in E.EPISODES:
                continue
            body = [scene_seg(sc, (n - 1, i)) for i, sc in enumerate(story(n - 1))]
            blocks.append([dict(kind="bumper", icon=icon, label=label, lines=[("ABU", label)])] + body)
            continue
        for j in range(count):
            body = E.library_segments(lib_pick(kind, n, used))
            bump = [dict(kind="bumper", icon=icon, label=label, lines=[("ABU", label)])] if j == 0 else []
            blocks.append(bump + body)
    nxt = E.EPISODES.get(n + 1)
    tease = f"Mañana: {nxt['tes']}." if nxt else "¡Mañana, una aventura nueva!"
    closing = [dict(kind="album", lines=[("PIPO", "¡Una figurita nueva para mi Libro de Descubrimientos!"),
                                         ("ABU", f"¡Hoy aprendimos que {ep['les']}!"),
                                         ("ALL", "¡Un, dos, tres, a descubrir otra vez!"), ("ABU", tease)]),
               dict(kind="end", lines=[])]
    # elegir cuántos bloques entran para llegar a 10:30–11:40 antes del cierre
    chosen = []
    _, t_head = timeline([dict(s) for s in head], vdir, cache)
    t = t_head
    for b in blocks:
        _, tb = timeline([dict(s) for s in b], vdir, cache)
        if t >= TARGET_MIN:
            break
        if t + tb > TARGET_MAX and b[0].get("label") == LABEL["OTRA"][1]:
            continue  # la repetición no entra entera: se saltea
        chosen.append(b)
        t += tb
    segs = [dict(s) for s in head] + [dict(s) for b in chosen for s in b] + [dict(s) for s in closing]
    events, total = timeline(segs, vdir, cache)
    return segs, events, total


def program_picks(n):
    """Bloques de la biblioteca que entran seguro en el programa del día n (antes de «¡Otra aventura!»)."""
    used, picks = set(), []
    for kind, count in PATTERN:
        if kind == "OTRA":
            break
        picks += [(kind, lib_pick(kind, n, used)) for _ in range(count)]
    return picks


def lib_short(n):
    """Tercer short del día: una canción, un juego o un dato del programa que no haya sido short antes."""
    prev = {lib_short(d) for d in range(1, n) if d in E.EPISODES} if n > 1 else set()
    order = ["F", "E", "B"]
    order = order[(n - 1) % 3:] + order[:(n - 1) % 3]
    picks = program_picks(n)
    for kind in order:
        for kd, sid in picks:
            if kd == kind and sid not in prev:
                return sid
    return picks[0][1]


def n_shorts(n):
    return len(SHORTS[n]) + 1


def build_short(n, k, vdir, cache):
    if k >= len(SHORTS[n]):
        sid = lib_short(n)
        segs = [dict(s) for s in E.library_segments(sid)]
        hook = R.get_short(sid)["hes"]
        a_theme = next((s.get("theme") for s in segs if s.get("theme")), "show")
    else:
        st = story(n)
        a, b, hook = SHORTS[n][k]
        segs = [scene_seg(sc, (n, a + j)) for j, sc in enumerate(st[a:b + 1])]
        a_theme = st[a][0]
    segs.append(dict(kind="scene", theme=a_theme, props=[E.EPISODES[n]["sticker"]], chars=["PIPO", "ABU"], guests=[],
                     mood="happy", lines=[("ABU", "¡El programa completo está en el canal!"),
                                          ("ALL", "¡Un, dos, tres, a descubrir otra vez!")], idx=-1, closing=True))
    events, total = timeline(segs, vdir, cache)
    return segs, events, total, hook


def render_job(job):
    kind, n, k, vdir, out, cache = job
    R.set_lang("es")
    ep = E.EPISODES[n]
    fecha = START + dt.timedelta(days=n - 1)
    if kind == "prog":
        W, H = 1920, 1080
        segs, events, total = build_program(n, vdir, cache)
        name = f"Bombolin_Dia{n:02d}_{fecha.strftime('%d-%m')}_{R.safe(ep['tes'])}"
        hook = ep["thumb"]["t1_es"] if E.STYLE2 else None
    else:
        W, H = 1080, 1920
        segs, events, total, hook = build_short(n, k, vdir, cache)
        name = f"Bombolin_Dia{n:02d}_Short{k + 1}"
    mix = E.mix_audio(segs, events, total, kind == "short")
    wav_p = os.path.join(cache, name + ".wav")
    with wave.open(wav_p, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    nf = int(total * FPS) + 1
    if os.environ.get("BOMBOLIN_MAXT"):
        nf = min(nf, int(float(os.environ["BOMBOLIN_MAXT"]) * FPS))
    P = E.Painter(W, H, ep, "es", segs, events, nf, kind == "short")
    mp4 = os.path.join(out, name + ".mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", wav_p, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-g", "120",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", mp4]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(nf):
        pr.stdin.write(P.frame(fi, hook).convert("RGB").tobytes())
    pr.stdin.close()
    pr.wait()
    os.remove(wav_p)
    if kind == "prog":
        E.write_srt(events, mp4[:-4] + ".srt")
        chapters, last = [], None
        for sg in segs:
            lab = {"title": "Presentación", "album": "Libro de Descubrimientos"}.get(sg["kind"])
            if sg["kind"] == "bumper":
                lab = sg["label"]
            if sg is segs[0]:
                lab = "¡Empieza!"
            if lab and lab != last:
                chapters.append((sg["t0"], lab))
                last = lab
        json.dump({"duration": total, "chapters": chapters, "fecha": fecha.isoformat()},
                  open(mp4[:-4] + ".json", "w"), ensure_ascii=False)
    return name, round(total, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voices", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dias", required=True)
    ap.add_argument("--what", default="prog,short")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cache = os.path.join(a.out, "_cache")
    os.makedirs(cache, exist_ok=True)
    R.set_lang("es")
    dias = [int(x) for x in a.dias.split(",")]
    jobs = []
    for n in dias:
        if "prog" in a.what:
            jobs.append(("prog", n, 0, a.voices, a.out, cache))
        if "short" in a.what:
            jobs += [("short", n, k, a.voices, a.out, cache) for k in range(n_shorts(n))]
    for n in dias:  # voces primero, en serie
        s, e, t = build_program(n, a.voices, cache)
        print(f"día {n}: {t / 60:.1f} min", flush=True)
        for k in range(n_shorts(n)):
            build_short(n, k, a.voices, cache)
    jobs.sort(key=lambda j: j[0] != "prog")
    with Pool(a.jobs) as p:
        for name, dur in p.imap_unordered(render_job, jobs):
            print("OK", name, dur, flush=True)


if __name__ == "__main__":
    main()
