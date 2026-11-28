"""Objetos 3D para reemplazar los emojis de los bloques de la biblioteca (canciones, juegos, ¿Sabías qué?).
Mismo estilo y luz que objetos.py / objetos2.py: formas redondeadas de juguete, colores vivos, fondo transparente.

Uso: python3 objetos4.py CARPETA_SALIDA [objeto ...]
No pisa archivos que ya existan en la carpeta.
"""
import math
import os
import random

import bpy
from mathutils import Euler, Vector

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


def shape(pts, m, depth=0.08, bevel=0.04, loc=(0, 0, 0), rot=(R(90), 0, 0), smooth=False, name="sh", sharp=()):
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
        for i in sharp:  # esquinas en punta
            sp.bezier_points[i].handle_left_type = sp.bezier_points[i].handle_right_type = "VECTOR"
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


def meta(name, m, elems, res=0.02, thr=0.6, stiff=2.0):
    """Metaball (unión suave de elipsoides). elems: (centro, semiejes) o (centro, semiejes, rotación euler).
    Los semiejes son el tamaño final de cada elipsoide suelto; juntos se funden sin costuras."""
    mb = bpy.data.metaballs.new(name)
    mb.resolution = mb.render_resolution = res
    mb.threshold = thr
    for el in elems:
        e = mb.elements.new()
        e.type = "ELLIPSOID"
        e.co = el[0]
        e.radius = 1 / 0.575
        e.stiffness = stiff
        e.size_x, e.size_y, e.size_z = el[1]
        if len(el) > 2:
            e.rotation = Euler(el[2]).to_quaternion()
    mb.materials.append(m)
    return link(bpy.data.objects.new(name, mb))


