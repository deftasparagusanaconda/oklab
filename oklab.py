"python implementation of Björn Ottosson's oklab colour space (https://bottosson.github.io/posts/oklab/) (https://en.wikipedia.org/wiki/Oklab_color_space)"

# typehinting tuple[float, float, float] everywhere is messy

import math

def matvec(matrix, vector):
    'matrix × vector'
    return tuple(math.sumprod(row, vector) for row in matrix)

def root(a, b):
    'a ** (1 / b)'

    # this is proven to be bad in daamath
    #return math.exp(math.log(a) / b)

    return a ** (1 / b)

# xyz_to_lms
M1 = ((+0.8189330101, +0.3618667424, -0.1288597137),
      (+0.0329845436, +0.9293118715, +0.0361456387),
      (+0.0482003018, +0.2643662691, +0.6338517070))

# lms_to_xyz
M2 = ((+0.2104542553, +0.7936177850, -0.0040720468), 
      (+1.9779984951, -2.4285922050, +0.4505937099), 
      (+0.0259040371, +0.7827717662, -0.8086757660))

# lms_to_lab: numpy.linalg.inv(M1)
M1_inv = ((+1.2270138511035211, -0.5577999806518222 , +0.2812561489664678 ),
          (-0.0405801784232806, +1.11225686961683   , -0.07167667866560119),
          (-0.0763812845057069, -0.4214819784180127 , +1.5861632204407947 ))

# lab_to_lms: numpy.linalg.inv(M2); hand-corrected so the first column is all +1.0
M2_inv = ((+1.0               , +0.39633779217376774, +0.2158037580607588 ),
          (+1.0               , -0.10556134232365633, -0.0638541747717059 ),
          (+1.0               , -0.08948418209496574, -1.2914855378640917 ))

def xyz_to_lms(xyz):
    'convert (x, y, z) to (l, m, s)'
    return matvec(M1, xyz)

def lms_to_xyz(lms):
    'convert (l, m, s) to (x, y ,z)'
    return matvec(M1_inv, lms)

def lms_to_lab(lms):
    'convert (l, m, s) to (l, a, b)'
    return matvec(M2, tuple(math.cbrt(cone) for cone in lms))

def lab_to_lms(lab):
    'convert (l, a, b) to (l, m, s)'
    return tuple(cone ** 3 for cone in matvec(M2_inv, lab))

# extra ------------------------------------------------------------------------

# for convenience, we also want lch, rgb (srgb), hex (srgb), and p3, rec2020 in the future
# totally we have a directed graph of 8 formats and 56 possible conversions

def lch_to_lab(lch, *, degrees: bool = True):
    'convert (l, c, h) to (l, a, b)'
    l, c, h = lch
    h = math.radians(h) if degrees else h
    a = c * math.cos(h)
    b = c * math.sin(h)
    return l, a, b

def lab_to_lch(lab, *, degrees: bool = True):
    'convert (l, a, b) to (l, c, h)'
    l, a, b = lab
    c = math.hypot(a, b)
    h = math.atan2(b, a) % math.tau
    h = math.degrees(h) if degrees else h
    return l, c, h

def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    "convert (r, g, b) to '#rrggbb' (rounding to 8 bit)"
    #return '#' + ''.join(f'{round(channel * 255):02x}' for channel in rgb)
    return f'#{round(rgb[0] * 255):02x}{round(rgb[1] * 255):02x}{round(rgb[2] * 255):02x}'

def hex_to_rgb(hex: str) -> tuple[float, float, float]:
    "convert '#rrggbb' to (r, g, b)"
    return tuple(int(hex.lstrip('#')[i:i+2], base=16) / 255 for i in (0, 2, 4))

# from colour_science: colour.RGB_COLOURSPACES['sRGB']._derived_matrix_RGB_to_XYZ
_RGB_TO_XYZ = ((+0.41239079926595934 , +0.35758433938387796, +0.1804807884018343 ),
               (+0.2126390058715103  , +0.7151686787677559 , +0.07219231536073371),
               (+0.019330818715591825, +0.11919477979462595, +0.9505321522496606 ))

