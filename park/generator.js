/**
 * Procedural Zoo Map Generator (Pure JS, no DOM)
 * 
 * Generates a complete zoo layout conforming to park/layout.schema.json.
 * Strict adherence to 2m metric grid, bottom-center pivot, deterministic PRNG.
 */

export const GRID_M = 2; // Metric grid cell size in meters
export const EDGE_DEPTH_M = 0.5;
export const TOL_M = 0.001; // 1 mm tolerance

// Deterministic PRNG: Mulberry32
function createPRNG(seed) {
  let s = 0;
  if (typeof seed === 'number') {
    s = seed >>> 0;
  } else {
    // Hash string to 32-bit int
    const str = String(seed);
    for (let i = 0; i < str.length; i++) {
      s = (Math.imul(31, s) + str.charCodeAt(i)) >>> 0;
    }
  }
  if (s === 0) s = 1337;

  return function next() {
    s = (s + 0x6D2B79F5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Built-in catalog of common zoo animals and their real-world dimensions
const DEFAULT_ANIMALS = [
  { id: 'african_elephant', name: 'African elephant', size_m: [1.8, 5.5, 3.2] },
  { id: 'asian_elephant', name: 'Asian elephant', size_m: [1.6, 5.0, 2.7] },
  { id: 'giraffe', name: 'Giraffe', size_m: [1.0, 4.0, 5.2] },
  { id: 'hippo', name: 'Hippo', size_m: [1.5, 4.2, 1.5] },
  { id: 'white_rhino', name: 'White rhino', size_m: [1.4, 3.8, 1.8] },
  { id: 'lion', name: 'Lion', size_m: [0.9, 2.1, 1.2] },
  { id: 'bengal_tiger', name: 'Bengal tiger', size_m: [0.9, 2.4, 1.1] },
  { id: 'zebra', name: 'Plains zebra', size_m: [0.8, 2.3, 1.4] },
  { id: 'grizzly_bear', name: 'Grizzly bear', size_m: [1.0, 2.2, 1.3] },
  { id: 'polar_bear', name: 'Polar bear', size_m: [1.1, 2.5, 1.4] },
  { id: 'western_gorilla', name: 'Western gorilla', size_m: [0.9, 1.1, 1.7] },
  { id: 'chimpanzee', name: 'Chimpanzee', size_m: [0.7, 0.9, 1.2] },
  { id: 'grey_wolf', name: 'Grey wolf', size_m: [0.5, 1.4, 0.8] },
  { id: 'red_kangaroo', name: 'Red kangaroo', size_m: [0.7, 1.5, 1.6] },
  { id: 'giant_panda', name: 'Giant panda', size_m: [0.8, 1.6, 0.9] },
  { id: 'snow_leopard', name: 'Snow leopard', size_m: [0.6, 1.8, 0.6] },
  { id: 'cheetah', name: 'Cheetah', size_m: [0.6, 1.9, 0.8] },
  { id: 'ostrich', name: 'Ostrich', size_m: [0.9, 1.6, 2.4] },
  { id: 'emperor_penguin', name: 'Emperor penguin', size_m: [0.4, 0.4, 1.1] },
  { id: 'flamingo', name: 'Greater flamingo', size_m: [0.4, 0.6, 1.3] },
  { id: 'nile_crocodile', name: 'Nile crocodile', size_m: [0.9, 4.5, 0.6] },
  { id: 'komodo_dragon', name: 'Komodo dragon', size_m: [0.6, 2.6, 0.5] },
  { id: 'galapagos_tortoise', name: 'Galapagos tortoise', size_m: [0.9, 1.2, 0.7] },
  { id: 'meerkat', name: 'Meerkat', size_m: [0.15, 0.3, 0.3] },
  { id: 'red_panda', name: 'Red panda', size_m: [0.3, 0.6, 0.4] },
  { id: 'ring_tailed_lemur', name: 'Ring-tailed lemur', size_m: [0.3, 0.5, 0.45] },
  { id: 'koala', name: 'Koala', size_m: [0.4, 0.4, 0.7] },
  { id: 'bald_eagle', name: 'Bald eagle', size_m: [0.5, 0.9, 0.9] },
  { id: 'poison_dart_frog', name: 'Poison dart frog', size_m: [0.06, 0.06, 0.04] },
  { id: 'chameleon', name: 'Chameleon', size_m: [0.1, 0.45, 0.2] }
];

const DEFAULT_FACILITIES = [
  { id: 'kiosk_ice_cream', category: 'food', footprint: [4, 4] },
  { id: 'kiosk_drinks', category: 'food', footprint: [4, 4] },
  { id: 'kiosk_burgers', category: 'food', footprint: [4, 4] },
  { id: 'restroom_small', category: 'facilities', footprint: [4, 4] },
  { id: 'restroom_large', category: 'facilities', footprint: [6, 4] },
  { id: 'gift_shop_small', category: 'shop', footprint: [6, 4] },
  { id: 'info_kiosk', category: 'facilities', footprint: [2, 2] },
  { id: 'first_aid_station', category: 'facilities', footprint: [4, 4] },
  { id: 'bench_wood_straight', category: 'benches_lamps_bins_signs', footprint: [2, 2] },
  { id: 'trash_bin_wood', category: 'benches_lamps_bins_signs', footprint: [2, 2] },
  { id: 'park_lamp_post', category: 'benches_lamps_bins_signs', footprint: [2, 2] }
];

const DEFAULT_DECORATIONS = [
  { id: 'tree_oak_medium' },
  { id: 'tree_pine_tall' },
  { id: 'tree_acacia' },
  { id: 'bush_flowering' },
  { id: 'rock_boulder_cluster' },
  { id: 'flower_bed_circular' }
];

const DEFAULT_KEEPERS = [
  'keeper_m_uniform_khaki',
  'keeper_f_uniform_green',
  'keeper_m_tools_rake',
  'keeper_f_bucket'
];

const DEFAULT_VISITORS = [
  'visitor_man_casual',
  'visitor_woman_summer',
  'visitor_child_boy',
  'visitor_child_girl',
  'visitor_tourist_camera'
];

/**
 * Compute minimum enclosure dimension in meters from animal max dimension.
 * Ensures animals have sufficient roaming area while adhering to 2m grid multiples.
 */
export function getEnclosureSizeMeters(size_m) {
  const maxDim = Math.max(...size_m);
  let dim;
  if (maxDim >= 4.0) {
    dim = 24; // Elephants, giraffes, hippos
  } else if (maxDim >= 2.0) {
    dim = 18; // Rhinos, tigers, lions, bears, zebras
  } else if (maxDim >= 1.0) {
    dim = 14; // Kangaroos, primates, wolves
  } else if (maxDim >= 0.4) {
    dim = 10; // Penguins, tortoises, lemurs
  } else {
    dim = 6;  // Small reptiles, frogs, insects
  }
  return { width: dim, depth: dim };
}

/**
 * Procedurally generates a complete zoo layout
 * 
 * @param {Object} settings
 * @param {number} settings.size_m - Park dimension in meters (80 to 600)
 * @param {number} settings.density - Asset density (0 to 1)
 * @param {number} settings.population - Visitor/keeper population (0 to 300)
 * @param {string|number} settings.seed - PRNG seed
 * @param {Object} [options] - Optional custom asset lists
 */
export function generateLayout(settings, options = {}) {
  const startTime = Date.now();

  const size_m = Math.max(80, Math.min(600, Math.round((settings.size_m || 160) / GRID_M) * GRID_M));
  const density = Math.max(0, Math.min(1, typeof settings.density === 'number' ? settings.density : 0.5));
  const population = Math.max(0, Math.min(300, Math.round(settings.population !== undefined ? settings.population : 50)));
  const seed = settings.seed !== undefined ? settings.seed : 42;

  const rand = createPRNG(seed);

  const animalCatalog = (options.assets && options.assets.filter(a => a.category === 'animals')) || DEFAULT_ANIMALS;
  const facilityCatalog = DEFAULT_FACILITIES;
  const decorCatalog = DEFAULT_DECORATIONS;
  const keeperCatalog = DEFAULT_KEEPERS;
  const visitorCatalog = DEFAULT_VISITORS;

  const gridCells = Math.floor(size_m / GRID_M);

  // Cell types: 0=empty, 1=path, 2=entrance, 3=enclosure, 4=facility, 5=decor
  const OCC_EMPTY = 0;
  const OCC_PATH = 1;
  const OCC_ENTRANCE = 2;
  const OCC_ENCLOSURE = 3;
  const OCC_FACILITY = 4;
  const OCC_DECOR = 5;

  const occ = new Uint8Array(gridCells * gridCells);

  function cellIdx(gx, gy) {
    return gy * gridCells + gx;
  }

  function isCellValid(gx, gy) {
    return gx >= 0 && gx < gridCells && gy >= 0 && gy < gridCells;
  }

  function getCell(gx, gy) {
    if (!isCellValid(gx, gy)) return 255;
    return occ[cellIdx(gx, gy)];
  }

  function setCell(gx, gy, val) {
    if (isCellValid(gx, gy)) {
      occ[cellIdx(gx, gy)] = val;
    }
  }

  function isRegionFree(gx, gy, gw, gh) {
    if (gx < 0 || gy < 0 || gx + gw > gridCells || gy + gh > gridCells) return false;
    for (let dy = 0; dy < gh; dy++) {
      for (let dx = 0; dx < gw; dx++) {
        if (occ[cellIdx(gx + dx, gy + dy)] !== OCC_EMPTY) return false;
      }
    }
    return true;
  }

  function markRegion(gx, gy, gw, gh, val) {
    for (let dy = 0; dy < gh; dy++) {
      for (let dx = 0; dx < gw; dx++) {
        setCell(gx + dx, gy + dy, val);
      }
    }
  }

  // 1. Entrance on South boundary (centered on X, at bottom Y=0)
  const entranceWidthM = 4;
  const entranceDepthM = 2;
  const entranceGW = Math.round(entranceWidthM / GRID_M);
  const entranceGH = Math.round(entranceDepthM / GRID_M);
  const entranceGX = Math.floor((gridCells - entranceGW) / 2);
  const entranceGY = 0;

  markRegion(entranceGX, entranceGY, entranceGW, entranceGH, OCC_ENTRANCE);

  const entrance = {
    id: 'entrance_main',
    asset_id: 'gate_archway_main',
    position: [
      (entranceGX + entranceGW / 2) * GRID_M,
      (entranceGY + entranceGH / 2) * GRID_M,
      0
    ],
    rotation_deg: 0,
    footprint: [entranceWidthM, entranceDepthM]
  };

  // 2. Arterial Path Network
  // Main spine road moving North from entrance to North boundary (minus margin)
  const spineGX = entranceGX + Math.floor(entranceGW / 2);
  const pathSet = new Set();

  function addPathCell(gx, gy) {
    if (isCellValid(gx, gy)) {
      if (getCell(gx, gy) === OCC_EMPTY) {
        setCell(gx, gy, OCC_PATH);
      }
      pathSet.add(`${gx},${gy}`);
    }
  }

  // Entrance approach paths
  for (let dy = 0; dy <= entranceGH; dy++) {
    addPathCell(spineGX, entranceGY + dy);
    if (entranceGW > 1) addPathCell(spineGX - 1, entranceGY + dy);
  }

  // Central spine
  const northBoundGY = gridCells - 4;
  for (let gy = entranceGY + entranceGH; gy <= northBoundGY; gy++) {
    addPathCell(spineGX, gy);
  }

  // Cross avenues spaced regularly across the grid
  const avenueSpacingCells = Math.max(8, Math.floor(gridCells / (3 + Math.floor(density * 4))));
  const avenueYList = [];
  for (let gy = 4; gy <= northBoundGY; gy += avenueSpacingCells) {
    avenueYList.push(gy);
    const minX = 4;
    const maxX = gridCells - 5;
    for (let gx = minX; gx <= maxX; gx++) {
      addPathCell(gx, gy);
    }
  }

  // Outer ring side paths connecting avenues at East and West
  for (const gy of avenueYList) {
    const minX = 4;
    const maxX = gridCells - 5;
    for (let y = avenueYList[0]; y <= avenueYList[avenueYList.length - 1]; y++) {
      addPathCell(minX, y);
      addPathCell(maxX, y);
    }
  }

  // 3. Enclosure Placement
  // Determine number of enclosures based on density and size
  const maxPossibleEnc = Math.floor((gridCells * gridCells) / (12 * 12));
  const targetEncCount = Math.max(4, Math.min(Math.min(maxPossibleEnc, animalCatalog.length), Math.floor(4 + density * 40)));

  // Shuffle animals deterministically
  const animalsShuffled = [...animalCatalog];
  for (let i = animalsShuffled.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [animalsShuffled[i], animalsShuffled[j]] = [animalsShuffled[j], animalsShuffled[i]];
  }

  const enclosures = [];

  // Try placing enclosures adjacent to path avenues
  for (let i = 0; i < animalsShuffled.length && enclosures.length < targetEncCount; i++) {
    const animal = animalsShuffled[i];
    const encSize = getEnclosureSizeMeters(animal.size_m);
    const encGW = Math.round(encSize.width / GRID_M);
    const encGH = Math.round(encSize.depth / GRID_M);

    let placed = false;
    let attempts = 0;

    while (!placed && attempts < 80) {
      attempts++;
      // Pick an avenue and a side (North or South of avenue)
      const avY = avenueYList[Math.floor(rand() * avenueYList.length)];
      const onNorth = rand() > 0.5;
      
      const encGY = onNorth ? avY + 1 : avY - 1 - encGH;
      const minGX = 4;
      const maxGX = gridCells - 4 - encGW;
      if (maxGX <= minGX) continue;

      const encGX = minGX + Math.floor(rand() * ((maxGX - minGX) / 2)) * 2;

      // Check if region (including 1-cell border margin) is free
      if (isRegionFree(encGX - 1, encGY - 1, encGW + 2, encGH + 2)) {
        // Enclosure footprint must be adjacent to at least one path tile
        let hasPathAdj = false;
        let gateGX = encGX + Math.floor(encGW / 2);
        let gateGY = onNorth ? encGY : encGY + encGH - 1;

        // Check if adjacent row is path
        const adjPathY = onNorth ? encGY - 1 : encGY + encGH;
        if (isCellValid(gateGX, adjPathY) && getCell(gateGX, adjPathY) === OCC_PATH) {
          hasPathAdj = true;
        }

        if (hasPathAdj) {
          markRegion(encGX, encGY, encGW, encGH, OCC_ENCLOSURE);

          const minXM = encGX * GRID_M;
          const minYM = encGY * GRID_M;
          const widthM = encGW * GRID_M;
          const depthM = encGH * GRID_M;
          const maxXM = minXM + widthM;
          const maxYM = minYM + depthM;
          const centerXM = minXM + widthM / 2;
          const centerYM = minYM + depthM / 2;

          const gatePos = [gateGX * GRID_M + GRID_M / 2, adjPathY * GRID_M + GRID_M / 2, 0];

          // Spawn animal instances inside enclosure bounds
          const animalInstances = [];
          const animalCount = 1 + (density > 0.4 ? Math.floor(rand() * 2) : 0);

          for (let aIdx = 0; aIdx < animalCount; aIdx++) {
            const isAdult = aIdx === 0;
            const isBaby = !isAdult && aIdx === 1 && rand() > 0.4;
            const isMutation = !isAdult && !isBaby && rand() > 0.7;

            const variant = isAdult ? 'adult' : (isBaby ? 'baby' : (isMutation ? 'mutation' : 'adult'));
            const marginM = 1.5;
            const posX = minXM + marginM + rand() * (widthM - 2 * marginM);
            const posY = minYM + marginM + rand() * (depthM - 2 * marginM);

            animalInstances.push({
              id: `${animal.id}_${enclosures.length + 1}_${aIdx + 1}`,
              asset_id: animal.id,
              variant: variant,
              position: [Math.round(posX * 100) / 100, Math.round(posY * 100) / 100, 0],
              rotation_deg: Math.round(rand() * 360)
            });
          }

          enclosures.push({
            id: `enclosure_${animal.id}_${enclosures.length + 1}`,
            species_id: animal.id,
            name: `${animal.name} Habitat`,
            bounds: {
              min_x: minXM,
              min_y: minYM,
              max_x: maxXM,
              max_y: maxYM,
              width: widthM,
              depth: depthM
            },
            center: [centerXM, centerYM, 0],
            fence_asset_id: 'fence_wood_rail_straight',
            gate_position: gatePos,
            animals: animalInstances
          });

          placed = true;
        }
      }
    }
  }

  // 4. Facility Placement (adjacent to paths)
  const facilities = [];
  const targetFacilityCount = Math.max(6, Math.floor(4 + density * 24));
  const pathTileArray = Array.from(pathSet).map(s => s.split(',').map(Number));

  let facAttempts = 0;
  while (facilities.length < targetFacilityCount && facAttempts < 300) {
    facAttempts++;
    const pathTile = pathTileArray[Math.floor(rand() * pathTileArray.length)];
    const ptGX = pathTile[0];
    const ptGY = pathTile[1];

    const facTemplate = facilityCatalog[Math.floor(rand() * facilityCatalog.length)];
    const facGW = Math.round(facTemplate.footprint[0] / GRID_M);
    const facGH = Math.round(facTemplate.footprint[1] / GRID_M);

    // Try 4 cardinal directions adjacent to this path tile
    const directions = [
      { dx: 1, dy: 0 },
      { dx: -facGW, dy: 0 },
      { dx: 0, dy: 1 },
      { dx: 0, dy: -facGH }
    ];

    const dir = directions[Math.floor(rand() * directions.length)];
    const targetGX = ptGX + dir.dx;
    const targetGY = ptGY + dir.dy;

    if (isRegionFree(targetGX, targetGY, facGW, facGH)) {
      markRegion(targetGX, targetGY, facGW, facGH, OCC_FACILITY);

      const fXM = (targetGX + facGW / 2) * GRID_M;
      const fYM = (targetGY + facGH / 2) * GRID_M;

      facilities.push({
        id: `facility_${facTemplate.id}_${facilities.length + 1}`,
        asset_id: facTemplate.id,
        category: facTemplate.category,
        position: [fXM, fYM, 0],
        rotation_deg: (Math.floor(rand() * 4) * 90),
        footprint: [facTemplate.footprint[0], facTemplate.footprint[1]],
        path_tile: [ptGX * GRID_M + GRID_M / 2, ptGY * GRID_M + GRID_M / 2]
      });
    }
  }

  // 5. Decorations (trees, rocks, flowers in empty spots)
  const decorations = [];
  const targetDecorCount = Math.floor(10 + density * 50);
  let decorAttempts = 0;
  while (decorations.length < targetDecorCount && decorAttempts < 200) {
    decorAttempts++;
    const dgx = 2 + Math.floor(rand() * (gridCells - 4));
    const dgy = 2 + Math.floor(rand() * (gridCells - 4));

    if (getCell(dgx, dgy) === OCC_EMPTY) {
      setCell(dgx, dgy, OCC_DECOR);
      const decTemplate = decorCatalog[Math.floor(rand() * decorCatalog.length)];
      decorations.push({
        id: `decor_${decTemplate.id}_${decorations.length + 1}`,
        asset_id: decTemplate.id,
        position: [dgx * GRID_M + GRID_M / 2, dgy * GRID_M + GRID_M / 2, 0],
        rotation_deg: Math.round(rand() * 360),
        scale: Math.round((0.85 + rand() * 0.3) * 100) / 100
      });
    }
  }

  // 6. People (Visitors and Keepers)
  const people = [];
  const keeperCount = Math.max(1, Math.min(25, Math.round(population * 0.15)));
  const visitorCount = population - keeperCount;

  // Spawn keepers near enclosures and facilities
  for (let k = 0; k < keeperCount; k++) {
    const kAsset = keeperCatalog[Math.floor(rand() * keeperCatalog.length)];
    let pos;
    let encId = null;

    if (enclosures.length > 0 && rand() > 0.3) {
      const enc = enclosures[Math.floor(rand() * enclosures.length)];
      encId = enc.id;
      // Positioned on path at enclosure gate
      pos = [
        enc.gate_position[0] + (rand() - 0.5) * 0.6,
        enc.gate_position[1] + (rand() - 0.5) * 0.6,
        0
      ];
    } else {
      const pt = pathTileArray[Math.floor(rand() * pathTileArray.length)];
      pos = [
        pt[0] * GRID_M + GRID_M / 2 + (rand() - 0.5) * 0.8,
        pt[1] * GRID_M + GRID_M / 2 + (rand() - 0.5) * 0.8,
        0
      ];
    }

    people.push({
      id: `person_keeper_${k + 1}`,
      asset_id: kAsset,
      role: 'keeper',
      position: [Math.round(pos[0] * 100) / 100, Math.round(pos[1] * 100) / 100, 0],
      rotation_deg: Math.round(rand() * 360),
      near_enclosure_id: encId
    });
  }

  // Spawn visitors along paths, especially viewing enclosures
  for (let v = 0; v < visitorCount; v++) {
    const vAsset = visitorCatalog[Math.floor(rand() * visitorCatalog.length)];
    let pos;
    let encId = null;

    if (enclosures.length > 0 && rand() > 0.4) {
      const enc = enclosures[Math.floor(rand() * enclosures.length)];
      encId = enc.id;
      // Positioned near enclosure gate / viewing path
      pos = [
        enc.gate_position[0] + (rand() - 0.5) * 1.2,
        enc.gate_position[1] + (rand() - 0.5) * 1.2,
        0
      ];
    } else {
      const pt = pathTileArray[Math.floor(rand() * pathTileArray.length)];
      pos = [
        pt[0] * GRID_M + GRID_M / 2 + (rand() - 0.5) * 1.0,
        pt[1] * GRID_M + GRID_M / 2 + (rand() - 0.5) * 1.0,
        0
      ];
    }

    people.push({
      id: `person_visitor_${v + 1}`,
      asset_id: vAsset,
      role: 'visitor',
      position: [Math.round(pos[0] * 100) / 100, Math.round(pos[1] * 100) / 100, 0],
      rotation_deg: Math.round(rand() * 360),
      near_enclosure_id: encId
    });
  }

  // 7. Format Path Tiles
  const pathTiles = [];
  for (const pKey of pathSet) {
    const [pgx, pgy] = pKey.split(',').map(Number);
    const conns = [];
    if (pathSet.has(`${pgx},${pgy + 1}`)) conns.push('north');
    if (pathSet.has(`${pgx},${pgy - 1}`)) conns.push('south');
    if (pathSet.has(`${pgx + 1},${pgy}`)) conns.push('east');
    if (pathSet.has(`${pgx - 1},${pgy}`)) conns.push('west');

    pathTiles.push({
      id: `path_${pgx}_${pgy}`,
      position: [pgx * GRID_M + GRID_M / 2, pgy * GRID_M + GRID_M / 2, 0],
      size: [GRID_M, GRID_M],
      connections: conns
    });
  }

  const endTime = Date.now();
  const generationTimeMs = Math.max(1, endTime - startTime);

  let totalAnimals = 0;
  for (const e of enclosures) {
    totalAnimals += e.animals.length;
  }

  return {
    version: '1.0.0',
    settings: {
      size_m: size_m,
      density: density,
      population: population,
      seed: seed
    },
    boundary: {
      width_m: size_m,
      depth_m: size_m,
      min_x: 0,
      min_y: 0,
      max_x: size_m,
      max_y: size_m
    },
    entrance: entrance,
    paths: pathTiles,
    enclosures: enclosures,
    facilities: facilities,
    decorations: decorations,
    people: people,
    stats: {
      enclosure_count: enclosures.length,
      facility_count: facilities.length,
      animal_count: totalAnimals,
      visitor_count: visitorCount,
      keeper_count: keeperCount,
      path_tile_count: pathTiles.length,
      generation_time_ms: generationTimeMs
    }
  };
}
