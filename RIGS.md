# RIGS: skeletons and clips (draft, from `Decision: skeletons and clips`, #94)

Status: draft until the decision (#94) has a marked answer. Starting point: `docs/RIG-PROPOSAL.md`; where this file differs, this file wins.

## Rules
- Every asset has a `root` bone at its floor centre and rigid weights (one bone per vertex).
- Every asset has `idle`. Every animal and every moving thing also has `move` (swim, walk, slither, fly, drive). A species name (`walk`, `swim`) stays as an alias clip with the same motion.
- `eat` is required for four-leg, upright, primate, bird, reptile and marine mammal. Fish, insect, arachnid, snake, mollusc have none.
- Clips loop: 24 frames (fast) or 48 frames (idle, slow) at 24 fps.
- Legs bend at the knee only for bears, panda, primates, birds, kangaroo and the species the proposal marks "2-bone". All other legs are one piece and swing. Chains (trunk, tail, spine) exist only where the proposal lists them.
- Snake, fish, moray, octopus bend in rigid segments. Smooth weights only if the stretch goal is reached.
- Baby and rare variants use their adult's `rig` id.

## The `rig` field in `assets.json`
One id per skeleton. A species with its own bones or clips gets `<family>.<species>` (for example `quadruped.elephant`). The tables below list bones and the clips validate.py requires for each id. Species extras (`spray`, `howl`, ...) are required only for the species id that lists them.

| Id | Required clips | Base bones |
|---|---|---|
| quadruped, hoofed, bigcat | idle, move, walk, eat | body, neck, head, tail, leg_FL/FR/BL/BR |
| upright | idle, move, eat | body, head, tail, arm_L/R, foot_L/R |
| primate | idle, move, eat, sit | hips, spine, chest, neck, head, upperarm/forearm L/R, thigh/shin L/R, tail |
| bird | idle, move, eat | body, neck, head, beak, wing_L/R, leg_L/R, tail |
| reptile | idle, move, eat | body, head, jaw, tail chain, 4 legs |
| snake | idle, move | spine chain, head, jaw |
| fish | idle, move | spine chain, tail, fin_L/R |
| marine | idle, move, eat | spine chain, fluke or flippers, head |
| insect | idle, move | thorax, abdomen, head, antenna_L/R, legs |
| arachnid | idle, move | body, 8 legs |
| mollusc (giant African snail) | idle, move | foot, shell, eyestalk_L/R |
| human | idle, move, wave, talk (keepers also carry) | hips, spine, chest, neck, head, upperarm/forearm L/R, thigh/shin L/R, prop |
| vehicle | idle, move | body, one bone per wheel |
| facility, gate or door | idle, open, close | door or gate bone |
| plant | idle, sway | trunk, crown |
| static | idle | root |

Scorpion and tarantula use `arachnid` and are built by `insect.py`. Species extras and the non-animal groups follow the tables in `docs/RIG-PROPOSAL.md` until the team edits them here.

Written by seat 1/rig-core · claude-sonnet-5-5 in round 8
