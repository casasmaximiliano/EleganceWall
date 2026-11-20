"""Genera los shorts de «El mundo de Pipo» (video vertical 1080x1920 con voces, música y subtítulos).

Uso:
  python3 render.py --voices DIR --out DIR [--only ID,ID] [--jobs 4]

- Voces: Piper TTS (offline) con modelos es_MX / es_AR; cada personaje tiene tono y velocidad propios.
- Imagen: personajes vectoriales originales (characters.py) + emojis Noto Color para animales y objetos.
- Música y efectos: sintetizados acá mismo (sin derechos de terceros).
"""
import argparse
import csv
import hashlib
import math
import os
import re
import subprocess
import sys
import unicodedata
import wave
import zlib
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, HERE)
from data_a import A  # noqa: E402
from data_bc import B, C  # noqa: E402
from data_def import D, E, F  # noqa: E402
from characters import build_sprites  # noqa: E402

W, H, FPS, SR = 1080, 1920, 24, 44100
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
JINGLE = "¡Un, dos, tres, a descubrir otra vez!"
ALL_SHORTS = {x["id"]: x for x in A + B + C + D + E + F}

# ---------------------------------------------------------------- voces
VOICES = {  # modelo, tono (x), length_scale (más alto = más lento)
    "PIPO": ("es_AR-daniela-high", 1.30, 1.00),
    "TOTO": ("es_MX-ald-medium", 0.86, 1.15),
    "LULA": ("es_MX-claude-high", 1.20, 1.08),
    "ZUMBI": ("es_AR-daniela-high", 1.45, 0.85),
    "ABU": ("es_MX-claude-high", 0.93, 1.12),
    "GM": ("es_MX-ald-medium", 1.10, 1.02),
    "GF": ("es_AR-daniela-high", 1.05, 1.02),
}
COLOR = {"PIPO": (110, 230, 150), "TOTO": (255, 160, 70), "LULA": (130, 205, 255), "ZUMBI": (255, 215, 60),
         "ABU": (205, 170, 255), "ALL": (255, 215, 60), "GUEST": (255, 140, 200)}
NAMES = {"Pipo": "PIPO", "Toto": "TOTO", "Lula": "LULA", "Zumbi": "ZUMBI", "Abu Tortu": "ABU", "Todos": "ALL"}
GUESTS = {  # nombre: (emoji, voz)
    "Gallina": ("🐔", "GF"), "Mamá Cocodrilo": ("🐊", "GF"), "Cocodrilo": ("🐊", "GM"), "Avestruz bebé": ("🐣", "GF"),
    "Mamá Avestruz": ("🪶", "GF"), "Rana": ("🐸", "GM"), "Colibrí": ("🐦", "GM"), "Guepardo": ("🐆", "GM"),
    "Pájaro": ("🐦", "GM"), "Pingüino": ("🐧", "GM"), "Murciélago": ("🦇", "GM"), "Chispi": ("🦇", "GF"),
    "Ardilla": ("🐿", "GF"), "Elefante": ("🐘", "GM"), "Gatito": ("🐱", "GF"), "Pajarito": ("🐤", "GM"),
    "Castor": ("🦫", "GM"), "Pulpo": ("🐙", "GM"), "Koala": ("🐨", "GM"), "Camaleón": ("🦎", "GM"),
    "Pez": ("🐠", "GF"), "Braquiosaurio": ("🦕", "GM"), "Caracol": ("🐌", "GF"), "Canguro": ("🦘", "GM"),
    "Tricerátops": ("🦕", "GM"), "Eco": (None, "PIPO"),
}
EMOJI_KW = [
    ("t. rex", "🦖"), ("tiranosaurio", "🦖"), ("velocirraptor", "🦖"), ("braquiosaurio", "🦕"), ("argentinosaurus", "🦕"),
    ("tricerátops", "🦕"), ("dinosaurio", "🦕"), ("huevo", "🥚"), ("cascarón", "🥚"), ("gallina", "🐔"), ("granja", "🏡"),
    ("cocodrilo", "🐊"), ("tortuga", "🐢"), ("caparazón", "🐢"), ("arena", "🏖"), ("playa", "🏖"), ("avestruz", "🐣"),
    ("gota", "💧"), ("lluvia", "🌧"), ("nube", "☁"), ("girasol", "🌻"), ("sol ", "☀"), ("rana", "🐸"), ("nenúfar", "🪷"),
    ("mariposa", "🦋"), ("lupa", "🔍"), ("arcoíris", "🌈"), ("avión", "✈"), ("colmena", "🐝"), ("abeja", "🐝"),
    ("colibrí", "🐦"), ("guepardo", "🐆"), ("mariquita", "🐞"), ("auto", "🚗"), ("meta", "🏁"), ("largada", "🏁"),
    ("confeti", "🎉"), ("flor", "🌸"), ("globo", "🎈"), ("torta", "🎂"), ("sorpresa", "🎁"), ("regalo", "🎁"),
    ("piedr", "🪨"), ("pingüino", "🐧"), ("pájaro", "🐦"), ("tapita", "🔵"), ("corazon", "❤"), ("corazón", "❤"),
    ("fósil", "🦴"), ("murciélago", "🦇"), ("linterna", "🔦"), ("cristal", "💎"), ("estalactita", "💎"), ("puerta", "🚪"),
    ("flamenco", "🦩"), ("camaron", "🦐"), ("alga", "🌿"), ("zanahoria", "🥕"), ("delfín", "🐬"), ("cerebro", "🧠"),
    ("reloj de arena", "⏳"), ("reloj", "⏰"), ("luna", "🌙"), ("estrella de mar", "⭐"), ("estrella", "⭐"),
    ("peluche", "🧸"), ("pijama", "🛏"), ("hipopótamo", "🦛"), ("sombrero", "👒"), ("protector", "🧴"), ("pulpo", "🐙"),
    ("roca", "🪨"), ("colectivo", "🚌"), ("nutria", "🦦"), ("cebra", "🦓"), ("huella", "👣"), ("miel", "🍯"),
    ("cuchar", "🥄"), ("frasco", "🍯"), ("juguete", "🧸"), ("media", "🧦"), ("ardilla", "🐿"), ("nuez", "🌰"),
    ("árbol", "🌳"), ("tobogán", "🛝"), ("tablet", "📱"), ("nieve", "❄"), ("rayo", "⚡"), ("trueno", "⚡"),
    ("esponja", "🧽"), ("elefante", "🐘"), ("burbuja", "🫧"), ("espuma", "🫧"), ("helado", "🍦"), ("brócoli", "🥦"),
    ("pileta", "🏊"), ("vaso", "🥛"), ("lágrima", "💧"), ("charco", "💧"), ("gato", "🐱"), ("micrófono", "🎤"),
    ("escenario", "🎤"), ("zapatilla", "👟"), ("castor", "🦫"), ("casco", "⛑"), ("manguera", "🚿"), ("patito", "🐥"),
    ("chimpancé", "🐒"), ("koala", "🐨"), ("camaleón", "🦎"), ("pez", "🐠"), ("branquia", "🐠"), ("edificio", "🏢"),
    ("caracol", "🐌"), ("medalla", "🏅"), ("cohete", "🚀"), ("astronauta", "🚀"), ("tierra", "🌍"), ("canguro", "🦘"),
    ("casa", "🏠"), ("techo", "🏠"), ("trampolín", "🤸"), ("ballena", "🐋"), ("barco", "⛵"), ("halcón", "🦅"),
    ("arañ", "🕷"), ("hormiga", "🐜"), ("caballito", "🐴"), ("búho", "🦉"), ("pluma", "🪶"), ("perro", "🐶"),
    ("pavo", "🦃"), ("frutilla", "🍓"), ("banana", "🍌"), ("manzana", "🍎"), ("kiwi", "🥝"), ("uva", "🍇"),
    ("diente", "🦷"), ("cepillo", "🪥"), ("jabón", "🧼"), ("manos", "🙌"), ("perezoso", "🦥"), ("calendario", "📅"),
    ("espejo", "🪞"), ("lengua", "👅"), ("jirafa", "🦒"), ("cinta métrica", "📏"), ("regla", "📏"), ("agua", "💧"),
    ("mar", "🌊"), ("ola", "🌊"), ("caramelo", "🍬"), ("fruta", "🍓"), ("plato", "🍽"), ("cometa", "🪁"),
    ("mapa", "🗺"), ("pato", "🦆"), ("velocímetro", "🏎"), ("ventana", "🪟"), ("hoja", "🍃"), ("risa", "😂"),
]
NUM_WORDS = {"0": "cero"}


