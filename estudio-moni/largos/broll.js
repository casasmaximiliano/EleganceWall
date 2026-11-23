// B-roll animado para videos largos (se inyecta DESPUÉS de motion.js; necesita d3-array, d3-geo, topojson-client y window.__WORLD).
// Agrega, según lo que se dice:
//  · Mapas: al nombrar un país, mapamundi que hace zoom al país con un pin.
//  · Gráficos: “sube / crece / se duplica” → línea verde que sube; “cae / baja / quiebra” → línea roja que se desploma.
//  · Dona de porcentaje cuando el panel muestra un %.
//  · Línea de tiempo arriba cuando se menciona un año.
//  · Lista que se va tildando con los paneles numerados (“1 · …”, “2 · …”) del capítulo.
//  · Objetos que cruzan la pantalla (auto, avión, barco, colectivo, carretilla).
//  · Cameos: personajes secundarios que aparecen cuando se los nombra (vía motion.js).
(function () {
const CSS = `
#Lbr{position:absolute;inset:0;pointer-events:none;z-index:8}
.wdg{position:absolute;display:none;background:#FFFDF6;border-radius:28px;box-shadow:0 16px 0 rgba(0,0,0,.22);overflow:hidden;border:6px solid #F7BC2B}
.wdg h4{position:absolute;left:0;right:0;bottom:8px;margin:0;text-align:center;font:800 26px "Bricolage Grotesque";color:#14221D;text-transform:uppercase;letter-spacing:.02em}
.wdg svg{position:absolute;left:0;top:0}
#Ltl{position:absolute;left:560px;width:800px;top:40px;height:56px;display:none}
#Ltl .bar{position:absolute;left:30px;right:30px;top:26px;height:6px;border-radius:3px;background:rgba(255,255,255,.35)}
#L.b-pizarra #Ltl .bar,#L.b-sitcom #Ltl .bar{background:rgba(0,0,0,.18)}
#Ltl .tick{position:absolute;top:18px;width:4px;height:22px;background:rgba(255,255,255,.55);border-radius:2px}
#Ltl .tick.on{background:#F7BC2B}
#Ltl .mk{position:absolute;top:-6px;transform:translateX(-50%);font:800 26px "Figtree";color:#14221D;background:#F7BC2B;padding:2px 12px;border-radius:999px;white-space:nowrap}
#Lck{position:absolute;left:44px;top:118px;width:400px;display:none;background:rgba(255,253,246,.94);border-radius:22px;padding:14px 18px;box-shadow:0 10px 0 rgba(0,0,0,.18)}
#Lck div{font:800 24px/1.25 "Figtree";color:#14221D;padding:6px 0 6px 44px;position:relative;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#Lck div::before{content:"";position:absolute;left:4px;top:7px;width:26px;height:26px;border-radius:8px;border:3px solid #0E5A40}
#Lck div.done::after{content:"✓";position:absolute;left:8px;top:1px;font:900 28px "Figtree";color:#17865A}
#Lck div.cur{color:#0E5A40}
#Lcross{position:absolute;font:400 150px/1 "Noto Color Emoji",sans-serif;display:none;z-index:9;filter:drop-shadow(0 10px 6px rgba(0,0,0,.25))}
`;
const st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = x => 1 - Math.pow(1 - clamp(x), 3);
const back = x => { x = clamp(x); const c = 1.9; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2) };
const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
const rnd = s => { const x = Math.sin(s * 91.7 + 17.3) * 43758.5453; return x - Math.floor(x) };

const COUNTRIES = [
 [/\bargentin/, '032', 'Argentina'], [/\bzimbabu/, '716', 'Zimbabue'], [/\balemani/, '276', 'Alemania'],
 [/\bholand|paises bajos|amsterdam|haarlem/, '528', 'Holanda'], [/estados unidos|nueva york|florida|dallas|texas|miami|boston|california|oregon|manhattan/, '840', 'Estados Unidos'],
 [/reino unido|inglaterra|londres|escoces/, '826', 'Reino Unido'], [/\bbahamas/, '044', 'Bahamas'], [/\bvenezuel/, '862', 'Venezuela'],
 [/\bbrasil/, '076', 'Brasil'], [/\bperu\b/, '604', 'Perú'], [/\bbolivi/, '068', 'Bolivia'], [/\bmexic/, '484', 'México'],
 [/\bespana/, '724', 'España'], [/\bcolombi/, '170', 'Colombia'], [/imperio otomano|turquia/, '792', 'Turquía'], [/\bchile\b/, '152', 'Chile'], [/\buruguay/, '858', 'Uruguay'],
];
const UP = /\b(se dispar|dispararon|se duplica|se duplico|se multiplic|multiplicaron|subieron|subio|crecio|crecieron|crece mas|creciendo|se acelera)/;
const DOWN = /\b(se desplom|desplomaron|derrumb|cayeron|cayo|quebro|se hundio|perdieron todo|perdio todo|perdio la mitad)/;
const CROSS = [[/\bauto(s)?\b/, '🚗'], [/\bavion/, '✈️'], [/\bbarco/, '🚢'], [/\bcolectivo/, '🚌'], [/carretilla/, '🛒'], [/\bcamion/, '🚚'], [/\bmoto\b/, '🛵']];
const CAMEO = [[/tarjeta/, 'card', 'Tarjetín'], [/inflacion/, 'ghost', 'Infla'], [/prestamo/, 'bill', 'Préstamín'], [/\bcafe\b|cafecito/, 'cup', 'Cafecito'],
 [/delivery/, 'bag', 'Delivy'], [/\boferta|descuento/, 'tag', 'Ofertín'], [/cripto|fomo|bitcoin/, 'fomito', 'Fomito'], [/suscripcion/, 'zombi', 'Zombi'],
 [/merezco|capricho|impulso/, 'bow', 'Capricho'], [/supermercado|\bsuper\b|carrito/, 'cart', 'Carrito'], [/\bprimo\b/, 'centavito', 'Centavito'],
 [/\bpareja\b/, 'peso', 'Peso'], [/\bauto\b|\bautos\b/, 'car', 'Autito'], [/celular/, 'phone', 'Celulín'], [/cajero/, 'atm', 'Cajero']];
const WDG_DUR = 4.2, TL_DUR = 4.5, CROSS_DUR = 1.7;
let B = {};
// zona del widget según el armado de la escena
function wdgBox(s) {
  const n = s.cast ? s.cast.length : 1;
  if (n === 1 && s.panel) return [880, 100, 380, 290];      // arriba a la derecha del panel
  if (n === 1) return [140, 110, 380, 290];                  // a la izquierda, Moni al centro
  return [800, 92, 320, 245];                                // centro arriba, más chico para no tapar el panel
}
const origSetup = window.setupLong, origFrame = window.frameLong;
window.setupLong = function (tl) {
  const r = origSetup(tl);
  const cam = document.getElementById('Lcam'); const L = document.getElementById('L');
  const br = document.createElement('div'); br.id = 'Lbr';
  br.innerHTML = `<div class="wdg" id="Lw"><svg id="Lwsvg" viewBox="0 0 380 290" preserveAspectRatio="xMidYMid meet" style="width:100%;height:100%"></svg><h4 id="Lwt"></h4></div>
    <div id="Ltl"><div class="bar"></div><div class="mk" id="Ltlm"></div></div><div id="Lck"></div><div id="Lcross"></div>`;
  cam.appendChild(br);
  // mapa
  if (window.__WORLD && !B.geo) { B.geo = topojson.feature(window.__WORLD, window.__WORLD.objects.countries); B.byId = {}; B.geo.features.forEach(f => B.byId[f.id] = f) }
  B.w = []; B.years = []; B.cross = []; B.lists = []; const mot = window.__MOTION;
  let lastW = -10, lastCross = -10; const usedCountry = {}; let lastCameo = {};
  const lines = tl.scenes.map((s, i) => [s, i]).filter(([s]) => s.type === 'line');
  lines.forEach(([s, idx]) => {
    const tx = norm(s.text); const words = s.text.split(' '); const n = words.length;
    const at = re => { const m = tx.match(re); if (!m) return null; const pre = tx.slice(0, m.index).split(' ').length - 1; return s.start + clamp(pre / n) * s.audio };
    // mapas (un país no se repite en 40 s)
    for (const [re, id, name] of COUNTRIES) { const t = at(re); if (t !== null && (!usedCountry[id] || t - usedCountry[id] > 40) && t - lastW > WDG_DUR + 0.5 && B.byId && B.byId[id]) { B.w.push({t, type: 'map', id, name, scene: idx}); usedCountry[id] = t; lastW = t; break } }
    // gráficos
    if (t0Free(lastW, s)) {
      const tu = at(UP), td = /cayo del cielo|cae del cielo/.test(tx) ? null : at(DOWN);
      if (tu !== null && (td === null || tu < td) && tu - lastW > WDG_DUR + 2) { B.w.push({t: tu, type: 'up', scene: idx}); lastW = tu }
      else if (td !== null && td - lastW > WDG_DUR + 2) { B.w.push({t: td, type: 'down', scene: idx}); lastW = td }
    }
    // dona de porcentaje
    if (s.panel && s.panel.new) { const m = s.panel.big.match(/(\d+(?:,\d+)?)\s?%/); if (m) { const v = parseFloat(m[1].replace(',', '.')); if (v > 0 && v <= 100 && s.start - lastW > WDG_DUR + 0.5) { B.w.push({t: s.start + 0.3, type: 'pct', v, scene: idx}); lastW = s.start + 0.3 } } }
    // años
    (s.text.match(/\b(1[5-9]\d\d|20\d\d)\b/g) || []).forEach(y => { const t = at(new RegExp(y)); if (t !== null) B.years.push({t, y: +y}) });
    // objetos que cruzan
    for (const [re, emo] of CROSS) { const t = at(re); if (t !== null && t - lastCross > 6) { B.cross.push({t, emo, dir: rnd(idx) > .5 ? 1 : -1}); lastCross = t; break } }
    // cameos (solo si el personaje no está en escena)
    if (mot) for (const [re, kind, name] of CAMEO) { const t = at(re); if (t !== null && !(s.cast || []).includes(kind) && (!lastCameo[kind] || t - lastCameo[kind] > 45)) { mot.events.push({t: t + 0.05, kind, label: name, scene: idx}); lastCameo[kind] = t; break } }
  });
  if (mot) mot.events.sort((a, b) => a.t - b.t);
  B.yr = B.years.length ? [Math.min(...B.years.map(y => y.y)), Math.max(...B.years.map(y => y.y))] : null;
  // listas: por capítulo, paneles que empiezan con número
  let cur = null;
  tl.scenes.forEach((s, idx) => {
    if (s.type === 'card') { cur = {start: s.start, items: [], end: null}; B.lists.push(cur); return }
    if (s.type === 'line' && cur && s.panel && s.panel.new) { const m = s.panel.big.match(/^(\d+)\s*·\s*(.+)$/); if (m) cur.items.push({t: s.start, text: m[2]}) }
    if (cur) cur.end = s.start + s.dur;
  });
  B.lists = B.lists.filter(l => l.items.length >= 2);
  function t0Free() { return true }
  window.__BROLL = B;
  return r;
};
window.__brollBusy = function (t) {
  const out = [];
  const w = B.w && B.w.find(e => t >= e.t && t < e.t + WDG_DUR);
  if (w) { const sc = window.__TL.scenes[w.scene]; const [x, y, ww, hh] = wdgBox(sc); out.push({x0: x, y0: y, x1: x + ww, y1: y + hh}) }
  const l = B.lists && B.lists.find(l => t >= l.items[0].t && t < l.end);
  if (l && !(w && wdgBox(window.__TL.scenes[w.scene])[0] < 500)) out.push({x0: 44, y0: 118, x1: 444, y1: 118 + 40 + 44 * l.items.filter(it => it.t <= t).length});
  return out.length ? out : null;
};
function mapSvg(ev, k) {
  const f = B.byId[ev.id]; const W = 380, H = 240;
  const p0 = d3.geoEquirectangular().fitSize([W, H], B.geo), p1 = d3.geoEquirectangular().fitExtent([[70, 45], [W - 70, H - 35]], f);
  const cen = d3.geoCentroid(f); const c0 = p0(cen), c1 = p1(cen);
  const sc = Math.exp(Math.log(p0.scale()) + (Math.log(p1.scale()) - Math.log(p0.scale())) * k);
  const unit = d3.geoEquirectangular().scale(1).translate([0, 0])(cen);
  const proj = d3.geoEquirectangular().scale(sc).translate([c0[0] + (c1[0] - c0[0]) * k - sc * unit[0], c0[1] + (c1[1] - c0[1]) * k - sc * unit[1]]);
  const path = d3.geoPath(proj);
  let out = `<rect width="${W}" height="${H + 50}" fill="#CDEBF5"/>`;
  B.geo.features.forEach(g => { const d = path(g); if (d) out += `<path d="${d}" fill="${g.id === ev.id ? '#F7BC2B' : '#9ED3B4'}" stroke="#FFFDF6" stroke-width="${0.6 + k}"/>` });
  const c = proj(cen); if (k > 0.7) out += `<text x="${c[0]}" y="${c[1] - 4 - Math.abs(Math.sin(k * 9)) * 8}" text-anchor="middle" font-size="46" style="font-family:'Noto Color Emoji'">📍</text>`;
  return out;
}
function chartSvg(ev, k) {
  const W = 380, H = 240; const up = ev.type === 'up'; const n = 14; let pts = [];
  for (let i = 0; i < n; i++) { const x = 30 + i * (W - 60) / (n - 1); const base = up ? Math.pow(i / (n - 1), 1.8) : 1 - Math.pow(i / (n - 1), 2.2) * 0.95; const noise = (rnd(i * 3.1 + (up ? 1 : 2)) - 0.5) * 0.12; pts.push([x, H - 30 - clamp(base + noise, 0.02, 1) * (H - 70)]) }
  const d = pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' ');
  const col = up ? '#17865A' : '#D23A4E'; const last = pts[Math.min(n - 1, Math.floor(k * (n - 1)))];
  let g = ''; for (let i = 1; i < 4; i++) g += `<line x1="30" x2="${W - 30}" y1="${H - 30 - i * (H - 70) / 4}" y2="${H - 30 - i * (H - 70) / 4}" stroke="#E3E9EC" stroke-width="2"/>`;
  return `<rect width="${W}" height="${H + 50}" fill="#FFFDF6"/>${g}<path d="${d}" fill="none" stroke="${col}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${1 - k}"/>
    <circle cx="${last[0]}" cy="${last[1]}" r="12" fill="${col}"/><text x="${W - 40}" y="58" font-size="54" text-anchor="middle" style="font-family:'Noto Color Emoji'">${up ? '📈' : '📉'}</text>`;
}
function pctSvg(ev, k) {
  const W = 380, H = 240, r = 80, cx = W / 2, cy = 120, c = 2 * Math.PI * r; const v = ev.v * ease(k);
  return `<rect width="${W}" height="${H + 50}" fill="#FFFDF6"/><circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#E3E9EC" stroke-width="34"/>
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#F7BC2B" stroke-width="34" stroke-dasharray="${c * v / 100} ${c}" transform="rotate(-90 ${cx} ${cy})"/>
    <text x="${cx}" y="${cy + 16}" text-anchor="middle" style="font:800 46px 'Bricolage Grotesque'" fill="#14221D">${v.toFixed(ev.v % 1 ? 1 : 0).replace('.', ',')} %</text>`;
}
window.frameLong = function (t) {
  const i = origFrame(t);
  const s = window.__TL.scenes[i]; const W = document.getElementById('Lw'); if (!W) return i;
  // widget (mapa / gráfico / dona)
  const ev = s.type === 'line' && B.w.find(e => t >= e.t && t < e.t + WDG_DUR);
  if (ev) {
    const [x, y, ww, hh] = wdgBox(window.__TL.scenes[ev.scene]); const et = t - ev.t; const inK = back(et / 0.4), outK = clamp((WDG_DUR - et) / 0.35);
    Object.assign(W.style, {display: 'block', left: x + 'px', top: y + 'px', width: ww + 'px', height: hh + 'px', opacity: outK, transform: `scale(${(0.3 + 0.7 * inK) * (0.7 + 0.3 * outK)}) rotate(${(rnd(B.w.indexOf(ev)) - .5) * 6}deg)`});
    const k = ease((et - 0.25) / (ev.type === 'map' ? 1.1 : 1.3));
    const svg = document.getElementById('Lwsvg');
    if (W.dataset.ev !== String(B.w.indexOf(ev)) || k < 1 || !W.dataset.done) {
      svg.innerHTML = ev.type === 'map' ? mapSvg(ev, k) : ev.type === 'pct' ? pctSvg(ev, k) : chartSvg(ev, k);
      W.dataset.ev = String(B.w.indexOf(ev)); W.dataset.done = k >= 1 ? '1' : '';
    }
    document.getElementById('Lwt').textContent = ev.type === 'map' ? ev.name : ev.type === 'up' ? 'Sube' : ev.type === 'down' ? 'Cae' : 'Porcentaje';
  } else W.style.display = 'none';
  // línea de tiempo
  const T = document.getElementById('Ltl'); const yev = B.years.filter(y => t >= y.t && t < y.t + TL_DUR).pop();
  if (yev && B.yr && s.type === 'line') {
    const [a, b] = B.yr; const span = Math.max(1, b - a); const pos = y => 30 + (b === a ? 0.5 : (y - a) / span) * 740;
    if (T.dataset.built !== '1') { T.querySelectorAll('.tick').forEach(e => e.remove()); [...new Set(B.years.map(v => v.y))].forEach(y => { const d = document.createElement('div'); d.className = 'tick'; d.dataset.y = y; d.style.left = pos(y) + 'px'; T.appendChild(d) }); T.dataset.built = '1' }
    T.querySelectorAll('.tick').forEach(d => d.classList.toggle('on', B.years.some(v => v.y == d.dataset.y && v.t <= t)));
    const prev = B.years.filter(v => v.t < yev.t).pop(); const from = prev ? pos(prev.y) : pos(yev.y); const k = ease((t - yev.t) / 0.6);
    const M = document.getElementById('Ltlm'); M.textContent = yev.y; M.style.left = (from + (pos(yev.y) - from) * k) + 'px';
    T.style.display = 'block'; T.style.opacity = Math.min(clamp((t - yev.t) / 0.25), clamp((yev.t + TL_DUR - t) / 0.4));
  } else T.style.display = 'none';
  // lista que se va tildando
  const C = document.getElementById('Lck'); const lst = B.lists.find(l => t >= l.items[0].t && t < l.end);
  const wNow = s.type === 'line' && B.w.find(e => t >= e.t && t < e.t + WDG_DUR); const wLeft = wNow && wdgBox(window.__TL.scenes[wNow.scene])[0] < 500;
  if (lst && s.type === 'line' && !wLeft) {
    const vis = lst.items.filter(it => it.t <= t); const curIdx = vis.length - 1;
    C.innerHTML = vis.map((it, k) => `<div class="${k < curIdx ? 'done' : 'cur'}">${it.text}</div>`).join('');
    const last = C.lastElementChild; if (last) { const lk = back((t - vis[curIdx].t) / 0.35); last.style.transform = `translateX(${(1 - lk) * -60}px)`; last.style.opacity = clamp((t - vis[curIdx].t) / 0.2) }
    C.style.display = 'block'; C.style.opacity = clamp((lst.end - t) / 0.4);
  } else C.style.display = 'none';
  // objetos que cruzan
  const X = document.getElementById('Lcross'); const cr = B.cross.find(c => t >= c.t && t < c.t + CROSS_DUR);
  if (cr && s.type === 'line') { const k = (t - cr.t) / CROSS_DUR; const x = cr.dir > 0 ? -200 + k * 2320 : 2120 - k * 2320;
    X.textContent = cr.emo; Object.assign(X.style, {display: 'block', left: x + 'px', top: (700 + Math.sin(k * 30) * 6) + 'px', transform: `scaleX(${cr.dir > 0 ? -1 : 1})`}) } else X.style.display = 'none';
  return i;
};
})();
