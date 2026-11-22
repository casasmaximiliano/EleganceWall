"""Identidad visual del canal «Bombolín y sus amigos» / «Bombolín & Friends».

Genera: logo (foto de perfil para YouTube, Instagram y TikTok), banner de YouTube (ES y EN),
marca de agua para los videos de YouTube y portadas de historias destacadas de Instagram.

Uso: python3 branding.py CARPETA_SALIDA
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "video"))
import characters as ch  # noqa: E402

ch.SS, ch.OUT_SCALE = 4, 2.0  # personajes en alta resolución
F700 = os.path.join(HERE, "fonts", "fredoka-latin-700-normal.woff")
F600 = os.path.join(HERE, "fonts", "fredoka-latin-600-normal.woff")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
INK = (40, 40, 70)
GREEN = (60, 175, 110)
RAINBOW = [(255, 95, 95), (255, 170, 60), (255, 225, 80), (110, 205, 110), (90, 160, 255), (170, 115, 230)]


def font(path, size):
    return ImageFont.truetype(path, size)


def sprite(name, h):
    f = {"PIPO": ch.pipo, "TOTO": ch.toto, "ZUMBI": ch.zumbi, "ABU": ch.abu}.get(name)
    im = ch.lula(False, False, "happy") if name == "LULA" else f(True, False) if name == "PIPO" else f(False, False)
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)


def emoji(c, size):
    ef = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((8, 8), c, font=ef, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * size / im.height), size), Image.LANCZOS)


def vgrad(w, h, c1, c2):
    a = np.linspace(0, 1, h)[:, None, None]
    g = (np.array(c1)[None, None] * (1 - a) + np.array(c2)[None, None] * a).astype(np.uint8)
    return Image.fromarray(np.repeat(g, w, axis=1), "RGB").convert("RGBA")


def outlined(d, xy, text, f, fill, stroke=INK, sw=None, anchor="mm"):
    d.text(xy, text, font=f, fill=fill, anchor=anchor, stroke_width=sw or max(3, f.size // 11), stroke_fill=stroke)


def meadow(w, h, seed=3, horizon=0.72):
    rng = np.random.default_rng(seed)
    im = vgrad(w, h, (120, 200, 255), (210, 242, 255))
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(int(w * h / 9000)):
        x, y = rng.integers(0, w), rng.integers(0, int(h * 0.6))
        d.ellipse([x, y, x + 5, y + 5], fill=(255, 255, 255, 90))
    for (cx, cy, s) in [(0.12, 0.16, 1.0), (0.45, 0.10, 0.8), (0.8, 0.2, 1.1), (0.95, 0.07, 0.7)]:
        x, y = cx * w, cy * h
        for dx, dy, r in [(0, 0, 60), (70, -25, 75), (150, 0, 60), (75, 20, 55)]:
            r *= s * h / 1000
            d.ellipse([x + dx * s - r, y + dy * s - r, x + dx * s + r, y + dy * s + r], fill=(255, 255, 255, 240))
    hy = h * horizon
    d.ellipse([-0.3 * w, hy - 0.05 * h, 0.6 * w, hy + 1.2 * h], fill=(125, 210, 115))
    d.ellipse([0.35 * w, hy - 0.02 * h, 1.3 * w, hy + 1.2 * h], fill=(100, 192, 98))
    for _ in range(int(w / 12)):
        x, y = rng.integers(0, w), rng.integers(int(hy + 0.05 * h), h)
        c = [(255, 120, 150), (255, 230, 90), (255, 255, 255), (180, 140, 255)][rng.integers(0, 4)]
        r = rng.integers(5, 11)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    return im


# ------------------------------------------------------------------ logo
def logo(size=1080):
    S = size
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # anillo arcoíris
    for i, c in enumerate(RAINBOW):
        r = S / 2 - i * S * 0.018
        d.ellipse([S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r], fill=c)
    r_in = S / 2 - 6 * S * 0.018
    inner = vgrad(S, S, (255, 248, 220), (150, 215, 255))
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([S / 2 - r_in, S / 2 - r_in, S / 2 + r_in, S / 2 + r_in], fill=255)
    im.paste(inner, (0, 0), m)
    # estrellitas
    d = ImageDraw.Draw(im)
    for (x, y, r) in [(0.22, 0.30, 18), (0.80, 0.26, 22), (0.17, 0.55, 12), (0.85, 0.52, 14)]:
        x, y, r = x * S, y * S, r * S / 1080
        d.polygon([(x, y - r * 2), (x + r * 0.6, y - r * 0.6), (x + r * 2, y), (x + r * 0.6, y + r * 0.6),
                   (x, y + r * 2), (x - r * 0.6, y + r * 0.6), (x - r * 2, y), (x - r * 0.6, y - r * 0.6)],
                  fill=(255, 215, 70))
    # Bombolín
    p = sprite("PIPO", int(S * 0.95))
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    layer.paste(p, (int(S / 2 - p.width / 2 + S * 0.02), int(S * 0.13)), p)
    im.alpha_composite(Image.composite(layer, Image.new("RGBA", (S, S), (0, 0, 0, 0)), m))
    # cinta con el nombre
    d = ImageDraw.Draw(im)
    bw, bh, by = S * 0.62, S * 0.15, S * 0.80
    d.rounded_rectangle([S / 2 - bw / 2, by - bh / 2, S / 2 + bw / 2, by + bh / 2], bh / 2,
                        fill=(255, 255, 255), outline=INK, width=int(S * 0.008))
    outlined(d, (S / 2, by - S * 0.005), "BOMBOLÍN", font(F700, int(S * 0.085)), GREEN, stroke=(255, 255, 255), sw=1)
    return im


# ------------------------------------------------------------------ banner de YouTube
def banner(lang):
    W, H = 2560, 1440
    im = meadow(W, H, horizon=0.60)
    d = ImageDraw.Draw(im, "RGBA")
    for i, c in enumerate(RAINBOW):
        d.arc([250 + i * 34, 180 + i * 34, W - 250 - i * 34, 2300 - i * 34], 180, 360, fill=c + (150,), width=34)
    # zona segura (se ve en todos los dispositivos): 1546x423 centrada
    sx0, sy0, sx1, sy1 = (W - 1546) // 2, (H - 423) // 2, (W + 1546) // 2, (H + 423) // 2
    title = {"es": ("Bombolín", " y sus amigos"), "en": ("Bombolín", " & Friends")}[lang]
    sub = {"es": "Canciones, juegos y aventuras para pequeños exploradores",
           "en": "Songs, games and adventures for little explorers"}[lang]
    pill = {"es": "¡Videos nuevos todos los días!", "en": "New videos every day!"}[lang]
    # placa blanca detrás del texto
    d.rounded_rectangle([sx0 + 250, sy0 + 15, sx1 - 250, sy1 - 15], 60, fill=(255, 255, 255, 220))
    f1 = font(F700, 112)
    while d.textlength(title[0] + title[1], font=f1) > 960:
        f1 = font(F700, f1.size - 4)
    tw = d.textlength(title[0] + title[1], font=f1)
    x = W / 2 - tw / 2
    y = sy0 + 135
    d.text((x, y), title[0], font=f1, fill=GREEN, anchor="lm", stroke_width=6, stroke_fill=(255, 255, 255))
    x += d.textlength(title[0], font=f1)
    d.text((x, y), title[1], font=f1, fill=(70, 120, 220), anchor="lm", stroke_width=6, stroke_fill=(255, 255, 255))
    f2 = font(F600, 35)
    d.text((W / 2, sy0 + 255), sub, font=f2, fill=INK, anchor="mm")
    f3 = font(F700, 40)
    pw = d.textlength(pill, font=f3) + 80
    d.rounded_rectangle([W / 2 - pw / 2, sy0 + 305, W / 2 + pw / 2, sy0 + 375], 35, fill=(255, 120, 150))
    d.text((W / 2, sy0 + 340), pill, font=f3, fill=(255, 255, 255), anchor="mm")
    # personajes: Bombolín y Toto dentro de la zona segura; el resto en la zona extendida (PC y TV)
    for name, cx, base, h in [("PIPO", sx0 + 120, sy1 - 5, 360), ("TOTO", sx1 - 115, sy1 - 5, 310),
                              ("ABU", sx0 - 260, sy1 + 140, 400), ("LULA", sx1 + 300, sy0 + 140, 240),
                              ("ZUMBI", sx0 - 220, sy0 + 20, 190)]:
        sp = sprite(name, h)
        im.alpha_composite(sp, (int(cx - sp.width / 2), int(base - sp.height)))
    return im


def watermark():
    lg = logo(600)
    return lg.resize((150, 150), Image.LANCZOS)


def highlight(em, bg):
    W, H = 1080, 1920
    im = vgrad(W, H, bg, tuple(min(255, c + 40) for c in bg))
    d = ImageDraw.Draw(im)
    d.ellipse([W / 2 - 330, H / 2 - 330, W / 2 + 330, H / 2 + 330], fill=(255, 255, 255))
    e = emoji(em, 380)
    im.alpha_composite(e, (W // 2 - e.width // 2, H // 2 - e.height // 2))
    return im


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    lg = logo(1080)
    lg.save(os.path.join(out, "logo_perfil_1080.png"))
    sq = Image.new("RGBA", lg.size, (255, 248, 230, 255))
    sq.alpha_composite(lg)
    sq.convert("RGB").save(os.path.join(out, "logo_perfil_1080_fondo.jpg"), quality=95)
    watermark().save(os.path.join(out, "youtube_marca_de_agua_150.png"))
    for lang in ("es", "en"):
        banner(lang).convert("RGB").save(os.path.join(out, f"youtube_banner_{lang}_2560x1440.jpg"), quality=92)
    for name, em, bg in [("canciones", "🎵", (255, 140, 170)), ("juegos", "🎲", (140, 120, 240)),
                         ("series", "🥚", (110, 200, 150)), ("animales", "🦒", (255, 190, 80)),
                         ("dinosaurios", "🦕", (90, 170, 255))]:
        highlight(em, bg).convert("RGB").save(os.path.join(out, f"instagram_destacada_{name}.jpg"), quality=92)
    print("ok", sorted(os.listdir(out)))


if __name__ == "__main__":
    main()