def fit(sc, margin=0.05):
    """Encuadre automático: ajusta la escala ortográfica y el desplazamiento de la cámara para que todo el objeto
    entre con un margen en cada lado."""
    camo = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    inv = camo.matrix_world.inverted()
    xs, ys = [], []
    for o in sc.objects:
        if o.type not in ("MESH", "CURVE", "META", "SURFACE", "FONT"):
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        if me is None:
            continue
        mw = ev.matrix_world
        for v in me.vertices:
            q = inv @ (mw @ v.co)
            xs.append(q.x)
            ys.append(q.y)
        ev.to_mesh_clear()
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    S = max(w, h) / (1 - 2 * margin)
    camo.data.ortho_scale = S
    camo.data.shift_x = (max(xs) + min(xs)) / 2 / S
    camo.data.shift_y = (max(ys) + min(ys)) / 2 / S


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
    edge = mat("windedge", (74, 155, 224), 0.12, alpha=0.72)
    core = mat("windcore", (245, 250, 255), 0.1, emis=0.3)
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
        tube(pts, 0.092, edge, radii=radii)
        tube(pts, 0.05, core, radii=radii)
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
    B = mat("dolph", (70, 150, 240), 0.22)
    Bl = mat("dolphb", (205, 232, 255), 0.25)

    def arc(t):  # lomo arqueado (salto): de la cabeza (izquierda) a la cola (derecha)
        a = R(165 - 150 * t)
        P = Vector((1.0 * math.cos(a), 0, 0.15 + 0.45 * math.sin(a)))
        N = Vector((math.cos(a) / 1.0, 0, math.sin(a) / 0.45)).normalized()
        return a, P, N

    def rad(t):
        return 0.43 * math.sin(math.pi * (0.32 + 0.68 * t)) ** 0.9 + 0.1 * (1 - t) if t < 0.95 else 0.11
    el = []
    for k in range(12):
        t = k / 11
        a, P, N = arc(t)
        r = rad(t)
        el.append((tuple(P), (r * 1.15, r * 0.92, r)))
    # hocico largo hacia abajo a la izquierda
    a, P0, N0 = arc(0)
    el.append((tuple(P0 + Vector((-0.42, 0, -0.1))), (0.34, 0.15, 0.13), (0, R(-20), 0)))
    # aleta dorsal (curva hacia la cola)
    a, Pf, Nf = arc(0.42)
    el.append((tuple(Pf + Nf * 0.42), (0.11, 0.06, 0.25), (0, R(-30), 0)))
    # aleta de la cola, soldada
    a, Pe, Ne = arc(1.0)
    tang = Vector((math.sin(a) * 1.0, 0, -math.cos(a) * 0.45)).normalized()
    for ang in (-45, 45):
        dv = Euler((0, R(ang), 0)).to_matrix() @ tang
        el.append((tuple(Pe + dv * 0.2), (0.24, 0.06, 0.08), (0, -math.atan2(dv.z, dv.x), 0)))
    # aleta lateral
    a, Pl, Nl = arc(0.25)
    el.append((tuple(Pl - Nl * 0.3 + Vector((0.05, -0.32, 0))), (0.22, 0.06, 0.1), (R(10), R(-40), 0)))
    parts = [meta("dolbody", B, el)]
    bel = []
    for k in range(7):
        t = k / 11
        a, P, N = arc(t)
        r = rad(t)
        bel.append((tuple(P - N * r * 0.45 + Vector((0, -0.06, 0))), (r * 0.95, r * 0.8, r * 0.55)))
    bel.append((tuple(P0 + Vector((-0.42, -0.03, -0.16))), (0.3, 0.12, 0.07), (0, R(-20), 0)))
    parts.append(meta("dolbelly", Bl, bel))
    # carita: armada mirando a -Y y girada -28° para que, con el giro del delfín, quede de frente a la cámara
    th = R(-28)
    d = Vector((-0.469, -0.883, 0))
    fc = P0 + Vector((0.08, 0, 0.1)) + d * 0.46
    fparts = []
    for sx in (-1, 1):
        fparts += M.eye(sx * 0.17, 0, 0.1, 0.155, (40, 30, 40), False, B)
    fparts.append(torus((-0.2, -0.03, -0.2), 0.14, 0.022, mat("ink", INK, 0.6), rot=(R(90), 0, R(-20)), arc=(0, 0, -1)))
    for sx in (-1, 1):
        fparts.append(sphere((sx * 0.3, 0.02, -0.08), (0.07, 0.02, 0.045), mat("cheek", (255, 140, 160), 0.6)))
    parts.append(group(fparts, tuple(fc), (0, 0, th)))
    parts.append(shine((0.05, -0.4, 0.78), 1.2, rot=(0, R(10), 0)))
    group(parts, (0, 0, 0), (0, 0, R(28)))
    cam(sc, (0, 0, 0.55), 3.0, height=1.2)
    return sc


