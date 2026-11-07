import fs from 'fs';
import { spawn, execSync } from 'child_process';

const args = process.argv.slice(2).filter(a => !a.startsWith('--'));
const targetUrl = args[0] || 'https://ai-hackathon-only.github.io/zoo-assets/park/?size=600&density=1&population=300&seed=42';

// 0. Machine info
let cpuInfo = 'Unknown CPU';
let gpuInfo = 'Unknown GPU';
try {
  cpuInfo = execSync('sysctl -n machdep.cpu.brand_string', { encoding: 'utf8' }).trim();
} catch (e) {}
try {
  const sp = execSync('system_profiler SPDisplaysDataType', { encoding: 'utf8' });
  const m = sp.match(/Chipset Model:\s*(.+)/);
  if (m) gpuInfo = m[1].trim();
} catch (e) {}

const isHeaded = process.argv.includes('--headed');

console.log(`=== Testbed Environment ===`);
console.log(`Machine: ${cpuInfo} · GPU: ${gpuInfo}`);
console.log(`Browser: Google Chrome ${isHeaded ? 'headed' : 'headless (angle / webgl)'}`);
console.log(`Target URL: ${targetUrl}\n`);

// Launch Chrome with remote debugging
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const userDataDir = fs.mkdtempSync('/tmp/chrome-park-');
const chromeArgs = [
  '--remote-debugging-port=0',
  `--user-data-dir=${userDataDir}`,
  '--no-first-run',
  '--no-default-browser-check',
  '--window-size=1280,800'
];
if (!isHeaded) {
  chromeArgs.unshift('--headless=new', '--use-gl=angle', '--enable-webgl');
}
const chrome = spawn(chromePath, chromeArgs);

let wsUrl = '';
chrome.stderr.on('data', d => {
  const m = d.toString().match(/ws:\/\/[^\s]+/);
  if (m && !wsUrl) wsUrl = m[0];
});

while (!wsUrl) {
  await new Promise(r => setTimeout(r, 50));
}

const ws = new WebSocket(wsUrl);
await new Promise(r => ws.onopen = r);

let id = 1;
const callbacks = new Map();
ws.onmessage = e => {
  const msg = JSON.parse(e.data);
  if (msg.id && callbacks.has(msg.id)) {
    const cb = callbacks.get(msg.id);
    callbacks.delete(msg.id);
    cb(msg);
  }
};

function send(method, params = {}) {
  const reqId = id++;
  return new Promise(resolve => {
    callbacks.set(reqId, resolve);
    ws.send(JSON.stringify({ id: reqId, method, params }));
  });
}

const targetRes = await send('Target.createTarget', { url: targetUrl });
const targetId = targetRes.result.targetId;
const attachRes = await send('Target.attachToTarget', { targetId, flatten: true });
const sessionId = attachRes.result.sessionId;

function sendSession(method, params = {}) {
  const reqId = id++;
  return new Promise(resolve => {
    callbacks.set(reqId, resolve);
    ws.send(JSON.stringify({ id: reqId, sessionId, method, params }));
  });
}

const consoleErrors = [];
ws.addEventListener('message', e => {
  const msg = JSON.parse(e.data);
  if (msg.method === 'Runtime.consoleAPICalled') {
    if (msg.params.type === 'error') {
      consoleErrors.push(msg.params.args.map(a => a.value || a.description || JSON.stringify(a)).join(' '));
    }
  } else if (msg.method === 'Runtime.exceptionThrown') {
    consoleErrors.push(msg.params.exceptionDetails?.exception?.description || msg.params.exceptionDetails.text);
  }
});

await sendSession('Runtime.enable');
await sendSession('Page.enable');

async function evalJs(expr) {
  const res = await sendSession('Runtime.evaluate', {
    expression: `(() => { ${expr} })()`,
    returnByValue: true,
    awaitPromise: true
  });
  return res.result?.result?.value;
}

// 1. Wait for load and first frame
console.log('--- 1. Speed & Batch Loading (600m safari, 300 pop) ---');
const startTime = Date.now();
let firstFrameText = '';
let fpsText = '';
let statsText = '';

