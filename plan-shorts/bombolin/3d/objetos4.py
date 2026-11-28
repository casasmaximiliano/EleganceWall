"""Objetos 3D para reemplazar los emojis de los bloques de la biblioteca (canciones, juegos, ¿Sabías qué?).
Mismo estilo y luz que objetos.py / objetos2.py: formas redondeadas de juguete, colores vivos, fondo transparente.

Uso: python3 objetos4.py CARPETA_SALIDA [objeto ...]
No pisa archivos que ya existan en la carpeta.
"""
import math
import os
import random

import bpy
from mathutils import Vector

import objetos as O
from objetos import cam, setup
from modelos import mat, sphere, cyl, torus, cone
import modelos as M

R = math.radians
INK = (45, 35, 55)


# ------------------------------------------------------------------ utilidades
def box(loc, size, m, bevel=0.08, rot=(0, 0, 0)):
    """Caja redondeada con el origen en su centro (objetos.box aplica la posición a la malla y no se puede rotar)."""
    o = O.box((0, 0, 0), size, m, bevel)
    o.location = loc
    o.rotation_euler = rot
    return o


def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def rounded(pts, r, n=6):
    """Redondea las esquinas de un polígono 2D (lista de (x, y)) con arcos de radio r."""
    out = []
    N = len(pts)
    for i in range(N):
        P, A, B = Vector(pts[i]), Vector(pts[i - 1]), Vector(pts[(i + 1) % N])
        u, v = (A - P), (B - P)
        la, lb = u.length, v.length
        u.normalize()
        v.normalize()
        th = math.acos(max(-1, min(1, u.dot(v))))
        if th < 1e-3 or th > math.pi - 1e-3:
            out.append(tuple(P))
            continue
        d = min(r / math.tan(th / 2), 0.45 * la, 0.45 * lb)
        rr = d * math.tan(th / 2)
        bis = (u + v).normalized()
        C = P + bis * (rr / math.sin(th / 2))
        T1, T2 = P + u * d, P + v * d
        a1 = math.atan2(T1.y - C.y, T1.x - C.x)
        a2 = math.atan2(T2.y - C.y, T2.x - C.x)
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for k in range(n + 1):
            a = a1 + da * k / n
            out.append((C.x + rr * math.cos(a), C.y + rr * math.sin(a)))
    return out


def shape(pts, m, depth=0.08, bevel=0.04, loc=(0, 0, 0), rot=(R(90), 0, 0), smooth=False, name="sh"):
    """Forma 2D (x, z de frente a la cámara) extruida y con bordes redondeados (curva con bisel)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    cu.extrude = depth
    cu.bevel_depth = bevel
    cu.bevel_resolution = 6
    cu.resolution_u = 24
    if smooth:
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(len(pts) - 1)
        for p, (x, y) in zip(sp.bezier_points, pts):
            p.co = (x, y, 0)
            p.handle_left_type = p.handle_right_type = "AUTO"
    else:
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for p, (x, y) in zip(sp.points, pts):
            p.co = (x, y, 0, 1)
    sp.use_cyclic_u = True
    sp.use_smooth = True
    cu.materials.append(m)
    ob = link(bpy.data.objects.new(name, cu))
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def tube(pts, r, m, radii=None, name="tb", poly=False, res=12):
    """Tubo 3D por una lista de puntos (curva suave), con radio por punto opcional."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 6
    cu.resolution_u = res
    cu.use_fill_caps = True
    if poly:
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for i, (p, c) in enumerate(zip(sp.points, pts)):
            p.co = (c[0], c[1], c[2], 1)
            if radii:
                p.radius = radii[i]
    else:
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(len(pts) - 1)
        for i, (p, c) in enumerate(zip(sp.bezier_points, pts)):
            p.co = c
            p.handle_left_type = p.handle_right_type = "AUTO"
            if radii:
                p.radius = radii[i]
    sp.use_smooth = True
    cu.materials.append(m)
    return link(bpy.data.objects.new(name, cu))


def group(objs, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0):
    """Agrupa objetos bajo un vacío para moverlos/rotarlos juntos."""
    e = link(bpy.data.objects.new("grp", None))
    for o in objs:
        o.parent = e
    e.location = loc
    e.rotation_euler = rot
    e.scale = (scale, scale, scale)
    return e


def deform(o, fn):
    """Deforma los vértices (coordenadas locales, antes de la escala del objeto)."""
    for v in o.data.vertices:
        v.co = fn(Vector(v.co))
    return o


def since(fn):
    """Lista de objetos creados por fn() (para agrupar)."""
    before = set(bpy.data.objects)
    fn()
    return [o for o in bpy.data.objects if o not in before]


def face(x, y, z, s, skin, closed=False, open_=False, cheeks=True, iris=(60, 40, 30), gap=0.36, er=0.2):
    """Carita: ojos grandes (modelos.eye) + sonrisa + cachetes, mirando a -Y. s = tamaño."""
    for sx in (-1, 1):
        M.eye(x + sx * gap * s, y, z + 0.12 * s, er * s, iris, closed, skin)
    M.mouth(x, y - 0.02 * s, z - 0.22 * s, 0.34 * s, open_)
    if cheeks:
        for sx in (-1, 1):
            sphere((x + sx * (gap + 0.2) * s, y + 0.01 * s, z - 0.12 * s), (0.09 * s, 0.03 * s, 0.06 * s),
                   mat("cheek", (255, 140, 160), 0.6))


def shine(loc, s, rot=(0, 0, 0)):
    """Brillito blanco de juguete plástico."""
    o = sphere(loc, (0.075 * s, 0.02 * s, 0.045 * s), mat("shine", (255, 255, 255), 0.0, emis=1.0, alpha=0.75))
    o.rotation_euler = rot
    return o


def sparkle(loc, s, col=(255, 250, 200)):
    """Destello de 4 puntas."""
    pts = []
    for k in range(8):
        a = k / 8 * 2 * math.pi + math.pi / 2
        rr = 1.0 if k % 2 == 0 else 0.28
        pts.append((rr * s * math.cos(a), rr * s * math.sin(a)))
    return shape(rounded(pts, 0.04 * s), mat("spark", col, 0.2, emis=2.5), depth=0.01 * s, bevel=0.03 * s, loc=loc)


def star_pts(n, r1, r2, rot=math.pi / 2):
    pts = []
    for k in range(2 * n):
        a = rot + k * math.pi / n
        rr = r1 if k % 2 == 0 else r2
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    return pts


def ell_y(c, sc, x, z, off=0.0):
    """Coordenada y (lado de la cámara) de la superficie de un elipsoide en (x, z)."""
    a, b, cc = sc
    t = 1 - ((x - c[0]) / a) ** 2 - ((z - c[2]) / cc) ** 2
    return c[1] - b * math.sqrt(max(t, 0.0)) - off


# ------------------------------------------------------------------ objetos
def paws():
    sc = setup()
    P = mat("pawpad", (120, 75, 60), 0.5)
    Pk = mat("pawpink", (255, 150, 170), 0.5)
    allo = []
    for (x, z, r) in [(-0.38, 0.0, -18), (0.38, 0.9, 14)]:
        parts = [sphere((0, 0, 0), (0.33, 0.08, 0.27), P)]
        parts.append(sphere((0, -0.05, -0.02), (0.18, 0.05, 0.13), Pk))
        for k, a in enumerate((-52, -18, 18, 52)):
            ax = math.radians(a)
            parts.append(sphere((0.44 * math.sin(ax), 0, 0.27 + 0.2 * math.cos(ax)), (0.12, 0.08, 0.14), P))
        allo.append(group(parts, (x, 0, z), (0, R(r), 0)))
    group(allo, (0, 0, 0), (R(-30), 0, 0))
    cam(sc, (0, 0, 0.45), 2.5, height=1.8)
    return sc


def wind():
    sc = setup()
    cols = [(140, 210, 255), (180, 230, 255), (110, 190, 250)]
    for i, (z, L, curl) in enumerate([(1.05, 1.9, 0.26), (0.55, 2.3, 0.3), (0.05, 1.6, 0.22)]):
        pts = []
        x0 = -1.15 + i * 0.12
        n = 10
        for k in range(n):  # tramo recto con ondita
            t = k / (n - 1)
            pts.append((x0 + t * L, -0.1 * i, z + 0.05 * math.sin(t * 5 + i)))
        cx, cz = pts[-1][0], pts[-1][2] + curl
        for k in range(1, 16):  # rulo al final
            a = -math.pi / 2 + k / 15 * 1.7 * math.pi
            rr = curl * (1 - 0.45 * k / 15)
            pts.append((cx + rr * math.cos(a), -0.1 * i, cz + rr * math.sin(a)))
        radii = [0.25 + 0.75 * min(1, k / 5) for k in range(len(pts))]
        radii = [r * (1 - 0.6 * max(0, k - n) / 15) for k, r in enumerate(radii)]
        tube(pts, 0.07, mat(f"wind{i}", cols[i], 0.15, alpha=0.8, emis=0.25), radii=radii, poly=False)
    cam(sc, (0.15, 0, 0.6), 2.8, height=1.0)
    return sc


