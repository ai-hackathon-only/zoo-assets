import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/GLTFLoader.js';
import { InkLook, lookFromUrl, setLookInUrl } from '../vendor/ink.js';
import { buildNightShiftWorld } from './world.js';
import { NightAudio } from './audio.js';

const SHIFT_DURATION_S = 360; // 6-minute night shift
const PLAYER_SPEED = 8.5;
const INTERACT_RANGE = 3.2;
const HOLD_DURATION_S = 1.5;

const canvas = document.getElementById('scene');
const startScreen = document.getElementById('start-screen');
const dawnScreen = document.getElementById('dawn-screen');
const hud = document.getElementById('hud');
const startBtn = document.getElementById('start-btn');
const nextShiftBtn = document.getElementById('next-shift-btn');
const replayBtn = document.getElementById('replay-btn');
const startLookBtn = document.getElementById('start-look-btn');
const hudLookBtn = document.getElementById('hud-look-btn');
const startSoundBtn = document.getElementById('start-sound-btn');
const hudSoundBtn = document.getElementById('hud-sound-btn');
const clockPill = document.getElementById('clock-pill');
const tasksPill = document.getElementById('tasks-pill');
const promptText = document.getElementById('prompt-text');
const promptSub = document.getElementById('prompt-sub');
const actionBtn = document.getElementById('action-btn');
const actionProgress = document.getElementById('action-progress');
const minimap = document.getElementById('minimap');
const minimapCtx = minimap.getContext('2d');
const dawnStars = document.getElementById('dawn-stars');
const dawnSubtitle = document.getElementById('dawn-subtitle');
const dawnList = document.getElementById('dawn-list');
const srAnnouncer = document.getElementById('sr-announcer');

function announce(text) {
  if (!srAnnouncer) return;
  srAnnouncer.textContent = '';
  requestAnimationFrame(() => {
    srAnnouncer.textContent = text;
  });
}

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.2, 260);
const ink = new InkLook(THREE, renderer);
ink.lineScale = 0.3;

function setLook(on) {
  ink.enabled = on;
  setLookInUrl(on);
  document.body.dataset.look = on ? 'ink' : 'toy';
  startLookBtn.textContent = on ? 'Look: Sumi-e' : 'Look: Toy';
  hudLookBtn.textContent = on ? 'Sumi-e' : 'Toy';
  const nextMode = on ? 'Toy' : 'Sumi-e';
  const curMode = on ? 'Sumi-e' : 'Toy';
  startLookBtn.setAttribute('aria-pressed', String(on));
  hudLookBtn.setAttribute('aria-pressed', String(on));
  startLookBtn.setAttribute('aria-label', `Look mode: ${curMode}. Press to switch to ${nextMode}.`);
  hudLookBtn.setAttribute('aria-label', `Look mode: ${curMode}. Press L or click to switch to ${nextMode}.`);
}
setLook(lookFromUrl());

startLookBtn.addEventListener('click', () => setLook(!ink.enabled));
hudLookBtn.addEventListener('click', () => setLook(!ink.enabled));

const audio = new NightAudio();
function setSoundMuted(muted) {
  audio.setMuted(muted);
  startSoundBtn.textContent = audio.muted ? 'Sound: Off' : 'Sound: On';
  hudSoundBtn.textContent = audio.muted ? 'Muted' : 'Sound';
  const pressed = audio.muted ? 'false' : 'true';
  const label = audio.muted ? 'Sound: Off. Press to unmute.' : 'Sound: On. Press to mute.';
  startSoundBtn.setAttribute('aria-pressed', pressed);
  hudSoundBtn.setAttribute('aria-pressed', pressed);
  startSoundBtn.setAttribute('aria-label', label);
  hudSoundBtn.setAttribute('aria-label', label);
}
startSoundBtn.addEventListener('click', () => setSoundMuted(!audio.muted));
hudSoundBtn.addEventListener('click', () => setSoundMuted(!audio.muted));

let world = null;
let worldGroup = null;
let screen = 'start'; // 'start' | 'playing' | 'dawn'
let pendingStart = false;
let loadingWorld = false;
let loadFailed = false;
let shiftNumber = 1;
let currentSeed = 'night-shift-1';
let shiftElapsed = 0;
let currentClip = 'idle';
let stepTimer = 0;
let moveTarget = null;
let holdingAction = false;
let holdProgress = 0;
let activeVisitorWalks = [];
let fpsEstimate = 60;
let fpsFrames = 0;
let fpsTimer = 0;

