// Renderiza los shorts a MP4 1080x1920 30 fps con el audio generado por build_audio.py.
// Uso: node render.js [--workers 4] [--frames-only 1,2.5] [n1 n2 ...]
const {chromium} = require('playwright');
const {spawn} = require('child_process');
const fs = require('fs'), path = require('path');

const HERE = __dirname, OUT = path.join(HERE, 'out');
const FPS = 30;
const args = process.argv.slice(2);
let workers = 4, stills = null; const nums = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--workers') workers = +args[++i];
  else if (args[i] === '--stills') stills = args[++i].split(',').map(Number);
  else nums.push(+args[i]);
}
const all = fs.readdirSync(path.join(OUT, 'timeline')).filter(f => f.endsWith('.json')).map(f => +f.slice(0, 3)).sort((a, b) => a - b);
const queue = (nums.length ? nums : all).filter(n => all.includes(n));
fs.mkdirSync(path.join(OUT, 'mp4'), {recursive: true});
fs.mkdirSync(path.join(OUT, 'stills'), {recursive: true});

async function renderOne(page, n) {
  const tl = JSON.parse(fs.readFileSync(path.join(OUT, 'timeline', `${String(n).padStart(3, '0')}.json`), 'utf8'));
  await page.evaluate(t => window.setup(t), tl);
  if (stills) {
    for (const t of stills) {
      await page.evaluate(t => window.frame(t), t);
      await page.screenshot({path: path.join(OUT, 'stills', `${String(n).padStart(3, '0')}_${t}.jpg`), type: 'jpeg', quality: 80});
    }
    return;
  }
  const frames = Math.ceil(tl.total * FPS);
  const file = path.join(OUT, 'mp4', `${String(n).padStart(3, '0')}.mp4`);
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', path.join(OUT, 'audio', `${String(n).padStart(3, '0')}.wav`),
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', String(FPS),
    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-shortest', '-movflags', '+faststart', file]);
  let ffErr = ''; ff.stderr.on('data', d => ffErr += d);
  const done = new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error(`ffmpeg ${n}: ${ffErr}`))));
  for (let f = 0; f < frames; f++) {
    await page.evaluate(t => window.frame(t), f / FPS);
    const buf = await page.screenshot({type: 'jpeg', quality: 93});
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await done;
}

(async () => {
  const browser = await chromium.launch();
  const t0 = Date.now(); let doneCount = 0;
  const work = async (w) => {
    const page = await browser.newPage({viewport: {width: 1080, height: 1920}, deviceScaleFactor: 1});
    page.on('pageerror', e => console.error('pageerror', e.message));
    await page.goto('file://' + path.join(HERE, 'renderer.html'));
    await page.evaluate(() => document.fonts.ready);
    while (queue.length) {
      const n = queue.shift();
      const s = Date.now();
      try { await renderOne(page, n); doneCount++; console.log(`[w${w}] ${n} ok ${((Date.now() - s) / 1000).toFixed(0)}s (total ${doneCount}, ${((Date.now() - t0) / 60000).toFixed(1)} min)`); }
      catch (e) { console.error(`[w${w}] ${n} FAILED`, e.message); }
    }
    await page.close();
  };
  await Promise.all(Array.from({length: workers}, (_, i) => work(i)));
  await browser.close();
})();
