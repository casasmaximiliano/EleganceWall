"""Video musical de una canción (horizontal 1920x1080 o vertical 1080x1920, 60 fps) con letra tipo karaoke.

La canción se genera aparte (ElevenLabs Music, con plan de composición en JSON: secciones, duración y letra).
Este script arma las escenas siguiendo las secciones, hace bailar a los personajes al ritmo y muestra la letra.

Uso: python3 cancion.py PLAN.json CANCION.mp3 SALIDA.mp4 [--vertical] [--desde S --hasta S]
Variables: las mismas del programa (BOMBOLIN_ESTILO=2, BOMBOLIN_SPRITES3D, BOMBOLIN_BG3D, BOMBOLIN_OBJ3D).
"""
import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import episode as E  # noqa: E402
import programa as P  # noqa: E402

R = E.R
SR = R.SR
BPM = 112

# Escenas de «Plic, plic, ploc» por sección: fondo, personajes y puesta en escena (misma sintaxis que staging.py)
ESCENAS = {
    "Intro": [("meadow", "PIPO LULA:calm", [dict(sp="raincloud", em="🌧️", mode="sky", x=0.5, y=0.16, size=0.24),
                                             dict(mode="rain", n=25)])],
    "Verse 1": [("room", "PIPO LULA:calm", [dict(mode="rain", n=30), dict(sp="umbrella", em="☂️", mode="ground", x=0.1, size=0.22)]),
                ("night", "PIPO LULA:sad ZUMBI", [dict(mode="rain", n=60), dict(mode="flash", lines=[1])])],
    "Chorus": [("meadow", "PIPO TOTO LULA:happy ZUMBI", [dict(mode="rain", n=25),
                                                        dict(mode="puddle", x=0.3, w=0.2, col=(80, 160, 240)),
                                                        dict(mode="puddle", x=0.7, w=0.22, col=(80, 160, 240)),
                                                        dict(em="💦", mode="orbit", who="TOTO", n=3, size=0.06)]),
               ("meadow", "PIPO TOTO LULA:happy ZUMBI", [dict(sp="rainbow", em="🌈", mode="sky", x=0.5, y=0.2, size=0.3),
                                                        dict(mode="puddle", x=0.5, w=0.3, col=(80, 160, 240))])],
    "Verse 2": [("night", "PIPO LULA:sad", [dict(mode="rain", n=60), dict(mode="flash", lines=[0])]),
                ("room", "PIPO LULA:calm TOTO", [dict(mode="dark", alpha=90),
                                                 dict(sp="teddy", em="🧸", mode="on", who="PIPO", at=(0.05, 0.62), w=0.55)])],
    "Bridge": [("meadow", "PIPO LULA:happy ZUMBI", [dict(sp="rainbow", em="🌈", mode="sky", x=0.5, y=0.2, size=0.34),
                                                   dict(mode="sparkle", who="LULA")])],
    "Final Chorus": [("meadow", "PIPO TOTO LULA:happy ZUMBI", [dict(sp="rainbow", em="🌈", mode="sky", x=0.5, y=0.18, size=0.3),
                                                              dict(mode="puddle", x=0.5, w=0.3, col=(80, 160, 240)),
                                                              dict(sp="kite", em="🪁", mode="on", who="PIPO", at=(0.95, -0.55), w=0.75, rot=-12)]),
                     ("meadow", "PIPO TOTO LULA:happy ZUMBI ABU", [dict(sp="rainbow", em="🌈", mode="sky", x=0.5, y=0.18, size=0.3),
                                                                  dict(mode="sparkle", who="PIPO")])],
    "Outro": [("meadow", "PIPO TOTO LULA:happy ZUMBI ABU", [dict(sp="rainbow", em="🌈", mode="sky", x=0.5, y=0.18, size=0.3)])],
}


def line_times(plan, align):
    """Tiempos reales de cada palabra (alineación de ElevenLabs) repartidos por renglón de la letra."""
    words = [w for w in align["words"] if w["text"].strip()]
    out, k = [], 0
    for sec in plan["composition_plan"]["sections"]:
        for line in sec["lines"]:
            n = len(line.split())
            ws = words[k:k + n]
            k += n
            out.append([(w["start"], w["end"]) for w in ws])
    return out


