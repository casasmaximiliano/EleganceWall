"""Objetos 3D de «La gran carrera de Zumbi» (carrera de flores). Mismo estilo y luz que objetos.py.

Uso: python3 objetos3.py CARPETA_SALIDA [objeto ...]
Cada objeto se renderiza una vez como PNG con transparencia (700x700). No pisa archivos que ya existen.
"""
import math
import os
import random

import bpy

import modelos as M
from modelos import mat, sphere, cyl, torus, cone, eye, mouth
from objetos import box
from invitados import tube, chain, bez, frame, patch

INK = (40, 35, 55)


def setup():
    sc = M.reset()
    sc.render.resolution_x = sc.render.resolution_y = 700
    M._mats.clear()
    return sc


def checker_mat(name, c1=(255, 255, 255), c2=(40, 35, 55), scale=8.0, coords="UV"):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.5
    ch = nt.nodes.new("ShaderNodeTexChecker")
    ch.inputs["Scale"].default_value = scale
    ch.inputs["Color1"].default_value = tuple(M.srgb2lin(v) for v in c1) + (1,)
    ch.inputs["Color2"].default_value = tuple(M.srgb2lin(v) for v in c2) + (1,)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs[coords], ch.inputs["Vector"])
    nt.links.new(ch.outputs["Color"], b.inputs["Base Color"])
    return m


def text(body, loc, size, m, extrude=0.04, rot=(math.radians(90), 0, 0)):
    cu = bpy.data.curves.new("txt", "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = 0.01
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new("txt", cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    ob.data.materials.append(m)
    return ob


def plane(verts, m, thick=0.02, subdiv=0, name="pl"):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], [tuple(range(len(verts)))])
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if thick:
        ob.modifiers.new("sol", "SOLIDIFY").thickness = thick
    ob.data.materials.append(m)
    return ob


