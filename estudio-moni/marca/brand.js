// Genera logo, banner y portadas de destacados reutilizando los personajes del renderizador.
// Uso: node brand.js   → PNGs en ./out
const {chromium} = require('playwright');
const path = require('path'), fs = require('fs');
const OUT = path.join(__dirname, 'out'); fs.mkdirSync(OUT, {recursive: true});
const RENDERER = 'file://' + path.join(__dirname, '..', 'video', 'renderer.html');

const BASE = `
html,body{width:auto!important;height:auto!important;overflow:visible!important;background:transparent!important}
#stage{display:none}
.asset{position:relative;overflow:hidden;font-family:"Figtree",system-ui,sans-serif}
.asset .actor{position:absolute}
.coin{position:absolute;border-radius:50%;background:radial-gradient(circle at 35% 30%,#FFF0A8,#F7BC2B 55%,#B87400);box-shadow:inset 0 0 0 6px rgba(156,100,0,.35)}
.coin::after{content:"$";position:absolute;inset:0;display:grid;place-items:center;font:800 1em "Bricolage Grotesque",sans-serif;color:rgba(122,82,0,.6)}
`;
const GREEN_BG = 'radial-gradient(circle at 50% 38%,#1C8C62 0,#0E5A40 55%,#083626 100%)';

function actor(kind, ex, left, top, width, extra = '') {
  return `<div class="actor ex-${ex} ${extra}" style="left:${left}px;top:${top}px;width:${width}px" data-kind="${kind}"></div>`;
}
function coins(list) {
  return list.map(([x, y, s, o = 1, r = 0]) => `<div class="coin" style="left:${x}px;top:${y}px;width:${s}px;height:${s}px;font-size:${s * 0.42}px;opacity:${o};transform:rotate(${r}deg)"></div>`).join('');
}

const ASSETS = {
  // Foto de perfil: se recorta en círculo en las tres redes
  'logo_800.png': {w: 800, h: 800, html: `
    <div class="asset" style="width:800px;height:800px;background:${GREEN_BG}">
      <div style="position:absolute;inset:22px;border-radius:50%;border:16px solid #F7BC2B"></div>
      ${actor('moni', 'happy', 25, 50, 750)}
    </div>`},
  // Banner de YouTube: 2560x1440, zona segura central 1546x423
  'banner_youtube_2560x1440.png': {w: 2560, h: 1440, html: `
    <div class="asset" style="width:2560px;height:1440px;background:linear-gradient(180deg,#0E5A40 0%,#0B4733 100%)">
      <div style="position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 2px,transparent 2px),linear-gradient(90deg,rgba(255,255,255,.05) 2px,transparent 2px);background-size:80px 80px"></div>
      <svg style="position:absolute;left:0;top:0" width="2560" height="1440"><path d="M0 1180 C600 1150 900 1000 1300 900 S2100 520 2560 300" fill="none" stroke="rgba(247,188,43,.25)" stroke-width="16" stroke-linecap="round"/></svg>
      ${coins([[140, 160, 120, .9, -12], [330, 1100, 90, .7, 20], [2280, 180, 140, .9, 15], [2120, 1150, 100, .7, -10], [560, 260, 60, .5], [1980, 330, 70, .5]])}
      ${actor('card', 'sly', 120, 420, 360)}
      ${actor('ghost', 'sly', 2090, 380, 330)}
      ${actor('cup', 'happy', 300, 860, 260)}
      ${actor('zombi', 'happy', 2220, 860, 240)}
      <!-- zona segura -->
      <div style="position:absolute;left:507px;top:508px;width:1546px;height:423px;display:flex;align-items:center;gap:56px">
        ${''}
        <div style="position:relative;width:330px;height:423px;flex:none"><div class="actor ex-happy ex-wave" data-kind="moni" style="left:0;top:-30px;width:330px"></div></div>
        <div style="display:grid;gap:14px;color:#fff">
          <div style="font:800 150px/0.95 'Bricolage Grotesque',sans-serif;letter-spacing:-.04em">Moni <span style="color:#F7BC2B">Finanzas</span></div>
          <div style="font:700 50px/1.2 'Figtree',sans-serif;color:#DDF3E8">Finanzas sin vueltas, en 30 segundos.</div>
          <div style="display:flex;gap:16px;margin-top:10px">
            <span style="font:800 34px 'Figtree',sans-serif;color:#0B3D2E;background:#F7BC2B;padding:10px 26px;border-radius:999px">Un short nuevo cada día</span>
            <span style="font:700 34px 'Figtree',sans-serif;color:#fff;border:3px solid rgba(255,255,255,.5);padding:8px 24px;border-radius:999px">@moni.finanzas</span>
          </div>
        </div>
      </div>
    </div>`},
  // Marca de agua de YouTube (150x150)
  'marca_de_agua_150.png': {w: 150, h: 150, html: `
    <div class="asset" style="width:150px;height:150px;border-radius:50%;background:${GREEN_BG}">${actor('moni', 'happy', 4, 8, 142)}</div>`},
};
// Portadas de destacados de Instagram (1080x1920, el ícono va al centro)
const HL = [
  ['destacado_telenovela.png', 'card', 'sly', 'Telenovela', '#A23C8F'],
  ['destacado_pizarra.png', 'moni', 'happy', 'Pizarra', '#2C7FB8'],
  ['destacado_sitcom.png', 'cup', 'happy', 'Gastos hormiga', '#B9622A'],
  ['destacado_y_si.png', 'moni', 'shock', '¿Y si…?', '#14825A'],
  ['destacado_mito.png', 'moni', 'think', 'Mito o verdad', '#C53B4E'],
];
for (const [file, kind, ex, label, color] of HL) {
  ASSETS[file] = {w: 1080, h: 1920, html: `
    <div class="asset" style="width:1080px;height:1920px;background:${color}">
      <div style="position:absolute;left:190px;top:610px;width:700px;height:700px;border-radius:50%;background:#FFF7E0"></div>
      ${actor(kind, ex, 290, 650, 500)}
    </div>`};
}

(async () => {
  const b = await chromium.launch();
  for (const [file, a] of Object.entries(ASSETS)) {
    const p = await b.newPage({viewport: {width: a.w, height: a.h}, deviceScaleFactor: 1});
    await p.goto(RENDERER);
    await p.evaluate(() => document.fonts.ready);
    await p.evaluate(({css, html}) => {
      const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
      document.documentElement.dataset.look = 'soft';
      const wrap = document.createElement('div'); wrap.innerHTML = html; document.body.appendChild(wrap);
      wrap.querySelectorAll('.actor[data-kind]').forEach(el => {
        el.innerHTML = charSVG(el.dataset.kind);
        if (el.classList.contains('ex-wave')) el.querySelector('.arm-r').style.transform = 'rotate(10deg)';
      });
    }, {css: BASE, html: a.html});
    await p.evaluate(() => document.fonts.ready);
    await p.locator('.asset').first().screenshot({path: path.join(OUT, file), omitBackground: true});
    await p.close();
    console.log('ok', file);
  }
  await b.close();
})();
