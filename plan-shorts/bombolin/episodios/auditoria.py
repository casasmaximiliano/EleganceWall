"""Auditoría antes de renderizar: lista todo lo que saldría en pantalla como emoji (y no como modelo 3D).

Uso: BOMBOLIN_ESTILO=2 BOMBOLIN_OBJ3D=... BOMBOLIN_GUESTS3D=... BOMBOLIN_BG3D=... python3 auditoria.py DIA [DIA...]
Regla del canal: si la lista no está vacía, no se renderiza hasta modelar lo que falta.
"""
import os
import sys
from collections import Counter

import episode as E
import programa as P
from props3d import EMOJI3D

R = E.R


def ok3d(ch):
    m = EMOJI3D.get(ch)
    if not m:
        return False
    if m[0] == "prop":
        return bool(E.OBJ3D_DIR and os.path.exists(os.path.join(E.OBJ3D_DIR, m[1] + ".png")))
    base = E.GUEST_ALIAS.get(m[1], (m[1], 1))[0]
    return bool(E.GUEST3D_DIR and os.path.exists(os.path.join(E.GUEST3D_DIR, base + "_0.png")))


def guest_ok(g):
    base = E.GUEST_ALIAS.get(g, (g, 1))[0]
    return bool(E.GUEST3D_DIR and os.path.exists(os.path.join(E.GUEST3D_DIR, base + "_0.png")))


def audit(n, vdir, cache):
    segs, _, _ = P.build_program(n, vdir, cache)
    shorts = [P.build_short(n, k, vdir, cache)[0] for k in range(P.n_shorts(n))]
    falta = Counter()
    where = {}
    for tag, ss in [("programa", segs)] + [(f"short{k + 1}", s) for k, s in enumerate(shorts)]:
        for sg in ss:
            items = []
            if sg["kind"] == "bumper":
                items.append(sg["icon"])
            if sg["kind"] == "album":
                items += [E.EPISODES[k]["sticker"] for k in E.EPISODES if k <= n]
            if sg["kind"] == "scene":
                st = sg.get("stage")
                if st:
                    for it in st:
                        if it.get("em") and not (it.get("sp") and E.OBJ3D_DIR and
                                                  os.path.exists(os.path.join(E.OBJ3D_DIR, it["sp"] + ".png"))):
                            items.append(it["em"])
                else:
                    for lp in (sg.get("line_props") or [sg.get("props", [])]):
                        items += list(lp)
                for g in sg.get("guests", []):
                    if not guest_ok(g):
                        items.append("G:" + g)
            for ch in items:
                if ch.startswith("G:") or not ok3d(ch):
                    falta[ch] += 1
                    where.setdefault(ch, set()).add(tag)
    return falta, where


if __name__ == "__main__":
    S = os.environ.get("BOMBOLIN_SCRATCH", ".")
    for d in sys.argv[1:]:
        falta, where = audit(int(d), os.path.join(S, "voices"), os.path.join(S, "audit_cache"))
        print(f"== Día {d}: {len(falta)} cosas todavía sin modelo 3D")
        for ch, c in falta.most_common():
            print(f"  {ch}  x{c}  ({', '.join(sorted(where[ch]))})  -> {EMOJI3D.get(ch, 'SIN MAPEO')}")
