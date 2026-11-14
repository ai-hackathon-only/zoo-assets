// Night Shift: game loop, controls, tasks, screens, test hooks. Design: game/DESIGN.md
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/GLTFLoader.js';
import { InkLook, lookFromUrl, setLookInUrl } from '../vendor/ink.js';
import { buildNightShiftWorld } from './world.js';

const $ = (id) => document.getElementById(id);
const SHIFT_SECONDS = 390;        // 6.5 minutes, dusk to dawn
const RANGE = 3.2;                // metres to a task marker
const HOLD = 1.5;                 // seconds to hold Action
const SPEED = 5.5;

const canvas = $('scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
const ink = new InkLook(THREE, renderer);
ink.lineScale = 0.3;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, 1, 0.3, 300);

function setLook(on) {
  ink.enabled = on; setLookInUrl(on);
  for (const id of ['look', 'look-start']) $(id).textContent = on ? 'Look: Sumi-e' : 'Look: Toy';
}
for (const id of ['look', 'look-start']) $(id).addEventListener('click', () => setLook(!ink.enabled));
setLook(lookFromUrl());

function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h; camera.updateProjectionMatrix();
  if (ink.resize) ink.resize(w, h);
}
addEventListener('resize', resize); resize();

const S = { screen: 'start', elapsed: 0, hold: 0, carrying: false, target: null, world: null, loading: false, doneAt: null };
const keys = new Set();
const show = (name) => {
  S.screen = name; document.body.dataset.screen = name;
  $('start').hidden = name !== 'start'; $('hud').hidden = name !== 'play'; $('end').hidden = name !== 'end';
};

// ---------- world ----------
async function ensureWorld() {
  if (S.world) return;
  S.world = await buildNightShiftWorld({ THREE, GLTFLoader, scene });
}
function resetShift() {
  const w = S.world;
  S.elapsed = 0; S.hold = 0; S.carrying = false; S.target = null; S.doneAt = null;
  const e = w.layout.entrance.position;
  w.player.obj.position.set(e[0], 0, e[1] + 3);
  w.player.playClip('idle');
  for (const t of w.tasks) {
    t.status = 'pending'; t.beacon.visible = true; t.walkTo = null;
    if (t.type === 'gate') t.rig.playClip('open', { loop: false, fade: 0, clampWhenFinished: true });
    if (t.type === 'feed') t.rig.playClip('idle');
    if (t.type === 'visitor') { t.rig.playClip('wave'); }
    if (t.type === 'lamp') t.light.intensity = 0;
    if (t.type === 'carry') { t.origin = t.origin || t.position; t.carried = false; w.detachProp(t.prop, t.origin); t.beacon.position.set(t.origin[0], 0, t.origin[2]); }
  }
}

// ---------- tasks ----------
const taskPos = (t) => (t.type === 'carry' && t.carried ? t.dropoff : t.position);
const dist = (p, q) => Math.hypot(p.x - q[0], p.z - q[2]);
function completeTask(t) {
  const w = S.world;
  if (t.type === 'feed') { t.rig.playClip('eat', { loop: false, fade: 0.2, clampWhenFinished: false }); }
  if (t.type === 'gate') t.rig.playClip('close', { loop: false, fade: 0, clampWhenFinished: true });
  if (t.type === 'visitor') { t.rig.playClip('wave', { loop: false, fade: 0.1 }); t.walkTo = t.exitPosition; t.waveLeft = 1.4; }
  if (t.type === 'lamp') t.light.intensity = 2.4;
  if (t.type === 'carry') {
    if (!t.carried) {   // stage 1: pick up
      t.carried = true; w.attachProp(t.prop);
      w.player.playClip('carry'); t.beacon.position.set(t.dropoff[0], 0, t.dropoff[2]);
      toast('Bucket picked up. Take it to the trough.'); return false;
    }
    w.detachProp(t.prop, t.dropoff); w.player.playClip('idle');
  }
  t.status = 'done'; t.beacon.visible = false;
  return true;
}
function nextPending(type) { return S.world.tasks.find((t) => t.status === 'pending' && (!type || t.type === type)); }
function nearestTask() {
  let best = null, bd = RANGE;
  const p = S.world.player.obj.position;
  for (const t of S.world.tasks) {
    if (t.status !== 'pending') continue;
    const d = dist(p, taskPos(t));
    if (d < bd) { bd = d; best = t; }
  }
  return best;
}
function toast(msg) { $('hint').textContent = msg; }

