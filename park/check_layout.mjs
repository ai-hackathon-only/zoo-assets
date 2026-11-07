#!/usr/bin/env node
/**
 * park/check_layout.mjs
 * 
 * Verification build tool: generates 200 seeds across the setting ranges
 * and prints pass/fail per rule plus ms per layout.
 * 
 * Rules checked:
 * 1. One entrance (on boundary)
 * 2. Path connectivity (paths reach every enclosure and facility)
 * 3. Enclosure sizing & presence (sized per animal's size_m; enclosures > 0)
 * 4. Animals contained inside enclosure (pivot ± half animal length within bounds)
 * 5. No overlapping footprints (enclosures, facilities, entrance, paths)
 * 6. Facilities next to a path
 * 7. People on paths or near enclosures
 * 8. Ground & boundary (Z=0 and inside boundary)
 * 9. Every asset_id exists in assets.json
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { generateLayout, GRID_M, getEnclosureSizeMeters } from './generator.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

// Load assets.json
let assets = null;
let knownAssetIds = new Set();
try {
  const raw = JSON.parse(fs.readFileSync(path.join(ROOT, 'assets.json'), 'utf8'));
  assets = raw.assets || raw;
  for (const a of assets) {
    knownAssetIds.add(a.id);
  }
} catch (e) {
  console.warn('Warning: could not load assets.json:', e.message);
}

const TOTAL_SEEDS = 200;

console.log(`Starting procedural layout check across ${TOTAL_SEEDS} seeds...`);
console.log(`Setting ranges: size 80m-600m, density 0.0-1.0, population 0-300 people.\n`);

const ruleFailures = {
  one_entrance: 0,
  path_connectivity: 0,
  enclosure_sizing_and_presence: 0,
  animals_contained: 0,
  no_overlapping_footprints: 0,
  facilities_next_to_path: 0,
  people_on_paths_or_near_enclosures: 0,
  ground_and_boundary: 0,
  asset_ids_exist: 0,
  every_species_at_max_settings: 0
};

const timings = [];
const enclosureCounts = [];
const animalCounts = [];

// Quick determinism check before the 200-seed loop (excluding wall-clock elapsed timing)
const sampleSettings = { size_m: 160, density: 0.5, population: 50, seed: 'determinism_test' };
const runA = generateLayout(sampleSettings, { assets });
const runB = generateLayout(sampleSettings, { assets });
delete runA.stats.generation_time_ms;
delete runB.stats.generation_time_ms;
if (JSON.stringify(runA) !== JSON.stringify(runB)) {
  console.error('FATAL: Layout generator is not deterministic for identical settings and seed!');
  process.exit(1);
}

for (let i = 0; i < TOTAL_SEEDS; i++) {
  let size_m, density, population;
  if (i === 0) {
    size_m = 80; density = 0.0; population = 0;
  } else if (i === 1) {
    size_m = 80; density = 1.0; population = 300;
  } else if (i === 2) {
    size_m = 600; density = 0.0; population = 0;
  } else if (i === 3) {
    size_m = 600; density = 1.0; population = 300;
  } else {
    const t = i / (TOTAL_SEEDS - 1);
    size_m = 80 + Math.round((t * 520) / GRID_M) * GRID_M;
    density = Math.round(((i * 7 + 13) % 100) / 100 * 100) / 100;
    population = Math.round(((i * 17 + 29) % 301));
  }

  const seed = `seed_${i}_${size_m}_${density}_${population}`;

  const t0 = performance.now();
  const layout = generateLayout({ size_m, density, population, seed }, { assets });
  const t1 = performance.now();
  timings.push(t1 - t0);

  enclosureCounts.push(layout.enclosures.length);
  const totalAnimalsInLayout = layout.enclosures.reduce((sum, e) => sum + e.animals.length, 0);
  animalCounts.push(totalAnimalsInLayout);

  // 1. One entrance rule
  if (!layout.entrance || !layout.entrance.position || layout.entrance.position.length !== 3) {
    ruleFailures.one_entrance++;
  } else {
    const [ex, ey, ez] = layout.entrance.position;
    if (ez !== 0 || ex < 0 || ex > size_m || ey < 0 || ey > size_m) {
      ruleFailures.one_entrance++;
    }
  }

  // 2. Path connectivity (BFS from entrance to all path tiles, enclosures, facilities)
  const pathTileMap = new Map();
  for (const pt of layout.paths) {
    const key = `${Math.round(pt.position[0])},${Math.round(pt.position[1])}`;
    pathTileMap.set(key, pt);
  }

  let startTile = null;
  let minEntDist = Infinity;
  for (const pt of layout.paths) {
    const d = Math.hypot(pt.position[0] - layout.entrance.position[0], pt.position[1] - layout.entrance.position[1]);
    if (d < minEntDist) {
      minEntDist = d;
      startTile = pt;
    }
  }

  const reachablePaths = new Set();
  if (startTile) {
    const queue = [startTile];
    const visited = new Set();
    const startKey = `${Math.round(startTile.position[0])},${Math.round(startTile.position[1])}`;
    visited.add(startKey);
    reachablePaths.add(startKey);

    while (queue.length > 0) {
      const cur = queue.shift();
      const cx = Math.round(cur.position[0]);
      const cy = Math.round(cur.position[1]);

      const neighbors = [
        [cx + GRID_M, cy],
        [cx - GRID_M, cy],
        [cx, cy + GRID_M],
        [cx, cy - GRID_M]
      ];

      for (const [nx, ny] of neighbors) {
        const nKey = `${nx},${ny}`;
        if (pathTileMap.has(nKey) && !visited.has(nKey)) {
          visited.add(nKey);
          reachablePaths.add(nKey);
          queue.push(pathTileMap.get(nKey));
        }
      }
    }
  }

  let pathsConnected = true;
  for (const enc of layout.enclosures) {
    const gateKey = `${Math.round(enc.gate_position[0])},${Math.round(enc.gate_position[1])}`;
    if (!reachablePaths.has(gateKey)) {
      pathsConnected = false;
      break;
    }
  }
  for (const fac of layout.facilities) {
    const facPathKey = `${Math.round(fac.path_tile[0])},${Math.round(fac.path_tile[1])}`;
    if (!reachablePaths.has(facPathKey)) {
      pathsConnected = false;
      break;
    }
  }
  if (!pathsConnected) ruleFailures.path_connectivity++;

  // 3. Enclosure sizing & presence rule (must have enclosures >= 4, and dimensions >= expected tier)
  let sizingOk = true;
  if (layout.enclosures.length < 4) {
    sizingOk = false;
  } else {
    for (const enc of layout.enclosures) {
      const w = enc.bounds.width;
      const d = enc.bounds.depth;
      const animalMeta = assets ? assets.find(a => a.id === enc.species_id) : null;
      if (animalMeta && animalMeta.size_m) {
        const expected = getEnclosureSizeMeters(animalMeta.size_m);
        if (w < expected.width || d < expected.depth) {
          sizingOk = false;
          break;
        }
      } else if (w < 6 || d < 6) {
        sizingOk = false;
        break;
      }
    }
  }
  if (!sizingOk) ruleFailures.enclosure_sizing_and_presence++;

  // 4. Animals contained rule (pivot ± half animal length within enclosure bounds)
  let animalsContained = true;
  for (const enc of layout.enclosures) {
    const b = enc.bounds;
    const animalMeta = assets ? assets.find(a => a.id === enc.species_id) : null;
    const maxDim = (animalMeta && animalMeta.size_m) ? Math.max(animalMeta.size_m[0], animalMeta.size_m[1]) : 1.0;
    const halfLen = maxDim / 2;

    for (const an of enc.animals) {
      const [ax, ay, az] = an.position;
      if (
        (ax - halfLen) < b.min_x ||
        (ax + halfLen) > b.max_x ||
        (ay - halfLen) < b.min_y ||
        (ay + halfLen) > b.max_y ||
        az !== 0
      ) {
        animalsContained = false;
        break;
      }
    }
    if (!animalsContained) break;
  }
  if (!animalsContained) ruleFailures.animals_contained++;

  // 5. No overlapping footprints (enclosures, facilities, entrance, AND paths)
  let noOverlap = true;
  const boxes = [];

  boxes.push({
    type: 'entrance',
    minX: layout.entrance.position[0] - layout.entrance.footprint[0] / 2,
    minY: layout.entrance.position[1] - layout.entrance.footprint[1] / 2,
    maxX: layout.entrance.position[0] + layout.entrance.footprint[0] / 2,
    maxY: layout.entrance.position[1] + layout.entrance.footprint[1] / 2
  });

  for (const enc of layout.enclosures) {
    boxes.push({
      type: 'enclosure',
      minX: enc.bounds.min_x,
      minY: enc.bounds.min_y,
      maxX: enc.bounds.max_x,
      maxY: enc.bounds.max_y
    });
  }

  for (const fac of layout.facilities) {
    boxes.push({
      type: 'facility',
      minX: fac.position[0] - fac.footprint[0] / 2,
      minY: fac.position[1] - fac.footprint[1] / 2,
      maxX: fac.position[0] + fac.footprint[0] / 2,
      maxY: fac.position[1] + fac.footprint[1] / 2
    });
  }

  for (let j = 0; j < boxes.length; j++) {
    for (let k = j + 1; k < boxes.length; k++) {
      const b1 = boxes[j];
      const b2 = boxes[k];
      const overlap = !(b1.maxX <= b2.minX || b1.minX >= b2.maxX || b1.maxY <= b2.minY || b1.minY >= b2.maxY);
      if (overlap) {
        noOverlap = false;
        break;
      }
    }
    if (!noOverlap) break;
  }

  // Check that no path tile lies strictly inside any enclosure or facility
  if (noOverlap) {
    for (const pt of layout.paths) {
      const px = pt.position[0];
      const py = pt.position[1];

      for (const enc of layout.enclosures) {
        if (px > enc.bounds.min_x && px < enc.bounds.max_x && py > enc.bounds.min_y && py < enc.bounds.max_y) {
          noOverlap = false;
          break;
        }
      }
      if (!noOverlap) break;

      for (const fac of layout.facilities) {
        const minX = fac.position[0] - fac.footprint[0] / 2;
        const maxX = fac.position[0] + fac.footprint[0] / 2;
        const minY = fac.position[1] - fac.footprint[1] / 2;
        const maxY = fac.position[1] + fac.footprint[1] / 2;
        if (px > minX && px < maxX && py > minY && py < maxY) {
          noOverlap = false;
          break;
        }
      }
      if (!noOverlap) break;
    }
  }

  if (!noOverlap) ruleFailures.no_overlapping_footprints++;

  // 6. Facilities next to path
  let facNextToPath = true;
  for (const fac of layout.facilities) {
    const [px, py] = fac.path_tile;
    const pKey = `${Math.round(px)},${Math.round(py)}`;
    if (!pathTileMap.has(pKey)) {
      facNextToPath = false;
      break;
    }
    const distToFac = Math.hypot(fac.position[0] - px, fac.position[1] - py);
    const maxAllowedDist = Math.max(fac.footprint[0], fac.footprint[1]) + GRID_M;
    if (distToFac > maxAllowedDist) {
      facNextToPath = false;
      break;
    }
  }
  if (!facNextToPath) ruleFailures.facilities_next_to_path++;

  // 7. People on paths or near enclosures
  let peopleOk = true;
  for (const p of layout.people) {
    const [px, py, pz] = p.position;
    if (pz !== 0) {
      peopleOk = false;
      break;
    }

    const pgx = Math.floor(px / GRID_M);
    const pgy = Math.floor(py / GRID_M);
    const cellKey = `${pgx * GRID_M + GRID_M / 2},${pgy * GRID_M + GRID_M / 2}`;
    const onPath = pathTileMap.has(cellKey);

    let nearEnc = false;
    if (!onPath && p.near_enclosure_id) {
      const enc = layout.enclosures.find(e => e.id === p.near_enclosure_id);
      if (enc) {
        const d = Math.hypot(px - enc.gate_position[0], py - enc.gate_position[1]);
        if (d <= 3.0) nearEnc = true;
      }
    }

    if (!onPath && !nearEnc) {
      peopleOk = false;
      break;
    }
  }
  if (!peopleOk) ruleFailures.people_on_paths_or_near_enclosures++;

  // 8. Ground and boundary
  let groundAndBound = true;
  const bound = layout.boundary;
  function checkPos(pos) {
    const [x, y, z] = pos;
    if (z !== 0) return false;
    if (x < bound.min_x || x > bound.max_x || y < bound.min_y || y > bound.max_y) return false;
    return true;
  }

  if (!checkPos(layout.entrance.position)) groundAndBound = false;
  for (const pt of layout.paths) {
    if (!checkPos(pt.position)) { groundAndBound = false; break; }
  }
  for (const enc of layout.enclosures) {
    if (!checkPos(enc.center)) { groundAndBound = false; break; }
    for (const an of enc.animals) {
      if (!checkPos(an.position)) { groundAndBound = false; break; }
    }
  }
  for (const f of layout.facilities) {
    if (!checkPos(f.position)) { groundAndBound = false; break; }
  }
  for (const p of layout.people) {
    if (!checkPos(p.position)) { groundAndBound = false; break; }
  }
  if (!groundAndBound) ruleFailures.ground_and_boundary++;

  // 9. Every asset_id exists in assets.json
  if (knownAssetIds.size > 0) {
    let idsExist = true;
    const idsToCheck = [];
    idsToCheck.push(layout.entrance.asset_id);
    for (const enc of layout.enclosures) {
      idsToCheck.push(enc.fence_asset_id);
      for (const an of enc.animals) idsToCheck.push(an.asset_id);
    }
    for (const fac of layout.facilities) idsToCheck.push(fac.asset_id);
    for (const dec of layout.decorations) idsToCheck.push(dec.asset_id);
    for (const p of layout.people) idsToCheck.push(p.asset_id);

    for (const aid of idsToCheck) {
      if (!knownAssetIds.has(aid)) {
        idsExist = false;
        console.error(`Unknown asset_id in layout: ${aid}`);
        break;
      }
    }
    if (!idsExist) ruleFailures.asset_ids_exist++;
  }

  // 10. Every species present at max settings rule (size 600m, density 1.0)
  if (size_m === 600 && density === 1.0) {
    const totalSpecies = assets ? assets.filter(a => a.category === 'animals' && !a.variant_of && !a.id.endsWith('_baby') && !a.id.endsWith('_rare')).length : 130;
    const speciesInLayout = new Set(layout.enclosures.map(e => e.species_id));
    if (speciesInLayout.size < totalSpecies) {
      ruleFailures.every_species_at_max_settings++;
      console.error(`Max settings layout missed species: placed ${speciesInLayout.size} of ${totalSpecies}`);
    }
  }
}

const avgMs = (timings.reduce((a, b) => a + b, 0) / timings.length).toFixed(2);
const minMs = Math.min(...timings).toFixed(2);
const maxMs = Math.max(...timings).toFixed(2);
const totalMs = timings.reduce((a, b) => a + b, 0).toFixed(1);

const minEnc = Math.min(...enclosureCounts);
const maxEnc = Math.max(...enclosureCounts);
const avgEnc = (enclosureCounts.reduce((a, b) => a + b, 0) / enclosureCounts.length).toFixed(1);

const minAni = Math.min(...animalCounts);
const maxAni = Math.max(...animalCounts);
const avgAni = (animalCounts.reduce((a, b) => a + b, 0) / animalCounts.length).toFixed(1);

console.log('--- Layout Rules Verification Report (200 seeds) ---');
let allPassed = true;
for (const [rule, failCount] of Object.entries(ruleFailures)) {
  const status = failCount === 0 ? 'PASS' : `FAIL (${failCount} failures)`;
  if (failCount > 0) allPassed = false;
  console.log(`• Rule [${rule}]: ${status}`);
}

console.log('\n--- Content Distribution (across 200 seeds) ---');
console.log(`• Enclosures: min=${minEnc}, avg=${avgEnc}, max=${maxEnc}`);
console.log(`• Animals:    min=${minAni}, avg=${avgAni}, max=${maxAni}`);

console.log('\n--- Performance Timing ---');
console.log(`• Average generation time: ${avgMs} ms / layout`);
console.log(`• Min / Max time: ${minMs} ms / ${maxMs} ms`);
console.log(`• Total time for 200 layouts: ${totalMs} ms`);

if (allPassed) {
  console.log('\nRESULT: All rules pass for all 200.');
  process.exit(0);
} else {
  console.error('\nRESULT: Verification FAILED.');
  process.exit(1);
}
