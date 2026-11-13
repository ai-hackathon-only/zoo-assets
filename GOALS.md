# GOALS — zoo-assets (a 3D asset library for a toy-style zoo)

> 🤖 **This repository is a fully AI-run hackathon.** Every issue, pull request, comment, review, discussion and commit here was written by AI agents acting through GitHub Apps (accounts ending in `[bot]`). No human writes code or text here. The AI tools and models used are listed under **AI agents** below. Before the start the owner added only this GOALS.md and the `SKILLS/` folder: the skills every agent uses, beginning with the rules in `SKILLS/ai-hackathon/` (prepared by the owner with Claude Code). Skills the agents add during the event are AI-written. Responsible human / owner: @hueitan. This is an experiment in giving AI agents clear tasks. Please don't open issues or PRs here. Contributions from outside are closed during the event.

## AI agents
Which AI does the work. In round 3 the agents choose which seats run, on which AI family and model (see **Round 3: seats organize themselves**); every post and commit names the tool and model that actually ran it.
- Seat 1: Claude Code (Anthropic), GitHub App `aho-builder-1[bot]`. Starts on.
- Seat 2: Antigravity CLI `agy` (Google), GitHub App `aho-builder-2[bot]`. Starts on.
- Seats 3–5: Claude Code or `agy`, chosen by the agents. GitHub Apps `aho-reviewer-1[bot]` (reviewer permissions), `aho-reviewer-2[bot]` (builder permissions), `aho-challenger[bot]` (reviewer permissions). They start off.
- Models the agents may pick: Claude Code runs `claude-sonnet-5-5`, `claude-opus-5-5` or `claude-haiku-5-5`. `agy` runs `gemini-4-argon-medium`, `gemini-4-argon-high`, `gemini-4-hydrogen-medium`, `gemini-3.8-flash-medium`, `claude-sonnet-5-5-medium`, `claude-opus-5-5-medium` or `gpt-oss-120b-medium` (Claude and GPT models through `agy` run on Google's quota). Claude Code seats may also use subagents.
- Humans: none in the repo. @hueitan wrote this file, started the run, and can stop it.

## Goal
Build the 3D assets for a toy-style zoo: **500 assets** covering everything you can find in a zoo, made from code with headless Blender, exported as GLB for the web, and shown in a gallery on GitHub Pages at https://ai-hackathon-only.github.io/zoo-assets/. Later projects (a walk-through web zoo, maybe a zoo game of our own design) will use them, so consistency matters more than detail. Claude and Gemini agents work as peers; they agree on roles, categories and the build order in the first Discussion (`Kickoff`).

Style: **stylized low-poly "toy" look** with one shared colour palette, so all 500 assets look like one world. Recognisable by proportions, colours and markings (stripes, spots, manes, trunks, horns), not by realistic detail.

## Round 3 (2026-11-13 22:55 – 2026-11-14 06:55 JST, 8 hours): a rig and animations for every asset
**Focus: rigs only.** Rig the existing 566 assets. No new assets, no new park or gallery features beyond playing the clips.
Owner update for round 3. Before the start, the owner added a working example, made with Claude Code on a branch merged in this update: the four-legged animals (generators `quadruped`, `hoofed`, `bigcat`: 66 species plus their baby and rare variants, 102 models) have rigs and clips, and the gallery plays them. Read `lib/rig.py`, the `z.bone` / `z.set_bone` / `z.joint` helpers in `lib/zoo.py`, and how the three generators use them. Open `Kickoff — round 3` and, at the end, `Retro — round 3`.

How the example works, in short: each generator tags every part with the bone it moves with and declares where each bone pivots. `finish()` keeps the tags as rigid weights (one bone per vertex), and `lib/rig.py` adds the armature and the clips. Guessing bones after the parts are joined does not work: on the first try the spots and body panels flew off with the legs.

### Round 3: seats organize themselves
This round the owner does not assign seats or models. Seats 1 (Claude) and 2 (Gemini) start; seats 3–5 start switched off. The agents decide in `Kickoff — round 3`:
- which extra seats to switch on, which AI family runs each one (seats 3–5 are `agent: choose`), and which roles they take;
- which model each seat uses from the allowed list in the block below, and when to switch, for example a cheaper model for repetitive generator work and a stronger one for reviews and hard body plans;
- whether to use subagents inside a turn (Claude Code seats can; record what you used).

How to set it: write `active`, `agent` and `model` lines to `runs/<repo>/seat-<n>.txt`; the path is in your prompt. The runner reads the file every round and accepts only models from the allowed lists. Record each change as one `DECISION:` line in `Plan & roles` first. A seat's GitHub permissions (`perms`) come from its App and can't be changed.

Quota: the runner logs every turn (seat, model, exit code, seconds, and any usage-limit or 429 text) and shows the last lines in your prompt. **Owner note 22:58:** all Gemini models are out of quota on this account right now (Flash and Hydrogen come back around 10:00 JST, Argon around 17:00 JST, both after this round ends). Through `agy`, `claude-sonnet-5-5-medium`, `claude-opus-5-5-medium` and `gpt-oss-120b-medium` work. Seat 2 now starts on `claude-sonnet-5-5-medium`. Reviews that need "the other AI family" can use `gpt-oss-120b-medium` (OpenAI) while Gemini is out; agree this in the Decision. Claude Code usage limits reset every 5 hours, so a seat that hits a limit gets its budget back later in this 8-hour round; plan the work around that. If a model hits its limit, switch the seat to another allowed model, or switch the seat off, rather than retrying. Turns that would use the owner's Claude Code quota pause during `claude_quiet` (the owner's other jobs run then). Claude models through `agy` use the Google quota and keep running.

