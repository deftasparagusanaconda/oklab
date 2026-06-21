"lightweight python implementation of Björn Ottosson's oklab colour space"

# conversions between two non-oklab-related formats is discouraged
# causes combinatorial explosion of conversions
# except core, have only (oklch|oklab) <-> (hex|srgb|dp3|bt2020)

# math -------------------------------------------------------------------------

import math as _math

def _matvec(matrix, vector):
    'matrix × vector'
    return tuple(sum(a * b for a, b in zip(row, vector)) for row in matrix)

def _find_boundary(interior, exterior, membership, *, bisections: int = 32, final_interior: bool = True):
    'find point closest to boundary along interior-to-exterior'

    assert membership(interior) == True
    assert membership(exterior) == False

    e0, e1, e2 = exterior
    i0, i1, i2 = interior
    d0, d1, d2 = e0 - i0, e1 - i1, e2 - i2 # exterior - interior

    segment = lambda t: (i0 + d0 * t, i1 + d1 * t, i2 + d2 * t)

    t_low = 0.0
    t_high = 1.0
    
    for _ in range(bisections):
        t_mean = (t_low + t_high) * 0.5

        if membership(segment(t_mean)): 
            t_low = t_mean
        else:                           
            t_high = t_mean

    return segment(t_low if final_interior else t_high)

# core -------------------------------------------------------------------------

# mysterious numbers from https://github.com/w3c/csswg-drafts/issues/6642#issuecomment-945714988
M0     = (( 0.77849780,  0.34399940, -0.12249720),
          ( 0.03303601,  0.93076195,  0.03620204),
          ( 0.05092917,  0.27933344,  0.66973739))

# source of truth: https://bottosson.github.io/posts/oklab/#converting-from-linear-srgb-to-oklab
M2_inv = (( 1.0       ,  0.3963377774,  0.2158037573),
          ( 1.0       , -0.1055613458, -0.0638541728),
          ( 1.0       , -0.0894841775, -1.2914855480))

# M0 / numpy.outer(numpy.dot(M0, ((3127/3290, 1, (10000-3127-3290)/3290))), (1, 1, 1))
M1     = (( 0.819022437996703   ,  0.3619062600528904, -0.1288737815209879  ),
          ( 0.03298365393238847 ,  0.9292868615863434,  0.03614466635064236 ),
          ( 0.04817718935962421 ,  0.2642395317527308,  0.6335478284694309  ))

# numpy.linalg.inv(M2_inv)
M2     = (( 0.21045426827458136 ,  0.7936177747300267, -0.004072043004608034),
          ( 1.9779985323885083  , -2.428592241936286 ,  0.450593709547778   ),
          ( 0.025904042487658187,  0.7827717124269178, -0.808675754914576   ))

# numpy.linalg.inv(M1)
M1_inv = (( 1.2268798758459243  , -0.5578149944602171,  0.2813910456659647  ),
          (-0.04057574521480085 ,  1.112286803280317 , -0.07171105806551636 ),
          (-0.07637293667466007 , -0.4214933324022432,  1.5869240198367816  ))

def xyz_to_lms(xyz):
    'convert xyz (x, y, z) in CIEXYZ to cone-like lms (l, m, s)'
    return _matvec(M1, xyz)

def lms_to_xyz(lms):
    'convert cone-like lms (l, m, s) to xyz (x, y, z) in CIEXYZ'
    return _matvec(M1_inv, lms)

def lms_to_oklab(lms):
    'convert cone-like lms (l, m, s) to oklab (l, a, b)'
    return _matvec(M2, tuple(cone ** (1 / 3) for cone in lms))

def oklab_to_lms(lab):
    'convert oklab (l, a, b) to cone-like lms (l, m, s)'
    return tuple(cone ** 3 for cone in _matvec(M2_inv, lab))

# minor conversions ------------------------------------------------------------

def oklch_to_oklab(lch, *, radians: bool = False):
    'convert oklch (l, c, h) to oklab (l, a, b)'
    l, c, h = lch
    h = h if radians else _math.radians(h)
    a = c * _math.cos(h)
    b = c * _math.sin(h)
    return l, a, b

def oklab_to_oklch(lab, *, radians: bool = False):
    'convert oklab (l, a, b) to oklch (l, c, h)'
    l, a, b = lab
    c = _math.hypot(a, b)
    h = _math.atan2(b, a) % _math.tau
    h = h if radians else _math.degrees(h)
    return l, c, h

