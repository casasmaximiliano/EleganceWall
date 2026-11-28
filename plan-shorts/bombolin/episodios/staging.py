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
- "guest":  suma un invitado 3D a la escena aunque no hable ("name").
Si una escena tiene puesta en escena, sus emojis «sueltos» no se dibujan.
"""

MUD = (120, 78, 40)
# Lo de Toto sucio: fideos con salsa sobre la cabeza y una media pegada al costado
SPAG = dict(sp="spaghetti", em="🍝", mode="on", who="TOTO", at=(0.06, 0.16), w=0.55, rot=-8, anchor="bottom")
SOCK = dict(sp="sock", em="🧦", mode="on", who="TOTO", at=(0.47, 0.50), w=0.26, rot=-35)
# Toto metido en la bañera llena de espuma
TUB = dict(sp="bathtub", em="🛁", mode="front", who="TOTO", w=1.45, size=0.62, hide=-0.38)  # Toto sentado adentro

# Variantes 3D de Toto (3d/variantes.py): el personaje y sus objetos modelados juntos, con la misma luz
SUCIO = dict(mode="variant", who="TOTO", name="sucio")
BANERA = dict(mode="variant", who="TOTO", name="banera")
CAMA = dict(mode="variant", who="TOTO", name="cama")
LIMPIO = dict(mode="variant", who="TOTO", name="limpio")

# Bombolín sostiene la cometa que vuela arriba a su derecha
KITE = dict(sp="kite", em="🪁", mode="on", who="PIPO", at=(0.95, -0.55), w=0.75, rot=-12)

STAGE = {
    # Día 2: ¡Toto no quiere bañarse!  ("sp" = objeto 3D de 3d/objetos.py; "em" = emoji de respaldo)
    (2, 0): [dict(sp="sponge", em="🧽", mode="ground", x=0.22, size=0.11),
             dict(em="🫧", mode="rise", n=6), dict(CAMA, frm=1)],
    (2, 1): [SUCIO],
    (2, 2): [SUCIO, dict(sp="fly", em="🪰", mode="orbit", who="TOTO", n=3, size=0.07)],
    (2, 3): [SUCIO, dict(sp="fly", em="🪰", mode="orbit", who="TOTO", n=2, size=0.07),
             dict(em="💦", mode="orbit", who="G:Pájaro", n=3, size=0.09, frm=2)],
    (2, 4): [SUCIO, dict(mode="puddle", x=0.38, w=0.22, col=MUD, back=True),
             dict(em="🐷", mode="ground", x=0.38, size=0.17, back=True)],
    (2, 5): [SUCIO, dict(mode="river"), dict(em="🌴", mode="ground", x=0.92, size=0.42, back=True)],
    (2, 6): [SUCIO, dict(mode="puddle", x=0.83, w=0.30, col=MUD),
             dict(sp="mudball", em="🟤", mode="orbit", who="G:Elefante", n=4, size=0.05, frm=2),
             dict(em="💦", mode="orbit", who="G:Elefante", n=2, size=0.09, frm=2)],
    (2, 8): [SUCIO, dict(em="🫧", mode="rise", n=6),
             dict(sp="soap", em="🧼", mode="ground", x=0.5, size=0.10)],
    (2, 9): [BANERA, dict(mode="theme", name="bath"), dict(em="🫧", mode="rise", n=6)],
    (2, 10): [BANERA, dict(mode="theme", name="bath"),
              dict(em="🫧", mode="on", size=0.20, who="TOTO", at=(0.0, 0.42), frm=2),
              dict(em="🫧", mode="rise", n=6)],
    (2, 11): [LIMPIO, dict(mode="theme", name="bath"),
              dict(sp="lotion", em="🧴", mode="ground", x=0.12, size=0.16),
              dict(sp="comb", em="🪮", mode="on", who="TOTO", at=(0.18, 0.06), w=0.36, rot=25, anchor="bottom")],
    (2, 12): [LIMPIO, dict(sp="sock", em="🧦", mode="ground", x=0.86, size=0.16, frm=1)],

    # Día 3: Lula tiene miedo de la tormenta
    (3, 0): [KITE],
    (3, 1): [KITE, dict(sp="raincloud", em="🌧️", mode="sky", x=0.82, y=0.16, size=0.18),
             dict(sp="raincloud", em="🌧️", mode="sky", x=0.64, y=0.10, size=0.13)],
    (3, 2): [dict(sp="raincloud", em="🌧️", mode="sky", x=0.5, y=0.26, size=0.30), dict(mode="rain", n=70),
             dict(mode="flash", lines=[0, 2])],
    (3, 3): [dict(mode="rain", n=40), dict(sp="teddy", em="🧸", mode="ground", x=0.9, size=0.17)],
    (3, 4): [dict(mode="dark", alpha=175), dict(sp="flashlight", em="🔦", mode="on", who="TOTO", at=(0.62, 0.48), w=0.85, frm=1),
             dict(sp="book", em="📖", mode="ground", x=0.1, size=0.12, frm=1)],
    (3, 5): [dict(mode="dark", alpha=120), dict(sp="teddy", em="🧸", mode="on", who="PIPO", at=(0.05, 0.62), w=0.55, frm=2)],
    (3, 6): [dict(mode="flash", lines=[0, 2]), dict(sp="teddy", em="🧸", mode="ground", x=0.9, size=0.15)],
    (3, 8): [dict(mode="flash", lines=[0]), dict(sp="teddy", em="🧸", mode="on", who="LULA", at=(0.0, 0.75), w=0.4)],
    (3, 9): [dict(mode="rain", n=25), dict(sp="umbrella", em="☂️", mode="ground", x=0.08, size=0.22)],
    (3, 10): [dict(sp="rainbow", em="🌈", mode="sky", x=0.5, y=0.2, size=0.32, frm=1), dict(mode="sparkle", who="LULA", frm=2)],
    (3, 11): [dict(sp="rainbow", em="🌈", mode="sky", x=0.5, y=0.2, size=0.32), KITE],
    (3, 12): [dict(mode="puddle", x=0.30, w=0.20, col=(80, 160, 240)), dict(mode="puddle", x=0.72, w=0.24, col=(80, 160, 240)),
              dict(em="💦", mode="orbit", who="ZUMBI", n=3, size=0.06, frm=1),
              dict(sp="rainbow", em="🌈", mode="sky", x=0.5, y=0.16, size=0.24)],

    # Día 4: La gran carrera de Zumbi — en la pista que se mueve (mode="race": v = velocidad de cada frase, en
    # pantallas por segundo; lead = corrimiento de cada corredor; world = objeto pegado a la pista)
    (4, 0): [dict(mode="race", v=[0.0]),
             dict(sp="start_line", em="🏁", mode="ground", x=0.5, size=0.1),
             dict(sp="flower_big", em="🌸", mode="ground", x=0.1, size=0.2)],
    (4, 1): [dict(mode="race", v=[0.0]),
             dict(sp="sneakers", em="👟", mode="ground", x=0.14, size=0.1),
             dict(sp="banana", em="🍌", mode="on", who="ZUMBI", at=(0.0, 0.5), w=0.45, rot=-20, frm=2)],
    (4, 2): [dict(mode="race", v=[0.0], lead=dict(ZUMBI=[0.0, 0.32, 0.32, 0.0])),
             dict(sp="start_line", em="🏁", mode="ground", x=0.5, size=0.1),
             dict(sp="flag", em="🚩", mode="on", who="ABU", at=(0.2, -0.05), w=0.45, rot=10)],
    (4, 3): [dict(mode="race", v=[0.0, 0.32], lead=dict(TOTO=[0.0, -0.06], ZUMBI=[0.0, 0.06])),
             dict(sp="start_line", em="🏁", mode="ground", x=0.5, size=0.1, world="start"),
             dict(sp="flag", em="🚩", mode="on", who="ABU", at=(0.2, -0.05), w=0.45, rot=10)],
    (4, 4): [dict(mode="race", v0=0.35, v=[0.45, 0.35, 0.35], lead={"G:Guepardo": [0.0]}),
             dict(sp="wind", em="💨", mode="sky", x=0.2, y=0.45, size=0.16)],
    (4, 5): [dict(mode="race", v0=0.32, v=[0.32]),
             dict(sp="flower_big", em="🌸", mode="ground", x=0.08, size=0.18, back=True, world="start")],
    (4, 6): [dict(sp="car", em="🚗", mode="ground", x=0.8, size=0.16, frm=0)],
    (4, 7): [dict(mode="race", v0=0.4, v=[0.45, 0.0, 0.0], lead={"G:Mariquita": [1.2, 0.0, 0.0]}),
             dict(mode="guest", name="Mariquita")],
    (4, 8): [dict(mode="race", v=[0.0]),
             dict(sp="water_bottle", em="💧", mode="on", who="PIPO", at=(0.42, 0.45), w=0.28, rot=-10)],
    (4, 9): [dict(mode="race", v=[0.0, 0.1, 0.14]),
             dict(sp="leaves", em="🍃", mode="ground", x=0.12, size=0.1, world="start")],
    (4, 10): [dict(mode="race", v0=0.14, v=[0.14], lead=dict(TOTO=[-0.45, 0.0, 0.0]))],
    (4, 11): [dict(mode="race", v0=0.8, stop_at=1.4),
              dict(sp="finish", em="🏁", mode="ground", x=0.5, size=0.42, back=True, world="end"),
              dict(sp="confetti", em="🎉", mode="sky", x=0.5, y=0.2, size=0.3, frm=0),
              dict(sp="medal", em="🏅", mode="on", who="ZUMBI", at=(0.0, 0.55), w=0.3, frm=1)],
}