def build(plan, song, align=None):
    secs = plan["composition_plan"]["sections"]
    total = len(song) / SR
    lt_all = line_times(plan, align) if align else None
    # renglones con su inicio y fin reales (o repartidos en partes iguales si no hay alineación)
    rows, t, li = [], 0.0, 0
    for si_, sec in enumerate(secs):
        dur = sec["duration_ms"] / 1000
        for j, x in enumerate(sec["lines"]):
            if lt_all and lt_all[li]:
                st, en, ws = lt_all[li][0][0], lt_all[li][-1][1], lt_all[li]
            else:
                lt = dur / len(sec["lines"])
                st, en, ws = t + j * lt, t + (j + 1) * lt, None
            rows.append(dict(sec=si_, text=x, st=st, en=en, words=ws))
            li += 1
        t += dur
    segs, events, seen = [], [], {}
    sec_start = 0.0
    for si_, sec in enumerate(secs):
        name = sec["section_name"]
        k = seen.get(name, 0)
        seen[name] = k + 1
        opts = ESCENAS.get(name, ESCENAS["Chorus"])
        mine = [r for r in rows if r["sec"] == si_]
        nxt = [r for r in rows if r["sec"] > si_]
        sec_end = (nxt[0]["st"] - 0.25) if nxt else total
        if not mine:
            groups = [[]]
        else:
            per = max(1, math.ceil(len(mine) / len(opts)))
            groups = [mine[i:i + per] for i in range(0, len(mine), per)]
        for j, g in enumerate(groups):
            th, cast, stage = opts[(j + k) % len(opts)]
            chars, guests, mood = E.parse_cast(cast)
            t0 = sec_start if j == 0 else g[0]["st"] - 0.25
            t1 = (groups[j + 1][0]["st"] - 0.25) if j + 1 < len(groups) else sec_end
            sg = dict(kind="scene", theme=th, props=[], chars=chars, guests=guests, mood=mood, idx=0,
                      lines=[("ALL", r["text"]) for r in g] or [("ALL", "♪")], stage=stage, dance=BPM, t0=t0, t1=t1)
            segs.append(sg)
            for r in g:
                a = song[int(r["st"] * SR):int(r["en"] * SR)]
                events.append(dict(t=r["st"], a=a, sp="ALL", text=r["text"], seg=len(segs) - 1, words=r["words"]))
        sec_start = sec_end
    segs[-1]["t1"] = max(segs[-1]["t1"], total)
    return segs, events, total


class SongPainter(E.Painter):
    def subtitles(self, d, ev, tt):
        return  # la letra la dibuja frame() con los tiempos reales de cada palabra

    def frame(self, fi, hook=None):
        fr = super().frame(fi, hook)
        tt = fi / E.FPS
        if hook and self.H > self.W and tt >= 3.6:  # en el short el título va al empezar aunque no sea el segundo 0
            dh = ImageDraw.Draw(fr, "RGBA")
            self.text(dh, self.W // 2, 330, hook, int(118 * (1 + 0.04 * math.sin(tt * 9))), (255, 214, 60), sw=12,
                      maxw=self.W - 70)
        ev = None
        for e in self.events:
            if e["t"] - 0.15 <= tt < e["t"] + len(e["a"]) / SR + 0.6:
                ev = e
        if ev is not None and ev["text"] != "♪" and tt < ev["t"] + len(ev["a"]) / SR + 0.6:
            d = ImageDraw.Draw(fr, "RGBA")
            W, H = self.W, self.H
            words = ev["text"].split()
            dur = max(0.3, len(ev["a"]) / SR)
            if ev.get("words"):
                k = sum(1 for (ws, we) in ev["words"] if ws <= tt) - 1
            else:
                k = min(len(words) - 1, int((tt - ev["t"]) / dur * len(words) * 1.05))
            sz = int(0.062 * H) if W > H else 74
            f = E.font(E.F700, sz)
            full = " ".join(words)
            while d.textlength(full, font=f) > W - 100 and sz > 36:
                sz -= 4
                f = E.font(E.F700, sz)
            y = int(0.91 * H) if W > H else 1560
            x = (W - d.textlength(full, font=f)) / 2
            d.rounded_rectangle([x - 30, y - sz * 0.8, W - x + 30, y + sz * 0.8], 30, fill=(40, 30, 70, 150))
            for j, w in enumerate(words):
                col = (255, 214, 60) if j <= k else (255, 255, 255)
                d.text((x, y), w + " ", font=f, fill=col, anchor="lm", stroke_width=6, stroke_fill=E.INK)
                x += d.textlength(w + " ", font=f)
        return fr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("song")
    ap.add_argument("out")
    ap.add_argument("--vertical", action="store_true")
    ap.add_argument("--desde", type=float, default=0)
    ap.add_argument("--hasta", type=float, default=0)
    ap.add_argument("--titulo", default="¡PLIC, PLIC, PLOC!")
    a = ap.parse_args()
    E.FPS = 60
    plan = json.load(open(a.plan))
    wav = a.out + ".wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.song, "-ac", "1", "-ar", str(SR), wav], check=True)
    song = R.read_wav(wav)
    al = a.song[:-4] + "_align.json"
    align = json.load(open(al)) if os.path.exists(al) else None
    segs, events, total = build(plan, song, align)
    W, H = (1080, 1920) if a.vertical else (1920, 1080)
    ep = dict(E.EPISODES[3])
    f0 = int(a.desde * E.FPS)
    f1 = int((a.hasta or total) * E.FPS)
    nf = int(total * E.FPS) + 1
    Pn = SongPainter(W, H, ep, "es", segs, events, nf, a.vertical)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(E.FPS), "-i", "-",
           "-ss", str(a.desde), "-t", str((f1 - f0) / E.FPS), "-i", a.song,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-g", "120", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", a.out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        pr.stdin.write(Pn.frame(fi, a.titulo if fi - f0 < 3 * E.FPS else None).convert("RGB").tobytes())
    pr.stdin.close()
    pr.wait()
    os.remove(wav)
    print("OK", a.out, round((f1 - f0) / E.FPS, 1))


if __name__ == "__main__":
    main()
