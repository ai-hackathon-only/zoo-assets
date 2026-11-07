// park/park.js: assembles a layout from park/generator.js into a three.js scene.
// Every GLB is fetched once; each mesh inside it becomes one InstancedMesh.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/OrbitControls.js';
import { GLTFLoader } from 'three/addons/GLTFLoader.js';
import { generateLayout, GRID_M } from './generator.js';

// rAF timestamps count from navigation start, so first-frame time includes HTML, three.js and GLB downloads.
const $ = (id) => document.getElementById(id);
const PATH_ASSET = 'path_asphalt_straight';
const DEFAULTS = { size: 200, density: 0.5, population: 60, seed: 42, style: 'grid' };

// ---------- settings <-> URL ----------
function readSettings() {
  const q = new URLSearchParams(location.search);
  const num = (k, lo, hi) => {
    const v = Number(q.get(k));
    return q.has(k) && Number.isFinite(v) ? Math.min(hi, Math.max(lo, v)) : DEFAULTS[k];
  };
  const styleVal = q.get('style');
  return {
    size: num('size', 80, 600),
    density: num('density', 0, 1),
    population: Math.round(num('population', 0, 300)),
    seed: q.get('seed') || String(DEFAULTS.seed),
    theme: q.get('theme') === 'night' ? 'night' : 'day',
    style: ['grid', 'loop', 'radial'].includes(styleVal) ? styleVal : DEFAULTS.style,
  };
}
function writeSettings(s) {
  const params = { size: s.size, density: s.density, population: s.population, seed: s.seed };
  if (s.theme === 'night') params.theme = 'night';
  if (s.style && s.style !== 'grid') params.style = s.style;
  const q = new URLSearchParams(params);
  history.replaceState(null, '', `${location.pathname}?${q}`);
}

// ---------- three.js setup ----------
const canvas = $('scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xcfe8f3);
const camera = new THREE.PerspectiveCamera(50, 1, 0.5, 4000);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.maxPolarAngle = Math.PI * 0.47;
const hemiLight = new THREE.HemisphereLight(0xffffff, 0x8a9a6a, 1.6);
scene.add(hemiLight);
const sun = new THREE.DirectionalLight(0xffffff, 1.8);
sun.position.set(-1, 2, 1.2);
scene.add(sun);

const ground = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshLambertMaterial({ color: 0x9cc77a }));
ground.rotation.x = -Math.PI / 2;
scene.add(ground);
const world = new THREE.Group();
scene.add(world);

let currentTheme = 'day';
const loadedMaterials = new Set();

function setTheme(theme) {
  currentTheme = theme === 'night' ? 'night' : 'day';
  const isNight = currentTheme === 'night';
  const themeBtn = $('theme');
  if (themeBtn) {
    themeBtn.textContent = isNight ? '☀️ Day' : '🌙 Night';
    themeBtn.setAttribute('aria-pressed', isNight ? 'true' : 'false');
  }
  document.body.dataset.theme = currentTheme;
  if (isNight) {
    scene.background.setHex(0x0a1122);
    hemiLight.color.setHex(0x3a4866);
    hemiLight.groundColor.setHex(0x18202c);
    hemiLight.intensity = 0.5;
    sun.color.setHex(0x5c7ca8);
    sun.intensity = 0.6;
    ground.material.color.setHex(0x233120);
    for (const mat of loadedMaterials) {
      if (mat.emissive && (mat.emissive.r > 0 || mat.emissive.g > 0 || mat.emissive.b > 0)) {
        mat.emissiveIntensity = 8.0;
        mat.needsUpdate = true;
      }
    }
  } else {
    scene.background.setHex(0xcfe8f3);
    hemiLight.color.setHex(0xffffff);
    hemiLight.groundColor.setHex(0x8a9a6a);
    hemiLight.intensity = 1.6;
    sun.color.setHex(0xffffff);
    sun.intensity = 1.8;
    ground.material.color.setHex(0x9cc77a);
    for (const mat of loadedMaterials) {
      if (mat.emissive && (mat.emissive.r > 0 || mat.emissive.g > 0 || mat.emissive.b > 0)) {
        mat.emissiveIntensity = 0.0;
        mat.needsUpdate = true;
      }
    }
  }
}

