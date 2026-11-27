"""Genera los episodios largos (horizontal 1920x1080, subtítulos en .srt aparte) y los shorts verticales
(1080x1920, subtítulos grabados) de «Bombolín y sus amigos».

Uso:
  python3 episode.py --voices DIR --out DIR --lang es|en [--eps 1,2,3] [--what ep,short] [--jobs 4]
"""
import argparse
import math
import os
import re
import subprocess
import sys
import wave
import zlib
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "video"))
sys.path.insert(0, HERE)
import render as R  # noqa: E402  (voces, música, efectos, emojis)
from characters import build_sprites  # noqa: E402
from eps_1_5 import EPS_A  # noqa: E402
from eps_6_9 import EPS_B  # noqa: E402
from eps_10_13 import EPS_C  # noqa: E402

EPISODES = {e["n"]: e for e in EPS_A + EPS_B + EPS_C}
# Bloques fijos de cada episodio: una canción (formato F) y un juego (formato E) de la biblioteca de shorts
EXTRAS = {1: ("D09", "F03", "E13"), 2: ("C09", "F02", "E01"), 3: ("B05", "F05", "E06"), 4: ("D10", "F07", "E03"),
          5: ("C14", "F01", "E10"), 6: ("B08", "F04", "E05"), 7: ("C18", "F08", "E11"), 8: ("D07", "F12", "E04"),
          9: ("C05", "F11", "E07"), 10: ("D08", "F15", "E02"), 11: ("D03", "F10", "E09"), 12: ("B02", "F09", "E08"),
          13: ("B11", "F06", "E12")}
THEME_MAP = {"moon": "night", "sea": "sea", "show": "show"}


def library_segments(sid):
    """Convierte un short de la biblioteca (render.py) en escenas horizontales."""
    x = R.get_short(sid)
    out = []
    allv = R.norm(" ".join(sc.split("|")[0] for sc in x["s"]))
    fallback = []
    for kw, em in R.EMOJI_KW:
        mm = re.search(r"(?<![a-záéíóúñ])" + re.escape(kw.strip()), allv)
        if mm:
            fallback.append((mm.start(), em))
    fallback = [e for _, e in sorted(fallback)][:2]
    for sc in x["s"]:
        vis, txt = [p.strip() for p in sc.split("|", 1)]
        lines, chars, guests = [], [], []
        for raw, text in R.LINE_RE.findall(txt):
            key, name, qual = R.speaker_key(raw)
            sp = key
            lines.append((sp, text.strip()))
            if key in ("PIPO", "TOTO", "LULA", "ZUMBI") and key not in chars:
                chars.append(key)
            if key == "ABU" and "voz" not in qual and key not in chars:
                chars.append(key)
            if key == "ALL":
                for c in x["ch"]:
                    if c != "ABU" and c not in chars:
                        chars.append(c)
            if key.startswith("G:") and R.GUESTS.get(key[2:], (None,))[0] and key[2:] not in guests:
                guests.append(key[2:])
        v = R.norm(vis)
        nm = {"PIPO": "bombolín", "TOTO": "toto", "LULA": "lula", "ZUMBI": "zumbi"}
        for c in x["ch"]:
            if c in nm and nm[c] in v and c not in chars:
                chars.append(c)
        props = []
        for kw, em in R.EMOJI_KW:
            mm = re.search(r"(?<![a-záéíóúñ])" + re.escape(kw.strip()), v)
            if mm and em not in [e for _, e in props]:
                props.append((mm.start(), em))
        props = [e for _, e in sorted(props)][:3] or fallback
        th = R.theme_of(vis, x["f"])
        th = THEME_MAP.get(th, th)
        if "pizarra" in v:
            th = "board"
        if th not in ("meadow", "night", "xmas", "cave", "snow", "room", "board", "sea", "show"):
            th = "meadow"
        out.append(dict(kind="scene", theme=th, props=props, chars=chars or ["PIPO"], guests=guests,
                        mood=R.lula_mood(x, vis), lines=lines, idx=-2))
    return out
R.GUESTS["Reno"] = ("🦌", "GM")
R.LABEL_EN["Reno"] = "Reindeer"
FPS, SR = 24, R.SR
F700 = os.path.join(ROOT, "branding", "fonts", "fredoka-latin-700-normal.woff")
F600 = os.path.join(ROOT, "branding", "fonts", "fredoka-latin-600-normal.woff")
LOGO = os.path.join(ROOT, "branding", "logo_1080.png")
INK = (40, 35, 60)
TXT = {
    "es": dict(show="Bombolín y sus amigos", ep="Episodio", learned="¡Hoy aprendimos que {l}!", banner="¡HOY APRENDIMOS!",
               sticker="¡Una figurita nueva para mi Libro de Descubrimientos!", next="En el próximo episodio: {t}.",
               last="¡Nos vemos en la próxima temporada!", bye="¡Hasta la próxima!", jingle="¡Un, dos, tres, a descubrir otra vez!",
               intro="¡Bombolín y sus amigos!", full="¡El episodio completo está en el canal!",
               sing="¡Hora de cantar!", play="¡Hora de jugar!", know="¿Sabías qué?", tale="¡Un cuento cortito!"),
    "en": dict(show="Bombolín & Friends", ep="Episode", learned="Today we learned that {l}!", banner="TODAY WE LEARNED!",
               sticker="A new sticker for my Discovery Book!", next="In the next episode: {t}.",
               last="See you next season!", bye="See you next time!", jingle="One, two, three, come discover with me!",
               intro="Bombolín and friends!", full="Watch the full episode on the channel!",
               sing="Time to sing!", play="Time to play!", know="Did you know?", tale="A little story!"),
}
_fc = {}
_em_master, _em = {}, {}


def emoji(ch, size):
    """Emoji en caché: se dibuja una vez y se reescala a tamaños cuantizados (rápido)."""
    size = max(16, int(size) // 8 * 8)
    key = (ch, size)
    if key not in _em:
        if ch not in _em_master:
            _em_master[ch] = R.emoji(ch, 160)
        m = _em_master[ch]
        sc = size / max(m.size)
        _em[key] = m.resize((max(1, int(m.width * sc)), max(1, int(m.height * sc))), Image.LANCZOS)
    return _em[key]


_bgc = {}


def cached_bg(theme, W, H, seed):
    k = (theme, W, H, seed)
    if k not in _bgc:
        _bgc[k] = background(theme, W, H, seed)
    return _bgc[k]


def font(p, s):
    if (p, s) not in _fc:
        _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]


def vgrad(W, H, c1, c2):
    a = np.linspace(0, 1, H)[:, None, None]
    g = (np.array(c1)[None, None] * (1 - a) + np.array(c2)[None, None] * a).astype(np.uint8)
    return Image.fromarray(np.repeat(g, W, axis=1), "RGB")


# ------------------------------------------------------------------ fondos (coordenadas relativas)
SPRITE_DIR = os.environ.get("BOMBOLIN_SPRITES3D")
BG3D_DIR = os.environ.get("BOMBOLIN_BG3D")
# Estilo 2 (desde el día 2, 27/11): colores vivos, contorno, profundidad de campo, entradas, gestos y chispas
STYLE2 = os.environ.get("BOMBOLIN_ESTILO") == "2"
OBJ3D_DIR = os.environ.get("BOMBOLIN_OBJ3D")
_PROPS = {}


def prop_img(name, h=None, w=None):
    """Objeto 3D (cama, bañera, fideos…) recortado, con el mismo color y contorno que los personajes."""
    key = (name, h, w)
    if key in _PROPS:
        return _PROPS[key]
    base = _PROPS.get((name, None, None))
    if base is None:
        from PIL import ImageEnhance
        im = Image.open(os.path.join(OBJ3D_DIR, name + ".png")).convert("RGBA")
        a = im.getchannel("A")
        im = ImageEnhance.Contrast(ImageEnhance.Color(im.convert("RGB")).enhance(1.15)).enhance(1.08).convert("RGBA")
        im.putalpha(a)
        im = im.crop(a.point(lambda v: 255 if v > 40 else 0).getbbox())
        base = outline(im, px=5)
        _PROPS[(name, None, None)] = base
    if h:
        out = base.resize((max(1, int(base.width * h / base.height)), int(h)), Image.LANCZOS)
    elif w:
        out = base.resize((int(w), max(1, int(base.height * w / base.width))), Image.LANCZOS)
    else:
        out = base
    if len(_PROPS) > 400:
        _PROPS.clear()
        _PROPS[(name, None, None)] = base
    _PROPS[key] = out
    return out


