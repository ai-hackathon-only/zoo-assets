/**
 * Night Shift — World, Night Lighting, Asset Loader & Task Spawner.
 * Reuses park/generator.js layouts, assets.json GLBs, and RIGS.md clips.
 */

import { generateLayout } from '../park/generator.js';

export const DEFAULT_WORLD_SETTINGS = {
  size_m: 100,
  density: 0.6,
  population: 6,
  seed: 'night-shift-1',
  style: 'grid',
  shiftNumber: 1,
};

function hashSeed(str) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

/**
 * Convert park/generator.js 2D layout coordinate [x, y, 0] to Three.js world [x, y_up, z].
 */
export function layoutToWorld(pos, y = 0) {
  return [pos[0], y, pos[1]];
}

/**
 * Clone a skinned Three.js scene so each instance has its own bone hierarchy.
 */
export function cloneSkinned(source) {
  const srcOf = new Map();
  const cloneOf = new Map();
  const copy = source.clone();
  (function walk(a, b) {
    srcOf.set(b, a);
    cloneOf.set(a, b);
    for (let i = 0; i < a.children.length; i++) walk(a.children[i], b.children[i]);
  })(source, copy);
  copy.traverse((node) => {
    if (!node.isSkinnedMesh) return;
    const src = srcOf.get(node);
    node.skeleton = src.skeleton.clone();
    node.bindMatrix.copy(src.bindMatrix);
    node.skeleton.bones = src.skeleton.bones.map((b) => cloneOf.get(b));
    node.bind(node.skeleton, node.bindMatrix);
  });
  return copy;
}

/**
 * Cached GLB loader and rig clip controller.
 */
export class AssetLoader {
  constructor(THREE, GLTFLoader, basePath = '..') {
    this.THREE = THREE;
    this.loader = new GLTFLoader();
    this.basePath = basePath;
    this.catalog = [];
    this.byId = new Map();
    this.cache = new Map();
    this.materials = new Set();
  }

  async loadCatalog() {
    if (this.catalog.length > 0) return this.catalog;
    const res = await fetch(`${this.basePath}/assets.json`);
    if (!res.ok) throw new Error(`Failed to load assets.json: ${res.status}`);
    const data = await res.json();
    this.catalog = Array.isArray(data) ? data : (data.assets || []);
    for (const item of this.catalog) this.byId.set(item.id, item);
    return this.catalog;
  }

  async loadAsset(id) {
    if (this.cache.has(id)) return this.cache.get(id);
    const meta = this.byId.get(id);
    if (!meta) throw new Error(`Unknown asset id: ${id}`);
    const relPath = meta.file || meta.glb;
    const url = `${this.basePath}/${relPath}`;
    const promise = this.loader.loadAsync(url).then((gltf) => {
      gltf.scene.traverse((obj) => {
        if (obj.isMesh && obj.material) {
          const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
          for (const m of mats) this.materials.add(m);
        }
      });
      return {
        id,
        meta,
        scene: gltf.scene,
        clips: gltf.animations || [],
      };
    });
    this.cache.set(id, promise);
    return promise;
  }

  instantiate(assetData, { rigged = true } = {}) {
    const obj = rigged ? cloneSkinned(assetData.scene) : assetData.scene.clone();
    obj.traverse((o) => {
      if (o.isMesh) o.frustumCulled = false;
    });
    const mixer = new this.THREE.AnimationMixer(obj);
    const actions = new Map();
    for (const clip of assetData.clips) {
      actions.set(clip.name, mixer.clipAction(clip));
    }

    let currentAction = null;
    let currentName = null;

    const playClip = (name, { loop = true, fade = 0.25, clampWhenFinished = false } = {}) => {
      const next = actions.get(name) || actions.get('idle');
      if (!next) return null;
      const resolvedName = actions.has(name) ? name : 'idle';
      if (currentName === resolvedName && loop) return next;

      next.reset();
      next.setLoop(loop ? this.THREE.LoopRepeat : this.THREE.LoopOnce, loop ? Infinity : 1);
      next.clampWhenFinished = clampWhenFinished;
      next.enabled = true;
      next.setEffectiveWeight(1);
      next.play();

      if (currentAction && currentAction !== next && fade > 0) {
        currentAction.crossFadeTo(next, fade, false);
      } else if (currentAction && currentAction !== next) {
        currentAction.stop();
      }
      currentAction = next;
      currentName = resolvedName;
      return next;
    };

    if (actions.has('idle')) {
      const a = playClip('idle', { loop: true, fade: 0 });
      if (a) a.time = Math.random() * a.getClip().duration;
      mixer.update(0);
    }

    return {
      obj,
      mixer,
      actions,
      playClip,
      getCurrentClip: () => currentName,
    };
  }
}

