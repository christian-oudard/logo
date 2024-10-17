from math import sin
import vec

import numpy as np
import cairo

from braid_equation import braid
from grid_index import GridIndex
from utility import discretize_polar


tau = np.pi * 2

LINE_WIDTH = 0.08
RIBBON_WIDTH = 0.3 + LINE_WIDTH / 2

GRID_SIZE = 0.1


def main():
    theta_vals = np.linspace(0, 3*tau, 3*7*64, endpoint=False)
    braid_points = discretize_polar(braid, theta_vals)

    curves = ribbonize(braid_points, RIBBON_WIDTH)
    curve_sections = break_curves(curves)

    # Create cairo SVG surface.
    width, height = (768, 768)
    surface = cairo.SVGSurface('output.svg', width, height)
    cr = cairo.Context(surface)

    cr.set_source_rgb(0, 0, 0)
    cr.paint()

    # Set a view box ranging from -2 to +2 in both axes.
    cr.translate(width/2, height/2)
    cr.scale(width/4, height/4)
    cr.rotate(-tau/4)

    # Draw braid lines.
    cr.set_source_rgb(1, 1, 1)
    cr.set_line_width(LINE_WIDTH)
    cr.set_line_cap(cairo.LineCap.ROUND)
    for i, c in enumerate(curve_sections):
        if i % 4 != 3:
            draw_curve(cr, c)

    surface.finish()


def draw_curve(cr, points, closed=False):
    start = points[0]
    cr.move_to(*start)
    for p in points[1:]:
        cr.line_to(*p)
    if closed:
        cr.line_to(*start)
    cr.stroke()


def dot(cr, p):
    cr.save()
    cr.set_source_rgb(0.8, 0.0, 0.0)
    cr.arc(*p, 0.005, 0, tau)
    cr.fill()
    cr.restore()


def ribbonize(curve, width):
    # Offset the curve an equal distance to the left and right. At each point, we look at the previous and next segment,
    # offset each segment to each side, then find the intersection of these lines. When the angle between segments is
    # zero or small, this becomes numerically unstable, so instead we use an angle bisection method.

    offset = width / 2
    curve_left = []
    curve_right = []
    for p_prev, p, p_next in iter_segments(curve):
        v_prev = vec.vfrom(p_prev, p)
        v_next = vec.vfrom(p, p_next)

        # For each segment, get a vector perpendicular to the segment, then add them. This is an angle bisector for the
        # angle of the joint.
        w_prev = vec.norm(vec.perp(v_prev), offset)
        w_next = vec.norm(vec.perp(v_next), offset)
        bisector = vec.add(w_prev, w_next)

        # Make the bisector have the correct length.
        half_angle = vec.angle(v_next, bisector)
        bisector = vec.norm(
            bisector,
            offset / sin(half_angle)
        )

        # Determine the left and right joint spots.
        p_left = vec.add(p, bisector)
        curve_left.append(p_left)
        p_right = vec.sub(p, bisector)
        curve_right.append(p_right)

    return curve_left, curve_right


def break_curves(curves):
    # Collect every line segment in the curves.
    segments = []
    for c in curves:
        for _, p, p_next in iter_segments(c):
            segments.append((p, p_next))

    # Put the line segments into a grid index.
    grid = GridIndex(GRID_SIZE)
    for segment in segments:
        grid.add(segment)

    # Separate the curves at the points where they intersect.
    all_sections = []
    for c in curves:
        curve_segments = []
        for _, p, p_next in iter_segments(c):
            curve_segments.append((p, p_next))

        sections = []
        current_section = []
        for segment in curve_segments:
            for other in grid.query(segment):
                x = vec.intersect_lines(segment, other, segment=True, include_endpoints = False)
                if x is not None:
                    # Split the current segment.
                    split_before = (segment[0], x)
                    split_after = (x, segment[1])
                    # End the current section and start the new one.
                    current_section.append(split_before)
                    sections.append(current_section)
                    current_section = [split_after]
                    break
            else:  # No intersection found for this segment.
                current_section.append(segment)

        # Because the starting point is not a section break, we have to join the remainder to the start.
        # We've reached the end of the curve, so this is a section boundary too.
        sections[0] = current_section + sections[0]
        all_sections.extend(sections)

    new_curves = [ join_segments(s) for s in all_sections ]
    return new_curves


def iter_segments(curve):
    num_points = len(curve)
    for i, p in enumerate(curve):
        p_prev = curve[ (i-1) % num_points ]
        p_next = curve[ (i+1) % num_points ]
        yield p_prev, p, p_next


def join_segments(segments):
    curve = []
    for (a, b) in segments:
        if len(curve) == 0:
            curve.append(a)
            curve.append(b)
        else:
            assert vec.equal(curve[-1], a), f'{vec.dist(curve[-1], a)}'
            curve.append(b)
    return curve


if __name__ == '__main__':
    main()

