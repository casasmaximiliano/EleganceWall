"""Genera voz (Kokoro TTS), música y efectos para cada short, y la línea de tiempo que usa el renderizador.

Uso: python3 build_audio.py [n1 n2 ...]   (sin argumentos: los 100)
Salida: out/audio/NNN.wav y out/timeline/NNN.json
"""
import json, os, re, subprocess, sys, tempfile
import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from shorts_pantalla import PANTALLA  # noqa: E402

SR = 24000
OUT = os.path.join(HERE, "out")
os.makedirs(os.path.join(OUT, "audio"), exist_ok=True)
os.makedirs(os.path.join(OUT, "timeline"), exist_ok=True)
CACHE = os.path.join(OUT, "tts_cache")
os.makedirs(CACHE, exist_ok=True)

# hablante -> (voz Kokoro, semitonos, velocidad, tipo de personaje en pantalla)
VOICES = {
 "Moni": ("ef_dora", 2, 1.08, "moni"),
 "Narrador": ("em_alex", 0, 1.05, None),
 "Tarjetín": ("em_santa", -1, 1.0, "card"),
 "Infla": ("ef_dora", -3, 0.98, "ghost"),
 "Préstamín": ("em_alex", 2, 1.12, "bill"),
 "Ofertín": ("em_alex", 4, 1.15, "tag"),
 "Zombi": ("em_santa", -4, 0.92, "zombi"),
 "Zombis": ("em_santa", -4, 0.92, "zombi"),
 "Gym Zombi": ("em_santa", -3, 0.95, "gymzombi"),
 "Delivy": ("em_santa", 3, 1.08, "bag"),
 "Carrito": ("em_alex", 5, 1.12, "cart"),
 "Botellín": ("em_alex", 3, 1.05, "bottle"),
 "Cafecito": ("ef_dora", 5, 1.05, "cup"),
 "Capricho": ("ef_dora", 6, 1.1, "bow"),
 "Fomito": ("em_alex", 6, 1.15, "fomito"),
 "Cajero": ("em_santa", -2, 0.98, "atm"),
 "Snacky": ("em_alex", 6, 1.1, "chips"),
 "Autito": ("em_santa", 2, 1.05, "car"),
 "Centavito": ("ef_dora", 7, 1.1, "centavito"),
 "Peso": ("em_alex", 1, 1.04, "peso"),
 "Resumen": ("em_alex", -3, 0.98, "doc"),
 "Cuotín": ("ef_dora", 8, 1.12, "cuotin"),
 "Cuotines": ("ef_dora", 8, 1.12, "cuotin"),
 "Celulín": ("em_santa", -3, 0.95, "phone"),
 "Remera": ("ef_dora", 4, 1.08, "shirt"),
 "Campera": ("em_santa", 0, 1.0, "jacket"),
}
FRIENDLY = {"moni", "centavito", "peso", "shirt", "jacket"}

_k = None
def kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro("/home/user/tts/kokoro-v1.0.onnx", "/home/user/tts/voices-v1.0.bin")
    return _k

EMOJI = re.compile("[\U0001F000-\U0001FFFF☀-➿️]")
def clean_for_tts(text):
    t = EMOJI.sub("", text).replace("…", "...").replace("“", "").replace("”", "")
    return re.sub(r"\s+", " ", t).strip()

def tts(text, speaker, speed_mult=1.0):
    voice, semis, speed, _ = VOICES[speaker]
    speed = speed * speed_mult
    import hashlib
    tag = "" if speed_mult == 1.0 else f"_s{speed_mult}"
    key = re.sub(r"[^a-z0-9]+", "_", f"{speaker}_{text}".lower())[:100] + "_" + hashlib.md5(f"{speaker}|{text}{tag}".encode()).hexdigest()[:10]
    path = os.path.join(CACHE, key + ".wav")
    if not os.path.exists(path):
        samples, sr = kokoro().create(clean_for_tts(text), voice=voice, speed=speed, lang="es")
        assert sr == SR
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            sf.write(tmp.name, samples, SR)
        f = 2 ** (semis / 12)
        filt = f"asetrate={int(SR * f)},aresample={SR},atempo={1 / f:.5f}"
        if speaker == "Infla":
            filt += ",aecho=0.8:0.7:60:0.3"
        if speaker in ("Zombi", "Zombis", "Gym Zombi"):
            filt += ",aecho=0.8:0.6:40:0.25"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp.name, "-af", filt, "-ar", str(SR), "-ac", "1", path], check=True)
        os.unlink(tmp.name)
    data, _ = sf.read(path, dtype="float32")
    # recortar silencios de los extremos
    idx = np.where(np.abs(data) > 0.01)[0]
    if len(idx):
        data = data[max(0, idx[0] - 240): idx[-1] + 480]
    return data

# ───── síntesis de música y efectos ─────
def env(n, a=0.005, r=None):
    e = np.ones(n, dtype=np.float32)
    na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    if r:
        nr = min(n, int(r * SR)); e[-nr:] *= np.linspace(1, 0, nr)
    return e

