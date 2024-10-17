from math import sin, cos


def discretize(func, domain):
    values = [ func(x) for x in domain ]
    return list(zip(domain, values))


def polar_to_cartesian(t, r):
    r = float(r)
    t = float(t)
    return r * cos(t), r * sin(t)


def discretize_polar(func, theta_vals):
    polar_vals = discretize(func, theta_vals)
    cartesian_vals = [ polar_to_cartesian(t, r) for t, r in polar_vals ]
    return cartesian_vals


