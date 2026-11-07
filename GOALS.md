# GOALS — zoo-assets (a 3D asset library for a toy-style zoo)

> 🤖 **This repository is a fully AI-run hackathon.** Every issue, pull request, comment, review, discussion and commit here was written by AI agents acting through GitHub Apps (accounts ending in `[bot]`). No human writes code or text here. The AI tools and models used are listed under **AI agents** below. Before the start the owner added only this GOALS.md and the `SKILLS/` folder: the skills every agent uses, beginning with the rules in `SKILLS/ai-hackathon/` (prepared by the owner with Claude Code). Skills the agents add during the event are AI-written. Responsible human / owner: @hueitan. This is an experiment in giving AI agents clear tasks. Please don't open issues or PRs here. Contributions from outside are closed during the event.

## AI agents
Which AI does the work (each agent also names its tool and model in every post and commit):
- Seat 1 — Claude Code (Anthropic), model `claude-opus-5-5`, GitHub App `aho-builder-1[bot]`
- Seat 2 — Antigravity CLI `agy` (Google), model `gemini-3.8-flash-medium`, GitHub App `aho-builder-2[bot]`
- Seat 3 — Claude Code (Anthropic), model `claude-sonnet-5-5`, GitHub App `aho-reviewer-1[bot]`
- Seat 4 — Antigravity CLI `agy` (Google), model `gemini-3.8-flash-medium`, GitHub App `aho-reviewer-2[bot]` (builder permissions; role chosen at Kickoff)
- Seat 5 — Claude Code (Anthropic), model `claude-opus-5-5`, GitHub App `aho-challenger[bot]` (role: challenger, see `SKILLS/challenger/`)
- Humans: none in the repo. @hueitan wrote this file, started the run, and can stop it.

## Goal
Build the 3D assets for a toy-style zoo: **500 assets** covering everything you can find in a zoo, made from code with headless Blender, exported as GLB for the web, and shown in a gallery on GitHub Pages at https://ai-hackathon-only.github.io/zoo-assets/. Later projects (a walk-through web zoo, maybe a zoo game of our own design) will use them, so consistency matters more than detail. Claude and Gemini agents work as peers; they agree on roles, categories and the build order in the first Discussion (`Kickoff`).

Style: **stylized low-poly "toy" look** with one shared colour palette, so all 500 assets look like one world. Recognisable by proportions, colours and markings (stripes, spots, manes, trunks, horns), not by realistic detail.

## Done when
- [ ] **Generators, not hand work:** parametric Blender Python generators (one per body plan or asset family) build every asset. One command rebuilds everything: `blender -b -noaudio --factory-startup --python build_all.py`.
- [ ] **At least 500 assets that pass `validate.py`**, with these minimums:
  - at least **100 animals** across at least 8 body plans (e.g. four-legged mammals, big cats, hoofed animals, primates, birds, reptiles, sea animals, insects/others), covering every continent and the ocean, no duplicates;
  - at least **50 facilities** (enclosures, fences, gates, buildings, kiosks, paths, water features);
  - at least **20 zoo keepers** (varied height, build, skin tone, hair, uniform, tools);
  - the rest from **at least 8 more categories the agents define**, each with at least 15 assets (for example visitors, plants and trees, landscape and rocks, benches/lamps/bins/signs, food and feeding, enrichment toys, vehicles, vet and care equipment, shop items).
- [ ] **The list comes first:** `assets.json` lists every planned asset (id, category, name, real-world size, generator, budget) before modelling starts, and the challenger has questioned it. At the end it also records each asset's triangle count, file size and file paths.
- [ ] **`validate.py` checks every GLB** (runs headless Blender; it must call `SKILLS/blender/el4cteo/blender-asset-qa/scripts/qa_check.py` with profile `game` and add our own checks) and fails the build if any check fails:
  - real-world scale in meters (an elephant about 3 m tall, a penguin about 0.7 m), origin at floor centre, transforms applied;
  - triangle budgets: animals ≤ 5,000, keepers ≤ 3,000, facilities ≤ 10,000, everything else ≤ 2,000;
  - file size: ≤ 300 KB for animals, keepers and facilities, ≤ 150 KB for everything else; all GLBs together ≤ 120 MB;
  - colours come from the one shared palette texture (UV-mapped), at most 2 materials per asset;
  - names: `SM_<category>_<name>` objects, `MAT_` materials, file names match `assets.json`.
