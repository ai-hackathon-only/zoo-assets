# Rig proposal (owner's starting point for `Decision: skeletons and clips`)

Written by the owner with Claude Code before round 3. **This is a proposal, not the decision.** Change anything: bone names, which species share a skeleton, clip lists, what counts as static. The team discusses it in `Decision: skeletons and clips`, and the answer marked there is the final version. Record that version in `RIGS.md` and in the `rig` field of every row in `assets.json`. Where this file and the decision disagree, the decision wins.

## Rules the proposal assumes
- Every asset has a `root` bone at its floor centre. Rigid weights: every vertex follows exactly one bone (see `lib/rig.py`).
- Every asset has at least an `idle` clip. A static asset gets `root` only and an `idle` with no visible motion, so a game can load all assets the same way.
- Baby and rare variants use their adult's rig. A baby's joints move with its bigger head and shorter legs (`_babyfy` in `lib/zoo.py` already does this for the four-leg animals).
- Clip lengths: loops of 24 frames (fast moves) or 48 frames (idle, slow moves) at 24 fps.
- Bones can only bend where the generator splits a part. A leg made as one cylinder can swing but not bend at the knee. Wherever the proposal says "2-bone leg" or "chain", the generator has to build that part from separate pieces.

## Animals: every species is different
The four-leg rig that exists today (body, neck, head, tail, 4 one-piece legs; clips walk, idle, eat) is the minimum. It is not the target for all 66 four-leg species: below, each species gets its own extra bones and clips. Read the family base first, then the species row.

### Family bases
| Family | Base bones | Base clips |
|---|---|---|
| four-leg (quadruped, bigcat, hoofed) | body, neck, head, tail, leg_FL/FR/BL/BR | walk, idle, eat |
| upright mammal | body, head, tail, arm_L/R, foot_L/R | idle, eat |
| primate | hips, spine, chest, neck, head, upperarm/forearm L/R, thigh/shin L/R, tail | walk, idle, eat, sit |
| bird | body, neck, head, beak, wing_L/R, leg_L/R, tail | walk, idle, eat (peck) |
| reptile | body, head, jaw, tail chain, 4 legs | crawl, idle, eat |
| snake | spine chain (8), head, jaw | slither, idle |
| fish | spine chain (2–6), tail, fin_L/R | swim, idle |
| marine mammal | spine chain, fluke or rear flippers, flipper_L/R, head | swim, idle |
| insect | thorax, abdomen, head, antenna_L/R, 6 legs | walk, idle |
| arachnid | body, 8 legs (+ tail chain and claws for the scorpion) | walk, idle |

### Four-leg mammals: quadruped generator (30)
| Species | Extra bones | Extra or changed clips |
|---|---|---|
| African elephant, Asian elephant | trunk chain (3), ear_L/R | idle: ears flap, trunk swings; eat: trunk curls to mouth; **spray** |
| white rhino, Indian rhino | ear_L/R | idle: ear flick; **charge** (fast walk, head down) |
| hippo, pygmy hippo | jaw, ear_L/R | **yawn** (jaw wide open), **swim** (only the head shows above water) |
| brown bear, polar bear | 2-bone legs | **stand** (rears up on hind legs), polar bear: **swim** |
| giant panda | 2-bone front legs, arm reach | **sit-eat** (sits, bamboo to mouth) |
| red panda, raccoon | tail chain (2) | raccoon: **wash** (front paws together) |
| sloth bear, spectacled bear | 2-bone legs | sloth bear: **dig** |
| grey wolf, arctic fox, red fox, African wild dog | tail chain (2), jaw | wolf: **howl** (head up, jaw open); foxes: **pounce** |
| meerkat | upright base | **lookout** (stands tall, head turns) |
| koala | upright base | **cling** (arms around a branch), sleep idle |
| red kangaroo | upright base, tail chain (2), 2-bone hind legs | **hop**, idle with tail as a prop |
| aardvark, giant anteater | snout, ear_L/R (aardvark), tongue (anteater) | **dig**; anteater: **lick** (tongue flicks) |
| capybara, wombat | none | **sit**; wombat: **dig** |
| Tasmanian devil | jaw | **yawn** (wide gape) |
| platypus | bill, flat tail | **swim** (paddle), **dig** |
| porcupine | quills as one bone group | **quills up** (threat) |
| American beaver | flat tail | **swim**, **tail slap** |
| European badger | 2-bone front legs | **dig** |
| river otter | spine chain (2), tail chain (2) | **swim** (body waves), **roll** |