function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(canvas);

// ---------- asset loading (one fetch per GLB) ----------
const loader = new GLTFLoader();
let catalog = [];
const byId = new Map();
const glbCache = new Map(); // asset id -> Promise<[{geometry, material, local}]>

function loadParts(id) {
  if (glbCache.has(id)) return glbCache.get(id);
  const row = byId.get(id);
  const p = !row || !row.glb ? Promise.resolve([]) : loader.loadAsync(`../${row.glb}`).then((gltf) => {
    const parts = [];
    gltf.scene.updateMatrixWorld(true);
    gltf.scene.traverse((o) => {
      if (o.isMesh) {
        parts.push({ geometry: o.geometry, material: o.material, local: o.matrixWorld.clone() });
        if (Array.isArray(o.material)) o.material.forEach((m) => loadedMaterials.add(m));
        else if (o.material) loadedMaterials.add(o.material);
      }
    });
    setTheme(currentTheme);
    return parts;
  }).catch((e) => { console.warn('GLB failed', id, e.message); return []; });
  glbCache.set(id, p);
  return p;
}

// layout (x, y) on the ground -> three (x, 0, y), centred on the park.
function placement(pos, rotDeg, half, scale = [1, 1, 1]) {
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), THREE.MathUtils.degToRad(-(rotDeg || 0)));
  m.compose(new THREE.Vector3(pos[0] - half, pos[2] || 0, pos[1] - half), q, new THREE.Vector3(...scale));
  return m;
}

// ---------- dynamic living scene (pathfinding & NPC simulation) ----------
let dynamicEntities = [];
const dynamicMeshes = new Set();
let simRunning = true;
let lastSimTime = performance.now();

const _posVec = new THREE.Vector3();
const _scaleVec = new THREE.Vector3(1, 1, 1);
const _quat = new THREE.Quaternion();
const _upAxis = new THREE.Vector3(0, 1, 0);
const _dynMatrix = new THREE.Matrix4();
const _tmpMatrix = new THREE.Matrix4();

function updatePlacementMatrix(m, pos, rotDeg, half, scale = [1, 1, 1]) {
  _quat.setFromAxisAngle(_upAxis, THREE.MathUtils.degToRad(-(rotDeg || 0)));
  _posVec.set(pos[0] - half, pos[2] || 0, pos[1] - half);
  _scaleVec.set(...scale);
  m.compose(_posVec, _quat, _scaleVec);
  return m;
}

function updateSimulation(dt, half) {
  for (const ent of dynamicEntities) {
    if (ent.type === 'visitor' || ent.type === 'keeper') {
      if (ent.waitTimer > 0) {
        ent.waitTimer -= dt;
      } else if (ent.currentNode && ent.targetNode && ent.currentNode !== ent.targetNode) {
        const segDist = Math.hypot(ent.targetNode.x - ent.currentNode.x, ent.targetNode.y - ent.currentNode.y);
        ent.progress += (ent.speed * dt) / Math.max(0.1, segDist);
        if (ent.progress >= 1) {
          ent.curX = ent.targetNode.x;
          ent.curY = ent.targetNode.y;
          ent.prevNode = ent.currentNode;
          ent.currentNode = ent.targetNode;
          ent.progress = 0;

          const candidates = ent.currentNode.neighbors.filter((n) => n !== ent.prevNode);
          const next = (candidates.length > 0)
            ? candidates[Math.floor(Math.random() * candidates.length)]
            : (ent.currentNode.neighbors[0] || ent.currentNode);
          ent.targetNode = next;

          if (Math.random() < 0.25) {
            ent.waitTimer = 1.0 + Math.random() * 2.5;
          }
        } else {
          ent.curX = (1 - ent.progress) * ent.currentNode.x + ent.progress * ent.targetNode.x;
          ent.curY = (1 - ent.progress) * ent.currentNode.y + ent.progress * ent.targetNode.y;
          const dx = ent.targetNode.x - ent.currentNode.x;
          const dy = ent.targetNode.y - ent.currentNode.y;
          if (Math.hypot(dx, dy) > 0.01) {
            ent.rotDeg = Math.atan2(dx, dy) * (180 / Math.PI);
          }
        }
      }
    } else if (ent.type === 'animal') {
      if (ent.state === 'idle') {
        ent.waitTimer -= dt;
        if (ent.waitTimer <= 0) {
          const b = ent.bounds;
          ent.targetX = b.minX + Math.random() * Math.max(0.1, b.maxX - b.minX);
          ent.targetY = b.minY + Math.random() * Math.max(0.1, b.maxY - b.minY);
          ent.state = 'walk';
        }
      } else if (ent.state === 'walk') {
        const dx = ent.targetX - ent.curX;
        const dy = ent.targetY - ent.curY;
        const dist = Math.hypot(dx, dy);
        const step = ent.speed * dt;
        if (dist <= step || dist < 0.05) {
          ent.curX = ent.targetX;
          ent.curY = ent.targetY;
          ent.state = 'idle';
          ent.waitTimer = 2.0 + Math.random() * 4.0;
        } else {
          ent.curX += (dx / dist) * step;
          ent.curY += (dy / dist) * step;
          ent.rotDeg = Math.atan2(dx, dy) * (180 / Math.PI);
        }
      }
    }

    updatePlacementMatrix(_dynMatrix, [ent.curX, ent.curY, ent.z], ent.rotDeg, half);
    for (const b of ent.bindings) {
      _tmpMatrix.multiplyMatrices(_dynMatrix, b.local);
      b.im.setMatrixAt(b.index, _tmpMatrix);
    }
  }

  for (const im of dynamicMeshes) {
    im.instanceMatrix.needsUpdate = true;
  }
}