def has_prop(it):
    return bool(it.get("sp") and OBJ3D_DIR and os.path.exists(os.path.join(OBJ3D_DIR, it["sp"] + ".png")))
SKY = {"meadow": ((120, 195, 255), (215, 240, 255)), "night": ((25, 35, 95), (95, 80, 160)),
       "xmas": ((25, 35, 95), (95, 80, 160)), "snow": ((165, 205, 250), (235, 245, 255)),
       "cave": ((60, 40, 95), (30, 20, 50)), "sea": ((110, 200, 250), (25, 90, 175)),
       "show": ((110, 55, 190), (60, 20, 120)), "room": ((255, 230, 210), (255, 220, 190))}


def outline(im, px=7, col=(45, 35, 70)):
    """Contorno oscuro suave alrededor del personaje: lo separa del fondo (estilo dibujo animado)."""
    from PIL import ImageFilter
    a = im.getchannel("A").point(lambda v: 255 if v > 90 else 0)
    big = a.filter(ImageFilter.MaxFilter(px * 2 + 1)).filter(ImageFilter.GaussianBlur(1.5))
    out = Image.new("RGBA", im.size, col + (0,))
    out.putalpha(big.point(lambda v: int(v * 0.85)))
    out.alpha_composite(im)
    return out


def load_3d_sprites(d):
    """Carga los sprites 3D y los recorta con el mismo cuadro por personaje (sin saltos entre estados)."""
    import glob as _g
    files = {}
    for p in _g.glob(os.path.join(d, "*.png")):
        parts = os.path.basename(p)[:-4].split("_")
        files[tuple(parts)] = p
    by_char = {}
    for k in files:
        by_char.setdefault(k[0], []).append(k)
    sp = {}
    for c, keys in by_char.items():
        from PIL import ImageEnhance
        ims = {}
        for k in keys:
            im = Image.open(files[k]).convert("RGBA")
            a = im.getchannel("A")
            if STYLE2:
                rgb = ImageEnhance.Contrast(ImageEnhance.Color(im.convert("RGB")).enhance(1.15)).enhance(1.08)
                im = rgb.convert("RGBA")
                im.putalpha(a)
                im = outline(im)
            else:
                rgb = ImageEnhance.Contrast(ImageEnhance.Color(im.convert("RGB")).enhance(1.35)).enhance(1.06)
                im = rgb.convert("RGBA")
                im.putalpha(a)
            ims[k] = im
        boxes = [im.getchannel("A").point(lambda v: 255 if v > 60 else 0).getbbox() for im in ims.values()]
        boxes = [b for b in boxes if b]
        box = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
        for k, im in ims.items():
            im = im.crop(box)
            if c == "LULA":
                sp[(c, k[1], int(k[2]), int(k[3]))] = im
            elif c == "ZUMBI":
                sp[(c, int(k[1]), int(k[2]), int(k[3]))] = im
            else:
                sp[(c, int(k[1]), int(k[2]))] = im
    return sp


_SHD = {}