// ---------- input ----------
addEventListener('keydown', (e) => {
  if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(e.key)) e.preventDefault();
  keys.add(e.key.toLowerCase());
  if (e.key === 'Enter' && S.screen === 'start') startShift();
});
addEventListener('keyup', (e) => keys.delete(e.key.toLowerCase()));
const actHeld = () => keys.has('e') || keys.has(' ') || S.btnDown;
const act = $('action');
act.addEventListener('pointerdown', (e) => { e.preventDefault(); S.btnDown = true; });
for (const ev of ['pointerup', 'pointerleave', 'pointercancel']) act.addEventListener(ev, () => { S.btnDown = false; });

const ray = new THREE.Raycaster(), ndc = new THREE.Vector2(), plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
canvas.addEventListener('pointerdown', (e) => {
  if (S.screen !== 'play') return;
  ndc.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  ray.setFromCamera(ndc, camera);
  const hit = new THREE.Vector3();
  if (ray.ray.intersectPlane(plane, hit)) S.target = hit;
});

// ---------- flow ----------
async function startShift() {
  if (S.loading) return;
  S.loading = true; $('go').disabled = true; $('go').textContent = 'Loading…';
  try { await ensureWorld(); } catch (err) { console.error(err); $('go').textContent = 'Load failed'; S.loading = false; return; }
  resetShift(); show('play'); toast('Find a glowing marker and hold Act.');
  $('go').disabled = false; $('go').textContent = 'Start shift'; S.loading = false;
}
function endShift() {
  const tasks = S.world.tasks, done = tasks.filter((t) => t.status === 'done');
  const n = done.length, total = tasks.length;
  const stars = n >= total ? 3 : n >= 5 ? 2 : n >= 4 ? 1 : 0;
  $('stars').textContent = stars ? '★'.repeat(stars) + '☆'.repeat(3 - stars) : '☆☆☆';
  $('verdict').textContent = n >= 4 ? 'A good shift. The day team will find a calm zoo.' : 'A quiet night. The day team will pick up from here.';
  $('summary').innerHTML = tasks.map((t) => t.status === 'done'
    ? `<li>✓ ${t.label}</li>` : `<li class="left">· ${t.label} (left for the day team)</li>`).join('');
  S.world.lighting.setProgress(1);
  show('end');
}
$('go').addEventListener('click', startShift);
$('again').addEventListener('click', () => { resetShift(); show('play'); });

