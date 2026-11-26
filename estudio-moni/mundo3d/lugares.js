// Lugares del mundo 3D. Cada lugar es una escena propia con luces, decorado, gente y movimiento.
// M3.lugar(nombre) -> {scene, spots: {nombre: {p:[x,y,z], ry, sit}}, cams: {nombre: {p:[...], look:[...], fov}}, update(t), sky}
(function () {
const {toon, flat, box, rbox, cyl, sph, plane, canvasTex, font, sign} = M3;

function baseScene(sky, o = {}) {
  const S = new THREE.Scene(); S.background = new THREE.Color(sky);
  S.add(new THREE.HemisphereLight(o.hemiSky || '#FFF6E8', o.hemiGround || '#B98A5E', o.hemi ?? 1.35));
  const sun = new THREE.DirectionalLight(o.sun || '#FFE3B8', o.sunI ?? 2.3); sun.position.set(...(o.sunPos || [8, 14, 10])); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0005; Object.assign(sun.shadow.camera, {left: -22, right: 22, top: 18, bottom: -10, near: 1, far: 80}); S.add(sun);
  return S;
}
const texWood = (a = '#B97B4E', b = '#A86E45') => { const t = canvasTex(512, 512, (g, w, h) => { for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? a : b; g.fillRect(0, i * 64, w, 64); g.fillStyle = 'rgba(0,0,0,.12)'; g.fillRect(0, i * 64 + 62, w, 2); g.fillRect((i * 173) % w, i * 64, 2, 64) } }); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t };
const texTiles = (a, b, n = 8) => { const t = canvasTex(256, 256, (g, w) => { const s = w / n; for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { g.fillStyle = (i + j) % 2 ? a : b; g.fillRect(i * s, j * s, s, s) } }); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t };
function windowsTex(base, win, cols, rows, lit) {
  return canvasTex(256, 512, (g, w, h) => { g.fillStyle = base; g.fillRect(0, 0, w, h); const cw = w / cols, rh = h / rows;
    for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) { g.fillStyle = (lit && (i * 7 + j * 3) % 5 === 0) ? '#FFE08A' : win; g.fillRect(i * cw + cw * .2, j * rh + rh * .2, cw * .6, rh * .55); g.fillStyle = 'rgba(0,0,0,.25)'; g.fillRect(i * cw + cw * .2, j * rh + rh * .72, cw * .6, rh * .05) } });
}
function building(w, h, d, color, o = {}) {
  const g = new THREE.Group(); const tex = windowsTex(color, o.win || '#9FD3EE', o.cols || Math.max(2, Math.round(w / 1.4)), o.rows || Math.max(2, Math.round(h / 1.6)), o.lit);
  const body = box(w, h, d, [toon(color), toon(color), toon(color), toon(color), toon('#fff', {map: tex}), toon(color)]); body.position.y = h / 2; g.add(body);
  const roof = box(w + .3, .3, d + .3, toon(o.roof || '#6B4A3A')); roof.position.y = h + .15; g.add(roof);
  if (o.balcony) for (let y = 3; y < h - 1; y += 3) { const b = box(w * .5, .15, .8, toon('#EDE6DA')); b.position.set(0, y, d / 2 + .4); g.add(b); const r = box(w * .5, .6, .06, toon('#3a3a3a')); r.position.set(0, y + .35, d / 2 + .8); g.add(r) }
  return g;
}
function car(color) {
  const g = new THREE.Group();
  const body = rbox(3.2, .8, 1.6, .25, toon(color)); body.position.y = .75; g.add(body);
  const cab = rbox(1.8, .7, 1.45, .25, toon(color)); cab.position.set(-.2, 1.45, 0); g.add(cab);
  const glass = plane(1.5, .5, toon('#BFE6F7')); glass.position.set(-.2, 1.47, .74); g.add(glass); const glass2 = glass.clone(); glass2.position.z = -.74; glass2.rotation.y = Math.PI; g.add(glass2);
  [[-1, 1], [1, 1], [-1, -1], [1, -1]].forEach(([x, z]) => { const wh = cyl(.38, .38, .3, toon('#222'), {seg: 20}); wh.rotation.x = Math.PI / 2; wh.position.set(x * 1.05, .38, z * .75); g.add(wh) });
  const l = sph(.12, flat('#FFF4C0')); l.position.set(1.6, .85, .5); g.add(l); const l2 = l.clone(); l2.position.z = -.5; g.add(l2);
  return g;
}
function moto() {
  const g = new THREE.Group();
  [-1, 1].forEach(x => { const w = cyl(.35, .35, .15, toon('#222'), {seg: 18}); w.rotation.x = Math.PI / 2; w.position.set(x * .8, .35, 0); g.add(w) });
  const b = rbox(1.5, .45, .45, .15, toon('#E85D4E')); b.position.y = .85; g.add(b);
  const box2 = rbox(.7, .7, .7, .08, toon('#F4C542')); box2.position.set(-.5, 1.45, 0); g.add(box2);
  const rider = M3.extra({seed: 5, shirt: '#E85D4E', hair: 2}); rider.scale.setScalar(.75); rider.position.set(.15, .55, 0); rider.rotation.y = Math.PI / 2; g.add(rider); g.userData.rider = rider;
  return g;
}
function tree(s = 1) {
  const g = new THREE.Group(); const tr = cyl(.18 * s, .25 * s, 2.2 * s, toon('#7A5230'), {seg: 10}); tr.position.y = 1.1 * s; g.add(tr);
  [[0, 2.8, 0, 1.1], [.6, 2.4, .2, .8], [-.6, 2.5, -.1, .85], [0, 3.4, 0, .8]].forEach(([x, y, z, r]) => { const c = sph(r * s, toon('#4FAE52')); c.position.set(x * s, y * s, z * s); g.add(c) });
  return g;
}
function lamp() { const g = new THREE.Group(); const p = cyl(.08, .1, 5, toon('#2f3a40'), {seg: 10}); p.position.y = 2.5; g.add(p); const a = box(1, .08, .08, toon('#2f3a40')); a.position.set(.45, 4.95, 0); g.add(a); const h = sph(.22, toon('#FFF1C2', {emissive: '#FFE08A', emissiveIntensity: .4})); h.position.set(.9, 4.8, 0); g.add(h); return g }
function cloud() { const g = new THREE.Group(); [[0, 0, 1.2], [1.2, .2, .9], [-1.2, .1, .9], [.4, .6, .9]].forEach(([x, y, r]) => { const c = new THREE.Mesh(new THREE.SphereGeometry(r, 16, 12), flat('#FFFFFF')); c.position.set(x, y, 0); g.add(c) }); return g }
function npcs(S, list) { return list.map(([x, z, ry, o]) => { const e = M3.extra(o); e.position.set(x, 0, z); e.rotation.y = ry || 0; S.add(e); return e }) }

