import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';

const rootDir = path.resolve('.');

// Simple static server
const server = http.createServer((req, res) => {
  let reqPath = req.url.split('?')[0];
  if (reqPath === '/') reqPath = '/index.html';
  const filePath = path.join(rootDir, reqPath);
  if (!fs.existsSync(filePath)) {
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
    '.glb': 'model/gltf-binary',
    '.css': 'text/css'
  };
  res.writeHead(200, { 'Content-Type': types[ext] || 'application/octet-stream' });
  fs.createReadStream(filePath).pipe(res);
});

await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const port = server.address().port;
const url = process.argv[2] || 'https://ai-hackathon-only.github.io/zoo-assets/';

// Launch Chrome with remote debugging
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const userDataDir = fs.mkdtempSync('/tmp/chrome-test-');
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

// Wait for Chrome wsUrl
while (!wsUrl) {
  await new Promise(r => setTimeout(r, 50));
}

// Connect to browser ws
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

// Create new target
const targetRes = await send('Target.createTarget', { url });
const targetId = targetRes.result.targetId;

// Attach to target
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
// Listen for console events
ws.addEventListener('message', e => {
  const msg = JSON.parse(e.data);
  if (msg.method === 'Runtime.consoleAPICalled') {
    if (msg.params.type === 'error') {
      consoleErrors.push(msg.params.args.map(a => a.value || a.description).join(' '));
    }
  } else if (msg.method === 'Runtime.exceptionThrown') {
    consoleErrors.push(msg.params.exceptionDetails.text);
  }
});

await sendSession('Runtime.enable');
await sendSession('Page.enable');

// Wait for page load
await new Promise(r => setTimeout(r, 1000));

async function evalJs(expr) {
  const res = await sendSession('Runtime.evaluate', { expression: `(() => { ${expr} })()`, returnByValue: true, awaitPromise: true });
  return res.result?.result?.value;
}

// One asset per skeleton (id from assets.json rig field): open it, click every clip button, read the result.
const assetsJson = JSON.parse(fs.readFileSync('assets.json', 'utf8'));
const list = assetsJson.assets || assetsJson;
const firstByRig = new Map();
for (const a of list) if (!firstByRig.has(a.rig)) firstByRig.set(a.rig, a.id);
await new Promise(r => setTimeout(r, 2000));
let bad = 0;
for (const [rig, aid] of firstByRig) {
  await evalJs(`const c=document.querySelector('.card[data-id="${aid}"]'); if(c) c.click(); else { const i=document.getElementById('search-input'); i.value='${aid}'; i.dispatchEvent(new Event('input',{bubbles:true})); setTimeout(()=>document.querySelector('.card[data-id="${aid}"]')?.click(),300);}`);
  await new Promise(r => setTimeout(r, 2500));
  const names = await evalJs(`return [...document.querySelectorAll('#clip-btns button')].map(b=>b.textContent)`) || [];
  const played = [];
  for (let i = 0; i < names.length; i++) {
    await evalJs(`document.querySelectorAll('#clip-btns button')[${i}].click()`);
    await new Promise(r => setTimeout(r, 300));
    const act = await evalJs(`return document.querySelectorAll('#clip-btns button.active').length`);
    played.push(`${names[i]}:${act === 1 ? 'ok' : 'FAIL'}`);
    if (act !== 1) bad++;
  }
  if (!names.length) bad++;
  console.log(`${rig} (${aid}): ${played.join(' ') || 'NO CLIP BUTTONS'}`);
  await evalJs(`document.getElementById('modal-close')?.click(); document.querySelector('.modal-close')?.click()`);
  await new Promise(r => setTimeout(r, 300));
}
console.log(`animated tab: ` + await evalJs(`document.querySelector('[data-cat="animated"]').click(); return document.querySelectorAll('.card').length`) + ' cards');
console.log(`skeletons=${firstByRig.size} failures=${bad}`);
console.log(`console errors: ${consoleErrors.length}`, consoleErrors.slice(0, 5));
chrome.kill(); server.close(); process.exit(bad || consoleErrors.length ? 1 : 0);