def norm(s):
    return unicodedata.normalize("NFC", s.lower())


def tts_text(t):
    t = t.replace("«", "").replace("»", "")
    t = re.sub(r"Zzz-?", "Bsss, ", t)
    t = re.sub(r"\bzzz\b", "sss", t, flags=re.I)
    t = t.replace("T. rex", "Tiranosaurio Rex").replace("rawr", "roarrr").replace("Rawr", "Roarrr")
    t = t.replace("RAWR", "ROARRR").replace("…", ", ")
    return t


# ---------------------------------------------------------------- audio
_voice_cache = {}


def _load_voice(model, vdir):
    if model not in _voice_cache:
        from piper import PiperVoice
        _voice_cache[model] = PiperVoice.load(os.path.join(vdir, model + ".onnx"))
    return _voice_cache[model]


def read_wav(p):
    with wave.open(p) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            a = a.reshape(-1, 2).mean(1)
    return a


def tts(key, text, vdir, cache, echo=False):
    model, pitch, ls = VOICES[key]
    h = hashlib.md5(f"{key}|{text}|{echo}|v3".encode()).hexdigest()
    out = os.path.join(cache, h + ".wav")
    if not os.path.exists(out):
        from piper import SynthesisConfig
        raw = out + ".raw.wav"
        v = _load_voice(model, vdir)
        with wave.open(raw, "wb") as wf:
            v.synthesize_wav(tts_text(text), wf, syn_config=SynthesisConfig(length_scale=ls, noise_scale=0.6))
        sr = v.config.sample_rate
        af = f"asetrate={int(sr * pitch)},aresample={SR},atempo={1 / pitch:.4f}"
        if echo:
            af += ",aecho=0.8:0.7:350|700:0.45|0.25"
        af += ",silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", af, "-ac", "1", "-ar", str(SR), out], check=True)
        os.remove(raw)
    a = read_wav(out)
    pk = np.abs(a).max() or 1
    return a / pk * 0.85


