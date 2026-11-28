"""Animales invitados en 3D (mismo estilo que modelos.py): reemplazan a los emojis de los invitados.

Uso: python3 invitados.py CARPETA_SALIDA [Nombre ...]
Cada animal se renderiza dos veces: <Nombre>_0.png (boca cerrada) y <Nombre>_1.png (boca abierta), 900x900 con
transparencia. La cámara se encuadra sola (ortográfica) para que el animal entre completo con las patas abajo.
Los archivos que ya existen no se vuelven a renderizar (si Blender se cae en una tanda larga, volver a correrlo).
"""
import math
import os
import random

import bpy
from mathutils import Vector

import modelos as M
from modelos import mat, sphere, cyl, torus, cone, eye, mouth

OUT = M.OUT
ONLY = M.ONLY
TEST = os.environ.get("INVITADOS_TEST", "") in ("1", "2")  # 1: prueba rápida solo boca cerrada; 2: las dos
BOTH = os.environ.get("INVITADOS_TEST", "") != "1"

INK = (40, 35, 55)
PINK = (255, 150, 170)


# ------------------------------------------------------------------ utilidades
def surf_y(c, r, x, z):
    """Coordenada y de la cara delantera (−Y) de un elipsoide en (x, z)."""
    dx = (x - c[0]) / r[0]
    dz = (z - c[2]) / r[2]
    return c[1] - r[1] * math.sqrt(max(0.0, 1 - dx * dx - dz * dz))


def eyes(c, r, dx, z, er, iris, skin, closed=False, lashes=False):
    for s in (-1, 1):
        x = c[0] + s * dx
        eye(x, surf_y(c, r, x, z) + er * 0.25, z, er, iris, closed, skin, lashes=lashes)


def cheeks(c, r, dx, z, size=0.08):
    for s in (-1, 1):
        x = c[0] + s * dx
        sphere((x, surf_y(c, r, x, z) + 0.005, z), (size, 0.03, size * 0.65), mat("cheek", PINK, 0.6), name="cheek")


def put_mouth(c, r, z, w, open_, tooth=False, lip=INK, x=None):
    x = c[0] if x is None else x
    return mouth(x, surf_y(c, r, x, z) - 0.015, z, w, open_, tooth=tooth, lip=lip)


def nose(c, r, z, size, col=INK, x=None):
    x = c[0] if x is None else x
    o = sphere((x, surf_y(c, r, x, z) + size * 0.3, z), (size, size * 0.6, size * 0.72), mat("nose" + str(col), col, 0.25), name="nose")
    sphere((x - size * 0.3, surf_y(c, r, x, z) - size * 0.2, z + size * 0.3), (size * 0.25, size * 0.1, size * 0.18),
           mat("glint", (255, 255, 255), 0.1, emis=1.0), name="nglint")
    return o


def patch(c, r, az, el, size, m, flat=0.3, sx=1.0):
    """Mancha sobre la superficie de un elipsoide. az=0 mira a cámara (−Y); az>0 hacia +X; el>0 hacia arriba (grados)."""
    a, e = math.radians(az), math.radians(el)
    n0 = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    p = Vector((c[0] + r[0] * n0.x, c[1] + r[1] * n0.y, c[2] + r[2] * n0.z))
    n = Vector((n0.x / r[0], n0.y / r[1], n0.z / r[2])).normalized()
    o = sphere(tuple(p), (size * sx, size, size * flat), m, seg=24, name="patch")
    o.rotation_euler = n.to_track_quat("Z", "Y").to_euler()
    return o


def tube(p0, p1, r0, r1, m, caps=True, name="tube"):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=r0, radius2=r1, depth=d.length, location=tuple((p0 + p1) / 2))
    o = bpy.context.object
    o.name = name
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    if caps:
        sphere(tuple(p0), (r0, r0, r0), m, seg=24, name="cap")
        sphere(tuple(p1), (r1, r1, r1), m, seg=24, name="cap")
    return o


def chain(f, rf, m, n=40, name="chain"):
    """Tubo suave hecho de esferas a lo largo de la curva f(t), t en [0, 1], con radio rf(t)."""
    pts = [Vector(f(i / 50)) for i in range(51)]
    L = sum((pts[i + 1] - pts[i]).length for i in range(50))
    rmin = min(rf(i / 10) for i in range(11))
    n = max(n, int(L / (rmin * 0.12)))
    for i in range(n + 1):
        t = i / n
        r = rf(t)
        sphere(f(t), (r, r, r), m, seg=20, name=name)