/**
 * Night-to-dawn lighting rig with keeper flashlight.
 */
export class NightLighting {
  constructor(THREE, scene, ground) {
    this.THREE = THREE;
    this.scene = scene;
    this.ground = ground;

    this.nightSky = new THREE.Color(0x0c1428);
    this.dawnSky = new THREE.Color(0xdba784);
    this.nightHemiSky = new THREE.Color(0x6a7fb0);
    this.dawnHemiSky = new THREE.Color(0xffe1c2);
    this.nightHemiGround = new THREE.Color(0x2c3a50);
    this.dawnHemiGround = new THREE.Color(0x6d7c58);
    this.nightSun = new THREE.Color(0x6b8ec2);
    this.dawnSun = new THREE.Color(0xffcfa0);
    this.nightGround = new THREE.Color(0x35502f);
    this.dawnGround = new THREE.Color(0x7ca65e);

    scene.background = this.nightSky.clone();
    scene.fog = new THREE.FogExp2(0x0c1428, 0.014);

    this.hemi = new THREE.HemisphereLight(0x3a4866, 0x18202c, 1.25);
    scene.add(this.hemi);

    this.sun = new THREE.DirectionalLight(0x6b8ec2, 0.75);
    this.sun.position.set(28, 42, -24);
    scene.add(this.sun);

    this.flashlight = null;
    this.flashlightTarget = null;
  }

  attachFlashlight(playerObj) {
    const spot = new this.THREE.SpotLight(0xfff1d0, 3.2, 26, Math.PI / 5, 0.45, 1.4);
    spot.position.set(0, 1.5, 0.15);
    const target = new this.THREE.Object3D();
    target.position.set(0, 0.3, 8);
    playerObj.add(spot);
    playerObj.add(target);
    spot.target = target;
    this.flashlight = spot;
    this.flashlightTarget = target;
    return spot;
  }

  setProgress(t) {
    const p = Math.max(0, Math.min(1, t));
    // Stay dark for most of the shift, then brighten smoothly in the last 35%.
    const dawn = Math.max(0, (p - 0.65) / 0.35);
    this.scene.background.lerpColors(this.nightSky, this.dawnSky, dawn);
    if (this.scene.fog) {
      this.scene.fog.color.copy(this.scene.background);
      this.scene.fog.density = 0.014 * (1 - dawn * 0.55);
    }
    this.hemi.color.lerpColors(this.nightHemiSky, this.dawnHemiSky, dawn);
    this.hemi.groundColor.lerpColors(this.nightHemiGround, this.dawnHemiGround, dawn);
    this.hemi.intensity = 1.25 + dawn * 0.4;
    this.sun.color.lerpColors(this.nightSun, this.dawnSun, dawn);
    this.sun.intensity = 0.75 + dawn * 1.05;
    if (this.ground && this.ground.material) {
      this.ground.material.color.lerpColors(this.nightGround, this.dawnGround, dawn);
    }
    if (this.flashlight) {
      this.flashlight.intensity = 3.2 * (1 - dawn * 0.7);
    }
  }
}

function makeBeacon(THREE, colorHex = 0xfbbf24) {
  const group = new THREE.Group();
  const ringGeo = new THREE.RingGeometry(0.65, 0.9, 24);
  ringGeo.rotateX(-Math.PI / 2);
  const ringMat = new THREE.MeshBasicMaterial({
    color: colorHex,
    transparent: true,
    opacity: 0.85,
    side: THREE.DoubleSide,
  });
  const ring = new THREE.Mesh(ringGeo, ringMat);
  ring.position.y = 0.06;
  group.add(ring);

  const pillarGeo = new THREE.CylinderGeometry(0.12, 0.25, 3.2, 12, 1, true);
  const pillarMat = new THREE.MeshBasicMaterial({
    color: colorHex,
    transparent: true,
    opacity: 0.25,
    side: THREE.DoubleSide,
    depthWrite: false,
  });
  const pillar = new THREE.Mesh(pillarGeo, pillarMat);
  pillar.position.y = 1.65;
  group.add(pillar);

  return group;
}

/**
 * Build the complete Night Shift world, player keeper, park props, and 6 tasks.
 */
