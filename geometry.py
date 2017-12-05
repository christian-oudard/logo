import numpy as np

from collections import namedtuple


tau = 2 * np.pi

Arc = namedtuple('Arc', ['center', 'radius', 'angle1', 'angle2'])


def print_arc(arc):
    print(
        'Arc(\n'
        '  center=({:.2f},{:.2f}),\n'
        '  radius={:.2f},\n'
        '  angle1={:.2f}t,\n'
        '  angle2={:.2f}t\n)'.format(
            *arc.center,
            arc.radius,
            arc.angle1 / tau,
            arc.angle2 / tau,
        )
    )


def arc_center_a_b(center, a, b):
    radius = mag(a - center)
    angle1 = heading(a - center)
    angle2 = heading(b - center)
    return Arc(center, radius, angle1, angle2)


def heading(v):
    x, y = v
    return np.arctan2(y, x) % tau


def midpoint(a, b):
    return (a + b) / 2


def perp(v):
    return np.array([-v[1], v[0]])


def mag(x):
    return np.linalg.norm(x)


def normalize(v):
    length = mag(v)
    if np.isclose(length, 0):
       return v
    return v / length


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

    transverse = center2 - center1
    dist = mag(transverse)

    # Check for identical or concentric circles. These will have either
    # no points in common or all points in common, and in either case, we
    # return an empty list.
    if np.isclose(dist, 0):
        return []

    # Check for exterior or interior tangent.
    radius_sum = radius1 + radius2
    radius_difference = abs(radius1 - radius2)
    if (
        np.isclose(dist, radius_sum) or
        np.isclose(dist, radius_difference)
    ):
        return [center1 + normalize(transverse) * radius1]

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
    x = (dist**2 - radius2**2 + radius1**2) / (2 * dist)
    a = (
        (1 / dist) *
        np.sqrt(
            (-dist + radius1 - radius2) *
            (-dist - radius1 + radius2) *
            (-dist + radius1 + radius2) *
            (dist + radius1 + radius2)
        )
    )
    chord_middle = center1 + normalize(transverse) * x
    p = normalize(perp(transverse)) * (a/2)
    return [
        chord_middle + p,
        chord_middle - p,
    ]


def intersect_arcs(arc1, arc2):
    points = intersect_circles(arc1.center, arc1.radius, arc2.center, arc2.radius)
    result = []
    for p in points:
        if (
            is_angle_between(
                heading(p - arc1.center),
                arc1.angle1,
                arc1.angle2,
            ) and
            is_angle_between(
                heading(p - arc2.center),
                arc2.angle1,
                arc2.angle2,
            )
        ):
            result.append(p)
    return result


def is_angle_between(theta, lo, hi):
    # Reference: https://fgiesen.wordpress.com/2015/09/24/intervals-in-modular-arithmetic/
    theta %= tau
    lo %= tau
    hi %= tau
    if (np.isclose(theta, hi) or np.isclose(theta, lo)):
        return False  # Endpoints are not included.
    else:
        return (theta - lo) % tau < (hi - lo) % tau


def break_arc(arc, points):
    assert len(points) == 2
    breaks = [ heading(p - arc.center) for p in points ]

    # Sort breaks along the segment.
    if not (
            is_angle_between(breaks[0], arc.angle1, breaks[1]) and
            is_angle_between(breaks[1], breaks[0], arc.angle2)
    ):
        breaks = [breaks[1], breaks[0]]

    return (
        Arc(arc.center, arc.radius, arc.angle1, breaks[0]),
        Arc(arc.center, arc.radius, breaks[0], breaks[1]),
        Arc(arc.center, arc.radius, breaks[1], arc.angle2),
    )
