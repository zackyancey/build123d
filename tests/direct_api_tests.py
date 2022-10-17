# system modules
import math
import unittest
from OCP.gp import (
    gp_Vec,
    gp_Pnt,
    gp_Ax2,
    gp_Circ,
    gp_Elips,
    gp,
    gp_XYZ,
    gp_Trsf,
    gp_Ax1,
    gp_Dir,
)
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge

from build123d import *
from build123d import Shape, Matrix, BoundBox

DEG2RAD = math.pi / 180
RAD2DEG = 180 / math.pi


def _assertTupleAlmostEquals(self, expected, actual, places, msg=None):
    """Check Tuples"""
    for i, j in zip(actual, expected):
        self.assertAlmostEqual(i, j, places, msg=msg)


unittest.TestCase.assertTupleAlmostEquals = _assertTupleAlmostEquals


class TestCadObjects(unittest.TestCase):
    def _make_circle(self):

        circle = gp_Circ(gp_Ax2(gp_Pnt(1, 2, 3), gp.DZ_s()), 2.0)
        return Shape.cast(BRepBuilderAPI_MakeEdge(circle).Edge())

    def _make_ellipse(self):

        ellipse = gp_Elips(gp_Ax2(gp_Pnt(1, 2, 3), gp.DZ_s()), 4.0, 2.0)
        return Shape.cast(BRepBuilderAPI_MakeEdge(ellipse).Edge())

    def test_vector_constructors(self):
        v1 = Vector(1, 2, 3)
        v2 = Vector((1, 2, 3))
        v3 = Vector(gp_Vec(1, 2, 3))
        v4 = Vector([1, 2, 3])
        v5 = Vector(gp_XYZ(1, 2, 3))

        for v in [v1, v2, v3, v4, v5]:
            self.assertTupleAlmostEquals((1, 2, 3), v.to_tuple(), 4)

        v6 = Vector((1, 2))
        v7 = Vector([1, 2])
        v8 = Vector(1, 2)

        for v in [v6, v7, v8]:
            self.assertTupleAlmostEquals((1, 2, 0), v.to_tuple(), 4)

        v9 = Vector()
        self.assertTupleAlmostEquals((0, 0, 0), v9.to_tuple(), 4)

        v9.X = 1.0
        v9.Y = 2.0
        v9.Z = 3.0
        self.assertTupleAlmostEquals((1, 2, 3), (v9.X, v9.Y, v9.Z), 4)

        with self.assertRaises(TypeError):
            Vector("vector")
        with self.assertRaises(TypeError):
            Vector(1, 2, 3, 4)

    def test_vector_rotate(self):
        """Validate vector rotate methods"""
        vector_x = Vector(1, 0, 1).rotate_x(45)
        vector_y = Vector(1, 2, 1).rotate_y(45)
        vector_z = Vector(-1, -1, 3).rotate_z(45)
        self.assertTupleAlmostEquals(
            vector_x.to_tuple(), (1, -math.sqrt(2) / 2, math.sqrt(2) / 2), 7
        )
        self.assertTupleAlmostEquals(vector_y.to_tuple(), (math.sqrt(2), 2, 0), 7)
        self.assertTupleAlmostEquals(vector_z.to_tuple(), (0, -math.sqrt(2), 3), 7)

    def test_get_signed_angle(self):
        """Verify getSignedAngle calculations with and without a provided normal"""
        a = math.pi / 3
        v1 = Vector(1, 0, 0)
        v2 = Vector(math.cos(a), -math.sin(a), 0)
        d1 = v1.get_signed_angle(v2)
        d2 = v1.get_signed_angle(v2, Vector(0, 0, 1))
        self.assertAlmostEqual(d1, a * 180 / math.pi)
        self.assertAlmostEqual(d2, -a * 180 / math.pi)

    def test_center(self):
        v = Vector(1, 1, 1)
        self.assertAlmostEqual(v, v.center())

    # def test_to_vertex(self):
    #     """Verify conversion of Vector to Vertex"""
    #     v = Vector(1, 2, 3).to_vertex()
    #     self.assertTrue(isinstance(v, Vertex))
    #     self.assertTupleAlmostEquals(v.to_tuple(), (1, 2, 3), 5)


    def test_basic_bounding_box(self):
        v = Vertex(1, 1, 1)
        v2 = Vertex(2, 2, 2)
        self.assertEqual(BoundBox, type(v.bounding_box()))
        self.assertEqual(BoundBox, type(v2.bounding_box()))

        bb1 = v.bounding_box().add(v2.bounding_box())

        # OCC uses some approximations
        self.assertAlmostEqual(bb1.xlen, 1.0, 1)

        # Test adding to an existing bounding box
        v0 = Vertex(0, 0, 0)
        bb2 = v0.bounding_box().add(v.bounding_box())

        bb3 = bb1.add(bb2)
        self.assertTupleAlmostEquals((2, 2, 2), (bb3.xlen, bb3.ylen, bb3.zlen), 7)

        bb3 = bb2.add((3, 3, 3))
        self.assertTupleAlmostEquals((3, 3, 3), (bb3.xlen, bb3.ylen, bb3.zlen), 7)

        bb3 = bb2.add(Vector(3, 3, 3))
        self.assertTupleAlmostEquals((3, 3, 3), (bb3.xlen, bb3.ylen, bb3.zlen), 7)

        # Test 2D bounding boxes
        bb1 = Vertex(1, 1, 0).bounding_box().add(Vertex(2, 2, 0).bounding_box())
        bb2 = Vertex(0, 0, 0).bounding_box().add(Vertex(3, 3, 0).bounding_box())
        bb3 = Vertex(0, 0, 0).bounding_box().add(Vertex(1.5, 1.5, 0).bounding_box())
        # Test that bb2 contains bb1
        self.assertEqual(bb2, BoundBox.find_outside_box_2d(bb1, bb2))
        self.assertEqual(bb2, BoundBox.find_outside_box_2d(bb2, bb1))
        # Test that neither bounding box contains the other
        self.assertIsNone(BoundBox.find_outside_box_2d(bb1, bb3))

        # Test creation of a bounding box from a shape - note the low accuracy comparison
        # as the box is a little larger than the shape
        bb1 = BoundBox._from_topo_ds(Solid.make_cylinder(1, 1).wrapped, optimal=False)
        self.assertTupleAlmostEquals((2, 2, 1), (bb1.xlen, bb1.ylen, bb1.zlen), 1)

        bb2 = BoundBox._from_topo_ds(
            Solid.make_cylinder(0.5, 0.5).translate((0, 0, 0.1)).wrapped, optimal=False
        )
        self.assertTrue(bb2.is_inside(bb1))

    def test_edge_wrapper_center(self):
        e = self._make_circle()

        self.assertTupleAlmostEquals((1.0, 2.0, 3.0), e.center().to_tuple(), 3)

    def test_edge_wrapper_ellipse_center(self):
        e = self._make_ellipse()
        w = Wire.assemble_edges([e])
        self.assertTupleAlmostEquals(
            (1.0, 2.0, 3.0), Face.make_from_wires(w).center().to_tuple(), 3
        )

    def test_edge_wrapper_make_circle(self):
        halfCircleEdge = Edge.make_circle(
            radius=10, pnt=(0, 0, 0), dir=(0, 0, 1), angle1=0, angle2=180
        )

        # self.assertTupleAlmostEquals((0.0, 5.0, 0.0), halfCircleEdge.centerOfBoundBox(0.0001).to_tuple(),3)
        self.assertTupleAlmostEquals(
            (10.0, 0.0, 0.0), halfCircleEdge.start_point().to_tuple(), 3
        )
        self.assertTupleAlmostEquals(
            (-10.0, 0.0, 0.0), halfCircleEdge.end_point().to_tuple(), 3
        )

    def test_edge_wrapper_make_tangent_arc(self):
        tangent_arc = Edge.make_tangent_arc(
            Vector(1, 1),  # starts at 1, 1
            Vector(0, 1),  # tangent at start of arc is in the +y direction
            Vector(2, 1),  # arc cureturn_valuees 180 degrees and ends at 2, 1
        )
        self.assertTupleAlmostEquals((1, 1, 0), tangent_arc.start_point().to_tuple(), 3)
        self.assertTupleAlmostEquals((2, 1, 0), tangent_arc.end_point().to_tuple(), 3)
        self.assertTupleAlmostEquals(
            (0, 1, 0), tangent_arc.tangent_at(location_param=0).to_tuple(), 3
        )
        self.assertTupleAlmostEquals(
            (1, 0, 0), tangent_arc.tangent_at(location_param=0.5).to_tuple(), 3
        )
        self.assertTupleAlmostEquals(
            (0, -1, 0), tangent_arc.tangent_at(location_param=1).to_tuple(), 3
        )

    def test_edge_wrapper_make_ellipse1(self):
        # Check x_radius > y_radius
        x_radius, y_radius = 20, 10
        angle1, angle2 = -75.0, 90.0
        arcEllipseEdge = Edge.make_ellipse(
            x_radius=x_radius,
            y_radius=y_radius,
            pnt=(0, 0, 0),
            dir=(0, 0, 1),
            angle1=angle1,
            angle2=angle2,
        )

        start = (
            x_radius * math.cos(angle1 * DEG2RAD),
            y_radius * math.sin(angle1 * DEG2RAD),
            0.0,
        )
        end = (
            x_radius * math.cos(angle2 * DEG2RAD),
            y_radius * math.sin(angle2 * DEG2RAD),
            0.0,
        )
        self.assertTupleAlmostEquals(start, arcEllipseEdge.start_point().to_tuple(), 3)
        self.assertTupleAlmostEquals(end, arcEllipseEdge.end_point().to_tuple(), 3)

    def test_edge_wrapper_make_ellipse2(self):
        # Check x_radius < y_radius
        x_radius, y_radius = 10, 20
        angle1, angle2 = 0.0, 45.0
        arcEllipseEdge = Edge.make_ellipse(
            x_radius=x_radius,
            y_radius=y_radius,
            pnt=(0, 0, 0),
            dir=(0, 0, 1),
            angle1=angle1,
            angle2=angle2,
        )

        start = (
            x_radius * math.cos(angle1 * DEG2RAD),
            y_radius * math.sin(angle1 * DEG2RAD),
            0.0,
        )
        end = (
            x_radius * math.cos(angle2 * DEG2RAD),
            y_radius * math.sin(angle2 * DEG2RAD),
            0.0,
        )
        self.assertTupleAlmostEquals(start, arcEllipseEdge.start_point().to_tuple(), 3)
        self.assertTupleAlmostEquals(end, arcEllipseEdge.end_point().to_tuple(), 3)

    def test_edge_wrapper_make_circle_with_ellipse(self):
        # Check x_radius == y_radius
        x_radius, y_radius = 20, 20
        angle1, angle2 = 15.0, 60.0
        arcEllipseEdge = Edge.make_ellipse(
            x_radius=x_radius,
            y_radius=y_radius,
            pnt=(0, 0, 0),
            dir=(0, 0, 1),
            angle1=angle1,
            angle2=angle2,
        )

        start = (
            x_radius * math.cos(angle1 * DEG2RAD),
            y_radius * math.sin(angle1 * DEG2RAD),
            0.0,
        )
        end = (
            x_radius * math.cos(angle2 * DEG2RAD),
            y_radius * math.sin(angle2 * DEG2RAD),
            0.0,
        )
        self.assertTupleAlmostEquals(start, arcEllipseEdge.start_point().to_tuple(), 3)
        self.assertTupleAlmostEquals(end, arcEllipseEdge.end_point().to_tuple(), 3)

    def test_face_wrapper_make_plane(self):
        mplane = Face.make_plane(10, 10)

        self.assertTupleAlmostEquals((0.0, 0.0, 1.0), mplane.normal_at().to_tuple(), 3)

    def test_center_of_boundbox(self):
        pass

    def test_combined_center_of_boundbox(self):
        pass

    # def testCompoundcenter(self):
    #     """
    #     Tests whether or not a proper weighted center can be found for a compound
    #     """

    #     def cylinders(self, radius, height):

    #         c = Solid.make_cylinder(radius, height, Vector())

    #         # Combine all the cylinders into a single compound
    #         r = self.eachpoint(lambda loc: c.located(loc), True).combinesolids()

    #         return r

    #     Workplane.cyl = cylinders

    #     # Now test. here we want weird workplane to see if the objects are transformed right
    #     s = (
    #         Workplane("XY")
    #         .rect(2.0, 3.0, for_construction=true)
    #         .vertices()
    #         .cyl(0.25, 0.5)
    #     )

    #     self.assertEqual(4, len(s.val().solids()))
    #     self.assertTupleAlmostEquals((0.0, 0.0, 0.25), s.val().center().to_tuple(), 3)

    def test_dot(self):
        v1 = Vector(2, 2, 2)
        v2 = Vector(1, -1, 1)
        self.assertEqual(2.0, v1.dot(v2))

    def test_vector_add(self):
        result = Vector(1, 2, 0) + Vector(0, 0, 3)
        self.assertTupleAlmostEquals((1.0, 2.0, 3.0), result.to_tuple(), 3)

    def test_vector_operators(self):
        result = Vector(1, 1, 1) + Vector(2, 2, 2)
        self.assertEqual(Vector(3, 3, 3), result)

        result = Vector(1, 2, 3) - Vector(3, 2, 1)
        self.assertEqual(Vector(-2, 0, 2), result)

        result = Vector(1, 2, 3) * 2
        self.assertEqual(Vector(2, 4, 6), result)

        result = 3 * Vector(1, 2, 3)
        self.assertEqual(Vector(3, 6, 9), result)

        result = Vector(2, 4, 6) / 2
        self.assertEqual(Vector(1, 2, 3), result)

        self.assertEqual(Vector(-1, -1, -1), -Vector(1, 1, 1))

        self.assertEqual(0, abs(Vector(0, 0, 0)))
        self.assertEqual(1, abs(Vector(1, 0, 0)))
        self.assertEqual((1 + 4 + 9) ** 0.5, abs(Vector(1, 2, 3)))

    def test_vector_equals(self):
        a = Vector(1, 2, 3)
        b = Vector(1, 2, 3)
        c = Vector(1, 2, 3.000001)
        self.assertEqual(a, b)
        self.assertEqual(a, c)

    def test_vector_project(self):
        """
        Test line projection and plane projection methods of Vector
        """
        decimal_places = 9

        normal = Vector(1, 2, 3)
        base = Vector(5, 7, 9)
        x_dir = Vector(1, 0, 0)

        # test passing Plane object
        point = Vector(10, 11, 12).project_to_plane(Plane(base, x_dir, normal))
        self.assertTupleAlmostEquals(
            point.to_tuple(), (59 / 7, 55 / 7, 51 / 7), decimal_places
        )

        # test line projection
        vec = Vector(10, 10, 10)
        line = Vector(3, 4, 5)
        angle = vec.get_angle(line)

        vecLineProjection = vec.project_to_line(line)

        self.assertTupleAlmostEquals(
            vecLineProjection.normalized().to_tuple(),
            line.normalized().to_tuple(),
            decimal_places,
        )
        self.assertAlmostEqual(
            vec.length * math.cos(angle), vecLineProjection.length, decimal_places
        )

    def test_vector_not_implemented(self):
        v = Vector(1, 2, 3)
        with self.assertRaises(NotImplementedError):
            v.distance_to_line()
        with self.assertRaises(NotImplementedError):
            v.distance_to_plane()

    def test_vector_special_methods(self):
        v = Vector(1, 2, 3)
        self.assertEqual(repr(v), "Vector: (1.0, 2.0, 3.0)")
        self.assertEqual(str(v), "Vector: (1.0, 2.0, 3.0)")

    def test_matrix_creation_and_access(self):
        def matrix_vals(m):
            return [[m[r, c] for c in range(4)] for r in range(4)]

        # default constructor creates a 4x4 identity matrix
        m = Matrix()
        identity = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
        self.assertEqual(identity, matrix_vals(m))

        vals4x4 = [
            [1.0, 0.0, 0.0, 1.0],
            [0.0, 1.0, 0.0, 2.0],
            [0.0, 0.0, 1.0, 3.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
        vals4x4_tuple = tuple(tuple(r) for r in vals4x4)

        # test constructor with 16-value input
        m = Matrix(vals4x4)
        self.assertEqual(vals4x4, matrix_vals(m))
        m = Matrix(vals4x4_tuple)
        self.assertEqual(vals4x4, matrix_vals(m))

        # test constructor with 12-value input (the last 4 are an implied
        # [0,0,0,1])
        m = Matrix(vals4x4[:3])
        self.assertEqual(vals4x4, matrix_vals(m))
        m = Matrix(vals4x4_tuple[:3])
        self.assertEqual(vals4x4, matrix_vals(m))

        # Test 16-value input with invalid values for the last 4
        invalid = [
            [1.0, 0.0, 0.0, 1.0],
            [0.0, 1.0, 0.0, 2.0],
            [0.0, 0.0, 1.0, 3.0],
            [1.0, 2.0, 3.0, 4.0],
        ]
        with self.assertRaises(ValueError):
            Matrix(invalid)
        # Test input with invalid type
        with self.assertRaises(TypeError):
            Matrix("invalid")
        # Test input with invalid size / nested types
        with self.assertRaises(TypeError):
            Matrix([[1, 2, 3, 4], [1, 2, 3], [1, 2, 3, 4]])
        with self.assertRaises(TypeError):
            Matrix([1, 2, 3])

        # Invalid sub-type
        with self.assertRaises(TypeError):
            Matrix([[1, 2, 3, 4], "abc", [1, 2, 3, 4]])

        # test out-of-bounds access
        m = Matrix()
        with self.assertRaises(IndexError):
            m[0, 4]
        with self.assertRaises(IndexError):
            m[4, 0]
        with self.assertRaises(IndexError):
            m["ab"]

        # test __repr__ methods
        m = Matrix(vals4x4)
        mRepr = "Matrix([[1.0, 0.0, 0.0, 1.0],\n        [0.0, 1.0, 0.0, 2.0],\n        [0.0, 0.0, 1.0, 3.0],\n        [0.0, 0.0, 0.0, 1.0]])"
        self.assertEqual(repr(m), mRepr)
        self.assertEqual(str(eval(repr(m))), mRepr)

    def test_matrix_functionality(self):
        # Test rotate methods
        def matrix_almost_equal(m, target_matrix):
            for r, row in enumerate(target_matrix):
                for c, target_value in enumerate(row):
                    self.assertAlmostEqual(m[r, c], target_value)

        root_3_over_2 = math.sqrt(3) / 2
        m_rotate_x_30 = [
            [1, 0, 0, 0],
            [0, root_3_over_2, -1 / 2, 0],
            [0, 1 / 2, root_3_over_2, 0],
            [0, 0, 0, 1],
        ]
        mx = Matrix()
        mx.rotate_x(30 * DEG2RAD)
        matrix_almost_equal(mx, m_rotate_x_30)

        m_rotate_y_30 = [
            [root_3_over_2, 0, 1 / 2, 0],
            [0, 1, 0, 0],
            [-1 / 2, 0, root_3_over_2, 0],
            [0, 0, 0, 1],
        ]
        my = Matrix()
        my.rotate_y(30 * DEG2RAD)
        matrix_almost_equal(my, m_rotate_y_30)

        m_rotate_z_30 = [
            [root_3_over_2, -1 / 2, 0, 0],
            [1 / 2, root_3_over_2, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
        mz = Matrix()
        mz.rotate_z(30 * DEG2RAD)
        matrix_almost_equal(mz, m_rotate_z_30)

        # Test matrix multipy vector
        v = Vector(1, 0, 0)
        self.assertTupleAlmostEquals(
            mz.multiply(v).to_tuple(), (root_3_over_2, 1 / 2, 0), 7
        )

        # Test matrix multipy matrix
        m_rotate_xy_30 = [
            [root_3_over_2, 0, 1 / 2, 0],
            [1 / 4, root_3_over_2, -root_3_over_2 / 2, 0],
            [-root_3_over_2 / 2, 1 / 2, 3 / 4, 0],
            [0, 0, 0, 1],
        ]
        mxy = mx.multiply(my)
        matrix_almost_equal(mxy, m_rotate_xy_30)

        # Test matrix inverse
        vals4x4 = [[1, 2, 3, 4], [5, 1, 6, 7], [8, 9, 1, 10], [0, 0, 0, 1]]
        vals4x4_invert = [
            [-53 / 144, 25 / 144, 1 / 16, -53 / 144],
            [43 / 144, -23 / 144, 1 / 16, -101 / 144],
            [37 / 144, 7 / 144, -1 / 16, -107 / 144],
            [0, 0, 0, 1],
        ]
        m = Matrix(vals4x4).inverse()
        matrix_almost_equal(m, vals4x4_invert)

    def test_translate(self):
        e = Edge.make_circle(2, (1, 2, 3))
        e2 = e.translate(Vector(0, 0, 1))

        self.assertTupleAlmostEquals((1.0, 2.0, 4.0), e2.center().to_tuple(), 3)

    def test_vertices(self):
        e = Shape.cast(BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(1, 1, 0)).Edge())
        self.assertEqual(2, len(e.vertices()))

    def test_plane_equal(self):
        # default orientation
        self.assertEqual(
            Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), normal=(0, 0, 1)),
            Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), normal=(0, 0, 1)),
        )
        # moved origin
        self.assertEqual(
            Plane(origin=(2, 1, -1), x_dir=(1, 0, 0), normal=(0, 0, 1)),
            Plane(origin=(2, 1, -1), x_dir=(1, 0, 0), normal=(0, 0, 1)),
        )
        # moved x-axis
        self.assertEqual(
            Plane(origin=(0, 0, 0), x_dir=(1, 1, 0), normal=(0, 0, 1)),
            Plane(origin=(0, 0, 0), x_dir=(1, 1, 0), normal=(0, 0, 1)),
        )
        # moved z-axis
        self.assertEqual(
            Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), normal=(0, 1, 1)),
            Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), normal=(0, 1, 1)),
        )

    def test_plane_not_equal(self):
        # type difference
        for value in [None, 0, 1, "abc"]:
            self.assertNotEqual(
                Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), normal=(0, 0, 1)), value
            )
        # origin difference
        self.assertNotEqual(
            Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), normal=(0, 0, 1)),
            Plane(origin=(0, 0, 1), x_dir=(1, 0, 0), normal=(0, 0, 1)),
        )
        # x-axis difference
        self.assertNotEqual(
            Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), normal=(0, 0, 1)),
            Plane(origin=(0, 0, 0), x_dir=(1, 1, 0), normal=(0, 0, 1)),
        )
        # z-axis difference
        self.assertNotEqual(
            Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), normal=(0, 0, 1)),
            Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), normal=(0, 1, 1)),
        )

    def test_invalid_plane(self):
        # Test plane creation error handling
        with self.assertRaises(ValueError):
            Plane(origin=(0, 0, 0), x_dir=(0, 0, 0), normal=(0, 1, 1))
        with self.assertRaises(ValueError):
            Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), normal=(0, 0, 0))

    def test_plane_methods(self):
        # Test error checking
        p = Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), normal=(0, 1, 0))
        with self.assertRaises(ValueError):
            p.to_local_coords("box")
        with self.assertRaises(NotImplementedError):
            p.mirror_in_plane([Solid.make_box(1, 1, 1)], "Z")

        # Test translation to local coordinates
        # local_box = Workplane(p.to_local_coords(Solid.make_box(1, 1, 1)))
        local_box = p.to_local_coords(Solid.make_box(1, 1, 1))
        # local_box_vertices = [(v.X, v.Y, v.Z) for v in local_box.vertices().vals()]
        local_box_vertices = [(v.X, v.Y, v.Z) for v in local_box.vertices()]
        target_vertices = [
            (0, -1, 0),
            (0, 0, 0),
            (0, -1, 1),
            (0, 0, 1),
            (1, -1, 0),
            (1, 0, 0),
            (1, -1, 1),
            (1, 0, 1),
        ]
        for i, target_point in enumerate(target_vertices):
            self.assertTupleAlmostEquals(target_point, local_box_vertices[i], 7)

        # Test mirror_in_plane
        # mirror_box = Workplane(p.mirror_in_plane([Solid.make_box(1, 1, 1)], "Y")[0])
        mirror_box = p.mirror_in_plane([Solid.make_box(1, 1, 1)], "Y")[0]
        # mirror_box_vertices = [(v.X, v.Y, v.Z) for v in mirror_box.vertices().vals()]
        mirror_box_vertices = [(v.X, v.Y, v.Z) for v in mirror_box.vertices()]
        target_vertices = [
            (0, 0, 1),
            (0, 0, 0),
            (0, -1, 1),
            (0, -1, 0),
            (-1, 0, 1),
            (-1, 0, 0),
            (-1, -1, 1),
            (-1, -1, 0),
        ]
        for i, target_point in enumerate(target_vertices):
            self.assertTupleAlmostEquals(target_point, mirror_box_vertices[i], 7)

    def test_location(self):

        loc0 = Location()
        T = loc0.wrapped.Transformation().TranslationPart()
        self.assertTupleAlmostEquals((T.X(), T.Y(), T.Z()), (0, 0, 0), 6)
        angle = loc0.wrapped.Transformation().GetRotation().GetRotationAngle() * RAD2DEG
        self.assertAlmostEqual(0, angle)

        # Tuple
        loc0 = Location((0, 0, 1))

        T = loc0.wrapped.Transformation().TranslationPart()
        self.assertTupleAlmostEquals((T.X(), T.Y(), T.Z()), (0, 0, 1), 6)

        # Vector
        loc1 = Location(Vector(0, 0, 1))

        T = loc1.wrapped.Transformation().TranslationPart()
        self.assertTupleAlmostEquals((T.X(), T.Y(), T.Z()), (0, 0, 1), 6)

        # rotation + translation
        loc2 = Location(Vector(0, 0, 1), Vector(0, 0, 1), 45)

        angle = loc2.wrapped.Transformation().GetRotation().GetRotationAngle() * RAD2DEG
        self.assertAlmostEqual(45, angle)

        # gp_Trsf
        T = gp_Trsf()
        T.SetTranslation(gp_Vec(0, 0, 1))
        loc3 = Location(T)

        self.assertEqual(
            loc1.wrapped.Transformation().TranslationPart().Z(),
            loc3.wrapped.Transformation().TranslationPart().Z(),
        )

        # Test creation from the OCP.gp.gp_Trsf object
        loc4 = Location(gp_Trsf())
        self.assertTupleAlmostEquals(loc4.to_tuple()[0], (0, 0, 0), 7)
        self.assertTupleAlmostEquals(loc4.to_tuple()[1], (0, 0, 0), 7)

        # Test creation from Plane and Vector
        loc4 = Location(Plane.XY, (0, 0, 1))
        self.assertTupleAlmostEquals(loc4.to_tuple()[0], (0, 0, 1), 7)
        self.assertTupleAlmostEquals(loc4.to_tuple()[1], (0, 0, 0), 7)

        # Test composition
        loc4 = Location((0, 0, 0), Vector(0, 0, 1), 15)

        loc5 = loc1 * loc4
        loc6 = loc4 * loc4
        loc7 = loc4**2

        T = loc5.wrapped.Transformation().TranslationPart()
        self.assertTupleAlmostEquals((T.X(), T.Y(), T.Z()), (0, 0, 1), 6)

        angle5 = (
            loc5.wrapped.Transformation().GetRotation().GetRotationAngle() * RAD2DEG
        )
        self.assertAlmostEqual(15, angle5)

        angle6 = (
            loc6.wrapped.Transformation().GetRotation().GetRotationAngle() * RAD2DEG
        )
        self.assertAlmostEqual(30, angle6)

        angle7 = (
            loc7.wrapped.Transformation().GetRotation().GetRotationAngle() * RAD2DEG
        )
        self.assertAlmostEqual(30, angle7)

        # Test error handling on creation
        with self.assertRaises(TypeError):
            Location([0, 0, 1])
        with self.assertRaises(TypeError):
            Location("xy_plane")

    def test_location_repr_and_str(self):
        self.assertEqual(
            repr(Location()), "(p=(0.00, 0.00, 0.00), o=(0.00, -0.00, 0.00))"
        )
        self.assertEqual(
            str(Location()),
            "Location: (position=(0.00, 0.00, 0.00), orientation=(0.00, -0.00, 0.00))",
        )

    def test_location_inverted(self):
        loc = Location(Plane.XZ)
        self.assertTupleAlmostEquals(
            loc.inverse.rotation().to_tuple(), (-math.pi / 2, 0, 0), 6
        )

    def test_edge_wrapper_radius(self):

        # get a radius from a simple circle
        e0 = Edge.make_circle(2.4)
        self.assertAlmostEqual(e0.radius(), 2.4)

        # radius of an arc
        e1 = Edge.make_circle(1.8, pnt=(5, 6, 7), dir=(1, 1, 1), angle1=20, angle2=30)
        self.assertAlmostEqual(e1.radius(), 1.8)

        # test value errors
        e2 = Edge.make_ellipse(10, 20)
        with self.assertRaises(ValueError):
            e2.radius()

        # radius from a wire
        w0 = Wire.make_circle(10, Vector(1, 2, 3), (-1, 0, 1))
        self.assertAlmostEqual(w0.radius(), 10)

        # radius from a wire with multiple edges
        rad = 2.3
        pnt = (7, 8, 9)
        direction = (1, 0.5, 0.1)
        w1 = Wire.assemble_edges(
            [
                Edge.make_circle(rad, pnt, direction, 0, 10),
                Edge.make_circle(rad, pnt, direction, 10, 25),
                Edge.make_circle(rad, pnt, direction, 25, 230),
            ]
        )
        self.assertAlmostEqual(w1.radius(), rad)

        # test value error from wire
        w2 = Wire.make_polygon(
            [
                Vector(-1, 0, 0),
                Vector(0, 1, 0),
                Vector(1, -1, 0),
            ]
        )
        with self.assertRaises(ValueError):
            w2.radius()

        # (I think) the radius of a wire is the radius of it's first edge.
        # Since this is stated in the docstring better make sure.
        no_rad = Wire.assemble_edges(
            [
                Edge.make_line(Vector(0, 0, 0), Vector(0, 1, 0)),
                Edge.make_circle(1.0, angle1=90, angle2=270),
            ]
        )
        with self.assertRaises(ValueError):
            no_rad.radius()
        yes_rad = Wire.assemble_edges(
            [
                Edge.make_circle(1.0, angle1=90, angle2=270),
                Edge.make_line(Vector(0, -1, 0), Vector(0, 1, 0)),
            ]
        )
        self.assertAlmostEqual(yes_rad.radius(), 1.0)
        many_rad = Wire.assemble_edges(
            [
                Edge.make_circle(1.0, angle1=0, angle2=180),
                Edge.make_circle(3.0, pnt=Vector(2, 0, 0), angle1=180, angle2=359),
            ]
        )
        self.assertAlmostEqual(many_rad.radius(), 1.0)