### Big cats: bigcat generator (12)
All 12 get 2-bone legs, a 2-part spine (cats arch and stretch) and a 2-segment tail (it already exists in the model).
| Species | Extra bones | Extra or changed clips |
|---|---|---|
| lion, lioness, Bengal tiger, Amur tiger | jaw | **roar**, **lie down** |
| leopard, snow leopard, jaguar, black panther, cougar | jaw | **crouch-stalk**; snow leopard: tail wraps around the body in idle |
| cheetah | jaw | **run** (gallop, spine flexes) |
| Eurasian lynx, serval | ear_L/R | **pounce** (leap up and down) |

### Hoofed animals: hoofed generator (24)
All 24 get 2-bone legs (knees bend, important for the run) and ear_L/R.
| Species | Extra bones | Extra or changed clips |
|---|---|---|
| giraffe | neck chain (3) | eat: neck bends up to browse a tree, plus the **splay-drink** pose (front legs spread, neck down) |
| okapi | neck chain (2), tongue | **lick** |
| plains zebra, Grevy's zebra, Przewalski's horse | neck chain (2), mane follows neck | **gallop**, **rear** |
| dromedary, Bactrian camel | neck chain (2) | **kneel** (folds legs to rest), **chew** |
| llama, alpaca | neck chain (2) | **spit** (head jerk), **kneel** |
| American bison, European bison | none | **charge**, **wallow** (rolls on its side) |
| moose, reindeer, red deer, sika deer | none (antlers follow head) | **bugle** (head up, call); reindeer: **trot** |
| gemsbok, impala, greater kudu, blue wildebeest | none (horns follow head) | impala: **leap**; wildebeest: **buck** |
| Cape buffalo | none | **charge** |
| warthog | none | **kneel-eat** (kneels on front knees to graze), **run** with tail up |
| tapir | short trunk (1) | **sniff** (trunk curls) |
| mountain goat, markhor | none | **climb-leap** (jump up a step) |

### Primates: primate generator (12)
| Species | Extra bones | Extra or changed clips |
|---|---|---|
| chimpanzee, bonobo | jaw | walk = **knuckle-walk**; **hoot** (jaw, arms up) |
| western gorilla | jaw | knuckle-walk; **chest beat** |
| Bornean orangutan | long arms | **hang** (arms overhead), slow walk |
| lar gibbon | very long arms | **brachiate** (swings arm over arm), **sing** |
| ring-tailed lemur | tail chain (3) | **sunbathe** (sits, arms open), tail held up in walk |
| mandrill, Japanese macaque | jaw | **yawn** (shows teeth), macaque: **groom** |
| golden lion tamarin, common squirrel monkey | tail chain (3) | **leap**, idle head-flick |
| black howler | prehensile tail chain (3), jaw | **howl** |
| proboscis monkey | nose | **honk** (nose bounces) |

