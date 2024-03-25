from sympy import symbols, sin, solve, Rational

x0_val = Rational(1, 7)
w_val = Rational(6, 7)
thickness = Rational(1, 3)

theta, a, w, x0, y0 = symbols('theta a w x0 y0')

# Create a shaping function from a sinusoid. This function must intersect
# the points (-1,-1) and (+1,+1). We define a two-parameter family of sine
# curves.

def sinusoid(x):
    return a * sin(w * (x - x0)) + y0

# Solve the system of equations. This will get y0 and a in terms of x0 and w.
eq1 = sinusoid(-1) - (-1)  # (-1, -1)
eq2 = sinusoid(1) - 1  # (1, 1)
solutions = solve((eq1, eq2), (a, w, x0, y0))

a_sol, w_sol, x0_sol, y0_sol = solutions[0]
a_sol = a_sol.subs({x0: x0_val, w: w_val})
assert w_sol == w
assert x0_sol == x0
y0_sol = y0_sol.subs({x0: x0_val, w: w_val})


def shape(x):
    return sinusoid(x).subs({
        x0: x0_val,
        y0: y0_sol,
        a: a_sol,
        w: w_val,
    })


def braid(theta):
    return 1 + thickness * shape(sin(Rational(7, 3) * theta))


print(braid(theta))
