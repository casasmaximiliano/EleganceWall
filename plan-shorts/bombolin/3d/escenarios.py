"""Escenarios 3D de Bombolín (Blender / bpy). Se renderizan una vez por tema y orientación,
con el cielo transparente; después se combinan con un cielo de dibujo animado (degradé + estrellas).

Uso: python3 escenarios.py CARPETA_SALIDA [tema ...]
Temas: meadow room night snow xmas cave sea show
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
    c = tuple(x / 255 for x in col) + (1,)
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


def tree(x, y, s=1.0, snowy=False, pine=False):
    cyl((x, y, 0.8 * s), 0.18 * s, 1.6 * s, mat("trunk", (140, 95, 55)))
    if pine:
        for k in range(3):
            cone((x, y, (1.6 + k * 0.8) * s), (1.3 - k * 0.35) * s, 0.05, 1.3 * s,
                 mat("snowpine" if snowy else "pine", (235, 245, 255) if snowy else (60, 150, 90)))
        return
    for (dx, dz, r) in [(0, 2.4, 1.0), (-0.6, 2.0, 0.75), (0.6, 2.0, 0.75), (0, 2.9, 0.7)]:
        sph((x + dx * s, y, dz * s), (r * s, r * s, r * s), mat("leaves", (95, 185, 95), 0.8))


def flowers(n, area, seed=1):
    rnd = random.Random(seed)
    cols = [(255, 120, 150), (255, 225, 80), (255, 255, 255), (180, 140, 255), (255, 160, 70)]
    for _ in range(n):
        x, y = rnd.uniform(*area[0]), rnd.uniform(*area[1])
        cyl((x, y, 0.15), 0.015, 0.3, mat("stem", (70, 160, 70)))
        sph((x, y, 0.32), (0.09, 0.09, 0.06), mat(f"fl{rnd.randint(0, 4)}", cols[rnd.randint(0, 4)], 0.5))


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


# ------------------------------------------------------------------ temas
def meadow(portrait, night=False):
    ground(mat("grass", (110, 200, 100) if not night else (60, 90, 120), 0.9))
    hills([(125, 210, 115), (100, 190, 95)] if not night else [(55, 80, 120), (45, 70, 110)])
    for (x, y, s) in [(-7, 7, 1.0), (7.5, 9, 1.2), (-11, 14, 1.3), (12, 16, 1.1), (-3.5, 20, 1.0), (4, 22, 0.9)]:
        tree(x, y, s)
    for (x, y) in [(-5, 3), (5.2, 4), (-8, 10), (9, 12)]:
        sph((x, y, 0.3), (0.9, 0.8, 0.6), mat("bush", (80, 170, 85), 0.85))
    flowers(70, ((-9, 9), (-1, 12)))
    if not night:
        clouds()
        sph((14, 40, 14), (2.2, 2.2, 2.2), mat("sunball", (255, 225, 90), 0.5, emis=3))
    else:
        sph((-12, 40, 14), (2.0, 2.0, 2.0), mat("moon", (255, 245, 200), 0.5, emis=2.5))


def room(portrait):
    wood = bpy.data.materials.new("wood")
    wood.use_nodes = True
    nt = wood.node_tree
    b = nt.nodes["Principled BSDF"]
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.inputs["Scale"].default_value = 8.0
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].color = (0.5, 0.3, 0.17, 1)
    rp.color_ramp.elements[1].color = (0.78, 0.55, 0.36, 1)
    nt.links.new(wv.outputs["Fac"], rp.inputs["Fac"])
    nt.links.new(rp.outputs["Color"], b.inputs["Base Color"])
    bpy.ops.mesh.primitive_plane_add(size=40)
    bpy.context.object.data.materials.append(wood)
    cube((0, 9, 8), (20, 0.2, 9), mat("wall", (255, 214, 190), 0.9), 0.01)
    cube((-11, 0, 8), (0.2, 20, 9), mat("wall2", (250, 200, 175), 0.9), 0.01)
    cube((11, 0, 8), (0.2, 20, 9), mat("wall2", (250, 200, 175), 0.9), 0.01)
    cube((4.5, 8.7, 4.2), (2.2, 0.15, 1.7), mat("frame", (255, 255, 255), 0.4))
    cube((4.5, 8.6, 4.2), (1.9, 0.12, 1.45), mat("glass", (150, 205, 255), 0.2, emis=0.35))
    cyl((0, 2, 0.02), 4.5, 0.04, mat("rug", (255, 170, 190), 0.95), v=64)
    cube((-6.5, 7.5, 1.0), (1.6, 0.9, 1.0), mat("toybox", (255, 190, 90), 0.5))
    for k, c in enumerate([(255, 100, 100), (100, 170, 255), (120, 210, 120), (255, 220, 90), (190, 140, 255)]):
        cube((-7.5 + k * 0.55, 8.4, 3.4), (0.2, 0.5, 0.7 + 0.1 * (k % 2)), mat(f"book{k}", c, 0.5), 0.02)
    cube((-6.2, 8.5, 2.6), (2.0, 0.4, 0.08), mat("shelf", (200, 140, 90), 0.6))
    sph((-6.5, 7.0, 2.4), (0.45, 0.45, 0.45), mat("ball", (255, 90, 120), 0.4))
    cyl((7.5, 7.5, 1.4), 0.08, 2.8, mat("lampstem", (240, 240, 240), 0.4))
    cone((7.5, 7.5, 3.0), 0.8, 0.4, 0.8, mat("lampshade", (255, 240, 180), 0.6, emis=0.8))
    L = bpy.data.lights.new("ceiling", "AREA")
    L.energy, L.size = 450, 10
    o = bpy.data.objects.new("ceil", L)
    bpy.context.scene.collection.objects.link(o)
    o.location = (0, 2, 9)


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


THEMES = {"meadow": lambda p: meadow(p), "night": lambda p: meadow(p, night=True), "room": room, "snow": snow,
          "xmas": xmas, "cave": cave, "sea": sea, "show": show}
SUN = {"meadow": (3.5, (1, 0.95, 0.88)), "night": (0.6, (0.6, 0.7, 1.0)), "room": (1.0, (1, 0.95, 0.9)),
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