def chorus(text, vdir, cache):
    """Coro sincronizado: UNA sola locución base (misma duración de cada sílaba) a la que se le cambia
    solo el tono para cada personaje. Así todas las voces empiezan y terminan cada palabra a la vez."""
    h = hashlib.md5(f"CHORUS|{text}|v4".encode()).hexdigest()
    out = os.path.join(cache, h + ".wav")
    if not os.path.exists(out):
        from piper import SynthesisConfig
        model = "es_AR-daniela-high"
        v = _load_voice(model, vdir)
        raw, base = out + ".raw.wav", out + ".base.wav"
        with wave.open(raw, "wb") as wf:
            v.synthesize_wav(tts_text(text), wf, syn_config=SynthesisConfig(length_scale=1.05, noise_scale=0.5, noise_w_scale=0.0))
        trim = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                "silenceremove=start_periods=1:start_threshold=-45dB,areverse")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", f"aresample={SR},{trim}", "-ac", "1", base], check=True)
        sr0 = SR
        parts = []
        for pitch, gain in ((1.30, 1.0), (0.86, 0.55), (1.20, 0.5), (1.45, 0.45)):  # Pipo (voz principal), Toto, Lula, Zumbi
            pv = out + f".{pitch}.wav"
            af = f"asetrate={int(sr0 * pitch)},aresample={SR},atempo={1 / pitch:.5f}"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", base, "-af", af, "-ac", "1", pv], check=True)
            a = read_wav(pv)
            parts.append((a / (np.abs(a).max() or 1)) * gain)
            os.remove(pv)
        n = min(len(p) for p in parts)  # misma duración: se recorta al más corto (difieren en milisegundos)
        mix = sum(p[:n] for p in parts)
        mix = mix / (np.abs(mix).max() or 1) * 0.85
        with wave.open(out, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((mix * 32767).astype(np.int16).tobytes())
        os.remove(raw)
        os.remove(base)
    a = read_wav(out)
    return a / (np.abs(a).max() or 1) * 0.85


def env(n, a=0.005, r=0.3):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / r)


def tone(f, d, r=0.25, harm=(1, 0.4, 0.15)):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = sum(amp * np.sin(2 * np.pi * f * (i + 1) * t) for i, amp in enumerate(harm))
    return (s * env(n, r=r)).astype(np.float32)


def sfx(kind):
    if kind == "tin":
        a = 0.5 * tone(1568, 0.7, 0.25)
        b = 0.4 * np.pad(tone(2093, 0.6, 0.25), (int(0.09 * SR), 0))
        b = np.pad(b, (0, max(0, len(a) - len(b))))[:len(a)]
        return a + b
    if kind == "beep":
        return tone(880, 0.25, 0.12)
    if kind == "go":
        return tone(1320, 0.5, 0.2)
    if kind == "boing":
        n = int(0.5 * SR)
        t = np.arange(n) / SR
        f = 250 + 400 * t + 40 * np.sin(2 * np.pi * 14 * t)
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, r=0.25)).astype(np.float32)
    if kind == "whoosh":
        n = int(0.8 * SR)
        rng = np.random.default_rng(1)
        x = rng.standard_normal(n).astype(np.float32)
        k = np.linspace(2, 40, n).astype(int)
        y = np.convolve(x, np.ones(20) / 20, "same") * np.sin(np.linspace(0, np.pi, n))
        return (y * 0.9).astype(np.float32)
    if kind == "pop":
        n = int(0.12 * SR)
        t = np.arange(n) / SR
        return (np.sin(2 * np.pi * (500 + 3000 * t) * t) * env(n, r=0.05)).astype(np.float32)
    if kind == "yay":
        return sum(0.3 * tone(f, 1.0, 0.5) for f in (523, 659, 784, 1047))
    return np.zeros(1, np.float32)


