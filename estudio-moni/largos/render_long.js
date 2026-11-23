// Renderiza los videos largos a MP4 1920x1080 24 fps.
// Uso: node render_long.js [--workers 4] [--stills 5,60,120] [n ...]
const {chromium} = require('playwright');
const {spawn} = require('child_process');
const fs = require('fs'), path = require('path');
const HERE = __dirname, OUT = path.join(HERE, 'out');
const FPS = 24;
const args = process.argv.slice(2); let workers = 4, stills = null; const nums = [];
for (let i = 0; i < args.length; i++) { if (['--watch','--desc','--no-motion','--out-motion'].includes(args[i])) {} else if (args[i] === '--workers') workers = +args[++i]; else if (args[i] === '--stills') stills = args[++i].split(',').map(Number); else nums.push(+args[i]) }
const all = fs.readdirSync(path.join(OUT, 'timeline')).filter(f => f.endsWith('.json')).map(f => +f.slice(0, 2)).sort((a, b) => a - b);
let watch = args.includes('--watch');
const queue = watch ? [] : (nums.length ? nums : all).filter(n => all.includes(n));
const claimed = new Set();
function nextReady() {
  const order = args.includes('--desc') ? [...Array(24).keys()].map(i => 24 - i) : [...Array(24).keys()].map(i => i + 1);
  for (const n of order) {
    if (claimed.has(n)) continue;
    if (fs.existsSync(path.join(OUT, 'ready', pad(n))) && !fs.existsSync(path.join(OUT, 'mp4', `${pad(n)}.mp4`))) { claimed.add(n); return n }
  }
  return null;
}
fs.mkdirSync(path.join(OUT, 'mp4'), {recursive: true}); fs.mkdirSync(path.join(OUT, 'stills'), {recursive: true});
const pad = n => String(n).padStart(2, '0');

async function renderOne(page, n) {
  const tl = JSON.parse(fs.readFileSync(path.join(OUT, 'timeline', `${pad(n)}.json`), 'utf8'));
  await page.evaluate(t => window.setupLong(t), tl);
  if (stills) { for (const t of stills) { await page.evaluate(t => window.frameLong(t), t); await page.screenshot({path: path.join(OUT, 'stills', `${pad(n)}_${t}.jpg`), type: 'jpeg', quality: 80}) } return }
  const frames = Math.ceil(tl.total * FPS);
  const file = path.join(OUT, args.includes('--out-motion') ? 'mp4_motion' : 'mp4', `${pad(n)}.mp4`);
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', path.join(OUT, 'audio', `${pad(n)}.wav`), '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-pix_fmt', 'yuv420p', '-r', String(FPS),
    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-shortest', '-movflags', '+faststart', file]);
  let err = ''; ff.stderr.on('data', d => err += d);
  const done = new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error(err))));
  for (let f = 0; f < frames; f++) {
    await page.evaluate(t => window.frameLong(t), f / FPS);
    const buf = await page.screenshot({type: 'jpeg', quality: 90});
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % (FPS * 60) === 0 && f) console.log(`  ${pad(n)}: ${Math.round(f / FPS / 60)} min de ${(tl.total / 60).toFixed(1)}`);
  }
  ff.stdin.end(); await done;
}
(async () => {
  const browser = await chromium.launch(); const t0 = Date.now(); let ok = 0;
  await Promise.all(Array.from({length: workers}, async (_, w) => {
    const page = await browser.newPage({viewport: {width: 1920, height: 1080}});
    page.on('pageerror', e => console.error('pageerror', e.message));
    await page.goto('file://' + path.join(HERE, '..', 'video', 'renderer.html'));
    await page.addScriptTag({path: path.join(HERE, 'long.js')});
    if (!args.includes('--no-motion')) await page.addScriptTag({path: path.join(HERE, 'motion.js')});
    await page.evaluate(() => document.fonts.ready);
    while (true) {
      let n = watch ? nextReady() : queue.shift();
      if (watch && n === null) { const done = [...Array(24).keys()].every(i => fs.existsSync(path.join(OUT, 'mp4', `${pad(i + 1)}.mp4`)) || claimed.has(i + 1));
        if (done && claimed.size >= 24) break; await new Promise(r => setTimeout(r, 20000)); continue }
      if (n === undefined) break;
      const s = Date.now();
      try { await renderOne(page, n); ok++; console.log(`[w${w}] video ${n} ok en ${((Date.now() - s) / 60000).toFixed(1)} min (listos ${ok}, ${((Date.now() - t0) / 60000).toFixed(0)} min)`) }
      catch (e) { console.error(`[w${w}] video ${n} FAILED`, e.message) } }
    await page.close();
  }));
  await browser.close();
})();
