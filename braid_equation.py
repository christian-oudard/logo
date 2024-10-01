from sympy import (
    symbols,
    sin,
    cos,
    tan,
    solve,
    Rational,
    diff,
    pi,
)

tau = 2*pi

theta, a, w, x0, y0, ratio, thickness = symbols('theta a w x0 y0 ratio thickness')

# Create a shaping function from a sinusoid. This function must intersect
# the points (-1,-1) and (+1,+1). We define a two-parameter family of sine
# curves.
def sinusoid(x):
    return a * sin(w * (x - x0)) + y0


# Solve the system of equations. This will get y0 and a in terms of x0 and w.
def solve_shape():
    eq1 = sinusoid(-1) - (-1)  # (-1, -1)
    eq2 = sinusoid(1) - 1  # (1, 1)
    solutions = solve((eq1, eq2), (a, w, x0, y0))
    a_sol, w_sol, x0_sol, y0_sol = solutions[0]
    assert w_sol == w
    assert x0_sol == x0
    return a_sol, y0_sol


# Solving these equations is expensive, so we just write in the result.
# a_sol, y0_sol = solve_shape()
a_sol = 1 / (sin(w) * cos(w * x0))
y0_sol = tan(w * x0) / tan(w)
def shape(x):
    return sinusoid(x).subs({
        y0: y0_sol,
        a: a_sol,
    })


# Draw the circular braid with a shaped radial sine wave.
def braid(theta):
    # theta from 0 to 3*tau
    return 1 + thickness * shape(cos(ratio * theta))


braid_equation = braid(theta).subs({
    ratio: Rational(7, 3),
    thickness: Rational(1, 3),
    x0: Rational(1, 7),
    w: Rational(6, 7),
})

# Derivatives.
braid_equation_d1 = diff(braid_equation, theta)
braid_equation_d2 = diff(braid_equation_d1, theta)

# Intersections.
step = Rational(1/14) * tau
intersection_angles = [ i*step for i in range(3*14) if i % 3 == 1 ]
intersection_radiuses = [ braid_equation.subs(theta, t) for t in intersection_angles ]
intersections = list(zip(intersection_angles, intersection_radiuses))
assert len(intersections) == 14