def soft_shadow(w, strength):
    """Sombra elíptica difuminada (cacheada por tamaño): oscura al centro, suave en los bordes."""
    from PIL import ImageFilter
    w = max(20, int(w) // 8 * 8)
    q = round(strength * 10) / 10
    k = (w, q)
    if k not in _SHD:
        h = max(8, int(w * 0.16))
        pad = int(w * 0.12)
        m = Image.new("L", (w * 2 + pad * 2, h * 2 + pad * 2), 0)
        ImageDraw.Draw(m).ellipse([pad, pad, pad + w * 2, pad + h * 2], fill=int(255 * q))
        m = m.filter(ImageFilter.GaussianBlur(max(3, w * 0.07)))
        core = Image.new("L", m.size, 0)
        ImageDraw.Draw(core).ellipse([pad + w * 0.45, pad + h * 0.55, pad + w * 1.55, pad + h * 1.45], fill=int(255 * q * 0.6))
        core = core.filter(ImageFilter.GaussianBlur(max(2, w * 0.03)))
        from PIL import ImageChops
        a = ImageChops.add(m, core)
        im = Image.new("RGBA", m.size, (30, 25, 40, 0))
        im.putalpha(a)
        _SHD[k] = im
    return _SHD[k]


def vignette(im, k=0.28):
    W, H = im.size
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    m = 1 - k * np.clip(r - 0.6, 0, 1) ** 1.6
    arr = (np.asarray(im.convert("RGB")).astype(np.float32) * m[..., None]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def background(theme, W, H, seed):
    key = {"board": "meadow", "title": "meadow"}.get(theme, theme)
    if BG3D_DIR:
        p = os.path.join(BG3D_DIR, f"{key}_{'h' if W > H else 'v'}.png")
        if os.path.exists(p):
            c1, c2 = SKY.get(key, SKY["meadow"])
            im = vgrad(W, H, c1, c2).convert("RGBA")
            if key in ("night", "xmas"):
                rng = np.random.default_rng(seed)
                dd = ImageDraw.Draw(im)
                for _ in range(int(W * H / 9000)):
                    x, y = rng.integers(0, W), rng.integers(0, int(H * 0.5))
                    r = rng.integers(2, 5)
                    dd.ellipse([x, y, x + r, y + r], fill=(255, 250, 210, 255))
            im.alpha_composite(Image.open(p).convert("RGBA").resize((W, H)))
            from PIL import ImageEnhance
            im = ImageEnhance.Color(im.convert("RGB")).enhance(1.12 if STYLE2 else 1.2)
            if STYLE2 and theme not in ("title", "board"):
                from PIL import ImageFilter
                im = im.filter(ImageFilter.GaussianBlur(2.2))
                im = vignette(im)
            if theme == "title":
                from PIL import ImageFilter
                im = im.filter(ImageFilter.GaussianBlur(6))
            if theme == "board":
                d = ImageDraw.Draw(im, "RGBA")
                bx0, by0, bx1, by1 = board_box(W, H)
                d.rounded_rectangle([bx0 - 4, by0 + 14, bx1 + 30, by1 + 44], 30, fill=(0, 0, 0, 70))
                d.rounded_rectangle([bx0 - 18, by0 - 18, bx1 + 18, by1 + 18], 30, fill=(150, 100, 60))
                d.rounded_rectangle([bx0 - 18, by0 - 18, bx1 + 18, by0 - 4], 20, fill=(185, 130, 80))
                d.rounded_rectangle([bx0, by0, bx1, by1], 20, fill=(40, 90, 70))
                rng = np.random.default_rng(seed)
                for _ in range(6):
                    x, y = rng.uniform(bx0 + 40, bx1 - 200), rng.uniform(by0 + 30, by1 - 60)
                    d.arc([x, y, x + 150, y + 50], 180, 360, fill=(220, 240, 220, 120), width=4)
            return im
    return background2d(theme, W, H, seed)


def background2d(theme, W, H, seed):
    rng = np.random.default_rng(seed)
    gy = 0.72 * H if W > H else 0.70 * H  # horizonte
    if theme in ("night", "xmas"):
        im = vgrad(W, H, (35, 45, 115), (105, 90, 170))
    elif theme == "cave":
        im = vgrad(W, H, (70, 50, 110), (30, 20, 50))
    elif theme == "snow":
        im = vgrad(W, H, (175, 215, 255), (235, 245, 255))
    elif theme == "room":
        im = vgrad(W, H, (255, 236, 210), (255, 220, 190))
    elif theme == "sea":
        im = vgrad(W, H, (120, 210, 255), (25, 90, 175))
    elif theme == "show":
        im = vgrad(W, H, (125, 65, 205), (60, 20, 120))
    elif theme == "title":
        im = vgrad(W, H, (130, 205, 255), (255, 240, 200))
    else:
        im = vgrad(W, H, (125, 200, 255), (205, 240, 255))
    d = ImageDraw.Draw(im, "RGBA")
    m = min(W, H)
    if theme in ("meadow", "board", "title"):
        d.ellipse([0.80 * W, 0.06 * H, 0.80 * W + 0.17 * m, 0.06 * H + 0.17 * m], fill=(255, 225, 90))
        for cx, cy in [(0.12, 0.14), (0.45, 0.08), (0.68, 0.18)]:
            for dx, dy, r in [(0, 0, 0.055), (0.06, -0.02, 0.065), (0.125, 0, 0.05)]:
                x, y, rr = (cx + dx * m / W) * W, (cy + dy) * H, r * m
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 255, 255, 235))
        d.ellipse([-0.35 * W, gy - 0.06 * H, 0.65 * W, gy + 1.4 * H], fill=(125, 210, 115))
        d.ellipse([0.35 * W, gy - 0.02 * H, 1.35 * W, gy + 1.4 * H], fill=(100, 192, 98))
        for _ in range(int(W / 25)):
            x, y = rng.integers(0, W), rng.integers(int(gy + 0.04 * H), H)
            c = [(255, 120, 150), (255, 230, 90), (255, 255, 255), (180, 140, 255)][rng.integers(0, 4)]
            r = m * 0.008
            d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    if theme in ("night", "xmas"):
        for _ in range(int(W * H / 12000)):
            x, y = rng.integers(0, W), rng.integers(0, int(gy))
            r = rng.integers(2, 5)
            d.ellipse([x, y, x + r, y + r], fill=(255, 250, 200, 220))
        d.ellipse([0.80 * W, 0.07 * H, 0.80 * W + 0.15 * m, 0.07 * H + 0.15 * m], fill=(255, 245, 190))
        d.ellipse([0.78 * W, 0.05 * H, 0.78 * W + 0.13 * m, 0.05 * H + 0.13 * m], fill=(35, 45, 115))
        ground = (240, 245, 255) if theme == "xmas" else (70, 60, 130)
        d.ellipse([-0.3 * W, gy - 0.03 * H, 1.3 * W, gy + 1.5 * H], fill=ground)
        if theme == "xmas":
            for _ in range(int(W * H / 9000)):
                x, y = rng.integers(0, W), rng.integers(0, H)
                d.ellipse([x, y, x + 6, y + 6], fill=(255, 255, 255, 200))
            for i in range(14):  # guirnalda de luces
                x = W * (i + 0.5) / 14
                y = 0.04 * H + 0.03 * H * math.sin(i * 0.9)
                c = [(255, 90, 90), (255, 220, 80), (110, 210, 110), (90, 160, 255)][i % 4]
                d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=c)
    if theme == "sea":
        for _ in range(30):
            x, y, r = rng.integers(0, W), rng.integers(0, int(gy)), rng.integers(8, 28)
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, 120), width=4)
        d.rectangle([0, gy + 0.04 * H, W, H], fill=(240, 210, 140))
        for x in range(40, W, int(W / 10)):
            d.polygon([(x, gy + 0.04 * H), (x + 30, gy - 0.12 * H), (x + 60, gy + 0.04 * H)], fill=(60, 180, 110))
    if theme == "show":
        for i in range(14):
            a = i / 14 * 2 * math.pi
            d.polygon([(W / 2, H * 0.45), (W / 2 + 2 * W * math.cos(a), H * 0.45 + 2 * W * math.sin(a)),
                       (W / 2 + 2 * W * math.cos(a + 0.2), H * 0.45 + 2 * W * math.sin(a + 0.2))], fill=(255, 255, 255, 25))
        d.ellipse([0.15 * W, gy + 0.02 * H, 0.85 * W, gy + 0.22 * H], fill=(255, 200, 80), outline=(255, 255, 255), width=8)
    if theme == "snow":
        d.ellipse([-0.3 * W, gy - 0.05 * H, 1.3 * W, gy + 1.5 * H], fill=(255, 255, 255))
        for _ in range(int(W * H / 8000)):
            x, y = rng.integers(0, W), rng.integers(0, int(gy))
            d.ellipse([x, y, x + 7, y + 7], fill=(255, 255, 255, 230))
    if theme == "cave":
        for x in range(0, W, int(W / 20)):
            h = rng.integers(int(0.06 * H), int(0.2 * H))
            d.polygon([(x, 0), (x + W / 40, h), (x + W / 20, 0)], fill=(120, 100, 160))
        for _ in range(16):
            x, y = rng.integers(0, W), rng.integers(int(0.15 * H), int(gy))
            c = [(120, 255, 230, 200), (255, 150, 230, 200), (255, 240, 120, 200)][rng.integers(0, 3)]
            s = m * 0.02
            d.polygon([(x, y), (x + s, y + 2 * s), (x, y + 4 * s), (x - s, y + 2 * s)], fill=c)
        d.rectangle([0, gy + 0.02 * H, W, H], fill=(90, 70, 120))
    if theme == "room":
        d.rectangle([0, gy + 0.02 * H, W, H], fill=(200, 150, 110))
        for x in range(0, W, int(W / 14)):
            d.line([x, gy + 0.02 * H, x, H], fill=(180, 130, 95), width=4)
        wx = 0.70 * W
        d.rounded_rectangle([wx, 0.12 * H, wx + 0.18 * W, 0.12 * H + 0.30 * H], 20, fill=(170, 220, 255),
                            outline=(255, 255, 255), width=12)
        d.line([wx + 0.09 * W, 0.12 * H, wx + 0.09 * W, 0.42 * H], fill=(255, 255, 255), width=8)
        d.rounded_rectangle([0.08 * W, 0.18 * H, 0.22 * W, 0.40 * H], 14, fill=(255, 200, 120), outline=(200, 140, 90), width=8)
    if theme == "board":
        bx0, by0, bx1, by1 = (0.25 * W, 0.06 * H, 0.75 * W, 0.50 * H) if W > H else (0.06 * W, 0.20 * H, 0.94 * W, 0.52 * H)
        d.rounded_rectangle([bx0 - 18, by0 - 18, bx1 + 18, by1 + 18], 30, fill=(150, 100, 60))
        d.rounded_rectangle([bx0, by0, bx1, by1], 20, fill=(40, 90, 70))
        for _ in range(6):
            x, y = rng.uniform(bx0 + 40, bx1 - 200), rng.uniform(by0 + 30, by1 - 60)
            d.arc([x, y, x + 150, y + 50], 180, 360, fill=(220, 240, 220, 120), width=4)
    return im


def cam_crop(img, cx, cy, z, W, H):
    if z <= 1.001:
        return img
    cw, ch = W / z, H / z
    x0 = min(max(cx - cw / 2, 0), W - cw)
    y0 = min(max(cy - ch / 2, 0), H - ch)
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)


def board_box(W, H):
    return (0.25 * W, 0.06 * H, 0.75 * W, 0.50 * H) if W > H else (0.06 * W, 0.20 * H, 0.94 * W, 0.52 * H)


# ------------------------------------------------------------------ armado del episodio (audio + línea de tiempo)
def parse_cast(cast):
    chars, guests, mood = [], [], "calm"
    for tok in cast.split():
        if tok.startswith("G:"):
            guests.append(tok[2:].replace("_", " "))
        else:
            k, _, md = tok.partition(":")
            chars.append(k)
            if k == "LULA" and md:
                mood = md
    return chars, guests, mood