// ───────────── DEPARTAMENTO DE MONI: living + escritorio ─────────────
function depto() {
  const S = baseScene('#F3E2C8', {sunPos: [-10, 12, 6], sunI: 2.0});
  const wood = texWood(); wood.repeat.set(3, 3);
  const floor = plane(40, 30, toon('#fff', {map: wood})); floor.rotation.x = -Math.PI / 2; S.add(floor);
  const wallC = '#F2DDBE';
  const back = plane(40, 12, toon(wallC)); back.position.set(0, 6, -6); S.add(back);
  const left = plane(30, 12, toon('#EDD3AE')); left.rotation.y = Math.PI / 2; left.position.set(-12, 6, 6); S.add(left);
  const base = box(40, .4, .1, toon('#FFFFFF')); base.position.set(0, .2, -5.95); S.add(base);
  // ventana grande con vista a la ciudad
  const view = new THREE.Group(); view.position.set(4.5, 0, -14); S.add(view);
  const skyP = plane(30, 16, flat('#9FD8F2')); skyP.position.set(0, 8, -4); view.add(skyP);
  [[-6, 4, 7, '#E9A96B'], [-2, 3.5, 10, '#8FB1D9'], [2, 4, 8, '#C98BB9'], [6, 3.5, 11, '#9CCB8A'], [9.5, 3, 6.5, '#E8C26B']].forEach(([x, w, h, c]) => { const b = building(w, h, 3, c, {rows: Math.round(h / 1.4)}); b.position.set(x, 0, 0); view.add(b) });
  const cars = [car('#E85D4E'), car('#4B8FD8')]; cars.forEach((c, i) => { c.scale.setScalar(.7); c.position.set(0, 0, 3 + i * 1.6); view.add(c) });
  const frame = new THREE.Group(); frame.position.set(4.5, 0, -5.9); S.add(frame);
  [[0, 7.2, 7.4, .3], [0, 2.1, 7.4, .3], [-3.6, 4.65, .3, 5.4], [3.6, 4.65, .3, 5.4], [0, 4.65, .2, 5.2], [0, 4.65, 7.2, .15]].forEach(([x, y, w, h]) => { const b = box(w, h, .3, toon('#FFFFFF')); b.position.set(x, y, 0); frame.add(b) });
  // cortar la pared detrás de la ventana: dos paneles de pared alrededor
  back.visible = false;
  [[-9.6, 6, 21.2, 12], [14.1, 6, 11.8, 12], [4.5, 9.67, 7.4, 4.66], [4.5, 1, 7.4, 2]].forEach(([x, y, w, h]) => { const p = plane(w, h, toon(wallC)); p.position.set(x, y, -6); S.add(p) });
  const curtain = [-1, 1].map(s => { const c = rbox(1.2, 5.6, .15, .1, toon('#E85D4E')); c.position.set(4.5 + s * 4.3, 4.6, -5.7); S.add(c); return c });
  // sillón, mesa ratona, alfombra, planta, lámpara, cuadro, reloj, biblioteca
  const rug = new THREE.Mesh(new THREE.CircleGeometry(4.2, 40), toon('#C8B6E2')); rug.rotation.x = -Math.PI / 2; rug.position.set(-3.5, .02, 1.2); rug.scale.x = 1.35; S.add(rug);
  const sofa = new THREE.Group(); sofa.position.set(-3.5, 0, -3.6); S.add(sofa);
  const seat = rbox(6.4, .9, 2.2, .3, toon('#3F6FB8')); seat.position.y = .85; sofa.add(seat);
  const backr = rbox(6.6, 2.0, .7, .3, toon('#3A64A8')); backr.position.set(0, 1.9, -.85); sofa.add(backr);
  [-1, 1].forEach(s => { const arm = rbox(.7, 1.5, 2.3, .3, toon('#3A64A8')); arm.position.set(s * 3.4, 1.15, 0); sofa.add(arm) });
  [-1.5, 1.5].forEach(x => { const cu = rbox(2.6, .5, 1.8, .2, toon('#5C88CC')); cu.position.set(x, 1.5, .1); sofa.add(cu) });
  const ct = new THREE.Group(); ct.position.set(-3.5, 0, 1.6); S.add(ct);
  const ctt = rbox(3.2, .2, 1.6, .1, toon('#8A5A3B')); ctt.position.y = 1.05; ct.add(ctt);
  [[-1.3, -.6], [1.3, -.6], [-1.3, .6], [1.3, .6]].forEach(([x, z]) => { const l = cyl(.07, .07, 1, toon('#5a3a26'), {seg: 8}); l.position.set(x, .5, z); ct.add(l) });
  const mug = cyl(.22, .19, .38, toon('#FFFFFF')); mug.position.set(-.6, 1.35, .1); ct.add(mug);
  const plant = new THREE.Group(); plant.position.set(-9.5, 0, -4.2); S.add(plant);
  const pot = cyl(.6, .45, 1.1, toon('#C46A3C')); pot.position.y = .55; plant.add(pot);
  const leaves = []; for (let i = 0; i < 7; i++) { const l = sph(.45, toon(i % 2 ? '#3FAE6B' : '#4FBF72')); l.scale.set(.5, 1.4, .25); const a = i / 7 * Math.PI * 2; l.position.set(Math.cos(a) * .45, 1.9, Math.sin(a) * .45); l.rotation.z = Math.cos(a) * .6; l.rotation.x = Math.sin(a) * .6; plant.add(l); leaves.push(l) }
  const lampG = new THREE.Group(); lampG.position.set(1.2, 0, -4.4); S.add(lampG);
  const lp = cyl(.06, .06, 4.2, toon('#2f2f2f'), {seg: 8}); lp.position.y = 2.1; lampG.add(lp); const shade = cyl(.45, .75, .8, toon('#F7E7C6', {emissive: '#FFD38A', emissiveIntensity: .3})); shade.position.y = 4.3; lampG.add(shade);
  const pic = new THREE.Group(); pic.position.set(-3.5, 5.3, -5.9); S.add(pic);
  const pf = box(3, 1.9, .12, toon('#5a3a26')); pic.add(pf);
  const pimg = plane(2.7, 1.6, toon('#fff', {map: canvasTex(270, 160, g => { g.fillStyle = '#9FD8F2'; g.fillRect(0, 0, 270, 160); g.fillStyle = '#7CC46A'; g.beginPath(); g.moveTo(0, 160); g.lineTo(90, 60); g.lineTo(170, 130); g.lineTo(230, 80); g.lineTo(270, 120); g.lineTo(270, 160); g.fill(); g.fillStyle = '#FFE27A'; g.beginPath(); g.arc(210, 40, 18, 0, 7); g.fill() })})); pimg.position.z = .07; pic.add(pimg);
  const clock = new THREE.Group(); clock.position.set(-8.5, 6.5, -5.9); S.add(clock);
  const cf = cyl(.7, .7, .12, toon('#FFFFFF'), {seg: 40}); cf.rotation.x = Math.PI / 2; clock.add(cf);
  const hand1 = box(.06, .5, .03, flat('#222'), {outline: false}); hand1.geometry.translate(0, .25, 0); hand1.position.z = .08; clock.add(hand1);
  const hand2 = box(.05, .38, .03, flat('#C8102E'), {outline: false}); hand2.geometry.translate(0, .19, 0); hand2.position.z = .09; clock.add(hand2);
  const shelf = new THREE.Group(); shelf.position.set(-11.5, 0, 0); shelf.rotation.y = Math.PI / 2; S.add(shelf);
  const sh = box(4, 6, .9, toon('#8A5A3B')); sh.position.y = 3; shelf.add(sh);
  for (let r = 0; r < 4; r++) for (let i = 0; i < 6; i++) { const bk = box(.35, 1 + (i % 3) * .15, .6, toon(['#E85D4E', '#4B8FD8', '#F4C542', '#3FAE6B', '#A66BC9'][(r + i) % 5]), {t: .02}); bk.position.set(-1.5 + i * .55, .9 + r * 1.45, .2); shelf.add(bk) }
  // escritorio (zona de "la foto"): mesa con papeles, laptop, celular y lámpara
  const desk = new THREE.Group(); desk.position.set(7.5, 0, 2.4); desk.rotation.y = -.2; S.add(desk);
  const dt = rbox(4.6, .2, 2.4, .08, toon('#F1E4CF')); dt.position.y = 1.85; desk.add(dt);
  [[-2.1, -1], [2.1, -1], [-2.1, 1], [2.1, 1]].forEach(([x, z]) => { const l = cyl(.08, .08, 1.85, toon('#3b2a20'), {seg: 8}); l.position.set(x, .92, z); desk.add(l) });
  const lap = new THREE.Group(); lap.position.set(1.2, 1.97, -.2); lap.rotation.y = Math.PI + .7; lap.scale.setScalar(.85); desk.add(lap);
  const lb = rbox(1.6, .08, 1.1, .05, toon('#B8C0C8')); lap.add(lb); const ls = rbox(1.6, 1.0, .06, .05, toon('#2f3740')); ls.position.set(0, .5, -.55); ls.rotation.x = -.2; lap.add(ls);
  const lsc = plane(1.45, .85, toon('#fff', {map: canvasTex(290, 170, g => { g.fillStyle = '#EAF6EF'; g.fillRect(0, 0, 290, 170); g.fillStyle = '#0E5A40'; g.fillRect(0, 0, 290, 30); g.fillStyle = '#fff'; g.font = font(18); g.fillText('Mi banco', 10, 21); g.fillStyle = '#14221D'; g.font = font(22); ['Ingresos', 'Gastos', 'Tarjeta'].forEach((s, i) => g.fillText(s, 14, 66 + i * 36)); g.fillStyle = '#17865A'; g.fillText('$1.200', 190, 66); g.fillStyle = '#C8102E'; g.fillText('$1.150', 190, 102); g.fillText('$900', 200, 138) })}));
  lsc.position.set(0, .51, -.51); lsc.rotation.x = -.2; lap.add(lsc);
  const papers = []; for (let i = 0; i < 4; i++) { const p = plane(.9, 1.2, toon('#FFFFFF')); p.rotation.x = -Math.PI / 2; p.rotation.z = (i - 1.5) * .25; p.position.set(-1.2 + i * .25, 1.97 + i * .005, .3); desk.add(p); papers.push(p) }
  const chair = new THREE.Group(); chair.position.set(7.5, 0, .5); chair.rotation.y = -.2 + Math.PI; S.add(chair);
  const cs = rbox(1.6, .2, 1.5, .1, toon('#C46A3C')); cs.position.y = 1.45; chair.add(cs);
  const cb = rbox(1.6, 1.6, .2, .1, toon('#C46A3C')); cb.position.set(0, 2.3, .7); chair.add(cb);
  [[-.65, -.6], [.65, -.6], [-.65, .6], [.65, .6]].forEach(([x, z]) => { const l = cyl(.06, .06, 1.45, toon('#3b2a20'), {seg: 8}); l.position.set(x, .72, z); chair.add(l) });
  const wall2 = plane(16, 12, toon('#F7E4C6')); wall2.position.set(14, 6, 0); wall2.rotation.y = -Math.PI / 2; S.add(wall2);
  const cal = M3.prop('calendario', {text: '90'}); cal.position.set(10.4, 5.6, -5.92); cal.scale.setScalar(1.25); S.add(cal);
  const warm = new THREE.PointLight('#FFD9A0', 18, 14); warm.position.set(1.2, 4.6, -3.6); S.add(warm);
  return {
    scene: S,
    spots: {sofaL: {p: [-5, 0, -2.9], ry: .3, sit: 1.75}, sofaR: {p: [-1.9, 0, -2.9], ry: -.3, sit: 1.75}, centro: {p: [-3.5, 0, 3.2], ry: 0},
      escritorio: {p: [7.5, 0, .7], ry: -.2, sit: 1.6}, junto: {p: [9.3, 1.96, 3.5], ry: -.4}, detras: {p: [9.8, 0, -.4], ry: -.5}, flota: {p: [-1.7, 0, -1.3], ry: -.3}, frente: {p: [-3.5, 0, 4.2], ry: 0}},
    cams: {two: {p: [-3.5, 4.6, 6.2], look: [-3.5, 3.2, -2.8], fov: 36}, wide: {p: [1, 5.6, 14], look: [-2, 2.6, -2], fov: 42},
      calendario: {p: [10.4, 5.6, -2.6], look: [10.4, 5.6, -5.9], fov: 32},
      deskWide: {p: [4.6, 4.2, 9.5], look: [7.6, 2.8, 1.4], fov: 34}, deskOver: {p: [3.6, 4.9, 7.8], look: [8.2, 2.9, 1.4], fov: 36}},
    update(t) {
      cars[0].position.x = -9 + ((t * 2.2) % 18); cars[1].position.x = 9 - ((t * 1.7 + 9) % 18); cars[1].rotation.y = Math.PI;
      curtain.forEach((c, i) => c.rotation.z = Math.sin(t * .9 + i) * .02);
      leaves.forEach((l, i) => l.rotation.y = Math.sin(t * .7 + i) * .05);
      hand1.rotation.z = -t * .02; hand2.rotation.z = -Math.floor(t) * Math.PI / 30;
    },
  };
}