// ---------- build ----------
let layout = null;
let buildToken = 0;

const GATE_ASSET = 'gate_pedestrian_wicket';

function collectPlacements(L) {
  const half = L.boundary.width_m / 2;
  const groups = new Map();
  dynamicEntities = [];
  dynamicMeshes.clear();

  const add = (id, m, entity = null) => {
    if (!groups.has(id)) groups.set(id, []);
    groups.get(id).push({ m, entity });
  };

  add(L.entrance.asset_id, placement(L.entrance.position, L.entrance.rotation_deg, half));
  for (const p of L.paths) add(PATH_ASSET, placement(p.position, 0, half, [1, 1, 0.5])); // tile is 2 x 4 m

  // Build path navigation graph for people
  const pathGraph = new Map();
  const tileKey = (x, y) => `${Math.round(x)},${Math.round(y)}`;
  for (const p of L.paths) {
    const k = tileKey(p.position[0], p.position[1]);
    pathGraph.set(k, { x: p.position[0], y: p.position[1], neighbors: [] });
  }
  for (const node of pathGraph.values()) {
    for (const [dx, dy] of [[GRID_M, 0], [-GRID_M, 0], [0, GRID_M], [0, -GRID_M]]) {
      const neighbor = pathGraph.get(tileKey(node.x + dx, node.y + dy));
      if (neighbor) node.neighbors.push(neighbor);
    }
  }

  for (const e of L.enclosures) {
    const b = e.bounds, gx = e.gate_position[0], gy = e.gate_position[1];
    const pad = Math.max(1.2, (e.animals[0]?.size_m || 1.5) * 0.45);
    const minX = Math.min(b.min_x + pad, e.center[0]);
    const maxX = Math.max(b.max_x - pad, e.center[0]);
    const minY = Math.min(b.min_y + pad, e.center[1]);
    const maxY = Math.max(b.max_y - pad, e.center[1]);

    for (const a of e.animals) {
      const entity = {
        type: 'animal',
        id: a.id,
        curX: a.position[0],
        curY: a.position[1],
        z: a.position[2] || 0,
        rotDeg: a.rotation_deg,
        speed: 0.6 + Math.random() * 0.5,
        state: 'idle',
        waitTimer: 1.0 + Math.random() * 4.0,
        targetX: a.position[0],
        targetY: a.position[1],
        bounds: { minX, maxX, minY, maxY },
        bindings: []
      };
      dynamicEntities.push(entity);
      add(a.asset_id, placement(a.position, a.rotation_deg, half), entity);
    }

    // fence pieces are 2 m long along X; the gate tile gets a 2 m wicket gate (same grid footprint).
    for (let x = b.min_x; x < b.max_x - 0.01; x += GRID_M) {
      for (const y of [b.min_y, b.max_y]) {
        if (Math.abs(x + 1 - gx) < 1.01 && Math.abs(y - gy) < 1.01) { add(GATE_ASSET, placement([x + 1, y, 0], 0, half)); continue; }
        add(e.fence_asset_id, placement([x + 1, y, 0], 0, half));
      }
    }
    for (let y = b.min_y; y < b.max_y - 0.01; y += GRID_M) {
      for (const x of [b.min_x, b.max_x]) {
        if (Math.abs(y + 1 - gy) < 1.01 && Math.abs(x - gx) < 1.01) { add(GATE_ASSET, placement([x, y + 1, 0], 90, half)); continue; }
        add(e.fence_asset_id, placement([x, y + 1, 0], 90, half));
      }
    }
  }

  for (const k of ['facilities', 'decorations']) {
    for (const o of L[k]) add(o.asset_id, placement(o.position, o.rotation_deg, half));
  }

  // Dynamic people (visitors and keepers)
  for (const p of L.people) {
    let closestNode = null, minDist = Infinity;
    for (const node of pathGraph.values()) {
      const d = Math.hypot(node.x - p.position[0], node.y - p.position[1]);
      if (d < minDist) { minDist = d; closestNode = node; }
    }

    // Smoothly walk from spawn position to closest path node, then continue onto graph
    const spawnNode = { x: p.position[0], y: p.position[1], neighbors: closestNode ? [closestNode] : [] };
    const targetNode = closestNode || spawnNode;

    const entity = {
      type: p.role,
      id: p.id,
      curX: p.position[0],
      curY: p.position[1],
      z: p.position[2] || 0,
      rotDeg: p.rotation_deg,
      speed: (p.role === 'keeper' ? 1.2 : 0.8) + (Math.random() * 0.4),
      currentNode: spawnNode,
      targetNode: targetNode,
      prevNode: null,
      progress: 0,
      waitTimer: Math.random() * 2,
      bindings: []
    };
    dynamicEntities.push(entity);
    add(p.asset_id, placement(p.position, p.rotation_deg, half), entity);
  }

  return groups;
}

