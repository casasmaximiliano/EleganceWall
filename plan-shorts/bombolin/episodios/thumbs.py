"""Miniaturas 1280x720 (3 variantes por video y por idioma) para episodios y recopilaciones.

Uso: python3 thumbs.py CARPETA_SALIDA [1,2,3]   (con la lista, solo esos episodios y sin recopilaciones)
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
VIVID = bool(os.environ.get("BOMBOLIN_ESTILO") == "2")
PALETTE = ([((255, 40, 120), (255, 170, 0)), ((10, 90, 255), (0, 210, 255)), ((0, 160, 80), (160, 235, 30)),
            ((120, 40, 230), (255, 70, 190)), ((255, 90, 0), (255, 210, 0))] if VIVID else
           [((255, 120, 150), (255, 200, 120)), ((90, 160, 255), (150, 230, 255)), ((120, 200, 110), (220, 250, 150)),
            ((170, 115, 230), (255, 160, 220)), ((255, 170, 60), (255, 230, 120))])


def pop(im, px=12):
    """Borde blanco grueso alrededor de un recorte (estilo calcomanía): resalta sobre cualquier fondo."""
    if not VIVID:
        return im
    from PIL import ImageFilter
    a = im.getchannel("A").point(lambda v: 255 if v > 80 else 0)
    pad = px + 4
    big = Image.new("L", (im.width + pad * 2, im.height + pad * 2), 0)
    big.paste(a, (pad, pad))
    big = big.filter(ImageFilter.MaxFilter(px * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2))
    out = Image.new("RGBA", big.size, (255, 255, 255, 0))
    out.putalpha(big)
    out.alpha_composite(im, (pad, pad))
    return out


def finish(im):
    if not VIVID:
        return im
    from PIL import ImageEnhance
    rgb = ImageEnhance.Contrast(ImageEnhance.Color(im.convert("RGB")).enhance(1.2)).enhance(1.06)
    return rgb.convert("RGBA")
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
            _sp[(name, h)] = pop(im.resize((int(im.width * h / im.height), h), Image.LANCZOS))
        else:
            _sp[(name, h)] = B.sprite(name, h)
    return _sp[(name, h)]


def scene_bg(seed):
    if os.environ.get("BOMBOLIN_BG3D"):
        import episode as E
        if VIVID:  # en la miniatura, fondo nítido y saturado (sin desenfoque ni viñeta)
            from PIL import ImageEnhance
            old, E.STYLE2 = E.STYLE2, False
            im = E.background("meadow", W, H, seed)
            E.STYLE2 = old
            return ImageEnhance.Color(im.convert("RGB")).enhance(1.35).convert("RGBA")
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
        col = ((255, 240, 90) if i % 2 else (255, 255, 255)) if VIVID else c
        d.polygon([(W / 2, H / 2), (W / 2 + 1500 * math.cos(a), H / 2 + 1500 * math.sin(a)),
                   (W / 2 + 1500 * math.cos(a + 0.17), H / 2 + 1500 * math.sin(a + 0.17))], fill=col + (70 if VIVID else 60,))


def v1(ep, lang, pal):
    im = B.vgrad(W, H, *pal)
    burst(im, (255, 255, 255))
    p = sprite("PIPO", 600)
    im.alpha_composite(p, (40, H - p.height + 20))
    e = pop(B.emoji(ep["thumb"]["em"], 360))
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
    e = pop(B.emoji(ep["thumb"]["em"], 330))
    im.alpha_composite(e, (W // 2 - e.width // 2, 150))
    logo_corner(im)
    return im


def v3(ep, lang, pal):
    im = B.vgrad(W, H, pal[1], pal[0])
    burst(im, (255, 255, 255))
    c = ep["thumb"]["chars"][1] if ep["thumb"]["chars"][0] == "PIPO" else ep["thumb"]["chars"][0]
    s = sprite(c, 560 if c not in ("LULA", "ZUMBI") else 380)
    im.alpha_composite(s, (W - s.width - 30, H - s.height + 10 if c not in ("LULA", "ZUMBI") else 200))
    e = pop(B.emoji(ep["thumb"]["em"], 300))
    im.alpha_composite(e, (90, 260))
    d = ImageDraw.Draw(im)
    big_text(d, (W * 0.40, 120), ep["thumb"]["t2_" + lang], 96, fill=(255, 255, 255), maxw=W * 0.75)
    return im


# ---------------------------------------------------------------------------------------------
# Estilo 2: miniaturas «de clic» (una cara enorme con emoción, un objeto grande de la historia,
# 2 o 3 palabras gigantes, fondo saturado de color complementario con rayos y viñeta).
# ---------------------------------------------------------------------------------------------
YELLOW = (255, 217, 60)
INK4 = (35, 20, 60)
# Fondos: (centro luminoso, borde oscuro). Complementarios del personaje principal.
BG4 = {"azul": ((110, 230, 255), (0, 60, 190)), "cian": ((150, 255, 240), (0, 120, 190)),
       "magenta": ((255, 130, 225), (140, 0, 150)), "violeta": ((200, 130, 255), (70, 10, 170)),
       "amarillo": ((255, 250, 140), (255, 140, 0)), "naranja": ((255, 205, 90), (225, 60, 0)),
       "rojo": ((255, 150, 120), (190, 0, 60)), "noche": ((120, 140, 255), (20, 10, 90))}
# Dónde está la cara dentro del recorte de cada personaje (x0, y0, x1, y1 normalizados).
FACE = {"PIPO": (0.08, 0.0, 0.92, 0.47), "TOTO": (0.0, 0.0, 1.0, 0.86), "LULA": (0.06, 0.0, 0.94, 0.78),
        "ZUMBI": (0.12, 0.08, 0.88, 0.82), "ABU": (0.0, 0.0, 0.31, 0.46)}
# Cuánto de la altura ocupa la cara (los personajes «solo cara» no pueden ser tan altos).
FACE_H = {"PIPO": 0.56, "TOTO": 0.62, "LULA": 0.58, "ZUMBI": 0.60, "ABU": 0.50}

# Por episodio: protagonista de la miniatura 1, objeto, pareja de la 2 y personaje de la 3.
# Objeto: nombre de un PNG 3D (BOMBOLIN_OBJ3D), "draw:..." (dibujado aquí) o un emoji.
T4 = {
    1: dict(star="PIPO", obj="draw:egg", bg=("magenta", "amarillo", "azul"), pair=("PIPO", "TOTO"), q="TOTO",
            w1=("¡HUEVO", "GIGANTE!"), w2="¡CRAC!", w3=("¿QUIÉN", "SALDRÁ?"),
            e1=("GIANT", "EGG!"), e2="CRACK!", e3=("WHO'S", "INSIDE?")),
    2: dict(star="TOTO", hat="spaghetti", obj="bathtub", extra="bubbles", bg=("azul", "cian", "magenta"),
            pair=("TOTO", "PIPO"), q="PIPO", obj3="mudball",
            w1=("¡NO AL", "BAÑO!"), w2="¡PUAJ!", w3=("¿BAÑO DE", "BARRO?"),
            e1=("NO", "BATH!"), e2="YUCK!", e3=("MUD", "BATH?")),
    3: dict(star=("LULA", "sad"), obj="⚡", bg=("amarillo", "naranja", "violeta"), pair=("LULA", "PIPO"), q="PIPO",
            obj2="⛈️", obj3="🌈", w1=("¡QUÉ", "MIEDO!"), w2="¡BUM!", w3=("¿UN", "ARCOÍRIS?"),
            e1=("SO", "SCARY!"), e2="BOOM!", e3=("A", "RAINBOW?")),
    4: dict(star="ZUMBI", obj="🏁", bg=("violeta", "azul", "rojo"), pair=("ZUMBI", "ABU"), q="ABU",
            obj3="🏅", w1=("¡A", "CORRER!"), w2="¡YA!", w3=("¿QUIÉN", "GANA?"),
            e1=("READY,", "GO!"), e2="GO!", e3=("WHO", "WINS?")),
    5: dict(star="TOTO", obj="🪥", bg=("azul", "violeta", "magenta"), pair=("TOTO", "PIPO"), q="PIPO",
            w1=("¿Y MI", "CEPILLO?"), w2="¿DÓNDE?", w3=("¿DÓNDE", "ESTÁ?"),
            e1=("MY", "TOOTHBRUSH?"), e2="WHERE?", e3=("WHERE", "IS IT?")),
    6: dict(star="PIPO", obj="🐧", bg=("magenta", "cian", "naranja"), pair=("PIPO", "ZUMBI"), q="ZUMBI",
            obj3="❄️", w1=("¡NIEVE!",), w2="¡BRRR!", w3=("¿YO", "PRIMERO?"),
            e1=("SNOW!",), e2="BRRR!", e3=("ME", "FIRST?")),
    7: dict(star="ABU", obj="🎂", bg=("magenta", "amarillo", "azul"), pair=("ABU", "PIPO"), q="PIPO",
            obj3="🎁", w1=("¡SORPRESA!",), w2="¡FIESTA!", w3=("¿UNA", "FIESTA?"),
            e1=("SURPRISE!",), e2="PARTY!", e3=("A", "PARTY?")),
    8: dict(star="PIPO", obj="🦇", bg=("violeta", "noche", "naranja"), pair=("PIPO", "TOTO"), q="TOTO",
            w1=("¿QUIÉN", "HABLA?"), w2="¡HOLAAA!", w3=("¿UN", "FANTASMA?"),
            e1=("WHO'S", "THERE?"), e2="HELLO!", e3=("A", "GHOST?")),
    9: dict(star="PIPO", obj="🎄", bg=("rojo", "azul", "violeta"), pair=("PIPO", "TOTO"), q="TOTO",
            obj3="🎁", w1=("¡NAVIDAD!",), w2="¡REGALOS!", w3=("¿PARA", "MÍ?"),
            e1=("CHRISTMAS!",), e2="GIFTS!", e3=("FOR", "ME?")),
    10: dict(star="PIPO", obj="🦌", bg=("rojo", "noche", "amarillo"), pair=("PIPO", "LULA"), q="LULA",
             obj3="⭐", w1=("¡UN", "RENO!"), w2="¡NIEVE!", w3=("¿SE", "PERDIÓ?"),
             e1=("A", "REINDEER!"), e2="SNOW!", e3=("IS HE", "LOST?")),
    11: dict(star="PIPO", obj="bed", bg=("magenta", "noche", "naranja"), pair=("PIPO", "ABU"), q="ABU",
             obj3="🌙", w1=("¡NO TENGO", "SUEÑO!"), w2="¡SHHH!", w3=("¿A", "DORMIR?"),
             e1=("NOT", "SLEEPY!"), e2="SHHH!", e3=("BED", "TIME?")),
    12: dict(star="TOTO", obj="🥦", bg=("azul", "cian", "magenta"), pair=("TOTO", "PIPO"), q="PIPO",
             w1=("¡PUAJ!",), w2="¡ÑAM!", w3=("¿LO", "PRUEBA?"),
             e1=("YUCK!",), e2="YUM!", e3=("WILL HE", "TRY IT?")),
    13: dict(star="PIPO", obj="🎆", bg=("violeta", "noche", "magenta"), pair=("PIPO", "ZUMBI"), q="ZUMBI",
             obj3="🎉", w1=("¡AÑO", "NUEVO!"), w2="¡3, 2, 1!", w3=("¿LISTOS?",),
             e1=("NEW", "YEAR!"), e2="3, 2, 1!", e3=("READY?",)),
}


def t4conf(ep):
    """Configuración del episodio; los que no están en T4 se arman con los datos de ep['thumb']."""
    if ep["n"] in T4:
        return T4[ep["n"]]
    th = ep["thumb"]
    a, b = (th["chars"] + ["PIPO", "TOTO"])[:2]
    return dict(star=a, obj=th["em"], bg=("magenta", "azul", "amarillo"), pair=(a, b), q=b if b != a else "TOTO",
                w1=tuple(th["t1_es"].split(" ", 1)), w2="", w3=tuple(th["t2_es"].split(" ", 1)),
                e1=tuple(th["t1_en"].split(" ", 1)), e2="", e3=tuple(th["t2_en"].split(" ", 1)))


def _obj_dir():
    d = os.environ.get("BOMBOLIN_OBJ3D")
    if not d and os.environ.get("BOMBOLIN_SPRITES3D"):
        d = os.path.join(os.path.dirname(os.path.abspath(os.environ["BOMBOLIN_SPRITES3D"])), "obj3d")
    return d


def radial_bg(name, cx, cy, rays=True):
    """Fondo saturado: brillo radial detrás del personaje, rayos suaves y viñeta."""
    import numpy as np
    c_in, c_out = (np.array(c, float) for c in BG4[name])
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    r = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.15) ** 2) / (W * 0.62)
    t = np.clip(r, 0, 1) ** 0.9
    img = c_in[None, None] * (1 - t[..., None]) + c_out[None, None] * t[..., None]
    if rays:
        ang = np.arctan2(yy - cy, xx - cx)
        ray = (np.sin(ang * 14) > 0).astype(float) * np.clip(1.2 - r, 0, 1) * 0.16
        img = img + (255 - img) * ray[..., None]
    vig = 1 - 0.38 * np.clip((np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) - 0.75) / 0.7, 0, 1)
    img = img * vig[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype("uint8"), "RGB").convert("RGBA")


def _glow(im, cx, cy, rad, col=(255, 255, 240), alpha=150):
    from PIL import ImageFilter
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=alpha)
    m = m.filter(ImageFilter.GaussianBlur(rad * 0.35))
    lay = Image.new("RGBA", (W, H), col + (0,))
    lay.putalpha(m)
    im.alpha_composite(lay)


def sticker(src, px=14, shadow=True):
    """Calcomanía: borde blanco grueso + sombra oscura suave detrás (se despega del fondo)."""
    from PIL import ImageFilter
    a = src.getchannel("A").point(lambda v: 255 if v > 80 else 0)
    pad = px + 30
    big = Image.new("L", (src.width + pad * 2, src.height + pad * 2), 0)
    big.paste(a, (pad, pad))
    white = big.filter(ImageFilter.MaxFilter(px * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2))
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    if shadow:
        sh = Image.new("L", big.size, 0)
        sh.paste(white, (6, 12))
        sh = sh.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.55))
        lay = Image.new("RGBA", big.size, (20, 5, 40, 0))
        lay.putalpha(sh)
        out.alpha_composite(lay)
    wl = Image.new("RGBA", big.size, (255, 255, 255, 0))
    wl.putalpha(white)
    out.alpha_composite(wl)
    out.alpha_composite(src, (pad, pad))
    return out, pad


def _sharp(im):
    from PIL import ImageFilter
    a = im.getchannel("A")
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 80, 2))
    rgb = rgb.convert("RGBA")
    rgb.putalpha(a)
    return rgb


def char_img(spec, mouth=1):
    """Sprite 3D recortado a su silueta, con la boca abierta (sorpresa/alegría)."""
    global _SP3D
    name, mood = (spec if isinstance(spec, tuple) else (spec, "happy"))
    if _SP3D is None:
        import episode as E
        _SP3D = E.load_3d_sprites(os.environ["BOMBOLIN_SPRITES3D"])
    key = {"LULA": ("LULA", mood, mouth, 0), "ZUMBI": ("ZUMBI", 1, mouth, 0)}.get(name, (name, mouth, 0))
    im = _SP3D[key]
    return name, im.crop(im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox())


def place_char(im, spec, cx, cy, face_h, tilt=0, hat=None, flip=False):
    """Pone al personaje con la CARA centrada en (cx, cy) y de alto face_h, inclinado tilt grados."""
    name, sp = char_img(spec)
    if flip:
        sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
    fx0, fy0, fx1, fy1 = FACE[name]
    if name == "LULA" and isinstance(spec, tuple) and spec[1] == "sad":
        fy1 = 0.70  # las gotas de lluvia no cuentan como cara
    if flip:
        fx0, fx1 = 1 - fx1, 1 - fx0
    k = face_h / ((fy1 - fy0) * sp.height)
    sp = _sharp(sp.resize((max(1, int(sp.width * k)), max(1, int(sp.height * k))), Image.LANCZOS))
    fcx, fcy = (fx0 + fx1) / 2 * sp.width, (fy0 + fy1) / 2 * sp.height
    if hat:  # objeto en la cabeza (los fideos de Toto)
        h = prop(hat, int(sp.width * 0.66))
        if h is not None:
            top = int(h.height * 0.30)
            can = Image.new("RGBA", (sp.width, sp.height + top), (0, 0, 0, 0))
            can.paste(sp, (0, top))
            hx = int((fx0 + fx1) / 2 * sp.width - h.width / 2)
            can.alpha_composite(h.rotate(-8, Image.BICUBIC, expand=False), (hx, 0))
            sp, fcy = can, fcy + top
    st, pad = sticker(sp, 16)
    fcx, fcy = fcx + pad, fcy + pad
    R = int(max(fcx, st.width - fcx, fcy, st.height - fcy) * 1.45)
    can = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
    can.paste(st, (int(R - fcx), int(R - fcy)))
    if tilt:
        can = can.rotate(tilt, Image.BICUBIC)
    _paste(im, can, int(cx - R), int(cy - R))


def _paste(dst, src, x, y):
    """alpha_composite que acepta coordenadas negativas o que se salen del cuadro."""
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(dst.width, x + src.width), min(dst.height, y + src.height)
    if x1 <= x0 or y1 <= y0:
        return
    dst.alpha_composite(src.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def draw_egg(h):
    """Huevo gigante con lunares azules (como el gorrito de Bombolín) y una grieta."""
    import numpy as np
    w = int(h * 0.78)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    nx = (xx - w / 2) / (w / 2)
    ny = (yy - h * 0.56) / (h * 0.5)
    ny = np.where(ny < 0, ny * 0.88, ny * 1.08)  # más fino arriba
    r = nx ** 2 + ny ** 2
    a = (np.clip((1 - r) * 60, 0, 1) * 255).astype("uint8")
    light = np.clip(1.12 - 0.32 * np.sqrt((nx + 0.35) ** 2 + (ny + 0.45) ** 2), 0.78, 1.05)
    base = np.array([255, 250, 232], float)
    rgb = np.clip(base[None, None] * light[..., None], 0, 255).astype("uint8")
    egg = Image.fromarray(rgb, "RGB").convert("RGBA")
    egg.putalpha(Image.fromarray(a, "L"))
    d = ImageDraw.Draw(egg)
    for (px, py, s) in [(0.3, 0.32, 0.11), (0.68, 0.24, 0.08), (0.62, 0.55, 0.12), (0.28, 0.68, 0.09), (0.55, 0.82, 0.07),
                        (0.8, 0.7, 0.06)]:
        d.ellipse([px * w - s * w, py * h - s * w, px * w + s * w, py * h + s * w], fill=(50, 130, 245))
    pts = [(0.18, 0.42), (0.3, 0.36), (0.38, 0.46), (0.5, 0.37), (0.6, 0.47), (0.7, 0.39), (0.8, 0.45)]
    d.line([(x * w, y * h) for x, y in pts], fill=(90, 60, 40), width=max(4, h // 70), joint="curve")
    m = Image.new("L", egg.size, 0)
    m.paste(egg.getchannel("A"))
    egg.putalpha(Image.fromarray(np.minimum(np.array(egg.getchannel("A")), a), "L"))
    return egg


def prop(name, size):
    """Objeto de la historia, de ancho/alto máximo `size`: PNG 3D, dibujo propio o emoji ampliado."""
    if name.startswith("draw:"):
        return {"egg": draw_egg}[name[5:]](size)
    d = _obj_dir()
    p = os.path.join(d, name + ".png") if d else None
    if p and os.path.exists(p):
        im = Image.open(p).convert("RGBA")
        im = im.crop(im.getbbox())
        k = size / max(im.width, im.height)
        return _sharp(im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS))
    if len(name) > 3 and name.isascii():
        return None
    return _sharp(B.emoji(name, size))


def place_prop(im, name, cx, cy, size, tilt=0):
    p = prop(name, size)
    if p is None:
        return
    st, pad = sticker(p, 12)
    if tilt:
        st = st.rotate(tilt, Image.BICUBIC, expand=True)
    _paste(im, st, int(cx - st.width / 2), int(cy - st.height / 2))


def bubbles(im, pts):
    for (x, y, s) in pts:
        b = prop("bubble", s)
        if b is not None:
            _paste(im, b, int(x - s / 2), int(y - s / 2))


def words(im, lines, cx, cy, size, fill=YELLOW, maxw=600, tilt=-4):
    """Texto gigante con contorno oscuro grueso y sombra; cada renglón se ajusta al ancho."""
    from PIL import ImageFilter
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    fs = []
    for ln in lines:
        s = size
        f = B.font(B.F700, s)
        while d.textlength(ln, font=f) > maxw and s > 50:
            s -= 4
            f = B.font(B.F700, s)
        fs.append(f)
    s = min(f.size for f in fs)  # todos los renglones del mismo tamaño
    f = B.font(B.F700, s)
    lh = s * 0.98
    y0 = cy - lh * (len(lines) - 1) / 2
    sw = max(8, s // 8)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    for i, ln in enumerate(lines):
        ds.text((cx + 4, y0 + i * lh + 12), ln, font=f, fill=(20, 5, 40, 200), anchor="mm", stroke_width=sw,
                stroke_fill=(20, 5, 40, 200))
        d.text((cx, y0 + i * lh), ln, font=f, fill=fill, anchor="mm", stroke_width=sw, stroke_fill=INK4)
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    if tilt:
        sh = sh.rotate(tilt, Image.BICUBIC, center=(cx, cy))
        lay = lay.rotate(tilt, Image.BICUBIC, center=(cx, cy))
    im.alpha_composite(sh)
    im.alpha_composite(lay)


def _lines(c, key, lang):
    v = c[key if lang == "es" else "e" + key[1:]]
    return (v,) if isinstance(v, str) else v


def v1_4(ep, lang):
    """Protagonista ENORME a la derecha + objeto grande abajo a la izquierda + 2 o 3 palabras."""
    c = t4conf(ep)
    star = c["star"]
    name = star[0] if isinstance(star, tuple) else star
    fh = FACE_H[name] * H
    cx, cy = W * 0.70, H * 0.47
    im = radial_bg(c["bg"][0], cx, cy)
    _glow(im, cx, cy, fh * 0.75)
    obj = c["obj"]
    big = obj in ("bathtub", "bed")
    ox, oy = (W * 0.27, H * 0.72) if big else (W * 0.25, H * 0.70)
    place_char(im, star, cx, cy, fh, tilt=-6, hat=c.get("hat"))
    place_prop(im, obj, ox, oy, 470 if big else (380 if obj.startswith("draw:") else 340), tilt=5)
    if c.get("extra") == "bubbles":
        bubbles(im, [(W * 0.08, H * 0.50, 90), (W * 0.42, H * 0.52, 70), (W * 0.47, H * 0.80, 110), (W * 0.06, H * 0.88, 60),
                     (W * 0.52, H * 0.25, 80), (W * 0.94, H * 0.12, 70)])
    words(im, _lines(c, "w1", lang), W * 0.27, H * 0.24, 150, maxw=W * 0.50)
    return im


def v2_4(ep, lang):
    """Dos personajes reaccionando al objeto (en el centro); una sola palabra o ninguna."""
    c = t4conf(ep)
    a, b = c["pair"]
    im = radial_bg(c["bg"][1], W / 2, H * 0.62)
    _glow(im, W / 2, H * 0.62, 260)
    obj = c.get("obj2", c["obj"])
    big = obj in ("bathtub", "bed")
    for spec, x, t, fl in ((a, W * 0.20, 8, False), (b, W * 0.80, -8, True)):
        n = spec[0] if isinstance(spec, tuple) else spec
        fh = FACE_H[n] * H * (0.78 if n != "ABU" else 0.72)
        # Abu mira hacia el centro: su cabeza está a la izquierda del sprite, se espeja si va a la izquierda.
        place_char(im, spec, x if n != "ABU" else (W * 0.17 if not fl else W * 0.80), H * 0.56 if n != "ABU" else H * 0.44,
                   fh, tilt=t, hat=c.get("hat") if spec == c["star"] else None, flip=(not fl) and n == "ABU")
    place_prop(im, obj, W / 2, H * 0.68, 480 if big else 330)
    if c.get("extra") == "bubbles":
        bubbles(im, [(W * 0.36, H * 0.38, 80), (W * 0.62, H * 0.33, 100), (W * 0.50, H * 0.20, 60), (W * 0.66, H * 0.92, 70)])
    w = _lines(c, "w2", lang)
    if w and w[0]:
        words(im, w, W / 2, H * 0.14, 130, maxw=W * 0.5, tilt=3)
    return im


def v3_4(ep, lang):
    """Otro personaje grande a la izquierda con una pregunta «¿…?» gigante en blanco a la derecha."""
    c = t4conf(ep)
    q = c["q"]
    name = q[0] if isinstance(q, tuple) else q
    fh = FACE_H[name] * H * 0.95
    cx, cy = W * 0.28, H * 0.50
    im = radial_bg(c["bg"][2], cx, cy)
    _glow(im, cx, cy, fh * 0.75)
    obj = c.get("obj3", c["obj"])
    big = obj in ("bathtub", "bed")
    place_char(im, q, cx if name != "ABU" else W * 0.34, cy, fh, tilt=6, flip=name == "ABU")
    place_prop(im, obj, W * 0.74, H * 0.73, 400 if big else 260, tilt=-6)
    words(im, _lines(c, "w3", lang), W * 0.72, H * 0.27, 140, fill=(255, 255, 255), maxw=W * 0.48, tilt=3)
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
    only = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None  # p. ej. 1,2,3
    for n, ep in EPISODES.items():
        if only and n not in only:
            continue
        pal = PALETTE[n % len(PALETTE)]
        for lang in ("es", "en"):
            fns = (v1_4, v2_4, v3_4) if VIVID and os.environ.get("BOMBOLIN_SPRITES3D") else (v1, v2, v3)
            for k, f in enumerate(fns, 1):
                im = f(ep, lang) if f in (v1_4, v2_4, v3_4) else f(ep, lang, pal)
                finish(im).convert("RGB").save(os.path.join(out, f"E{n:02d}_{lang.upper()}_miniatura{k}.jpg"), quality=90)
    for cid, eps in ([] if only else COMPS):
        for lang in ("es", "en"):
            for k in range(3):
                compilation(eps, lang, k, comp_label(cid, eps, lang)).convert("RGB").save(
                    os.path.join(out, f"{cid}_{lang.upper()}_miniatura{k + 1}.jpg"), quality=90)
    print("ok", len(os.listdir(out)))


if __name__ == "__main__":
    main()