def music(dur, fmt, calm):
    """Cama musical alegre (marimba + bajo + shaker), loop de 4 acordes."""
    bpm = 100 if calm else (116 if fmt == "F" else 108)
    beat = 60 / bpm
    n = int((dur + 1) * SR)
    out = np.zeros(n, np.float32)
    chords = [(60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)]  # C G Am F
    mel = [0, 2, 1, 2, 0, 1, 2, 1]
    f = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731
    i, t = 0, 0.0
    while t < dur + 1:
        ch = chords[(i // 8) % 4]
        note = ch[mel[i % 8]] + 12
        s = tone(f(note), beat * 1.2, 0.18, (1, 0.25, 0.08)) * 0.5
        a = int(t * SR)
        out[a:a + len(s)] += s[: max(0, n - a)]
        if i % 2 == 0:
            b = tone(f(ch[0] - 24), beat * 1.8, 0.4, (1, 0.5)) * 0.55
            out[a:a + len(b)] += b[: max(0, n - a)]
        if not calm:
            rng = np.random.default_rng(i)
            sh = rng.standard_normal(int(0.05 * SR)).astype(np.float32) * env(int(0.05 * SR), 0.001, 0.015) * 0.12
            out[a:a + len(sh)] += sh[: max(0, n - a)]
            if fmt == "F" and i % 4 == 2:
                cl = rng.standard_normal(int(0.12 * SR)).astype(np.float32) * env(int(0.12 * SR), 0.001, 0.03) * 0.35
                out[a:a + len(cl)] += cl[: max(0, n - a)]
        i += 1
        t += beat / 2
    fade = np.ones(n, np.float32)
    k = int(0.8 * SR)
    fade[-k:] = np.linspace(1, 0, k)
    return out * fade / (np.abs(out).max() or 1)


# ---------------------------------------------------------------- guion -> líneas
LINE_RE = re.compile(r"([A-ZÁÉÍÓÚÑ][^:«»|]*?):\s*«([^»]*)»")


def speaker_key(raw):
    base = raw.split("(")[0].strip()
    qual = raw[len(base):].lower()
    if base in NAMES:
        return NAMES[base], base, qual
    for g in sorted(GUESTS, key=len, reverse=True):
        if base.startswith(g) or g in base:
            return "G:" + g, g, qual
    return "G:?", base, qual


def build_lines(x):
    scenes = []
    for sc in x["s"]:
        vis, txt = [p.strip() for p in sc.split("|", 1)]
        lines = [(speaker_key(r), t.strip()) for r, t in LINE_RE.findall(txt)]
        scenes.append({"vis": vis, "lines": lines})
    l = x["l"]
    close = []
    ABU = ("ABU", "Abu Tortu", "")
    ALL = ("ALL", "Todos", "")
    if x["f"] == "F":
        close = [(ALL, x["song"][0].replace(" | ", " ")), (ABU, f"¡Hoy aprendimos que {l}! ¡Cántala otra vez!")]
    elif x["f"] == "A":
        close = [(ABU, f"¡Hoy aprendimos que {l}!"), (ABU, x["cliff"]), (ALL, JINGLE)]
    elif x["f"] == "E":
        close = [(ABU, f"¡Hoy aprendimos que {l}! ¡Juega otra vez!"), (ALL, JINGLE)]
    else:
        close = [(ABU, f"¡Hoy aprendimos que {l}!"), (ALL, JINGLE)]
    scenes.append({"vis": "CIERRE " + x["s"][0].split("|")[0], "lines": close, "closing": True})
    return scenes


# ---------------------------------------------------------------- dibujo
_font_cache, _emoji_cache = {}, {}


def font(sz):
    if sz not in _font_cache:
        _font_cache[sz] = ImageFont.truetype(FONT_B, sz)
    return _font_cache[sz]


def emoji(ch, size):
    key = (ch, size)
    if key not in _emoji_cache:
        ef = ImageFont.truetype(FONT_EMOJI, 109)
        im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((8, 8), ch.replace("️", ""), font=ef, embedded_color=True)
        bb = im.getbbox() or (0, 0, 1, 1)
        im = im.crop(bb)
        sc = size / max(im.size)
        _emoji_cache[key] = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    return _emoji_cache[key]


def vgrad(c1, c2, h=H):
    a = np.linspace(0, 1, h)[:, None, None]
    g = (np.array(c1)[None, None] * (1 - a) + np.array(c2)[None, None] * a).astype(np.uint8)
    return Image.fromarray(np.repeat(g, W, axis=1), "RGB")


def theme_of(vis, fmt):
    v = norm(vis)
    if "pizarra" in v or (fmt == "B" and not v.startswith("cierre")):
        return "board"
    if any(k in v for k in ("luna", "astronauta")) and "lunares" not in v:
        return "moon"
    if any(k in v for k in ("cueva", "estalactita")):
        return "cave"
    if any(k in v for k in ("mar ", "bucea", "océano", "submarin", "fondo del mar", "caballito", "nada con", "pulpo")):
        return "sea"
    if any(k in v for k in ("noche", "pijama", "duerme", "dormir", "oscur", "apagué")):
        return "night"
    if any(k in v for k in ("nieve", "pingüino")):
        return "snow"
    if fmt == "E" or any(k in v for k in ("escenario", "podio", "cuenta regresiva")):
        return "show"
    if any(k in v for k in ("cuarto", "baño", "cocina", "cama", "habitación", "espejo", "vaso", "plato")):
        return "room"
    return "meadow"


def make_bg(theme, seed):
    rng = np.random.default_rng(seed)
    if theme == "sea":
        im = vgrad((120, 210, 255), (20, 80, 170))
        d = ImageDraw.Draw(im, "RGBA")
        for _ in range(25):
            x, y, r = rng.integers(0, W), rng.integers(300, H), rng.integers(8, 30)
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, 120), width=4)
        d.rectangle([0, 1500, W, H], fill=(240, 210, 140))
        for x in range(60, W, 180):
            d.polygon([(x, 1500), (x + 30, 1300), (x + 60, 1500)], fill=(60, 180, 110))
    elif theme == "moon":
        im = vgrad((10, 10, 40), (30, 30, 80))
        d = ImageDraw.Draw(im, "RGBA")
        for _ in range(120):
            x, y = rng.integers(0, W), rng.integers(0, 1300)
            d.ellipse([x, y, x + 4, y + 4], fill=(255, 255, 255, 200))
        d.ellipse([700, 300, 950, 550], fill=(80, 150, 255))
        d.ellipse([-300, 1300, W + 300, 2600], fill=(190, 190, 200))
        for (x, y, r) in [(200, 1500, 50), (700, 1600, 70), (450, 1750, 40)]:
            d.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=(160, 160, 170))
    elif theme == "cave":
        im = vgrad((70, 50, 110), (30, 20, 50))
        d = ImageDraw.Draw(im, "RGBA")
        for x in range(0, W, 90):
            hgt = rng.integers(80, 260)
            d.polygon([(x, 0), (x + 45, hgt), (x + 90, 0)], fill=(120, 100, 160))
        for _ in range(14):
            x, y = rng.integers(0, W), rng.integers(200, 1300)
            c = [(120, 255, 230, 200), (255, 150, 230, 200), (255, 240, 120, 200)][rng.integers(0, 3)]
            d.polygon([(x, y), (x + 18, y + 40), (x, y + 80), (x - 18, y + 40)], fill=c)
        d.rectangle([0, 1450, W, H], fill=(90, 70, 120))
    elif theme == "night":
        im = vgrad((40, 50, 120), (110, 90, 170))
        d = ImageDraw.Draw(im, "RGBA")
        for _ in range(70):
            x, y = rng.integers(0, W), rng.integers(0, 1200)
            d.ellipse([x, y, x + 6, y + 6], fill=(255, 250, 200, 220))
        d.ellipse([760, 200, 960, 400], fill=(255, 245, 190))
        d.ellipse([720, 170, 900, 350], fill=(40, 50, 120))
        d.rectangle([0, 1450, W, H], fill=(70, 60, 130))
    elif theme == "snow":
        im = vgrad((180, 220, 255), (235, 245, 255))
        d = ImageDraw.Draw(im, "RGBA")
        d.ellipse([-200, 1350, W + 200, 2400], fill=(255, 255, 255))
        for _ in range(60):
            x, y = rng.integers(0, W), rng.integers(0, 1400)
            d.ellipse([x, y, x + 10, y + 10], fill=(255, 255, 255, 230))
    elif theme == "show":
        im = vgrad((120, 60, 200), (60, 20, 120))
        d = ImageDraw.Draw(im, "RGBA")
        for i in range(12):
            a = i / 12 * 2 * math.pi
            d.polygon([(W / 2, 900), (W / 2 + 1500 * math.cos(a), 900 + 1500 * math.sin(a)),
                       (W / 2 + 1500 * math.cos(a + 0.2), 900 + 1500 * math.sin(a + 0.2))], fill=(255, 255, 255, 25))
        d.ellipse([140, 1380, W - 140, 1560], fill=(255, 200, 80), outline=(255, 255, 255), width=8)
        for x in range(40, W, 80):
            d.ellipse([x, 60, x + 30, 90], fill=(255, 230, 120))
    elif theme == "room":
        im = vgrad((255, 236, 210), (255, 220, 190))
        d = ImageDraw.Draw(im, "RGBA")
        d.rectangle([0, 1420, W, H], fill=(200, 150, 110))
        for x in range(0, W, 120):
            d.line([x, 1420, x, H], fill=(180, 130, 95), width=4)
        d.rounded_rectangle([700, 260, 980, 560], 20, fill=(170, 220, 255), outline=(255, 255, 255), width=14)
        d.line([840, 260, 840, 560], fill=(255, 255, 255), width=10)
    else:  # meadow / board base
        im = vgrad((130, 205, 255), (205, 240, 255))
        d = ImageDraw.Draw(im, "RGBA")
        d.ellipse([780, 140, 980, 340], fill=(255, 225, 90))
        for (x, y) in [(120, 300), (480, 200)]:
            for dx, dy, r in [(0, 0, 60), (60, -20, 70), (130, 0, 55)]:
                d.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=(255, 255, 255, 235))
        d.ellipse([-400, 1250, 700, 2300], fill=(120, 205, 110))
        d.ellipse([300, 1300, W + 500, 2300], fill=(100, 190, 95))
        for _ in range(30):
            x, y = rng.integers(0, W), rng.integers(1400, H)
            c = [(255, 120, 150), (255, 230, 90), (255, 255, 255)][rng.integers(0, 3)]
            d.ellipse([x, y, x + 16, y + 16], fill=c)
    if theme == "board":
        d = ImageDraw.Draw(im, "RGBA")
        d.rounded_rectangle([60, 420, W - 60, 1080], 30, fill=(150, 100, 60))
        d.rounded_rectangle([90, 450, W - 90, 1050], 20, fill=(40, 90, 70))
        for _ in range(6):
            x, y = rng.integers(130, W - 300), rng.integers(500, 980)
            d.arc([x, y, x + 160, y + 60], 180, 360, fill=(220, 240, 220, 120), width=5)
    return im


