// Short 24 · El gimnasio al que no voy me costó $480 — vertical, en la vereda del gimnasio.
const GYM = {moni: 'vereda', gymzombi: 'vereda2'};
const TWO = {p: [1.0, 3.5, 3.4], look: [1.0, 2.5, -7.1], fov: 46};
module.exports = {
  0: [[1, {loc: 'calle', cam: 'close:gymzombi', camOpt: {angle: -.25, dist: 8.6, fov: 44}, cast: GYM, gesture: {gymzombi: 'armsUp'}, push: .12}]],
  1: [[1, {loc: 'calle', cam: TWO, cast: GYM, push: .1}]],
  2: [[.55, {loc: 'calle', cam: 'close:moni', camOpt: {angle: .3, dist: 8.6, fov: 44}, cast: GYM, gesture: {moni: 'armsUp'}}], [1, {loc: 'calle', cam: 'close:gymzombi', camOpt: {angle: -.3, dist: 8.6, fov: 44}, cast: GYM}]],
  3: [[1, {loc: 'calle', cam: TWO, cast: GYM, push: .14}]],
  4: [[1, {loc: 'calle', cam: 'close:moni', camOpt: {angle: .3, dist: 8.6, fov: 44}, cast: GYM, gesture: {moni: 'wave'}, push: .1}]],
};
