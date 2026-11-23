// Capa de movimiento para videos largos: se inyecta DESPUÉS de long.js.
// Agrega: íconos que aparecen con las palabras clave, cámara viva (push-in, punch, shake),
// partículas de fondo, lluvia de monedas en cifras grandes, barridos entre escenarios y palabras clave resaltadas.
(function () {
const CSS = `
#Lcam{position:absolute;inset:0;transform-origin:960px 540px;will-change:transform}
#Lfx{position:absolute;inset:0;pointer-events:none;overflow:hidden}
#Lfx i{position:absolute;font-style:normal;line-height:1;will-change:transform}
#Lrain{position:absolute;inset:0;pointer-events:none;overflow:hidden;z-index:6}
#Lrain i{position:absolute;font-style:normal;font-size:64px;line-height:1}
#Lst{position:absolute;inset:0;pointer-events:none;z-index:7}
.stk{position:absolute;width:230px;height:230px;margin:-115px 0 0 -115px;display:none;flex-direction:column;align-items:center;justify-content:center;
  background:#FFFDF6;border-radius:50%;box-shadow:0 12px 0 rgba(0,0,0,.22),0 0 0 7px #F7BC2B inset}
.stk b{font:400 128px/1 "Noto Color Emoji",sans-serif}
.stk span{position:absolute;bottom:-26px;font:800 32px "Figtree";color:#14221D;background:#F7BC2B;padding:4px 14px;border-radius:999px;white-space:nowrap;text-transform:uppercase;letter-spacing:.04em}
.stk.cam{background:transparent;box-shadow:none;width:250px;height:290px;margin:-145px 0 0 -125px}
.stk.cam b{width:250px;font-size:0;display:block}
.stk.cam b svg{width:100%;height:auto;overflow:visible;filter:drop-shadow(0 14px 10px rgba(0,0,0,.3))}
.stk.cam span{bottom:-6px}
#Lwipe{position:absolute;top:-20%;bottom:-20%;width:140%;left:-150%;z-index:15;background:linear-gradient(90deg,#0E5A40 0 40%,#F7BC2B 40% 60%,#0E5A40 60%);transform:skewX(-14deg);display:none}
#L .cap .w.kw.lit{color:#7EFFC4}
#L.b-pizarra .cap .w.kw.lit{color:#C2185B}
`;
const st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);

// palabra (sin tildes, raíz) -> [emoji, etiqueta]
const KW = [
 ['florida','🌴','Florida'],['estados unidos','🇺🇸','EE. UU.'],['nueva york','🗽','Nueva York'],['reino unido','🇬🇧','Reino Unido'],
 ['loteri','🎟️','lotería'],['billete','💵','billete'],['millon','💰','millones'],['dolar','💵','dólares'],['plata','💰','plata'],['dinero','💰','dinero'],
 ['ahorr','🐷','ahorro'],['invert','📈','invertir'],['inversion','📈','inversión'],['accion','📊','acciones'],['bolsa','📊','bolsa'],['bono','📜','bonos'],
 ['interes','➕','interés'],['tasa','％','tasa'],['inflacion','🎈','inflación'],['precio','🏷️','precios'],['oferta','🏷️','oferta'],['descuento','🏷️','descuento'],
 ['tarjeta','💳','tarjeta'],['cuota','🗓️','cuotas'],['deuda','⛓️','deuda'],['prestamo','🤝','préstamo'],['banco','🏦','banco'],['cajero','🏧','cajero'],
 ['impuesto','🧾','impuestos'],['sueldo','💼','sueldo'],['salario','💼','sueldo'],['trabajo','💼','trabajo'],['aguinaldo','🎁','aguinaldo'],['bono ','🎁','bono'],
 ['casa','🏠','casa'],['departamento','🏢','depto'],['alquil','🔑','alquiler'],['hipotec','🏡','hipoteca'],['auto','🚗','auto'],['nafta','⛽','nafta'],
 ['seguro','🛡️','seguro'],['yate','🛥️','yate'],['viaje','✈️','viaje'],['vacacion','🏖️','vacaciones'],['fiesta','🎉','fiesta'],['regalo','🎁','regalo'],
 ['navidad','🎄','navidad'],['cumplea','🎂','cumple'],['cafe','☕','café'],['delivery','🛵','delivery'],['pizza','🍕','pizza'],['supermercado','🛒','súper'],
 ['super ','🛒','súper'],['carrito','🛒','carrito'],['comida','🍝','comida'],['pan ','🥖','pan'],['galletita','🍪','galletitas'],['ropa','👕','ropa'],
 ['zapatilla','👟','zapatillas'],['celular','📱','celular'],['telefono','📱','teléfono'],['internet','🌐','internet'],['aplicacion','📲','app'],['suscripcion','📺','suscripción'],
 ['gimnasio','🏋️','gym'],['salud','🩺','salud'],['familia','👨‍👩‍👧','familia'],['hijo','🧒','hijos'],['pareja','💑','pareja'],['amigo','🫂','amigos'],
 ['primo','🫂','primo'],['cerebro','🧠','cerebro'],['emocion','🎢','emoción'],['miedo','😱','miedo'],['estafa','🕵️','estafa'],['fraude','🕵️','fraude'],
 ['ponzi','🔺','pirámide'],['piramide','🔺','pirámide'],['fbi','🚨','FBI'],['carcel','🚔','cárcel'],['prision','🚔','prisión'],['juicio','⚖️','juicio'],
 ['condena','⚖️','condena'],['quiebra','💥','quiebra'],['crisis','🌪️','crisis'],['derrumb','📉','derrumbe'],
 ['crec','🌱','crece'],['tiempo','⏳','tiempo'],['año','📅','años'],['mes ','📅','mes'],['reloj','⏰','reloj'],
 ['meta','🎯','meta'],['plan','🗺️','plan'],['regla','📏','regla'],['lista','📝','lista'],['anot','📝','anotar'],['presupuesto','📒','presupuesto'],
 ['fondo de emergencia','🛟','fondo'],['emergencia','🚑','emergencia'],['heladera','🧊','heladera'],['colchon','🛏️','colchón'],
 ['tulipan','🌷','tulipán'],['flor','🌷','flor'],['netflix','🍿','streaming'],['pelicula','🎬','película'],['dvd','📀','DVD'],['correo','📮','correo'],
 ['cripto','🪙','cripto'],['bitcoin','🪙','bitcoin'],['moneda','🪙','moneda'],['oro','🥇','oro'],['empresa','🏭','empresa'],['negocio','🏪','negocio'],
 ['diploma','🎓','estudio'],['universidad','🎓','universidad'],['jubilacion','👵','jubilación'],['comision','✂️','comisión'],['riesgo','⚠️','riesgo'],
 ['secreto','🤫','secreto'],['confianza','🤝','confianza'],['mito','❌','mito'],['verdad','✅','verdad'],['pregunta','❓','pregunta'],['idea','💡','idea'],
 ['diversific','🧺','diversificar'],['canasta','🧺','canasta'],['huevo','🥚','huevos'],['pizzeria','🍕','pizzería'],['dividendo','🍋','dividendo'],['limonada','🍋','limonada'],
 ['guerra','⚔️','guerra'],['gobierno','🏛️','gobierno'],['carretilla','🛒','carretilla'],['zimbabue','🌍','Zimbabue'],['alemania','🇩🇪','Alemania'],['holanda','🇳🇱','Holanda'],
 ['estados unidos','🇺🇸','EE. UU.'],['nueva york','🗽','Nueva York'],['florida','🌴','Florida'],['reino unido','🇬🇧','Reino Unido'],['bahamas','🏝️','Bahamas'],
];
const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9ñ ]/g, ' ');
const STOP = new Set(['interesante','interesantes','interesa','florida','idealmente','ideal','seguramente','plantear','planeta','metas ','aniversario','mesa','tasas']);
function findKW(text) {
  // devuelve [{wordIdx, emoji, label}] por palabra
  const words = text.split(' '); const hits = []; const nw = words.map(w => norm(w).trim());
  for (let k = 0; k < nw.length; k++) {
    const w = nw[k] + ' '; const two = (nw[k] + ' ' + (nw[k + 1] || '')).trim();
    for (const [stem, emo, lab] of KW) {
      const s = stem.trim();
      if (stem.includes(' ') && stem.trim().split(' ').length > 1 ? two.startsWith(s) : (stem.endsWith(' ') ? w === stem : nw[k].startsWith(s) && nw[k].length <= s.length + 4 && !STOP.has(nw[k]))) {
        if (s.length < 3 && nw[k] !== s) continue;
        hits.push({k, emoji: emo, label: lab}); break;
      }
    }
  }
  return hits;
}
const SLOTS = {
  '1p': [[260, 270], [1130, 260], [270, 650], [1150, 650]],
  '1': [[340, 300], [1580, 300], [360, 650], [1560, 650]],
  '2': [[330, 260], [1590, 260], [690, 670], [1230, 670]],
  '3': [[300, 270], [1620, 270], [960, 200], [600, 230]],
};
const ICON_DUR = 3.0; let CU = 0;
let M = {};
const origSetup = window.setupLong, origFrame = window.frameLong;
window.setupLong = function (tl) {
  const r = origSetup(tl);
  const L = document.getElementById('L');
  const cam = document.createElement('div'); cam.id = 'Lcam';
  const fx = document.createElement('div'); fx.id = 'Lfx';
  const rain = document.createElement('div'); rain.id = 'Lrain';
  const stk = document.createElement('div'); stk.id = 'Lst';
  [L.querySelector('.bg'), L.querySelector('.deco'), fx, L.querySelector('#Lp'), L.querySelector('#La'), rain, stk].forEach(el => cam.appendChild(el));
  L.insertBefore(cam, L.firstChild);
  const wipe = document.createElement('div'); wipe.id = 'Lwipe'; L.appendChild(wipe);
  // partículas
  for (let k = 0; k < 16; k++) { const i = document.createElement('i'); fx.appendChild(i) }
  for (let k = 0; k < 14; k++) { const i = document.createElement('i'); i.textContent = '🪙'; rain.appendChild(i) }
  for (let k = 0; k < 4; k++) { const d = document.createElement('div'); d.className = 'stk'; d.innerHTML = '<b></b><span></span>'; stk.appendChild(d) }
  // eventos de íconos: una palabra clave dispara un ícono, máximo 1 cada 1,6 s, sin repetir el mismo en 12 s
  M = {events: [], rains: [], lastBg: []};
  let lastT = -10; const lastIcon = {};
  let prevBg = null;
  tl.scenes.forEach((s, idx) => {
    if (s.type !== 'line') { return }
    s._bgChange = prevBg !== null && prevBg !== s.bg; prevBg = s.bg;
    const words = s.text.split(' '); const n = words.length;
    s._kw = new Set();
    findKW(s.text).forEach(h => {
      s._kw.add(h.k);
      const t = s.start + (h.k / n) * s.audio;
      if (t - lastT < 1.1) return; if (lastIcon[h.emoji] && t - lastIcon[h.emoji] < 8) return;
      M.events.push({t, emoji: h.emoji, label: h.label, scene: idx}); lastT = t; lastIcon[h.emoji] = t;
    });
    if (s.panel && s.panel.new && /\$\s?[\d.]{4,}/.test(s.panel.big)) M.rains.push({t: s.start + 0.15, seed: idx});
    // relleno: si la escena no tuvo íconos y pasaron más de 6 s desde el último, un ícono por el tono de la frase
    if (s.audio > 3 && s.start + s.audio * 0.4 - lastT > 6) {
      const t = s.start + s.audio * 0.4; const q = s.text.includes('?'), ex = s.text.includes('!');
      const pick = q ? ['🤔', 'pregunta'] : ex ? ['❗', 'atención'] : (s.panel && /\d/.test(s.panel.big)) ? ['🔢', 'dato'] : ['👀', 'ojo'];
      M.events.push({t, emoji: pick[0], label: pick[1], scene: idx}); lastT = t;
    }
  });
  // marcar cambios de fondo para el barrido
  const lines = tl.scenes.filter(s => s.type === 'line');
  lines.forEach((s, k) => { s._bgChangeNext = k + 1 < lines.length && lines[k + 1].bg !== s.bg });
  M.slotUse = {}; window.__MOTION = M;
  return r;
};
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = x => 1 - Math.pow(1 - clamp(x), 3);
const back = x => { x = clamp(x); const c = 1.9; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2) };
const rnd = s => { const x = Math.sin(s * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x) };
const FX = {
  marca: {icons: ['🪙', '✨', '🪙', '💵'], op: .28, size: [34, 70]},
  novela: {icons: ['✨', '💫', '✨'], op: .35, size: [26, 56]},
  simulador: {icons: ['📈', '$', '％', '📊'], op: .26, size: [30, 64]},
  pizarra: {icons: ['✏️', '📎', '⭐'], op: .22, size: [30, 50]},
  sitcom: {icons: [], op: 0, size: [0, 0]},
  mito: {icons: ['❓', '❗'], op: .2, size: [40, 70]},
};
window.frameLong = function (t) {
  const i = origFrame(t);
  const L = document.getElementById('L'); const s = TL_scene(i); if (!s) return i;
  const cam = document.getElementById('Lcam');
  const bg = (L.className || 'b-marca').slice(2);
  // partículas de fondo
  const cfg = FX[bg] || FX.marca;
  [...document.querySelectorAll('#Lfx i')].forEach((el, k) => {
    if (!cfg.icons.length) { el.style.display = 'none'; return }
    el.style.display = 'block'; el.textContent = cfg.icons[k % cfg.icons.length];
    const sp = 18 + rnd(k) * 40, x0 = rnd(k + 9) * 1920, sz = cfg.size[0] + rnd(k + 3) * (cfg.size[1] - cfg.size[0]);
    const y = 1150 - ((t * sp + rnd(k + 5) * 1300) % 1300);
    const x = x0 + Math.sin(t * (0.3 + rnd(k + 7) * 0.5) + k) * 40;
    Object.assign(el.style, {left: x + 'px', top: y + 'px', fontSize: sz + 'px', opacity: cfg.op, transform: `rotate(${Math.sin(t * .7 + k) * 25}deg)`, color: '#F7BC2B', fontWeight: 800});
  });
  // lluvia de monedas
  const rainEls = [...document.querySelectorAll('#Lrain i')];
  const rain = M.rains.find(r => t >= r.t && t < r.t + 1.8);
  rainEls.forEach((el, k) => {
    if (!rain) { el.style.display = 'none'; return }
    const rt = t - rain.t; const x = 80 + rnd(rain.seed * 31 + k) * 1760; const d = rnd(rain.seed * 17 + k) * 0.5;
    const y = -100 + Math.max(0, rt - d) * (900 + rnd(k + rain.seed) * 500) + 0.5 * 900 * Math.pow(Math.max(0, rt - d), 2);
    Object.assign(el.style, {display: 'block', left: x + 'px', top: y + 'px', opacity: clamp((1.8 - rt) / 0.4), transform: `rotate(${rt * 360 * (rnd(k) > .5 ? 1 : -1)}deg)`});
  });
  // cámara: push-in lento alternado + punch en paneles nuevos + sacudida en sustos
  let z = 1, px = 0, py = 0;
  if (s.type === 'line') {
    const ts = t - s.start, dir = (i % 2) ? -1 : 1, e = ease(ts / s.dur);
    z = 1.02 + dir * 0.025 * (e - 0.5) * 2 * 0.5 + 0.0125;
    px = ((i % 3) - 1) * 14 * e; py = ((i % 2) ? -1 : 1) * 6 * e;
    if (s.panel && s.panel.new) z += 0.07 * Math.max(0, 1 - ease(ts / 0.4));
    if (Object.values(s.ex || {}).includes('shock') && ts < 0.45) { px += Math.sin(ts * 90) * 10 * (1 - ts / 0.45); py += Math.cos(ts * 77) * 6 * (1 - ts / 0.45) }
    // énfasis en palabras clave
    const C = document.getElementById('Lc');
    if (C.dataset.sc !== String(i)) { C.dataset.sc = String(i); [...C.querySelectorAll('.w')].forEach((w, k) => w.classList.toggle('kw', s._kw && s._kw.has(k))) }
  }
  cam.style.transform = `translate(${px}px,${py}px) scale(${z})`;
  const P = document.getElementById('Lp'); if (P && P.style.display !== 'none') P.style.translate = `0 ${Math.sin(t * 1.3) * 6}px`;
  // íconos
  let slots = (() => { const n = s.cast ? s.cast.length : 1; return n === 1 ? (s.panel ? SLOTS['1p'] : SLOTS['1']) : SLOTS[String(Math.min(3, n))] })();
  const busy = window.__brollBusy ? window.__brollBusy(t) : null;   // zona ocupada por un widget: {x0,y0,x1,y1}
  if (busy) slots = slots.filter(([x, y]) => !busy.some(b => x > b.x0 - 130 && x < b.x1 + 130 && y > b.y0 - 130 && y < b.y1 + 130));
  if (!slots.length) slots = [[300, 650]];
  const active = M.events.filter(ev => t >= ev.t && t < ev.t + ICON_DUR && TL_scene(ev.scene) && TL_scene(i).type === 'line').slice(-3);
  const els = [...document.querySelectorAll('#Lst .stk')];
  els.forEach((el, k) => {
    const ev = active[k];
    if (!ev) { el.style.display = 'none'; return }
    const slot = slots[(M.events.indexOf(ev)) % slots.length];
    const et = t - ev.t; const inK = back(et / 0.35), outK = clamp((ICON_DUR - et) / 0.3);
    const rot = (rnd(M.events.indexOf(ev)) - 0.5) * 24;
    el.style.display = 'flex';
    if (ev.kind) {   // cameo de personaje
      if (el.dataset.kind !== ev.kind) { el.dataset.kind = ev.kind; el.classList.add('cam'); const u = '_c' + (++CU);
        el.querySelector('b').innerHTML = charSVG(ev.kind).split('g-' + ev.kind + '"').join('g-' + ev.kind + u + '"').split('#g-' + ev.kind + ')').join('#g-' + ev.kind + u + ')') }
    } else { if (el.dataset.kind) { delete el.dataset.kind; el.classList.remove('cam') } el.querySelector('b').textContent = ev.emoji }
    el.querySelector('span').textContent = ev.label;
    Object.assign(el.style, {left: slot[0] + 'px', top: (slot[1] + Math.sin(et * 3) * 8) + 'px', opacity: outK,
      transform: `scale(${(0.2 + 0.8 * inK) * (0.6 + 0.4 * outK)}) rotate(${rot * (1 - 0.3 * ease(et))}deg)`});
  });
  // barrido entre escenarios
  const W = document.getElementById('Lwipe');
  let wx = null;
  if (s.type === 'line') {
    const ts = t - s.start;
    if (s._bgChange && ts < 0.25) wx = 0.5 + 0.5 * ease(ts / 0.25);          // sale hacia la derecha
    else if (s._bgChangeNext && s.dur - ts < 0.25) wx = 0.5 * ease((0.25 - (s.dur - ts)) / 0.25); // entra desde la izquierda
  }
  if (wx === null) W.style.display = 'none'; else { W.style.display = 'block'; W.style.left = (-150 + wx * 260) + '%' }
  return i;
};
function TL_scene(i) { try { return window.__TL ? window.__TL.scenes[i] : null } catch (e) { return null } }
// guardar el timeline para leerlo desde acá
const s2 = window.setupLong; window.setupLong = function (tl) { window.__TL = tl; return s2(tl) };
})();