def balloon():
    sc = setup()
    Rd = mat("balloon", (240, 40, 55), 0.12)
    b = sphere((0, 0, 1.25), (1, 1, 1), Rd, seg=64)
    deform(b, lambda v: Vector((v.x * (0.88 + 0.12 * v.z), v.y * (0.88 + 0.12 * v.z), v.z)))
    b.scale = (0.52, 0.5, 0.62)
    cone((0, 0, 0.6), 0.07, 0.02, 0.1, Rd)
    shine((-0.2, -0.47, 1.48), 1.3, rot=(0, R(-35), 0))
    tube([(0, 0, 0.56), (0.08, 0, 0.35), (-0.06, 0, 0.1), (0.05, 0, -0.15), (-0.02, 0, -0.4)], 0.012,
         mat("string", (250, 250, 250), 0.6))
    cam(sc, (0, 0, 0.65), 2.1, height=1.2)
    return sc


def feather():
    sc = setup()
    cols = [(150, 90, 230), (60, 150, 255), (60, 200, 160), (130, 210, 80), (255, 210, 50), (255, 140, 50), (255, 70, 90)]
    parts = []
    n = 26
    for k in range(n):
        t = k / (n - 1)
        z = 0.15 + t * 1.55
        x = 0.12 * math.sin(t * 2.6)
        w = 0.3 * math.sin(math.pi * (0.1 + 0.85 * t)) ** 0.6 + 0.03
        c = cols[min(len(cols) - 1, int(t * len(cols)))]
        for sx in (-1, 1):  # barbas inclinadas hacia la punta, a cada lado del raquis
            o = sphere((x + sx * w * 0.5, 0.0, z + w * 0.25), (w * 0.55, 0.025, 0.07), mat(f"fe{c}", c, 0.5), seg=24)
            o.rotation_euler = (0, R(-sx * 28), 0)
            parts.append(o)
    shaft = [(0.12 * math.sin((z - 0.15) / 1.55 * 2.6), -0.035, z) for z in [-0.3, 0.15, 0.6, 1.1, 1.55, 1.85]]
    parts.append(tube(shaft, 0.025, mat("shaft", (255, 250, 235), 0.4)))
    group(parts, (0, 0, 0), (0, R(-30), 0))
    cam(sc, (0.2, 0, 0.72), 2.2, height=1.0)
    return sc


def strawberry():
    sc = setup()
    Rd = mat("straw", (235, 35, 55), 0.25)
    b = sphere((0, 0, 0.55), (1, 1, 1), Rd, seg=64)
    deform(b, lambda v: Vector((v.x * (0.62 + 0.38 * (v.z + 1) / 2) ** 1.3, v.y * (0.62 + 0.38 * (v.z + 1) / 2) ** 1.3,
                                v.z * (1.15 if v.z < 0 else 1))))
    b.scale = (0.5, 0.48, 0.5)
    Sd = mat("seed", (255, 225, 90), 0.4)
    random.seed(7)
    for zi in range(6):
        z = 0.2 + zi * 0.13
        for xi in range(-3, 4):
            x = xi * 0.11 + (0.055 if zi % 2 else 0)
            # radio del cuerpo en esa altura
            vz = (z - 0.55) / 0.5
            vz2 = vz / 1.15 if vz < 0 else vz
            if abs(vz2) > 0.95:
                continue
            f = (0.62 + 0.38 * (vz2 + 1) / 2) ** 1.3
            rr = 0.5 * f * math.sqrt(max(0, 1 - vz2 ** 2))
            if abs(x) > rr * 0.85:
                continue
            y = -math.sqrt(max(rr ** 2 - x ** 2, 0)) * 0.96
            o = sphere((x, y, z), (0.022, 0.015, 0.035), Sd, seg=12)
    G = mat("stleaf", (60, 180, 70), 0.5)
    for k in range(6):
        a = k / 6 * 2 * math.pi
        o = sphere((0.2 * math.cos(a), 0.2 * math.sin(a), 1.02), (0.2, 0.07, 0.03), G)
        o.rotation_euler = (0, R(-15), a)
    cyl((0, 0, 1.12), 0.035, 0.2, mat("stem", (70, 150, 60), 0.5), rot=(R(10), 0, 0))
    shine((-0.16, -0.44, 0.82), 0.8, rot=(0, R(-30), 0))
    cam(sc, (0, 0, 0.6), 1.4, height=1.3)
    return sc


def dolphin():
    sc = setup()
    B = mat("dolph", (70, 150, 240), 0.25)
    Bl = mat("dolphb", (205, 232, 255), 0.3)

    def body(v, r=0.52, L=1.1):
        X = v.x * L
        t = (v.x + 1) / 2                     # 0 cabeza, 1 cola
        f = r * (1.0 - 0.78 * t ** 1.4) * (1.0 + 0.12 * math.sin(math.pi * t))
        return Vector((X, v.y * f, v.z * f + 0.3 * (1 - (X / L) ** 2)))
    b = sphere((0, 0, 0), (1, 1, 1), B, seg=64)
    deform(b, body)
    bl = sphere((0, 0, 0), (1, 1, 1), Bl, seg=64)
    deform(bl, lambda v: body(v, r=0.47, L=0.92) + Vector((-0.14, -0.08, -0.1)))
    b.location = bl.location = (0, 0, 0.3)
    sphere((-1.22, -0.02, 0.24), (0.24, 0.17, 0.13), B)        # hocico
    sphere((-1.2, -0.04, 0.18), (0.2, 0.14, 0.07), Bl)
    cone((0.1, 0.0, 1.08), 0.22, 0.02, 0.4, B, rot=(0, R(-35), 0))    # aleta dorsal
    o = sphere((-0.35, -0.42, 0.3), (0.24, 0.06, 0.1), B)
    o.rotation_euler = (0, R(40), R(-15))
    for s_ in (-1, 1):  # cola
        o = sphere((1.28, 0, 0.42 + s_ * 0.16), (0.08, 0.06, 0.22), B)
        o.rotation_euler = (0, R(s_ * -40), 0)
    # cara
    for (x, z, r) in [(-0.82, 0.62, 0.16), (-0.47, 0.68, 0.15)]:
        M.eye(x, -0.38, z, r, (40, 30, 40), False, B)
    torus((-1.0, -0.36, 0.33), 0.15, 0.02, mat("ink", INK, 0.6), rot=(R(90), 0, R(-15)), arc=(0, 0, -1))
    sphere((-0.72, -0.46, 0.42), (0.07, 0.02, 0.045), mat("cheek", (255, 140, 160), 0.6))
    shine((-0.2, -0.38, 0.95), 1.2, rot=(0, R(15), 0))
    for (x, z, r) in [(1.5, 0.15, 0.06), (1.62, 0.32, 0.045), (-1.55, 0.6, 0.05)]:
        sphere((x, -0.1, z), (r, r, r), mat("wdrop", (120, 200, 255), 0.05))
    cam(sc, (-0.12, 0, 0.55), 3.15, height=1.1)
    return sc


def spider():
    sc = setup()
    P = mat("spid", (130, 80, 210), 0.45)
    Pd = mat("spidl", (100, 60, 170), 0.5)
    sphere((0, 0.25, 0.65), (0.42, 0.42, 0.38), Pd)  # abdomen detrás
    body = (0, 0, 0.6)
    bs = (0.5, 0.45, 0.46)
    sphere(body, bs, P)
    for s in (-1, 1):
        for k in range(4):
            y0 = -0.25 + k * 0.2
            kx = 0.72 + 0.12 * k
            fx = 0.85 + 0.2 * k
            pts = [(s * 0.35, y0 * 0.6, 0.58), (s * kx, y0, 1.0 - 0.06 * k), (s * (fx + 0.05), y0 * 1.3, 0.45),
                   (s * fx, y0 * 1.4, 0.06)]
            tube(pts, 0.055, Pd if k % 2 else P)
            sphere((s * (fx + 0.04), y0 * 1.4 - 0.04, 0.05), (0.1, 0.12, 0.06), mat("spshoe", (255, 120, 170), 0.4))
    face(0, ell_y(body, bs, 0, 0.62, -0.08), 0.62, 0.7, P, iris=(60, 40, 90), er=0.26, gap=0.33)
    tube([(0, 0.1, 1.05), (0, 0.1, 1.8)], 0.008, mat("thread", (255, 255, 255), 0.5))
    cam(sc, (0, 0, 0.75), 2.7, height=1.3)
    return sc


