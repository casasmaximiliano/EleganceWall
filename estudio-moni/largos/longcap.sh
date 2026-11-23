#!/bin/bash
# Extrae del MP4 el fotograma con el subtítulo más largo, para revisar que entre.
N=$(printf "%02d" "$1"); D="$(dirname "$0")/out"
T=$(python3 -c "
import json;tl=json.load(open('$D/timeline/$N.json'));s=max([x for x in tl['scenes'] if x.get('type')=='line'],key=lambda x:len(x['text']));print(round(s['start']+s['audio']*0.7,2))")
ffmpeg -loglevel error -y -ss $T -i "$D/${MP4DIR:-mp4}/$N.mp4" -frames:v 1 -vf scale=960:-1 "$D/check/${N}_cap.jpg" && echo "$D/check/${N}_cap.jpg"