const keys = new Set();
const raycaster = new THREE.Raycaster();
const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);

function getTaskTargetPos(task) {
  return task.type === 'carry' && task.carried ? task.dropoff : task.position;
}

function getNearbyTask() {
  if (!world) return null;
  const p = world.player.obj.position;
  let best = null;
  let bestDist = INTERACT_RANGE;
  for (const t of world.tasks) {
    if (t.done) continue;
    const pos = getTaskTargetPos(t);
    const d = Math.hypot(pos[0] - p.x, pos[2] - p.z);
    if (d <= bestDist) {
      bestDist = d;
      best = t;
    }
  }
  return best;
}

function resolveTask(task) {
  if (!task || task.done) return;
  if (task.type === 'carry' && !task.carried) {
    world.attachProp(task.prop);
    task.carried = true;
    task.beacon.position.set(task.dropoff[0], 0.06, task.dropoff[2]);
    audio.playTaskCue('carry', task.label);
    announce('Picked up fish bucket. Carry it to the trough.');
    return;
  }
  if (task.type === 'carry' && task.carried) {
    world.detachProp(task.prop, task.dropoff);
    task.carried = false;
  } else if (task.type === 'feed') {
    task.rig?.playClip('eat', { loop: true });
  } else if (task.type === 'gate') {
    task.rig?.playClip('close', { loop: false, clampWhenFinished: true });
  } else if (task.type === 'visitor') {
    task.rig?.playClip('walk', { loop: true });
    const exitPos = task.exitPosition || [world.layout.entrance.position[0], 0, world.layout.entrance.position[1]];
    if (task.rig?.obj) {
      activeVisitorWalks.push({
        obj: task.rig.obj,
        dest: new THREE.Vector3(exitPos[0], 0, exitPos[2]),
      });
    }
  } else if (task.type === 'lamp' && task.light) {
    task.light.intensity = 2.6;
  }
  audio.playTaskCue(task.type, task.label);
  task.done = true;
  if (task.beacon) task.beacon.visible = false;
  updateTaskCounter();
  announce(`Completed: ${task.label}`);
  if (world.tasks.every((t) => t.done)) {
    setTimeout(() => {
      if (screen === 'playing') showDawnSummary();
    }, 1200);
  }
}

function updateTaskCounter() {
  if (!world) return;
  const doneCount = world.tasks.filter((t) => t.done).length;
  tasksPill.textContent = `${doneCount} / ${world.tasks.length} tasks`;
}

function formatClock(progress) {
  const totalMinutes = Math.round(progress * 450); // 22:00 to 05:30 (7.5h)
  const hour = (22 + Math.floor(totalMinutes / 60)) % 24;
  const min = totalMinutes % 60;
  const hh = String(hour).padStart(2, '0');
  const mm = String(min).padStart(2, '0');
  const phase = progress < 0.35 ? 'Night' : progress < 0.75 ? 'Late Night' : 'Pre-Dawn';
  return `${hh}:${mm} · ${phase}`;
}

function showDawnSummary() {
  screen = 'dawn';
  holdingAction = false;
  holdProgress = 0;
  hud.classList.add('hidden');
  dawnScreen.classList.remove('hidden');
  audio.playDawnChime();

  const tasks = world ? world.tasks : [];
  const doneCount = tasks.filter((t) => t.done).length;
  const stars = doneCount >= tasks.length ? 3 : doneCount >= 4 ? 2 : 1;
  dawnStars.textContent = '★'.repeat(stars) + '☆'.repeat(3 - stars);
  dawnStars.setAttribute('aria-label', `${stars} of 3 stars`);
  dawnSubtitle.textContent = `Shift ${shiftNumber} (${currentSeed}): you handled ${doneCount} of ${tasks.length} night-shift tasks before sunrise.`;

  dawnList.innerHTML = '';
  for (const t of tasks) {
    const li = document.createElement('li');
    const name = document.createElement('span');
    name.textContent = t.label;
    const status = document.createElement('span');
    status.className = t.done ? 'tag-done' : 'tag-left';
    status.textContent = t.done ? 'Handled' : 'Left for day team';
    li.append(name, status);
    dawnList.appendChild(li);
  }
  announce(`Dawn reached. Shift ${shiftNumber} complete: ${doneCount} of ${tasks.length} tasks handled.`);
  nextShiftBtn.focus();
}