def bez(p0, p1, p2, p3=None):
    """Curva de Bézier cuadrática o cúbica como función de t."""
    P = [Vector(p) for p in ((p0, p1, p2) if p3 is None else (p0, p1, p2, p3))]
    if len(P) == 3:
        return lambda t: tuple((1 - t) ** 2 * P[0] + 2 * (1 - t) * t * P[1] + t * t * P[2])
    return lambda t: tuple((1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t * t * P[2] + t ** 3 * P[3])


def beak(base, length, r, m, open_, up=0.0, lower_ratio=0.75):
    """Pico de pájaro hacia −Y desde base. Abierto: se separan las dos mitades y se ve la boca."""
    x, y, z = base
    a_up = math.radians(90 - up - (14 if open_ else 0))
    cone((x, y - length * 0.45, z + r * 0.25), r, 0.0, length, m, rot=(a_up, 0, 0), name="beakU")
    a_lo = math.radians(90 - up + (24 if open_ else 0))
    cone((x, y - length * 0.4 * lower_ratio, z - r * 0.35), r * 0.85, 0.0, length * lower_ratio, m, rot=(a_lo, 0, 0), name="beakL")
    if open_:
        sphere((x, y - length * 0.2, z - r * 0.1), (r * 0.8, length * 0.3, r * 0.7), mat("mouth", (95, 20, 40), 0.7), name="mouthin")


def stripes_mat(name, c1, c2, freq=16.0, rough=0.45, split=0.55):
    """Material a rayas horizontales (como el de Zumbi), según la altura Z del objeto."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    sin = nt.nodes.new("ShaderNodeMath")
    sin.operation = "SINE"
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = freq
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = tuple(M.srgb2lin(v) for v in c1) + (1,)
    ramp.color_ramp.elements[1].position = split
    ramp.color_ramp.elements[1].color = tuple(M.srgb2lin(v) for v in c2) + (1,)
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mul.inputs[0])
    nt.links.new(mul.outputs[0], sin.inputs[0])
    nt.links.new(sin.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def chibi(skin, belly=None, foot=None, hz=1.35, hr=(0.5, 0.46, 0.44), bz=0.6, br=(0.42, 0.38, 0.48), arms=True,
          feet=True, arm_m=None, foot_scale=(0.17, 0.24, 0.09)):
    """Cuerpo base de dibujo animado: cuerpo, panza, cabeza grande, bracitos y pies. Devuelve (cabeza, radios)."""
    sphere((0, 0, bz), br, skin, name="body")
    if belly:
        sphere((0, -br[1] * 0.5, bz - 0.03), (br[0] * 0.7, br[1] * 0.55, br[2] * 0.75), belly, name="belly")
    if arms:
        for s in (-1, 1):
            o = sphere((s * br[0] * 0.98, -0.1, bz + br[2] * 0.25), (0.12, 0.11, 0.2), arm_m or skin, name="arm")
            o.rotation_euler = (0, s * math.radians(-25), 0)
    if feet:
        for s in (-1, 1):
            sphere((s * 0.22, -0.12, foot_scale[2]), foot_scale, foot or skin, name="foot")
    hc = (0, 0, hz)
    sphere(hc, hr, skin, name="head")
    return hc, hr


def frame(sc, pad=1.08, rise=0.55):
    """Cámara como la de los personajes (ángulo 3/4) y encuadre automático del modelo."""
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in sc.objects:
        if o.type not in ("MESH", "META", "FONT", "CURVE"):
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ev.matrix_world
        pts += [mw @ v.co for v in me.vertices]
        ev.to_mesh_clear()
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    tgt = (lo + hi) / 2
    cam = M.camera_and_lights(sc, target=tuple(tgt), dist=6.2, height=tgt.z + rise, ortho=2.5)
    bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted()
    loc = [inv @ p for p in pts]
    x0, x1 = min(p.x for p in loc), max(p.x for p in loc)
    y0, y1 = min(p.y for p in loc), max(p.y for p in loc)
    R = cam.matrix_world.to_3x3()
    cam.location = cam.location + R @ Vector(((x0 + x1) / 2, (y0 + y1) / 2, 0))
    cam.data.ortho_scale = max(x1 - x0, y1 - y0) * pad
    return cam


def setup():
    sc = M.reset()
    M._mats.clear()
    return sc


def spots(c, r, m, pts, size=0.07, flat=0.3):
    for (az, el, k) in pts:
        patch(c, r, az, el, size * k, m, flat=flat)


# ------------------------------------------------------------------ animales
def guepardo(o):
    sc = setup()
    Y = mat("cheetah", (250, 190, 70), 0.55)
    C = mat("cream", (255, 240, 205), 0.6)
    K = mat("spot", (70, 45, 35), 0.6)
    hc, hr = chibi(Y, C, mat("shoe", (230, 50, 60), 0.4), foot_scale=(0.17, 0.25, 0.1))
    for s in (-1, 1):  # suela blanca de zapatilla
        sphere((s * 0.22, -0.13, 0.03), (0.18, 0.26, 0.04), mat("sole", (255, 255, 255), 0.5), name="sole")
        sphere((s * 0.22, -0.3, 0.12), (0.08, 0.06, 0.03), mat("sole", (255, 255, 255), 0.5), name="lace")
    mc, mr = (0, -0.33, 1.2), (0.25, 0.16, 0.15)
    sphere(mc, mr, C, name="muzzle")
    eyes(hc, hr, 0.19, 1.42, 0.13, (200, 140, 40), Y, lashes=False)
    for s in (-1, 1):  # «lágrimas» negras del guepardo
        x = s * 0.25
        tube((x, surf_y(hc, hr, x, 1.31) + 0.01, 1.31), (s * 0.23, surf_y(hc, hr, s * 0.23, 1.21) + 0.005, 1.21), 0.018, 0.016, K)
        sphere((s * 0.38, -0.02, 1.72), (0.12, 0.08, 0.13), Y, name="ear")
        sphere((s * 0.38, -0.07, 1.72), (0.07, 0.04, 0.08), mat("earin", (255, 170, 170), 0.6), name="earin")
    nose(mc, mr, 1.27, 0.06, (60, 40, 40))
    put_mouth(mc, mr, 1.15, 0.2, o)
    cheeks(hc, hr, 0.36, 1.25)
    torus((0, 0, 1.55), 0.47, 0.06, mat("band", (60, 150, 255), 0.6), rot=(math.radians(-8), 0, 0), name="headband")
    spots(hc, hr, K, [(-40, 40, 1), (40, 45, 0.8), (0, 62, 0.9), (-60, 10, 0.8), (65, 15, 0.9)], 0.06)
    spots((0, 0, 0.6), (0.42, 0.38, 0.48), K, [(-55, 20, 1), (55, 30, 1), (-60, -25, 0.8), (62, -15, 0.9), (90, 0, 1)], 0.07)
    f = bez((0.25, 0.3, 0.35), (0.85, 0.5, 0.2), (0.75, 0.4, 0.95))
    chain(f, lambda t: 0.07 - 0.015 * t, Y, n=40)
    sphere(f(1.0), (0.07, 0.07, 0.07), K, name="tailtip")
    for t in (0.3, 0.5, 0.7):
        p = f(t)
        torus(p, 0.065, 0.02, K, rot=(0, math.radians(60), 0), name="ring")
    frame(sc)
    return sc


def canguro(o):
    sc = setup()
    B = mat("kanga", (210, 145, 90), 0.6)
    C = mat("cream", (255, 230, 195), 0.6)
    hc, hr = chibi(B, C, B, hz=1.45, br=(0.45, 0.4, 0.55), bz=0.62, foot_scale=(0.15, 0.36, 0.08))
    # bolsa con un canguro bebé que se asoma
    pc, pr = (0, -0.4, 0.5), (0.3, 0.12, 0.2)
    sphere(pc, pr, C, name="pouch")
    torus((0, -0.44, 0.66), 0.25, 0.03, mat("pouchrim", (235, 200, 160), 0.6), rot=(math.radians(80), 0, 0), name="rim")
    bh, bhr = (0.04, -0.42, 0.78), (0.15, 0.13, 0.14)
    sphere(bh, bhr, B, name="joey")
    for s in (-1, 1):
        eye(0.04 + s * 0.06, surf_y(bh, bhr, 0.04 + s * 0.06, 0.8) + 0.01, 0.8, 0.04, (90, 60, 40), False, B)
        sphere((0.04 + s * 0.08, -0.4, 0.95), (0.03, 0.02, 0.08), B, name="joeyear")
    sphere((0.04, surf_y(bh, bhr, 0.04, 0.73), 0.73), (0.025, 0.02, 0.02), mat("ink", INK, 0.3), name="joeynose")
    mc, mr = (0, -0.36, 1.3), (0.22, 0.17, 0.15)
    sphere(mc, mr, C, name="muzzle")
    eyes(hc, hr, 0.19, 1.52, 0.13, (110, 70, 40), B, lashes=True)
    for s in (-1, 1):
        e = sphere((s * 0.24, 0.0, 1.95), (0.1, 0.06, 0.28), B, name="ear")
        e.rotation_euler = (0, s * math.radians(15), 0)
        e = sphere((s * 0.24, -0.04, 1.95), (0.055, 0.03, 0.2), mat("earin", (255, 170, 170), 0.6), name="earin")
        e.rotation_euler = (0, s * math.radians(15), 0)
    nose(mc, mr, 1.37, 0.06)
    put_mouth(mc, mr, 1.25, 0.2, o)
    cheeks(hc, hr, 0.35, 1.36)
    chain(bez((0.1, 0.3, 0.35), (0.3, 0.75, 0.1), (0.45, 0.95, 0.08)), lambda t: 0.16 - 0.1 * t, B, n=40)
    frame(sc)
    return sc


def mariquita(o):
    sc = setup()
    R = mat("ladyred", (235, 40, 50), 0.3)
    K = mat("ladyblack", (45, 40, 55), 0.45)
    F = mat("ladyface", (60, 55, 80), 0.45)
    # caparazón rojo detrás, con línea central y lunares; cuerpo oscuro adelante
    sc_c, sc_r = (0, 0.08, 0.72), (0.62, 0.5, 0.62)
    sphere(sc_c, sc_r, R, name="shell")
    tube((0, sc_c[1] - 0.02, 0.15), (0, sc_c[1] - 0.02, 1.29), 0.025, 0.025, K, caps=False)
    for (az, el, k) in [(55, 30, 1), (65, -20, 0.9), (110, 5, 1.1), (-55, 30, 1), (-65, -20, 0.9), (-110, 5, 1.1),
                        (150, 40, 0.9), (-150, 40, 0.9), (90, 55, 0.8), (-90, 55, 0.8)]:
        patch(sc_c, sc_r, az, el, 0.1 * k, K, flat=0.25)
    sphere((0, -0.33, 0.48), (0.2, 0.13, 0.22), mat("ladybelly", (255, 225, 200), 0.5), name="belly")
    for s in (-1, 1):
        sphere((s * 0.2, -0.15, 0.08), (0.14, 0.2, 0.08), mat("shoe", (255, 210, 60), 0.4), name="foot")
        sphere((s * 0.42, -0.25, 0.75), (0.09, 0.08, 0.16), K, name="arm")
    hc, hr = (0, -0.18, 1.32), (0.44, 0.4, 0.38)
    sphere(hc, hr, F, name="head")
    eyes(hc, hr, 0.17, 1.38, 0.13, (60, 140, 230), F, lashes=True)
    cheeks(hc, hr, 0.31, 1.24)
    put_mouth(hc, hr, 1.15, 0.2, o, lip=(255, 240, 240))
    for s in (-1, 1):
        f = bez((s * 0.12, -0.2, 1.65), (s * 0.18, -0.25, 1.95), (s * 0.32, -0.3, 2.0))
        chain(f, lambda t: 0.022, K, n=20)
        sphere(f(1), (0.06, 0.06, 0.06), R, name="antball")
    frame(sc)
    return sc


def pajaro(o):
    sc = setup()
    B = mat("bluebird", (70, 150, 255), 0.45)
    L = mat("bbelly", (210, 235, 255), 0.55)
    Or = mat("beak", (255, 165, 40), 0.35)
    bc, br = (0, 0, 0.72), (0.58, 0.52, 0.6)
    sphere(bc, br, B, name="body")
    sphere((0, -0.3, 0.55), (0.42, 0.3, 0.4), L, name="belly")
    eyes(bc, br, 0.2, 0.92, 0.13, (60, 90, 170), B, lashes=False)
    beak((0, surf_y(bc, br, 0, 0.76) + 0.05, 0.76), 0.26, 0.1, Or, o)
    cheeks(bc, br, 0.34, 0.74)
    for s in (-1, 1):
        w = sphere((s * 0.56, 0.05, 0.7), (0.12, 0.28, 0.34), B, name="wing")
        w.rotation_euler = (math.radians(-15), s * math.radians(20), 0)
        for k in (-1, 1):
            tube((s * 0.18, -0.05, 0.13), (s * 0.18 + k * 0.08, -0.2, 0.02), 0.025, 0.02, Or)
        tube((s * 0.18, -0.05, 0.2), (s * 0.18, -0.06, 0.08), 0.03, 0.025, Or)
    for k, a in enumerate((-25, 0, 25)):
        cone((math.sin(math.radians(a)) * 0.1, 0.02, 1.36), 0.07, 0.0, 0.25, B, rot=(math.radians(-15), math.radians(a), 0), name="tuft")
    for a in (-20, 0, 20):
        cone((math.sin(math.radians(a)) * 0.15, 0.55, 0.65), 0.08, 0.0, 0.4, B, rot=(math.radians(-60), math.radians(a), 0), name="tail")
    frame(sc)
    return sc


def gallina(o):
    sc = setup()
    W = mat("hen", (255, 250, 240), 0.6)
    R = mat("comb", (240, 50, 60), 0.4)
    Y = mat("beak", (255, 190, 40), 0.35)
    bc, br = (0, 0.05, 0.75), (0.62, 0.58, 0.62)
    sphere(bc, br, W, name="body")
    hc, hr = (0, -0.15, 1.28), (0.4, 0.38, 0.4)
    sphere(hc, hr, W, name="head")
    eyes(hc, hr, 0.16, 1.36, 0.12, (150, 90, 40), W, lashes=True)
    beak((0, surf_y(hc, hr, 0, 1.2) + 0.05, 1.2), 0.22, 0.09, Y, o)
    tube((0, surf_y(hc, hr, 0, 1.06) + 0.04, 1.08), (0, surf_y(hc, hr, 0, 1.06) - 0.02, 0.98), 0.05, 0.06, R)
    cheeks(hc, hr, 0.28, 1.2)
    for k, (x, z, r) in enumerate([(-0.12, 1.68, 0.09), (0.0, 1.73, 0.11), (0.12, 1.68, 0.09)]):
        sphere((x, -0.15, z), (r, r * 0.7, r), R, name="comb")
    for s in (-1, 1):
        w = sphere((s * 0.6, 0.05, 0.75), (0.14, 0.34, 0.3), W, name="wing")
        w.rotation_euler = (math.radians(-10), s * math.radians(15), 0)
        tube((s * 0.2, 0.0, 0.25), (s * 0.2, -0.03, 0.08), 0.035, 0.03, Y)
        for k in (-1, 0, 1):
            tube((s * 0.2, -0.03, 0.05), (s * 0.2 + k * 0.08, -0.2, 0.03), 0.03, 0.025, Y)
    for k, a in enumerate((-30, 0, 30)):
        e = sphere((math.sin(math.radians(a)) * 0.15, 0.6, 1.0), (0.09, 0.08, 0.28), W, name="tail")
        e.rotation_euler = (math.radians(-30), math.radians(a), 0)
    frame(sc)
    return sc


def cerdito(o):
    sc = setup()
    P = mat("pig", (255, 170, 190), 0.5, sss=0.05)
    D = mat("pigdark", (240, 120, 150), 0.5)
    hc, hr = chibi(P, mat("pigbelly", (255, 195, 210), 0.5), D, br=(0.46, 0.42, 0.48))
    sc_c = (0, surf_y(hc, hr, 0, 1.25) - 0.02, 1.25)
    cyl(sc_c, 0.15, 0.12, P, rot=(math.radians(90), 0, 0), name="snout")
    for s in (-1, 1):
        sphere((s * 0.05, sc_c[1] - 0.06, 1.25), (0.03, 0.02, 0.045), D, name="nostril")
    eyes(hc, hr, 0.2, 1.45, 0.12, (90, 60, 40), P, lashes=True)
    put_mouth(hc, hr, 1.08, 0.2, o)
    cheeks(hc, hr, 0.34, 1.22)
    for s in (-1, 1):
        cone((s * 0.32, -0.05, 1.75), 0.14, 0.0, 0.3, P, rot=(math.radians(-25), s * math.radians(25), 0), name="ear")
    f = lambda t: (0.12 * math.cos(t * 4 * math.pi) * (1 - 0.4 * t), 0.38 + 0.15 * t, 0.62 + 0.12 * math.sin(t * 4 * math.pi) * (1 - 0.4 * t))
    chain(f, lambda t: 0.035, P, n=50)
    frame(sc)
    return sc


def elefante(o):
    sc = setup()
    G = mat("ele", (150, 175, 210), 0.55)
    P = mat("earin", (255, 175, 195), 0.6)
    hc, hr = chibi(G, mat("elebelly", (180, 200, 230), 0.55), G, hr=(0.55, 0.5, 0.48), br=(0.5, 0.45, 0.5),
                   foot_scale=(0.2, 0.24, 0.12))
    for s in (-1, 1):
        for k in range(3):
            sphere((s * 0.22 + (k - 1) * 0.07, -0.34, 0.05), (0.035, 0.02, 0.03), mat("toenail", (255, 250, 240), 0.4), name="nail")
        e = sphere((s * 0.62, 0.08, 1.38), (0.34, 0.06, 0.4), G, name="ear")
        e.rotation_euler = (0, 0, s * math.radians(-20))
        e = sphere((s * 0.6, 0.02, 1.38), (0.25, 0.03, 0.3), P, name="earin")
        e.rotation_euler = (0, 0, s * math.radians(-20))
    eyes(hc, hr, 0.22, 1.52, 0.13, (70, 110, 190), G, lashes=True)
    cheeks(hc, hr, 0.37, 1.3)
    # trompa corta que sube hacia un costado y deja ver la boca
    y0 = surf_y(hc, hr, 0, 1.34)
    f = bez((0, y0 + 0.06, 1.34), (0.0, y0 - 0.22, 1.3), (-0.3, y0 - 0.3, 1.32), (-0.38, y0 - 0.22, 1.62))
    chain(f, lambda t: 0.12 - 0.06 * t, G, n=50)
    torus(f(1.0), 0.05, 0.015, mat("trunktip", (130, 155, 195), 0.55), rot=(0, math.radians(90), 0), name="tiprim")
    put_mouth(hc, hr, 1.06, 0.26, o)
    frame(sc)
    return sc


def pinguino(o):
    sc = setup()
    K = mat("peng", (44, 62, 102), 0.3)
    W = mat("pengw", (255, 255, 255), 0.5)
    Or = mat("beak", (255, 160, 40), 0.35)
    bc, br = (0, 0, 0.85), (0.58, 0.5, 0.78)
    sphere(bc, br, K, name="body")
    sphere((0, -0.2, 0.7), (0.45, 0.35, 0.6), W, name="belly")
    for s in (-1, 1):  # ojos sobre la cabeza oscura (contraste) y carita blanca abajo
        lc, lr = (s * 0.16, -0.22, 1.08), (0.22, 0.26, 0.2)
        sphere(lc, lr, W, name="mask")
        eye(s * 0.2, surf_y(bc, br, s * 0.2, 1.33) + 0.025, 1.33, 0.11, (60, 110, 200), False, K)
        sphere((s * 0.3, surf_y(lc, lr, s * 0.3, 1.04) + 0.005, 1.04), (0.07, 0.03, 0.045), mat("cheek", PINK, 0.6), name="cheek")
    yb = surf_y((0.16, -0.22, 1.08), (0.22, 0.26, 0.2), 0, 1.12)
    beak((0, yb + 0.05, 1.14), 0.26, 0.11, Or, o)
    for s in (-1, 1):
        w = sphere((s * 0.58, 0.0, 0.8), (0.1, 0.2, 0.42), K, name="flipper")
        w.rotation_euler = (0, s * math.radians(-25), 0)
        sphere((s * 0.2, -0.18, 0.05), (0.15, 0.24, 0.06), Or, name="foot")
    frame(sc)
    return sc


def perrito(o):
    sc = setup()
    Br = mat("dog", (200, 140, 85), 0.6)
    W = mat("dogw", (255, 248, 235), 0.6)
    D = mat("dogear", (130, 80, 45), 0.6)
    hc, hr = chibi(Br, W, W)
    mc, mr = (0, -0.36, 1.2), (0.25, 0.17, 0.16)
    sphere(mc, mr, W, name="muzzle")
    patch(hc, hr, 20, 25, 0.17, W, flat=0.25)  # mancha blanca en un ojo
    eyes(hc, hr, 0.2, 1.42, 0.13, (110, 70, 40), Br)
    nose(mc, mr, 1.29, 0.075)
    put_mouth(mc, mr, 1.15, 0.2, o)
    cheeks(hc, hr, 0.35, 1.25)
    for s in (-1, 1):
        e = sphere((s * 0.48, 0.0, 1.45), (0.13, 0.08, 0.3), D, name="ear")
        e.rotation_euler = (0, s * math.radians(-20), 0)
    torus((0, 0, 1.02), 0.38, 0.045, mat("collar", (240, 60, 70), 0.4), name="collar")
    sphere((0, -0.4, 0.96), (0.06, 0.04, 0.06), mat("gold", (240, 195, 60), 0.25, metal=0.7), name="tag")
    chain(bez((0.0, 0.35, 0.5), (0.15, 0.7, 0.6), (0.2, 0.6, 0.95)), lambda t: 0.07 - 0.03 * t, Br, n=30)
    frame(sc)
    return sc


def gato(o):
    sc = setup()
    Or = mat("cat", (255, 160, 65), 0.55)
    C = mat("catw", (255, 240, 215), 0.6)
    S = mat("stripe", (215, 105, 35), 0.55)
    hc, hr = chibi(Or, C, C)
    mc, mr = (0, -0.37, 1.22), (0.21, 0.13, 0.13)
    sphere(mc, mr, C, name="muzzle")
    eyes(hc, hr, 0.2, 1.42, 0.13, (90, 180, 80), Or, lashes=True)
    nose(mc, mr, 1.28, 0.05, (255, 120, 150))
    put_mouth(mc, mr, 1.17, 0.18, o)
    cheeks(hc, hr, 0.36, 1.26)
    for s in (-1, 1):
        cone((s * 0.3, -0.02, 1.8), 0.17, 0.0, 0.32, Or, rot=(0, s * math.radians(20), 0), name="ear")
        cone((s * 0.3, -0.1, 1.77), 0.09, 0.0, 0.2, mat("earin", (255, 170, 180), 0.6), rot=(0, s * math.radians(20), 0), name="earin")
        for k in (-1, 1):
            p0 = (s * 0.15, mc[1] - 0.1, 1.2 + k * 0.03)
            tube(p0, (s * 0.45, mc[1] - 0.05, 1.22 + k * 0.08), 0.008, 0.006, mat("ink", INK, 0.5), caps=False)
    spots(hc, hr, S, [(0, 62, 1), (-12, 58, 0.8), (12, 58, 0.8), (-75, 15, 1), (75, 15, 1)], 0.08, flat=0.2)
    for el in (25, 0, -25):
        for az in (-70, 70):
            patch((0, 0, 0.6), (0.42, 0.38, 0.48), az, el, 0.12, S, flat=0.2, sx=0.4)
    f = bez((0.25, 0.3, 0.3), (0.9, 0.5, 0.2), (0.7, 0.5, 1.1))
    chain(f, lambda t: 0.065, Or, n=40)
    for t in (0.35, 0.6, 0.85):
        torus(f(t), 0.06, 0.02, S, rot=(0, math.radians(70), 0), name="ring")
    frame(sc)
    return sc


def pato(o):
    sc = setup()
    Y = mat("duck", (255, 215, 60), 0.5)
    Or = mat("bill", (255, 140, 30), 0.4)
    hc, hr = chibi(Y, None, Or, hz=1.3, br=(0.5, 0.45, 0.5), bz=0.62, arms=False, foot_scale=(0.17, 0.26, 0.06))
    zb = 1.2
    yb = surf_y(hc, hr, 0, zb)
    sphere((0, yb - 0.12, zb + 0.03), (0.22, 0.2, 0.07), Or, name="billU")
    lo = sphere((0, yb - 0.1 + (0.02 if o else 0), zb - 0.06 - (0.08 if o else 0)), (0.19, 0.18, 0.05), Or, name="billL")
    if o:
        lo.rotation_euler = (math.radians(-15), 0, 0)
        sphere((0, yb - 0.08, zb - 0.06), (0.15, 0.12, 0.07), mat("mouth", (95, 20, 40), 0.7), name="mouthin")
    eyes(hc, hr, 0.2, 1.42, 0.13, (60, 90, 170), Y)
    cheeks(hc, hr, 0.36, 1.27)
    for s in (-1, 1):
        w = sphere((s * 0.5, 0.05, 0.68), (0.12, 0.3, 0.28), Y, name="wing")
        w.rotation_euler = (math.radians(-20), s * math.radians(25), 0)
    for a in (-15, 15):
        cone((math.sin(math.radians(a)) * 0.06, 0.0, 1.76), 0.06, 0.0, 0.18, Y, rot=(0, math.radians(a), 0), name="tuft")
    cone((0, 0.5, 0.75), 0.15, 0.0, 0.3, Y, rot=(math.radians(-70), 0, 0), name="tail")
    frame(sc)
    return sc


def vaca(o):
    sc = setup()
    W = mat("cow", (255, 252, 248), 0.55)
    K = mat("cowspot", (50, 45, 55), 0.55)
    P = mat("cowsnout", (255, 175, 190), 0.5)
    hc, hr = chibi(W, None, K, hr=(0.52, 0.46, 0.44), br=(0.46, 0.42, 0.5))
    mc, mr = (0, -0.36, 1.15), (0.33, 0.2, 0.19)
    sphere(mc, mr, P, name="muzzle")
    for s in (-1, 1):
        sphere((s * 0.12, surf_y(mc, mr, s * 0.12, 1.2) + 0.01, 1.2), (0.045, 0.02, 0.03), mat("nostril", (200, 90, 120), 0.5), name="nostril")
    eyes(hc, hr, 0.2, 1.47, 0.12, (110, 70, 40), W, lashes=True)
    put_mouth(mc, mr, 1.06, 0.2, o)
    cheeks(hc, hr, 0.38, 1.3)
    patch(hc, hr, -25, 35, 0.17, K, flat=0.2)
    spots((0, 0, 0.6), (0.46, 0.42, 0.5), K, [(-50, 10, 1.4), (55, -20, 1.2), (90, 30, 1.2), (20, -35, 0.9)], 0.12, flat=0.2)
    for s in (-1, 1):
        cone((s * 0.28, 0.0, 1.78), 0.07, 0.02, 0.22, mat("horn", (255, 235, 180), 0.4), rot=(0, s * math.radians(25), 0), name="horn")
        e = sphere((s * 0.55, 0.0, 1.5), (0.18, 0.07, 0.09), W, name="ear")
        e.rotation_euler = (0, s * math.radians(-20), 0)
        sphere((s * 0.55, -0.04, 1.5), (0.12, 0.04, 0.05), P, name="earin")
    torus((0, 0, 1.0), 0.38, 0.04, mat("collar", (70, 140, 255), 0.4), name="collar")
    sphere((0, -0.43, 0.92), (0.08, 0.08, 0.09), mat("gold", (240, 195, 60), 0.25, metal=0.7), name="bell")
    tube((0.15, 0.36, 0.55), (0.3, 0.55, 0.25), 0.025, 0.02, W)
    sphere((0.3, 0.55, 0.22), (0.05, 0.05, 0.07), K, name="tailtuft")
    frame(sc)
    return sc


def oveja(o):
    sc = setup()
    W = mat("wool", (255, 253, 245), 0.9)
    F = mat("sheepface", (245, 220, 200), 0.55)
    D = mat("hoof", (70, 60, 75), 0.5)
    random.seed(7)
    for k in range(60):
        a = random.uniform(0, 2 * math.pi)
        z = random.uniform(-1, 1)
        rr = math.sqrt(1 - z * z)
        sphere((0.52 * rr * math.cos(a), 0.45 * rr * math.sin(a) + 0.05, 0.72 + 0.45 * z), (0.2, 0.2, 0.2), W, seg=24, name="wool")
    for s in (-1, 1):
        cyl((s * 0.22, -0.1, 0.18), 0.07, 0.3, F, name="leg")
        sphere((s * 0.22, -0.12, 0.06), (0.1, 0.14, 0.07), D, name="hoof")
    hc, hr = (0, -0.3, 1.25), (0.36, 0.3, 0.38)
    sphere(hc, hr, F, name="head")
    eyes(hc, hr, 0.15, 1.3, 0.11, (90, 60, 40), F, lashes=True)
    nose(hc, hr, 1.13, 0.04, (200, 110, 120))
    put_mouth(hc, hr, 1.04, 0.16, o)
    cheeks(hc, hr, 0.25, 1.15, 0.065)
    for s in (-1, 1):
        e = sphere((s * 0.42, -0.25, 1.35), (0.2, 0.06, 0.08), F, name="ear")
        e.rotation_euler = (0, s * math.radians(-25), 0)
    for (x, z) in [(-0.14, 1.6), (0.0, 1.66), (0.14, 1.6), (-0.07, 1.7), (0.08, 1.71)]:
        sphere((x, -0.3, z), (0.12, 0.12, 0.12), W, seg=24, name="tuft")
    frame(sc)
    return sc


def rana(o):
    sc = setup()
    G = mat("frog", (110, 210, 80), 0.4)
    L = mat("frogbelly", (215, 245, 160), 0.5)
    bc, br = (0, 0, 0.6), (0.62, 0.52, 0.55)
    sphere(bc, br, G, name="body")
    sphere((0, -0.3, 0.5), (0.45, 0.3, 0.38), L, name="belly")
    hc, hr = (0, -0.05, 1.05), (0.62, 0.48, 0.38)
    sphere(hc, hr, G, name="head")
    for s in (-1, 1):
        sphere((s * 0.28, -0.1, 1.35), (0.2, 0.18, 0.2), G, name="eyebump")
        eye(s * 0.28, -0.22, 1.4, 0.14, (40, 40, 40), False, G)
        sphere((s * 0.45, -0.2, 0.15), (0.22, 0.32, 0.1), G, name="leg")
        for k in (-1, 0, 1):
            sphere((s * 0.45 + k * 0.1, -0.48, 0.05), (0.06, 0.06, 0.04), G, name="toe")
        sphere((s * 0.3, -0.42, 0.42), (0.08, 0.1, 0.2), G, name="arm")
    cheeks(hc, hr, 0.42, 1.0, 0.09)
    put_mouth(hc, hr, 1.0, 0.36, o)
    frame(sc)
    return sc


def mono(o):
    sc = setup()
    Br = mat("monkey", (150, 95, 60), 0.6)
    F = mat("monkface", (250, 215, 175), 0.55)
    hc, hr = chibi(Br, F, F)
    for s in (-1, 1):
        sphere((s * 0.15, surf_y(hc, hr, s * 0.15, 1.42) + 0.08, 1.42), (0.18, 0.12, 0.2), F, name="facetop")
        sphere((s * 0.55, 0.0, 1.38), (0.17, 0.08, 0.17), Br, name="ear")
        sphere((s * 0.55, -0.05, 1.38), (0.11, 0.05, 0.11), F, name="earin")
    mc, mr = (0, -0.33, 1.18), (0.3, 0.2, 0.2)
    sphere(mc, mr, F, name="muzzle")
    eyes(hc, hr, 0.16, 1.42, 0.12, (100, 60, 30), F)
    for s in (-1, 1):
        sphere((s * 0.04, surf_y(mc, mr, s * 0.04, 1.27), 1.27), (0.02, 0.015, 0.02), mat("nostril", (130, 80, 50), 0.5), name="nostril")
    put_mouth(mc, mr, 1.12, 0.26, o)
    cheeks(hc, hr, 0.35, 1.25)
    chain(bez((0.2, 0.35, 0.4), (0.8, 0.5, 0.3), (0.6, 0.45, 1.1), (0.4, 0.4, 0.9)), lambda t: 0.05, Br, n=45)
    frame(sc)
    return sc


def leon(o):
    sc = setup()
    Y = mat("lion", (245, 185, 80), 0.55)
    Mn = mat("mane", (215, 110, 40), 0.85)
    C = mat("cream", (255, 235, 200), 0.6)
    hc, hr = chibi(Y, C, Y)
    for k in range(16):  # melena
        a = k / 16 * 2 * math.pi
        sphere((0.5 * math.sin(a), 0.1, 1.35 + 0.47 * math.cos(a)), (0.17, 0.15, 0.17), Mn, seg=24, name="mane")
    sphere((0, 0.15, 1.35), (0.5, 0.25, 0.5), Mn, name="maneback")
    sphere(hc, hr, Y, name="head2")
    for s in (-1, 1):
        sphere((s * 0.36, -0.05, 1.73), (0.12, 0.08, 0.12), Y, name="ear")
        sphere((s * 0.36, -0.1, 1.73), (0.07, 0.04, 0.07), mat("earin", (255, 170, 160), 0.6), name="earin")
    mc, mr = (0, -0.34, 1.2), (0.25, 0.16, 0.15)
    sphere(mc, mr, C, name="muzzle")
    eyes(hc, hr, 0.19, 1.43, 0.13, (180, 120, 40), Y)
    nose(mc, mr, 1.27, 0.065, (150, 80, 60))
    put_mouth(mc, mr, 1.15, 0.2, o)
    cheeks(hc, hr, 0.35, 1.25)
    f = bez((0.25, 0.3, 0.35), (0.85, 0.5, 0.2), (0.7, 0.45, 0.85))
    chain(f, lambda t: 0.05, Y, n=35)
    sphere(f(1), (0.11, 0.11, 0.13), Mn, name="tuft")
    frame(sc)
    return sc


def jirafa(o):
    sc = setup()
    Y = mat("giraffe", (250, 200, 85), 0.55)
    Br = mat("gspot", (200, 120, 55), 0.55)
    C = mat("cream", (255, 235, 200), 0.6)
    bc, br = (0, 0.05, 0.7), (0.42, 0.42, 0.42)
    sphere(bc, br, Y, name="body")
    for s in (-1, 1):
        cyl((s * 0.2, -0.05, 0.28), 0.09, 0.5, Y, name="leg")
        sphere((s * 0.2, -0.1, 0.06), (0.12, 0.15, 0.07), mat("hoof", (130, 80, 50), 0.5), name="hoof")
    tube((0, -0.05, 0.95), (0, -0.1, 1.6), 0.2, 0.16, Y)
    hc, hr = (0, -0.15, 1.95), (0.55, 0.5, 0.48)
    sphere(hc, hr, Y, name="head")
    mc, mr = (0, -0.5, 1.78), (0.36, 0.24, 0.23)
    sphere(mc, mr, C, name="muzzle")
    eyes(hc, hr, 0.22, 2.06, 0.15, (110, 70, 40), Y, lashes=True)
    put_mouth(mc, mr, 1.71, 0.24, o)
    for s in (-1, 1):
        sphere((s * 0.1, surf_y(mc, mr, s * 0.1, 1.85), 1.85), (0.035, 0.02, 0.028), mat("nostril", (150, 90, 60), 0.5), name="nostril")
    cheeks(hc, hr, 0.38, 1.86, 0.085)
    for s in (-1, 1):
        cyl((s * 0.18, -0.1, 2.48), 0.05, 0.24, Y, name="ossicone")
        sphere((s * 0.18, -0.1, 2.62), (0.08, 0.08, 0.08), Br, name="ossiball")
        e = sphere((s * 0.58, -0.1, 2.1), (0.22, 0.07, 0.09), Y, name="ear")
        e.rotation_euler = (0, s * math.radians(-20), 0)
    spots(hc, hr, Br, [(-55, 35, 1), (60, 40, 0.8), (90, 10, 1)], 0.08, flat=0.25)
    random.seed(2)
    for k in range(5):
        z = 1.05 + k * 0.11
        s = 1 if k % 2 else -1
        patch((0, -0.05 - 0.07 * (z - 0.95), z), (0.19, 0.19, 0.3), s * random.uniform(15, 60), 0, 0.06, Br, flat=0.3)
    spots(bc, br, Br, [(-40, 20, 1), (40, 10, 1.1), (0, -10, 0.9), (75, 35, 1), (-75, -15, 1), (110, 20, 1)], 0.09, flat=0.25)
    chain(bez((0.1, 0.42, 0.75), (0.25, 0.6, 0.55), (0.25, 0.6, 0.4)), lambda t: 0.03, Y, n=20)
    frame(sc)
    return sc


def pulpo(o):
    sc = setup()
    P = mat("octo", (200, 120, 235), 0.4)
    L = mat("octos", (240, 190, 255), 0.4)
    hc, hr = (0, 0.05, 1.05), (0.62, 0.58, 0.68)
    sphere(hc, hr, P, name="head")
    for k in range(8):
        a = k / 8 * 2 * math.pi + 0.2
        dx, dy = math.sin(a), -math.cos(a)
        curl = 1 if k % 2 else -1
        f = bez((dx * 0.3, dy * 0.25 + 0.05, 0.55), (dx * 0.65, dy * 0.55, 0.15), (dx * 0.85, dy * 0.7, 0.08),
                (dx * 0.85 + curl * dy * 0.15, dy * 0.7 - curl * dx * 0.15, 0.25))
        chain(f, lambda t: 0.14 - 0.1 * t, P, n=40)
    spots(hc, hr, L, [(-40, 45, 1), (35, 55, 0.8), (60, 25, 0.9), (-65, 20, 0.7), (0, 70, 0.8)], 0.08, flat=0.2)
    eyes(hc, hr, 0.22, 1.1, 0.15, (60, 120, 210), P, lashes=True)
    cheeks(hc, hr, 0.4, 0.92, 0.09)
    put_mouth(hc, hr, 0.82, 0.22, o)
    frame(sc)
    return sc


def ballena(o):
    sc = setup()
    B = mat("whale", (80, 140, 235), 0.4)
    L = mat("whalebelly", (200, 225, 255), 0.5)
    bc, br = (0, 0.1, 0.62), (0.75, 0.8, 0.62)
    sphere(bc, br, B, name="body")
    lc, lr = (0, -0.2, 0.42), (0.6, 0.6, 0.42)
    sphere(lc, lr, L, name="belly")
    eyes(bc, br, 0.3, 0.82, 0.14, (40, 80, 170), B, lashes=True)
    cheeks(bc, br, 0.5, 0.66, 0.09)
    # boca ancha justo en la línea entre la cara azul y la panza clara
    zm = 0.68
    ym = min(min(surf_y(bc, br, x, z), surf_y(lc, lr, x, z)) for x in (0, 0.2) for z in (0.5, 0.6, 0.7)) - 0.02
    mouth(0, ym, zm, 0.42, o)
    chain(bez((0, 0.75, 0.45), (0, 1.2, 0.5), (0, 1.25, 0.95)), lambda t: 0.22 - 0.12 * t, B, n=30)
    for s in (-1, 1):
        e = sphere((s * 0.22, 1.25, 1.1), (0.25, 0.08, 0.12), B, name="fluke")
        e.rotation_euler = (0, s * math.radians(-30), 0)
        e = sphere((s * 0.72, -0.1, 0.3), (0.22, 0.12, 0.07), B, name="fin")
        e.rotation_euler = (0, s * math.radians(-30), s * math.radians(20))
    W = mat("spout", (150, 210, 255), 0.1, alpha=0.85)
    tube((0, 0.0, 1.15), (0, 0.0, 1.5), 0.04, 0.06, W)
    for a in (-60, -25, 25, 60):
        sphere((0.25 * math.sin(math.radians(a)), 0.0, 1.55 - 0.1 * abs(a) / 60), (0.08, 0.08, 0.1), W, name="drop")
    frame(sc)
    return sc


def buho(o):
    sc = setup()
    Br = mat("owl", (165, 115, 75), 0.6)
    L = mat("owlface", (250, 225, 185), 0.55)
    Y = mat("beak", (255, 180, 40), 0.35)
    bc, br = (0, 0, 0.82), (0.6, 0.52, 0.78)
    sphere(bc, br, Br, name="body")
    sphere((0, -0.3, 0.58), (0.42, 0.3, 0.45), L, name="belly")
    for (x, z) in [(-0.15, 0.7), (0.15, 0.7), (0, 0.55), (-0.2, 0.45), (0.2, 0.45), (0, 0.85)]:
        torus((x, -0.6, z), 0.06, 0.015, mat("feather", (200, 150, 100), 0.6), rot=(math.radians(90), 0, 0), name="v", arc=(0, 0, -1))
    fc, fr = (0, -0.22, 1.12), (0.5, 0.3, 0.32)
    for s in (-1, 1):
        sphere((s * 0.21, -0.32, 1.13), (0.25, 0.2, 0.25), L, name="disc")
    eyes((0, -0.3, 1.13), (0.45, 0.24, 0.3), 0.21, 1.15, 0.16, (240, 160, 30), L)
    beak((0, -0.5, 0.97), 0.15, 0.07, Y, o, up=-30)
    cheeks(fc, fr, 0.38, 0.95, 0.07)
    for s in (-1, 1):
        cone((s * 0.36, -0.05, 1.6), 0.13, 0.0, 0.3, Br, rot=(0, s * math.radians(25), 0), name="tuft")
        w = sphere((s * 0.58, 0.05, 0.75), (0.13, 0.3, 0.45), Br, name="wing")
        w.rotation_euler = (0, s * math.radians(-12), 0)
        for k in (-1, 0, 1):
            sphere((s * 0.2 + k * 0.07, -0.35, 0.05), (0.04, 0.08, 0.04), Y, name="toe")
    frame(sc)
    return sc


def ardilla(o):
    sc = setup()
    Or = mat("squirrel", (220, 125, 60), 0.6)
    C = mat("cream", (255, 230, 195), 0.6)
    hc, hr = chibi(Or, C, Or, br=(0.4, 0.36, 0.46))
    mc, mr = (0, -0.35, 1.2), (0.21, 0.14, 0.13)
    sphere(mc, mr, C, name="muzzle")
    eyes(hc, hr, 0.19, 1.43, 0.13, (90, 55, 30), Or, lashes=True)
    nose(mc, mr, 1.27, 0.05, (120, 60, 50))
    put_mouth(mc, mr, 1.15, 0.18, o, tooth=True)
    cheeks(hc, hr, 0.35, 1.25)
    for s in (-1, 1):
        cone((s * 0.3, 0.0, 1.8), 0.13, 0.0, 0.3, Or, rot=(0, s * math.radians(15), 0), name="ear")
        cone((s * 0.32, 0.0, 1.98), 0.05, 0.0, 0.12, Or, rot=(0, s * math.radians(25), 0), name="eartuft")
    # cola grande y peluda
    f = bez((0.15, 0.35, 0.3), (0.95, 0.6, 0.4), (0.7, 0.55, 1.6), (0.35, 0.45, 1.5))
    chain(f, lambda t: 0.2 + 0.12 * math.sin(math.pi * t), Or, n=40)
    chain(bez((0.2, 0.42, 0.35), (0.98, 0.68, 0.45), (0.75, 0.62, 1.55), (0.4, 0.52, 1.5)),
          lambda t: 0.1 + 0.08 * math.sin(math.pi * t), C, n=30)
    # bellota en las manos
    ac = (0, -0.45, 0.62)
    sphere(ac, (0.1, 0.1, 0.12), mat("acorn", (180, 110, 50), 0.4), name="acorn")
    sphere((ac[0], ac[1], ac[2] + 0.08), (0.11, 0.11, 0.06), mat("cap", (120, 75, 40), 0.8), name="acorncap")
    frame(sc)
    return sc


def conejo(o):
    sc = setup()
    W = mat("bunny", (248, 245, 250), 0.6)
    P = mat("earin", (255, 170, 190), 0.6)
    hc, hr = chibi(W, mat("bunbelly", (255, 252, 255), 0.6), W, foot_scale=(0.15, 0.3, 0.08))
    mc, mr = (0, -0.36, 1.2), (0.2, 0.12, 0.12)
    sphere(mc, mr, W, name="muzzle")
    eyes(hc, hr, 0.2, 1.42, 0.13, (150, 90, 200), W, lashes=True)
    nose(mc, mr, 1.27, 0.05, (255, 120, 150))
    put_mouth(mc, mr, 1.15, 0.18, o, tooth=True)
    cheeks(hc, hr, 0.35, 1.25)
    for s in (-1, 1):
        e = sphere((s * 0.18, 0.0, 2.05), (0.12, 0.07, 0.42), W, name="ear")
        e.rotation_euler = (0, s * math.radians(12), 0)
        e = sphere((s * 0.19, -0.05, 2.05), (0.07, 0.03, 0.32), P, name="earin")
        e.rotation_euler = (0, s * math.radians(12), 0)
        sphere((s * 0.22, -0.4, 0.06), (0.06, 0.04, 0.04), P, name="toepad")
    sphere((0.0, 0.42, 0.45), (0.13, 0.13, 0.13), W, name="cottontail")
    frame(sc)
    return sc


def avestruz(o):
    sc = setup()
    K = mat("ostrich", (74, 64, 64), 0.6)
    Wt = mat("ostw", (255, 252, 248), 0.8)
    S = mat("ostskin", (250, 175, 175), 0.5)
    Or = mat("ostbeak", (255, 160, 60), 0.4)
    bc, br = (0, 0.1, 1.05), (0.55, 0.62, 0.48)
    sphere(bc, br, K, name="body")
    for (x, y, z, sx, sz, ry) in [(0.0, 0.7, 1.25, 0.18, 0.22, 0), (-0.2, 0.62, 1.2, 0.14, 0.18, -25),
                                   (0.2, 0.62, 1.2, 0.14, 0.18, 25)]:
        e = sphere((x, y, z), (sx, 0.14, sz), Wt, name="tailtuft")
        e.rotation_euler = (math.radians(-30), math.radians(ry), 0)
    for s in (-1, 1):
        w = sphere((s * 0.52, 0.15, 1.05), (0.12, 0.35, 0.22), K, name="wing")
        w.rotation_euler = (math.radians(-10), s * math.radians(15), 0)
        sphere((s * 0.6, 0.35, 0.95), (0.1, 0.14, 0.12), Wt, name="wingtuft")
        tube((s * 0.2, 0.05, 0.7), (s * 0.22, -0.02, 0.12), 0.09, 0.07, S)
        sphere((s * 0.22, -0.12, 0.07), (0.15, 0.22, 0.08), S, name="foot")
    chain(bez((0, -0.28, 1.25), (0, -0.4, 1.6), (0, -0.28, 1.9)), lambda t: 0.16 - 0.03 * t, S, n=30)
    hc, hr = (0, -0.3, 2.12), (0.46, 0.42, 0.42)
    sphere(hc, hr, S, name="head")
    for (x, z) in [(-0.1, 2.53), (0.08, 2.55), (0.0, 2.59)]:
        sphere((x, -0.3, z), (0.1, 0.1, 0.1), K, seg=24, name="fluff")
    eyes(hc, hr, 0.18, 2.2, 0.15, (90, 60, 40), S, lashes=True)
    cheeks(hc, hr, 0.33, 2.02, 0.08)
    yb = surf_y(hc, hr, 0, 1.98)
    sphere((0, yb - 0.08, 2.0 + (0.02 if o else 0)), (0.17, 0.16, 0.06), Or, name="beakU")
    if o:
        sphere((0, yb - 0.04, 1.9), (0.12, 0.08, 0.06), mat("mouth", (95, 20, 40), 0.7), name="mouthin")
        sphere((0, yb - 0.06, 1.88), (0.07, 0.05, 0.03), mat("tongue", (240, 100, 125), 0.5), name="tongue")
    lo = sphere((0, yb - 0.06, 1.93 - (0.08 if o else 0)), (0.15, 0.14, 0.05), Or, name="beakL")
    if o:
        lo.rotation_euler = (math.radians(-12), 0, 0)
    frame(sc)
    return sc


def cocodrilo(o):
    sc = setup()
    G = mat("croc", (90, 180, 90), 0.45)
    L = mat("crocbelly", (220, 240, 150), 0.5)
    hc, hr = chibi(G, None, G, hr=(0.46, 0.44, 0.36), hz=1.3, br=(0.45, 0.4, 0.5))
    sphere((0, -0.22, 0.58), (0.32, 0.22, 0.38), L, name="belly")
    sn, snr = (0, -0.45, 1.2), (0.32, 0.38, 0.16)
    sphere(sn, snr, G, name="snout")
    for s in (-1, 1):
        sphere((s * 0.08, -0.78, 1.3), (0.035, 0.03, 0.025), mat("nostril", (40, 90, 40), 0.5), name="nostril")
        sphere((s * 0.2, -0.15, 1.6), (0.16, 0.15, 0.16), G, name="eyebump")
        eye(s * 0.2, -0.27, 1.63, 0.13, (230, 170, 30), False, G)
    if o:
        sphere((0, -0.55, 1.08), (0.25, 0.3, 0.08), mat("mouth", (95, 20, 40), 0.7), name="mouthin")
        sphere((0, -0.55, 1.08), (0.15, 0.2, 0.05), mat("tongue", (240, 100, 125), 0.5), name="tongue")
        sphere((0, -0.45, 0.98), (0.3, 0.35, 0.08), G, name="jaw")
    else:
        t = torus((0, -0.45, 1.13), 0.3, 0.022, mat("ink", INK, 0.6), name="smile", arc=(0, -1, 0))
        t.scale = (1.1, 1.3, 1)
    for x in (-0.18, -0.06, 0.06, 0.18):
        cone((x, surf_y(sn, snr, x, 1.1) - 0.01 + (0.03 if o else 0), 1.1 - (0.0 if not o else 0.02)), 0.03, 0.0, 0.06,
             mat("tooth", (255, 255, 255), 0.3), rot=(math.pi, 0, 0), name="tooth")
    cheeks(hc, hr, 0.36, 1.28)
    f = bez((0.1, 0.3, 0.35), (0.5, 0.8, 0.2), (0.9, 0.7, 0.12))
    chain(f, lambda t: 0.2 - 0.17 * t, G, n=40)
    for t in (0.2, 0.45, 0.7):
        p = f(t)
        cone((p[0], p[1], p[2] + 0.2 - 0.17 * t), 0.05, 0.0, 0.1, mat("ridge", (60, 150, 70), 0.45), name="ridge")
    frame(sc)
    return sc


def colibri(o):
    sc = setup()
    G = mat("hummer", (40, 200, 160), 0.25, metal=0.2)
    P = mat("throat", (255, 70, 140), 0.3)
    Bk = mat("hbeak", (85, 85, 100), 0.4)
    bc, br = (0, 0, 0.9), (0.45, 0.42, 0.5)
    sphere(bc, br, G, name="body")
    sphere((0, -0.2, 0.68), (0.3, 0.25, 0.3), mat("hbelly", (220, 250, 235), 0.5), name="belly")
    eyes(bc, br, 0.17, 1.05, 0.13, (60, 60, 120), G, lashes=True)
    cheeks(bc, br, 0.3, 0.9, 0.07)
    patch(bc, br, 0, -20, 0.075, P, flat=0.3, sx=1.4)  # babero rosado chiquito
    yb = surf_y(bc, br, 0, 0.92)
    tip = (-0.3, yb - 0.17, 0.9)
    if o:
        tube((0, yb + 0.05, 0.94), (tip[0], tip[1], tip[2] + 0.04), 0.055, 0.025, Bk)
        tube((0, yb + 0.05, 0.89), (tip[0] * 0.8, tip[1] + 0.04, tip[2] - 0.05), 0.045, 0.022, Bk)
        sphere((0, yb - 0.01, 0.915), (0.05, 0.03, 0.04), mat("mouth", (95, 20, 40), 0.7), name="mouthin")
    else:
        tube((0, yb + 0.05, 0.92), tip, 0.055, 0.025, Bk)
    Wm = mat("hwing", (150, 230, 205), 0.1, alpha=0.75)
    for s in (-1, 1):
        w = sphere((s * 0.6, 0.15, 1.15), (0.5, 0.05, 0.18), Wm, name="wing")
        w.rotation_euler = (0, s * math.radians(-30), s * math.radians(-15))
        tube((s * 0.1, -0.05, 0.42), (s * 0.12, -0.08, 0.3), 0.02, 0.02, mat("ink", INK, 0.4))
        e = sphere((s * 0.12, 0.5, 0.45), (0.05, 0.08, 0.25), G, name="tail")
        e.rotation_euler = (math.radians(-35), s * math.radians(25), 0)
    cone((0, 0.0, 1.43), 0.06, 0.0, 0.15, G, name="crest")
    frame(sc)
    return sc


def koala(o):
    sc = setup()
    G = mat("koala", (165, 165, 180), 0.75)
    W = mat("koalaw", (250, 248, 252), 0.8)
    hc, hr = chibi(G, W, G, hr=(0.52, 0.46, 0.44))
    for s in (-1, 1):
        sphere((s * 0.52, 0.0, 1.62), (0.24, 0.1, 0.24), G, name="ear")
        sphere((s * 0.52, -0.06, 1.62), (0.16, 0.06, 0.16), W, name="earin")
    nc = (0, surf_y(hc, hr, 0, 1.3) - 0.05, 1.3)
    sphere(nc, (0.11, 0.09, 0.15), mat("knose", (55, 50, 65), 0.25), name="nose")
    sphere((nc[0] - 0.03, nc[1] - 0.08, 1.36), (0.025, 0.01, 0.03), mat("glint", (255, 255, 255), 0.1, emis=1.0), name="nglint")
    eyes(hc, hr, 0.24, 1.43, 0.12, (90, 60, 40), G)
    put_mouth(hc, hr, 1.08, 0.18, o)
    cheeks(hc, hr, 0.38, 1.22)
    # hojita de eucalipto en la mano
    tube((0.42, -0.3, 0.6), (0.5, -0.35, 1.0), 0.015, 0.012, mat("stem", (110, 140, 80), 0.6), caps=False)
    for (x, z, a) in [(0.47, 0.85, 40), (0.52, 0.98, -30), (0.44, 0.72, -40)]:
        e = sphere((x, -0.35, z), (0.08, 0.02, 0.04), mat("leaf", (120, 200, 140), 0.5), name="leaf")
        e.rotation_euler = (0, math.radians(a), 0)
    frame(sc)
    return sc


def castor(o):
    sc = setup()
    Br = mat("beaver", (165, 105, 60), 0.65)
    C = mat("cream", (240, 205, 160), 0.6)
    T = mat("btail", (95, 70, 60), 0.5)
    hc, hr = chibi(Br, C, T)
    for s in (-1, 1):
        sphere((s * 0.38, -0.02, 1.7), (0.1, 0.06, 0.1), Br, name="ear")
    mc, mr = (0, -0.36, 1.2), (0.24, 0.15, 0.15)
    sphere(mc, mr, C, name="muzzle")
    eyes(hc, hr, 0.19, 1.43, 0.13, (90, 55, 30), Br, lashes=False)
    nose(mc, mr, 1.28, 0.06, (70, 45, 40))
    put_mouth(mc, mr, 1.16, 0.2, o)
    for s in (-1, 1):
        y = surf_y(mc, mr, s * 0.035, 1.06)
        sphere((s * 0.037, y - 0.0, 1.03 - (0.05 if o else 0)), (0.035, 0.02, 0.06), mat("tooth", (255, 255, 255), 0.3), name="buck")
    cheeks(hc, hr, 0.35, 1.25)
    t = sphere((0.0, 0.6, 0.12), (0.3, 0.45, 0.06), T, name="tail")
    t.rotation_euler = (math.radians(-15), 0, math.radians(15))
    for k in range(4):
        cyl((0.0, 0.45 + k * 0.1, 0.17), 0.006, 0.4, mat("hatch", (70, 50, 45), 0.5), rot=(0, math.radians(90), math.radians(15)), name="hatch")
    frame(sc)
    return sc


def camaleon(o):
    sc = setup()
    G = mat("cham", (120, 215, 90), 0.35)
    Y = mat("chambelly", (240, 230, 110), 0.45)
    hc, hr = chibi(G, Y, G, hr=(0.46, 0.44, 0.42), br=(0.42, 0.38, 0.48))
    for k in range(5):  # cresta
        a = math.radians(-30 + k * 25)
        cone((0, 0.44 * math.sin(a) * -1 + 0.0, 1.35 + 0.42 * math.cos(a)), 0.07, 0.0, 0.14, mat("crest", (255, 140, 60), 0.4),
             rot=(-a, 0, 0), name="crest")
    for s in (-1, 1):
        sphere((s * 0.27, -0.18, 1.5), (0.19, 0.18, 0.19), G, name="eyeturret")
        eye(s * 0.27, -0.29, 1.52, 0.14, (230, 120, 30), False, G)
    spots(hc, hr, mat("champ", (60, 180, 230), 0.4), [(-60, 10, 1), (65, 20, 0.8), (40, 60, 0.7)], 0.07, flat=0.2)
    spots((0, 0, 0.6), (0.42, 0.38, 0.48), mat("champ", (60, 180, 230), 0.4), [(-60, 10, 1), (60, -10, 1), (90, 30, 0.8)], 0.08, flat=0.2)
    cheeks(hc, hr, 0.33, 1.22)
    put_mouth(hc, hr, 1.17, 0.3, o)
    def spiral(t):
        if t < 0.4:
            u = t / 0.4
            return (0.25 + 0.4 * u, 0.4 + 0.05 * u, 0.3)
        u = (t - 0.4) / 0.6
        R = 0.2 * (1 - 0.6 * u)
        a = u * 1.8 * math.pi
        return (0.65 + R * math.sin(a), 0.45, 0.5 - R * math.cos(a))
    chain(spiral, lambda t: 0.09 - 0.06 * t, G, n=60)
    frame(sc)
    return sc


def caracol(o):
    sc = setup()
    Y = mat("snail", (200, 230, 120), 0.35)
    S = mat("shell", (255, 140, 90), 0.4)
    S2 = mat("shell2", (255, 200, 110), 0.4)
    body = sphere((0, -0.15, 0.2), (0.35, 0.85, 0.2), Y, name="foot")
    tube((0, -0.6, 0.25), (0, -0.7, 0.85), 0.2, 0.18, Y)
    hc, hr = (0, -0.72, 0.95), (0.27, 0.24, 0.25)
    sphere(hc, hr, Y, name="head")
    for s in (-1, 1):
        tube((s * 0.08, -0.72, 1.15), (s * 0.18, -0.75, 1.42), 0.03, 0.025, Y)
        eye(s * 0.18, -0.77, 1.48, 0.1, (60, 120, 60), False, Y)
    cheeks(hc, hr, 0.18, 0.9, 0.06)
    put_mouth(hc, hr, 0.85, 0.16, o)
    # caparazón en espiral: toros que se achican
    for k in range(4):
        R = 0.42 * (0.68 ** k)
        r = 0.18 * (0.68 ** k)
        cx = 0.0 + 0.02 * k
        torus((0, 0.25, 0.65 + 0.0 * k), R, r, S if k % 2 == 0 else S2, rot=(0, math.radians(90), 0), name="shellring")
        bpy.context.object.location.x = 0.03 * k - 0.02
    sphere((0.0, 0.25, 0.65), (0.2, 0.42, 0.42), S2, name="shellcore")
    frame(sc)
    return sc


def murcielago(o):
    sc = setup()
    P = mat("bat", (150, 110, 205), 0.5)
    L = mat("batbelly", (205, 180, 240), 0.55)
    D = mat("batwing", (110, 80, 170), 0.55)
    hc, hr = chibi(P, L, D, hr=(0.48, 0.44, 0.42), br=(0.36, 0.32, 0.42), arms=False)
    eyes(hc, hr, 0.19, 1.42, 0.14, (140, 90, 50), P, lashes=True)
    cheeks(hc, hr, 0.34, 1.24)
    put_mouth(hc, hr, 1.15, 0.2, o, tooth=True)
    sphere((0, surf_y(hc, hr, 0, 1.28) + 0.01, 1.28), (0.05, 0.03, 0.035), mat("nose", (255, 140, 170), 0.3), name="nose")
    for s in (-1, 1):
        cone((s * 0.3, 0.0, 1.82), 0.16, 0.0, 0.38, P, rot=(0, s * math.radians(22), 0), name="ear")
        cone((s * 0.3, -0.08, 1.8), 0.09, 0.0, 0.26, mat("earin", (255, 170, 200), 0.6), rot=(0, s * math.radians(22), 0), name="earin")
        # ala de murciélago: malla plana con borde festoneado, con grosor y suavizada
        pts2 = [(0.25, 1.0), (0.6, 1.12), (1.05, 1.22), (0.98, 0.95), (0.86, 0.72), (0.74, 0.86), (0.6, 0.58),
                (0.47, 0.72), (0.3, 0.5)]
        verts = [(s * x, 0.12, z) for (x, z) in pts2]
        me = bpy.data.meshes.new("batwing")
        me.from_pydata(verts, [], [tuple(range(len(verts)))])
        ob = bpy.data.objects.new("batwing", me)
        bpy.context.scene.collection.objects.link(ob)
        ob.modifiers.new("sol", "SOLIDIFY").thickness = 0.05
        ob.data.materials.append(D)
        tube((s * 0.3, 0.09, 1.0), (s * 1.05, 0.09, 1.22), 0.04, 0.025, P)
        for (x, z) in [(0.86, 0.72), (0.6, 0.58)]:
            tube((s * 0.7, 0.1, 1.12), (s * x, 0.1, z), 0.02, 0.015, P)
    frame(sc)
    return sc


def pez(o):
    sc = setup()
    Or = mat("fish", (255, 120, 60), 0.3)
    W = mat("fishw", (255, 255, 255), 0.4)
    Ln = mat("ink", INK, 0.5)
    Bl = mat("fishfin", (80, 170, 255), 0.35)
    bc, br = (0, 0, 0.75), (0.5, 0.62, 0.6)
    sphere(bc, br, Or, name="body")
    for y, half in ((0.12, 0.075), (0.42, 0.06)):  # bandas blancas con borde oscuro
        k = math.sqrt(1 - (y / br[1]) ** 2)
        sphere((0, y, 0.75), (br[0] * k * 1.03, half + 0.018, br[2] * k * 1.03), Ln, name="bandline")
        sphere((0, y, 0.75), (br[0] * k * 1.055, half, br[2] * k * 1.055), W, name="band")
    eyes(bc, br, 0.22, 0.9, 0.15, (40, 90, 200), Or, lashes=True)
    cheeks(bc, br, 0.33, 0.7, 0.08)
    put_mouth(bc, br, 0.6, 0.22, o)
    for s in (-1, 1):
        e = sphere((s * 0.48, 0.0, 0.55), (0.06, 0.18, 0.12), Bl, name="pfin")
        e.rotation_euler = (math.radians(30), 0, s * math.radians(-30))
        e = sphere((0, 0.78, 0.75 + s * 0.17), (0.06, 0.26, 0.2), Bl, name="tail")
        e.rotation_euler = (math.radians(s * -35), 0, 0)
    sphere((0, 0.62, 0.75), (0.08, 0.1, 0.1), Bl, name="tailroot")
    e = sphere((0, 0.15, 1.35), (0.05, 0.35, 0.18), Bl, name="dorsal")
    e.rotation_euler = (math.radians(-10), 0, 0)
    # girar el pez un poco para que se vea de costado (bandas y cola)
    bpy.context.view_layer.update()
    from mathutils import Matrix
    R = Matrix.Rotation(math.radians(-25), 4, "Z")
    for ob in list(sc.objects):
        if ob.type == "MESH":
            ob.matrix_world = R @ ob.matrix_world
    W2 = mat("bubble", (190, 230, 255), 0.05, alpha=0.6)
    for (x, z, r) in [(-0.6, 1.3, 0.07), (-0.7, 1.5, 0.05)]:
        sphere((x, -0.3, z), (r, r, r), W2, name="bubble")
    frame(sc)
    return sc


def braquiosaurio(o):
    sc = setup()
    T = mat("brachio", (110, 190, 225), 0.5)
    L = mat("brbelly", (210, 240, 245), 0.55)
    Sp = mat("brspot", (70, 140, 200), 0.5)
    bc, br = (0, 0.15, 0.7), (0.55, 0.6, 0.45)
    sphere(bc, br, T, name="body")
    patch(bc, br, 0, -10, 0.3, L, flat=0.3, sx=0.85)  # panza ovalada como la del elenco
    for (x, y) in [(-0.3, -0.15), (0.3, -0.15), (-0.3, 0.45), (0.3, 0.45)]:
        cyl((x, y, 0.25), 0.13, 0.5, T, name="leg")
        sphere((x, y - 0.03, 0.06), (0.15, 0.17, 0.07), T, name="foot")
    chain(bez((0, -0.2, 0.9), (0, -0.4, 1.4), (0, -0.25, 1.75)), lambda t: 0.21 - 0.05 * t, T, n=40)
    hc, hr = (0, -0.32, 2.0), (0.58, 0.55, 0.48)
    sphere(hc, hr, T, name="head")
    eyes(hc, hr, 0.23, 2.1, 0.17, (110, 70, 40), T, lashes=True)
    cheeks(hc, hr, 0.4, 1.9, 0.09)
    put_mouth(hc, hr, 1.82, 0.3, o)
    for s in (-1, 1):
        sphere((s * 0.08, surf_y(hc, hr, s * 0.08, 1.98) + 0.005, 1.98), (0.03, 0.02, 0.02), mat("nostril", (60, 120, 170), 0.5), name="nostril")
    chain(bez((0.1, 0.7, 0.75), (0.5, 1.1, 0.5), (0.8, 1.0, 0.2)), lambda t: 0.18 - 0.15 * t, T, n=40)
    spots(bc, br, Sp, [(-60, 40, 1), (60, 40, 0.9), (90, 20, 1), (-90, 10, 0.8), (0, 80, 1)], 0.1, flat=0.2)
    spots(hc, hr, Sp, [(0, 70, 0.9), (-45, 55, 0.7), (50, 50, 0.6)], 0.1, flat=0.2)
    frame(sc)
    return sc


def triceratops(o):
    sc = setup()
    P = mat("trike", (175, 145, 235), 0.5)
    Y = mat("frill", (255, 205, 80), 0.45)
    H = mat("horn", (255, 245, 220), 0.35)
    hc, hr = chibi(P, mat("trbelly", (225, 210, 250), 0.5), P, hr=(0.5, 0.46, 0.42), br=(0.48, 0.42, 0.5))
    fr = sphere((0, 0.15, 1.55), (0.72, 0.1, 0.55), Y, name="frill")
    fr.rotation_euler = (math.radians(-20), 0, 0)
    for k in range(9):
        a = math.radians(-80 + k * 20)
        sphere((0.72 * math.sin(a), 0.15 + 0.2 * math.cos(a) * 0.3, 1.55 + 0.55 * math.cos(a)), (0.08, 0.08, 0.08),
               mat("frilldot", (255, 120, 120), 0.4), name="frilldot")
    sphere(hc, hr, P, name="head2")
    mc, mr = (0, -0.35, 1.2), (0.26, 0.18, 0.17)
    sphere(mc, mr, P, name="muzzle")
    cone((0, surf_y(mc, mr, 0, 1.3) + 0.03, 1.38), 0.06, 0.0, 0.16, H, rot=(math.radians(20), 0, 0), name="nosehorn")
    for s in (-1, 1):
        cone((s * 0.22, -0.3, 1.78), 0.07, 0.0, 0.3, H, rot=(math.radians(20), s * math.radians(15), 0), name="horn")
    eyes(hc, hr, 0.2, 1.44, 0.13, (90, 170, 80), P, lashes=False)
    put_mouth(mc, mr, 1.14, 0.22, o)
    cheeks(hc, hr, 0.36, 1.26)
    spots((0, 0, 0.6), (0.48, 0.42, 0.5), mat("trspot", (140, 110, 210), 0.5), [(-60, 20, 1), (60, 10, 1), (90, 35, 0.8)], 0.09, flat=0.2)
    chain(bez((0.1, 0.35, 0.35), (0.5, 0.8, 0.2), (0.8, 0.7, 0.1)), lambda t: 0.18 - 0.15 * t, P, n=35)
    frame(sc)
    return sc


def flamenco(o):
    sc = setup()
    P = mat("flamingo", (255, 140, 180), 0.5)
    D = mat("flamdark", (240, 100, 150), 0.5)
    K = mat("flamink", (50, 45, 60), 0.4)
    Bw = mat("flambeak", (255, 225, 230), 0.4)
    bc, br = (0, 0.1, 1.2), (0.42, 0.55, 0.38)
    sphere(bc, br, P, name="body")
    for s in (-1, 1):
        w = sphere((s * 0.38, 0.15, 1.25), (0.12, 0.4, 0.25), D, name="wing")
        w.rotation_euler = (math.radians(-15), s * math.radians(15), 0)
    for a in (-20, 0, 20):
        e = sphere((0.12 * math.sin(math.radians(a)), 0.65, 1.35), (0.08, 0.2, 0.07), D, name="tail")
        e.rotation_euler = (math.radians(-25), math.radians(a), 0)
    tube((0.05, 0.05, 0.9), (0.05, -0.02, 0.08), 0.045, 0.04, P)
    sphere((0.05, -0.12, 0.04), (0.11, 0.17, 0.045), D, name="foot")
    tube((-0.12, 0.05, 0.9), (-0.14, 0.0, 0.62), 0.045, 0.04, P)
    tube((-0.14, 0.0, 0.62), (0.02, 0.0, 0.72), 0.04, 0.035, P)
    chain(bez((0, -0.25, 1.3), (0, -0.55, 1.65), (0, -0.25, 1.95)), lambda t: 0.13, P, n=30)
    hc, hr = (0, -0.3, 2.2), (0.5, 0.46, 0.45)
    sphere(hc, hr, P, name="head")
    eyes(hc, hr, 0.2, 2.3, 0.16, (90, 60, 40), P, lashes=True)
    cheeks(hc, hr, 0.36, 2.12, 0.085)
    # pico curvo blanco con punta negra; en _1 se abre la parte de abajo
    yb = surf_y(hc, hr, 0, 2.08)
    up = bez((0, yb + 0.05, 2.1), (0, yb - 0.2, 2.12), (0, yb - 0.32, 1.9))
    chain(lambda t: up(t * 0.7), lambda t: 0.09 - 0.03 * t, Bw, n=30)
    chain(lambda t: up(0.7 + 0.3 * t), lambda t: 0.06 - 0.03 * t, K, n=15)
    if o:
        sphere((0, yb - 0.08, 1.98), (0.09, 0.08, 0.07), mat("mouth", (95, 20, 40), 0.7), name="mouthin")
        lo = bez((0, yb + 0.05, 2.0), (0, yb - 0.12, 1.88), (0, yb - 0.2, 1.74))
    else:
        lo = bez((0, yb + 0.05, 2.04), (0, yb - 0.15, 2.04), (0, yb - 0.27, 1.88))
    chain(lo, lambda t: 0.065 - 0.03 * t, Bw, n=25)
    for k, (x, z) in enumerate([(-0.05, 2.66), (0.06, 2.68)]):
        cone((x, -0.3, z), 0.06, 0.0, 0.2, D, rot=(0, math.radians(-20 + 40 * k), 0), name="crest")
    frame(sc)
    return sc


def hormiga(o):
    sc = setup()
    R = mat("ant", (215, 75, 60), 0.35)
    D = mat("antdark", (165, 50, 45), 0.4)
    K = mat("ink", INK, 0.5)
    sphere((0, 0.42, 0.5), (0.36, 0.42, 0.36), R, name="abdomen")
    sphere((0, 0.05, 0.62), (0.3, 0.28, 0.36), R, name="thorax")
    sphere((0, -0.15, 0.6), (0.2, 0.12, 0.25), mat("antbelly", (245, 150, 120), 0.4), name="belly")
    for s in (-1, 1):  # dos patitas con zapatillas y cuatro bracitos cortos
        tube((s * 0.15, 0.0, 0.35), (s * 0.2, -0.05, 0.12), 0.06, 0.055, D)
        sphere((s * 0.2, -0.12, 0.07), (0.13, 0.19, 0.08), mat("antshoe", (255, 210, 60), 0.4), name="shoe")
        for z, a in ((0.8, 30), (0.6, -10)):
            tube((s * 0.25, -0.05, z), (s * 0.45, -0.15, z - 0.08), 0.045, 0.04, D)
            sphere((s * 0.47, -0.16, z - 0.09), (0.06, 0.06, 0.06), D, name="hand")
    hc, hr = (0, -0.15, 1.25), (0.46, 0.42, 0.42)
    sphere(hc, hr, R, name="head")
    eyes(hc, hr, 0.18, 1.32, 0.14, (60, 40, 30), R, lashes=False)
    cheeks(hc, hr, 0.32, 1.15)
    put_mouth(hc, hr, 1.07, 0.2, o)
    for s in (-1, 1):
        f = bez((s * 0.12, -0.15, 1.6), (s * 0.15, -0.2, 1.9), (s * 0.35, -0.3, 1.95))
        chain(f, lambda t: 0.022, K, n=20)
        sphere(f(1), (0.055, 0.055, 0.055), D, name="antball")
    frame(sc)
    return sc


def perezoso(o):
    sc = setup()
    Br = mat("sloth", (175, 140, 105), 0.8)
    F = mat("slothface", (245, 225, 195), 0.6)
    D = mat("slotheye", (115, 85, 65), 0.6)
    hc, hr = chibi(Br, mat("slothbelly", (200, 170, 135), 0.8), Br, hz=1.3, br=(0.46, 0.4, 0.5))
    fc, fr = (0, -0.18, 1.28), (0.4, 0.32, 0.34)
    sphere(fc, fr, F, name="face")
    for s in (-1, 1):  # antifaz típico del perezoso
        e = patch(fc, fr, s * 28, 5, 0.15, D, flat=0.3, sx=1.5)
    eyes(fc, fr, 0.16, 1.32, 0.11, (70, 45, 30), D)
    nose(fc, fr, 1.2, 0.06, (80, 55, 45))
    put_mouth(fc, fr, 1.1, 0.18, o)
    cheeks(fc, fr, 0.3, 1.16, 0.07)
    for s in (-1, 1):  # brazos largos que abrazan una ramita
        tube((s * 0.42, -0.05, 0.85), (s * 0.15, -0.42, 0.65), 0.09, 0.08, Br)
        for k in (-1, 0, 1):
            cone((s * 0.13 + k * 0.03, -0.5, 0.6 + k * 0.03), 0.02, 0.0, 0.1, mat("claw", (240, 230, 210), 0.4),
                 rot=(math.radians(150), 0, 0), name="claw")
    tube((-0.6, -0.48, 0.62), (0.6, -0.48, 0.66), 0.04, 0.04, mat("branch", (130, 90, 55), 0.7))
    for x in (-0.45, 0.48):
        e = sphere((x, -0.5, 0.75), (0.08, 0.02, 0.05), mat("leaf", (110, 200, 110), 0.5), name="leaf")
        e.rotation_euler = (0, math.radians(30 if x > 0 else -30), 0)
    frame(sc)
    return sc


def tortuga(o):
    sc = setup()
    SK = mat("turtle", (175, 205, 85), 0.5)
    SH = mat("tshell", (215, 135, 55), 0.4)
    PL = mat("tplate", (175, 95, 40), 0.45)
    RIM = mat("trim", (250, 205, 120), 0.45)
    PS = mat("plastron", (245, 225, 160), 0.5)
    # caparazón en domo, detrás del cuerpo, con placas hexagonales y borde
    shc, shr = (0, 0.28, 0.72), (0.66, 0.48, 0.66)
    sphere(shc, shr, SH, name="shell")
    for (az, el) in [(180, 0), (135, 30), (-135, 30), (90, 10), (-90, 10), (180, 55), (120, -20), (-120, -20),
                     (90, 50), (-90, 50), (60, 25), (-60, 25)]:
        p = patch(shc, shr, az, el, 0.16, PL, flat=0.2)
        p.data.materials.clear()
        p.data.materials.append(PL)
    t = torus((0, 0.08, 0.72), 0.64, 0.06, RIM, rot=(math.radians(90), 0, 0), name="rim")
    t.scale = (1.0, 1.0, 1.0)
    # cuerpo con peto (plastrón) de placas en vez de panza ovalada
    sphere((0, 0, 0.62), (0.4, 0.34, 0.46), SK, name="body")
    pc, pr = (0, -0.18, 0.6), (0.34, 0.2, 0.4)
    sphere(pc, pr, PS, name="plastron")
    for z in (0.45, 0.62, 0.79):
        w = 0.32 * math.sqrt(max(0.1, 1 - ((z - 0.6) / 0.4) ** 2))
        tube((-w, surf_y(pc, pr, -w * 0.9, z) + 0.01, z), (w, surf_y(pc, pr, w * 0.9, z) + 0.01, z), 0.012, 0.012,
             mat("plline", (215, 185, 110), 0.5), caps=False)
    tube((0, surf_y(pc, pr, 0, 0.32) + 0.01, 0.32), (0, surf_y(pc, pr, 0, 0.9) + 0.01, 0.9), 0.012, 0.012,
         mat("plline", (215, 185, 110), 0.5), caps=False)
    for s in (-1, 1):
        o_ = sphere((s * 0.42, -0.1, 0.72), (0.11, 0.11, 0.2), SK, name="arm")
        o_.rotation_euler = (0, s * math.radians(-25), 0)
        sphere((s * 0.22, -0.12, 0.09), (0.16, 0.22, 0.09), SK, name="foot")
    hc, hr = (0, -0.1, 1.36), (0.44, 0.4, 0.38)
    sphere(hc, hr, SK, name="head")
    mc, mr = (0, -0.36, 1.25), (0.25, 0.16, 0.15)
    sphere(mc, mr, SK, name="snout")
    eyes(hc, hr, 0.18, 1.44, 0.13, (110, 70, 30), SK)
    cheeks(hc, hr, 0.33, 1.28)
    for s in (-1, 1):
        sphere((s * 0.05, surf_y(mc, mr, s * 0.05, 1.32), 1.32), (0.02, 0.015, 0.015), mat("nostril", (110, 140, 50), 0.5), name="nostril")
    put_mouth(mc, mr, 1.2, 0.2, o)
    # gorrita roja con visera
    cap = sphere((0, -0.06, 1.62), (0.36, 0.34, 0.2), mat("capred", (235, 60, 70), 0.45), name="cap")
    sphere((0, -0.42, 1.6), (0.22, 0.16, 0.03), mat("capred", (235, 60, 70), 0.45), name="visor")
    sphere((0, -0.06, 1.82), (0.05, 0.05, 0.04), mat("capbtn", (255, 255, 255), 0.4), name="capbtn")
    frame(sc)
    return sc


def abeja(o):
    sc = setup()
    A = mat("bee", (255, 160, 40), 0.4)
    K = mat("beebrown", (110, 60, 35), 0.45)
    bc, br = (0, 0, 0.82), (0.5, 0.48, 0.72)
    sphere(bc, br, stripes_mat("beestr", (255, 160, 40), (110, 60, 35), freq=11.0, split=0.62), name="body")
    fc, fr = (0, -0.2, 1.05), (0.42, 0.34, 0.36)
    sphere(fc, fr, A, name="face")
    eyes(fc, fr, 0.17, 1.12, 0.13, (110, 60, 30), A, lashes=True)
    cheeks(fc, fr, 0.3, 0.98)
    put_mouth(fc, fr, 0.9, 0.2, o)
    Wm = mat("wingp", (255, 215, 235), 0.1, alpha=0.65)
    for s in (-1, 1):
        w = sphere((s * 0.45, 0.3, 1.35), (0.3, 0.05, 0.22), Wm, name="wing")
        w.rotation_euler = (0, s * math.radians(35), 0)
        w = sphere((s * 0.4, 0.32, 1.05), (0.2, 0.05, 0.14), Wm, name="wing2")
        w.rotation_euler = (0, s * math.radians(-15), 0)
        # antenas con espiral en la punta
        f = bez((s * 0.12, -0.05, 1.48), (s * 0.15, -0.1, 1.72), (s * 0.3, -0.12, 1.78))
        chain(f, lambda t: 0.02, K, n=20)
        torus(f(1), 0.05, 0.02, K, rot=(math.radians(90), 0, 0), name="curl")
        sphere((s * 0.18, -0.12, 0.08), (0.1, 0.14, 0.07), K, name="foot")
        sphere((s * 0.46, -0.1, 0.8), (0.08, 0.08, 0.14), A, name="arm")
    # florcita en la cabeza
    fz = 1.56
    for k in range(6):
        a = k / 6 * 2 * math.pi
        sphere((0.1 + 0.1 * math.cos(a), -0.1, fz + 0.1 * math.sin(a)), (0.075, 0.04, 0.075), mat("fpetal", (255, 255, 255), 0.4), name="petal")
    sphere((0.1, -0.14, fz), (0.06, 0.04, 0.06), mat("fcenter", (255, 90, 140), 0.4), name="fcenter")
    cone((0, 0.5, 0.6), 0.07, 0.0, 0.16, K, rot=(math.radians(-80), 0, 0), name="stinger")
    frame(sc)
    return sc


def mariposa(o):
    sc = setup()
    B = mat("bfbody", (120, 90, 200), 0.45)
    W1 = mat("bfwing", (255, 150, 60), 0.4)
    W2 = mat("bfwing2", (255, 90, 160), 0.4)
    Dt = mat("bfdot", (255, 240, 120), 0.4)
    sphere((0, 0, 0.6), (0.18, 0.18, 0.45), B, name="body")
    hc, hr = (0, -0.05, 1.2), (0.32, 0.3, 0.3)
    sphere(hc, hr, B, name="head")
    eyes(hc, hr, 0.12, 1.25, 0.1, (60, 40, 120), B, lashes=True)
    cheeks(hc, hr, 0.21, 1.13, 0.055)
    put_mouth(hc, hr, 1.07, 0.15, o)
    for s in (-1, 1):
        w = sphere((s * 0.55, 0.15, 1.0), (0.5, 0.04, 0.42), W1, name="wingU")
        w.rotation_euler = (0, s * math.radians(-25), s * math.radians(-25))
        w = sphere((s * 0.42, 0.17, 0.45), (0.33, 0.04, 0.3), W2, name="wingL")
        w.rotation_euler = (0, s * math.radians(25), s * math.radians(-25))
        for (x, z, r) in [(0.65, 1.1, 0.12), (0.45, 0.85, 0.07), (0.45, 0.45, 0.09)]:
            d = sphere((s * x, 0.08, z), (r, 0.03, r), Dt, name="wdot")
        f = bez((s * 0.08, -0.05, 1.45), (s * 0.12, -0.1, 1.7), (s * 0.28, -0.15, 1.78))
        chain(f, lambda t: 0.018, B, n=20)
        sphere(f(1), (0.05, 0.05, 0.05), W2, name="antball")
    frame(sc)
    return sc


ANIMALS = {
    "Guepardo": guepardo, "Canguro": canguro, "Mariquita": mariquita, "Pájaro": pajaro, "Gallina": gallina,
    "Cerdito": cerdito, "Elefante": elefante, "Pingüino": pinguino, "Perrito": perrito, "Gato": gato,
    "Pato": pato, "Vaca": vaca, "Oveja": oveja, "Rana": rana, "Mono": mono, "León": leon, "Jirafa": jirafa,
    "Pulpo": pulpo, "Ballena": ballena, "Búho": buho, "Ardilla": ardilla, "Conejo": conejo,
    "Avestruz": avestruz, "Cocodrilo": cocodrilo, "Colibrí": colibri, "Koala": koala, "Castor": castor,
    "Camaleón": camaleon, "Caracol": caracol, "Murciélago": murcielago, "Pez": pez, "Braquiosaurio": braquiosaurio,
    "Tricerátops": triceratops, "Flamenco": flamenco, "Hormiga": hormiga, "Perezoso": perezoso, "Tortuga": tortuga,
    "Abeja": abeja, "Mariposa": mariposa,
}


def main():
    for name in (ONLY or list(ANIMALS)):  # en el orden pedido
        fn = ANIMALS[name]
        for o in ((0, 1) if BOTH else (0,)):
            p = os.path.join(OUT, f"{name}_{o}.png")
            if os.path.exists(p):
                continue
            sc = fn(o)
            if TEST:  # prueba rápida: mitad de resolución
                sc.render.resolution_x = sc.render.resolution_y = 450
                sc.eevee.taa_render_samples = 16
            M.render(sc, p)
            print("OK", name, o, flush=True)


if __name__ == "__main__":
    main()
