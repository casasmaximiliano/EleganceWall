"""Puesta en escena: dónde y cómo aparece cada objeto de la historia (no flotando en el cielo, sino en la escena).

STAGE[(día, escena)] = lista de objetos. Cada objeto es un dict con "em" (emoji) y "mode":
- "on":     pegado al cuerpo de un personaje ("who"); "at" = (dx, dy) en fracciones de su ancho/alto
            desde el centro horizontal y la parte de arriba; "size" en fracción de su alto; "rot" en grados.
- "ground": apoyado en el piso con sombra; "x" en fracción del ancho; "size" en fracción del alto de la imagen.
- "front":  delante de un personaje (bañera, cama); "hide" = cuánto se hunde el personaje detrás.
- "orbit":  vuela alrededor de la cabeza de un personaje ("n" copias).
- "rise":   burbujas que suben por toda la escena ("n" copias).
- "puddle": charco de barro o agua en el piso ("x", "w", "col").
- "river":  un río que cruza el piso.
- "sparkle": brillitos alrededor de un personaje.
Todos aceptan "from" (número de frase de la escena desde la que aparece; por defecto 0).
Si una escena tiene puesta en escena, sus emojis «sueltos» no se dibujan.
"""

MUD = (120, 78, 40)

STAGE = {
    # Día 2: ¡Toto no quiere bañarse!
    (2, 0): [dict(em="🧽", mode="ground", x=0.24, size=0.14),
             dict(em="🫧", mode="rise", n=6),
             dict(em="🛏️", mode="front", who="TOTO", size=0.85, hide=0.42, frm=1)],
    (2, 1): [dict(em="🍝", mode="on", who="TOTO", at=(0.10, 0.02), size=0.42, rot=-12),
             dict(em="🧦", mode="on", who="TOTO", at=(0.36, 0.42), size=0.26, rot=25),
             dict(em="🟤", mode="on", who="TOTO", at=(-0.25, 0.55), size=0.10)],
    (2, 2): [dict(em="🍝", mode="on", who="TOTO", at=(0.10, 0.02), size=0.42, rot=-12),
             dict(em="🧦", mode="on", who="TOTO", at=(0.36, 0.42), size=0.26, rot=25),
             dict(em="🪰", mode="orbit", who="TOTO", n=3, size=0.10)],
    (2, 3): [dict(em="🍝", mode="on", who="TOTO", at=(0.10, 0.02), size=0.42, rot=-12),
             dict(em="🪰", mode="orbit", who="TOTO", n=2, size=0.09),
             dict(em="💦", mode="orbit", who="G:Pájaro", n=3, size=0.10, frm=2)],
    (2, 4): [dict(mode="puddle", x=0.38, w=0.20, col=MUD, back=True),
             dict(em="🐷", mode="ground", x=0.38, size=0.16, back=True),
             dict(em="🍝", mode="on", who="TOTO", at=(0.10, 0.02), size=0.42, rot=-12)],
    (2, 5): [dict(mode="river"),
             dict(em="🌴", mode="ground", x=0.92, size=0.42, back=True),
             dict(em="🍝", mode="on", who="TOTO", at=(0.10, 0.02), size=0.42, rot=-12)],
    (2, 6): [dict(mode="puddle", x=0.83, w=0.30, col=MUD),
             dict(em="🟤", mode="orbit", who="G:Elefante", n=4, size=0.06, frm=2),
             dict(em="💦", mode="orbit", who="G:Elefante", n=2, size=0.10, frm=2)],
    (2, 8): [dict(em="🫧", mode="rise", n=10),
             dict(em="🧼", mode="ground", x=0.5, size=0.12)],
    (2, 9): [dict(em="🛁", mode="front", who="TOTO", size=0.62, hide=0.30),
             dict(em="🫧", mode="rise", n=12)],
    (2, 10): [dict(em="🛁", mode="front", who="TOTO", size=0.62, hide=0.30),
              dict(em="🦆", mode="on", who="TOTO", at=(0.42, 0.55), size=0.22),
              dict(em="🫧", mode="on", who="TOTO", at=(-0.12, 0.50), size=0.20, frm=2),
              dict(em="🫧", mode="on", who="TOTO", at=(0.10, 0.52), size=0.22, frm=2),
              dict(em="🫧", mode="rise", n=10)],
    (2, 11): [dict(em="🧴", mode="ground", x=0.12, size=0.14),
              dict(em="🪮", mode="on", who="TOTO", at=(0.22, -0.02), size=0.22, rot=30),
              dict(mode="sparkle", who="TOTO", frm=1)],
    (2, 12): [dict(mode="sparkle", who="TOTO"),
              dict(em="🧦", mode="on", who="TOTO", at=(0.0, 0.70), size=0.24, rot=-10, frm=1)],
}
