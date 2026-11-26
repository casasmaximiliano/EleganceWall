// Planos del video 25 (Cambiá tus finanzas en 90 días). Índice = escena del timeline (out/timeline/25.json).
// Cada escena: lista de [hasta (fracción de la escena), plano]. Plano: {loc, cam, cast, insert, title, gesture, propSet, push}.
const SOFA = {moni: 'sofaL', card: 'sofaR'};
const DESK = {moni: 'escritorio', centavito: 'junto'};
const DESK_T = {moni: 'escritorio', centavito: 'junto', card: 'detras'};
const CAFE = {moni: 'mesaA', cup: 'mesaB'};
const CAFE_D = {moni: 'mesaA', cup: 'mesaB', bag: 'llega'};
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
};