def build_timeline(ep, lang, vdir, cache, scene_range=None, short=False):
    """Devuelve (segmentos, eventos, audio_voz, duración). Cada segmento es una escena o tarjeta."""
    t = TXT[lang]
    li = 1 if lang == "es" else 2
    segs = []
    if scene_range is None:
        story = list(range(len(ep["s"])))
    else:
        story = list(range(scene_range[0], scene_range[1] + 1))

    def scene_seg(i):
        th, props, cast, lines = ep["s"][i]
        chars, guests, mood = parse_cast(cast)
        return dict(kind="scene", theme=th, props=props, chars=chars, guests=guests, mood=mood,
                    lines=[(x[0].replace("_", " "), x[1] if lang == "es" else x[2]) for x in lines],
                    idx=i)

    if short:
        for i in story:
            segs.append(scene_seg(i))
        segs.append(dict(kind="scene", theme=ep["s"][story[0]][0], props=[ep["sticker"]], chars=["PIPO", "ABU"],
                         guests=[], mood="happy", lines=[("ABU", t["full"]), ("ALL", t["jingle"])], idx=-1, closing=True))
    else:
        segs.append(scene_seg(story[0]))  # arranque directo (gancho), sin presentación antes
        segs.append(dict(kind="title", lines=[("ALL", t["intro"]), ("ABU", ep["tes"] if lang == "es" else ep["ten"])]))
        for i in story[1:]:
            segs.append(scene_seg(i))
        mini, song, game = EXTRAS[ep["n"]]
        lbl = t["know"] if mini.startswith("B") else t["tale"]
        segs.append(dict(kind="bumper", icon="📚" if not mini.startswith("B") else "💡", label=lbl, lines=[("ABU", lbl)]))
        segs += library_segments(mini)
        segs.append(dict(kind="bumper", icon="🎵", label=t["sing"], lines=[("ABU", t["sing"])]))
        segs += library_segments(song)
        segs.append(dict(kind="bumper", icon="🎲", label=t["play"], lines=[("ABU", t["play"])]))
        segs += library_segments(game)
        nxt = EPISODES.get(ep["n"] + 1)
        tease = t["next"].format(t=(nxt["tes"] if lang == "es" else nxt["ten"])) if nxt else t["last"]
        segs.append(dict(kind="album", lines=[("PIPO", t["sticker"]),
                                              ("ABU", t["learned"].format(l=(ep["les"] if lang == "es" else ep["len"]))),
                                              ("ALL", t["jingle"]), ("ABU", tease)]))
        segs.append(dict(kind="end", lines=[]))

    events = []
    tt = 0.05
    for si, sg in enumerate(segs):
        sg["t0"] = tt if si else 0.0
        if sg["kind"] in ("title",):
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
            tt += len(a) / SR + 0.6
        if sg["kind"] == "end":
            tt += 4.0
        elif sg["kind"] == "title":
            tt = max(tt, sg["t0"] + 5.5)
        elif sg["kind"] == "bumper":
            tt = max(tt, sg["t0"] + 2.6)
        else:
            tt = max(tt, sg["t0"] + 3.0) + (1.2 if not short else 0.2)
        sg["t1"] = tt
    total = tt + 0.3
    return segs, events, total


