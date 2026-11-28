"""Pista de carrera en capas que se repiten sin costura (para que el escenario se mueva mientras los personajes corren).

Uso: python3 carrera.py CARPETA_SALIDA   (CARRERA_SOLO="far" para rehacer una sola capa)
Salida: track_near_h.png (pasto, pista, cerca, flores y árboles cercanos) y track_far_h.png (lomas, árboles lejanos
y nubes), de 3840x1080 cada una (dos pantallas de ancho). El compositor (episode.py, modo «race») las desliza a
distintas velocidades: la de adelante rápido y la del fondo lento (paralaje), como en los dibujos animados.
Cada objeto se pone también una vuelta antes y una después (x ± L): al repetir la imagen no se ve el corte.
"""
import math
import os
import random
import sys

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
sys.argv = [sys.argv[0], OUT, "__ninguno__"]  # escenarios.py no renderiza nada al importarlo
import bpy  # noqa: E402
import escenarios as S  # noqa: E402
from escenarios import mat, sph, cyl, cube, cone, rod, tree, big_flower, flat  # noqa: E402

L = 32.0  # ancho de la imagen en unidades (dos pantallas)
PXW, PXH = 3840, 1080


def rep(fn, x, *a, **k):
    for dx in (-L, 0, L):
        fn(x + dx, *a, **k)


def ortho(sc, tilt_deg, vc):
    """Cámara ortográfica centrada en x = L/2, mirando hacia +y con inclinación tilt; vc = altura del centro."""
    c = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(c)
    c.data.type = "ORTHO"
    c.data.ortho_scale = L
    t = math.radians(tilt_deg)
    # el centro de la imagen cae en el punto (L/2, y0, z0) con  y0*sin(t) + z0*cos(t) = vc
    c.location = (L / 2, -40 * math.cos(t), 40 * math.sin(t) + vc / math.cos(t))
    c.rotation_euler = (math.radians(90 - tilt_deg), 0, 0)
    c.data.clip_end = 300
    sc.camera = c


def flower_bunch(x, y, n, seed):
    cols = [(255, 120, 160), (255, 220, 70), (255, 255, 255), (185, 140, 255), (255, 150, 60), (120, 190, 255)]
    rr = random.Random(seed)
    for _ in range(n):
        big_flower(x + rr.uniform(-0.8, 0.8), y + rr.uniform(-0.4, 0.4), rr.uniform(0.35, 0.6),
                   cols[rr.randint(0, 5)], lambda c: c, rr)


def bush(x, y, r, seed):
    rnd = random.Random(seed)
    sph((x, y, 0.3), (r, 0.85 * r, 0.65 * r), mat("bush", (95, 195, 70), 0.85))
    sph((x + 0.5 * r, y - 0.2, 0.25), (0.6 * r, 0.55 * r, 0.5 * r), mat("bush2", (115, 205, 75), 0.85))
    for k in range(6):
        a = rnd.uniform(0.3, math.pi - 0.3)
        sph((x + math.cos(a) * r * 0.85, y - 0.6 * r, 0.3 + math.sin(a) * 0.5 * r), (0.09,) * 3,
            mat("berry" + str(k % 2), [(255, 255, 255), (255, 130, 170)][k % 2], 0.4), seg=12)


def mushroom(x, y, s):
    cyl((x, y, 0.25 * s), 0.12 * s, 0.5 * s, mat("mstem", (255, 245, 225), 0.6))
    sph((x, y, 0.5 * s), (0.42 * s, 0.42 * s, 0.3 * s), mat("mcap", (240, 70, 70), 0.45))
    for k in range(5):
        a = k * 2 * math.pi / 5 + 0.4
        sph((x + 0.27 * s * math.cos(a), y + 0.27 * s * math.sin(a) - 0.05, 0.66 * s), (0.07 * s, 0.07 * s, 0.04 * s),
            mat("mdot", (255, 255, 255), 0.5), seg=10)


