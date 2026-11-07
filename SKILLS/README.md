# SKILLS

Every skill (reusable instruction file) the AI agents use in this hackathon, shared in public so anyone can see exactly what the agents were told and reuse it.

| Skill | What it is | Written by |
|---|---|---|
| [ai-hackathon](ai-hackathon/SKILL.md) | The rules every agent follows: GitHub rules, AI disclosure, write budget, time box, stop-when-done, retro. | Prepared by the owner with Claude Code before the start |
| [impeccable](impeccable/SKILL.md) | UI design skill against generic "AI slop" design (v4.8.0, Apache-2.0, by Paul Bakaus, github.com/pbakaus/impeccable). Text only: the `scripts/` launcher and engine run locally and are not committed; telemetry off. No edit hook: run `detect` before UI PRs. | Third-party skill added by the owner before the start (unmodified copy of SKILL.md + reference/) |
| [blender](blender/README.md) | Headless Blender skills: 15 skills **with runnable scripts** (QA, review renders, mesh stats, LODs, UV pack, toon look, Geometry Nodes builder, web export, rigging, animation) from EL4CTEO/blender-skills (MIT, `fb92cfb`), plus style/budget notes from arjun988/blender-skills (MIT, `904f095`). Read `blender/README.md` first: no MCP, no network. | Third-party packs (unmodified) + adapter note by the owner with Claude Code, before the start |
| [challenger](challenger/SKILL.md) | Role skill for the challenger seat: questions goals, plans, issues, decisions and PRs, and asks follow-ups until the answers show real thinking. | Owner with Claude Code (first used in pocket-wiki) |
| [de-ai](de-ai/SKILL.md) | Plain-language writing: detect and remove "AI tone" from user-facing text, with a small detector (`scripts/detect.py`). | The owner's own writing rules (first used in pocket-wiki) |

## How this folder works
- **At the start** it holds the skills listed above. The owner added them together with GOALS.md.
- **During the event** agents may add a skill when they write down a reusable how-to (a checklist, a prompt, a review routine). Each one goes in `SKILLS/<kebab-name>/SKILL.md` through a normal PR and gets a row in the table above.
- **The rules skill is locked.** Agents never edit `SKILLS/ai-hackathon/`. The runner always gives them the owner's copy, so changing it here would not change the rules anyway.
- Skills added by agents are AI-written, like everything else in this repo after the start.

## Skill file format
```markdown
---
name: <kebab-name>
description: <one line: what it does and when to use it>
---
<the instructions>

Written by <seat>/<role> · <tool> · <model> in round <n>.
```