for (let i = 0; i < 40; i++) {
  await new Promise(r => setTimeout(r, 250));
  firstFrameText = await evalJs("return document.getElementById('first')?.innerText || ''");
  if (firstFrameText && !firstFrameText.includes('loading') && !firstFrameText.includes('generating')) {
    break;
  }
}
const elapsedSec = ((Date.now() - startTime) / 1000).toFixed(2);
statsText = await evalJs("return document.getElementById('stats')?.innerText || ''");
fpsText = await evalJs("return document.getElementById('fps')?.innerText || ''");

console.log(`Elapsed to ready: ${elapsedSec}s`);
console.log(`First frame hud: "${firstFrameText}"`);
console.log(`Initial stats: "${statsText}"`);

// Measure FPS while actively orbiting
console.log('Sampling active rendering FPS while orbiting camera over 3 seconds...');
await evalJs(`
  let angle = 0;
  window.__orbitInterval = setInterval(() => {
    angle += 0.03;
    if (window.__park?.camera) {
      window.__park.camera.position.x = Math.sin(angle) * 300;
      window.__park.camera.position.z = Math.cos(angle) * 300;
      window.__park.camera.position.y = 120;
      if (window.__park?.controls) {
        window.__park.controls.target.set(0, 0, 0);
      } else {
        window.__park.camera.lookAt(0, 0, 0);
      }
    }
  }, 16);
`);
await new Promise(r => setTimeout(r, 3000));
fpsText = await evalJs("return document.getElementById('fps')?.innerText || ''");
await evalJs("clearInterval(window.__orbitInterval)");
console.log(`Orbiting FPS: "${fpsText}"`);

// 2. Interactive Controls Check
console.log('\n--- 2. Interactive Controls Check ---');
// Seed & Shuffle
const seedBefore = await evalJs("return document.getElementById('seed')?.value");
console.log(`Seed before shuffle: "${seedBefore}"`);
await evalJs("document.getElementById('shuffle')?.click()");
await new Promise(r => setTimeout(r, 500));
const seedAfter = await evalJs("return document.getElementById('seed')?.value");
console.log(`Seed after shuffle: "${seedAfter}" (changed: ${seedBefore !== seedAfter})`);

// Sliders
await evalJs(`
  const s = document.getElementById('size');
  s.value = '300';
  s.dispatchEvent(new Event('input', { bubbles: true }));
`);
await new Promise(r => setTimeout(r, 300));
const sizeOut = await evalJs("return document.getElementById('size-out')?.innerText");
console.log(`Size slider set to 300m -> output: "${sizeOut}"`);

await evalJs(`
  const d = document.getElementById('density');
  d.value = '0.5';
  d.dispatchEvent(new Event('input', { bubbles: true }));
`);
await new Promise(r => setTimeout(r, 300));
const densityOut = await evalJs("return document.getElementById('density-out')?.innerText");
console.log(`Density slider set to 0.50 -> output: "${densityOut}"`);

await evalJs(`
  const p = document.getElementById('population');
  p.value = '150';
  p.dispatchEvent(new Event('input', { bubbles: true }));
`);
await new Promise(r => setTimeout(r, 300));
const popOut = await evalJs("return document.getElementById('population-out')?.innerText");
console.log(`Population slider set to 150 -> output: "${popOut}"`);

// 3. Minimap & Camera Move Check
console.log('\n--- 3. Minimap Camera Flight Check ---');
const camBefore = await evalJs(`
  const c = window.__park?.camera?.position;
  return c ? { x: Math.round(c.x), y: Math.round(c.y), z: Math.round(c.z) } : null;
`);
const focusBefore = await evalJs("return document.getElementById('focus-name')?.innerText");

