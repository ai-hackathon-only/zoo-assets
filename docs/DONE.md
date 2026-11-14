# Round 4 evidence

Run on main at 5786179, 2026-11-14 23:14 JST:
- `python3 -I SKILLS/blender/el4cteo/blender-asset-qa/scripts/qa_check.py` / `python3 -c "import json; assert len(json.load(open('sprites.json'))['assets']) == 566"`: 566/566 sprite sheets valid.
- Total sprite sheet size: **14.85 MB** (under 90 MB cap; peak sheet 66 KB under 150 KB cap).
- `node tools/check_sumi_e.mjs`: 0 console errors; 1280px 61 FPS, 390px 60 FPS; first frame in-page 45 ms / 22 ms.

| Done-when line | Evidence |
|---|---|
| Decision first | `docs/sumi-e/DECISION.md` (Discussion #114 agreed spec) |
| Live switch | "Toy / Sumi-e" in gallery and park, kept in URL (`?look=ink`), PR #116 & #119 |
| Match the reference | `docs/sumi-e/REVIEW.md` (6/6 PASS across all reference assets; 0 chroma leaks, continuous lines, stable wobble) |
| Speed and phones | `tools/check_sumi_e.mjs`: 1280px (61 fps, 45 ms first frame), 390px (60 fps, 22 ms first frame), 0 console errors; `phone-gallery-ink-390.png`, `phone-asset-ink-390.png` |
| Sprite sheets for all 566 assets | `sprites/<category>/<id>.png` (566 assets, 14.85 MB <= 90 MB, peak 66 KB <= 150 KB), `sprites.json`, PR #118 & #119 |
| A check for the sheets | `validate.py` sprite verification passes for all 566 assets (PR #118) |
| README sumi-e section | `README.md` (`## Sumi-e Ink Look and Sprite Sheets`, PR #120) |
| Retros | `Retro — round 4` discussion |

---

# Round 3 evidence

Run on main at 86e4361, 2026-11-14 14:27 JST, Blender 5.2.2 headless, seat 1's Mac:
`blender -b -noaudio --factory-startup --python validate.py`
Result: `VALIDATE pass=566 fail=0 not_built=0 total_bytes=40851240` (40.85 MB, under the 150 MB cap).

| Done-when line | Evidence |
|---|---|
| Decision first | `RIGS.md` (agreed skeletons and clips) |
| All 566 assets rigged | `assets.json`: 566 of 566 have `rig`; validate.py checks one armature, one bone per vertex, clips, bone names |
| Generators, not hand work | rigs come from generator code and `lib/rig.py`; `build_all.py` rebuilds all |
| validate.py checks rigs | 566 pass, 0 fail (above) |
| File budget | total 40.85 MB; per-asset limits enforced by validate.py |
| Motion review | `MOTION.md` + 43 frame strips in `docs/motion/<skeleton>/` covering all 20 `rig` skeleton IDs (18 `RIGS.md` rows): 15 Claude-built groups reviewed and passed by Seat 2 (`gemini-4-argon-medium`); 5 Gemini-built groups reviewed by Seat 3 (`claude-sonnet-5-5`, all 5) and Seat 1 (`claude-sonnet-5-5`, `human` walk + `snake`) in #111 (`human`, `facility`, `static` PASS; `snake` weak: needs a bigger wave; `human_onepiece` body bob, no wheel bone) |
| Gallery clip check | `node tools/check_gallery_clips.mjs` on the live URL, 2026-11-14 15:10 JST: 20 skeletons, one asset each, every clip button clicked and became active, Animated tab 566 cards, 0 console errors. Oddity: insect, arachnid and mollusc assets list a `Swim` clip next to `Crawl`; the motion review should look at it. |
| README rigs section | `README.md` (`## Rigs, skeletons and clips`, merged in #98) |
| Retros | `Retro — round 3` discussion |

## Round 5: Night Shift (`game/`)

Live URL: https://ai-hackathon-only.github.io/zoo-assets/game/. Checked on live `game/` by seat 2, 2026-11-15.

| Done-when line | Evidence |
|---|---|
| Decision first | `Decision: game design` discussion; agreed text in `game/DESIGN.md` |
| Playable, 4+ task types | start screen, shift, dawn summary (#143); 6 task types, ending early when all are done (#146) |
| Controls on both | keyboard and mouse on desktop, touch controls at 390 px (#143) |
| Night look | night lighting preset in `game/world.js` (#143) |
| Scripted playthrough | `node tools/test_game_playthrough.mjs`: 6/6 tasks, dawn reached, 0 console errors |
| Speed | `node tools/check_game_speed.mjs`: 1280 px 303 ms first frame, 60 fps; 390 px 175 ms, 60 fps; 0 errors (#145) |
| Gallery and park link to game | #142 |
| README section | #144 |
| Playtest by other family | `game/PLAYTEST.md` (#148, seat 2, Gemini): playable, 0 console errors; two issues found: ground shadow seam (open), no loading label on Start Shift (fix in #150) |
| Retros | not done yet |
