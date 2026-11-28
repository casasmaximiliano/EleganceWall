"""Bombolín y sus amigos: render de los personajes en CAPAS separadas («rig 2D») para animarlos en el compositor.

Uso: python3 partes.py CARPETA_SALIDA [PIPO TOTO LULA ZUMBI ABU]

Usa los mismos constructores de `modelos.py` (misma cámara, mismo lienzo de 900x900) y renderiza varias pasadas
ocultando objetos con `hide_render` (lo oculto no tapa ni hace sombra). Por personaje, en CARPETA/C/:
  body_m{m}_c{c}.png        todo menos brazos, iris/pupilas (y, en PIPO y ABU, la cabeza) — LULA: body_{ánimo}_m{m}_c{c}.png
  body.png                  PIPO y ABU: torso, patas y cola, sin cabeza ni brazos
  head_m{m}_c{c}.png        PIPO y ABU: la cabeza (gorrito, hocico, boca, blancos de los ojos o párpados, anteojos)
  pupil.png                 un solo iris + pupila + brillos, recortado (se dibuja en cada centro de ojo)
  eyes_mask.png             parte visible de los blancos de los ojos (alfa), para recortar la pupila si se la mueve mucho
  arm_L.png / arm_R.png     PIPO: un brazo por capa, lienzo completo (L = izquierda de la PANTALLA)
  wing_L.png / wing_R.png   ZUMBI: un ala por capa (abierta), lienzo completo
  rig.json                  centros de ojos, pivotes (hombros, cuello, alas), orden de capas, tamaño de la pupila
Los archivos que ya existen no se vuelven a renderizar (Blender sin GPU a veces se cae: volver a correrlo).
Al final se compara la superposición de capas con el render normal (_ref/) y se guarda el error en rig.json.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modelos as M  # noqa: E402  (lee OUT = sys.argv[1])
import bpy  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
from mathutils import Vector  # noqa: E402

OUT = sys.argv[1]
CHARS = [a for a in sys.argv[2:] if not a.startswith("-")] or ["PIPO", "TOTO", "LULA", "ZUMBI", "ABU"]
W = H = 900
IRIS = {"iris", "pupil", "glint", "glint2"}
HEAD = {
    "PIPO": {"head", "snout", "eyew", "lid", "lidline", "cheek", "mouth", "tongue", "tooth", "smile", "hat", "dot"},
    "ABU": {"head", "eyew", "lid", "lidline", "glass", "bridge", "cheek", "mouth", "tongue", "tooth", "smile"},
}
BUILD = {
    "PIPO": lambda m, c, v=None: M.bombolin(m, c),
    "TOTO": lambda m, c, v=None: M.toto(m, c),
    "LULA": lambda m, c, v=None: M.lula(m, c, v),
    "ZUMBI": lambda m, c, v=None: M.zumbi(m, c, 1),
    "ABU": lambda m, c, v=None: M.abu(m, c),
}


def base(o):
    return o.name.split(".")[0]


def geo():
    return [o for o in bpy.context.scene.objects if o.type in ("MESH", "META", "CURVE")]


def render_pass(sc, path, visible, shadow=lambda o: False, holdout=lambda o: False):
    """Renderiza solo los objetos con visible(o). holdout(o): tapan como «agujero» transparente.
    shadow(o): no se ven en cámara pero siguen dando sombra (partes quietas respecto de la capa).
    El resto se oculta del todo (hide_render): no tapa ni da sombra."""
    if os.path.exists(path):
        return
    for o in geo():
        v, h, s = visible(o), holdout(o), shadow(o)
        o.hide_render = not (v or h or s)
        o.is_holdout = bool(h and not v)
        o.visible_camera = bool(v or h)
    M.render(sc, path)
    for o in geo():
        o.hide_render = False
        o.is_holdout = False
        o.visible_camera = True
    print("OK", path, flush=True)


def px(sc, co):
    u, v, _ = world_to_camera_view(sc, sc.camera, Vector(co))
    return [round(u * W, 1), round((1 - v) * H, 1)]


def build(who, m, c, v=None):
    M._mats.clear()
    sc = BUILD[who](m, c, v)
    FIX.get(who, lambda sc, v: None)(sc, v)
    bpy.context.view_layer.update()
    return sc


# ------------------------------------------------------------------ retoques (solo en las capas; modelos.py no cambia)
def fix_pipo(sc, v):
    """La panza amarilla casi coincide con la superficie del cuerpo arriba: se ve una línea fantasma (z-fighting).
    Se la adelanta 6 mm y se agranda 1 % en profundidad; además la boca ya no proyecta sombra sobre la panza."""
    sc.eevee.taa_render_samples = 96
    sc.eevee.shadow_ray_count = 2
    for o in geo():
        if base(o) == "belly":
            o.location.y -= 0.006
            o.scale.y *= 1.01
        # la sonrisa y la boca proyectaban un arco de sombra granulado arriba de la panza
        if base(o) in ("smile", "mouth", "tongue", "eyew", "iris", "pupil", "glint", "glint2", "lid", "lidline", "cheek"):
            o.visible_shadow = False


def fix_lula(sc, v):
    sc.eevee.taa_render_samples = 96  # menos grano en las sombras suaves de la cara
    sc.eevee.shadow_ray_count = 3
    sc.eevee.shadow_step_count = 12
    for o in geo():
        if base(o) in ("eyew", "lash", "iris", "pupil", "glint", "glint2", "lid", "lidline"):
            o.visible_shadow = False  # los ojos ya no manchan la cara con sombra granulada
    # pestañas pegadas al borde de arriba del blanco (antes flotaban un poco arriba)
    r, ey, ez = 0.12, -0.46, 1.12
    for o in geo():
        if base(o) != "lash":
            continue
        ex = min((-0.22, 0.22), key=lambda e: abs(o.location.x - e))
        a = o.rotation_euler.y  # inclinación de la pestaña
        h = 0.45 * r
        bx = o.location.x - ex - (h / 2) * math.sin(a)  # x del pie de la pestaña, relativo al ojo
        yy = 0.3 / 0.85
        zs = 1.08 * r * math.sqrt(max(0.0, 1 - (bx / r) ** 2 - yy ** 2))  # alto del blanco en ese punto
        o.location.z = ez + zs - 0.06 * r + (h / 2) * math.cos(a)  # el pie queda apenas metido en el blanco
    # patitas de arcoíris en todos los ánimos (en modelos.py solo las tiene «happy»)
    if v != "happy" and not any(base(o) == "rainbow" for o in geo()):
        for i, col in enumerate([(255, 90, 90), (255, 170, 60), (255, 230, 80), (110, 210, 110), (90, 160, 255),
                                 (170, 110, 230)]):
            M.torus((0, 0.05, 0.55), 0.62 - i * 0.055, 0.03, M.mat(f"rb{i}", col, 0.4, emis=0.3),
                    rot=(math.radians(90), 0, 0), name="rainbow", arc=(0, 0, 1))


def fix_abu(sc, v):
    sc.eevee.taa_render_samples = 96  # menos grano en el caparazón
    sc.eevee.shadow_ray_count = 2
    skin = None
    for o in geo():
        if base(o) == "leg":
            skin = o.data.materials[0]
            bv = o.modifiers.new("bevel", "BEVEL")  # bordes redondeados: ya no parecen caños
            bv.width, bv.segments, bv.limit_method = 0.07, 5, "ANGLE"
            x, y, _ = o.location
            M.sphere((x, y - 0.03, 0.07), (0.19, 0.22, 0.09), skin, name="foot")  # piecito blando
            for k in (-1, 0, 1):  # deditos
                M.sphere((x + k * 0.08, y - 0.2, 0.05), (0.045, 0.04, 0.035), M.mat("toe", (235, 230, 200), 0.5),
                         name="toe")


FIX = {"PIPO": fix_pipo, "LULA": fix_lula, "ABU": fix_abu}


def is_arm(o):
    return base(o) == "arm"


def side(o):
    return "L" if o.matrix_world.translation.x < 0 else "R"


# ------------------------------------------------------------------ pasadas
def passes(who):
    d = os.path.join(OUT, who)
    ref = os.path.join(d, "_ref")
    os.makedirs(ref, exist_ok=True)
    head = HEAD.get(who, set())
    variants = list(M.LULA_COL) if who == "LULA" else [None]
    rig = {"canvas": [W, H]}
    for v in variants:
        for m in (0, 1):
            for c in (0, 1):
                tag = (f"{v}_" if v else "") + f"m{m}_c{c}"
                todo = [os.path.join(ref, f"full_{tag}.png")]
                bodyp = os.path.join(d, f"body_{tag}.png") if not head else None
                headp = os.path.join(d, f"head_m{m}_c{c}.png") if head else None
                todo += [p for p in (bodyp, headp) if p]
                first = v == variants[0] and m == 0 and c == 0
                if not first and all(os.path.exists(p) for p in todo):
                    continue
                sc = build(who, m, c, v)
                iris = lambda o: base(o) in IRIS  # noqa: E731
                moving = lambda o: is_arm(o) or base(o) == "wing"  # noqa: E731
                render_pass(sc, todo[0], lambda o: True)
                if bodyp:
                    render_pass(sc, bodyp, lambda o: not iris(o) and not moving(o))
                if headp:
                    render_pass(sc, headp, lambda o: base(o) in head,
                                holdout=lambda o: not iris(o) and not moving(o))  # el torso tapa la papada como en 3D
                if not first:
                    continue
                # pasadas que no dependen de la boca ni de los ojos cerrados (estado m0 c0)
                if head:
                    render_pass(sc, os.path.join(d, "body.png"),
                                lambda o: base(o) not in head and not iris(o) and not moving(o),
                                lambda o: base(o) in head)
                for s in ("L", "R"):
                    for kind, test in (("arm", is_arm), ("wing", lambda o: base(o) == "wing")):
                        if not any(test(o) for o in geo()):
                            continue
                        mine = lambda o, s=s, test=test: test(o) and side(o) == s  # noqa: E731
                        # entera (va detrás del cuerpo) y «_front»: solo lo que se ve delante del cuerpo
                        render_pass(sc, os.path.join(d, f"{kind}_{s}.png"), mine,
                                    lambda o: not moving(o) and not iris(o))
                        render_pass(sc, os.path.join(d, f"{kind}_{s}_front.png"), mine,
                                    lambda o: False, lambda o: not moving(o) and not iris(o))
                # iris entero (sin recortar); el compositor lo recorta con eyes_mask.png
                render_pass(sc, os.path.join(ref, "irises.png"), iris, lambda o: not iris(o))
                render_pass(sc, os.path.join(d, "eyes_mask.png"), lambda o: base(o) == "eyew",
                            holdout=lambda o: not iris(o))
                rig.update(geometry(sc, who))
    return rig


def geometry(sc, who):
    """Centros de ojos y pivotes proyectados al lienzo."""
    bpy.context.view_layer.update()  # sin esto la cámara recién creada no tiene matrix_world
    g = {}
    irises = sorted([o for o in geo() if base(o) == "iris"], key=lambda o: o.matrix_world.translation.x)
    g["eyes"] = [px(sc, o.matrix_world.translation) for o in irises]
    g["eyes_on"] = "head" if who in HEAD else "body"
    arms = {side(o): o for o in geo() if is_arm(o)}
    if arms:
        g["arms"] = {}
        for s, o in arms.items():
            # hombro: borde de arriba y hacia adentro del brazo (queda metido en el cuerpo)
            sg = -1 if s == "L" else 1
            p = o.matrix_world @ Vector((-sg * 0.55, 0, 0.55))
            g["arms"][s] = {"pivot": px(sc, p)}
    wings = {side(o): o for o in geo() if base(o) == "wing"}
    if wings:
        g["wings"] = {}
        for s, o in wings.items():
            sg = -1 if s == "L" else 1
            g["wings"][s] = {"pivot": px(sc, o.matrix_world @ Vector((-sg * 0.85, 0, 0)))}
    if who == "PIPO":
        g["head_pivot"] = px(sc, (0, -0.05, 1.08))
    if who == "ABU":
        neck = [o for o in geo() if base(o) == "neck"][0]
        g["head_pivot"] = px(sc, neck.matrix_world @ Vector((0, 0, 0.22)))
    return g


# ------------------------------------------------------------------ armado y verificación (PIL)
def load(p):
    return Image.open(p).convert("RGBA")


def paste(canvas, layer, dx=0, dy=0, rot=0, pivot=None):
    if rot and pivot:
        layer = layer.rotate(rot, resample=Image.BICUBIC, center=tuple(pivot))
    t = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    t.paste(layer, (int(round(dx)), int(round(dy))))
    return Image.alpha_composite(canvas, t)


def pupil_sprite(who, rig):
    d = os.path.join(OUT, who)
    a = np.array(load(os.path.join(d, "_ref", "irises.png")))
    ex, ey = rig["eyes"][-1]  # ojo de la derecha de la pantalla
    mid = (rig["eyes"][0][0] + rig["eyes"][1][0]) / 2
    al = a[..., 3].copy()
    al[:, : int(mid)] = 0
    ys, xs = np.nonzero(al > 2)
    cx, cy = int(round(ex)), int(round(ey))
    hw = int(max(cx - xs.min(), xs.max() - cx)) + 3
    hh = int(max(cy - ys.min(), ys.max() - cy)) + 3
    crop = a[cy - hh: cy + hh + 1, cx - hw: cx + hw + 1].copy()
    crop[..., 3] = np.where(np.arange(crop.shape[1])[None, :] + cx - hw < mid, 0, crop[..., 3])
    img = Image.fromarray(crop)
    img.save(os.path.join(d, "pupil.png"))
    rig["pupil_size"] = [img.width, img.height]
    rig["pupil_anchor"] = "center"
    return img


def put_pupils(canvas, rig, pup, mask, dx=0, dy=0, rot=0, pivot=None):
    """Pupilas en los centros de los ojos, recortadas con la máscara del blanco (que gira con la cabeza)."""
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    for ex, ey in rig["eyes"]:
        lay = paste(lay, pup, ex + dx - pup.width / 2 + 0.5, ey + dy - pup.height / 2 + 0.5)
    if rot and pivot:
        lay = lay.rotate(rot, resample=Image.BICUBIC, center=tuple(pivot))
        mask = mask.rotate(rot, resample=Image.BICUBIC, center=tuple(pivot))
    a = np.asarray(lay).copy()
    a[..., 3] = (a[..., 3].astype(np.uint16) * np.asarray(mask.getchannel("A")) // 255).astype(np.uint8)
    return Image.alpha_composite(canvas, Image.fromarray(a))


def compose(who, rig, tag, order, arm_rot=None, head_rot=0, look=(0, 0), wing_rot=None):
    d = os.path.join(OUT, who)
    c = tag.endswith("c1")
    m_c = tag[-5:]
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pup = load(os.path.join(d, "pupil.png"))
    mask = load(os.path.join(d, "eyes_mask.png"))
    for lay in order:
        if lay == "body":
            cv = paste(cv, load(os.path.join(d, "body.png" if who in HEAD else f"body_{tag}.png")))
            if who not in HEAD and not c:
                cv = put_pupils(cv, rig, pup, mask, *look)
        elif lay == "head":
            hv = load(os.path.join(d, f"head_{m_c}.png"))
            cv = paste(cv, hv, rot=head_rot, pivot=rig["head_pivot"])
            if not c:
                cv = put_pupils(cv, rig, pup, mask, look[0], look[1], head_rot, rig["head_pivot"])
        elif lay.startswith("arm_"):
            s = lay[4]
            cv = paste(cv, load(os.path.join(d, lay + ".png")), rot=(arm_rot or {}).get(s, 0),
                       pivot=rig["arms"][s]["pivot"])
        elif lay.startswith("wing_"):
            s = lay[5]
            cv = paste(cv, load(os.path.join(d, lay + ".png")), rot=(wing_rot or {}).get(s, 0),
                       pivot=rig["wings"][s]["pivot"])
    return cv


def err(a, b):
    """Diferencia media en RGB premultiplicado (0-255) y máximo del 99,9 %."""
    A = np.asarray(a, dtype=np.float32)
    B = np.asarray(b, dtype=np.float32)
    pa = np.concatenate([A[..., :3] * A[..., 3:] / 255, A[..., 3:]], -1)
    pb = np.concatenate([B[..., :3] * B[..., 3:] / 255, B[..., 3:]], -1)
    dd = np.abs(pa - pb).max(-1)
    mask = (A[..., 3] > 0) | (B[..., 3] > 0)
    return float(dd[mask].mean()), float(np.percentile(dd[mask], 99.9))


def choose_order(who, rig, tag):
    """Cada brazo/ala puede ir detrás o delante del cuerpo: se elige el que reproduce mejor el render normal."""
    ref = load(os.path.join(OUT, who, "_ref", f"full_{tag}.png"))
    order = ["body"] + (["head"] if who in HEAD else [])
    parts = [f"arm_{s}" for s in rig.get("arms", {})] + [f"wing_{s}" for s in rig.get("wings", {})]
    for p in parts:
        back = [p] + order
        i = order.index("body") + 1
        both = [p] + order[:i] + [p + "_front"] + order[i:]  # entera detrás + parte visible delante
        order = min((back, both), key=lambda o: err(compose(who, rig, tag, o), ref)[0])
    return order


def pupil_range(who, rig, pup):
    """Cuánto se puede correr la pupila sin salirse del blanco (se pierde como mucho un 3 % más de iris)."""
    mask = np.asarray(load(os.path.join(OUT, who, "eyes_mask.png")))[..., 3] > 128
    pa = np.asarray(pup)[..., 3] > 128
    ph, pw = pa.shape

    def cover(dx, dy):
        out = []
        for ex, ey in rig["eyes"]:
            x0 = int(round(ex + dx - pw / 2 + 0.5))
            y0 = int(round(ey + dy - ph / 2 + 0.5))
            win = mask[y0: y0 + ph, x0: x0 + pw]
            out.append((pa & win).sum() / pa.sum() if win.shape == pa.shape else 0.0)
        return out  # la máscara se renderizó sin iris: incluye el blanco que el iris tapa

    base_c = cover(0, 0)
    dirs = {"x": (1, 0), "-x": (-1, 0), "y": (0, 1), "-y": (0, -1)}
    per_eye = []
    for e in range(len(base_c)):
        rng = {}
        for name, (ux, uy) in dirs.items():
            r = 0
            for k in range(1, 80):
                if cover(ux * k, uy * k)[e] < base_c[e] * 0.75:
                    break
                r = k
            rng[name] = r
        per_eye.append(rng)
    rig["pupil_range_per_eye"] = per_eye
    rng = {k: min(p[k] for p in per_eye) for k in dirs}
    return rng, base_c


def contact(who, rig, tags):
    d = os.path.join(OUT, who)
    order = rig["order"]
    tiles = []
    for tag in tags:
        ref = load(os.path.join(d, "_ref", f"full_{tag}.png"))
        comp = compose(who, rig, tag, order)
        e = err(comp, ref)
        rig.setdefault("verify", {})[tag] = {"mean": round(e[0], 3), "p99.9": round(e[1], 1)}
        dif = np.abs(np.asarray(comp, np.int16) - np.asarray(ref, np.int16))[..., :4].max(-1)
        dimg = Image.fromarray(np.clip(dif * 4, 0, 255).astype(np.uint8)).convert("RGBA")
        tiles += [(f"ref {tag}", ref), ("capas", comp), (f"dif x4 ({e[0]:.2f})", dimg)]
    t0 = tags[0]
    r = rig["pupil_range_xy"]
    poses = [("brazos +30/-30", dict(arm_rot={"L": 30, "R": -30})),
             ("brazos -30/+30", dict(arm_rot={"L": -30, "R": 30})),
             ("cabeza 8°", dict(head_rot=8)), ("cabeza -8°", dict(head_rot=-8)),
             ("mira izq.", dict(look=(-r["-x"], 0))), ("mira der.", dict(look=(r["x"], 0))),
             ("mira arriba", dict(look=(0, -r["-y"]))), ("alas ±25°", dict(wing_rot={"L": -25, "R": 25})),
             ("todo junto", dict(arm_rot={"L": 30, "R": 30}, head_rot=-8, look=(r["x"], -r["-y"]),
                                 wing_rot={"L": 25, "R": -25}))]
    for name, kw in poses:
        if "arm_rot" in kw and "arms" not in rig and name != "todo junto":
            continue
        if "head_rot" in kw and "head_pivot" not in rig and name != "todo junto":
            continue
        if "wing_rot" in kw and "wings" not in rig and name != "todo junto":
            continue
        tiles.append((name, compose(who, rig, t0, order, **kw)))
    S = 300
    cols = 6
    rows = (len(tiles) + cols - 1) // cols
    from PIL import ImageDraw
    sheet = Image.new("RGBA", (cols * S, rows * (S + 22)), (90, 170, 90, 255))
    dr = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(tiles):
        x, y = (i % cols) * S, (i // cols) * (S + 22)
        bg = Image.new("RGBA", im.size, (0, 0, 0, 255) if name.startswith("dif") else (90, 170, 90, 255))
        sheet.paste(Image.alpha_composite(bg, im).resize((S, S), Image.LANCZOS), (x, y + 22))
        dr.text((x + 4, y + 4), name, fill=(255, 255, 255, 255))
    p = os.path.join(OUT, f"contact_{who}.png")
    sheet.convert("RGB").save(p)
    # detalle al 100 %: hombros y cuello con la pose más exigente
    big = compose(who, rig, t0, order, **poses[-1][1])
    bg = Image.new("RGBA", big.size, (90, 170, 90, 255))
    Image.alpha_composite(bg, big).convert("RGB").save(os.path.join(OUT, f"pose_{who}.png"))
    return p


def finish(who, rig):
    d = os.path.join(OUT, who)
    pup = pupil_sprite(who, rig)
    rng, cov = pupil_range(who, rig, pup)
    rig["pupil_range_xy"] = rng  # px por dirección (x = derecha, y = abajo)
    rig["pupil_range"] = min(rng.values())
    rig["order"] = choose_order(who, rig, "m0_c0" if who != "LULA" else "calm_m0_c0")
    tags = [f"m{m}_c{c}" for m in (0, 1) for c in (0, 1)]
    if who == "LULA":
        tags = [f"{v}_{t}" for v in M.LULA_COL for t in tags]
    p = contact(who, rig, tags[:4] if who != "LULA" else tags[:4] + ["happy_m1_c0", "angry_m0_c1"])
    for t in tags:  # verificar todos los estados aunque no salgan en la hoja
        if t not in rig["verify"]:
            e = err(compose(who, rig, t, rig["order"]), load(os.path.join(d, "_ref", f"full_{t}.png")))
            rig["verify"][t] = {"mean": round(e[0], 3), "p99.9": round(e[1], 1)}
    rig["notes"] = {
        "L_R": "L/R = lado izquierdo/derecho de la PANTALLA, no del personaje",
        "order": "capas de atrás hacia adelante; las pupilas van sobre la capa de 'eyes_on'. X_front.png = la parte de X que se ve delante del cuerpo: se dibuja ADEMÁS de X.png (entera, detrás) con la misma rotación y pivote, así al girar no quedan huecos",
        "pupils": "pupil.png centrado en cada punto de 'eyes' (+ desplazamiento de la mirada), recortado con el alfa de eyes_mask.png (lienzo completo; gira con la cabeza si eyes_on=head). Con c=1 (ojos cerrados) no se dibujan",
        "pupil_range": "px que se puede mover la pupila y que en los dos ojos se siga viendo al menos el 75 % del iris que se ve en reposo (lo que se sale lo recorta eyes_mask, como un ojo que gira); pupil_range_xy por dirección (x = derecha, y = abajo) y pupil_range_per_eye por ojo",
        "rotation": "grados en sentido antihorario (como PIL Image.rotate) alrededor del pivote",
    }
    if who == "LULA":
        rig["body_files"] = "body_{mood}_m{m}_c{c}.png, moods: " + ", ".join(M.LULA_COL)
    elif who in HEAD:
        rig["body_files"] = "body.png (fija) + head_m{m}_c{c}.png"
    else:
        rig["body_files"] = "body_m{m}_c{c}.png"
    with open(os.path.join(d, "rig.json"), "w") as f:
        json.dump(rig, f, indent=1, ensure_ascii=False)
    print("RIG", who, json.dumps(rig["verify"]), "->", p, flush=True)


def main():
    for who in CHARS:
        rig = passes(who)
        if "eyes" not in rig:  # todo ya renderizado: rearmar la geometría sin renderizar
            sc = build(who, 0, 0, "calm" if who == "LULA" else None)
            rig.update(geometry(sc, who))
        finish(who, rig)


if __name__ == "__main__":
    main()