def drop():
    sc = setup()
    B = mat("waterdrop", (70, 170, 255), 0.08)
    d = sphere((0, 0, 0.5), (1, 1, 1), B, seg=64)

    def f(v):
        if v.z > 0:
            k = (1 - v.z) ** 1.25
            return Vector((v.x * k, v.y * k, v.z * 1.6))
        return v
    deform(d, f)
    d.scale = (0.45, 0.42, 0.45)
    shine((-0.18, -0.38, 0.72), 1.0, rot=(0, R(-40), 0))
    sphere((-0.24, -0.33, 0.55), (0.04, 0.02, 0.07), mat("shine", (255, 255, 255), 0.0, emis=1.5))
    face(0, ell_y((0, 0, 0.5), (0.45, 0.42, 0.45), 0, 0.45, -0.05), 0.45, 0.6, B, iris=(30, 60, 120), er=0.2)
    cam(sc, (0, 0, 0.62), 1.45, height=1.2)
    return sc


def guitar():
    sc = setup()
    Rd = mat("gbody", (255, 90, 70), 0.3)
    Y = mat("gtop", (255, 210, 70), 0.35)
    parts = []
    for (z, r) in [(0.0, 0.5), (0.62, 0.38)]:
        parts.append(cyl((0, 0.02, z), r, 0.3, Rd, rot=(R(90), 0, 0)))
        parts.append(cyl((0, -0.06, z), r - 0.06, 0.18, Y, rot=(R(90), 0, 0)))
    parts.append(cyl((0, -0.155, 0.38), 0.15, 0.02, mat("hole", (60, 30, 30), 0.8), rot=(R(90), 0, 0)))
    parts.append(torus((0, -0.155, 0.38), 0.16, 0.025, mat("gring", (60, 160, 255), 0.4), rot=(R(90), 0, 0)))
    parts.append(box((0, -0.12, 1.25), (0.16, 0.1, 1.0), mat("neck", (170, 100, 60), 0.5), 0.03))
    parts.append(box((0, -0.12, 1.85), (0.28, 0.12, 0.3), mat("ghead", (60, 160, 255), 0.4), 0.06))
    for s in (-1, 1):
        for z in (1.78, 1.92):
            parts.append(sphere((s * 0.19, -0.12, z), (0.05, 0.05, 0.05), mat("peg", (255, 255, 255), 0.3)))
    parts.append(box((0, -0.17, -0.18), (0.36, 0.06, 0.08), mat("bridge", (90, 50, 40), 0.5), 0.02))
    for k in range(4):
        x = -0.045 + k * 0.03
        parts.append(cyl((x, -0.19, 0.83), 0.006, 2.0, mat("gstr", (240, 240, 240), 0.2, metal=0.6)))
    for (x, z) in [(-0.3, -0.05), (0.32, 0.05), (0.22, 0.7)]:
        parts.append(sphere((x, -0.155, z), (0.05, 0.02, 0.05), mat("gdot", (255, 255, 255), 0.4)))
    group(parts, (0, 0, 0.3), (0, R(-28), 0))
    cam(sc, (0.15, 0, 0.95), 2.6, height=1.0)
    return sc


def dice():
    sc = setup()
    W = mat("die", (255, 255, 255), 0.25)
    parts = [box((0, 0, 0), (1, 1, 1), W, 0.16)]
    cols = [(240, 50, 70), (40, 120, 255), (60, 190, 90), (255, 160, 30), (160, 80, 230), (255, 90, 170)]
    faces = {  # normal: lista de posiciones (u, v)
        (0, -1, 0): [(-0.25, 0.25), (0, 0), (0.25, -0.25)],                  # 3
        (0, 0, 1): [(-0.25, -0.25), (0.25, 0.25), (-0.25, 0.25), (0.25, -0.25), (0, 0)],  # 5
        (1, 0, 0): [(-0.25, -0.25), (0.25, 0.25)],                            # 2
        (-1, 0, 0): [(-0.25, -0.25), (0.25, 0.25), (-0.25, 0.25), (0.25, -0.25)],
        (0, 1, 0): [(-0.25, 0.25), (-0.25, 0), (-0.25, -0.25), (0.25, 0.25), (0.25, 0), (0.25, -0.25)],
        (0, 0, -1): [(0, 0)],
    }
    for i, (n, ds) in enumerate(faces.items()):
        m = mat(f"dot{i}", cols[i], 0.35)
        for (u, v) in ds:
            if n[1]:
                loc, sc_ = (u, n[1] * 0.49, v), (0.09, 0.025, 0.09)
            elif n[2]:
                loc, sc_ = (u, v, n[2] * 0.49), (0.09, 0.09, 0.025)
            else:
                loc, sc_ = (n[0] * 0.49, u, v), (0.025, 0.09, 0.09)
            parts.append(sphere(loc, sc_, m, seg=24))
    group(parts, (0, 0, 0.6), (R(-8), R(8), R(-28)))
    cam(sc, (0, 0, 0.62), 1.95, height=2.6)
    return sc


def house():
    sc = setup()
    Wl = mat("hwall", (255, 230, 170), 0.6)
    Rf = mat("hroof", (235, 60, 60), 0.4)
    box((0, 0, 0.5), (1.3, 1.0, 1.0), Wl, 0.08)
    roof = rounded([(-0.88, 0), (0.88, 0), (0, 0.72)], 0.08)
    shape(roof, Rf, depth=0.58, bevel=0.05, loc=(0, 0, 0.98))
    box((0.4, 0.15, 1.45), (0.2, 0.2, 0.4), mat("chim", (200, 110, 80), 0.6), 0.04)
    box((0.18, -0.5, 0.33), (0.36, 0.06, 0.62), mat("door", (120, 190, 255), 0.4), 0.1)
    sphere((0.3, -0.54, 0.33), (0.04, 0.03, 0.04), mat("knob", (255, 200, 40), 0.3, metal=0.5))
    box((-0.33, -0.5, 0.6), (0.34, 0.06, 0.34), mat("hwin", (255, 240, 150), 0.2, emis=0.6), 0.06)
    for (sz, ax) in [((0.05, 0.08, 0.38), 0), ((0.38, 0.08, 0.05), 0)]:
        box((-0.33, -0.52, 0.6), sz, mat("hframe", (255, 255, 255), 0.4), 0.02)
    cyl((0, -0.5, 1.22), 0.12, 0.08, mat("hwin2", (255, 240, 150), 0.2, emis=0.6), rot=(R(90), 0, 0))
    torus((0, -0.54, 1.22), 0.12, 0.03, mat("hframe", (255, 255, 255), 0.4), rot=(R(90), 0, 0))
    for x in (-0.5, -0.2):
        sphere((x, -0.6, 0.08), (0.14, 0.12, 0.12), mat("bush", (80, 190, 80), 0.6))
    sphere((-0.5, -0.7, 0.17), (0.04, 0.02, 0.04), mat("flower", (255, 120, 180), 0.4))
    cam(sc, (0, 0, 0.82), 2.3, height=1.4)
    return sc


def ruler():
    sc = setup()
    parts = [box((0, 0, 0), (2.4, 0.1, 0.5), mat("ruler", (255, 210, 40), 0.35), 0.05)]
    K = mat("rmark", (70, 50, 40), 0.5)
    for k in range(23):
        x = -1.1 + k * 0.1
        L = 0.2 if k % 5 == 0 else 0.11
        parts.append(box((x, -0.055, 0.25 - L / 2 - 0.03), (0.022, 0.02, L), K, 0.008))
    for k, c in enumerate([(240, 60, 70), (60, 140, 255), (60, 190, 90), (160, 80, 230), (255, 140, 40)]):
        parts.append(sphere((-1.1 + k * 0.5, -0.055, -0.1), (0.05, 0.015, 0.05), mat(f"rdot{k}", c, 0.4), seg=16))
    group(parts, (0, 0, 0.5), (0, R(18), 0))
    cam(sc, (0, 0, 0.5), 2.6, height=0.9)
    return sc


def sun():
    sc = setup()
    Y = mat("sunb", (255, 200, 30), 0.35, emis=0.25)
    Or = mat("sunray", (255, 140, 30), 0.35, emis=0.25)
    sphere((0, 0, 0.9), (0.55, 0.42, 0.55), Y)
    for k in range(10):
        a = k / 10 * 2 * math.pi
        cone((0.78 * math.cos(a), 0.05, 0.9 + 0.78 * math.sin(a)), 0.14, 0.03, 0.32, Or if k % 2 else Y,
             rot=(0, -a + math.pi / 2, 0))
    face(0, ell_y((0, 0, 0.9), (0.55, 0.42, 0.55), 0, 0.9, -0.06), 0.9, 0.85, Y, iris=(120, 60, 20), er=0.18)
    cam(sc, (0, 0, 0.9), 2.2, height=1.0)
    return sc


