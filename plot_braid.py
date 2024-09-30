from braid_equation import braid_equation, theta

import numpy as np
import matplotlib.pyplot as plt

theta_vals = np.linspace(0, 6*np.pi, 3*7*64, endpoint=False)
r_vals = [braid_equation.subs({theta: t}).evalf() for t in theta_vals]
cartesian_vals = [(r * np.cos(t), r * np.sin(t)) for t, r in zip(theta_vals, r_vals)]
cartesian_vals.append(cartesian_vals[0])  # Close the loop.

plt.plot(*zip(*cartesian_vals))
plt.axis('equal')
plt.show()
