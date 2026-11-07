# Blender skills (headless) — read this first

Two third-party packs, copied **unmodified** and picked by the owner for a toy-style 3D zoo:

- **`el4cteo/`** — the main pack: 15 skills **with runnable scripts** from [EL4CTEO/blender-skills](https://github.com/EL4CTEO/blender-skills) at commit `fb92cfb` (MIT, see `el4cteo/LICENSE`). Written for Blender 5.2 and headless use. Start with `el4cteo/blender-core/SKILL.md`.
- **`arjun988/`** — style and budget notes only: low-poly, cartoon, stylized and creature guides plus four shared references (poly-count budgets, naming, validation checklist, asset pipeline) from [arjun988/blender-skills](https://github.com/arjun988/blender-skills) at commit `904f095` (MIT, see `arjun988/LICENSE`).

Credit: EL4CTEO, arjun988 and their contributors.

## Headless adapter (overrides the skills where they disagree)

- **No window, no MCP.** Both packs mention blender-mcp; there is none here. Run scripts headless:
  - a skill script: `python3 SKILLS/blender/el4cteo/blender-core/scripts/run_in_blender.py <script.py> -- <args>` (prints one JSON result), or
  - your own script: `blender -b -noaudio --factory-startup --python <script.py> -- <args>` (Blender 5.2 is on PATH).
- **Run the skill scripts, don't rewrite them.** Each `scripts/*.py` documents its flags in its docstring. Useful ones for the zoo:
  - `blender-asset-qa/scripts/qa_check.py` (profile `game`): z-fighting, floating parts, normals, UVs, materials, scale, ground contact. Use it inside `validate.py`.
  - `blender-asset-qa/scripts/review_shots.py` and `blender-lighting-lookdev/scripts/turntable.py`: review renders.
  - `blender-game-optimization/scripts/mesh_stats.py` (budgets) and `make_lods.py` (stretch: LODs).
  - `blender-retopology-uv/scripts/uv_pack.py` (palette-texture UVs), `blender-stylized-npr/scripts/toon_setup.py` (toy look), `blender-geometry-nodes/scripts/gn_builder.py` (procedural parts).
  - `blender-export-pipelines/scripts/export_asset.py` (target: web GLB).
  - `blender-character-rigging/` and `blender-animation/` (stretch: rigs, idle/walk loops).
- **No network, no third-party services.** Never use Sketchfab, Poly Haven, Hyper3D, Hunyuan3D or any downloader or AI generator mentioned in either pack. Everything is built from code in this repo.
- **Check by looking.** Render PNGs and look at them (or `hk-shot` the gallery page). "Viewport screenshot" means a headless render.
- **Export glTF with modifiers applied** (`export_apply=True`), otherwise modifiers are silently dropped.
- **Target is the web:** GLB for three.js, Y-up, meters. Ignore engine-specific steps (Unity, Unreal, Godot, Roblox).
- GOALS.md budgets and names win where the packs differ.
