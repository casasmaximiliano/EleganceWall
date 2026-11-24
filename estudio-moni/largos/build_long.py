"""Videos largos: lee los guiones (guiones/NN.txt), genera voz + música + efectos, la línea de tiempo,
los subtítulos .srt y la descripción con los capítulos reales.

Formato del guion:
  @tipo historia|guia|simulacion|telenovela
  ## Título de capítulo            -> placa de capítulo
  @bg novela|pizarra|sitcom|simulador|mito|marca
  @cast moni,card                   -> personajes en escena (izquierda a derecha)
  P: GRANDE | chico                 -> panel de texto (P: - lo borra)
  HABLANTE: texto  /  HABLANTE{expresión}: texto

Uso: python3 build_long.py [n ...]
"""
import json, os, re, sys
import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "video"))
import build_audio as A  # noqa: E402  (voces, música y efectos de los Shorts)

OUT = os.path.join(HERE, "out"); os.makedirs(os.path.join(OUT, "audio"), exist_ok=True)
os.makedirs(os.path.join(OUT, "timeline"), exist_ok=True); os.makedirs(os.path.join(OUT, "srt"), exist_ok=True)
SR = A.SR
SPEED = 0.84          # narración un poco más pausada que en los Shorts
GAP = 0.85            # silencio entre líneas
CARD = 2.6            # duración de la placa de capítulo
INTRO_PAD = 0.15
OUTRO = 20.0          # pantalla final de YouTube (5 a 20 s)

SPEAKERS = {k.upper(): k for k in A.VOICES}
EXPR = {"shock", "happy", "sly", "angry", "worried", "think", "wave"}
# Compañero de escena cuando Moni está sola (los datos de los Shorts: 2 personajes retienen más que Moni sola)
SIDEKICK = {2: "centavito", 4: "card", 5: "cup", 6: "centavito", 7: "centavito", 12: "centavito", 17: "bow",
            18: "ghost", 22: "centavito", 23: "ghost", 24: "peso", 25: "centavito"}
# Fondos de escena: el capítulo elige el ambiente según de qué se habla (para que no sea siempre el mismo living)
ROOMS = [("cocina", r"caf[eé]|cafecito|cocin|comida|heladera|delivery|almuerzo|cena|pizza"),
         ("super", r"s[uú]per|supermercado|g[oó]ndola|carrito|oferta|precio por kilo|compras?\b"),
         ("oficina", r"sueldo|trabaj|jef[ea]|oficina|aumento|cobr[oa]|empresa|negocio"),
         ("banco", r"banco|tarjeta|pr[eé]stamo|deuda|cuota|cr[eé]dito|inter[eé]s|tasa"),
         ("calle", r"\bauto|transporte|ciudad|alquil|vivienda|pa[ií]s|barrio"),
         ("parque", r"futuro|jubil|a[nñ]os|tiempo|plan\b|meta")]
ROOM_ORDER = ["living", "cocina", "oficina", "parque", "super", "calle", "banco"]

def pick_room(text, prev):
    low = text.lower(); best = None; score = 0
    for name, rx in ROOMS:
        k = len(re.findall(rx, low))
        if k > score and name != prev:
            best, score = name, k
    if best:
        return best
    return next(r for r in ROOM_ORDER if r != prev)

VILLAINS = {"card", "ghost", "bill", "tag", "zombi", "gymzombi", "bow", "fomito", "atm", "chips", "cuotin", "phone", "cart", "bag", "bottle", "car", "doc"}
KIND_OF = {k: v[3] for k, v in A.VOICES.items()}