def spider():
    sc = setup()
    P = mat("spid", (130, 80, 210), 0.45)
    Pd = mat("spidl", (100, 60, 170), 0.5)
    sphere((0, 0.28, 0.66), (0.42, 0.42, 0.38), Pd)  # abdomen detrás
    body = (0, 0, 0.6)
    bs = (0.5, 0.45, 0.46)
    sphere(body, bs, P)
    for s in (-1, 1):
        for k, ph in enumerate((-12, 18, 48, 78)):   # patas a los costados y atrás, lejos de la cara
            a = R(ph)
            u = Vector((s * math.cos(a), math.sin(a), 0))
            hip = Vector(body) + u * 0.4 + Vector((0, 0, -0.14))
            knee = hip + u * 0.36 + Vector((0, 0, 0.26))
            foot = hip + u * 0.66 + Vector((0, 0, -0.42))
            mid = hip + u * 0.56 + Vector((0, 0, -0.04))
            tube([tuple(hip), tuple(knee), tuple(mid), tuple(foot)], 0.07, Pd if k % 2 else P)
            sphere(tuple(foot + u * 0.03 + Vector((0, 0, -0.02))), (0.1, 0.1, 0.06), mat("spshoe", (255, 120, 170), 0.4))
    face(0, ell_y(body, bs, 0, 0.62, -0.08), 0.62, 0.7, P, iris=(60, 40, 90), er=0.26, gap=0.33)
    tube([(0, 0.1, 1.05), (0, 0.1, 1.7)], 0.008, mat("thread", (255, 255, 255), 0.5))
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
    # contorno en forma de 8: círculo grande abajo, chico arriba y una cintura suave
    out = []
    for k in range(9):        # círculo de abajo, de la cintura derecha a la izquierda pasando por abajo
        a = R(40 - k * 35)
        out.append((0.5 * math.cos(a), 0.5 * math.sin(a)))
    out.append((-0.27, 0.42))
    for k in range(7):        # círculo de arriba, de izquierda a derecha pasando por arriba
        a = R(200 - k * 36.6)
        out.append((0.38 * math.cos(a), 0.62 + 0.38 * math.sin(a)))
    out.append((0.27, 0.42))
    parts = [shape(out, Rd, depth=0.13, bevel=0.05, smooth=True, loc=(0, 0, 0))]
    inner = [(x * 0.85, 0.06 + y * 0.85) for x, y in out]
    parts.append(shape(inner, Y, depth=0.005, bevel=0.02, smooth=True, loc=(0, -0.19, 0)))
    parts.append(cyl((0, -0.2, 0.42), 0.14, 0.02, mat("hole", (70, 35, 35), 0.8), rot=(R(90), 0, 0)))
    parts.append(torus((0, -0.21, 0.42), 0.15, 0.025, mat("gring", (60, 160, 255), 0.4), rot=(R(90), 0, 0)))
    parts.append(box((0, -0.12, 1.4), (0.24, 0.16, 0.95), mat("neck", (170, 100, 60), 0.5), 0.05))
    parts.append(box((0, -0.12, 1.98), (0.32, 0.16, 0.34), mat("ghead", (60, 160, 255), 0.4), 0.07))
    for sx in (-1, 1):
        for z in (1.9, 2.05):
            parts.append(cyl((sx * 0.2, -0.12, z), 0.025, 0.1, mat("pegs", (230, 230, 240), 0.3), rot=(0, R(90), 0)))
            parts.append(sphere((sx * 0.26, -0.12, z), (0.04, 0.06, 0.05), mat("peg", (255, 255, 255), 0.3)))
    parts.append(box((0, -0.21, -0.18), (0.36, 0.06, 0.08), mat("bridge", (90, 50, 40), 0.5), 0.02))
    for k in range(4):
        x = -0.06 + k * 0.04
        parts.append(cyl((x, -0.215, 0.88), 0.006, 2.1, mat("gstr", (240, 240, 240), 0.2, metal=0.6)))
    for (x, z) in [(-0.3, -0.05), (0.32, 0.0), (0.22, 0.78)]:
        parts.append(sphere((x, -0.2, z), (0.05, 0.02, 0.05), mat("gdot", (255, 255, 255), 0.4)))
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
    Pk = mat("tface", (255, 175, 195), 0.4)
    C, S = (0, 0, 0.75), (0.7, 0.62, 0.66)
    sphere(C, S, Pk, seg=64)
    for sx in (-1, 1):  # orejitas redondas
        sphere((sx * 0.5, 0.1, 1.3), (0.18, 0.12, 0.18), Pk)
    yf = ell_y(C, S, 0, 0.58)
    for sx in (-1, 1):
        M.eye(sx * 0.25, ell_y(C, S, sx * 0.25, 0.95, -0.07), 0.95, 0.17, (70, 45, 35), False, Pk)
        sphere((sx * 0.45, ell_y(C, S, sx * 0.45, 0.68, -0.01), 0.68), (0.1, 0.03, 0.065), mat("cheek", (255, 120, 150), 0.6))
    # boca abierta (rosa cálido) con la lengua afuera
    sphere((0, yf + 0.02, 0.55), (0.28, 0.08, 0.17), mat("mouthin", (176, 71, 90), 0.5))
    torus((0, yf - 0.01, 0.55), 1.0, 0.035, mat("lip", (220, 90, 120), 0.4), rot=(R(90), 0, 0)).scale = (0.29, 0.18, 1)
    box((0, yf - 0.03, 0.66), (0.16, 0.05, 0.07), mat("teeth", (255, 255, 255), 0.25), 0.03)
    T = mat("tongue", (255, 85, 125), 0.15)
    t = sphere((0, yf - 0.12, 0.36), (0.2, 0.09, 0.27), T)
    t.rotation_euler = (R(-25), 0, 0)
    tube([(0, yf - 0.215, 0.5), (0, yf - 0.23, 0.38), (0, yf - 0.2, 0.22)], 0.012, mat("tline", (215, 55, 95), 0.4))
    shine((-0.08, yf - 0.22, 0.34), 0.6, rot=(0, R(-60), 0))
    shine((-0.35, ell_y(C, S, -0.35, 1.2, 0.01), 1.2), 1.3, rot=(0, R(-40), 0))
    cam(sc, (0, 0, 0.75), 1.9, height=1.1)
    return sc


