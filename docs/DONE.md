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
| Motion review | not run beyond the human and reptile strips in `docs/motion` |
| Gallery clip check | `node tools/check_gallery_clips.mjs` on the live URL, 2026-11-15 15:10 JST: 20 skeletons, one asset each, every clip button clicked and became active, Animated tab 566 cards, 0 console errors. Oddity: insect, arachnid and mollusc assets list a `Swim` clip next to `Crawl`; the motion review should look at it. |
| README rigs section | not checked here |
| Retros | not yet |
