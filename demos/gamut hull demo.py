import math, itertools, oklab, numpy as np
from matplotlib import pyplot as plt
from array import array

def rgb_hull(n: int):
    'returns 6n² + 2 points'
    inv = 1 / n

    yield (0.0, 0.0, 0.0)

    for pi in range(n):
        pi *= inv
        ni = 1.0 - pi

        for pj in range(n):
            pj *= inv
            nj = 1.0 - pj
            
            yield ( ni,  pj, 0.0)
            yield (0.0,  ni,  pj)
            yield ( pj, 0.0,  ni)
            yield ( pi,  nj, 1.0)
            yield (1.0,  pi,  nj)
            yield ( nj, 1.0,  pi)
    
    yield (1.0, 1.0, 1.0)

def rgb_hull_unscaled(n: int):
    'returns 6n² + 2 points'
    yield (0, 0, 0)

    for pi in range(n):
        ni = n - pi
        for pj in range(n):
            nj = n - pj
            yield (ni, pj,  0)
            yield ( 0, ni, pj)
            yield (pj,  0, ni)
            yield (pi, nj,  n)
            yield ( n, pi, nj)
            yield (nj,  n, pi)
    
    yield (n, n, n)

rgbs = list(rgb_hull(0xff))
labs = list(map(oklab.srgb_to_oklab, rgbs))
l, a, b = tuple(map(np.array, zip(*labs)))

fig = plt.figure()
ax = fig.add_subplot(projection="3d")
ax.scatter(a, b, l, c=rgbs, s=0.01)
ax.set_title("sRGB gamut hull in Oklab space")
ax.set_xlabel("a")
ax.set_ylabel("b")
ax.set_zlabel("l")
plt.show()
