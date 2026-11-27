"""Más objetos 3D de las historias (día 3 en adelante). Mismo estilo y luz que objetos.py.

Uso: python3 objetos2.py CARPETA_SALIDA [objeto ...]
"""
import math
import os
import random

import objetos as O
from objetos import box, cam, setup
from modelos import mat, sphere, cyl, torus, cone
import modelos as M


def kite():
    sc = setup()
    import bpy
    cols = [(255, 80, 90), (255, 200, 40), (60, 170, 255), (120, 210, 90)]
    # rombo: 4 triángulos de colores alrededor del centro (malla plana)
    z0 = 1.2
    pts = [(0, 0, z0 + 0.62), (0.45, 0, z0 + 0.1), (0, 0, z0 - 0.75), (-0.45, 0, z0 + 0.1)]
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        me = bpy.data.meshes.new(f"kt{i}")
        me.from_pydata([(0, 0, z0 + 0.1), a, b], [], [(0, 1, 2)])
        ob = bpy.data.objects.new(f"kt{i}", me)
        bpy.context.scene.collection.objects.link(ob)
        sol = ob.modifiers.new("sol", "SOLIDIFY")
        sol.thickness = 0.03
        ob.data.materials.append(mat(f"k{i}", cols[i], 0.4))
    cyl((0, -0.03, 1.12), 0.02, 1.35, mat("stick", (150, 100, 60), 0.6))
    cyl((0, -0.03, 1.3), 0.02, 0.9, mat("stick", (150, 100, 60), 0.6), rot=(0, math.radians(90), 0))
    for k in range(5):  # cola con moñitos
        z = 0.5 - k * 0.22
        x = 0.08 * math.sin(k * 1.3)
        sphere((x, 0, z), (0.02, 0.02, 0.11), mat("tail", (90, 90, 110), 0.6))
        for s in (-1, 1):
            cone((x + s * 0.07, 0, z), 0.07, 0.0, 0.12, mat(f"bow{k}", cols[k % 4], 0.5), rot=(0, math.radians(90 * s), 0))
    cam(sc, (0, 0, 0.85), 2.2, height=1.0)
    return sc


def raincloud():
    sc = setup()
    C = mat("rcloud", (110, 130, 190), 0.8)
    for (x, z, r) in [(-0.5, 1.2, 0.35), (-0.1, 1.38, 0.45), (0.35, 1.25, 0.38), (0.0, 1.1, 0.4), (0.6, 1.1, 0.28), (-0.7, 1.05, 0.25)]:
        sphere((x, 0, z), (r, r * 0.8, r * 0.85), C)
    D = mat("drop", (80, 170, 255), 0.1, alpha=0.85)
    random.seed(4)
    for k in range(9):
        x = -0.6 + k * 0.15 + random.uniform(-0.04, 0.04)
        z = 0.55 + random.uniform(-0.25, 0.15)
        sphere((x, 0, z), (0.05, 0.05, 0.07), D)
        cone((x, 0, z + 0.08), 0.045, 0.0, 0.1, D)
    cam(sc, (0, 0, 1.0), 2.3, height=1.3)
    return sc


def flashlight():
    sc = setup()
    import bpy
    Y = mat("flash", (255, 205, 40), 0.35)
    cyl((0, 0, 0.5), 0.16, 0.9, Y, rot=(0, math.radians(90), 0))
    cyl((0.5, 0, 0.5), 0.24, 0.18, Y, rot=(0, math.radians(90), 0))
    cyl((0.6, 0, 0.5), 0.2, 0.03, mat("lens", (255, 255, 220), 0.1, emis=3), rot=(0, math.radians(90), 0))
    box((-0.05, -0.15, 0.5), (0.15, 0.06, 0.1), mat("button", (230, 60, 60), 0.4), 0.03)
    beam = cone((1.35, 0, 0.5), 0.12, 0.55, 1.4, mat("beam", (255, 250, 190), 0.1, emis=1.5, alpha=0.28),
                rot=(0, math.radians(-90), 0))
    cam(sc, (0.45, 0, 0.5), 2.4, height=0.9)
    return sc


