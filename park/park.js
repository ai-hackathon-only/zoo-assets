// park/park.js: assembles a layout from park/generator.js into a three.js scene.
// Every GLB is fetched once; each mesh inside it becomes one InstancedMesh.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/OrbitControls.js';
import { GLTFLoader } from 'three/addons/GLTFLoader.js';
import { generateLayout, GRID_M } from './generator.js';

// rAF timestamps count from navigation start, so first-frame time includes HTML, three.js and GLB downloads.
const $ = (id) => document.getElementById(id);
const PATH_ASSET = 'path_asphalt_straight';
const DEFAULTS = { size: 200, density: 0.5, population: 60, seed: 42 };

// ---------- settings <-> URL ----------
function readSettings() {
  const q = new URLSearchParams(location.search);
  const num = (k, lo, hi) => {
    const v = Number(q.get(k));
    return q.has(k) && Number.isFinite(v) ? Math.min(hi, Math.max(lo, v)) : DEFAULTS[k];
  };
  return {
    size: num('size', 80, 600),
    density: num('density', 0, 1),
    population: Math.round(num('population', 0, 300)),
    seed: q.get('seed') || String(DEFAULTS.seed),
  };
}
function writeSettings(s) {
  const q = new URLSearchParams({ size: s.size, density: s.density, population: s.population, seed: s.seed });
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
scene.add(new THREE.HemisphereLight(0xffffff, 0x8a9a6a, 1.6));
const sun = new THREE.DirectionalLight(0xffffff, 1.8);
sun.position.set(-1, 2, 1.2);
scene.add(sun);

const ground = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshLambertMaterial({ color: 0x9cc77a }));
ground.rotation.x = -Math.PI / 2;
scene.add(ground);
const world = new THREE.Group();
scene.add(world);

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
      if (o.isMesh) parts.push({ geometry: o.geometry, material: o.material, local: o.matrixWorld.clone() });
    });
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

// ---------- build ----------
let layout = null;
let buildToken = 0;

const GATE_ASSET = 'gate_pedestrian_wicket';

function collectPlacements(L) {
  const half = L.boundary.width_m / 2;
  const groups = new Map();
  const add = (id, m) => { if (!groups.has(id)) groups.set(id, []); groups.get(id).push(m); };
  add(L.entrance.asset_id, placement(L.entrance.position, L.entrance.rotation_deg, half));
  for (const p of L.paths) add(PATH_ASSET, placement(p.position, 0, half, [1, 1, 0.5])); // tile is 2 x 4 m
  for (const e of L.enclosures) {
    for (const a of e.animals) add(a.asset_id, placement(a.position, a.rotation_deg, half));
    const b = e.bounds, gx = e.gate_position[0], gy = e.gate_position[1];
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
  for (const k of ['facilities', 'decorations', 'people']) {
    for (const o of L[k]) add(o.asset_id, placement(o.position, o.rotation_deg, half));
  }
  return groups;
}

async function build(s) {
  const token = ++buildToken;
  const t = performance.now();
  layout = generateLayout({ size_m: s.size, density: s.density, population: s.population, seed: s.seed }, { assets: catalog });
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
    const mats = groups.get(id);
    for (const part of parts) {
      const im = new THREE.InstancedMesh(part.geometry, part.material, mats.length);
      mats.forEach((m, i) => im.setMatrixAt(i, tmp.multiplyMatrices(m, part.local)));
      im.instanceMatrix.needsUpdate = true;
      im.computeBoundingSphere();
      world.add(im);
      draws++;
    }
    instances += mats.length;
  }
  const st = layout.stats;
  $('stats').textContent =
    `${st.total_enclosures} enclosures · ${st.total_animals} animals · ${st.total_facilities} facilities · ` +
    `${st.total_people} people · ${glbCache.size} GLBs · ${instances} instances · ${draws} draws · layout ${genMs.toFixed(1)} ms`;
  document.body.dataset.ready = '1';
  document.body.dataset.animals = String(st.total_animals);
  document.body.dataset.people = String(st.total_people);
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
const inputs = { size: $('size'), density: $('density'), population: $('population'), seed: $('seed') };
function current() {
  return {
    size: Number(inputs.size.value), density: Number(inputs.density.value),
    population: Number(inputs.population.value), seed: inputs.seed.value.trim() || '0',
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
$('shuffle').addEventListener('click', () => {
  inputs.seed.value = String(Math.floor(Math.random() * 1e6));
  apply(false);
});
$('overview').addEventListener('click', () => { frameAll(); $('focus-name').textContent = 'Whole park'; });

// ---------- fps ----------
let frames = 0, last = performance.now(), firstFrame = 0;
function loop(now) {
  controls.update();
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
showValues();
const res = await fetch('../assets.json');
const json = await res.json();
catalog = Array.isArray(json) ? json : json.assets;
for (const a of catalog) byId.set(a.id, a);
resize();
await build(s0);
frameAll();
requestAnimationFrame(loop);

// read-only hook for scripted interaction checks
window.__park = { get layout() { return layout; } };
