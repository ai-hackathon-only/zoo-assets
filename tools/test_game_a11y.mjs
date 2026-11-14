// Keyboard-only & a11y verification on Night Shift. Usage: node tools/test_game_a11y.mjs [url] [width] [height]
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';

const url = process.argv[2] || 'https://ai-hackathon-only.github.io/zoo-assets/game/';
const W = +process.argv[3] || 390, H = +process.argv[4] || 844;
const shotDir = 'docs/game';
fs.mkdirSync(shotDir, { recursive: true });

const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
  '--headless=new', '--use-gl=angle', '--enable-webgl', '--remote-debugging-port=0',
  `--user-data-dir=${fs.mkdtempSync('/tmp/chrome-a11y-')}`, '--no-first-run', `--window-size=${W},${H}`,
]);
let wsUrl = '';
chrome.stderr.on('data', (d) => { const m = d.toString().match(/ws:\/\/[^\s]+/); if (m && !wsUrl) wsUrl = m[0]; });
while (!wsUrl) await new Promise((r) => setTimeout(r, 50));

const ws = new WebSocket(wsUrl);
await new Promise((r) => (ws.onopen = r));
let id = 1; const cbs = new Map(); const errors = []; let sid;
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && cbs.has(m.id)) { cbs.get(m.id)(m); cbs.delete(m.id); }
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errors.push(m.params.args.map((a) => a.value || a.description).join(' '));
  if (m.method === 'Runtime.exceptionThrown') errors.push(m.params.exceptionDetails?.exception?.description || m.params.exceptionDetails.text);
};
const send = (method, params = {}, s) => new Promise((res) => { const i = id++; cbs.set(i, res); ws.send(JSON.stringify({ id: i, sessionId: s, method, params })); });
const t = await send('Target.createTarget', { url: 'about:blank' });
sid = (await send('Target.attachToTarget', { targetId: t.result.targetId, flatten: true })).result.sessionId;
const ev = async (expr) => (await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true }, sid)).result?.result?.value;
const key = async (type, k, code, vk) => send('Input.dispatchKeyEvent', { type, key: k, code, windowsVirtualKeyCode: vk, ...(k === 'Enter' && type === 'keyDown' ? { text: '\r' } : {}) }, sid);
const tapKey = async (k, code, vk, holdMs = 40) => { await key('keyDown', k, code, vk); await sleep(holdMs); await key('keyUp', k, code, vk); };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const shot = async (name) => {
  const r = await send('Page.captureScreenshot', { format: 'png' }, sid);
  const out = path.join(shotDir, name);
  fs.writeFileSync(out, Buffer.from(r.result.data, 'base64'));
  console.log('shot:', out);
};

await send('Runtime.enable', {}, sid); await send('Page.enable', {}, sid);
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 600 }, sid);

await send('Page.navigate', { url }, sid);
for (let i = 0; i < 40 && !(await ev('!!window.game')); i++) await sleep(250);
await tapKey('Tab', 'Tab', 9);
await tapKey('Tab', 'Tab', 9);
// Focus back to #start-btn via Shift+Tab if needed, or verify activeElement
while ((await ev('document.activeElement?.id')) !== 'start-btn') await tapKey('Tab', 'Tab', 9);
console.log('start focus:', await ev('document.activeElement?.id'));
await shot(`a11y-${W}-start-focus.png`);

await tapKey('Enter', 'Enter', 13);
for (let i = 0; i < 120 && (await ev('window.game.debug.getState().screen')) !== 'playing'; i++) await sleep(250);
console.log('after Enter:', await ev('window.game.debug.getState().screen'));

await tapKey('l', 'KeyL', 76);
await sleep(100);
const look1 = await ev('document.getElementById("hud-look-btn").getAttribute("aria-pressed") + " | " + document.getElementById("sr-announcer").textContent');
await tapKey('l', 'KeyL', 76);
await sleep(100);
const look2 = await ev('document.getElementById("hud-look-btn").getAttribute("aria-pressed") + " | " + document.getElementById("sr-announcer").textContent');
console.log('L key toggle:', look1, '->', look2);

const p0 = await ev('JSON.stringify(window.game.debug.getState().playerPosition)');
await tapKey('d', 'KeyD', 68, 500);
const p1 = await ev('JSON.stringify(window.game.debug.getState().playerPosition)');
console.log('D key move:', p0, '->', p1);

// Move next to first non-carry task beacon and hold KeyE to complete it
const task = JSON.parse(await ev('JSON.stringify(window.game.debug.getState().tasks.find(t => !t.done && t.type !== "carry"))'));
await ev(`window.game.debug.moveTo(${task.position[0]}, ${task.position[2]})`);
await sleep(200);
await tapKey('e', 'KeyE', 69, 1600);
await sleep(200);
const afterHold = JSON.parse(await ev('JSON.stringify(window.game.debug.getState())'));
console.log('E hold task:', task.type, 'completedCount:', afterHold.completedCount, 'sr:', await ev('document.getElementById("sr-announcer").textContent'));

while ((await ev('JSON.stringify(window.game.debug.completeTask())')) !== 'false') await sleep(150);
for (let i = 0; i < 30 && (await ev('window.game.debug.getState().screen')) !== 'dawn'; i++) await sleep(250);
console.log('dawn focus:', await ev('document.activeElement?.id'));
await shot(`a11y-${W}-dawn-focus.png`);

await tapKey('Enter', 'Enter', 13);
for (let i = 0; i < 60 && (await ev('window.game.debug.getState().screen')) !== 'playing'; i++) await sleep(250);
const s2 = JSON.parse(await ev('JSON.stringify(window.game.debug.getState())'));
console.log('after Enter on dawn:', s2.screen, 'shift:', s2.shiftNumber);
console.log('console errors:', errors.length ? errors : 'none');

const fail = errors.length || afterHold.completedCount < 1 || s2.screen !== 'playing' || s2.shiftNumber !== 2 || p0 === p1;
chrome.kill();
process.exit(fail ? 1 : 0);
