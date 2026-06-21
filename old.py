def oetf_gamma(c, γ):
    return c ** γ

def eotf_gamma(c, γ):
    return root(c, γ)

def oetf_prophotorgb(c, *, e = 0.001953125):
    return c / 16 if c <= 16 * e else c ** 1.8

def eotf_prophotorgb(c, *, e = 0.001953125):
    return 16 * c if c <= e else root(c, 1.8)

def oetf_L_star(c, *, k = 24389 / 27):
    return (100 * c) / k if c <= 0.08 else ((c + 0.16) / 1.16) ** 3

def eotf_L_star(c, *, e = 216 / 24389, k = 24389 / 27):
    return (c * k) / 100 if c <= e else 1.16 * math.cbrt(c) - 0.16
