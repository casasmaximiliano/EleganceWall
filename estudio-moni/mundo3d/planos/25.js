// Planos del video 25 (Cambiá tus finanzas en 90 días). Índice = escena del timeline (out/timeline/25.json).
// Cada escena: lista de [hasta (fracción de la escena), plano]. Plano: {loc, cam, cast, insert, title, gesture, propSet, push}.
const SOFA = {moni: 'sofaL', card: 'sofaR'};
const DESK = {moni: 'escritorio', centavito: 'junto'};
const DESK_T = {moni: 'escritorio', centavito: 'junto', card: 'detras'};
const CAFE = {moni: 'mesaA', cup: 'mesaB'};
const CAFE_D = {moni: 'mesaA', cup: 'mesaB', bag: 'llega'};
const BANCO = {moni: 'ventanilla', card: 'junto'};
const INFLA = {moni: 'sofaL', ghost: 'flota'};
const CALLE = {moni: 'alquilaA', cup: 'alquilaB'};
const PLAN = [{t: 'Días 1-7: anotar 5 números'}, {t: 'Días 8-30: gastos hormiga'}, {t: 'Días 31-60: deuda más cara'}, {t: 'Días 61-90: automatizar'}, {t: 'Día 90: la misma foto', c: '#17865A'}];
const nb = (title, lines) => ({prop: 'cuaderno', content: {title, lines}});
const G = '#17865A';
module.exports = {
  0: [[.45, {loc: 'depto', cam: 'two', cast: SOFA, push: .1}], [1, {loc: 'depto', cam: 'close:card', cast: SOFA, camOpt: {angle: -.25}}]],
  1: [[.55, {loc: 'depto', cam: 'close:moni', cast: SOFA, camOpt: {angle: .3}}], [1, {loc: 'depto', cam: 'calendario', cast: SOFA, push: .12}]],
  2: [[1, {loc: 'depto', cam: 'close:card', cast: SOFA, camOpt: {angle: -.35, dist: 3.8}, gesture: {card: 'shock'}}]],
  3: [[.45, {loc: 'depto', cam: 'two', cast: SOFA}], [1, {insert: nb('Mis 5 números', [{t: '1. Lo que entra'}, {t: '2. Lo que sale'}, {t: '3. Lo que me queda'}, {t: '4. Lo que debo'}, {t: '5. Mi colchón'}])}]],
  4: [[.55, {loc: 'depto', cam: 'wide', cast: SOFA, push: .15}], [1, {loc: 'depto', cam: 'close:moni', cast: SOFA, camOpt: {angle: .2}, gesture: {moni: 'wave'}}]],
  5: [[1, {loc: 'depto', cam: 'two', cast: SOFA, push: .12}]],
  6: [[1, {loc: 'calle', cam: 'establish', cast: {}, title: {over: 'Días 1 a 7', text: 'La foto'}}]],
  7: [[.5, {loc: 'depto', cam: 'deskWide', cast: DESK}], [1, {insert: {prop: 'resumen', content: {title: 'RESUMEN DEL BANCO', lines: [{t: 'Sueldo', v: '+$1.200', vc: G}, {t: 'Alquiler', v: '−$450'}, {t: 'Súper', v: '−$280'}, {t: 'Delivery', v: '−$60'}, {t: 'Café', v: '−$66'}, {t: 'Otros', v: '−$294'}]}}}]],
  8: [[.6, {insert: {prop: 'celular', content: {rows: [{label: 'Ingresos del mes', value: '+$1.200', hl: true}]}}}], [1, {loc: 'depto', cam: 'close:moni', cast: DESK, camOpt: {angle: -.3}}]],
  9: [[.6, {insert: {prop: 'celular', content: {rows: [{label: 'Ingresos del mes', value: '+$1.200'}, {label: 'Gastos del mes', value: '−$1.150', neg: true, hl: true}]}}}], [1, {loc: 'depto', cam: 'close:centavito', cast: DESK, camOpt: {dist: 4.2}, gesture: {centavito: 'shock'}}]],
  10: [[.6, {insert: nb('Mis 5 números', [{t: '1. Entra', v: '$1.200', vc: G}, {t: '2. Sale', v: '$1.150'}, {t: '3. Me queda', v: '4 %'}])}], [1, {loc: 'depto', cam: 'close:moni', cast: DESK, camOpt: {angle: -.35}}]],
  11: [[.5, {insert: {prop: 'resumen', content: {title: 'TARJETA DE CRÉDITO', lines: [{t: 'Saldo', v: '$900'}, {t: 'Tasa anual', v: '40 %'}, {t: 'Pago mínimo', v: '$27'}], stamp: '¡OJO!'}}}], [1, {loc: 'depto', cam: 'deskOver', cast: DESK_T}]],
  12: [[.45, {insert: {prop: 'alcancia', cam: {p: [0, 3.2, 4.4], look: [0, 1, 0], fov: 34}}}], [1, {loc: 'depto', cam: 'close:moni', cast: DESK, camOpt: {angle: -.35}}]],
  13: [[.5, {loc: 'depto', cam: 'close:moni', cast: DESK, camOpt: {dist: 4.6, angle: -.35}, push: .1}], [1, {loc: 'depto', cam: 'deskWide', cast: DESK}]],
  14: [[.5, {insert: nb('Día 1 · mis 5 números', [{t: '1. Entra', v: '$1.200', vc: G}, {t: '2. Sale', v: '$1.150'}, {t: '3. Me queda', v: '4 %'}, {t: '4. Debo', v: '$900'}, {t: '5. Colchón', v: '0 meses'}])}], [1, {loc: 'depto', cam: 'deskWide', cast: DESK, push: .12}]],
  15: [[1, {loc: 'calle', cam: 'cafeFront', cast: {}, title: {over: 'Días 8 a 30', text: 'Los gastos hormiga'}}]],
  16: [[1, {loc: 'cafeteria', cam: 'close:cup', cast: CAFE, camOpt: {angle: -.2}}]],
  17: [[.5, {loc: 'cafeteria', cam: 'two', cast: CAFE}], [1, {loc: 'cafeteria', cam: 'close:moni', cast: CAFE, camOpt: {angle: .25}}]],
  18: [[.5, {loc: 'cafeteria', cam: 'menu', cast: CAFE, propSet: {name: 'menu', content: {items: [['Café', '$3'], ['Latte', '$3,50'], ['Medialuna', '$1,50'], ['Tostado', '$4']], note: '22 cafés × $3 = $66 al mes'}}}], [1, {loc: 'cafeteria', cam: 'wide', cast: CAFE}]],
  19: [[1, {loc: 'cafeteria', cam: 'close:cup', cast: CAFE, camOpt: {angle: -.15}, gesture: {cup: 'wave'}}]],
  20: [[1, {loc: 'cafeteria', cam: 'close:bag', cast: CAFE_D, camOpt: {dist: 6.2, angle: .2}}]],
  21: [[.5, {loc: 'cafeteria', cam: 'two', cast: CAFE_D}], [1, {insert: {prop: 'celular', content: {app: 'YA! Delivery', color: '#E85D4E', rows: [{label: 'Pedidos este mes', value: '4 × $15'}, {label: 'Total', value: '$60', neg: true, hl: true}]}}}]],

  // ── gastos hormiga: suscripciones (living) y gimnasio (calle) ──
  22: [[.5, {loc: 'depto', cam: 'two', cast: {moni: 'sofaL', zombi: 'sofaR'}}], [1, {insert: {prop: 'celular', content: {app: 'Mis suscripciones', color: '#6B5B95', rows: [{label: '4 plataformas', value: '4 × $10'}, {label: 'Por mes', value: '$40', neg: true, hl: true}]}}}]],
  23: [[.55, {loc: 'depto', cam: 'close:moni', cast: {moni: 'sofaL', zombi: 'sofaR'}, camOpt: {angle: .3}}], [1, {insert: {prop: 'celular', content: {app: 'Mis suscripciones', color: '#6B5B95', rows: [{label: '1 por vez, rotando', value: '$10', hl: true}, {label: 'Ahorro', value: '+$30'}]}}}]],
  24: [[1, {loc: 'calle', cam: 'gymTwo', cast: {moni: 'vereda', gymzombi: 'vereda2'}, enter: {gymzombi: [5, 0]}}]],
  25: [[.5, {insert: {prop: 'celular', content: {app: 'Gimnasio', color: '#2F6DB5', rows: [{label: 'Cuota mensual', value: '$40', neg: true}, {label: '2 clases sueltas', value: '2 × $8 = $16', hl: true}]}}}], [1, {loc: 'calle', cam: 'close:moni', cast: {moni: 'vereda', gymzombi: 'vereda2'}, camOpt: {angle: .3, dist: 7.2}}]],
  26: [[.6, {insert: nb('Gastos hormiga', [{t: 'Café', v: '+$53', vc: G}, {t: 'Delivery', v: '+$45', vc: G}, {t: 'Suscripciones', v: '+$30', vc: G}, {t: 'Gimnasio', v: '+$24', vc: G}, {t: 'TOTAL POR MES', v: '+$152', vc: G}])}], [1, {loc: 'calle', cam: 'gymTwo', cast: {moni: 'vereda', gymzombi: 'vereda2'}, gesture: {moni: 'armsUp'}}]],
  27: [[.45, {insert: {prop: 'alcancia', cam: {p: [0, 3.2, 4.4], look: [0, 1, 0], fov: 34}}}], [1, {loc: 'depto', cam: 'deskWide', cast: DESK, push: .1}]],
  // ── Tarjetín en el banco ──
  28: [[1, {loc: 'calle', cam: 'bancoFront', cast: {}, title: {over: 'Días 31 a 60', text: 'Tarjetín'}}]],
  29: [[1, {loc: 'banco', cam: 'two', cast: BANCO, enter: {card: [5, 1]}}]],
  30: [[1, {loc: 'banco', cam: 'close:moni', cast: BANCO, camOpt: {angle: .25}}]],
  31: [[1, {loc: 'banco', cam: 'close:card', cast: BANCO, camOpt: {angle: -.25}, gesture: {card: 'shock'}}]],
  32: [[.4, {loc: 'banco', cam: 'two', cast: BANCO}], [1, {insert: {prop: 'resumen', content: {title: 'PAGANDO EL MÍNIMO', lines: [{t: 'Deuda', v: '$900'}, {t: 'Interés del mes', v: '+$30'}, {t: 'Pago mínimo', v: '−$27', vc: G}]}}}]],
  33: [[.6, {insert: {prop: 'resumen', content: {title: 'PAGANDO EL MÍNIMO', lines: [{t: 'Antes', v: '$900'}, {t: 'Un mes después', v: '$903'}], stamp: '¡SUBE!'}}}], [1, {loc: 'banco', cam: 'close:card', cast: BANCO, camOpt: {angle: -.25}}]],
  34: [[.6, {insert: {prop: 'resumen', content: {title: 'PAGANDO $200', lines: [{t: 'Antes', v: '$900'}, {t: 'Un mes después', v: '$730', vc: G}]}}}], [1, {loc: 'banco', cam: 'close:moni', cast: BANCO, camOpt: {angle: .25}}]],
  35: [[1, {loc: 'banco', cam: 'close:card', cast: BANCO, camOpt: {angle: -.3}}]],
  36: [[.5, {loc: 'banco', cam: 'two', cast: BANCO}], [1, {insert: nb('Regla de la tarjeta', [{t: 'Solo cargo lo que puedo'}, {t: 'pagar COMPLETO'}, {t: 'cuando llega el resumen.'}])}]],
  37: [[.6, {insert: nb('Mis deudas', [{t: '1. Tarjeta', v: '40 %'}, {t: '2. Préstamo', v: '25 %'}, {t: '3. Celular en cuotas', v: '0 %'}, {t: '→ primero la tasa más alta', c: '#17865A'}])}], [1, {loc: 'banco', cam: 'wide', cast: BANCO}]],
  38: [[.5, {loc: 'banco', cam: 'close:moni', cast: BANCO, camOpt: {angle: .2}}], [1, {insert: nb('Bola de nieve', [{t: 'Primero la más chica'}, {t: '→ un logro rápido', c: '#17865A'}, {t: 'Sirven las dos'}, {t: 'si las sostenés.'}])}]],
  // ── piloto automático con Infla ──
  39: [[1, {loc: 'banco', cam: 'est', cast: {}, title: {over: 'Días 61 a 90', text: 'El piloto automático'}}]],
  40: [[1, {loc: 'depto', cam: 'two', cast: INFLA, enter: {ghost: [5, -2]}}]],
  41: [[1, {loc: 'depto', cam: 'close:moni', cast: INFLA, camOpt: {angle: .3}}]],
  42: [[.5, {insert: {prop: 'celular', content: {app: 'Día de cobro', color: '#0E5A40', rows: [{label: 'Automática → Tarjeta', value: '$150'}, {label: 'Automática → Colchón', value: '$50', hl: true}]}}}], [.75, {loc: 'depto', cam: 'close:ghost', cast: INFLA, camOpt: {dist: 6.4}}], [1, {loc: 'depto', cam: 'two', cast: INFLA}]],
  43: [[.5, {loc: 'depto', cam: 'close:moni', cast: INFLA, camOpt: {angle: .3}}], [1, {loc: 'depto', cam: 'two', cast: INFLA}]],
  44: [[1, {loc: 'depto', cam: 'close:ghost', cast: INFLA, camOpt: {dist: 6.2}}]],
  45: [[.35, {loc: 'depto', cam: 'two', cast: INFLA}], [.7, {insert: nb('El orden', [{t: '1. Terminar la deuda'}, {t: '2. Unos meses de colchón'}, {t: '3. Recién ahí, invertir', c: '#17865A'}])}], [1, {loc: 'depto', cam: 'close:moni', cast: INFLA, camOpt: {angle: .3}}]],
  // ── día 90 ──
  46: [[1, {loc: 'depto', cam: 'wide', cast: {}, title: {over: 'Día 90', text: 'Los 5 números de nuevo'}}]],
  47: [[1, {loc: 'depto', cam: 'deskWide', cast: DESK_T}]],
  48: [[.6, {insert: nb('Día 90', [{t: '1. Entra', v: '$1.200 = $1.200', vc: '#22304A'}])}], [1, {loc: 'depto', cam: 'close:moni', cast: DESK_T, camOpt: {angle: -.35}}]],
  49: [[1, {insert: nb('Día 90', [{t: '1. Entra', v: '$1.200 = $1.200', vc: '#22304A'}, {t: '2. Sale', v: '$1.150 → $998', vc: G}])}]],
  50: [[.55, {insert: nb('Día 90', [{t: '1. Entra', v: '$1.200 = $1.200', vc: '#22304A'}, {t: '2. Sale', v: '$1.150 → $998', vc: G}, {t: '3. Me queda', v: '4 % → 17 %', vc: G}])}], [1, {loc: 'depto', cam: 'close:moni', cast: DESK_T, camOpt: {angle: -.35}, gesture: {moni: 'armsUp'}}]],
  51: [[.5, {insert: nb('Día 90', [{t: '1. Entra', v: '$1.200 = $1.200', vc: '#22304A'}, {t: '2. Sale', v: '$1.150 → $998', vc: G}, {t: '3. Me queda', v: '4 % → 17 %', vc: G}, {t: '4. Debo', v: '$900 → $604', vc: G}])}], [1, {loc: 'depto', cam: 'deskOver', cast: DESK_T}]],
  52: [[1, {loc: 'depto', cam: 'deskOver', cast: DESK_T, push: .18}]],
  53: [[.5, {insert: nb('Día 90', [{t: '1. Entra', v: '$1.200 = $1.200', vc: '#22304A'}, {t: '2. Sale', v: '$1.150 → $998', vc: G}, {t: '3. Me queda', v: '4 % → 17 %', vc: G}, {t: '4. Debo', v: '$900 → $604', vc: G}, {t: '5. Colchón', v: '$0 → $250', vc: G}])}], [1, {insert: {prop: 'alcancia', cam: {p: [0, 3.2, 4.4], look: [0, 1, 0], fov: 34}}}]],
  54: [[1, {loc: 'depto', cam: 'deskWide', cast: DESK_T, push: .15}]],
  // ── ¿y si no me sobra nada? (calle, alquileres) ──
  55: [[1, {loc: 'calle', cam: 'alquilaTwo', cast: {}, title: {over: 'La pregunta clave', text: '¿Y si no me sobra nada?'}}]],
  56: [[1, {loc: 'calle', cam: 'alquilaTwo', cast: CALLE}]],
  57: [[.5, {loc: 'calle', cam: 'close:moni', cast: CALLE, camOpt: {angle: .3, dist: 7.2}}], [1, {loc: 'calle', cam: 'alquilaTwo', cast: CALLE}]],
  58: [[1, {insert: nb('Los 3 grandes', [{t: 'Vivienda'}, {t: 'Transporte'}, {t: 'Comida'}, {t: '= la mayor parte del sueldo', c: '#C8102E'}])}]],
  59: [[.5, {loc: 'calle', cam: 'establish', cast: {}}], [1, {loc: 'calle', cam: 'alquilaTwo', cast: CALLE}]],
  60: [[.5, {insert: {prop: 'celular', content: {app: 'Ganar más', color: '#17865A', rows: [{label: 'Pedir un aumento con datos', value: '+', hl: true}, {label: 'Vender lo que no uso', value: '+'}, {label: 'Trabajo extra', value: '+'}]}}}], [1, {loc: 'calle', cam: 'close:moni', cast: CALLE, camOpt: {angle: .3, dist: 7.2}}]],
  // ── los 3 errores (cafetería) ──
  61: [[1, {loc: 'calle', cam: 'cafeFront', cast: {}, title: {over: 'Cuidado', text: 'Los 3 errores'}}]],
  62: [[1, {loc: 'cafeteria', cam: 'two', cast: CAFE}]],
  63: [[.5, {insert: nb('3 errores', [{t: '1. Hacer todo el primer día', c: '#C8102E'}])}], [1, {loc: 'cafeteria', cam: 'close:moni', cast: CAFE, camOpt: {angle: .25}}]],
  64: [[1, {loc: 'cafeteria', cam: 'close:cup', cast: CAFE, camOpt: {angle: -.2}}]],
  65: [[.4, {loc: 'cafeteria', cam: 'two', cast: CAFE}], [.7, {insert: nb('3 errores', [{t: '1. Hacer todo el primer día', c: '#C8102E'}, {t: '2. Cortar lo que te gusta', c: '#C8102E'}])}], [1, {loc: 'cafeteria', cam: 'close:moni', cast: CAFE, camOpt: {angle: .25}}]],
  66: [[.6, {insert: nb('3 errores', [{t: '1. Hacer todo el primer día', c: '#C8102E'}, {t: '2. Cortar lo que te gusta', c: '#C8102E'}, {t: '3. No automatizar', c: '#C8102E'}])}], [1, {loc: 'cafeteria', cam: 'wide', cast: CAFE}]],
  // ── tu plan en una hoja ──
  67: [[1, {loc: 'depto', cam: 'deskWide', cast: {}, title: {over: 'Para copiar', text: 'Tu plan en una hoja'}}]],
  68: [[.5, {loc: 'depto', cam: 'deskWide', cast: DESK}], [1, {insert: nb('Mi plan de 90 días', PLAN.slice(0, 1))}]],
  69: [[.5, {insert: nb('Mi plan de 90 días', PLAN.slice(0, 2))}], [1, {loc: 'depto', cam: 'close:moni', cast: DESK, camOpt: {angle: -.35}}]],
  70: [[.5, {insert: nb('Mi plan de 90 días', PLAN.slice(0, 3))}], [1, {loc: 'depto', cam: 'close:centavito', cast: DESK, camOpt: {dist: 4.2}}]],
  71: [[.5, {insert: nb('Mi plan de 90 días', PLAN.slice(0, 4))}], [1, {loc: 'depto', cam: 'deskWide', cast: DESK}]],
  72: [[.5, {insert: nb('Mi plan de 90 días', PLAN)}], [1, {loc: 'depto', cam: 'close:moni', cast: DESK, camOpt: {angle: -.35}}]],
  // ── cierre ──
  73: [[1, {loc: 'depto', cam: 'wide', cast: SOFA, title: {over: 'Moni Finanzas', text: 'Cierre'}}]],
  74: [[1, {loc: 'depto', cam: 'two', cast: SOFA}]],
  75: [[1, {loc: 'depto', cam: 'close:card', cast: SOFA, camOpt: {angle: -.3}}]],
  76: [[.5, {loc: 'depto', cam: 'close:moni', cast: SOFA, camOpt: {angle: .3}}], [1, {loc: 'depto', cam: 'two', cast: SOFA, gesture: {moni: 'wave'}}]],
  77: [[1, {loc: 'depto', cam: 'wide', cast: SOFA, gesture: {moni: 'wave', card: 'wave'}, push: .2}]],
};
