from math import sqrt, cos, sin, tau as τ
import oklab
from matplotlib import pyplot

def sphere(n: int, centre=(0.5, 0.0, 0.0), radius=0.5):
    """
    Generate approximately equally-spaced points on a sphere
    using Fibonacci distribution.
    """

    φ = (1 + sqrt(5)) / 2

    x0, y0, z0 = centre

    for i in range(n):
        z = 1 - (2 * i + 1) / n
        θ = τ * i / φ

        r = sqrt(1 - z*z)
    
        yield (
            x0 + radius * r * cos(θ),
            y0 + radius * r * sin(θ),
            z0 + radius * z,
        )

unclamped = list(sphere(2 ** 16))
l, a, b = list(zip(*unclamped))
clamped = list(map(oklab.clamp, unclamped))
l_, a_, b_ = list(zip(*clamped))
clamped_rgbs = list(map(oklab.lab_to_rgb, clamped))

fig = pyplot.figure()
ax = fig.add_subplot(projection="3d")

ax.scatter(a, b, l, c=clamped_rgbs, s=0.2)
ax.scatter(a_, b_, l_, c=clamped_rgbs, s=0.2)
ax.set_xlabel("a")
ax.set_ylabel("b")
ax.set_zlabel("l")
pyplot.show()