def teddy():
    sc = setup()
    B = mat("bear", (190, 120, 70), 0.8)
    L = mat("bearl", (240, 200, 150), 0.8)
    sphere((0, 0, 0.45), (0.38, 0.33, 0.42), B)
    sphere((0, -0.22, 0.42), (0.22, 0.12, 0.26), L)
    sphere((0, 0, 1.02), (0.32, 0.3, 0.3), B)
    sphere((0, -0.24, 0.95), (0.14, 0.1, 0.1), L)
    sphere((0, -0.34, 0.99), (0.05, 0.03, 0.04), mat("nose", (60, 35, 30), 0.3))
    for x in (-0.12, 0.12):
        sphere((x, -0.27, 1.1), (0.04, 0.02, 0.05), mat("beye", (30, 25, 30), 0.2))
    for x in (-0.25, 0.25):
        sphere((x, 0, 1.28), (0.12, 0.08, 0.12), B)
        sphere((x, -0.04, 1.28), (0.07, 0.04, 0.07), L)
        sphere((x * 1.5, -0.08, 0.55), (0.12, 0.12, 0.22), B)
        sphere((x * 0.9, -0.25, 0.12), (0.14, 0.2, 0.11), B)
    torus((0, -0.05, 0.78), 0.2, 0.05, mat("ribbon", (255, 80, 140), 0.4), rot=(math.radians(80), 0, 0))
    cam(sc, (0, 0, 0.7), 1.8, height=1.2)
    return sc


def book():
    sc = setup()
    cov = mat("cover", (60, 140, 255), 0.5)
    for s in (-1, 1):
        o = box((s * 0.42, 0, 0.12), (0.84, 1.1, 0.05), cov, 0.03)
        o.rotation_euler = (0, s * math.radians(-12), 0)
        p = box((s * 0.4, -0.01, 0.17), (0.78, 1.02, 0.06), mat("page", (255, 252, 240), 0.7), 0.02)
        p.rotation_euler = (0, s * math.radians(-12), 0)
    sphere((-0.4, -0.05, 0.28), (0.14, 0.14, 0.02), mat("sunp", (255, 200, 40), 0.5))
    sphere((0.35, -0.05, 0.27), (0.2, 0.25, 0.02), mat("treep", (90, 190, 90), 0.5))
    cam(sc, (0, 0, 0.2), 1.9, height=2.2)
    return sc


def rainbow():
    sc = setup()
    cols = [(255, 70, 80), (255, 150, 40), (255, 220, 50), (90, 200, 90), (60, 150, 255), (150, 90, 230)]
    for i, c in enumerate(cols):
        torus((0, 0, 0), 1.6 - i * 0.14, 0.075, mat(f"rb{i}", c, 0.4), rot=(math.radians(90), 0, 0), arc=(0, 0, 1))
    W = mat("rbcloud", (255, 255, 255), 0.8)
    for x in (-1.25, 1.25):
        for (dx, dz, r) in [(-0.2, 0.05, 0.22), (0.05, 0.15, 0.28), (0.3, 0.05, 0.2)]:
            sphere((x + dx, -0.1, dz), (r, r * 0.8, r * 0.8), W)
    cam(sc, (0, 0, 0.75), 3.6, height=0.8)
    return sc


def umbrella():
    sc = setup()
    import bpy
    cols = [(255, 80, 90), (255, 210, 50), (60, 170, 255), (120, 210, 90)]
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=(0, 0, 1.2))
    o = bpy.context.object
    o.scale = (0.8, 0.8, 0.45)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.bisect(plane_co=(0, 0, 1.2), plane_no=(0, 0, 1), clear_inner=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat("umb", cols[0], 0.4))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        sphere((0.62 * math.cos(a), 0.62 * math.sin(a), 1.32), (0.12, 0.12, 0.08), mat(f"ud{i % 4}", cols[(i + 1) % 4], 0.4))
    cyl((0, 0, 0.7), 0.025, 1.1, mat("handle", (120, 80, 50), 0.5))
    torus((0.08, 0, 0.15), 0.08, 0.025, mat("handle", (120, 80, 50), 0.5), rot=(math.radians(90), 0, 0))
    cam(sc, (0, 0, 0.85), 2.0, height=1.3)
    return sc


OBJS = dict(kite=kite, raincloud=raincloud, flashlight=flashlight, teddy=teddy, book=book, rainbow=rainbow,
            umbrella=umbrella)

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