export async function buildNightShiftWorld({
  THREE,
  GLTFLoader,
  scene,
  settings = {},
  basePath = '..',
}) {
  const cfg = { ...DEFAULT_WORLD_SETTINGS, ...settings };
  const loader = new AssetLoader(THREE, GLTFLoader, basePath);
  const catalog = await loader.loadCatalog();
  const layout = generateLayout(cfg, { assets: catalog });

  const worldGroup = new THREE.Group();
  scene.add(worldGroup);

  // Extend ground past camera far plane (260 m) so no plane edge seam shows in fog.
  const half = layout.boundary.width_m / 2 + 220;
  const groundGeo = new THREE.PlaneGeometry(half * 2, half * 2);
  groundGeo.rotateX(-Math.PI / 2);
  const groundMat = new THREE.MeshStandardMaterial({ color: 0x202d1d, roughness: 0.95 });
  const ground = new THREE.Mesh(groundGeo, groundMat);
  worldGroup.add(ground);

  const lighting = new NightLighting(THREE, scene, ground);
  lighting.setProgress(0);

  // Path tiles
  const pathMat = new THREE.MeshStandardMaterial({ color: 0x4b4e52, roughness: 0.9 });
  const pathGeo = new THREE.BoxGeometry(1, 0.04, 1);
  for (const p of layout.paths) {
    const tile = new THREE.Mesh(pathGeo, pathMat);
    tile.position.set(p.position[0], 0.02, p.position[1]);
    tile.scale.set(p.size[0], 1, p.size[1]);
    worldGroup.add(tile);
  }

  const mixers = [];
  const beacons = [];
  const tasks = [];

  // Preload core game assets in parallel
  const neededIds = new Set([
    'keeper_safari_lead_01',
    'gate_paddock_double_wood',
    'lamp_post_victorian_single',
    'food_fish_bucket_herring_04',
    'food_water_drink_trough_20',
    'visitor_tourist_camera_01',
    layout.entrance.asset_id,
  ]);
  for (const enc of layout.enclosures) {
    if (enc.animals[0]) neededIds.add(enc.animals[0].asset_id);
  }
  for (const dec of layout.decorations.slice(0, 12)) {
    neededIds.add(dec.asset_id);
  }

  await Promise.all([...neededIds].map((id) => loader.loadAsset(id).catch(() => null)));

  // Spawn player keeper at entrance
  const keeperAsset = await loader.loadAsset('keeper_safari_lead_01');
  const playerRig = loader.instantiate(keeperAsset, { rigged: true });
  playerRig.obj.position.set(
    layout.entrance.position[0],
    0,
    layout.entrance.position[1] + 3
  );
  worldGroup.add(playerRig.obj);
  mixers.push(playerRig.mixer);
  lighting.attachFlashlight(playerRig.obj);

  const propBone = playerRig.obj.getObjectByName('prop') || playerRig.obj;
  const attachProp = (propObj) => {
    if (!propObj) return;
    propBone.add(propObj);
    propObj.position.set(0, 0, 0);
    propObj.rotation.set(0, 0, 0);
  };
  const detachProp = (propObj, worldPos) => {
    if (!propObj) return;
    worldGroup.add(propObj);
    if (worldPos) {
      propObj.position.set(worldPos[0], worldPos[1] ?? 0, worldPos[2]);
    }
    propObj.rotation.set(0, 0, 0);
  };

  // Entrance arch
  if (loader.cache.has(layout.entrance.asset_id)) {
    const archData = await loader.loadAsset(layout.entrance.asset_id);
    const arch = loader.instantiate(archData, { rigged: false });
    arch.obj.position.set(...layoutToWorld(layout.entrance.position));
    arch.obj.rotation.y = (layout.entrance.rotation_deg * Math.PI) / 180;
    worldGroup.add(arch.obj);
  }

  // Decorations (trees/rocks)
  for (const dec of layout.decorations.slice(0, 12)) {
    if (!loader.cache.has(dec.asset_id)) continue;
    const data = await loader.loadAsset(dec.asset_id);
    const inst = loader.instantiate(data, { rigged: false });
    inst.obj.position.set(...layoutToWorld(dec.position));
    inst.obj.rotation.y = (dec.rotation_deg * Math.PI) / 180;
    if (dec.scale) inst.obj.scale.setScalar(dec.scale);
    worldGroup.add(inst.obj);
  }

  // Enclosures: simple perimeter rails + primary animal
  const railMat = new THREE.MeshStandardMaterial({ color: 0x6f553b, roughness: 0.85 });
  const animalRigs = [];
  for (const enc of layout.enclosures) {
    const b = enc.bounds;
    const w = b.width;
    const d = b.depth;
    const cx = enc.center[0];
    const cz = enc.center[1];
    const railH = 0.9;
    const walls = [
      [cx, railH / 2, b.min_y, w, 0.14],
      [cx, railH / 2, b.max_y, w, 0.14],
      [b.min_x, railH / 2, cz, 0.14, d],
      [b.max_x, railH / 2, cz, 0.14, d],
    ];
    for (const [wx, wy, wz, sw, sd] of walls) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(sw, railH, sd), railMat);
      m.position.set(wx, wy, wz);
      worldGroup.add(m);
    }

    const firstAnimal = enc.animals[0];
    if (firstAnimal && loader.cache.has(firstAnimal.asset_id)) {
      const aData = await loader.loadAsset(firstAnimal.asset_id);
      const aRig = loader.instantiate(aData, { rigged: true });
      aRig.obj.position.set(...layoutToWorld(firstAnimal.position));
      aRig.obj.rotation.y = (firstAnimal.rotation_deg * Math.PI) / 180;
      worldGroup.add(aRig.obj);
      mixers.push(aRig.mixer);
      animalRigs.push({ enc, rig: aRig, pos: firstAnimal.position });
    }
  }

  // Helper to register a task with a beacon
  const addTask = (task) => {
    const beacon = makeBeacon(THREE, task.color || 0xfbbf24);
    beacon.position.set(task.position[0], 0, task.position[2]);
    worldGroup.add(beacon);
    beacons.push(beacon);
    tasks.push({ ...task, beacon, status: 'pending' });
  };

  const seedHash = hashSeed(String(cfg.seed || 'night-shift-1'));
  const isDefaultShift = cfg.seed === 'night-shift-1' && (cfg.shiftNumber || 1) === 1;
  const encCount = Math.max(1, animalRigs.length);
  const encOffset = isDefaultShift ? 0 : (seedHash % encCount);
  const pickEncRig = (idx) => animalRigs[(idx + encOffset) % encCount];
  const pickLayoutEnc = (idx) => layout.enclosures[(idx + encOffset) % layout.enclosures.length] || layout.enclosures[0];
  const pickPath = (frac, fallbackIdx = 0) => {
    if (!layout.paths.length) return null;
    const shiftFrac = isDefaultShift ? frac : ((frac + ((seedHash % 7) * 0.11)) % 1);
    return layout.paths[Math.floor(layout.paths.length * shiftFrac)] || layout.paths[fallbackIdx] || layout.paths[0];
  };

  // Vary the 6-task mix on shift 2+ while keeping all 5 task types represented
  const extraType = isDefaultShift ? 'feed' : ['gate', 'lamp', 'feed'][seedHash % 3];

  // Task 1 (and Task 2 if extraType === 'feed'): Feed animals
  const feedCount = extraType === 'feed' ? 2 : 1;
  for (let i = 0; i < Math.min(feedCount, animalRigs.length); i++) {
    const target = pickEncRig(i);
    const enc = target.enc;
    addTask({
      id: `task-feed-${i + 1}`,
      type: 'feed',
      label: `Feed ${enc.name || enc.species_id}`,
      position: layoutToWorld(enc.gate_position),
      color: 0xf59e0b,
      rig: target.rig,
    });
  }

  // Gate task(s): Close an open gate
  const gateCount = extraType === 'gate' ? 2 : 1;
  for (let g = 0; g < gateCount; g++) {
    const gateEnc = pickLayoutEnc(2 + g);
    if (gateEnc && loader.cache.has('gate_paddock_double_wood')) {
      const gateData = await loader.loadAsset('gate_paddock_double_wood');
      const gateRig = loader.instantiate(gateData, { rigged: true });
      gateRig.obj.position.set(...layoutToWorld(gateEnc.gate_position));
      gateRig.playClip('open', { loop: false, fade: 0, clampWhenFinished: true });
      worldGroup.add(gateRig.obj);
      mixers.push(gateRig.mixer);
      addTask({
        id: `task-gate-${g + 1}`,
        type: 'gate',
        label: g === 0 ? 'Close paddock gate' : `Secure ${gateEnc.name || 'north'} gate`,
        position: layoutToWorld(gateEnc.gate_position),
        color: 0x38bdf8,
        rig: gateRig,
      });
    }
  }

  // Visitor task: Guide lost visitor
  const pathSpot = pickPath(0.6);
  if (pathSpot && loader.cache.has('visitor_tourist_camera_01')) {
    const visData = await loader.loadAsset('visitor_tourist_camera_01');
    const visRig = loader.instantiate(visData, { rigged: true });
    visRig.obj.position.set(...layoutToWorld(pathSpot.position));
    visRig.playClip('wave', { loop: true, fade: 0 });
    worldGroup.add(visRig.obj);
    mixers.push(visRig.mixer);
    addTask({
      id: 'task-visitor-1',
      type: 'visitor',
      label: 'Guide lost visitor to exit',
      position: layoutToWorld(pathSpot.position),
      color: 0xa78bfa,
      rig: visRig,
      exitPosition: layoutToWorld(layout.entrance.position),
    });
  }

  // Lamp task(s): Relight broken lamp
  const lampCount = extraType === 'lamp' ? 2 : 1;
  for (let l = 0; l < lampCount; l++) {
    const lampSpot = pickPath(l === 0 ? 0.35 : 0.78);
    if (lampSpot && loader.cache.has('lamp_post_victorian_single')) {
      const lampData = await loader.loadAsset('lamp_post_victorian_single');
      const lampInst = loader.instantiate(lampData, { rigged: false });
      const lx = lampSpot.position[0] + (l === 0 ? 1.5 : -1.5);
      lampInst.obj.position.set(lx, 0, lampSpot.position[1]);
      worldGroup.add(lampInst.obj);
      const bulbLight = new THREE.PointLight(0xffcb77, 0, 14, 1.5);
      bulbLight.position.set(lx, 3.1, lampSpot.position[1]);
      worldGroup.add(bulbLight);
      addTask({
        id: `task-lamp-${l + 1}`,
        type: 'lamp',
        label: l === 0 ? 'Relight broken lamp' : 'Relight path lantern',
        position: [lx, 0, lampSpot.position[1]],
        color: 0xfde047,
        light: bulbLight,
      });
    }
  }

  // Carry task: Carry fish bucket to trough
  const bucketSpot = pickPath(0.2);
  const troughEnc = pickLayoutEnc(3);
  if (!troughEnc) {
    console.warn(`[world] Skipping carry task: layout.enclosures[3] missing (count=${layout.enclosures.length})`);
  } else if (bucketSpot && loader.cache.has('food_fish_bucket_herring_04')) {
    const bucketData = await loader.loadAsset('food_fish_bucket_herring_04');
    const bucketInst = loader.instantiate(bucketData, { rigged: false });
    bucketInst.obj.position.set(bucketSpot.position[0] - 1.2, 0, bucketSpot.position[1]);
    worldGroup.add(bucketInst.obj);

    if (loader.cache.has('food_water_drink_trough_20')) {
      const troughData = await loader.loadAsset('food_water_drink_trough_20');
      const troughInst = loader.instantiate(troughData, { rigged: false });
      troughInst.obj.position.set(troughEnc.gate_position[0] + 1.4, 0, troughEnc.gate_position[1]);
      worldGroup.add(troughInst.obj);
    }

    addTask({
      id: 'task-carry-1',
      type: 'carry',
      label: 'Carry fish bucket to trough',
      position: [bucketSpot.position[0] - 1.2, 0, bucketSpot.position[1]],
      dropoff: [troughEnc.gate_position[0] + 1.4, 0, troughEnc.gate_position[1]],
      color: 0x34d399,
      prop: bucketInst.obj,
      carried: false,
    });
  }

  // Warm ambient lights on working path lamps (first 2 path junctions)
  for (const idx of [0, Math.floor(layout.paths.length * 0.75)]) {
    const p = layout.paths[idx];
    if (!p || !loader.cache.has('lamp_post_victorian_single')) continue;
    const lampData = await loader.loadAsset('lamp_post_victorian_single');
    const lampInst = loader.instantiate(lampData, { rigged: false });
    lampInst.obj.position.set(p.position[0] - 1.6, 0, p.position[1]);
    worldGroup.add(lampInst.obj);
    const l = new THREE.PointLight(0xffcb77, 2.2, 14, 1.5);
    l.position.set(p.position[0] - 1.6, 3.1, p.position[1]);
    worldGroup.add(l);
  }

  let pulseTime = 0;
  const update = (dt, shiftProgress = 0) => {
    pulseTime += dt;
    lighting.setProgress(shiftProgress);
    for (const m of mixers) m.update(dt);
    for (let i = 0; i < beacons.length; i++) {
      const b = beacons[i];
      if (!b.visible) continue;
      const s = 1 + Math.sin(pulseTime * 3 + i) * 0.12;
      b.scale.set(s, 1, s);
    }
  };

  return {
    layout,
    loader,
    lighting,
    player: playerRig,
    attachProp,
    detachProp,
    tasks,
    mixers,
    bounds: layout.boundary,
    update,
  };
}