def shrimp():
    sc = setup()
    Or = mat("shrimp", (255, 130, 100), 0.3)
    Ol = mat("shrimpl", (255, 190, 160), 0.35)
    cx, cz, Rc = 0.1, 0.6, 0.42
    n = 8
    segs = []
    for k in range(n):  # cuerpo curvado en C (de la cabeza, a la izquierda, por arriba hasta abajo)
        t = k / (n - 1)
        a = R(165 - t * 240)
        r = 0.27 - 0.15 * t
        segs.append((a, r, Vector((cx + Rc * math.cos(a), 0, cz + Rc * math.sin(a)))))
    elems = [(tuple(P), (r * 1.1, r * 0.95, r)) for a, r, P in segs]
    # cola en abanico soldada al último segmento
    a, r, P = segs[-1]
    tang = Vector((math.sin(a), 0, -math.cos(a)))
    for k, ang in enumerate((-35, 0, 35)):
        dv = Euler((0, R(ang), 0)).to_matrix() @ tang
        c = P + dv * 0.2
        rot = (0, -math.atan2(dv.z, dv.x), 0)
        elems.append((tuple(c), (0.17, 0.04, 0.07), rot))
    hc = Vector((-0.42, 0, 0.7))
    elems.append((tuple(hc), (0.32, 0.28, 0.28)))
    meta("shrbody", Or, elems)
    # placas del caparazón: bandas claras que cruzan el lomo
    Op = mat("shrplate", (255, 155, 125), 0.3)
    for k in range(1, n - 1):  # placas apenas en relieve, del mismo coral un poco más claro
        a, r, P = segs[k]
        a2, r2, P2 = segs[k + 1]
        Pm = (P + P2) / 2
        rm = (r + r2) / 2
        N = Vector((math.cos((a + a2) / 2), 0, math.sin((a + a2) / 2)))
        Y = Vector((0, -1, 0))
        rr = rm * 0.98
        pts = [tuple(Pm + rr * (math.cos(R(q)) * N + math.sin(R(q)) * Y)) for q in range(20, 111, 10)]
        tube(pts, 0.035, Op, res=4)
    # patitas en el lado de adentro de la C
    for k in range(1, 6):  # patitas cortas y redondas pegadas a la panza
        a, r, P = segs[k]
        N = Vector((math.cos(a), 0, math.sin(a)))
        b = P - N * (r * 0.55) + Vector((0, -r * 0.45, 0))
        e = P - N * (r + 0.1) + Vector((0, -r * 0.5, 0))
        tube([tuple(b), tuple(e)], 0.04, Op, poly=True)
        sphere(tuple(e), (0.045, 0.045, 0.045), Op)
    # cara
    for (x, z, er) in [(-0.6, 0.8, 0.12), (-0.33, 0.83, 0.11)]:
        M.eye(x, ell_y(hc, (0.32, 0.28, 0.28), x, z, -0.07), z, er, (40, 30, 40), False, Or)
    torus((-0.5, ell_y(hc, (0.32, 0.28, 0.28), -0.5, 0.6, 0.01), 0.62), 0.07, 0.015, mat("ink", INK, 0.6),
          rot=(R(90), 0, 0), arc=(0, 0, -1))
    sphere((-0.7, ell_y(hc, (0.32, 0.28, 0.28), -0.68, 0.66), 0.66), (0.05, 0.02, 0.035), mat("cheek", (255, 90, 120), 0.6))
    for s_ in (0, 1):  # antenas
        tube([(-0.5, -0.05, 0.95), (-0.65 - s_ * 0.12, -0.05, 1.25), (-0.35 + s_ * 0.15, -0.05, 1.45)], 0.013, Or)
    cam(sc, (-0.05, 0, 0.7), 2.0, height=1.1)
    return sc


