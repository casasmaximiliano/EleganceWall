"""Objetos 3D de las historias (cama, bañera, fideos, media, patito, etc.), con la misma luz y estilo que los personajes.

Uso: python3 objetos.py CARPETA_SALIDA [objeto ...]
Cada objeto se renderiza una vez como PNG con transparencia; el compositor los ubica en la escena (staging.py).
"""
import math
import os
import random
import sys

import bpy

import modelos as M
from modelos import mat, sphere, cyl, torus, cone

OUT = M.OUT
ONLY = M.ONLY


def box(loc, size, m, bevel=0.08, rot=(0, 0, 0), name="b"):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    bv = o.modifiers.new("bev", "BEVEL")
    bv.width, bv.segments = bevel, 6
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


def cam(sc, target, ortho, height=1.4):
    M.camera_and_lights(sc, target=target, dist=6.2, height=height, ortho=ortho)


def setup():
    sc = M.reset()
    sc.render.resolution_x = sc.render.resolution_y = 700
    M._mats.clear()
    return sc


def bed():
    sc = setup()
    wood, wood2 = mat("wood", (200, 125, 70), 0.5), mat("wood2", (170, 100, 55), 0.5)
    box((0, 0, 0.35), (2.4, 1.2, 0.3), wood, 0.06)                     # base
    for x in (-1.15, 1.15):
        box((x, -0.5, 0.25), (0.14, 0.14, 0.5), wood2, 0.04)          # patas
        box((x, 0.5, 0.25), (0.14, 0.14, 0.5), wood2, 0.04)
    box((-1.22, 0, 0.95), (0.14, 1.25, 1.3), wood, 0.07)              # cabecera
    sphere((-1.22, 0, 1.62), (0.12, 0.62, 0.12), wood2)
    box((1.22, 0, 0.72), (0.14, 1.25, 0.85), wood, 0.07)              # pie de cama
    box((0, 0, 0.6), (2.2, 1.1, 0.26), mat("mattress", (255, 252, 240), 0.6), 0.1)
    box((-0.8, 0, 0.83), (0.5, 0.85, 0.22), mat("pillow", (255, 255, 255), 0.7), 0.1)
    blanket = box((0.25, -0.02, 0.8), (1.75, 1.18, 0.18), mat("blanket", (70, 140, 255), 0.75), 0.08)
    for k in range(5):
        sphere((-0.45 + k * 0.33, -0.6, 0.86), (0.07, 0.03, 0.07), mat("star", (255, 220, 60), 0.4))
    cam(sc, (0, 0, 0.7), 2.9, height=1.6)
    return sc


def bathtub():
    sc = setup()
    W = mat("tub", (255, 255, 255), 0.25)
    tub = box((0, 0, 0.55), (2.3, 1.1, 0.8), W, 0.35)
    rim = torus((0, 0, 0.95), 1.0, 0.09, W)
    rim.scale = (1.13, 0.5, 1)
    for x in (-0.9, 0.9):
        for y in (-0.38, 0.38):
            sphere((x, y, 0.12), (0.12, 0.12, 0.12), mat("gold", (240, 190, 60), 0.3, metal=0.7))
    foam = mat("foam", (250, 252, 255), 0.8)
    random.seed(3)
    for k in range(38):
        x = random.uniform(-1.0, 1.0)
        y = random.uniform(-0.35, 0.4)
        r = random.uniform(0.12, 0.24)
        sphere((x, y, 1.0 + random.uniform(-0.02, 0.12)), (r, r, r * 0.85), foam, seg=24)
    cam(sc, (0, 0, 0.6), 2.7, height=1.5)
    return sc


def spaghetti():
    """Montoncito de fideos con salsa (para pegarlo en la cabeza de Toto)."""
    sc = setup()
    noodle = mat("noodle", (255, 214, 120), 0.45)
    random.seed(5)
    for k in range(26):
        R = random.uniform(0.22, 0.42)
        t = torus((random.uniform(-0.25, 0.25), random.uniform(-0.2, 0.2), 0.12 + random.uniform(0, 0.25)), R, 0.035,
                  noodle, rot=(random.uniform(-0.6, 0.6), random.uniform(-0.6, 0.6), random.uniform(0, 3.14)))
    sauce = sphere((0, -0.05, 0.42), (0.36, 0.32, 0.16), mat("sauce", (220, 40, 30), 0.3))
    for (x, y) in [(-0.12, -0.12), (0.15, 0.02), (0.0, 0.18)]:
        sphere((x, y, 0.55), (0.11, 0.11, 0.1), mat("meatball", (130, 70, 40), 0.7))
    cam(sc, (0, 0, 0.3), 1.3, height=2.2)
    return sc


def sock():
    sc = setup()
    Wt, Rd = mat("sockw", (255, 255, 255), 0.8), mat("sockr", (240, 60, 70), 0.8)
    cyl((0, 0, 0.75), 0.22, 0.9, Wt)
    for z in (1.0, 1.12):
        cyl((0, 0, z), 0.225, 0.06, Rd)
    sphere((0, 0, 0.3), (0.23, 0.23, 0.23), Wt)
    sphere((0, -0.3, 0.22), (0.22, 0.42, 0.16), Wt)
    sphere((0, -0.6, 0.22), (0.2, 0.12, 0.15), Rd)
    cam(sc, (0, -0.15, 0.6), 1.7, height=1.2)
    return sc


