// Render 3D de un video largo (o un tramo) con el audio de build_long.py.
// Uso: node render3d.js NN [--desde 0] [--hasta 147] [--workers 3] [--stills 3,40,90] [--out archivo.mp4]
const {chromium} = require('playwright'); const {spawn} = require('child_process');
const fs = require('fs'), path = require('path');
const HERE = __dirname, LARGOS = path.join(HERE, '..', 'largos', 'out');
const FPS = 24;
const a = process.argv.slice(2); const n = +a[0]; const opt = k => { const i = a.indexOf('--' + k); return i >= 0 ? a[i + 1] : null };
const pad = v => String(v).padStart(2, '0');
const tl = JSON.parse(fs.readFileSync(path.join(LARGOS, 'timeline', `${pad(n)}.json`), 'utf8'));
const spec = require(path.join(HERE, 'planos', `${n}.js`));
const t0 = +(opt('desde') || 0), t1 = +(opt('hasta') || tl.total), workers = +(opt('workers') || 3);
const stills = opt('stills') ? opt('stills').split(',').map(Number) : null;
const outFile = opt('out') ? path.resolve(opt('out')) : path.join(LARGOS, 'mp4_3d', `${pad(n)}${t0 || t1 < tl.total ? `_${Math.round(t0)}-${Math.round(t1)}` : ''}.mp4`);

// planos absolutos a partir del guion de planos
const shots = [];
tl.scenes.forEach((s, i) => {
  const list = spec[i]; if (!list) return;
  let prev = s.start; list.forEach(([f, sh]) => { const end = s.start + s.dur * f; shots.push(Object.assign({start: prev, end}, sh)); prev = end });
});
if (!shots.length) throw new Error('sin planos');
const lines = tl.scenes.filter(s => s.type === 'line').map(s => ({start: s.start, dur: s.dur, audio: s.audio, kind: s.kind, text: s.text, ex: s.ex}));
const data = {tl: {scenes: tl.scenes.map(s => s.type === 'line' ? Object.assign({}, s, {cast: undefined}) : s)}, shots};

async function page(browser) {
  const p = await browser.newPage({viewport: {width: 1920, height: 1080}});
  p.on('pageerror', e => console.error('pageerror', e.message));
  await p.goto('file://' + path.join(HERE, 'page.html')); await p.evaluate(d => window.setup3d(d), data);
  return p;
}
function enc(file, withAudio, from, dur) {
  const args = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-'];
  if (withAudio) args.push('-ss', String(from), '-t', String(dur), '-i', path.join(LARGOS, 'audio', `${pad(n)}.wav`));
  args.push('-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p');
  if (withAudio) args.push('-c:a', 'aac', '-b:a', '192k', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-shortest');
  args.push(file); return spawn('ffmpeg', args, {stdio: ['pipe', 'inherit', 'inherit']});
}
(async () => {
  const browser = await chromium.launch({args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
  if (stills) {
    const p = await page(browser); fs.mkdirSync(path.join(LARGOS, 'stills3d'), {recursive: true});
    for (const t of stills) { await p.evaluate(t => window.frame3d(t), t); await p.screenshot({path: path.join(LARGOS, 'stills3d', `${pad(n)}_${t}.jpg`), type: 'jpeg', quality: 88}) }
    await browser.close(); console.log('stills ok'); return;
  }
  fs.mkdirSync(path.dirname(outFile), {recursive: true});
  const total = Math.round((t1 - t0) * FPS), per = Math.ceil(total / workers), t00 = Date.now(); const parts = [];
  await Promise.all(Array.from({length: workers}, async (_, w) => {
    const f0 = w * per, f1 = Math.min(total, f0 + per); if (f0 >= f1) return;
    const part = outFile.replace('.mp4', `.part${w}.mp4`); parts[w] = part;
    const p = await page(browser); const ff = enc(part, false); const done = new Promise(r => ff.on('close', r));
    for (let f = f0; f < f1; f++) {
      await p.evaluate(t => window.frame3d(t), t0 + f / FPS);
      const buf = await p.screenshot({type: 'jpeg', quality: 90}); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if ((f - f0) % (FPS * 10) === 0) console.log(`[w${w}] ${((f - f0) / FPS).toFixed(0)}s de ${((f1 - f0) / FPS).toFixed(0)}s · ${((Date.now() - t00) / 60000).toFixed(1)} min`);
    }
    ff.stdin.end(); await done; await p.close();
  }));
  await browser.close();
  const list = outFile.replace('.mp4', '.txt'); fs.writeFileSync(list, parts.filter(Boolean).map(f => `file '${f}'`).join('\n'));
  await new Promise(r => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-i', path.join(LARGOS, 'audio', `${pad(n)}.wav`),
    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-af', `atrim=${t0}:${t1},asetpts=PTS-STARTPTS,loudnorm=I=-14:TP=-1.5:LRA=11`, '-shortest', outFile], {stdio: 'inherit'}).on('close', r));
  if (!fs.existsSync(outFile) || fs.statSync(outFile).size < 1000) { console.error('ERROR: no se pudo unir; quedan las partes en', path.dirname(outFile)); process.exit(1) }
  parts.filter(Boolean).forEach(f => fs.unlinkSync(f)); fs.unlinkSync(list);
  console.log(`listo ${outFile} en ${((Date.now() - t00) / 60000).toFixed(1)} min`);
})();
