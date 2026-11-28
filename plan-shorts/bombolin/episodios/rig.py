"""Personajes articulados: arma cada cuadro con las capas 3D de 3d/partes.py (cuerpo, cabeza, brazos, alas y pupilas).

Carpeta en BOMBOLIN_RIG (una subcarpeta por personaje con rig.json). Convenciones del rig:
- capas a lienzo completo 900x900, mismo encuadre que los sprites; se dibujan en el orden de rig.json["order"];
- X_front.png se dibuja además de X.png con la misma rotación (parte del brazo/ala que queda delante del cuerpo);
- pupil.png se pega centrada en cada ojo + la mirada, recortada con eyes_mask.png; con ojos cerrados no hay pupilas;
- ángulos antihorarios (PIL), L/R = izquierda/derecha de la pantalla.
"""
import json
import os
from collections import OrderedDict

from PIL import Image, ImageChops

WS = 0.7  # resolución de trabajo (0.7 x 900 = 630 px de lienzo)


class Rig:
    def __init__(self, folder, name, box, full=None):
        self.dir = os.path.join(folder, name)
        self.cfg = json.load(open(os.path.join(self.dir, "rig.json")))
        self.N = int(900 * WS)
        self.cache = {}
        self.lru = OrderedDict()
        # recorte: el cuadro del sprite normal (box, en px de 900) con margen arriba y a los costados para brazos y cabeza
        x0, y0, x1, y1 = box
        mx, my = (x1 - x0) * 0.18, (y1 - y0) * 0.14
        cx0, cy0, cx1, cy1 = max(0, x0 - mx), max(0, y0 - my), min(900, x1 + mx), y1
        if full:  # recorte más grande para lo que sale del cuerpo (lluvia, chispas), simétrico para no correr el centro
            ex = max(0, cx0 - full[0], full[2] - cx1)
            cx0, cx1 = max(0, cx0 - ex), min(900, cx1 + ex)
            cy0, cy1 = min(cy0, full[1]), max(cy1, full[3])
        self.crop = tuple(int(v * WS) for v in (cx0, cy0, cx1, cy1))
        self.core_h = (y1 - y0) * WS
        self.core_w = (x1 - x0) * WS
        self.pad_top = (y0 * WS) - self.crop[1]

    def img(self, fname):
        if fname not in self.cache:
            p = os.path.join(self.dir, fname)
            if not os.path.exists(p):
                self.cache[fname] = None
            else:
                im = Image.open(p).convert("RGBA")
                if fname != "pupil.png":
                    im = im.resize((self.N, self.N), Image.LANCZOS)
                else:
                    im = im.resize((max(1, int(im.width * WS)), max(1, int(im.height * WS))), Image.LANCZOS)
                self.cache[fname] = im
        return self.cache[fname]

    def _memo(self, key, fn):
        if key in self.lru:
            self.lru.move_to_end(key)
            return self.lru[key]
        v = fn()
        self.lru[key] = v
        if len(self.lru) > 260:
            self.lru.popitem(last=False)
        return v

    def _rot(self, fname, ang, pivot):
        ang = round(ang)
        if ang == 0:
            return self.img(fname)
        return self._memo((fname, ang), lambda: self.img(fname).rotate(
            ang, resample=Image.BICUBIC, center=(pivot[0] * WS, pivot[1] * WS)))

    def _eye_data(self):
        """Por ojo: máscara del blanco (solo ese ojo) y área visible del iris en reposo (A0)."""
        if not hasattr(self, "_eyes_d"):
            import numpy as np
            m = self.img("eyes_mask.png")
            pup = self.img("pupil.png")
            self._eyes_d = None
            if m is not None and pup is not None:
                ma = np.asarray(m.getchannel("A"), dtype=np.float32) / 255
                pa = np.asarray(pup.getchannel("A"), dtype=np.float32) / 255
                eyes = self.cfg["eyes"]
                cxs = [ex * WS for ex, _ in eyes]
                xs = np.arange(self.N)[None, :]
                data = []
                for i, (ex, ey) in enumerate(eyes):
                    # cada ojo se queda con los píxeles más cercanos a su centro que a los otros
                    own = np.ones_like(ma, dtype=bool)
                    for j, cj in enumerate(cxs):
                        if j != i:
                            own &= np.abs(xs - cxs[i]) <= np.abs(xs - cj)
                    mi = ma * own
                    data.append((mi, self._vis(mi, pa, ex * WS, ey * WS)))
                self._eyes_d = (data, pa, float(pa.sum()))
        return self._eyes_d

    def _vis(self, mi, pa, cx, cy):
        """Área del iris (pupil.png centrada en cx, cy) que queda dentro del blanco mi."""
        h, w = pa.shape
        x0, y0 = int(cx - w / 2), int(cy - h / 2)
        X0, Y0 = max(0, x0), max(0, y0)
        X1, Y1 = min(self.N, x0 + w), min(self.N, y0 + h)
        if X1 <= X0 or Y1 <= Y0:
            return 0.0
        return float((mi[Y0:Y1, X0:X1] * pa[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]).sum())

    def _with_pupils(self, base, gx, gy):
        """base + pupilas desplazadas (gx, gy en -1..1), recortadas por la máscara de los ojos.
        El recorrido de cada ojo se acorta hasta que el iris no quede más cortado que en reposo
        (área visible >= A0 - 2 %): así nunca se ve una «D» ni parece que bizquea."""
        c = self.cfg
        per = c.get("pupil_range_per_eye")
        rx = c.get("pupil_range_xy", {})
        r = c.get("pupil_range", 8)
        gx, gy = max(-1.0, min(1.0, gx)), max(-1.0, min(1.0, gy))
        pup = self.img("pupil.png")
        ed = self._eye_data()
        if ed is None:
            print("AVISO rig: sin eyes_mask/pupil, pupilas sin control", self.dir, flush=True)
        lay = Image.new("RGBA", (self.N, self.N), (0, 0, 0, 0))
        for i, (ex, ey) in enumerate(c["eyes"]):
            rr = per[i] if per and i < len(per) else rx
            dx = gx * (rr.get("x", r) if gx > 0 else rr.get("-x", r)) * WS
            dy = gy * (rr.get("y", r) if gy > 0 else rr.get("-y", r)) * WS
            cx, cy = ex * WS, ey * WS
            if ed is not None:
                data, pa, tot = ed
                mi, a0 = data[i]
                t = 1.0
                while t > 0 and self._vis(mi, pa, cx + dx * t, cy + dy * t) < a0 - 0.02 * tot:
                    t -= 0.05
                dx, dy = dx * max(0.0, t), dy * max(0.0, t)
            lay.alpha_composite(pup, (int(cx + dx - pup.width / 2), int(cy + dy - pup.height / 2)))
        mask = self.img("eyes_mask.png")
        if mask is not None:
            a = ImageChops.multiply(lay.getchannel("A"), mask.getchannel("A"))
            lay.putalpha(a)
        out = base.copy()
        out.alpha_composite(lay)
        return out

    def compose(self, m, c, mood=None, head=0.0, arm_l=0.0, arm_r=0.0, wings=0.0, gx=0.0, gy=0.0):
        cfg = self.cfg
        q = lambda v: round(v * 4) / 4  # noqa: E731
        gx, gy = q(gx), q(gy)
        has_head = "head" in cfg.get("order", [])
        body_f = "body.png" if has_head else (f"body_{mood}_m{m}_c{c}.png" if mood and
                                              os.path.exists(os.path.join(self.dir, f"body_{mood}_m{m}_c{c}.png"))
                                              else f"body_m{m}_c{c}.png")
        out = Image.new("RGBA", (self.N, self.N), (0, 0, 0, 0))
        for name in cfg.get("order", ["body"]):
            if name == "body":
                if not has_head and c == 0:
                    lay = self._memo(("bodyp", body_f, gx, gy), lambda: self._with_pupils(self.img(body_f), gx, gy))
                else:
                    lay = self.img(body_f)
            elif name == "head":
                hf = f"head_m{m}_c{c}.png"
                hp = cfg["head_pivot"]
                hd = round(head)

                def mk():
                    base = self._with_pupils(self.img(hf), gx, gy) if c == 0 else self.img(hf)
                    return base.rotate(hd, resample=Image.BICUBIC, center=(hp[0] * WS, hp[1] * WS)) if hd else base
                lay = self._memo(("head", hf, gx, gy, hd), mk)
            elif name.startswith("arm_"):
                side = name.split("_")[1]
                lay = self._rot(name + ".png", arm_l if side == "L" else arm_r, cfg["arms"][side]["pivot"])
            elif name.startswith("wing_"):
                side = name.split("_")[1]
                lay = self._rot(name + ".png", wings if side == "L" else -wings, cfg["wings"][side]["pivot"])
            else:
                lay = self.img(name + ".png")
            if lay is not None:
                out.alpha_composite(lay)
        return out.crop(self.crop)


def load_rigs(folder, sprites):
    """Un Rig por personaje con rig.json; el recorte se alinea con el sprite normal (mismo cuadro de 900 px)."""
    rigs = {}
    if not folder or not os.path.isdir(folder):
        return rigs
    for name in ("PIPO", "TOTO", "LULA", "ZUMBI", "ABU"):
        if not os.path.exists(os.path.join(folder, name, "rig.json")):
            continue
        ref = os.path.join(folder, name, "_ref")
        box = full = None
        for f in sorted(os.listdir(ref)) if os.path.isdir(ref) else []:
            if f.endswith(".png") and "iris" not in f:
                a = Image.open(os.path.join(ref, f)).getchannel("A").point(lambda v: 255 if v > 60 else 0)
                b = a.getbbox()
                if not b:
                    continue
                un = lambda p: b if p is None else (min(p[0], b[0]), min(p[1], b[1]), max(p[2], b[2]), max(p[3], b[3]))  # noqa: E731
                full = un(full)
                # el tamaño sale solo de las poses neutras: la lluvia (triste) y las chispas (enojada) no cuentan
                if not any(k in f for k in ("sad", "angry", "shy")):
                    box = un(box)
        if box:
            rigs[name] = Rig(folder, name, box, full)
    return rigs