class TestAxis(unittest.TestCase):
    """Test the Axis class"""

    def test_axis_from_occt(self):
        occt_axis = gp_Ax1(gp_Pnt(1, 1, 1), gp_Dir(0, 1, 0))
        test_axis = Axis.from_occt(occt_axis)
        self.assertTupleAlmostEquals(test_axis.position.to_tuple(), (1, 1, 1), 5)
        self.assertTupleAlmostEquals(test_axis.direction.to_tuple(), (0, 1, 0), 5)

    def test_axis_repr_and_str(self):
        self.assertEqual(repr(Axis.X), "((0.0, 0.0, 0.0),(1.0, 0.0, 0.0))")
        self.assertEqual(str(Axis.Y), "Axis: ((0.0, 0.0, 0.0),(0.0, 1.0, 0.0))")

    def test_axis_copy(self):
        x_copy = Axis.X.copy()
        self.assertTupleAlmostEquals(x_copy.position.to_tuple(), (0, 0, 0), 5)
        self.assertTupleAlmostEquals(x_copy.direction.to_tuple(), (1, 0, 0), 5)

    def test_axis_to_location(self):
        # TODO: Verify this is correct
        x_location = Axis.X.to_location()
        self.assertTrue(isinstance(x_location, Location))
        self.assertTupleAlmostEquals(x_location.position().to_tuple(), (0, 0, 0), 5)
        self.assertTupleAlmostEquals(
            x_location.rotation().to_tuple(), (-math.pi, -math.pi / 2, 0), 5
        )

    def test_axis_to_plane(self):
        x_plane = Axis.X.to_plane()
        self.assertTrue(isinstance(x_plane, Plane))
        self.assertTupleAlmostEquals(x_plane.origin.to_tuple(), (0, 0, 0), 5)
        self.assertTupleAlmostEquals(x_plane.z_dir.to_tuple(), (1, 0, 0), 5)

    def test_axis_is_coaxial(self):
        self.assertTrue(Axis.X.is_coaxial(Axis((0, 0, 0), (1, 0, 0))))
        self.assertFalse(Axis.X.is_coaxial(Axis((0, 0, 1), (1, 0, 0))))
        self.assertFalse(Axis.X.is_coaxial(Axis((0, 0, 0), (0, 1, 0))))

    def test_axis_is_normal(self):
        self.assertTrue(Axis.X.is_normal(Axis.Y))
        self.assertFalse(Axis.X.is_normal(Axis.X))

    def test_axis_is_opposite(self):
        self.assertTrue(Axis.X.is_opposite(Axis((1, 1, 1), (-1, 0, 0))))
        self.assertFalse(Axis.X.is_opposite(Axis.X))

    def test_axis_is_parallel(self):
        self.assertTrue(Axis.X.is_parallel(Axis((1, 1, 1), (1, 0, 0))))
        self.assertFalse(Axis.X.is_parallel(Axis.Y))

    def test_axis_angle_between(self):
        self.assertAlmostEqual(Axis.X.angle_between(Axis.Y), 90, 5)
        self.assertAlmostEqual(
            Axis.X.angle_between(Axis((1, 1, 1), (-1, 0, 0))), 180, 5
        )

    def test_axis_reversed(self):
        self.assertTupleAlmostEquals(
            Axis.X.reversed().direction.to_tuple(), (-1, 0, 0), 5
        )


