// node snap.js pagina.html salida.jpg [t]
const {chromium} = require('playwright'); const path = require('path');
(async () => { const [page, out, t] = process.argv.slice(2);
  const b = await chromium.launch({args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
  const p = await b.newPage({viewport: {width: 1920, height: 1080}}); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve(page)); await p.waitForTimeout(600);
  if (t) await p.evaluate(t => window.renderAt(+t), t);
  await p.screenshot({path: out, type: 'jpeg', quality: 88}); console.log('ok', errs.slice(0, 3)); await b.close() })();
