"lightweight python implementation of Björn Ottosson's oklab colour space"

# typehinting tuple[float, float, float] everywhere is messy

import math

def _matvec(matrix, vector):
    'matrix × vector'
    return tuple(sum(a * b for a, b in zip(row, vector)) for row in matrix)

# mysterious numbers from https://github.com/w3c/csswg-drafts/issues/6642#issuecomment-945714988
M0     = ((+0.77849780, +0.34399940, -0.12249720),
          (+0.03303601, +0.93076195, +0.03620204),
          (+0.05092917, +0.27933344, +0.66973739))

# source of truth: https://bottosson.github.io/posts/oklab/#converting-from-linear-srgb-to-oklab
M2_inv = ((+1.0       , +0.3963377774, +0.2158037573),
          (+1.0       , -0.1055613458, -0.0638541728),
          (+1.0       , -0.0894841775, -1.2914855480))

# M0 / numpy.outer(numpy.dot(M0, ((3127/3290, 1, (10000-3127-3290)/3290))), (1, 1, 1))
M1     = ((+0.819022437996703   , +0.3619062600528904, -0.1288737815209879  ),
          (+0.03298365393238847 , +0.9292868615863434, +0.03614466635064236 ),
          (+0.04817718935962421 , +0.2642395317527308, +0.6335478284694309  ))

# numpy.linalg.inv(M2_inv)
M2     = ((+0.21045426827458136 , +0.7936177747300267, -0.004072043004608034),
          (+1.9779985323885083  , -2.428592241936286 , +0.450593709547778   ),
          (+0.025904042487658187, +0.7827717124269178, -0.808675754914576   ))

# numpy.linalg.inv(M1)
M1_inv = ((+1.2268798758459243  , -0.5578149944602171, +0.2813910456659647  ),
          (-0.04057574521480085 , +1.112286803280317 , -0.07171105806551636 ),
          (-0.07637293667466007 , -0.4214933324022432, +1.5869240198367816  ))

def xyz_to_lms(xyz):
    'convert (x, y, z) to (l, m, s)'
    return _matvec(M1, xyz)

def lms_to_xyz(lms):
    'convert (l, m, s) to (x, y ,z)'
    return _matvec(M1_inv, lms)

def lms_to_lab(lms):
    'convert (l, m, s) to (l, a, b)'
    return _matvec(M2, tuple(cone ** (1 / 3) for cone in lms))

def lab_to_lms(lab):
    'convert (l, a, b) to (l, m, s)'
    return tuple(cone ** 3 for cone in _matvec(M2_inv, lab))

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

def _clamp_chroma_reduction(lab):
    'clamp (l, a, b) into valid sRGB gamut by simply reducing the chroma. results in unoptimal yellows, and such'

def _clamp_optimal(lab):
    'clamp (l, a, b) into valid sRGB gamut by clamping to the nearest point. result is discontinuous iff the gamut is concave (a fact of topology)'

def _clamp_point_projection(lab, centre = (0.5, 0.0, 0.0)):
    """clamp (l, a, b) into gamut by reducing the euclidean distance to centre in oklab space. the output will be the intersection of the gamut hull and the ray from centre to lab

    assumptions
    -----------
    - centre is inside gamut
    - lab is outside gamut
    - all rays from centre have exactly one unique intersection with the hull
    """
    
    diff = tuple(a - b for a, b in zip(lab, centre))
    point = lambda t: tuple(a + b * t for a, b in zip(centre, diff))
    t_interior = 0.0
    t_exterior = 1.0
    iter_count = 0
    
    # find t numerically by bisecting optimization
    # we'll use this for now until we find a way to analytically intersect the hull and the ray.
    while True:
        t_mean = (t_interior + t_exterior) / 2
        
        if all(0.0 <= channel <= 1.0 for channel in lab_to_rgb(point(t_mean))):
            # inside gamut
            t_interior = t_mean
        else:
            # outside gamut
            t_exterior = t_mean
        
        if math.isclose(t_interior, t_exterior, abs_tol=1e-9):
            break
        
        if (iter_count := iter_count + 1) > 100:
            print(f'stopped clamping at {iter_count} iterations')
            break
    
    assert 0.0 < t_mean < 1.0
    
    return point(t_interior)
    
    # the better algorithm wouldve been to represent the hull as six parameterized surfaces, and intersect the ray with them. 
    # the surfaces are simply (r|g|b)(lab) = (0|1)

def clamp(*args, algorithm = 'point projection', **kwargs):
    if algorithm == 'point projection':
        return _clamp_point_projection(*args, **kwargs)

