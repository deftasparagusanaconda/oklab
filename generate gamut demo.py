# its slow, but it works 
# 
# ... eventually

import oklab
from PIL import Image

W, H = 1920, 1080
img = Image.new('RGB', (W, H))

for y in range(H):
    l = 1 - y / (H - 1)            # lightness top→bottom
    for x in range(W):
        h = x / (W - 1) * 360       # hue left→right
        c = 0.125
        colour = oklab.lch_to_rgb((l, c, h))
        if not all(0 <= v <= 1 for v in colour):
            img.putpixel((x, y), (0, 0, 0))   # out-of-gamut → black
            continue
        r, g, b = (round(v * 255) for v in colour)
        img.putpixel((x, y), (r, g, b))

img.save('gamut demo.png')