def parse(path):
    meta = {"tipo": "guia"}; items = []
    bg = "marca"; cast = ["moni"]; panel = None
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#!"):
            continue
        if line.startswith("@tipo"):
            meta["tipo"] = line.split()[1]
        elif line.startswith("## "):
            items.append({"type": "card", "title": line[3:].strip(), "bg": bg})
            panel = None
        elif line.startswith("@bg"):
            bg = line.split()[1]
        elif line.startswith("@cast"):
            cast = [c.strip() for c in line.split(None, 1)[1].split(",")]
        elif line.startswith("P:"):
            body = line[2:].strip()
            if body == "-":
                panel = None
            else:
                big, _, small = body.partition("|")
                panel = {"big": big.strip(), "small": small.strip(), "new": True}
        else:
            m = re.match(r"^([A-ZÁÉÍÓÚÑ ]+)(\{(\w+)\})?:\s*(.+)$", line)
            if not m:
                raise ValueError(f"{path}: línea no reconocida: {line}")
            sp = SPEAKERS.get(m.group(1).strip())
            if not sp:
                raise ValueError(f"{path}: hablante desconocido {m.group(1)}")
            ex = m.group(3)
            if ex and ex not in EXPR:
                raise ValueError(f"{path}: expresión desconocida {ex}")
            items.append({"type": "line", "speaker": sp, "text": m.group(4).strip(), "ex": ex, "bg": bg,
                          "cast": list(cast), "panel": dict(panel) if panel else None})
            if panel:
                panel["new"] = False
    return meta, items

def expressions(it, nxt_is_card):
    sp = it["speaker"]; kind = KIND_OF[sp]; txt = it["text"]; ex = {}
    for c in it["cast"]:
        if c == kind:
            if it["ex"]:
                e = it["ex"]
            elif c == "moni":
                e = "think" if "?" in txt else ("shock" if (it["panel"] and re.search(r"\d", it["panel"]["big"]) and "¡" in txt) else "happy")
            else:
                e = "sly" if c in VILLAINS else "happy"
        else:
            if c == "moni":
                e = "worried" if kind in VILLAINS else ("shock" if it["panel"] and re.search(r"\$\d", it["panel"]["big"]) else "think" if kind is None else "happy")
            elif it.get("side") == c:
                pb = it["panel"]["big"] if it["panel"] else ""
                e = ("worried" if c in VILLAINS else "shock") if re.search(r"\d", pb) else ("think" if "?" in txt else ("sly" if c in VILLAINS else "happy"))
            else:
                e = "worried" if (kind == "moni" and it["ex"] in ("angry", "wave")) else ("sly" if c in VILLAINS else "happy")
        ex[c] = e
    return ex

