#!/bin/bash
# Verifica un video largo renderizado: formato, duración, sonido y una hoja de fotogramas.
# Uso: bash verify.sh NN
set -e
N=$(printf "%02d" "$1")
D="$(dirname "$0")/out"
F="$D/mp4/$N.mp4"
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate -show_entries format=duration -of csv=p=0 "$F" | tr '\n' ' '
echo
ffmpeg -hide_banner -nostats -i "$F" -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1
ffmpeg -hide_banner -nostats -i "$F" -af silencedetect=n=-45dB:d=3 -f null - 2>&1 | grep -c silence_start | sed 's/^/silencios>3s: /'
echo "errores de decodificación: $(ffmpeg -v error -i "$F" -f null - 2>&1 | wc -l)"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$F")
mkdir -p "$D/check"
ffmpeg -loglevel error -y -i "$F" -vf "fps=8/$DUR,scale=480:-1,tile=4x2" -frames:v 1 "$D/check/$N.jpg"
echo "hoja: $D/check/$N.jpg"
