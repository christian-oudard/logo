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
    trim_arc,
    midpoint,
    perp,
    tau,
)


def main():
    crossovers = np.array([ sympy_polar_to_rect(p) for p in calculate_crossovers() ])
    arcs = logo_arcs(crossovers)
    arcs = trim_arcs(arcs)

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
    cr.set_line_width(0.05)
    cr.set_line_cap(cairo.LineCap.ROUND)
    for arc in arcs:
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


def trim_arcs(arcs):
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
        result_arcs.append(trim_arc(arcs_by_id[arc_id], points))

    return result_arcs


def logo_arcs(crossovers):
    arcs = []

    # Draw outer arcs.
    for i in range(0, 14, 2):
        inner = crossovers[i]
        outer1 = crossovers[(i-1) % 14]
        outer2 = crossovers[(i+1) % 14]
        arcs.extend(
            ribbon_arcs(
                arc_center_a_b(inner, outer1, outer2)))

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
        arcs.extend(
            ribbon_arcs(
                arc_center_a_b(center1, inner1, outer)))

        mid2 = midpoint(inner2, outer)
        tangent2 = perp(outer - inner2)
        center2 = intersect_lines(
            outer, inner1,
            mid2, mid2 - tangent2,
        )
        arcs.extend(
            ribbon_arcs(
                arc_center_a_b(center2, outer, inner2)))

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
        arcs.extend(
            ribbon_arcs(
                arc_center_a_b(center, inner2, inner1)))

    return arcs


def ribbon_arcs(arc, width=0.8):
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
