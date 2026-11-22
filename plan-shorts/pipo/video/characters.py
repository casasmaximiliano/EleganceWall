"""Dibujo vectorial (PIL) de los personajes originales de «El mundo de Pipo».

Cada personaje se dibuja una vez en alta resolución (con supersampling para suavizar bordes)
y se guarda como sprite RGBA en sus variantes: boca cerrada / abierta y ojos abiertos / cerrados.
"""
from PIL import Image, ImageDraw

SS = 2  # supersampling
OUT_SCALE = 1.0  # escala de salida (1 = tamaño usado en los videos)


def _c(d, cx, cy, r, fill, outline=None, w=0):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=w)


def _e(d, box, fill, outline=None, w=0):
    d.ellipse(box, fill=fill, outline=outline, width=w)


OUT = (40, 40, 60)


def _eyes(d, xs, y, r, iris, blink, lashes=False):
    for x in xs:
        if blink:
            d.arc([x - r, y - r * 0.4, x + r, y + r * 0.9], 200, 340, fill=OUT, width=int(r * 0.28))
            continue
        _c(d, x, y, r, (255, 255, 255), OUT, int(r * 0.12))
        _c(d, x + r * 0.08, y + r * 0.1, r * 0.62, iris)
        _c(d, x + r * 0.12, y + r * 0.14, r * 0.32, (25, 20, 30))
        _c(d, x - r * 0.15, y - r * 0.2, r * 0.22, (255, 255, 255))
        _c(d, x + r * 0.3, y + r * 0.32, r * 0.09, (255, 255, 255))
        if lashes:
            for k in (-1, 0, 1):
                d.line([x + k * r * 0.5, y - r * 0.92, x + k * r * 0.75, y - r * 1.3], fill=OUT, width=int(r * 0.13))


def _mouth(d, cx, cy, w, open_, tooth=False):
    if open_:
        _e(d, [cx - w * 0.55, cy - w * 0.2, cx + w * 0.55, cy + w * 0.55], (150, 40, 60), OUT, int(w * 0.07))
        _e(d, [cx - w * 0.3, cy + w * 0.2, cx + w * 0.3, cy + w * 0.5], (255, 120, 140))
        if tooth:
            d.rectangle([cx - w * 0.1, cy - w * 0.18, cx + w * 0.1, cy + w * 0.05], fill=(255, 255, 255))
    else:
        d.arc([cx - w * 0.55, cy - w * 0.45, cx + w * 0.55, cy + w * 0.3], 20, 160, fill=OUT, width=int(w * 0.09))
        if tooth:
            d.rectangle([cx - w * 0.09, cy + w * 0.25, cx + w * 0.09, cy + w * 0.42], fill=(255, 255, 255), outline=OUT)


