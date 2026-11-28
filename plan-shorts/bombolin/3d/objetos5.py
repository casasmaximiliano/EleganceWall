"""Más objetos 3D para los bloques de la biblioteca (mismo estilo que objetos4.py).

Uso: python3 objetos5.py CARPETA_SALIDA [objeto ...]
No pisa archivos que ya existan en la carpeta.
"""
import math
import os

import bpy  # noqa: F401  (carga mathutils)

from objetos import cam, setup
from objetos4 import meta, group, shine, fit, INK, R
from modelos import mat, sphere, torus
import modelos as M


_N = 0


def _seahorse(s=1.0, loc=(0, 0, 0), body=(255, 170, 50), belly=(255, 230, 150), fin=(255, 120, 160), baby=False):
    """Caballito de mar de juguete: cabeza con hocico, panza redonda, cola enrulada, aleta y crestita."""
    B = mat("sh_b%s" % (body,), body, 0.35)
    L = mat("sh_l%s" % (belly,), belly, 0.4)
    F = mat("sh_f%s" % (fin,), fin, 0.3, alpha=0.9)
    global _N
    _N += 1
    tag = f"sh{_N}x"  # los metaballs con el mismo nombre base se funden entre sí: cada caballito con el suyo
    el = []
    # cuerpo: cabeza arriba, cuello curvo hacia atrás (+x), panza redonda adelante y cola fina que se enrula
    spine = [(0.0, 1.58, 0.22), (0.1, 1.42, 0.17), (0.16, 1.26, 0.15), (0.1, 1.08, 0.2), (0.0, 0.88, 0.25),
             (0.02, 0.66, 0.23), (0.1, 0.46, 0.16), (0.16, 0.3, 0.12), (0.18, 0.16, 0.1)]
    for x, z, r in spine:
        el.append(((x, 0, z), (r, r * 0.8, r)))
    # cola enrulada hacia adelante (espiral que se achica)
    cx, cz = 0.04, 0.02
    for k in range(11):
        a = R(10 - k * 36)
        rr = 0.15 * (1 - k / 16)
        el.append(((cx + rr * math.cos(a), 0, cz + rr * math.sin(a)), (0.075 - k * 0.004,) * 3))
    # hocico: tubito largo hacia la izquierda con la puntita ensanchada
    el.append(((-0.24, -0.02, 1.52), (0.2, 0.07, 0.065), (0, R(12), 0)))
    el.append(((-0.44, -0.02, 1.48), (0.055, 0.075, 0.075)))
    parts = [meta(tag + "b", B, el)]
    # panza clara con anillitos
    parts.append(meta(tag + "l", L, [((-0.1, -0.06, z), (0.17, 0.17, 0.17)) for z in (0.95, 0.78, 0.6)]))
    for k, z in enumerate((1.02, 0.88, 0.74, 0.6)):
        parts.append(torus((-0.14 + 0.01 * k, -0.13, z), 0.12, 0.014,
                           mat("ring", tuple(min(255, int(c * 0.88)) for c in belly), 0.4),
                           rot=(R(90), R(20), 0), arc=(0.0, 0.0, 0.5)))
    # aleta del lomo (abanico) y crestita de la cabeza
    for k in range(5):
        parts.append(sphere((0.3 + 0.02 * k, 0.02, 0.62 + k * 0.09), (0.12, 0.025, 0.045), F))
    for k, (x, z) in enumerate([(0.02, 1.8), (0.13, 1.76), (0.21, 1.66)]):
        parts.append(sphere((x, 0, z), (0.06, 0.05, 0.1 - k * 0.015), F))
    # carita de frente (ojo grande y sonrisa); la cámara lo ve de 3/4
    for sx in (-1, 1):
        parts += M.eye(-0.04 + sx * 0.11, -0.17, 1.63, 0.095, (60, 40, 30), False, B)
    parts.append(torus((-0.12, -0.2, 1.48), 0.05, 0.013, mat("ink", INK, 0.6), rot=(R(90), 0, 0), arc=(0, 0, -1)))
    for sx in (-1, 1):
        parts.append(sphere((-0.04 + sx * 0.19, -0.18, 1.52), (0.045, 0.02, 0.03), mat("cheek", (255, 140, 160), 0.6)))
    if not baby:
        parts.append(shine((-0.06, -0.24, 0.86), 0.8, rot=(0, R(10), 0)))
    return group(parts, loc, (0, 0, R(-18)), s)


def seahorse():
    """El papá caballito de mar con su bolsita y dos bebés que salen nadando."""
    sc = setup()
    _seahorse(1.0, (0, 0, 0))
    _seahorse(0.4, (-0.75, -0.1, 1.05), body=(120, 200, 255), belly=(220, 245, 255), fin=(150, 120, 255), baby=True)
    _seahorse(0.34, (-0.6, -0.1, 0.35), body=(255, 140, 190), belly=(255, 225, 240), fin=(255, 190, 80), baby=True)
    for (x, z, r) in [(-0.45, 1.8, 0.045), (-0.35, 1.98, 0.03), (-0.95, 1.85, 0.035)]:  # burbujitas
        sphere((x, -0.1, z), (r, r, r), mat("bub", (200, 235, 255), 0.05, alpha=0.6))
    cam(sc, (0, 0, 0.9), 2.6, height=1.0)
    return sc


OBJS = dict(seahorse=seahorse)

if __name__ == "__main__":
    for name, fn in OBJS.items():
        if M.ONLY and name not in M.ONLY:
            continue
        p = os.path.join(M.OUT, name + ".png")
        if os.path.exists(p):
            continue
        sc = fn()
        fit(sc, 0.05)
        M.render(sc, p)
        print("OK", name, flush=True)
