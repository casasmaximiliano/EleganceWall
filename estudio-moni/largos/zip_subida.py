"""Arma out/Moni_videos_largos_subida.zip: descripción completa, .srt y miniatura por video + resumen.csv."""
import json, os, csv, zipfile
plan = json.load(open('largos.json', encoding='utf-8'))
os.makedirs('out/entrega', exist_ok=True)
rows = []
z = zipfile.ZipFile('out/Moni_videos_largos_subida.zip', 'w', zipfile.ZIP_DEFLATED)
for v in plan:
    n = f"{v['n']:02d}"
    tl = json.load(open(f'out/timeline/{n}.json', encoding='utf-8'))
    dur = tl['total']; mm = f"{int(dur//60)}:{int(dur%60):02d}"
    txt = (f"VIDEO {n} · {v['dia']} {v['fecha']} · {v['hora_ar']} (hora Argentina)\n\nTÍTULO:\n{v['titulo']}\n\n"
           f"TÍTULO ALTERNATIVO (Probar y comparar):\n{v['alt']}\n\nDESCRIPCIÓN:\n{tl['descripcion']}\n\n"
           f"ETIQUETAS:\n{v['tags']}\n\nLISTA DE REPRODUCCIÓN: {v['playlist']}\nDURACIÓN: {mm}\n"
           "SHORTS PARA VINCULAR (Video relacionado): " + ", ".join(f"#{s['n']} {s['titulo']}" for s in v['shorts_rel']) + "\n")
    z.writestr(f"{n}/descripcion.txt", txt)
    z.write(f'out/srt/{n}.srt', f"{n}/subtitulos_{n}.srt")
    z.write(f'miniaturas/miniatura_{n}.png', f"{n}/miniatura_{n}.png")
    rows.append([n, v['fecha'], v['dia'], v['hora_ar'], v['titulo'], mm, f"{n}.mp4"])
with open('out/entrega/resumen.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f); w.writerow(['N°', 'Fecha', 'Día', 'Hora AR', 'Título', 'Duración', 'Archivo']); w.writerows(rows)
z.write('out/entrega/resumen.csv', 'resumen.csv')
z.close()
print(os.path.getsize('out/Moni_videos_largos_subida.zip') // 1024, 'KB')