const enclosureName = await evalJs(`
  const L = window.__park?.layout;
  const enc = L?.enclosures?.[0];
  const canvas = document.getElementById('minimap');
  const rect = canvas.getBoundingClientRect();
  const widthM = L?.boundary?.width_m || 300;
  const targetX = rect.left + (enc.center[0] / widthM) * rect.width;
  const targetY = rect.top + (enc.center[1] / widthM) * rect.height;
  const evt = new MouseEvent('click', {
    clientX: targetX,
    clientY: targetY,
    bubbles: true
  });
  canvas.dispatchEvent(evt);
  return enc?.name;
`);
await new Promise(r => setTimeout(r, 800));

const camAfter = await evalJs(`
  const c = window.__park?.camera?.position;
  return c ? { x: Math.round(c.x), y: Math.round(c.y), z: Math.round(c.z) } : null;
`);
const focusAfterClick = await evalJs("return document.getElementById('focus-name')?.innerText");

if (camBefore && camAfter) {
  console.log(`Camera before minimap click: [${camBefore.x}, ${camBefore.y}, ${camBefore.z}]`);
  console.log(`Clicked minimap enclosure: "${enclosureName}"`);
  console.log(`Camera after minimap click: [${camAfter.x}, ${camAfter.y}, ${camAfter.z}]`);
} else {
  console.log(`Clicked minimap enclosure: "${enclosureName}"`);
}
console.log(`Focus name changed from "${focusBefore}" to: "${focusAfterClick}"`);

await evalJs("document.getElementById('overview')?.click()");
await new Promise(r => setTimeout(r, 400));
const focusAfterOverview = await evalJs("return document.getElementById('focus-name')?.innerText");
console.log(`Overview button click restored focus to: "${focusAfterOverview}"`);

// 4. URL State Preservation & Day/Night Toggle Check
console.log('\n--- 4. Day/Night Toggle & URL State Check ---');
const themeBefore = await evalJs("return window.__park?.theme || 'day'");
const btnTextBefore = await evalJs("return document.getElementById('theme')?.innerText || ''");
await evalJs("document.getElementById('theme')?.click()");
await new Promise(r => setTimeout(r, 400));
const themeAfter = await evalJs("return window.__park?.theme || ''");
const btnTextAfter = await evalJs("return document.getElementById('theme')?.innerText || ''");
console.log(`Day/Night toggle clicked: ${themeBefore} ("${btnTextBefore}") -> ${themeAfter} ("${btnTextAfter}")`);
const urlState = await evalJs("return window.location.search");
console.log(`URL search params preserved: "${urlState}"`);

// 4b. Living Scene NPC Simulation Check (if button exists)
const simToggleCheck = await evalJs(`
  const btn = document.getElementById('sim-toggle');
  if (!btn) return { hasBtn: false };
  const initialSim = document.body.dataset.simulating;
  btn.click();
  const pausedSim = document.body.dataset.simulating;
  btn.click();
  const resumedSim = document.body.dataset.simulating;
  return { hasBtn: true, initialSim, pausedSim, resumedSim };
`);
if (simToggleCheck && simToggleCheck.hasBtn) {
  console.log(`\n--- 3b. Living Scene Simulation Toggle Check ---`);
  console.log(`Simulation toggle: initial=${simToggleCheck.initialSim} -> paused=${simToggleCheck.pausedSim} -> resumed=${simToggleCheck.resumedSim}`);
}

// 4c. Layout Style Setting Check
const styleCheck = await evalJs(`
  const sel = document.getElementById('style');
  if (!sel) return { hasSel: false };
  const initialStyle = sel.value;
  sel.value = 'loop';
  sel.dispatchEvent(new Event('change', { bubbles: true }));
  return { hasSel: true, initialStyle, newStyle: sel.value };
`);
if (styleCheck && styleCheck.hasSel) {
  await new Promise(r => setTimeout(r, 600));
  const urlWithStyle = await evalJs("return window.location.search");
  console.log(`\n--- 3c. Layout Style Setting Check ---`);
  console.log(`Layout style selector switched: ${styleCheck.initialStyle} -> ${styleCheck.newStyle} (URL: "${urlWithStyle}")`);
}