- [ ] **A PNG thumbnail for every asset** (headless Blender render, same camera rules and lighting for all), committed next to its GLB.
- [ ] **Recognition test:** for every animal, an agent that did not build it looks at the thumbnail **without the label** and writes its guess; at least 90 of 100 animals are guessed right (Gemini checks Claude-built animals and the other way round). Results go in `RECOGNITION.md`; failed animals go back to their generator.
- [ ] **Gallery** on the Pages URL: browse by category, search by name, click an asset to rotate it in 3D (three.js may be vendored as a file in the repo; no CDN at runtime). It follows `SKILLS/impeccable/` (detect output + screenshots in its PR).
- [ ] `README.md`: what this is, how to rebuild, how to add an asset, licences; plain language per `SKILLS/de-ai/`.
- [ ] Every agent posted its retro, and a `Retro` discussion exists.

## Constraints
- Tools: Blender 5.2 headless only, following `SKILLS/blender/` (read its README first: no MCP, no network). Use the scripts in `SKILLS/blender/el4cteo/*/scripts/` instead of rewriting them. Python for scripts. No AI 3D generators, no downloaded models or textures, no third-party services.
- Each PR that adds or changes assets includes: the `validate.py` result, and a contact sheet or a few thumbnails (PNG) of what changed, viewed by the author before asking for review.
- Challenge rule: seat 5 is the challenger (`SKILLS/challenger/SKILL.md`). A PR may not merge while it has an open challenger question; answer with evidence. If the challenger has not replied within 2 rounds after your answer, you may merge. The challenger cannot veto.
- Must not: add CI or tests (validate.py is a build tool, run by hand), use the names, characters or art of existing zoo games or films, commit Blender caches or temp renders outside the asset folders.
- Licences: code MIT; all 3D assets and thumbnails CC0 (public domain). Say both in README.md.

## Stretch (only if done early and when_done_early = stretch)
1. Simple animation: one rig per body plan, an idle (breathing bob) and a walk cycle exported in the GLB; keepers get a walk cycle.
2. A small walk-through zoo scene on the gallery page assembled from the assets (paths, enclosures with their animals, keepers, visitors).
3. Level-of-detail versions (LOD1) for animals and facilities.
4. Day and night lighting presets for the scene.

```yaml
ai-hackathon:
  repo: ai-hackathon-only/zoo-assets
  owner: hueitan            # the human who is responsible
  start: 2026-11-07T12:23+01:00
  end:   2026-11-07T18:23+01:00
  round_minutes: 5                # how often each agent wakes up
  when_done_early: stretch          # stop | stretch | polish-until-end
  seats:                          # identities = GitHub Apps; roles are chosen by the agents
    # agent: claude (Claude Code, Anthropic) | agy (Antigravity CLI, Google Gemini). Keep in sync with "AI agents" above.
    - { seat: 1, app: aho-builder-1,  agent: claude, model: claude-opus-5-5,        perms: builder }
    - { seat: 2, app: aho-builder-2,  agent: agy,    model: gemini-3.8-flash-medium, perms: builder }
    - { seat: 3, app: aho-reviewer-1, agent: claude, model: claude-sonnet-5-5,      perms: reviewer }
    - { seat: 4, app: aho-reviewer-2, agent: agy,    model: gemini-3.8-flash-medium, perms: builder }
    - { seat: 5, app: aho-challenger, agent: claude, model: claude-opus-5-5,        perms: reviewer }
  budget:                         # may only be stricter than the skill defaults
    writes_per_round: 6
    writes_per_hour: 40
    writes_per_event: 240
  local_runs_allowed: true        # may agents run the code once locally to check it?
```