class ProjectionTests(unittest.TestCase):
    def test_flat_projection(self):

        sphere = Solid.make_sphere(50)
        projection_direction = Vector(0, -1, 0)
        planar_text_faces = (
            Compound.make_2d_text("Flat", 30, halign=Halign.CENTER)
            .rotate((0, 0, 0), (1, 0, 0), 90)
            .faces()
        )
        projected_text_faces = [
            f.project_to_shape(sphere, projection_direction)[0]
            for f in planar_text_faces
        ]
        self.assertEqual(len(projected_text_faces), 4)

    def test_conical_projection(self):
        sphere = Solid.make_sphere(50)
        projection_center = Vector(0, 0, 0)
        planar_text_faces = (
            Compound.make_2d_text("Conical", 25, halign=Halign.CENTER)
            .rotate((0, 0, 0), (1, 0, 0), 90)
            .translate((0, -60, 0))
            .faces()
        )

        projected_text_faces = [
            f.project_to_shape(sphere, center=projection_center)[0]
            for f in planar_text_faces
        ]
        self.assertEqual(len(projected_text_faces), 8)

    def test_projection_with_internal_points(self):
        sphere = Solid.make_sphere(50)
        f = Face.make_plane(10, 10).translate(Vector(0, 0, 60))
        pts = [Vector(x, y, 60) for x in [-5, 5] for y in [-5, 5]]
        projected_faces = f.project_to_shape(
            sphere, center=(0, 0, 0), internal_face_points=pts
        )
        self.assertEqual(len(projected_faces), 1)

    def test_text_projection(self):

        sphere = Solid.make_sphere(50)
        arch_path = (
            sphere.cut(
                Solid.make_cylinder(
                    80, 100, pnt=Vector(-50, 0, -70), dir=Vector(1, 0, 0)
                )
            )
            .edges()
            .sort_by(Axis.Z)[0]
        )

        projected_text = sphere.project_text(
            txt="fox",
            fontsize=14,
            depth=3,
            path=arch_path,
        )
        self.assertEqual(len(projected_text.solids()), 3)
        projected_text = sphere.project_text(
            txt="dog",
            fontsize=14,
            depth=0,
            path=arch_path,
        )
        self.assertEqual(len(projected_text.solids()), 0)
        self.assertEqual(len(projected_text.faces()), 3)

    def test_error_handling(self):
        sphere = Solid.make_sphere(50)
        f = Face.make_plane(10, 10)
        with self.assertRaises(ValueError):
            f.project_to_shape(sphere, center=None, direction=None)[0]
        w = Face.make_plane(10, 10).outer_wire()
        with self.assertRaises(ValueError):
            w.project_to_shape(sphere, center=None, direction=None)[0]


