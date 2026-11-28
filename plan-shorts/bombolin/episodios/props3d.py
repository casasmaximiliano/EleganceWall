"""Reemplazo de emojis por modelos 3D. Regla del canal: NADA de emojis en pantalla (emoji = baja calidad).

EMOJI3D[emoji] = ("prop", nombre) para objetos de BOMBOLIN_OBJ3D, o ("guest", nombre) para animales de BOMBOLIN_GUESTS3D.
La auditoría (auditoria.py) lista los emojis que todavía no tienen modelo para un día dado.
"""
EMOJI3D = {
    # objetos ya modelados
    "🛁": ("prop", "bathtub"), "🛏": ("prop", "bed"), "🛏️": ("prop", "bed"), "🧽": ("prop", "sponge"),
    "🧼": ("prop", "soap"), "🦆": ("prop", "duck"), "🧦": ("prop", "sock"), "🍝": ("prop", "spaghetti"),
    "🪰": ("prop", "fly"), "🫧": ("prop", "bubble"), "🧴": ("prop", "lotion"), "🪮": ("prop", "comb"),
    "🟤": ("prop", "mudball"), "🪁": ("prop", "kite"), "☂️": ("prop", "umbrella"), "☂": ("prop", "umbrella"),
    "🌧️": ("prop", "raincloud"), "🌧": ("prop", "raincloud"), "🔦": ("prop", "flashlight"), "🧸": ("prop", "teddy"),
    "📖": ("prop", "book"), "📚": ("prop", "book"), "🌈": ("prop", "rainbow"),
    # carrera y otros (objetos3.py)
    "🏁": ("prop", "flag"), "🥇": ("prop", "medal"), "🏅": ("prop", "medal"), "🏆": ("prop", "trophy"),
    "👟": ("prop", "sneakers"), "🍌": ("prop", "banana"), "🌸": ("prop", "flower_big"), "🌼": ("prop", "flower_big"),
    "🌷": ("prop", "flower_big"), "🎉": ("prop", "confetti"), "🎊": ("prop", "confetti"),
    # animales (invitados.py)
    "🐆": ("guest", "Guepardo"), "🦘": ("guest", "Canguro"), "🐇": ("guest", "Conejo"), "🐞": ("guest", "Mariquita"),
    "🐦": ("guest", "Pájaro"), "🐔": ("guest", "Gallina"), "🐓": ("guest", "Gallina"), "🐷": ("guest", "Cerdito"),
    "🐘": ("guest", "Elefante"), "🐧": ("guest", "Pingüino"), "🐶": ("guest", "Perrito"), "🐕": ("guest", "Perrito"),
    "🐱": ("guest", "Gato"), "🐈": ("guest", "Gato"), "🐄": ("guest", "Vaca"), "🐮": ("guest", "Vaca"),
    "🐑": ("guest", "Oveja"), "🐸": ("guest", "Rana"), "🐒": ("guest", "Mono"), "🐵": ("guest", "Mono"),
    "🦁": ("guest", "León"), "🦒": ("guest", "Jirafa"), "🐙": ("guest", "Pulpo"), "🐳": ("guest", "Ballena"),
    "🐋": ("guest", "Ballena"), "🦉": ("guest", "Búho"), "🐿️": ("guest", "Ardilla"), "🐿": ("guest", "Ardilla"),
    "🐰": ("guest", "Conejo"), "🦜": ("guest", "Pájaro"), "🐤": ("guest", "Pájaro"), "🐥": ("guest", "Pájaro"),
    "🐣": ("guest", "Pájaro"), "🐊": ("guest", "Cocodrilo"), "🦩": ("guest", "Flamenco"), "🐜": ("guest", "Hormiga"),
    "🦥": ("guest", "Perezoso"), "🦕": ("guest", "Braquiosaurio"), "🦖": ("guest", "Tricerátops"),
    "🐢": ("guest", "Tortuga"), "🐌": ("guest", "Caracol"), "🦇": ("guest", "Murciélago"), "🐟": ("guest", "Pez"),
    "🐠": ("guest", "Pez"), "🐨": ("guest", "Koala"), "🦫": ("guest", "Castor"), "🦎": ("guest", "Camaleón"),
    "🐝": ("guest", "Abeja"), "🦋": ("guest", "Mariposa"),
    # objetos4.py (todo lo demás que salía como emoji)
    "🐾": ("prop", "paws"), "💨": ("prop", "wind"), "🎈": ("prop", "balloon"), "🪶": ("prop", "feather"),
    "🍓": ("prop", "strawberry"), "🐬": ("prop", "dolphin"), "🕷": ("prop", "spider"), "🕷️": ("prop", "spider"),
    "💧": ("prop", "drop"), "🎸": ("prop", "guitar"), "🎲": ("prop", "dice"), "🏠": ("prop", "house"),
    "🏡": ("prop", "house"), "📏": ("prop", "ruler"), "☀": ("prop", "sun"), "☀️": ("prop", "sun"),
    "🌞": ("prop", "sun"), "🧠": ("prop", "brain"), "🚗": ("prop", "car"), "🚙": ("prop", "car"),
    "🍃": ("prop", "leaves"), "🌿": ("prop", "leaf"), "🍂": ("prop", "leaf"), "👅": ("prop", "tongue"),
    "🦐": ("prop", "shrimp"), "🦅": ("prop", "eagle"), "🌳": ("prop", "tree"), "🌲": ("prop", "tree"),
    "🦴": ("prop", "bone"), "⏰": ("prop", "clock"), "⭐": ("prop", "star"), "🌟": ("prop", "star"),
    "✨": ("prop", "star"), "⚡": ("prop", "lightning"), "💦": ("prop", "splash"), "🦷": ("prop", "tooth"),
    "🪥": ("prop", "toothbrush"), "🎤": ("prop", "microphone"), "🙌": ("prop", "hands_up"), "👏": ("prop", "hands_up"),
    "🥚": ("prop", "egg"), "💡": ("prop", "lightbulb"), "🌙": ("prop", "moon"), "🌛": ("prop", "moon"),
    "❤️": ("prop", "heart"), "❤": ("prop", "heart"), "💛": ("prop", "heart"), "🥕": ("prop", "carrot"),
    "🍎": ("prop", "apple"), "🍪": ("prop", "cookie"), "🌊": ("prop", "sea_wave"), "🌴": ("prop", "palm"),
    "🍄": ("prop", "mushroom"), "❄": ("prop", "snowflake"), "❄️": ("prop", "snowflake"),
}
