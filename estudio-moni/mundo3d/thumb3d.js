// Miniaturas 1280x720 en el mundo 3D: una escena con los personajes y el texto grande encima.
// Uso: node thumb3d.js 21   → largos/miniaturas/miniatura_21_3D_A.png, _B, _C
const {chromium} = require('playwright');
const path = require('path'), fs = require('fs');
const OUT = path.join(__dirname, '..', 'largos', 'miniaturas');
const n = +process.argv[2];

// Por video: variantes con lugar, elenco, gestos, cámara y texto (la última línea va en amarillo).
const CAFE = {moni: 'mesaA', cup: 'mesaB'};
const CAM_MONI = {p: [.7, 3.7, 7.7], look: [-3.9, 3.0, 3.5], fov: 34}, CAM_CUP = {p: [-.7, 3.7, 7.7], look: [.9, 3.0, 1.7], fov: 34};
const T = {
  21: [
    {loc: 'cafeteria', cast: CAFE, ex: {moni: 'shock', cup: 'shock'}, gesture: {moni: 'shock', cup: 'shock'},
      cam: CAM_MONI, txt: ['CAFÉ =', '$173.000'], side: 'left'},
    {loc: 'cafeteria', cast: CAFE, ex: {moni: 'think', cup: 'happy'}, gesture: {moni: 'think'},
      cam: CAM_MONI, txt: ['¿TU CAFÉ', 'VALE UNA', 'CASA?'], side: 'left'},
    {loc: 'cafeteria', cast: CAFE, ex: {cup: 'shock', moni: 'happy'}, gesture: {cup: 'shock'}, cam: CAM_CUP,
      txt: ['$3 →', '$173.238'], side: 'left'},
  ],
};

const CSS = `#ov{display:none!important}
#th{position:fixed;inset:0;z-index:20;pointer-events:none;font-family:"Bricolage Grotesque","Figtree",sans-serif}
#th .shade{position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,.25) 42%,transparent 60%)}
#th .txt{position:absolute;left:70px;top:0;bottom:0;width:1000px;display:flex;flex-direction:column;justify-content:center}
#th .txt span{display:block;font:800 220px/.95 "Bricolage Grotesque",sans-serif;color:#fff;letter-spacing:-.03em;paint-order:stroke;-webkit-text-stroke:26px #000;text-transform:uppercase}
#th .txt span.hl{color:#FFD43B}
#th .txt.s span{font-size:176px}
#th .logo{position:absolute;right:40px;bottom:34px;width:96px;height:96px;border-radius:50%;background:#0E5A40;border:6px solid #F7BC2B}`;

(async () => {
  const vs = T[n]; if (!vs) throw new Error('sin miniaturas 3D para ' + n);
  const browser = await chromium.launch({args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
  const p = await browser.newPage({viewport: {width: 1920, height: 1080}});
  p.on('pageerror', e => console.error('pageerror', e.message));
  await p.goto('file://' + path.join(__dirname, 'page.html'));
  for (let i = 0; i < vs.length; i++) {
    const v = vs[i], letter = 'ABC'[i];
    const kind = Object.keys(v.cast)[0];
    const tl = {scenes: [{type: 'line', start: 0, dur: 9, audio: .01, kind, text: '.', ex: v.ex}]};
    const shot = {start: 0, end: 9, loc: v.loc, cast: v.cast, gesture: v.gesture, push: 0, cam: v.closeOf ? 'close:' + v.closeOf : '_th', camOpt: v.camOpt};
    await p.evaluate(({tl, shot, cam}) => { if (!window._ready) { window._ready = true } return window.setup3d({tl, shots: [shot]}).then(() => { if (cam) M3.lugar(shot.loc).cams._th = cam }) }, {tl, shot, cam: v.cam || null});
    await p.evaluate(() => window.frame3d(2.2));
    const longest = Math.max(...v.txt.map(s => s.length));
    await p.evaluate(({css, txt, small}) => {
      let st = document.getElementById('thcss'); if (!st) { st = document.createElement('style'); st.id = 'thcss'; document.head.appendChild(st) } st.textContent = css;
      let d = document.getElementById('th'); if (!d) { d = document.createElement('div'); d.id = 'th'; document.body.appendChild(d) }
      d.innerHTML = `<div class="shade"></div><div class="txt ${small ? 's' : ''}">${txt.map((s, i) => `<span class="${i === txt.length - 1 ? 'hl' : ''}">${s}</span>`).join('')}</div>`;
      return document.fonts.ready;
    }, {css: CSS, txt: v.txt, small: longest > 8});
    // si hubo un setup previo, quitar el canvas viejo
    await p.evaluate(() => { const cs = document.querySelectorAll('canvas'); for (let k = 0; k < cs.length - 1; k++) cs[k].remove() });
    const big = path.join(OUT, `miniatura_${String(n).padStart(2, '0')}_3D_${letter}.png`);
    await p.screenshot({path: big});
    console.log('ok', big);
  }
  await browser.close();
})();
