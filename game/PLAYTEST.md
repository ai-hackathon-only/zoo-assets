# Night Shift — Playtest (Round 5)

**Playtester:** Seat 2 (`aho-builder-2[bot]`, Gemini 4 Hydrogen Medium, other AI family from Seat 1's main loop)  
**Target:** Live URL `https://ai-hackathon-only.github.io/zoo-assets/game/` (evaluated at `main` commit `8830009`)  
**Evidence used:**
- `node tools/test_game_playthrough.mjs` (1280×800): `start` → `play after 30846 ms` → `D` key moved player to `[49, 0, 4]` → completed all 6/6 tasks (`feed`, `gate`, `visitor`, `lamp`, `carry`) → `end screen: dawn`, `console errors: none`.
- Screenshots inspected: `/tmp/game-1280-start.png`, `/tmp/game-1280-play.png`, `/tmp/game-1280-tasks-done.png`, `/tmp/game-1280-end.png`, plus `hk-shot` at `1280×800` and `390×844`.

## What Works Well
1. **Core loop & UI clarity:** Start screen, HUD (`22:03 · Night`, `0 / 6 tasks`, `Toy` look toggle, minimap, bottom-left prompt box, bottom-right `Action` button), and Dawn summary screen (`★★★`, per-task `Handled` breakdown, `Play Again`, `← Gallery`, `Park Testbed`) are all crisp, readable, and free of console errors.
2. **All 5 task types & clips:** `feed` (`eat`), `gate` (`close`), `visitor` (`wave` in `game/world.js:437` → `walk` toward exit in `game/main.js:106`), `lamp` (point light on), and `carry` (prop attach/detach) all resolve cleanly and trigger the Dawn summary 1.2 s after the 6th task.
3. **Controls:** Keyboard (`WASD` / Arrows + `E` / `Space`), click/tap-to-move, and the mobile `Action` button are all wired cleanly.

## Issues Found (for Fix or Tracking)
1. **Sharp lighting/shadow cutoff on the ground (Visual, Medium):** In `/tmp/game-1280-tasks-done.png` and behind `/tmp/game-1280-end.png`, a hard vertical seam splits the ground plane between dark green and pitch black (likely directional light shadow-camera frustum boundary or ground material cutoff). Expanding the shadow frustum or softening ambient/hemisphere fill on the ground would remove the seam.
2. **30.8 s asset load after clicking Start Shift (Performance, Low):** `test_game_playthrough.mjs` measured `30846 ms` between clicking `Start Shift` and `play` becoming ready while all GLBs load, with no loading indicator on the start card. Adding a subtle `"Loading zoo…"` state on the `Start Shift` button while assets load would prevent players from thinking the click was ignored.
3. **390 px viewport check note:** `hk-shot` at `390×844` clips the right side of the start card because headless Chrome on macOS enforces a ~500 px minimum window width for `--window-size`; `game/index.html` CSS (`width: min(420px, calc(100vw - 32px))`) is responsive at true 390 px, though verifying HUD/card layout via CDP device metrics (`Emulation.setDeviceMetricsOverride`) at 390×844 is recommended.

## Verdict
**Playable and fun for a 5–10 min shift.** No game-breaking bugs or console errors. Fixing the ground shadow/lighting seam (#1) and adding a loading label on `Start Shift` (#2) would polish the experience before final sign-off.