// ───────────── CALLE CON EDIFICIOS, AUTOS Y GENTE ─────────────
function calle() {
  const S = baseScene('#9FDCF5', {sunPos: [12, 18, 8], sunI: 2.5});
  const road = plane(140, 9, toon('#5C6066')); road.rotation.x = -Math.PI / 2; S.add(road);
  for (let x = -70; x < 70; x += 6) { const l = plane(3, .25, flat('#F4F4F4')); l.rotation.x = -Math.PI / 2; l.position.set(x, .01, 0); S.add(l) }
  [-1, 1].forEach(s => { const sw = box(140, .3, 5, toon('#D9D3C7')); sw.position.set(0, .15, s * 7); S.add(sw) });
  const grass = plane(140, 40, toon('#86C96F')); grass.rotation.x = -Math.PI / 2; grass.position.set(0, -.01, -30); S.add(grass);
  const colors = ['#E9A96B', '#8FB1D9', '#C98BB9', '#9CCB8A', '#E8C26B', '#F08A7E', '#7FC8C8'];
  let x = -40; let k = 0; while (x < 40) { const w = 5 + (k % 3) * 1.5, h = 7 + ((k * 5) % 4) * 2.5; const b = building(w, h, 5, colors[k % colors.length], {balcony: k % 2 === 0}); b.position.set(x + w / 2, 0, -12); S.add(b); x += w + .4; k++ }
  x = -40; k = 3; while (x < 40) { const w = 5 + (k % 3) * 1.5, h = 6 + ((k * 3) % 4) * 2; const b = building(w, h, 5, colors[k % colors.length]); b.position.set(x + w / 2, 0, 12); b.rotation.y = Math.PI; S.add(b); x += w + .4; k++ }
  // fachadas con carteles: café, banco, se alquila
  const cafeF = new THREE.Group(); cafeF.position.set(-6, 0, -9.4); S.add(cafeF);
  const awn = rbox(6, .25, 1.8, .1, toon('#E85D4E')); awn.position.set(0, 3.6, .8); awn.rotation.x = .25; cafeF.add(awn);
  const cs = sign('CAFÉ', {w: 3.2, h: .9, bg: '#7A4A2C'}); cs.position.set(0, 4.6, .3); cafeF.add(cs);
  const door = box(1.6, 2.8, .2, toon('#5a3a26')); door.position.set(-1.8, 1.4, 0); cafeF.add(door);
  const shop = plane(3, 2.2, toon('#CFEFFF')); shop.position.set(1, 1.6, .12); cafeF.add(shop);
  const bancoF = sign('BANCO', {w: 3.4, h: .9, bg: '#0E5A40'}); bancoF.position.set(9, 4.8, -9.3); S.add(bancoF);
  const alq = sign('SE ALQUILA', {w: 3, h: .8, bg: '#C8102E'}); alq.position.set(19, 6.5, -9.3); S.add(alq);
  const gym = sign('GIMNASIO', {w: 3.6, h: .9, bg: '#2F6DB5'}); gym.position.set(1.5, 4.6, -9.3); S.add(gym);
  const gymW = plane(4, 2.2, toon('#CFEFFF')); gymW.position.set(1.5, 1.8, -9.35); S.add(gymW);
  const alq2 = sign('SE ALQUILA', {w: 2.6, h: .7, bg: '#C8102E'}); alq2.position.set(-14, 3.2, -9.3); S.add(alq2);
  const libre = x => (x > -17.5 && x < -10.5) || (x > -2.5 && x < 4.5); // sin árboles ni faroles delante de los personajes
  for (let i = -36; i < 40; i += 9) { if (!libre(i)) { const tr = tree(1); tr.position.set(i, .3, -6.2); S.add(tr) } if (!libre(i + 4.5)) { const lp = lamp(); lp.position.set(i + 4.5, .3, -5.6); S.add(lp) } }
  const clouds = [0, 1, 2, 3].map(i => { const c = cloud(); c.position.set(-30 + i * 18, 22 + (i % 2) * 3, -30); c.scale.setScalar(1.6); S.add(c); return c });
  const traffic = [car('#E85D4E'), car('#4B8FD8'), car('#F4C542'), car('#3FAE6B')]; traffic.forEach(c => S.add(c));
  const mt = moto(); S.add(mt);
  const walkers = npcs(S, [[0, 6.2, Math.PI / 2, {seed: 1}], [0, 7.6, -Math.PI / 2, {seed: 2}], [0, -6.5, Math.PI / 2, {seed: 3}], [0, -7.6, -Math.PI / 2, {seed: 4}], [0, 6.8, Math.PI / 2, {seed: 6}]]);
  return {
    scene: S, spots: {vereda: {p: [-.6, .3, -7.2], ry: .35}, vereda2: {p: [2.6, .3, -7.0], ry: -.35}, alquilaA: {p: [-15.6, .3, -7.3], ry: .3}, alquilaB: {p: [-12.4, .3, -7.1], ry: -.3}},
    cams: {establish: {p: [-22, 7, 6], to: [-15, 4, 5], look: [-5, 3.5, -9], fov: 42}, cafeFront: {p: [-3, 3, 6], to: [-4.6, 3, 3.6], look: [-6, 3.4, -9.4], fov: 40},
      street: {p: [-18, 2.2, 3.5], look: [0, 2, -2], fov: 38}, gymTwo: {p: [3.2, 3.6, 2.2], look: [1, 2.6, -7.2], fov: 38},
      alquilaTwo: {p: [-9.4, 3.4, -3.5], look: [-14, 2.8, -7.8], fov: 40}, bancoFront: {p: [4, 3.2, 5], to: [6, 3.4, 3.2], look: [9, 4, -9.3], fov: 40}},
    update(t) {
      traffic.forEach((c, i) => { const dir = i % 2 ? -1 : 1, sp = 5 + i; const xx = ((t * sp + i * 23) % 90) - 45; c.position.set(dir * xx, 0, dir * 2.1); c.rotation.y = dir > 0 ? 0 : Math.PI });
      mt.position.set(-45 + ((t * 7) % 90), 0, 2.2); mt.userData.rider.anim(t, {sit: true});
      walkers.forEach((w, i) => { const dir = Math.sign(Math.sin(w.rotation.y)) || 1; w.position.x = -30 + ((t * 1.6 * dir + i * 13) % 60 + 60) % 60; w.anim(t, {walk: true, seed: i}) });
      clouds.forEach((c, i) => c.position.x = -40 + ((t * .6 + i * 22) % 90));
    },
  };
}

