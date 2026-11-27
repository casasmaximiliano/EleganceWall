// Video 15 · Blockbuster pudo comprar Netflix por $50 millones (y se rió) — planos del mundo 3D.
// Moni le cuenta la historia a Centavito en un videoclub y en su escritorio; la reunión de Dallas se ve en la sala.
const G = '#17865A', R = '#C8102E';
const VC = {moni: 'pasillo', centavito: 'mostrador'};
const DESK = {moni: 'escritorio', centavito: 'junto'};
const CALLE = {moni: 'alquilaA', centavito: 'alquilaB'};
const nb = (title, lines, stamp) => ({prop: 'cuaderno', content: {title, lines, stamp}});
const res = (title, lines, stamp) => ({prop: 'resumen', content: {title, lines, stamp}});
const cm = (loc, cast, a = .25, o = {}) => ({loc, cast, cam: 'close:moni', camOpt: Object.assign({angle: a}, o)});
const cc = (loc, cast, a = -.2, o = {}) => ({loc, cast, cam: 'close:centavito', camOpt: Object.assign({angle: a, dist: 4.4}, o)});
const X = (a, b) => Object.assign({}, a, b);
const RAZONES = [{t: '1. Lo que tenían funcionaba', c: R}, {t: '2. Internet era lento', c: R}, {t: '3. Cambiar dolía', c: R}];
const PREG = [{t: '1. ¿Qué pago sin revisar?'}, {t: '2. ¿Qué hago por costumbre?'}, {t: '3. ¿Qué vengo postergando?'}];
module.exports = {
  // ── arranque en frío en el videoclub ──
  0: [[.55, X(cm('videoclub', VC, .2), {gesture: {moni: 'shock'}})], [1, X({loc: 'videoclub', cam: 'two', cast: VC}, {insert: undefined})]],
  1: [[1, X(cc('videoclub', VC), {gesture: {centavito: 'shock'}})]],
  2: [[.5, {loc: 'sala', cam: 'risa', cast: {}, fx: {laugh: 1}}], [1, cm('videoclub', VC, .2)]],
  3: [[1, cc('videoclub', VC)]],
  4: [[1, {loc: 'videoclub', cam: 'est', cast: VC}]],
  5: [[1, X(cc('videoclub', VC), {gesture: {centavito: 'think'}})]],
  6: [[.5, cm('videoclub', VC, .2)], [1, {loc: 'videoclub', cam: 'two', cast: VC, push: .12}]],
  // ── el imperio ──
  7: [[1, {loc: 'videoclub', cam: 'est', cast: {}, title: {over: 'Capítulo 1', text: 'El imperio del videoclub'}}]],
  8: [[.45, {loc: 'videoclub', cam: 'estantes', cast: VC}], [1, {loc: 'videoclub', cam: 'two', cast: VC}]],
  9: [[1, cc('videoclub', VC)]],
  10: [[1, cm('videoclub', VC, .2)]],
  11: [[.4, {loc: 'videoclub', cam: 'wide', cast: VC}], [1, {insert: res('BLOCKBUSTER', [{t: 'Locales en el mundo', v: '≈ 9.000'}, {t: 'a mediados de los 2000'}])}]],
  12: [[.5, {loc: 'videoclub', cam: 'tele', cast: VC}], [1, X(cm('videoclub', VC, .2), {gesture: {moni: 'point'}})]],
  13: [[1, cc('videoclub', VC)]],
  14: [[.35, cm('videoclub', VC, .2)], [1, {insert: res('MULTAS POR DEVOLVER TARDE', [{t: 'Año 2000', v: '≈ $800 M', vc: R}], '¡MULTA!')}]],
  15: [[1, X(cc('videoclub', VC), {gesture: {centavito: 'shock'}})]],
  16: [[1, {loc: 'videoclub', cam: 'two', cast: VC}]],
  17: [[1, X(cc('videoclub', VC), {gesture: {centavito: 'cross'}})]],
  18: [[.4, cm('videoclub', VC, .2)], [1, {insert: nb('La clave', [{t: 'Ganaban más'}, {t: 'cuando el cliente'}, {t: 'se equivocaba', c: R}])}]],
  // ── la apuesta de Netflix (escritorio) ──
  19: [[1, {loc: 'depto', cam: 'deskWide', cast: {}, title: {over: 'Capítulo 2', text: 'La apuesta de Netflix'}}]],
  20: [[.35, {loc: 'depto', cam: 'deskWide', cast: DESK}], [1, {insert: nb('Netflix', [{t: '1997', v: 'DVD por correo'}])}]],
  21: [[1, cc('depto', DESK, -.2, {dist: 4.2})]],
  22: [[.4, cm('depto', DESK, -.35)], [1, {insert: nb('Netflix', [{t: '1997', v: 'DVD por correo'}, {t: '1999', v: 'suscripción', vc: G}, {t: 'sin multas', c: G}])}]],
  23: [[.45, {loc: 'depto', cam: 'deskOver', cast: DESK}], [1, {insert: {prop: 'celular', content: {app: 'Videoclub', color: '#C8102E', rows: [{label: 'Película devuelta tarde', value: 'Multa'}, {label: 'Total', value: '$40', neg: true, hl: true, big: true}]}}}]],
  24: [[1, X(cc('depto', DESK, -.2, {dist: 4.2}), {gesture: {centavito: 'point'}})]],
  25: [[1, {loc: 'depto', cam: 'deskWide', cast: DESK, push: .1}]],
  // ── la reunión de Dallas ──
  26: [[1, {loc: 'sala', cam: 'mesa', cast: {}, title: {over: 'Dallas · año 2000', text: 'La reunión'}}]],
  27: [[.5, {loc: 'sala', cam: 'fundadores', cast: {}}], [1, {loc: 'sala', cam: 'atril', cast: {}}]],
  28: [[1, cc('depto', DESK, -.2, {dist: 4.2})]],
  29: [[1, {loc: 'sala', cam: 'risa', cast: {}, fx: {laugh: 1}, push: .1}]],
  30: [[1, X(cc('depto', DESK, -.2, {dist: 4.2}), {gesture: {centavito: 'cross'}})]],
  31: [[.55, {loc: 'sala', cam: 'mesa', cast: {}, push: .12}], [1, {loc: 'sala', cam: 'fundadores', cast: {}}]],
  32: [[1, X(cm('depto', DESK, -.35), {gesture: {moni: 'think'}})]],
  // ── por qué dijeron que no ──
  33: [[1, {loc: 'depto', cam: 'deskWide', cast: {}, title: {over: 'Capítulo 3', text: 'Por qué dijeron que no'}}]],
  34: [[1, {loc: 'depto', cam: 'deskWide', cast: DESK}]],
  35: [[1, {insert: nb('¿Por qué no?', RAZONES.slice(0, 1))}]],
  36: [[1, {insert: nb('¿Por qué no?', RAZONES.slice(0, 2))}]],
  37: [[1, {insert: nb('¿Por qué no?', RAZONES)}]],
  38: [[1, X(cc('depto', DESK, -.2, {dist: 4.2}), {gesture: {centavito: 'think'}})]],
  39: [[.4, cm('depto', DESK, -.35)], [1, {insert: res('EL DILEMA DEL INNOVADOR', [{t: 'Lo nuevo empieza'}, {t: 'peor y menos rentable'}, {t: '→ el gigante lo ignora', vc: R, v: ''}])}]],
  40: [[.4, {loc: 'depto', cam: 'deskOver', cast: DESK}], [1, {insert: res('BLOCKBUSTER REACCIONA', [{t: '2004', v: 'servicio online'}, {t: 'sin multas', v: 'sí'}], 'TARDE')}]],
  // ── la caída (calle con locales en alquiler) ──
  41: [[1, {loc: 'calle', cam: 'establish', cast: {}, title: {over: 'Capítulo 4', text: 'La caída'}}]],
  42: [[.45, {loc: 'calle', cam: 'alquilaFront', cast: CALLE}], [1, {insert: {prop: 'celular', content: {app: 'Netflix · 2007', color: '#14100c', rows: [{label: 'Streaming', value: '▶ Play', hl: true, big: true}, {label: 'Sin sobres, sin esperar', value: ''}]}}}]],
  43: [[1, X(cc('calle', CALLE, -.2, {dist: 5.2}), {gesture: {centavito: 'point'}})]],
  44: [[.4, {loc: 'calle', cam: 'alquilaFront', cast: CALLE}], [1, {insert: res('BLOCKBUSTER', [{t: 'Septiembre de 2010'}, {t: 'Deudas enormes'}], 'QUIEBRA')}]],
  45: [[.55, {loc: 'videoclub', cam: 'wide', cast: {}}], [1, {insert: res('HOY', [{t: 'Queda 1 local'}, {t: 'Bend, Oregon (EE. UU.)'}])}]],
  46: [[1, X(cm('calle', CALLE, .3, {dist: 6.6}), {gesture: {moni: 'shock'}})]],
  47: [[1, cc('calle', CALLE, -.2, {dist: 5.2})]],
  48: [[.5, {loc: 'calle', cam: 'alquilaFront', cast: CALLE}], [1, {insert: res('NETFLIX TAMBIÉN SE EQUIVOCÓ', [{t: '2011', v: 'separar DVD'}, {t: 'perdió suscriptores', c: R}, {t: '→ volvió atrás', c: G}])}]],
  // ── tu propio Blockbuster ──
  49: [[1, {loc: 'depto', cam: 'wide', cast: {}, title: {over: 'Capítulo 5', text: 'Tu propio Blockbuster'}}]],
  50: [[1, {loc: 'depto', cam: 'deskWide', cast: DESK, push: .1}]],
  51: [[.35, cm('depto', DESK, -.35)], [1, {insert: {prop: 'celular', content: {app: 'Mi banco', color: '#0E5A40', rows: [{label: 'Mantenimiento', value: '$8 / mes', neg: true}, {label: 'Por año', value: '$96', neg: true, hl: true, big: true}]}}}]],
  52: [[1, X(cc('depto', DESK, -.2, {dist: 4.2}), {gesture: {centavito: 'shock'}})]],
  53: [[.4, cm('depto', DESK, -.35)], [1, {insert: nb('Mi Blockbuster', [{t: '1. Cuenta con mantenimiento', c: R}, {t: '2. Plan o seguro de siempre', c: R}])}]],
  54: [[1, cc('depto', DESK, -.2, {dist: 4.2})]],
  55: [[1, {loc: 'depto', cam: 'deskOver', cast: DESK}]],
  56: [[.45, cm('depto', DESK, -.35)], [1, {insert: nb('Mi Blockbuster', [{t: '1. Cuenta con mantenimiento', c: R}, {t: '2. Plan o seguro de siempre', c: R}, {t: '3. Todo en un solo lugar', c: R}])}]],
  57: [[.4, X(cm('depto', DESK, -.35), {gesture: {moni: 'think'}})], [1, {insert: res('COSTO DE OPORTUNIDAD', [{t: 'Lo que dejás de ganar'}, {t: 'por no elegir otra opción', c: R}])}]],
  // ── encontrá el tuyo ──
  58: [[1, {loc: 'depto', cam: 'deskWide', cast: {}, title: {over: 'Para anotar', text: 'Encontrá el tuyo'}}]],
  59: [[1, {loc: 'depto', cam: 'deskWide', cast: DESK}]],
  60: [[1, {insert: nb('3 preguntas', PREG.slice(0, 1))}]],
  61: [[1, {insert: nb('3 preguntas', PREG.slice(0, 2))}]],
  62: [[1, {insert: nb('3 preguntas', PREG)}]],
  63: [[1, X(cc('depto', DESK, -.2, {dist: 4.2}), {gesture: {centavito: 'hips'}})]],
  64: [[1, cm('depto', DESK, -.35)]],
  // ── no fueron los únicos ──
  65: [[1, {loc: 'calle', cam: 'establish', cast: {}, title: {over: 'Capítulo 6', text: 'No fueron los únicos'}}]],
  66: [[.3, {loc: 'calle', cam: 'alquilaFront', cast: CALLE}], [1, {insert: res('KODAK', [{t: '1975', v: 'cámara digital'}, {t: 'vivía de los rollos'}, {t: '2012', v: 'quiebra', vc: R}])}]],
  67: [[.3, cm('calle', CALLE, .3, {dist: 6.6})], [1, {insert: res('NOKIA', [{t: 'N.° 1 en celulares'}, {t: 'Pantallas táctiles', v: 'tarde', vc: R}, {t: 'perdió el liderazgo', c: R}])}]],
  68: [[1, X(cc('calle', CALLE, -.2, {dist: 5.2}), {gesture: {centavito: 'think'}})]],
  69: [[1, {loc: 'calle', cam: 'alquilaFront', cast: CALLE, push: .1}]],
  // ── cambiar sin saltar al vacío ──
  70: [[1, {loc: 'depto', cam: 'wide', cast: {}, title: {over: 'Capítulo 7', text: 'Cambiar sin saltar al vacío'}}]],
  71: [[.4, {loc: 'depto', cam: 'deskWide', cast: DESK}], [1, {insert: nb('Cambiar de a poco', [{t: 'Mantener lo que funciona'}, {t: '+ aprender algo nuevo', c: G}])}]],
  72: [[.4, cm('depto', DESK, -.35)], [1, {insert: nb('Cambiar de a poco', [{t: 'Mantener lo que funciona'}, {t: '+ aprender algo nuevo', c: G}, {t: '+ un colchón de meses', c: G}])}]],
  // ── una última curiosidad ──
  73: [[1, {loc: 'videoclub', cam: 'est', cast: {}, title: {over: 'Bonus', text: 'Una última curiosidad'}}]],
  74: [[.5, {loc: 'videoclub', cam: 'wide', cast: VC}], [1, {loc: 'videoclub', cam: 'estantes', cast: VC}]],
  75: [[1, X(cc('videoclub', VC), {gesture: {centavito: 'shock'}})]],
  76: [[1, cm('videoclub', VC, .2)]],
  77: [[1, X(cc('videoclub', VC), {gesture: {centavito: 'point'}})]],
  78: [[1, {loc: 'videoclub', cam: 'two', cast: VC}]],
  // ── resumen y cierre ──
  79: [[1, {loc: 'depto', cam: 'deskWide', cast: {}, title: {over: 'En 30 segundos', text: 'Resumen'}}]],
  80: [[.3, {loc: 'depto', cam: 'deskWide', cast: DESK}], [1, {insert: nb('Resumen', [{t: '2000: dijo que no a $50 M'}, {t: 'funcionaba · lento · dolía'}, {t: '2010: quiebra', c: R}])}]],
  81: [[1, {insert: nb('Para tu plata', [{t: 'Revisá lo de siempre', c: G}, {t: 'No todo en un lugar', c: G}, {t: 'Aprendé antes de que urja', c: G}])}]],
  82: [[1, {loc: 'videoclub', cam: 'two', cast: VC, title: {over: 'Moni Finanzas', text: 'Cierre'}}]],
  83: [[1, cc('videoclub', VC)]],
  84: [[1, X(cm('videoclub', VC, .2), {gesture: {moni: 'point'}})]],
  85: [[1, {loc: 'videoclub', cam: 'two', cast: VC, gesture: {moni: 'wave'}, push: .12}]],
  86: [[1, {loc: 'videoclub', cam: 'wide', cast: VC, gesture: {moni: 'wave', centavito: 'wave'}, push: .2}]],
};
