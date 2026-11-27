"""Escenarios 3D de Bombolín (Blender / bpy). Se renderizan una vez por tema y orientación,
con el cielo transparente; después se combinan con un cielo de dibujo animado (degradé + estrellas).

Uso: python3 escenarios.py CARPETA_SALIDA [tema ...]
Temas: meadow room bath night snow xmas cave sea show
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

OUT = sys.argv[1]
ONLY = sys.argv[2:]
os.makedirs(OUT, exist_ok=True)
_m = {}


def srgb2lin(v):
    """Colores sRGB (0-255) a lineal, como los usa Blender: así salen vivos y no lavados."""
    v = v / 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def reset(w, h):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = 24
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = 0.3
    wd = bpy.data.worlds.new("w")
    wd.use_nodes = True
    wd.node_tree.nodes["Background"].inputs[1].default_value = 0.45
    sc.world = wd
    _m.clear()
    return sc


def mat(name, col, rough=0.6, emis=0.0, alpha=1.0):
    k = (name, col, rough, emis, alpha)
    if k in _m:
        return _m[k]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    c = tuple(srgb2lin(x) for x in col) + (1,)
    b.inputs["Base Color"].default_value = c
    b.inputs["Roughness"].default_value = rough
    if emis:
        b.inputs["Emission Color"].default_value = c
        b.inputs["Emission Strength"].default_value = emis
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
    _m[k] = m
    return m


def sph(loc, sc, m, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, location=loc)
    o = bpy.context.object
    o.scale = sc
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


def cyl(loc, r, d, m, rot=(0, 0, 0), v=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.object
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


def cone(loc, r1, r2, d, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=r1, radius2=r2, depth=d, location=loc, rotation=rot)
    o = bpy.context.object
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


def cube(loc, sc, m, bevel=0.05):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.scale = sc
    o.data.materials.append(m)
    b = o.modifiers.new("b", "BEVEL")
    b.width, b.segments = bevel, 3
    return o


def ground(m, size=80, bumps=0.25, z=0):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=120, y_subdivisions=120, size=size, location=(0, 0, z))
    o = bpy.context.object
    t = bpy.data.textures.new("g", "CLOUDS")
    t.noise_scale = 6
    d = o.modifiers.new("d", "DISPLACE")
    d.texture, d.strength = t, bumps
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


def look(o, target):
    o.rotation_euler = (Vector(target) - o.location).to_track_quat("-Z", "Y").to_euler()


def camera(sc, portrait):
    c = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(c)
    c.location = (0, -10, 2.2)
    c.data.lens = 30 if portrait else 32
    look(c, (0, 6, 1.3 if not portrait else 2.4))
    sc.camera = c


def sun(sc, energy=3.5, color=(1, 0.95, 0.88), rot=(0.9, 0.2, 0.6)):
    L = bpy.data.lights.new("sun", "SUN")
    L.energy, L.color, L.angle = energy, color, 0.2
    o = bpy.data.objects.new("sun", L)
    sc.collection.objects.link(o)
    o.rotation_euler = rot


def tree(x, y, s=1.0, snowy=False, pine=False, col=(70, 190, 75), fruit=None):
    cyl((x, y, 0.8 * s), 0.18 * s, 1.6 * s, mat("trunk", (140, 95, 55)))
    if pine:
        for k in range(3):
            cone((x, y, (1.6 + k * 0.8) * s), (1.3 - k * 0.35) * s, 0.05, 1.3 * s,
                 mat("snowpine" if snowy else "pine", (235, 245, 255) if snowy else (60, 150, 90)))
        return
    for (dx, dz, r) in [(0, 2.4, 1.0), (-0.6, 2.0, 0.75), (0.6, 2.0, 0.75), (0, 2.9, 0.7)]:
        sph((x + dx * s, y, dz * s), (r * s, r * s, r * s), mat(f"leaves{col}", col, 0.8))
    if fruit:
        for (dx, dz) in [(-0.7, 2.1), (0.5, 2.6), (0.75, 1.8), (-0.3, 3.0), (0.1, 2.0)]:
            sph((x + dx * s, y - 0.75 * s, dz * s), (0.13 * s,) * 3, mat(f"fruit{fruit}", fruit, 0.35), seg=16)


def flowers(n, area, seed=1, C=lambda c: c):
    rnd = random.Random(seed)
    cols = [(255, 120, 150), (255, 225, 80), (255, 255, 255), (180, 140, 255), (255, 160, 70)]
    for _ in range(n):
        x, y = rnd.uniform(*area[0]), rnd.uniform(*area[1])
        cyl((x, y, 0.15), 0.015, 0.3, mat("stem", C((70, 160, 70))))
        c = cols[rnd.randint(0, 4)]
        sph((x, y, 0.32), (0.11, 0.11, 0.07), mat(f"fl{c}", C(c), 0.5))


def clouds(seed=2, z=7):
    rnd = random.Random(seed)
    mb = bpy.data.metaballs.new("clouds")
    mb.resolution = 0.3
    mb.render_resolution = 0.2
    ob = bpy.data.objects.new("clouds", mb)
    bpy.context.scene.collection.objects.link(ob)
    for cx, cy in [(-9, 30), (6, 34), (16, 26), (-18, 24)]:
        for _ in range(5):
            e = mb.elements.new()
            e.co = (cx + rnd.uniform(-2.5, 2.5), cy, z + rnd.uniform(-0.5, 0.8))
            e.radius = rnd.uniform(1.4, 2.2)
    ob.data.materials.append(mat("cloud", (255, 255, 255), 0.9, emis=0.4))
    ob.visible_shadow = False


def hills(colors):
    for (x, y, sx, sz, c) in [(-14, 30, 16, 5, colors[0]), (10, 34, 20, 6, colors[1]), (0, 40, 30, 7, colors[0])]:
        sph((x, y, -1), (sx, 6, sz), mat("hill" + str(c), c, 0.9), seg=48)


# ------------------------------------------------------------------ ayudas de decorado
def rod(p1, p2, r, m, v=16):
    """Cilindro entre dos puntos (barras, caños, piolines)."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    o = cyl((p1 + p2) / 2, r, d.length, m, v=v)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o


def torus(loc, R, r, m, rot=(0, 0, 0), sc=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=48, minor_segments=16,
                                     location=loc, rotation=rot)
    o = bpy.context.object
    if sc:
        o.scale = sc
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


def disc(loc, r, m, depth=0.04, sc=(1, 1, 1), v=32):
    """Círculo plano pegado a una pared que mira hacia la cámara (-Y)."""
    o = cyl(loc, r, depth, m, rot=(math.pi / 2, 0, 0), v=v)
    o.scale = sc
    return o


def flat(verts, m, loc=(0, 0, 0), thick=0.04):
    """Figura plana (en el plano XZ) con grosor: banderines, techos, triángulos."""
    me = bpy.data.meshes.new("flat")
    me.from_pydata([(x, 0, z) for x, z in verts], [], [list(range(len(verts)))])
    o = bpy.data.objects.new("flat", me)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    s = o.modifiers.new("s", "SOLIDIFY")
    s.thickness = thick
    o.data.materials.append(m)
    return o


def star(loc, r, m, depth=0.06, inner=0.48, spin=0.0):
    """Estrellita de 5 puntas con relieve redondeado, mirando hacia la cámara."""
    pts = []
    for k in range(10):
        a = math.pi / 2 + spin + k * math.pi / 5
        rr = r if k % 2 == 0 else r * inner
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    o = flat(pts, m, loc, depth)
    b = o.modifiers.new("b", "BEVEL")
    b.width, b.segments = min(depth * 0.45, r * 0.1), 3
    return o