// given: an imported layout object; when set, the generator is skipped.
async function build(s, given = null) {
  const token = ++buildToken;
  const t = performance.now();
  layout = given || generateLayout({ size_m: s.size, density: s.density, population: s.population, seed: s.seed, style: s.style }, { assets: catalog });
  const genMs = performance.now() - t;
  const size = layout.boundary.width_m;
  ground.scale.set(size + 40, size + 40, 1);
  drawMinimap();

  const groups = collectPlacements(layout);
  const loaded = await Promise.all([...groups.keys()].map((id) => loadParts(id).then((parts) => [id, parts])));
  if (token !== buildToken) return;

  for (const c of [...world.children]) { world.remove(c); c.dispose?.(); }
  let instances = 0, draws = 0;
  const tmp = new THREE.Matrix4();
  for (const [id, parts] of loaded) {
    const items = groups.get(id);
    for (const part of parts) {
      const im = new THREE.InstancedMesh(part.geometry, part.material, items.length);
      items.forEach((item, i) => {
        im.setMatrixAt(i, tmp.multiplyMatrices(item.m, part.local));
        if (item.entity) {
          item.entity.bindings.push({ im, index: i, local: part.local });
          dynamicMeshes.add(im);
          im.frustumCulled = false;
        }
      });
      im.instanceMatrix.needsUpdate = true;
      im.computeBoundingSphere();
      world.add(im);
      draws++;
    }
    instances += items.length;
  }
  const st = layout.stats;
  $('stats').textContent =
    `${st.total_enclosures} enclosures · ${st.total_animals} animals · ${st.total_facilities} facilities · ` +
    `${st.total_people} people · ${glbCache.size} GLBs · ${instances} instances · ${draws} draws · ` +
    (given ? 'imported layout.json' : `layout ${genMs.toFixed(1)} ms`);
  document.body.dataset.ready = '1';
  document.body.dataset.animals = String(st.total_animals);
  document.body.dataset.people = String(st.total_people);
  document.body.dataset.source = given ? 'import' : 'generator';
  document.body.dataset.simulating = simRunning ? '1' : '0';
}