### Birds: bird generator (16)
| Species | Extra bones | Extra or changed clips |
|---|---|---|
| bald eagle, scarlet macaw, white stork, kookaburra | 2-part wings | **flap**, **glide** (wings open, still); kookaburra: **laugh** (head back, beak open) |
| snowy owl | 2-part wings, head on a long turn | **head turn** (up to 180°), **flap** |
| toco toucan | big beak follows head | **hop**, **toss** (flips food up with the beak) |
| Indian peafowl | tail fan (5 feather bones) | **display** (fan opens and shakes) |
| red-crowned crane | neck chain (2), 2-part wings | **dance** (leaps, wings open) |
| greater flamingo | neck chain (3), 2-bone legs | idle on one leg, **filter-feed** (head upside down in the water) |
| pelican | pouch / lower beak | **scoop** (pouch swells) |
| shoebill | beak | **clatter** (beak claps), very slow walk |
| ostrich, emu | neck chain (2), 2-bone legs, small wings | **run**, ostrich: **wing display** |
| kiwi | long beak | **probe** (beak into ground) |
| African penguin, emperor penguin | flipper_L/R, feet | walk = **waddle**, **swim**, **belly slide** |

### Reptiles and amphibians: reptile generator (12)
| Species | Extra bones | Extra or changed clips |
|---|---|---|
| Nile crocodile, American alligator, gharial | spine chain (2), tail chain (3), jaw | crawl = **belly crawl**, **high walk**, **swim** (tail sculls), **snap** |
| Komodo dragon, green iguana | tail chain (3), tongue (Komodo) | **tongue flick**, iguana: **head bob** |
| chameleon | eye_L/R, tail chain (4, curls), tongue | **eye roll** (each eye on its own), **tongue shot**, slow **sway walk** |
| Galápagos tortoise | head pulls into the shell | very slow walk, **hide** (head and legs in) |
| green sea turtle | front flippers (2-part) | **swim** (flipper strokes), **surface** |
| reticulated python | snake base | **slither**, **coil** |
| king cobra | snake base + hood | **hood up** (raises the front third), **strike** |
| poison dart frog | 2-bone hind legs, throat | **hop**, **call** (throat swells) |
| axolotl | gills (6), tail chain (2) | **swim**, idle: gills wave |

### Sea animals: sea generator (14)
| Species | Extra bones | Extra or changed clips |
|---|---|---|
| bottlenose dolphin, orca calf | spine chain (3), fluke | **swim** (up-down body wave), **breach** (jump) |
| California sea lion, harbour seal, walrus | neck, front/rear flippers | **hump-walk** on land, **swim**; sea lion: **balance** (head up); walrus: tusks on head, **haul out** |
| manatee | paddle tail | **swim** (slow), **graze** |
| great white shark | spine chain (3), jaw | **swim** (side-to-side), **bite** |
| manta ray | wing chain (2 per side) | **swim** (wing waves) |
| green moray | spine chain (6), jaw | **swim** (snake-like), idle: mouth opens and closes |
| clownfish, blue tang | spine (2), pectoral fins | **swim**, **hover** (fins flutter); clownfish: **nestle** |
| giant Pacific octopus | 8 arms × 3 bones, mantle | **crawl**, **jet** (arms trail), idle: arms curl |
| moon jellyfish | bell, 4 tentacle chains (3) | **pulse** (bell squeezes, tentacles follow) |
| sea otter | spine (2), paws | **float** on its back, **crack** (taps paws on its chest) |

### Insects and others: insect generator (10)
| Species | Extra bones | Extra or changed clips |
|---|---|---|
| monarch butterfly, Atlas moth | wing_L/R (no legs move) | **fly** (flap), idle: slow open and close |
| honey bee | wing_L/R | **fly** (fast flap), **waggle dance** |
| goliath beetle | horn, wing cases | walk (tripod gait), **open wings** |
| leafcutter ant | mandibles, leaf piece | walk, **carry** (leaf held high) |
| stick insect | none | **sway walk** (rocks like a twig) |
| praying mantis | 2-part forelegs, head | **strike**, idle: head tilt |
| emperor scorpion | tail chain (5), claw_L/R | walk, **tail raise**, **pinch** |
| Mexican redknee tarantula | 8 legs, fangs | walk (alternating), **rear up** (front legs raised) |
| giant African snail | foot, eye stalks (2) | **crawl** (foot stretches), stalks pull in |

