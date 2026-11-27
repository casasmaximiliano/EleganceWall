// Director del mundo 3D (navegador): arma la escena de cada plano, mueve la cámara, hace hablar a los personajes y dibuja subtítulos.
// window.setup3d({tl, shots}) y window.frame3d(t). Los planos vienen calculados desde Node (ver render3d.js y los guiones de planos).
(function () {
let W = 1920, H = 1080;
let R, cam, TL, SHOTS, CH = {}, INS, overlay;
const KIND = {moni: 'moni', card: 'tarjetin', centavito: 'centavito', cup: 'cafecito', bag: 'delivy', zombi: 'zombi', gymzombi: 'gymzombi', ghost: 'infla', car: 'autito'};

// Gestos con sentido: se eligen por las palabras de cada frase (yo → pecho, vos → señalar, números → contar, pregunta → palmas arriba).
const NUM = /^(\$?\d|uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|cien|mil|veinte|treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa|doscientos|trescientos|novecientos|ciento|primer|primera)/i;
function planBeats(s) {
  const words = s.text.split(/\s+/), total = s.text.length; let acc = 0; const at = [];
  words.forEach(w => { at.push(acc / total * s.audio); acc += w.length + 1 });
  const beats = []; let lastEnd = -1;
  const add = (i, pose, len) => { const t0 = Math.max(at[i] - .15, 0); if (t0 < lastEnd + .35) return; const t1 = Math.min(s.audio + .2, t0 + len); beats.push({t0, t1, pose}); lastEnd = t1 };
  const ex = (s.ex && s.ex[s.kind]) || 'happy';
  if (ex === 'shock') add(0, 'armsUp', 1.3);
  if (/^no\b/i.test(s.text)) add(0, 'no', 1.2);
  words.forEach((w, i) => {
    const lw = w.toLowerCase().replace(/[¿¡,.;:!?…“”"]/g, '');
    if (/^(yo|me|mi|mis|conmigo)$/.test(lw)) add(i, 'chest', 1.1);
    else if (/^(vos|te|tu|tus|contigo|ti|quedate|fijate|mirá|anotalos|cazá)$/.test(lw)) add(i, 'point', 1.1);
    else if (NUM.test(lw)) add(i, 'count', 1.2);
    else if (/\?$/.test(w)) add(Math.max(0, i - 2), 'palmsUp', 1.3);
  });
  if (!beats.length) add(0, ex === 'think' ? 'think' : ex === 'angry' ? 'hips' : 'open', Math.min(1.8, s.audio * .6));
  return beats.sort((a, b) => a.t0 - b.t0);
}
// énfasis: pequeños golpes en palabras largas (no un vaivén continuo)
function emphasis(s, tt) { const words = s.text.split(/\s+/), total = s.text.length; let acc = 0, e = 0;
  for (const w of words) { const t0 = acc / total * s.audio; acc += w.length + 1; if (w.length >= 6) { const d = tt - t0; if (d > 0 && d < .35) e = Math.max(e, Math.sin(d / .35 * Math.PI)) } } return e }

window.setup3d = function (data) {
  TL = data.tl; SHOTS = data.shots; window.SHORT = !!data.short; if (data.size) { W = data.size[0]; H = data.size[1]; document.body.classList.add(H > W ? 'vert' : 'hor') }
  TL.scenes.forEach(s => { if (s.type === 'line') s.beats = planBeats(s) });
  R = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true}); R.setSize(W, H); R.setPixelRatio(1);
  R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFSoftShadowMap; R.outputColorSpace = THREE.SRGBColorSpace;
  document.body.appendChild(R.domElement);
  cam = new THREE.PerspectiveCamera(36, W / H, .1, 400);
  Object.keys(KIND).forEach(k => { CH[k] = M3.personaje(KIND[k]) });
  INS = M3.insert();
  overlay = document.createElement('div'); overlay.id = 'ov'; document.body.appendChild(overlay);
  overlay.innerHTML = `<div id="cap"></div><div id="ttl"></div><div id="pn"></div><div id="big"><b></b><small></small></div><div id="disc">Contenido educativo. No es asesoramiento financiero.</div><div id="wm"><i></i>@moni.finanzas</div>`;
  return document.fonts.ready.then(() => true);
};

function lineAt(t) { // escena de línea vigente (o la última hablada) del timeline
  let cur = null; for (const s of TL.scenes) { if (s.start > t) break; if (s.type === 'line') cur = s; }
  return cur;
}
function shotAt(t) { let lo = 0, hi = SHOTS.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (SHOTS[m].start <= t) lo = m; else hi = m - 1 } return SHOTS[lo] }

function place(c, L, spotName) {
  const s = L.spots[spotName]; if (c.parent !== L.scene) L.scene.add(c);
  c.position.set(s.p[0], s.sit ? s.sit - (c.legY0 - c.sitDrop) : s.p[1], s.p[2]); c.rotation.y = s.ry || 0; c.visible = true; c.userData.sit = !!s.sit; c.userData.walking = false;
}
function closeCamAt(c, o, ang, d) {
  const e = new THREE.Vector3(0, (c.eye.y - (c.userData.sit ? c.sitDrop : 0)) * c.scale.y, 0).add(c.position);
  const ry = c.rotation.y + ang;
  const p = new THREE.Vector3(Math.sin(ry) * d, .45, Math.cos(ry) * d).add(e);
  if (o.shift) { const rx = Math.cos(ry) * o.shift, rz = -Math.sin(ry) * o.shift; p.x -= rx; p.z -= rz; e.x -= rx; e.z -= rz }  // corre al personaje a la derecha del cuadro
  return {p: p.toArray(), look: [e.x, e.y - .1, e.z], fov: o.fov || 33};
}
// Puntaje de un encuadre: algo entre la cámara y la cara (árbol, farol, otro personaje) o un personaje cortado por el borde.
const RAY = new THREE.Raycaster(), TMP = new THREE.PerspectiveCamera();
function ownerOf(obj, list) { for (let x = obj; x; x = x.parent) if (list.includes(x)) return x; return null }
let dbgPen = {};
function camPenalty(C, c, others, scene) {
  dbgPen = {};
  TMP.fov = C.fov; TMP.aspect = W / H; TMP.position.fromArray(C.p); TMP.lookAt(...C.look); TMP.updateProjectionMatrix(); TMP.updateMatrixWorld();
  let pen = 0; const from = new THREE.Vector3().fromArray(C.p);
  const eye = new THREE.Vector3().fromArray(C.look), dir = eye.clone().sub(from), dist = dir.length(); dir.normalize();
  RAY.set(from, dir); RAY.far = dist - .9;
  const hit = RAY.intersectObjects(scene.children, true).find(h => h.object.visible && !h.object.userData.outline && h.object.material && !h.object.material.transparent && !ownerOf(h.object, [c]));
  if (hit) { pen += 10; dbgPen.hit = (hit.object.name || hit.object.geometry.type) + '@' + hit.distance.toFixed(1) }
  others.forEach(o => {  // caja aproximada fija (no depende de la pose): un personaje a medias en el borde molesta
    const hgt = (o.rig ? o.rig.height : 3) * o.scale.y, w = 1.25 * o.scale.x; let inside = 0, n = 0;
    for (const dx of [-w, -w / 2, 0, w / 2, w]) for (const dz of [-w / 2, w / 2]) for (const dy of [.2, hgt * .35, hgt * .7, hgt]) {
      const v = new THREE.Vector3(o.position.x + dx, o.position.y + dy, o.position.z + dz).project(TMP); n++; if (v.z < 1 && Math.abs(v.x) < 1.02 && Math.abs(v.y) < 1.02) inside++ }
    const f = inside / n; if (f > 0 && f < .75) { pen += 3 * f + 1; dbgPen.cut = (dbgPen.cut || '') + o.tipo + f.toFixed(2) }
  });
  return pen;
}
function panelOffset(C, chars) {
  TMP.fov = C.fov || 36; TMP.aspect = W / H; TMP.position.fromArray(C.p); TMP.lookAt(...C.look); TMP.updateProjectionMatrix(); TMP.updateMatrixWorld();
  let minX = W, maxX = 0;
  chars.forEach(o => { const hgt = (o.rig ? o.rig.height : 3) * o.scale.y, w = 1.1 * o.scale.x;
    for (const dx of [-w, w]) for (const dy of [.3, hgt * .6, hgt]) { const v = new THREE.Vector3(o.position.x + dx, o.position.y + dy, o.position.z).project(TMP);
      if (v.z >= 1 || Math.abs(v.y) > 1.1) continue; const px = (v.x + 1) / 2 * W; minX = Math.min(minX, px); maxX = Math.max(maxX, px) } });
  const panelLeft = W - 70 - 640 - 40;                       // borde izquierdo del panel, con aire
  let off = Math.max(W * .1, maxX - panelLeft);             // lo justo para despejar al de más a la derecha
  off = Math.min(off, Math.max(W * .1, minX - 40), W * .34); // sin sacar de cuadro al de la izquierda
  return off;
}
function closeCam(c, o = {}, others = [], scene) {
  const base = o.angle || 0, d0 = o.dist || 5.6;
  if (!scene || o.fixed) return closeCamAt(c, o, base, d0);
  let best = null;
  for (const da of [0, .14, -.14, .28, -.28, .42, -.42, .6, -.6]) for (const d of [d0, d0 * .85, d0 * 1.2]) {
    const C = closeCamAt(c, o, base + da, d); const pen = camPenalty(C, c, others, scene) + Math.abs(da) * .8 + Math.abs(d - d0) * .3;
    if (!best || pen < best.pen) best = {C, pen};
    if (window.DBG && da === 0 && d === d0) console.log('  base pen', c.tipo, pen.toFixed(2), JSON.stringify(dbgPen));
    if (pen < .01) return C;
  }
  if (window.DBG) console.log('closeCam', c.tipo, best.pen.toFixed(2));
  return best.C;
}
function chunkCaption(text, k) { // 2-4 palabras por pantalla, sincronizado por proporción de letras
  const words = text.split(/\s+/); const chunks = []; let cur = [];
  words.forEach(w => { cur.push(w); const len = cur.join(' ').length; if (cur.length >= 4 || len > 18 || /[.,;:?!…]$/.test(w)) { chunks.push(cur.join(' ')); cur = [] } });
  if (cur.length) chunks.push(cur.join(' '));
  const total = chunks.reduce((a, c) => a + c.length + 2, 0); let acc = 0;
  for (const c of chunks) { acc += c.length + 2; if (k <= acc / total) return c } return chunks[chunks.length - 1];
}
// Panel con los números: entra de costado, los renglones aparecen de a uno, el sello cae al final.
function drawPanel(sh, k, t) {
  const el = document.getElementById('pn'); const P = sh.panel;
  if (!P) { el.style.opacity = 0; return }
  const dur = sh.end - sh.start, tt = t - sh.start, lines = P.lines || [], keep = P.keep || 0;
  const step = Math.min(.9, Math.max(.35, (dur * .55) / Math.max(1, lines.length - keep)));
  const rows = lines.map((l, i) => { const at = i < keep ? -1 : .25 + (i - keep) * step; const a = M3.clamp((tt - at) / .3);
    const v = l.v ? `<em style="color:${l.vc || '#14221D'}">${esc(l.v)}</em>` : '';
    return `<div class="r" style="opacity:${a};transform:translateX(${(1 - M3.ease(a)) * 40}px);color:${l.c || '#14221D'}"><span>${esc(l.t || '')}</span>${v}</div>` }).join('');
  const stA = P.stamp ? M3.clamp((tt - (.25 + (lines.length - keep) * step + .2)) / .25) : 0;
  const stamp = P.stamp ? `<div class="st" style="opacity:${stA};transform:rotate(-8deg) scale(${1.6 - .6 * M3.ease(stA)})">${esc(P.stamp)}</div>` : '';
  el.className = 'pn-' + (P.kind || 'cuaderno');
  const inA = P.cont ? 1 : M3.ease(M3.clamp(tt / .45)), outA = M3.clamp((dur - tt) / .3);
  el.style.opacity = Math.min(inA, P.contNext ? 1 : outA);
  el.style.transform = `translateX(${(1 - inA) * 120}%) rotate(${P.kind === 'resumen' ? 1.5 : -1.5}deg)`;
  el.innerHTML = `<h3>${esc(P.title || '')}</h3>${rows}${stamp}`;
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
    const L = M3.lugar(sh.loc); scene = L.scene;
    L.obstacles = Object.entries(sh.cast || {}).map(([k, sp]) => ({x: L.spots[sp].p[0], z: L.spots[sp].p[2]}));
    L.laugh = 0; if (sh.fx) Object.assign(L, sh.fx);
    L.update(t);
    if (sh.propSet && !sh._propApplied) { L.props[sh.propSet.name].set(sh.propSet.content); sh._propApplied = true }
    Object.entries(sh.cast || {}).forEach(([kind, spot]) => place(CH[kind], L, spot));
    if (sh.enter) Object.entries(sh.enter).forEach(([kind, from]) => { const c = CH[kind], k2 = M3.clamp((t - sh.start) / 1.4);
      if (k2 < 1) { const e2 = M3.ease(k2); c.position.x = M3.lerp(c.position.x + from[0], c.position.x, e2); c.position.z = M3.lerp(c.position.z + from[1], c.position.z, e2); c.userData.walking = true } else c.userData.walking = false });
    const speaker = talkWho && sh.cast && sh.cast[talkWho] ? CH[talkWho] : null;
    Object.keys(sh.cast || {}).forEach(kind => { const c = CH[kind];
      const ex = (ln && ln.ex && ln.ex[kind]) || 'happy'; const talking = talkWho === kind; const tt = ln ? t - ln.start : 0;
      let pose = 'rest', poseW = 0, emph = 0, nod = 0, turn = 0, lookX = 0;
      const GMAP = {shock: 'armsUp', wave: 'wave', point: 'point', think: 'think', cross: 'cross', hold: 'hold'};
      if (sh.gesture && sh.gesture[kind]) { pose = GMAP[sh.gesture[kind]] || sh.gesture[kind]; poseW = M3.clamp((t - sh.start) / .35) }
      else if (talking) { const b = ln.beats.find(b => tt >= b.t0 && tt < b.t1); if (b) { pose = b.pose; poseW = Math.min(M3.clamp((tt - b.t0) / .3), M3.clamp((b.t1 - tt) / .3)) } emph = emphasis(ln, tt) }
      else { if (ex === 'think') { pose = 'think'; poseW = .9 } else if (ex === 'angry') { pose = 'cross'; poseW = .9 } }
      if (!talking && speaker) {  // el que escucha mira al que habla y asiente en las pausas
        const d = new THREE.Vector3().subVectors(speaker.position, c.position); const ang = Math.atan2(d.x, d.z) - c.rotation.y;
        turn = M3.clamp(Math.atan2(Math.sin(ang), Math.cos(ang)) * .35, -.5, .5); lookX = M3.clamp(turn * .12, -.06, .06);
        const ph = (tt % 2.6) / 2.6; nod = ph > .1 && ph < .25 ? Math.sin((ph - .1) / .15 * Math.PI) : 0;
      }
      c.anim(t, {talk: talking ? 1 : 0, expr: ex, pose, poseW, emph, nod, turn, lookX, sit: c.userData.sit, walk: !!c.userData.walking, seed: kind.length, lean: talking ? .03 : 0}) });
    if (typeof sh.cam === 'string' && sh.cam.startsWith('close:')) {
      if (!sh._cc) { const subj = CH[sh.cam.slice(6)]; const others = Object.keys(sh.cast || {}).filter(k => CH[k] !== subj).map(k => CH[k]);
        const saved = Object.keys(sh.cast || {}).map(k => [CH[k], CH[k].position.clone()]); Object.entries(sh.cast || {}).forEach(([k, sp]) => place(CH[k], L, sp));
        L.scene.updateMatrixWorld(true); sh._cc = closeCam(subj, sh.camOpt || {}, others, L.scene); saved.forEach(([c, p]) => c.position.copy(p)) }
      C = Object.assign({}, sh._cc);
    }
    else C = Object.assign({}, typeof sh.cam === 'object' ? sh.cam : L.cams[sh.cam]);
  }
  // movimiento de cámara: del punto inicial al final (o empuje suave) + leve pulso de mano
  const to = C.to || C.p.map((v, i) => v + (C.look[i] - v) * (sh.push ?? .06));
  const e = M3.ease(k);
  const pos = C.p.map((v, i) => M3.lerp(v, to[i], e));
  const hand = [M3.noise(t * .7, 1) * .04, M3.noise(t * .6, 2) * .03, 0];
  cam.fov = C.fov || 36; cam.aspect = W / H;
  if (sh.panel && !sh.insert && H < W) {  // corre la escena lo justo para que ningún personaje quede debajo del panel
    if (sh._off == null) sh._off = panelOffset(C, Object.keys(sh.cast || {}).map(k => CH[k]));
    cam.setViewOffset(W, H, sh._off, 0, W, H) } else cam.clearViewOffset();
  cam.updateProjectionMatrix();
  cam.position.set(pos[0] + hand[0], pos[1] + hand[1], pos[2]); cam.lookAt(...C.look);
  R.render(scene, cam);
  // subtítulos y títulos
  const capEl = document.getElementById('cap');
  if (ln && t < ln.start + ln.audio + .15 && !sh.title) { const kk = M3.clamp((t - ln.start) / ln.audio); const txt = chunkCaption(ln.text, kk);
    capEl.innerHTML = esc(txt).replace(/(\$?\d[\d.,]*\s?%?)/g, '<b>$1</b>'); capEl.style.opacity = 1 } else capEl.style.opacity = 0;
  drawPanel(sh, k, t);
  // Short: el número grande de cada frase arriba (pop al entrar) y el aviso al final
  const bg = document.getElementById('big'), P = window.SHORT && ln && ln.panel && t < ln.start + ln.dur ? ln.panel : null;
  if (P && P.big) { const a = M3.clamp((t - ln.start) / .22); bg.querySelector('b').textContent = P.big; bg.querySelector('b').style.fontSize = Math.min(170, Math.round(1500 / Math.max(4, [...P.big].length))) + 'px'; bg.querySelector('small').textContent = P.small || '';
    bg.style.opacity = a; bg.style.transform = `translateX(-50%) scale(${.6 + .4 * M3.ease(a) + (a >= 1 ? 0 : .08 * Math.sin(a * Math.PI))})` } else bg.style.opacity = 0;
  const last = TL.scenes[TL.scenes.length - 1]; document.getElementById('disc').style.opacity = window.SHORT && t > last.start ? 1 : 0;
  const ttl = document.getElementById('ttl');
  if (sh.title) { ttl.innerHTML = `<small>${esc(sh.title.over || '')}</small>${esc(sh.title.text)}`; ttl.style.opacity = M3.clamp(k * 4) * M3.clamp((1 - k) * 4); ttl.style.transform = `translate(-50%,-50%) scale(${.9 + .1 * M3.ease(k * 3)})` } else ttl.style.opacity = 0;
  return sh;
};
})();