def srgb_to_hex(rgb: tuple, *, clip: bool = False) -> str:
    "convert rgb (r, g, b) in sRGB to rounded 8-bit hexadecimal '#rrggbb'"
    
    r, g, b = rgb

    r = round(r * 255)
    g = round(g * 255)
    b = round(b * 255)
    
    if clip:
        r = 0 if r < 0 else (255 if r > 255 else r)
        g = 0 if g < 0 else (255 if g > 255 else g)
        b = 0 if b < 0 else (255 if b > 255 else b)
    elif not(0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        raise ValueError(f"out of gamut: {rgb=}→({r}, {g}, {b}) …try rgb_to_hex(rgb, clip=True) or oklab_to_hex(clamp(srgb_to_oklab(rgb), gamut=gamut_srgb))")
    
    return f'#{r:02x}{g:02x}{b:02x}'

def hex_to_srgb(hex: str) -> tuple:
    "convert hexadecimal '#rrggbb' to rgb (r, g, b) in sRGB"
    
    hex = hex.lstrip('#')
    
    r = int(hex[0:2], base=0x10) / 255
    g = int(hex[2:4], base=0x10) / 255
    b = int(hex[4:6], base=0x10) / 255
    
    return r, g, b

# colour formats ---------------------------------------------------------------

# numpy.matmul(M1, colour_science.RGB_COLOURSPACES['sRGB']._derived_matrix_RGB_to_XYZ)
_SRGB_TO_LMS   = (( 0.4121764591770371  ,  0.536273974269589  ,  0.05144037229550145 ),
                  ( 0.2119091995880486  ,  0.680717870982313  ,  0.10739984387775395 ),
                  ( 0.08834481407213206 ,  0.28185396309857735,  0.6302808688015095  ))

# numpy.matmul(colour_science.RGB_COLOURSPACES['sRGB']._derived_matrix_XYZ_to_RGB, M1_inv)
_LMS_TO_SRGB   = (( 4.077186823717315   , -3.307622521664363  ,  0.2308591954879519  ),
                  (-1.2685764914005104  ,  2.609687114485009  , -0.34115574866072784 ),
                  (-0.004196542231656323, -0.7033996761010274 ,  1.7067960338654136  ))

# numpy.matmul(M1, colour_science.RGB_COLOURSPACES['Display P3'].matrix_RGB_to_XYZ)
_DP3_TO_LMS    = (( 0.48137985274995415 ,  0.4621183710113182 ,  0.05650177623872756 ),
                  ( 0.2288319418112446  ,  0.6532168193835679 ,  0.11795123880518774 ),
                  ( 0.08394575232299312 ,  0.22416527097756653,  0.6918889766994404  ))

# numpy.matmul(colour_science.RGB_COLOURSPACES['Display P3'].matrix_XYZ_to_RGB, M1_inv)
_LMS_TO_DP3    = (( 3.127768971361876   , -2.2571357625916404 ,  0.12936679122976508 ),
                  (-1.0910090184377976  ,  2.4133317103069216 , -0.3223226918691246  ),
                  (-0.02601080193857028 , -0.5080413317041671 ,  1.5340521336427375  ))

# numpy.matmul(M1, colour_science.RGB_COLOURSPACES['ITU-R BT.2020'].matrix_RGB_to_XYZ)
_BT2020_TO_LMS = (( 0.6167557848654442  ,  0.36019840122646346,  0.023045813908092305),
                  ( 0.2651330593926367  ,  0.6358393720678494 ,  0.0990275685395141  ),
                  ( 0.10010262952034829 ,  0.20390652261661452,  0.6959908478630372  ))

# numpy.matmul(colour_science.RGB_COLOURSPACES['ITU-R BT.2020'].matrix_XYZ_to_RGB, M1_inv)
_LMS_TO_BT2020 = (( 2.1399067304346517  , -1.246389493760618  ,  0.10648276332596684 ),
                  (-0.884735835757767   ,  2.1632309383612    , -0.2784951026034334  ),
                  (-0.048573746400444116, -0.45450314971409606,  1.50307689611454    ))

def _eotf_srgb(rgb, *, A = 12.92, C = 0.055, γ = 2.4, X = 0.04045):
    'convert gamma-encoded sRGB to linear sRGB'
    r, g, b = rgb
    return (r / A if r <= X else ((r + C) / (1 + C)) ** γ,
            g / A if g <= X else ((g + C) / (1 + C)) ** γ,
            b / A if b <= X else ((b + C) / (1 + C)) ** γ)

def _oetf_srgb(rgb, *, A = 12.92, C = 0.055, γ = 2.4, Y = 0.0031308):
    'convert linear sRGB to gamma-encoded sRGB'
    r, g, b = rgb
    return (r * A if r <= Y else (1 + C) * r ** (1 / γ) - C,
            g * A if g <= Y else (1 + C) * g ** (1 / γ) - C,
            b * A if b <= Y else (1 + C) * b ** (1 / γ) - C)

def _eotf_bt2020(rgb, *, α = 1.0992968268094157, β = 0.018053968510807):
    'convert gamma-encoded rec2020 to linear rec2020'
    r, g, b = rgb
    return (r / 4.5 if abs(r) < β * 4.5 else _math.copysign(((abs(r) + α - 1) / α) ** (1 / 0.45), r),
            g / 4.5 if abs(g) < β * 4.5 else _math.copysign(((abs(g) + α - 1) / α) ** (1 / 0.45), g),
            b / 4.5 if abs(b) < β * 4.5 else _math.copysign(((abs(b) + α - 1) / α) ** (1 / 0.45), b))

def _oetf_bt2020(rgb, *, α = 1.0992968268094157, β = 0.018053968510807):
    'convert linear rec2020 to gamma-encoded rec2020'
    r, g, b = rgb
    return (4.5 * r if abs(r) < β else _math.copysign(α * abs(r) ** 0.45 - (α - 1), r),
            4.5 * g if abs(g) < β else _math.copysign(α * abs(g) ** 0.45 - (α - 1), g),
            4.5 * b if abs(b) < β else _math.copysign(α * abs(b) ** 0.45 - (α - 1), b))

def srgb_to_oklab(rgb):
    'convert rgb (r, g, b) in sRGB to oklab (l, a, b)'
    return lms_to_oklab(_matvec(_SRGB_TO_LMS, _eotf_srgb(rgb)))

def oklab_to_srgb(lab):
    'convert oklab (l, a, b) to (r, g, b) in sRGB'
    return _oetf_srgb(_matvec(_LMS_TO_SRGB, oklab_to_lms(lab)))

def dp3_to_oklab(rgb):
    'convert rgb (r, g, b) in Display P3 to oklab (l, a, b)'
    return lms_to_oklab(_matvec(_DP3_TO_LMS, _eotf_srgb(rgb)))

def oklab_to_dp3(lab):
    'convert oklab (l, a, b) to rgb (r, g, b) in Display P3'
    return _oetf_srgb(_matvec(_LMS_TO_DP3, oklab_to_lms(lab)))

def bt2020_to_oklab(rgb):
    'convert (r, g, b) in ITU-R BT.2020 (rec2020) to oklab (l, a, b)'
    return lms_to_oklab(_matvec(_BT2020_TO_LMS, _eotf_bt2020(rgb)))

def oklab_to_bt2020(lab):
    'convert oklab (l, a, b) to rgb (r, g, b) in ITU-R BT.2020 (rec2020)'
    return _oetf_bt2020(_matvec(_LMS_TO_BT2020, oklab_to_lms(lab)))

def  oklab_to_xyz   (lab): return lms_to_xyz(oklab_to_lms(lab))
def    xyz_to_oklab (rgb): return lms_to_oklab(xyz_to_lms(rgb))

def  oklch_to_srgb  (lch): return oklab_to_srgb(oklch_to_oklab(lch))
def   srgb_to_oklch (rgb): return oklab_to_oklch(srgb_to_oklab(rgb))
def  oklch_to_dp3   (lch): return oklab_to_dp3(oklch_to_oklab(lch))
def    dp3_to_oklch (rgb): return oklab_to_oklch(dp3_to_oklab(rgb))
def  oklch_to_bt2020(lch): return oklab_to_bt2020(oklch_to_oklab(lch))
def bt2020_to_oklch (rgb): return oklab_to_oklch(bt2020_to_oklab(rgb))

def  oklab_to_hex   (lab): return srgb_to_hex(oklab_to_srgb(lab))
def    hex_to_oklab (hex): return srgb_to_oklab(hex_to_srgb(hex))
def  oklch_to_hex   (lch): return srgb_to_hex(oklab_to_srgb(oklch_to_oklab(lch)))
def    hex_to_oklch (hex): return oklab_to_oklch(srgb_to_oklab(hex_to_srgb(hex)))

# gamuts and clamping ----------------------------------------------------------

def gamut_srgb(lab) -> bool:
    'set of colours in sRGB gamut, represented as an indicator function of (l, a, b)'
    r, g, b = oklab_to_srgb(lab)
    return 0.0 <= r <= 1.0 and 0.0 <= g <= 1.0 and 0.0 <= b <= 1.0

def gamut_dp3(lab) -> bool:
    'set of colours in Display P3 gamut, represented as an indicator function of (l, a, b)'
    r, g, b = oklab_to_dp3(lab)
    return 0.0 <= r <= 1.0 and 0.0 <= g <= 1.0 and 0.0 <= b <= 1.0

def gamut_bt2020(lab) -> bool:
    'set of colours in Rec. 2020 gamut, represented as an indicator function of (l, a, b)'
    r, g, b = oklab_to_bt2020(lab)
    return 0.0 <= r <= 1.0 and 0.0 <= g <= 1.0 and 0.0 <= b <= 1.0

def clamp(lab, gamut, *, centre = None):
    'clamp (l, a, b) continuously to valid gamut in oklab space. centre is (l, 0, 0) by default (chroma reduction). if the gamut is concave, the result can be either continuous or optimal, but not both (a fact of topology)'
    
    if gamut(lab):
        return lab

    l = 0.9998 if lab[0] >= 0.9998 else lab[0]
    centre = (l, 0.0, 0.0) if centre is None else centre

    if not gamut(centre):
        raise ValueError(f'centre is not in gamut, i.e., {gamut}({centre}) is False')
    
    return _find_boundary(centre, lab, gamut)
