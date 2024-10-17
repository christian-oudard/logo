import numpy as np
from scipy.optimize import fsolve

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from utility import (
    discretize,
    polar_to_cartesian,
    discretize_polar,
)


import vec

from braid_equation import (
    braid,
    braid_d1,
    braid_d2,
    intersections,
    curvature,
)

tau = np.pi * 2

theta_vals = np.linspace(0, 3*tau, 3*7*32, endpoint=False)


def polar_tangent(t, r, dr_dt):
    dx_dt = dr_dt * np.cos(t) - r * np.sin(t)
    dy_dt = dr_dt * np.sin(t) + r * np.cos(t)
    return dx_dt, dy_dt


def osculating_circle(t):
    r = braid(t)
    p = polar_to_cartesian(t, r)
    curv = curvature(t)
    radius = 1 / curv
    tangent = polar_tangent(t, braid(t), braid_d1(t))
    normal = vec.norm(vec.perp(tangent))
    center = vec.add(p, vec.mul(normal, radius))
    return p, center, radius


braid_points = discretize_polar(braid, theta_vals)
braid_points.append(braid_points[0])  # Close the loop.
intersection_points = list(vec.unique( polar_to_cartesian(t, r) for (t, r) in intersections ))
assert len(intersection_points) == 14

fig, ax = plt.subplots()
ax.set_aspect('equal')
size = 2
plt.xlim(-size, size)
plt.ylim(-size, size)

plt.plot(*zip(*intersection_points), 'ro')

step = (3/14) * tau
for t in [ i*step for i in range(3*14) ]:
    p, center, radius = osculating_circle(t)
    plt.plot(*p, 'go', markersize=2)
    ax.add_patch(Circle(center, radius=radius, edgecolor='green', facecolor='none', linewidth=0.5))

plt.plot(*zip(*braid_points))

plt.show()