def brain():
    sc = setup()
    Pk = mat("brain", (255, 150, 180), 0.45)
    Pd = mat("brainf", (235, 110, 150), 0.45)
    C, S = (0, 0, 0.7), (0.75, 0.55, 0.55)
    sphere(C, S, Pk, seg=64)
    for s_ in (-1, 1):  # dos lóbulos que sobresalen un poco arriba
        sphere((s_ * 0.33, 0.02, 0.8), (0.42, 0.52, 0.46), Pk)
    # pliegues: tubos ondulados sobre la superficie
    def on_surf(x, z, off=0.0):
        best = None
        for (c, sc_) in [(C, S), ((-0.33, 0.02, 0.8), (0.42, 0.52, 0.46)), ((0.33, 0.02, 0.8), (0.42, 0.52, 0.46))]:
            t = 1 - ((x - c[0]) / sc_[0]) ** 2 - ((z - c[2]) / sc_[2]) ** 2
            if t > 0:
                y = c[1] - sc_[1] * math.sqrt(t)
                best = y if best is None else min(best, y)
        return best
    for row, z in enumerate([0.98, 1.12, 0.84]):
        for s_ in (-1, 1):
            pts = []
            for k in range(30):
                t = k / 29
                x = s_ * (0.07 + t * 0.66)
                zz = z + 0.06 * math.sin(t * 17 + row * 1.7 + (s_ + 1))
                y = on_surf(x, zz)
                if y is None or (row == 2 and abs(x) < 0.5):
                    continue
                pts.append((x, y + 0.015, zz))
            if len(pts) > 3:
                tube(pts, 0.03, Pd, res=6)
    tube([(0, on_surf(0, z) + 0.02, z) for z in (1.2, 1.1, 0.98, 0.9)], 0.03, Pd)   # surco central
    face(0, ell_y(C, S, 0, 0.55, -0.02), 0.55, 0.6, Pk, iris=(70, 40, 60), er=0.22, gap=0.4)
    cam(sc, (0, 0, 0.75), 1.85, height=1.2)
    return sc


def car():
    sc = setup()
    Rd = mat("car", (235, 45, 50), 0.2)
    box((0, 0, 0.42), (1.8, 0.9, 0.45), Rd, 0.18)
    box((-0.1, 0, 0.78), (1.0, 0.8, 0.5), Rd, 0.2)
    Gl = mat("carwin", (170, 225, 255), 0.05)
    box((-0.37, -0.39, 0.8), (0.38, 0.04, 0.3), Gl, 0.06)
    box((0.15, -0.39, 0.8), (0.38, 0.04, 0.3), Gl, 0.06)
    for x in (-0.55, 0.55):
        cyl((x, -0.42, 0.24), 0.24, 0.2, mat("tire", (45, 45, 55), 0.7), rot=(R(90), 0, 0))
        cyl((x, -0.53, 0.24), 0.12, 0.04, mat("hub", (230, 230, 240), 0.25, metal=0.5), rot=(R(90), 0, 0))
        sphere((x, -0.555, 0.24), (0.04, 0.02, 0.04), mat("hubc", (255, 200, 40), 0.3))
    sphere((0.9, -0.28, 0.5), (0.05, 0.08, 0.07), mat("hlight", (255, 240, 150), 0.1, emis=2.0))
    sphere((-0.9, -0.28, 0.5), (0.04, 0.07, 0.06), mat("tlight", (255, 140, 40), 0.2, emis=1.0))
    box((0.0, -0.46, 0.4), (0.04, 0.02, 0.3), mat("door", (200, 35, 40), 0.3), 0.01)
    sphere((0.1, -0.46, 0.5), (0.05, 0.02, 0.02), mat("handle", (255, 255, 255), 0.3))
    cam(sc, (0, 0, 0.55), 2.2, height=1.4)
    return sc


LEAF = [(0, 0), (0.28, 0.25), (0.36, 0.62), (0.22, 1.0), (0, 1.25), (-0.22, 1.0), (-0.36, 0.62), (-0.28, 0.25)]


def one_leaf(col, loc, rot, s=1.0, name="leaf"):
    G = mat(name, col, 0.45)
    Gv = mat(name + "v", tuple(min(255, int(c * 1.25 + 25)) for c in col), 0.45)
    parts = [shape([(x * s, y * s) for x, y in LEAF], G, depth=0.015 * s, bevel=0.025 * s, smooth=True)]
    parts.append(tube([(0, -0.04 * s, -0.2 * s), (0, -0.045 * s, 0.4 * s), (0, -0.04 * s, 1.1 * s)], 0.018 * s, Gv))
    for k in range(3):
        z = (0.3 + k * 0.25) * s
        for sx in (-1, 1):
            parts.append(tube([(0, -0.045 * s, z), (sx * 0.12 * s, -0.045 * s, z + 0.1 * s),
                               (sx * 0.22 * s, -0.04 * s, z + 0.22 * s)], 0.011 * s, Gv))
    return group(parts, loc, rot)


def leaf():
    sc = setup()
    one_leaf((70, 185, 70), (0, 0, 0.0), (0, R(-30), 0), 1.2)
    cam(sc, (-0.33, 0, 0.62), 2.0, height=1.0)
    return sc


def leaves():
    sc = setup()
    cols = [(60, 170, 70), (120, 205, 70), (40, 150, 90), (170, 210, 60), (80, 190, 110)]
    for k, a in enumerate((-55, -25, 0, 25, 55)):
        one_leaf(cols[k], (0, -0.02 * abs(k - 2), 0.1), (0, R(a), 0), 0.95 if k != 2 else 1.1, name=f"lv{k}")
    tube([(0, -0.05, -0.3), (0.03, -0.05, 0.0), (0, -0.05, 0.15)], 0.03, mat("lstem", (120, 90, 50), 0.6))
    cam(sc, (0, 0, 0.6), 2.4, height=1.0)
    return sc


def tongue():
    sc = setup()
    Lp = mat("lip", (255, 120, 140), 0.35)
    In = mat("mouthin", (110, 20, 40), 0.7)
    sphere((0, 0, 0.8), (0.75, 0.2, 0.45), In)
    lip = torus((0, -0.12, 0.8), 1.0, 0.09, Lp, rot=(R(90), 0, 0))
    lip.scale = (0.78, 0.47, 1)
    # dientes de arriba
    for x in (-0.13, 0.13):
        box((x, -0.18, 1.08), (0.24, 0.06, 0.18), mat("teeth", (255, 255, 255), 0.25), 0.06)
    # lengua afuera
    T = mat("tongue", (255, 95, 130), 0.35)
    t = sphere((0, -0.3, 0.45), (0.36, 0.12, 0.42), T)
    tube([(0, -0.415, 0.62), (0, -0.425, 0.45), (0, -0.405, 0.3)], 0.014, mat("tline", (220, 60, 100), 0.4))
    shine((-0.15, -0.43, 0.38), 0.7, rot=(0, R(-60), 0))
    for sx in (-1, 1):
        sphere((sx * 0.98, -0.05, 0.85), (0.14, 0.04, 0.09), mat("cheek", (255, 140, 160), 0.6))
    cam(sc, (0, 0, 0.7), 2.3, height=1.1)
    return sc


def shrimp():
    sc = setup()
    Or = mat("shrimp", (255, 130, 100), 0.35)
    Ol = mat("shrimpl", (255, 180, 150), 0.35)
    n = 9
    for k in range(n):  # cuerpo curvado en C
        t = k / (n - 1)
        a = R(170 - t * 250)
        x, z = 0.5 * math.cos(a), 0.6 + 0.45 * math.sin(a)
        r = 0.27 - 0.17 * t
        o = sphere((x, 0, z), (r, r * 0.9, r * 1.05), Or if k % 2 == 0 else Ol, seg=32)
    # cola en abanico
    ax, az = 0.5 * math.cos(R(-80)), 0.6 + 0.45 * math.sin(R(-80))
    for s in (-1, 0, 1):
        o = sphere((ax - 0.14 + s * 0.12, -0.02, az - 0.07 - abs(s) * 0.02), (0.07, 0.04, 0.16), Or)
        o.rotation_euler = (0, R(70 + s * 25), 0)
    # cabeza
    hx, hz = -0.52, 0.66
    sphere((hx - 0.08, 0, hz + 0.02), (0.3, 0.26, 0.28), Or)
    M.eye(hx - 0.2, -0.22, hz + 0.12, 0.11, (40, 30, 40), False, Or)
    M.eye(hx + 0.04, -0.22, hz + 0.14, 0.1, (40, 30, 40), False, Or)
    torus((hx - 0.1, -0.24, hz - 0.08), 0.07, 0.015, mat("ink", INK, 0.6), rot=(R(90), 0, 0), arc=(0, 0, -1))
    sphere((hx - 0.3, -0.18, hz - 0.04), (0.05, 0.02, 0.035), mat("cheek", (255, 90, 120), 0.6))
    for s in (0, 1):  # antenas
        tube([(hx - 0.2, -0.05, hz + 0.25), (hx - 0.4 - s * 0.1, -0.05, hz + 0.6), (hx - 0.1 + s * 0.1, -0.05, hz + 0.95)],
             0.012, Or)
    cam(sc, (-0.05, 0, 0.62), 1.9, height=1.1)
    return sc


