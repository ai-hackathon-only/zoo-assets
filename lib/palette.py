"""The one shared colour palette. Every asset UV-maps its faces onto swatches of palette/palette.png.

8 columns x 4 rows, 8 px per swatch (64 x 32 px). Add colours only at the end (keeps old UVs valid).
Regenerate the PNG: blender -b -noaudio --factory-startup --python lib/palette.py
"""
COLS, ROWS, PX = 8, 4, 8
COLOURS = [  # name, hex (sRGB)
    ("white", "f4f1ea"), ("cream", "efe0b9"), ("sand", "d9bf86"), ("tan", "c49a5e"),
    ("orange", "e8892b"), ("rust", "b5562a"), ("brown", "7a4b2a"), ("dark_brown", "4a2e1c"),
    ("black", "26231f"), ("charcoal", "4b4a48"), ("grey", "8a8986"), ("light_grey", "c2c1bd"),
    ("pink", "f0a6a6"), ("red", "d0423a"), ("maroon", "7d2a2e"), ("yellow", "f2c933"),
    ("lime", "a9cf4a"), ("leaf", "5f9e3a"), ("forest", "2f6b34"), ("olive", "7e7d3c"),
    ("teal", "2f9c95"), ("sky", "7cc4e8"), ("water", "3f86c4"), ("navy", "28406e"),
    ("purple", "7b5ea7"), ("lavender", "b9a7d9"), ("skin_1", "f3cfb0"), ("skin_2", "d9a37c"),
    ("skin_3", "b07a52"), ("skin_4", "7d5034"), ("skin_5", "4f3222"), ("gold", "d4a640"),
]
INDEX = {n: i for i, (n, _) in enumerate(COLOURS)}


def rgb(name):
    h = COLOURS[INDEX[name]][1]
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def swatch(name):
    """(u_centre, v_centre, half_size) of a colour in UV space. Row 0 is the top row of the PNG."""
    i = INDEX[name]
    c, r = i % COLS, i // COLS
    return ((c + .5) / COLS, 1 - (r + .5) / ROWS, .5 / max(COLS, ROWS) * 0.5)


def write_png(path):
    import bpy
    w, h = COLS * PX, ROWS * PX
    img = bpy.data.images.new("palette", w, h, alpha=False)
    px = [0.0] * (w * h * 4)
    for y in range(h):
        for x in range(w):
            r = ROWS - 1 - y // PX  # Blender rows go bottom-up
            i = r * COLS + x // PX
            col = rgb(COLOURS[i][0]) if i < len(COLOURS) else (1, 0, 1)
            px[(y * w + x) * 4:(y * w + x) * 4 + 4] = (*col, 1.0)
    img.pixels = px
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()


if __name__ == "__main__":
    import os
    write_png(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "palette", "palette.png"))