function frameAll() {
  const size = layout ? layout.boundary.width_m : 200;
  camera.position.set(0, size * 0.55, size * 0.75);
  controls.target.set(0, 0, 0);
  camera.far = size * 6;
  camera.updateProjectionMatrix();
}

function focusEnclosure(e) {
  const half = layout.boundary.width_m / 2;
  const cx = e.center[0] - half, cz = e.center[1] - half;
  const d = Math.max(e.bounds.width, e.bounds.depth) * 1.4 + 6;
  controls.target.set(cx, 0, cz);
  camera.position.set(cx + d * 0.4, d * 0.8, cz + d);
  $('focus-name').textContent = e.name;
  document.body.dataset.focus = e.id;
}

// ---------- minimap ----------
const mini = $('minimap');
const mctx = mini.getContext('2d');
function drawMinimap() {
  const L = layout, W = mini.width, k = W / L.boundary.width_m;
  mctx.fillStyle = '#b9d99c';
  mctx.fillRect(0, 0, W, W);
  mctx.fillStyle = '#e9dfc8';
  for (const p of L.paths) mctx.fillRect((p.position[0] - 1) * k, (p.position[1] - 1) * k, Math.max(1, 2 * k), Math.max(1, 2 * k));
  mctx.fillStyle = '#7e9f62';
  for (const f of L.facilities) mctx.fillRect((f.position[0] - f.footprint[0] / 2) * k, (f.position[1] - f.footprint[1] / 2) * k, f.footprint[0] * k, f.footprint[1] * k);
  mctx.font = `${Math.max(8, Math.min(11, 160 / Math.sqrt(L.enclosures.length + 1)))}px system-ui, sans-serif`;
  mctx.textAlign = 'center';
  for (const e of L.enclosures) {
    const b = e.bounds;
    mctx.fillStyle = '#f6c56a';
    mctx.strokeStyle = '#5b4220';
    mctx.fillRect(b.min_x * k, b.min_y * k, b.width * k, b.depth * k);
    mctx.strokeRect(b.min_x * k, b.min_y * k, b.width * k, b.depth * k);
  }
  mctx.fillStyle = '#2d2414';
  for (const e of L.enclosures) {
    const label = e.name.replace(/ Habitat$/, '');
    mctx.fillText(label.length > 14 ? label.slice(0, 13) + '…' : label, e.center[0] * k, e.center[1] * k + 3);
  }
  const en = L.entrance;
  mctx.fillStyle = '#c0392b';
  mctx.fillRect((en.position[0] - 3) * k, (en.position[1] - 1) * k, Math.max(4, 6 * k), Math.max(3, 2 * k));
}
mini.addEventListener('click', (ev) => {
  if (!layout) return;
  const r = mini.getBoundingClientRect();
  const x = (ev.clientX - r.left) / r.width * layout.boundary.width_m;
  const y = (ev.clientY - r.top) / r.height * layout.boundary.width_m;
  let best = null, bd = Infinity;
  for (const e of layout.enclosures) {
    const b = e.bounds;
    const dx = Math.max(b.min_x - x, 0, x - b.max_x), dy = Math.max(b.min_y - y, 0, y - b.max_y);
    const d = Math.hypot(dx, dy);
    if (d < bd) { bd = d; best = e; }
  }
  if (best && bd < layout.boundary.width_m * 0.05 + 4) focusEnclosure(best);
});