def srt_time(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"

def build(n, plan):
    meta, items = parse(os.path.join(HERE, "guiones", f"{n:02d}.txt"))
    side = SIDEKICK.get(n, "centavito")
    for it in items:  # nunca Moni sola: suma un compañero que reacciona
        if it["type"] == "line" and it["cast"] == ["moni"]:
            it["cast"] = ["moni", side]; it["side"] = side
    # ambiente por capítulo para las escenas de living (sitcom) y de marca
    chap = []; cur = None
    for it in items:
        if it["type"] == "card":
            cur = []; chap.append(cur)
        elif cur is not None:
            cur.append(it)
    prev = None
    for group in chap:
        lines = [it for it in group if it["type"] == "line" and it["bg"] in ("sitcom", "marca")]
        if not lines:
            continue
        room = pick_room(" ".join(it["text"] for it in group if it["type"] == "line"), prev)
        for it in lines:
            it["bg"] = "sitcom"; it["room"] = room
        prev = room
    t = INTRO_PAD; scenes = []; clips = []; chapters = []; srt = []
    for i, it in enumerate(items):
        if it["type"] == "card":
            chapters.append({"t": round(t, 2), "title": it["title"]})
            if len(chapters) == 1 and not scenes:
                continue  # arranque en frío: el video empieza directo en la escena, sin placa

            scenes.append({"type": "card", "start": round(t, 3), "dur": CARD, "title": it["title"], "num": len(chapters), "bg": it["bg"]})
            t += CARD
            continue
        clip = A.tts(it["text"], it["speaker"], SPEED)
        ad = len(clip) / SR
        dur = ad + GAP
        scenes.append({"type": "line", "start": round(t, 3), "dur": round(dur, 3), "audio": round(ad, 3), "speaker": it["speaker"],
                       "kind": KIND_OF[it["speaker"]], "text": it["text"], "bg": it["bg"], "cast": it["cast"],
                       "panel": it["panel"], "ex": expressions(it, False), "room": it.get("room")})
        clips.append((t, clip))
        srt.append((t, t + ad, it["text"]))
        t += dur
    outro_start = t
    scenes.append({"type": "outro", "start": round(t, 3), "dur": OUTRO})
    total = round(t + OUTRO, 3)

    track = np.zeros(int((total + 0.5) * SR), dtype=np.float32)
    for st, c in clips:
        A.mix_at(track, c * 0.95, st)
    prev_panel = None
    for sc in scenes:
        if sc["type"] == "card":
            A.mix_at(track, A.whoosh(0.5, 0.14), max(0, sc["start"] - 0.1)); A.mix_at(track, A.thump(110, 0.25, 0.4), sc["start"] + 0.15)
        elif sc["type"] == "line" and sc["panel"] and sc["panel"].get("new"):
            A.mix_at(track, A.pop(0.16), sc["start"] + 0.05)
            if re.search(r"\d{2,}", sc["panel"]["big"].replace(".", "")):
                A.mix_at(track, A.ding(0.10), sc["start"] + 1.0)
    mkind = {"historia": "minor", "telenovela": "minor", "simulacion": "bright"}.get(meta["tipo"], "major")
    m = A.music(mkind, len(track) / SR)
    if len(m) < len(track):
        m = np.pad(m, (0, len(track) - len(m)))
    # música baja bajo la voz y más alta en placas y pantalla final
    gain = np.full(len(track), 0.075, dtype=np.float32)
    for sc in scenes:
        if sc["type"] in ("card", "outro"):
            a = int(sc["start"] * SR); b = int((sc["start"] + sc["dur"]) * SR)
            gain[a:b] = 0.16
    k = int(0.4 * SR); gain = np.convolve(gain, np.ones(k) / k, mode="same").astype(np.float32)
    track += m[: len(track)] * gain
    fade = int(2.0 * SR); track[-fade:] *= np.linspace(1, 0, fade)
    peak = np.max(np.abs(track))
    if peak > 0.98:
        track *= 0.98 / peak
    sf.write(os.path.join(OUT, "audio", f"{n:02d}.wav"), track, SR, subtype="PCM_16")

    with open(os.path.join(OUT, "srt", f"{n:02d}.srt"), "w", encoding="utf-8") as f:
        for i, (a, b, txt) in enumerate(srt, 1):
            f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n\n")
    def ts(x):
        x = int(x); return f"{x // 60:02d}:{x % 60:02d}"
    chap_txt = "\n".join(f"{'00:00' if i == 0 else ts(c['t'])} {c['title']}" for i, c in enumerate(chapters))
    v = next(x for x in plan if x["n"] == n)
    desc = (v["descripcion"].split("⏱️ Capítulos")[0] + "⏱️ Capítulos\n" + chap_txt + "\n\n" +
            "📺" + v["descripcion"].split("📺", 1)[1])
    tl = {"n": n, "tipo": meta["tipo"], "titulo": v["titulo"], "total": total, "outro": round(outro_start, 3), "scenes": scenes,
          "chapters": chapters, "descripcion": desc, "badge": {"historia": "Historias del dinero", "guia": "Guía de Moni",
          "simulacion": "Simulación de Moni", "telenovela": "Telenovela del dinero"}[meta["tipo"]]}
    json.dump(tl, open(os.path.join(OUT, "timeline", f"{n:02d}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    words = sum(len(s["text"].split()) for s in scenes if s["type"] == "line")
    return total, words, len(chapters)

if __name__ == "__main__":
    plan = json.load(open(os.path.join(HERE, "largos.json"), encoding="utf-8"))
    nums = [int(a) for a in sys.argv[1:]] or [i for i in range(1, 25) if os.path.exists(os.path.join(HERE, "guiones", f"{i:02d}.txt"))]
    for n in nums:
        tot, w, c = build(n, plan)
        os.makedirs(os.path.join(OUT, "ready"), exist_ok=True); open(os.path.join(OUT, "ready", f"{n:02d}"), "w").write("ok")
        print(f"{n:02d} {tot / 60:5.1f} min · {w} palabras · {c} capítulos", flush=True)