## People: one shared human skeleton (45)
| Group | Bones | Clips |
|---|---|---|
| all keepers and visitors | hips, spine, chest, neck, head, upperarm/forearm L/R, thigh/shin L/R, `prop` (in the right hand) | walk, idle, wave, talk |
| keepers (20) | same | + **carry**, **feed** (bend and toss), **point**; vet: **examine**; ranger: **radio**; landscaper: **rake** |
| visitors (25) | same; a few add bones | camera: **photo**; balloon child: balloon sways from `prop`; ice cream: **lick**; teen with phone: **look down**; skateboarder: **ride**; senior with cane: cane walk; stroller parent: **push** (stroller wheels turn); wheelchair user: **roll** (wheel bones); parent with child on shoulders: child gets head and arms; jogger: **jog**; toddler: **waddle**; bird watcher: **binoculars** |

## Vehicles (25)
| Group | Bones | Clips |
|---|---|---|
| wheeled: golf cart, utility truck, safari jeep, safari bus, delivery van, water tanker, quad bike, feed trailer, train carriage, ice cream cart | body, one bone per wheel, front steering | **drive** (wheels turn, body bobs), idle (engine shake); ice cream cart: umbrella sways |
| with doors or ramp: animal transport truck (ramp), vet van (rear doors), safari bus (door) | + hinge | + **open/close** |
| zoo train engine | wheels, side rods | **drive** (rods move with the wheels), whistle puff idle |
| tractor | big rear and small front wheels | drive |
| forklift | wheels, mast, forks | drive, **lift** |
| lawn mower | wheels, blade | drive, blade **spin** |
| wheelbarrow, hand cart | wheel(s), handles | **push**, wheelbarrow: **tip** |
| bicycle, kick scooter, stroller, wheelchair | wheels, pedals or crank | **roll** / **pedal** |
| pedal boat, rowing boat | paddle wheel or oars | **paddle** / **row**, idle **bob** |
| sky-tram gondola | hook, cabin | **sway** |

## Facilities (70)
| Group | Clips |
|---|---|
| gates: grand entrance arch, paddock double gate, keeper metal slide gate, pedestrian wicket, safari vehicle airlock (two gates, one after the other) | **open/close** |
| visitor turnstile, turnstile bank (4 rotors), ticket barrier (arm) | **spin** / **arm up-down** |
| buildings with doors: night shelter, timber lean-to, keeper shed, vet clinic, quarantine bay, hay barn, restroom, staff breakroom, lost and found, first aid, reptile house, aquarium dome, aviary, butterfly hothouse | **door open/close** |
| kiosks: ticketing booth, ice cream, pretzel, souvenir, beverage bar, visitor info, ice slush | **shutter up/down** |
| water: penguin pool, hippo mud pond, fountain, duck pond, alligator swamp, waterfall, elephant splash pool, flamingo lagoon, underwater tunnel | water **ripple**; fountain **jets pulse**; waterfall **sheet ripple** |
| safari sunshade, picnic pergola, rope stanchions, canopy walkway (straight, ramp) | **flutter** / **sway** |
| static (root + idle): fences and walls, paths, bridges, moat, observation tower, glass overlook, viewing pavilion, meerkat dome, giraffe platform, petting corral, compost bay, otter holts, bat cave | idle |

## Benches, lamps, bins and signs (20)
| Group | Clips |
|---|---|
| bear-proof bin, recycling bin, solar compactor | **lid open/close** |
| misting cooling station | fan **spin** |
| fingerpost sign | **wobble** |
| static: 5 benches, 4 lamps, timber bin, map board, info plaque, caution barrier, entrance totem, drinking fountain | idle |