def tiles(name, c1, c2, grout, size=0.8, plane="wall", rough=0.25):
    """Azulejos redondeados (textura de ladrillos sin desfase) en metros reales del objeto."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    if plane == "wall":
        add = nt.nodes.new("ShaderNodeMath")
        add.operation = "ADD"
        nt.links.new(sep.outputs[0], add.inputs[0])
        nt.links.new(sep.outputs[1], add.inputs[1])
        nt.links.new(add.outputs[0], comb.inputs[0])
        nt.links.new(sep.outputs[2], comb.inputs[1])
    else:
        nt.links.new(sep.outputs[0], comb.inputs[0])
        nt.links.new(sep.outputs[1], comb.inputs[1])
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.0
    br.inputs["Color1"].default_value = tuple(srgb2lin(x) for x in c1) + (1,)
    br.inputs["Color2"].default_value = tuple(srgb2lin(x) for x in c2) + (1,)
    br.inputs["Mortar"].default_value = tuple(srgb2lin(x) for x in grout) + (1,)
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = 0.035 * size
    br.inputs["Mortar Smooth"].default_value = 0.6
    br.inputs["Brick Width"].default_value = size
    br.inputs["Row Height"].default_value = size
    br.inputs["Bias"].default_value = 0.0
    nt.links.new(comb.outputs[0], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.invert = True
    nt.links.new(br.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def slab(loc, sc, m, bevel=0.05):
    """Cubo con la escala aplicada (para que los azulejos midan lo mismo en todas las paredes)."""
    o = cube(loc, sc, m, bevel)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return o


def bunting(x0, x1, z, y, sag, cols, n=None, size=0.45):
    """Guirnalda de banderines entre dos puntos de la pared."""
    n = n or int((x1 - x0) / 0.9)
    pts = []
    for k in range(41):
        t = k / 40
        pts.append((x0 + (x1 - x0) * t, z - sag * 4 * t * (1 - t)))
    for k in range(40):
        rod((pts[k][0], y, pts[k][1]), (pts[k + 1][0], y, pts[k + 1][1]), 0.025, mat("string", (250, 250, 250), 0.6), v=8)
    for k in range(n):
        t = (k + 0.5) / n
        x, zz = x0 + (x1 - x0) * t, z - sag * 4 * t * (1 - t)
        flat([(-size / 2, 0), (size / 2, 0), (0, -size * 1.25)], mat(f"flag{k % len(cols)}", cols[k % len(cols)], 0.7),
             (x, y - 0.03, zz - 0.02), 0.03)


def potted_plant(x, y, z=0.0, s=1.0, pot=(240, 130, 90), leaf=(80, 185, 95), seed=4):
    rnd = random.Random(seed)
    cone((x, y, z + 0.4 * s), 0.38 * s, 0.5 * s, 0.8 * s, mat(f"pot{pot}", pot, 0.6))
    torus((x, y, z + 0.8 * s), 0.5 * s, 0.07 * s, mat(f"pot{pot}", pot, 0.6))
    for k in range(9):
        a = k * 2 * math.pi / 9 + rnd.uniform(-0.2, 0.2)
        h = rnd.uniform(0.9, 1.5) * s
        tip = (x + math.cos(a) * 0.55 * s, y + math.sin(a) * 0.35 * s, z + 0.8 * s + h)
        rod((x, y, z + 0.8 * s), tip, 0.03 * s, mat("plantstem", (70, 150, 70)), v=8)
        o = sph(tip, (0.28 * s, 0.13 * s, 0.42 * s), mat(f"leaf{leaf}", leaf, 0.6), seg=16)
        o.rotation_euler = (0, -math.cos(a) * 0.6, 0)


def hanging_plant(x, y, ztop, drop, s=1.0, pot=(255, 255, 255), leaf=(90, 195, 100), seed=8):
    """Macetita colgante con hojas que caen."""
    rnd = random.Random(seed)
    zp = ztop - drop
    for a in (0, 2.1, 4.2):
        rod((x, y, ztop), (x + 0.35 * s * math.cos(a), y + 0.35 * s * math.sin(a), zp + 0.3 * s), 0.015,
            mat("rope", (230, 200, 150), 0.8), v=6)
    sph((x, y, zp), (0.45 * s, 0.45 * s, 0.35 * s), mat(f"hpot{pot}", pot, 0.5))
    for k in range(7):
        a = k * 2 * math.pi / 7
        sx, sy = x + 0.42 * s * math.cos(a), y + 0.3 * s * math.sin(a)
        L = rnd.uniform(0.6, 1.4) * s
        for j in range(int(L / 0.22) + 1):
            sph((sx + rnd.uniform(-0.05, 0.05), sy, zp + 0.25 * s - j * 0.22), (0.13 * s, 0.08 * s, 0.11 * s),
                mat(f"hleaf{leaf}", leaf, 0.6), seg=12)
    sph((x, y, zp + 0.3 * s), (0.4 * s, 0.35 * s, 0.2 * s), mat(f"hleaf{leaf}", leaf, 0.6), seg=16)


def area_light(loc, energy, size, color=(1, 1, 1)):
    L = bpy.data.lights.new("area", "AREA")
    L.energy, L.size, L.color = energy, size, color
    o = bpy.data.objects.new("area", L)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    return o


def strip_on(ground_obj, pts, width, m, n=90, lift=0.04):
    """Senderito: cinta suave (Catmull-Rom) apoyada sobre el pasto con shrinkwrap."""
    P = [Vector((p[0], p[1], 0)) for p in pts]
    P = [P[0]] + P + [P[-1]]
    cen = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n // (len(P) - 3)):
            t = k / (n // (len(P) - 3))
            cen.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    cen.append(P[-2])
    verts, faces, across = [], [], 6
    for i, c in enumerate(cen):
        d = (cen[min(i + 1, len(cen) - 1)] - cen[max(i - 1, 0)]).normalized()
        nrm = Vector((-d.y, d.x, 0))
        w = width(i / (len(cen) - 1)) if callable(width) else width
        for j in range(across + 1):
            verts.append(c + nrm * w * (j / across - 0.5) + Vector((0, 0, 0.3)))
    for i in range(len(cen) - 1):
        for j in range(across):
            a = i * (across + 1) + j
            faces.append([a, a + 1, a + across + 2, a + across + 1])
    me = bpy.data.meshes.new("path")
    me.from_pydata([tuple(v) for v in verts], [], faces)
    o = bpy.data.objects.new("path", me)
    bpy.context.scene.collection.objects.link(o)
    sw = o.modifiers.new("sw", "SHRINKWRAP")
    sw.target, sw.wrap_method, sw.offset = ground_obj, "PROJECT", lift
    sw.use_negative_direction, sw.use_project_z = True, True
    o.data.materials.append(m)
    for p in me.polygons:
        p.use_smooth = True
    return o


# ------------------------------------------------------------------ temas
def meadow(portrait, night=False):
    def C(c):
        """En la noche, todo más oscuro y azulado."""
        return c if not night else tuple(int(v * 0.38 + k) for v, k in zip(c, (22, 34, 70)))

    g = ground(mat("grass", C((165, 225, 85)), 0.9))
    # lomas lejanas en capas de distintos verdes (más azuladas cuanto más lejos)
    for (x, y, sx, sz, c) in [(-22, 52, 22, 9, (150, 205, 170)), (8, 56, 26, 10, (140, 195, 175)),
                              (30, 50, 18, 8, (155, 210, 165)),
                              (-14, 30, 16, 5, (125, 210, 115)), (10, 34, 20, 6, (100, 190, 95)),
                              (0, 40, 30, 7, (115, 200, 105)), (24, 28, 12, 4, (150, 215, 95)),
                              (-28, 34, 14, 6, (90, 180, 110))]:
        sph((x, y, -1), (sx, 6, sz), mat("hill" + str(c), C(c), 0.9), seg=48)
    # senderito de tierra que se pierde entre las lomas
    strip_on(g, [(0.5, -6), (0.0, 2), (2.2, 9), (0.5, 15), (-1.5, 21), (0.5, 28)],
             lambda t: 2.4 * (1 - t) + 0.7 * t, mat("path", C((240, 205, 140)), 0.95))
    # árboles redondos de distintos verdes, algunos con manzanas
    for (x, y, s, col, fruit) in [(-7, 7, 1.0, (70, 190, 75), True), (7.5, 9, 1.2, (95, 200, 70), False),
                                  (-11, 14, 1.3, (60, 175, 90), False), (12, 16, 1.1, (80, 195, 85), True),
                                  (-3.5, 20, 1.0, (110, 205, 80), False), (4, 22, 0.9, (65, 180, 95), False),
                                  (-15, 22, 1.4, (85, 190, 80), False), (16, 24, 1.3, (70, 175, 95), False)]:
        tree(x, y, s, col=C(col), fruit=C((255, 80, 80)) if fruit else None)
    # arbustos con florcitas
    rnd = random.Random(11)
    for (x, y, r) in [(-5.5, 3.5, 0.9), (5.6, 4.2, 0.85), (-8.5, 10, 1.0), (9.5, 12, 1.0), (-9.5, 4, 1.1)]:
        sph((x, y, 0.3), (r, 0.85 * r, 0.65 * r), mat("bush", C((95, 195, 70)), 0.85))
        sph((x + 0.5 * r, y - 0.2, 0.25), (0.6 * r, 0.55 * r, 0.5 * r), mat("bush2", C((115, 205, 75)), 0.85))
        for k in range(6):
            a = rnd.uniform(0.3, math.pi - 0.3)
            sph((x + math.cos(a) * r * 0.85, y - 0.6 * r, 0.3 + math.sin(a) * 0.5 * r), (0.09,) * 3,
                mat("berry" + str(k % 2), C([(255, 255, 255), (255, 130, 170)][k % 2]), 0.4), seg=12)
    # laguna con nenúfares y juncos, al fondo a la izquierda
    cyl((-6.5, 16, 0.0), 1.0, 0.3, mat("pond", C((90, 190, 240)), 0.08), v=64).scale = (3.6, 1.9, 1)
    torus((-6.5, 16, 0.13), 1.0, 0.06, mat("pondrim", C((140, 200, 120)), 0.8), sc=(3.65, 1.95, 1.5))
    for (dx, dy, r) in [(-1.6, 0.3, 0.38), (1.2, -0.6, 0.32), (0.3, 0.8, 0.28), (2.2, 0.4, 0.25)]:
        cyl((-6.5 + dx, 16 + dy, 0.17), r, 0.03, mat("lily", C((80, 175, 85)), 0.6))
    sph((-6.5 - 1.6, 16.3, 0.24), (0.14, 0.14, 0.1), mat("lilyfl", C((255, 160, 200)), 0.5), seg=16)
    for k in range(7):
        x = -10.3 + k * 0.18 + rnd.uniform(-0.05, 0.05)
        h = rnd.uniform(0.9, 1.6)
        rod((x, 16.6, 0), (x + rnd.uniform(-0.15, 0.15), 16.6, h), 0.035, mat("reed", C((90, 160, 70))), v=8)
        if k % 2 == 0:
            cyl((x, 16.6, h - 0.15), 0.07, 0.35, mat("cattail", C((150, 95, 60)), 0.8), v=12)
    # cerquita de madera a la derecha, en diagonal
    for k in range(9):
        x, y = 5.5 + k * 0.85, 6.0 + k * 0.55
        cube((x, y, 0.55), (0.14, 0.08, 0.55), mat("fence", C((255, 250, 240)), 0.6), 0.06)
        cone((x, y, 1.18), 0.2, 0.0, 0.2, mat("fence", C((255, 250, 240)), 0.6), rot=(0, 0, math.pi / 4)).scale = (0.7, 0.4, 1)
    for z in (0.4, 0.85):
        rod((5.3, 5.85, z), (12.5, 10.5, z), 0.07, mat("fencebar", C((250, 240, 225)), 0.6), v=12)
    # hongos de sombrero rojo con lunares
    for (x, y, s) in [(-4.0, 1.2, 0.9), (-3.4, 1.7, 0.6), (4.6, 1.3, 0.75), (8.5, 7.5, 0.8), (-12, 9, 1.0)]:
        cyl((x, y, 0.25 * s), 0.12 * s, 0.5 * s, mat("mstem", C((255, 245, 225)), 0.6))
        cap = sph((x, y, 0.5 * s), (0.42 * s, 0.42 * s, 0.3 * s), mat("mcap", C((240, 70, 70)), 0.45))
        for k in range(5):
            a = k * 2 * math.pi / 5 + 0.4
            sph((x + 0.27 * s * math.cos(a), y + 0.27 * s * math.sin(a) - 0.05, 0.66 * s),
                (0.07 * s, 0.07 * s, 0.04 * s), mat("mdot", C((255, 255, 255)), 0.5), seg=10)
        sph((x, y - 0.1 * s, 0.72 * s), (0.08 * s,) * 3, mat("mdot", C((255, 255, 255)), 0.5), seg=10)
    # piedras redondas
    for (x, y, r) in [(3.6, 2.6, 0.45), (4.2, 2.9, 0.28), (-9, 8, 0.7), (-8.3, 8.2, 0.4), (10.5, 14, 0.8), (-5, 14.2, 0.5)]:
        sph((x, y, 0.08), (r, 0.85 * r, 0.6 * r), mat("rock", C((175, 170, 190)), 0.85), seg=20)
    # ramilletes de flores grandes a los costados
    cols = [(255, 120, 160), (255, 220, 70), (255, 255, 255), (185, 140, 255), (255, 150, 60), (120, 190, 255)]
    for (cx, cy, n, sd) in [(-4.8, 0.2, 9, 1), (4.9, -0.5, 9, 2), (-7.2, 2.6, 8, 3), (7.4, 2.8, 8, 4),
                            (-2.8, 5.5, 6, 5), (3.2, 7.2, 6, 6), (-10.5, 7, 7, 7), (11.5, 9, 7, 8),
                            (-1.8, 11, 6, 9), (6.5, 13, 6, 10), (-3.0, 3.6, 5, 11), (3.1, 4.0, 5, 12)]:
        rr = random.Random(sd)
        for _ in range(n):
            x, y = cx + rr.uniform(-0.9, 0.9), cy + rr.uniform(-0.6, 0.6)
            big_flower(x, y, rr.uniform(0.35, 0.65), C(cols[rr.randint(0, 5)]), C, rr)
    flowers(40, ((-9, 9), (1, 14)), C=C)
    # mariposas
    if not night:
        for (x, y, z, c) in [(-3, 4, 2.8, (255, 150, 200)), (3.5, 8, 3.4, (255, 210, 80)), (-6, 12, 3.8, (150, 200, 255))]:
            for s in (-1, 1):
                o = sph((x + s * 0.17, y, z), (0.18, 0.03, 0.14), mat(f"bfly{c}", c, 0.5), seg=12)
                o.rotation_euler = (0, s * 0.4, 0)
            sph((x, y, z), (0.03, 0.03, 0.12), mat("bbody", (70, 60, 80)), seg=8)
        clouds()
        sph((14, 40, 14), (2.2, 2.2, 2.2), mat("sunball", (255, 225, 90), 0.5, emis=3))
    else:
        sph((-12, 40, 14), (2.0, 2.0, 2.0), mat("moon", (255, 245, 200), 0.5, emis=2.5))


def big_flower(x, y, h, col, C, rr):
    """Flor de dibujo: tallo, hojita, 5 pétalos redondos y centro amarillo."""
    m = mat(f"petal{col}", col, 0.5)
    cyl((x, y, h / 2), 0.022, h, mat("stem", C((70, 160, 70))), v=8)
    o = sph((x + 0.07, y, h * 0.4), (0.1, 0.03, 0.05), mat("stem", C((70, 160, 70))), seg=10)
    o.rotation_euler = (0, -0.6, 0)
    s = rr.uniform(0.85, 1.25)
    for k in range(5):
        a = k * 2 * math.pi / 5 + rr.uniform(0, 1)
        sph((x + 0.11 * s * math.cos(a), y - 0.02, h + 0.11 * s * math.sin(a)), (0.09 * s, 0.04 * s, 0.09 * s), m, seg=12)
    sph((x, y - 0.05, h), (0.07 * s, 0.05 * s, 0.07 * s),
        mat("fcenter", C((255, 200, 60)) if col != C((255, 220, 70)) else C((255, 140, 60)), 0.5), seg=12)


def room(portrait):
    wood = bpy.data.materials.new("wood")
    wood.use_nodes = True
    nt = wood.node_tree
    b = nt.nodes["Principled BSDF"]
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.inputs["Scale"].default_value = 8.0
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].color = (0.66, 0.43, 0.25, 1)
    rp.color_ramp.elements[1].color = (0.85, 0.62, 0.40, 1)
    nt.links.new(wv.outputs["Fac"], rp.inputs["Fac"])
    nt.links.new(rp.outputs["Color"], b.inputs["Base Color"])
    bpy.ops.mesh.primitive_plane_add(size=40)
    bpy.context.object.data.materials.append(wood)
    WALL, WALL2 = (255, 236, 150), (255, 214, 120)
    cube((0, 9, 8), (20, 0.2, 9), mat("wall", WALL, 0.9), 0.01)
    cube((-11, 0, 8), (0.2, 20, 9), mat("wall2", WALL2, 0.9), 0.01)
    cube((11, 0, 8), (0.2, 20, 9), mat("wall2", WALL2, 0.9), 0.01)
    # zócalo de friso celeste con moldura blanca
    cube((0, 8.78, 0.9), (20, 0.06, 0.9), mat("wainscot", (150, 210, 245), 0.7), 0.02)
    rod((-20, 8.7, 1.82), (20, 8.7, 1.82), 0.09, mat("trim", (255, 255, 255), 0.4))
    for k in range(-24, 25):
        cube((k * 0.8, 8.72, 0.9), (0.03, 0.03, 0.8), mat("wainline", (130, 195, 235), 0.7), 0.01)
    # empapelado: lunares y estrellitas alternados
    rnd = random.Random(21)
    for row in range(12):
        z = 2.6 + row * 1.0
        for col in range(-12, 13):
            x = col * 1.0 + (0.5 if row % 2 else 0)
            if (col + row) % 2:
                disc((x, 8.79, z), 0.12, mat("dot", (255, 255, 255), 0.8, emis=0.25), 0.02)
            else:
                star((x, 8.79, z), 0.16, mat("wstar", (255, 200, 110), 0.8), 0.02, spin=rnd.uniform(-0.3, 0.3))
    # ventana con cortinas a rayas, barral y una plantita en el alféizar
    WX = 3.2
    cube((WX, 8.7, 4.3), (1.9, 0.15, 1.5), mat("frame", (255, 255, 255), 0.4))
    cube((WX, 8.6, 4.3), (1.65, 0.12, 1.28), mat("glass", (150, 205, 255), 0.2, emis=0.45))
    cube((WX, 8.5, 4.3), (0.06, 0.06, 1.3), mat("frame", (255, 255, 255), 0.4))
    cube((WX, 8.5, 4.3), (1.65, 0.06, 0.06), mat("frame", (255, 255, 255), 0.4))
    cube((WX, 8.35, 2.72), (2.1, 0.35, 0.09), mat("frame", (255, 255, 255), 0.4))
    sph((WX - 0.9, 8.6, 5.0), (0.55, 0.05, 0.3), mat("wcloud", (255, 255, 255), 0.8, emis=0.3), seg=16)
    sph((WX - 0.5, 8.6, 5.1), (0.4, 0.05, 0.35), mat("wcloud", (255, 255, 255), 0.8, emis=0.3), seg=16)
    rod((WX - 2.7, 8.35, 6.1), (WX + 2.7, 8.35, 6.1), 0.06, mat("brass", (240, 190, 90), 0.3))
    for s in (-1, 1):
        sph((WX + s * 2.75, 8.35, 6.1), (0.13,) * 3, mat("brass", (240, 190, 90), 0.3))
        for k in range(4):
            x = WX + s * (1.85 + k * 0.28)
            o = cyl((x, 8.3 - 0.06 * (k % 2), 4.3), 0.17, 3.6, mat(f"curt{k % 2}", [(255, 140, 180), (255, 190, 215)][k % 2], 0.85), v=16)
            o.scale = (1, 0.8, 1)
        torus((WX + s * 2.25, 8.25, 3.6), 0.6, 0.05, mat("tie", (255, 230, 100), 0.5), rot=(math.pi / 2, 0, 0), sc=(1, 1, 0.3))
    potted_plant(WX + 1.1, 8.3, 2.8, 0.45, pot=(255, 160, 90), leaf=(90, 190, 90))
    # dibujito enmarcado (sol, loma y casita)
    FX, FZ = -2.6, 4.6
    cube((FX, 8.72, FZ), (1.15, 0.08, 0.9), mat("pframe", (120, 200, 255), 0.5), 0.06)
    cube((FX, 8.65, FZ), (0.98, 0.05, 0.74), mat("paper", (255, 255, 250), 0.9), 0.01)
    disc((FX + 0.55, 8.58, FZ + 0.38), 0.2, mat("dsun", (255, 210, 60), 0.6), 0.02)
    sph((FX, 8.6, FZ - 0.75), (0.98, 0.02, 0.45), mat("dhill", (120, 210, 110), 0.7), seg=24)
    cube((FX - 0.35, 8.57, FZ - 0.12), (0.28, 0.02, 0.24), mat("dhouse", (255, 110, 110), 0.6), 0.01)
    flat([(-0.38, 0), (0.38, 0), (0, 0.32)], mat("droof", (150, 110, 230), 0.6), (FX - 0.35, 8.56, FZ + 0.12), 0.02)
    # repisa juguetera (cubos) a la izquierda con bloques, pelota, libros y osito
    SX = -7.4
    cube((SX, 8.3, 1.95), (1.7, 0.45, 1.95), mat("cubby", (120, 195, 255), 0.5), 0.08)
    for (dx, dz) in [(-0.82, 1.0), (0.82, 1.0), (-0.82, 2.8), (0.82, 2.8)]:
        cube((SX + dx, 7.85, dz), (0.72, 0.1, 0.78), mat("cubbyin", (255, 250, 235), 0.7), 0.04)
    cube((SX - 0.82, 7.7, 0.55), (0.4, 0.3, 0.3), mat("bin1", (255, 120, 140), 0.5), 0.08)
    for k, c in enumerate([(255, 100, 100), (100, 170, 255), (120, 210, 120), (255, 220, 90), (190, 140, 255)]):
        cube((SX + 0.4 + k * 0.17, 7.6, 2.55 + 0.04 * (k % 2)), (0.07, 0.35, 0.5 + 0.06 * (k % 2)), mat(f"book{k}", c, 0.5), 0.02)
    for k, (dx, dz, c) in enumerate([(-1.15, 0.4, (255, 90, 90)), (-0.65, 0.4, (90, 160, 255)), (-0.9, 0.82, (255, 210, 70))]):
        cube((SX + dx + 0.18, 7.3, dz + 1.98), (0.2, 0.2, 0.2), mat(f"blk{k}", c, 0.45), 0.05)
    sph((SX + 0.82, 7.4, 0.7), (0.48,) * 3, mat("ball", (255, 90, 120), 0.4))
    for k in range(3):
        rod((SX + 0.82 + 0.48 * math.cos(k * 2.1), 7.4, 0.7 - 0.48), (SX + 0.82 + 0.48 * math.cos(k * 2.1 + 1), 7.4, 0.7 + 0.48),
            0.02, mat("ballstripe", (255, 255, 255)), v=6)
    # osito arriba del mueble
    TB = (255 * 0 + 205, 150, 95)
    sph((SX + 0.5, 8.0, 4.35), (0.42, 0.35, 0.45), mat("teddy", TB, 0.9))
    sph((SX + 0.5, 7.95, 5.0), (0.34,) * 3, mat("teddy", TB, 0.9))
    for s in (-1, 1):
        sph((SX + 0.5 + s * 0.26, 7.95, 5.28), (0.12, 0.08, 0.12), mat("teddy", TB, 0.9), seg=12)
        sph((SX + 0.5 + s * 0.12, 7.65, 5.05), (0.04,) * 3, mat("eye", (40, 30, 30), 0.3), seg=8)
    sph((SX + 0.5, 7.65, 4.93), (0.12, 0.06, 0.09), mat("snout", (250, 215, 170), 0.8), seg=12)
    for k, c in enumerate([(255, 90, 90), (255, 210, 70), (100, 200, 120)]):
        cube((SX - 0.8 + k * 0.38, 8.0, 4.1 + 0.0), (0.16, 0.16, 0.16), mat(f"blk{k}", c, 0.45), 0.04)
    cube((SX - 0.6, 8.0, 4.43), (0.16, 0.16, 0.16), mat("blk1", (90, 160, 255), 0.45), 0.04)
    # baúl de juguetes con tapa y estrella
    cube((-5.2, 6.4, 0.75), (1.1, 0.7, 0.75), mat("toybox", (255, 190, 90), 0.5), 0.08)
    cube((-5.2, 6.4, 1.6), (1.18, 0.78, 0.12), mat("toylid", (255, 150, 80), 0.5), 0.06)
    star((-5.2, 5.66, 0.8), 0.38, mat("boxstar", (255, 255, 255), 0.5), 0.05)
    # camita baja a la derecha: cabecera redonda, colchón, frazada con lunares y almohada
    BX = 8.6
    cube((BX, 4.7, 0.45), (1.55, 2.8, 0.45), mat("bedframe", (150, 200, 255), 0.5), 0.12)
    cube((BX, 4.7, 1.0), (1.45, 2.7, 0.16), mat("mattress", (255, 255, 255), 0.8), 0.12)
    cube((BX, 4.0, 1.22), (1.55, 2.0, 0.14), mat("blanket", (255, 150, 190), 0.85), 0.14)
    for k in range(10):
        disc((BX - 1.2 + (k % 5) * 0.6, 2.0 - 0.01, 0.95 + 0.25 * (k // 5)), 0.08, mat("bdot", (255, 255, 255), 0.8), 0.02)
    sph((BX, 6.7, 1.35), (1.0, 0.45, 0.28), mat("pillow", (255, 250, 220), 0.9))
    cyl((BX, 7.55, 1.4), 1.55, 0.25, mat("bedframe", (150, 200, 255), 0.5), rot=(math.pi / 2, 0, 0), v=48)
    cube((BX, 7.55, 0.75), (1.55, 0.125, 0.75), mat("bedframe", (150, 200, 255), 0.5), 0.05)
    star((BX, 7.4, 1.95), 0.4, mat("bedstar", (255, 220, 90), 0.5), 0.06)
    cube((BX, 1.95, 0.8), (1.55, 0.12, 0.8), mat("bedframe", (150, 200, 255), 0.5), 0.1)
    # lámpara de pie al lado de la cama
    cyl((6.2, 7.9, 0.06), 0.4, 0.12, mat("lampstem", (240, 240, 240), 0.4))
    cyl((6.2, 7.9, 1.6), 0.06, 3.1, mat("lampstem", (240, 240, 240), 0.4))
    cone((6.2, 7.9, 3.3), 0.7, 0.38, 0.75, mat("lampshade", (255, 240, 180), 0.6, emis=0.8))
    # alfombra redonda con borde
    cyl((0, 2, 0.02), 4.5, 0.04, mat("rug", (255, 120, 175), 0.95), v=64)
    torus((0, 2, 0.05), 4.25, 0.12, mat("rugrim", (255, 255, 255), 0.95), sc=(1, 1, 0.4))
    torus((0, 2, 0.05), 3.4, 0.05, mat("rugrim2", (255, 190, 220), 0.95), sc=(1, 1, 0.4))
    # planta grande en el rincón izquierdo
    potted_plant(-9.6, 6.5, 0, 1.3, pot=(255, 255, 255), leaf=(70, 180, 90), seed=6)
    # guirnalda de banderines y móvil de estrellas (este se ve en el vertical)
    BC = [(255, 110, 140), (255, 210, 70), (110, 190, 255), (130, 215, 120), (190, 140, 255)]
    bunting(-10.5, 10.5, 6.8, 8.6, 0.2, BC, n=24, size=0.38)
    bunting(-6, 6, 11.0, 8.6, 0.5, BC[::-1], n=12, size=0.5)
    for k, (x, z, c) in enumerate([(-3.4, 8.6, (255, 210, 70)), (-1.2, 9.2, (255, 140, 180)), (1.3, 8.8, (120, 190, 255)),
                                   (3.6, 9.4, (255, 210, 70))]):
        rod((x, 8.2, 13), (x, 8.2, z + 0.3), 0.012, mat("string", (250, 250, 250), 0.6), v=6)
        star((x, 8.2, z), 0.4, mat(f"mob{c}", c, 0.4, emis=0.2), 0.12)
    star((-4.8, 8.7, 9.7), 0.7, mat("bigstar", (255, 170, 60), 0.5, emis=0.15), 0.1)
    area_light((0, 2, 9), 1100, 10)
    area_light((0, 3, 15), 900, 12, (1, 0.97, 0.9))
    area_light((0, -6, 5), 500, 8, (1, 0.95, 0.85)).rotation_euler = (math.radians(70), 0, 0)


def bath(portrait):
    """Baño alegre: azulejos celestes, espejo redondo, lavatorio, estante con patito, toallero y plantas.
    El centro de abajo queda libre: ahí se compone la bañera."""
    slab((0, 0, -0.1), (20, 20, 0.1), tiles("floortile", (255, 255, 255), (185, 228, 250), (160, 200, 225), 1.1, "floor", 0.3), 0.01)
    WT = tiles("walltile", (160, 218, 248), (175, 226, 252), (255, 255, 255), 0.7)
    PAINT = mat("bathpaint", (190, 240, 215), 0.9)
    slab((0, 9, 1.7), (20, 0.2, 1.7), WT, 0.01)
    cube((0, 9.02, 10.4), (20, 0.2, 7.0), PAINT, 0.01)
    for s in (-1, 1):
        slab((s * 11, 0, 1.7), (0.2, 20, 1.7), WT, 0.01)
        cube((s * 11.02, 0, 10.4), (0.2, 20, 7.0), PAINT, 0.01)
    # moldura amarilla sobre los azulejos y zócalo
    rod((-20, 8.78, 3.45), (20, 8.78, 3.45), 0.12, mat("btrim", (255, 215, 100), 0.4))
    for s in (-1, 1):
        rod((s * 10.78, -10, 3.45), (s * 10.78, 9, 3.45), 0.12, mat("btrim", (255, 215, 100), 0.4))
    # burbujas pintadas en la pared de arriba
    rnd = random.Random(31)
    for k in range(34):
        x, z = rnd.uniform(-11, 11), rnd.uniform(4.0, 15)
        if abs(x) < 1.6 and z < 7.4:
            continue
        r = rnd.uniform(0.12, 0.38)
        torus((x, 8.8, z), r, 0.03, mat("bubring", (255, 255, 255), 0.5), rot=(math.pi / 2, 0, 0))
        disc((x - r * 0.35, 8.79, z + r * 0.35), r * 0.22, mat("bubhl", (255, 255, 255), 0.5), 0.02)
    # ventanita redonda (ojo de buey) arriba en el centro, con cielo y nube
    torus((0, 8.75, 5.8), 1.0, 0.16, mat("wframe", (255, 255, 255), 0.35), rot=(math.pi / 2, 0, 0))
    disc((0, 8.77, 5.8), 1.0, mat("bglass", (120, 195, 255), 0.2, emis=0.6), 0.04)
    rod((-1.0, 8.75, 5.8), (1.0, 8.75, 5.8), 0.05, mat("wframe", (255, 255, 255), 0.35))
    rod((0, 8.75, 4.8), (0, 8.75, 6.8), 0.05, mat("wframe", (255, 255, 255), 0.35))
    sph((-0.4, 8.74, 6.25), (0.35, 0.03, 0.18), mat("wcloud", (255, 255, 255), 0.8, emis=0.4), seg=16)
    sph((0.45, 8.74, 5.3), (0.3, 0.03, 0.15), mat("wcloud", (255, 255, 255), 0.8, emis=0.4), seg=16)
    # espejo redondo con marco rosa y lavatorio con pie
    MX = -5.2
    torus((MX, 8.72, 5.1), 1.15, 0.17, mat("mframe", (255, 160, 190), 0.4), rot=(math.pi / 2, 0, 0))
    disc((MX, 8.77, 5.1), 1.15, mat("mirror", (185, 225, 250), 0.05, emis=0.35), 0.04)
    for (dx, dz, L) in [(-0.35, 0.35, 0.42), (0.05, 0.5, 0.22)]:
        o = sph((MX + dx, 8.73, 5.1 + dz), (L, 0.02, 0.07), mat("mhl", (255, 255, 255), 0.3, emis=0.6), seg=16)
        o.rotation_euler = (0, math.radians(40), 0)
    cone((MX, 8.2, 1.2), 0.35, 0.5, 2.4, mat("porcelain", (255, 255, 255), 0.25))
    o = sph((MX, 8.05, 2.55), (1.2, 0.75, 0.45), mat("porcelain", (255, 255, 255), 0.25))
    cyl((MX, 8.05, 2.95), 1.05, 0.12, mat("porcelain", (255, 255, 255), 0.25), v=48).scale = (1, 0.62, 1)
    cyl((MX, 8.0, 3.0), 0.95, 0.06, mat("basin", (170, 215, 240), 0.2), v=48).scale = (1, 0.55, 1)
    rod((MX, 8.6, 3.0), (MX, 8.6, 3.6), 0.07, mat("chrome", (220, 230, 240), 0.1))
    rod((MX, 8.6, 3.55), (MX, 8.2, 3.55), 0.06, mat("chrome", (220, 230, 240), 0.1))
    for s in (-1, 1):
        sph((MX + s * 0.35, 8.6, 3.2), (0.11,) * 3, mat(["hot", "cold"][s > 0], [(255, 110, 110), (110, 170, 255)][s > 0], 0.3))
    # vasito con cepillos y jabón líquido
    cyl((MX - 0.8, 8.4, 3.3), 0.15, 0.35, mat("cup", (130, 220, 180), 0.4))
    for k, c in enumerate([(255, 120, 160), (120, 180, 255)]):
        rod((MX - 0.8, 8.4, 3.3), (MX - 0.85 + 0.12 * k, 8.4, 3.85), 0.025, mat(f"brush{k}", c, 0.4), v=8)
        cube((MX - 0.85 + 0.12 * k, 8.38, 3.9), (0.03, 0.03, 0.08), mat("bristle", (255, 255, 255), 0.6), 0.01)
    cyl((MX + 0.85, 8.4, 3.35), 0.15, 0.45, mat("soap", (255, 170, 210), 0.3))
    rod((MX + 0.85, 8.4, 3.55), (MX + 0.85, 8.4, 3.75), 0.03, mat("chrome", (220, 230, 240), 0.1), v=8)
    rod((MX + 0.85, 8.4, 3.75), (MX + 0.85, 8.25, 3.75), 0.025, mat("chrome", (220, 230, 240), 0.1), v=8)
    # estante con botellas de champú y patito de goma
    HX, HZ = 4.1, 4.5
    cube((HX, 8.5, HZ), (1.35, 0.32, 0.07), mat("shelfb", (255, 255, 255), 0.4), 0.04)
    for s in (-1, 1):
        cone((HX + s * 1.0, 8.75, HZ - 0.25), 0.05, 0.15, 0.4, mat("chrome", (220, 230, 240), 0.1))
    for k, (dx, h, c) in enumerate([(-1.0, 0.75, (255, 120, 170)), (-0.55, 0.6, (120, 200, 255)),
                                    (-0.15, 0.85, (140, 220, 140))]):
        b = cube((HX + dx, 8.5, HZ + 0.07 + h / 2), (0.18, 0.13, h / 2), mat(f"bottle{k}", c, 0.3), 0.08)
        cyl((HX + dx, 8.5, HZ + 0.07 + h + 0.07), 0.08, 0.14, mat("cap", (255, 255, 255), 0.4))
        cube((HX + dx, 8.36, HZ + 0.07 + h * 0.45), (0.13, 0.01, 0.14), mat("label", (255, 255, 255), 0.6), 0.01)
    rubber_duck(HX + 0.75, 8.45, HZ + 0.07, 0.75)
    # toallero con toalla a rayas (se ve en el horizontal)
    TX = 7.9
    rod((TX - 1.3, 8.55, 3.0), (TX + 1.3, 8.55, 3.0), 0.06, mat("chrome", (220, 230, 240), 0.1))
    for s in (-1, 1):
        rod((TX + s * 1.3, 8.8, 3.0), (TX + s * 1.3, 8.55, 3.0), 0.06, mat("chrome", (220, 230, 240), 0.1))
    cyl((TX, 8.55, 3.0), 0.16, 1.9, mat("towel0", (255, 140, 120), 0.95), rot=(0, math.pi / 2, 0))
    for side, dy in ((1, 0.12), (-1, -0.12)):
        for k in range(6):
            col = [(255, 140, 120), (255, 255, 255), (255, 210, 90)][k % 3] if side < 0 else (255, 140, 120)
            cube((TX, 8.55 + dy, 2.85 - k * 0.27), (0.95, 0.05, 0.135), mat(f"towel{col}", col, 0.95), 0.04)
    # tapete de baño mullido y planta en el rincón
    cube((-4.6, 5.4, 0.04), (1.6, 0.9, 0.04), mat("bmat", (255, 150, 190), 0.95), 0.03)
    for k in range(5):
        cube((-4.6, 5.4 - 0.8 + k * 0.4, 0.07), (1.5, 0.08, 0.02), mat("bmatst", (255, 255, 255), 0.95), 0.02)
    for k in range(12):
        sph((-4.6 + (k - 5.5) * 0.28, 4.48, 0.04), (0.08, 0.08, 0.04), mat("bmat", (255, 150, 190), 0.95), seg=10)
    potted_plant(-9.4, 6.6, 0, 1.1, pot=(255, 200, 120), leaf=(80, 190, 110), seed=9)
    cyl((8.6, 6.4, 0.7), 0.75, 1.4, mat("basket", (255, 220, 170), 0.8), v=32)
    torus((8.6, 6.4, 1.4), 0.75, 0.09, mat("basketrim", (240, 180, 120), 0.8))
    sph((8.5, 6.3, 1.45), (0.55, 0.5, 0.25), mat("laundry", (150, 210, 255), 0.9))
    # plantas colgantes en las esquinas y una arriba en el centro (vertical)
    hanging_plant(-8.4, 6.0, 12, 7.2, 1.1, pot=(255, 255, 255), leaf=(90, 195, 100), seed=1)
    hanging_plant(8.2, 6.0, 12, 7.3, 1.0, pot=(255, 170, 200), leaf=(110, 200, 90), seed=2)
    # cuadrito con un pez (arriba, se ve en el vertical)
    cube((-2.8, 8.74, 9.2), (1.0, 0.06, 0.75), mat("pframe2", (255, 200, 90), 0.5), 0.06)
    cube((-2.8, 8.68, 9.2), (0.85, 0.03, 0.6), mat("sea", (130, 205, 255), 0.7), 0.01)
    sph((-2.9, 8.62, 9.2), (0.42, 0.03, 0.26), mat("fish", (255, 150, 70), 0.5), seg=20)
    flat([(0, 0), (0.3, 0.22), (0.3, -0.22)], mat("fish", (255, 150, 70), 0.5), (-2.52, 8.62, 9.2), 0.03)
    disc((-3.12, 8.59, 9.27), 0.05, mat("eye", (40, 30, 30), 0.3), 0.02)
    for (bx, bz, br) in [(-3.45, 9.5, 0.07), (-3.55, 9.68, 0.05)]:
        torus((bx, 8.62, bz), br, 0.015, mat("bubring", (255, 255, 255), 0.5), rot=(math.pi / 2, 0, 0))
    hanging_plant(3.6, 7.6, 15, 4.5, 1.0, pot=(255, 215, 100), leaf=(80, 190, 110), seed=3)
    # burbujas de jabón flotando (translúcidas)
    for k in range(10):
        x, y, z = rnd.uniform(-7, 7), rnd.uniform(4, 8), rnd.uniform(4.5, 12)
        if abs(x) < 2.2 and z < 7:
            continue
        o = sph((x, y, z), (rnd.uniform(0.12, 0.3),) * 3, mat("bubble", (225, 245, 255), 0.05, emis=0.2, alpha=0.35), seg=16)
        o.visible_shadow = False
    area_light((0, 2, 9), 1000, 10, (1, 0.98, 0.95))
    area_light((0, 3, 15), 900, 12, (1, 0.98, 0.95))
    area_light((0, -6, 5), 500, 8, (0.95, 0.97, 1.0)).rotation_euler = (math.radians(70), 0, 0)


def rubber_duck(x, y, z, s=1.0):
    Y = mat("duck", (255, 215, 50), 0.3)
    sph((x, y, z + 0.28 * s), (0.38 * s, 0.3 * s, 0.26 * s), Y)
    sph((x + 0.28 * s, y, z + 0.38 * s), (0.12 * s, 0.1 * s, 0.14 * s), Y, seg=16)
    sph((x - 0.12 * s, y, z + 0.66 * s), (0.22 * s,) * 3, Y)
    o = sph((x - 0.12 * s, y - 0.2 * s, z + 0.6 * s), (0.1 * s, 0.1 * s, 0.05 * s), mat("beak", (255, 140, 40), 0.4), seg=16)
    for dx in (-0.09, 0.09):
        sph((x - 0.12 * s + dx * s, y - 0.17 * s, z + 0.74 * s), (0.035 * s,) * 3, mat("eye", (40, 30, 30), 0.3), seg=8)


# ------------------------------------------------------------------ ayudas para nieve, Navidad, cueva, mar y escenario
def world(col, strength):
    """Luz ambiente del mundo (da el color de las sombras: celeste en la nieve, azul en el mar)."""
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = tuple(srgb2lin(x) for x in col) + (1,)
    bg.inputs[1].default_value = strength


def point(loc, energy, col=(255, 255, 255), radius=0.3, shadow=True):
    L = bpy.data.lights.new("pt", "POINT")
    L.energy, L.color, L.shadow_soft_size = energy, tuple(x / 255 for x in col), radius
    L.use_shadow = shadow
    o = bpy.data.objects.new("pt", L)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    return o


def spot(loc, target, energy, col=(255, 255, 255), size=0.6, blend=0.4):
    L = bpy.data.lights.new("spot", "SPOT")
    L.energy, L.color, L.spot_size, L.spot_blend = energy, tuple(x / 255 for x in col), size, blend
    o = bpy.data.objects.new("spot", L)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    look(o, target)
    return o


def nomix(o):
    """Objetos de adorno que no tiran sombra (brillos, burbujas, rayos de luz)."""
    o.visible_shadow = False
    return o


def mix_rgb(nt, fac, a, b):
    n = nt.nodes.new("ShaderNodeMix")
    n.data_type = "RGBA"
    nt.links.new(fac, n.inputs[0])
    ia = [s for s in n.inputs if s.name == "A" and s.type == "RGBA"][0]
    ib = [s for s in n.inputs if s.name == "B" and s.type == "RGBA"][0]
    for s, v in ((ia, a), (ib, b)):
        if isinstance(v, tuple):
            s.default_value = tuple(srgb2lin(x) for x in v) + (1,)
        else:
            nt.links.new(v, s)
    return [s for s in n.outputs if s.type == "RGBA"][0]


def band_mat(name, c1, c2, scale=3.0, distortion=6.0, kind="BANDS", rough=0.6, bump=0.3, emis=0.0):
    """Material con ondas (coral cerebro, caracoles, rayas suaves)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = kind
    wv.inputs["Scale"].default_value = scale
    wv.inputs["Distortion"].default_value = distortion
    col = mix_rgb(nt, wv.outputs["Fac"], c1, c2)
    nt.links.new(col, b.inputs["Base Color"])
    if emis:
        nt.links.new(col, b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emis
    if bump:
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        nt.links.new(wv.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def stripe_rod(p1, p2, r, c1, c2, n, v=16):
    """Barra a rayas (bastón de caramelo, postes): n tramos alternados."""
    p1, p2 = Vector(p1), Vector(p2)
    for k in range(n):
        a, b = p1 + (p2 - p1) * (k / n), p1 + (p2 - p1) * ((k + 1) / n)
        rod(a, b, r, mat(f"str{[c1, c2][k % 2]}", [c1, c2][k % 2], 0.35), v=v)


def candy_cane(x, y, h, s=1.0, c1=(235, 40, 60), c2=(255, 255, 255)):
    stripe_rod((x, y, 0), (x, y, h), 0.1 * s, c1, c2, int(h / (0.16 * s)))
    R = 0.32 * s
    n = 14
    for k in range(n + 1):
        a = math.pi - k * (math.pi * 1.15) / n
        sph((x + R + R * math.cos(a), y, h + R * math.sin(a)), (0.1 * s,) * 3, mat(f"str{[c1, c2][k % 2]}", [c1, c2][k % 2], 0.35), seg=16)


def snowy_pine(x, y, s=1.0, green=(45, 150, 100), snowc=(250, 252, 255), tiers=3):
    """Pino de dibujo con nieve en cada piso y gotitas de nieve en el borde."""
    cyl((x, y, 0.5 * s), 0.2 * s, 1.0 * s, mat("trunk", (140, 95, 55)))
    G, W = mat(f"pine{green}", green, 0.8), mat(f"psnow{snowc}", snowc, 0.55)
    for k in range(tiers):
        R, Hh, zc = (1.5 - k * 0.38) * s, 1.5 * s, (1.5 + k * 0.85) * s
        cone((x, y, zc), R, 0.0, Hh, G)
        f = 0.55
        cone((x, y, zc + Hh / 2 - f * Hh / 2 + 0.05 * s), R * f * 1.14, 0.0, f * Hh * 1.06, W)
        for j in range(8):
            a = j * 2 * math.pi / 8 + k
            sph((x + R * f * 1.05 * math.cos(a), y + R * f * 1.05 * math.sin(a), zc + Hh / 2 - f * Hh - 0.02 * s),
                (0.16 * s, 0.16 * s, 0.11 * s), W, seg=12)


def mountains(cols, snowc=(250, 252, 255)):
    """Montañas lejanas azuladas con la punta nevada."""
    for (x, y, r, h, c) in [(-26, 62, 14, 16, cols[0]), (-6, 70, 18, 21, cols[1]), (16, 64, 15, 17, cols[0]),
                            (34, 70, 16, 19, cols[1]), (-40, 70, 15, 18, cols[1])]:
        bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=r, radius2=0, depth=h, location=(x, y, h / 2 - 2))
        o = bpy.context.object
        bpy.ops.object.shade_smooth()
        o.data.materials.append(mat(f"mount{c}", c, 0.9))
        f = 0.32
        cone((x, y - 0.1, h - 2 - f * h / 2 + 0.2), r * f * 1.06, 0.0, f * h * 1.04, mat(f"mcap{snowc}", snowc, 0.7))
        for j in range(9):
            a = math.pi + j * math.pi / 8
            sph((x + r * f * math.cos(a), y + r * f * 0.7 * math.sin(a), h - 2 - f * h), (1.0, 0.8, 0.7),
                mat(f"mcap{snowc}", snowc, 0.7), seg=16)


def snowman(x, y, s=1.0, scarf=(235, 55, 70), hat=(70, 120, 230), mitt=(255, 120, 160)):
    W = mat("snowman", (252, 253, 255), 0.55)
    coal = mat("coal", (40, 40, 55), 0.4)
    sph((x, y, 0.75 * s), (0.95 * s, 0.95 * s, 0.85 * s), W)
    sph((x, y, 1.95 * s), (0.7 * s,) * 3, W)
    sph((x, y, 2.95 * s), (0.52 * s,) * 3, W)
    for dx in (-0.18, 0.18):
        sph((x + dx * s, y - 0.46 * s, 3.07 * s), (0.07 * s, 0.05 * s, 0.085 * s), coal, seg=12)
        sph((x + dx * s - 0.02 * s, y - 0.5 * s, 3.1 * s), (0.02 * s,) * 3, mat("eyehl", (255, 255, 255), 0.2), seg=8)
    cone((x, y - 0.72 * s, 2.93 * s), 0.09 * s, 0.0, 0.5 * s, mat("carrot", (255, 140, 40), 0.5), rot=(math.radians(90), 0, 0))
    for k in range(5):
        a = math.radians(-150 + k * 30)
        sph((x + 0.25 * s * math.cos(a), y - 0.46 * s, 2.92 * s + 0.12 * s * math.sin(a)), (0.04 * s,) * 3, coal, seg=8)
    for k in range(3):
        sph((x, y - 0.68 * s + 0.03 * k * s, 2.2 * s - k * 0.32 * s), (0.08 * s,) * 3, coal, seg=12)
    # bufanda a rayas
    torus((x, y, 2.52 * s), 0.5 * s, 0.13 * s, mat("scarf", scarf, 0.85), sc=(1, 1, 0.9))
    for k in range(4):
        col = [scarf, (255, 255, 255)][k % 2]
        cube((x + 0.33 * s, y - 0.45 * s, 2.32 * s - k * 0.17 * s), (0.11 * s, 0.05 * s, 0.085 * s), mat(f"scarf{col}", col, 0.85), 0.03)
    # gorro con pompón
    sph((x, y, 3.3 * s), (0.47 * s, 0.47 * s, 0.32 * s), mat("hat", hat, 0.8))
    torus((x, y, 3.27 * s), 0.46 * s, 0.09 * s, mat("hatband", (255, 255, 255), 0.85))
    sph((x, y, 3.68 * s), (0.15 * s,) * 3, mat("hatband", (255, 255, 255), 0.85), seg=16)
    # brazos de rama con guantes
    for sgn in (-1, 1):
        p1 = (x + sgn * 0.6 * s, y, 2.1 * s)
        p2 = (x + sgn * 1.45 * s, y - 0.1 * s, 2.65 * s)
        rod(p1, p2, 0.045 * s, mat("twig", (120, 80, 50), 0.8), v=8)
        rod(((p1[0] + p2[0]) / 2, y, (p1[2] + p2[2]) / 2), (p2[0] - sgn * 0.1 * s, y, p2[2] + 0.35 * s), 0.03 * s,
            mat("twig", (120, 80, 50), 0.8), v=8)
        sph(p2, (0.16 * s, 0.11 * s, 0.19 * s), mat("mitt", mitt, 0.8), seg=16)
        sph((p2[0] - sgn * 0.12 * s, p2[1], p2[2] + 0.06 * s), (0.07 * s, 0.07 * s, 0.09 * s), mat("mitt", mitt, 0.8), seg=12)


def penguin(x, y, s=1.0, turn=0.0, scarf=None):
    k = mat("pengb", (45, 60, 100), 0.5)
    w = mat("pengw", (255, 255, 255), 0.6)
    o = mat("pengo", (255, 165, 40), 0.5)
    dx, dy = math.sin(turn), -math.cos(turn)
    sph((x, y, 0.48 * s), (0.36 * s, 0.32 * s, 0.48 * s), k)
    sph((x + dx * 0.12 * s, y + dy * 0.12 * s, 0.45 * s), (0.27 * s, 0.24 * s, 0.38 * s), w)
    sph((x, y, 1.02 * s), (0.27 * s,) * 3, k)
    sph((x + dx * 0.1 * s, y + dy * 0.1 * s, 1.0 * s), (0.2 * s, 0.2 * s, 0.18 * s), w)
    for e in (-1, 1):
        ex, ey = x + dx * 0.24 * s + e * 0.08 * s * -dy, y + dy * 0.24 * s + e * 0.08 * s * dx
        sph((ex, ey, 1.06 * s), (0.04 * s,) * 3, mat("eye", (40, 30, 30), 0.3), seg=8)
        sph((x + e * 0.33 * s * -dy, y + e * 0.33 * s * dx, 0.55 * s), (0.08 * s, 0.1 * s, 0.26 * s), k, seg=12).rotation_euler = (0, e * 0.35, turn)
        sph((x + e * 0.13 * s * -dy + dx * 0.15 * s, y + e * 0.13 * s * dx + dy * 0.15 * s, 0.04 * s), (0.11 * s, 0.14 * s, 0.04 * s), o, seg=12)
    cone((x + dx * 0.32 * s, y + dy * 0.32 * s, 0.96 * s), 0.07 * s, 0.0, 0.18 * s, o, rot=(math.pi / 2, 0, turn))
    if scarf:
        torus((x, y, 0.8 * s), 0.25 * s, 0.07 * s, mat("pscarf", scarf, 0.85))


def sled(x, y, s=1.0, col=(230, 60, 60), rotz=0.0):
    objs = []
    for k in range(4):
        objs.append(cube((x - 0.45 * s + k * 0.3 * s, y, 0.42 * s), (0.13 * s, 0.6 * s, 0.05 * s), mat("sledwood", col, 0.5), 0.03))
    for sgn in (-1, 1):
        objs.append(rod((x - 0.62 * s, y + sgn * 0.45 * s, 0.1 * s), (x + 0.55 * s, y + sgn * 0.45 * s, 0.1 * s), 0.045 * s,
                        mat("runner", (250, 210, 70), 0.3), v=10))
        objs.append(torus((x - 0.62 * s, y + sgn * 0.45 * s, 0.3 * s), 0.2 * s, 0.045 * s, mat("runner", (250, 210, 70), 0.3),
                          rot=(math.pi / 2, 0, 0)))
        for px in (-0.3, 0.3):
            objs.append(rod((x + px * s, y + sgn * 0.45 * s, 0.1 * s), (x + px * s, y + sgn * 0.45 * s, 0.4 * s), 0.035 * s,
                            mat("runner", (250, 210, 70), 0.3), v=8))
    return objs


def birdhouse(x, y, h=2.6, s=1.0, body=(255, 205, 70), roof=(235, 70, 80)):
    rod((x, y, 0), (x, y, h), 0.08 * s, mat("pole", (150, 105, 65), 0.8))
    cube((x, y, h + 0.4 * s), (0.4 * s, 0.35 * s, 0.42 * s), mat(f"bh{body}", body, 0.6), 0.05)
    for sgn in (-1, 1):
        o = cube((x + sgn * 0.25 * s, y, h + 0.98 * s), (0.34 * s, 0.48 * s, 0.05 * s), mat(f"bhr{roof}", roof, 0.6), 0.03)
        o.rotation_euler = (0, sgn * 0.7, 0)
        o = cube((x + sgn * 0.26 * s, y, h + 1.04 * s), (0.34 * s, 0.5 * s, 0.05 * s), mat("snowman", (252, 253, 255), 0.55), 0.05)
        o.rotation_euler = (0, sgn * 0.7, 0)
    disc((x, y - 0.36 * s, h + 0.48 * s), 0.13 * s, mat("hole", (70, 45, 40), 0.9), 0.02)
    rod((x, y - 0.36 * s, h + 0.25 * s), (x, y - 0.55 * s, h + 0.25 * s), 0.025 * s, mat("pole", (150, 105, 65), 0.8), v=8)
    # pajarito rojo
    sph((x + 0.12 * s, y - 0.5 * s, h + 0.38 * s), (0.12 * s, 0.1 * s, 0.11 * s), mat("robin", (230, 60, 60), 0.5), seg=16)
    sph((x + 0.2 * s, y - 0.55 * s, h + 0.5 * s), (0.08 * s,) * 3, mat("robin", (230, 60, 60), 0.5), seg=16)
    cone((x + 0.2 * s, y - 0.64 * s, h + 0.5 * s), 0.025 * s, 0, 0.07 * s, mat("beak", (255, 160, 40), 0.4), rot=(math.pi / 2, 0, 0))


def igloo(x, y, s=1.0):
    I = mat("ice", (238, 246, 255), 0.35)
    line = mat("iceline", (185, 210, 245), 0.4)
    sph((x, y, 0), (2.0 * s, 2.0 * s, 1.75 * s), I, seg=48)
    for k, h in enumerate((0.42, 0.84, 1.22, 1.52)):
        r = 2.0 * s * math.sqrt(max(0.0, 1 - (h / 1.75) ** 2))
        torus((x, y, h * s), r + 0.01, 0.035 * s, line, sc=(1, 1, 0.6))
        n = max(3, int(r * 3.2))
        for j in range(n):
            a = (j + 0.5 * (k % 2)) * 2 * math.pi / n
            h2 = (h + 0.42) if k < 3 else 1.72
            r2 = 2.0 * s * math.sqrt(max(0.0, 1 - (h2 / 1.75) ** 2))
            rod((x + r * math.cos(a) * 1.01, y + r * math.sin(a) * 1.01, h * s),
                (x + r2 * math.cos(a) * 1.01, y + r2 * math.sin(a) * 1.01, min(h2, 1.72) * s), 0.03 * s, line, v=6)
    o = cyl((x, y - 1.9 * s, 0), 0.8 * s, 1.3 * s, I, rot=(math.pi / 2, 0, 0), v=32)
    disc((x, y - 2.56 * s, 0.02), 0.55 * s, mat("igdoor", (70, 110, 170), 0.9), 0.04)
    torus((x, y - 2.55 * s, 0), 0.68 * s, 0.07 * s, line, rot=(math.pi / 2, 0, 0))


def mitten_tree(x, y, s=1.0):
    """Arbolito pelado con mitones y un gorro colgados de las ramas."""
    B = mat("bark", (130, 90, 60), 0.85)
    rod((x, y, 0), (x, y, 2.2 * s), 0.12 * s, B, v=12)
    tips = []
    for (dx, dz, ex, ez) in [(0, 1.3, -1.0, 2.2), (0, 1.6, 0.9, 2.5), (0, 2.1, -0.3, 3.0), (0, 2.2, 0.4, 3.0)]:
        p1, p2 = (x + dx * s, y, dz * s), (x + ex * s, y, ez * s)
        rod(p1, p2, 0.06 * s, B, v=8)
        sph(p2, (0.12 * s, 0.1 * s, 0.07 * s), mat("snowman", (252, 253, 255), 0.55), seg=12)
        tips.append((p1, p2))
    for (p1, p2), col in zip(tips[:2], [(255, 110, 150), (90, 170, 255)]):
        hx, hz = p1[0] + (p2[0] - p1[0]) * 0.6, p1[2] + (p2[2] - p1[2]) * 0.6
        rod((hx, y - 0.05, hz), (hx, y - 0.05, hz - 0.35 * s), 0.012, mat("string", (250, 250, 250), 0.6), v=6)
        sph((hx, y - 0.05, hz - 0.55 * s), (0.17 * s, 0.09 * s, 0.22 * s), mat(f"mitt{col}", col, 0.8), seg=16)
        sph((hx + 0.15 * s, y - 0.05, hz - 0.48 * s), (0.07 * s, 0.07 * s, 0.1 * s), mat(f"mitt{col}", col, 0.8), seg=12)
        cyl((hx, y - 0.05, hz - 0.35 * s), 0.16 * s, 0.1 * s, mat("cuff", (255, 255, 255), 0.85))


def snow_piles(spots, W):
    for (x, y, r) in spots:
        sph((x, y, 0.05), (r, 0.8 * r, 0.45 * r), W, seg=24)
        sph((x + 0.55 * r, y - 0.1, 0.03), (0.6 * r, 0.5 * r, 0.32 * r), W, seg=20)


def falling_snow(n, seed, area=((-14, 14), (0, 22), (1.5, 14)), avoid=2.5):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y, z = rnd.uniform(*area[0]), rnd.uniform(*area[1]), rnd.uniform(*area[2])
        if abs(x) < avoid and z < 5 and y < 6:
            continue
        nomix(sph((x, y, z), (rnd.uniform(0.05, 0.1),) * 3, mat("flake", (255, 255, 255), 0.5, emis=0.6), seg=8))


# ------------------------------------------------------------------ nieve
def snow(portrait, night=False):
    world((150, 185, 255), 0.85)
    W = mat("snowg", (236, 243, 255), 0.65)
    g = ground(W, bumps=0.35)
    mountains([(175, 195, 240), (160, 180, 235)])
    # lomas nevadas en capas, con sombras celestes
    for (x, y, sx, sz, c) in [(-22, 46, 20, 8, (225, 235, 255)), (12, 50, 24, 9, (215, 228, 252)),
                              (-14, 30, 16, 5, (240, 246, 255)), (10, 34, 20, 6, (232, 240, 255)),
                              (0, 40, 30, 7, (236, 243, 255)), (24, 28, 12, 4, (245, 249, 255)), (-28, 34, 14, 6, (230, 238, 255))]:
        sph((x, y, -1), (sx, 6, sz), mat("hill" + str(c), c, 0.8), seg=48)
    # caminito de pisadas (huella celeste)
    strip_on(g, [(0.5, -6), (0.0, 2), (2.0, 9), (0.8, 14), (-1.0, 20)], lambda t: 2.0 * (1 - t) + 0.6 * t,
             mat("snowpath", (215, 228, 252), 0.7))
    # pinos nevados de distintos verdes
    for (x, y, s, gcol) in [(-7.5, 7, 1.0, (45, 150, 100)), (13.0, 9.0, 1.15, (55, 160, 95)), (-11, 13, 1.35, (40, 140, 105)),
                            (15.0, 13, 1.2, (50, 155, 110)), (-4, 21, 1.0, (60, 165, 100)), (5, 23, 0.95, (45, 150, 100)),
                            (-15, 21, 1.4, (55, 155, 95)), (16.5, 22, 1.3, (45, 145, 105)), (-9.3, 9.5, 0.7, (65, 170, 100)),
                            (2.8, 17.5, 0.75, (60, 165, 105)), (-2.0, 25, 1.1, (50, 150, 110)), (9, 27, 1.2, (45, 150, 100))]:
        snowy_pine(x, y, s, gcol)
    # muñeco de nieve con bufanda roja y gorro azul
    snowman(4.4, 3.8, 0.8)
    # iglú a la izquierda
    igloo(-6.5, 11.5, 1.1)
    # laguna congelada con tobogán de hielo para pingüinos
    PX, PY = 6.8, 12.5
    cyl((PX, PY, 0.02), 1.0, 0.16, mat("icepond", (150, 215, 250), 0.05), v=64).scale = (3.2, 1.6, 1)
    torus((PX, PY, 0.1), 1.0, 0.08, mat("snowman", (252, 253, 255), 0.55), sc=(3.25, 1.65, 1.6))
    for (dx, dy, L) in [(-1.2, -0.3, 0.8), (0.9, 0.4, 0.5), (1.9, -0.5, 0.35)]:
        o = sph((PX + dx, PY + dy - 0.6, 0.11), (L, 0.05, 0.02), mat("icehl", (235, 250, 255), 0.1, emis=0.3), seg=12)
        o.rotation_euler = (0, 0, 0.25)
    MX, MY = PX + 4.6, PY + 1.6
    sph((MX, MY, 0), (2.0, 1.8, 2.3), W)
    pts = [(MX - 0.2, MY - 0.4, 2.2), (MX - 1.0, MY - 1.2, 1.6), (MX - 2.0, MY - 1.5, 0.9), (MX - 3.0, MY - 1.3, 0.35), (PX + 2.6, PY, 0.15)]
    ICE = mat("slide", (120, 195, 250), 0.15)
    for a, b in zip(pts, pts[1:]):
        o = rod(a, b, 0.42, ICE, v=24)
        o.scale = (1, 0.25, 1.02)
        for sgn in (-1, 1):
            off = Vector((b[1] - a[1], -(b[0] - a[0]), 0)).normalized() * 0.42 * sgn
            rod(Vector(a) + off + Vector((0, 0, 0.12)), Vector(b) + off + Vector((0, 0, 0.12)), 0.06, mat("rail", (255, 255, 255), 0.4), v=8)
    penguin(MX - 0.2, MY - 0.2, 0.75, turn=-0.6, scarf=(255, 200, 60))
    penguin(PX - 1.6, PY - 0.4, 0.8, turn=0.3, scarf=(235, 60, 80))
    penguin(PX + 0.3, PY + 0.2, 0.6, turn=-0.4)
    # trineo rojo, casita de pájaros y arbolito con mitones
    sled(-4.6, 3.0, 1.1, rotz=0.3)
    birdhouse(-4.2, 6.2, 2.4, 1.0)
    mitten_tree(-2.6, 8.5, 1.0)
    # montones de nieve y piedras nevadas
    W2 = mat("snowpile", (250, 252, 255), 0.6)
    snow_piles([(-6.5, 1.5, 1.2), (6.8, 2.0, 1.0), (-9.5, 5.5, 1.5), (9.8, 5.5, 1.3), (3.6, 8.5, 0.8), (-3.2, 12.5, 0.9)], W2)
    # cerca de madera con nieve arriba, en diagonal a la izquierda
    for k in range(7):
        x, y = -5.0 - k * 0.9, 4.2 + k * 0.6
        cube((x, y, 0.55), (0.13, 0.08, 0.55), mat("sfence", (200, 140, 90), 0.7), 0.05)
        sph((x, y, 1.13), (0.17, 0.12, 0.08), W2, seg=12)
    for z in (0.4, 0.85):
        rod((-4.8, 4.05, z), (-10.6, 8.0, z), 0.06, mat("sfence", (200, 140, 90), 0.7), v=10)
    rod((-4.8, 4.0, 0.95), (-10.6, 7.95, 0.95), 0.07, W2, v=10)
    falling_snow(60, 4)
    clouds()
    sph((14, 40, 14), (2.2, 2.2, 2.2), mat("sunball", (255, 235, 140), 0.5, emis=2.5))


# ------------------------------------------------------------------ Navidad
def present(x, y, w, d, h, col, rib, rotz=0.0):
    b = cube((x, y, h), (w, d, h), mat(f"gift{col}", col, 0.45), 0.04)
    b.rotation_euler = (0, 0, rotz)
    c, s = math.cos(rotz), math.sin(rotz)
    for o in (cube((x, y, h), (w + 0.01, 0.12 * min(w, d) + 0.02, h + 0.01), mat(f"rib{rib}", rib, 0.35), 0.01),
              cube((x, y, h), (0.12 * min(w, d) + 0.02, d + 0.01, h + 0.01), mat(f"rib{rib}", rib, 0.35), 0.01)):
        o.rotation_euler = (0, 0, rotz)
    for sgn in (-1, 1):
        torus((x + sgn * 0.14 * c * min(w, 0.6), y + sgn * 0.14 * s * min(w, 0.6), 2 * h + 0.1), 0.14, 0.05,
              mat(f"rib{rib}", rib, 0.35), rot=(math.pi / 2, sgn * 0.5, rotz))


def house(x, y, s, wall, roof, door, rotz=0.0):
    """Casita con techo nevado, ventanas cálidas, puerta con corona y chimenea."""
    w, d, h = 1.3 * s, 1.1 * s, 0.95 * s
    cube((x, y, h), (w, d, h), mat(f"hw{wall}", wall, 0.7), 0.06)
    flat([(-w, 0), (w, 0), (0, 0.85 * w)], mat(f"hw{wall}", wall, 0.7), (x, y - d + 0.02, 2 * h), 0.05)
    run, rise = w + 0.3 * s, 0.85 * w + 0.2 * s
    L, a = math.hypot(run, rise), math.atan2(rise, run)
    ztop = 2 * h + 0.85 * w + 0.05 * s
    for sgn in (-1, 1):
        cx, cz = x + sgn * run / 2, ztop - rise / 2
        o = cube((cx, y, cz), (L / 2 + 0.06, d + 0.25 * s, 0.09 * s), mat(f"hr{roof}", roof, 0.6), 0.04)
        o.rotation_euler = (0, sgn * a, 0)
        n = Vector((sgn * math.sin(a), 0, math.cos(a)))
        o = cube(Vector((cx, y, cz)) + n * 0.17 * s, (L / 2 + 0.1, d + 0.3 * s, 0.1 * s), mat("roofsnow", (250, 252, 255), 0.55), 0.09)
        o.rotation_euler = (0, sgn * a, 0)
        for k in range(6):
            t = (k + 0.5) / 6
            sph((x + sgn * run - sgn * 0.05, y - d - 0.25 * s + t * 2 * (d + 0.25 * s), 2 * h - 0.2 * s + 0.05),
                (0.12 * s, 0.14 * s, 0.16 * s), mat("roofsnow", (250, 252, 255), 0.55), seg=12)
    # chimenea
    cube((x + 0.55 * w, y + 0.3 * d, ztop), (0.2 * s, 0.2 * s, 0.45 * s), mat("chim", (200, 95, 80), 0.8), 0.03)
    sph((x + 0.55 * w, y + 0.3 * d, ztop + 0.47 * s), (0.25 * s, 0.25 * s, 0.1 * s), mat("roofsnow", (250, 252, 255), 0.55), seg=16)
    WIN = mat("win", (255, 205, 110), 0.4, emis=3.0)
    FR = mat("wframe", (255, 255, 255), 0.4)
    for sgn in (-1, 1):
        cube((x + sgn * 0.6 * w, y - d - 0.01, 1.15 * h), (0.24 * s, 0.03, 0.26 * s), WIN, 0.02)
        cube((x + sgn * 0.6 * w, y - d - 0.04, 1.15 * h), (0.025 * s, 0.02, 0.27 * s), FR, 0.01)
        cube((x + sgn * 0.6 * w, y - d - 0.04, 1.15 * h), (0.25 * s, 0.02, 0.025 * s), FR, 0.01)
        cube((x + sgn * 0.6 * w, y - d - 0.1, 1.15 * h - 0.3 * s), (0.3 * s, 0.1 * s, 0.04 * s), mat("roofsnow", (250, 252, 255), 0.55), 0.03)
    disc((x, y - d - 0.01, 2 * h + 0.35 * w), 0.2 * s, WIN, 0.03)
    torus((x, y - d - 0.03, 2 * h + 0.35 * w), 0.2 * s, 0.035 * s, FR, rot=(math.pi / 2, 0, 0))
    cube((x, y - d - 0.01, 0.45 * s), (0.25 * s, 0.03, 0.45 * s), mat(f"door{door}", door, 0.5), 0.03)
    sph((x, y - d - 0.03, 0.9 * s), (0.25 * s, 0.03, 0.25 * s), mat(f"door{door}", door, 0.5), seg=20)
    torus((x, y - d - 0.07, 0.72 * s), 0.14 * s, 0.05 * s, mat("wreath", (50, 150, 80), 0.7), rot=(math.pi / 2, 0, 0))
    sph((x, y - d - 0.12, 0.62 * s), (0.05 * s,) * 3, mat("wbow", (235, 50, 60), 0.4), seg=10)
    point((x, y - d - 1.0 * s, 1.2 * h), 120 * s, (255, 190, 110), 0.5, shadow=False)


def light_string(p1, p2, sag, n, cols, r=0.07):
    """Guirnalda de lucecitas de colores entre dos postes."""
    pts = []
    for k in range(31):
        t = k / 30
        pts.append(Vector(p1) + (Vector(p2) - Vector(p1)) * t - Vector((0, 0, sag * 4 * t * (1 - t))))
    for a, b in zip(pts, pts[1:]):
        rod(a, b, 0.018, mat("wire", (40, 90, 60), 0.6), v=6)
    for k in range(n):
        t = (k + 0.5) / n
        p = Vector(p1) + (Vector(p2) - Vector(p1)) * t - Vector((0, 0, sag * 4 * t * (1 - t) + 0.12))
        c = cols[k % len(cols)]
        nomix(sph(p, (r, r, r * 1.35), mat(f"bulb{c}", c, 0.3, emis=4.0), seg=12))


def xmas_tree(x, y, s=1.0):
    G = mat("xtree", (40, 150, 85), 0.75)
    cyl((x, y, 0.35 * s), 0.3 * s, 0.7 * s, mat("trunk", (140, 95, 55)))
    tiers = [(1.0, 2.0, 1.9), (2.2, 1.65, 1.7), (3.25, 1.25, 1.5), (4.15, 0.85, 1.2)]
    for (zc, R, Hh) in tiers:
        cone((x, y, zc * s), R * s, 0.0, Hh * s, G)
        for j in range(12):
            a = j * 2 * math.pi / 12
            sph((x + R * 0.96 * s * math.cos(a), y + R * 0.96 * s * math.sin(a), (zc - Hh / 2 + 0.06) * s),
                (0.18 * s, 0.18 * s, 0.1 * s), mat("roofsnow", (250, 252, 255), 0.55), seg=12)
    rnd = random.Random(12)

    def surf(h, a, off=0.06):
        for (zc, R, Hh) in tiers:
            if zc - Hh / 2 <= h <= zc + Hh / 2:
                r = R * (1 - (h - (zc - Hh / 2)) / Hh) + off
                return (x + r * s * math.cos(a), y + r * s * math.sin(a), h * s)
        return None
    # guirnalda de lucecitas en espiral
    LC = [(255, 80, 80), (255, 215, 70), (90, 180, 255), (120, 230, 120), (255, 130, 220)]
    for k in range(70):
        h = 0.3 + k * 0.066
        p = surf(h, -math.pi / 2 + k * 0.62)
        if p:
            nomix(sph(p, (0.1 * s,) * 3, mat(f"bulb{LC[k % 5]}", LC[k % 5], 0.3, emis=6.0), seg=10))
    # bolas brillantes
    BC = [(235, 50, 70), (255, 200, 60), (70, 140, 240), (255, 120, 200), (180, 110, 240)]
    for k in range(26):
        p = surf(rnd.uniform(0.2, 4.4), rnd.uniform(-math.pi, 0.1), 0.12)
        if p:
            c = BC[k % 5]
            sph(p, (0.17 * s,) * 3, mat(f"bauble{c}", c, 0.15, emis=0.6), seg=16)
    # estrella dorada arriba
    star((x, y - 0.1, 5.15 * s), 0.6 * s, mat("tstar", (255, 215, 70), 0.3, emis=3.0), 0.18 * s)
    point((x, y - 1.2, 5.1 * s), 150, (255, 220, 120), 0.5, shadow=False)
    point((x, y - 2.0, 2.4 * s), 260, (255, 200, 140), 1.0, shadow=False)


def xmas(portrait):
    world((70, 90, 170), 0.55)
    W = mat("snowg", (232, 238, 255), 0.65)
    g = ground(W, bumps=0.35)
    mountains([(110, 120, 190), (95, 105, 175)], (215, 225, 250))
    for (x, y, sx, sz, c) in [(-14, 30, 16, 5, (205, 215, 245)), (10, 34, 20, 6, (195, 205, 240)),
                              (0, 40, 30, 7, (200, 210, 245)), (-28, 34, 14, 6, (190, 200, 238))]:
        sph((x, y, -1), (sx, 6, sz), mat("hill" + str(c), c, 0.8), seg=48)
    strip_on(g, [(0.5, -6), (0.0, 3), (0.5, 9), (0.0, 12)], lambda t: 2.2 * (1 - t) + 1.2 * t, mat("snowpath", (200, 210, 245), 0.7))
    # aldea: casitas de colores con ventanas cálidas
    house(-3.6, 12.5, 1.15, (235, 85, 85), (120, 75, 160), (60, 140, 90))
    house(3.4, 13.0, 1.05, (255, 200, 90), (60, 120, 200), (210, 60, 70))
    house(8.4, 10.6, 1.2, (110, 180, 240), (215, 70, 80), (255, 200, 80))
    house(-9.6, 11.5, 1.25, (140, 210, 140), (200, 80, 80), (120, 80, 170))
    house(0.0, 19.0, 1.0, (255, 160, 190), (80, 150, 110), (90, 120, 220))
    house(-14.5, 17.5, 1.2, (255, 215, 120), (70, 110, 190), (210, 60, 70))
    house(13.5, 17.0, 1.2, (240, 120, 100), (120, 80, 170), (60, 140, 90))
    for (x, y, s) in [(-6.5, 17, 1.0), (6.5, 18, 1.1), (-12, 23, 1.3), (11, 24, 1.3), (-3, 25, 1.1), (4, 27, 1.2)]:
        snowy_pine(x, y, s, (40, 135, 100), (235, 240, 255))
    # árbol de Navidad grande, con regalos
    xmas_tree(-5.6, 6.0, 1.0)
    for (x, y, w, d, h, col, rib, rz) in [(-4.2, 4.4, 0.45, 0.4, 0.35, (235, 60, 80), (255, 215, 70), 0.3),
                                          (-5.0, 3.9, 0.35, 0.35, 0.25, (70, 150, 240), (255, 255, 255), -0.2),
                                          (-6.8, 4.3, 0.5, 0.45, 0.42, (255, 200, 60), (235, 60, 80), 0.1),
                                          (-3.6, 5.2, 0.3, 0.3, 0.3, (140, 210, 120), (235, 60, 80), 0.6),
                                          (-7.6, 5.0, 0.32, 0.3, 0.22, (200, 120, 240), (255, 255, 255), -0.4),
                                          (6.4, 3.6, 0.4, 0.38, 0.3, (255, 120, 180), (255, 255, 255), -0.3),
                                          (7.2, 4.4, 0.32, 0.3, 0.24, (90, 200, 220), (255, 215, 70), 0.4)]:
        present(x, y, w, d, h, col, rib, rz)
    # bastones de caramelo a los costados del camino
    candy_cane(-3.0, 3.2, 1.6, 1.1)
    candy_cane(3.2, 3.6, 1.6, 1.1, c1=(60, 170, 90))
    candy_cane(-2.6, 7.6, 1.2, 0.9, c1=(60, 170, 90))
    candy_cane(2.6, 8.0, 1.2, 0.9)
    # postes a rayas con guirnaldas de lucecitas
    LC = [(255, 80, 80), (255, 215, 70), (90, 180, 255), (120, 230, 120), (255, 130, 220)]
    poles = [(-11.5, 8.5), (-6.5, 9.2), (0.0, 9.6), (6.5, 9.2), (11.5, 8.5)]
    for (px, py) in poles:
        stripe_rod((px, py, 0), (px, py, 4.2), 0.09, (235, 50, 60), (255, 255, 255), 14)
        sph((px, py, 4.3), (0.17,) * 3, mat("polegold", (255, 210, 80), 0.25, emis=0.5))
    for (a, b) in zip(poles, poles[1:]):
        light_string((a[0], a[1], 4.1), (b[0], b[1], 4.1), 0.7, 11, LC)
    # muñeco de nieve y farolito
    snowman(6.0, 6.6, 0.8, scarf=(60, 170, 90), hat=(235, 55, 70), mitt=(255, 210, 70))
    rod((8.4, 6.8, 0), (8.4, 6.8, 2.8), 0.07, mat("lamp", (40, 50, 70), 0.4), v=12)
    cube((8.4, 6.8, 3.05), (0.22, 0.22, 0.28), mat("lampglass", (255, 220, 140), 0.3, emis=4.0), 0.05)
    cone((8.4, 6.8, 3.5), 0.33, 0.05, 0.25, mat("lamp", (40, 50, 70), 0.4))
    sph((8.4, 6.8, 3.58), (0.3, 0.3, 0.09), mat("roofsnow", (250, 252, 255), 0.55), seg=16)
    point((8.4, 6.4, 3.0), 200, (255, 200, 120), 0.4, shadow=False)
    snow_piles([(-8.8, 2.0, 1.3), (8.8, 1.8, 1.2), (-10.5, 6.5, 1.4), (10.8, 6.5, 1.3)], mat("snowpile", (240, 244, 255), 0.6))
    falling_snow(70, 5)
    sph((-12, 40, 14), (2.0, 2.0, 2.0), mat("moon", (255, 245, 200), 0.5, emis=2.5))
    area_light((0, 0, 12), 900, 16, (0.75, 0.8, 1.0))


# ------------------------------------------------------------------ cueva de cristales
def crystal(x, y, z, h, r, col, tilt=(0, 0), emis=1.4, spin=0.0):
    """Cristal hexagonal con punta, apoyado en su base."""
    verts, faces = [], []
    for k in range(6):
        a = k * math.pi / 3
        verts.append((r * math.cos(a), r * math.sin(a), 0))
    for k in range(6):
        a = k * math.pi / 3
        verts.append((r * 1.05 * math.cos(a), r * 1.05 * math.sin(a), h * 0.72))
    verts.append((0, 0, h))
    for k in range(6):
        k2 = (k + 1) % 6
        faces.append([k, k2, 6 + k2, 6 + k])
        faces.append([6 + k, 6 + k2, 12])
    faces.append(list(range(5, -1, -1)))
    me = bpy.data.meshes.new("cry")
    me.from_pydata(verts, [], faces)
    o = bpy.data.objects.new("cry", me)
    bpy.context.scene.collection.objects.link(o)
    o.location = (x, y, z)
    o.rotation_euler = (tilt[0], tilt[1], spin)
    b = o.modifiers.new("b", "BEVEL")
    b.width, b.segments = min(0.05, r * 0.2), 2
    o.data.materials.append(mat(f"cry{col}{emis}", col, 0.12, emis=emis))
    return o


def crystal_cluster(x, y, s, col, seed, light=True, z=0.0):
    rnd = random.Random(seed)
    crystal(x, y, z - 0.1, 1.9 * s, 0.32 * s, col, (0, 0), spin=rnd.uniform(0, 1))
    for k in range(6):
        a = k * 2 * math.pi / 6 + rnd.uniform(-0.3, 0.3)
        t = rnd.uniform(0.35, 0.7)
        crystal(x + 0.25 * s * math.cos(a), y + 0.25 * s * math.sin(a), z - 0.1, rnd.uniform(0.7, 1.4) * s,
                rnd.uniform(0.16, 0.25) * s, col, (-t * math.sin(a), t * math.cos(a)), spin=rnd.uniform(0, 1))
    sph((x, y, z), (0.75 * s, 0.6 * s, 0.25 * s), mat("crybase", (125, 105, 175), 0.9), seg=20)
    if light:
        point((x, y - 0.9 * s, z + 1.0 * s), 220 * s, col, 0.6, shadow=False)


def glow_mushroom(x, y, s, cap, stem=(240, 235, 255), z=0.0):
    cyl((x, y, z + 0.3 * s), 0.1 * s, 0.6 * s, mat("gmstem", stem, 0.5, emis=0.4))
    sph((x, y, z + 0.62 * s), (0.42 * s, 0.42 * s, 0.26 * s), mat(f"gmcap{cap}", cap, 0.3, emis=1.6))
    sph((x, y, z + 0.55 * s), (0.4 * s, 0.4 * s, 0.1 * s), mat("gmunder", (255, 245, 230), 0.6, emis=0.5), seg=20)
    for k in range(5):
        a = k * 2 * math.pi / 5 + 0.3
        sph((x + 0.26 * s * math.cos(a), y + 0.26 * s * math.sin(a) - 0.05 * s, z + 0.76 * s), (0.06 * s, 0.06 * s, 0.035 * s),
            mat("gmdot", (255, 255, 255), 0.4, emis=1.5), seg=10)


def cave(portrait):
    world((150, 120, 210), 0.9)
    floor = bpy.data.materials.new("cavefloor")
    floor.use_nodes = True
    nt = floor.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.9
    vo = nt.nodes.new("ShaderNodeTexVoronoi")
    vo.inputs["Scale"].default_value = 0.6
    nt.links.new(mix_rgb(nt, vo.outputs["Distance"], (175, 145, 210), (150, 120, 195)), b.inputs["Base Color"])
    ground(floor, bumps=0.4)
    # bóveda de roca lila
    rock = band_mat("caverock", (140, 110, 195), (120, 95, 180), 0.25, 3.0, rough=0.9, bump=0.2)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, location=(0, 4, 0))
    o = bpy.context.object
    o.scale = (24, 22, 11)
    t = bpy.data.textures.new("rockt", "CLOUDS")
    t.noise_scale = 1.5
    d = o.modifiers.new("d", "DISPLACE")
    d.texture, d.strength = t, 1.2
    o.data.materials.append(rock)
    bpy.ops.object.shade_smooth()
    rnd = random.Random(3)
    # rocas redondas en capas a los costados y al fondo
    RC = [(165, 140, 210), (150, 130, 200), (180, 155, 220), (135, 120, 190)]
    for (x, y, r) in [(-9.5, 4, 2.2), (-11, 9, 3.0), (-7, 12, 2.0), (9.5, 4.5, 2.0), (11.5, 9.5, 3.2), (7.5, 13.5, 2.2),
                      (-3, 19, 2.6), (4, 20, 3.0), (0, 23, 3.5), (-13, 15, 3.4), (13, 16, 3.4), (-5.5, 1.5, 0.8),
                      (6.0, 1.2, 0.7), (-2.5, 13, 1.0), (2.8, 14, 0.9)]:
        sph((x, y, 0), (r, 0.85 * r, 0.75 * r), mat(f"boulder{RC[int(abs(x * 3)) % 4]}", RC[int(abs(x * 3)) % 4], 0.85), seg=32)
    # racimos de cristales de colores que brillan
    CC = [(110, 240, 230), (255, 140, 220), (255, 225, 110), (150, 170, 255), (170, 255, 150)]
    for k, (x, y, s, z) in enumerate([(-6.2, 4.5, 1.1, 0), (6.6, 5.2, 1.0, 0), (-8.6, 7.8, 1.3, 1.2), (9.2, 8.5, 1.4, 1.0),
                                      (-4.2, 10.5, 0.9, 0), (4.5, 11.2, 0.8, 0), (-10.5, 2.5, 0.8, 0.6), (10.0, 2.8, 0.75, 0.5),
                                      (-1.5, 18.5, 1.2, 1.4), (6.5, 17, 1.1, 1.2), (-6.5, 15.5, 1.0, 1.0)]):
        crystal_cluster(x, y, s, CC[k % 5], k + 1, z=z)
    for k in range(14):
        x, y = rnd.choice([-1, 1]) * rnd.uniform(3.5, 9), rnd.uniform(2, 14)
        crystal(x, y, -0.05, rnd.uniform(0.4, 0.8), rnd.uniform(0.08, 0.14), CC[k % 5], (rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4)))
    # hongos que brillan
    for (x, y, s, c) in [(-4.6, 2.2, 0.8, (110, 230, 255)), (-4.0, 2.7, 0.55, (255, 150, 230)), (4.4, 2.5, 0.7, (255, 150, 230)),
                         (5.0, 3.0, 0.5, (110, 230, 255)), (-7.6, 10.0, 0.9, (255, 220, 110)), (8.4, 11.5, 0.9, (170, 255, 150)),
                         (2.5, 12.6, 0.6, (110, 230, 255)), (-2.2, 12.2, 0.7, (255, 150, 230))]:
        glow_mushroom(x, y, s, c)
        point((x, y - 0.6, 0.9 * s), 40 * s, c, 0.3, shadow=False)
    # laguna subterránea que brilla
    LX, LY = 1.2, 15.5
    cyl((LX, LY, 0.05), 1.0, 0.2, mat("cpond", (70, 200, 230), 0.05, emis=0.7), v=64).scale = (3.6, 1.7, 1)
    for k in range(18):
        a = k * 2 * math.pi / 18
        sph((LX + 3.7 * math.cos(a), LY + 1.75 * math.sin(a), 0.1), (0.4, 0.35, 0.25), mat("pebble", (185, 165, 225), 0.8), seg=16)
    for (dx, dy, r) in [(-1.2, 0.2, 0.3), (1.0, -0.4, 0.25)]:
        cyl((LX + dx, LY + dy, 0.17), r, 0.03, mat("clily", (120, 235, 190), 0.4, emis=0.8))
    point((LX, LY - 1.5, 1.2), 250, (90, 220, 240), 1.0, shadow=False)
    # estalactitas de colores suaves con punta redonda
    SC = [(200, 170, 240), (240, 175, 220), (170, 200, 245), (215, 190, 245)]
    for k in range(34):
        x, y = rnd.uniform(-13, 13), rnd.uniform(1, 20)
        top = 11.0 * math.sqrt(max(0.05, 1 - (x / 24) ** 2 - ((y - 4) / 22) ** 2)) + 0.6
        L = rnd.uniform(1.2, 3.2)
        c = SC[k % 4]
        cone((x, y, top - L / 2), rnd.uniform(0.3, 0.55), 0.08, L, mat(f"stal{c}", c, 0.7), rot=(math.pi, 0, 0))
        sph((x, y, top - L), (0.09,) * 3, mat(f"stal{c}", c, 0.7), seg=12)
    # estalagmitas redondeadas a los costados
    for (x, y, h) in [(-7.5, 3.0, 1.6), (-8.2, 3.6, 1.0), (7.8, 3.4, 1.5), (8.5, 4.0, 0.9), (-5.0, 13.5, 1.8), (5.6, 14.5, 2.0)]:
        cone((x, y, h / 2), 0.45, 0.1, h, mat("stalg", (195, 170, 235), 0.7))
        sph((x, y, h), (0.12,) * 3, mat("stalg", (195, 170, 235), 0.7), seg=12)
    # rayos de luz que entran desde arriba
    for (x, y, tilt, r) in [(-2.5, 10, 0.18, 1.3), (3.0, 12, -0.2, 1.0), (0.0, 16, 0.1, 1.6)]:
        o = cone((x, y, 6), r * 0.35, r, 12, mat("shaft", (255, 250, 215), 0.5, emis=1.2, alpha=0.08))
        o.rotation_euler = (0, tilt, 0)
        nomix(o)
        nomix(cyl((x - 6 * math.sin(tilt), y, 0.3), r, 0.02, mat("pool", (255, 245, 210), 0.5, emis=0.5, alpha=0.25), v=48))
    spot((0, 4, 14), (0, 8, 0), 9000, (255, 245, 225), 1.2, 0.8)
    # chispitas (luciérnagas)
    for k in range(40):
        x, y, z = rnd.uniform(-10, 10), rnd.uniform(2, 16), rnd.uniform(1.2, 8)
        if abs(x) < 2.5 and z < 5 and y < 6:
            continue
        c = [(255, 240, 150), (180, 255, 240), (255, 190, 240)][k % 3]
        nomix(sph((x, y, z), (0.06,) * 3, mat(f"spark{c}", c, 0.3, emis=6), seg=8))
    area_light((0, 0, 9), 1600, 12, (1.0, 0.95, 1.0))
    area_light((0, -6, 5), 700, 8, (1, 0.95, 0.95)).rotation_euler = (math.radians(70), 0, 0)