def text_center(d, cx, y, s, sz, fill, stroke=(30, 25, 45), sw=None, maxw=W - 100):
    f = font(sz)
    while d.textlength(s, font=f) > maxw and sz > 30:
        sz -= 4
        f = font(sz)
    d.text((cx, y), s, font=f, fill=fill, anchor="mm", stroke_width=sw or max(4, sz // 10), stroke_fill=stroke)


def chunk_words(words, max_chars=22):
    chunks, cur = [], []
    for i, w in enumerate(words):
        if cur and (sum(len(words[j]) + 1 for j in cur) + len(w) > max_chars):
            chunks.append(cur)
            cur = []
        cur.append(i)
        if w.endswith((".", "!", "?", ",")) and len(cur) >= 2:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


# ---------------------------------------------------------------- render de un short
def lula_mood(x, vis):
    v = norm(vis)
    if any(k in v for k in ("gris", "llora", "triste", "tiembla")):
        return "sad"
    if any(k in v for k in ("roja", "enoj", "truenito")):
        return "angry"
    if any(k in v for k in ("rosada", "vergüenza", "escondida")):
        return "shy"
    if any(k in v for k in ("arcoíris", "feliz", "colores", "festejan")):
        return "happy"
    if x.get("serie") == "Lula perdió su arcoíris" and x["cap"] < 5:
        return "sad"
    return "calm"


def render_short(args):
    sid, vdir, outdir, cache, meta = args
    x = ALL_SHORTS[sid]
    sprites = build_sprites()
    scenes = build_lines(x)

    # ---- audio por línea y línea de tiempo
    events, sfx_ev = [], []
    t = 0.05
    for si, sc in enumerate(scenes):
        sc["t0"] = t if si else 0.0
        if "pizarra" in norm(sc["vis"]):
            sfx_ev.append((t + 0.1, "tin", 0.35))
        if si and not sc.get("closing"):
            sfx_ev.append((t, "pop", 0.25))
        for (key, name, qual), text in sc["lines"]:
            if key == "ALL":
                a = chorus(text, vdir, cache)
            elif key.startswith("G:"):
                g = key[2:]
                vk = GUESTS.get(g, (None, "GM"))[1]
                a = tts(vk, text, vdir, cache, echo=(g == "Eco"))
            else:
                a = tts(key, text, vdir, cache)
            if "rebobin" in norm(text):
                sfx_ev.append((t, "whoosh", 0.5))
            if key == "TOTO" and text.startswith("¡Uy"):
                sfx_ev.append((t, "boing", 0.3))
            if "tres, dos, uno" in norm(text):
                d3 = len(a) / SR
                for k in range(3):
                    sfx_ev.append((t + k * d3 / 3, "beep", 0.4))
                sfx_ev.append((t + d3, "go", 0.4))
            if sc.get("closing") and text == JINGLE:
                sfx_ev.append((t, "yay", 0.25))
            events.append({"t": t, "a": a, "key": key, "name": name, "qual": qual, "text": text, "scene": si})
            t += len(a) / SR + 0.28
        t = max(t, sc["t0"] + 3.4) + 0.15
        sc["t1"] = t
    total = t + 0.5
    n = int(total * SR)
    voice = np.zeros(n, np.float32)
    talk = {}  # personaje -> envolvente por frame
    nf = int(total * FPS) + 1
    for ev in events:
        a = int(ev["t"] * SR)
        voice[a:a + len(ev["a"])] += ev["a"][: n - a]
        keys = ["PIPO", "TOTO", "LULA", "ZUMBI"] if ev["key"] == "ALL" else [ev["key"]]
        hop = SR // FPS
        rms = np.sqrt(np.convolve(ev["a"] ** 2, np.ones(hop) / hop, "same"))[::hop]
        f0 = int(ev["t"] * FPS)
        for k in keys:
            arr = talk.setdefault(k, np.zeros(nf, np.float32))
            m = min(len(rms), nf - f0)
            arr[f0:f0 + m] = np.maximum(arr[f0:f0 + m], rms[:m])
    mix = voice * 1.0
    calm = meta["hora"] == "19:30"
    mvol = {"F": 0.16, "B": 0.07}.get(x["f"], 0.09) * (0.8 if calm else 1)
    mix += music(total, x["f"], calm)[:n] * mvol
    for (ts, kind, vol) in sfx_ev:
        s = sfx(kind) * vol
        a = int(ts * SR)
        mix[a:a + len(s)] += s[: max(0, n - a)]
    mix = np.tanh(mix * 1.1) * 0.95
    base = meta["file"]
    wav_p = os.path.join(cache, base + ".wav")
    with wave.open(wav_p, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())

    # ---- preparar escenas visuales
    sc_fallback = []
    allv = norm(" ".join(sc["vis"] for sc in scenes))
    for kw, em in EMOJI_KW:
        mm = re.search(r"(?<![a-záéíóúñ])" + re.escape(kw.strip()), allv)
        if mm:
            sc_fallback.append((mm.start(), em))
    sc_fallback = [e for _, e in sorted(sc_fallback)]
    for si, sc in enumerate(scenes):
        vis = sc["vis"]
        th = theme_of(vis if not sc.get("closing") else scenes[0]["vis"], x["f"])
        sc["theme"] = th
        sc["bg"] = make_bg(th, zlib.crc32(sid.encode()) % 1000 + si)
        v = norm(vis)
        props = []
        for kw, em in EMOJI_KW:
            mm = re.search(r"(?<![a-záéíóúñ])" + re.escape(kw.strip()), v)
            p = mm.start() if mm else -1
            if p >= 0 and em not in [e for _, e in props]:
                props.append((p, em))
        props = [e for _, e in sorted(props)][:3]
        speakers = [ln[0][0] for ln in sc["lines"]]
        guests = []
        for (key, name, qual), _ in sc["lines"]:
            if key.startswith("G:"):
                em = GUESTS.get(key[2:], (None,))[0]
                if em and em not in guests:
                    guests.append(em)
        props = [p for p in props if p not in guests]
        if not props and not guests:
            props = sc_fallback[:1]
        cast = []
        for c in x["ch"]:
            nm = {"PIPO": "pipo", "TOTO": "toto", "LULA": "lula", "ZUMBI": "zumbi", "ABU": "abu tortu"}[c]
            on = nm in v or (c in speakers and not (c == "ABU" and any("voz" in q for (k, _, q), _ in sc["lines"] if k == "ABU")))
            if sc.get("closing"):
                on = True
            if c == "ABU" and sc.get("closing") and "ABU" not in x["ch"]:
                on = False
            if on:
                cast.append(c)
        if "ALL" in speakers and not sc.get("closing"):
            cast = list(dict.fromkeys(cast + [c for c in x["ch"] if c != "ABU"]))
        if sc.get("closing"):
            cast = [c for c in ["PIPO", "TOTO", "LULA", "ZUMBI"] if c in x["ch"]] or ["PIPO"]
            if "PIPO" not in cast:
                cast.insert(0, "PIPO")
        if not cast:
            cast = ["PIPO"]
        sc["cast"], sc["props"], sc["guests"] = cast, props, guests
        sc["mood"] = lula_mood(x, vis)
        # posiciones
        items = cast + ["G" + g for g in guests]
        k = len(items)
        sc["pos"] = {it: (int(W * (i + 1) / (k + 1)), 1430) for i, it in enumerate(items)}
        sc["scale"] = 0.95 if k <= 2 else (0.78 if k == 3 else 0.62)

    hook_t = 3.6
    abu_narr = any(ev["key"] == "ABU" for ev in events)

    def scene_at(tt):
        for sc in scenes:
            if tt < sc["t1"]:
                return sc
        return scenes[-1]

    def event_at(tt):
        cur = None
        for ev in events:
            if ev["t"] - 0.05 <= tt < ev["t"] + len(ev["a"]) / SR + 0.25:
                cur = ev
        return cur

    out_mp4 = os.path.join(outdir, base + ".mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", wav_p, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out_mp4]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    rng = np.random.default_rng(zlib.crc32(sid.encode()) % 10000)
    blink_at = {c: set(rng.integers(0, nf, nf // 70)) for c in ["PIPO", "TOTO", "LULA", "ZUMBI", "ABU"]}

    for fi in range(nf):
        tt = fi / FPS
        sc = scene_at(tt)
        st = tt - sc["t0"]
        frame = sc["bg"].copy()
        d = ImageDraw.Draw(frame, "RGBA")
        ev = event_at(tt)
        speaking = ev["key"] if ev else None
        # props flotando (con pop-in escalonado)
        for i, em in enumerate(sc["props"]):
            appear = 0.15 + i * 0.9
            if st < appear:
                continue
            k = min(1, (st - appear) / 0.25)
            size = int((320 if sc["theme"] == "board" else 280) * (0.6 + 0.4 * k) * (1.1 if k < 1 else 1))
            if sc["theme"] == "board":
                cx = int(W * (i + 1) / (len(sc["props"]) + 1))
                cy = 760 + int(14 * math.sin(tt * 2 + i))
            else:
                cx = [260, 820, 540][i]
                cy = [640, 700, 980][i] + int(18 * math.sin(tt * 2.2 + i))
            e = emoji(em, max(40, size))
            frame.paste(e, (cx - e.width // 2, cy - e.height // 2), e)
        # cuenta regresiva
        if ev and "tres, dos, uno" in norm(ev["text"]):
            dur = len(ev["a"]) / SR
            k = int(min(2, (tt - ev["t"]) / (dur / 3)))
            num = str(3 - k)
            ph = ((tt - ev["t"]) % (dur / 3)) / (dur / 3)
            r = int(230 + 40 * (1 - ph))
            d.ellipse([W // 2 - r, 800 - r, W // 2 + r, 800 + r], fill=(255, 90, 120, 230), outline=(255, 255, 255), width=14)
            text_center(d, W // 2, 800, num, int(300 + 60 * (1 - ph)), (255, 255, 255))
        # personajes
        sp_scale = sc["scale"]
        for it, (px, py) in sc["pos"].items():
            if it.startswith("G"):
                talking = speaking and speaking.startswith("G:") and GUESTS.get(speaking[2:], (None,))[0] == it[1:]
                amp = 1.12 + 0.06 * math.sin(tt * 18) if talking else 1.0
                e = emoji(it[1:], int(300 * sp_scale * amp))
                bob = int(10 * math.sin(tt * 3))
                frame.paste(e, (px - e.width // 2, py - e.height - 20 + bob), e)
                continue
            c = it
            lvl = talk.get(c, np.zeros(nf))[fi] if fi < len(talk.get(c, [])) else 0
            is_sp = speaking == c or (speaking == "ALL" and c != "ABU")
            mouth = 1 if (is_sp and lvl > 0.06 and (fi // 3) % 2 == 0) else 0
            blink = 1 if (fi in blink_at[c] or fi - 1 in blink_at[c] or fi - 2 in blink_at[c]) else 0
            if c == "LULA":
                spr = sprites[(c, sc["mood"] if not sc.get("closing") else "happy", mouth, blink)]
            elif c == "ZUMBI":
                spr = sprites[(c, fi % 2, mouth, blink)]
            else:
                spr = sprites[(c, mouth, blink)]
            base_h = {"PIPO": 540, "TOTO": 490, "LULA": 340, "ZUMBI": 280, "ABU": 540}[c]
            bounce = (abs(math.sin(tt * 7)) * 22 if is_sp else abs(math.sin(tt * 2 + px)) * 6)
            sq = 1 + (0.035 * math.sin(tt * 14) if is_sp else 0)
            hh = int(base_h * sp_scale * sq)
            ww = int(spr.width * hh / spr.height / sq)
            s2 = spr.resize((ww, hh), Image.BILINEAR)
            lift = {"LULA": 330, "ZUMBI": 300}.get(c, 0) * sp_scale
            frame.paste(s2, (px - ww // 2, int(py - hh - bounce - lift)), s2)
        # Abu narradora en burbuja (cuando habla «(voz)» y no está en escena)
        if speaking == "ABU" and "ABU" not in sc["cast"] and abu_narr:
            lvl = talk.get("ABU", np.zeros(nf))[fi]
            spr = sprites[("ABU", 1 if (lvl > 0.06 and (fi // 3) % 2 == 0) else 0, 0)]
            head = spr.crop((0, 75, 230, 305)).resize((200, 200), Image.BILINEAR)
            d.ellipse([30, 1100, 260, 1330], fill=(255, 250, 235), outline=(205, 170, 255), width=10)
            m = Image.new("L", (200, 200), 0)
            ImageDraw.Draw(m).ellipse([0, 0, 199, 199], fill=255)
            frame.paste(head, (45, 1115), Image.composite(head, Image.new("RGBA", (200, 200), (0, 0, 0, 0)), m))
        # efecto rebobinar
        if ev and "rebobin" in norm(ev["text"]):
            arr = np.asarray(frame).astype(np.int16)
            arr[::6] = np.clip(arr[::6] + 60, 0, 255)
            arr[..., 2] = np.clip(arr[..., 2] + 30, 0, 255)
            frame = Image.fromarray(arr.astype(np.uint8))
            d = ImageDraw.Draw(frame, "RGBA")
            text_center(d, W // 2, 760, "◀◀", 260, (255, 255, 255))
        # cámara: plano general / plano cerrado alternando cada ~3,2 s
        shot = int(st / 3.2) % 2
        if shot == 1 and not sc.get("closing"):
            z = 1.12 + 0.02 * ((st % 3.2) / 3.2)
            fx = sc["pos"].get(speaking, (W // 2, 0))[0] if speaking in sc["pos"] else W // 2
            cw, chh = int(W / z), int(H / z)
            x0 = int(min(max(fx - cw / 2, 0), W - cw))
            y0 = int((H - chh) * 0.62)
            frame = frame.crop((x0, y0, x0 + cw, y0 + chh)).resize((W, H), Image.BILINEAR)
            d = ImageDraw.Draw(frame, "RGBA")
        # cabecera
        d.rounded_rectangle([W // 2 - 230, 40, W // 2 + 230, 110], 35, fill=(255, 255, 255, 215))
        d.text((W // 2, 75), "El mundo de Pipo", font=font(40), fill=(60, 150, 100), anchor="mm")
        if x["f"] == "A":
            text_center(d, W // 2, 150, f"{x['serie']} · Cap. {x['cap']}", 38, (255, 255, 255), sw=5)
        # gancho (visible desde el frame 0)
        if tt < hook_t:
            wob = 1 + 0.04 * math.sin(tt * 9)
            text_center(d, W // 2, 330, x["hes"], int(118 * wob), (255, 214, 60), sw=12, maxw=W - 70)
        # cierre: banner
        if sc.get("closing"):
            if ev and ev["text"].startswith("¡Hoy aprendimos"):
                text_center(d, W // 2, 330, "¡HOY APRENDIMOS!", 96, (255, 214, 60), sw=11)
            elif ev and ev["key"] == "ALL":
                for i, c in enumerate([(255, 90, 90), (255, 170, 60), (255, 230, 80), (110, 210, 110), (90, 160, 255), (170, 110, 230)]):
                    d.arc([60 + i * 22, 420 + i * 22, W - 60 - i * 22, 1500 - i * 22], 180, 360, fill=c, width=22)
        # subtítulos palabra por palabra
        if ev:
            words = ev["text"].split()
            dur = max(0.3, len(ev["a"]) / SR)
            weights = np.array([len(w) + 2 for w in words], float)
            cum = np.cumsum(weights) / weights.sum() * dur
            wi = int(np.searchsorted(cum, tt - ev["t"]))
            wi = min(wi, len(words) - 1)
            chunks = chunk_words(words)
            ch = next(c for c in chunks if wi in c)
            col = COLOR.get(ev["key"], COLOR["GUEST"]) if not ev["key"].startswith("G:") else COLOR["GUEST"]
            sz = 84
            f = font(sz)
            full = " ".join(words[j] for j in ch)
            while d.textlength(full, font=f) > W - 80 and sz > 50:
                sz -= 4
                f = font(sz)
            tw = d.textlength(full, font=f)
            xx = (W - tw) / 2
            y = 1560
            label = ev["name"] if not ev["key"] == "ALL" else "Todos"
            d.text((W // 2, y - 85), label, font=font(40), fill=col, anchor="mm", stroke_width=5, stroke_fill=(30, 25, 45))
            for j in ch:
                wtxt = words[j] + " "
                fill = col if j == wi else (255, 255, 255)
                d.text((xx, y), wtxt, font=f, fill=fill, anchor="lm", stroke_width=8, stroke_fill=(30, 25, 45))
                xx += d.textlength(wtxt, font=f)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()
    os.remove(wav_p)
    return sid, round(total, 1)


def safe(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")[:50]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voices", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cache = os.path.join(a.out, "_cache")
    os.makedirs(cache, exist_ok=True)
    cal = list(csv.DictReader(open(os.path.join(HERE, "..", "calendario.csv"), encoding="utf-8")))
    only = set(filter(None, a.only.split(",")))
    jobs = []
    for r in cal:
        if only and r["id"] not in only:
            continue
        x = ALL_SHORTS[r["id"]]
        fname = f"Dia{int(r['dia']):02d}_{r['hora'].replace(':', '')}_{r['id']}_{safe(x['tes'])}"
        jobs.append((r["id"], a.voices, a.out, cache, {"hora": r["hora"], "file": fname}))
    # 1) voces primero (en serie, se guardan en caché)
    for j in jobs:
        for sc in build_lines(ALL_SHORTS[j[0]]):
            for (key, name, qual), text in sc["lines"]:
                if key == "ALL":
                    chorus(text, a.voices, cache)
                elif key.startswith("G:"):
                    g = key[2:]
                    tts(GUESTS.get(g, (None, "GM"))[1], text, a.voices, cache, echo=(g == "Eco"))
                else:
                    tts(key, text, a.voices, cache)
    print("voces listas", flush=True)
    with Pool(a.jobs) as p:
        for sid, dur in p.imap_unordered(render_short, jobs):
            print(f"OK {sid} {dur}s", flush=True)


if __name__ == "__main__":
    main()