def pluck(freq, dur, bright=0.5):
    n = int(dur * SR); p = max(2, int(SR / freq))
    rng = np.random.default_rng(int(freq * 100))
    buf = (rng.random(p) * 2 - 1).astype(np.float32)
    out = np.zeros(n, dtype=np.float32)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * (bright * buf[i % p] + (1 - bright) * buf[(i + 1) % p]) if True else 0
    return out * env(n, 0.002, 0.05)

def pluck_fast(freq, dur, decay=0.996):
    n = int(dur * SR); p = max(2, int(round(SR / freq)))
    rng = np.random.default_rng(int(freq * 100))
    buf = (rng.random(p) * 2 - 1).astype(np.float32)
    reps = n // p + 2
    out = np.empty(reps * p, dtype=np.float32)
    for r in range(reps):
        out[r * p:(r + 1) * p] = buf
        buf = decay * 0.5 * (buf + np.roll(buf, -1))
    return out[:n] * env(n, 0.002, 0.08)

NOTE = lambda m: 440.0 * 2 ** ((m - 69) / 12)
PROGS = {
 "major": ([[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]], 98),   # C G Am F
 "minor": ([[57, 60, 64], [53, 57, 60], [48, 52, 55], [52, 56, 59]], 84),   # Am F C E
 "bright": ([[62, 66, 69], [57, 61, 64], [59, 62, 66], [55, 59, 62]], 104), # D A Bm G
}
_music_cache = {}
def music(kind, total):
    key = (kind, round(total, 2))
    if key in _music_cache:
        return _music_cache[key]
    chords, bpm = PROGS[kind]
    beat = 60 / bpm; eighth = beat / 2
    n = int(total * SR); out = np.zeros(n + SR * 2, dtype=np.float32)
    t = 0.0; bar = 0
    pattern = [0, 1, 2, 1, 0, 2, 1, 2]
    while t < total:
        ch = chords[bar % 4]
        bass = pluck_fast(NOTE(ch[0] - 24), beat * 4, 0.998) * 0.55
        s = int(t * SR); out[s:s + len(bass)] += bass[: len(out) - s]
        for k, pi in enumerate(pattern):
            note = ch[pi] + (12 if k in (2, 6) else 0)
            pl = pluck_fast(NOTE(note), eighth * 3, 0.995) * 0.32
            s = int((t + k * eighth) * SR)
            if s < len(out):
                out[s:s + len(pl)] += pl[: len(out) - s]
        t += beat * 4; bar += 1
    out = out[:n]
    out *= env(n, 0.4, 1.2)
    _music_cache[key] = out
    return out

def sine_sweep(f0, f1, dur, amp):
    n = int(dur * SR); f = np.linspace(f0, f1, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * amp * env(n, 0.003, dur * 0.8)).astype(np.float32)

def whoosh(dur=0.32, amp=0.10):
    n = int(dur * SR); rng = np.random.default_rng(7)
    x = rng.standard_normal(n).astype(np.float32)
    # filtro pasa-banda simple con barrido: mezcla de promedio móvil variable
    y = np.convolve(x, np.ones(6) / 6, mode="same") - np.convolve(x, np.ones(40) / 40, mode="same")
    shape = np.sin(np.linspace(0, np.pi, n)) ** 2
    return (y * shape * amp * 2).astype(np.float32)

def pop(amp=0.22):
    return sine_sweep(700, 280, 0.09, amp)

def ding(amp=0.16):
    n = int(0.9 * SR); t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * 1318.5 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t) + 0.25 * np.sin(2 * np.pi * 3955 * t)) * np.exp(-t * 5)
    return (y * amp).astype(np.float32)

def thump(freq=90, amp=0.45, dur=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    f = freq * (1 + 1.5 * np.exp(-t * 30))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    return (y * amp).astype(np.float32)

def tick(amp=0.25):
    n = int(0.06 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1600 * t) * np.exp(-t * 80) * amp).astype(np.float32)

def boing(amp=0.18):
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 300 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * amp).astype(np.float32)

def mix_at(track, clip, t):
    s = int(t * SR)
    if s >= len(track):
        return
    e = min(len(track), s + len(clip))
    track[s:e] += clip[: e - s]

# ───── expresiones y reparto ─────
def actor_kinds(guion):
    kinds = []
    for line in guion:
        sp = line.split(":")[0]
        k = VOICES.get(sp, (None, 0, 1, None))[3]
        if k and k != "moni" and k not in kinds:
            kinds.append(k)
    return kinds[:2]

