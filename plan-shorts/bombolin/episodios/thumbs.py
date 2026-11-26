"""Miniaturas 1280x720 (3 variantes por video y por idioma) para episodios y recopilaciones.

Uso: python3 thumbs.py CARPETA_SALIDA
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "branding"))
sys.path.insert(0, HERE)
import branding as B  # noqa: E402
from episode import EPISODES  # noqa: E402

W, H = 1280, 720
PALETTE = [((255, 120, 150), (255, 200, 120)), ((90, 160, 255), (150, 230, 255)), ((120, 200, 110), (220, 250, 150)),
           ((170, 115, 230), (255, 160, 220)), ((255, 170, 60), (255, 230, 120))]
_sp = {}


_SP3D = None


def sprite(name, h):
    """Sprite del personaje: 3D si existe BOMBOLIN_SPRITES3D, si no el dibujo 2D."""
    global _SP3D
    if (name, h) not in _sp:
        d = os.environ.get("BOMBOLIN_SPRITES3D")
        if d:
            if _SP3D is None:
                import episode as E
                _SP3D = E.load_3d_sprites(d)
            key = {"PIPO": ("PIPO", 1, 0), "LULA": ("LULA", "happy", 0, 0), "ZUMBI": ("ZUMBI", 1, 1, 0)}.get(name, (name, 0, 0))
            im = _SP3D[key]
            _sp[(name, h)] = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
        else:
            _sp[(name, h)] = B.sprite(name, h)
    return _sp[(name, h)]


def scene_bg(seed):
    if os.environ.get("BOMBOLIN_BG3D"):
        import episode as E
        return E.background("meadow", W, H, seed).convert("RGBA")
    return B.meadow(W, H, seed=seed, horizon=0.62)


def big_text(d, xy, text, size, fill=(255, 214, 60), anchor="mm", maxw=W - 80):
    f = B.font(B.F700, size)
    while d.textlength(text, font=f) > maxw and size > 40:
        size -= 6
        f = B.font(B.F700, size)
    d.text(xy, text, font=f, fill=fill, anchor=anchor, stroke_width=max(6, size // 9), stroke_fill=(40, 30, 60))


def logo_corner(im):
    lg = B.logo(400).resize((130, 130))
    im.alpha_composite(lg, (W - 145, 15))


def burst(im, c):
    d = ImageDraw.Draw(im, "RGBA")
    import math
    for i in range(18):
        a = i / 18 * 2 * math.pi
        d.polygon([(W / 2, H / 2), (W / 2 + 1500 * math.cos(a), H / 2 + 1500 * math.sin(a)),
                   (W / 2 + 1500 * math.cos(a + 0.17), H / 2 + 1500 * math.sin(a + 0.17))], fill=c + (60,))


def v1(ep, lang, pal):
    im = B.vgrad(W, H, *pal)
    burst(im, (255, 255, 255))
    p = sprite("PIPO", 600)
    im.alpha_composite(p, (40, H - p.height + 20))
    e = B.emoji(ep["thumb"]["em"], 360)
    im.alpha_composite(e, (W - e.width - 90, 230))
    d = ImageDraw.Draw(im)
    big_text(d, (W * 0.62, 110), ep["thumb"]["t1_" + lang], 110)
    return im


def v2(ep, lang, pal):
    im = scene_bg(ep["n"])
    chars = ep["thumb"]["chars"][:2]
    x = [250, W - 250]
    for i, c in enumerate(chars):
        s = sprite(c, 470 if c != "LULA" else 300)
        y = H - s.height + 10 if c not in ("LULA", "ZUMBI") else 230
        im.alpha_composite(s, (int(x[i] - s.width / 2), int(y)))
    e = B.emoji(ep["thumb"]["em"], 330)
    im.alpha_composite(e, (W // 2 - e.width // 2, 150))
    logo_corner(im)
    return im


def v3(ep, lang, pal):
    im = B.vgrad(W, H, pal[1], pal[0])
    burst(im, (255, 255, 255))
    c = ep["thumb"]["chars"][1] if ep["thumb"]["chars"][0] == "PIPO" else ep["thumb"]["chars"][0]
    s = sprite(c, 560 if c not in ("LULA", "ZUMBI") else 380)
    im.alpha_composite(s, (W - s.width - 30, H - s.height + 10 if c not in ("LULA", "ZUMBI") else 200))
    e = B.emoji(ep["thumb"]["em"], 300)
    im.alpha_composite(e, (90, 260))
    d = ImageDraw.Draw(im)
    big_text(d, (W * 0.40, 120), ep["thumb"]["t2_" + lang], 96, fill=(255, 255, 255), maxw=W * 0.75)
    return im


def compilation(eps, lang, variant, label):
    pal = PALETTE[variant % len(PALETTE)]
    im = B.vgrad(W, H, *pal) if variant != 1 else scene_bg(len(eps))
    if variant != 1:
        burst(im, (255, 255, 255))
    d = ImageDraw.Draw(im, "RGBA")
    n = len(eps)
    cols = 4 if n <= 4 else 7
    sz = 150 if n <= 4 else 82
    for i, k in enumerate(eps):
        r, c = divmod(i, cols)
        cx = W * 0.645 + (c - (min(n, cols) - 1) / 2) * (sz + 30)
        cy = 300 + r * (sz + 30)
        d.rounded_rectangle([cx - sz / 2 - 12, cy - sz / 2 - 12, cx + sz / 2 + 12, cy + sz / 2 + 12], 24,
                            fill=(255, 255, 255, 230))
        e = B.emoji(EPISODES[k]["sticker"], sz)
        im.alpha_composite(e, (int(cx - e.width / 2), int(cy - e.height / 2)))
    p = sprite("PIPO", 520)
    im.alpha_composite(p, (10, H - p.height + 30))
    d = ImageDraw.Draw(im)
    big_text(d, (W * 0.60, 95), label, 92, maxw=W * 0.75)
    if variant == 2:
        logo_corner(im)
    return im


COMPS = [("C1", [1, 2, 3, 4]), ("C2", [3, 4, 5, 6]), ("C3", [5, 6, 7, 8]), ("C4", [7, 8, 9, 10]),
         ("C5", [9, 10, 11, 12]), ("C6", list(range(1, 14)))]


def comp_label(cid, eps, lang):
    if cid == "C6":
        return "¡TEMPORADA COMPLETA!" if lang == "es" else "FULL SEASON!"
    if cid in ("C4", "C5"):
        return "¡ESPECIAL NAVIDAD!" if lang == "es" else "CHRISTMAS SPECIAL!"
    return (f"¡{len(eps)} EPISODIOS!" if lang == "es" else f"{len(eps)} EPISODES!")


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for n, ep in EPISODES.items():
        pal = PALETTE[n % len(PALETTE)]
        for lang in ("es", "en"):
            for k, f in enumerate((v1, v2, v3), 1):
                f(ep, lang, pal).convert("RGB").save(os.path.join(out, f"E{n:02d}_{lang.upper()}_miniatura{k}.jpg"), quality=90)
    for cid, eps in COMPS:
        for lang in ("es", "en"):
            for k in range(3):
                compilation(eps, lang, k, comp_label(cid, eps, lang)).convert("RGB").save(
                    os.path.join(out, f"{cid}_{lang.upper()}_miniatura{k + 1}.jpg"), quality=90)
    print("ok", len(os.listdir(out)))


if __name__ == "__main__":
    main()
