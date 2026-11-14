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
await cdp('Emulation.setDeviceMetricsOverride', { width: 1280, height: 800, deviceScaleFactor: 1, mobile: false });

const t0 = Date.now();
await cdp('Page.navigate', { url: targetUrl });

let firstFrameMs = 0;
for (let i = 0; i < 150; i++) {
  const evalRes = await cdp('Runtime.evaluate', {
    expression: 'Boolean(window.game && window.game.debug && window.game.debug.getState && window.game.debug.getState().tasks.length > 0)',
    returnByValue: true
  });
  if (evalRes.result.value) {
    firstFrameMs = Date.now() - t0;
    break;
  }
  await new Promise(r => setTimeout(r, 100));
}

await cdp('Runtime.evaluate', {
  expression: `(() => { const b = document.getElementById('start-btn'); if (b) b.click(); })()`
});
await new Promise(r => setTimeout(r, 800));

// 1280x800 Toy (walking)
await cdp('Input.dispatchKeyEvent', { type: 'keyDown', key: 'w', code: 'KeyW' });
const fps1280Toy = await measureFps();
await cdp('Input.dispatchKeyEvent', { type: 'keyUp', key: 'w', code: 'KeyW' });

// 1280x800 Sumi-e (walking)
await cdp('Runtime.evaluate', {
  expression: `(() => { const b = document.getElementById('hud-look-btn'); if (b) b.click(); })()`
});
await new Promise(r => setTimeout(r, 400));
await cdp('Input.dispatchKeyEvent', { type: 'keyDown', key: 's', code: 'KeyS' });
const fps1280Ink = await measureFps();
await cdp('Input.dispatchKeyEvent', { type: 'keyUp', key: 's', code: 'KeyS' });

// 390x844 Sumi-e -> Toy
await cdp('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
await new Promise(r => setTimeout(r, 500));
const fps390Ink = await measureFps();

await cdp('Runtime.evaluate', {
  expression: `(() => { const b = document.getElementById('hud-look-btn'); if (b) b.click(); })()`
});
await new Promise(r => setTimeout(r, 400));
const fps390Toy = await measureFps();

console.log(`1280x800 first-frame: ${firstFrameMs} ms (limit < 8000 ms)`);
console.log(`1280x800 walking FPS (Toy): ${fps1280Toy} fps (limit >= 30 fps)`);
console.log(`1280x800 walking FPS (Sumi-e): ${fps1280Ink} fps (limit >= 30 fps)`);
console.log(`390x844 FPS (Toy): ${fps390Toy} fps (limit >= 30 fps)`);
console.log(`390x844 FPS (Sumi-e): ${fps390Ink} fps (limit >= 30 fps)`);
console.log(`Console errors: ${consoleErrors.length === 0 ? 'none' : consoleErrors.join('; ')}`);

const passed = firstFrameMs > 0 && firstFrameMs < 8000 &&
  fps1280Toy >= 30 && fps1280Ink >= 30 && fps390Toy >= 30 && fps390Ink >= 30 &&
  consoleErrors.length === 0;

ws.close();
chrome.kill();
try { fs.rmSync(userDataDir, { recursive: true, force: true }); } catch (e) {}
process.exit(passed ? 0 : 1);
