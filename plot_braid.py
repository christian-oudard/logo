from braid_equation import (
    theta,
    braid_equation,
    braid_equation_d1,
    braid_equation_d2,
    intersections,
)

import numpy as np
import matplotlib.pyplot as plt


theta_vals = np.linspace(0, 12*np.pi, 3*7*64, endpoint=False)

def discretize(equation, var, domain):
    values = [equation.subs({var: x}).evalf() for x in domain]
    return list(zip(domain, values))


def polar_to_cartesian(t, r):
    r = float(r)
    t = float(t)
    return r * np.cos(t), r * np.sin(t)


def discretize_polar(equation, theta_vals):
    polar_vals = discretize(equation, theta, theta_vals)
    cartesian_vals = [polar_to_cartesian(t, r) for t, r in polar_vals]
    cartesian_vals.append(cartesian_vals[0])  # Close the loop.
    return cartesian_vals


braid_points = discretize_polar(braid_equation, theta_vals)
intersection_points = [ polar_to_cartesian(t.evalf(), r.evalf()) for (t, r) in intersections ]

plt.plot(*zip(*braid_points), label='braid')
plt.plot(*zip(*intersection_points), 'ro', label='intersection points')
plt.axis('equal')
plt.show()
