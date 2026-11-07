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

// Built-in catalog of real zoo animals from assets.json and their dimensions
const DEFAULT_ANIMALS = [
  { id: 'african_elephant', name: 'African elephant', size_m: [1.8, 5.5, 3.2] },
  { id: 'asian_elephant', name: 'Asian elephant', size_m: [1.6, 5.0, 2.7] },
  { id: 'white_rhino', name: 'White rhino', size_m: [1.4, 3.8, 1.8] },
  { id: 'indian_rhino', name: 'Indian rhino', size_m: [1.5, 3.5, 1.7] },
  { id: 'hippo', name: 'Hippo', size_m: [1.5, 4.2, 1.5] },
  { id: 'lion', name: 'Lion', size_m: [0.9, 2.1, 1.2] },
  { id: 'bengal_tiger', name: 'Bengal tiger', size_m: [0.9, 2.4, 1.1] },
  { id: 'plains_zebra', name: 'Plains zebra', size_m: [0.8, 2.3, 1.4] },
  { id: 'brown_bear', name: 'Brown bear', size_m: [1.0, 2.2, 1.3] },
  { id: 'polar_bear', name: 'Polar bear', size_m: [1.1, 2.5, 1.4] },
  { id: 'western_gorilla', name: 'Western gorilla', size_m: [0.9, 1.1, 1.7] },
  { id: 'chimpanzee', name: 'Chimpanzee', size_m: [0.7, 0.9, 1.2] },
  { id: 'grey_wolf', name: 'Grey wolf', size_m: [0.5, 1.4, 0.8] },
  { id: 'red_kangaroo', name: 'Red kangaroo', size_m: [0.7, 1.5, 1.6] },
  { id: 'giant_panda', name: 'Giant panda', size_m: [0.8, 1.6, 0.9] },
  { id: 'snow_leopard', name: 'Snow leopard', size_m: [0.6, 1.8, 0.6] },
  { id: 'cheetah', name: 'Cheetah', size_m: [0.6, 1.9, 0.8] },
  { id: 'ostrich', name: 'Ostrich', size_m: [0.9, 1.6, 2.4] },
  { id: 'african_penguin', name: 'African penguin', size_m: [0.35, 0.35, 0.65] },
  { id: 'greater_flamingo', name: 'Greater flamingo', size_m: [0.4, 0.6, 1.3] },
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
  { id: 'kiosk_ice_cream', category: 'facilities', footprint: [4, 4] },
  { id: 'kiosk_beverage_bar', category: 'facilities', footprint: [4, 4] },
  { id: 'kiosk_pretzel_snack', category: 'facilities', footprint: [4, 4] },
  { id: 'kiosk_souvenir_stand', category: 'facilities', footprint: [4, 4] },
  { id: 'booth_visitor_info', category: 'facilities', footprint: [4, 4] },
  { id: 'building_public_restroom', category: 'facilities', footprint: [6, 4] },
  { id: 'building_first_aid_station', category: 'facilities', footprint: [4, 4] },
  { id: 'bench_park_wood_classic', category: 'benches_lamps_bins_signs', footprint: [2, 2] },
  { id: 'bin_waste_general_timber', category: 'benches_lamps_bins_signs', footprint: [2, 2] },
  { id: 'lamp_post_victorian_single', category: 'benches_lamps_bins_signs', footprint: [2, 2] }
];

const DEFAULT_DECORATIONS = [
  { id: 'acacia_tree' },
  { id: 'oak_tree' },
  { id: 'pine_tree' },
  { id: 'boulder_medium' },
  { id: 'boulder_large' },
  { id: 'sandstone_boulder' },
  { id: 'flag_pole' },
  { id: 'patio_umbrella' }
];

const DEFAULT_KEEPERS = [
  'keeper_safari_lead_01',
  'keeper_carnivore_specialist_02',
  'keeper_aquatic_feeder_03',
  'keeper_primate_caregiver_04',
  'keeper_vet_surgeon_05'
];

