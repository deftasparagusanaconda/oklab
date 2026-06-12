"""python implementation of Björn Ottosson's oklab colour space (https://bottosson.github.io/posts/oklab/) (https://en.wikipedia.org/wiki/Oklab_color_space)

lch: (0.0, 0.0, 0.0) → (1.0, 1.0, 360.0)
rgb: (0, 0, 0) → (256, 256, 256)
hex: '#000000' → '#ffffff'
"""

import math

lms_to_lab_matrix = ( # M2
    (+0.2104542553, +0.7936177850, -0.0040720468), 
    (+1.9779984951, -2.4285922050, +0.4505937099), 
    (+0.0259040371, +0.7827717662, -0.8086757660))
lab_to_lms_matrix = ( # from numpy.linalg.inv, and hand-corrected so the first column is all +1.0
    (+1.0                , +0.39633779217376774, +0.2158037580607588 ),
    (+1.0                , -0.10556134232365633, -0.0638541747717059 ),
    (+1.0                , -0.08948418209496574, -1.2914855378640917 ))
lms_to_xyz_matrix = ( # from numpy.linalg.inv
    (+1.2270138511035211 , -0.5577999806518222 , +0.2812561489664678 ),
    (-0.0405801784232806 , +1.11225686961683   , -0.07167667866560119),
    (-0.0763812845057069 , -0.4214819784180127 , +1.5861632204407947 ))
xyz_to_lms_matrix = ( # M1
    (+0.8189330101, +0.3618667424, -0.1288597137),
    (+0.0329845436, +0.9293118715, +0.0361456387),
    (+0.0482003018, +0.2643662691, +0.6338517070))
lms_to_rgb_matrix = ( # from numpy.linalg.inv
    (+4.076741661347994  , -3.3077115904081933 , +0.23096992872942793),
    (-1.2684380040921763 , +2.6097574006633715 , -0.3413193963102196 ),
    (-0.00419608654183708, -0.7034186144594495 , +1.7076147009309446 ))
rgb_to_lms_matrix = (
    (+0.4122214708, +0.5363325363, +0.0514459929),
    (+0.2119034982, +0.6806995451, +0.1073969566),
    (+0.0883024619, +0.2817188376, +0.6299787005))

def matvec(matrix, vector):
    'matrix * vector'
    return type(vector)(math.sumprod(row, vector) for row in matrix)

def lch_to_lab(lch):
    'convert (l, c, h) to (l, a, b)'
    l, c, h = lch
    return l, c * math.cos(math.radians(h)), c * math.sin(math.radians(h))

def lab_to_lch(lab):
    'convert (l, a, b) to (l, c, h)'
    l, a, b = lab
    return l, math.hypot(a, b), math.degrees(math.atan2(b, a))

def lab_to_lms(lab):
    'convert (l, a, b) to (l, m, s)'
    return tuple(cone ** 3 for cone in matvec(lab_to_lms_matrix, lab))

def lms_to_lab(lms):
    'convert (l, m, s) to (l, a, b)'
    return matvec(lms_to_lab_matrix, tuple(math.cbrt(cone) for cone in lms))

def xyz_to_lms(xyz):
    'convert (x, y, z) to (l, m, s)'
    return matvec(xyz_to_lms_matrix, xyz)

def lms_to_xyz(lms):
    'convert (l, m, s) to (x, y ,z)'
    return matvec(lms_to_xyz_matrix, lms)

def rgb_to_lms(rgb):
    'convert (r, g, b) to (l, m, s)'
    return matvec(rgb_to_lms_matrix, tuple(channel / 255 for channel in rgb))

def lms_to_rgb(lms):
    'convert (l, m, s) to (r, g, b)'
    return tuple(round(channel * 255) for channel in matvec(lms_to_rgb_matrix, lms))

def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    "convert (r, g, b) to '#rrggbb'"
    return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

def hex_to_rgb(hex: str) -> tuple[int, int, int]:
    "convert '#rrggbb' to (r, g, b)"
    return tuple(int(hex.lstrip('#')[i:i+2], base=16) for i in (0, 2, 4))

# 10 converters have made a minimally connected graph of 6 formats
# lets derive the remaining 20 to complete the graph
def lch_to_lms(lch): return lab_to_lms(lch_to_lab(lch))
def lms_to_lch(lms): return lab_to_lch(lms_to_lab(lms))
def lab_to_xyz(lab): return lms_to_xyz(lab_to_lms(lab))
def xyz_to_lab(xyz): return lms_to_lab(xyz_to_lms(xyz))
def rgb_to_lab(rgb): return lms_to_lab(rgb_to_lms(rgb))
def lab_to_rgb(lab): return lms_to_rgb(lab_to_lms(lab))
def xyz_to_lch(xyz): return lab_to_lch(xyz_to_lab(xyz))
def lch_to_xyz(lch): return lab_to_xyz(lch_to_lab(lch))
def rgb_to_lch(rgb): return lab_to_lch(rgb_to_lab(rgb))
def lch_to_rgb(lch): return lab_to_rgb(lch_to_lab(lch))
def hex_to_lms(hex): return rgb_to_lms(hex_to_rgb(hex))
def lms_to_hex(lms): return rgb_to_hex(lms_to_rgb(lms))
def hex_to_lab(hex): return rgb_to_lab(hex_to_rgb(hex))
def lab_to_hex(lab): return rgb_to_hex(lab_to_rgb(lab))
def hex_to_lch(hex): return rgb_to_lch(hex_to_rgb(hex))
def lch_to_hex(lch): return rgb_to_hex(lch_to_rgb(lch))
def xyz_to_rgb(xyz): return lms_to_rgb(xyz_to_lms(xyz))
def rgb_to_xyz(rgb): return lms_to_xyz(rgb_to_lms(rgb))
def xyz_to_hex(xyz): return lms_to_hex(xyz_to_lms(xyz))
def hex_to_xyz(hex): return lms_to_xyz(hex_to_lms(hex))

# color spaces

def srgb_to_rgb(y):
    return y / 12.92 if y <= 0.04045 else ((y + 0.055) / 1.055) ** 2.4

def rgb_to_srgb(x):
    return x * 12.92 if x <= 0.0031308 else 1.055 * x ** (1/2.4) - 0.055