def eagle():
    sc = setup()
    Br = mat("eagleb", (150, 95, 55), 0.55)
    Bd = mat("eagled", (115, 70, 40), 0.55)
    W = mat("eaglew", (255, 255, 250), 0.55)
    Yb = mat("beakE", (255, 190, 40), 0.35)
    sphere((0, 0, 0.6), (0.42, 0.38, 0.5), Br)
    sphere((0, -0.2, 0.5), (0.26, 0.2, 0.32), mat("eaglebel", (220, 180, 130), 0.6))
    head = (0, -0.05, 1.18)
    hs = (0.38, 0.36, 0.34)
    sphere(head, hs, W)
    for s in (-1, 1):  # alas abiertas
        o = sphere((s * 0.62, 0.08, 0.95), (0.42, 0.07, 0.22), Br)
        o.rotation_euler = (0, R(-s * 30), 0)
        for k in range(4):  # plumas de la punta del ala
            ang = R(-s * (30 + k * 14))
            L = 0.3 - k * 0.03
            o = sphere((s * (0.62 + 0.36 * math.cos(R(30 + k * 14))), 0.1, 0.95 + 0.36 * math.sin(R(30 + k * 14)) - 0.1),
                       (L, 0.05, 0.075), Bd)
            o.rotation_euler = (0, ang, 0)
    for s in (-1, 0, 1):  # cola
        o = sphere((s * 0.1, 0.1, 0.12), (0.08, 0.05, 0.18), Bd)
        o.rotation_euler = (0, R(s * 20), 0)
    for s in (-1, 1):
        sphere((s * 0.16, -0.2, 0.08), (0.1, 0.12, 0.05), Yb)
        M.eye(s * 0.15, ell_y(head, hs, s * 0.15, 1.25, -0.06), 1.25, 0.11, (110, 70, 30), False, W)
        o = sphere((s * 0.17, ell_y(head, hs, s * 0.17, 1.38, -0.04), 1.38), (0.12, 0.04, 0.035), mat("brow", (120, 80, 50), 0.5))
        o.rotation_euler = (0, R(s * 12), 0)
    sphere((0, -0.38, 1.08), (0.1, 0.12, 0.08), Yb)
    cone((0, -0.43, 0.98), 0.06, 0.0, 0.12, Yb, rot=(R(160), 0, 0))
    for s in (-1, 1):
        sphere((s * 0.26, ell_y(head, hs, s * 0.26, 1.08, -0.02), 1.08), (0.06, 0.02, 0.04), mat("cheek", (255, 140, 160), 0.6))
    cam(sc, (0, 0, 0.75), 2.6, height=1.3)
    return sc


def tree():
    sc = setup()
    Tr = mat("trunk", (150, 95, 55), 0.7)
    cone((0, 0, 0.5), 0.2, 0.13, 1.0, Tr)
    for s in (-1, 1):
        o = sphere((s * 0.17, 0, 0.06), (0.15, 0.1, 0.06), Tr)
    G = [mat("tg1", (70, 185, 75), 0.6), mat("tg2", (100, 205, 80), 0.6), mat("tg3", (50, 160, 70), 0.6)]
    random.seed(11)
    for k, (x, z, r) in enumerate([(0, 1.45, 0.55), (-0.45, 1.2, 0.4), (0.45, 1.2, 0.42), (-0.25, 1.75, 0.38),
                                   (0.28, 1.72, 0.38), (0, 1.15, 0.45), (-0.55, 1.5, 0.3), (0.56, 1.5, 0.3)]):
        sphere((x, 0.05 * (k % 3), z), (r, r * 0.9, r * 0.95), G[k % 3])
    for (x, z) in [(-0.3, 1.25), (0.32, 1.55), (0.05, 1.2), (-0.1, 1.7)]:
        sphere((x, -0.52 + abs(x) * 0.3, z), (0.04, 0.02, 0.04), mat("tdot", (150, 225, 110), 0.5))
    cam(sc, (0, 0, 1.0), 2.4, height=1.2)
    return sc


def bone():
    sc = setup()
    C = mat("bone", (255, 245, 220), 0.45)
    parts = [cyl((0, 0, 0), 0.14, 1.2, C, rot=(0, R(90), 0))]
    for sx in (-1, 1):
        for sz in (-1, 1):
            parts.append(sphere((sx * 0.62, 0, sz * 0.14), (0.2, 0.18, 0.2), C))
    group(parts, (0, 0, 0.5), (0, R(-20), 0))
    cam(sc, (0, 0, 0.5), 1.9, height=1.2)
    return sc


def clock():
    sc = setup()
    Rd = mat("clock", (240, 60, 70), 0.3)
    cyl((0, 0, 0.85), 0.6, 0.35, Rd, rot=(R(90), 0, 0))
    torus((0, -0.18, 0.85), 0.55, 0.06, Rd, rot=(R(90), 0, 0))
    cyl((0, -0.17, 0.85), 0.52, 0.02, mat("dial", (255, 252, 240), 0.4), rot=(R(90), 0, 0))
    for k in range(12):
        a = k / 12 * 2 * math.pi
        r = 0.04 if k % 3 == 0 else 0.022
        sphere((0.42 * math.sin(a), -0.19, 0.85 + 0.42 * math.cos(a)), (r, 0.015, r), mat("tick", (60, 60, 80), 0.4), seg=16)
    K = mat("hand", (40, 40, 60), 0.4)
    box((0.0, -0.2, 0.85 + 0.13), (0.06, 0.02, 0.28), K, 0.025)
    a = R(120)
    box((0.15 * math.sin(a), -0.2, 0.85 + 0.15 * math.cos(a)), (0.05, 0.02, 0.36), K, 0.02, rot=(0, a, 0))
    sphere((0, -0.21, 0.85), (0.05, 0.02, 0.05), mat("hubc", (255, 200, 40), 0.3))
    Gd = mat("bell", (255, 200, 40), 0.25, metal=0.6)
    for s in (-1, 1):
        b = sphere((s * 0.36, 0, 1.43), (0.22, 0.22, 0.2), Gd)
        b.rotation_euler = (0, R(s * 35), 0)
        cyl((s * 0.4, 0, 0.22), 0.05, 0.3, Rd, rot=(0, R(-s * 35), 0))
        sphere((s * 0.48, 0, 0.1), (0.07, 0.07, 0.05), Rd)
    cyl((0, 0, 1.5), 0.025, 0.25, mat("hammer", (120, 120, 140), 0.3, metal=0.5))
    sphere((0, 0, 1.63), (0.06, 0.06, 0.06), Gd)
    shine((-0.38, -0.25, 1.15), 0.8, rot=(0, R(-45), 0))
    cam(sc, (0, 0, 0.88), 2.0, height=1.1)
    return sc


def star():
    sc = setup()
    G = mat("star", (255, 200, 30), 0.25, metal=0.25, emis=0.15)
    shape(rounded(star_pts(5, 0.75, 0.33), 0.1), G, depth=0.08, bevel=0.1, loc=(0, 0, 0.75))
    shine((-0.18, -0.2, 0.95), 0.9, rot=(0, R(-40), 0))
    cam(sc, (0, 0, 0.72), 1.85, height=1.0)
    return sc


def lightning():
    sc = setup()
    Y = mat("bolt", (255, 215, 30), 0.25, emis=0.35)
    pts = [(0.15, 1.0), (-0.42, 0.0), (-0.02, 0.06), (-0.22, -0.85), (0.45, 0.25), (0.05, 0.2), (0.38, 1.0)]
    shape(rounded(pts, 0.04), Y, depth=0.06, bevel=0.05, loc=(0, 0, 0.8))
    for (x, z) in [(0.62, 1.55), (-0.55, 0.4)]:
        sparkle((x, -0.1, z), 0.12)
    cam(sc, (0, 0, 0.82), 2.15, height=1.0)
    return sc


