var circles = [
	[3, 0, 7 * 5],
	[3 - 7, 0, 7],	
	[3 + 7, 0, 4],	
];

var startFrame = 1;
var endFrame = startFrame + 720;

var points = [];
var s = 0;

var circleColor, lineColor, pointColor, pathColor;
var canvas;

function setup() {
	canvas = createCanvas(window.innerWidth, window.innerHeight);
	circleColor = color(500, 50);
	lineColor = color(255);
	pointColor = color(255, 0);
	pathColor = color(255, 0, 0);
	
	window.onresize();
}

function draw() {
	background(45)
	push()
	translate(width / 2, height / 2)
	var px = 0, py = 0

	var t = frameCount * PI / 360

	fill(0, 0, 0, 0)
	stroke(255)
	for (var i = 0; i < circles.length; i++) {
		var c = circles[i];
		
		var hz = c[0]
		var angle = (c[1] + t) * hz;
		var radius = c[2] * s
		var lx = px
		var ly = py
		px += sin(angle) * radius
		py -= cos(angle) * radius
			//draw line
		strokeWeight(1)
		stroke(lineColor)
		line(lx, ly, px, py)
			//draw circle
		stroke(circleColor)
		ellipse(lx, ly, radius * 2, radius * 2)
			//draw point
		strokeWeight(5)
		stroke(pointColor)
		point(px, py)
	}

	if (frameCount >= startFrame && frameCount <= endFrame) {
		points.push(createVector(px / s, py / s))
	}

	beginShape()
	stroke(255, 0, 0)
	strokeWeight(2)
	for (i = 0; i < points.length; i++) {
		vertex(points[i].x * s, points[i].y * s)
	}

	endShape()
	pop()
}

window.onresize = function() {
  var w = innerWidth
  var h = window.innerHeight; 
  canvas.size(w,h)
  width = w
  height = h
	s = min(width, height) / (circles.length * 35)
};
