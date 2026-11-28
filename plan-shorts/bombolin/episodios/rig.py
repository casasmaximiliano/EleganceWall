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
    def __init__(self, folder, name, box):
        self.dir = os.path.join(folder, name)
        self.cfg = json.load(open(os.path.join(self.dir, "rig.json")))
        self.N = int(900 * WS)
        self.cache = {}
        self.lru = OrderedDict()
        # recorte: el cuadro del sprite normal (box, en px de 900) con margen arriba y a los costados para brazos y cabeza
        x0, y0, x1, y1 = box
        mx, my = (x1 - x0) * 0.18, (y1 - y0) * 0.14
        self.crop = tuple(int(v * WS) for v in (max(0, x0 - mx), max(0, y0 - my), min(900, x1 + mx), y1))
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

    def _with_pupils(self, base, gx, gy):
        """base + pupilas desplazadas (gx, gy en -1..1), recortadas por la máscara de los ojos."""
        c = self.cfg
        rx = c.get("pupil_range_xy", {})
        r = c.get("pupil_range", 8)
        dx = gx * (rx.get("x", r) if gx > 0 else rx.get("-x", r)) * 0.85 * WS
        dy = gy * (rx.get("y", r) if gy > 0 else rx.get("-y", r)) * 0.85 * WS
        pup = self.img("pupil.png")
        lay = Image.new("RGBA", (self.N, self.N), (0, 0, 0, 0))
        for ex, ey in c["eyes"]:
            lay.alpha_composite(pup, (int(ex * WS + dx - pup.width / 2), int(ey * WS + dy - pup.height / 2)))
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
        box = None
        for f in sorted(os.listdir(ref)) if os.path.isdir(ref) else []:
            if f.endswith(".png") and "iris" not in f:
                a = Image.open(os.path.join(ref, f)).getchannel("A").point(lambda v: 255 if v > 60 else 0)
                b = a.getbbox()
                if b:
                    box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
        if box:
            rigs[name] = Rig(folder, name, box)
    return rigs