// ───────────── CAFETERÍA CON FILA Y BARISTA ─────────────
function cafeteria() {
  const S = baseScene('#F3D7AE', {sunPos: [12, 12, 6], sunI: 1.9, hemi: 1.5});
  const wood = texWood('#A8683F', '#B67547'); wood.repeat.set(5, 5);
  const floor = plane(40, 30, toon('#fff', {map: wood})); floor.rotation.x = -Math.PI / 2; S.add(floor);
  const brick = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#C9714A'; g.fillRect(0, 0, w, h); g.fillStyle = '#E9C9A0'; for (let y = 0; y < h; y += 32) { g.fillRect(0, y, w, 3); for (let x = (y / 32) % 2 * 32; x < w; x += 64) g.fillRect(x, y, 3, 32) } }); brick.wrapS = brick.wrapT = THREE.RepeatWrapping; brick.repeat.set(4, 2);
  const back = plane(40, 14, toon('#fff', {map: brick})); back.position.set(0, 7, -9); S.add(back);
  // pared lateral en paneles alrededor de la ventana (ventana: z -3..7, y 1.6..6.8)
  [[-7.5, 7, 9, 14], [13, 7, 12, 14], [2, 10.4, 10, 7.2], [2, .8, 10, 1.6]].forEach(([z, y, w, h]) => { const p = plane(w, h, toon('#EAD2B0')); p.rotation.y = -Math.PI / 2; p.position.set(14, y, z); S.add(p) });
  // afuera: vereda, calle y edificios de enfrente
  const sw = plane(6, 40, toon('#D9D3C7')); sw.rotation.x = -Math.PI / 2; sw.position.set(17, .02, 2); S.add(sw);
  const rd = plane(10, 60, toon('#5C6066')); rd.rotation.x = -Math.PI / 2; rd.position.set(25, .01, 2); S.add(rd);
  [[31, -8, '#8FB1D9'], [31, 0, '#E9A96B'], [31, 8, '#9CCB8A'], [31, 16, '#C98BB9']].forEach(([x, z, c]) => { const b = building(6, 10, 7, c); b.position.set(x, 0, z); b.rotation.y = -Math.PI / 2; S.add(b) });
  const tr1 = tree(1); tr1.position.set(18.5, 0, -1); S.add(tr1);
  // ventanal hacia la calle (con autos que pasan)
  const winG = new THREE.Group(); winG.position.set(13.9, 0, 2); winG.rotation.y = -Math.PI / 2; S.add(winG);
  const glass = plane(10, 5.2, toon('#DFF3FA', {transparent: true, opacity: .18})); glass.position.set(0, 4.2, 0); winG.add(glass);
  const outCar = car('#4B8FD8'); outCar.scale.setScalar(.8); outCar.rotation.y = Math.PI / 2; S.add(outCar);
  [[0, 6.8, 10.4, .3], [0, 1.6, 10.4, .3], [-5.1, 4.2, .3, 5.5], [5.1, 4.2, .3, 5.5], [0, 4.2, .2, 5.3]].forEach(([x, y, w, h]) => { const b = box(w, h, .3, toon('#3b2a20')); b.position.set(x, y, 0); winG.add(b) });
  // mostrador, máquina, vitrina, pizarrón con precios
  const counter = rbox(12, 2.2, 2, .1, toon('#7A4A2C')); counter.position.set(-4, 1.1, -6); S.add(counter);
  const top = rbox(12.4, .2, 2.3, .06, toon('#EFE6D8')); top.position.set(-4, 2.3, -6); S.add(top);
  const mach = rbox(2.2, 1.5, 1.1, .12, toon('#B8C0C8')); mach.position.set(-7.5, 3.15, -6.3); S.add(mach);
  const vit = rbox(2.6, 1.2, 1.4, .08, toon('#DFF3FA', {transparent: true, opacity: .55})); vit.position.set(-1.2, 3, -6); S.add(vit);
  for (let i = 0; i < 5; i++) { const p = sph(.28, toon(i % 2 ? '#E9B05E' : '#C98A3A')); p.scale.set(1.4, .6, 1); p.position.set(-2.1 + i * .45, 2.7, -6); S.add(p) }
  const menu = M3.prop('pizarron', {}); menu.position.set(-4.5, 7.2, -8.9); S.add(menu);
  const lamps = []; for (let i = 0; i < 4; i++) { const l = new THREE.Group(); l.position.set(-9 + i * 5, 0, -1); S.add(l); const c = cyl(.02, .02, 4, flat('#222')); c.position.y = 11; l.add(c); const sh = cyl(.35, .7, .6, toon('#2B2B2B')); sh.position.y = 8.8; l.add(sh); const b = sph(.22, toon('#FFE7B0', {emissive: '#FFD38A', emissiveIntensity: 1.2})); b.position.y = 8.5; l.add(b); lamps.push(l) }
  const pl = new THREE.PointLight('#FFC27A', 30, 18); pl.position.set(0, 7, 0); S.add(pl);
  // mesas
  function table(x, z) { const g = new THREE.Group(); g.position.set(x, 0, z); S.add(g); const t = cyl(1.5, 1.5, .14, toon('#F4EBDD'), {seg: 40}); t.position.y = 2.1; g.add(t); const l = cyl(.12, .12, 2.1, toon('#3B2A20'), {seg: 10}); l.position.y = 1.05; g.add(l); const f = cyl(.6, .6, .06, toon('#3B2A20'), {seg: 24}); f.position.y = .03; g.add(f); return g }
  const main = table(0, 2.5);
  const cup = cyl(.25, .21, .42, toon('#FFFFFF')); cup.position.set(-.4, 2.38, .5); main.add(cup); const coffee = cyl(.22, .22, .02, flat('#5A3420')); coffee.position.set(-.4, 2.6, .5); main.add(coffee);
  const med = sph(.3, toon('#E9B05E')); med.scale.set(1.5, .55, .8); med.position.set(.5, 2.3, .4); main.add(med);
  [[-2.4, 2.4], [2.4, 2.4]].forEach(([x, z]) => { const ch = rbox(1.5, .2, 1.4, .1, toon('#C46A3C')); ch.position.set(x, 1.45, z); S.add(ch); [[-.6, -.55], [.6, -.55], [-.6, .55], [.6, .55]].forEach(([a, b]) => { const l = cyl(.05, .05, 1.45, toon('#3b2a20'), {seg: 8}); l.position.set(x + a, .72, z + b); S.add(l) }) });
  table(8, -1); table(-9, 3);
  // fila de clientes y barista
  const queue = npcs(S, [[-3, -3.6, 0, {seed: 1, kind: 4}], [-1.4, -2.6, -.3, {seed: 2, kind: 2}], [.3, -1.8, -.5, {seed: 3, kind: 1}], [1.9, -1.2, -.6, {seed: 7}]]);
  queue.forEach(q => q.rotation.y = Math.PI);
  const barista = M3.extra({seed: 9, shirt: '#2B2B2B', hair: 2}); barista.position.set(-6, 0, -7.6); S.add(barista);
  const seated = npcs(S, [[8, 1.0, Math.PI, {seed: 4, kind: 3}], [-9.6, 5.2, Math.PI * .85, {seed: 6, kind: 2}], [8, -3.1, 0, {seed: 11, kind: 1}]]);
  seated.forEach(q => { const ch = rbox(1.4, .2, 1.3, .1, toon('#C46A3C')); ch.position.set(q.position.x, 1.45, q.position.z); S.add(ch);
    [[-.55, -.5], [.55, -.5], [-.55, .5], [.55, .5]].forEach(([a, b]) => { const l = cyl(.05, .05, 1.45, toon('#3b2a20'), {seg: 8}); l.position.set(q.position.x + a, .72, q.position.z + b); S.add(l) });
    q.position.y = 1.55 - (q.legY0 - q.sitDrop) * q.scale.y; });
  return {
    scene: S, props: {menu},
    spots: {mesaA: {p: [-2.4, 0, 2.6], ry: .55, sit: 1.55}, mesaB: {p: [2.4, 0, 2.6], ry: -.55, sit: 1.55}, llega: {p: [4.2, 0, 4.4], ry: -.7}},
    cams: {two: {p: [0, 4, 11], look: [0, 2.6, 1.5], fov: 34}, wide: {p: [9, 7, 15], look: [-2, 2.8, -2], fov: 42}, queue: {p: [5, 4, 6], look: [-2, 3, -4], fov: 36},
      menu: {p: [-3.2, 6.4, -1.4], look: [-4.5, 7.0, -8.9], fov: 34}},
    update(t) {
      queue.forEach((q, i) => { q.anim(t, {seed: i, talk: i === 1 && (t % 6) < 3}); q.rotation.y = Math.PI + Math.sin(t * .5 + i) * .4 });
      barista.position.x = -6 + Math.sin(t * .6) * 2.2; barista.rotation.y = Math.cos(t * .6) > 0 ? .3 : -.3; barista.anim(t, {pose: 'hold', poseW: 1, seed: 9});
      seated.forEach((q, i) => q.anim(t, {sit: true, seed: 4 + i, talk: (t + i * 3) % 7 < 3}));
      outCar.position.set(23.5, 0, -20 + ((t * 4) % 44));
    },
  };
}