# ------------------------------------------------------------------ fondo del mar
WATER = (70, 160, 215)


def fog(c, y, near=6, far=34, mx=0.85):
    t = min(mx, max(0.0, (y - near) / (far - near)))
    return tuple(int(a + (b - a) * t) for a, b in zip(c, WATER))


def sand_mat():
    m = bpy.data.materials.new("sand")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.95
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    # rayitas de luz (cáusticas) sobre la arena
    vo = nt.nodes.new("ShaderNodeTexVoronoi")
    vo.feature = "DISTANCE_TO_EDGE"
    vo.inputs["Scale"].default_value = 0.55
    nt.links.new(tc.outputs["Object"], vo.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs[1].default_value, mr.inputs[2].default_value = 0.0, 0.06
    mr.inputs[3].default_value, mr.inputs[4].default_value = 0.55, 0.0
    nt.links.new(vo.outputs["Distance"], mr.inputs[0])
    sand = mix_rgb(nt, mr.outputs[0], (232, 200, 140), (250, 235, 190))
    # a lo lejos la arena se pierde en el azul del agua
    fr = nt.nodes.new("ShaderNodeMapRange")
    fr.inputs[1].default_value, fr.inputs[2].default_value = 6.0, 30.0
    fr.inputs[3].default_value, fr.inputs[4].default_value = 0.0, 0.92
    nt.links.new(sep.outputs[1], fr.inputs[0])
    col = mix_rgb(nt, fr.outputs[0], sand, WATER)
    nt.links.new(col, b.inputs["Base Color"])
    # ondulaciones de la arena
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.inputs["Scale"].default_value = 0.7
    wv.inputs["Distortion"].default_value = 3.0
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.35
    nt.links.new(wv.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def seaweed(x, y, h, col, seed, w=0.1, amp=0.35):
    """Alga ondulada (curva NURBS con grosor que se afina hacia la punta)."""
    rnd = random.Random(seed)
    cu = bpy.data.curves.new("weed", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth, cu.bevel_resolution = w, 3
    cu.use_fill_caps = True
    sp = cu.splines.new("NURBS")
    n = 12
    sp.points.add(n - 1)
    ph = rnd.uniform(0, 6)
    for i, p in enumerate(sp.points):
        t = i / (n - 1)
        p.co = (amp * math.sin(ph + t * 8.5) * (0.3 + t), 0.15 * math.sin(ph * 1.3 + t * 5), t * h, 1)
        p.radius = 1.15 - 0.85 * t
    sp.use_endpoint_u, sp.order_u = True, 4
    o = bpy.data.objects.new("weed", cu)
    bpy.context.scene.collection.objects.link(o)
    o.location = (x, y, -0.1)
    o.scale = (1.0, 0.55, 1.0)
    o.data.materials.append(mat(f"weed{col}", col, 0.6))
    # hojitas a los costados
    for i in range(2, n - 1, 2):
        t = i / (n - 1)
        px = x + amp * math.sin(ph + t * 8.5) * (0.3 + t)
        side = 1 if i % 4 else -1
        lf = sph((px + side * 0.18, y, t * h), (0.22 * (1.2 - t), 0.06, 0.09), mat(f"weed{col}", col, 0.6), seg=12)
        lf.rotation_euler = (0, -side * 0.6, 0)
    return o


def branch_coral(x, y, s, col, seed):
    rnd = random.Random(seed)
    m = mat(f"bcoral{col}", col, 0.55)

    def grow(p, d, L, r, depth):
        q = p + d * L
        rod(p, q, r, m, v=12)
        sph(q, (r * 1.25,) * 3, m, seg=12)
        if depth == 0:
            return
        for k in range(2):
            a = rnd.uniform(0.35, 0.7) * (1 if k else -1)
            nd = Vector((d.x * math.cos(a) - d.z * math.sin(a), d.y + rnd.uniform(-0.2, 0.2), d.x * math.sin(a) + d.z * math.cos(a))).normalized()
            grow(q, nd, L * 0.72, r * 0.78, depth - 1)
    grow(Vector((x, y, 0)), Vector((0, 0, 1)), 0.9 * s, 0.13 * s, 3)


def tube_coral(x, y, s, col, seed):
    rnd = random.Random(seed)
    for k in range(6):
        a = k * 2 * math.pi / 6 + rnd.uniform(-0.3, 0.3)
        r = 0.35 * s if k else 0.0
        h = rnd.uniform(0.6, 1.3) * s
        px, py = x + r * math.cos(a), y + r * math.sin(a)
        cyl((px, py, h / 2), 0.17 * s, h, mat(f"tube{col}", col, 0.5))
        torus((px, py, h), 0.17 * s, 0.05 * s, mat(f"tube{col}", col, 0.5))
        cyl((px, py, h - 0.01), 0.14 * s, 0.02, mat("tubein", tuple(int(c * 0.55) for c in col), 0.8))


def fan_coral(x, y, s, col):
    pts = [(1.2 * s * math.cos(a), 1.2 * s * math.sin(a) * 1.1) for a in [math.pi * k / 16 for k in range(17)]]
    o = flat(pts, mat(f"fan{col}", col, 0.6), (x, y, 0.1), 0.05)
    b = o.modifiers.new("b", "BEVEL")
    b.width, b.segments = 0.03, 2
    for k in range(7):
        a = math.pi * (k + 0.5) / 7
        rod((x, y - 0.04, 0.1), (x + 1.1 * s * math.cos(a), y - 0.04, 0.1 + 1.2 * s * math.sin(a)), 0.03 * s,
            mat(f"fanv{col}", tuple(min(255, int(c * 1.25)) for c in col), 0.5), v=6)


def brain_coral(x, y, r, c1, c2):
    sph((x, y, 0.0), (r, 0.9 * r, 0.7 * r), band_mat(f"brain{c1}", c1, c2, 2.2, 9.0, rough=0.6, bump=0.6), seg=32)


def scallop(x, y, s, col, rot=0.0):
    for k in range(7):
        a = math.radians(25 + k * 21.6)
        o = sph((x + 0.22 * s * math.cos(a), y, 0.08 + 0.22 * s * math.sin(a)), (0.25 * s, 0.05 * s, 0.07 * s),
                mat(f"shell{col}", col, 0.4), seg=12)
        o.rotation_euler = (0, -a, 0)
    sph((x, y, 0.08), (0.08 * s, 0.05 * s, 0.05 * s), mat(f"shell{col}", col, 0.4), seg=10)


def starfish(x, y, s, col, spin=0.0):
    o = star((x, y, 0.08), 0.42 * s, mat(f"sf{col}", col, 0.5), 0.12 * s, 0.42, spin)
    o.rotation_euler = (1.25, 0, 0)
    sph((x, y - 0.05, 0.12), (0.06 * s,) * 3, mat("sfdot", (255, 240, 200), 0.5), seg=10)


def fish(x, y, z, s, col, fin, left=True):
    d = -1 if left else 1
    sph((x, y, z), (0.55 * s, 0.25 * s, 0.38 * s), mat(f"fish{col}", col, 0.4))
    flat([(0, 0), (0.45 * s, 0.32 * s), (0.45 * s, -0.32 * s)], mat(f"fin{fin}", fin, 0.5), (x - d * 0.5 * s, y, z), 0.05)\
        .rotation_euler = (0, 0 if d < 0 else math.pi, 0)
    flat([(-0.2 * s, 0), (0.15 * s, 0), (0.0, 0.25 * s)], mat(f"fin{fin}", fin, 0.5), (x, y, z + 0.32 * s), 0.04)
    for k in range(2):
        sph((x - d * (0.1 + 0.18 * k) * s, y - 0.02, z), (0.05 * s, 0.24 * s, 0.33 * s - k * 0.05 * s), mat(f"fin{fin}", fin, 0.5), seg=12)
    sph((x + d * 0.3 * s, y - 0.15 * s, z + 0.08 * s), (0.1 * s,) * 3, mat("eyew", (255, 255, 255), 0.3), seg=12)
    sph((x + d * 0.33 * s, y - 0.23 * s, z + 0.08 * s), (0.05 * s,) * 3, mat("eye", (40, 30, 30), 0.3), seg=10)


def treasure_chest(x, y, s=1.0):
    WD, GD = mat("chest", (170, 100, 55), 0.7), mat("gold", (255, 200, 60), 0.25, emis=0.3)
    cube((x, y, 0.45 * s), (0.8 * s, 0.5 * s, 0.45 * s), WD, 0.05)
    for dx in (-0.6, 0.6):
        cube((x + dx * s, y, 0.45 * s), (0.08 * s, 0.52 * s, 0.47 * s), GD, 0.02)
    cube((x, y - 0.5 * s, 0.75 * s), (0.14 * s, 0.03 * s, 0.17 * s), GD, 0.02)
    # monedas y joyas que brillan
    for k in range(16):
        a = k * 2.4
        sph((x + 0.55 * s * math.cos(a) * (k / 16), y + 0.3 * s * math.sin(a) * (k / 16), 0.9 * s + 0.06 * s * (k % 3)),
            (0.16 * s, 0.16 * s, 0.05 * s), mat("coin", (255, 215, 70), 0.2, emis=1.2), seg=16)
    for (dx, c) in [(-0.3, (255, 60, 110)), (0.25, (90, 200, 255)), (0.05, (120, 240, 140))]:
        sph((x + dx * s, y - 0.1 * s, 1.02 * s), (0.11 * s,) * 3, mat(f"gem{c}", c, 0.1, emis=1.5), seg=16)
    # tapa abierta hacia atrás
    th = -1.95
    hy, hz = y + 0.5 * s, 0.9 * s
    oy, oz = -0.5 * s, 0.14 * s
    cy = hy + oy * math.cos(th) - oz * math.sin(th)
    cz = hz + oy * math.sin(th) + oz * math.cos(th)
    o = cube((x, cy, cz), (0.82 * s, 0.5 * s, 0.14 * s), WD, 0.06)
    o.rotation_euler = (th, 0, 0)
    for dx in (-0.6, 0.6):
        o = cube((x + dx * s, cy, cz), (0.08 * s, 0.52 * s, 0.16 * s), GD, 0.02)
        o.rotation_euler = (th, 0, 0)
    point((x, y - 0.6 * s, 1.4 * s), 120 * s, (255, 210, 110), 0.4, shadow=False)


def bubble(loc, r):
    nomix(sph(loc, (r,) * 3, mat("bubble", (220, 245, 255), 0.05, emis=0.25, alpha=0.3), seg=16))
    nomix(sph((loc[0] - r * 0.35, loc[1] - r * 0.6, loc[2] + r * 0.4), (r * 0.25, r * 0.1, r * 0.2),
              mat("bubhl", (255, 255, 255), 0.2, emis=1.5), seg=8))


def sea(portrait):
    world((90, 170, 235), 1.0)
    ground(sand_mat(), bumps=0.3)
    rnd = random.Random(7)
    # arrecife lejano azulado (se pierde en el agua)
    for (x, y, sx, sz) in [(-20, 34, 14, 5), (6, 38, 18, 6), (26, 32, 12, 4), (-6, 44, 22, 8), (-34, 40, 14, 6)]:
        sph((x, y, -1), (sx, 6, sz), mat(f"reef{y}", fog((120, 150, 170), y, mx=0.9), 0.9), seg=40)
    for k in range(18):
        x, y = rnd.uniform(-22, 22), rnd.uniform(20, 30)
        sph((x, y, 0.3), (rnd.uniform(0.8, 1.8),) * 2 + (rnd.uniform(0.8, 1.6),), mat(f"farcoral{k % 3}",
            fog([(255, 130, 150), (255, 180, 90), (190, 130, 255)][k % 3], y, mx=0.8), 0.7), seg=20)
    for k in range(10):
        x, y = rnd.choice([-1, 1]) * rnd.uniform(4, 16), rnd.uniform(16, 26)
        seaweed(x, y, rnd.uniform(3, 5), fog((60, 170, 110), y, mx=0.75), 100 + k, 0.12)
    # rocas redondas con algas verdes
    for (x, y, r) in [(-8.5, 6.5, 1.6), (-7.4, 7.6, 1.0), (9.0, 7.0, 1.5), (8.0, 8.4, 0.9), (-12, 12, 2.4), (12.5, 13, 2.4),
                      (-4.5, 15, 1.4), (5.0, 16, 1.6)]:
        c = fog((150, 160, 195), y, mx=0.6)
        sph((x, y, 0), (r, 0.85 * r, 0.75 * r), mat(f"srock{c}", c, 0.85), seg=32)
        sph((x - 0.2 * r, y - 0.1, 0.65 * r), (0.6 * r, 0.5 * r, 0.18 * r), mat(f"moss{y}", fog((110, 200, 120), y, mx=0.6), 0.9), seg=20)
    # corales de colores
    for (x, y, s, col, sd) in [(-5.8, 4.0, 1.0, (255, 110, 150), 1), (6.4, 4.6, 0.9, (255, 150, 70), 2), (-10.0, 9.5, 1.2, (255, 130, 200), 3),
                               (10.5, 10.0, 1.1, (255, 110, 120), 4), (-2.8, 11.5, 0.9, (255, 170, 80), 5), (3.2, 12.5, 1.0, (255, 120, 170), 6)]:
        branch_coral(x, y, s, fog(col, y, mx=0.5), sd)
    for (x, y, s, col, sd) in [(-7.0, 3.2, 1.0, (180, 120, 255), 1), (7.6, 3.6, 0.9, (255, 210, 70), 2), (-4.2, 8.5, 0.8, (90, 220, 210), 3),
                               (4.8, 9.0, 0.9, (180, 120, 255), 4)]:
        tube_coral(x, y, s, fog(col, y, mx=0.5), sd)
    fan_coral(-6.4, 9.2, 1.3, (200, 90, 220))
    fan_coral(7.2, 11.0, 1.4, (255, 120, 140))
    fan_coral(-1.5, 16.5, 1.2, fog((255, 160, 90), 16.5))
    for (x, y, r, c1, c2) in [(-4.6, 5.6, 0.7, (255, 170, 120), (240, 130, 100)), (5.2, 6.4, 0.75, (170, 230, 130), (130, 200, 110)),
                              (-9.0, 3.0, 0.6, (255, 200, 100), (240, 160, 80)), (2.0, 14.0, 0.9, (255, 150, 180), (230, 110, 150))]:
        brain_coral(x, y, r, c1, c2)
    # algas onduladas
    WC = [(60, 180, 110), (90, 200, 100), (40, 160, 120), (120, 210, 90)]
    for k, (x, y, h) in enumerate([(-8.0, 4.8, 3.5), (-8.8, 5.6, 4.8), (-7.6, 6.0, 3.0), (8.4, 5.2, 4.0), (9.2, 5.8, 5.0),
                                   (7.8, 6.2, 3.2), (-11, 8, 5.5), (11.5, 8.5, 5.5), (-5.2, 10.5, 3.2), (5.8, 11.0, 3.4),
                                   (-3.6, 4.2, 2.2), (3.8, 4.4, 2.4), (-0.8, 14.5, 3.0), (1.2, 15.5, 3.6)]):
        seaweed(x, y, h, fog(WC[k % 4], y, mx=0.5), k, 0.1)
    # caracoles, estrellas de mar y cofre del tesoro
    for (x, y, s, c) in [(-3.2, 2.4, 0.8, (255, 190, 200)), (3.6, 1.8, 0.7, (255, 225, 180)), (-6.4, 1.8, 0.9, (255, 170, 140)),
                         (6.0, 2.6, 0.8, (255, 205, 220))]:
        scallop(x, y, s, c)
    for (x, y, s, c, sp) in [(-4.2, 1.2, 0.9, (255, 140, 70), 0.2), (4.6, 1.0, 0.8, (255, 110, 140), 0.6),
                             (-2.6, 6.2, 0.7, (255, 200, 70), 0.1), (2.6, 7.5, 0.7, (200, 120, 255), 0.4)]:
        starfish(x, y, s, c, sp)
    for (x, y, s) in [(-5.2, 2.8, 0.8), (5.4, 3.2, 0.7)]:
        cone((x, y, 0.25 * s), 0.25 * s, 0.0, 0.7 * s, band_mat("spiral", (255, 230, 200), (240, 170, 140), 6, 0, rough=0.4, bump=0.2),
             rot=(0, math.radians(70), 0))
    treasure_chest(6.6, 7.8, 1.0)
    # peces de colores
    for (x, y, z, s, c, f, l) in [(-6.5, 6, 4.5, 0.8, (255, 160, 50), (255, 255, 255), False), (7.0, 7, 5.2, 0.7, (255, 220, 70), (90, 170, 255), True),
                                  (-3.5, 12, 6.5, 0.6, (120, 200, 255), (255, 220, 70), True), (4.0, 13, 3.6, 0.6, (255, 120, 170), (255, 220, 90), False),
                                  (-9.0, 14, 7.5, 0.7, (170, 120, 255), (255, 180, 220), False), (2.0, 8, 8.5, 0.55, (255, 130, 90), (255, 255, 255), True),
                                  (-1.5, 9, 10.5, 0.6, (90, 220, 190), (255, 230, 120), False)]:
        fish(x, y, z, s, c, f, l)
    # burbujas (columnas desde el cofre y los corales)
    for (bx, by) in [(6.6, 7.4), (-5.8, 3.8), (3.2, 12.2)]:
        z = 1.4
        for k in range(10):
            z += rnd.uniform(0.5, 0.9)
            bubble((bx + 0.25 * math.sin(k * 1.7), by, z), rnd.uniform(0.07, 0.18))
    for k in range(22):
        x, y, z = rnd.uniform(-12, 12), rnd.uniform(3, 18), rnd.uniform(2, 12)
        if abs(x) < 2.5 and z < 5 and y < 6:
            continue
        bubble((x, y, z), rnd.uniform(0.06, 0.15))
    # rayos de sol que bajan desde la superficie
    for (x, y, w, tilt) in [(-6, 14, 1.4, 0.25), (-1.5, 18, 1.0, 0.2), (3.5, 15, 1.8, 0.22), (9, 19, 1.2, 0.28)]:
        o = flat([(-w / 2, 0), (w / 2, 0), (w * 1.1, 18), (-w * 1.1, 18)], mat("ray", (230, 250, 255), 0.5, emis=1.0, alpha=0.05),
                 (x, y, -1), 0.01)
        o.rotation_euler = (0, tilt, 0)
        nomix(o)
    area_light((0, 2, 12), 1400, 16, (0.85, 0.95, 1.0))
    area_light((0, -6, 5), 500, 8, (0.9, 0.97, 1.0)).rotation_euler = (math.radians(70), 0, 0)


# ------------------------------------------------------------------ escenario de canciones y juegos
def planks(name, c1, c2, grout):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.35
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.5
    br.inputs["Color1"].default_value = tuple(srgb2lin(x) for x in c1) + (1,)
    br.inputs["Color2"].default_value = tuple(srgb2lin(x) for x in c2) + (1,)
    br.inputs["Mortar"].default_value = tuple(srgb2lin(x) for x in grout) + (1,)
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = 0.02
    br.inputs["Brick Width"].default_value = 0.5
    br.inputs["Row Height"].default_value = 3.0
    br.inputs["Bias"].default_value = 0.0
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    return m


def tassel(x, y, z, s=1.0):
    G = mat("goldt", (255, 200, 60), 0.3, emis=0.2)
    sph((x, y, z), (0.1 * s,) * 3, G, seg=12)
    cone((x, y, z - 0.28 * s), 0.05 * s, 0.14 * s, 0.4 * s, G)


def balloons(x, y, z, cols, seed):
    rnd = random.Random(seed)
    for k, c in enumerate(cols):
        bx, bz = x + rnd.uniform(-0.6, 0.6), z + rnd.uniform(-0.4, 0.6)
        by = y + rnd.uniform(-0.3, 0.3)
        sph((bx, by, bz), (0.42, 0.4, 0.5), mat(f"bal{c}", c, 0.15))
        cone((bx, by, bz - 0.52), 0.06, 0.0, 0.1, mat(f"bal{c}", c, 0.15), rot=(math.pi, 0, 0))
        sph((bx - 0.14, by - 0.36, bz + 0.18), (0.07, 0.03, 0.12), mat("balhl", (255, 255, 255), 0.2, emis=1.0), seg=8)
        rod((bx, by, bz - 0.55), (x, y, 0.9), 0.01, mat("string", (250, 250, 250), 0.6), v=6)


def music_note(x, y, z, s, col):
    m = mat(f"note{col}", col, 0.3, emis=1.2)
    o = sph((x, y, z), (0.28 * s, 0.1 * s, 0.2 * s), m, seg=16)
    o.rotation_euler = (0, 0.4, 0)
    rod((x + 0.24 * s, y, z + 0.05 * s), (x + 0.24 * s, y, z + 1.0 * s), 0.04 * s, m, v=8)
    o = cube((x + 0.42 * s, y, z + 0.88 * s), (0.2 * s, 0.05 * s, 0.07 * s), m, 0.03)
    o.rotation_euler = (0, -0.5, 0)


def show(portrait):
    world((120, 80, 170), 0.6)
    bpy.ops.mesh.primitive_plane_add(size=60)
    bpy.context.object.data.materials.append(planks("stagewood", (230, 160, 95), (215, 140, 80), (160, 95, 55)))
    # tarima de atrás, redonda, con lucecitas en el borde
    cyl((0, 9.5, 0.3), 7.5, 0.6, mat("riser", (120, 60, 180), 0.5), v=96).scale = (1, 0.5, 1)
    torus((0, 9.5, 0.6), 7.5, 0.08, mat("goldtrim", (255, 200, 60), 0.25, emis=0.4), sc=(1, 0.5, 1))
    for k in range(30):
        a = math.pi + (k + 0.5) * math.pi / 30
        nomix(sph((7.45 * math.cos(a), 9.5 + 3.72 * math.sin(a), 0.32), (0.1, 0.06, 0.1),
                  mat("foot", (255, 230, 150), 0.3, emis=5.0), seg=10))
    # fondo azul violeta con una gran estrella y chispitas
    cube((0, 13.2, 7), (16, 0.2, 9), mat("backdrop", (70, 55, 170), 0.85), 0.01)
    star((0, 12.9, 3.9), 2.4, mat("bstar2", (255, 130, 200), 0.5, emis=0.6), 0.1)
    star((0, 12.75, 3.9), 2.0, mat("bstar", (255, 215, 70), 0.35, emis=1.2), 0.18)
    for k in range(10):
        a = math.pi / 2 + k * math.pi / 5
        rr = 2.55 if k % 2 == 0 else 2.55 * 0.48
        nomix(sph((rr * 1.0 * math.cos(a), 12.6, 3.9 + rr * math.sin(a)), (0.12,) * 3, mat("sbulb", (255, 250, 220), 0.3, emis=6.0), seg=10))
    rnd = random.Random(2)
    SP = [(255, 230, 120), (255, 255, 255), (255, 150, 220), (140, 220, 255)]
    for k in range(60):
        x, z = rnd.uniform(-13, 13), rnd.uniform(1.0, 13)
        if abs(x) < 3.0 and 1.0 < z < 7.0:
            continue
        c = SP[k % 4]
        if k % 3 == 0:
            star((x, 13.0, z), rnd.uniform(0.15, 0.35), mat(f"spk{c}", c, 0.3, emis=2.5), 0.03, 0.4, rnd.uniform(0, 1))
        else:
            disc((x, 13.0, z), rnd.uniform(0.05, 0.1), mat(f"spk{c}", c, 0.3, emis=2.5), 0.02, v=12)
    # arco de bombitas alrededor del fondo
    for k in range(29):
        a = k * math.pi / 28
        nomix(sph((6.3 * math.cos(a), 12.8, 0.6 + 6.0 * math.sin(a)), (0.13,) * 3,
                  mat(f"arc{k % 3}", [(255, 230, 140), (255, 140, 200), (140, 220, 255)][k % 3], 0.3, emis=5.0), seg=10))
    torus((0, 12.9, 0.6), 6.3, 0.09, mat("goldtrim", (255, 200, 60), 0.25, emis=0.4), rot=(math.pi / 2, 0, 0))
    # notas musicales a los costados del fondo
    for (x, z, s, c) in [(-4.6, 3.2, 0.8, (255, 140, 200)), (4.4, 4.4, 0.7, (140, 220, 255)), (-5.4, 6.0, 0.6, (255, 220, 100)),
                         (5.6, 1.8, 0.6, (170, 255, 160))]:
        music_note(x, 12.85, z, s, c)
    # telones rojos con pliegues, flecos dorados, alzapaños y borlas
    for sgn in (-1, 1):
        for k in range(9):
            x = sgn * (8.2 + k * 0.55)
            col = [(215, 40, 75), (185, 30, 65)][k % 2]
            o = cyl((x, 10.5 - 0.15 * (k % 2), 7), 0.36, 14, mat(f"curt{col}", col, 0.75), v=20)
            o.scale = (1, 0.7, 1)
        rod((sgn * 8.0, 10.1, 0.25), (sgn * 13.2, 10.1, 0.25), 0.12, mat("goldtrim", (255, 200, 60), 0.25, emis=0.4))
        rod((sgn * 7.7, 9.85, 3.1), (sgn * 10.4, 9.85, 3.35), 0.1, mat("goldtrim", (255, 200, 60), 0.25, emis=0.4))
        sph((sgn * 7.75, 9.8, 3.1), (0.18,) * 3, mat("goldtrim", (255, 200, 60), 0.25, emis=0.4), seg=16)
        tassel(sgn * 7.75, 9.75, 2.85, 1.5)
    # bambalina de arriba: ondas rojas con borde dorado y borlas
    for k in range(-9, 10):
        x = k * 1.5
        sph((x, 10.2, 7.6), (0.85, 0.3, 0.55), mat("valance", (215, 40, 75), 0.75), seg=24)
        torus((x, 9.95, 7.35), 0.75, 0.06, mat("goldtrim", (255, 200, 60), 0.25, emis=0.4), rot=(math.pi / 2, 0, 0), sc=(1, 0.7, 1))
        tassel(x + 0.75, 9.9, 7.4, 1.0)
    cube((0, 10.3, 8.6), (16, 0.35, 0.7), mat("valance", (215, 40, 75), 0.75), 0.05)
    rod((-16, 9.95, 8.0), (16, 9.95, 8.0), 0.1, mat("goldtrim", (255, 200, 60), 0.25, emis=0.4))
    # guirnalda de banderines
    BC = [(255, 110, 140), (255, 210, 70), (110, 190, 255), (130, 215, 120), (190, 140, 255)]
    bunting(-7.8, 7.8, 6.6, 9.9, 0.6, BC, n=18, size=0.42)
    # globos a los costados
    balloons(-6.6, 8.6, 3.2, [(255, 90, 120), (255, 210, 70), (110, 190, 255), (170, 120, 255)], 3)
    balloons(6.8, 8.4, 3.4, [(120, 220, 130), (255, 140, 200), (255, 170, 70), (110, 190, 255)], 4)
    # reflectores de colores colgados de una barra (se ven en el vertical)
    rod((-9, 8.5, 10.5), (9, 8.5, 10.5), 0.12, mat("truss", (60, 60, 80), 0.4))
    BEAM = [(255, 110, 200), (110, 210, 255), (255, 230, 110), (150, 255, 150)]
    for k, x in enumerate((-6.0, -2.0, 2.0, 6.0)):
        c = BEAM[k]
        o = cyl((x, 8.5, 10.0), 0.35, 0.8, mat("can", (40, 40, 55), 0.4))
        look(o, (x * 0.2, 2.5, 0))
        spot((x, 8.0, 9.6), (x * 0.25, 3.0, 0), 2500, c, 0.5, 0.5)
        tgt = Vector((x * 0.25, 3.0, 0))
        src = Vector((x, 8.0, 9.6))
        dv = tgt - src
        bo = cone((src + tgt) / 2, 1.5, 0.22, dv.length, mat(f"beam{c}", c, 0.5, emis=1.0, alpha=0.05))
        bo.rotation_euler = dv.to_track_quat("-Z", "Y").to_euler()
        nomix(bo)
    # luces de candilejas a los costados del frente
    for sgn in (-1, 1):
        for k in range(4):
            x, y = sgn * (5.0 + k * 0.9), 0.5 + k * 1.3
            sph((x, y, 0.0), (0.32, 0.26, 0.2), mat("goldtrim", (255, 200, 60), 0.25, emis=0.4), seg=20)
            nomix(sph((x, y - 0.1, 0.16), (0.16, 0.12, 0.12), mat("foot", (255, 230, 150), 0.3, emis=5.0), seg=12))
    area_light((0, 2, 10), 1500, 12, (1.0, 0.95, 1.0))
    area_light((0, -6, 5), 600, 8, (1, 0.92, 0.95)).rotation_euler = (math.radians(70), 0, 0)


THEMES = {"meadow": lambda p: meadow(p), "night": lambda p: meadow(p, night=True), "room": room, "bath": bath, "snow": snow,
          "xmas": xmas, "cave": cave, "sea": sea, "show": show}
SUN = {"meadow": (3.5, (1, 0.95, 0.88)), "night": (0.6, (0.6, 0.7, 1.0)), "room": (2.2, (1, 0.95, 0.9)), "bath": (2.0, (1, 0.97, 0.95)),
       "snow": (2.6, (1, 0.93, 0.82)), "xmas": (1.2, (0.6, 0.7, 1.0)), "cave": (0.3, (0.7, 0.6, 1)),
       "sea": (1.7, (0.8, 0.93, 1)), "show": (0.3, (1, 0.9, 1))}

for th, fn in THEMES.items():
    if ONLY and th not in ONLY:
        continue
    for portrait in (False, True):
        W, H = (1080, 1920) if portrait else (1920, 1080)
        p = os.path.join(OUT, f"{th}_{'v' if portrait else 'h'}.png")
        if os.path.exists(p):
            continue
        sc = reset(W, H)
        camera(sc, portrait)
        e, c = SUN[th]
        sun(sc, e, c)
        fn(portrait)
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        print("OK", th, portrait, flush=True)