async function initWorld() {
  loadingWorld = true;
  loadFailed = false;
  startBtn.textContent = 'Loading zoo…';
  if (worldGroup) scene.remove(worldGroup);
  worldGroup = new THREE.Group();
  scene.add(worldGroup);
  activeVisitorWalks = [];
  shiftElapsed = 0;
  moveTarget = null;
  holdProgress = 0;
  holdingAction = false;
  currentClip = 'idle';

  try {
    world = await buildNightShiftWorld({
      THREE,
      GLTFLoader,
      scene: worldGroup,
      settings: { seed: currentSeed, shiftNumber },
      basePath: '..',
    });
    updateTaskCounter();
    updateCameraAndFlashlight();
    startBtn.textContent = 'Start Shift';
    if (pendingStart) {
      pendingStart = false;
      startShift();
    }
  } catch (err) {
    loadFailed = true;
    pendingStart = false;
    startBtn.textContent = 'Load failed — Retry';
    throw err;
  } finally {
    loadingWorld = false;
  }
}

function startShift() {
  audio.unlock();
  if (!world) {
    if (loadFailed && !loadingWorld) {
      pendingStart = true;
      initWorld().catch((err) => console.error('[game] initWorld failed:', err));
      return;
    }
    pendingStart = true;
    startBtn.textContent = 'Starting…';
    return;
  }
  screen = 'playing';
  shiftElapsed = 0;
  moveTarget = null;
  holdProgress = 0;
  holdingAction = false;
  startScreen.classList.add('hidden');
  dawnScreen.classList.add('hidden');
  hud.classList.remove('hidden');
  if (document.activeElement && typeof document.activeElement.blur === 'function') {
    document.activeElement.blur();
  }
  announce(`Shift ${shiftNumber} started. Use WASD or Arrow keys to walk toward a glowing beacon.`);
}

startBtn.addEventListener('click', startShift);
nextShiftBtn.addEventListener('click', async () => {
  nextShiftBtn.disabled = true;
  replayBtn.disabled = true;
  shiftNumber += 1;
  currentSeed = `night-shift-${shiftNumber}`;
  await initWorld();
  nextShiftBtn.disabled = false;
  replayBtn.disabled = false;
  startShift();
});
replayBtn.addEventListener('click', async () => {
  nextShiftBtn.disabled = true;
  replayBtn.disabled = true;
  await initWorld();
  nextShiftBtn.disabled = false;
  replayBtn.disabled = false;
  startShift();
});

// Keyboard controls
window.addEventListener('keydown', (e) => {
  audio.unlock();
  keys.add(e.code);
  if (e.code === 'KeyL' && !e.repeat && !e.ctrlKey && !e.metaKey && !e.altKey) {
    setLook(!ink.enabled);
    announce(`Look mode: ${ink.enabled ? 'Sumi-e' : 'Toy'}`);
  }
  if ((e.code === 'KeyE' || e.code === 'Space') && screen === 'playing') {
    if (e.code === 'Space' && (!document.activeElement || !document.activeElement.closest('button, a'))) {
      e.preventDefault();
    }
    holdingAction = true;
  }
});
window.addEventListener('keyup', (e) => {
  keys.delete(e.code);
  if (e.code === 'KeyE' || e.code === 'Space') {
    holdingAction = false;
  }
});
window.addEventListener('blur', () => {
  keys.clear();
  holdingAction = false;
});

// Pointer tap/click-to-move on ground
canvas.addEventListener('pointerdown', (e) => {
  audio.unlock();
  if (screen !== 'playing' || !world) return;
  const ndc = new THREE.Vector2(
    (e.clientX / window.innerWidth) * 2 - 1,
    -(e.clientY / window.innerHeight) * 2 + 1
  );
  raycaster.setFromCamera(ndc, camera);
  const hit = new THREE.Vector3();
  if (raycaster.ray.intersectPlane(groundPlane, hit)) {
    const b = world.bounds;
    hit.x = Math.max(b.min_x + 2, Math.min(b.max_x - 2, hit.x));
    hit.z = Math.max(b.min_y + 2, Math.min(b.max_y - 2, hit.z));
    moveTarget = hit;
  }
});

// Action button (hold or tap)
actionBtn.addEventListener('pointerdown', (e) => {
  e.preventDefault();
  if (screen === 'playing' && !actionBtn.disabled) holdingAction = true;
});
window.addEventListener('pointerup', () => { holdingAction = false; });
window.addEventListener('pointercancel', () => { holdingAction = false; });

