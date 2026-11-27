"""Variantes 3D de Toto con los objetos de la historia modelados JUNTO al personaje (una sola escena, misma luz,
sombras de contacto y oclusión), para no pegar objetos 2D encima del sprite.

Uso: python3 variantes.py CARPETA_SALIDA [variante ...]
Variantes: sucio (fideos, salsa, albóndigas, media y barro), banera (en la bañera con espuma y patito),
cama (escondido bajo la frazada) y limpio (pelo esponjoso y brillitos).
Cada variante se renderiza en sus 4 estados: TOTO-<variante>_<boca>_<ojos cerrados>.png.
Toto conserva la escala de su sprite normal (360 px por unidad de Blender, igual que TOTO_*.png de 900x900 con
ortho 2.5): la imagen se agranda para que entre todo, en vez de achicar al personaje. Además se escribe
TOTO-variantes.json con el tamaño de cada sprite, el centro del cuerpo de Toto y la línea del piso en píxeles.
"""
import json
import math
import os
import random

import bpy
import numpy as np
from mathutils import Matrix, Vector

import modelos as M
from modelos import mat, sphere, cyl, torus, cone
import objetos as O

OUT = M.OUT
ONLY = M.ONLY
PX_PER_UNIT = 900 / 2.5          # escala del sprite normal de Toto
BODY_C = Vector((0, 0, 0.8))     # centro del cuerpo de Toto (modelos.toto)
BODY_R = (0.78, 0.72, 0.78)      # radios del cuerpo


# ------------------------------------------------------------------ utilidades
def objs(prefix):
    return [o for o in bpy.data.objects if o.name.split(".")[0] == prefix]


def delete(prefixes):
    for p in prefixes:
        for o in objs(p):
            bpy.data.objects.remove(o, do_unlink=True)


def fur():
    return objs("fur")[0]


def surf(d, off=0.0):
    """Punto de la superficie del cuerpo (elipsoide) en la dirección d desde el centro, y su normal."""
    d = Vector(d).normalized()
    a, b, c = BODY_R
    t = 1 / math.sqrt((d.x / a) ** 2 + (d.y / b) ** 2 + (d.z / c) ** 2)
    p = BODY_C + d * t
    n = Vector(((p.x - BODY_C.x) / a ** 2, (p.y - BODY_C.y) / b ** 2, (p.z - BODY_C.z) / c ** 2)).normalized()
    return p + n * off, n


def frame(n, roll=0.0):
    """Matriz de rotación con Z = normal y Y = «arriba» proyectado sobre la superficie."""
    up = Vector((0, 0, 1))
    if abs(n.z) > 0.92:
        up = Vector((0, -1, 0))
    y = (up - n * up.dot(n)).normalized()
    x = y.cross(n).normalized()
    R = Matrix((x, y, n)).transposed()
    return R @ Matrix.Rotation(roll, 3, "Z")


def polar_mesh(name, rfun, rings=14, segs=72):
    verts = [(0, 0, 0)]
    for i in range(1, rings + 1):
        rho = i / rings
        for j in range(segs):
            f = 2 * math.pi * j / segs
            r = rfun(f) * rho
            verts.append((r * math.cos(f), r * math.sin(f), 0))
    faces = []
    for j in range(segs):
        faces.append((0, 1 + j, 1 + (j + 1) % segs))
    for i in range(rings - 1):
        a0, b0 = 1 + i * segs, 1 + (i + 1) * segs
        for j in range(segs):
            j1 = (j + 1) % segs
            faces.append((a0 + j, b0 + j, b0 + j1, a0 + j1))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    for p in me.polygons:
        p.use_smooth = True
    return o


def decal(name, rfun, d, m, thick=0.03, gap=0.012, roll=0.0, target=None):
    """Mancha / objeto plano que abraza la superficie del cuerpo (shrinkwrap + espesor + suavizado)."""
    o = polar_mesh(name, rfun)
    p, n = surf(d)
    o.matrix_world = Matrix.Translation(p + n * 0.15) @ frame(n, roll).to_4x4()
    sw = o.modifiers.new("wrap", "SHRINKWRAP")
    sw.target = target or fur()
    sw.wrap_method = "NEAREST_SURFACEPOINT"
    sw.wrap_mode = "OUTSIDE_SURFACE"
    sw.offset = gap
    so = o.modifiers.new("thick", "SOLIDIFY")
    so.thickness, so.offset = thick, 1.0
    sub = o.modifiers.new("sub", "SUBSURF")
    sub.levels, sub.render_levels = 1, 2
    o.data.materials.append(m)
    return o