class EmbossTests(unittest.TestCase):
    def test_emboss_text(self):

        sphere = Solid.make_sphere(50)
        arch_path = (
            sphere.cut(
                Solid.make_cylinder(
                    80, 100, pnt=Vector(-50, 0, -70), dir=Vector(1, 0, 0)
                )
            )
            .edges()
            .sort_by(Axis.Z)[0]
        )
        embossed_text = sphere.emboss_text(
            txt="quick",
            fontsize=14,
            depth=3,
            path=arch_path,
        )
        self.assertEqual(len(embossed_text.solids()), 6)
        embossed_text = sphere.emboss_text(
            txt="jumped",
            fontsize=14,
            depth=0,
            path=arch_path,
        )
        self.assertEqual(len(embossed_text.solids()), 0)
        self.assertEqual(len(embossed_text.faces()), 7)

    # def test_emboss_face(self):
    #     sphere = Solid.make_sphere(50)
    #     square_face = Face.make_plane(12, 12)
    #     square_face = Face.make_from_wires(Wire.make_rect(12, 12), [])
    #     embossed_face = square_face.emboss_to_shape(
    #         sphere,
    #         surface_point=(0, 0, 50),
    #         surface_x_direction=(1, 1, 0),
    #     )
    #     self.assertTrue(embossed_face.is_valid())

    #     pts = [Vector(x, y, 0) for x in [-5, 5] for y in [-5, 5]]
    #     embossed_face = square_face.emboss_to_shape(
    #         sphere,
    #         surface_point=(0, 0, 50),
    #         surface_x_direction=(1, 1, 0),
    #         internal_face_points=pts,
    #     )
    #     self.assertTrue(embossed_face.is_valid())

    def test_emboss_wire(self):
        sphere = Solid.make_sphere(50)
        triangle_face = Wire.make_polygon([(0, 0, 0), (6, 6, 0), (-6, 6, 0), (0, 0, 0)])
        embossed_face = triangle_face.emboss_to_shape(
            sphere,
            surface_point=(0, 0, 50),
            surface_x_direction=(1, 1, 0),
        )
        self.assertTrue(embossed_face.is_valid())


