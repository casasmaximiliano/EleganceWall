// Director del mundo 3D (navegador): arma la escena de cada plano, mueve la cámara, hace hablar a los personajes y dibuja subtítulos.
// window.setup3d({tl, shots}) y window.frame3d(t). Los planos vienen calculados desde Node (ver render3d.js y los guiones de planos).
(function () {
const W = 1920, H = 1080;
let R, cam, TL, SHOTS, CH = {}, INS, overlay;
const KIND = {moni: 'moni', card: 'tarjetin', centavito: 'centavito', cup: 'cafecito', bag: 'delivy'};

window.setup3d = function (data) {
  TL = data.tl; SHOTS = data.shots;
  R = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true}); R.setSize(W, H); R.setPixelRatio(1);
  R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFSoftShadowMap; R.outputColorSpace = THREE.SRGBColorSpace;
  document.body.appendChild(R.domElement);
  cam = new THREE.PerspectiveCamera(36, W / H, .1, 400);
  Object.keys(KIND).forEach(k => { CH[k] = M3.personaje(KIND[k]) });
  INS = M3.insert();
  overlay = document.createElement('div'); overlay.id = 'ov'; document.body.appendChild(overlay);
  overlay.innerHTML = `<div id="cap"></div><div id="ttl"></div><div id="wm"><i></i>@moni.finanzas</div>`;
  return document.fonts.ready.then(() => true);
};

function lineAt(t) { // escena de línea vigente (o la última hablada) del timeline
  let cur = null; for (const s of TL.scenes) { if (s.start > t) break; if (s.type === 'line') cur = s; }
  return cur;
}
function shotAt(t) { let lo = 0, hi = SHOTS.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (SHOTS[m].start <= t) lo = m; else hi = m - 1 } return SHOTS[lo] }

function place(c, L, spotName) {
  const s = L.spots[spotName]; if (c.parent !== L.scene) L.scene.add(c);
  c.position.set(s.p[0], s.sit ? s.sit - (c.legY0 - c.sitDrop) : s.p[1], s.p[2]); c.rotation.y = s.ry || 0; c.visible = true; c.userData.sit = !!s.sit;
}
function closeCam(c, o = {}) {
  const e = new THREE.Vector3(0, (c.eye.y - (c.userData.sit ? c.sitDrop : 0)) * c.scale.y, 0).add(c.position);
  const ry = c.rotation.y + (o.angle || 0), d = o.dist || 4.6;
  const p = new THREE.Vector3(Math.sin(ry) * d, .45, Math.cos(ry) * d).add(e);
  return {p: p.toArray(), look: [e.x, e.y + .05, e.z], fov: o.fov || 34};
}
function chunkCaption(text, k) { // 2-4 palabras por pantalla, sincronizado por proporción de letras
  const words = text.split(/\s+/); const chunks = []; let cur = [];
  words.forEach(w => { cur.push(w); const len = cur.join(' ').length; if (cur.length >= 4 || len > 18 || /[.,;:?!…]$/.test(w)) { chunks.push(cur.join(' ')); cur = [] } });
  if (cur.length) chunks.push(cur.join(' '));
  const total = chunks.reduce((a, c) => a + c.length + 2, 0); let acc = 0;
  for (const c of chunks) { acc += c.length + 2; if (k <= acc / total) return c } return chunks[chunks.length - 1];
}
const esc = s => String(s).replace(/[&<>]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;'}[c]));

window.frame3d = function (t) {
  const sh = shotAt(t), k = M3.clamp((t - sh.start) / Math.max(.01, sh.end - sh.start)), ln = lineAt(t);
  const talkWho = ln && t < ln.start + ln.audio ? ln.kind : null;
  let scene, C;
  Object.values(CH).forEach(c => c.visible = false);
  if (sh.insert) {
    INS.show(sh.insert.prop, sh._applied ? null : sh.insert.content); sh._applied = true;
    scene = INS.scene; C = Object.assign({}, INS.cam, sh.insert.cam || {});
  } else {
    const L = M3.lugar(sh.loc); scene = L.scene; L.update(t);
    if (sh.propSet && !sh._propApplied) { L.props[sh.propSet.name].set(sh.propSet.content); sh._propApplied = true }
    Object.entries(sh.cast || {}).forEach(([kind, spot]) => { const c = CH[kind]; place(c, L, spot);
      const ex = (ln && ln.ex && ln.ex[kind]) || 'happy'; const talking = talkWho === kind;
      const g = (sh.gesture && sh.gesture[kind]) || (talking ? (ex === 'shock' ? 'shock' : ex === 'wave' ? 'wave' : 'talk') : (ex === 'think' ? 'think' : 'idle'));
      c.anim(t, {talk: talking ? 1 : 0, expr: ex, gesture: g, sit: c.userData.sit, seed: kind.length, lean: talking ? .04 : 0}) });
    if (typeof sh.cam === 'string' && sh.cam.startsWith('close:')) C = closeCam(CH[sh.cam.slice(6)], sh.camOpt || {});
    else C = Object.assign({}, L.cams[sh.cam]);
  }
  // movimiento de cámara: del punto inicial al final (o empuje suave) + leve pulso de mano
  const to = C.to || C.p.map((v, i) => v + (C.look[i] - v) * (sh.push ?? .06));
  const e = M3.ease(k);
  const pos = C.p.map((v, i) => M3.lerp(v, to[i], e));
  const hand = [M3.noise(t * .7, 1) * .04, M3.noise(t * .6, 2) * .03, 0];
  cam.fov = C.fov || 36; cam.updateProjectionMatrix();
  cam.position.set(pos[0] + hand[0], pos[1] + hand[1], pos[2]); cam.lookAt(...C.look);
  R.render(scene, cam);
  // subtítulos y títulos
  const capEl = document.getElementById('cap');
  if (ln && t < ln.start + ln.audio + .15 && !sh.title) { const kk = M3.clamp((t - ln.start) / ln.audio); const txt = chunkCaption(ln.text, kk);
    capEl.innerHTML = esc(txt).replace(/(\$?\d[\d.,]*\s?%?)/g, '<b>$1</b>'); capEl.style.opacity = 1 } else capEl.style.opacity = 0;
  const ttl = document.getElementById('ttl');
  if (sh.title) { ttl.innerHTML = `<small>${esc(sh.title.over || '')}</small>${esc(sh.title.text)}`; ttl.style.opacity = M3.clamp(k * 4) * M3.clamp((1 - k) * 4); ttl.style.transform = `translate(-50%,-50%) scale(${.9 + .1 * M3.ease(k * 3)})` } else ttl.style.opacity = 0;
  return sh;
};
})();
