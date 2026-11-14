import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';

const rootDir = path.resolve('.');
const REF_ASSETS = [
  'lion',
  'giraffe',
  'giant_panda',
  'acacia_tree',
  'animal_transport_truck',
  'keeper_aquatic_feeder_03'
];

const server = http.createServer((req, res) => {
  let reqPath = req.url.split('?')[0];
  if (reqPath === '/') reqPath = '/index.html';
  else if (reqPath === '/park' || reqPath === '/park/') reqPath = '/park/index.html';
  const filePath = path.join(rootDir, reqPath);
  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    res.writeHead(404);
    res.end('Not found');
    return;
  }
  const ext = path.extname(filePath);
  const types = {
    '.html': 'text/html',
    '.js': 'application/javascript',
    '.mjs': 'application/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.glb': 'model/gltf-binary',
    '.css': 'text/css'
  };
  res.writeHead(200, { 'Content-Type': types[ext] || 'application/octet-stream' });
  fs.createReadStream(filePath).pipe(res);
});

await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const port = server.address().port;
const baseUrl = (process.argv[2] || `http://127.0.0.1:${port}/`).replace(/\/?$/, '/');

const chromePath = process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const userDataDir = fs.mkdtempSync('/tmp/chrome-sumie-');
const chrome = spawn(chromePath, [
  '--headless=new',
  '--remote-debugging-port=0',
  `--user-data-dir=${userDataDir}`,
  '--no-first-run',
  '--no-default-browser-check'
]);

let wsUrl = '';
chrome.stderr.on('data', d => {
  const m = d.toString().match(/ws:\/\/[^\s]+/);
  if (m && !wsUrl) wsUrl = m[0];
});
while (!wsUrl) await new Promise(r => setTimeout(r, 50));

const ws = new WebSocket(wsUrl);
await new Promise(r => ws.onopen = r);

let nextId = 1;
const callbacks = new Map();
ws.onmessage = e => {
  const msg = JSON.parse(e.data);
  if (msg.id && callbacks.has(msg.id)) {
    const cb = callbacks.get(msg.id);
    callbacks.delete(msg.id);
    cb(msg);
  }
};

function send(method, params = {}, sessionId = undefined) {
  const id = nextId++;
  return new Promise(resolve => {
    callbacks.set(id, resolve);
    ws.send(JSON.stringify(sessionId ? { id, sessionId, method, params } : { id, method, params }));
  });
}

const { result: { targetId } } = await send('Target.createTarget', { url: 'about:blank' });
const { result: { sessionId } } = await send('Target.attachToTarget', { targetId, flatten: true });

const consoleErrors = [];
ws.addEventListener('message', e => {
  const msg = JSON.parse(e.data);
  if (msg.method === 'Runtime.consoleAPICalled' && msg.params.type === 'error') {
    consoleErrors.push(msg.params.args.map(a => a.value || a.description).join(' '));
  } else if (msg.method === 'Runtime.exceptionThrown') {
    consoleErrors.push(msg.params.exceptionDetails.text);
  }
});

await send('Runtime.enable', {}, sessionId);
await send('Page.enable', {}, sessionId);

async function evalJs(expr) {
  const res = await send('Runtime.evaluate', {
    expression: `(async () => { ${expr} })()`,
    returnByValue: true,
    awaitPromise: true
  }, sessionId);
  return res.result?.result?.value;
}

async function setViewport(width, height, mobile = false) {
  await send('Emulation.setDeviceMetricsOverride', {
    width, height, deviceScaleFactor: 1, mobile
  }, sessionId);
}

async function saveScreenshot(outPath) {
  const { result } = await send('Page.captureScreenshot', { format: 'png' }, sessionId);
  fs.writeFileSync(outPath, Buffer.from(result.data, 'base64'));
}

