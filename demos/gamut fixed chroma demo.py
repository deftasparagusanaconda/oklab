# its slow, but it works 
# 
# ... eventually

import oklab
from PIL import Image

W, H = 720//2, 405//2
img = Image.new('RGB', (W, H))

for y in range(H):
    l = 1 - y / (H - 1)   # lightness top→bottom
    c = y / (H - 1)
    c = 1.5 * c if 3 * c < 2 else 3 - 3 * c
    c *= 0.2

    for x in range(W):
        h = x / (W - 1) * 360       # hue left→right
        colour = oklab.oklch_to_srgb((l, c, h))

        if not all(0 <= v <= 1 for v in colour):
            colour = oklab.oklab_to_srgb(oklab.clamp(oklab.oklch_to_oklab((l, c, h)), gamut=oklab.gamut_srgb))

        rgb = tuple(round(v * 255) for v in colour)
        img.putpixel((x, y), rgb)

img.save('gamut fixed chroma demo.png', optimize=True)