## Plants (55)
| Group | Bones | Clips |
|---|---|---|
| trees: acacia, baobab, oak, birch, pine, spruce, eucalyptus, willow, autumn maple, cherry blossom, mangrove, kapok, cypress, joshua tree, dead tree, tree fern, bonsai pine, banana plant | trunk + crown (2–3 bones); willow: hanging branch chains | **sway** (crown lags the trunk) |
| palm tree, date palm | trunk + fronds | sway, fronds **flutter** |
| bamboo, tall grass, savanna grass, pampas, reeds, papyrus | 2–3 bones per clump | fast **sway** |
| sunflower, tulip bed, daisy patch, lavender, flowering shrub, rhododendron, berry bush, monstera, bromeliad, agave, aloe | stem / head bones | gentle **nod** |
| water lily, lotus | leaf, flower | **bob** |
| kelp strand | chain (4) | **wave** |
| hanging vine | chain (3) | **swing** |
| static: saguaro, barrel cactus, prickly pear, box hedge, hedge corner, topiary ball, round shrub, fern bush, ivy wall patch, flower planter, round pot, mushrooms, tree stump, coral | idle |

## Landscape (45)
| Group | Clips |
|---|---|
| ice floe, iceberg rock | **bob** |
| the other 43 | idle (static) |

## Decor (30)
| Group | Clips |
|---|---|
| flag pole, banner pole, bunting string | **flutter** (cloth chains) |
| patio umbrella, striped parasol | **open/close** |
| wind chime, lantern string, hanging basket, bird feeder post | **swing** |
| weather vane | **turn** |
| wishing well | crank and bucket **turn** |
| tiki torch | flame **flicker** (flame bone scales) |
| the other 17 | idle (static) |

## Food (20)
| Group | Clips |
|---|---|
| slow-feeder haynet, nectar tube feeder | **swing** |
| water drink trough | water **ripple** |
| the other 17 | idle (static) |

## Enrichment (20)
| Group | Clips |
|---|---|
| boomer balls (large, small), puzzle barrel | **roll / bounce** |
| tire swing, firehose cube, rope tug, bungee net, bamboo wind chime, cargo net | **swing** |
| floating log buoy, floating ring | **bob** |
| wobble cone | **wobble** |
| treat labyrinth plate | **tilt** |
| primate puzzle box | **lid** |
| ice block treat | **melt** (shrinks over the clip) |
| tire pyramid, scratch post, scent log, misting rub station, splash tub | idle (static) |

## Shop (20)
| Group | Clips |
|---|---|
| plush lion, elephant, penguin, giraffe | **squish / bounce** |
| postcard carousel rack, keychain | **spin** |
| helium tiger balloon | **bob**, string sways |
| blind box, zoo guide brochure | **open** (lid / unfold) |
| the other 11 | idle (static) |

## Vet equipment (20)
| Group | Clips |
|---|---|
| exam table, surgical light, portable X-ray, mobile ultrasound | **raise / swivel** |
| recovery stretcher, transport gurney, oxygen trolley, IV drip stand | **roll** |
| incubator, centrifuge (+ **spin**), dart rifle case, first aid trunk, medicine cabinet | **open/close** |
| capture net pole | **swing** |
| hydrotherapy tank | water **ripple** |
| both scales, anesthesia machine, instrument tray, microscope | idle (static) |

## Open questions for the team
1. **Knees and chains.** 2-bone legs and chains need generator changes (parts split where they bend). Which families get them in this round, and which keep one-piece legs?
2. **Rigid weights on bending bodies.** Snakes, fish, the moray and the octopus will bend in visible segments. Is that fine for the toy look, or should these few use smooth weights, with the file budget checked?
3. **Shared clip names.** Should the game rely on one fixed set (`idle`, `move`, `eat`, `special`) with species names kept as extra clips, so any animal can be driven the same way?
4. **Order.** Animals are the biggest job and need the most review. Split them by generator across seats, and do the people rig (45 assets, one skeleton) and the object rigs in parallel?
