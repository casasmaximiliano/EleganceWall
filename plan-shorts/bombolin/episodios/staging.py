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
# Lo de Toto sucio: fideos con salsa sobre la cabeza y una media pegada al costado
SPAG = dict(sp="spaghetti", em="🍝", mode="on", who="TOTO", at=(0.06, 0.16), w=0.55, rot=-8, anchor="bottom")
SOCK = dict(sp="sock", em="🧦", mode="on", who="TOTO", at=(0.47, 0.50), w=0.26, rot=-35)
# Toto metido en la bañera llena de espuma
TUB = dict(sp="bathtub", em="🛁", mode="front", who="TOTO", w=1.7, size=0.62, hide=0.32)

STAGE = {
    # Día 2: ¡Toto no quiere bañarse!  ("sp" = objeto 3D de 3d/objetos.py; "em" = emoji de respaldo)
    (2, 0): [dict(sp="sponge", em="🧽", mode="ground", x=0.22, size=0.11),
             dict(sp="bubble", em="🫧", mode="rise", n=6),
             dict(sp="bed", em="🛏️", mode="front", who="TOTO", w=1.9, size=0.85, hide=0.50, frm=1)],
    (2, 1): [SPAG, SOCK],
    (2, 2): [SPAG, SOCK, dict(sp="fly", em="🪰", mode="orbit", who="TOTO", n=3, size=0.07)],
    (2, 3): [SPAG, dict(sp="fly", em="🪰", mode="orbit", who="TOTO", n=2, size=0.07),
             dict(em="💦", mode="orbit", who="G:Pájaro", n=3, size=0.09, frm=2)],
    (2, 4): [dict(mode="puddle", x=0.38, w=0.22, col=MUD, back=True),
             dict(em="🐷", mode="ground", x=0.38, size=0.17, back=True), SPAG],
    (2, 5): [dict(mode="river"), dict(em="🌴", mode="ground", x=0.92, size=0.42, back=True), SPAG],
    (2, 6): [dict(mode="puddle", x=0.83, w=0.30, col=MUD),
             dict(sp="mudball", em="🟤", mode="orbit", who="G:Elefante", n=4, size=0.05, frm=2),
             dict(em="💦", mode="orbit", who="G:Elefante", n=2, size=0.09, frm=2)],
    (2, 8): [dict(sp="bubble", em="🫧", mode="rise", n=10),
             dict(sp="soap", em="🧼", mode="ground", x=0.5, size=0.10)],
    (2, 9): [TUB, dict(sp="bubble", em="🫧", mode="rise", n=10)],
    (2, 10): [TUB, dict(sp="duck", em="🦆", mode="on", who="TOTO", at=(0.55, 0.62), w=0.38, anchor="bottom"),
              dict(sp="bubble", em="🫧", mode="on", who="TOTO", at=(-0.10, 0.60), w=0.22, frm=2),
              dict(sp="bubble", em="🫧", mode="on", who="TOTO", at=(0.10, 0.62), w=0.26, frm=2),
              dict(sp="bubble", em="🫧", mode="rise", n=10)],
    (2, 11): [dict(sp="lotion", em="🧴", mode="ground", x=0.12, size=0.16),
              dict(sp="comb", em="🪮", mode="on", who="TOTO", at=(0.18, 0.06), w=0.42, rot=25, anchor="bottom"),
              dict(mode="sparkle", who="TOTO", frm=1)],
    (2, 12): [dict(mode="sparkle", who="TOTO"),
              dict(sp="sock", em="🧦", mode="ground", x=0.86, size=0.16, frm=1)],
}
