// Objetos para planos de detalle: celular con app del banco, cuaderno, resumen de tarjeta, calendario, pizarrón, alcancía.
// M3.prop(tipo, contenido) -> Group con .set(contenido) para cambiar lo que muestra. M3.insert() -> escena de mesa para primeros planos.
(function () {
const {toon, flat, box, rbox, cyl, sph, plane, canvasTex, font} = M3;
const W = (g, txt, x, y, px, col, w = 800, al = 'left') => { g.fillStyle = col; g.font = font(px, w); g.textAlign = al; g.fillText(txt, x, y) };

function screenDraw(c) {
  return (g, w, h) => {
    g.fillStyle = '#F4F8F6'; g.fillRect(0, 0, w, h); g.fillStyle = c.color || '#0E5A40'; g.fillRect(0, 0, w, 150);
    W(g, c.app || 'Mi Banco', 40, 95, 54, '#fff'); W(g, '9:41', w - 40, 60, 34, '#fff', 700, 'right');
    (c.rows || []).forEach((r, i) => {
      const y = 260 + i * 200; g.fillStyle = r.hl ? '#FFF1C2' : '#FFFFFF'; g.fillRect(30, y - 90, w - 60, 170);
      g.strokeStyle = '#D3DDD7'; g.lineWidth = 4; g.strokeRect(30, y - 90, w - 60, 170);
      W(g, r.label, 60, y - 20, 44, '#56675F', 700); W(g, r.value, 60, y + 50, 84, r.neg ? '#C8102E' : '#17865A');
    });
    if (c.big) { W(g, c.big, w / 2, h - 170, 120, c.bigColor || '#14221D', 800, 'center') }
  };
}
function paperDraw(c) {
  return (g, w, h) => {
    g.fillStyle = c.bg || '#FFFDF6'; g.fillRect(0, 0, w, h);
    if (c.lined !== false) { g.strokeStyle = '#BFD7EA'; g.lineWidth = 3; for (let y = 120; y < h; y += 80) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke() } g.strokeStyle = '#F2A0A0'; g.beginPath(); g.moveTo(90, 0); g.lineTo(90, h); g.stroke() }
    if (c.title) W(g, c.title, 120, 95, 58, c.titleColor || '#14221D', 800);
    (c.lines || []).forEach((l, i) => { const y = 190 + i * 80; W(g, l.t, 120, y, 50, l.c || '#22304A', 700); if (l.v) W(g, l.v, w - 50, y, 54, l.vc || '#C8102E', 800, 'right') });
    if (c.stamp) { g.save(); g.translate(w * .68, h * .8); g.rotate(-.2); g.strokeStyle = '#C8102E'; g.lineWidth = 10; g.strokeRect(-200, -70, 400, 120); W(g, c.stamp, 0, 15, 62, '#C8102E', 800, 'center'); g.restore() }
  };
}
const SIZES = {celular: [600, 1200], cuaderno: [800, 1000], resumen: [800, 1000]};

M3.prop = function (tipo, c = {}) {
  const g = new THREE.Group(); let tex, face;
  const mk = (pw, ph, draw, ww, hh) => { tex = canvasTex(pw, ph, draw); face = plane(ww, hh, toon('#fff', {map: tex})); return face };
  if (tipo === 'celular') {
    const body = rbox(1.25, 2.5, .12, .18, toon('#1d1d1f')); g.add(body);
    const scr = mk(600, 1200, screenDraw(c), 1.12, 2.24); scr.position.z = .12; g.add(scr);
    g.set = (n) => { const ctx = tex.image.getContext('2d'); screenDraw(n)(ctx, 600, 1200); tex.needsUpdate = true };
  } else if (tipo === 'cuaderno' || tipo === 'resumen') {
    const cover = rbox(2.2, 2.8, .1, .06, toon(tipo === 'cuaderno' ? '#3F6FB8' : '#E8E2D6')); g.add(cover);
    const pg = mk(800, 1000, paperDraw(Object.assign({lined: tipo === 'cuaderno', bg: tipo === 'resumen' ? '#FFFFFF' : undefined}, c)), 2.0, 2.5); pg.position.z = .11; g.add(pg);
    if (tipo === 'cuaderno') for (let i = 0; i < 9; i++) { const r = new THREE.Mesh(new THREE.TorusGeometry(.07, .02, 6, 12), toon('#9AA0A6')); r.position.set(-1.05, -1.1 + i * .28, .12); r.rotation.y = Math.PI / 2; g.add(r) }
    g.set = (n) => { const ctx = tex.image.getContext('2d'); paperDraw(Object.assign({lined: tipo === 'cuaderno', bg: tipo === 'resumen' ? '#FFFFFF' : undefined}, n))(ctx, 800, 1000); tex.needsUpdate = true };
  } else if (tipo === 'calendario') {
    const draw = (n) => (gg, w, h) => { gg.fillStyle = '#FFFFFF'; gg.fillRect(0, 0, w, h); gg.fillStyle = '#C8102E'; gg.fillRect(0, 0, w, 110); W(gg, n.mes || 'DÍAS', w / 2, 80, 64, '#fff', 800, 'center');
      W(gg, n.text || '90', w / 2, 330, 230, '#14221D', 800, 'center'); if (n.sub) W(gg, n.sub, w / 2, 440, 54, '#C8102E', 800, 'center');
      if (n.circle) { gg.strokeStyle = '#C8102E'; gg.lineWidth = 12; gg.beginPath(); gg.ellipse(w / 2, 260, 190, 140, 0, 0, 7); gg.stroke() } };
    const b = rbox(2, 2.4, .08, .05, toon('#FFFFFF')); g.add(b);
    const f = mk(400, 480, draw(c), 1.9, 2.3); f.position.z = .1; g.add(f);
    for (let i = 0; i < 6; i++) { const r = new THREE.Mesh(new THREE.TorusGeometry(.06, .018, 6, 12), toon('#9AA0A6')); r.position.set(-.7 + i * .28, 1.2, .1); g.add(r) }
    g.set = (n) => { draw(n)(tex.image.getContext('2d'), 400, 480); tex.needsUpdate = true };
  } else if (tipo === 'pizarron') {
    const draw = (n) => (gg, w, h) => { gg.fillStyle = '#23302B'; gg.fillRect(0, 0, w, h); gg.strokeStyle = '#8A5A3B'; gg.lineWidth = 22; gg.strokeRect(0, 0, w, h);
      W(gg, n.title || 'CAFÉ', 50, 100, 72, '#F7E9D2'); (n.items || [['Café', '$3'], ['Latte', '$3,50'], ['Medialuna', '$1,50'], ['Tostado', '$4']]).forEach(([a, p], i) => { W(gg, a, 50, 200 + i * 85, 56, '#F7E9D2', 700); W(gg, p, w - 50, 200 + i * 85, 56, '#F4C542', 800, 'right') });
      if (n.note) W(gg, n.note, w / 2, h - 40, 50, '#F28B82', 800, 'center') };
    const f = mk(900, 560, draw(c), 5, 3.1); g.add(f); const fr = box(5.2, 3.3, .1, toon('#8A5A3B')); fr.position.z = -.06; g.add(fr);
    g.set = (n) => { draw(n)(tex.image.getContext('2d'), 900, 560); tex.needsUpdate = true };
  } else if (tipo === 'alcancia') {
    const pig = sph(.9, toon('#F49AB8')); pig.scale.set(1.3, 1, 1); g.add(pig);
    const snout = cyl(.3, .3, .25, toon('#F07AA0'), {seg: 20}); snout.rotation.x = Math.PI / 2; snout.position.set(0, 0, .95); snout.rotation.z = 0; snout.position.x = 0; g.add(snout);
    [-1, 1].forEach(s => { const e = new THREE.Mesh(new THREE.SphereGeometry(.07, 10, 8), flat('#141010')); e.position.set(s * .3, .3, .85); g.add(e); const ear = new THREE.Mesh(new THREE.ConeGeometry(.2, .35, 10), toon('#F07AA0')); ear.position.set(s * .5, .85, .2); g.add(ear); M3.outline(ear); const leg = cyl(.15, .15, .4, toon('#F07AA0'), {seg: 10}); leg.position.set(s * .6, -.9, .4); g.add(leg); const leg2 = leg.clone(); leg2.position.z = -.4; g.add(leg2) });
    const slot = box(.5, .05, .1, flat('#5a1a2a'), {outline: false}); slot.position.set(0, .98, 0); g.add(slot);
    g.set = () => {};
  }
  return g;
};

// Escena de primer plano: mesa de madera iluminada donde se apoya el objeto.
M3.insert = function () {
  const S = new THREE.Scene(); S.background = new THREE.Color('#E9CFA6');
  S.add(new THREE.HemisphereLight('#FFF6E8', '#B98A5E', 1.5)); const sun = new THREE.DirectionalLight('#FFE3B8', 2.2); sun.position.set(-4, 10, 6); sun.castShadow = true; sun.shadow.mapSize.set(1024, 1024); S.add(sun);
  const wood = canvasTex(512, 512, (g, w, h) => { for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? '#C79466' : '#BC8A5C'; g.fillRect(0, i * 64, w, 64); g.fillStyle = 'rgba(0,0,0,.1)'; g.fillRect(0, i * 64 + 62, w, 2) } }); wood.wrapS = wood.wrapT = THREE.RepeatWrapping; wood.repeat.set(2, 2);
  const table = plane(14, 10, toon('#fff', {map: wood})); table.rotation.x = -Math.PI / 2; S.add(table);
  const mug = cyl(.45, .4, .8, toon('#FFFFFF')); mug.position.set(3.2, .4, -1.6); S.add(mug);
  const pen = cyl(.05, .05, 1.8, toon('#2F6DB5'), {seg: 8}); pen.rotation.z = Math.PI / 2; pen.rotation.y = .5; pen.position.set(-3, .06, 1.6); S.add(pen);
  const slots = {};
  ['celular', 'cuaderno', 'resumen', 'calendario', 'alcancia'].forEach(k => { const p = M3.prop(k, {}); p.visible = false; S.add(p); slots[k] = p;
    if (k === 'alcancia') p.position.set(0, 1.05, 0); else { p.rotation.x = -Math.PI / 2 + .02; p.position.set(0, .08, 0) } });
  const cam = {p: [0, 3.9, 1.7], look: [0, 0, -.15], fov: 42};
  return {scene: S, slots, cam, show(k, content) { Object.entries(slots).forEach(([n, p]) => p.visible = n === k); if (content) slots[k].set(content) }};
};
})();
