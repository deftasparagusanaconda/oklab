"""numerically careful implementation of Björn Ottosson's oklab colour space (https://bottosson.github.io/posts/oklab/) (https://en.wikipedia.org/wiki/Oklab_color_space)

lch: (0.0, 0.0, 0.0) → (1.0, 1.0, 360.0)
rgb: (0.0, 0.0, 0.0) → (256.0, 256.0, 256.0)
hex: '#000000' → '#ffffff'
"""

import math

# for xyz_to_lms
M1     = ((+0.8189330101, +0.3618667424, -0.1288597137),
          (+0.0329845436, +0.9293118715, +0.0361456387),
          (+0.0482003018, +0.2643662691, +0.6338517070))

# for lms_to_xyz
M1_inv = ((+1.2270138511035211 , -0.5577999806518222 , +0.2812561489664678 ),
          (-0.0405801784232806 , +1.11225686961683   , -0.07167667866560119),
          (-0.0763812845057069 , -0.4214819784180127 , +1.5861632204407947 ))

# for lms_to_lab
M2     = ((+0.2104542553, +0.7936177850, -0.0040720468), 
          (+1.9779984951, -2.4285922050, +0.4505937099), 
          (+0.0259040371, +0.7827717662, -0.8086757660))

# for lab_to_lms. hand-corrected so the first column is all +1.0
M2_inv = ((+1.0                , +0.39633779217376774, +0.2158037580607588 ),
          (+1.0                , -0.10556134232365633, -0.0638541747717059 ),
          (+1.0                , -0.08948418209496574, -1.2914855378640917 ))

# for rgb_to_lms
M3     = ((+0.4122214708, +0.5363325363, +0.0514459929),
          (+0.2119034982, +0.6806995451, +0.1073969566),
          (+0.0883024619, +0.2817188376, +0.6299787005))

# for lms_to_rgb
M3_inv = ((+4.076741661347994  , -3.3077115904081933 , +0.23096992872942793),
          (-1.2684380040921763 , +2.6097574006633715 , -0.3413193963102196 ),
          (-0.00419608654183708, -0.7034186144594495 , +1.7076147009309446 ))

def matmul(a, b):
    'matrix multiplication, pure python'
    if isinstance(b[0], (int, float)):
        # b is a vector, not a matrix
        return type(a)(math.sumprod(row, b) for row in a)
    else:
        # b is a matrix
        return type(a)(type(b[0])(math.sumprod(row, col) for col in zip(*b)) for row in a)

def lch_to_lab(lch):
    'convert (l, c, h) to (l, a, b)'
    l, c, h = lch
    h = math.radians(h)
    return l, c * math.cos(h), c * math.sin(h)

def lab_to_lch(lab):
    'convert (l, a, b) to (l, c, h)'
    l, a, b = lab
    return l, math.hypot(a, b), math.degrees(math.atan2(b, a))

def xyz_to_lms(xyz):
    'convert (x, y, z) to (l, m, s)'
    return matmul(M1, xyz)

def lms_to_xyz(lms):
    'convert (l, m, s) to (x, y ,z)'
    return matmul(M1_inv, lms)

def rgb_to_lms(rgb):
    'convert (r, g, b) to (l, m, s)'
    return matmul(M3, tuple(colour / 256 for colour in rgb))

def lms_to_rgb(lms):
    'convert (l, m, s) to (r, g, b)'
    return tuple(colour * 256 for colour in matmul(M3_inv, lms))

def lab_to_lms(lab):
    'convert (l, a, b) to (l, m, s)'
    return tuple(cone ** 3 for cone in matmul(M2_inv, lab))

def lms_to_lab(lms):
    'convert (l, m, s) to (l, a, b)'
    return matmul(M2, tuple(math.cbrt(cone) for cone in lms))

def xyz_to_lab(xyz):
    'convert (x, y, z) to (l, a, b). returns lms_to_lab(xyz_to_lms(xyz))'
    return lms_to_lab(xyz_to_lms(xyz))

def lab_to_xyz(lab):
    'convert (x, y, z) to (l, a, b). returns lms_to_xyz(lab_to_lms(lab))'
    return lms_to_xyz(lab_to_lms(lab))

def rgb_to_lab(rgb):
    'convert (r, g, b) to (l, a, b). returns lms_to_lab(rgb_to_lms(rgb))'
    return lms_to_lab(rgb_to_lms(rgb))

def lab_to_rgb(lab):
    'convert (l, a, b) to (r, g, b). returns lms_to_rgb(lab_to_lms(lab))'
    return lms_to_rgb(lab_to_lms(lab))

def xyz_to_lch(xyz):
    'convert (x, y, z) to (l, c, h). returns lab_to_lch(xyz_to_lab(xyz))'
    return lab_to_lch(xyz_to_lab(xyz))

def lch_to_xyz(lch):
    'convert (l, c, h) to (x, y, z). returns lab_to_xyz(lch_to_lab(lch))'
    return lab_to_xyz(lch_to_lab(lch))

def rgb_to_lch(rgb):
    'convert (r, g, b) to (l, c, h). returns lab_to_lch(rgb_to_lab(lch))'
    return lab_to_lch(rgb_to_lab(rgb))

def lch_to_rgb(lch):
    'convert (l, c, h) to (r, g, b). returns lab_to_rgb(lch_to_lab(lch))'
    return lab_to_rgb(lch_to_lab(lch))

def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    r, g, b = (round(x) for x in rgb)
    return f'#{r:02x}{g:02x}{b:02x}'

def hex_to_rgb(hex: str) -> tuple[float, float, float]:
    return tuple(int(hex.lstrip('#')[i:i+2], 16) / 255 for i in (0, 2, 4))

def hex_to_lms(hex: str):
    'convert hex to (l, m, s). returns rgb_to_lms(hex_to_rgb(hex))'
    return rgb_to_lms(hex_to_rgb(hex))

def lms_to_hex(lms) -> str:
    'convert (l, m, s) to hex. returns rgb_to_hex(lms_to_rgb(lms))'
    return rgb_to_hex(lms_to_rgb(lms))

def hex_to_lab(hex: str):
    'convert hex to (l, a, b). returns rgb_to_lab(hex_to_rgb(hex))'
    return rgb_to_lab(hex_to_rgb(hex))

def lab_to_hex(lab) -> str:
    'convert (l, a, b) to hex. returns rgb_to_hex(lab_to_rgb(lab))'
    return rgb_to_hex(lab_to_rgb(lab))

def hex_to_lch(hex: str):
    'convert hex to (l, c, h). returns rgb_to_lch(hex_to_rgb(hex))'
    return rgb_to_lch(hex_to_rgb(hex))

def lch_to_hex(lch) -> str:
    'convert (l, c, h) to hex. returns rgb_to_hex(lch_to_rgb(lch))'
    return rgb_to_hex(lch_to_rgb(lch))
