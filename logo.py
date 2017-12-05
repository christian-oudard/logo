# TODO
# - show overlap by removing arc segments

from collections import defaultdict

import numpy as np
import mpmath
import cairo

from crossovers import calculate_crossovers
from geometry import (
    Arc,
    arc_center_a_b,
    intersect_lines,
    intersect_arcs,
    break_arc,
    midpoint,
    perp,
    tau,
)


def main():
    crossovers = np.array([ sympy_polar_to_rect(p) for p in calculate_crossovers() ])
    arcs = logo_arcs(crossovers)
    arcs = ribbonize(arcs)
    arcs = break_arcs(arcs)

    # Remove every other crossing.
    # FIXME Arc ordering is weird.
    arcs = [
        a for (i, a) in enumerate(arcs)
        if i % 24 in [1, 2, 4, 5, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19, 21, 22]
    ]

    # Create cairo SVG surface.
    width, height = (640, 640)
    surface = cairo.SVGSurface('output.svg', width, height)
    cr = cairo.Context(surface)

    # Set a view box ranging from -4 to +4 in both axes.
    cr.translate(width/2, height/2)
    cr.scale(width/8, height/8)
    cr.rotate(-tau/4)

    # Draw construction lines.
    # cr.set_source_rgb(0.9, 0.9, 0.9)
    # cr.set_line_width(0.008)
    # for arc in arcs:
    #     cr.arc(*arc.center, arc.radius, 0, tau)
    #     cr.stroke()

    # Draw arcs.
    cr.set_source_rgb(0, 0, 0)
    cr.set_line_width(0.15)
    cr.set_line_cap(cairo.LineCap.ROUND)
    for i, arc in enumerate(arcs):
        cr.arc(
            *arc.center,
            arc.radius,
            arc.angle1,
            arc.angle2,
        )
        cr.stroke()

    # Draw arc intersections.
    for (a, b) in every_pair(arcs):
        intersections = intersect_arcs(a, b)
        for p in intersections:
            dot(cr, p)

    # Draw crossover points.
    # for p in crossovers:
    #     dot(cr, p)

    surface.finish()


def dot(cr, p):
    cr.save()
    cr.set_source_rgb(0.85, 0.0, 0.0)
    cr.arc(*p, 0.05, 0, tau)
    cr.fill()
    cr.restore()


def ribbonize(arcs):
    result = []
    for arc in arcs:
        result.extend(ribbon_arcs(arc))
    return result


def break_arcs(arcs):
    arc_ids = list(range(len(arcs)))
    arcs_by_id = dict(enumerate(arcs))
    intersections_by_arc = defaultdict(list)

    for (a, b) in every_pair(arc_ids):
        arc_a = arcs_by_id[a]
        arc_b = arcs_by_id[b]
        points = intersect_arcs(arc_a, arc_b)
        intersections_by_arc[a].extend(points)
        intersections_by_arc[b].extend(points)

    result_arcs = []
    for arc_id, points in intersections_by_arc.items():
        result_arcs.extend(break_arc(arcs_by_id[arc_id], points))

    return result_arcs


def logo_arcs(crossovers):
    n = len(crossovers)

    # Outer arcs.
    outer_arcs = []
    for i in range(0, n, 2):
        inner = crossovers[i]
        outer1 = crossovers[(i-1) % n]
        outer2 = crossovers[(i+1) % n]
        outer_arcs.append(arc_center_a_b(inner, outer1, outer2))

    # Middle arcs.
    middle_left_arcs = []
    middle_right_arcs = []
    middle_centers = {}
    for i in range(0, n, 2):
        outer = crossovers[(i+1) % n]
        inner1 = crossovers[i]
        inner2 = crossovers[(i+2) % n]

        mid1 = midpoint(inner1, outer)
        tangent1 = perp(outer - inner1)
        center1 = intersect_lines(
            outer, inner2,
            mid1, mid1 + tangent1,
        )
        middle_left_arcs.append(arc_center_a_b(center1, inner1, outer))

        mid2 = midpoint(inner2, outer)
        tangent2 = perp(outer - inner2)
        center2 = intersect_lines(
            outer, inner1,
            mid2, mid2 - tangent2,
        )
        middle_right_arcs.append(arc_center_a_b(center2, outer, inner2))

        middle_centers[i] = center1
        middle_centers[i + 1] = center2

    # Inner arcs.
    inner_arcs = []
    for i in range(1, n, 2):
        inner1 = crossovers[(i-1) % n]
        inner2 = crossovers[(i+1) % n]

        # Get the middle arc circle centers which are perpendicular to the ends of the
        # inner arc, so the arcs will be cotangent.
        middleCenter1 = middle_centers[(i-2) % n]
        middleCenter2 = middle_centers[(i+1) % n]

        # These lines intersect at the inner arc center.
        center = intersect_lines(middleCenter1, inner1, middleCenter2, inner2)
        inner_arcs.append(arc_center_a_b(center, inner2, inner1))

    # Assemble arcs.
    m = n // 2
    arcs = []
    for i in range(m):
        j = i * 3 % m
        arcs.append(outer_arcs[j])
        arcs.append(middle_right_arcs[j])
        arcs.append(inner_arcs[(j+1) % m])
        arcs.append(middle_left_arcs[(j+2) % m])

    return arcs


def ribbon_arcs(arc, width=1.15):
    return (
        Arc(arc.center, arc.radius + width/2, arc.angle1, arc.angle2),
        Arc(arc.center, arc.radius - width/2, arc.angle1, arc.angle2),
    )


def sympy_polar_to_rect(p):
    """Convert points from symbolic polar to numeric rectangular coordinates."""
    r, theta = p
    rect = mpmath.rect(float(r), float(theta))
    return np.array([float(rect.real), float(rect.imag)])


def every_pair(iterable):
    enumerated_values = list(enumerate(iterable))
    for low_index, first_item in enumerated_values:
        for high_index, second_item in enumerated_values:
            if high_index <= low_index:
                continue
            yield (first_item, second_item)


if __name__ == '__main__':
    main()