def eagle():
    sc = setup()
    Br = mat("eagleb", (125, 78, 42), 0.5)
    Bd = mat("eagled", (85, 50, 28), 0.5)
    W = mat("eaglew", (255, 255, 255), 0.45)
    Yb = mat("beakE", (255, 185, 30), 0.3)
    sphere((0, 0, 0.6), (0.42, 0.38, 0.5), Br)
    sphere((0, -0.2, 0.5), (0.26, 0.2, 0.32), mat("eaglebel", (200, 150, 100), 0.6))
    head = (0, -0.05, 1.18)
    hs = (0.4, 0.37, 0.36)
    sphere(head, hs, W)
    for s in (-1, 1):  # alas abiertas, oscuras
        o = sphere((s * 0.62, 0.08, 0.95), (0.42, 0.07, 0.22), Bd)
        o.rotation_euler = (0, R(-s * 30), 0)
        for k in range(4):
            o = sphere((s * (0.62 + 0.36 * math.cos(R(30 + k * 14))), 0.1, 0.85 + 0.36 * math.sin(R(30 + k * 14))),
                       (0.3 - k * 0.03, 0.05, 0.075), Bd)
            o.rotation_euler = (0, R(-s * (30 + k * 14)), 0)
    for s in (-1, 0, 1):  # cola
        o = sphere((s * 0.1, 0.1, 0.12), (0.08, 0.05, 0.18), Bd)
        o.rotation_euler = (0, R(s * 20), 0)
    for s in (-1, 1):
        sphere((s * 0.16, -0.2, 0.08), (0.1, 0.12, 0.05), Yb)
        M.eye(s * 0.17, ell_y(head, hs, s * 0.17, 1.3, -0.06), 1.3, 0.12, (110, 70, 30), False, W)
        sphere((s * 0.3, ell_y(head, hs, s * 0.3, 1.08, -0.01), 1.08), (0.065, 0.02, 0.04), mat("cheek", (255, 140, 160), 0.6))
    # pico grande y ganchudo
    yb = ell_y(head, hs, 0, 1.1)
    sphere((0, yb - 0.08, 1.12), (0.16, 0.18, 0.12), Yb)
    tube([(0, yb - 0.18, 1.15), (0, yb - 0.27, 1.08), (0, yb - 0.24, 0.98)], 0.06, Yb, radii=[1.0, 0.7, 0.3])
    torus((0, yb - 0.02, 0.98), 0.08, 0.014, mat("ink", INK, 0.6), rot=(R(90), 0, 0), arc=(0, 0, -1))
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
    sphere((0, 0.1, 0.05), (1.05, 0.6, 0.08), Bl)                 # charco
    el = []
    for k in range(24):                                              # anillo continuo de la corona
        a = k / 24 * 2 * math.pi
        el.append(((0.45 * math.cos(a), 0.1 + 0.3 * math.sin(a), 0.14), (0.13, 0.13, 0.12)))
    tips = []
    for k in range(8):                                               # puntas que suben y se afinan
        a = k / 8 * 2 * math.pi + 0.2
        h = 0.5 if math.sin(a) > 0 else 0.4
        for j in range(5):
            t = j / 4
            rr = 0.45 + 0.14 * t
            el.append(((rr * math.cos(a), 0.1 + rr * 0.66 * math.sin(a), 0.16 + h * t), (0.11 - 0.06 * t, 0.11 - 0.06 * t, 0.1)))
        tips.append((0.62 * math.cos(a), 0.1 + 0.62 * 0.66 * math.sin(a), 0.16 + h + 0.15, a))
    meta("crown", B, el, res=0.015)
    for (x, y, z, a) in tips:                                        # gotitas en la punta
        sphere((x, y, z), (0.07, 0.07, 0.07), B)
    for (x, z, r) in [(-0.85, 1.0, 0.13), (-0.35, 1.3, 0.15), (0.3, 1.35, 0.14), (0.85, 1.05, 0.13), (0.0, 1.05, 0.1),
                      (-1.1, 0.55, 0.09), (1.1, 0.6, 0.09)]:
        droplet((x, -0.15, z), r, (-x, 0, -(z - 0.2)))
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
    c = (0, 0, 1.24)
    parts.append(sphere(c, (0.3, 0.3, 0.3), mat("micg", (215, 220, 232), 0.25, metal=0.75)))
    K = mat("micmesh", (160, 165, 185), 0.35, metal=0.6)
    for k in range(6):  # malla fina: meridianos
        parts.append(torus(c, 0.302, 0.006, K, rot=(R(90), 0, k * math.pi / 6)))
    for z in (-0.2, -0.1, 0.0, 0.1, 0.2):  # y paralelos
        r = math.sqrt(0.302 ** 2 - z ** 2)
        parts.append(torus((0, 0, c[2] + z), r, 0.006, K))
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
        parts = [sphere((0, 0, 0), (0.3, 0.15, 0.28), W)]
        for k, (a, L) in enumerate([(-26, 0.28), (-9, 0.34), (9, 0.33), (26, 0.27)]):
            ar = R(a)
            bx, bz = 0.21 * math.sin(ar), 0.18
            ex, ez = bx + L * math.sin(ar), bz + L * math.cos(ar)
            parts.append(tube([(bx, 0, bz), (ex, 0, ez)], 0.095, W, poly=True))
            parts.append(sphere((ex, 0, ez), (0.095, 0.095, 0.095), W))
        parts.append(tube([(0.22, 0, -0.02), (0.38, 0, 0.12), (0.44, 0, 0.26)], 0.095, W))
        parts.append(sphere((0.44, 0, 0.26), (0.095, 0.095, 0.095), W))
        parts.append(cyl((0, 0, -0.32), 0.2, 0.18, Cf))
        parts.append(torus((0, 0, -0.24), 0.2, 0.05, Cf))
        group(parts, (s * 0.55, 0, 0.72), (0, R(s * 15), 0)).scale = (-s * 1.2, 1.2, 1.2)
        for (a, L) in [(-50, 0.2), (-15, 0.24), (20, 0.2)]:  # rayitas de festejo
            ar = R(a * s + s * 15)
            cx, cz = s * 0.55 + 1.0 * math.sin(ar), 0.72 + 1.0 * math.cos(ar)
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