def wavy_flag(x0, z0, w, h, m, waves=1.2, amp=0.14, nx=24, nz=8):
    """Bandera ondulada con coordenadas UV (para el cuadriculado)."""
    verts, faces, uvs = [], [], []
    for j in range(nz + 1):
        for i in range(nx + 1):
            u, v = i / nx, j / nz
            verts.append((x0 + u * w, amp * math.sin(u * waves * 2 * math.pi) * u, z0 + v * h - 0.05 * u * u))
    for j in range(nz):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    me = bpy.data.meshes.new("flag")
    me.from_pydata(verts, [], faces)
    uvl = me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            uvl.data[li].uv = ((vi % (nx + 1)) / nx, (vi // (nx + 1)) / nz)
    ob = bpy.data.objects.new("flag", me)
    bpy.context.scene.collection.objects.link(ob)
    ob.modifiers.new("sol", "SOLIDIFY").thickness = 0.02
    for p in me.polygons:
        p.use_smooth = True
    ob.data.materials.append(m)
    return ob


def striped_pole(x, h, r=0.07, c1=(240, 60, 70), c2=(255, 255, 255), n=8):
    for k in range(n):
        cyl((x, 0, h * (k + 0.5) / n), r, h / n, mat("pole%d" % (k % 2), c1 if k % 2 == 0 else c2, 0.4))


# ------------------------------------------------------------------ objetos
def finish():
    sc = setup()
    for x in (-1.3, 1.3):
        striped_pole(x, 2.2)
        sphere((x, 0, 2.28), (0.12, 0.12, 0.12), mat("gold", (240, 195, 60), 0.25, metal=0.7))
        cyl((x, 0, 0.05), 0.2, 0.1, mat("base", (90, 90, 110), 0.5))
        for k, c in enumerate([(255, 90, 120), (90, 170, 255), (255, 210, 60)]):  # globos
            dx = (k - 1) * 0.22
            sphere((x + dx, -0.05, 2.75 + 0.08 * (k % 2)), (0.17, 0.17, 0.21), mat("balloon%d" % k, c, 0.25))
            tube((x + dx, -0.05, 2.55), (x, 0, 2.3), 0.008, 0.008, mat("ink", INK, 0.5), caps=False)
    bn = box((0, 0, 2.0), (2.75, 0.12, 0.55), mat("banner", (255, 255, 255), 0.5), 0.04)
    sq = 0.12
    for row in range(2):  # franja cuadriculada abajo del cartel
        for i in range(int(2.6 / sq)):
            if (i + row) % 2 == 0:
                box((-1.3 + sq / 2 + i * sq, -0.065, 1.79 + row * sq - sq / 2 + 0.03), (sq, 0.02, sq), mat("chk", INK, 0.5), 0.0)
    text("META", (0, -0.1, 2.08), 0.36, mat("red", (235, 50, 60), 0.4))
    for x in (-0.95, 0.95):
        sphere((x, -0.08, 2.1), (0.07, 0.02, 0.07), mat("star", (255, 205, 50), 0.4))
    frame(sc, pad=1.06)
    return sc


def flag():
    sc = setup()
    cyl((0, 0, 1.0), 0.04, 2.0, mat("pole", (210, 210, 225), 0.3, metal=0.6))
    sphere((0, 0, 2.03), (0.08, 0.08, 0.08), mat("gold", (240, 195, 60), 0.25, metal=0.7))
    wavy_flag(0.03, 1.2, 1.1, 0.75, checker_mat("chkflag", scale=5.0))
    frame(sc, pad=1.1)
    return sc


def sneaker(x, rotz, col, stripe):
    W = mat("sole", (255, 255, 255), 0.5)
    C = mat("shoe" + str(col), col, 0.4)
    S = mat("stripe" + str(stripe), stripe, 0.4)
    parts = []
    parts.append(sphere((x, 0.0, 0.12), (0.26, 0.55, 0.08), W))
    parts.append(sphere((x, 0.05, 0.25), (0.24, 0.5, 0.17), C))
    parts.append(sphere((x, 0.2, 0.4), (0.21, 0.24, 0.2), C))           # talón alto
    parts.append(torus((x, 0.18, 0.56), 0.13, 0.04, mat("collar", (255, 255, 255), 0.5)))
    parts.append(sphere((x, -0.42, 0.2), (0.19, 0.12, 0.1), W))          # puntera
    for s in (-1, 1):  # raya de color pegada al costado
        for k in range(2):
            o = patch((x, 0.05, 0.25), (0.24, 0.5, 0.17), s * (100 - 25 * k), 5 + 10 * k, 0.09, S, flat=0.25, sx=0.6)
            parts.append(o)
    for k in range(3):
        z = 0.37 + k * 0.035
        y = -0.12 + k * 0.1
        parts.append(cyl((x, y, z), 0.022, 0.26, mat("lace", (255, 255, 255), 0.4), rot=(0, math.radians(90), 0)))
    o = torus((x - 0.05, -0.06, 0.48), 0.07, 0.02, mat("lace", (255, 255, 255), 0.4), rot=(math.radians(60), 0, math.radians(30)))
    o2 = torus((x + 0.07, -0.06, 0.48), 0.07, 0.02, mat("lace", (255, 255, 255), 0.4), rot=(math.radians(60), 0, math.radians(-30)))
    parts += [o, o2]
    # girar todo el zapato alrededor de su centro
    import mathutils
    R = mathutils.Matrix.Rotation(math.radians(rotz), 4, "Z")
    T = mathutils.Matrix.Translation((x, 0, 0))
    bpy.context.view_layer.update()
    for p in parts:
        p.matrix_world = T @ R @ T.inverted() @ p.matrix_world


def sneakers():
    sc = setup()
    sneaker(-0.3, -62, (40, 190, 230), (255, 210, 50))
    sneaker(0.32, -35, (40, 190, 230), (255, 210, 50))
    frame(sc, pad=1.1, rise=1.6)
    return sc


def banana():
    sc = setup()
    Y = mat("banana", (255, 220, 60), 0.4)
    f = bez((-0.7, 0, 0.75), (-0.3, -0.1, 0.05), (0.35, -0.1, 0.05), (0.75, 0, 0.6))
    chain(f, lambda t: 0.04 + 0.19 * math.sin(math.pi * min(1, max(0, t))) ** 0.7, Y, n=60)
    sphere(f(0.0), (0.05, 0.05, 0.05), mat("tip", (110, 80, 40), 0.6))
    tube(f(1.0), (0.82, 0.0, 0.78), 0.05, 0.045, mat("stem", (150, 170, 70), 0.6))
    sphere((0.83, 0, 0.8), (0.055, 0.055, 0.04), mat("tip", (110, 80, 40), 0.6))
    frame(sc, pad=1.1, rise=1.0)
    return sc


def water_bottle():
    sc = setup()
    B = mat("bottle", (90, 180, 255), 0.15, alpha=0.75)
    cyl((0, 0, 0.6), 0.32, 1.0, B)
    sphere((0, 0, 1.1), (0.32, 0.32, 0.18), B)
    sphere((0, 0, 0.1), (0.32, 0.32, 0.06), B)
    cyl((0, 0, 0.7), 0.29, 0.95, mat("water", (60, 150, 255), 0.1, alpha=0.6))
    cyl((0, 0, 0.6), 0.325, 0.38, mat("label", (255, 255, 255), 0.5))
    sphere((0, -0.33, 0.62), (0.11, 0.02, 0.13), mat("drop", (60, 150, 255), 0.2))
    cone((0, -0.33, 0.75), 0.08, 0.0, 0.12, mat("drop", (60, 150, 255), 0.2), rot=(0, 0, 0))
    cyl((0, 0, 1.3), 0.17, 0.22, mat("cap", (255, 90, 110), 0.4))
    cyl((0, 0, 1.47), 0.07, 0.14, mat("cap2", (255, 210, 60), 0.4))
    torus((0.0, 0, 1.58), 0.1, 0.025, mat("cap2", (255, 210, 60), 0.4), rot=(math.radians(90), 0, 0))
    frame(sc, pad=1.12)
    return sc


def medal():
    sc = setup()
    G = mat("gold", (245, 195, 50), 0.25, metal=0.8)
    Bl = mat("ribbon", (50, 120, 255), 0.5)
    for s in (-1, 1):  # cinta en V
        b = box((s * 0.22, 0.05, 1.25), (0.26, 0.04, 1.0), Bl, 0.02, rot=(0, s * math.radians(-22), 0))
        box((s * 0.22, 0.03, 1.25), (0.07, 0.02, 1.0), mat("ribw", (255, 255, 255), 0.5), 0.01, rot=(0, s * math.radians(-22), 0))
    cyl((0, 0, 0.55), 0.42, 0.1, G, rot=(math.radians(90), 0, 0))
    torus((0, -0.05, 0.55), 0.36, 0.03, mat("gold2", (255, 225, 120), 0.2, metal=0.8), rot=(math.radians(90), 0, 0))
    # estrella en relieve
    pts = []
    for k in range(10):
        a = math.pi / 2 + k * math.pi / 5
        r = 0.25 if k % 2 == 0 else 0.11
        pts.append((r * math.cos(a), -0.06, 0.55 + r * math.sin(a)))
    st = plane(pts, mat("gold2", (255, 225, 120), 0.2, metal=0.8), thick=0.04)
    sphere((0, 0, 0.98), (0.08, 0.06, 0.08), G)
    frame(sc, pad=1.12)
    return sc


def trophy():
    sc = setup()
    G = mat("gold", (245, 195, 50), 0.22, metal=0.85)
    box((0, 0, 0.12), (0.8, 0.6, 0.24), mat("wood", (150, 90, 50), 0.5), 0.05)
    box((0, 0, 0.32), (0.55, 0.42, 0.16), mat("wood2", (120, 70, 40), 0.5), 0.04)
    box((0, -0.31, 0.12), (0.4, 0.02, 0.12), G, 0.01)
    cyl((0, 0, 0.5), 0.07, 0.3, G)
    cone((0, 0, 0.45), 0.2, 0.06, 0.1, G)
    cup = cone((0, 0, 1.05), 0.2, 0.5, 0.75, G)
    sphere((0, 0, 0.72), (0.22, 0.22, 0.12), G)
    torus((0, 0, 1.41), 0.44, 0.045, G)
    for s in (-1, 1):
        t = torus((s * 0.55, 0, 1.05), 0.18, 0.04, G, rot=(math.radians(90), 0, 0))
    pts = []
    for k in range(10):
        a = math.pi / 2 + k * math.pi / 5
        r = 0.17 if k % 2 == 0 else 0.075
        pts.append((r * math.cos(a), -0.39, 1.05 + r * math.sin(a)))
    plane(pts, mat("star", (255, 255, 255), 0.3), thick=0.03)
    frame(sc, pad=1.1)
    return sc


def flower_big():
    sc = setup()
    Gs = mat("stem", (80, 180, 80), 0.5)
    tube((0, 0.05, 0.0), (0.0, 0.05, 1.45), 0.06, 0.06, Gs)
    for s, z in ((-1, 0.45), (1, 0.75)):
        lf = sphere((s * 0.25, 0.05, z), (0.25, 0.04, 0.1), mat("leaf", (110, 205, 90), 0.5))
        lf.rotation_euler = (0, s * math.radians(-30), 0)
    cz = 1.75
    for k in range(10):
        a = k / 10 * 2 * math.pi
        p = sphere((0.42 * math.cos(a), 0.05, cz + 0.42 * math.sin(a)), (0.24, 0.06, 0.14), mat("petal" + str(k % 2),
                   (255, 110, 160) if k % 2 else (255, 140, 185), 0.4))
        p.rotation_euler = (0, -a, 0)
    hc, hr = (0, -0.02, cz), (0.3, 0.12, 0.3)
    sphere(hc, hr, mat("center", (255, 210, 50), 0.45))
    Y = mat("center", (255, 210, 50), 0.45)
    for x in (-0.1, 0.1):
        eye(x, -0.1, cz + 0.06, 0.07, (110, 70, 40), False, Y)
    for x in (-0.18, 0.18):
        sphere((x, -0.13, cz - 0.06), (0.05, 0.02, 0.035), mat("cheek", (255, 150, 170), 0.6))
    mouth(0, -0.15, cz - 0.11, 0.12, False)
    sphere((0, 0.05, 0.03), (0.25, 0.2, 0.05), mat("grass", (90, 175, 80), 0.6))
    frame(sc, pad=1.08)
    return sc


def start_line():
    sc = setup()
    box((0, 0, 0.01), (3.0, 0.5, 0.02), mat("paint", (255, 255, 255), 0.6), 0.005)
    sq = 0.16
    for row in range(2):
        for i in range(int(3.0 / sq)):
            if (i + row) % 2 == 0:
                box((-1.5 + sq / 2 + i * sq, -0.08 - sq / 2 + row * sq + 0.08, 0.022), (sq, sq, 0.005), mat("chk", INK, 0.5), 0.0)
    for x in (-1.6, 1.6):  # conitos en las puntas
        cone((x, 0, 0.18), 0.12, 0.02, 0.36, mat("cone", (255, 130, 30), 0.45))
    frame(sc, pad=1.05, rise=3.5)
    return sc


def traffic_cone():
    sc = setup()
    Or = mat("cone", (255, 120, 30), 0.4)
    box((0, 0, 0.05), (1.0, 1.0, 0.1), Or, 0.05)
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.38, radius2=0.07, depth=1.3, location=(0, 0, 0.75))
    o = bpy.context.object
    bpy.ops.object.shade_smooth()
    o.data.materials.append(Or)
    for z, r in ((0.55, 0.3), (0.95, 0.19)):
        bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=r + 0.013, radius2=r - 0.027, depth=0.14, location=(0, 0, z))
        w = bpy.context.object
        bpy.ops.object.shade_smooth()
        w.data.materials.append(mat("white", (255, 255, 255), 0.4))
    sphere((0, 0, 1.4), (0.07, 0.07, 0.04), Or)
    frame(sc, pad=1.1)
    return sc