def fence_post(x, y):
    cube((x, y, 0.55), (0.14, 0.08, 0.55), mat("fence", (255, 250, 240), 0.6), 0.06)
    cone((x, y, 1.18), 0.2, 0.0, 0.2, mat("fence", (255, 250, 240), 0.6), rot=(0, 0, math.pi / 4)).scale = (0.7, 0.4, 1)


def pennant_pole(x, y):
    """Mástil con guirnalda de banderines de colores hasta el próximo (fiesta de carrera)."""
    cyl((x, y, 1.6), 0.07, 3.2, mat("pole", (250, 250, 255), 0.4))
    sph((x, y, 3.25), (0.14,) * 3, mat("polecap", (255, 205, 60), 0.3))
    cols = [(255, 90, 120), (255, 210, 70), (110, 190, 255), (130, 215, 120), (190, 140, 255)]
    x1, n = x + 8.0, 10
    for k in range(n):
        t = (k + 0.5) / n
        xx, zz = x + (x1 - x) * t, 3.05 - 0.6 * 4 * t * (1 - t)
        flat([(-0.22, 0), (0.22, 0), (0, -0.5)], mat(f"pen{k % 5}", cols[k % 5], 0.7), (xx, y - 0.05, zz), 0.03)
    for k in range(20):
        t0, t1 = k / 20, (k + 1) / 20
        rod((x + 8 * t0, y, 3.05 - 2.4 * t0 * (1 - t0)), (x + 8 * t1, y, 3.05 - 2.4 * t1 * (1 - t1)), 0.02,
            mat("string", (250, 250, 250), 0.6), v=6)


def near():
    sc = S.reset(PXW, PXH)
    S.sun(sc, 3.5, (1, 0.95, 0.88), (0.9, 0.2, 0.6))
    ortho(sc, 20, 3.9)
    # pasto (plano, color parejo para que la unión no se note) y pista de tierra con líneas blancas
    bpy.ops.mesh.primitive_plane_add(size=1, location=(L / 2, 2.0, 0))
    g = bpy.context.object
    g.scale = (L * 4, 26, 1)
    g.data.materials.append(mat("grass", (165, 225, 85), 0.9))
    bpy.ops.mesh.primitive_plane_add(size=1, location=(L / 2, 0.0, 0.01))
    t = bpy.context.object
    t.scale = (L * 4, 3.4, 1)
    t.data.materials.append(mat("track", (236, 190, 125), 0.95))
    for y in (-1.7, 1.7):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(L / 2, y, 0.02))
        o = bpy.context.object
        o.scale = (L * 4, 0.12, 1)
        o.data.materials.append(mat("line", (255, 255, 255), 0.6))
    # piedritas sobre la pista (dan sensación de velocidad al pasar)
    rnd = random.Random(3)
    for k in range(18):
        x = rnd.uniform(0, L)
        y = rnd.uniform(-1.4, 1.4)
        rep(lambda xx: sph((xx, y, 0.02), (0.09, 0.07, 0.03), mat("pebble", (205, 160, 105), 0.9), seg=10), x)
    # cerquita blanca detrás de la pista
    for k in range(int(L / 1.6)):
        rep(fence_post, k * 1.6, 2.8)
    for z in (0.4, 0.85):
        rod((-L, 2.75, z), (2 * L, 2.75, z), 0.07, mat("fencebar", (250, 240, 225), 0.6), v=12)
    # mástiles con banderines cada 16 unidades
    for x in (2.0, 18.0):
        rep(pennant_pole, x, 3.4)
    # flores, arbustos y hongos detrás de la cerca
    for k, (x, n) in enumerate([(1.0, 7), (5.5, 6), (9.0, 8), (13.5, 6), (17.0, 7), (21.0, 6), (25.5, 8), (29.0, 6)]):
        rep(flower_bunch, x, 4.2 + 0.4 * (k % 2), n, k + 1)
    for k, (x, r) in enumerate([(3.5, 0.9), (11.5, 1.0), (19.5, 0.85), (27.0, 1.05)]):
        rep(bush, x, 5.6, r, k + 7)
    for (x, s) in [(7.5, 0.8), (15.0, 0.6), (23.5, 0.9), (30.5, 0.7)]:
        rep(mushroom, x, 4.6, s)
    # árboles redondos al fondo (tapan el borde del pasto)
    cols = [(70, 190, 75), (95, 200, 70), (60, 175, 90), (110, 205, 80), (80, 195, 85)]
    for k, x in enumerate([0.5, 4.5, 8.0, 12.0, 15.5, 19.5, 23.0, 27.0, 30.0]):
        s = 1.0 + 0.25 * ((k * 7) % 3)
        rep(lambda xx: tree(xx, 9.0 + (k % 3) * 0.8, s, col=cols[k % 5], fruit=(255, 80, 80) if k % 3 == 0 else None), x)
    for k, x in enumerate([2.5, 6.0, 10.0, 14.0, 17.5, 21.5, 25.0, 28.5]):
        rep(lambda xx: bush(xx, 8.2, 1.2, 40 + k), x)
    sc.render.filepath = os.path.join(OUT, "track_near_h.png")
    bpy.ops.render.render(write_still=True)
    print("OK near", flush=True)