// 5. Gallery Search Interaction Check
console.log('\n--- 4. Gallery Search Interaction Check ---');
const galleryUrl = 'https://ai-hackathon-only.github.io/zoo-assets/';
const galleryRes = await send('Target.createTarget', { url: galleryUrl });
const gTargetId = galleryRes.result.targetId;
const gAttach = await send('Target.attachToTarget', { targetId: gTargetId, flatten: true });
const gSessionId = gAttach.result.sessionId;

function sendGallery(method, params = {}) {
  const reqId = id++;
  return new Promise(resolve => {
    callbacks.set(reqId, resolve);
    ws.send(JSON.stringify({ id: reqId, sessionId: gSessionId, method, params }));
  });
}

await sendGallery('Runtime.enable');
await sendGallery('Page.enable');

// Wait for gallery assets to render
await new Promise(r => setTimeout(r, 1500));

async function evalGallery(expr) {
  const res = await sendGallery('Runtime.evaluate', {
    expression: `(() => { ${expr} })()`,
    returnByValue: true,
    awaitPromise: true
  });
  return res.result?.result?.value;
}

const initialCards = await evalGallery("return document.querySelectorAll('.card').length");
// Type "lion" into search input
await evalGallery(`
  const input = document.querySelector('input[type="search"]') || document.querySelector('#search') || document.querySelector('input');
  if (input) {
    input.value = 'lion';
    input.dispatchEvent(new Event('input', { bubbles: true }));
  }
`);
await new Promise(r => setTimeout(r, 400));
const lionCards = await evalGallery("return document.querySelectorAll('.card:not([hidden]):not([style*=\"display: none\"])').length");
console.log(`Gallery search: initial total cards = ${initialCards}, typed "lion" → visible cards = ${lionCards}`);

// 6. Console Errors Summary
console.log(`\n--- 5. Console Diagnostics ---`);
console.log(`Total console errors: ${consoleErrors.length}`);
if (consoleErrors.length > 0) {
  console.log('Errors:', consoleErrors);
}

// 7. Screenshots of 3 different seeds at 1280px and 390px if requested
if (process.argv.includes('--screenshots')) {
  console.log('\n--- 6. Screenshots (1280px & 390px) ---');
  const shotsDir = '/tmp/park-shots';
  if (!fs.existsSync(shotsDir)) fs.mkdirSync(shotsDir, { recursive: true });

  const seeds = ['42', '101', '777'];
  for (const s of seeds) {
    await evalJs(`
      const input = document.getElementById('seed');
      input.value = '${s}';
      input.dispatchEvent(new Event('change', { bubbles: true }));
    `);
    await new Promise(r => setTimeout(r, 1500));

    // 1280px desktop
    await sendSession('Emulation.setDeviceMetricsOverride', {
      width: 1280, height: 800, deviceScaleFactor: 1, mobile: false
    });
    await new Promise(r => setTimeout(r, 400));
    const shotDesktop = await sendSession('Page.captureScreenshot', { format: 'png' });
    const pDesktop = `${shotsDir}/park-seed-${s}-1280px.png`;
    fs.writeFileSync(pDesktop, Buffer.from(shotDesktop.result.data, 'base64'));
    console.log(`Saved 1280px screenshot for seed ${s}: ${pDesktop}`);

    // 390px mobile
    await sendSession('Emulation.setDeviceMetricsOverride', {
      width: 390, height: 844, deviceScaleFactor: 2, mobile: true
    });
    await new Promise(r => setTimeout(r, 400));
    const shotMobile = await sendSession('Page.captureScreenshot', { format: 'png' });
    const pMobile = `${shotsDir}/park-seed-${s}-390px.png`;
    fs.writeFileSync(pMobile, Buffer.from(shotMobile.result.data, 'base64'));
    console.log(`Saved 390px screenshot for seed ${s}: ${pMobile}`);
  }
}

// Cleanup
chrome.kill();
await new Promise(r => setTimeout(r, 200));
try {
  fs.rmSync(userDataDir, { recursive: true, force: true });
} catch (e) {}

console.log('\nTest completed successfully.');
