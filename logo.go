package main

import (
	"github.com/golang/geo/r2"
	"github.com/ajstarks/svgo"
	"math"
	"os"
	// "fmt"
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
	thickLine = "fill:none; stroke:"+red+"; stroke-width:8000"
)

func p(x, y float64) r2.Point {
	return r2.Point{X:x, Y:y}
}

func toSvg(v float64) int {
	return int(v * float64(svgUnits))
}

func circle(c *svg.SVG, center r2.Point, radius float64, style string) {
		c.Circle(toSvg(center.X), toSvg(center.Y), toSvg(radius), style)
}

func dot(c *svg.SVG, p r2.Point, color string) {
	circle(c, p, 1/20.0, "fill:"+color)
}

func line(c *svg.SVG, a, b r2.Point) {
		c.Line(toSvg(a.X), toSvg(a.Y), toSvg(b.X), toSvg(b.Y), thinLine)
}

func fromPolar(r, theta float64) r2.Point {
	return p(r * math.Cos(theta), r * math.Sin(theta))
}

func main() {
	c := svg.New(os.Stdout)
	c.Startview(pxWidth, pxHeight, -4*svgUnits, -4*svgUnits, 8*svgUnits, 8*svgUnits)

	// Grid lines.
	for i := 0; i < 14; i++ {
		c.Rotate((float64(i) / 14) * 360)
		line(c, p(0, 0), p(0, 4))
		c.Gend()
	}
	circle(c, p(0,0), 11/6.0, thinLine)
	circle(c, p(0,0), 17/6.0, thinLine)

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

	// Draw crossovers.
	for _, p := range crossovers {
		dot(c, p, red)
	}

	// // Draw arcs.
	// for i := 0; i < 7; i++ {
	// 	// Outer arc.
	// 	inner1 := crossovers[2*i]
	// 	outer := crossovers[2*i + 1]
	// 	radius1 := inner1.Sub(outer)
	// 	circle(c, inner1, radius1.Norm(), thinLine)

	// 	if i == 0 {
	// 		// Middle arc.
	// 		//BROKEN
	// 		inner2 := crossovers[2*(i+1) % 14]
	// 		midpoint := outer.Add(inner2).Mul(0.5)
	// 		dot(c, midpoint, blue)
	// 		tangent := outer.Sub(inner2).Ortho()
	// 		dot(c, midpoint.Add(tangent), blue)
	// 		center2 := intersectLines(inner1, outer, midpoint, midpoint.Add(tangent))

	// 		dot(c, center2, blue)
	// 		radius2 := inner2.Sub(center2)
	// 		circle(c, center2, radius2.Norm(), thinLine)
	// 	}
	// }

	c.End()
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
	return w.Add(u.Mul(s))
}