def puffy(pts, m, H=0.25, back=0.5, step=0.03, loc=(0, 0, 0), name="puffy", hfun=None, smooth=25):
    """Forma 2D «inflada» como un globo (x, z de frente): malla de Delaunay dentro del contorno y cada punto sale
    hacia la cámara según su distancia al borde (alisada). Mantiene las puntas (la del corazón) sin los picos que
    deja el bisel de las curvas en las esquinas agudas."""
    from mathutils import geometry
    P = [Vector(p) for p in pts]
    edges = [(P[i], P[(i + 1) % len(P)]) for i in range(len(P))]
    def dist(q):
        best = 1e9
        for A, Bp in edges:
            ab = Bp - A
            t = max(0.0, min(1.0, (q - A).dot(ab) / ab.length_squared))
            best = min(best, (A + ab * t - q).length)
        return best

    def inside(q):
        c = False
        for A, Bp in edges:
            if (A.y > q.y) != (Bp.y > q.y) and q.x < A.x + (q.y - A.y) * (Bp.x - A.x) / (Bp.y - A.y):
                c = not c
        return c
    xs, ys = [p.x for p in P], [p.y for p in P]
    verts = list(P)
    j = 0
    y = min(ys)
    while y < max(ys):
        x = min(xs) + (step / 2 if j % 2 else 0)
        while x < max(xs):
            q = Vector((x, y))
            if inside(q) and dist(q) > step * 0.6:
                verts.append(q)
            x += step
        y += step * 0.866
        j += 1
    out = geometry.delaunay_2d_cdt(verts, [(i, (i + 1) % len(P)) for i in range(len(P))], [], 1, 1e-7)
    V, F = out[0], out[2]
    ds = [dist(Vector(v)) for v in V]
    dmax = max(ds)
    hs = [math.sqrt(max(0.0, 1 - (1 - min(1.0, d / dmax)) ** 2)) for d in ds]
    if hfun:  # altura propia (p. ej. lóbulos que se funden), siempre 0 en el borde
        hs = [hfun(Vector(v), h) * math.sqrt(min(1.0, d / 0.07)) for v, h, d in zip(V, hs, ds)]
    nb = [set() for _ in V]
    for f in F:
        for i in range(len(f)):
            a_, b_ = f[i], f[(i + 1) % len(f)]
            nb[a_].add(b_)
            nb[b_].add(a_)
    nP = len(P)
    for _ in range(smooth):  # alisar las alturas (sin la «cresta» del medio)
        hs = [hs[i] if i < nP else 0.5 * hs[i] + 0.5 * sum(hs[n] for n in nb[i]) / max(1, len(nb[i])) for i in range(len(V))]
    objs = []
    for side, k in ((-1, 1.0), (1, back)):
        me = bpy.data.meshes.new(name)
        me.from_pydata([(v.x, side * k * H * h, v.y) for v, h in zip(V, hs)], [], [list(f) for f in F])
        me.update()
        ny = sum(pl.normal.y for pl in me.polygons)
        if ny * side < 0:
            me.flip_normals()
        for pl in me.polygons:
            pl.use_smooth = True
        me.materials.append(m)
        ob = link(bpy.data.objects.new(name, me))
        ob.location = loc
        objs.append(ob)
    return objs


