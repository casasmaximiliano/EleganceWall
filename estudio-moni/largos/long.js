// Capa de video largo (1920x1080). Se inyecta sobre video/renderer.html, que aporta charSVG() y los estilos de personajes.
(function () {
const CSS = `
html,body{width:1920px!important;height:1080px!important;overflow:hidden!important;background:#000!important}
#stage{display:none!important}
#L{position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:hidden;font-family:"Figtree",sans-serif}
#L .bg{position:absolute;inset:0}
#L.b-novela .bg{background:radial-gradient(ellipse 70% 60% at 50% 45%,#7B2A73 0,#3A0F3E 50%,#14051A 100%)}
#L.b-pizarra .bg{background:#FBFBF6;background-image:linear-gradient(#E3E9EC 2px,transparent 2px),linear-gradient(90deg,#E3E9EC 2px,transparent 2px);background-size:80px 80px}
#L.b-sitcom .bg{background:linear-gradient(#F4C98E 0 66%,#B9784A 66% 100%)}
#L.b-simulador .bg{background:#0A241D;background-image:linear-gradient(rgba(126,255,196,.07) 2px,transparent 2px),linear-gradient(90deg,rgba(126,255,196,.07) 2px,transparent 2px);background-size:90px 90px}
#L.b-mito .bg{background:linear-gradient(115deg,#C7243A 0 49.7%,#0F8A57 50.3% 100%)}
#L.b-marca .bg{background:radial-gradient(circle at 50% 40%,#1C8C62 0,#0E5A40 55%,#083626 100%)}
#L .deco{position:absolute;inset:0}
#L .sit{display:none}#L.b-sitcom .sit{display:block}
#L .win{position:absolute;left:1180px;top:110px;width:380px;height:300px;background:linear-gradient(#9FD8F2,#D9F1FA);border:22px solid #FFF4E2}
#L .frm{position:absolute;left:300px;top:150px;width:240px;height:170px;background:#5C8C7A;border:18px solid #6B3F22}
#L .couch{position:absolute;left:-40px;right:-40px;top:660px;height:200px;background:#5E7FB8;border-radius:60px 60px 0 0;box-shadow:inset 0 -40px 0 #4A68A0}
#L .badge{position:absolute;left:48px;top:40px;font:800 26px "Figtree";letter-spacing:.12em;text-transform:uppercase;padding:10px 22px;border-radius:12px;background:rgba(0,0,0,.25);color:#fff}
#L.b-pizarra .badge,#L.b-sitcom .badge{background:rgba(255,255,255,.75);color:#14221D}
#L .wm{position:absolute;right:48px;top:44px;font:800 26px "Figtree";color:rgba(255,255,255,.85);display:flex;align-items:center;gap:10px}
#L .wm i{width:34px;height:34px;border-radius:50%;background:#F7BC2B;border:4px solid #fff}
#L.b-pizarra .wm,#L.b-sitcom .wm{color:rgba(20,34,29,.7)}
#L .chapbar{position:absolute;left:48px;right:48px;top:14px;height:8px;display:flex;gap:6px}
#L .chapbar i{flex:1;background:rgba(255,255,255,.25);border-radius:4px;overflow:hidden;position:relative}
#L.b-pizarra .chapbar i,#L.b-sitcom .chapbar i{background:rgba(0,0,0,.12)}
#L .chapbar i b{position:absolute;inset:0;width:0;background:#F7BC2B}
#L .panel{position:absolute;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:14px;transform-origin:50% 50%}
#L .panel .big{font:800 132px/1 "Bricolage Grotesque";letter-spacing:-.03em;color:#FFD43B;text-shadow:0 0 60px rgba(255,212,59,.35)}
#L .panel .big.mid{font-size:100px}#L .panel .big.long{font-size:76px;line-height:1.05}
#L .panel .small{font:700 42px/1.2 "Figtree";color:#F2F7F4}
#L.b-pizarra .panel .big{font-family:"Patrick Hand";font-weight:400;color:#1b1b1b;text-shadow:none}
#L.b-pizarra .panel .small{font-family:"Patrick Hand";font-weight:400;font-size:54px;color:#1E8A52}
#L.b-sitcom .panel{background:#FFF4E2;border-radius:40px;box-shadow:0 14px 0 rgba(58,29,8,.25)}
#L.b-sitcom .panel .big{color:#C8102E;text-shadow:none}#L.b-sitcom .panel .small{color:#3A1D08}
#L.b-simulador .panel .big{color:#7EFFC4;text-shadow:0 0 60px rgba(126,255,196,.5)}
#L.b-mito .panel{background:#fff;border-radius:40px;box-shadow:0 18px 0 rgba(0,0,0,.25)}
#L.b-mito .panel .big{color:#1b1b1b;text-shadow:none}#L.b-mito .panel .small{color:#444}
#L .cap{position:absolute;left:160px;right:160px;top:878px;text-align:center;font:800 54px/1.15 "Bricolage Grotesque";color:#fff;paint-order:stroke;-webkit-text-stroke:13px #000}
#L .cap .w{opacity:.5}#L .cap .w.lit{opacity:1}#L .cap .w.now{color:#FFD43B}
#L.b-pizarra .cap{-webkit-text-stroke:0;color:#1b1b1b;font:400 64px/1.1 "Patrick Hand"}
#L.b-pizarra .cap .w.now{color:#0F7A4E;background:#FFF07A}
#L .actor{position:absolute;transform-origin:50% 100%}
#L .card{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;gap:18px;background:#0E5A40;z-index:20}
#L .card small{font:800 34px "Figtree";letter-spacing:.2em;text-transform:uppercase;color:#F7BC2B}
#L .card h2{margin:0;font:800 110px/1.02 "Bricolage Grotesque";color:#fff;letter-spacing:-.03em;text-align:center;max-width:1500px;text-wrap:balance}
#L .card .cm{position:absolute;right:120px;bottom:60px;width:300px}
#L .outro{position:absolute;inset:0;display:none;background:radial-gradient(circle at 50% 40%,#1C8C62 0,#0E5A40 55%,#083626 100%);z-index:21}
#L .outro h2{position:absolute;left:0;right:0;top:70px;margin:0;text-align:center;font:800 72px "Bricolage Grotesque";color:#fff}
#L .outro .slot{position:absolute;top:300px;width:640px;height:360px;border-radius:24px;border:4px dashed rgba(255,255,255,.35)}
#L .outro .s1{left:140px}#L .outro .s2{left:1140px}
#L .outro .om{position:absolute;left:810px;top:330px;width:300px}
#L .outro p{position:absolute;left:0;right:0;bottom:70px;margin:0;text-align:center;font:700 34px "Figtree";color:#DDF3E8}
#L .disc{position:absolute;left:0;right:0;bottom:22px;text-align:center;font:600 24px "Figtree";color:rgba(255,255,255,.7)}
#L.b-pizarra .disc,#L.b-sitcom .disc{color:rgba(30,20,10,.6)}
`;
const st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
document.documentElement.dataset.look = 'soft';
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = x => 1 - Math.pow(1 - clamp(x), 3);
const back = x => { x = clamp(x); const c = 1.9; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2) };
const esc = t => String(t).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
const fmtNum = (v, d) => v.toLocaleString('es-AR', {minimumFractionDigits: d, maximumFractionDigits: d});
function numParts(big) {
  const m = big.match(/^(.*?)(\d[\d.]*(?:,\d+)?)(.*)$/); if (!m) return null;
  const raw = m[2]; const dec = (raw.split(',')[1] || '').length; const val = parseFloat(raw.replace(/\./g, '').replace(',', '.'));
  if (!(val >= 10) || /[×÷→=]/.test(big) || /\d.*\s.*\d/.test(big) || /^\d{4}$/.test(raw)) return null;
  return {pre: m[1], val, dec, post: m[3]};
}
// posiciones [left, width, top] según cantidad de personajes y si hay panel
function layout(n, hasPanel) {
  if (n === 1) return hasPanel ? [[1340, 470, 330]] : [[700, 520, 250]];
  if (n === 2) return [[90, 440, 380], [1390, 440, 380]];
  return [[40, 380, 430], [770, 380, 430], [1500, 380, 430]];
}
function panelBox(n, hasPanel) {
  if (n === 1) return [130, 1180, 170, 640];   // left, width, top, height
  return [560, 800, 140, 600];
}
let TL, S = {}, UID = 0;
const charU = k => { const u = '_' + (++UID); return charSVG(k).split('g-' + k + '"').join('g-' + k + u + '"').split('#g-' + k + ')').join('#g-' + k + u + ')') };
window.setupLong = function (tl) {
  TL = tl; S = {scene: -1, actors: {}};
  document.getElementById('L')?.remove();
  const L = document.createElement('div'); L.id = 'L';
  L.innerHTML = `<div class="bg"></div><div class="deco sit"><div class="win"></div><div class="frm"></div><div class="couch"></div></div>
    <div class="chapbar">${tl.chapters.map(() => '<i><b></b></i>').join('')}</div>
    <div class="badge">${esc(tl.badge)}</div><div class="wm"><i></i>@moni.finanzas</div>
    <div class="panel" id="Lp"></div><div id="La"></div><div class="cap" id="Lc"></div>
    <div class="disc" id="Ld">Contenido educativo. No es asesoramiento financiero.</div>
    <div class="card" id="Lk"><small id="Lkn"></small><h2 id="Lkt"></h2><div class="cm actor ex-happy" data-k="moni"></div></div>
    <div class="outro" id="Lo"><h2>¿Seguimos?</h2><div class="slot s1"></div><div class="slot s2"></div>
      <div class="om actor ex-happy ex-wave" data-k="moni"></div><p>Suscribite a Moni Finanzas · un short cada día y videos largos miércoles y domingos</p></div>`;
  document.body.appendChild(L);
  L.querySelectorAll('.actor[data-k]').forEach(a => a.innerHTML = charU(a.dataset.k));
  const kinds = [...new Set(tl.scenes.filter(s => s.cast).flatMap(s => s.cast))];
  kinds.forEach(k => { const el = document.createElement('div'); el.className = 'actor'; el.innerHTML = charU(k); el.style.display = 'none'; document.getElementById('La').appendChild(el); S.actors[k] = {el, pos: null}; });
  return document.fonts.ready.then(() => true);
};
function sceneAt(t) { const sc = TL.scenes; for (let i = 0; i < sc.length; i++) if (t < sc[i].start + sc[i].dur) return i; return sc.length - 1 }
window.frameLong = function (t) {
  const L = document.getElementById('L'); const i = sceneAt(t); const s = TL.scenes[i]; const ts = t - s.start;
  // escena de contenido de referencia (para fondo durante placas)
  let ref = s; if (s.type !== 'line') { for (let k = i; k < TL.scenes.length; k++) if (TL.scenes[k].type === 'line') { ref = TL.scenes[k]; break } }
  if (s.type === 'outro') { for (let k = i; k >= 0; k--) if (TL.scenes[k].type === 'line') { ref = TL.scenes[k]; break } }
  L.className = 'b-' + (ref.bg || 'marca');
  // barra de capítulos
  const bars = L.querySelectorAll('.chapbar i b');
  TL.chapters.forEach((c, k) => { const end = k + 1 < TL.chapters.length ? TL.chapters[k + 1].t : TL.outro; bars[k].style.width = (clamp((t - c.t) / (end - c.t)) * 100) + '%' });
  // placa de capítulo
  const K = document.getElementById('Lk');
  if (s.type === 'card') {
    K.style.display = 'flex'; document.getElementById('Lkn').textContent = 'Capítulo ' + s.num; document.getElementById('Lkt').textContent = s.title;
    const a = clamp(ts / 0.35), b = clamp((s.dur - ts) / 0.3); K.style.opacity = Math.min(a, b);
    K.querySelector('h2').style.transform = `translateY(${(1 - ease(ts / 0.5)) * 40}px)`;
    const cm = K.querySelector('.cm'); cm.style.transform = `translateY(${Math.sin(t * 5) * 8}px)`;
  } else K.style.display = 'none';
  // pantalla final
  const O = document.getElementById('Lo');
  if (s.type === 'outro') { O.style.display = 'block'; O.style.opacity = clamp(ts / 0.5); O.querySelector('.om').style.transform = `translateY(${Math.sin(t * 4) * 10}px)`;
    const arm = O.querySelector('.arm-r'); if (arm) arm.style.transform = `rotate(${Math.sin(t * 11) * 16 + 4}deg)` } else O.style.display = 'none';
  document.getElementById('Ld').style.opacity = (t < 12 || s.type === 'outro') ? 1 : 0;
  if (s.type !== 'line') { document.getElementById('Lc').innerHTML = ''; return i }
  // cambio de escena
  if (i !== S.scene) {
    const P = document.getElementById('Lp');
    const n = s.cast.length; const hasPanel = !!s.panel;
    if (s.panel) { const b = s.panel.big; const cls = b.length > 16 ? 'long' : (b.length > 9 ? 'mid' : '');
      P.innerHTML = `<div class="big ${cls}">${esc(b)}</div>${s.panel.small ? `<div class="small">${esc(s.panel.small)}</div>` : ''}`;
      const [l, w, tp, h] = panelBox(n, hasPanel); Object.assign(P.style, {left: l + 'px', width: w + 'px', top: tp + 'px', height: h + 'px', display: 'flex'});
      S.num = s.panel.new ? numParts(b) : null; S.panelStart = s.panel.new ? s.start : (S.panelStart ?? s.start);
    } else { P.style.display = 'none'; S.num = null }
    const C = document.getElementById('Lc'); C.style.fontSize = s.text.length > 150 ? (L.className === 'b-pizarra' ? '54px' : '46px') : '';
    C.innerHTML = s.text.split(' ').map(w => `<span class="w">${esc(w)}</span>`).join(' '); S.words = [...C.querySelectorAll('.w')];
    const pos = layout(n, hasPanel);
    Object.entries(S.actors).forEach(([k, a]) => { const idx = s.cast.indexOf(k);
      if (idx < 0) { a.el.style.display = 'none'; a.pos = null; return }
      a.from = a.pos || [pos[idx][0] + (pos[idx][0] > 900 ? 500 : -500), pos[idx][1], pos[idx][2]]; a.to = pos[idx]; a.el.style.display = 'block' });
    S.scene = i;
  }
  const P = document.getElementById('Lp');
  if (s.panel) { const pt = t - S.panelStart; const k = back((pt - 0.05) / 0.38); P.style.transform = `scale(${0.4 + 0.6 * k})`; P.style.opacity = clamp(pt / 0.12);
    if (S.num) { const big = P.querySelector('.big'); const e = ease((pt - 0.1) / 0.9); big.textContent = S.num.pre + fmtNum(S.num.val * e, e < 1 ? 0 : S.num.dec) + S.num.post } }
  const prog = clamp(ts / Math.max(.3, s.audio)); const nl = Math.ceil(prog * S.words.length);
  S.words.forEach((w, k) => { w.classList.toggle('lit', k < nl); w.classList.toggle('now', k === nl - 1 && prog < 1) });
  Object.entries(S.actors).forEach(([k, a], ai) => {
    if (a.el.style.display === 'none') return;
    const e = ease(ts / 0.5); const p = a.to.map((v, j) => a.from[j] + (v - a.from[j]) * e); if (e >= 1) a.pos = a.to; else a.pos = p;
    const talking = s.kind === k && ts < s.audio; const ex = (s.ex && s.ex[k]) || 'happy';
    const cls = ex === 'wave' ? 'ex-happy ex-wave' : 'ex-' + ex; if (a.el.dataset.ex !== cls) { a.el.className = 'actor ' + cls; a.el.dataset.ex = cls }
    const bob = Math.sin((t + ai) * Math.PI * 2 * (talking ? 2.2 : .38)) * (talking ? 12 : 7);
    const sh = ex === 'shock' && ts < .6 ? Math.sin(ts * 70) * 9 * (1 - ts / .6) : 0;
    const rot = talking ? Math.sin(t * Math.PI * 2 * 1.6) * 2 : 0;
    Object.assign(a.el.style, {left: p[0] + 'px', width: p[1] + 'px', top: p[2] + 'px', transform: `translate(${sh}px,${bob}px) rotate(${rot}deg) scale(${talking ? 1.04 : 1})`, zIndex: talking ? 3 : 2});
    const m = a.el.querySelector('.mouth'); if (m) m.style.transform = `scaleY(${talking ? (0.25 + 0.85 * Math.abs(Math.sin(t * Math.PI * 2 * 3.3 + Math.sin(t * 7) * 1.2))).toFixed(3) : 1})`;
    const eye = a.el.querySelector('.eye'); if (eye) eye.style.transform = `scaleY(${((t + ai * 1.37) % 3.6) < .12 ? .1 : 1})`;
    const arm = a.el.querySelector('.arm-r'); if (arm) arm.style.transform = ex === 'wave' ? `rotate(${Math.sin(t * Math.PI * 2 * 1.8) * 16 + 4}deg)` : 'none';
  });
  return i;
};
})();