def duck():
    sc = setup()
    Y = mat("duck", (255, 215, 30), 0.3)
    sphere((0, 0, 0.35), (0.48, 0.38, 0.3), Y)
    sphere((-0.22, -0.05, 0.78), (0.26, 0.26, 0.26), Y)
    sphere((-0.48, -0.05, 0.74), (0.14, 0.1, 0.05), mat("beak", (255, 130, 20), 0.4))
    for y in (-0.12, 0.12):
        sphere((-0.34, y - 0.12, 0.86), (0.05, 0.03, 0.06), mat("eye", (25, 20, 30), 0.2))
    cone((0.45, 0, 0.5), 0.12, 0.0, 0.25, Y, rot=(0, math.radians(-60), 0))
    cam(sc, (-0.05, 0, 0.5), 1.4, height=1.4)
    return sc


def sponge():
    sc = setup()
    box((0, 0, 0.3), (1.2, 0.7, 0.5), mat("sponge", (255, 220, 60), 0.9), 0.12)
    random.seed(2)
    for k in range(14):
        sphere((random.uniform(-0.5, 0.5), -0.36, random.uniform(0.15, 0.48)), (0.05, 0.02, 0.05), mat("hole", (220, 170, 30), 0.9))
    box((0, 0, 0.62), (1.2, 0.7, 0.14), mat("scrub", (60, 180, 90), 0.9), 0.05)
    cam(sc, (0, 0, 0.35), 1.5, height=1.4)
    return sc


def soap():
    sc = setup()
    box((0, 0, 0.25), (1.0, 0.6, 0.4), mat("soap", (255, 140, 200), 0.25), 0.15)
    for k, (x, z) in enumerate([(-0.2, 0.55), (0.15, 0.62), (0.35, 0.5)]):
        sphere((x, 0, z), (0.12, 0.12, 0.12), mat("bub", (220, 240, 255), 0.05, alpha=0.6), seg=24)
    cam(sc, (0, 0, 0.35), 1.4, height=1.4)
    return sc


def comb():
    sc = setup()
    P = mat("comb", (170, 90, 240), 0.3)
    box((0, 0, 0.7), (1.2, 0.12, 0.22), P, 0.05)
    for k in range(11):
        box((-0.5 + k * 0.1, 0, 0.45), (0.05, 0.08, 0.36), P, 0.02)
    cam(sc, (0, 0, 0.6), 1.4, height=1.2)
    return sc


def fly():
    sc = setup()
    sphere((0, 0, 0.5), (0.3, 0.38, 0.26), mat("flyb", (60, 70, 80), 0.4))
    for x in (-0.12, 0.12):
        sphere((x, -0.3, 0.6), (0.11, 0.08, 0.11), mat("flye", (255, 255, 255), 0.2))
        sphere((x, -0.37, 0.6), (0.05, 0.03, 0.05), mat("flyp", (20, 20, 25), 0.2))
    Wg = mat("flyw", (200, 230, 255), 0.1, alpha=0.5)
    for s in (-1, 1):
        w = sphere((s * 0.35, 0.1, 0.8), (0.3, 0.05, 0.16), Wg)
        w.rotation_euler = (0, s * 0.5, s * 0.3)
    cam(sc, (0, 0, 0.55), 1.4, height=1.5)
    return sc


def bubble():
    sc = setup()
    sphere((0, 0, 0.5), (0.45, 0.45, 0.45), mat("bubble", (200, 230, 255), 0.02, alpha=0.35))
    sphere((-0.18, -0.4, 0.68), (0.09, 0.03, 0.06), mat("shine", (255, 255, 255), 0.0, emis=2))
    torus((0, 0, 0.5), 0.45, 0.012, mat("film", (255, 170, 230), 0.1, alpha=0.6), rot=(math.radians(90), 0, 0))
    cam(sc, (0, 0, 0.5), 1.2, height=1.2)
    return sc


def lotion():
    sc = setup()
    cyl((0, 0, 0.5), 0.3, 0.9, mat("bottle", (80, 190, 255), 0.25))
    cyl((0, 0, 1.02), 0.12, 0.16, mat("cap", (255, 255, 255), 0.3))
    box((0, -0.29, 0.5), (0.36, 0.02, 0.36), mat("label", (255, 240, 120), 0.5), 0.02)
    cam(sc, (0, 0, 0.55), 1.5, height=1.3)
    return sc


def mudball():
    sc = setup()
    m = sphere((0, 0, 0.4), (0.4, 0.36, 0.34), mat("mud", (120, 75, 40), 0.25))
    tex = bpy.data.textures.new("mudtex", "CLOUDS")
    tex.noise_scale = 0.3
    d = m.modifiers.new("disp", "DISPLACE")
    d.texture, d.strength = tex, 0.12
    cam(sc, (0, 0, 0.4), 1.2, height=1.4)
    return sc


OBJS = dict(bed=bed, bathtub=bathtub, spaghetti=spaghetti, sock=sock, duck=duck, sponge=sponge, soap=soap,
            comb=comb, fly=fly, bubble=bubble, lotion=lotion, mudball=mudball)

if __name__ == "__main__":
    for name, fn in OBJS.items():
        if ONLY and name not in ONLY:
            continue
        p = os.path.join(OUT, name + ".png")
        if os.path.exists(p):
            continue
        sc = fn()
        M.render(sc, p)
        print("OK", name, flush=True)
