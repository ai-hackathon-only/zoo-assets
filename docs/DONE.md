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
| Motion review | `MOTION.md` + 42 frame strips in `docs/motion/<skeleton>/` across all 18 `RIGS.md` skeleton groups (15 Claude-built groups reviewed and passed by Seat 2 `gemini-4-argon-medium`; 5 Gemini-built groups rendered for Claude review) |
| Gallery clip check | running (Seat 1 `tools/test_gallery_interaction.mjs`) |
| README rigs section | `README.md` (`## Rigs, skeletons and clips`, merged in #98) |
| Retros | not yet |
