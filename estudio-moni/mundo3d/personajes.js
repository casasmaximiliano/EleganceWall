// Personajes del mundo 3D. Principales (detallados) y gente de fondo (simple). Expone M3.personaje(tipo) y M3.extra(opciones).
// Cada personaje: Group con .face (expresiones), .arms [izq, der], .legs, .rig.body (lo que se balancea),
// y .anim(t, estado) donde estado = {talk: 0-1, expr, gesture, sit, walk, seed}.
(function () {
const {toon, flat, box, rbox, cyl, sph, cap, plane, canvasTex, font} = M3;

function rig(root, o) {
  const body = new THREE.Group(); root.add(body);           // se mueve con respiración, rebote y squash
  root.rig = {body, height: o.height};
  return body;
}
function attachLimbs(root, body, o) {
  root.arms = [-1, 1].map(side => M3.arm(body, {x: side * o.armX, y: o.armY, z: o.armZ || 0, color: o.limb, handColor: o.hand, side, len: o.armLen, len2: o.armLen2}));
  root.legs = [-1, 1].map(side => M3.leg(root, {x: side * o.legX, y: o.legY, color: o.limb, len: o.legLen, shoe: o.shoe}));
}

// Poses de brazos con sentido (lado derecho; el izquierdo se espeja). [x, z, codoX, codoZ]
const POSES = {
  rest:    {R: [0, .22, -.15, 0],    L: [0, .22, -.15, 0]},
  open:    {R: [-.85, .45, -.75, 0], L: [-.85, .45, -.75, 0]},        // explica con las dos manos adelante
  chest:   {R: [-1.15, .05, -2.0, 0], L: [0, .22, -.15, 0]},          // "yo", "me", "mi": mano al pecho
  point:   {R: [-1.35, .55, -.1, 0], L: [0, .25, -.2, 0]},            // "vos", "te": señala al otro
  palmsUp: {R: [-.6, .75, -1.0, 0],  L: [-.6, .75, -1.0, 0]},         // pregunta: palmas arriba
  count:   {R: [-.35, 1.35, -.9, 0], L: [0, .22, -.15, 0]},           // número: levanta la mano
  armsUp:  {R: [0, 2.35, .25, 0],    L: [0, 2.35, .25, 0]},           // sorpresa
  no:      {R: [-1.0, .4, -1.25, 0], L: [0, .22, -.15, 0]},           // "no": mueve la mano
  think:   {R: [-1.5, .3, -2.2, 0],  L: [-.6, .1, -1.6, 0]},          // pensando: mano al mentón
  hold:    {R: [-1.1, .35, -.5, 0],  L: [-1.1, .35, -.5, 0]},
  cross:   {R: [-1.2, .15, -1.7, 0], L: [-1.2, .15, -1.7, 0]},        // enojo: brazos cruzados
  wave:    {R: [0, 2.5, .4, 0],      L: [0, .25, -.2, 0]},
  hips:    {R: [-.2, .9, -1.9, 0],   L: [-.2, .9, -1.9, 0]},          // manos en la cintura
};
M3.POSES = POSES;
const smooth = x => { x = M3.clamp(x); return x * x * (3 - 2 * x) };

// Animación común. estado: {talk, expr, pose, poseW (0-1), sit, walk, seed, nod (0-1), turn (rad), lean, emph (0-1)}
function animate(c, t, st) {
  const talk = st.talk || 0, seed = st.seed || 0, B = c.rig.body;
  const breath = Math.sin(t * 2.0 + seed) * .01;
  const emph = st.emph || 0;                                  // énfasis en palabras acentuadas (lo calcula el director)
  B.scale.set(1 - emph * .03 + breath, 1 + emph * .045 - breath, 1);
  B.position.y = (st.sit ? -(c.sitDrop || .6) : 0) + emph * .05;
  B.rotation.z = talk ? M3.noise(t * .5, seed) * .03 : M3.noise(t * .25, seed) * .012;
  B.rotation.x = (st.lean || 0) + (st.nod || 0) * .12 + emph * .03;
  B.rotation.y = st.turn || 0;
  c.face.set(st.expr || 'happy', .3);
  c.face.update(t, talk ? (.3 + .7 * Math.abs(Math.sin(t * 12.5 + Math.sin(t * 4.3) * 1.5))) : 0, seed, st.lookX || 0);
  // brazos: mezcla entre reposo y la pose del momento
  const P = POSES[st.pose] || POSES.rest, Rst = POSES[st.idle || 'rest'] || POSES.rest, w = smooth(st.poseW ?? 1);
  c.arms.forEach(a => {
    const s = a.userData.side, el = a.userData.el, key = s > 0 ? 'R' : 'L';
    const v = P[key].map((x, i) => M3.lerp(Rst[key][i], x, w));
    let wig = 0, ez = v[3];
    if (st.pose === 'no' && s > 0) ez += Math.sin(t * 11) * .45 * w;
    if (st.pose === 'wave' && s > 0) ez += Math.sin(t * 10) * .5 * w;
    if (talk && w > .5 && st.pose !== 'rest') wig = Math.sin(t * 4.2 + s) * .06;   // leve gesticulación, no balanceo
    a.rotation.set(v[0] + wig, 0, s * (v[1] + Math.sin(t * 1.1 + s + seed) * .02));
    el.rotation.set(v[2] - wig * .8, 0, s * ez);
  });
  // piernas
  c.legs.forEach((l, i) => {
    if (st.sit) { l.rotation.x = -1.45; l.position.y = c.legY0 - (c.sitDrop || .6) + .05 }
    else { l.position.y = c.legY0; l.rotation.x = st.walk ? Math.sin(t * 8 + i * Math.PI) * .45 : 0 }
  });
  if (st.walk) c.rig.body.position.y += Math.abs(Math.sin(t * 8)) * .05;
}

// ───── MONI: moneda dorada con canto, borde, $ grabado y brote ─────
function moni() {
  const c = new THREE.Group(); const B = rig(c, {height: 3.3});
  const gold = toon('#F8C02E'), goldD = toon('#D99A16'), goldE = toon('#E8AE22');
  const coin = cyl(1, 1, .34, gold, {seg: 64}); coin.rotation.x = Math.PI / 2; coin.position.y = 2.05; B.add(coin);
  const rim = new THREE.Mesh(new THREE.TorusGeometry(.97, .075, 14, 64), goldD); rim.position.set(0, 2.05, .17); B.add(rim);
  const rimB = rim.clone(); rimB.position.z = -.17; B.add(rimB);
  for (let i = 0; i < 40; i++) { const a = i / 40 * Math.PI * 2; const d = new THREE.Mesh(new THREE.SphereGeometry(.018, 6, 4), goldD); d.position.set(Math.cos(a) * .86, 2.05 + Math.sin(a) * .86, .175); B.add(d) }
  const dollar = plane(.32, .32, new THREE.MeshToonMaterial({map: canvasTex(128, 128, g => { g.fillStyle = '#B9800F'; g.font = font(108); g.textAlign = 'center'; g.fillText('$', 64, 104) }), transparent: true, gradientMap: M3.grad}));
  dollar.position.set(0, 2.72, .176); B.add(dollar);
  const stem = cyl(.045, .055, .38, toon('#2E8B57'), {seg: 10}); stem.position.set(0, 3.22, 0); B.add(stem);
  [-1, 1].forEach(s => { const leaf = sph(.24, toon('#3FBF6B')); leaf.scale.set(1.6, .32, .85); leaf.position.set(s * .3, 3.43, 0); leaf.rotation.z = s * .45; B.add(leaf) });
  c.face = M3.face(B, {y: 2.02, z: .2, s: 1, lidColor: '#F3B524'});
  attachLimbs(c, B, {armX: .97, armY: 2.0, limb: '#8A5A1F', hand: '#F7BC2B', legX: .38, legY: 1.05, legLen: .85});
  c.legY0 = 1.05; c.sitDrop = .75; c.anim = (t, st) => animate(c, t, st); c.eye = new THREE.Vector3(0, 2.1, 0); return c;
}
// ───── CENTAVITO: moneda de cobre más chica, primo de Moni ─────
function centavito() {
  const c = new THREE.Group(); const B = rig(c, {height: 2.4});
  const cu = toon('#D9824A'), cuD = toon('#9E5527');
  const coin = cyl(.72, .72, .26, cu, {seg: 56}); coin.rotation.x = Math.PI / 2; coin.position.y = 1.6; B.add(coin);
  const rim = new THREE.Mesh(new THREE.TorusGeometry(.7, .06, 12, 56), cuD); rim.position.set(0, 1.6, .13); B.add(rim);
  c.face = M3.face(B, {y: 1.58, z: .15, s: .78, lidColor: '#D07A40'});
  attachLimbs(c, B, {armX: .7, armY: 1.55, limb: '#6B3A1A', hand: '#E09060', legX: .28, legY: .85, legLen: .68, armLen: .38, armLen2: .34});
  c.legY0 = .85; c.sitDrop = .6; c.anim = (t, st) => animate(c, t, st); c.eye = new THREE.Vector3(0, 1.6, 0); return c;
}
// ───── TARJETÍN: tarjeta de crédito frambuesa con chip dorado ─────
function tarjetin() {
  const c = new THREE.Group(); const B = rig(c, {height: 3.1});
  const card = rbox(2.0, 1.32, .14, .16, toon('#E0306A')); card.position.y = 2.05; B.add(card);
  const chip = rbox(.36, .28, .03, .05, toon('#F2C14E')); chip.position.set(-.55, 2.28, .09); B.add(chip);
  const stripe = plane(1.6, .08, toon('#B0174D')); stripe.position.set(0, 1.55, .085); B.add(stripe);
  const nums = plane(1.2, .14, new THREE.MeshToonMaterial({map: canvasTex(512, 60, g => { g.fillStyle = '#FFD1DF'; g.font = font(44, 700); g.fillText('••••  ••••  4040', 8, 46) }), transparent: true, gradientMap: M3.grad}));
  nums.position.set(.15, 1.62, .086); B.add(nums);
  c.face = M3.face(B, {y: 2.05, z: .1, s: .95, lidColor: '#C9265C', cheek: '#FF8FB0'});
  attachLimbs(c, B, {armX: 1.02, armY: 2.0, limb: '#7A1035', hand: '#E0306A', legX: .45, legY: 1.4, legLen: 1.15});
  c.legY0 = 1.4; c.sitDrop = 1.0; c.anim = (t, st) => animate(c, t, st); c.eye = new THREE.Vector3(0, 2.1, 0); return c;
}
// ───── CAFECITO: vaso de café para llevar con tapa y vapor ─────
function cafecito() {
  const c = new THREE.Group(); const B = rig(c, {height: 3.4});
  const cup = cyl(.88, .68, 2.0, toon('#F6ECDD'), {seg: 48}); cup.position.y = 2.0; B.add(cup);
  const band = cyl(.79, .72, .45, toon('#7A4A2C'), {seg: 48}); band.position.y = 1.45; B.add(band);
  const lid = cyl(.95, .93, .18, toon('#FFFFFF'), {seg: 48}); lid.position.y = 3.05; B.add(lid);
  const lid2 = cyl(.72, .88, .14, toon('#FFFFFF'), {seg: 48}); lid2.position.y = 3.2; B.add(lid2);
  c.face = M3.face(B, {y: 2.25, z: .86, s: .9, lidColor: '#EADCC7'});
  c.steam = []; for (let i = 0; i < 7; i++) { const s = new THREE.Mesh(new THREE.SphereGeometry(.13, 12, 8), toon('#FFFFFF', {transparent: true, opacity: .6})); B.add(s); c.steam.push(s) }
  attachLimbs(c, B, {armX: .86, armY: 2.25, limb: '#5A3420', hand: '#F6ECDD', legX: .34, legY: 1.0, legLen: .8});
  c.legY0 = 1.0; c.sitDrop = .75;
  c.anim = (t, st) => { animate(c, t, st); c.steam.forEach((s, i) => { const p = (t * .45 + i / 7) % 1; s.position.set(Math.sin(p * 6 + i) * .18, 3.35 + p * 1.5, 0); s.scale.setScalar(.6 + p * 1.2); s.material.opacity = .55 * (1 - p) }) };
  c.eye = new THREE.Vector3(0, 2.3, 0); return c;
}
// ───── DELIVY: bolsa de delivery de papel con gorra ─────
function delivy() {
  const c = new THREE.Group(); const B = rig(c, {height: 3.4});
  const bag = rbox(1.7, 2.0, 1.1, .08, toon('#C9A26B')); bag.position.y = 2.05; B.add(bag);
  const fold = rbox(1.72, .25, 1.12, .05, toon('#B58A52')); fold.position.y = 3.0; B.add(fold);
  const capTop = sph(.6, toon('#2F6DB5')); capTop.scale.set(1, .55, 1); capTop.position.set(0, 3.2, 0); B.add(capTop);
  const visor = cyl(.55, .55, .06, toon('#245A99'), {seg: 32}); visor.scale.set(1, 1, .7); visor.position.set(0, 3.12, .45); B.add(visor);
  const logo = plane(.9, .3, new THREE.MeshToonMaterial({map: canvasTex(256, 86, g => { g.fillStyle = '#E85D4E'; g.fillRect(0, 0, 256, 86); g.fillStyle = '#fff'; g.font = font(54); g.textAlign = 'center'; g.fillText('YA!', 128, 64) }), gradientMap: M3.grad}));
  logo.position.set(0, 1.45, .57); B.add(logo);
  c.face = M3.face(B, {y: 2.35, z: .57, s: .95, lidColor: '#B58A52'});
  attachLimbs(c, B, {armX: .88, armY: 2.2, limb: '#6B4A22', hand: '#C9A26B', legX: .4, legY: 1.05, legLen: .85});
  c.legY0 = 1.05; c.sitDrop = .75; c.anim = (t, st) => animate(c, t, st); c.eye = new THREE.Vector3(0, 2.4, 0); return c;
}


// ───── ZOMBI DE SUSCRIPCIONES: tierno, verde, con control remoto y balde de pochoclo ─────
function zombi(o = {}) {
  const c = new THREE.Group(); const B = rig(c, {height: 3.3});
  const skin = toon(o.skin || '#8BCB7A'), cloth = toon(o.cloth || '#6B5B95');
  const torso = M3.cap(.62, .6, cloth); torso.position.y = 1.75; B.add(torso);
  const head = sph(.72, skin); head.position.y = 2.95; head.scale.set(1, .95, .95); B.add(head);
  const hair = sph(.74, toon('#3d5a35')); hair.scale.set(1, .45, 1); hair.position.set(0, 3.32, -.05); B.add(hair);
  const stitch = box(.35, .04, .04, flat('#3d2a2a'), {outline: false}); stitch.position.set(.35, 3.3, .6); stitch.rotation.z = .4; B.add(stitch);
  c.face = M3.face(B, {y: 2.92, z: .62, s: .85, lidColor: '#7BBB6A', cheek: '#9ED68E'});
  attachLimbs(c, B, {armX: .68, armY: 2.2, limb: '#6BAA5C', hand: '#8BCB7A', legX: .3, legY: 1.15, legLen: .95});
  if (o.gym) { const band = cyl(.74, .74, .16, toon('#E85D4E'), {seg: 32}); band.position.y = 3.2; B.add(band); const bag = rbox(.9, .45, .45, .1, toon('#2F6DB5')); bag.position.set(.95, 1.4, 0); B.add(bag) }
  else { const remote = rbox(.14, .45, .08, .04, toon('#2b2b2b')); c.arms[1].userData.el.add(remote); remote.position.y = -.55; const pop = cyl(.32, .25, .45, toon('#E84D4D')); pop.position.set(-.55, 1.25, .45); B.add(pop); for (let i = 0; i < 6; i++) { const k = sph(.09, toon('#FFF6D8'), {seg: 8}); k.position.set(-.55 + Math.sin(i) * .15, 1.52, .45 + Math.cos(i) * .15); B.add(k) } }
  c.legY0 = 1.15; c.sitDrop = .8; c.anim = (t, st) => animate(c, t, Object.assign({}, st, {expr: st.expr === 'happy' ? 'sly' : st.expr})); c.eye = new THREE.Vector3(0, 2.95, 0); return c;
}
// ───── INFLA: fantasma verde translúcido con % en la panza, flota ─────
function infla() {
  const c = new THREE.Group(); const B = rig(c, {height: 3.4});
  const mat = toon('#7FE0B8', {transparent: true, opacity: .88});
  const head = sph(1.05, mat, {seg: 36}); head.position.y = 2.45; B.add(head);
  const skirt = new THREE.Mesh(new THREE.CylinderGeometry(1.05, 1.2, 1.3, 36, 1, true), mat); skirt.position.y = 1.4; B.add(skirt); M3.outline(skirt);
  const waves = []; for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2; const w = sph(.28, mat, {seg: 14}); w.position.set(Math.cos(a) * 1.05, .75, Math.sin(a) * 1.05); B.add(w); waves.push(w) }
  const pct = M3.plane(.7, .7, new THREE.MeshToonMaterial({map: M3.canvasTex(128, 128, g => { g.fillStyle = '#2E8F6A'; g.font = M3.font(110); g.textAlign = 'center'; g.fillText('%', 64, 104) }), transparent: true, gradientMap: M3.grad}));
  pct.position.set(0, 1.55, 1.13); B.add(pct);
  c.face = M3.face(B, {y: 2.55, z: .98, s: .95, lidColor: '#6FD0A8', cheek: '#A8F0D0'});
  c.arms = [-1, 1].map(side => M3.arm(B, {x: side * 1.0, y: 2.0, color: '#6FD0A8', handColor: '#7FE0B8', side, len: .45, len2: .4}));
  c.legs = []; c.legY0 = 0; c.sitDrop = 0;
  c.anim = (t, st) => { animate(c, t, Object.assign({}, st, {sit: false})); B.position.y = .5 + Math.sin(t * 1.6) * .2; waves.forEach((w, i) => w.position.y = .75 + Math.sin(t * 3 + i) * .08) };
  c.eye = new THREE.Vector3(0, 3.0, 0); return c;
}

// ───── AUTITO: auto compacto de frente, con cara en el parabrisas y ruedas ─────
function autito() {
  const c = new THREE.Group(); const B = rig(c, {height: 3.0});
  const red = toon('#2F8FD8');
  const body = rbox(2.7, 1.05, 1.9, .3, red); body.position.y = 1.0; B.add(body);
  const cabin = rbox(1.9, 1.05, 1.5, .3, red); cabin.position.set(0, 1.95, -.1); B.add(cabin);
  const glass = rbox(1.55, .78, .06, .14, toon('#CFEFFF')); glass.position.set(0, 1.98, .66); B.add(glass);
  const grill = rbox(1.1, .22, .05, .08, toon('#2b2b2b')); grill.position.set(0, .78, .97); B.add(grill);
  [-1, 1].forEach(s => { const l = cyl(.18, .18, .08, toon('#FFF3B0', {emissive: '#FFE08A', emissiveIntensity: .4}), {seg: 20}); l.rotation.x = Math.PI / 2; l.position.set(s * .95, 1.08, .97); B.add(l) });
  c.wheels = []; [[-1, .55], [1, .55], [-1, -.6], [1, -.6]].forEach(([s, z]) => { const w = cyl(.42, .42, .32, toon('#222'), {seg: 24}); w.rotation.z = Math.PI / 2; w.position.set(s * 1.25, .42, z); c.add(w); c.wheels.push(w) });
  c.face = M3.face(B, {y: 1.98, z: .72, s: .78, lidColor: '#2678BD', cheek: '#F49A9A'});
  c.arms = [-1, 1].map(side => M3.arm(B, {x: side * 1.4, y: 1.25, color: '#1D5F96', handColor: '#2F8FD8', side, len: .45, len2: .4}));
  c.legs = []; c.legY0 = 0; c.sitDrop = 0;
  c.anim = (t, st) => { animate(c, t, Object.assign({}, st, {sit: false})); B.position.y += Math.abs(Math.sin(t * 9)) * (st.talk ? .03 : 0) };
  c.eye = new THREE.Vector3(0, 2.0, 0); return c;
}
M3.personaje = function (tipo) {
  const f = {moni, centavito, tarjetin, card: tarjetin, cafecito, cup: cafecito, delivy, bag: delivy, zombi: () => zombi(), gymzombi: () => zombi({gym: true, cloth: '#3FAE6B', skin: '#9AD08A'}), infla, ghost: infla, autito, car: autito}[tipo];
  if (!f) throw new Error('personaje desconocido ' + tipo);
  const c = f(); c.tipo = tipo; return c;
};

// ───── GENTE DE FONDO: simple pero bien armada (cabeza grande, cuerpo de cápsula, piernas de palito) ─────
const SKIN = ['#F2C9A0', '#E0AC7E', '#C68A5C', '#9C6B44', '#F5D5B8'];
const SHIRT = ['#4B8FD8', '#E85D4E', '#3FAE6B', '#A66BC9', '#F4C542', '#2B2B2B', '#E98AB0', '#5FC0C0', '#8B5A3C'];
const HAIR = ['#2b1d12', '#4a2f1a', '#111111', '#7a4b23', '#c98d3a', '#9a9a9a'];
M3.extra = function (o = {}) {
  const r = (k, arr) => arr[(o.seed * 7 + k) % arr.length | 0];
  const seed = o.seed || 0, c = new THREE.Group(); const B = rig(c, {height: 3});
  const shirt = toon(o.shirt || r(1, SHIRT)), skin = toon(o.skin || r(2, SKIN));
  const kind = o.kind ?? (seed % 5);                     // 0 remera, 1 buzo con capucha, 2 vestido, 3 camisa y corbata, 4 campera
  const torso = cap(.42, .55, shirt); torso.position.y = 1.55; B.add(torso);
  if (kind === 1) { const hood = sph(.36, shirt); hood.scale.set(1.25, .6, .9); hood.position.set(0, 2.08, -.18); B.add(hood); const pk = rbox(.5, .25, .05, .05, toon('#00000022'.slice(0, 7))); pk.position.set(0, 1.35, .41); B.add(pk) }
  if (kind === 2) { const sk = new THREE.Mesh(new THREE.ConeGeometry(.62, .9, 20, 1, true), shirt); sk.position.y = 1.15; B.add(sk); M3.outline(sk) }
  if (kind === 3) { const tie = rbox(.12, .45, .04, .03, toon('#C8102E')); tie.position.set(0, 1.75, .43); B.add(tie); const col = rbox(.5, .1, .1, .04, toon('#FFFFFF')); col.position.set(0, 2.02, .3); B.add(col) }
  if (kind === 4) { const z = plane(.04, .7, flat('#1d140f')); z.position.set(0, 1.55, .43); B.add(z); const col = rbox(.6, .14, .3, .05, shirt); col.position.set(0, 2.0, .1); B.add(col) }
  const head = sph(.55, skin); head.position.y = 2.6; B.add(head);
  const hairStyle = o.hair ?? (seed % 4);
  const hairMat = toon(r(3, HAIR));
  if (hairStyle === 0) { const h = sph(.57, hairMat); h.scale.set(1, .55, 1); h.position.set(0, 2.82, -.05); B.add(h) }
  if (hairStyle === 1) { const h = sph(.57, hairMat); h.scale.set(1, .6, 1); h.position.set(0, 2.8, -.06); B.add(h); const bun = sph(.22, hairMat); bun.position.set(0, 3.2, -.25); B.add(bun) }
  if (hairStyle === 2) { const capM = toon(r(4, SHIRT)); const cp = sph(.58, capM); cp.scale.set(1, .5, 1); cp.position.set(0, 2.88, 0); B.add(cp); const v = cyl(.4, .4, .05, capM, {seg: 24}); v.scale.z = .6; v.position.set(0, 2.86, .45); B.add(v) }
  if (hairStyle === 3) { for (let i = -2; i <= 2; i++) { const s = new THREE.Mesh(new THREE.ConeGeometry(.13, .35, 8), hairMat); s.position.set(i * .17, 3.1, 0); s.rotation.z = -i * .15; B.add(s); M3.outline(s) } }
  // cara simple: ojos de punto, cejas y boca
  const fg = new THREE.Group(); fg.position.set(0, 2.6, .52); B.add(fg);
  const eyes = [-1, 1].map(s => { const e = new THREE.Mesh(new THREE.SphereGeometry(.06, 10, 8), flat('#141010')); e.position.set(s * .18, .05, 0); fg.add(e); return e });
  const mouth = new THREE.Mesh(new THREE.TorusGeometry(.1, .025, 8, 16, Math.PI), flat('#5a1414')); mouth.rotation.z = Math.PI; mouth.position.y = -.17; fg.add(mouth);
  if (seed % 3 === 0) { const m = rbox(.32, .07, .04, .03, toon('#3b2410'), {outline: false}); m.position.set(0, -.08, .02); fg.add(m) }
  if (seed % 4 === 1) { [-1, 1].forEach(sd => { const r = new THREE.Mesh(new THREE.TorusGeometry(.12, .02, 8, 20), flat('#1d140f')); r.position.set(sd * .18, .05, .02); fg.add(r) }); const br = box(.12, .02, .02, flat('#1d140f'), {outline: false}); br.position.set(0, .07, .02); fg.add(br) }
  if (seed % 6 === 5) { const brim = cyl(.75, .75, .05, toon('#E8C57A'), {seg: 28}); brim.position.y = 2.95; B.add(brim); const top = cyl(.42, .48, .4, toon('#E8C57A'), {seg: 24}); top.position.y = 3.15; B.add(top) }
  c.face = {set() {}, update(t, talk) { const b = ((t + seed) % 4.1) < .1; eyes.forEach(e => e.scale.y = b ? .1 : 1); mouth.scale.y = talk ? .4 + Math.abs(Math.sin(t * 12)) : 1 }};
  attachLimbs(c, B, {armX: .45, armY: 1.95, limb: '#1d140f', hand: o.skin || r(2, SKIN), legX: .2, legY: 1.05, legLen: 1.0, armLen: .55, armLen2: .5});
  c.arms.forEach(a => a.children.forEach(ch => { if (ch.material && ch.material.color && ch !== a.userData.el) ch.material = toon('#1d140f') }));
  c.legY0 = 1.05; c.sitDrop = .7; c.anim = (t, st) => animate(c, t, Object.assign({seed}, st)); c.eye = new THREE.Vector3(0, 2.6, 0);
  const sc = o.scale || (seed % 7 === 3 ? .72 : .92 + (seed % 4) * .05); c.scale.setScalar(sc); return c;
};
})();
