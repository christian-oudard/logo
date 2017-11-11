# TODO
# - record ribbon edge arcs
# - find intersections between arcs
# - show overlap by removing arc segments


from collections import namedtuple

import numpy as np
import mpmath
import cairo

from crossovers import calculate_crossovers

tau = 2 * np.pi

Arc = namedtuple('Arc', ['center', 'radius', 'angle1', 'angle2'])


def main():
    arcs = logo_arcs()

    # Create cairo SVG surface.
    width, height = (500, 500)
    surface = cairo.SVGSurface('output.svg', width, height)
    cr = cairo.Context(surface)

    # Set a view box ranging from -4 to +4 in both axes.
    cr.translate(width/2, height/2)
    cr.scale(width/8, height/8)
    cr.rotate(-tau/4)

    # Draw.
    cr.set_source_rgb(0, 0, 0)
    cr.set_line_width(0.05)
    for arc in arcs:
        cr.arc(
            *arc.center,
            arc.radius,
            arc.angle1,
            arc.angle2,
        )
        cr.stroke()

    surface.finish()


def dot(cr, p):
    cr.save()
    cr.set_source_rgb(0.7, 0, 0)
    cr.arc(*p, 0.05, 0, tau)
    cr.fill()
    cr.restore()


def logo_arcs():
    crossovers = np.array([ sympy_polar_to_rect(p) for p in calculate_crossovers() ])
    result = []

    # Draw outer arcs.
    for i in range(0, 14, 2):
        inner = crossovers[i]
        outer1 = crossovers[(i-1) % 14]
        outer2 = crossovers[(i+1) % 14]
        result.extend(ribbon_arcs(arc_center_a_b(inner, outer1, outer2)))

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
        result.extend(ribbon_arcs(arc_center_a_b(center1, inner1, outer)))

        mid2 = midpoint(inner2, outer)
        tangent2 = perp(outer - inner2)
        center2 = intersect_lines(
            outer, inner1,
            mid2, mid2 - tangent2,
        )
        result.extend(ribbon_arcs(arc_center_a_b(center2, outer, inner2)))

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
        result.extend(ribbon_arcs(arc_center_a_b(center, inner2, inner1)))

    return result


def arc_center_a_b(center, a, b):
    radius = np.linalg.norm(a - center)
    angle1 = heading_from(center, a)
    angle2 = heading_from(center, b)
    return Arc(center, radius, angle1, angle2)


def ribbon_arcs(arc, width=0.8):
    return (
        Arc(arc.center, arc.radius + width/2, arc.angle1, arc.angle2),
        Arc(arc.center, arc.radius - width/2, arc.angle1, arc.angle2),
    )


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


def intersect_circles(center1, radius1, center2, radius2):
    radius1 = abs(radius1)
    radius2 = abs(radius2)

    if radius2 > radius1:
        return intersect_circles(center2, radius2, center1, radius1)

    transverse = vec.vfrom(center1, center2)
    dist = vec.mag(transverse)

    # Check for identical or concentric circles. These will have either
    # no points in common or all points in common, and in either case, we
    # return an empty list.
    if points_equal(center1, center2):
        return []

    # Check for exterior or interior tangent.
    radius_sum = radius1 + radius2
    radius_difference = abs(radius1 - radius2)
    if (
        float_equal(dist, radius_sum) or
        float_equal(dist, radius_difference)
    ):
        return [
            vec.add(
                center1,
                vec.norm(transverse, radius1)
            ),
        ]

    # Check for non intersecting circles.
    if dist > radius_sum or dist < radius_difference:
        return []

    # If we've reached this point, we know that the two circles intersect
    # in two distinct points.
    # Reference:
    # http://mathworld.wolfram.com/Circle-CircleIntersection.html

    # Pretend that the circles are arranged along the x-axis.
    # Find the x-value of the intersection points, which is the same for both
    # points. Then find the chord length "a" between the two intersection
    # points, and use vector math to find the points.
    dist2 = vec.mag2(transverse)
    x = (dist2 - radius2**2 + radius1**2) / (2 * dist)
    a = (
        (1 / dist) *
        sqrt(
            (-dist + radius1 - radius2) *
            (-dist - radius1 + radius2) *
            (-dist + radius1 + radius2) *
            (dist + radius1 + radius2)
        )
    )
    chord_middle = vec.add(
        center1,
        vec.norm(transverse, x),
    )
    perp = vec.perp(transverse)
    return [
        vec.add(chord_middle, vec.norm(perp, a / 2)),
        vec.add(chord_middle, vec.norm(perp, -a / 2)),
    ]


def sympy_polar_to_rect(p):
    """Convert points from symbolic polar to numeric rectangular coordinates."""
    r, theta = p
    rect = mpmath.rect(float(r), float(theta))
    return np.array([float(rect.real), float(rect.imag)])


if __name__ == '__main__':
    main()