// ───────────── BANCO: columnas, ventanillas, fila con cinta, cajero automático ─────────────
function banco() {
  const S = baseScene('#EDE3D2', {sunPos: [-8, 14, 10], sunI: 1.9, hemi: 1.5});
  const marble = texTiles('#EFE9DF', '#E2DACB', 6); marble.repeat.set(6, 6);
  const floor = plane(44, 32, toon('#fff', {map: marble})); floor.rotation.x = -Math.PI / 2; S.add(floor);
  const back = plane(44, 14, toon('#E6DCCB')); back.position.set(0, 7, -9); S.add(back);
  const side = plane(32, 14, toon('#DDD1BC')); side.rotation.y = Math.PI / 2; side.position.set(-16, 7, 4); S.add(side);
  const logo = sign('BANCO', {w: 5, h: 1.3, bg: '#0E5A40'}); logo.position.set(0, 9.6, -8.9); S.add(logo);
  [-12, -6, 6, 12].forEach(x => { const col = cyl(.7, .7, 12, toon('#F7F2EA'), {seg: 24}); col.position.set(x, 6, -7.6); S.add(col); const cap = box(1.9, .5, 1.9, toon('#E9E0CF')); cap.position.set(x, 11.8, -7.6); S.add(cap) });
  const counter = rbox(16, 2.4, 1.6, .1, toon('#6E4B33')); counter.position.set(0, 1.2, -5.2); S.add(counter);
  const ctop = rbox(16.4, .2, 1.9, .06, toon('#F2ECE2')); ctop.position.set(0, 2.45, -5.2); S.add(ctop);
  [-5, 0, 5].forEach(x => { const gl = plane(4.2, 2.2, toon('#DFF3FA', {transparent: true, opacity: .35})); gl.position.set(x, 3.7, -5.2); S.add(gl); const fr = box(4.4, .12, .12, toon('#3b3b3b')); fr.position.set(x, 4.85, -5.2); S.add(fr);
    const num = sign(['1', '2', '3'][(x + 5) / 5], {w: .7, h: .7, bg: '#0E5A40'}); num.position.set(x, 5.4, -5.2); S.add(num) });
  const tellers = npcs(S, [[-5, -6.6, 0, {seed: 12, kind: 3}], [0, -6.6, 0, {seed: 13, kind: 3}], [5, -6.6, 0, {seed: 14, kind: 3}]]);
  // fila con postes y cinta
  for (let i = 0; i < 5; i++) { const p = cyl(.08, .1, 1.6, toon('#C9A24A'), {seg: 10}); p.position.set(-9 + i * 1.8, .8, 1.4); S.add(p); if (i < 4) { const r = box(1.8, .1, .05, toon('#C8102E'), {outline: false}); r.position.set(-8.1 + i * 1.8, 1.35, 1.4); S.add(r) } }
  const queue = npcs(S, [[-8, -.2, Math.PI, {seed: 15}], [-6.2, .1, Math.PI, {seed: 16, kind: 2}], [-4.4, -.1, Math.PI, {seed: 17, kind: 4}]]);
  const atm = new THREE.Group(); atm.position.set(12.5, 0, -2); atm.rotation.y = -Math.PI / 2 + .3; S.add(atm);
  const ab = rbox(2, 4, 1.4, .15, toon('#2F6DB5')); ab.position.y = 2; atm.add(ab); const as = plane(1.3, .9, toon('#BFE6F7', {emissive: '#9FD8F2', emissiveIntensity: .4})); as.position.set(0, 2.9, .72); atm.add(as);
  const plant = sph(.9, toon('#4FAE52')); plant.position.set(-13.5, 2.2, -6); S.add(plant); const pot = cyl(.6, .45, 1.2, toon('#C46A3C')); pot.position.set(-13.5, .6, -6); S.add(pot);
  return {
    scene: S,
    spots: {ventanilla: {p: [-1.4, 0, -2.6], ry: .25}, junto: {p: [1.6, 0, -2.4], ry: -.3}, flota: {p: [2.4, 0, -1.6], ry: -.35}},
    cams: {two: {p: [0, 4.2, 7.5], look: [0, 2.8, -2.6], fov: 38}, wide: {p: [8, 7, 15], look: [-1, 3, -3], fov: 44}, est: {p: [-12, 5, 14], to: [-8, 4.4, 11], look: [0, 4, -6], fov: 44}},
    update(t) {
      tellers.forEach((q, i) => { q.anim(t, {seed: 12 + i, talk: (t + i * 2) % 6 < 2.5}); q.rotation.y = Math.sin(t * .4 + i) * .3 });
      queue.forEach((q, i) => { q.anim(t, {seed: 15 + i}); q.rotation.y = Math.PI + Math.sin(t * .5 + i) * .35 });
    },
  };
}

const CACHE = {};
M3.lugar = function (nombre) {
  if (!CACHE[nombre]) CACHE[nombre] = ({depto, calle, cafeteria, banco})[nombre]();
  return CACHE[nombre];
};
})();