def splash():
    sc = setup()
    B = mat("splash", (60, 165, 255), 0.06)
    Bl = mat("splashl", (130, 205, 255), 0.06)

    def droplet(loc, r, direction):
        d = sphere((0, 0, 0), (1, 1, 1), B, seg=32)
        deform(d, lambda v: Vector((v.x * (1 - v.z) ** 1.2, v.y * (1 - v.z) ** 1.2, v.z * 1.8)) if v.z > 0 else v)
        d.scale = (r, r, r)
        d.location = loc
        d.rotation_mode = "QUATERNION"
        d.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(direction).normalized())
        shine((loc[0] - r * 0.3, loc[1] - r * 0.95, loc[2] + r * 0.15), r * 4)
    sphere((0, 0.1, 0.06), (1.05, 0.6, 0.1), Bl)                 # charco
    sphere((0, 0.1, 0.12), (0.55, 0.36, 0.14), B)                # base de la corona
    for k in range(8):                                               # puntas de la corona
        a = k / 8 * 2 * math.pi + 0.2
        x, y = 0.45 * math.cos(a), 0.1 + 0.3 * math.sin(a)
        h = 0.55 if math.sin(a) > 0 else 0.42
        o = cyl((0, 0, 0), 0.17, h, B)
        deform(o, lambda v, h=h: Vector((v.x * (1 - 0.5 * (v.z / h + 0.5)), v.y * (1 - 0.5 * (v.z / h + 0.5)), v.z)))
        o.location = (x * 1.1, y, 0.12 + h / 2)
        o.rotation_euler = (R(-22 * math.sin(a)), R(22 * math.cos(a)), 0)
        sphere((x * 1.1 + 0.22 * h * math.cos(a), y + 0.2 * h * math.sin(a), 0.12 + h + 0.05), (0.11, 0.11, 0.11), B)
    for (x, z, r) in [(-0.85, 1.0, 0.13), (-0.35, 1.3, 0.15), (0.3, 1.35, 0.14), (0.85, 1.05, 0.13), (0.0, 1.0, 0.1),
                      (-1.1, 0.55, 0.09), (1.1, 0.6, 0.09)]:
        droplet((x, -0.15, z), r, (-x, 0, -(z - 0.2)))   # la colita apunta al centro
    cam(sc, (0, 0, 0.7), 2.45, height=1.3)
    return sc


def tooth():
    sc = setup()
    W = mat("tooth", (255, 255, 255), 0.2)
    sphere((0, 0, 0.85), (0.5, 0.42, 0.45), W)
    for s in (-1, 1):
        sphere((s * 0.22, 0, 1.18), (0.24, 0.3, 0.2), W)
        o = cone((s * 0.24, 0, 0.35), 0.2, 0.08, 0.6, W, rot=(0, R(s * 12), 0))
        sphere((s * 0.28, 0, 0.08), (0.09, 0.09, 0.07), W)
    face(0, ell_y((0, 0, 0.85), (0.5, 0.42, 0.45), 0, 0.82, -0.05), 0.82, 0.75, W, iris=(60, 130, 230), er=0.2)
    sparkle((0.55, -0.4, 1.35), 0.22, col=(200, 240, 255))
    sparkle((-0.6, -0.4, 0.55), 0.13, col=(200, 240, 255))
    cam(sc, (0, 0, 0.75), 1.9, height=1.1)
    return sc


def toothbrush():
    sc = setup()
    parts = []
    H = mat("tbh", (60, 160, 255), 0.25)
    parts.append(box((-0.2, 0, 0), (1.6, 0.26, 0.24), H, 0.11))
    parts.append(box((-0.45, -0.02, 0), (0.7, 0.26, 0.27), mat("tbgrip", (130, 220, 120), 0.6), 0.11))
    parts.append(box((0.75, 0, 0.04), (0.6, 0.28, 0.16), H, 0.07))
    for i in range(6):
        for j in range(3):
            c = (255, 255, 255) if (i + j) % 2 == 0 else (120, 200, 255)
            parts.append(cyl((0.52 + i * 0.09, -0.09 + j * 0.09, 0.24), 0.04, 0.28, mat(f"brist{c}", c, 0.5)))
    path = [(0.45, -0.0, 0.42), (0.6, -0.04, 0.5), (0.78, 0.03, 0.45), (0.95, -0.04, 0.5), (1.02, 0.0, 0.58)]
    radii = [0.8, 1, 1, 1, 0.5]
    parts.append(tube(path, 0.09, mat("paste", (255, 255, 255), 0.3), radii=radii))
    parts.append(tube([(x, y - 0.07, z + 0.03) for x, y, z in path], 0.03, mat("paster", (240, 60, 80), 0.3), radii=radii))
    parts.append(tube([(x, y - 0.02, z + 0.08) for x, y, z in path], 0.03, mat("pastea", (60, 200, 200), 0.3), radii=radii))
    group(parts, (0, 0, 0.6), (0, R(-30), 0))
    cam(sc, (0.15, 0, 0.75), 2.2, height=1.3)
    return sc


def microphone():
    sc = setup()
    parts = []
    Pk = mat("micb", (255, 90, 160), 0.3)
    h = cyl((0, 0, 0.5), 0.15, 0.9, Pk)
    deform(h, lambda v: Vector((v.x * (0.62 + 0.38 * (v.z + 0.45) / 0.9), v.y * (0.62 + 0.38 * (v.z + 0.45) / 0.9), v.z)))
    parts.append(h)
    parts.append(sphere((0, 0, 0.05), (0.095, 0.095, 0.04), Pk))
    parts.append(cyl((0, 0, 0.98), 0.21, 0.14, mat("micr", (255, 210, 40), 0.3, metal=0.4)))
    parts.append(sphere((0, 0, 1.24), (0.3, 0.3, 0.3), mat("micg", (205, 210, 225), 0.3, metal=0.7)))
    K = mat("micd", (140, 145, 170), 0.4, metal=0.5)
    for i in range(6):
        for j in range(14):
            th = R(25 + i * 22)
            ph = j / 14 * 2 * math.pi + i * 0.2
            v = Vector((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)))
            if v.y > 0.3:
                continue
            parts.append(sphere((0.3 * v.x, 0.3 * v.y, 1.24 + 0.3 * v.z), (0.022, 0.022, 0.022), K, seg=12))
    parts.append(sphere((0, -0.13, 0.65), (0.05, 0.03, 0.05), mat("micbtn", (255, 255, 255), 0.3)))
    parts.append(shine((-0.12, -0.28, 1.38), 0.8, rot=(0, R(-40), 0)))
    group(parts, (0, 0, 0), (0, R(-20), 0))
    cam(sc, (0.2, 0, 0.78), 1.75, height=1.1)
    return sc


def hands_up():
    sc = setup()
    W = mat("glove", (255, 255, 255), 0.5)
    Cf = mat("cuff", (255, 200, 40), 0.4)
    Y = mat("burst", (255, 200, 40), 0.3, emis=0.8)
    for s in (-1, 1):
        parts = [sphere((0, 0, 0), (0.28, 0.13, 0.27), W)]
        for k, (a, L) in enumerate([(-24, 0.3), (-8, 0.36), (8, 0.35), (24, 0.29)]):
            ar = R(a)
            bx, bz = 0.2 * math.sin(ar), 0.18
            ex, ez = bx + L * math.sin(ar), bz + L * math.cos(ar)
            parts.append(tube([(bx, 0, bz), (ex, 0, ez)], 0.075, W, poly=True))
            parts.append(sphere((ex, 0, ez), (0.075, 0.075, 0.075), W))
        parts.append(tube([(0.2, 0, -0.02), (0.36, 0, 0.12), (0.42, 0, 0.26)], 0.075, W))
        parts.append(sphere((0.42, 0, 0.26), (0.075, 0.075, 0.075), W))
        parts.append(cyl((0, 0, -0.32), 0.2, 0.18, Cf))
        parts.append(torus((0, 0, -0.24), 0.2, 0.05, Cf))
        for k in range(2):  # pliegues del guante
            parts.append(tube([(-0.12 + k * 0.1, -0.135, 0.02), (-0.1 + k * 0.1, -0.135, 0.14)], 0.01,
                              mat("ink", INK, 0.6), poly=True))
        group(parts, (s * 0.5, 0, 0.72), (0, R(s * 15), 0)).scale = (-s, 1, 1)
        for (a, L) in [(-50, 0.2), (-15, 0.24), (20, 0.2)]:  # rayitas de festejo
            ar = R(a * s + s * 15)
            cx, cz = s * 0.5 + 0.85 * math.sin(ar), 0.72 + 0.85 * math.cos(ar)
            box((cx, 0, cz), (0.07, 0.06, L), Y, 0.03, rot=(0, ar, 0))
    cam(sc, (0, 0, 0.95), 2.6, height=1.0)
    return sc


