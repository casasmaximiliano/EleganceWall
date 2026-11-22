// Genera las miniaturas 1280x720 de los videos largos con los personajes del canal.
const {chromium} = require('playwright');
const path = require('path'), fs = require('fs');
const OUT = path.join(__dirname, 'miniaturas'); fs.mkdirSync(OUT, {recursive: true});
const V = JSON.parse(fs.readFileSync(path.join(__dirname, 'largos.json'), 'utf8'));
const only = process.argv.slice(2).map(Number);

const CSS = `
html,body{width:1280px!important;height:720px!important;overflow:hidden!important;background:#000!important}
#stage{display:none}
#t{position:absolute;inset:0;overflow:hidden;font-family:"Bricolage Grotesque",sans-serif}
#t .rays{position:absolute;inset:-200px;background:repeating-conic-gradient(from 0deg at 72% 55%,rgba(255,255,255,.07) 0 8deg,transparent 8deg 18deg)}
#t .glow{position:absolute;left:560px;top:80px;width:760px;height:760px;border-radius:50%;background:radial-gradient(circle,rgba(255,240,180,.45),transparent 65%)}
#t .txt{position:absolute;left:44px;top:0;bottom:0;width:640px;display:flex;flex-direction:column;justify-content:center;gap:4px}
#t .txt span{display:block;font:800 104px/0.98 "Bricolage Grotesque",sans-serif;color:#fff;letter-spacing:-.03em;
  paint-order:stroke;-webkit-text-stroke:16px #000;text-transform:uppercase}
#t .txt span.hl{color:#FFD43B}
#t .txt.s span{font-size:88px}
#t .txt.xs span{font-size:76px}
#t .actor{position:absolute;transform-origin:50% 100%}
#t .prop{position:absolute;font-size:190px;line-height:1;filter:drop-shadow(0 10px 10px rgba(0,0,0,.35))}
#t .logo{position:absolute;right:28px;bottom:22px;width:64px;height:64px;border-radius:50%;background:#0E5A40;border:4px solid #F7BC2B;overflow:hidden}
`;
function lines(t) {
  const w = t.split(' '); const out = []; let cur = '';
  for (const x of w) { if ((cur + ' ' + x).trim().length > 11 && cur) { out.push(cur); cur = x } else cur = (cur + ' ' + x).trim() }
  if (cur) out.push(cur); return out;
}
function html(v) {
  const th = v.thumb; const L = lines(th.texto); const longest = Math.max(...L.map(s => s.length));
  const size = longest > 11 || L.length > 3 ? 'xs' : (longest > 9 ? 's' : '');
  const hlIdx = L.length - 1;
  const chars = th.chars;
  let actors = '';
  if (chars.length === 1) actors = `<div class="actor ex-${chars[0][1]}" data-k="${chars[0][0]}" style="left:700px;top:90px;width:520px"></div>`;
  else actors = `<div class="actor ex-${chars[1][1]}" data-k="${chars[1][0]}" style="left:930px;top:200px;width:360px"></div>
                 <div class="actor ex-${chars[0][1]}" data-k="${chars[0][0]}" style="left:640px;top:130px;width:430px"></div>`;
  const prop = th.prop ? `<div class="prop" style="left:${chars.length === 1 ? 1050 : 1060}px;top:${chars.length === 1 ? 40 : 30}px">${th.prop}</div>` : '';
  return `<div id="t" style="background:linear-gradient(135deg,${th.fondo} 0%,${th.fondo} 45%,#000 140%)">
    <div class="rays"></div><div class="glow"></div>${actors}${prop}
    <div class="txt ${size}">${L.map((s, i) => `<span class="${i === hlIdx ? 'hl' : ''}">${s}</span>`).join('')}</div></div>`;
}
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 1280, height: 720}});
  await p.goto('file://' + path.join(__dirname, '..', 'video', 'renderer.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.addStyleTag({content: CSS});
  await p.evaluate(() => { document.documentElement.dataset.look = 'soft' });
  for (const v of V) {
    if (only.length && !only.includes(v.n)) continue;
    await p.evaluate(h => {
      document.getElementById('t')?.remove();
      const d = document.createElement('div'); d.innerHTML = h; document.body.appendChild(d.firstElementChild);
      document.querySelectorAll('#t .actor').forEach(a => { a.innerHTML = charSVG(a.dataset.k) });
    }, html(v));
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({path: path.join(OUT, v.thumb_file), clip: {x: 0, y: 0, width: 1280, height: 720}});
  }
  await b.close();
  console.log('ok');
})();