const DEFAULT_VISITORS = [
  'visitor_tourist_camera_01',
  'visitor_tourist_sunhat_02',
  'visitor_child_balloon_03',
  'visitor_child_icecream_04',
  'visitor_child_cap_05'
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

  const allAssets = options.assets || null;
  const assetIdSet = new Set(allAssets ? allAssets.map(a => a.id) : []);

  const animalCatalog = (allAssets ? allAssets.filter(a => a.category === 'animals' && !a.variant_of) : null) || DEFAULT_ANIMALS;

  const facilityCatalog = (allAssets ? allAssets.filter(a =>
    (a.category === 'facilities' && (a.id.startsWith('kiosk_') || a.id.startsWith('building_') || a.id.startsWith('booth_') || a.id.startsWith('pavilion_'))) ||
    (a.category === 'benches_lamps_bins_signs')
  ).map(a => ({
    id: a.id,
    category: a.category,
    footprint: [
      Math.max(2, Math.round(a.size_m[0] / GRID_M) * GRID_M),
      Math.max(2, Math.round(a.size_m[1] / GRID_M) * GRID_M)
    ]
  })) : null) || DEFAULT_FACILITIES;

  const decorCatalog = (allAssets ? allAssets.filter(a =>
    (a.category === 'plants' || a.category === 'landscape' || a.category === 'decor') && !a.id.includes('bunting')
  ).map(a => ({ id: a.id })) : null) || DEFAULT_DECORATIONS;

  const keeperCatalog = (allAssets ? allAssets.filter(a => a.category === 'keepers').map(a => a.id) : null) || DEFAULT_KEEPERS;
  const visitorCatalog = (allAssets ? allAssets.filter(a => a.category === 'visitors').map(a => a.id) : null) || DEFAULT_VISITORS;

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
    if (gx < 2 || gy < 2 || gx + gw > gridCells - 2 || gy + gh > gridCells - 2) return false;
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
  const entranceWidthM = 6;
  const entranceDepthM = 2;
  const entranceGW = Math.round(entranceWidthM / GRID_M);
  const entranceGH = Math.round(entranceDepthM / GRID_M);
  const entranceGX = Math.floor((gridCells - entranceGW) / 2);
  const entranceGY = 0;

  markRegion(entranceGX, entranceGY, entranceGW, entranceGH, OCC_ENTRANCE);

  const entrance = {
    id: 'entrance_main',
    asset_id: 'gate_entrance_arch_grand',
    position: [
      (entranceGX + entranceGW / 2) * GRID_M,
      (entranceGY + entranceGH / 2) * GRID_M,
      0
    ],
    rotation_deg: 0,
    footprint: [entranceWidthM, entranceDepthM]
  };

  // 2. Arterial Path Network
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

  // Central spine road moving North
  const northBoundGY = gridCells - 4;
  for (let gy = entranceGY + entranceGH; gy <= northBoundGY; gy++) {
    addPathCell(spineGX, gy);
  }

  // Cross avenues spaced regularly so enclosures fit cleanly between them
  const avenueSpacingCells = Math.max(16, Math.floor(gridCells / (2 + Math.floor(density * 3))));
  const avenueYList = [];
  for (let gy = 6; gy <= northBoundGY - 6; gy += avenueSpacingCells) {
    avenueYList.push(gy);
    const minX = 4;
    const maxX = gridCells - 5;
    for (let gx = minX; gx <= maxX; gx++) {
      addPathCell(gx, gy);
    }
  }
  if (avenueYList.length === 0) {
    const midY = Math.floor(gridCells / 2);
    avenueYList.push(midY);
    for (let gx = 4; gx <= gridCells - 5; gx++) addPathCell(gx, midY);
  }

  // 3. Enclosure Placement
  // When park is large and density is high, scale up to all available animal species
  const maxForSize = Math.min(
    animalCatalog.length,
    Math.floor(4 + ((size_m - 80) / 520) * (animalCatalog.length - 4))
  );
  const targetEncCount = Math.max(4, Math.min(animalCatalog.length, Math.round(4 + density * (maxForSize - 4))));

  // Deterministic shuffle of animals
  const animalsShuffled = [...animalCatalog];
  for (let i = animalsShuffled.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [animalsShuffled[i], animalsShuffled[j]] = [animalsShuffled[j], animalsShuffled[i]];
  }

  const enclosures = [];

  // Try placing enclosures adjacent to path avenues and spine
  for (let i = 0; i < animalsShuffled.length && enclosures.length < targetEncCount; i++) {
    const animal = animalsShuffled[i];
    const encSize = getEnclosureSizeMeters(animal.size_m);
    const encGW = Math.round(encSize.width / GRID_M);
    const encGH = Math.round(encSize.depth / GRID_M);

    let placed = false;
    let attempts = 0;

    while (!placed && attempts < 300) {
      attempts++;
      const avY = avenueYList[Math.floor(rand() * avenueYList.length)];
      const onNorth = rand() > 0.5;

      const encGY = onNorth ? avY + 1 : avY - encGH;
      const minGX = 4;
      const maxGX = gridCells - 4 - encGW;
      if (maxGX <= minGX) continue;

      const encGX = minGX + Math.floor(rand() * (maxGX - minGX));

      if (isRegionFree(encGX, encGY, encGW, encGH)) {
        // Enclosure footprint must be adjacent to at least one path tile
        const adjPathY = onNorth ? encGY - 1 : encGY + encGH;
        let gateGX = encGX + Math.floor(encGW / 2);

        // Find path tile on adjacent row
        let hasAdjPath = false;
        for (let gx = encGX; gx < encGX + encGW; gx++) {
          if (getCell(gx, adjPathY) === OCC_PATH) {
            gateGX = gx;
            hasAdjPath = true;
            break;
          }
        }

        if (hasAdjPath) {
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
          const maxAnimalDim = Math.max(animal.size_m[0], animal.size_m[1]);
          const halfAnimalLen = maxAnimalDim / 2;
          const animalMargin = halfAnimalLen + 0.5;

          const hasBaby = assetIdSet.has(`${animal.id}_baby`);
          const hasRare = assetIdSet.has(`${animal.id}_rare`);

          // Adult primary instance
          const adultX = minXM + animalMargin + rand() * Math.max(0.1, widthM - 2 * animalMargin);
          const adultY = minYM + animalMargin + rand() * Math.max(0.1, depthM - 2 * animalMargin);

          animalInstances.push({
            id: `${animal.id}_${enclosures.length + 1}_1`,
            asset_id: animal.id,
            variant: 'adult',
            position: [Math.round(adultX * 100) / 100, Math.round(adultY * 100) / 100, 0],
            rotation_deg: Math.round(rand() * 360)
          });

          // Helper to spawn companion instance nearby within safe enclosure bounds
          const spawnNearby = (assetId, variantType, idx) => {
            const spreadX = Math.min(3.5, Math.max(0.5, (widthM - 2 * animalMargin) / 3));
            const spreadY = Math.min(3.5, Math.max(0.5, (depthM - 2 * animalMargin) / 3));
            const offsetX = (rand() - 0.5) * spreadX * 2;
            const offsetY = (rand() - 0.5) * spreadY * 2;
            const posX = Math.max(minXM + animalMargin, Math.min(maxXM - animalMargin, adultX + offsetX));
            const posY = Math.max(minYM + animalMargin, Math.min(maxYM - animalMargin, adultY + offsetY));
            animalInstances.push({
              id: `${animal.id}_${enclosures.length + 1}_${idx}`,
              asset_id: assetId,
              variant: variantType,
              position: [Math.round(posX * 100) / 100, Math.round(posY * 100) / 100, 0],
              rotation_deg: Math.round(rand() * 360)
            });
          };

          let instIdx = 2;
          // Spawn babies and rare mutations next to adults when variants exist
          if (hasBaby && (density > 0.25 || density >= 1.0)) {
            spawnNearby(`${animal.id}_baby`, 'baby', instIdx++);
          }
          if (hasRare && (density > 0.5 || density >= 1.0)) {
            spawnNearby(`${animal.id}_rare`, 'rare', instIdx++);
          }

          // If no variants exist for this animal, add extra adults when density is high
          if (!hasBaby && !hasRare) {
            const extraCount = density > 0.7 ? 2 : (density > 0.35 ? 1 : 0);
            for (let e = 0; e < extraCount; e++) {
              spawnNearby(animal.id, 'adult', instIdx++);
            }
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
  while (facilities.length < targetFacilityCount && facAttempts < 400) {
    facAttempts++;
    const pathTile = pathTileArray[Math.floor(rand() * pathTileArray.length)];
    const ptGX = pathTile[0];
    const ptGY = pathTile[1];

    const facTemplate = facilityCatalog[Math.floor(rand() * facilityCatalog.length)];
    const facGW = Math.round(facTemplate.footprint[0] / GRID_M);
    const facGH = Math.round(facTemplate.footprint[1] / GRID_M);

    // Try 4 cardinal directions adjacent to this path tile
    const directions = [
      { gx: ptGX, gy: ptGY + 1, rot: 180 },
      { gx: ptGX, gy: ptGY - facGH, rot: 0 },
      { gx: ptGX + 1, gy: ptGY, rot: 270 },
      { gx: ptGX - facGW, gy: ptGY, rot: 90 }
    ];

    const dir = directions[Math.floor(rand() * directions.length)];
    if (isRegionFree(dir.gx, dir.gy, facGW, facGH)) {
      markRegion(dir.gx, dir.gy, facGW, facGH, OCC_FACILITY);

      const posX = (dir.gx + facGW / 2) * GRID_M;
      const posY = (dir.gy + facGH / 2) * GRID_M;

      facilities.push({
        id: `fac_${facTemplate.id}_${facilities.length + 1}`,
        asset_id: facTemplate.id,
        category: facTemplate.category,
        position: [Math.round(posX * 100) / 100, Math.round(posY * 100) / 100, 0],
        rotation_deg: dir.rot,
        footprint: facTemplate.footprint,
        path_tile: [ptGX * GRID_M + GRID_M / 2, ptGY * GRID_M + GRID_M / 2]
      });
    }
  }

  // 5. Decorations (in empty open spaces)
  const decorations = [];
  const targetDecorCount = Math.max(8, Math.floor(6 + density * 50));
  let decorAttempts = 0;

  while (decorations.length < targetDecorCount && decorAttempts < 500) {
    decorAttempts++;
    const gx = 2 + Math.floor(rand() * (gridCells - 4));
    const gy = 2 + Math.floor(rand() * (gridCells - 4));

    if (getCell(gx, gy) === OCC_EMPTY) {
      setCell(gx, gy, OCC_DECOR);
      const decorItem = decorCatalog[Math.floor(rand() * decorCatalog.length)];
      decorations.push({
        id: `decor_${decorItem.id}_${decorations.length + 1}`,
        asset_id: decorItem.id,
        position: [gx * GRID_M + GRID_M / 2, gy * GRID_M + GRID_M / 2, 0],
        rotation_deg: Math.round(rand() * 360)
      });
    }
  }

  // 6. People Placement (Visitors and Keepers on paths or near enclosure gates)
  const people = [];
  const keeperCount = Math.min(population, Math.max(1, Math.floor(population * 0.15)));
  const visitorCount = population - keeperCount;

  // Keepers spawn near enclosure gates or along paths
  for (let k = 0; k < keeperCount; k++) {
    const keeperId = keeperCatalog[Math.floor(rand() * keeperCatalog.length)];
    let pos, nearEncId = null;

    if (enclosures.length > 0 && rand() > 0.4) {
      const enc = enclosures[Math.floor(rand() * enclosures.length)];
      pos = [enc.gate_position[0], enc.gate_position[1], 0];
      nearEncId = enc.id;
    } else {
      const pt = pathTileArray[Math.floor(rand() * pathTileArray.length)];
      pos = [pt[0] * GRID_M + GRID_M / 2, pt[1] * GRID_M + GRID_M / 2, 0];
    }

    people.push({
      id: `person_keeper_${k + 1}`,
      asset_id: keeperId,
      role: 'keeper',
      position: pos,
      rotation_deg: Math.round(rand() * 360),
      near_enclosure_id: nearEncId
    });
  }

  // Visitors spawn on paths
  for (let v = 0; v < visitorCount; v++) {
    const visitorId = visitorCatalog[Math.floor(rand() * visitorCatalog.length)];
    const pt = pathTileArray[Math.floor(rand() * pathTileArray.length)];
    const jitterX = (rand() - 0.5) * 0.8;
    const jitterY = (rand() - 0.5) * 0.8;

    people.push({
      id: `person_visitor_${v + 1}`,
      asset_id: visitorId,
      role: 'visitor',
      position: [
        Math.round((pt[0] * GRID_M + GRID_M / 2 + jitterX) * 100) / 100,
        Math.round((pt[1] * GRID_M + GRID_M / 2 + jitterY) * 100) / 100,
        0
      ],
      rotation_deg: Math.round(rand() * 360)
    });
  }

  // Format path instances
  const paths = Array.from(pathSet).map((pStr, idx) => {
    const [gx, gy] = pStr.split(',').map(Number);
    return {
      id: `path_${idx + 1}`,
      position: [gx * GRID_M + GRID_M / 2, gy * GRID_M + GRID_M / 2, 0],
      size: [GRID_M, GRID_M]
    };
  });

  const durationMs = Date.now() - startTime;

  return {
    version: '1.0.0',
    settings: {
      size_m,
      density,
      population,
      seed
    },
    boundary: {
      width_m: size_m,
      depth_m: size_m,
      min_x: 0,
      min_y: 0,
      max_x: size_m,
      max_y: size_m
    },
    entrance,
    paths,
    enclosures,
    facilities,
    decorations,
    people,
    stats: {
      total_enclosures: enclosures.length,
      total_animals: enclosures.reduce((sum, e) => sum + e.animals.length, 0),
      total_facilities: facilities.length,
      total_decorations: decorations.length,
      total_people: people.length,
      generation_time_ms: durationMs
    }
  };
}
