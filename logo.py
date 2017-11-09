import numpy as np
import mpmath
import cairo

from crossovers import calculate_crossovers

tau = 2 * np.pi

def sympy_polar_to_rect(p):
    """Convert points from symbolic polar to numeric rectangular coordinates."""
    r, theta = p
    rect = mpmath.rect(float(r), float(theta))
    return np.array([float(rect.real), float(rect.imag)])

crossovers = np.array([ sympy_polar_to_rect(p) for p in calculate_crossovers() ])

def draw(cr, width, height):
    # Set a view box ranging from -4 to +4 in both axes.
    cr.translate(width/2, height/2)
    cr.scale(width/8, height/8)
    cr.rotate(-tau/4)

    # Draw outer arcs.
    for i in range(0, 14, 2):
        inner = crossovers[i]
        outer1 = crossovers[(i-1) % 14]
        outer2 = crossovers[(i+1) % 14]

        arc_center_a_b(cr, inner, outer1, outer2)
        cr.stroke()

    # Draw middle arcs.
    middleCenters = {}
    for i in range(0, 14, 2):
        outer = crossovers[(i+1) % 14]
        inner1 = crossovers[i]
        inner2 = crossovers[(i+2) % 14]

        mid1 = midpoint(inner1, outer)
        tangent1 = perp(outer - inner1)
        center1 = intersect_lines(
            outer, inner2,
            mid1, mid1 + tangent1,
        )
        arc_center_a_b(cr, center1, inner1, outer)
        cr.stroke()

        mid2 = midpoint(inner2, outer)
        tangent2 = perp(outer - inner2)
        center2 = intersect_lines(
            outer, inner1,
            mid2, mid2 - tangent2,
        )
        arc_center_a_b(cr, center2, outer, inner2)
        cr.stroke()

        middleCenters[i] = center1
        middleCenters[i + 1] = center2

    # Draw inner arcs.
    for i in range(1, 14, 2):
        inner1 = crossovers[(i-1) % 14]
        inner2 = crossovers[(i+1) % 14]

        # Get the middle arc circle centers which are perpendicular to the ends of the
        # inner arc, so the arcs will be cotangent.
        middleCenter1 = middleCenters[(i-2) % 14]
        middleCenter2 = middleCenters[(i+1) % 14]

        # These lines intersect at the inner arc center.
        center = intersect_lines(middleCenter1, inner1, middleCenter2, inner2)
        arc_center_a_b(cr, center, inner2, inner1)
        cr.stroke()

        # if debug {
        # 	dot(c, center)
        # 	line(c, center, inner1)
        # 	line(c, center, inner2)
        # 	circle(c, center, center.Sub(inner1).Norm(), thinLine)
        # }

    # Draw crossovers.
    # for p in crossovers:
    #     dot(cr, p)

def dot(cr, p):
    cr.save()
    cr.set_source_rgb(0.7, 0, 0)
    cr.arc(*p, 0.05, 0, tau)
    cr.fill()
    cr.restore()


def arc_center_a_b(cr, center, a, b):
    cr.save()

    radius = np.linalg.norm(a - center)
    start = heading_from(center, a)
    end = heading_from(center, b)

    ribbon_width = 0.8

    cr.set_source_rgb(0, 0, 0)
    cr.set_line_width(0.05)

    cr.arc(*center, radius + ribbon_width/2, start, end)
    cr.stroke()
    cr.arc(*center, radius - ribbon_width/2, start, end)
    cr.stroke()

    cr.restore()

def heading_from(a, b):
    x, y = (b - a)
    return np.arctan2(y, x)


def midpoint(a, b):
    return (a + b) / 2


def perp(v):
    return np.array([-v[1], v[0]])


def intersect_lines(a, b, c, d, segment=False):
    """
    Find the intersection of lines a-b and c-d.

    If the "segment" argument is true, treat the lines as segments, and check
    whether the intersection point is off the end of either segment.
    """
    # Reference:
    # http://geomalgorithms.com/a05-_intersect-1.html
    u = b - a
    v = d - c
    w = a - c

    u_perp_dot_v = perp(u).dot(v)
    if np.isclose(u_perp_dot_v, 0):
        return None  # We have collinear segments, no single intersection.

    v_perp_dot_w = perp(v).dot(w)
    s = v_perp_dot_w / u_perp_dot_v
    if segment and (s < 0 or s > 1):
        return None

    u_perp_dot_w = perp(u).dot(w)
    t = u_perp_dot_w / u_perp_dot_v
    if segment and (t < 0 or t > 1):
        return None

    return a + s*u


if __name__ == '__main__':
    width, height = (500, 500)
    surface = cairo.SVGSurface('output.svg', width, height)
    cr = cairo.Context(surface)
    draw(cr, width, height)
    surface.finish()
