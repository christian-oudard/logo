package main

import (
	"fmt"
	"github.com/golang/geo/r2"
	"github.com/ajstarks/svgo"
	"math"
	"os"
)

var (
	svgUnits int = 1 << 20
	pxWidth = 500
	pxHeight = 500
	tau = 2 * math.Pi
	gray = "#a59da0"
	red = "#600b26"
	blue = "#607bc6"
	thinLine = "fill:none; stroke:"+gray+"; stroke-width:4000"
	thickLine = "fill:none; stroke:"+red+"; stroke-width:60000"
	debug = false;
)

func main() {
	c := svg.New(os.Stdout)
	c.Startview(pxWidth, pxHeight, -4*svgUnits, -4*svgUnits, 8*svgUnits, 8*svgUnits)

	// The knot crossover points are the self-intersections of the curve
	// r = (7/3) + sin((7/3) * theta)
	// For even i in i*(tau/14), the intersection is at radius 11/6,
	// and for odd i, the intersection is at radius 17/6.
	var (
		r, theta float64
		crossovers [14]r2.Point
	)
	for i := 0; i < 14; i++ {
		theta = float64(i) * (tau / 14)
		if i%2 == 0 {
			r = 11/6.0
		} else {
			r = 17/6.0
		}
		theta -= tau / 4 // Start from south position.
		crossovers[i] = fromPolar(r, theta)
	}

	// Draw outer arcs.
	for i := 0; i < 7; i++ {
		inner := crossovers[2*i]
		outer1 := crossovers[(2*i - 1 + 14) % 14] // left outer
		outer2 := crossovers[2*i + 1] // right outer
		arc(c, inner, outer1, outer2)
		if debug {
			line(c, inner, outer1)
			line(c, inner, outer2)
			circle(c, inner, outer1.Sub(inner).Norm(), thinLine)
		}
	}

	var middleCenters [14]r2.Point

	// Draw middle arcs.
	for i := 0; i < 7; i++ {
		outer := crossovers[2*i + 1]
		inner1 := crossovers[2*i]
		inner2 := crossovers[(2*i + 2) % 14]

		mid1 := midpoint(inner1, outer)
		tangent1 := outer.Sub(inner1).Ortho()
		center1 := intersectLines(
			outer, inner2,
			mid1, mid1.Add(tangent1),
		)
		arc(c, center1, outer, inner1)
		if debug {
			dot(c, center1)
			line(c, center1, outer)
			line(c, center1, inner1)
			circle(c, center1, outer.Sub(center1).Norm(), thinLine)
		}

		mid2 := midpoint(inner2, outer)
		tangent2 := outer.Sub(inner2).Ortho()
		center2 := intersectLines(
			outer, inner1,
			mid2, mid2.Add(tangent2),
		)
		arc(c, center2, outer, inner2)
		if debug {
			dot(c, center2)
			line(c, center2, outer)
			line(c, center2, inner2)
			circle(c, center2, outer.Sub(center2).Norm(), thinLine)
		}

		middleCenters[2*i] = center1
		middleCenters[2*i + 1] = center2
	}

	// Draw inner arcs.
	for i := 1; i < 14; i += 2 {
		inner1 := crossovers[(i-1 + 14) % 14]
		inner2 := crossovers[(i+1 + 14) % 14]

		// Get the middle arc circle centers which are perpendicular to the ends of the
		// inner arc.
		middleCenter1 := middleCenters[(i-2 + 14) % 14]
		middleCenter2 := middleCenters[(i+1 + 14) % 14]

		// These lines intersect at the inner arc center.
		center := intersectLines(middleCenter1, inner1, middleCenter2, inner2)
		arc(c, center, inner1, inner2)
		if debug {
			dot(c, center)
			line(c, center, inner1)
			line(c, center, inner2)
			circle(c, center, center.Sub(inner1).Norm(), thinLine)
		}
	}

	// Draw crossovers.
	if debug {
		for _, p := range crossovers {
			dot(c, p)
		}
	}

	// Draw grid lines.
	if debug {
		for i := 0; i < 14; i++ {
			c.Rotate((float64(i) / 14) * 360)
			line(c, p(0, 0), p(0, 4))
			c.Gend()
		}
		circle(c, p(0,0), 11/6.0, thinLine)
		circle(c, p(0,0), 17/6.0, thinLine)
	}

	c.End()
}

func p(x, y float64) r2.Point {
	return r2.Point{X:x, Y:y}
}

func fromPolar(r, theta float64) r2.Point {
	return p(r * math.Cos(theta), r * math.Sin(theta))
}

func toSvg(v float64) int {
	return int(v * float64(svgUnits))
}

func line(c *svg.SVG, a, b r2.Point) {
		c.Line(toSvg(a.X), toSvg(a.Y), toSvg(b.X), toSvg(b.Y), thinLine)
}

func circle(c *svg.SVG, center r2.Point, radius float64, style string) {
		c.Circle(toSvg(center.X), toSvg(center.Y), toSvg(radius), style)
}

func dot(c *svg.SVG, p r2.Point) {
	circle(c, p, 1/15.0, "fill:"+blue)
}

func arc(c *svg.SVG, center, a, b r2.Point) {
		r := a.Sub(center).Norm()

		var sweep int
		if ccw(center, a, b) {
			sweep = 1
		} else {
			sweep = 0
		}

		d := fmt.Sprintf(
			"M%d,%d A%d,%d 0 0,%d %d,%d",
			toSvg(a.X), toSvg(a.Y),
			toSvg(r), toSvg(r),
			sweep,
			toSvg(b.X), toSvg(b.Y),
		)
		c.Path(d, thickLine)
}

func ccw(a, b, c r2.Point) bool {
	det := (b.X - a.X) * (c.Y - a.Y) - (c.X - a.X) * (b.Y - a.Y)
	return det > 0
}

func midpoint(a, b r2.Point) r2.Point {
	return a.Add(b).Mul(0.5)
}

func intersectLines(p0, p1, q0, q1 r2.Point) r2.Point {
	// u is the tangent vector along line P.
	// v is the tangent vector along line Q.
	// w is the vector from p0 to q0.
	u := p1.Sub(p0)
	v := q1.Sub(q0)
	w := p0.Sub(q0)

	// vPerp is a perpendicular to vector v.
	// Parametrize points on line P by the equation P(s) = p0 + s*u.
	// A vector from q0 to these parametrized points is w + s*u.
	// A point P(s) is on line Q when the dot product to vPerp is zero.
	// This gives us the equation vPerp.Dot(w + s*u) = 0. Solving for s, we get:
	// s = -vPerp.Dot(w) / vPerp.Dot(u)
	// This is the location along line P of the intersection point.
	vPerp := v.Ortho()
	s := vPerp.Mul(-1).Dot(w) / vPerp.Dot(u)
	return p0.Add(u.Mul(s))
}
