// Video 21 · ¿Qué pasa si ahorrás el cafecito toda tu vida? — planos del mundo 3D.
// {índiceDeEscena: [[fracciónFin, plano], ...]}
const G = '#17865A', R = '#C8102E';
const CAFE = {moni: 'mesaA', cup: 'mesaB'};
const SOFA = {moni: 'sofaL', cup: 'sofaR'};
const DESK = {moni: 'escritorio', centavito: 'junto'};
const CALLE = {moni: 'alquilaA', cup: 'alquilaB'};
const AUTO = {moni: 'veredaAuto', car: 'cordon'};
const BANCO = {moni: 'ventanilla', cup: 'junto'};
const nb = (title, lines) => ({prop: 'cuaderno', content: {title, lines}});
const cuenta = (rows) => ({prop: 'celular', content: {app: 'Inversión Moni B', color: '#0E5A40', rows}});
const anio = (a, total, puso, extra) => cuenta([{label: `Año ${a}`, value: total, hl: true, big: true}, {label: 'Puso de su bolsillo', value: puso}].concat(extra || []));
const res = (title, lines, stamp) => ({prop: 'resumen', content: {title, lines, stamp}});
const cl = (k, a = .3, o = {}) => Object.assign({cam: 'close:' + k, camOpt: Object.assign({angle: a}, o)});
module.exports = {
  // ── cold open en la cafetería ──
  0: [[1, {loc: 'cafeteria', cam: 'two', cast: CAFE, push: .12}]],
  1: [[.45, Object.assign({loc: 'cafeteria', cast: CAFE}, cl('moni', .25))], [1, {insert: {prop: 'celular', content: {app: 'Internet dice', color: '#C8102E', rows: [{label: 'Un café por día', value: '$3'}, {label: 'En 40 años', value: '$173.238', neg: true, hl: true, big: true}]}}}]],
  2: [[1, Object.assign({loc: 'cafeteria', cast: CAFE, gesture: {cup: 'shock'}}, cl('cup', -.25))]],
  3: [[.5, {loc: 'cafeteria', cam: 'two', cast: CAFE}], [1, Object.assign({loc: 'cafeteria', cast: CAFE}, cl('moni', .25))]],
  4: [[.4, {loc: 'cafeteria', cam: 'queue', cast: CAFE}], [1, {insert: nb('El café del mes', [{t: '22 cafés por mes'}, {t: '× $3 cada uno'}, {t: '= por mes', v: '$66', vc: R}])}]],
  5: [[.35, Object.assign({loc: 'cafeteria', cast: CAFE}, cl('moni', .25))], [1, {insert: nb('Dos Monis', [{t: 'Moni A', v: 'café afuera', vc: R}, {t: 'Moni B', v: 'café en casa', vc: G}, {t: '+ invierte $66/mes al 7 %', c: G}])}]],
  6: [[1, Object.assign({loc: 'cafeteria', cast: CAFE}, cl('cup', -.25))]],
  7: [[1, {loc: 'cafeteria', cam: 'two', cast: CAFE}]],
  8: [[.5, Object.assign({loc: 'cafeteria', cast: CAFE}, cl('moni', .25))], [1, {insert: nb('La simulación', [{t: 'Desde los 25 años'}, {t: 'hasta los 65'}, {t: '= 40 años', c: G}])}]],
  9: [[.5, {loc: 'cafeteria', cam: 'wide', cast: CAFE}], [1, {insert: res('EJEMPLO ILUSTRATIVO', [{t: 'Rendimiento', v: '7 % anual'}, {t: 'Garantizado', v: 'NO', vc: R}, {t: 'Las inversiones suben y bajan'}])}]],
  // ── año 1 a 10: en el living ──
  10: [[1, {loc: 'depto', cam: 'wide', cast: {}, title: {over: 'Capítulo 1', text: 'Año 1 a 10'}}]],
  11: [[.35, {loc: 'depto', cam: 'two', cast: SOFA}], [1, {insert: anio(1, '≈ $820', '$792', [{label: 'Ganó', value: '≈ $30'}])}]],
  12: [[1, Object.assign({loc: 'depto', cast: SOFA, gesture: {cup: 'armsUp'}}, cl('cup', -.3))]],
  13: [[.5, Object.assign({loc: 'depto', cast: SOFA}, cl('moni', .3))], [1, {insert: nb('Moni A', [{t: 'Cafés en un año', v: '264', vc: R}])}]],
  14: [[1, Object.assign({loc: 'depto', cast: SOFA}, cl('cup', -.3))]],
  15: [[1, {insert: anio(5, '≈ $4.700', '$3.960')}]],
  16: [[1, {insert: anio(10, '≈ $11.400', '$7.920')}]],
  17: [[.55, Object.assign({loc: 'depto', cast: SOFA}, cl('moni', .3))], [1, {loc: 'depto', cam: 'two', cast: SOFA}]],
  18: [[1, Object.assign({loc: 'depto', cast: SOFA}, cl('cup', -.3))]],
  19: [[1, {loc: 'depto', cam: 'two', cast: SOFA, push: .15}]],
  // ── año 10 a 25: en la calle ──
  20: [[1, {loc: 'calle', cam: 'establish', cast: {}, title: {over: 'Capítulo 2', text: 'Año 10 a 25'}}]],
  21: [[.35, {loc: 'calle', cam: 'alquilaTwo', cast: CALLE}], [1, {insert: anio(15, '≈ $20.900', '$11.880', [{label: 'Ganancias ≈ aportes', value: '≈'}])}]],
  22: [[1, Object.assign({loc: 'calle', cast: CALLE}, cl('cup', -.3, {dist: 7.2}))]],
  23: [[1, {insert: anio(20, '≈ $34.400', '$15.840')}]],
  24: [[.5, {insert: anio(25, '≈ $53.500', '$19.800', [{label: 'Ganancias', value: '≈ 2 × aportes', hl: true}])}], [1, Object.assign({loc: 'calle', cast: CALLE, gesture: {moni: 'armsUp'}}, cl('moni', .3, {dist: 7.2}))]],
  25: [[.4, {loc: 'calle', cam: 'alquilaTwo', cast: CALLE}], [1, {insert: nb('El cruce', [{t: 'Interés del año'}, {t: 'supera'}, {t: 'lo que ponés por año', c: G}, {t: '→ la bola de nieve rueda sola', c: G}])}]],
  26: [[1, Object.assign({loc: 'calle', cast: CALLE}, cl('cup', -.3, {dist: 7.2}))]],
  27: [[1, {loc: 'calle', cam: 'alquilaTwo', cast: CALLE, push: .12}]],
  // ── año 25 a 40: en el banco ──
  28: [[1, {loc: 'calle', cam: 'bancoFront', cast: {}, title: {over: 'Capítulo 3', text: 'Año 25 a 40'}}]],
  29: [[.4, {loc: 'banco', cam: 'two', cast: BANCO}], [1, {insert: anio(30, '≈ $80.500', '$23.760')}]],
  30: [[1, {insert: anio(35, '≈ $118.800', '$27.720')}]],
  31: [[.5, {insert: res('MONI B · AÑO 40', [{t: 'Total', v: '$173.238', vc: G}], '¡40 AÑOS!')}], [1, Object.assign({loc: 'banco', cast: BANCO, gesture: {moni: 'armsUp'}}, cl('moni', .25))]],
  32: [[.6, {insert: res('MONI B · AÑO 40', [{t: 'Total', v: '$173.238', vc: G}, {t: 'Puso', v: '$31.680'}, {t: 'Interés', v: '+$141.558', vc: G}])}], [1, {loc: 'banco', cam: 'wide', cast: BANCO}]],
  33: [[.5, {loc: 'banco', cam: 'two', cast: BANCO}], [1, {insert: nb('Moni A en 40 años', [{t: 'Cafés tomados', v: '10.560', vc: R}])}]],
  34: [[1, Object.assign({loc: 'banco', cast: BANCO, gesture: {cup: 'armsUp'}}, cl('cup', -.3))]],
  35: [[1, Object.assign({loc: 'banco', cast: BANCO}, cl('moni', .25))]],
  // ── la trampa: cafetería ──
  36: [[1, {loc: 'calle', cam: 'cafeFront', cast: {}, title: {over: 'Capítulo 4', text: 'La trampa'}}]],
  37: [[1, {loc: 'cafeteria', cam: 'two', cast: CAFE}]],
  38: [[1, Object.assign({loc: 'cafeteria', cast: CAFE, gesture: {cup: 'wave'}}, cl('cup', -.25))]],
  39: [[.4, Object.assign({loc: 'cafeteria', cast: CAFE}, cl('moni', .25))], [1, {insert: nb('La trampa', [{t: '1. Inflación', c: R}, {t: '$173.000 en 40 años'}, {t: 'compran menos que hoy'}])}]],
  40: [[1, Object.assign({loc: 'cafeteria', cast: CAFE}, cl('cup', -.25))]],
  41: [[.5, {insert: nb('La trampa', [{t: '1. Inflación', c: R}, {t: '2. El café te hace feliz', c: R}])}], [1, {loc: 'cafeteria', cam: 'two', cast: CAFE}]],
  42: [[.4, Object.assign({loc: 'cafeteria', cast: CAFE}, cl('moni', .25))], [1, {insert: nb('La trampa', [{t: '1. Inflación', c: R}, {t: '2. El café te hace feliz', c: R}, {t: '3. Los gastos grandes', c: R}, {t: 'vivienda · auto · comisiones'}])}]],
  43: [[1, {loc: 'cafeteria', cam: 'wide', cast: CAFE, push: .1}]],
  // ── tu versión: escritorio ──
  44: [[1, {loc: 'depto', cam: 'deskWide', cast: {}, title: {over: 'Capítulo 5', text: 'Tu versión'}}]],
  45: [[1, {loc: 'depto', cam: 'deskWide', cast: DESK}]],
  46: [[.25, Object.assign({loc: 'depto', cast: DESK}, cl('moni', -.35))], [1, {insert: nb('Encontrá tu café', [{t: '1. ¿Qué pago seguido?'}, {t: '2. ¿Cuánto suma por mes?'}, {t: '3. ¿Me hace feliz?'}])}]],
  47: [[.45, {insert: nb('Tu cuenta', [{t: 'Monto por mes'}, {t: '× 12'}, {t: '× años que te faltan'}, {t: '→ calculadora de interés', c: G}])}], [1, {loc: 'depto', cam: 'deskOver', cast: DESK}]],
  48: [[1, Object.assign({loc: 'depto', cast: DESK, gesture: {moni: 'wave'}}, cl('moni', -.35))]],
  // ── los gastos grandes: el auto en la calle ──
  49: [[1, {loc: 'calle', cam: 'street', cast: {}, title: {over: 'Capítulo 6', text: 'Los gastos grandes'}}]],
  50: [[1, Object.assign({loc: 'calle', cast: AUTO, enter: {car: [6, 0]}}, cl('car', -.3, {dist: 7.6}))]],
  51: [[.4, {loc: 'calle', cam: 'autoTwo', cast: AUTO}], [1, {insert: res('AUTO USADO', [{t: 'Más barato', v: '$10.000'}, {t: 'Invertido 10 años', v: ''}, {t: 'al 7 %', v: '≈ $19.600', vc: G}])}]],
  52: [[1, Object.assign({loc: 'calle', cast: AUTO, gesture: {car: 'armsUp'}}, cl('car', -.3, {dist: 7.6}))]],
  53: [[.35, Object.assign({loc: 'calle', cast: AUTO}, cl('moni', .3, {dist: 7.2}))], [1, {insert: res('COMISIONES', [{t: '$10.000 · 30 años'}, {t: '1 % vs. 0,1 %'}, {t: 'Perdés', v: '≈ $16.500', vc: R}])}]],
  54: [[1, {loc: 'calle', cam: 'autoTwo', cast: AUTO, push: .12}]],
  // ── por qué casi nadie lo hace: living ──
  55: [[1, {loc: 'depto', cam: 'wide', cast: {}, title: {over: 'Capítulo 7', text: 'Por qué casi nadie lo hace'}}]],
  56: [[1, {loc: 'depto', cam: 'two', cast: SOFA}]],
  57: [[.45, Object.assign({loc: 'depto', cast: SOFA}, cl('moni', .3))], [1, {insert: nb('Por qué no lo hacemos', [{t: '1. No se ve por años', c: R}])}]],
  58: [[1, Object.assign({loc: 'depto', cast: SOFA}, cl('cup', -.3))]],
  59: [[.45, {insert: nb('Por qué no lo hacemos', [{t: '1. No se ve por años', c: R}, {t: '2. $66 parece poco', c: R}])}], [1, {loc: 'depto', cam: 'two', cast: SOFA}]],
  60: [[.5, {insert: nb('Por qué no lo hacemos', [{t: '1. No se ve por años', c: R}, {t: '2. $66 parece poco', c: R}, {t: '3. No hay sistema', c: R}])}], [1, Object.assign({loc: 'depto', cast: SOFA}, cl('moni', .3))]],
  61: [[.5, {insert: {prop: 'celular', content: {app: 'Día de cobro', color: '#0E5A40', rows: [{label: 'Transferencia automática', value: '$66', hl: true}, {label: 'Destino', value: 'Inversión'}]}}}], [1, {loc: 'depto', cam: 'two', cast: SOFA}]],
  // ── diez años de atraso: calle ──
  62: [[1, {loc: 'calle', cam: 'establish', cast: {}, title: {over: 'Capítulo 8', text: 'Con 10 años de atraso'}}]],
  63: [[1, Object.assign({loc: 'calle', cast: CALLE}, cl('cup', -.3, {dist: 7.2}))]],
  64: [[.4, {loc: 'calle', cam: 'alquilaTwo', cast: CALLE}], [1, {insert: anio(30, '≈ $80.500', '$23.760', [{label: 'Empezó a los', value: '35 años'}])}]],
  65: [[.6, {insert: res('ANTES vs. DESPUÉS', [{t: '40 años', v: '$173.238', vc: G}, {t: '30 años', v: '$80.500', vc: R}], '-10 AÑOS')}], [1, Object.assign({loc: 'calle', cast: CALLE, gesture: {moni: 'armsUp'}}, cl('moni', .3, {dist: 7.2}))]],
  66: [[1, {loc: 'calle', cam: 'alquilaTwo', cast: CALLE}]],
  67: [[1, Object.assign({loc: 'calle', cast: CALLE}, cl('moni', .3, {dist: 7.2}))]],
  // ── las tres Monis: cafetería ──
  68: [[1, {loc: 'calle', cam: 'cafeFront', cast: {}, title: {over: 'Capítulo 9', text: 'Las tres Monis'}}]],
  69: [[1, {loc: 'cafeteria', cam: 'two', cast: CAFE}]],
  70: [[.4, {loc: 'cafeteria', cam: 'queue', cast: CAFE}], [1, {insert: nb('Tres Monis', [{t: 'A · todo el café', v: '$0', vc: R}])}]],
  71: [[1, {insert: nb('Tres Monis', [{t: 'A · todo el café', v: '$0', vc: R}, {t: 'B · cero café', v: '$66/mes', vc: G}])}]],
  72: [[.4, Object.assign({loc: 'cafeteria', cast: CAFE}, cl('moni', .25))], [1, {insert: nb('Tres Monis', [{t: 'A · todo el café', v: '$0', vc: R}, {t: 'B · cero café', v: '$66/mes', vc: G}, {t: 'C · café los sábados', v: '$54/mes', vc: G}])}]],
  73: [[1, Object.assign({loc: 'cafeteria', cast: CAFE, gesture: {cup: 'armsUp'}}, cl('cup', -.25))]],
  74: [[.55, {insert: nb('A los 40 años', [{t: 'Moni A', v: '$0', vc: R}, {t: 'Moni B', v: '$173.238', vc: G}, {t: 'Moni C', v: '≈ $142.000', vc: G}])}], [1, Object.assign({loc: 'cafeteria', cast: CAFE}, cl('moni', .25))]],
  75: [[1, {loc: 'cafeteria', cam: 'wide', cast: CAFE, push: .1}]],
  // ── resumen: escritorio ──
  76: [[1, {loc: 'depto', cam: 'deskWide', cast: {}, title: {over: 'En 30 segundos', text: 'Resumen'}}]],
  77: [[.45, {loc: 'depto', cam: 'deskWide', cast: DESK}], [1, {insert: nb('Resumen', [{t: '$66/mes · 40 años · 7 %'}, {t: '≈ $173.000', c: G}])}]],
  78: [[.5, {insert: nb('Resumen', [{t: '$66/mes · 40 años · 7 %'}, {t: '≈ $173.000', c: G}, {t: '− inflación', c: R}, {t: '+ el café puede valer la pena'}, {t: 'los gastos grandes pesan más', c: R}])}], [1, Object.assign({loc: 'depto', cast: DESK}, cl('moni', -.35))]],
  79: [[1, {loc: 'depto', cam: 'deskOver', cast: DESK, push: .15}]],
  // ── cierre: living ──
  80: [[1, {loc: 'depto', cam: 'wide', cast: SOFA, title: {over: 'Moni Finanzas', text: 'Cierre'}}]],
  81: [[.5, {loc: 'depto', cam: 'two', cast: SOFA}], [1, Object.assign({loc: 'depto', cast: SOFA}, cl('moni', .3))]],
  82: [[1, Object.assign({loc: 'depto', cast: SOFA}, cl('cup', -.3))]],
  83: [[1, {loc: 'depto', cam: 'two', cast: SOFA, gesture: {moni: 'wave'}}]],
  84: [[.5, Object.assign({loc: 'depto', cast: SOFA}, cl('moni', .3))], [1, {insert: nb('¿Cuál es tu café?', [{t: 'Contámelo en los comentarios'}])}]],
  85: [[1, {loc: 'depto', cam: 'two', cast: SOFA, push: .12}]],
  86: [[1, {loc: 'depto', cam: 'wide', cast: SOFA, gesture: {moni: 'wave', cup: 'wave'}, push: .2}]],
};