def confetti():
    sc = setup()
    random.seed(11)
    cols = [(255, 80, 90), (255, 200, 40), (60, 170, 255), (120, 210, 90), (200, 110, 240), (255, 140, 200)]
    for k in range(110):
        a = random.uniform(0, 2 * math.pi)
        r = random.uniform(0.05, 1.0) ** 0.6
        x, z = r * math.cos(a), 1.0 + r * math.sin(a)
        ci = (k + k // 6) % 6
        c = mat("cf%d" % ci, cols[ci], 0.35)
        rot = (random.uniform(0, 3), random.uniform(0, 3), random.uniform(0, 3))
        if k % 6 == 0:  # serpentinas
            t = torus((x, random.uniform(-0.2, 0.2), z), 0.09, 0.022, c, rot=rot)
        elif k % 6 == 3:  # circulitos
            sphere((x, random.uniform(-0.2, 0.2), z), (0.08, 0.08, 0.015), c, seg=20).rotation_euler = rot
        else:
            box((x, random.uniform(-0.2, 0.2), z), (0.17, 0.1, 0.015), c, 0.0, rot=rot)
    for k in range(8):  # estrellitas
        a = random.uniform(0, 2 * math.pi)
        r = random.uniform(0.3, 0.9)
        sphere((r * math.cos(a), -0.2, 1.0 + r * math.sin(a)), (0.05, 0.05, 0.05), mat("spark", (255, 240, 150), 0.2, emis=1.5))
    frame(sc, pad=1.08)
    return sc


def podium():
    sc = setup()
    steps = [(-0.9, 0.7, (200, 210, 225), "2"), (0.0, 1.05, (255, 200, 60), "1"), (0.9, 0.5, (230, 150, 90), "3")]
    for x, h, c, n in steps:
        box((x, 0, h / 2), (0.88, 0.8, h), mat("step" + n, c, 0.35), 0.05)
        box((x, 0, h - 0.03), (0.9, 0.82, 0.06), mat("top", (255, 255, 255), 0.4), 0.03)
        text(n, (x, -0.41, h * 0.5), 0.45, mat("num", (255, 255, 255), 0.4), extrude=0.03)
    frame(sc, pad=1.1)
    return sc


OBJS = {"finish": finish, "flag": flag, "sneakers": sneakers, "banana": banana, "water_bottle": water_bottle,
        "medal": medal, "trophy": trophy, "flower_big": flower_big, "start_line": start_line, "cone": traffic_cone,
        "confetti": confetti, "podium": podium}

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