def mix_audio(segs, events, total, fmt_short):
    n = int(total * SR) + SR
    voice = np.zeros(n, np.float32)
    for ev in events:
        a = int(ev["t"] * SR)
        voice[a:a + len(ev["a"])] += ev["a"][: n - a]
    mus = R.music(total + 1, "F" if fmt_short else "A", False)[:n]
    # la música sube en la presentación, en las transiciones y en el final; baja con las voces
    env = np.full(n, 0.06, np.float32)
    for sg in segs:
        if sg["kind"] in ("title", "end", "bumper"):
            env[int(sg["t0"] * SR):int(sg["t1"] * SR)] = 0.16
    k = int(0.5 * SR)
    c = np.cumsum(np.concatenate([[0.0], env.astype(np.float64)]))
    lo = np.clip(np.arange(n) - k // 2, 0, n)
    hi = np.clip(np.arange(n) + k // 2, 0, n)
    env = ((c[hi] - c[lo]) / np.maximum(hi - lo, 1)).astype(np.float32)
    mix = voice + mus[:n] * env
    for sg in segs:
        if sg.get("kind") == "scene" and sg.get("theme") == "board":
            s = R.sfx("tin") * 0.3
            a = int((sg["t0"] + 0.1) * SR)
            mix[a:a + len(s)] += s[: max(0, n - a)]
        if sg.get("kind") == "album":
            s = R.sfx("yay") * 0.25
            a = int((sg["t0"] + 0.2) * SR)
            mix[a:a + len(s)] += s[: max(0, n - a)]
    for ev in events:
        if ev["sp"] == "TOTO" and ev["text"].startswith(("¡Uy", "Uh-oh")):
            s = R.sfx("boing") * 0.25
            a = int(ev["t"] * SR)
            mix[a:a + len(s)] += s[: max(0, n - a)]
    return np.tanh(mix * 1.1) * 0.95


def talk_env(events, nf):
    talk = {}
    hop = SR // FPS
    for ev in events:
        keys = ["PIPO", "TOTO", "LULA", "ZUMBI"] if ev["sp"] == "ALL" else [ev["sp"]]
        sq = ev["a"].astype(np.float64) ** 2
        nb = len(sq) // hop
        rms = np.sqrt(sq[:nb * hop].reshape(nb, hop).mean(1)) if nb else np.zeros(0)
        f0 = int(ev["t"] * FPS)
        for k in keys:
            arr = talk.setdefault(k, np.zeros(nf, np.float32))
            m = max(0, min(len(rms), nf - f0))
            arr[f0:f0 + m] = np.maximum(arr[f0:f0 + m], rms[:m])
    return talk


# ------------------------------------------------------------------ dibujo de cuadros
BASE_H = {"PIPO": 0.50, "TOTO": 0.45, "LULA": 0.31, "ZUMBI": 0.25, "ABU": 0.50}
LIFT = {"LULA": 0.33, "ZUMBI": 0.30}


class Painter:
    def __init__(self, W, H, ep, lang, segs, events, nf, short):
        self.W, self.H, self.ep, self.lang, self.segs, self.events, self.short = W, H, ep, lang, segs, events, short
        self.sp = load_3d_sprites(SPRITE_DIR) if SPRITE_DIR else build_sprites()
        self.heads = {}
        self.talk = talk_env(events, nf)
        self.nf = nf
        self.bgs = {}
        rng = np.random.default_rng(ep["n"])
        self.blink = {c: set(rng.integers(0, nf, max(1, nf // 70))) for c in BASE_H}
        self.logo = Image.open(LOGO).convert("RGBA") if os.path.exists(LOGO) else None
        self.prev_last = None
        self.cur_ev = None
        self.last_pos = {}
        self.hide = {}
        self.box = {}

    def bg(self, si, theme):
        if si not in self.bgs:
            self.bgs[si] = background(theme, self.W, self.H, self.ep["n"] * 100 + si)
        return self.bgs[si]

    def char_sprite(self, c, mouth, blink, fi, mood):
        if c == "LULA":
            return self.sp[(c, mood, mouth, blink)]
        if c == "ZUMBI":
            return self.sp[(c, int(fi / FPS * 20) % 2, mouth, blink)]
        return self.sp[(c, mouth, blink)]

    def draw_cast(self, frame, sg, fi, tt, speaking):
        W, H = self.W, self.H
        items = sg["chars"] + ["G:" + g for g in sg["guests"]]
        k = max(1, len(items))
        land = W > H
        sc = {1: 1.0, 2: 1.0, 3: 0.92, 4: 0.82, 5: 0.74}.get(k, 0.66) if land else {1: 1, 2: 0.95, 3: 0.8}.get(k, 0.62)
        base_y = 0.97 * H if land else 0.745 * H
        x0, x1 = (0.12 * W, 0.88 * W) if land else (0.0, W)
        pos = {}
        for i, it in enumerate(items):
            px = int(x0 + (x1 - x0) * (i + 0.5) / k) if land else int(W * (i + 1) / (k + 1))
            pos[it] = px
            if it.startswith("G:"):
                g = it[2:]
                em = R.GUESTS.get(g, ("✨",))[0] or "✨"
                talking = speaking == it
                amp = 1.12 + 0.05 * math.sin(tt * 18) if talking else 1.0
                e = emoji(em, int(0.36 * H * sc * amp) if land else int(300 * sc * amp))
                bob = int(8 * math.sin(tt * 3 + i))
                sh = ImageDraw.Draw(frame, "RGBA")
                sh.ellipse([px - e.width * 0.38, base_y - 0.02 * H - e.width * 0.07, px + e.width * 0.38,
                            base_y - 0.02 * H + e.width * 0.07], fill=(0, 0, 0, 55))
                frame.paste(e, (px - e.width // 2, int(base_y - e.height - 0.02 * H + bob)), e)
                self.heads[it] = (px, base_y - e.height * 0.7)
                self.box[it] = (px, int(base_y - e.height - 0.02 * H + bob), e.width, e.height)
                continue
            c = it
            arr = self.talk.get(c)
            lvl = arr[fi] if arr is not None and fi < len(arr) else 0
            is_sp = speaking == c or (speaking == "ALL" and c != "ABU")
            mouth = 1 if (is_sp and lvl > 0.06 and int(tt * 8) % 2 == 0) else 0
            bl = 1 if any((fi - d) in self.blink[c] for d in range(max(3, FPS // 8))) else 0
            spr = self.char_sprite(c, mouth, bl, fi, sg.get("mood", "calm"))
            bh = BASE_H[c] * H if land else {"PIPO": 540, "TOTO": 490, "LULA": 340, "ZUMBI": 280, "ABU": 400}[c]
            bounce = abs(math.sin(tt * 7)) * 0.02 * H if is_sp else abs(math.sin(tt * 2 + i)) * 0.006 * H
            sq = 1 + (0.035 * math.sin(tt * 14) if is_sp else 0)
            tilt = 0.0
            if STYLE2:
                bounce = 0.0
                if is_sp:  # habla «con el cuerpo»: se estira y se aplasta sin despegarse del suelo
                    sq = 1 + 0.045 * abs(math.sin(tt * 7))
                st_ = tt - sg.get("t0", 0)
                # entrada: cada personaje llega saltando desde su lado
                if st_ < 0.55 and not sg.get("closing"):
                    e_ = 1 - (1 - st_ / 0.55) ** 3
                    side = -1 if px < W / 2 else 1
                    px = int(px + side * (1 - e_) * 0.35 * W)
                    bounce += abs(math.sin(st_ * 11)) * 0.05 * H * (1 - e_)
                ev_ = self.cur_ev
                if ev_ is not None and is_sp:
                    since = tt - ev_["t"]
                    if ev_["text"].strip().endswith("!") and since < 0.45:  # salto de entusiasmo
                        bounce += math.sin(since / 0.45 * math.pi) * 0.035 * H
                    # se inclina hacia quien escucha
                    others = [p for o, p in self.last_pos.items() if o != c]
                    if others:
                        tgt = sum(others) / len(others)
                        tilt = 4.0 * (1 if tgt < px else -1) * (0.6 + 0.4 * math.sin(tt * 3))
                elif speaking and speaking in self.last_pos and speaking != c:
                    # los que escuchan miran (se corren un poco) hacia el que habla y asienten
                    dx = self.last_pos[speaking] - px
                    px = int(px + max(-1, min(1, dx / (0.3 * W))) * 0.015 * W)
                    sq *= 1 - 0.015 * abs(math.sin(tt * 4.5 + i))  # asiente
                    tilt = 2.5 * (1 if dx < 0 else -1)
                # respiración
                sq *= 1 + 0.012 * math.sin(tt * 2.4 + i * 1.7)
            hh = int(bh * sc * sq)
            ww = int(spr.width * hh / spr.height / sq)
            crouch = self.hide.get(c, 0.0) if STYLE2 else 0.0
            if crouch > 0:  # se agacha: más bajito y un poco más ancho, con los pies en el piso
                hh = int(hh * (1 - crouch))
                ww = int(ww * (1 + 0.25 * crouch))
            s2 = spr.resize((ww, hh), Image.BILINEAR)
            if tilt:
                s2 = s2.rotate(tilt, resample=Image.BICUBIC, expand=True)
                ww = s2.width
                hh = s2.height
            lift = LIFT.get(c, 0) * (H if land else 1000) * sc
            if STYLE2:
                # sombra de contacto suave pegada a los pies (más chica y clara cuando salta o vuela)
                air = min(1.0, (bounce + lift) / (0.12 * H))
                sw_ = int(ww * 0.46 * (1 - 0.45 * air))
                shd = soft_shadow(sw_, 0.55 * (1 - 0.6 * air))
                frame.alpha_composite(shd, (int(px - shd.width / 2), int(base_y - shd.height / 2)))
                sink = int(0.012 * hh)  # los pies «pisan» un poco la sombra
            else:
                sh = ImageDraw.Draw(frame, "RGBA")
                sw_ = ww * (0.36 if lift else 0.42) * (1 - min(0.3, bounce / (0.08 * H)))
                sh.ellipse([px - sw_, base_y - ww * 0.06, px + sw_, base_y + ww * 0.06], fill=(0, 0, 0, 45 if lift else 70))
                sink = 0
            top = int(base_y - hh - bounce - lift + sink)
            hide = self.hide.get(c, 0.0)
            if hide < 0:
                top += int(hide * hh)
            self.box[c] = (px, top, ww, hh)
            frame.paste(s2, (px - ww // 2, top), s2)
            self.heads[c] = (px, top + hh * (0.32 if c in ("PIPO", "ABU") else 0.42))
            pos[c] = px
        self.last_pos = dict(pos)
        return pos

    def ambient(self, bg, theme, tt):
        """Vida en el fondo: mariposas en la pradera, luciérnagas de noche, copos de nieve, brillitos en el cuarto."""
        W, H = self.W, self.H
        d = ImageDraw.Draw(bg, "RGBA")
        if theme in ("meadow", "board"):
            for k in range(3):
                x = (0.15 + 0.35 * k) * W + 0.12 * W * math.sin(tt * 0.45 + k * 2.1)
                y = (0.35 + 0.08 * k) * H + 0.06 * H * math.sin(tt * 0.9 + k)
                e = emoji("🦋", int(0.10 * H))
                fl = 0.35 + 0.65 * abs(math.sin(tt * 9 + k))
                e = e.resize((max(4, int(e.width * fl)), e.height))
                bg.paste(e, (int(x - e.width / 2), int(y - e.height / 2)), e)
        elif theme in ("night", "xmas"):
            for k in range(18):
                x = W * ((k * 0.618 + 0.05 * math.sin(tt * 0.3 + k)) % 1.0)
                y = H * (0.35 + 0.4 * ((k * 0.377) % 1.0)) + 10 * math.sin(tt + k)
                a = int(180 * (0.5 + 0.5 * math.sin(tt * 3 + k * 1.7)))
                r = 0.006 * H
                d.ellipse([x - r * 2, y - r * 2, x + r * 2, y + r * 2], fill=(255, 240, 120, a // 4))
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 170, a))
        elif theme == "snow":
            for k in range(40):
                x = W * ((k * 0.618) % 1.0) + 30 * math.sin(tt * 1.2 + k)
                y = (H * ((k * 0.377) % 1.0) + tt * 0.06 * H * (1 + (k % 3) * 0.4)) % H
                r = 0.004 * H * (1 + k % 3)
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 230))
        elif theme in ("room", "show"):
            for k in range(14):
                x = W * ((k * 0.618) % 1.0) + 20 * math.sin(tt * 0.6 + k)
                y = H * (0.15 + 0.55 * ((k * 0.377 + tt * 0.02) % 1.0))
                a = int(150 * (0.5 + 0.5 * math.sin(tt * 2.2 + k * 1.3)))
                r = 0.004 * H
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 230, a))

    def _base_y(self):
        return 0.97 * self.H if self.W > self.H else 0.745 * self.H

    def stage_back(self, layer, items, tt):
        """Lo que va detrás de los personajes: río, charcos y objetos apoyados en el piso."""
        W, H = self.W, self.H
        by = self._base_y()
        d = ImageDraw.Draw(layer, "RGBA")
        for it in items:
            m = it["mode"]
            if m == "river":
                y0, y1 = by - 0.30 * H, by - 0.17 * H
                pts = [(x, y0 + 8 * math.sin(x / 90 + tt * 2)) for x in range(0, W + 40, 40)]
                pts += [(x, y1 + 8 * math.sin(x / 110 + tt * 2.3)) for x in range(W, -40, -40)]
                d.polygon(pts, fill=(70, 160, 245, 235))
                for k in range(7):
                    x = (k * W / 6 + tt * 60) % (W + 200) - 100
                    yy = y0 + (y1 - y0) * (0.3 + 0.4 * ((k * 37) % 10) / 10)
                    d.arc([x, yy - 10, x + 120, yy + 10], 200, 340, fill=(235, 250, 255, 220), width=5)
            elif m == "puddle":
                cx, w = it["x"] * W, it["w"] * W
                cy = by - (0.10 if it.get("back") else 0.03) * H
                c = it.get("col", (120, 78, 40))
                d.ellipse([cx - w / 2, cy - w * 0.09, cx + w / 2, cy + w * 0.09], fill=c + (240,))
                d.ellipse([cx - w * 0.3, cy - w * 0.05, cx + w * 0.05, cy - w * 0.01],
                          fill=tuple(min(255, v + 50) for v in c) + (200,))
            elif m == "ground":
                sz = int(it["size"] * H)
                e = prop_img(it["sp"], h=sz) if has_prop(it) else emoji(it["em"], sz)
                cx = it["x"] * W
                bot = by - (0.10 * H if it.get("back") else 0.025 * H)
                shd = soft_shadow(int(e.width * 0.42), 0.45)
                layer.alpha_composite(shd, (int(cx - shd.width / 2), int(bot - shd.height / 2)))
                y = int(bot - e.height * 0.92 + 3 * math.sin(tt * 1.5 + cx))
                layer.alpha_composite(e, (int(cx - e.width / 2), max(0, y)))

    def stage_front(self, layer, items, tt):
        """Lo que va delante o encima de los personajes: cama, bañera, cosas pegadas, moscas, burbujas."""
        W, H = self.W, self.H
        by = self._base_y()
        for it in items:
            m = it["mode"]
            who = it.get("who")
            if who is not None and who not in self.box:
                continue
            if m == "front":
                px, top, ww, hh = self.box[who]
                if has_prop(it):
                    e = prop_img(it["sp"], w=int(it.get("w", 1.5) * ww))
                    shd = soft_shadow(int(e.width * 0.5), 0.5)
                    layer.alpha_composite(shd, (int(px - shd.width / 2), int(by - shd.height / 2)))
                    layer.alpha_composite(e, (int(px - e.width / 2), int(by + 0.01 * H - e.height)))
                else:
                    e = emoji(it["em"], int(it["size"] * hh * 1.45))
                    layer.alpha_composite(e, (int(px - e.width / 2), int(by - e.height * 0.86)))
            elif m == "on":
                px, top, ww, hh = self.box[who]
                if has_prop(it):
                    e = prop_img(it["sp"], w=max(16, int(it.get("w", 0.4) * ww)))
                else:
                    e = emoji(it["em"], max(24, int(it["size"] * hh)))
                if it.get("rot"):
                    e = e.rotate(it["rot"] + 3 * math.sin(tt * 3), resample=Image.BICUBIC, expand=True)
                dx, dy = it["at"]
                y = top + dy * hh - (e.height if it.get("anchor") == "bottom" else e.height / 2)
                layer.alpha_composite(e, (int(px + dx * ww - e.width / 2), max(0, int(y))))
            elif m == "orbit":
                hx, hy = self.heads.get(who, (self.box[who][0], self.box[who][1]))
                ww = self.box[who][2]
                n = it.get("n", 3)
                for k in range(n):
                    a = tt * 2.6 + k * 2 * math.pi / n
                    r = 0.75 * ww
                    e = prop_img(it["sp"], h=max(16, int(it["size"] * H))) if has_prop(it) else emoji(it["em"], max(20, int(it["size"] * H)))
                    x = hx + r * math.cos(a)
                    y = hy - 0.16 * H + 0.25 * r * math.sin(a) + 6 * math.sin(tt * 9 + k)  # por arriba de la cabeza
                    layer.alpha_composite(e, (int(x - e.width / 2), max(0, int(y - e.height / 2))))
            elif m == "rise":
                n = it.get("n", 8)
                for k in range(n):
                    ph = (tt * 0.13 + k * 0.618) % 1.0
                    x = W * ((k * 0.381) % 1.0) + 40 * math.sin(tt * 1.3 + k)
                    y = by - ph * H * 0.95
                    sz = int((0.06 + 0.05 * ((k * 7) % 5) / 5) * H)
                    e = prop_img(it["sp"], h=sz) if has_prop(it) else emoji(it["em"], sz)
                    if 0 < y < H:
                        layer.alpha_composite(e, (int(x - e.width / 2), int(y - e.height / 2)))
            elif m == "sparkle":
                hd = self.heads.get(who)
                if hd:
                    cyc = int(tt / 1.2)
                    self.sparkles(layer, hd, tt - cyc * 1.2, cyc * 7.31 + 1)

    def sparkles(self, layer, head, since, seed):
        if since < 0 or since > 1.2:
            return
        d = ImageDraw.Draw(layer, "RGBA")
        rng = np.random.default_rng(int(seed * 1000) % 100000)
        hx, hy = head
        cols = [(255, 214, 60), (255, 90, 150), (90, 200, 255), (140, 230, 90), (190, 120, 255)]
        k = since / 1.2
        for j in range(14):
            ang = rng.uniform(0, 2 * math.pi)
            ang = math.pi + ang / 2  # solo arriba y a los costados de la cabeza, nunca sobre la cara
            dist = (0.16 + 0.10 * rng.random()) * self.H * (0.6 + 0.6 * k)
            x = hx + math.cos(ang) * dist
            y = hy - 0.10 * self.H + math.sin(ang) * dist * 0.6
            r = (0.012 * self.H) * (1 - k) * (0.6 + rng.random())
            if r < 1:
                continue
            c = cols[j % len(cols)] + (int(255 * (1 - k)),)
            d.polygon([(x, y - r * 2), (x + r * 0.6, y - r * 0.6), (x + r * 2, y), (x + r * 0.6, y + r * 0.6),
                       (x, y + r * 2), (x - r * 0.6, y + r * 0.6), (x - r * 2, y), (x - r * 0.6, y - r * 0.6)], fill=c)

    def draw_props(self, frame, sg, st, tt):
        W, H = self.W, self.H
        land = W > H
        if sg["theme"] == "board":
            bx0, by0, bx1, by1 = board_box(W, H)
            n = len(sg["props"])
            for i, em in enumerate(sg["props"]):
                if st < 0.2 + i * 0.7:
                    continue
                k = min(1, (st - 0.2 - i * 0.7) / 0.25)
                e = emoji(em, int((by1 - by0) * 0.55 * (0.6 + 0.4 * k)))
                cx = bx0 + (bx1 - bx0) * (i + 1) / (n + 1)
                cy = (by0 + by1) / 2 + 10 * math.sin(tt * 2 + i)
                frame.paste(e, (int(cx - e.width / 2), int(cy - e.height / 2)), e)
            return
        if sg.get("stage"):
            return
        if STYLE2 and sg["props"]:
            return  # se dibujan en el piso desde stage_auto (capa de personajes)
        spots = [(0.20, 0.30), (0.80, 0.33), (0.50, 0.22)] if land else [(0.24, 0.33), (0.76, 0.36), (0.5, 0.5)]
        for i, em in enumerate(sg["props"][:3]):
            if st < 0.15 + i * 0.8:
                continue
            k = min(1, (st - 0.15 - i * 0.8) / 0.25)
            sz = int((0.20 * H if land else 230) * (0.6 + 0.4 * k))
            e = emoji(em, max(30, sz))
            cx, cy = spots[i]
            frame.paste(e, (int(cx * W - e.width / 2), int(cy * H - e.height / 2 + 14 * math.sin(tt * 2.2 + i))), e)

    def text(self, d, x, y, s, size, fill, sw=None, maxw=None, path=F700):
        f = font(path, size)
        maxw = maxw or self.W - 80
        while d.textlength(s, font=f) > maxw and size > 24:
            size -= 4
            f = font(path, size)
        d.text((x, y), s, font=f, fill=fill, anchor="mm", stroke_width=sw if sw is not None else max(3, size // 10),
               stroke_fill=INK)

    def title_card(self, frame, sg, st):
        W, H = self.W, self.H
        d = ImageDraw.Draw(frame, "RGBA")
        if self.logo:
            sz = int(0.46 * min(W, H) * (0.85 + 0.15 * min(1, st / 0.4)))
            lg = self.logo.resize((sz, sz), Image.LANCZOS)
            frame.paste(lg, (W // 2 - sz // 2, int(0.30 * H - sz / 2)), lg)
        t = TXT[self.lang]
        self.text(d, W // 2, int(0.62 * H), t["show"], int(0.085 * H), (255, 214, 60), sw=8)
        title = self.ep["tes"] if self.lang == "es" else self.ep["ten"]
        self.text(d, W // 2, int(0.76 * H), title, int(0.065 * H), (255, 255, 255), sw=7)
        self.text(d, W // 2, int(0.86 * H), f"{t['ep']} {self.ep['n']}", int(0.04 * H), (255, 255, 255), sw=5, path=F600)

    def album(self, frame, sg, st, tt):
        W, H = self.W, self.H
        d = ImageDraw.Draw(frame, "RGBA")
        land = W > H
        bx0, by0, bx1, by1 = (0.30 * W, 0.08 * H, 0.95 * W, 0.80 * H) if land else (0.05 * W, 0.12 * H, 0.95 * W, 0.50 * H)
        d.rounded_rectangle([bx0, by0, bx1, by1], 30, fill=(150, 90, 60))
        mid = (bx0 + bx1) / 2
        d.rounded_rectangle([bx0 + 20, by0 + 20, mid - 6, by1 - 20], 18, fill=(255, 250, 235))
        d.rounded_rectangle([mid + 6, by0 + 20, bx1 - 20, by1 - 20], 18, fill=(255, 250, 235))
        cols, rows = 4, 4
        cw = (bx1 - bx0 - 60) / cols
        rh = (by1 - by0 - 60) / rows
        page0 = (self.ep["n"] - 1) // 16 * 16 + 1
        for n in range(page0, page0 + 16):
            if n not in EPISODES:
                continue
            r, c = divmod(n - page0, cols)
            cx = bx0 + 30 + cw * (c + 0.5)
            cy = by0 + 30 + rh * (r + 0.5)
            d.rounded_rectangle([cx - cw * 0.38, cy - rh * 0.38, cx + cw * 0.38, cy + rh * 0.38], 14,
                                outline=(220, 200, 170), width=4)
            if n < self.ep["n"] or (n == self.ep["n"] and st > 1.0):
                pop = 1.0
                if n == self.ep["n"]:
                    pop = min(1.25, 0.5 + (st - 1.0) * 2) if st < 1.6 else 1.0
                e = emoji(EPISODES[n]["sticker"], int(min(cw, rh) * 0.6 * pop))
                frame.paste(e, (int(cx - e.width / 2), int(cy - e.height / 2)), e)
        if any(ev["text"].startswith(TXT[self.lang]["learned"][:10]) and ev["t"] <= self.now < ev["t"] + len(ev["a"]) / SR
               for ev in self.events):
            self.text(d, W // 2 if not land else int(0.62 * W), int(0.90 * H) if land else int(0.07 * H),
                      TXT[self.lang]["banner"], int(0.075 * H) if land else 80, (255, 214, 60), sw=8)

    def subtitles(self, d, ev, tt):
        W, H = self.W, self.H
        words = ev["text"].split()
        dur = max(0.3, len(ev["a"]) / SR)
        w = np.array([len(x) + 2 for x in words], float)
        cum = np.cumsum(w) / w.sum() * dur
        wi = min(int(np.searchsorted(cum, tt - ev["t"])), len(words) - 1)
        chunks = R.chunk_words(words)
        ch = next(c for c in chunks if wi in c)
        key = ev["sp"]
        col = R.COLOR.get(key, R.COLOR["GUEST"]) if not key.startswith("G:") else R.COLOR["GUEST"]
        sz = 84
        f = font(F700, sz)
        full = " ".join(words[j] for j in ch)
        while d.textlength(full, font=f) > W - 80 and sz > 50:
            sz -= 4
            f = font(F700, sz)
        xx = (W - d.textlength(full, font=f)) / 2
        y = 1560
        for j in ch:
            wt = words[j] + " "
            d.text((xx, y), wt, font=f, fill=col if j == wi else (255, 255, 255), anchor="lm", stroke_width=8,
                   stroke_fill=INK)
            xx += d.textlength(wt, font=f)

    def camera(self, si, sg, st, tt, ev, speaking):
        """Plano general / medio / primer plano según la frase, siempre con un movimiento lento."""
        W, H = self.W, self.H
        land = W > H
        idx = sum(1 for e in self.events if e["seg"] == si and e["t"] <= tt) - 1
        t_shot = tt - next((e["t"] for e in reversed(self.events) if e["seg"] == si and e["t"] <= tt), sg["t0"])
        drift = 1 + 0.035 * min(1.0, t_shot / 4.0)
        target = speaking if speaking in self.heads else None
        kind = 0 if (idx < 0 or target is None or sg.get("closing")) else (idx % 3)
        if kind == 0:  # general con paneo suave
            z = 1.04 * drift
            cx = W / 2 + 0.03 * W * math.sin(tt * 0.35 + si)
            cy = H * (0.55 if land else 0.56)
        else:
            hx, hy = self.heads[target]
            z = (1.35 if kind == 1 else 1.75) * drift if land else (1.15 if kind == 1 else 1.38) * drift
            cx = hx + 0.01 * W * math.sin(tt * 0.5)
            cy = hy + (H / z) * (0.22 if kind == 1 else 0.08)
        return cx, cy, z

    def frame(self, fi, hook=None):
        tt = fi / FPS
        self.now = tt
        W, H = self.W, self.H
        si = next((i for i, s in enumerate(self.segs) if tt < s["t1"]), len(self.segs) - 1)
        sg = self.segs[si]
        st = tt - sg["t0"]
        ev = None
        for e in self.events:
            if e["t"] - 0.05 <= tt < e["t"] + len(e["a"]) / SR + 0.3:
                ev = e
        speaking = ev["sp"] if ev else None
        self.cur_ev = ev
        if sg["kind"] == "title":
            fr = cached_bg("title", W, H, 7).copy()
            self.title_card(fr, sg, st)
        elif sg["kind"] == "bumper":
            fr = cached_bg("show", W, H, 11).copy()
            e = emoji(sg["icon"], int(0.40 * min(W, H) * (0.8 + 0.2 * min(1, st / 0.3))))
            fr.paste(e, (W // 2 - e.width // 2, int(0.38 * H - e.height / 2)), e)
            dd = ImageDraw.Draw(fr, "RGBA")
            self.text(dd, W // 2, int(0.75 * H), sg["label"], int(0.10 * min(W, H) * 1.2), (255, 214, 60), sw=9)
        elif sg["kind"] in ("album", "end"):
            fr = self.bg(si, "room").copy()
            if sg["kind"] == "album":
                self.album(fr, sg, st, tt)
                fake = dict(chars=["PIPO", "TOTO", "LULA", "ZUMBI", "ABU"] if W < H else ["PIPO", "ABU"], guests=[],
                            mood="happy")
                if W > H:
                    sub = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    self.W = int(W * 0.30)
                    self.draw_cast(sub, fake, fi, tt, speaking)
                    self.W = W
                    fr.paste(sub, (int(0.02 * W), 0), sub)
                else:
                    self.draw_cast(fr, fake, fi, tt, speaking)
            else:
                fr = cached_bg("title", W, H, 9).copy()
                d = ImageDraw.Draw(fr, "RGBA")
                if self.logo:
                    sz = int(0.5 * min(W, H))
                    lg = self.logo.resize((sz, sz), Image.LANCZOS)
                    fr.paste(lg, (W // 2 - sz // 2, int(0.36 * H - sz / 2)), lg)
                self.text(d, W // 2, int(0.74 * H), TXT[self.lang]["bye"], int(0.08 * H), (255, 214, 60), sw=8)
                self.text(d, W // 2, int(0.86 * H), TXT[self.lang]["show"], int(0.05 * H), (255, 255, 255), sw=6)
        else:
            theme = sg["theme"]
            bgl = self.bg(si, theme).copy()
            self.draw_props(bgl, sg, st, tt)
            if STYLE2:
                self.ambient(bgl, theme, tt)
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            self.heads = {}
            self.box = {}
            stage = sg.get("stage") or []
            if STYLE2 and not stage and sg.get("theme") != "board" and sg.get("props"):
                xs = [0.10, 0.90, 0.50] if not sg.get("closing") else [0.88]
                stage = [dict(em=e, mode="ground", x=x, size=0.15 if W > H else 0.10)
                         for e, x in zip(sg["props"], xs)][:2]
            li = sum(1 for e in self.events if e["seg"] == si and e["t"] <= tt) - 1
            items = [it for it in stage if li >= it.get("frm", 0)]
            self.hide = {it["who"]: it.get("hide", 0.0) for it in items if it["mode"] == "front" and it.get("hide")}
            if items:
                self.stage_back(layer, items, tt)
            pos = self.draw_cast(layer, sg, fi, tt, speaking)
            if items:
                self.stage_front(layer, items, tt)
            if STYLE2 and ev is not None and ev["text"].strip().endswith("!") and speaking in self.heads:
                self.sparkles(layer, self.heads[speaking], tt - ev["t"], ev["t"])
            cx, cy, z = self.camera(si, sg, st, tt, ev, speaking)
            if STYLE2 and ev is not None:
                since = tt - ev["t"]
                if 0 <= since < 0.35:
                    z *= 1 + 0.03 * (1 - since / 0.35)
            # paralaje: el fondo se mueve y acerca menos que los personajes (sensación de profundidad)
            zb = 1 + (z - 1) * 0.55
            bx, by = W / 2 + (cx - W / 2) * 0.55, H / 2 + (cy - H / 2) * 0.55
            fr = cam_crop(bgl, bx, by, zb, W, H).convert("RGBA")
            fr.alpha_composite(cam_crop(layer, cx, cy, z, W, H))
            fr = fr.convert("RGB")
        d = ImageDraw.Draw(fr, "RGBA")
        if ev and sg["kind"] == "scene" and R.is_countdown(ev["text"]):
            dur = len(ev["a"]) / SR
            k = int(min(2, (tt - ev["t"]) / (dur / 3)))
            ph = ((tt - ev["t"]) % (dur / 3)) / (dur / 3)
            r = int((0.16 if W > H else 0.12) * H * (1 + 0.15 * (1 - ph)))
            cx, cy = W // 2, int(0.36 * H) if W > H else 800
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 90, 120, 235), outline=(255, 255, 255), width=12)
            self.text(d, cx, cy, str(3 - k), int(r * 1.3), (255, 255, 255), sw=10)
        # transición: en estilo 2, un círculo que se abre desde el centro (como en los dibujos animados)
        if STYLE2 and si > 0 and st < 0.34 and sg["kind"] != "end":
            k = st / 0.34
            r = int((0.05 + 0.95 * (1 - (1 - k) ** 3)) * math.hypot(W, H) / 2)
            mask = Image.new("L", (W, H), 255)
            ImageDraw.Draw(mask).ellipse([W // 2 - r, H // 2 - r, W // 2 + r, H // 2 + r], fill=0)
            fr.paste(Image.new("RGB", (W, H), (255, 200, 40)), (0, 0), mask)
            d = ImageDraw.Draw(fr, "RGBA")
            d.ellipse([W // 2 - r, H // 2 - r, W // 2 + r, H // 2 + r], outline=(255, 255, 255), width=14)
        elif not STYLE2 and si > 0 and st < 0.3 and sg["kind"] != "end":
            a = int(110 * (1 - st / 0.3))
            d.rectangle([0, 0, W, H], fill=(255, 255, 255, a))
        if STYLE2 and not self.short and hook and tt < 3.0:
            # gancho del programa: el título corto del día salta en grande al empezar
            pop = min(1.0, tt / 0.25)
            sz = int(0.13 * H * (0.6 + 0.4 * pop) * (1 + 0.03 * math.sin(tt * 9)))
            self.text(d, W // 2, int(0.15 * H), hook, sz, (255, 214, 60), sw=14, maxw=W - 120)
        if self.short:
            d.rounded_rectangle([W // 2 - 260, 40, W // 2 + 260, 110], 35, fill=(255, 255, 255, 215))
            d.text((W // 2, 75), TXT[self.lang]["show"], font=font(F700, 40), fill=(60, 150, 100), anchor="mm")
            if hook and tt < 3.6:
                self.text(d, W // 2, 330, hook, int(118 * (1 + 0.04 * math.sin(tt * 9))), (255, 214, 60), sw=12,
                          maxw=W - 70)
            if ev:
                self.subtitles(d, ev, tt)
        return fr


# ------------------------------------------------------------------ salida
def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def wrap2(text, n=42):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    return "\n".join(lines)


def write_srt(events, path, offset=0.0):
    out = []
    for i, ev in enumerate(events, 1):
        a, b = ev["t"] + offset, ev["t"] + offset + len(ev["a"]) / SR + 0.2
        out.append(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{wrap2(ev['text'])}\n")
    open(path, "w", encoding="utf-8").write("\n".join(out))


def slug_title(ep, lang):
    t = ep["tes"] if lang == "es" else ep["ten"]
    return R.safe(t)


def render_job(job):
    kind, n, k, lang, vdir, out, cache = job
    R.set_lang(lang)
    ep = EPISODES[n]
    tag = "ES" if lang == "es" else "EN"
    if kind == "ep":
        W, H = 1920, 1080
        segs, events, total = build_timeline(ep, lang, vdir, cache)
        name = f"Bombolin_E{n:02d}_{slug_title(ep, lang)}_{tag}"
        hook = None
    else:
        W, H = 1080, 1920
        a, b, hes, hen = ep["shorts"][k]
        segs, events, total = build_timeline(ep, lang, vdir, cache, scene_range=(a, b), short=True)
        name = f"Bombolin_E{n:02d}_Short{k + 1}_{tag}"
        hook = hes if lang == "es" else hen
    mix = mix_audio(segs, events, total, kind == "short")
    wav_p = os.path.join(cache, name + ".wav")
    with wave.open(wav_p, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    nf = int(total * FPS) + 1
    P = Painter(W, H, ep, lang, segs, events, nf, kind == "short")
    mp4 = os.path.join(out, name + ".mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", wav_p, "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest", "-movflags", "+faststart", mp4]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(nf):
        pr.stdin.write(P.frame(fi, hook).convert("RGB").tobytes())
    pr.stdin.close()
    pr.wait()
    os.remove(wav_p)
    if kind == "ep":
        write_srt(events, os.path.join(out, name + ".srt"))
        with open(os.path.join(out, name + ".json"), "w") as fh:
            import json
            json.dump({"duration": total, "srt": [(e["t"], len(e["a"]) / SR, e["text"]) for e in events]}, fh)
    return name, round(total, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voices", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lang", default="es")
    ap.add_argument("--eps", default="")
    ap.add_argument("--what", default="ep,short")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cache = os.path.join(a.out, "_cache")
    os.makedirs(cache, exist_ok=True)
    eps = [int(x) for x in a.eps.split(",") if x] or sorted(EPISODES)
    what = a.what.split(",")
    R.set_lang(a.lang)
    jobs = []
    for n in eps:
        if "ep" in what:
            jobs.append(("ep", n, 0, a.lang, a.voices, a.out, cache))
        if "short" in what:
            for k in range(len(EPISODES[n]["shorts"])):
                jobs.append(("short", n, k, a.lang, a.voices, a.out, cache))
    # voces primero (en serie, quedan en caché)
    for n in eps:
        build_timeline(EPISODES[n], a.lang, a.voices, cache)
        for k in range(len(EPISODES[n]["shorts"])):
            s0, s1 = EPISODES[n]["shorts"][k][:2]
            build_timeline(EPISODES[n], a.lang, a.voices, cache, scene_range=(s0, s1), short=True)
    print("voces listas", flush=True)
    jobs.sort(key=lambda j: j[0] != "ep")  # primero los episodios (los más largos)
    with Pool(a.jobs) as p:
        for name, dur in p.imap_unordered(render_job, jobs):
            print("OK", name, dur, flush=True)


if __name__ == "__main__":
    main()
