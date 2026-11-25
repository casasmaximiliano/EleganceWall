const {chromium} = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch({args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
  const p = await b.newPage({viewport: {width: 1920, height: 1080}});
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()) });
  await p.goto('file://' + path.join(__dirname, 'scene.html')); await p.waitForTimeout(500);
  for (const [t, s] of [[1, 0], [5, 1], [9, 2]]) { await p.evaluate(([t, s]) => window.renderAt(t, s), [t, s]); await p.screenshot({path: `out_${s}.jpg`, type: 'jpeg', quality: 85}) }
  const t0 = Date.now(); for (let i = 0; i < 0; i++) { await p.evaluate(t => window.renderAt(t), i / 24); await p.screenshot({type: 'jpeg', quality: 80}) }
  console.log('fps (render+captura):', (48 / ((Date.now() - t0) / 1000)).toFixed(2), errs.slice(0, 3));
  await b.close();
})();