def heart():
    sc = setup()
    Rd = mat("heart", (240, 40, 70), 0.15)
    pts = []
    for k in range(96):
        t = k / 96 * 2 * math.pi
        if t < 0.3 or t > 2 * math.pi - 0.3:      # sin el pico del medio de arriba: un hoyito suave
            continue
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x / 22, y / 22 * (0.85 if y < 0 else 1.0)))
    pts.append((0, 3.6 / 22))
    def lobes(q, hd, k=9.0, R_=0.38):
        # dos lóbulos redondos (cúpulas) fundidos con la forma general: sin pliegue bajo el hoyito
        hs_ = [hd]
        for cx in (-0.35, 0.35):
            r2 = (q.x - cx) ** 2 + (q.y - 0.19) ** 2
            hs_.append(math.sqrt(max(0.0, R_ * R_ - r2)) / R_)
        return math.log(sum(math.exp(k * h) for h in hs_)) / k - math.log(3) / k * 0.6
    puffy(pts, Rd, H=0.34, loc=(0, 0, 0.75), step=0.025, smooth=20, hfun=lobes)
    shine((-0.38, -0.3, 0.98), 1.2, rot=(0, R(-40), 0))
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
    C = mat("cookie", (215, 150, 80), 0.8)
    C.node_tree.nodes["Principled BSDF"].inputs["Coat Weight"].default_value = 0.0   # sin el reflejo cuadrado de la luz
    C.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.2
    parts.append(sphere((0, 0, 0), (0.66, 0.66, 0.12), C, seg=64))
    K = mat("chip", (85, 50, 35), 0.5)
    random.seed(9)
    for (x, y) in [(-0.3, 0.2), (0.2, 0.3), (0.35, -0.15), (-0.1, -0.3), (0.0, 0.05), (-0.42, -0.15), (0.12, -0.5),
                   (0.45, 0.2), (-0.2, 0.48)]:
        z = 0.12 * math.sqrt(max(0, 1 - (x * x + y * y) / 0.66 ** 2))
        parts.append(sphere((x, y, z), (0.07, 0.07, 0.05), K, seg=16))
    for k in range(18):
        x, y = random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)
        if x * x + y * y < 0.25:
            z = 0.12 * math.sqrt(max(0, 1 - (x * x + y * y) / 0.66 ** 2))
            parts.append(sphere((x, y, z), (0.02, 0.02, 0.012), mat("crumb", (240, 190, 120), 0.8), seg=10))
    group(parts, (0, 0, 0.6), (R(58), R(-10), 0))
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
    # espuma pegada a la cresta (la forma tiene el borde en x, z + 0.08)
    for (x, z, r) in [(-0.2, 1.0, 0.1), (0.1, 1.22, 0.13), (0.4, 1.28, 0.15), (0.7, 1.2, 0.13), (0.93, 1.02, 0.11),
                      (1.03, 0.78, 0.08)]:
        sphere((x, -0.08, z), (r, r * 0.9, r), W)
    # mar: bloque redondeado con el borde de arriba ondulado
    sea = [(1.45, -0.15), (-1.45, -0.15)] + [(-1.45 + 2.9 * k / 16, 0.3 + 0.06 * math.cos(k * math.pi / 2)) for k in range(17)]
    shape(sea, mat("wavebase", (50, 145, 240), 0.25), depth=0.22, bevel=0.1, loc=(0, -0.05, 0.0), smooth=True,
          sharp=(0, 1))
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
        top = Vector((x, 0, z + 0.05))
    G = [mat("palmg", (55, 175, 70), 0.3), mat("palmg2", (95, 200, 80), 0.3)]
    Gv = mat("palmv", (150, 225, 110), 0.4)
    for k, (az, L) in enumerate([(5, 1.05), (50, 0.85), (130, 0.85), (175, 1.05), (225, 0.8), (315, 0.8), (90, 0.7)]):
        W = 0.3 * L

        def frond(v, L=L, W=W):
            u = (v.x + 1) / 2
            w = W * max(0.0, math.sin(math.pi * min(1, max(0.0, u) * 1.05))) ** 0.6
            cut = 1 - 0.18 * (math.sin(u * 28) > 0.6) * (abs(v.y) > 0.55) * (u > 0.3)   # algunos cortecitos
            return Vector((u * L, v.y * w * cut, v.z * 0.035 + 0.35 * L * math.sin(u * math.pi * 0.75) - 0.75 * L * u * u))
        f = sphere((0, 0, 0), (1, 1, 1), G[k % 2], seg=48)
        deform(f, frond)
        f.location = top
        f.rotation_euler = (R(50 * math.cos(R(az))), 0, R(az))
        spine = [frond(Vector((-1 + 2 * j / 6, 0, 1))) + Vector((0, 0, 0.01)) for j in range(7)]
        rib = tube([tuple(p) for p in spine], 0.018, Gv)
        rib.location = top
        rib.rotation_euler = (R(50 * math.cos(R(az))), 0, R(az))
    for (dx, dz) in [(-0.13, -0.14), (0.13, -0.16), (0.0, -0.28)]:
        sphere((top.x + dx, -0.16, top.z + dz), (0.15, 0.14, 0.15), mat("coco", (120, 75, 40), 0.5))
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

# Encuadre automático con margen (revisión de calidad: nada tocando los bordes)
FIT = {"wind", "balloon", "dolphin", "spider", "guitar", "tongue", "shrimp", "eagle", "splash", "microphone",
       "hands_up", "lightbulb", "moon", "heart", "cookie", "sea_wave", "palm"}

if __name__ == "__main__":
    for name, fn in OBJS.items():
        if M.ONLY and name not in M.ONLY:
            continue
        p = os.path.join(M.OUT, name + ".png")
        if os.path.exists(p):
            continue
        sc = fn()
        if name in FIT:
            fit(sc, 0.05)
        M.render(sc, p)
        print("OK", name, flush=True)
