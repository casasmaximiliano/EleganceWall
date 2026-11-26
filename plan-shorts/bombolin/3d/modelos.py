"""Modelos 3D de Bombolín y sus amigos (Blender / bpy) y render de sus «estados» como sprites con transparencia.

Uso: python3 modelos.py CARPETA_SALIDA [personaje ...]
Cada personaje se renderiza con EEVEE en todas sus variantes: boca cerrada/abierta, ojos abiertos/cerrados,
(Lula: 5 ánimos; Zumbi: 2 posiciones de alas). Los sprites se usan después en la animación a 60 fps.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
ONLY = sys.argv[2:]
os.makedirs(OUT, exist_ok=True)


# ------------------------------------------------------------------ utilidades
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = 32
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = 900
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.35
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.85, 0.9, 1.0, 1)
    bg.inputs[1].default_value = 0.35
    sc.world = w
    return sc


_mats = {}


def mat(name, color, rough=0.45, emis=0.0, alpha=1.0, sss=0.0, metal=0.0):
    key = (name, color, rough, emis, alpha)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    c = tuple(x / 255 for x in color) + (1,)
    b.inputs["Base Color"].default_value = c
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Coat Weight" in b.inputs:
        b.inputs["Coat Weight"].default_value = 0.15
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
    if emis:
        b.inputs["Emission Color"].default_value = c
        b.inputs["Emission Strength"].default_value = emis
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
    _mats[key] = m
    return m


def sphere(loc, scale, m, seg=48, name="s"):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


def cone(loc, r1, r2, depth, m, rot=(0, 0, 0), name="c"):
    bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    sub = o.modifiers.new("sub", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 2
    return o


def cyl(loc, r, depth, m, rot=(0, 0, 0), name="cy"):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


def torus(loc, R, r, m, rot=(0, 0, 0), name="t", arc=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot,
                                     major_segments=64, minor_segments=16)
    o = bpy.context.object
    o.name = name
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    if arc is not None:  # recortar a un arco (para sonrisas y párpados): bisect
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.bisect(plane_co=o.location, plane_no=arc, clear_inner=True)
        bpy.ops.object.mode_set(mode="OBJECT")
    return o


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def camera_and_lights(sc, target=(0, 0, 1.0), dist=6.0, height=1.6, lens=60, ortho=None):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    cam.location = (dist * math.sin(math.radians(18)), -dist * math.cos(math.radians(18)), height)
    cam.data.lens = lens
    if ortho:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ortho
    look_at(cam, target)
    sc.camera = cam
    for name, loc, energy, size, color in [("key", (-3, -4, 5), 260, 4, (1, 0.96, 0.9)),
                                           ("fill", (4, -3, 2.5), 90, 5, (0.85, 0.9, 1)),
                                           ("rim", (0, 4, 4), 220, 3, (1, 1, 1))]:
        L = bpy.data.lights.new(name, "AREA")
        L.energy, L.size, L.color = energy, size, color
        o = bpy.data.objects.new(name, L)
        sc.collection.objects.link(o)
        o.location = loc
        look_at(o, target)
    return cam


def eye(x, y, z, r, iris, closed, skin, lashes=False, look=(0, -1, 0)):
    """Ojo de dibujo animado: blanco + iris + pupila + brillos. Cerrado: párpado de piel + línea."""
    parts = []
    if closed:
        parts.append(sphere((x, y + r * 0.05, z), (r * 1.04, r * 1.04, r * 1.04), skin, name="lid"))
        parts.append(torus((x, y - r * 0.98, z - r * 0.1), r * 0.62, r * 0.09, mat("ink", (40, 35, 55), 0.6),
                           rot=(math.radians(90), 0, 0), name="lidline", arc=(0, 0, 1)))
        parts[-1].rotation_euler = (math.radians(90), 0, math.radians(180))
        return parts
    parts.append(sphere((x, y, z), (r, r * 0.85, r * 1.08), mat("eyewhite", (255, 255, 255), 0.25), name="eyew"))
    parts.append(sphere((x + r * 0.05, y - r * 0.62, z - r * 0.05), (r * 0.62, r * 0.35, r * 0.66), mat("iris" + str(iris), iris, 0.3), name="iris"))
    parts.append(sphere((x + r * 0.07, y - r * 0.84, z - r * 0.05), (r * 0.34, r * 0.2, r * 0.36), mat("pupil", (20, 15, 25), 0.2), name="pupil"))
    parts.append(sphere((x - r * 0.2, y - r * 0.98, z + r * 0.28), (r * 0.18, r * 0.08, r * 0.18), mat("glint", (255, 255, 255), 0.1, emis=2.0), name="glint"))
    parts.append(sphere((x + r * 0.3, y - r * 0.96, z - r * 0.32), (r * 0.08, r * 0.05, r * 0.08), mat("glint", (255, 255, 255), 0.1, emis=2.0), name="glint2"))
    if lashes:
        for k in (-1, 0, 1):
            c = cyl((x + k * r * 0.45, y - r * 0.3, z + r * 1.1), r * 0.05, r * 0.45, mat("ink", (40, 35, 55), 0.6),
                    rot=(0, math.radians(-k * 25), 0), name="lash")
            parts.append(c)
    return parts


def mouth(x, y, z, w, open_, tooth=False, lip=(40, 35, 55)):
    if open_:
        m1 = sphere((x, y, z - w * 0.2), (w * 0.62, w * 0.2, w * 0.38), mat("mouth", (95, 20, 40), 0.7), name="mouth")
        sphere((x, y - w * 0.12, z - w * 0.4), (w * 0.34, w * 0.12, w * 0.14), mat("tongue", (240, 100, 125), 0.5), name="tongue")
        if tooth:
            sphere((x, y - w * 0.2, z + w * 0.02), (w * 0.12, w * 0.06, w * 0.12), mat("tooth", (255, 255, 255), 0.3), name="tooth")
        return m1
    t = torus((x, y, z + w * 0.12), w * 0.45, w * 0.075, mat("ink", lip, 0.6), rot=(math.radians(90), 0, 0), name="smile",
              arc=(0, 0, -1))
    if tooth:
        sphere((x, y - w * 0.02, z - w * 0.36), (w * 0.1, w * 0.05, w * 0.12), mat("tooth", (255, 255, 255), 0.3), name="tooth")
    return t


def render(sc, path):
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


# ------------------------------------------------------------------ personajes
def bombolin(mouth_open, closed):
    sc = reset()
    G = mat("pipo", (126, 217, 166), 0.5, sss=0.05)
    Y = mat("belly", (255, 228, 120), 0.5)
    O = mat("orange", (255, 150, 60), 0.45)
    W = mat("shell", (255, 253, 245), 0.3)
    B = mat("dots", (110, 170, 255), 0.35)
    K = mat("cheek", (255, 150, 170), 0.6)
    sphere((0, 0, 0.62), (0.56, 0.5, 0.62), G, name="body")
    sphere((0, -0.3, 0.6), (0.38, 0.22, 0.46), Y, name="belly")
    for (x, z) in [(-0.1, 0.72), (0.14, 0.55), (-0.05, 0.42)]:
        sphere((x, -0.5, z), (0.045, 0.02, 0.045), mat("spot", (100, 190, 130), 0.5), name="spot")
    sphere((0, -0.02, 1.42), (0.56, 0.52, 0.5), G, name="head")
    sphere((0, -0.33, 1.3), (0.34, 0.26, 0.24), G, name="snout")
    for x in (-0.24, 0.24):
        eye(x, -0.38, 1.5, 0.14, (140, 85, 40), closed, G)
    for x in (-0.36, 0.36):
        sphere((x, -0.4, 1.3), (0.09, 0.03, 0.06), K, name="cheek")
    mouth(0, -0.56, 1.2, 0.26, mouth_open)
    # gorrito de cascarón: media esfera con dientes en el borde y lunares
    hat = sphere((0, 0.0, 1.78), (0.5, 0.48, 0.34), W, name="hat")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.bisect(plane_co=(0, 0, 1.78), plane_no=(0, 0, 1), clear_inner=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    for i in range(14):
        a = i / 14 * 2 * math.pi
        cone((0.48 * math.sin(a), 0.46 * -math.cos(a), 1.74), 0.07, 0.0, 0.14, W, rot=(math.pi, 0, 0), name="tooth")
    for (x, y, z) in [(-0.2, -0.38, 1.9), (0.18, -0.4, 1.95), (0.0, -0.3, 2.05), (0.32, -0.2, 1.85), (-0.34, -0.2, 1.86)]:
        sphere((x, y, z), (0.06, 0.03, 0.05), B, name="dot")
    for k, (z, y) in enumerate([(1.1, 0.48), (0.8, 0.52), (0.5, 0.5)]):
        cone((0, y, z), 0.12, 0.0, 0.22, O, rot=(math.radians(-70), 0, 0), name="spike")
    cone((0.25, 0.55, 0.25), 0.18, 0.02, 0.6, G, rot=(math.radians(-80), math.radians(25), 0), name="tail")
    for s in (-1, 1):
        sphere((s * 0.55, -0.12, 0.78), (0.14, 0.12, 0.2), G, name="arm")
        sphere((s * 0.25, -0.12, 0.08), (0.2, 0.28, 0.1), O, name="shoe")
        sphere((s * 0.25, -0.32, 0.1), (0.12, 0.08, 0.04), mat("lace", (255, 255, 255), 0.4), name="lace")
    camera_and_lights(sc, target=(0, 0, 1.05), dist=6.2, height=1.5, ortho=2.6)
    return sc


def toto(mouth_open, closed):
    sc = reset()
    Or = mat("toto", (255, 154, 60), 0.85)
    body = sphere((0, 0, 0.8), (0.78, 0.72, 0.78), Or, seg=96, name="fur")
    tex = bpy.data.textures.new("furtex", "CLOUDS")
    tex.noise_scale = 0.08
    d = body.modifiers.new("disp", "DISPLACE")
    d.texture = tex
    d.strength = 0.06
    sub = body.modifiers.new("sub", "SUBSURF")
    sub.levels, sub.render_levels = 1, 2
    P = mat("horn", (165, 95, 225), 0.4)
    for s in (-1, 1):
        cone((s * 0.32, -0.05, 1.55), 0.1, 0.0, 0.3, P, rot=(0, math.radians(s * 15), 0), name="horn")
        sphere((s * 0.38, -0.2, 0.06), (0.26, 0.34, 0.12), mat("foot", (235, 120, 30), 0.7), name="foot")
    for x in (-0.24, 0.24):
        eye(x, -0.62, 1.05, 0.16, (95, 60, 170), closed, Or)
    mouth(0, -0.74, 0.7, 0.34, mouth_open, tooth=True)
    sock = cyl((0.7, -0.25, 0.55), 0.09, 0.32, mat("sock", (90, 160, 255), 0.6), rot=(0, math.radians(20), 0), name="sock")
    for k in range(2):
        cyl((0.7 + 0.03 * (k - 0.5), -0.25, 0.48 + 0.12 * k), 0.093, 0.05, mat("sockw", (255, 255, 255), 0.6),
            rot=(0, math.radians(20), 0), name="stripe")
    camera_and_lights(sc, target=(0, 0, 0.85), dist=6.2, height=1.4, ortho=2.5)
    return sc


LULA_COL = {"calm": (150, 210, 245), "sad": (175, 180, 195), "angry": (255, 140, 130), "shy": (255, 175, 210),
            "happy": (150, 210, 245)}


def lula(mouth_open, closed, mood):
    sc = reset()
    C = mat("cloud" + mood, LULA_COL[mood], 0.7, sss=0.1)
    mb = bpy.data.metaballs.new("cloud")
    mb.resolution = 0.04
    mb.render_resolution = 0.025
    ob = bpy.data.objects.new("cloud", mb)
    sc.collection.objects.link(ob)
    for (x, z, r) in [(-0.55, 0.0, 0.42), (0, 0.18, 0.55), (0.55, 0.0, 0.42), (-0.28, -0.12, 0.42), (0.28, -0.12, 0.42),
                      (0, -0.15, 0.45)]:
        e = mb.elements.new()
        e.co = (x, 0, z + 1.0)
        e.radius = r
    ob.data.materials.append(C)
    for x in (-0.22, 0.22):
        eye(x, -0.46, 1.12, 0.12, (60, 120, 210), closed, C, lashes=not closed)
    for x in (-0.42, 0.42):
        sphere((x, -0.4, 0.98), (0.09, 0.03, 0.06), mat("cheek", (255, 150, 170), 0.6), name="cheek")
    mouth(0, -0.56, 0.92, 0.2, mouth_open)
    if mood == "happy":
        for i, c in enumerate([(255, 90, 90), (255, 170, 60), (255, 230, 80), (110, 210, 110), (90, 160, 255), (170, 110, 230)]):
            torus((0, 0.05, 0.55), 0.62 - i * 0.055, 0.03, mat(f"rb{i}", c, 0.4, emis=0.3), rot=(math.radians(90), 0, 0),
                  name="rainbow", arc=(0, 0, 1))
    if mood == "sad":
        for (x, z) in [(-0.3, 0.35), (0.1, 0.25), (0.35, 0.38)]:
            sphere((x, -0.1, z), (0.05, 0.05, 0.08), mat("drop", (90, 150, 255), 0.1, alpha=0.85), name="drop")
    if mood == "angry":
        for s in (-1, 1):
            cone((s * 0.7, -0.1, 1.55), 0.06, 0.0, 0.25, mat("bolt", (255, 220, 60), 0.3, emis=1.5), rot=(0, s * 0.4, 0), name="bolt")
    camera_and_lights(sc, target=(0, 0, 0.95), dist=6.2, height=1.3, ortho=2.6)
    return sc


def zumbi(mouth_open, closed, wing):
    sc = reset()
    Yb = bpy.data.materials.new("beestripes")
    Yb.use_nodes = True
    nt = Yb.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.45
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mth = nt.nodes.new("ShaderNodeMath")
    mth.operation = "SINE"
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 16.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = (1.0, 0.82, 0.2, 1)
    ramp.color_ramp.elements[1].position = 0.55
    ramp.color_ramp.elements[1].color = (0.08, 0.07, 0.09, 1)
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mul.inputs[0])
    nt.links.new(mul.outputs[0], mth.inputs[0])
    nt.links.new(mth.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    body = sphere((0, 0, 0.8), (0.6, 0.55, 0.6), Yb, name="bee")
    # la cara va sobre una «máscara» amarilla lisa para que las rayas no tapen los ojos
    sphere((0, -0.2, 0.95), (0.46, 0.38, 0.38), mat("beeface", (255, 210, 50), 0.45), name="face")
    for x in (-0.18, 0.18):
        eye(x, -0.55, 1.0, 0.12, (60, 40, 20), closed, mat("beeface", (255, 210, 50), 0.45))
    mouth(0, -0.6, 0.83, 0.18, mouth_open)
    Wm = mat("wing", (220, 240, 255), 0.1, alpha=0.55)
    ang = math.radians(35 if wing else 10)
    for s in (-1, 1):
        w = sphere((s * 0.55, 0.25, 1.35), (0.42, 0.05, 0.28), Wm, name="wing")
        w.rotation_euler = (0, s * ang, s * math.radians(-20))
        cyl((s * 0.16, -0.25, 1.45), 0.02, 0.4, mat("ink", (40, 35, 55), 0.6), rot=(0, s * math.radians(20), 0), name="ant")
        hx = s * 0.24
        for d in (-1, 1):
            sphere((hx + d * 0.04, -0.25, 1.66), (0.05, 0.03, 0.05), mat("heart", (255, 90, 120), 0.4), name="heart")
        cone((hx, -0.25, 1.6), 0.07, 0.0, 0.08, mat("heart", (255, 90, 120), 0.4), rot=(math.pi, 0, 0), name="heartc")
    for x in (-0.22, 0.0, 0.22):
        cyl((x, -0.1, 0.24), 0.02, 0.16, mat("ink", (40, 35, 55), 0.6), name="leg")
        sphere((x, -0.15, 0.13), (0.07, 0.1, 0.05), mat("redshoe", (230, 50, 60), 0.4), name="shoe")
    camera_and_lights(sc, target=(0, 0, 0.85), dist=6.2, height=1.3, ortho=2.3)
    return sc


def abu(mouth_open, closed):
    sc = reset()
    SK = mat("abuskin", (150, 205, 120), 0.6)
    # caparazón tipo colcha: voronoi con colores
    sh = bpy.data.materials.new("shell")
    sh.use_nodes = True
    nt = sh.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.55
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 5.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.25, 0.55, 0.32, 1)
    ramp.color_ramp.elements[1].color = (0.62, 0.82, 0.45, 1)
    nt.links.new(vor.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    shell = sphere((0.25, 0.25, 0.7), (0.85, 0.78, 0.62), sh, name="shell")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.bisect(plane_co=(0, 0, 0.55), plane_no=(0, 0, 1), clear_inner=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    cyl((0.25, 0.25, 0.52), 0.86, 0.12, mat("rim", (232, 220, 160), 0.5), name="rim")
    for (x, y) in [(-0.3, -0.25), (0.75, -0.25), (-0.3, 0.7), (0.75, 0.7)]:
        cyl((x, y, 0.25), 0.15, 0.45, SK, name="leg")
    cyl((-0.45, -0.25, 0.95), 0.2, 0.6, SK, rot=(math.radians(10), math.radians(-25), 0), name="neck")
    sphere((-0.6, -0.35, 1.35), (0.42, 0.4, 0.38), SK, name="head")
    for x in (-0.76, -0.44):
        eye(x, -0.68, 1.42, 0.1, (90, 60, 40), closed, SK)
        torus((x, -0.76, 1.42), 0.13, 0.018, mat("gold", (225, 175, 45), 0.25, metal=0.8), rot=(math.radians(90), 0, 0), name="glass")
    cyl((-0.6, -0.76, 1.44), 0.012, 0.08, mat("gold", (225, 175, 45), 0.25, metal=0.8), rot=(0, math.radians(90), 0), name="bridge")
    for x in (-0.86, -0.34):
        sphere((x, -0.66, 1.25), (0.07, 0.03, 0.05), mat("cheek", (255, 150, 170), 0.6), name="cheek")
    mouth(-0.6, -0.74, 1.2, 0.2, mouth_open)
    torus((-0.48, -0.25, 1.02), 0.27, 0.08, mat("scarf", (190, 160, 235), 0.8), rot=(math.radians(10), math.radians(-25), 0), name="scarf")
    cyl((1.25, -0.3, 0.75), 0.03, 1.5, mat("wood", (130, 85, 45), 0.7), name="cane")
    leaf = sphere((1.25, -0.3, 1.55), (0.16, 0.04, 0.24), mat("leaf", (90, 190, 90), 0.5), name="leaf")
    camera_and_lights(sc, target=(0.2, 0, 0.85), dist=6.2, height=1.4, ortho=3.1)
    return sc


def main():
    jobs = []
    for m in (0, 1):
        for c in (0, 1):
            jobs.append(("PIPO", f"PIPO_{m}_{c}", lambda m=m, c=c: bombolin(m, c)))
            jobs.append(("TOTO", f"TOTO_{m}_{c}", lambda m=m, c=c: toto(m, c)))
            jobs.append(("ABU", f"ABU_{m}_{c}", lambda m=m, c=c: abu(m, c)))
            for wg in (0, 1):
                jobs.append(("ZUMBI", f"ZUMBI_{wg}_{m}_{c}", lambda m=m, c=c, wg=wg: zumbi(m, c, wg)))
            for mood in LULA_COL:
                jobs.append(("LULA", f"LULA_{mood}_{m}_{c}", lambda m=m, c=c, mood=mood: lula(m, c, mood)))
    for who, name, fn in jobs:
        if ONLY and who not in ONLY and name not in ONLY:
            continue
        p = os.path.join(OUT, name + ".png")
        if os.path.exists(p):
            continue
        _mats.clear()
        sc = fn()
        render(sc, p)
        print("OK", name, flush=True)


if __name__ == "__main__":
    main()
