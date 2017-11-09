import sympy as sy

tau = 2 * sy.pi

# The knot crossover points are the self-intersections of the curve
# r = 7/3 + 7/3 * sin(theta)
# For even i in i*(tau/14), the intersection is at radius 11/6,
# and for odd i, the intersection is at radius 17/6.
def f(theta):
    return sy.Rational(7,3) + sy.cos(sy.Rational(7,3) * theta)

def calculate_crossovers():
    points = set()
    for i in range(3 * 14):
        theta = tau * i/14
        r = f(theta)
        p = (r, theta % tau)
        points.add(p)

    crossovers = []
    for i in range(14):
        theta = tau * i/14
        if i % 2 == 0:
            r = sy.Rational(11,6)
        else:
            r = sy.Rational(17,6)
        assert (r, theta) in points
        crossovers.append((r, theta))

    return crossovers
