"""Animal variants made by the same generators: <id>_baby and <id>_rare (GOALS round 2).

A variant row in assets.json has `variant_of` (adult id), `variant` ("baby" or "rare") and copies the
adult's generator and params. lib/zoo.py applies the variant around the generator call:
- rare: every colour the generator paints goes through a recolour map (a preset name or a dict), so the
  mutation still uses the one shared palette.
- baby: the generator builds the animal at the baby's size_m, then zoo.finish() scales the head parts up
  (bigger head and eyes), shortens the legs and fits the result back to size_m.
Rows are written by tools/make_variants.py; rebuild them with build_all.py like any other asset.
"""
from lib import palette

DARK = {"black", "charcoal", "dark_brown"}
LIGHT = {"white", "cream", "sand", "yellow", "gold", "light_grey", "pink", "skin_1"}

# name -> function(colour) -> colour
PRESETS = {
    # no pigment: pale coat, pink eyes and nose, marks fade to cream
    "albino": lambda c: "pink" if c == "black" else "cream" if c in DARK | {"brown", "rust", "maroon"} else "white",
    # too much pigment: black coat, marks stay just visible as charcoal
    "melanistic": lambda c: "charcoal" if c in DARK or c in LIGHT else "black",
    # golden / strawberry morph: dark marks turn tan, warm coats turn gold
    "golden": lambda c: "tan" if c in DARK else "gold" if c in {"orange", "rust", "brown", "tan", "yellow", "sand"}
    else c,
    # blue morph (birds, frogs): warm colours turn sky/teal
    "blue": lambda c: {"red": "sky", "maroon": "navy", "orange": "teal", "yellow": "sky", "lime": "teal",
                       "leaf": "teal", "forest": "navy", "pink": "lavender", "gold": "sky"}.get(c, c),
}

BABY_SCALE = 0.45       # baby size_m = adult size_m * this
BABY_HEAD = 1.4         # head parts grow by this about the neck joint
BABY_LEG = 0.8          # parts below the torso are squashed in Z by this


def recolour_fn(spec, body=None):
    """spec: preset name or {colour: colour}; body: the adult's coat colour (params.body).
    Returns colour -> colour (unknown names pass through). Albino keeps pink eyes only when the coat
    is not black, else a black coat would turn pink."""
    if spec == "albino" and body in DARK:
        fn = lambda c: "white" if c == body else PRESETS["albino"](c)  # noqa: E731
    elif isinstance(spec, dict):
        fn = lambda c: spec.get(c, c)  # noqa: E731
    else:
        fn = PRESETS[spec]
    def safe(c):
        out = fn(c)
        return out if out in palette.INDEX else c
    return safe