def expressions(i, n_lines, speaker, text, kinds, panel_big):
    """Devuelve dict tipo->expresión para la escena i."""
    ex = {}
    spk_kind = VOICES[speaker][3]
    villain_speaking = spk_kind and spk_kind not in FRIENDLY
    last = i == n_lines - 1
    has_num = bool(re.search(r"\d", panel_big or ""))
    # Moni
    if speaker == "Moni":
        if "¡" in text and (i == 0 or has_num or "!" in text[-3:]):
            m = "shock" if (i == 0 or has_num) else "happy"
        elif "?" in text:
            m = "think"
        elif last:
            m = "wave"
        else:
            m = "happy"
        if any(w in text.lower() for w in ("se terminó", "no se queda", "afuera", "cancelado", "corré", "trampa")):
            m = "angry"
    elif villain_speaking:
        m = "worried" if i > 0 else "think"
    else:  # narrador u otro amable
        m = "shock" if has_num else "think"
    ex["moni"] = m
    for k in kinds:
        if spk_kind == k:
            ex[k] = "sly" if k not in FRIENDLY else "happy"
            if "¡" in text and k in FRIENDLY:
                ex[k] = "shock"
        else:
            if last and speaker == "Moni":
                ex[k] = "worried"
            elif has_num and speaker != k:
                ex[k] = "worried" if k not in FRIENDLY else "shock"
            else:
                ex[k] = "happy" if k in FRIENDLY else "sly"
    return ex

def parse_panel(s):
    if not s:
        return None
    big, _, small = s.partition("|")
    return {"big": big.strip(), "small": small.strip()}

def mito_parts(short):
    g = short["gancho"]
    frase = re.search(r"la frase “(.+?)”", g).group(1)
    verdict = short["guion"][2].split(":", 1)[1].strip().strip("¡!")
    verdict = verdict.split(".")[0].upper()
    return frase, verdict

def build(short):
    n = short["n"]; fmt = short["fmt"]; guion = short["guion"]
    kinds = actor_kinds(guion)
    pantalla = PANTALLA.get(n, [""] * len(guion))
    assert len(pantalla) == len(guion), (n, len(pantalla), len(guion))
    lead, gap, tail = 0.12, 0.32, 1.3
    t = lead; scenes = []; voice_clips = []
    for i, line in enumerate(guion):
        speaker, text = [x.strip() for x in line.split(":", 1)]
        clip = tts(text, speaker)
        ad = len(clip) / SR
        dur = ad + gap
        if fmt == "mito" and i == 1:
            dur = max(dur, 3.3)
        panel = parse_panel(pantalla[i]) if fmt != "mito" else None
        scenes.append(dict(start=round(t, 3), dur=round(dur, 3), audio=round(ad, 3), speaker=speaker,
                           kind=VOICES[speaker][3], text=text, panel=panel,
                           ex=expressions(i, len(guion), speaker, text, kinds, panel and panel["big"])))
        voice_clips.append((t, clip))
        t += dur
    scenes[-1]["dur"] = round(scenes[-1]["dur"] + tail, 3)
    total = round(t + tail, 3)

    track = np.zeros(int((total + 0.5) * SR), dtype=np.float32)
    for st, clip in voice_clips:
        mix_at(track, clip * 0.95, st)
    # efectos
    if fmt == "novela":
        mix_at(track, thump(98, 0.5), 0.0); mix_at(track, thump(82, 0.45), 0.42)
    for i, sc in enumerate(scenes):
        if i > 0:
            mix_at(track, whoosh(), sc["start"] - 0.12)
        if sc["panel"]:
            mix_at(track, pop(), sc["start"] + 0.08)
            if re.search(r"\$?\d", sc["panel"]["big"]) and re.search(r"\d{2,}", sc["panel"]["big"].replace(".", "")):
                mix_at(track, ding(), sc["start"] + 1.0)
    if fmt == "mito":
        s1 = scenes[1]
        for k in range(3):
            mix_at(track, tick(), s1["start"] + k * s1["dur"] / 3)
        mix_at(track, thump(70, 0.5), scenes[2]["start"]); mix_at(track, ding(0.14), scenes[2]["start"] + 0.05)
    if fmt == "sitcom" and len(scenes) > 3:
        mix_at(track, boing(), scenes[3]["start"] + 0.6)
    mkind = {"novela": "minor", "simulador": "bright"}.get(fmt, "major")
    m = music(mkind, len(track) / SR)
    if len(m) < len(track):
        m = np.pad(m, (0, len(track) - len(m)))
    track += m[: len(track)] * (0.16 if fmt != "pizarra" else 0.13)
    peak = np.max(np.abs(track))
    if peak > 0.98:
        track *= 0.98 / peak
    sf.write(os.path.join(OUT, "audio", f"{n:03d}.wav"), track, SR, subtype="PCM_16")

    tl = dict(n=n, fmt=fmt, serie=short["serie"], titulo=short["titulo"], total=total, kinds=kinds, scenes=scenes,
              cierre=short["cierre"])
    if fmt == "mito":
        tl["frase"], tl["verdict"] = mito_parts(short)
    json.dump(tl, open(os.path.join(OUT, "timeline", f"{n:03d}.json"), "w"), ensure_ascii=False, indent=1)
    return total

if __name__ == "__main__":
    data = json.load(open(os.path.join(ROOT, "shorts.json"), encoding="utf-8"))
    want = set(int(a) for a in sys.argv[1:])
    for s in data["shorts"]:
        if want and s["n"] not in want:
            continue
        tot = build(s)
        print(f"{s['n']:03d} {tot:5.1f}s {s['titulo']}", flush=True)
