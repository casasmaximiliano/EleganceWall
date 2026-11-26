// Núcleo del mundo 3D de Moni: render toon (3 tonos + contorno negro), ayudas de geometría y la cara con expresiones.
// Se carga como script clásico después de three.min.js (global THREE). Expone window.M3.
(function () {
const M3 = window.M3 = {};
const OUTLINE = 0.032;                       // grosor del contorno en unidades de escena
M3.grad = (() => { const d = new Uint8Array([105, 185, 255]); const t = new THREE.DataTexture(d, 3, 1, THREE.RedFormat); t.minFilter = t.magFilter = THREE.NearestFilter; t.needsUpdate = true; return t })();
M3.outlineMat = new THREE.MeshBasicMaterial({color: '#1d140f', side: THREE.BackSide});

M3.toon = (color, o = {}) => new THREE.MeshToonMaterial(Object.assign({color, gradientMap: M3.grad}, o));
M3.flat = (color, o = {}) => new THREE.MeshBasicMaterial(Object.assign({color}, o));

// Contorno por "casco invertido": un duplicado negro apenas más grande, visto por dentro.
M3.outline = function (mesh, t = OUTLINE) {
  mesh.geometry.computeBoundingBox(); const s = new THREE.Vector3(); mesh.geometry.boundingBox.getSize(s);
  const k = v => v < 1e-3 ? 1 : Math.min(1.7, 1 + 2 * t / v);
  const h = new THREE.Mesh(mesh.geometry, M3.outlineMat); h.scale.set(k(s.x), k(s.y), k(s.z)); h.userData.outline = true; mesh.add(h); return mesh;
};
function finish(m, o = {}) { m.castShadow = o.shadow !== false; m.receiveShadow = true; if (o.outline !== false) M3.outline(m, o.t); return m }
M3.box = (w, h, d, mat, o) => finish(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat), o);
M3.rbox = (w, h, d, r, mat, o) => finish(new THREE.Mesh(roundedBox(w, h, d, r), mat), o);
M3.cyl = (rt, rb, h, mat, o = {}) => finish(new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, o.seg || 32), mat), o);
M3.sph = (r, mat, o = {}) => finish(new THREE.Mesh(new THREE.SphereGeometry(r, o.seg || 28, o.seg || 20), mat), o);
M3.cap = (r, len, mat, o) => finish(new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 8, 16), mat), o);
M3.plane = (w, h, mat) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat); m.receiveShadow = true; return m };
function roundedBox(w, h, d, r) {
  const s = new THREE.Shape(), x = -w / 2, y = -h / 2;
  s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r); s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r); s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
  const g = new THREE.ExtrudeGeometry(s, {depth: d, bevelEnabled: true, bevelThickness: Math.min(.04, d / 3), bevelSize: Math.min(.04, r / 2), bevelSegments: 3, curveSegments: 10});
  g.translate(0, 0, -d / 2); return g;
}
M3.roundedBox = roundedBox;

// Texturas de texto (carteles, pantallas, papeles)
M3.canvasTex = function (w, h, draw) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t };
M3.font = (px, w = 800) => `${w} ${px}px "Figtree","Bricolage Grotesque","DejaVu Sans",sans-serif`;
M3.sign = function (text, o = {}) {
  const w = o.w || 3, h = o.h || .8, pxw = 512, pxh = Math.round(512 * h / w);
  const tex = M3.canvasTex(pxw, pxh, (g) => { g.fillStyle = o.bg || '#C8102E'; g.fillRect(0, 0, pxw, pxh); g.fillStyle = o.fg || '#fff'; g.font = M3.font(Math.round(pxh * .55)); g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(text, pxw / 2, pxh / 2 + 2) });
  const g = new THREE.Group();
  const back = M3.rbox(w + .08, h + .08, .08, .06, M3.toon(o.frame || '#2a2a2a')); g.add(back);
  const face = M3.plane(w, h, M3.toon('#fff', {map: tex})); face.position.z = .1; g.add(face);
  return g;
};

// Utilidades de animación
M3.clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
M3.ease = x => { x = M3.clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2 };
M3.lerp = (a, b, k) => a + (b - a) * k;
M3.noise = (t, s = 0) => Math.sin(t * 1.3 + s) * .5 + Math.sin(t * 2.1 + s * 1.7) * .3 + Math.sin(t * 3.7 + s * .3) * .2;