// ---------- controls ----------
const inputs = { size: $('size'), density: $('density'), population: $('population'), seed: $('seed'), style: $('style') };
function current() {
  return {
    size: Number(inputs.size.value), density: Number(inputs.density.value),
    population: Number(inputs.population.value), seed: inputs.seed.value.trim() || '0',
    theme: currentTheme,
    style: inputs.style ? inputs.style.value : 'grid',
  };
}
function showValues() {
  $('size-out').textContent = `${inputs.size.value} m`;
  $('density-out').textContent = `${Math.round(inputs.density.value * 100)}%`;
  $('population-out').textContent = inputs.population.value;
}
let pending = 0;
function apply(reframe) {
  showValues();
  const s = current();
  writeSettings(s);
  clearTimeout(pending);
  pending = setTimeout(() => build(s).then(() => { if (reframe) frameAll(); }), 120);
}
for (const k of ['size', 'density', 'population']) inputs[k].addEventListener('input', () => apply(k === 'size'));
inputs.seed.addEventListener('change', () => apply(false));
if (inputs.style) inputs.style.addEventListener('change', () => apply(false));
$('shuffle').addEventListener('click', () => {
  inputs.seed.value = String(Math.floor(Math.random() * 1e6));
  apply(false);
});
// ---------- export / import layout.json ----------
const REQUIRED = ['version', 'settings', 'boundary', 'entrance', 'paths', 'enclosures', 'facilities', 'decorations', 'people', 'stats'];
$('export').addEventListener('click', () => {
  if (!layout) return;
  const blob = new Blob([JSON.stringify(layout, null, 1)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `zoo-${layout.settings.seed}-${layout.settings.size_m}m.json`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
});
$('import').addEventListener('click', () => $('import-file').click());
$('import-file').addEventListener('change', async (ev) => {
  const file = ev.target.files[0];
  ev.target.value = '';
  if (!file) return;
  let L;
  try { L = JSON.parse(await file.text()); } catch { $('stats').textContent = 'Import failed: not valid JSON.'; return; }
  const missing = REQUIRED.filter((k) => !(L && k in L));
  if (missing.length) { $('stats').textContent = `Import failed: missing ${missing.join(', ')}.`; return; }
  const st = L.settings;
  inputs.size.value = st.size_m; inputs.density.value = st.density;
  inputs.population.value = st.population; inputs.seed.value = st.seed;
  if (st.style && inputs.style) inputs.style.value = st.style;
  showValues();
  writeSettings(current());
  clearTimeout(pending);
  await build(current(), L);
  frameAll();
});

$('overview').addEventListener('click', () => { frameAll(); $('focus-name').textContent = 'Whole park'; });
const themeBtn = $('theme');
if (themeBtn) {
  themeBtn.addEventListener('click', () => {
    const next = currentTheme === 'night' ? 'day' : 'night';
    setTheme(next);
    const s = current();
    writeSettings(s);
  });
}

const simBtn = $('sim-toggle');
function toggleSim() {
  simRunning = !simRunning;
  if (simBtn) simBtn.textContent = simRunning ? 'Pause NPCs' : 'Resume NPCs';
  document.body.dataset.simulating = simRunning ? '1' : '0';
}
if (simBtn) simBtn.addEventListener('click', toggleSim);

// ---------- fps ----------
let frames = 0, last = performance.now(), firstFrame = 0;
function loop(now) {
  controls.update();
  const dt = Math.min((now - lastSimTime) / 1000, 0.1);
  lastSimTime = now;
  if (simRunning && dynamicEntities.length > 0 && layout) {
    updateSimulation(dt, layout.boundary.width_m / 2);
  }
  renderer.render(scene, camera);
  if (!firstFrame && document.body.dataset.ready) {
    firstFrame = now;
    $('first').textContent = `first frame ${(firstFrame / 1000).toFixed(2)} s`;
    document.body.dataset.firstFrameMs = String(Math.round(firstFrame));
  }
  frames++;
  if (now - last >= 1000) {
    const fps = frames * 1000 / (now - last);
    $('fps').textContent = `${fps.toFixed(0)} fps`;
    document.body.dataset.fps = fps.toFixed(1);
    frames = 0; last = now;
  }
  requestAnimationFrame(loop);
}

// ---------- start ----------
const s0 = readSettings();
inputs.size.value = s0.size; inputs.density.value = s0.density;
inputs.population.value = s0.population; inputs.seed.value = s0.seed;
if (inputs.style) inputs.style.value = s0.style;
showValues();
setTheme(s0.theme);
const res = await fetch('../assets.json');
const json = await res.json();
catalog = Array.isArray(json) ? json : json.assets;
for (const a of catalog) byId.set(a.id, a);
resize();
await build(s0);
frameAll();
requestAnimationFrame(loop);

// read-only hook for scripted interaction checks
window.__park = {
  get layout() { return layout; },
  get camera() { return camera; },
  get controls() { return controls; },
  get theme() { return currentTheme; },
  setTheme,
  get npcs() { return dynamicEntities; },
  get isSimulating() { return simRunning; },
  toggleSimulation() { toggleSim(); }
};
