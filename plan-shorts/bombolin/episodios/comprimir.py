"""Deja un video listo para subir (URL pública en GitHub, máximo 100 MB) sin perder calidad, y la verifica.

- Si el original ya pesa menos del límite, se copia tal cual (sin recomprimir).
- Si no, se recomprime en H.265 (HEVC) a dos pasadas con la tasa justa para entrar en el límite. A igual peso,
  queda casi idéntico al original (SSIM ~0,98), mientras que la compresión vieja (H.264 rápido a ~950 kb/s) daba
  bloques visibles en las transiciones y en la carrera (SSIM ~0,85). YouTube y TikTok aceptan HEVC.
- Al final compara cuadro por cuadro con el original (SSIM) y avisa si algún segundo queda feo: si no pasa el
  control, NO se sube.

Uso: python3 comprimir.py ORIGINAL.mp4 SALIDA.mp4 [--max-mb 95]
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

MEAN_MIN = 0.96   # calidad promedio mínima
SEC_MIN = 0.90    # ningún segundo por debajo de esto


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)


def check(orig, out):
    """SSIM cuadro por cuadro; devuelve (promedio, peor segundo, lista de segundos malos)."""
    with tempfile.TemporaryDirectory() as td:
        st = os.path.join(td, "ssim.txt")
        subprocess.run(["ffmpeg", "-v", "error", "-i", out, "-i", orig, "-lavfi",
                        f"[0:v][1:v]ssim=stats_file={st}", "-f", "null", "-"], check=True)
        vals = [float(m.group(1)) for m in re.finditer(r"All:([0-9.]+)", open(st).read())]
    fps = len(vals) / max(1e-6, dur(orig))
    per = int(round(fps)) or 60
    secs = [sum(vals[i:i + per]) / len(vals[i:i + per]) for i in range(0, len(vals), per)]
    bad = [(k, round(v, 3)) for k, v in enumerate(secs) if v < SEC_MIN]
    return sum(vals) / len(vals), min(secs), bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("orig")
    ap.add_argument("out")
    ap.add_argument("--max-mb", type=float, default=95)
    a = ap.parse_args()
    size = os.path.getsize(a.orig) / 2 ** 20
    if size <= a.max_mb:
        shutil.copy(a.orig, a.out)
        print(f"OK sin recomprimir ({size:.1f} MB)")
        return
    d = dur(a.orig)
    vk = int(a.max_mb * 8 * 2 ** 20 / 1000 / d) - 140  # kb/s de video (deja lugar al audio de 128 kb/s)
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "x265")
        base = ["ffmpeg", "-v", "error", "-y", "-i", a.orig, "-c:v", "libx265", "-preset", "medium", "-b:v", f"{vk}k",
                "-pix_fmt", "yuv420p"]
        subprocess.run(base + ["-x265-params", f"pass=1:stats={log}:log-level=error", "-an", "-f", "null", "-"], check=True)
        subprocess.run(base + ["-x265-params", f"pass=2:stats={log}:log-level=error", "-tag:v", "hvc1",
                               "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", a.out], check=True)
    mb = os.path.getsize(a.out) / 2 ** 20
    mean, worst, bad = check(a.orig, a.out)
    print(f"{os.path.basename(a.out)}: {mb:.1f} MB, {vk} kb/s, SSIM promedio {mean:.3f}, peor segundo {worst:.3f}")
    if mb > 99.5 or mean < MEAN_MIN or bad:
        print("NO PASA EL CONTROL DE CALIDAD:", f"{mb:.1f} MB" if mb > 99.5 else "", bad[:20])
        sys.exit(1)
    print("OK calidad")


if __name__ == "__main__":
    main()