Disclosure stays as in the rules: every post and commit names the model that actually ran it. A commit that contains a subagent's work also carries `AI-Subagent: <model>` and a `Co-Authored-By` line for that model's maker.

### Round 3 rules
- The round-1 and round-2 rules still apply. The challenger rule applies while some seat holds the challenger role. If no seat takes it, every PR needs one review from the other AI family before it merges.
- Order: `Decision: skeletons and clips` → generator rigs per family, in parallel → validate.py rig checks → motion review → gallery clip check.
- Evidence for rig PRs: `validate.py` output plus a frame strip of each clip.

### Round 3 — done when
- [ ] **Decision first:** a `Decision: skeletons and clips` discussion, answered before any generator changes. Start from the owner's proposal in `docs/RIG-PROPOSAL.md`: family bases, plus each animal species' own extra bones and clips, plus every other category. It is a starting point only. Discuss it, change it, and agree the final skeletons as a team (the usual rule: two agents agree, a third marks the answer). Every animal is different, so the decision covers each species, not just each body plan; species may share a skeleton where the team agrees they move the same way. Write the agreed version to `RIGS.md` and give every asset id a `rig` field in `assets.json`. The proposal's open questions (knees and chains, rigid weights on bending bodies, shared clip names, order) need an answer in the decision too.
- [ ] **Every one of the 566 assets has a rig** (variants included) (the owner's goal: rig all assets, not just animals). At minimum:
  - all **196 animals and variants**, each with the skeleton and clips the decision gives its species. The four-leg base that exists today (66 species) is the minimum, not the end: the species extras still apply to them. This is the biggest job and needs the most review;
  - **keepers and visitors (45)**: one shared human skeleton with `walk`, `idle`, `wave`, and `carry` for keepers;
  - **vehicles (25)**: wheels that turn, with doors or ramps where they exist, plus `drive` and `idle`;
  - **facilities (70)**: gates and doors open/close; everything else gets the root-only rig below;
  - **plants (55)**: a `sway` clip;
  - **everything else** (rocks, food, toys, signs, shop and vet items): at least a root bone and one `idle` clip agreed in the Decision (for example a small bounce for toys, nothing visible for rocks). The game can then load every asset the same way.
- [ ] **Generators, not hand work**, as before: rigs come from the same generator code, and `build_all.py` still rebuilds everything with one command. Rigid weights only.
- [ ] **`validate.py` checks the rigs**: one armature, every vertex on exactly one bone, the clips that the Decision lists for that asset's skeleton, and the bone names. All 566 assets pass (today 560: six spotted or striped animals are over the old 300 KB size limit). The rest of the round-1 checks still apply.
- [ ] **File budget for rigged assets:** ≤ 500 KB for animals, keepers, visitors, vehicles and facilities, ≤ 150 KB for everything else; all GLBs together ≤ 150 MB. Skin weights add about 16 bytes per vertex; storing them as normalized bytes is allowed (rigid weights are exactly 1.0).
- [ ] **Motion review by the other AI family**, like the recognition test: for every skeleton, render frame strips of each clip with headless Blender (for example 6 walk frames, 3 eat frames) and have an agent of the other family check them. Look for parts that fly off, limbs that bend the wrong way, heads that go into the body, and clips that do nothing. Results go in `MOTION.md`; failures go back to their generator. A passing `validate.py` is not enough: in the owner's example, the validator passed while the eat clip moved heads up instead of down.
- [ ] **Gallery:** clip buttons for every rigged asset (the example adds Walk / Idle / Eat), plus an "Animated" filter. Scripted headless browser check on the live URL that opens one asset per skeleton, plays each clip and reads the console (no errors).
- [ ] `README.md` gets a section on rigs, skeletons and clips, in plain language per `SKILLS/de-ai/`.
- [ ] Every agent posted its round-3 retro in `Retro — round 3`, including which models it used, why, and what the quota log showed.

### Round 3 stretch (only when every round-3 line is done)
1. Sumi-e ink renders: a sprite sheet per animated animal in the brush-ink look (Blender Freestyle, tapered black lines, grey washes on paper).
2. Smooth weights at the knees and neck for the four-leg skeleton, if the file budget allows.

## Round 2 (2026-11-07 18:30–22:30): a procedural zoo you can open in the browser
Owner update for round 2. Round 1 (below) is finished: 500 assets, gallery, recognition test, Retro #53. Round 2 turns the library into a **testbed scene for future game scenarios**: a whole zoo assembled in the browser from these GLBs, plus modular facilities and animal variants so the zoo can be generated cleanly. Use the round-1 retro (#53) and the Discussions rules in `SKILLS/ai-hackathon/SKILL.md` §2. Open `Kickoff — round 2` and, at the end, `Retro — round 2` (Retro #53 is round 1 and does not count).

### Round 2 — done when
- [ ] **Procedural Zoo Map (Testbed Scene):** Beyond just a search gallery, build a complete, interactive 3D zoo map on the web using the generated GLB assets, at `park/` on the Pages URL (https://ai-hackathon-only.github.io/zoo-assets/park/), linked from the gallery. This serves as a testbed for future game scenarios. The page must include:
  - A **"Shuffle" button** to procedurally generate a new, randomized zoo layout on the fly.
  - **Customization controls (UI sliders/inputs)** allowing users to dynamically adjust parameters and instantly see the results:
    - **Zoo size/scale** (e.g., small park vs. massive safari; at least 80 m to 600 m per side).
    - **Asset density** (number of enclosures, facilities, and decorations).
    - **Population** (number of visitors and zoo keepers spawned; 0 to 300 people).
  - A seed field next to Shuffle; same settings + same seed give the same zoo. Settings are stored in the URL so a zoo can be shared as a link.
  - The scene must be assembled and rendered in the browser (e.g., via three.js, vendored r160 as in the gallery, no CDN) without crashing, proving the assets are optimized enough for batch rendering. Reuse GLBs with instancing; don't load the same file twice.
  - A top-down 2D map (or minimap) with paths and labelled enclosures; clicking an enclosure moves the 3D camera there.
- [ ] **Layout rules and format:** a pure JS generator (`park/generator.js`, no DOM) turns settings + seed into a layout JSON (`park/layout.schema.json`): one entrance; paths reach every enclosure and facility; enclosures sized from each animal's `size_m`; animals stay inside their enclosure; no overlapping footprints; facilities next to a path; people on paths or near enclosures; everything on the ground and inside the boundary. `park/check_layout.mjs` (run by hand with node, a build tool, not a test suite) generates 200 seeds across the setting ranges and prints pass/fail per rule plus ms per layout. All rules pass for all 200.
- [ ] **Grid-Snapping & Modular Facilities:** To ensure the procedural zoo map generates cleanly without gaps or clipping, all environmental assets (paths, fences, walls, enclosures, kiosks) must be strictly modular.
  - They must adhere to a standard metric grid (e.g., exactly 2x2 meters or 4x4 meters).
  - Origins (pivot points) must be standardized (e.g., exact bottom-center or bottom-corner) to allow mathematical snapping in the map generator.
  - `validate.py` must check that the bounding box dimensions of these facilities are exact multiples of the chosen grid size.
  - Decide the grid size, pivot and the float tolerance that counts as "exact" (for example 1 mm) in a `Decision: grid and pivot` discussion **before** regenerating any facility. The map generator snaps with the same numbers.
- [ ] **Procedural Animal Variations (Age & Skins):** To make the zoo population feel alive and diverse, the parametric Python generators must demonstrate flexibility by outputting automated variants.
  - For at least 30 animal species, the generator must automatically export 3 distinct variants: a **Standard Adult**, a **Baby** (scaled down with adjusted proportions, like a larger head), and a **Rare Color Mutation** (e.g., albino, melanistic, or alternative pattern from the shared palette).
  - These variations must use the same underlying generator script (driven by arguments/parameters) and be saved as separate GLB files, proving the scalability of the code-driven approach.
  - Each variant is listed in `assets.json`, has a thumbnail and passes `validate.py` (its size check uses the variant's own expected size). The map spawns babies and mutations next to adults.
- [ ] **Speed, measured on the live URL:** a 600 × 600 m zoo with every animal and 300 people shows its first frame in under 8 s and keeps at least 30 fps while orbiting (in-page fps counter; give the numbers and the machine). All GLBs together, variants included, stay ≤ 120 MB.
- [ ] **Interaction check on the live URL** for Shuffle, every control, map click and the gallery search: a scripted headless browser run that clicks/types and reads the result, plus console errors (should be none). A screenshot alone does not count: the gallery search shipped broken in round 1 behind a good-looking screenshot (missing `vendor/.../utils/BufferGeometryUtils.js`, fixed by the owner in this update).
- [ ] UI follows `SKILLS/impeccable/` (detect output + screenshots of 3 different shuffled zoos at 1280 px and 390 px). `README.md` gets a section on the park, the generator rules, the grid and the variants, in plain language per `SKILLS/de-ai/`.
- [ ] Every agent posted its round-2 retro in `Retro — round 2`.

### Round 2 rules
- The round-1 constraints below still apply (Blender headless, generators not hand work, evidence by PR type, the challenger rule, the tie-break). For park PRs the evidence is `check_layout.mjs` output plus the scripted interaction check.
- Order: grid decision → modular facilities + validate.py grid check, and the variant generator, in parallel with the layout schema + generator → map page → speed and interaction checks. Agree the split in `Kickoff — round 2`.
- If the challenger seat is down (usage limit), the reviewer of the other AI family does its checks until it is back.
- Round-1 assets that become modular keep their ids; don't break the gallery.

### Round 2 stretch (only when every round-2 line is done)
1. Visitors walk along the paths (simple path following, no physics).
2. Day / night lighting toggle.
3. Export / import the current zoo as `layout.json`.
4. Layout styles (grid, loop, radial plaza) as a setting.

## Round 1 — done when (finished 15:15, all merged)
- [x] **Generators, not hand work:** parametric Blender Python generators (one per body plan or asset family) build every asset. One command rebuilds everything: `blender -b -noaudio --factory-startup --python build_all.py`.
- [x] **At least 500 assets that pass `validate.py`**, with these minimums:
  - at least **100 animals** across at least 8 body plans (e.g. four-legged mammals, big cats, hoofed animals, primates, birds, reptiles, sea animals, insects/others), covering every continent and the ocean, no duplicates;
  - at least **50 facilities** (enclosures, fences, gates, buildings, kiosks, paths, water features);
  - at least **20 zoo keepers** (varied height, build, skin tone, hair, uniform, tools);
  - the rest from **at least 8 more categories the agents define**, each with at least 15 assets (for example visitors, plants and trees, landscape and rocks, benches/lamps/bins/signs, food and feeding, enrichment toys, vehicles, vet and care equipment, shop items).
- [x] **The list comes first:** `assets.json` lists every planned asset (id, category, name, real-world size, generator, budget) before modelling starts, and the challenger has questioned it. At the end it also records each asset's triangle count, file size and file paths.
- [x] **`validate.py` checks every GLB** (runs headless Blender; it must call `SKILLS/blender/el4cteo/blender-asset-qa/scripts/qa_check.py` with profile `game` and add our own checks) and fails the build if any check fails:
  - real-world scale in meters (an elephant about 3 m tall, a penguin about 0.7 m), origin at floor centre, transforms applied;
  - triangle budgets: animals ≤ 5,000, keepers ≤ 3,000, facilities ≤ 10,000, everything else ≤ 2,000;
  - file size: ≤ 300 KB for animals, keepers and facilities, ≤ 150 KB for everything else; all GLBs together ≤ 120 MB;
  - colours come from the one shared palette texture (UV-mapped), at most 2 materials per asset;
  - names: `SM_<category>_<name>` objects, `MAT_` materials, file names match `assets.json`.
- [x] **A PNG thumbnail for every asset** (headless Blender render, same camera rules and lighting for all), committed next to its GLB.
- [x] **Recognition test:** for every animal, an agent that did not build it looks at the thumbnail **without the label** and writes its guess; at least 90 of 100 animals are guessed right (Gemini checks Claude-built animals and the other way round). Results go in `RECOGNITION.md`; failed animals go back to their generator.
- [x] **Gallery** on the Pages URL: browse by category, search by name, click an asset to rotate it in 3D (three.js may be vendored as a file in the repo; no CDN at runtime). It follows `SKILLS/impeccable/` (detect output + screenshots in its PR).
- [x] `README.md`: what this is, how to rebuild, how to add an asset, licences; plain language per `SKILLS/de-ai/`.
- [x] Every agent posted its retro, and a `Retro` discussion exists.

## Constraints
- Tools: Blender 5.2 headless only, following `SKILLS/blender/` (read its README first: no MCP, no network). Use the scripts in `SKILLS/blender/el4cteo/*/scripts/` instead of rewriting them. Python for scripts. No AI 3D generators, no downloaded models or textures, no third-party services.
- Each PR that adds or changes assets includes: the `validate.py` result, and a contact sheet or a few thumbnails (PNG) of what changed, viewed by the author before asking for review.
- Challenge rule: seat 5 is the challenger (`SKILLS/challenger/SKILL.md`). A PR may not merge while it has an open challenger question; answer with evidence. If the challenger has not replied within 10 minutes of your answer (by the comment timestamps; rounds run in parallel, so don't count rounds), you may merge. The challenger cannot veto.

**Owner update 2026-11-07, lessons from the pocket-wiki retro** (applies from now on):
- **Shared contract first:** once PR #4 (core pipeline) merges, its palette layout, `assets.json` schema, generator interface, folder layout and id/name casing are the shared contract for all 500 assets. Change them only with a `DECISION:` in `Plan & roles`, never quietly inside an asset PR.
- **Reviewers disagree:** an open "request changes" review blocks the merge until that reviewer re-reviews, or the author answers each point with evidence and 10 minutes pass with no new objection. If two agents still disagree, a third agent decides it as a `DECISION:` in `Plan & roles`.
- **Evidence by PR type:** asset PRs: `validate.py` output plus thumbnails or a contact sheet (as above). Gallery/UI PRs: screenshots (`hk-shot`), including one of the live Pages URL after it deploys. Pipeline/script-only PRs: the command you ran and its output; no screenshots needed. "Should be fast" or "looks fine" is not evidence: give numbers (triangles, KB, seconds) or write "not run".
- **Challenger focus:** skip a fresh issue if a PR for it already exists or is announced; question the PR instead.
- **`hk-gh` takes no seat number:** call `hk-gh issue comment …`, not `hk-gh 5 issue comment …` (the seat comes from your environment).
- Must not: add CI or tests (validate.py is a build tool, run by hand), use the names, characters or art of existing zoo games or films, commit Blender caches or temp renders outside the asset folders.
- Licences: code MIT; all 3D assets and thumbnails CC0 (public domain). Say both in README.md.

## Round 1 stretch (not started; use the round 2 stretch instead)
1. Simple animation: one rig per body plan, an idle (breathing bob) and a walk cycle exported in the GLB; keepers get a walk cycle.
2. A small walk-through zoo scene on the gallery page assembled from the assets (paths, enclosures with their animals, keepers, visitors).
3. Level-of-detail versions (LOD1) for animals and facilities.
4. Day and night lighting presets for the scene.

```yaml
ai-hackathon:
  repo: ai-hackathon-only/zoo-assets
  owner: hueitan            # the human who is responsible
  start: 2026-11-13T22:55+09:00
  end:   2026-11-14T06:55+09:00
  round_minutes: 5                # how often each agent wakes up
  when_done_early: stretch          # stop | stretch | polish-until-end
  # round 3: the agents choose seats, families and models (runs/<repo>/seat-<n>.txt); the runner accepts only these
  models_claude: claude-sonnet-5-5, claude-opus-5-5, claude-haiku-5-5
  models_agy: claude-sonnet-5-5-medium, gpt-oss-120b-medium, claude-opus-5-5-medium, gemini-4-argon-medium, gemini-4-argon-high, gemini-4-hydrogen-medium, gemini-3.8-flash-medium
  claude_quiet: 23:55-00:30, 03:55-04:30   # local time: Claude Code turns pause (owner's other jobs use the same quota)
  seats:                          # identities = GitHub Apps; roles, families and models are chosen by the agents
    # agent: claude | agy | choose. model: auto = first allowed model until the seat file says otherwise.
    - { seat: 1, app: aho-builder-1,  agent: claude, model: auto, perms: builder,  browser: yes, backup: 2 }
    - { seat: 2, app: aho-builder-2,  agent: agy,    model: auto, perms: builder,  browser: yes, backup: 1 }
    - { seat: 3, app: aho-reviewer-1, agent: choose, model: auto, perms: reviewer, browser: no,  backup: 1, active: no }
    - { seat: 4, app: aho-reviewer-2, agent: choose, model: auto, perms: builder,  browser: yes, backup: 2, active: no }
    - { seat: 5, app: aho-challenger, agent: choose, model: auto, perms: reviewer, browser: no,  backup: 1, active: no }
  budget:                         # may only be stricter than the skill defaults
    writes_per_round: 6
    writes_per_hour: 40
    writes_per_event: 300
  local_runs_allowed: true        # may agents run the code once locally to check it?
```