def egg():
    sc = setup()
    C = mat("egg", (255, 245, 215), 0.35)
    e = sphere((0, 0, 0.62), (1, 1, 1), C, seg=64)
    deform(e, lambda v: Vector((v.x * (1 - 0.18 * v.z), v.y * (1 - 0.18 * v.z), v.z)))
    e.scale = (0.48, 0.46, 0.62)
    B = mat("eggdot", (60, 140, 255), 0.4)
    for (x, z, r) in [(-0.18, 0.85, 0.09), (0.15, 0.55, 0.12), (-0.25, 0.38, 0.07), (0.05, 1.05, 0.06), (0.3, 0.88, 0.07),
                      (-0.02, 0.3, 0.06), (-0.33, 0.65, 0.05)]:
        k = 1 - 0.18 * (z - 0.62) / 0.62
        a = 0.48 * k
        t = 1 - (x / a) ** 2 - ((z - 0.62) / 0.62) ** 2
        if t <= 0:
            continue
        y = -0.46 * k * math.sqrt(t)
        o = sphere((x, y - 0.004, z), (r, 0.03, r * 1.1), B, seg=24)
        n = Vector((x / a ** 2, y / (0.46 * k) ** 2, (z - 0.62) / 0.62 ** 2)).normalized()
        o.rotation_euler = Vector((0, -1, 0)).rotation_difference(n).to_euler()
    shine((-0.2, -0.38, 0.85), 1.0, rot=(0, R(-30), 0))
    cam(sc, (0, 0, 0.62), 1.5, height=1.1)
    return sc


def lightbulb():
    sc = setup()
    Gl = mat("bulb", (255, 230, 90), 0.1, emis=2.2)
    b = sphere((0, 0, 1.05), (1, 1, 1), Gl, seg=64)
    deform(b, lambda v: Vector((v.x * (1 - 0.45 * max(0, -v.z) ** 1.5), v.y * (1 - 0.45 * max(0, -v.z) ** 1.5), v.z * (1.25 if v.z < 0 else 1))))
    b.scale = (0.48, 0.48, 0.48)
    Gr = mat("bbase", (190, 195, 210), 0.3, metal=0.6)
    cyl((0, 0, 0.42), 0.2, 0.3, Gr)
    for z in (0.33, 0.42, 0.51):
        torus((0, 0, z), 0.2, 0.025, Gr)
    sphere((0, 0, 0.24), (0.1, 0.1, 0.08), mat("btip", (80, 80, 95), 0.4))
    sphere((-0.18, -0.38, 1.22), (0.08, 0.03, 0.12), mat("shine", (255, 255, 255), 0.0, emis=1.5))
    Y = mat("brays", (255, 220, 60), 0.3, emis=1.2)
    for a in (-75, -38, 0, 38, 75):
        ar = R(a)
        o = box((0.82 * math.sin(ar), 0, 1.08 + 0.82 * math.cos(ar)), (0.07, 0.06, 0.24), Y, 0.03)
        o.rotation_euler = (0, ar, 0)
    cam(sc, (0, 0, 0.95), 2.1, height=1.0)
    return sc


def moon():
    sc = setup()
    Y = mat("moon", (255, 230, 120), 0.45, emis=0.2)
    pts = []
    n = 40
    for k in range(n + 1):  # borde externo (círculo grande)
        a = R(60 + k / n * 240)
        pts.append((0.75 * math.cos(a), 0.75 * math.sin(a)))
    cx = 0.45
    ex, ey = pts[0]
    rin = math.hypot(ex - cx, ey)
    a0 = math.atan2(pts[-1][1], pts[-1][0] - cx) % (2 * math.pi)   # abajo (~263°)
    a1 = math.atan2(pts[0][1], pts[0][0] - cx) % (2 * math.pi)     # arriba (~97°)
    for k in range(1, n):  # borde interno, de abajo hacia arriba pasando por la izquierda
        a = a0 + (a1 - a0) * k / n
        pts.append((cx + rin * math.cos(a), rin * math.sin(a)))
    shape(pts, Y, depth=0.1, bevel=0.1, loc=(0, 0, 0.8))
    # cara dormida en la panza de la luna
    for (x, z) in [(-0.38, 0.98)]:
        o = torus((x, -0.22, z), 0.07, 0.016, mat("ink", INK, 0.6), rot=(R(90), 0, 0), arc=(0, 0, -1))
    torus((-0.3, -0.22, 0.75), 0.07, 0.016, mat("ink", INK, 0.6), rot=(R(90), 0, 0), arc=(0, 0, -1))
    sphere((-0.5, -0.21, 0.82), (0.06, 0.02, 0.04), mat("cheek", (255, 150, 150), 0.6))
    for (x, z, s) in [(0.6, 1.2, 0.16), (0.78, 0.55, 0.1)]:
        shape(rounded(star_pts(5, s, s * 0.42), s * 0.06), mat("mstar", (255, 240, 160), 0.3, emis=1.5), depth=0.01,
              bevel=0.02, loc=(x, 0, z))
    cam(sc, (0.05, 0, 0.95), 2.0, height=1.0)
    return sc


def heart():
    sc = setup()
    Rd = mat("heart", (240, 40, 70), 0.15)
    pts = []
    for k in range(72):
        t = k / 72 * 2 * math.pi
        if t < 0.3 or t > 2 * math.pi - 0.3:      # sin la punta del medio de arriba: un hoyito suave
            continue
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x / 22, y / 22))
    pts.append((0, 3.2 / 22))
    shape(pts[::2] + [pts[-1]], Rd, depth=0.08, bevel=0.16, loc=(0, 0, 0.75), smooth=True)
    shine((-0.4, -0.25, 1.0), 1.2, rot=(0, R(-40), 0))
    cam(sc, (0, 0, 0.72), 1.95, height=1.0)
    return sc


def carrot():
    sc = setup()
    Or = mat("carrot", (255, 130, 30), 0.45)
    Ol = mat("carrotl", (220, 95, 20), 0.5)
    parts = []
    c = cyl((0, 0, 0.7), 0.27, 1.3, Or)
    deform(c, lambda v: Vector((v.x * (0.08 + 0.92 * ((v.z + 0.65) / 1.3) ** 0.8),
                                v.y * (0.08 + 0.92 * ((v.z + 0.65) / 1.3) ** 0.8), v.z)))
    parts.append(c)
    parts.append(sphere((0, 0, 0.06), (0.025, 0.025, 0.03), Or))
    parts.append(sphere((0, 0, 1.35), (0.27, 0.27, 0.1), Or))
    for (z, x) in [(0.45, -0.03), (0.68, 0.04), (0.9, -0.05), (1.12, 0.05)]:
        r = 0.27 * (0.08 + 0.92 * ((z - 0.05) / 1.3) ** 0.8)
        o = sphere((x, -r * 0.92, z), (r * 0.45, 0.02, 0.016), Ol)
        parts.append(o)
    G = [mat("ctop", (80, 190, 70), 0.5), mat("ctop2", (120, 210, 80), 0.5)]
    for k, a in enumerate((-40, -15, 10, 35)):
        o = sphere((math.sin(R(a)) * 0.25, 0, 1.4 + math.cos(R(a)) * 0.25), (0.08, 0.05, 0.3), G[k % 2])
        o.rotation_euler = (0, R(a), 0)
        parts.append(o)
    group(parts, (0, 0, 0), (0, R(-25), 0))
    cam(sc, (-0.25, 0, 0.9), 2.05, height=1.0)
    return sc


def apple():
    sc = setup()
    Rd = mat("apple", (235, 40, 50), 0.2)
    a = sphere((0, 0, 0.55), (1, 1, 1), Rd, seg=64)

    def f(v):
        r = math.sqrt(v.x ** 2 + v.y ** 2)
        z = v.z
        z -= 0.28 * math.exp(-(r / 0.25) ** 2) * (1 if z > 0 else -0.6)
        return Vector((v.x * (1 + 0.05 * v.z), v.y * (1 + 0.05 * v.z), z))
    deform(a, f)
    a.scale = (0.52, 0.5, 0.48)
    tube([(0, 0, 0.75), (0.02, 0, 0.9), (0.08, 0, 1.0)], 0.03, mat("astem", (110, 70, 40), 0.6))
    one_leaf((80, 190, 70), (0.1, 0, 0.92), (0, R(70), 0), 0.25, name="aleaf")
    shine((-0.22, -0.45, 0.72), 1.1, rot=(0, R(-30), 0))
    cam(sc, (0, 0, 0.6), 1.45, height=1.1)
    return sc


def cookie():
    sc = setup()
    parts = []
    C = mat("cookie", (215, 150, 80), 0.75)
    parts.append(cyl((0, 0, 0), 0.65, 0.16, C))
    parts.append(torus((0, 0, 0), 0.62, 0.08, C))
    K = mat("chip", (85, 50, 35), 0.5)
    random.seed(9)
    for (x, y) in [(-0.3, 0.2), (0.2, 0.3), (0.35, -0.15), (-0.1, -0.3), (0.0, 0.05), (-0.42, -0.15), (0.12, -0.5),
                   (0.45, 0.2), (-0.2, 0.48)]:
        parts.append(sphere((x, y, 0.08), (0.07, 0.07, 0.05), K, seg=16))
    for k in range(18):
        x, y = random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)
        if x * x + y * y < 0.25:
            parts.append(sphere((x, y, 0.085), (0.02, 0.02, 0.012), mat("crumb", (240, 190, 120), 0.8), seg=10))
    group(parts, (0, 0, 0.6), (R(70), R(-10), 0))
    cam(sc, (0, 0, 0.6), 1.65, height=1.0)
    return sc