def wobbly(base, amps, seed, lobes=()):
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in amps]

    def r(f):
        v = 1 + sum(a * math.sin((k + 2) * f + ph[k]) for k, a in enumerate(amps))
        for (fc, w, L) in lobes:
            dfi = math.atan2(math.sin(f - fc), math.cos(f - fc))
            v += L * math.exp(-(dfi / w) ** 2)
        return base * v
    return r


def tube(name, pts, r, m, order=4):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new("NURBS")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1)
    sp.use_endpoint_u = True
    sp.order_u = min(order, len(pts))
    sp.resolution_u = 10
    sp.use_smooth = True
    o = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(m)
    return o


def stripes_mat(name, c1, c2, freq, rough=0.8, axis=1):
    """Material a rayas (coordenadas del objeto) para la media."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation, mul.inputs[1].default_value = "MULTIPLY", 2 * math.pi * freq
    sn = nt.nodes.new("ShaderNodeMath")
    sn.operation = "SINE"
    gt = nt.nodes.new("ShaderNodeMath")
    gt.operation, gt.inputs[1].default_value = "GREATER_THAN", 0.25
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs[6].default_value = tuple(M.srgb2lin(x) for x in c1) + (1,)
    mix.inputs[7].default_value = tuple(M.srgb2lin(x) for x in c2) + (1,)
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs[axis], mul.inputs[0])
    nt.links.new(mul.outputs[0], sn.inputs[0])
    nt.links.new(sn.outputs[0], gt.inputs[0])
    nt.links.new(gt.outputs[0], mix.inputs[0])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    return m


def bumpy(o, strength=0.03, scale=0.08):
    tex = bpy.data.textures.new("bump" + o.name, "CLOUDS")
    tex.noise_scale = scale
    d = o.modifiers.new("disp", "DISPLACE")
    d.texture, d.strength = tex, strength
    return o


def group(objs_, loc, scale=1.0, rotz=0.0):
    """Mueve y escala un conjunto de objetos construidos alrededor del origen."""
    T = Matrix.Translation(loc) @ Matrix.Rotation(rotz, 4, "Z") @ Matrix.Scale(scale, 4)
    for o in objs_:
        o.matrix_world = T @ o.matrix_world


# ------------------------------------------------------------------ piezas reutilizables
def rubber_duck():
    """Patito de goma (mismo diseño que objetos.duck), construido alrededor del origen."""
    Y = mat("duck", (255, 215, 30), 0.3)
    ps = [sphere((0, 0, 0.3), (0.48, 0.38, 0.3), Y, name="duck"),
          sphere((-0.24, -0.02, 0.74), (0.27, 0.26, 0.26), Y, name="duck"),
          sphere((-0.5, -0.02, 0.7), (0.15, 0.11, 0.055), mat("beak", (255, 130, 20), 0.4), name="duck")]
    for y in (-0.13, 0.11):
        ps.append(sphere((-0.38, y - 0.07, 0.83), (0.055, 0.035, 0.065), mat("deye", (25, 20, 30), 0.2), name="duck"))
        ps.append(sphere((-0.4, y - 0.1, 0.85), (0.018, 0.01, 0.018), mat("glint", (255, 255, 255), 0.1, emis=2.0), name="duck"))
    w = sphere((0.05, -0.32, 0.36), (0.26, 0.08, 0.15), Y, name="duck")
    w.rotation_euler = (0, math.radians(-15), 0)
    ps.append(w)
    ps.append(cone((0.48, 0, 0.45), 0.12, 0.0, 0.25, Y, rot=(0, math.radians(-60), 0), name="duck"))
    bpy.context.view_layer.update()
    return ps


def soap_bubble(loc, r):
    sphere(loc, (r, r, r), mat("bubble", (200, 230, 255), 0.02, alpha=0.32), seg=32, name="bubble")
    sphere((loc[0] - r * 0.4, loc[1] - r * 0.85, loc[2] + r * 0.4), (r * 0.2, r * 0.07, r * 0.14),
           mat("shine", (255, 255, 255), 0.0, emis=2), seg=16, name="bubble")
    t = torus(loc, r, r * 0.03, mat("film", (255, 170, 230), 0.1, alpha=0.55), rot=(math.radians(80), 0, 0.3),
              name="bubble")
    return t


def sparkle(loc, R, cam_loc, col=(255, 248, 190)):
    """Brillito de 4 puntas mirando a la cámara."""
    verts, faces = [(0, 0, 0)], []
    for k in range(8):
        f = k * math.pi / 4
        r = R if k % 2 == 0 else R * 0.28
        verts.append((r * math.cos(f + math.pi / 2), r * math.sin(f + math.pi / 2), 0))
    for k in range(8):
        faces.append((0, 1 + k, 1 + (k + 1) % 8))
    me = bpy.data.meshes.new("spark")
    me.from_pydata(verts, [], faces)
    o = bpy.data.objects.new("spark", me)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    d = Vector(cam_loc) - Vector(loc)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    so = o.modifiers.new("thick", "SOLIDIFY")
    so.thickness = 0.01
    o.data.materials.append(mat("spark", col, 0.2, emis=3.0))
    return o


# ------------------------------------------------------------------ variantes
def toto_base(mouth_open, closed, keep_sock=False):
    M._mats.clear()
    sc = M.toto(mouth_open, closed)
    if not keep_sock:
        delete(["sock", "stripe"])
    return sc


def v_sucio(mouth_open, closed):
    sc = toto_base(mouth_open, closed)
    rnd = random.Random(11)
    noodle = mat("noodle", (255, 214, 120), 0.4)
    noodle2 = mat("noodle2", (255, 190, 105), 0.4)
    top = Vector((0.08, -0.32, 1)).normalized()     # la salsa cae hacia la frente (lo que ve la cámara)

    def forbidden(d):
        # zona de la cara (ojos y boca): los fideos no la tapan
        return d.y < -0.25 and d.z < 0.55

    # montón de fideos enredados sobre la cabeza: rulos que se apoyan en el pelo y se cruzan entre sí
    tang = frame(top)
    e1, e2 = tang.col[0], tang.col[1]
    for k in range(13):
        ang, rad = rnd.uniform(0, 2 * math.pi), rnd.uniform(0.0, 0.42)
        c0 = (top + e1 * rad * math.cos(ang) + e2 * rad * math.sin(ang) * 0.8).normalized()
        f1 = frame(c0)
        u1, u2 = f1.col[0], f1.col[1]
        R = rnd.uniform(0.12, 0.22)
        turns = rnd.uniform(1.1, 1.6)
        ph, ph2, tilt = rnd.uniform(0, 6), rnd.uniform(0, 6), rnd.uniform(0.6, 1.0)
        layer = k % 3
        pts = []
        N = 40
        for i in range(N):
            u = 2 * math.pi * turns * i / (N - 1)
            rho = R * (1 + 0.3 * math.sin(3 * u + ph))
            d = (c0 + u1 * rho * math.cos(u) + u2 * rho * math.sin(u) * tilt).normalized()
            if forbidden(d):
                if len(pts) > 5:
                    break
                pts = []
                continue
            off = 0.05 + 0.03 * layer + 0.035 * math.sin(2 * u + ph2)
            pts.append(surf(d, off=off)[0])
        if len(pts) > 6:
            tube("noodle", pts, 0.032, noodle2 if k % 4 == 0 else noodle)
    # fideos que se escurren por los costados y quedan colgando
    for k, az in enumerate([math.radians(a_) for a_ in (180, 200, 160, 0, -20, 25, 120, 60)]):
        T = (top + e1 * rnd.uniform(-0.15, 0.15) + e2 * rnd.uniform(-0.1, 0.15)).normalized()
        h = Vector((math.cos(az), math.sin(az), 0))
        h = (h - T * h.dot(T)).normalized()
        bn = T.cross(h)
        ph, fq, amp = rnd.uniform(0, 6), rnd.uniform(4, 7), rnd.uniform(0.05, 0.1)
        smax = rnd.uniform(1.25, 1.6) if k < 6 else rnd.uniform(0.9, 1.2)
        ds = []
        for i in range(24):
            s = smax * i / 23
            d = (T * math.cos(s) + h * math.sin(s) + bn * (amp * math.sin(fq * s + ph))).normalized()
            if forbidden(d):
                break
            ds.append(d)
        if len(ds) < 6:
            continue
        pts = [surf(d, off=0.06)[0] for d in ds]
        end = ds[-1]
        if k < 6:
            p, n = surf(end, off=0.06)
            L = rnd.uniform(0.3, 0.5)
            for j in range(1, 7):
                t = j / 6
                sx = 1 if end.x > 0 else -1
                pts.append(p + n * (0.05 * t) + Vector((0.06 * sx * math.sin(t * 6 + ph), 0, -L * t)))
        tube("noodle", pts, 0.032, noodle2 if k % 3 == 0 else noodle)

    # salsa de tomate: manchón grueso arriba, con gotas que bajan
    sauce = mat("sauce", (225, 35, 25), 0.22)
    decal("sauce", wobbly(0.3, [0.12, 0.08, 0.05], 3, lobes=[(-math.pi / 2 + 0.35, 0.18, 0.45), (-math.pi / 2 - 0.5, 0.15, 0.3),
                                                             (0.2, 0.2, 0.25), (math.pi - 0.3, 0.2, 0.3)]),
          top, sauce, thick=0.06, gap=0.1)
    decal("stain", wobbly(0.06, [0.12], 8, lobes=[(-math.pi / 2, 0.25, 2.2)]), (0.02, -0.5, 0.8), sauce, thick=0.03)
    for (dx, dy, rr) in [(0.0, 0.0, 0.17), (0.12, 0.08, 0.12), (-0.13, 0.05, 0.13)]:
        p, n = surf(top + Vector((dx, dy, 0)), off=0.14)
        sphere(p, (rr, rr, rr * 0.45), sauce, name="sauceblob").rotation_euler = n.to_track_quat("Z", "Y").to_euler()
    # albóndigas
    meat = mat("meatball", (135, 72, 40), 0.75)
    for (dx, dy, rr) in [(-0.05, 0.05, 0.13), (0.16, 0.12, 0.11)]:
        p, n = surf(top + Vector((dx, dy, 0)), off=0.17 + rr * 0.6)
        bumpy(sphere(p, (rr, rr, rr * 0.92), meat, name="meatball"), 0.025, 0.05)
    # gotitas de salsa en la cara y el cuerpo
    decal("stain", wobbly(0.085, [0.15, 0.1], 5, lobes=[(-math.pi / 2, 0.25, 0.9)]), (-0.62, -0.75, 0.05), sauce,
          thick=0.025)
    decal("stain", wobbly(0.07, [0.18, 0.1], 7, lobes=[(-math.pi / 2, 0.3, 0.7)]), (0.3, -0.85, -0.62), sauce,
          thick=0.025)
    # barro
    mud = mat("mud", (120, 78, 42), 0.85)
    decal("mud", wobbly(0.13, [0.18, 0.12, 0.08], 9), (-0.45, -0.75, -0.6), mud, thick=0.025, roll=0.5)
    decal("mud", wobbly(0.04, [0.2], 2), (-0.62, -0.6, -0.55), mud, thick=0.02)
    decal("mud", wobbly(0.09, [0.2, 0.1, 0.1], 4), (0.75, -0.25, 0.45), mud, thick=0.025, roll=1.0)
    decal("mud", wobbly(0.035, [0.2], 6), (0.62, -0.42, 0.62), mud, thick=0.02)
    for f in objs("foot")[:1]:
        sphere((f.location.x + 0.05, f.location.y - 0.15, f.location.z + 0.08), (0.12, 0.09, 0.05), mud, name="mudfoot")

    # media rayada pegada al costado (blanca con rayas rojas): caña, pie, talón y punta, todo abrazando el cuerpo
    def superellipse(a, b, nexp=4.0):
        return lambda f: (abs(math.cos(f) / a) ** nexp + abs(math.sin(f) / b) ** nexp) ** (-1 / nexp)

    roll = math.radians(-22)
    p0, n0 = surf((0.84, -0.5, -0.12))
    F = frame(n0, roll)
    e1, e2 = F.col[0], F.col[1]

    def at(u, v):
        return p0 - BODY_C + e1 * u + e2 * v

    sockm = stripes_mat("sockstripes", (255, 255, 255), (235, 45, 55), 7.0)
    red = mat("sockred", (235, 45, 55), 0.8)
    white = mat("sockwhite", (255, 255, 255), 0.8)
    decal("sock", lambda f: 1.0 / math.hypot(math.cos(f) / 0.2, math.sin(f) / 0.115), at(0.08, -0.2), white,
          thick=0.04, gap=0.014, roll=roll)
    decal("sock", superellipse(0.12, 0.25), at(-0.02, 0.06), sockm, thick=0.04, gap=0.02, roll=roll)
    decal("sock", lambda f: 1.0 / math.hypot(math.cos(f) / 0.09, math.sin(f) / 0.085), at(0.22, -0.21), red,
          thick=0.03, gap=0.03, roll=roll)
    decal("sock", lambda f: 1.0 / math.hypot(math.cos(f) / 0.08, math.sin(f) / 0.08), at(-0.08, -0.24), red,
          thick=0.03, gap=0.03, roll=roll)
    return sc


def v_banera(mouth_open, closed):
    sc = toto_base(mouth_open, closed)
    rim_z = 0.42
    a, b, c = 1.32, 0.86, 0.72
    W = mat("tub", (255, 255, 255), 0.2)
    tub = sphere((0, 0, rim_z), (a, b, c), W, seg=96, name="tub")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.bisect(plane_co=(0, 0, rim_z), plane_no=(0, 0, 1), clear_outer=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    so = tub.modifiers.new("thick", "SOLIDIFY")
    so.thickness, so.offset = 0.05, -1
    # borde redondeado
    ring = [(a * math.cos(2 * math.pi * k / 96), b * math.sin(2 * math.pi * k / 96), rim_z + 0.01) for k in range(96)]
    r = tube("rim", ring + ring[:4], 0.065, W)
    r.data.splines[0].use_cyclic_u = True
    # agua celeste debajo de la espuma
    water = polar_mesh("water", lambda f: 1.0, rings=4, segs=64)
    water.scale = (a * 0.97, b * 0.95, 1)
    water.location = (0, 0, rim_z - 0.05)
    water.data.materials.append(mat("water", (120, 205, 255), 0.1))
    # patas doradas
    gold = mat("gold", (245, 195, 60), 0.28, metal=0.75)
    for x in (-0.86, 0.86):
        for y in (-0.42, 0.42):
            k = 1 - (x / a) ** 2 - (y / b) ** 2
            ztop = rim_z - c * math.sqrt(max(k, 0)) + 0.04
            zb = -0.42
            cone((x * 1.04, y * 1.04, (ztop + zb) / 2 + 0.05), 0.075, 0.045, ztop - zb - 0.06, gold, name="leg")
            sphere((x * 1.08, y * 1.08, zb + 0.06), (0.1, 0.1, 0.085), gold, name="paw")
    # espuma: en la superficie y trepando por el cuerpo de Toto (hasta la mitad; adelante, debajo de la boca)
    foam = mat("foam", (250, 252, 255), 0.75)
    rnd = random.Random(4)
    for k in range(240):
        ang, rr = rnd.uniform(0, 2 * math.pi), math.sqrt(rnd.uniform(0.0, 1.0))
        x, y = a * 0.93 * rr * math.cos(ang), b * 0.9 * rr * math.sin(ang)
        if math.hypot(x / 0.72, y / 0.66) < 1:   # dentro de Toto
            continue
        if math.hypot(x - 0.92, y + 0.42) < 0.28:  # lugar del patito
            continue
        s = rnd.uniform(0.1, 0.2)
        sphere((x, y, rim_z + rnd.uniform(-0.02, 0.07)), (s, s, s * 0.8), foam, seg=24, name="foam")
    for k in range(120):
        az = rnd.uniform(0, 2 * math.pi)
        hy = math.sin(az)                       # -1 = adelante
        front = max(0.0, -hy) ** 1.5 * (1 - abs(math.cos(az)) * 0.2)
        zmax = 0.85 - 0.42 * front                # costados hasta la mitad; adelante, debajo de la boca
        z = rnd.uniform(rim_z, zmax)
        rz = (z - BODY_C.z) / BODY_R[2]
        rh = math.sqrt(max(0.0, 1 - rz * rz))
        p = Vector((BODY_R[0] * rh * math.cos(az), BODY_R[1] * rh * math.sin(az), z))
        s = rnd.uniform(0.09, 0.17) * (0.8 if front > 0.5 else 1)
        if front > 0.3 and z + s * 0.8 > 0.47:
            continue
        n = Vector((p.x, p.y, 0)).normalized()
        sphere(p + n * s * 0.35, (s, s, s * 0.85), foam, seg=24, name="foam")
    # copete de espuma en la cabeza, entre los cuernos
    for (x, y, z, s) in [(0.0, 0.02, 1.6, 0.13), (-0.12, 0.05, 1.57, 0.1), (0.12, 0.0, 1.57, 0.1), (0.02, -0.02, 1.72, 0.08)]:
        sphere((x, y, z), (s, s, s * 0.85), foam, seg=24, name="foam")
    # patito flotando a la derecha (lado de la cámara)
    d = rubber_duck()
    group(d, (0.92, -0.42, rim_z + 0.06), 0.55, rotz=math.radians(-55))
    # burbujas
    for (loc, rr) in [((-1.0, -0.25, 1.25), 0.13), ((-0.75, -0.4, 1.7), 0.09), ((1.0, -0.1, 1.45), 0.11),
                      ((0.75, -0.3, 1.95), 0.07), ((-1.15, -0.1, 0.95), 0.07)]:
        soap_bubble(loc, rr)
    return sc


def v_cama(mouth_open, closed):
    """Toto metido en la cama, tapado hasta debajo de los ojos: solo asoman ojos, cuernos y la parte de arriba."""
    sc = toto_base(mouth_open, closed)
    delete(["foot"])
    dz = -0.45                               # Toto hundido bajo la frazada (lo que queda debajo no se ve)
    for o in bpy.data.objects:
        if o.type == "MESH":
            o.location.z += dz
    S = 1.35                                 # cama más grande que la de objetos.py: Toto es grandote
    L, D = 2.5 * S, 1.2 * S
    bx, by = 0.6, -0.1                       # centro de la cama: Toto cerca de la cabecera
    top = 0.0                                # parte de arriba del colchón
    wood, wood2 = mat("wood", (200, 125, 70), 0.5), mat("wood2", (170, 100, 55), 0.5)
    base_z = top - 0.3 * S
    O.box((bx, by, base_z - 0.1 * S), (L, D, 0.24 * S), wood, 0.06)
    floor = base_z - 0.55 * S
    for x in (-L / 2 + 0.1, L / 2 - 0.1):
        for y in (-D / 2 + 0.1, D / 2 - 0.1):
            O.box((bx + x, by + y, (floor + base_z) / 2), (0.16, 0.16, base_z - floor), wood2, 0.04)
    O.box((bx - L / 2, by, floor + 0.95 * S), (0.16, D + 0.06, 1.9 * S), wood, 0.07)           # cabecera
    sphere((bx - L / 2, by, floor + 1.9 * S), (0.14, D / 2 + 0.06, 0.14), wood2, name="knob")
    O.box((bx + L / 2, by, floor + 0.62 * S), (0.16, D + 0.06, 1.24 * S), wood, 0.07)          # pie de cama
    sphere((bx + L / 2, by, floor + 1.24 * S), (0.14, D / 2 + 0.06, 0.14), wood2, name="knob")
    O.box((bx, by, top - 0.15 * S), (L - 0.2, D - 0.06, 0.3 * S), mat("mattress", (255, 252, 240), 0.6), 0.1)
    O.box((bx - L / 2 + 0.42, by + 0.15, top + 0.42), (0.5, D * 0.7, 0.5), mat("pillow", (255, 255, 255), 0.7), 0.16)

    # frazada: superficie que cubre la cama, se levanta en un bulto sobre el cuerpo de Toto y cae por adelante
    z_edge = 0.86 + dz
    rz = (z_edge - (BODY_C.z + dz)) / BODY_R[2]
    hx, hy = BODY_R[0] * math.sqrt(1 - rz * rz), BODY_R[1] * math.sqrt(1 - rz * rz)   # contorno de la cabeza ahí
    base = top + 0.1

    def h(x, y):
        r = math.hypot(x / (hx * 1.06), y / (hy * 1.06))
        if r <= 1:
            p = 1.0
        elif r >= 2.1:
            p = 0.0
        else:
            t = (r - 1) / 1.1
            p = 0.5 + 0.5 * math.cos(math.pi * t)
        return base + (z_edge - base) * p + 0.015 * math.sin(7 * x + 2 * y)

    x0, x1 = bx - L / 2 + 0.2, bx + L / 2 - 0.1
    yf, yb = by - D / 2 - 0.03, by + D / 2 - 0.02
    Sd = 0.5                                  # largo de lo que cuelga por adelante
    NX, NS = 90, 70
    depth = yb - yf
    verts, faces = [], []
    for i in range(NX + 1):
        x = x0 + (x1 - x0) * i / NX
        for j in range(NS + 1):
            s = (Sd + depth) * j / NS
            if s < Sd:
                zt = h(x, yf)
                w = (Sd - s)
                verts.append((x, yf - 0.03 * math.sin(math.pi * min(1, w / Sd)) - 0.02 * math.sin(9 * x), zt - w))
            else:
                y = yf + (s - Sd)
                verts.append((x, y, h(x, y)))
    for i in range(NX):
        for j in range(NS):
            a = i * (NS + 1) + j
            faces.append((a, a + NS + 1, a + NS + 2, a + 1))
    me = bpy.data.meshes.new("blanket")
    me.from_pydata(verts, [], faces)
    bl = bpy.data.objects.new("blanket", me)
    sc.collection.objects.link(bl)
    for p in me.polygons:
        p.use_smooth = True
    blue = mat("blanket", (70, 140, 255), 0.75)
    bl.data.materials.append(blue)
    so = bl.modifiers.new("thick", "SOLIDIFY")
    so.thickness, so.offset = 0.05, 0
    sub = bl.modifiers.new("sub", "SUBSURF")
    sub.levels, sub.render_levels = 1, 2
    # borde blanco de la frazada alrededor de la cara (el dobladillo)
    hem = mat("hem", (255, 255, 255), 0.6)
    ring = [(hx * 1.04 * math.cos(2 * math.pi * i / 96), hy * 1.04 * math.sin(2 * math.pi * i / 96),
             z_edge + 0.012) for i in range(96)]
    t = tube("hem", ring + ring[:4], 0.055, hem)
    t.data.splines[0].use_cyclic_u = True
    O.box(((x0 + x1) / 2, yf - 0.04, top + 0.1 - Sd + 0.03), (x1 - x0, 0.06, 0.07), hem, 0.025)
    # estrellitas amarillas de la frazada
    star = mat("star", (255, 220, 60), 0.4)
    rnd = random.Random(8)
    for k in range(14):
        x, y = rnd.uniform(x0 + 0.1, x1 - 0.1), rnd.uniform(yf + 0.1, yb - 0.1)
        if math.hypot(x / (hx * 1.15), y / (hy * 1.15)) < 1:
            continue
        sphere((x, y, h(x, y) + 0.03), (0.06, 0.06, 0.02), star, name="star")
    for k in range(7):
        x = x0 + 0.25 + k * (x1 - x0 - 0.5) / 6
        sphere((x, yf - 0.06, top + 0.1 - Sd / 2 - 0.05), (0.06, 0.02, 0.06), star, name="star")
    return sc


def v_limpio(mouth_open, closed):
    sc = toto_base(mouth_open, closed)
    fb = fur()
    fb.data.materials.clear()
    fb.data.materials.append(mat("toto_clean", (255, 158, 60), 0.6, sss=0.03))
    d = fb.modifiers["disp"]
    d.texture.noise_scale = 0.045
    d.strength = 0.07
    cam_loc = sc.camera.location
    for (loc, R) in [((-0.9, -0.3, 1.5), 0.2), ((1.0, -0.2, 1.25), 0.15), ((0.72, -0.5, 1.8), 0.12),
                     ((-1.05, -0.2, 0.6), 0.13), ((1.0, -0.4, 0.45), 0.1), ((-0.5, -0.5, 1.85), 0.09)]:
        sparkle(loc, R, cam_loc)
    # brillito sobre el pelo limpio
    sparkle((0.45, -0.66, 1.3), 0.09, cam_loc, col=(255, 255, 255))
    return sc


VARIANTS = dict(sucio=v_sucio, banera=v_banera, cama=v_cama, limpio=v_limpio)


# ------------------------------------------------------------------ encuadre y render
def fit_camera(sc, margin=0.1):
    """Agranda el cuadro (no achica a Toto): misma escala de píxeles que el sprite normal."""
    bpy.context.view_layer.update()
    cam = sc.camera
    inv = cam.matrix_world.inverted()
    dg = bpy.context.evaluated_depsgraph_get()
    xs, ys, zs = [], [], []
    for o in sc.objects:
        if o.type not in ("MESH", "CURVE"):
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        co = np.empty(len(me.vertices) * 3, dtype=np.float32)
        me.vertices.foreach_get("co", co)
        ev.to_mesh_clear()
        co = co.reshape(-1, 3)
        if not len(co):
            continue
        mw = np.array(inv @ o.matrix_world)
        q = co @ mw[:3, :3].T + mw[:3, 3]
        xs += [q[:, 0].min(), q[:, 0].max()]
        ys += [q[:, 1].min(), q[:, 1].max()]
        w = np.array(o.matrix_world)
        zs.append((co @ w[:3, :3].T + w[:3, 3])[:, 2].min())
    x0, x1 = float(min(xs)) - margin, float(max(xs)) + margin
    y0, y1 = float(min(ys)) - margin, float(max(ys)) + margin
    rx, ry = math.ceil((x1 - x0) * PX_PER_UNIT / 2) * 2, math.ceil((y1 - y0) * PX_PER_UNIT / 2) * 2
    ortho = max(rx, ry) / PX_PER_UNIT
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    cam.data.ortho_scale = ortho
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cam.data.shift_x, cam.data.shift_y = cx / ortho, cy / ortho
    bpy.context.view_layer.update()

    def px(p):
        q = inv @ Vector(p)
        return [round(rx / 2 + (q.x - cx) * PX_PER_UNIT, 1), round(ry / 2 - (q.y - cy) * PX_PER_UNIT, 1)]
    zmin = float(min(zs))
    return {"size": [rx, ry], "toto_body_center_px": px(BODY_C), "toto_feet_px": px((0, 0, -0.06)),
            "floor_px_y": px((0, 0, zmin))[1], "px_per_unit": PX_PER_UNIT}


def main():
    info_path = os.path.join(OUT, "TOTO-variantes.json")
    info = {}
    if os.path.exists(info_path):
        info = json.load(open(info_path))
    for vname, fn in VARIANTS.items():
        if ONLY and vname not in ONLY:
            continue
        for m in (0, 1):
            for c in (0, 1):
                p = os.path.join(OUT, f"TOTO-{vname}_{m}_{c}.png")
                if os.environ.get("VARIANTES_ESTADOS") and f"{m}_{c}" not in os.environ["VARIANTES_ESTADOS"].split(","):
                    continue
                if os.path.exists(p) and vname in info:
                    continue
                sc = fn(m, c)
                info[vname] = fit_camera(sc)
                if not os.path.exists(p):
                    M.render(sc, p)
                    print("OK", os.path.basename(p), flush=True)
                json.dump(info, open(info_path, "w"), indent=1)


if __name__ == "__main__":
    main()