// 1. Capture 6 side-by-side reference comparisons (reference left 320x320, live ink right 320x320)
await setViewport(1280, 800, false);
for (const aid of REF_ASSETS) {
  await send('Page.navigate', { url: `${baseUrl}?look=ink&still=1&asset=${aid}` }, sessionId);
  await new Promise(r => setTimeout(r, 1800));
  const dataUrl = await evalJs(`
    for (let i = 0; i < 40; i++) {
      const ldr = document.getElementById('viewer-loader');
      if (ldr && ldr.style.display === 'none') break;
      await new Promise(r => setTimeout(r, 100));
    }
    const refImg = new Image();
    refImg.crossOrigin = 'anonymous';
    await new Promise((res, rej) => { refImg.onload = res; refImg.onerror = rej; refImg.src = 'docs/sumi-e/${aid}__ink.png'; });
    if (window.__zooRender) window.__zooRender();
    const gl = document.getElementById('three-canvas');
    const c = document.createElement('canvas');
    c.width = 640; c.height = 320;
    const ctx = c.getContext('2d');
    ctx.drawImage(refImg, 0, 0, 320, 320);
    const side = Math.min(gl.width, gl.height);
    const sx = (gl.width - side) / 2, sy = (gl.height - side) / 2;
    ctx.drawImage(gl, sx, sy, side, side, 320, 0, 320, 320);
    return c.toDataURL('image/png');
  `);
  if (dataUrl && dataUrl.startsWith('data:image/png;base64,')) {
    const out = path.join(rootDir, 'docs', 'sumi-e', `compare_${aid}.png`);
    fs.writeFileSync(out, Buffer.from(dataUrl.split(',')[1], 'base64'));
    console.log(`saved ${out}`);
  }
}

// 2. Check 2D sprite sheet player & clip switching in modal
const spriteCheck = await evalJs(`
  const box = document.getElementById('sprite-box');
  const info0 = document.getElementById('sprite-info')?.textContent || '';
  const btns = [...document.querySelectorAll('#clip-btns button')];
  if (btns.length > 1) btns[1].click();
  await new Promise(r => setTimeout(r, 200));
  const info1 = document.getElementById('sprite-info')?.textContent || '';
  return { visible: box && !box.hidden, info0, info1, look: document.body.dataset.look };
`);
console.log('sprite player check:', JSON.stringify(spriteCheck));

// 3. Phone 390x844 screenshots: gallery and one asset view with switch on
await setViewport(390, 844, true);
await send('Page.navigate', { url: `${baseUrl}?look=ink` }, sessionId);
await new Promise(r => setTimeout(r, 1500));
await saveScreenshot(path.join(rootDir, 'docs', 'sumi-e', 'phone-gallery-ink-390.png'));
console.log('saved docs/sumi-e/phone-gallery-ink-390.png');

await send('Page.navigate', { url: `${baseUrl}?look=ink&asset=lion` }, sessionId);
await new Promise(r => setTimeout(r, 2000));
await saveScreenshot(path.join(rootDir, 'docs', 'sumi-e', 'phone-asset-ink-390.png'));
console.log('saved docs/sumi-e/phone-asset-ink-390.png');

// 4. Park speed check with ?look=ink at 1280x800 and 390x844
for (const [w, h, mob] of [[1280, 800, false], [390, 844, true]]) {
  await setViewport(w, h, mob);
  const t0 = Date.now();
  await send('Page.navigate', { url: `${baseUrl}park/?look=ink&size=600&density=1&pop=300` }, sessionId);
  const metrics = await evalJs(`
    const start = performance.now();
    while (!document.querySelector('canvas')) await new Promise(r => setTimeout(r, 50));
    const firstFrameMs = Math.round(performance.now());
    await new Promise(r => setTimeout(r, 2500));
    let frames = 0;
    const tStart = performance.now();
    await new Promise(resolve => {
      function tick() {
        frames++;
        if (performance.now() - tStart < 1000) requestAnimationFrame(tick);
        else resolve();
      }
      requestAnimationFrame(tick);
    });
    const fps = Math.round(frames * 1000 / (performance.now() - tStart));
    return { firstFrameMs, fps, url: location.search };
  `);
  console.log(`park ink ${w}x${h}: nav+firstFrame=${Date.now() - t0}ms (in-page ${metrics?.firstFrameMs}ms), fps=${metrics?.fps}`);
}

console.log(`console errors: ${consoleErrors.length}`, consoleErrors.slice(0, 5));
chrome.kill();
server.close();
process.exit(consoleErrors.length ? 1 : 0);
