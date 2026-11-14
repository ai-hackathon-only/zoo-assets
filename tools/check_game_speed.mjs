/**
 * Headless Chrome CDP speed & console check for game/ (Night Shift).
 * Measures first-frame/ready time (< 8 s) and walking FPS (>= 30 fps)
 * at 1280x800 and 390x844 in both Toy and Sumi-e looks.
 *
 * Usage:
 *   node tools/check_game_speed.mjs [url]
 */
import fs from 'fs';
import { spawn, execSync } from 'child_process';

const targetUrl = process.argv[2] || 'https://ai-hackathon-only.github.io/zoo-assets/game/';

let cpuInfo = 'Unknown CPU';
let gpuInfo = 'Unknown GPU';
try { cpuInfo = execSync('sysctl -n machdep.cpu.brand_string', { encoding: 'utf8' }).trim(); } catch (e) {}
try {
  const sp = execSync('system_profiler SPDisplaysDataType', { encoding: 'utf8' });
  const m = sp.match(/Chipset Model:\s*(.+)/);
  if (m) gpuInfo = m[1].trim();
} catch (e) {}

console.log(`=== Night Shift Speed Check ===`);
console.log(`Machine: ${cpuInfo} · GPU: ${gpuInfo}`);
console.log(`Target: ${targetUrl}`);

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const userDataDir = fs.mkdtempSync('/tmp/chrome-game-speed-');
const chrome = spawn(chromePath, [
  '--headless=new', '--use-gl=angle', '--enable-webgl',
  '--remote-debugging-port=0',
  `--user-data-dir=${userDataDir}`,
  '--no-first-run', '--no-default-browser-check',
  '--window-size=1280,800'
]);

let wsUrl = '';
chrome.stderr.on('data', d => {
  const m = d.toString().match(/ws:\/\/[^\s]+/);
  if (m && !wsUrl) wsUrl = m[0];
});

for (let i = 0; i < 50 && !wsUrl; i++) {
  await new Promise(r => setTimeout(r, 100));
}
if (!wsUrl) throw new Error('Timeout waiting for Chrome WS');

const res = await fetch(wsUrl.replace('ws://', 'http://').replace(/\/devtools\/browser\/.*/, '/json/list'));
const targets = await res.json();
const pageTarget = targets.find(t => t.type === 'page') || targets[0];
const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r));

let msgId = 1;
const pending = new Map();
const consoleErrors = [];

ws.addEventListener('message', ev => {
  const data = JSON.parse(ev.data);
  if (data.id && pending.has(data.id)) {
    const { resolve, reject } = pending.get(data.id);
    pending.delete(data.id);
    if (data.error) reject(new Error(data.error.message));
    else resolve(data.result);
  } else if (data.method === 'Runtime.consoleAPICalled' && data.params.type === 'error') {
    consoleErrors.push(data.params.args.map(a => a.value || a.description || '').join(' '));
  } else if (data.method === 'Runtime.exceptionThrown') {
    consoleErrors.push(data.params.exceptionDetails.text || 'Exception');
  }
});

function cdp(method, params = {}) {
  const id = msgId++;
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });
}

async function measureFps(durationMs = 2000) {
  const r = await cdp('Runtime.evaluate', {
    expression: `new Promise(resolve => {
      let frames = 0;
      const start = performance.now();
      function tick() {
        frames++;
        const dt = performance.now() - start;
        if (dt >= ${durationMs}) resolve(Math.round(frames * 1000 / dt));
        else requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    })`,
    awaitPromise: true,
    returnByValue: true
  });
  return r.result.value;
}

await cdp('Page.enable');
await cdp('Runtime.enable');
await cdp('Network.enable');
await cdp('Network.setCacheDisabled', { cacheDisabled: true });

async function getPos() {
  const r = await cdp('Runtime.evaluate', {
    expression: 'window.game.debug.getState().playerPosition',
    returnByValue: true
  });
  return r.result.value;
}

function distXZ(a, b) {
  return Math.hypot((b[0] || 0) - (a[0] || 0), (b[2] || 0) - (a[2] || 0));
}

async function runViewport(label, width, height, deviceScaleFactor, mobile) {
  await cdp('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor, mobile });
  const t0 = Date.now();
  await cdp('Page.navigate', { url: targetUrl });

  let firstFrameMs = 0;
  for (let i = 0; i < 150; i++) {
    const evalRes = await cdp('Runtime.evaluate', {
      expression: 'Boolean(window.game && window.game.debug && window.game.debug.getState && window.game.debug.getState().tasks.length > 0)',
      returnByValue: true
    });
    if (evalRes.result.value) {
      await cdp('Runtime.evaluate', {
        expression: 'new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))',
        awaitPromise: true
      });
      firstFrameMs = Date.now() - t0;
      break;
    }
    await new Promise(r => setTimeout(r, 100));
  }

  await cdp('Runtime.evaluate', {
    expression: `(() => { const b = document.getElementById('start-btn'); if (b) b.click(); })()`
  });
  await new Promise(r => setTimeout(r, 800));

  const p0 = await getPos();
  await cdp('Runtime.evaluate', {
    expression: `window.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyW', key: 'w' }))`
  });
  const fpsToy = await measureFps();
  await cdp('Runtime.evaluate', {
    expression: `window.dispatchEvent(new KeyboardEvent('keyup', { code: 'KeyW', key: 'w' }))`
  });
  const p1 = await getPos();
  const movedToy = distXZ(p0, p1);

  await cdp('Runtime.evaluate', {
    expression: `(() => { const b = document.getElementById('hud-look-btn'); if (b) b.click(); })()`
  });
  await new Promise(r => setTimeout(r, 400));

  const p2 = await getPos();
  await cdp('Runtime.evaluate', {
    expression: `window.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyS', key: 's' }))`
  });
  const fpsInk = await measureFps();
  await cdp('Runtime.evaluate', {
    expression: `window.dispatchEvent(new KeyboardEvent('keyup', { code: 'KeyS', key: 's' }))`
  });
  const p3 = await getPos();
  const movedInk = distXZ(p2, p3);

  console.log(`${label} world-ready + first-frame: ${firstFrameMs} ms (limit < 8000 ms)`);
  console.log(`${label} walking FPS (Toy): ${fpsToy} fps (moved ${movedToy.toFixed(1)} m, limit >= 30 fps)`);
  console.log(`${label} walking FPS (Sumi-e): ${fpsInk} fps (moved ${movedInk.toFixed(1)} m, limit >= 30 fps)`);

  return firstFrameMs > 0 && firstFrameMs < 8000 &&
    fpsToy >= 30 && fpsInk >= 30 &&
    movedToy >= 0.5 && movedInk >= 0.5;
}

const ok1280 = await runViewport('1280x800', 1280, 800, 1, false);
const ok390 = await runViewport('390x844', 390, 844, 2, true);
console.log(`Console errors: ${consoleErrors.length === 0 ? 'none' : consoleErrors.join('; ')}`);

const passed = ok1280 && ok390 && consoleErrors.length === 0;

ws.close();
chrome.kill();
try { fs.rmSync(userDataDir, { recursive: true, force: true }); } catch (e) {}
process.exit(passed ? 0 : 1);
