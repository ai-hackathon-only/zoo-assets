#!/usr/bin/env python3
"""
Generate a contact sheet of representative modular facilities using Blender headless.
"""
import os
import subprocess
import sys

def main():
    script = """
import bpy, os

sample_ids = [
    'fence_wood_rail_straight', 'fence_chainlink_panel', 'fence_bamboo_panel', 'fence_wood_post',
    'wall_stone_perimeter_low', 'wall_glass_viewing_panel', 'wall_stone_perimeter_tall', 'gate_wooden_ranch_double',
    'building_public_restroom', 'building_first_aid_station', 'building_keeper_shed', 'building_staff_breakroom',
    'kiosk_beverage_bar', 'kiosk_ice_cream_cone', 'booth_visitor_info', 'platform_giraffe_feeding',
    'bridge_stone_arch', 'bridge_timber_footbridge', 'water_elephant_splash_pool', 'shelter_animal_night_brick'
]

cols = 4
rows = (len(sample_ids) + cols - 1) // cols
w, h = 160, 160
full_w, full_h = cols * w, rows * h

out_img = bpy.data.images.new('contact', full_w, full_h, alpha=True)
pixels = [1.0, 1.0, 1.0, 1.0] * (full_w * full_h)

for idx, aid in enumerate(sample_ids):
    c = idx % cols
    r = rows - 1 - (idx // cols)
    path = os.path.join('assets/facilities', f'{aid}.png')
    if not os.path.exists(path):
        continue
    src = bpy.data.images.load(os.path.abspath(path))
    src_pixels = list(src.pixels)
    sw, sh = src.size[0], src.size[1]
    for y in range(h):
        sy = int(y * sh / h)
        for x in range(w):
            sx = int(x * sw / w)
            src_i = (sy * sw + sx) * 4
            dst_x = c * w + x
            dst_y = r * h + y
            dst_i = (dst_y * full_w + dst_x) * 4
            pixels[dst_i:dst_i+4] = src_pixels[src_i:src_i+4]
    bpy.data.images.remove(src)

out_img.pixels = pixels
os.makedirs('docs/facilities', exist_ok=True)
out_img.filepath_raw = 'docs/facilities/contact_sheet.png'
out_img.file_format = 'PNG'
out_img.save()
print('SAVED docs/facilities/contact_sheet.png')
"""
    subprocess.run(["blender", "-b", "--python-expr", script], check=True)

if __name__ == "__main__":
    main()