function updatePlayer(dt) {
  if (!world || screen !== 'playing') return;
  const p = world.player.obj;
  let vx = 0;
  let vz = 0;
  if (keys.has('KeyW') || keys.has('ArrowUp')) vz -= 1;
  if (keys.has('KeyS') || keys.has('ArrowDown')) vz += 1;
  if (keys.has('KeyA') || keys.has('ArrowLeft')) vx -= 1;
  if (keys.has('KeyD') || keys.has('ArrowRight')) vx += 1;

  if (vx !== 0 || vz !== 0) {
    moveTarget = null;
    const len = Math.hypot(vx, vz);
    vx /= len;
    vz /= len;
  } else if (moveTarget) {
    const dx = moveTarget.x - p.position.x;
    const dz = moveTarget.z - p.position.z;
    const dist = Math.hypot(dx, dz);
    if (dist < 0.35) {
      moveTarget = null;
    } else {
      vx = dx / dist;
      vz = dz / dist;
    }
  }

  const moving = vx !== 0 || vz !== 0;
  if (moving) {
    const b = world.bounds;
    p.position.x = Math.max(b.min_x + 2, Math.min(b.max_x - 2, p.position.x + vx * PLAYER_SPEED * dt));
    p.position.z = Math.max(b.min_y + 2, Math.min(b.max_y - 2, p.position.z + vz * PLAYER_SPEED * dt));
    p.rotation.y = Math.atan2(vx, vz);
  }

  const carrying = world.tasks.some((t) => t.type === 'carry' && t.carried && !t.done);
  if (moving) {
    stepTimer += dt;
    if (stepTimer >= 0.36) {
      stepTimer = 0;
      audio.playFootstep(carrying);
    }
  } else {
    stepTimer = 0.25;
  }

  const desiredClip = carrying ? 'carry' : moving ? 'walk' : 'idle';
  if (desiredClip !== currentClip) {
    currentClip = desiredClip;
    world.player.playClip(desiredClip, { loop: true });
  }
}

function updateCameraAndFlashlight() {
  if (!world) return;
  const p = world.player.obj;
  camera.position.set(p.position.x, 14.5, p.position.z + 12.2);
  camera.lookAt(p.position.x, 0.8, p.position.z);

  const dirX = Math.sin(p.rotation.y);
  const dirZ = Math.cos(p.rotation.y);
  world.lighting.flashlight.position.set(p.position.x, 1.5, p.position.z);
  world.lighting.flashlightTarget.position.set(p.position.x + dirX * 8, 0.2, p.position.z + dirZ * 8);
}

function drawMinimap() {
  if (!world) return;
  const w = minimap.width;
  const h = minimap.height;
  minimapCtx.clearRect(0, 0, w, h);

  const b = world.bounds;
  const spanX = Math.max(1, b.max_x - b.min_x);
  const spanZ = Math.max(1, b.max_y - b.min_y);
  const toMapX = (x) => ((x - b.min_x) / spanX) * (w - 12) + 6;
  const toMapY = (z) => ((z - b.min_y) / spanZ) * (h - 12) + 6;

  // Enclosures
  minimapCtx.fillStyle = 'rgba(51, 65, 85, 0.75)';
  for (const enc of world.layout.enclosures) {
    const eb = enc.bounds;
    const x0 = toMapX(eb.min_x);
    const y0 = toMapY(eb.min_y);
    const ew = toMapX(eb.max_x) - x0;
    const eh = toMapY(eb.max_y) - y0;
    minimapCtx.fillRect(x0, y0, ew, eh);
  }

  // Task markers
  for (const t of world.tasks) {
    if (t.done) continue;
    const pos = getTaskTargetPos(t);
    minimapCtx.fillStyle = '#' + t.color.toString(16).padStart(6, '0');
    minimapCtx.beginPath();
    minimapCtx.arc(toMapX(pos[0]), toMapY(pos[2]), 3.5, 0, Math.PI * 2);
    minimapCtx.fill();
  }

  // Player dot
  const p = world.player.obj.position;
  minimapCtx.fillStyle = '#ffffff';
  minimapCtx.beginPath();
  minimapCtx.arc(toMapX(p.x), toMapY(p.z), 4, 0, Math.PI * 2);
  minimapCtx.fill();
}

