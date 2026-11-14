// Scripted full shift on the Night Shift page. Usage: node tools/test_game_playthrough.mjs [url] [width] [height]
// Start a server first for local runs: python3 -m http.server 8123 --bind 127.0.0.1
import fs from 'fs';
import { spawn } from 'child_process';
const url = process.argv[2] || 'https://ai-hackathon-only.github.io/zoo-assets/game/';
const W = +process.argv[3] || 1280, H = +process.argv[4] || 800;
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', ['--headless=new', '--use-gl=angle', '--enable-webgl',
  '--remote-debugging-port=0', `--user-data-dir=${fs.mkdtempSync('/tmp/chrome-game-')}`, '--no-first-run', `--window-size=${W},${H}`]);
let wsUrl = ''; chrome.stderr.on('data', (d) => { const m = d.toString().match(/ws:\/\/[^\s]+/); if (m && !wsUrl) wsUrl = m[0]; });
while (!wsUrl) await new Promise((r) => setTimeout(r, 50));
const ws = new WebSocket(wsUrl); await new Promise((r) => (ws.onopen = r));
let id = 1; const cbs = new Map(); const errors = []; let sid;
ws.onmessage = (e) => { const m = JSON.parse(e.data);
  if (m.id && cbs.has(m.id)) { cbs.get(m.id)(m); cbs.delete(m.id); }
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errors.push(m.params.args.map((a) => a.value || a.description).join(' '));
  if (m.method === 'Runtime.exceptionThrown') errors.push(m.params.exceptionDetails?.exception?.description || m.params.exceptionDetails.text); };
const send = (method, params = {}, s) => new Promise((res) => { const i = id++; cbs.set(i, res); ws.send(JSON.stringify({ id: i, sessionId: s, method, params })); });
const t = await send('Target.createTarget', { url: 'about:blank' });
sid = (await send('Target.attachToTarget', { targetId: t.result.targetId, flatten: true })).result.sessionId;
const ev = async (expr) => (await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true }, sid)).result?.result?.value;
await send('Runtime.enable', {}, sid); await send('Page.enable', {}, sid);
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 600 }, sid);
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'png' }, sid); fs.writeFileSync(`/tmp/game-${W}-${name}.png`, Buffer.from(r.result.data, 'base64')); console.log('shot', `/tmp/game-${W}-${name}.png`); };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const t0 = Date.now();
await send('Page.navigate', { url }, sid);
for (let i = 0; i < 40 && !(await ev('!!window.game')); i++) await sleep(250);
console.log('start screen:', await ev('window.game.debug.getState().screen')); await shot('start');
await ev("document.getElementById('go').click()");
for (let i = 0; i < 120 && (await ev('window.game.debug.getState().screen')) !== 'play'; i++) await sleep(250);
console.log(`play after ${Date.now() - t0} ms (page+assets, this machine)`); await sleep(1000); await shot('play');
// real input: hold E near nothing, then WASD for a moment
await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'd' }, sid); await sleep(500); await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'd' }, sid);
console.log('after D key:', await ev('JSON.stringify(window.game.debug.getState().player)'));
const types = await ev('JSON.stringify([...new Set(window.game.debug.getState().tasks.map(t=>t.type))])');
console.log('task types:', types);
for (const ty of JSON.parse(types)) { console.log('complete', ty, await ev(`JSON.stringify(window.game.debug.completeTask('${ty}'))`)); await sleep(300); }
while (await ev("JSON.stringify(window.game.debug.completeTask())") !== 'null') await sleep(200);
await sleep(600); await shot('tasks-done');
console.log('state:', await ev('JSON.stringify(window.game.debug.getState().tasks.map(t=>t.status))'));
for (let i = 0; i < 30 && (await ev('window.game.debug.getState().screen')) !== 'end'; i++) await sleep(300);
console.log('end screen:', await ev('window.game.debug.getState().screen')); await shot('end');
console.log('console errors:', errors.length ? errors : 'none');
chrome.kill(); process.exit(errors.length ? 1 : 0);