def rgb_to_hex(rgb: tuple) -> str:
    "convert (r, g, b) to '#rrggbb'"
    if not all(0.0 <= channel <= 1.0 for channel in rgb):
        raise ValueError(f"{rgb=} is out of gamut (violates 0 ≤ x ≤ 1). try rgb_to_hex(clamp(rgb))")
    
    r = round(rgb[0] * 0xFF)
    g = round(rgb[1] * 0xFF)
    b = round(rgb[2] * 0xFF)

    return f'#{r:02x}{g:02x}{b:02x}'

def hex_to_rgb(hex: str) -> tuple:
    "convert '#rrggbb' to (r, g, b)"
    hex = hex.lstrip('#')
    r = int(hex[0:2], base=0x10)
    g = int(hex[2:4], base=0x10)
    b = int(hex[4:6], base=0x10)
    return r, g, b

# from colour_science: colour.RGB_COLOURSPACES['sRGB']._derived_matrix_RGB_to_XYZ
RGB_TO_XYZ = ((+0.41239079926595934 , +0.35758433938387796, +0.1804807884018343 ),
              (+0.2126390058715103  , +0.7151686787677559 , +0.07219231536073371),
              (+0.019330818715591825, +0.11919477979462595, +0.9505321522496606 ))

# from colour_science: colour.RGB_COLOURSPACES['sRGB']._derived_matrix_XYZ_to_RGB
XYZ_TO_RGB = ((+3.2409699419045226  , -1.537383177570094  , -0.49861076029300344),
              (-0.9692436362808798  , +1.8759675015077206 , +0.04155505740717563),
              (+0.05563007969699364 , -0.20397695888897655, +1.0569715142428786 ))

def eotf_srgb(x, *, A = 12.92, C = 0.055, γ = 2.4, X = 0.04045):
    'convert gamma-encoded sRGB to linear sRGB'
    return x / A if x <= X else ((x + C) / (1 + C)) ** γ

def oetf_srgb(y, *, A = 12.92, C = 0.055, γ = 2.4, Y = 0.0031308):
    'convert linear sRGB to gamma-encoded sRGB'
    return y * A if y <= Y else (1 + C) * y ** (1 / γ) - C

def rgb_to_xyz(rgb):
    'convert (r, g, b) in sRGB to (x, y, z)'
    return _matvec(RGB_TO_XYZ, tuple(map(eotf_srgb, rgb)))

def xyz_to_rgb(xyz):
    'convert (x, y, z) to (r, g, b) in sRGB'
    return tuple(map(oetf_srgb, _matvec(XYZ_TO_RGB, xyz)))

# numpy.matmul(M1, _RGB_TO_XYZ)
RGB_TO_LMS = ((+0.4121764591770371  , +0.536273974269589  , +0.05144037229550145),
              (+0.2119091995880486  , +0.680717870982313  , +0.10739984387775395),
              (+0.08834481407213206 , +0.28185396309857735, +0.6302808688015095 ))

# numpy.matmul(_XYZ_TO_RGB, M1_inv)
LMS_TO_RGB = ((+4.077186823717315   , -3.307622521664363  , +0.2308591954879519 ),
              (-1.2685764914005104  , +2.609687114485009  , -0.34115574866072784),
              (-0.004196542231656323, -0.7033996761010274 , +1.7067960338654136 ))

def rgb_to_lms(rgb):
    'convert (r, g, b) in sRGB to (l, m, s)'
    return _matvec(RGB_TO_LMS, tuple(map(eotf_srgb, rgb)))

def lms_to_rgb(lms):
    'convert (l, m, s) to (r, g, b) in sRGB'
    return tuple(map(oetf_srgb, _matvec(LMS_TO_RGB, lms)))

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
def rgb_to_lab(rgb): return lms_to_lab(rgb_to_lms(rgb)) # rgb_encoded --eotf-> rgb_linear --RGB_TO_LMS-> lms --∛-> lms_cbrt --LMS_TO_LAB-> lab
def lab_to_rgb(lab): return lms_to_rgb(lab_to_lms(lab))
def rgb_to_lch(rgb): return lab_to_lch(lms_to_lab(rgb_to_lms(rgb)))
def lch_to_rgb(lch): return lms_to_rgb(lab_to_lms(lch_to_lab(lch)))
def xyz_to_lch(xyz): return lab_to_lch(lms_to_lab(xyz_to_lms(xyz)))
def lch_to_xyz(lch): return lms_to_xyz(lab_to_lms(lch_to_lab(lch)))
def lab_to_hex(lab): return rgb_to_hex(lms_to_rgb(lab_to_lms(lab)))
def hex_to_lab(hex): return lms_to_lab(rgb_to_lms(hex_to_rgb(hex)))
def lch_to_hex(lch): return rgb_to_hex(lms_to_rgb(lab_to_lms(lch_to_lab(lch))))
def hex_to_lch(hex): return lab_to_lch(lms_to_lab(rgb_to_lms(hex_to_rgb(hex))))
