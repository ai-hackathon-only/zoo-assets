# MOTION — Round 3 Cross-Family Motion Review

Status: All 18 skeleton groups in `RIGS.md` have frame strips rendered with headless Blender (`tools/clip_strip.py` / `tools/render_all_strips.py`, `360x360` per frame, EEVEE ortho).
- **Claude-built skeletons** (14 groups: `quadruped`, `hoofed`, `bigcat`, `upright`, `primate`, `bird`, `reptile`, `fish`, `marine`, `insect`, `arachnid`, `mollusc`, `vehicle`, `gate`, `plant`): reviewed below by **Seat 2 (`Antigravity agy (Google) · gemini-4-argon-medium`)**.
- **Gemini-built skeletons** (4 groups: `snake`, `human`, `human_onepiece`, `facility`, `static`): frame strips rendered and ready below for cross-family sign-off by **Seat 1 or Seat 3 (`Claude Code (Anthropic) · claude-sonnet-5-5`)**.

---

## 1. Claude-Built Skeletons (Reviewed by Seat 2 · `gemini-4-argon-medium`)

| Skeleton (`rig`) | Built by | Sample Asset | Clips Inspected (Frame Strips) | Visual Findings (Parts, Limbs, Head, Motion) | Result |
|---|---|---|---|---|---|
| `quadruped` | Claude | `african_elephant` | `walk` (`docs/motion/quadruped/african_elephant_walk.png`, 6f)<br>`eat` (`docs/motion/quadruped/african_elephant_eat.png`, 3f) | `walk`: diagonal leg pairs (`leg_FL`/`leg_BR` vs `leg_FR`/`leg_BL`) swing cleanly from hip/shoulder pivots; tusks, ears, and trunk stay attached to head/body with zero detached faces.<br>`eat`: head pitches **down** toward the ground and trunk curls inward cleanly (fixing the early upward-head bug noted in `GOALS.md`). | **PASS** |
| `hoofed` | Claude | `giraffe` | `walk` (`docs/motion/hoofed/giraffe_walk.png`, 6f)<br>`eat` (`docs/motion/hoofed/giraffe_eat.png`, 3f) | `walk`: long legs swing in clean alternating stride; brown spots (`SM_giraffe`) remain welded to the torso mesh without flying off.<br>`eat`: long neck pivots forward/downward from the chest junction (~60° pitch), lowering the head naturally without intersecting the forelegs. | **PASS** |
| `bigcat` | Claude | `lion` | `walk` (`docs/motion/bigcat/lion_walk.png`, 6f)<br>`eat` (`docs/motion/bigcat/lion_eat.png`, 3f) | `walk`: four legs swing in stride while tail counter-sways; mane stays locked to head/neck.<br>`eat`: head and mane pitch downward toward ground level cleanly without clipping into chest. | **PASS** |
| `upright` | Claude | `meerkat` | `walk` (`docs/motion/upright/meerkat_walk.png`, 6f)<br>`eat` (`docs/motion/upright/meerkat_eat.png`, 3f) | `walk`: bipedal waddle with alternating foot steps and forepaw swing; tail stays anchored at pelvis.<br>`eat`: torso and head dip forward/downward with forepaws brought toward snout. | **PASS** |
| `primate` | Claude | `western_lowland_gorilla`<br>`lar_gibbon`<br>`common_squirrel_monkey` | `walk`, `sit`, `eat` (`docs/motion/primate/*.png`, 5f each) | `western_lowland_gorilla`: knuckle-walk swings long arms and hind legs cleanly; silver back panel stays rigid on torso; `sit` lowers pelvis cleanly.<br>`lar_gibbon`: upright arm-raised walk and forward-dipping `eat` clip show clean shoulder/hip pivots.<br>`common_squirrel_monkey`: quadruped walk and sit posture keep long tail attached. | **PASS** |
| `bird` | Claude | `ostrich`<br>`bald_eagle`<br>`pelican`<br>`emperor_penguin` | `walk` (`ostrich_walk.png`, 6f)<br>`fly` (`bald_eagle_fly.png`, 6f)<br>`eat` (`pelican_eat.png`, `emperor_penguin_eat.png`, 6f) | `ostrich`: long 2-leg alternating stride with stable body and plumage.<br>`bald_eagle`: `fly` cycles `wing_L`/`wing_R` through full up/down flap arc without detaching from body.<br>`pelican` & `emperor_penguin`: `eat` pitches neck/head/beak downward and bobbing cleanly. | **PASS** |
| `reptile` | Claude | `saltwater_crocodile`<br>`komodo_dragon`<br>`galapagos_tortoise`<br>`green_iguana_rare`<br>`axolotl` | `walk` (`saltwater_crocodile_walk.png`, `galapagos_tortoise_walk.png`, `green_iguana_rare_walk.png`, `axolotl_walk.png`, 6f)<br>`eat` (`komodo_dragon_eat.png`, `axolotl_eat.png`, 6f) | Sprawled 4-leg gait swings limbs cleanly with lateral body/tail yaw; dorsal scutes (`saltwater_crocodile`), shell (`galapagos_tortoise`), and gill fronds (`axolotl`) stay firmly attached. In `eat`, `komodo_dragon` and `axolotl` dip head and tongue/snout downward cleanly. | **PASS** |
| `fish` | Claude | `clownfish` | `swim` (`docs/motion/fish/clownfish_swim.png`, 6f) | Multi-segment spine chain (`spine_0..2`, `tail`) undulates laterally with pectoral fins (`fin_L`/`fin_R`) oscillating; white/black stripe rings remain attached to their body segments. | **PASS** |
| `marine` | Claude | `bottlenose_dolphin`<br>`sea_otter` | `swim` (`bottlenose_dolphin_swim.png`, 4f)<br>`eat` (`sea_otter_eat.png`, 4f) | `bottlenose_dolphin`: vertical fluke/tail pitch undulation (`swim`) is smooth and continuous.<br>`sea_otter`: `eat` pitches head/snout downward toward chest while floating. | **PASS** |
| `insect` | Claude | `monarch_butterfly` | `crawl` (`docs/motion/insect/monarch_butterfly_crawl.png`, 6f) | 6 legs and antennae step/oscillate while orange/black forewings and hindwings gentle-flap in sync; no detached wing spots. | **PASS** |
| `arachnid` | Claude | `emperor_scorpion` | `crawl` (`docs/motion/arachnid/emperor_scorpion_crawl.png`, 6f) | 8 walking legs alternate in arachnid gait while pedipalps and curved metasoma (tail stinger) bob cleanly as a unit. | **PASS** |
| `mollusc` | Claude | `giant_african_snail` | `crawl` (`docs/motion/mollusc/giant_african_snail_crawl.png`, 6f) | Muscular foot slides/bobs while spiral shell rocks gently and eyestalks (`eyestalk_L`/`R`) pitch forward and back without detaching. | **PASS** |
| `vehicle` | Claude | `keeper_golf_cart` | `drive` (`docs/motion/vehicle/keeper_golf_cart_drive.png`, 6f) | All 4 wheel bones spin continuously around their axle centres while chassis, roof canopy, and steering wheel remain rigid and stable. | **PASS** |
| `gate` | Claude | `gate_paddock_double_wood` | `open` (`docs/motion/gate/gate_paddock_double_wood_open.png`, 3f) | Left and right gate leaves pivot cleanly 100° outward around the outer hinge posts from a 0 mm closed gap, with cross-braces attached. | **PASS** |
| `plant` | Claude | `baobab_tree` | `sway` (`docs/motion/plant/baobab_tree_sway.png`, 6f) | `crown` and upper `trunk` sway gently left/right (~4° arc) while the trunk base stays planted on the ground origin. | **PASS** |