// Cara con expresiones: ojos (con párpado y brillo), cejas, boca que habla, cachetes.
const EXPR = {
  happy:   {brow: [.0, .0], browY: 0, smile: 1, open: 0, lid: 0, look: [0, 0]},
  shock:   {brow: [.15, -.15], browY: .09, smile: 0, open: .9, lid: -.1, look: [0, .02]},
  worried: {brow: [-.35, .35], browY: .05, smile: -.6, open: .15, lid: .15, look: [0, -.02]},
  angry:   {brow: [.45, -.45], browY: -.03, smile: -.3, open: .2, lid: .3, look: [0, 0]},
  think:   {brow: [-.1, .25], browY: .05, smile: .1, open: 0, lid: .1, look: [.04, .04]},
  sly:     {brow: [.3, -.05], browY: -.01, smile: .6, open: 0, lid: .35, look: [.03, 0]},
  wave:    {brow: [.0, .0], browY: .03, smile: 1, open: .2, lid: 0, look: [0, 0]},
};
M3.EXPR = EXPR;
M3.face = function (parent, o = {}) {
  const s = o.s || 1, F = new THREE.Group(); F.position.set(o.x || 0, o.y || 0, o.z || 0); F.scale.setScalar(s); parent.add(F);
  const white = M3.toon('#FFFFFF'), black = M3.flat('#141010'), skinD = M3.toon(o.lidColor || '#E0A21C');
  const eyes = [];
  [-1, 1].forEach(side => {
    const g = new THREE.Group(); g.position.set(side * .3, .05, 0); F.add(g);
    const ball = M3.sph(.2, white, {t: .022}); ball.scale.set(1, 1.15, .55); g.add(ball);
    const pupil = new THREE.Mesh(new THREE.SphereGeometry(.105, 20, 14), black); pupil.scale.z = .5; pupil.position.z = .085; g.add(pupil);
    const hi = new THREE.Mesh(new THREE.SphereGeometry(.035, 10, 8), M3.flat('#fff')); hi.position.set(.04, .05, .14); g.add(hi);
    const lid = null;
    const brow = M3.rbox(.3, .065, .05, .03, M3.toon(o.browColor || '#3b2410'), {t: .0}); brow.position.set(0, .33, .05); g.add(brow);
    eyes.push({g, pupil, hi, lid, brow, side});
  });
  const mouth = new THREE.Group(); mouth.position.set(0, -.3, .02); F.add(mouth);
  const smile = new THREE.Mesh(new THREE.TorusGeometry(.17, .035, 10, 24, Math.PI), M3.flat('#5a1414')); smile.rotation.z = Math.PI; mouth.add(smile);
  const open = new THREE.Group(); mouth.add(open);
  const hole = new THREE.Mesh(new THREE.CircleGeometry(.15, 28), M3.flat('#5a1414')); open.add(hole);
  const tongue = new THREE.Mesh(new THREE.CircleGeometry(.08, 20), M3.flat('#E05A6A')); tongue.position.set(0, -.07, .002); tongue.scale.y = .6; open.add(tongue);
  const ring = new THREE.Mesh(new THREE.RingGeometry(.15, .18, 28), M3.flat('#141010')); ring.position.z = .001; open.add(ring);
  [-1, 1].forEach(side => { const c = new THREE.Mesh(new THREE.CircleGeometry(.1, 20), M3.flat(o.cheek || '#F49A9A', {transparent: true, opacity: .75})); c.position.set(side * .5, -.18, -.01); F.add(c) });
  let cur = Object.assign({}, EXPR.happy);
  F.set = function (name, k = 1) { const e = EXPR[name] || EXPR.happy; for (const key in e) cur[key] = Array.isArray(e[key]) ? e[key].map((v, i) => M3.lerp(cur[key][i], v, k)) : M3.lerp(cur[key], e[key], k) };
  F.update = function (t, talk, seed = 0, lookX = 0) {
    const bp = (t + seed * 1.37) % 3.7; const blink = bp < .07 ? bp / .07 : bp < .14 ? 1 - (bp - .07) / .07 : 0;
    eyes.forEach(E => {
      E.brow.rotation.z = cur.brow[E.side < 0 ? 0 : 1];
      E.brow.position.y = .33 + cur.browY + (talk > .1 ? Math.sin(t * 6) * .01 : 0);
      E.g.scale.y = Math.max(.08, 1 - blink * .95 - M3.clamp(cur.lid) * .25);
      const lx = cur.look[0] + lookX + M3.noise(t * .4, seed) * .012, ly = cur.look[1] + M3.noise(t * .35, seed + 4) * .008;
      E.pupil.position.x = lx; E.pupil.position.y = ly; E.hi.position.x = .04 + lx; E.hi.position.y = .05 + ly;
    });
    const o2 = M3.clamp(Math.max(cur.open, talk));
    open.visible = o2 > .12; smile.visible = !open.visible;
    open.scale.set(1 + cur.open * .2, .25 + o2 * .85, 1);
    smile.scale.set(1, Math.abs(cur.smile) * .9 + .1, 1); smile.rotation.z = cur.smile >= 0 ? Math.PI : 0; smile.position.y = cur.smile >= 0 ? 0 : -.1;
  };
  return F;
};

// Brazo de dos tramos con mano tipo mitón. Devuelve el hombro (Group) para rotar.
M3.arm = function (parent, o) {
  const sh = new THREE.Group(); sh.position.set(o.x, o.y, o.z || 0); parent.add(sh);
  const mat = M3.toon(o.color || '#8A5A1F');
  const up = M3.cyl(o.r || .055, o.r || .055, o.len || .5, mat, {seg: 12}); up.position.y = -(o.len || .5) / 2; sh.add(up);
  const el = new THREE.Group(); el.position.y = -(o.len || .5); sh.add(el);
  const lo = M3.cyl(o.r || .055, o.r || .055, o.len2 || .45, mat, {seg: 12}); lo.position.y = -(o.len2 || .45) / 2; el.add(lo);
  const hand = M3.sph(o.hand || .13, M3.toon(o.handColor || '#F2B12A'), {seg: 16}); hand.position.y = -(o.len2 || .45) - .05; el.add(hand);
  sh.userData = {el, side: o.side}; return sh;
};
M3.leg = function (parent, o) {
  const hip = new THREE.Group(); hip.position.set(o.x, o.y, 0); parent.add(hip);
  const l = M3.cyl(o.r || .06, o.r || .06, o.len || .8, M3.toon(o.color || '#8A5A1F'), {seg: 12}); l.position.y = -(o.len || .8) / 2; hip.add(l);
  const shoe = M3.sph(.17, M3.toon(o.shoe || '#222222'), {seg: 16}); shoe.scale.set(1.2, .65, 1.6); shoe.position.set(0, -(o.len || .8) - .02, .1); hip.add(shoe);
  return hip;
};
})();
