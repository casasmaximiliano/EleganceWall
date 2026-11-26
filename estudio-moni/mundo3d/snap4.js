const {chromium} = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch({args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
  const p = await b.newPage({viewport: {width: 1920, height: 1080}}); const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()) });
  await p.goto('file://' + path.resolve('test_lugares.html')); await p.waitForTimeout(500);
  for (let v = 0; v < 4; v++) { try { await p.evaluate(v => window.renderAt(3.3, v), v); await p.screenshot({path: `/tmp/claude-0/-home-user-EleganceWall/0c1790d7-1aea-5252-afaf-c55984760b78/scratchpad/lug_${v}.jpg`, type: 'jpeg', quality: 85}) } catch (e) { errs.push(String(e).slice(0, 300)) } }
  console.log(errs.slice(0, 4)); await b.close() })();
