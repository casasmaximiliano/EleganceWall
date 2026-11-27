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


def snow(portrait, night=False):
    ground(mat("snowg", (245, 250, 255), 0.7), bumps=0.35)
    for (x, y, s) in [(-7, 8, 1.0), (7, 10, 1.2), (-11, 15, 1.4), (12, 17, 1.1), (-3, 21, 1.0), (4, 24, 1.0)]:
        tree(x, y, s, snowy=True, pine=True)
    for (x, y, r) in [(5.5, 5, 0.9), (5.5, 5, 0.6), (5.5, 5, 0.42)]:
        pass
    sph((5.5, 5, 0.8), (0.9, 0.9, 0.85), mat("snowman", (250, 252, 255), 0.6))
    sph((5.5, 5, 2.1), (0.6, 0.6, 0.6), mat("snowman", (250, 252, 255), 0.6))
    cone((5.5, 4.45, 2.15), 0.09, 0.0, 0.5, mat("carrot", (255, 140, 40), 0.5), rot=(math.radians(90), 0, 0))
    for dx in (-0.2, 0.2):
        sph((5.5 + dx, 4.5, 2.3), (0.07, 0.07, 0.07), mat("coal", (30, 30, 35), 0.4))
    hills([(235, 242, 255), (220, 232, 250)])
    if night:
        sph((-12, 40, 14), (2.0, 2.0, 2.0), mat("moon", (255, 245, 200), 0.5, emis=2.5))
    else:
        clouds()


def xmas(portrait):
    snow(portrait, night=True)
    cone((-5.5, 6, 1.6), 1.6, 0.05, 3.2, mat("xtree", (40, 140, 80), 0.7))
    cone((-5.5, 6, 3.2), 1.1, 0.05, 2.2, mat("xtree", (40, 140, 80), 0.7))
    sph((-5.5, 6, 4.5), (0.3, 0.3, 0.3), mat("star", (255, 210, 50), 0.3, emis=2.0))
    rnd = random.Random(5)
    cols = [(255, 80, 80), (255, 210, 60), (90, 170, 255), (255, 255, 255)]
    for k in range(26):
        h = rnd.uniform(0.4, 3.8)
        r = 1.6 * (1 - h / 4.6) + 0.05
        a = rnd.uniform(0, 2 * math.pi)
        sph((-5.5 + r * math.cos(a), 6 + r * math.sin(a), h), (0.11, 0.11, 0.11), mat(f"bulb{k % 4}", cols[k % 4], 0.3, emis=1.6))
    for k in range(3):
        cube((-4.6 + k * 0.7, 5.0, 0.3), (0.3, 0.3, 0.3), mat(f"gift{k}", [(255, 90, 120), (90, 170, 255), (255, 210, 70)][k], 0.5))


def cave(portrait):
    rock = mat("rock", (110, 85, 150), 0.95)
    ground(mat("cavefloor", (90, 70, 120), 0.95), bumps=0.4)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, location=(0, 2, 0))
    o = bpy.context.object
    o.scale = (24, 22, 10)
    t = bpy.data.textures.new("rockt", "CLOUDS")
    t.noise_scale = 1.5
    d = o.modifiers.new("d", "DISPLACE")
    d.texture, d.strength = t, 1.2
    o.data.materials.append(rock)
    bpy.ops.object.shade_smooth()
    rnd = random.Random(3)
    cols = [(120, 255, 230), (255, 150, 230), (255, 240, 120)]
    for k in range(18):
        x, y = rnd.uniform(-10, 10), rnd.uniform(3, 18)
        cone((x, y, 0.5), rnd.uniform(0.15, 0.35), 0.0, rnd.uniform(0.8, 1.8), mat(f"cry{k % 3}", cols[k % 3], 0.2, emis=1.0),
             rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), 0))
    for k in range(20):
        x, y = rnd.uniform(-12, 12), rnd.uniform(4, 20)
        cone((x, y, 7.5), rnd.uniform(0.3, 0.6), 0.0, rnd.uniform(1.5, 3.5), mat("stal", (150, 125, 185), 0.8),
             rot=(math.pi, 0, 0))
    L = bpy.data.lights.new("glow", "POINT")
    L.energy, L.color = 3000, (0.8, 0.6, 1)
    o = bpy.data.objects.new("glow", L)
    bpy.context.scene.collection.objects.link(o)
    o.location = (0, 2, 5)


def sea(portrait):
    ground(mat("sand", (240, 215, 150), 0.95), bumps=0.3)
    rnd = random.Random(7)
    for k in range(16):
        x, y = rnd.uniform(-12, 12), rnd.uniform(4, 22)
        h = rnd.uniform(1.5, 4.5)
        o = cyl((x, y, h / 2), 0.12, h, mat("weed", (60, 170, 110), 0.7))
        o.rotation_euler = (rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), 0)
    for k in range(12):
        x, y = rnd.uniform(-11, 11), rnd.uniform(4, 16)
        sph((x, y, 0.3), (rnd.uniform(0.4, 0.9),) * 2 + (0.5,), mat(f"coral{k % 3}", [(255, 120, 140), (255, 170, 80), (180, 120, 255)][k % 3], 0.6))
    for k in range(25):
        sph((rnd.uniform(-12, 12), rnd.uniform(3, 18), rnd.uniform(1, 8)), (0.12,) * 3, mat("bubble", (220, 245, 255), 0.05, alpha=0.4))
    sun(bpy.context.scene, 2.5, (0.75, 0.9, 1.0))


def show(portrait):
    bpy.ops.mesh.primitive_plane_add(size=60)
    bpy.context.object.data.materials.append(mat("showfloor", (90, 40, 150), 0.6))
    cyl((0, 3, 0.15), 6.5, 0.3, mat("stage", (255, 200, 80), 0.4), v=96)
    for s in (-1, 1):
        for k in range(8):
            cyl((s * (7 + k * 0.6), 9, 5), 0.45, 10, mat("curtain", (220, 50, 90), 0.8))
    cube((0, 10, 5), (14, 0.3, 6), mat("backdrop", (110, 60, 190), 0.8), 0.01)
    rnd = random.Random(2)
    for k in range(24):
        sph((rnd.uniform(-12, 12), 9.6, rnd.uniform(2, 10)), (0.15,) * 3, mat(f"dot{k % 3}", [(255, 230, 120), (255, 255, 255), (255, 150, 200)][k % 3], 0.3, emis=4))
    for s in (-1, 1):
        L = bpy.data.lights.new("spot", "SPOT")
        L.energy, L.spot_size = 4000, 0.6
        o = bpy.data.objects.new("spot", L)
        bpy.context.scene.collection.objects.link(o)
        o.location = (s * 6, -4, 9)
        look(o, (0, 3, 0))


THEMES = {"meadow": lambda p: meadow(p), "night": lambda p: meadow(p, night=True), "room": room, "bath": bath, "snow": snow,
          "xmas": xmas, "cave": cave, "sea": sea, "show": show}
SUN = {"meadow": (3.5, (1, 0.95, 0.88)), "night": (0.6, (0.6, 0.7, 1.0)), "room": (2.2, (1, 0.95, 0.9)), "bath": (2.0, (1, 0.97, 0.95)),
       "snow": (3.0, (1, 0.97, 0.95)), "xmas": (0.7, (0.6, 0.7, 1.0)), "cave": (0.3, (0.7, 0.6, 1)),
       "sea": (1.5, (0.7, 0.9, 1)), "show": (0.5, (1, 0.9, 1))}

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
