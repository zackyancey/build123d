"""

name: general_examples_algebra.py
by:   Bernhard Walter
date: March 2023

desc:

    This is the build123d general examples python script. It generates the SVGs
    when run as a script, and is pulled into sphinx docs by
    tutorial_general.rst.

license:

    Copyright 2022 jdegenstein

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from build123d import *

svg_opts = {
    "width": 500,
    "height": 300,
    "pixel_scale": 4,
    "margin_left": 10,
    "margin_top": 10,
    "show_axes": False,
    "show_hidden": True,
}


def svgout(ex_counter):
    exec(
        f"""
ex{ex_counter}.export_svg(
    f"assets/general_ex{ex_counter}_algebra.svg",
    (-100, -100, 70),
    (0, 0, 1),
    svg_opts=svg_opts,
)
"""
    )


ex_counter = 1
##########################################
# 1. Simple Rectangular Plate
# [Ex. 1]
length, width, thickness = 80.0, 60.0, 10.0

ex1 = Box(length, width, thickness)
# [Ex. 1]

svgout(ex_counter)

ex_counter += 1

# show_object(ex1.part)


##########################################
# 2. Plane with hole
# [Ex. 2]
length, width, thickness = 80.0, 60.0, 10.0
center_hole_dia = 22.0

ex2 = Box(length, width, thickness)
ex2 -= Cylinder(radius=center_hole_dia / 2, height=thickness)
# [Ex. 2]

svgout(ex_counter)

ex_counter += 1
# show_object(ex2.part)

##########################################
# 3. An extruded prismatic solid
# [Ex. 3]
length, width, thickness = 80.0, 60.0, 10.0

sk3 = Circle(width) - Rectangle(length / 2, width / 2)
ex3 = extrude(sk3, amount=2 * thickness)
# [Ex. 3]

svgout(ex_counter)

ex_counter += 1
# show_object(ex3.part)

##########################################
# Building profiles using lines and arcs
# [Ex. 4]
length, width, thickness = 80.0, 60.0, 10.0

lines = Curve() + [
    Line((0, 0), (length, 0)),
    Line((length, 0), (length, width)),
    ThreePointArc((length, width), (width, width * 1.5), (0.0, width)),
    Line((0.0, width), (0, 0)),
]
sk4 = make_face(lines)
ex4 = extrude(sk4, amount=thickness)
# [Ex. 4]

svgout(ex_counter)

ex_counter += 1
# show_object(ex4.part)

##########################################
# Moving the current working point
# [Ex. 5]
a, b, c, d = 90, 45, 15, 7.5

sk5 = Circle(a) - Pos(b, 0.0) * Rectangle(c, c) - Pos(0.0, b) * Circle(d)
ex5 = extrude(sk5, amount=c)
# [Ex. 5]

svgout(ex_counter)

ex_counter += 1

# show_object(ex5.part)

##########################################
# Using Point Lists
# [Ex. 6]
a, b, c = 80, 60, 10

sk6 = [loc * Circle(c) for loc in Locations((b, 0), (0, b), (-b, 0), (0, -b))]
ex6 = extrude(Circle(a) - sk6, amount=c)
# [Ex. 6]

svgout(ex_counter)

ex_counter += 1

# show_object(ex6.part)
##########################################
# Polygons
# [Ex. 7]
a, b, c = 60, 80, 5

polygons = [
    loc * RegularPolygon(radius=2 * c, side_count=6)
    for loc in Locations((0, 3 * c), (0, -3 * c))
]
sk7 = Rot(0, 0, c) * Rectangle(a, b) - polygons
ex7 = extrude(sk7, amount=c)
# [Ex. 7]

svgout(ex_counter)

ex_counter += 1

# show_object(ex7.part)

##########################################
# 8. Polylines
# [Ex. 8]
(L, H, W, t) = (100.0, 20.0, 20.0, 1.0)
pts = [
    (0, H / 2.0),
    (W / 2.0, H / 2.0),
    (W / 2.0, (H / 2.0 - t)),
    (t / 2.0, (H / 2.0 - t)),
    (t / 2.0, (t - H / 2.0)),
    (W / 2.0, (t - H / 2.0)),
    (W / 2.0, H / -2.0),
    (0, H / -2.0),
]

ln = Polyline(*pts)
ln += mirror(ln, about=Plane.YZ)

sk8 = make_face(Plane.YZ * ln)
ex8 = extrude(sk8, amount=-L).clean()
# [Ex. 8]

svgout(ex_counter)

ex_counter += 1

# show_object(ex8.part)

##########################################
# 9. Selectors, fillets, and chamfers
# [Ex. 9]
length, width, thickness = 80.0, 60.0, 10.0

ex9 = Part() + Box(length, width, thickness)
ex9 = chamfer(*ex9.edges().group_by(Axis.Z)[-1], length=4, target=ex9)
ex9 = fillet(*ex9.edges().filter_by(Axis.Z), radius=5, target=ex9)
# [Ex. 9]

svgout(ex_counter)

ex_counter += 1

# show_object(ex9.part)

##########################################
# 10. Select last edges and Hole
# [Ex. 10]
ex10 = Part() + Box(length, width, thickness)
ex10 = chamfer(*ex10.edges().group_by(Axis.Z)[-1], length=4, target=ex10)
ex10 = fillet(*ex10.edges().filter_by(Axis.Z), radius=5, target=ex10)

snapshot = ex10.edges()
ex10 -= Hole(radius=width / 4, depth=thickness)
last_edges = ex10.edges() - snapshot
ex10 = fillet(last_edges.sort_by().last, radius=2, target=ex10)
# [Ex. 10]

svgout(ex_counter)

ex_counter += 1

# show_object(ex10.part)

##########################################
# 11. Use a face as workplane for BuildSketch and introduce GridLocations
# [Ex. 11]
length, width, thickness = 80.0, 60.0, 10.0

ex11 = Part() + Box(length, width, thickness)
ex11 = chamfer(*ex11.edges().group_by()[-1], length=4, target=ex11)
ex11 = fillet(*ex11.edges().filter_by(Axis.Z), radius=5, target=ex11)
last = ex11.edges()
ex11 -= Hole(radius=width / 4, depth=thickness)
ex11 = fillet((ex11.edges() - last).sort_by().last, radius=2, target=ex11)

plane = Plane(ex11.faces().sort_by().last)
polygons = Sketch() + [
    plane * loc * RegularPolygon(radius=5, side_count=5)
    for loc in GridLocations(length / 2, width / 2, 2, 2)
]
ex11 -= extrude(polygons, amount=-thickness)
# [Ex. 11]

svgout(ex_counter)

ex_counter += 1

# show_object(ex11)

##########################################
# 12. Defining an Edge with a Spline
# [Ex. 12]
sPnts = [
    (55, 30),
    (50, 35),
    (40, 30),
    (30, 20),
    (20, 25),
    (10, 20),
    (0, 20),
]

l1 = Spline(*sPnts)
l2 = Line(l1 @ 0, (60, 0))
l3 = Line(l2 @ 1, (0, 0))
l4 = Line(l3 @ 1, l1 @ 1)

sk12 = make_face(l1, l2, l3, l4)
ex12 = extrude(sk12, amount=10)
# [Ex. 12]

svgout(ex_counter)

ex_counter += 1

# show_object(ex12.part)


##########################################
# 13. CounterBoreHoles, CounterSinkHoles and PolarLocations
# [Ex. 13]
a, b = 40, 4

ex13 = Cylinder(radius=50, height=10)
plane = Plane(ex13.faces().sort_by().last)

ex13 -= [
    plane * loc * CounterSinkHole(radius=b, counter_sink_radius=2 * b, depth=10)
    for loc in PolarLocations(radius=a, count=4)
]
ex13 -= [
    plane
    * loc
    * CounterBoreHole(
        radius=b, counter_bore_radius=2 * b, depth=10, counter_bore_depth=b
    )
    for loc in PolarLocations(radius=a, count=4, start_angle=45, angular_range=360)
]
# [Ex. 13]

svgout(ex_counter)

ex_counter += 1

# show_object(ex13.part)

##########################################
# 14. Position on a line with '@', '%' and introduce Sweep
# [Ex. 14]
a, b = 40, 20

l1 = JernArc(start=(0, 0), tangent=(0, 1), radius=a, arc_size=180)
l2 = JernArc(start=l1 @ 1, tangent=l1 % 1, radius=a, arc_size=-90)
l3 = Line(l2 @ 1, l2 @ 1 + Vector(-a, a))
ex14_ln = l1 + l2 + l3

sk14 = Plane.XZ * Rectangle(b, b)
ex14 = sweep(sk14, path=ex14_ln.wires()[0])
# [Ex. 14]

svgout(ex_counter)

ex_counter += 1

# show_object(ex14.part)


##########################################
# 15. Mirroring Symmetric Geometry
# [Ex. 15]
a, b, c = 80, 40, 20

l1 = Line((0, 0), (a, 0))
l2 = Line(l1 @ 1, l1 @ 1 + Vector(0, b))
l3 = Line(l2 @ 1, l2 @ 1 + Vector(-c, 0))
l4 = Line(l3 @ 1, l3 @ 1 + Vector(0, -c))
l5 = Line(l4 @ 1, Vector(0, (l4 @ 1).Y))
ln = Curve() + [l1, l2, l3, l4, l5]
ln += mirror(ln, about=Plane.YZ)

sk15 = make_face(ln)
ex15 = extrude(sk15, amount=c)
# [Ex. 15]

svgout(ex_counter)

ex_counter += 1

# show_object(ex15.part)

##########################################
# 16. Mirroring 3D Objects
# same concept as CQ docs, but different object
# [Ex. 16]
length, width, thickness = 80.0, 60.0, 10.0

sk16 = Rectangle(length, width)
sk16 = fillet(*sk16.vertices(), radius=length / 10, target=sk16)

circles = [loc * Circle(length / 12) for loc in GridLocations(length / 4, 0, 3, 1)]

sk16 = sk16 - circles - Rectangle(length, width, align=(Align.MIN, Align.MIN))
ex16_single = extrude(Plane.XZ * sk16, amount=length)

planes = [
    Plane.XY.offset(width),
    Plane.YX.offset(width),
    Plane.YZ.offset(width),
    Plane.YZ.offset(-width),
]
objs = [mirror(ex16_single, about=plane) for plane in planes]
ex16 = ex16_single + objs

# [Ex. 16]

svgout(ex_counter)

ex_counter += 1

# show_object(ex16.part)

##########################################
# 17. Mirroring From Faces
# [Ex. 17]
a, b = 30, 20

sk17 = RegularPolygon(radius=a, side_count=5)
ex17 = extrude(sk17, amount=b)
ex17 += mirror(ex17, about=Plane(ex17.faces().sort_by(Axis.Y).first))
# [Ex. 17]

svgout(ex_counter)

ex_counter += 1

# show_object(ex17.part)

##########################################
# 18. Creating Workplanes on Faces
# based on Ex. 9
# [Ex. 18]
length, width, thickness = 80.0, 60.0, 10.0
a, b = 4, 5

ex18 = Part() + Box(length, width, thickness)
ex18 = chamfer(*ex18.edges().group_by()[-1], length=a, target=ex18)
ex18 = fillet(*ex18.edges().filter_by(Axis.Z), radius=b, target=ex18)

sk18 = Plane(ex18.faces().sort_by().first) * Rectangle(2 * b, 2 * b)
ex18 -= extrude(sk18, amount=-thickness)
# [Ex. 18]

svgout(ex_counter)

ex_counter += 1

# show_object(ex18.part)

##########################################
# 19. Locating a Workplane on a vertex
# [Ex. 19]
length, thickness = 80.0, 10.0

ex19_sk = RegularPolygon(radius=length / 2, side_count=7)
ex19 = extrude(ex19_sk, amount=thickness)

topf = ex19.faces().sort_by().last

vtx = topf.vertices().group_by(Axis.X)[-1][0]

vtx2Axis = Axis((0, 0, 0), (-1, -0.5, 0))
vtx2 = topf.vertices().sort_by(vtx2Axis)[-1]

ex19_sk2 = Circle(radius=length / 8)
ex19_sk2 = Pos(vtx.X, vtx.Y) * ex19_sk2 + Pos(vtx2.X, vtx2.Y) * ex19_sk2

ex19 -= extrude(ex19_sk2, amount=thickness)
# [Ex. 19]

svgout(ex_counter)

ex_counter += 1

# show_object(ex19.part)

##########################################
# 20. Offset Sketch Workplane
# [Ex. 20]
length, width, thickness = 80.0, 60.0, 10.0

ex20 = Box(length, width, thickness)
plane = Plane(ex20.faces().sort_by(Axis.X).first).offset(2 * thickness)

sk20 = plane * Circle(width / 3)
ex20 += extrude(sk20, amount=width)
# [Ex. 20]

svgout(ex_counter)

ex_counter += 1

# show_object(ex20.part)

##########################################
# 21. Copying Workplanes
# [Ex. 21]
width, length = 10.0, 60.0

ex21 = extrude(Circle(width / 2), amount=length)
plane = Plane(origin=ex21.center(), z_dir=(-1, 0, 0))
ex21 += plane * extrude(Circle(width / 2), amount=length)
# [Ex. 21]

svgout(ex_counter)

ex_counter += 1

# show_object(ex21.part)

##########################################
# 22. Rotated Workplanes
# [Ex. 22]
length, width, thickness = 80.0, 60.0, 10.0

ex22 = Box(length, width, thickness)
plane = Plane((ex22.faces().group_by(Axis.Z)[0])[0]) * Rot(0, 50, 0)

holes = Sketch() + [
    plane * loc * Circle(thickness / 4)
    for loc in GridLocations(length / 4, width / 4, 2, 2)
]
ex22 -= extrude(holes, amount=-100, both=True)
# [Ex. 22]

svgout(ex_counter)

ex_counter += 1

# show_object(ex22.part)

##########################################
# 23. Revolve
# [Ex. 23]
pts = [
    (-25, 35),
    (-25, 0),
    (-20, 0),
    (-20, 5),
    (-15, 10),
    (-15, 35),
]

l1 = Polyline(*pts)
l2 = Line(l1 @ 1, l1 @ 0)
sk23 = make_face(l1, l2)

sk23 += Pos(0, 35) * Circle(25)
sk23 = Plane.XZ * split(sk23, bisect_by=Plane.ZY)

ex23 = revolve(sk23, axis=Axis.Z)
# [Ex. 23]

svgout(ex_counter)

ex_counter += 1

# show_object(ex23.part)

##########################################
# 24. Lofts
# [Ex. 24]
length, width, thickness = 80.0, 60.0, 10.0

ex24 = Box(length, length, thickness)
plane = Plane(ex24.faces().sort_by().last)

faces = Sketch() + [
    plane * Circle(length / 3),
    plane.offset(length / 2) * Rectangle(length / 6, width / 6),
]

ex24 += loft(faces)
# [Ex. 24]

svgout(ex_counter)

ex_counter += 1

# show_object(ex24.part)

##########################################
# 25. Offset Sketch
# [Ex. 25]
rad, offs = 50, 10

sk25_1 = RegularPolygon(radius=rad, side_count=5)
sk25_2 = Plane.XY.offset(15) * RegularPolygon(radius=rad, side_count=5)
sk25_2 = offset(sk25_2, amount=offs)
sk25_3 = Plane.XY.offset(30) * RegularPolygon(radius=rad, side_count=5)
sk25_3 = offset(sk25_3, amount=offs, kind=Kind.INTERSECTION)

sk25 = Sketch() + [sk25_1, sk25_2, sk25_3]
ex25 = extrude(sk25, amount=1)
# [Ex. 25]

svgout(ex_counter)

ex_counter += 1

# show_object(ex25.part)

##########################################
# 26. Offset Part To Create Thin features
# [Ex. 26]
length, width, thickness, wall = 80.0, 60.0, 10.0, 2.0

ex26 = Box(length, width, thickness)
topf = ex26.faces().sort_by().last
ex26 = offset(ex26, amount=-wall, openings=topf)
# [Ex. 26]

svgout(ex_counter)

ex_counter += 1

# show_object(ex26.part)

##########################################
# 27. Splitting an Object
# [Ex. 27]
length, width, thickness = 80.0, 60.0, 10.0

ex27 = Box(length, width, thickness)
sk27 = Plane(ex27.faces().sort_by().first) * Circle(width / 4)
ex27 -= extrude(sk27, amount=-thickness)
ex27 = split(
    ex27, bisect_by=Plane(ex27.faces().sort_by(Axis.Y).last).offset(-width / 2)
)
# [Ex. 27]

svgout(ex_counter)

ex_counter += 1

# show_object(ex27.part)

##########################################
# 28. Locating features based on Faces
# [Ex. 28]
width, thickness = 80.0, 10.0

sk28 = RegularPolygon(radius=width / 4, side_count=3)
tmp28 = extrude(sk28, amount=thickness)
ex28 = Sphere(radius=width / 2)
for p in [Plane(face) for face in tmp28.faces().group_by(Axis.Z)[1]]:
    ex28 -= p * Hole(thickness / 2, depth=width)
# [Ex. 28]

svgout(ex_counter)

ex_counter += 1

# show_object(ex28.part)

##########################################
# 29. The Classic OCC Bottle
# [Ex. 29]
L, w, t, b, h, n = 60.0, 18.0, 9.0, 0.9, 90.0, 8.0

l1 = Line((0, 0), (0, w / 2))
l2 = ThreePointArc(l1 @ 1, (L / 2.0, w / 2.0 + t), (L, w / 2.0))
l3 = Line(l2 @ 1, Vector((l2 @ 1).X, 0, 0))
ln29 = l1 + l2 + l3
ln29 += mirror(ln29)
sk29 = make_face(ln29)
ex29 = extrude(sk29, amount=-(h + b))
# ex29 = fillet(*ex29.edges(), radius=w / 8, target=ex29)

neck = Plane(ex29.faces().sort_by().last) * Circle(t)
ex29 += extrude(neck, amount=n)
necktopf = ex29.faces().sort_by().last
ex29 = offset(ex29, amount=-b, openings=necktopf)
# [Ex. 29]

svgout(ex_counter)

ex_counter += 1

# show_object(ex29.part)

##########################################
# 30. Bezier Curve
# [Ex. 30]
pts = [
    (0, 0),
    (20, 20),
    (40, 0),
    (0, -40),
    (-60, 0),
    (0, 100),
    (100, 0),
]

wts = [
    1.0,
    1.0,
    2.0,
    3.0,
    4.0,
    2.0,
    1.0,
]

ex30_ln = Polyline(*pts) + Bezier(*pts, weights=wts)
ex30_sk = make_face(ex30_ln)
ex30 = extrude(ex30_sk, amount=-10)
# [Ex. 30]

svgout(ex_counter)

ex_counter += 1

# show_object(ex30.part)

##########################################
# 31. Nesting Locations
# [Ex. 31]
a, b, c = 80.0, 5.0, 3.0

ex31 = Sketch()

for ploc in PolarLocations(a / 2, 6):
    ex31 += ploc * RegularPolygon(b, 4)
    for gloc in GridLocations(3 * b, 3 * b, 2, 2):
        ex31 += ploc * gloc * RegularPolygon(b, 3)

ex31 += Rot(z=30) * RegularPolygon(3 * b, 6)
ex31 = extrude(ex31, 3)
# [Ex. 31]

svgout(ex_counter)

ex_counter += 1

# show_object(ex31.part)

##########################################
# 32. Python for-loop
# [Ex. 32]
a, b, c = 80.0, 10.0, 1.0

ex32_sk = RegularPolygon(2 * b, 6, rotation=30)
ex32_sk += [loc * RegularPolygon(b, 4) for loc in PolarLocations(a / 2, 6)]
ex32 = Part() + [
    extrude(obj, amount=c + 3 * idx) for idx, obj in enumerate(ex32_sk.faces())
]
# [Ex. 32]

svgout(ex_counter)

ex_counter += 1

# show_object(ex32.part)

##########################################
# 33. Python function and for-loop
# [Ex. 33]
a, b, c = 80.0, 5.0, 1.0


def square(rad, loc):
    return loc * RegularPolygon(rad, 4)


ex33 = Part() + [
    extrude(square(b + 2 * i, loc), amount=c + 2 * i)
    for i, loc in enumerate(PolarLocations(a / 2, 6))
]

# [Ex. 33]

svgout(ex_counter)

ex_counter += 1

# show_object(ex33.part)

##########################################
# 34. Embossed and Debossed Text
# [Ex. 34]
length, width, thickness, fontsz, fontht = 80.0, 60.0, 10.0, 25.0, 4.0

ex34 = Box(length, width, thickness)
plane = Plane(ex34.faces().sort_by().last)
ex34_sk = plane * Text("Hello", font_size=fontsz, align=(Align.CENTER, Align.MIN))
ex34 += extrude(ex34_sk, amount=fontht)
ex34_sk2 = plane * Text("World", font_size=fontsz, align=(Align.CENTER, Align.MAX))
ex34 -= extrude(ex34_sk2, amount=-fontht)
# [Ex. 34]

svgout(ex_counter)

ex_counter += 1

# show_object(ex34.part)

##########################################
# 35. Slots
# [Ex. 35]
length, width, thickness = 80.0, 60.0, 10.0

ex35 = Box(length, length, thickness)
plane = Plane(ex35.faces().sort_by().last)
ex35_sk = SlotCenterToCenter(width / 2, 10)
ex35_ln = RadiusArc((-width / 2, 0), (0, width / 2), radius=width / 2)
ex35_sk += SlotArc(arc=ex35_ln.edges()[0], height=thickness)
ex35_ln2 = RadiusArc((0, -width / 2), (width / 2, 0), radius=-width / 2)
ex35_sk += SlotArc(arc=ex35_ln2.edges()[0], height=thickness)
ex35 -= extrude(plane * ex35_sk, amount=-thickness)
# [Ex. 35]

svgout(ex_counter)

ex_counter += 1

# show_object(ex35.part)

##########################################
# 36. Extrude-Until
# [Ex. 36]
rad, rev = 6, 50

ex36_sk = Pos(0, rev) * Circle(rad)
ex36 = revolve(ex36_sk, axis=Axis.X, revolution_arc=180)
ex36_sk2 = Rectangle(rad, rev)
ex36 += extrude(ex36_sk2, until=Until.NEXT, target=ex36)

# [Ex. 36]

svgout(ex_counter)

ex_counter += 1

# show_object(ex36.part)
