import unittest
import numpy as np
from spherical_geometry import *


class TestSphereDistance(unittest.TestCase):

    def test_same_start_and_end_have_zero_distance(self):
        """for a range of lats and longs test that identical start and end points map to zero distance"""
        for lat1 in range(-90, 90, 5):
            for lon1 in range(-180, 180, 5):
                a = sphere_distance(lat1, lon1, lat1, lon1)
                self.assertEqual(0.0, a)

    def test_pole_to_pole(self):
        """make sure pole to pole distance is pi*r"""
        a = sphere_distance(-90.0, 0.0, 90.0, 0.0)
        self.assertEqual(6371.0088 * np.pi, a)

    def test_round_equator(self):
        """make sure half the equator is pi*r"""
        a = sphere_distance(0.0, 0.0, 0.0, 180.0)
        self.assertEqual(6371.0088 * np.pi, a)

    def test_small_steps_latitude(self):
        """test that 5degree lat increment is one 36th of pi*r to better than 1cm"""
        a = sphere_distance(-90.0, 0.0, -85.0, 0.0)
        self.assertAlmostEqual(6371.0088 * np.pi / 36, a, delta=0.00000001)

    def test_small_steps_longitude(self):
        """test that 5degree long increment is one 36th of pi*r to better than 1cm"""
        a = sphere_distance(0.0, 22.0, 0.0, 27.0)
        self.assertAlmostEqual(6371.0088 * np.pi / 36, a, delta=0.00000001)


class TestAngularDistance(unittest.TestCase):

    def test_same_start_and_end_have_zero_angular_distance(self):
        """for a range of lats and longs test that identical start and end points map to zero distance"""
        for lat1 in range(-90, 90, 5):
            for lon1 in range(-180, 180, 5):
                a = angular_distance(lat1, lon1, lat1, lon1)
                self.assertEqual(0.0, a)

    def test_pole_to_pole(self):
        """make sure pole to pole distance is pi"""
        a = angular_distance(-90.0, 0.0, 90.0, 0.0)
        self.assertEqual(np.pi, a)

    def test_round_equator(self):
        """make sure half the equator is pi"""
        a = angular_distance(0.0, 0.0, 0.0, 180.0)
        self.assertEqual(np.pi, a)

    def test_round_the_world_is_zero(self):
        """test all the way round the equator 0 - 360 gives zero angular distance"""
        a = angular_distance(0.0, 0.0, 0.0, 360.0)
        self.assertAlmostEqual(0.0, a, delta=0.00000001)


class TestLatLonFromCourseAndDistance(unittest.TestCase):

    def test_going_nowhere(self):
        """If ship heads north from 0,0 and travels 0 distance, should end up at same place"""
        lat, lon = lat_lon_from_course_and_distance(0.0, 0.0, 0.0, 0.0)
        self.assertEqual(0.0, lat)
        self.assertEqual(0.0, lon)

    def test_heading_north_from_pole_to_pole(self):
        """headin north from the southpole for an angular distance of pi takes you to the north pole"""
        lat, lon = lat_lon_from_course_and_distance(-90.0, 0.0, 0.0, np.pi * 6371.0088)
        self.assertEqual(90.0, lat)
        self.assertEqual(0.0, lon)

    def test_heading_north_from_pole_to_pole_on_different_headings(self):
        """headin north from the southpole for an angular distance of pi takes you to the north pole"""
        for i in range(0, 100):
            lat, lon = lat_lon_from_course_and_distance(-90.0, 0.0, i * 360. / 100., np.pi * 6371.0088)
            self.assertEqual(90.0, lat)

    def test_heading_east_round_equator(self):
        lat, lon = lat_lon_from_course_and_distance(0.0, 0.0, 90., 2 * np.pi * 6371.0088)
        self.assertAlmostEqual(0.0, lat, delta=0.00000001)
        self.assertAlmostEqual(0.0, lon, delta=0.00000001)

    def test_heading_eastish_round_equator(self):
        lat, lon = lat_lon_from_course_and_distance(0.0, 0.0, 45., np.pi * 6371.0088)
        self.assertAlmostEqual(0.0, lat, delta=0.00000001)
        self.assertIn(lon, [-180, 180])


class TestCourseBetweenPoints(unittest.TestCase):

    def test_heading_just_east_of_north(self):
        """just east of north heading should be zero"""
        heading = course_between_points(0.0, 0.0, 1.3, 0.0000001)
        self.assertAlmostEqual(heading, 0.0, delta=0.00001)

    def test_heading_just_west_of_north(self):
        """just west of north heading should be 360.0"""
        heading = course_between_points(0.0, 0.0, 1.3, -0.0000001)
        self.assertAlmostEqual(heading, 360.0, delta=0.00001)

    def test_heading_east(self):
        """heading due east should be course of 90degrees"""
        heading = course_between_points(0.0, 0.0, 0.0, 23.2)
        self.assertAlmostEqual(heading, 90.0, delta=0.0000001)

    def test_heading_west(self):
        """heading due west should be course of 90degrees"""
        heading = course_between_points(0.0, 0.0, 0.0, -23.2)
        self.assertAlmostEqual(heading, 270.0, delta=0.0000001)

    def test_heading_south(self):
        """heading due south should be course of 90degrees"""
        heading = course_between_points(0.0, 0.0, -11.1111, 0.0)
        self.assertAlmostEqual(heading, 180.0, delta=0.0000001)

    def test_heading_south2(self):
        """test added in response to bug where heading due south or due north occasionally 
        returned nan"""
        heading = course_between_points(4.0, 92.0, 3.0, 92.0)
        self.assertAlmostEqual(heading, 180.0, delta=0.000001)


class TestIntermediatePoints(unittest.TestCase):

    def test_equator_is_halfway_from_pole_to_pole(self):
        """make sure equator is halfway between (almost) the poles"""
        lat, lon = intermediate_point(-89, 0, 89, 0,
                                      0.5)  # don't do 90S to 90N as the great circle is not uniquely defined
        self.assertEqual(0.0, lat)
        self.assertEqual(0.0, lon)

    def test_that_5deg_is_one_72th_of_equator(self):
        """test that 5degrees is one eighteenth of 90degrees around the equator"""
        lat, lon = intermediate_point(0.0, 0.0, 0.0, 90.0, 1. / 18.)
        self.assertAlmostEqual(5.0, lon, delta=0.0000001)

    def test_any_fraction_of_no_move_is_nothing(self):
        lat, lon = intermediate_point(10.0, 152.0, 10.0, 152.0, 0.75)
        self.assertEqual(152.0, lon)
        self.assertEqual(10.0, lat)


# intermediate_point(lat1,lon1,lat2,lon2,f)


if __name__ == '__main__':
    unittest.main()
