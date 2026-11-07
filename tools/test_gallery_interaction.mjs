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
const url = `http://127.0.0.1:${port}/index.html`;

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

const headerText = await evalJs("return document.getElementById('header-asset-count').innerText");
const totalCards = await evalJs("return document.querySelectorAll('.card').length");
const allTabBadge = await evalJs("return document.querySelector('[data-cat=\"all\"] .cat-badge').innerText");
const variantsTabBadge = await evalJs("return document.querySelector('[data-cat=\"variants\"] .cat-badge').innerText");
const animalsTabBadge = await evalJs("return document.querySelector('[data-cat=\"animals\"] .cat-badge').innerText");

console.log(`Initial header: "${headerText}"`);
console.log(`Initial rendered cards: ${totalCards}`);
console.log(`Tab badges: All=${allTabBadge}, Variants=${variantsTabBadge}, Animals=${animalsTabBadge}`);

// Test search: 'baby'
await evalJs(`
  const input = document.getElementById('search-input');
  input.value = 'baby';
  input.dispatchEvent(new Event('input', { bubbles: true }));
`);
await new Promise(r => setTimeout(r, 200));
const babyCardCount = await evalJs("return document.querySelectorAll('.card').length");
console.log(`Search 'baby' card count: ${babyCardCount}`);

// Test search: 'elephant'
await evalJs(`
  const input = document.getElementById('search-input');
  input.value = 'elephant';
  input.dispatchEvent(new Event('input', { bubbles: true }));
`);
await new Promise(r => setTimeout(r, 200));
const elephantCardCount = await evalJs("return document.querySelectorAll('.card').length");
const elephantTitles = await evalJs("return Array.from(document.querySelectorAll('.card .card-title')).map(el => el.innerText)");
console.log(`Search 'elephant' card count: ${elephantCardCount} (${elephantTitles.join(', ')})`);

// Test click 'Animal Variants' tab
await evalJs(`
  const input = document.getElementById('search-input');
  input.value = '';
  input.dispatchEvent(new Event('input', { bubbles: true }));
  document.querySelector('[data-cat=\"variants\"]').click();
`);
await new Promise(r => setTimeout(r, 200));
const variantsCardCount = await evalJs("return document.querySelectorAll('.card').length");
console.log(`'Animal Variants' tab card count: ${variantsCardCount}`);

// Test open modal on first variant card
await evalJs(`
  document.querySelector('.card').click();
`);
await new Promise(r => setTimeout(r, 300));
const modalTitle = await evalJs("return document.getElementById('detail-title').innerText");
const modalVariant = await evalJs("return document.getElementById('detail-variant').innerText");
const modalDownload = await evalJs("return document.getElementById('detail-download').getAttribute('href')");
console.log(`Modal open: title="${modalTitle}", variant="${modalVariant}", glb="${modalDownload}"`);

// Test park link href
const parkLink = await evalJs("return document.querySelector('.park-btn').getAttribute('href')");
console.log(`Park link: "${parkLink}"`);

console.log(`Console errors count: ${consoleErrors.length}`);
if (consoleErrors.length > 0) {
  console.log(`Errors:`, consoleErrors);
}

// Cleanup
chrome.kill();
await new Promise(r => setTimeout(r, 200));
try {
  fs.rmSync(userDataDir, { recursive: true, force: true });
} catch (e) {}
server.close();
process.exit(0);