// ---------- loop ----------
const clock = new THREE.Clock();
const mm = $('minimap').getContext('2d');
let camPos = new THREE.Vector3(), heading = 0, moving = false;
function drawMap() {
  const w = S.world, b = w.bounds, W = 240;
  const half = b.width_m / 2 + 4, k = W / (half * 2);
  const X = (x) => (x + half) * k, Z = (z) => (z + half) * k;
  mm.clearRect(0, 0, W, W);
  mm.fillStyle = '#35435f';
  for (const p of w.layout.paths) mm.fillRect(X(p.position[0] - p.size[0] / 2), Z(p.position[1] - p.size[1] / 2), p.size[0] * k, p.size[1] * k);
  for (const t of w.tasks) if (t.status === 'pending') {
    const q = taskPos(t); mm.fillStyle = '#fbbf24'; mm.beginPath(); mm.arc(X(q[0]), Z(q[2]), 6, 0, 7); mm.fill();
  }
  const p = w.player.obj.position; mm.fillStyle = '#fff'; mm.beginPath(); mm.arc(X(p.x), Z(p.z), 5, 0, 7); mm.fill();
}
function frame() {
  requestAnimationFrame(frame);
  const dt = Math.min(clock.getDelta(), 0.1), w = S.world;
  if (w) {
    if (S.screen === 'play') {
      S.elapsed += dt;
      let dx = (keys.has('d') || keys.has('arrowright') ? 1 : 0) - (keys.has('a') || keys.has('arrowleft') ? 1 : 0);
      let dz = (keys.has('s') || keys.has('arrowdown') ? 1 : 0) - (keys.has('w') || keys.has('arrowup') ? 1 : 0);
      const p = w.player.obj.position;
      if (dx || dz) S.target = null;
      else if (S.target) {
        const ex = S.target.x - p.x, ez = S.target.z - p.z, d = Math.hypot(ex, ez);
        if (d < 0.4) S.target = null; else { dx = ex / d; dz = ez / d; }
      }
      const len = Math.hypot(dx, dz);
      const nowMoving = len > 0;
      if (nowMoving) {
        dx /= len; dz /= len;
        const hb = w.bounds.width_m / 2 + 6;
        p.x = Math.max(-hb, Math.min(hb, p.x + dx * SPEED * dt));
        p.z = Math.max(-hb, Math.min(hb, p.z + dz * SPEED * dt));
        heading = Math.atan2(dx, dz); w.player.obj.rotation.y = heading;
      }
      if (nowMoving !== moving) { moving = nowMoving; w.player.playClip(moving ? (S.carryingNow() ? 'carry' : 'walk') : (S.carryingNow() ? 'carry' : 'idle')); }
      // action
      const t = nearestTask();
      act.disabled = !t;
      if (t && actHeld()) {
        S.hold += dt;
        if (S.hold >= HOLD) { S.hold = 0; S.btnDown = false; keys.delete('e'); keys.delete(' '); if (completeTask(t)) toast(`Done: ${t.label}`); }
      } else S.hold = Math.max(0, S.hold - dt * 2);
      $('bar').firstElementChild.style.width = `${Math.min(100, (S.hold / HOLD) * 100)}%`;
      if (t && !S.hold) toast(`${t.label}: hold Act`);
      // visitor walks out
      for (const v of w.tasks) if (v.walkTo && v.status === 'done') {
        const o = v.rig.obj.position;
        if (v.waveLeft > 0) { v.waveLeft -= dt; if (v.waveLeft <= 0) v.rig.playClip('walk'); }
        else {
          const ex = v.walkTo[0] - o.x, ez = v.walkTo[2] - o.z, d = Math.hypot(ex, ez);
          if (d > 1) { o.x += (ex / d) * 2.2 * dt; o.z += (ez / d) * 2.2 * dt; v.rig.obj.rotation.y = Math.atan2(ex, ez); }
          else { v.walkTo = null; v.rig.obj.visible = false; }
        }
      }
      const prog = Math.min(1, S.elapsed / SHIFT_SECONDS);
      const left = w.tasks.filter((x) => x.status === 'pending').length;
      $('count').textContent = `${w.tasks.length - left} / ${w.tasks.length}`;
      const mins = Math.floor(prog * 6 * 60) , hh = (22 + Math.floor(mins / 60)) % 24, mi = mins % 60;
      $('clock').textContent = prog >= 1 ? 'Dawn' : `${String(hh).padStart(2, '0')}:${String(mi).padStart(2, '0')}`;
      if (!left && S.doneAt === null) S.doneAt = S.elapsed;
      w.update(dt, prog);
      if (prog >= 1 || (S.doneAt !== null && S.elapsed - S.doneAt > 3)) endShift();
      drawMap();
    } else w.update(dt, S.screen === 'end' ? 1 : 0);
    // chase camera ~50 deg
    const pp = w.player.obj.position, h = 13, back = 11;
    camPos.set(pp.x, h, pp.z + back);
    camera.position.lerp(camPos, 1 - Math.exp(-6 * dt));
    camera.lookAt(pp.x, 0.8, pp.z);
  } else { camera.position.set(0, 20, 30); camera.lookAt(0, 0, 0); }
  ink.render(scene, camera);
}
S.carryingNow = () => !!S.world?.tasks.find((t) => t.type === 'carry' && t.carried && t.status === 'pending');
frame();

// ---------- test hooks ----------
window.game = {
  debug: {
    ready: () => !!S.world,
    start: () => startShift(),
    completeTask(type) {
      const t = nextPending(type); if (!t) return null;
      const p = taskPos(t); S.world.player.obj.position.set(p[0], 0, p[2]);
      if (!completeTask(t)) completeTask(t);   // carry: pick up, then drop
      return { id: t.id, type: t.type, status: t.status };
    },
    skipTo(what) { if (what === 'dawn' && S.screen === 'play') { S.elapsed = SHIFT_SECONDS; } },
    getState() {
      const w = S.world;
      return { screen: S.screen, progress: Math.min(1, S.elapsed / SHIFT_SECONDS),
        player: w ? w.player.obj.position.toArray().map((v) => +v.toFixed(2)) : null,
        tasks: w ? w.tasks.map((t) => ({ id: t.id, type: t.type, status: t.status })) : [], look: ink.enabled ? 'ink' : 'toy' };
    },
  },
};