def pipo(open_=False, blink=False):
    W, H = 520 * SS, 620 * SS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = SS
    G, GD = (126, 217, 166), (80, 170, 120)
    OR = (255, 150, 60)
    # cola
    d.polygon([(110 * s, 470 * s), (20 * s, 500 * s), (120 * s, 530 * s)], fill=G, outline=OUT)
    # púas
    for (x, y) in [(110, 300), (95, 360), (95, 420)]:
        _c(d, x * s, y * s, 26 * s, OR, OUT, 4 * s)
    # cuerpo
    _e(d, [100 * s, 300 * s, 420 * s, 580 * s], G, OUT, 6 * s)
    _e(d, [175 * s, 360 * s, 345 * s, 565 * s], (255, 230, 120))
    for (x, y) in [(230, 420), (290, 450), (245, 500)]:
        _c(d, x * s, y * s, 12 * s, GD)
    # brazos
    _e(d, [80 * s, 380 * s, 140 * s, 440 * s], G, OUT, 5 * s)
    _e(d, [380 * s, 380 * s, 440 * s, 440 * s], G, OUT, 5 * s)
    # zapatillas
    for x in (170, 350):
        _e(d, [(x - 60) * s, 555 * s, (x + 60) * s, 610 * s], OR, OUT, 5 * s)
        d.line([(x - 40) * s, 575 * s, (x + 40) * s, 575 * s], fill=(255, 255, 255), width=6 * s)
    # cabeza
    _c(d, 260 * s, 220 * s, 165 * s, G, OUT, 6 * s)
    _c(d, 150 * s, 285 * s, 26 * s, (255, 160, 170))
    _c(d, 370 * s, 285 * s, 26 * s, (255, 160, 170))
    _eyes(d, [195 * s, 325 * s], 215 * s, 50 * s, (140, 85, 40), blink)
    _mouth(d, 260 * s, 300 * s, 90 * s, open_)
    # gorrito de cascarón (media cáscara con borde en zigzag)
    pts = [(120 * s, 125 * s)]
    for i in range(9):
        x = 120 + i * 35
        pts.append(((x + 17) * s, (110 if i % 2 else 140) * s))
    pts.append((420 * s, 125 * s))
    d.chord([115 * s, 4 * s, 425 * s, 246 * s], 180, 360, fill=(255, 255, 250), outline=OUT, width=5 * s)
    d.polygon(pts + [(420 * s, 105 * s), (120 * s, 105 * s)], fill=(255, 255, 250))
    d.line(pts, fill=OUT, width=5 * s)
    for (x, y, r) in [(200, 60, 16), (300, 45, 12), (350, 85, 14), (250, 95, 10)]:
        _c(d, x * s, y * s, r * s, (120, 180, 255))
    return im.resize((int(W * OUT_SCALE) // SS, int(H * OUT_SCALE) // SS), Image.LANCZOS)


def toto(open_=False, blink=False):
    W, H = 520 * SS, 600 * SS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = SS
    O, OD = (255, 154, 60), (235, 120, 30)
    # pies
    for x in (170, 350):
        _e(d, [(x - 75) * s, 520 * s, (x + 75) * s, 595 * s], OD, OUT, 5 * s)
    # pelo (borde con bolitas)
    import math
    for k in range(36):
        a = k / 36 * 2 * math.pi
        _c(d, (260 + 215 * math.cos(a)) * s, (320 + 215 * math.sin(a)) * s, 40 * s, O)
    _c(d, 260 * s, 320 * s, 225 * s, O)
    # cuernitos
    d.polygon([(150 * s, 120 * s), (175 * s, 40 * s), (205 * s, 110 * s)], fill=(160, 90, 220), outline=OUT)
    d.polygon([(315 * s, 110 * s), (345 * s, 40 * s), (370 * s, 120 * s)], fill=(160, 90, 220), outline=OUT)
    # media rayada pegada
    for i in range(4):
        col = (255, 255, 255) if i % 2 == 0 else (90, 160, 255)
        d.rectangle([(400 + i * 0) * s, (360 + i * 22) * s, 460 * s, (382 + i * 22) * s], fill=col)
    _e(d, [395 * s, 440 * s, 480 * s, 470 * s], (90, 160, 255))
    # migas
    for (x, y) in [(130, 420), (180, 470), (330, 480)]:
        _c(d, x * s, y * s, 7 * s, (200, 150, 90))
    _eyes(d, [195 * s, 325 * s], 260 * s, 55 * s, (90, 60, 160), blink)
    _mouth(d, 260 * s, 370 * s, 130 * s, open_, tooth=True)
    return im.resize((int(W * OUT_SCALE) // SS, int(H * OUT_SCALE) // SS), Image.LANCZOS)


LULA_COLORS = {
    "calm": (143, 211, 244), "sad": (170, 175, 190), "angry": (255, 130, 120),
    "shy": (255, 170, 205), "happy": (143, 211, 244),
}


def lula(open_=False, blink=False, mood="calm"):
    W, H = 560 * SS, 420 * SS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = SS
    col = LULA_COLORS.get(mood, LULA_COLORS["calm"])
    blobs = [(150, 250, 110), (280, 190, 150), (410, 250, 110), (220, 300, 100), (350, 300, 100)]
    for (x, y, r) in blobs:
        _c(d, x * s, y * s, (r + 7) * s, OUT)
    for (x, y, r) in blobs:
        _c(d, x * s, y * s, r * s, col)
    if mood == "happy":
        rb = [(255, 90, 90), (255, 170, 60), (255, 230, 80), (110, 210, 110), (90, 160, 255), (170, 110, 230)]
        for i, c in enumerate(rb):
            d.arc([(110 + i * 12) * s, (330 + i * 12) * s, (450 - i * 12) * s, (560 - i * 12) * s], 200, 340, fill=c, width=12 * s)
    _c(d, 185 * s, 270 * s, 24 * s, (255, 150, 170))
    _c(d, 375 * s, 270 * s, 24 * s, (255, 150, 170))
    _eyes(d, [225 * s, 335 * s], 220 * s, 42 * s, (60, 120, 200), blink, lashes=True)
    _mouth(d, 280 * s, 285 * s, 70 * s, open_)
    if mood == "sad":
        for (x, y) in [(200, 380), (300, 395), (370, 375)]:
            d.polygon([(x * s, (y - 18) * s), ((x - 9) * s, y * s), ((x + 9) * s, y * s)], fill=(90, 150, 255))
            _c(d, x * s, (y + 3) * s, 9 * s, (90, 150, 255))
    if mood == "angry":
        for x in (150, 410):
            d.line([(x) * s, 90 * s, (x + 20) * s, 120 * s, (x - 5) * s, 125 * s, (x + 15) * s, 160 * s], fill=(255, 220, 60), width=8 * s)
    return im.resize((int(W * OUT_SCALE) // SS, int(H * OUT_SCALE) // SS), Image.LANCZOS)


def zumbi(open_=False, blink=False, wing=0):
    W, H = 420 * SS, 420 * SS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = SS
    wy = 20 if wing else 0
    wing_im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wing_im)
    _e(wd, [70 * s, (40 + wy) * s, 200 * s, (170 + wy) * s], (220, 240, 255, 190), OUT, 4 * s)
    _e(wd, [220 * s, (40 + wy) * s, 350 * s, (170 + wy) * s], (220, 240, 255, 190), OUT, 4 * s)
    im.alpha_composite(wing_im)
    d = ImageDraw.Draw(im)
    for x in (165, 255):
        d.line([x * s, 140 * s, (x - 20 if x < 200 else x + 20) * s, 60 * s], fill=OUT, width=5 * s)
        hx = (x - 20 if x < 200 else x + 20) * s
        _c(d, hx - 8 * s, 55 * s, 10 * s, (255, 90, 120))
        _c(d, hx + 8 * s, 55 * s, 10 * s, (255, 90, 120))
        d.polygon([(hx - 18 * s, 58 * s), (hx + 18 * s, 58 * s), (hx, 78 * s)], fill=(255, 90, 120))
    _c(d, 210 * s, 250 * s, 130 * s, (255, 210, 63), OUT, 6 * s)
    for y in (300, 345):
        d.chord([85 * s, (y - 30) * s, 335 * s, (y + 30) * s], 0, 360, fill=None)
        d.rectangle([95 * s, (y - 12) * s, 325 * s, (y + 12) * s], fill=(40, 35, 45))
    # recortar las rayas al círculo
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse([86 * s, 126 * s, 334 * s, 374 * s], fill=255)
    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    body.paste(im, (0, 0), mask)
    im2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im2.alpha_composite(wing_im)
    im2.alpha_composite(im.copy().crop((0, 0, W, 126 * s)), (0, 0))
    im2.alpha_composite(body)
    d = ImageDraw.Draw(im2)
    d.ellipse([80 * s, 120 * s, 340 * s, 380 * s], outline=OUT, width=6 * s)
    # patitas con zapatillas rojas
    for x in (150, 210, 270):
        d.line([x * s, 370 * s, x * s, 395 * s], fill=OUT, width=5 * s)
        _e(d, [(x - 18) * s, 390 * s, (x + 18) * s, 412 * s], (230, 50, 60), OUT, 3 * s)
    _c(d, 140 * s, 250 * s, 18 * s, (255, 150, 170))
    _c(d, 280 * s, 250 * s, 18 * s, (255, 150, 170))
    _eyes(d, [170 * s, 250 * s], 205 * s, 36 * s, (60, 40, 20), blink)
    _mouth(d, 210 * s, 255 * s, 60 * s, open_)
    return im2.resize((int(W * OUT_SCALE) // SS, int(H * OUT_SCALE) // SS), Image.LANCZOS)


def abu(open_=False, blink=False):
    W, H = 700 * SS, 640 * SS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = SS
    SK = (150, 200, 120)
    # patas
    for x in (180, 330, 470):
        _e(d, [(x - 50) * s, 520 * s, (x + 50) * s, 620 * s], SK, OUT, 5 * s)
    # bastón hoja
    d.line([600 * s, 300 * s, 610 * s, 625 * s], fill=(120, 80, 40), width=12 * s)
    _e(d, [560 * s, 230 * s, 650 * s, 320 * s], (90, 190, 90), OUT, 4 * s)
    # caparazón tipo colcha
    d.chord([90 * s, 240 * s, 560 * s, 700 * s], 180, 360, fill=(70, 150, 90), outline=OUT, width=6 * s)
    patches = [(140, 420, (110, 180, 110)), (230, 340, (150, 200, 120)), (330, 310, (90, 160, 100)),
               (430, 350, (120, 190, 140)), (500, 430, (100, 170, 120)), (300, 420, (170, 210, 130)),
               (210, 440, (80, 140, 90)), (400, 440, (140, 200, 110))]
    for (x, y, c) in patches:
        d.rounded_rectangle([(x - 45) * s, (y - 38) * s, (x + 45) * s, (y + 38) * s], 14 * s, fill=c, outline=(250, 240, 220), width=3 * s)
    d.chord([90 * s, 240 * s, 560 * s, 700 * s], 180, 360, outline=OUT, width=6 * s)
    d.rectangle([90 * s, 468 * s, 560 * s, 530 * s], fill=(230, 220, 160), outline=OUT, width=5 * s)
    # cuello y cabeza
    _e(d, [10 * s, 230 * s, 170 * s, 470 * s], SK, OUT, 5 * s)
    _c(d, 110 * s, 200 * s, 120 * s, SK, OUT, 6 * s)
    # bufanda lavanda
    d.rounded_rectangle([20 * s, 300 * s, 210 * s, 350 * s], 22 * s, fill=(190, 160, 230), outline=OUT, width=4 * s)
    d.rounded_rectangle([150 * s, 320 * s, 200 * s, 420 * s], 18 * s, fill=(190, 160, 230), outline=OUT, width=4 * s)
    _c(d, 50 * s, 235 * s, 20 * s, (255, 160, 170))
    _c(d, 180 * s, 235 * s, 20 * s, (255, 160, 170))
    _eyes(d, [70 * s, 150 * s], 180 * s, 32 * s, (90, 60, 40), blink)
    # lentes dorados
    for x in (70, 150):
        d.ellipse([(x - 44) * s, 136 * s, (x + 44) * s, 224 * s], outline=(220, 170, 40), width=7 * s)
    d.line([114 * s, 178 * s, 106 * s, 178 * s], fill=(220, 170, 40), width=7 * s)
    _mouth(d, 110 * s, 250 * s, 70 * s, open_)
    return im.resize((int(W * OUT_SCALE) // SS, int(H * OUT_SCALE) // SS), Image.LANCZOS)


DRAW = {"PIPO": pipo, "TOTO": toto, "LULA": lula, "ZUMBI": zumbi, "ABU": abu}


def build_sprites():
    sp = {}
    for k, f in DRAW.items():
        if k == "LULA":
            for mood in LULA_COLORS:
                for o in (0, 1):
                    for b in (0, 1):
                        sp[(k, mood, o, b)] = f(bool(o), bool(b), mood)
        elif k == "ZUMBI":
            for o in (0, 1):
                for b in (0, 1):
                    for w in (0, 1):
                        sp[(k, w, o, b)] = f(bool(o), bool(b), w)
        else:
            for o in (0, 1):
                for b in (0, 1):
                    sp[(k, o, b)] = f(bool(o), bool(b))
    return sp


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "sheet.png"
    sheet = Image.new("RGBA", (2400, 760), (255, 246, 229, 255))
    x = 10
    for k, f in DRAW.items():
        im = f(False, False) if k != "LULA" else f(False, False, "happy")
        sheet.alpha_composite(im, (x, 760 - im.height - 20))
        x += im.width - 20
    sheet.save(out)