# from colour_science: colour.RGB_COLOURSPACES['sRGB']._derived_matrix_XYZ_to_RGB
_XYZ_TO_RGB = ((+3.2409699419045226  , -1.537383177570094  , -0.49861076029300344),
               (-0.9692436362808798  , +1.8759675015077206 , +0.04155505740717563),
               (+0.05563007969699364 , -0.20397695888897655, +1.0569715142428786 ))

def eotf_srgb(x, *, A = 12.92, C = 0.055, γ = 2.4, X = 0.04045):
    return x / A if x <= X else ((x + C) / (1 + C)) ** γ

def oetf_srgb(y, *, A = 12.92, C = 0.055, γ = 2.4, Y = 0.0031308):
    return y * A if y <= Y else math.fma(1 + C, root(y, γ), -C)

def rgb_to_xyz(rgb):
    'convert (r, g, b) in sRGB to (x, y, z)'
    return matvec(_RGB_TO_XYZ, tuple(map(eotf_srgb, rgb)))

def xyz_to_rgb(xyz):
    'convert (x, y, z) to (r, g, b) in sRGB'
    return tuple(map(oetf_srgb, matvec(_XYZ_TO_RGB, xyz)))

# numpy.matmul(M1, _RGB_TO_XYZ)
_RGB_TO_LMS = ((+0.4121764591770371  , +0.536273974269589  , +0.05144037229550145),
               (+0.2119091995880486  , +0.680717870982313  , +0.10739984387775395),
               (+0.08834481407213206 , +0.28185396309857735, +0.6302808688015095 ))

# numpy.matmul(_XYZ_TO_RGB, M1_inv)
_LMS_TO_RGB = ((+4.077186823717315   , -3.307622521664363  , +0.2308591954879519 ),
               (-1.2685764914005104  , +2.609687114485009  , -0.34115574866072784),
               (-0.004196542231656323, -0.7033996761010274 , +1.7067960338654136 ))

def rgb_to_lms(rgb):
    'convert (r, g, b) in sRGB to (l, m, s)'
    return matvec(_RGB_TO_LMS, tuple(map(eotf_srgb, rgb)))

def lms_to_rgb(lms):
    'convert (l, m, s) to (r, g, b) in sRGB'
    return tuple(map(oetf_srgb, matvec(_LMS_TO_RGB, lms)))

# conveniences -----------------------------------------------------------------

# with 6 formats, we now have 12 conversions out of a total of 6 * (6 - 1) = 30
# lets derive the remaining 18

def lab_to_xyz(lab): return lms_to_xyz(lab_to_lms(lab))
def xyz_to_lab(xyz): return lms_to_lab(xyz_to_lms(xyz))
def lch_to_lms(lch): return lab_to_lms(lch_to_lab(lch))
def lms_to_lch(lms): return lab_to_lch(lms_to_lab(lms))
def hex_to_lms(hex): return rgb_to_lms(hex_to_rgb(hex))
def lms_to_hex(lms): return rgb_to_hex(lms_to_rgb(lms))
def xyz_to_hex(xyz): return lms_to_hex(xyz_to_lms(xyz))
def hex_to_xyz(hex): return lms_to_xyz(hex_to_lms(hex))
def rgb_to_lab(rgb): return lms_to_lab(rgb_to_lms(rgb))
def lab_to_rgb(lab): return lms_to_rgb(lab_to_lms(lab))
def rgb_to_lch(rgb): return lab_to_lch(lms_to_lab(rgb_to_lms(rgb)))
def lch_to_rgb(lch): return lms_to_rgb(lab_to_lms(lch_to_lab(lch)))
def xyz_to_lch(xyz): return lab_to_lch(lms_to_lab(xyz_to_lms(xyz)))
def lch_to_xyz(lch): return lms_to_xyz(lab_to_lms(lch_to_lab(lch)))
def lab_to_hex(lab): return rgb_to_hex(lms_to_rgb(lab_to_lms(lab)))
def hex_to_lab(hex): return lms_to_lab(rgb_to_lms(hex_to_rgb(hex)))
def lch_to_hex(lch): return rgb_to_hex(lms_to_rgb(lab_to_lms(lch_to_lab(lch))))
def hex_to_lch(hex): return lab_to_lch(lms_to_lab(rgb_to_lms(hex_to_rgb(hex))))