def far():
    sc = S.reset(PXW, PXH)
    S.sun(sc, 3.5, (1, 0.95, 0.88), (0.9, 0.2, 0.6))
    ortho(sc, 0, 2.2)  # sin inclinación (más baja: las lomas asoman por detrás de los árboles): las lomas se ven de costado contra el cielo
    # lomas en capas (más claras y azuladas las de atrás)
    for (y, zc, cols, seed) in [(60, 1.5, [(150, 205, 170), (140, 195, 175)], 1),
                                (40, 0.6, [(125, 210, 115), (100, 190, 95), (115, 200, 105)], 2)]:
        rr = random.Random(seed)
        x = 0.0
        k = 0
        while x < L:
            sx = rr.uniform(5, 8)
            sz = rr.uniform(2.2, 3.4) + zc
            rep(lambda xx: sph((xx, y, -0.5), (sx, 5, sz), mat("hill" + str(cols[k % len(cols)]), cols[k % len(cols)], 0.9),
                               seg=48), x)
            x += sx * 1.3
            k += 1
    # relleno verde bajo las lomas (para que nunca se vea cielo abajo)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(L / 2, 38, -1.2))
    o = bpy.context.object
    o.scale = (L * 4, 1, 1)
    o.rotation_euler = (math.radians(90), 0, 0)
    o.scale = (L * 4, 6.0, 1)
    o.data.materials.append(mat("hillfill", (110, 195, 100), 0.9))
    # arbolitos lejanos sobre las lomas
    for k, x in enumerate([3.0, 9.5, 14.0, 21.0, 26.5]):
        rep(lambda xx: tree(xx, 36, 0.7, col=[(70, 175, 95), (90, 190, 85)][k % 2]), x)
    # nubes esponjosas (metaballs) que también se repiten
    mb = bpy.data.metaballs.new("clouds")
    mb.resolution = 0.3
    mb.render_resolution = 0.2
    ob = bpy.data.objects.new("clouds", mb)
    sc.collection.objects.link(ob)
    rnd = random.Random(5)
    for cx, cz in [(4, 6.3), (13, 6.9), (22, 6.1), (29, 6.7)]:
        pts = [(rnd.uniform(-1.6, 1.6), rnd.uniform(-0.3, 0.5), rnd.uniform(0.7, 1.2)) for _ in range(5)]
        for dx in (-L, 0, L):
            for (px, pz, r) in pts:
                e = mb.elements.new()
                e.co = (cx + px + dx, 70, cz + pz)
                e.radius = r
    ob.data.materials.append(mat("cloud", (255, 255, 255), 0.9, emis=0.4))
    ob.visible_shadow = False
    sc.render.filepath = os.path.join(OUT, "track_far_h.png")
    bpy.ops.render.render(write_still=True)
    print("OK far", flush=True)


for _k in os.environ.get("CARRERA_SOLO", "near far").split():
    {"near": near, "far": far}[_k]()