function updateInteraction(dt) {
  if (!world || screen !== 'playing') return;
  const nearby = getNearbyTask();
  if (!nearby) {
    actionBtn.disabled = true;
    actionBtn.setAttribute('aria-label', 'Action: walk near a task beacon first');
    holdProgress = 0;
    actionProgress.style.width = '0%';
    promptText.textContent = 'Walk toward a glowing beacon';
    promptSub.textContent = 'WASD / Tap ground to move';
    return;
  }

  actionBtn.disabled = false;
  const verb = nearby.type === 'carry'
    ? (nearby.carried ? 'Drop bucket at trough' : 'Pick up fish bucket')
    : nearby.label;
  actionBtn.setAttribute('aria-label', `Action: ${verb}. Hold E, Space, or this button.`);
  promptText.textContent = verb;
  promptSub.textContent = 'Hold Action (E / Space)';

  if (holdingAction) {
    holdProgress += dt / HOLD_DURATION_S;
    actionProgress.style.width = `${Math.min(100, holdProgress * 100)}%`;
    if (holdProgress >= 1) {
      holdProgress = 0;
      holdingAction = false;
      actionProgress.style.width = '0%';
      resolveTask(nearby);
    }
  } else {
    holdProgress = Math.max(0, holdProgress - dt * 2);
    actionProgress.style.width = `${Math.min(100, holdProgress * 100)}%`;
  }
}

let lastTime = performance.now();
function animate(now) {
  requestAnimationFrame(animate);
  const dt = Math.min(0.05, (now - lastTime) / 1000);
  lastTime = now;

  fpsFrames++;
  fpsTimer += dt;
  if (fpsTimer >= 0.5) {
    fpsEstimate = Math.round(fpsFrames / fpsTimer);
    fpsFrames = 0;
    fpsTimer = 0;
  }

  if (world) {
    let shiftProgress = 0;
    if (screen === 'playing') {
      shiftElapsed += dt;
      shiftProgress = Math.min(1, shiftElapsed / SHIFT_DURATION_S);
      clockPill.textContent = formatClock(shiftProgress);
      updatePlayer(dt);
      updateInteraction(dt);
      for (const vw of activeVisitorWalks) {
        const dx = vw.dest.x - vw.obj.position.x;
        const dz = vw.dest.z - vw.obj.position.z;
        const dist = Math.hypot(dx, dz);
        if (dist > 0.5) {
          vw.obj.position.x += (dx / dist) * 3.0 * dt;
          vw.obj.position.z += (dz / dist) * 3.0 * dt;
          vw.obj.rotation.y = Math.atan2(dx, dz);
        }
      }
      if (shiftProgress >= 1) showDawnSummary();
    }
    world.update(dt, screen === 'dawn' ? 1 : shiftProgress);
    updateCameraAndFlashlight();
    if (screen === 'playing') drawMinimap();
  }

  if (ink.enabled) ink.render(scene, camera);
  else renderer.render(scene, camera);
}

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Test / debug hooks per game/DESIGN.md
window.game = {
  debug: {
    completeTask(type) {
      if (!world) return false;
      if (screen === 'start') startShift();
      const task = world.tasks.find((t) => !t.done && (!type || t.type === type));
      if (!task) return false;
      if (task.type === 'carry' && !task.carried) {
        world.player.obj.position.set(task.position[0], 0, task.position[2]);
        resolveTask(task);
      }
      const pos = getTaskTargetPos(task);
      world.player.obj.position.set(pos[0], 0, pos[2]);
      resolveTask(task);
      return true;
    },
    skipTo(target) {
      if (!world) return false;
      if (target === 'dawn') {
        shiftElapsed = SHIFT_DURATION_S;
        world.update(0.016, 1);
        showDawnSummary();
        return true;
      }
      return false;
    },
    getState() {
      const p = world?.player?.obj?.position;
      return {
        screen,
        shiftNumber,
        seed: currentSeed,
        muted: audio.muted,
        shiftProgress: Math.min(1, shiftElapsed / SHIFT_DURATION_S),
        fps: fpsEstimate,
        completedCount: world ? world.tasks.filter((t) => t.done).length : 0,
        totalTasks: world ? world.tasks.length : 0,
        playerPosition: p ? [Number(p.x.toFixed(2)), Number(p.y.toFixed(2)), Number(p.z.toFixed(2))] : [0, 0, 0],
        tasks: world ? world.tasks.map((t) => ({ id: t.id, type: t.type, label: t.label, done: t.done, carried: Boolean(t.carried) })) : [],
      };
    },
  },
};

startBtn.focus();
initWorld().catch((err) => console.error('[game] initWorld failed:', err));
requestAnimationFrame(animate);