**Claude-built summary (Seat 2 review):** **15 / 15 skeleton groups PASS** (0 flying parts, 0 wrong-way limb bends, 0 upward-eat bugs, 0 dead clips).

---

## 2. Gemini-Built Skeletons (Strips Rendered for Claude Cross-Family Review)

Built by Seat 2 (`gemini-4-argon-medium` / `claude-sonnet-5-5-medium` on `agy`). Strips rendered with headless Blender for inspection by Seat 1 or Seat 3 (Claude family):

| Skeleton (`rig`) | Built by | Sample Asset | Clips Inspected (Frame Strips) | Pre-Check Notes (for Claude Reviewer) |
|---|---|---|---|---|
| `snake` | Seat 2 | `reticulated_python` | `slither` (`docs/motion/snake/reticulated_python_slither.png`, 6f) | 4-bone chain (`spine_0`, `spine_1`, `spine_2`, `head`) produces a travelling lateral S-wave across the coiled body segments while keeping the head level and tongue attached. |
| `human` | Seat 2 | `keeper_elephant_keeper_09`<br>`visitor_senior_sunvisor_10` | `walk` (`docs/motion/human/keeper_elephant_keeper_09_walk.png`, 6f)<br>`carry` (`docs/motion/human/keeper_elephant_keeper_09_carry.png`, 6f)<br>`wave` (`docs/motion/human/visitor_senior_sunvisor_10_wave.png`, 6f) | 16-bone human rig: `walk` swings thighs/shins and upper/forearms in contralateral stride with hat and tool (`prop`) locked to head/hand; `carry` raises both arms forward (-60°); `wave` raises right arm and oscillates forearm. |
| `human_onepiece` | Seat 2 | `visitor_wheelchair_user_22` | `walk` (`docs/motion/human_onepiece/visitor_wheelchair_user_22_walk.png`, 6f) | `root` + `body` rigid rig (`visitor_wheelchair_user_22`, `visitor_parent_shoulder_kid_23`) keeps wheelchair wheels, frame, and seated visitor moving together without tearing mesh vertices. |
| `facility` | Seat 2 | `fence_wood_rail_straight` | `idle` (`docs/motion/facility/fence_wood_rail_straight_idle.png`, 3f) | Static non-gate facility with `root` bone and 48-frame `idle` clip; geometry stays motionless on the grid origin as designed in `RIGS.md`. |
| `static` | Seat 2 | `boulder_small` | `idle` (`docs/motion/static/boulder_small_idle.png`, 3f) | Root-only rig with `idle` clip (subtle bob on enrichment toys; motionless hold on rocks/signs/props per `RIGS.md`). |