class VertexTests(unittest.TestCase):
    """Test the extensions to the cadquery Vertex class"""

    def test_basic_vertex(self):
        v = Vertex()
        self.assertEqual(0, v.X)

        v = Vertex(1, 1, 1)
        self.assertEqual(1, v.X)
        self.assertEqual(Vector, type(v.center()))

        with self.assertRaises(ValueError):
            Vertex(Vector())


    def test_vertex_add(self):
        test_vertex = Vertex(0, 0, 0)
        self.assertTupleAlmostEquals(
            (test_vertex + (100, -40, 10)).to_tuple(), (100, -40, 10), 7
        )
        self.assertTupleAlmostEquals(
            (test_vertex + Vector(100, -40, 10)).to_tuple(), (100, -40, 10), 7
        )
        self.assertTupleAlmostEquals(
            (test_vertex + Vertex(100, -40, 10)).to_tuple(),
            (100, -40, 10),
            7,
        )
        with self.assertRaises(TypeError):
            test_vertex + [1, 2, 3]

    def test_vertex_sub(self):
        test_vertex = Vertex(0, 0, 0)
        self.assertTupleAlmostEquals(
            (test_vertex - (100, -40, 10)).to_tuple(), (-100, 40, -10), 7
        )
        self.assertTupleAlmostEquals(
            (test_vertex - Vector(100, -40, 10)).to_tuple(), (-100, 40, -10), 7
        )
        self.assertTupleAlmostEquals(
            (test_vertex - Vertex(100, -40, 10)).to_tuple(),
            (-100, 40, -10),
            7,
        )
        with self.assertRaises(TypeError):
            test_vertex - [1, 2, 3]

    def test_vertex_str(self):
        self.assertEqual(str(Vertex(0, 0, 0)), "Vertex: (0.0, 0.0, 0.0)")

    def test_vertex_to_vector(self):
        self.assertIsInstance(Vertex(0, 0, 0).to_vector(), Vector)
        self.assertTupleAlmostEquals(
            Vertex(0, 0, 0).to_vector().to_tuple(), (0.0, 0.0, 0.0), 7
        )


if __name__ == "__main__":
    unittest.main()