def sea_wave():
    sc = setup()
    B = mat("wave", (40, 135, 235), 0.15)
    Bl = mat("wavel", (110, 200, 255), 0.15)
    W = mat("foam", (255, 255, 255), 0.6)
    prof = [(1.25, 0.0), (-1.25, 0.0), (-1.0, 0.22), (-0.6, 0.55), (-0.2, 0.95), (0.2, 1.2), (0.6, 1.18), (0.92, 0.95),
            (0.98, 0.68), (0.82, 0.5), (0.62, 0.52), (0.6, 0.66), (0.7, 0.74), (0.62, 0.86), (0.38, 0.86), (0.18, 0.66),
            (0.22, 0.4), (0.5, 0.22), (0.9, 0.16), (1.25, 0.16)]
    shape(prof, B, depth=0.25, bevel=0.06, loc=(0, 0.15, 0.08), smooth=True)
    inner = [(x * 0.9 - 0.05, z * 0.9 + 0.02) for x, z in prof[1:9]] + [(0.7, 0.62), (0.5, 0.75), (0.1, 0.5), (-0.4, 0.2)]
    shape(inner, Bl, depth=0.02, bevel=0.03, loc=(0, -0.2, 0.08), smooth=True)
    for (x, z, r) in [(-0.15, 1.12, 0.1), (0.12, 1.3, 0.13), (0.42, 1.35, 0.15), (0.72, 1.24, 0.13), (0.93, 1.03, 0.11),
                      (1.04, 0.8, 0.08)]:
        sphere((x, -0.05, z), (r, r, r), W)
    for (x, z, r) in [(1.2, 1.1, 0.05), (1.25, 0.88, 0.035), (-0.45, 1.05, 0.04)]:
        sphere((x, -0.1, z), (r, r, r), W)
    sphere((0, 0.15, 0.05), (1.45, 0.45, 0.12), B)
    cam(sc, (0, 0, 0.7), 2.8, height=0.8)
    return sc


def palm():
    sc = setup()
    Tr = mat("palmt", (180, 120, 70), 0.7)
    Td = mat("palmd", (155, 100, 60), 0.7)
    n = 12
    top = None
    for k in range(n):
        t = k / (n - 1)
        x, z = 0.35 * t ** 2, 0.08 + t * 1.55
        r = 0.15 - 0.05 * t
        sphere((x, 0, z), (r * 1.1, r * 1.1, 0.11), Tr if k % 2 else Td)
        top = (x, 0, z + 0.05)
    G = [mat("palmg", (55, 175, 70), 0.5), mat("palmg2", (95, 200, 80), 0.5)]
    for k, (a, L) in enumerate([(10, 1.0), (55, 0.8), (125, 0.8), (170, 1.0), (215, 0.75), (325, 0.75), (90, 0.6)]):
        ar = R(a)
        dx, dy = math.cos(ar), math.sin(ar) * 0.5
        spine = []
        for j in range(8):
            t = j / 7
            spine.append((top[0] + dx * t * L, top[1] + dy * t * L, top[2] + 0.3 * L * math.sin(t * math.pi * 0.8) - 0.55 * L * t * t))
        tube(spine, 0.03, G[0])
        for j in range(1, 8):  # hojitas colgando a los dos lados del nervio
            t = j / 7
            w = 0.2 * math.sin(math.pi * (0.2 + 0.75 * t)) + 0.05
            p = Vector(spine[j])
            for sy in (-1, 1):
                o = sphere(tuple(p + Vector((0, sy * 0.04, -w * 0.7))), (0.06, 0.03, w), G[(j + k) % 2], seg=16)
                o.rotation_euler = (R(sy * 25), R(-25 * math.cos(ar)), ar)
    for (dx, dz) in [(-0.1, -0.12), (0.1, -0.14), (0.0, -0.24)]:
        sphere((top[0] + dx, -0.14, top[2] + dz), (0.11, 0.11, 0.11), mat("coco", (120, 75, 40), 0.6))
    sphere((0, 0, 0.0), (0.75, 0.45, 0.14), mat("sand", (250, 220, 150), 0.8))
    cam(sc, (0.3, 0, 1.0), 2.6, height=1.2)
    return sc


def mushroom():
    sc = setup()
    Rd = mat("mush", (240, 45, 55), 0.3)
    Cr = mat("mstem", (255, 240, 215), 0.6)
    st = cyl((0, 0, 0.35), 0.24, 0.7, Cr)
    deform(st, lambda v: Vector((v.x * (1.12 - 0.15 * v.z), v.y * (1.12 - 0.15 * v.z), v.z)))
    cap = sphere((0, 0, 0.72), (0.65, 0.62, 0.5), Rd, seg=64)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.bisect(plane_co=(0, 0, 0.66), plane_no=(0, 0, 1), clear_inner=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    sphere((0, 0, 0.7), (0.64, 0.6, 0.08), mat("gill", (250, 225, 200), 0.7))
    W = mat("mdot", (255, 255, 255), 0.5)
    C, S = (0, 0, 0.72), (0.65, 0.62, 0.5)
    for (x, z, r) in [(-0.3, 0.92, 0.09), (0.12, 1.08, 0.1), (0.38, 0.88, 0.08), (-0.05, 0.85, 0.07), (-0.48, 0.78, 0.06),
                      (0.52, 0.75, 0.05), (-0.18, 1.12, 0.06)]:
        y = ell_y(C, S, x, z)
        o = sphere((x, y + 0.01, z), (r, 0.025, r), W, seg=24)
        n = Vector((x / S[0] ** 2, y / S[1] ** 2, (z - C[2]) / S[2] ** 2)).normalized()
        o.rotation_euler = Vector((0, -1, 0)).rotation_difference(n).to_euler()
    face(0, -0.25, 0.4, 0.45, Cr, iris=(90, 55, 35), er=0.2)
    sphere((0, 0, 0.0), (0.4, 0.35, 0.06), mat("grass", (90, 190, 80), 0.6))
    cam(sc, (0, 0, 0.62), 1.6, height=1.2)
    return sc


def snowflake():
    sc = setup()
    B = mat("snow", (150, 215, 255), 0.15, emis=0.35)
    Bw = mat("snoww", (230, 245, 255), 0.15, emis=0.5)
    parts = [shape(rounded([(0.18 * math.cos(R(k * 60 + 30)), 0.18 * math.sin(R(k * 60 + 30))) for k in range(6)], 0.03), Bw,
                   depth=0.03, bevel=0.03)]
    for k in range(6):
        a = R(k * 60)
        d = Vector((math.cos(a), 0, math.sin(a)))
        p = Vector((-d.z, 0, d.x))
        parts.append(tube([tuple(d * 0.1), tuple(d * 0.78)], 0.05, B, poly=True))
        parts.append(sphere(tuple(d * 0.82), (0.07, 0.07, 0.07), Bw))
        for (t, L) in [(0.38, 0.22), (0.6, 0.15)]:
            for s in (-1, 1):
                q = d * t
                e = q + (d * 0.6 + p * s) .normalized() * L
                parts.append(tube([tuple(q), tuple(e)], 0.035, B, poly=True))
    group(parts, (0, 0, 0.8), (0, R(10), 0))
    cam(sc, (0, 0, 0.8), 2.0, height=1.0)
    return sc


OBJS = dict(paws=paws, wind=wind, balloon=balloon, feather=feather, strawberry=strawberry, dolphin=dolphin,
            spider=spider, drop=drop, guitar=guitar, dice=dice, house=house, ruler=ruler, sun=sun, brain=brain,
            car=car, leaf=leaf, leaves=leaves, tongue=tongue, shrimp=shrimp, eagle=eagle, tree=tree, bone=bone,
            clock=clock, star=star, lightning=lightning, splash=splash, tooth=tooth, toothbrush=toothbrush,
            microphone=microphone, hands_up=hands_up, egg=egg, lightbulb=lightbulb, moon=moon, heart=heart,
            carrot=carrot, apple=apple, cookie=cookie, sea_wave=sea_wave, palm=palm, mushroom=mushroom,
            snowflake=snowflake)

if __name__ == "__main__":
    for name, fn in OBJS.items():
        if M.ONLY and name not in M.ONLY:
            continue
        p = os.path.join(M.OUT, name + ".png")
        if os.path.exists(p):
            continue
        sc = fn()
        M.render(sc, p)
        print("OK", name, flush=True)
