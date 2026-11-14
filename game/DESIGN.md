# Night Shift — Game Design

Agreed in [Decision: game design (#133)](https://github.com/ai-hackathon-only/zoo-assets/discussions/133) and recorded in `Plan & roles — round 5` (#134).

## Concept & Core Loop
- **Title:** Night Shift
- **Premise:** You are the zoo keeper on the night shift after closing. The park is dark, and you walk the paths handling tasks until dawn.
- **Shift length:** 6–7 minutes (dusk to dawn clock; sky and ambient light brighten smoothly toward dawn). Completing all 6 tasks ends the shift early (~1.2 s pause, then transitions to dawn).
- **Scoring:** Gentle, no fail state. 6 tasks total across 5 task types; 4+ completed counts as a good shift (1–3 stars on the dawn summary). Any unfinished tasks are listed kindly as "left for the day team".

## Tasks (5 types, 6 tasks per shift)
Each task appears as a glowing beacon marker on the park and 2D minimap. Walk within interaction range and hold/tap the Action button for 1.5 s to resolve it with its rig clip:

| Task Type | Target Asset / Rig | Clip(s) Used | Resolution |
|---|---|---|---|
| **Feed animal** | Animals (`quadruped`, `hoofed`, `bigcat`, `bird`) | Animal `eat`, keeper `idle`/`walk` | Animal plays `eat` clip |
| **Close gate** | Gate rigs (e.g. `gate_paddock_double_wood`, `gate_pedestrian_wicket`) | Gate `close` (starts `open`) | Gate animates shut |
| **Guide lost visitor** | Visitor (`visitor_*` human rig) | Visitor `wave` → `walk` | Visitor waves, then walks toward the park exit |
| **Relight lamp** | Lamp posts (`lamp_post_victorian_single`, `lamp_post_modern_led`) | Keeper `idle` | Warm point light + emissive bulb turn back on |
| **Carry bucket** | `food_fish_bucket_herring_04` → `food_water_drink_trough_20` / enclosure | Keeper `carry` → `walk` | Pick up bucket (parented to keeper's `prop` bone from `RIGS.md` during `carry`), carry to target trough, and release at the trough |

## World, Camera & Look
- **Park layout:** Generated via `park/generator.js` (`generateLayout`) with a fixed default seed (6 enclosures in the compact 100 m layout, paths, lamps, gates, entrance).
- **Player:** `keeper_safari_lead_01` (human rig: `idle`, `walk`, `carry`).
- **Camera:** Third-person chase camera tilted ~50° from horizontal, fixed follow distance.
- **Night look:** Reuses `park/park.js` dark blue night preset (`0x0c1428` sky/fog, cool moonlight), warm lamp pools (`PointLight`), keeper flashlight cone (`SpotLight`), and glowing task markers.
- **Ink switch:** Optional "Toy / Sumi-e" toggle using `vendor/ink.js`.

## Controls
- **Desktop:** `WASD` / Arrow keys to move, `E` / `Space` for Action, or click-to-move on ground.
- **Mobile (390 × 844):** Tap-to-move on ground (or virtual stick) + one large thumb-friendly **Action** button that fits cleanly on 390 px width.

## Screens & Navigation
- **Start screen:** Title, short instructions, "Start Shift" button, Ink look toggle, and links back to Gallery (`../`) and Park (`../park/`).
- **HUD:** Dusk-to-dawn clock, tasks completed counter (`0 / 6`), mini-map with task markers, Ink toggle, and Action button.
- **Dawn summary screen:** Star rating (1–3), completed vs. "left for the day team" breakdown, "Play Again" button, and links to Gallery / Park.

## Test Hooks
- `window.game.debug.completeTask(type)` — teleports/completes the next pending task of `type` (or any pending task if omitted) for scripted playthroughs.
- `window.game.debug.skipTo('dawn')` — advances the shift clock to dawn and triggers the summary screen.
- `window.game.debug.getState()` — returns current screen, clock progress, player position, and task statuses.
