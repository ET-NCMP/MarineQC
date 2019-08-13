import unittest
import numpy as np
import math
import Climatology as clim
from SimpleIMMA import IMMA
import Extended_IMMA as ex


class TestSafenames(unittest.TestCase):

    def test_simplecase(self):
        fname = 'D/BU'
        self.assertEqual('D_BU', ex.safe_filename(fname))
        fname = 'G*NY'
        self.assertEqual('G_NY', ex.safe_filename(fname))


class TestOldBuddy(unittest.TestCase):

    def setUp(self):

        vals = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 1, 'DY': 1, 'HR': 2, 'LAT': 0.5, 'LON': 20.5, 'SST': 5.0},
                {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 31, 'HR': 2, 'LAT': 1.5, 'LON': 20.5, 'SST': 2.0},
                {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 30, 'HR': 2, 'LAT': 1.5, 'LON': 21.5, 'SST': 2.0},
                {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 29, 'HR': 2, 'LAT': 1.5, 'LON': 19.5, 'SST': 2.0},
                {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 28, 'HR': 2, 'LAT': 0.5, 'LON': 19.5, 'SST': 2.0},
                {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 6, 'HR': 2, 'LAT': 0.5, 'LON': 21.5, 'SST': 2.0},
                {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 7, 'HR': 2, 'LAT': -0.5, 'LON': 20.5, 'SST': 2.0},
                {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 8, 'HR': 2, 'LAT': -0.5, 'LON': 21.5, 'SST': 2.0},
                {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 9, 'HR': 2, 'LAT': -0.5, 'LON': 19.5, 'SST': 2.0}]

        self.reps = []

        for v in vals:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReport(rec)
            rep.add_climate_variable('SST', 0.5)
            self.reps.append(rep)

        vals2 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 1, 'DY': 1, 'HR': 2, 'LAT': 0.5, 'LON': 20.5, 'SST': 5.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 21, 'HR': 2, 'LAT': 1.5, 'LON': 20.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 20, 'HR': 2, 'LAT': 1.5, 'LON': 21.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 19, 'HR': 2, 'LAT': 1.5, 'LON': 19.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 18, 'HR': 2, 'LAT': 0.5, 'LON': 19.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 16, 'HR': 2, 'LAT': 0.5, 'LON': 21.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 17, 'HR': 2, 'LAT': -0.5, 'LON': 20.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 18, 'HR': 2, 'LAT': -0.5, 'LON': 21.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 19, 'HR': 2, 'LAT': -0.5, 'LON': 19.5, 'SST': 2.0}]

        self.reps2 = []

        for v in vals2:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReport(rec)
            rep.add_climate_variable('SST', 0.5)
            self.reps2.append(rep)

        vals3 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 1, 'DY': 1, 'HR': 2, 'LAT': 0.5, 'LON': 20.5, 'SST': 5.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 21, 'HR': 2, 'LAT': 2.5, 'LON': 20.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 20, 'HR': 2, 'LAT': 2.5, 'LON': 22.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 19, 'HR': 2, 'LAT': 2.5, 'LON': 18.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 18, 'HR': 2, 'LAT': 0.5, 'LON': 18.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 16, 'HR': 2, 'LAT': 0.5, 'LON': 22.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 17, 'HR': 2, 'LAT': -1.5, 'LON': 20.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 18, 'HR': 2, 'LAT': -1.5, 'LON': 22.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 19, 'HR': 2, 'LAT': -1.5, 'LON': 18.5, 'SST': 2.0}]

        self.reps3 = []

        for v in vals3:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReport(rec)
            rep.add_climate_variable('SST', 0.5)
            self.reps3.append(rep)

        self.dummy_pentad_stdev = clim.Climatology(np.full([73, 180, 360], 1.5))

        vals4 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 1, 'DY': 1, 'HR': 2, 'LAT': 0.5, 'LON': 20.5, 'SST': 5.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 21, 'HR': 2, 'LAT': 3.5, 'LON': 20.5, 'SST': 1.9},
                 {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 20, 'HR': 2, 'LAT': 3.5, 'LON': 23.5, 'SST': 1.7},
                 {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 19, 'HR': 2, 'LAT': 3.5, 'LON': 17.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 18, 'HR': 2, 'LAT': 0.5, 'LON': 17.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 16, 'HR': 2, 'LAT': 0.5, 'LON': 23.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 17, 'HR': 2, 'LAT': -2.5, 'LON': 20.5, 'SST': 2.0},
                 {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 18, 'HR': 2, 'LAT': -2.5, 'LON': 23.5, 'SST': 2.3},
                 {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 19, 'HR': 2, 'LAT': -2.5, 'LON': 17.5, 'SST': 2.1}]

        self.reps4 = []

        for v in vals4:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReport(rec)
            rep.add_climate_variable('SST', 0.5)
            self.reps4.append(rep)

        self.dummy_pentad_stdev = clim.Climatology(np.full([73, 180, 360], 1.5))

    def test_eight_near_neighbours(self):

        g = ex.Np_Super_Ob()
        for rep in self.reps:
            g.add_rep(rep.lat(),
                      rep.lon(),
                      rep.getvar('YR'),
                      rep.getvar('MO'),
                      rep.getvar('DY'),
                      rep.getanom('SST'))
        g.take_average()
        g.get_buddy_limits_with_parameters(self.dummy_pentad_stdev, [[1, 1, 2], [2, 2, 2], [1, 1, 4], [2, 2, 4]],
                                           [[0, 5, 15, 100], [0], [0, 5, 15, 100], [0]],
                                           [[4.0, 3.5, 3.0, 2.5], [4.0], [4.0, 3.5, 3.0, 2.5], [4.0]])
        mn = g.get_buddy_mean(0.5, 20.5, 1, 1)
        sd = g.get_buddy_stdev(0.5, 20.5, 1, 1)
        self.assertEqual(mn, 1.5)
        self.assertEqual(sd, 3.5 * 1.5)

    def test_eight_distant_near_neighbours(self):

        g = ex.Np_Super_Ob()
        for rep in self.reps2:
            g.add_rep(rep.lat(),
                      rep.lon(),
                      rep.getvar('YR'),
                      rep.getvar('MO'),
                      rep.getvar('DY'),
                      rep.getanom('SST'))
        g.take_average()
        g.get_buddy_limits_with_parameters(self.dummy_pentad_stdev, [[1, 1, 2], [2, 2, 2], [1, 1, 4], [2, 2, 4]],
                                           [[0, 5, 15, 100], [0], [0, 5, 15, 100], [0]],
                                           [[4.0, 3.5, 3.0, 2.5], [4.0], [4.0, 3.5, 3.0, 2.5], [4.0]])
        mn = g.get_buddy_mean(0.5, 20.5, 1, 1)
        sd = g.get_buddy_stdev(0.5, 20.5, 1, 1)
        self.assertEqual(mn, 1.5)
        self.assertEqual(sd, 3.5 * 1.5)

    def test_eight_even_more_distant_near_neighbours(self):

        g = ex.Np_Super_Ob()
        for rep in self.reps3:
            g.add_rep(rep.lat(),
                      rep.lon(),
                      rep.getvar('YR'),
                      rep.getvar('MO'),
                      rep.getvar('DY'),
                      rep.getanom('SST'))
        g.take_average()
        g.get_buddy_limits_with_parameters(self.dummy_pentad_stdev, [[1, 1, 2], [2, 2, 2], [1, 1, 4], [2, 2, 4]],
                                           [[0, 5, 15, 100], [0], [0, 5, 15, 100], [0]],
                                           [[4.0, 3.5, 3.0, 2.5], [4.0], [4.0, 3.5, 3.0, 2.5], [4.0]])
        mn = g.get_buddy_mean(0.5, 20.5, 1, 1)
        sd = g.get_buddy_stdev(0.5, 20.5, 1, 1)
        self.assertEqual(mn, 1.5)
        self.assertEqual(sd, 4.0 * 1.5)

    def test_eight_too_distant_neighbours(self):

        g = ex.Np_Super_Ob()
        for rep in self.reps4:
            g.add_rep(rep.lat(),
                      rep.lon(),
                      rep.getvar('YR'),
                      rep.getvar('MO'),
                      rep.getvar('DY'),
                      rep.getanom('SST'))
        g.take_average()
        g.get_buddy_limits_with_parameters(self.dummy_pentad_stdev,
                                           [[1, 1, 2], [2, 2, 2], [1, 1, 4], [2, 2, 4]],
                                           [[0, 5, 15, 100], [0], [0, 5, 15, 100], [0]],
                                           [[4.0, 3.5, 3.0, 2.5], [4.0], [4.0, 3.5, 3.0, 2.5], [4.0]])
        mn = g.get_buddy_mean(0.5, 20.5, 1, 1)
        sd = g.get_buddy_stdev(0.5, 20.5, 1, 1)
        self.assertEqual(mn, 0.0)
        self.assertEqual(sd, 500.0)


class TestGetThresholdMultiplier(unittest.TestCase):
    # multiplier = get_threshold_multiplier(total_nobs,nob_limits,multiplier_values)
    def test_nobs_limits_not_ascending(self):
        with self.assertRaises(AssertionError):
            multiplier = ex.get_threshold_multiplier(0, [10, 5, 0], [4, 3, 2])

    def test_lowest_nobs_limit_not_zero(self):
        with self.assertRaises(AssertionError):
            multiplier = ex.get_threshold_multiplier(1, [1, 5, 10], [4, 3, 2])

    def test_simple(self):
        for n in range(1, 20):
            multiplier = ex.get_threshold_multiplier(n, [0, 5, 10], [4, 3, 2])
            if 1 <= n <= 5:
                self.assertEqual(multiplier, 4.0)
            elif 5 < n <= 10:
                self.assertEqual(multiplier, 3.0)
            else:
                self.assertEqual(multiplier, 2.0)


class TestClimVariable(unittest.TestCase):

    def test_that_basic_initialisation_works(self):
        c = ex.ClimVariable(0.0)

        self.assertEqual(c.getclim(), 0.0)
        self.assertEqual(c.getclim('clim'), 0.0)
        self.assertEqual(c.getclim('stdev'), None)

    def test_that_initialisation_with_clim_and_stdev_works(self):
        c = ex.ClimVariable(0.023, 1.1110)
        self.assertEqual(c.getclim(), 0.023)
        self.assertEqual(c.getclim('clim'), 0.023)
        self.assertEqual(c.getclim('stdev'), 1.1110)

    def test_setting_variables(self):
        c = ex.ClimVariable(3.2)
        self.assertEqual(c.getclim('clim'), 3.2)
        self.assertEqual(c.getclim('stdev'), None)
        c.setclim(5.9, 'clim')
        self.assertEqual(c.getclim('stdev'), None)
        self.assertEqual(c.getclim(), 5.9)
        c.setclim(12.33, 'stdev')
        self.assertEqual(c.getclim('stdev'), 12.33)
        self.assertEqual(c.getclim(), 5.9)


class TestNpSuperOb(unittest.TestCase):

    def setUp(self):

        vals = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0, 'LAT': 0.5, 'LON': 0.5, 'SST': 5.0},
                {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0, 'LAT': 0.5, 'LON': 0.5, 'SST': 5.0},
                {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 10.0, 'LAT': 0.5, 'LON': 0.5, 'SST': 5.0},
                {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 10.0, 'LAT': 1.5, 'LON': 0.5, 'SST': 5.0}]

        self.reps = []

        for v in vals:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReport(rec)
            rep.add_climate_variable('SST', 0.5)
            self.reps.append(rep)

        vals = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 1, 'DY': 1, 'HR': 0, 'LAT': 0.5, 'LON': 0.5, 'SST': 5.0},
                {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 1, 'HR': 0, 'LAT': 0.5, 'LON': 0.5, 'SST': 5.0},
                {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 1, 'HR': 10.0, 'LAT': 0.5, 'LON': 0.5, 'SST': 5.0},
                {'ID': 'BBBBBBBBB', 'YR': 2002, 'MO': 12, 'DY': 31, 'HR': 10.0, 'LAT': 0.5, 'LON': 0.5, 'SST': 2.0},
                {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 1, 'DY': 1, 'HR': 10.0, 'LAT': 1.5, 'LON': 0.5, 'SST': 5.0}]

        self.reps2 = []
        for v in vals:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReport(rec)
            rep.add_climate_variable('SST', 0.5)
            self.reps2.append(rep)

        self.dummy_pentad_stdev = clim.Climatology(np.full([73, 180, 360], 1.0))

    def test_neighbours(self):
        g = ex.Np_Super_Ob()
        for rep in self.reps2:
            g.add_rep(rep.lat(),
                      rep.lon(),
                      rep.getvar('YR'),
                      rep.getvar('MO'),
                      rep.getvar('DY'),
                      rep.getanom('SST'))
        g.take_average()
        temp_anom, temp_nobs = g.get_neighbour_anomalies([2, 2, 2], 180, 89, 0)

        self.assertEqual(len(temp_anom), 2)
        self.assertEqual(len(temp_nobs), 2)

        self.assertIn(4.5, temp_anom)
        self.assertIn(1.5, temp_anom)

        self.assertEqual(temp_nobs[0], 1)
        self.assertEqual(temp_nobs[1], 1)

    def test_add_one_maxes_limits(self):

        g = ex.Np_Super_Ob()
        g.add_rep(self.reps[0].lat(), self.reps[0].lon(), self.reps[0].getvar('YR'), self.reps[0].getvar('MO'),
                  self.reps[0].getvar('DY'), self.reps[0].getanom('SST'))
        g.take_average()
        g.get_new_buddy_limits(self.dummy_pentad_stdev, self.dummy_pentad_stdev, self.dummy_pentad_stdev)

        mn = g.get_buddy_mean(self.reps[0].getvar('LAT'),
                              self.reps[0].getvar('LON'),
                              self.reps[0].getvar('MO'),
                              self.reps[0].getvar('DY'))
        sd = g.get_buddy_stdev(self.reps[0].getvar('LAT'),
                               self.reps[0].getvar('LON'),
                               self.reps[0].getvar('MO'),
                               self.reps[0].getvar('DY'))
        self.assertAlmostEqual(sd, 500., delta=0.0001)
        self.assertEqual(mn, 0.0)

    def test_add_multiple(self):
        g = ex.Np_Super_Ob()
        for rep in self.reps:
            g.add_rep(rep.getvar('LAT'),
                      rep.getvar('LON'),
                      rep.getvar('YR'),
                      rep.getvar('MO'),
                      rep.getvar('DY'),
                      rep.getanom('SST'))
        g.take_average()
        g.get_new_buddy_limits(self.dummy_pentad_stdev, self.dummy_pentad_stdev, self.dummy_pentad_stdev)

        mn = g.get_buddy_mean(self.reps[0].getvar('LAT'),
                              self.reps[0].getvar('LON'),
                              self.reps[0].getvar('MO'),
                              self.reps[0].getvar('DY'))
        sd = g.get_buddy_stdev(self.reps[0].getvar('LAT'),
                               self.reps[0].getvar('LON'),
                               self.reps[0].getvar('MO'),
                               self.reps[0].getvar('DY'))
        self.assertAlmostEqual(sd, math.sqrt(10.), delta=0.0001)
        self.assertEqual(mn, 4.5)

    def test_creation(self):

        g = ex.Np_Super_Ob()


class TestVoyage(unittest.TestCase):

    def setUp(self):

        vals = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0},
                {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 1, 'LAT': 0.1, 'LON': 0.0, 'SST': 5.0},
                {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 2, 'LAT': 0.2, 'LON': 0.0, 'SST': 5.0},
                {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 3, 'LAT': 0.3, 'LON': 0.0, 'SST': 5.0},
                {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 4, 'LAT': 0.4, 'LON': 0.0, 'SST': 5.0},
                {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 5, 'LAT': 0.5, 'LON': 0.0, 'SST': 5.0},
                {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 6, 'LAT': 0.6, 'LON': 0.0, 'SST': 5.0}]

        badvals = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0},
                   {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 1, 'LAT': 0.1, 'LON': 0.0, 'SST': 5.0},
                   {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 2, 'LAT': 0.2, 'LON': 0.0, 'SST': 5.0},
                   {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 3, 'LAT': 0.3, 'LON': 10.0, 'SST': 5.0},
                   {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 4, 'LAT': 0.4, 'LON': 0.0, 'SST': 5.0},
                   {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 5, 'LAT': 0.5, 'LON': 0.0, 'SST': 5.0},
                   {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 6, 'LAT': 0.6, 'LON': 0.0, 'SST': 5.0}]

        self.reps = ex.Voyage()
        self.badreps = ex.Voyage()

        for v in vals:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps.add_report(rep)

        for v in badvals:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.badreps.add_report(rep)

    def test_spike_check_all_good(self):

        parameters = {"number_of_neighbours": 5,
                      "max_gradient_space": 0.5,
                      "max_gradient_time": 1.0,
                      "ship_delta_t": 2.0,
                      "buoy_delta_t": 1.0}

        self.reps.spike_check(parameters)
        for i in range(0, len(self.reps)):
            self.assertEqual(self.reps.get_qc(i, 'SST', 'spike'), 0)

    def test_spike_check_one_bad(self):

        parameters = {"number_of_neighbours": 5,
                      "max_gradient_space": 0.5,
                      "max_gradient_time": 1.0,
                      "ship_delta_t": 2.0,
                      "buoy_delta_t": 1.0}

        self.reps.setvar(3, 'SST', 16.0)
        self.reps.spike_check(parameters)
        for i in range(0, len(self.reps)):
            if i == 3:
                self.assertEqual(self.reps.get_qc(i, 'SST', 'spike'), 1)
            else:
                self.assertEqual(self.reps.get_qc(i, 'SST', 'spike'), 0)

    def test_iquam_track_check_all_good(self):

        parameters = {"number_of_neighbours": 5,
                      "buoy_speed_limit": 15.0,
                      "ship_speed_limit": 60.0,
                      "delta_d": 1.11,
                      "delta_t": 0.01}

        self.reps.iquam_track_check(parameters)

        for i in range(0, len(self.reps)):
            self.assertEqual(self.reps.get_qc(i, 'POS', 'iquam_track'), 0)

    def test_iquam_track_check_one_bad(self):

        parameters = {"number_of_neighbours": 5,
                      "buoy_speed_limit": 15.0,
                      "ship_speed_limit": 60.0,
                      "delta_d": 1.11,
                      "delta_t": 0.01}

        self.badreps.iquam_track_check(parameters)

        for i in range(0, len(self.badreps)):
            if i == 3:
                self.assertEqual(self.badreps.get_qc(i, 'POS', 'iquam_track'), 1)
            else:
                self.assertEqual(self.badreps.get_qc(i, 'POS', 'iquam_track'), 0)

    def test_track_check_all_good(self):

        parameters = {"max_direction_change": 60.0,
                      "max_speed_change": 10.00,
                      "max_absolute_speed": 40.00,
                      "max_midpoint_discrepancy": 150.0}

        self.reps.track_check(parameters)

        for i in range(0, len(self.reps)):
            self.assertEqual(self.reps.get_qc(i, 'POS', 'trk'), 0)

    def test_track_check_one_bad(self):

        parameters = {"max_direction_change": 60.0,
                      "max_speed_change": 10.00,
                      "max_absolute_speed": 40.00,
                      "max_midpoint_discrepancy": 150.0}

        self.badreps.track_check(parameters)

        for i in range(0, len(self.badreps)):
            if i == 3:
                self.assertEqual(self.badreps.get_qc(i, 'POS', 'trk'), 1)
            else:
                self.assertEqual(self.badreps.get_qc(i, 'POS', 'trk'), 0)

    def test_repeated_saturated_values(self):

        dumval = {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0}
        saturated = ex.Voyage()
        gaps = ex.Voyage()
        quick = ex.Voyage()
        for i in range(50):
            val = dumval.copy()
            val['HR'] = float(i)
            while val['HR'] >= 24:
                val['HR'] -= 24
                val['DY'] += 1
            val['DPT'] = 15.2
            val['AT'] = 15.2

            rec = IMMA()
            for key in val:
                rec.data[key] = val[key]
            rep = ex.MarineReportQC(rec)
            saturated.add_report(rep)

            if i % 19 == 0:
                rec.data['DPT'] = 13.0
            rep = ex.MarineReportQC(rec)
            gaps.add_report(rep)

            rec.data['HR'] = float(i) / 5.0
            rep = ex.MarineReportQC(rec)
            quick.add_report(rep)

        parameters = {'min_time_threshold': 48.0, 'shortest_run': 20}

        # make sure that 19 consecutive values passes
        gaps.find_saturated_runs(parameters)
        for rep in gaps.rep_feed():
            self.assertEqual(rep.get_qc('DPT', 'repsat'), 0)

        # make sure that 20 consecutive values in 24 hours passes
        quick.find_saturated_runs(parameters)
        for rep in quick.rep_feed():
            self.assertEqual(rep.get_qc('DPT', 'repsat'), 0)

        # make sure that 20 consecutive values in 48 hours fails
        saturated.find_saturated_runs(parameters)
        for rep in saturated.rep_feed():
            self.assertEqual(rep.get_qc('DPT', 'repsat'), 1)


class TestMarineReport(unittest.TestCase):

    def setUp(self):

        vals = [
            {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'AT': 10.0,
             'DPT': 11.0, 'SLP': 1023.0, 'UID': 'A642D2'},
            {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'AT': 10.0,
             'DPT': 10.0},
            {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'AT': 10.0,
             'DPT': 9.0},
            {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0},
            {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 10.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0},
            {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 10.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0},
            {'ID': 'BBBBBBBBB', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 10.0, 'LAT': 1.0, 'LON': 0.0, 'SST': 5.0}]

        self.reps = []

        for v in vals:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReport(rec)
            self.reps.append(rep)

        self.reps[0].set_qc('POS', 'pos', 0)
        self.reps[1].set_qc('POS', 'pos', 1)
        self.reps[2].set_qc('POS', 'pos', 0)
        self.reps[3].set_qc('POS', 'pos', 1)
        self.reps[4].set_qc('POS', 'pos', 0)
        self.reps[5].set_qc('POS', 'pos', 1)

    def tearDown(self):

        del self.reps

    def test_saturated(self):
        self.assertFalse(self.reps[0].saturated(), 'Observation is not saturated but flagged as saturated')
        self.assertTrue(self.reps[1].saturated(), 'Observation is saturated but not flagged as saturated')
        self.assertFalse(self.reps[2].saturated(), 'Observation is not saturated but flagged as saturated')

    def test_sort_same_ID_different_time(self):

        list_of_reps = [self.reps[2], self.reps[4]]
        list_of_reps.sort()

        self.assertEqual(list_of_reps[0].getvar('HR'), 0)

        list_of_reps = [self.reps[4], self.reps[2]]
        list_of_reps.sort()

        self.assertEqual(list_of_reps[0].getvar('HR'), 0)

    def test_sort_same_time_different_ID(self):

        list_of_reps = [self.reps[0], self.reps[2]]
        list_of_reps.sort()

        self.assertEqual(list_of_reps[0].getvar('ID'), 'AAAAAAAAA')

        list_of_reps = [self.reps[2], self.reps[0]]
        list_of_reps.sort()

        self.assertEqual(list_of_reps[0].getvar('ID'), 'AAAAAAAAA')

    def test_subtract(self):

        onedeg = 6371.0088 * 2. * np.pi / 360.

        speed, distance, course, timediff = self.reps[4] - self.reps[2]

        self.assertEqual(distance, 0)
        self.assertEqual(course, 0)
        self.assertAlmostEqual(timediff, 10, delta=0.000001)
        self.assertEqual(speed, 0)

        speed, distance, course, timediff = self.reps[6] - self.reps[2]

        self.assertAlmostEqual(distance, onedeg, delta=0.00001)  # 111.701072, delta=0.00001)
        self.assertIn(course, [0, 360])
        self.assertAlmostEqual(timediff, 10, delta=0.000001)
        self.assertAlmostEqual(speed, onedeg / 10., delta=0.000001)

    def test_climate_variables(self):

        self.reps[0].add_climate_variable('SST', 0.5)

        self.assertEqual(self.reps[0].getnorm('SST'), 0.5)
        self.assertEqual(self.reps[0].getanom('SST'), 4.5)

    def test_climate_variables_stdev(self):

        self.reps[0].add_climate_variable('SST', 0.5, 1.5)

        self.assertEqual(self.reps[0].getnorm('SST'), 0.5)
        self.assertEqual(self.reps[0].getnorm('SST', 'stdev'), 1.5)
        self.assertEqual(self.reps[0].getanom('SST'), 4.5)
        self.assertEqual(self.reps[0].get_normalised_anom('SST'), 3.0)

    def test_get_nonexistent_variable(self):
        self.assertEqual(self.reps[0].getvar('SQUIDINK'), None)

    def test_getvar_finds_variable_in_ext(self):
        self.reps[0].setext('ODDVARNAME', -99.99)
        self.assertEqual(self.reps[0].getvar('ODDVARNAME'), -99.99)

    def test_simple_set_and_get(self):
        self.reps[0].set_qc('POS', 'date', 0)
        self.assertEqual(self.reps[0].get_qc('POS', 'date'), 0)

    def test_set_invalid_value_causes_error(self):
        with self.assertRaises(AssertionError):
            self.reps[0].set_qc('POS', 'date', 11)

    def test_uninitialised_value_returns_9(self):
        self.assertEqual(self.reps[0].get_qc('POS', 'date'), 9)

    def test_print_variable_block(self):
        checkstring = 'A642D2,2003-12-01,67,"AAAAAAAAA",2003,12,1,0.0,0.0,0.0,10.0,\N,5.0,\N,11.0,\N,1023.0,\N\n'
        checkheader = 'UID,DATE,PENTAD,ID,YR,MO,DY,HR,LAT,LON,AT,AT_anom,SST,SST_anom,DPT,DPT_anom,SLP,SLP_anom\n'
        varnames = [['ID'], ['YR'], ['MO'], ['DY'], ['HR'], ['LAT'], ['LON'],
                    ['AT'], ['AT', 'anom'],
                    ['SST'], ['SST', 'anom'],
                    ['DPT'], ['DPT', 'anom'],
                    ['SLP'], ['SLP', 'anom']]
        outstring = self.reps[0].print_variable_block(varnames)
        self.assertEqual(outstring, checkstring)

        outstring = self.reps[0].print_variable_block(varnames, header=True)
        self.assertEqual(outstring, checkheader)

    def test_print_qc_block(self):
        checkstring = 'A642D2,9,9,9,9,9,9,9,9,9,9\n'
        checkheader = 'UID,bud,clim,nonorm,freez,noval,nbud,bbud,rep,spike,hardlimit\n'

        outstring = self.reps[0].print_qc_block('SST', ['bud', 'clim', 'nonorm',
                                                        'freez', 'noval', 'nbud',
                                                        'bbud', 'rep', 'spike',
                                                        'hardlimit'])
        self.assertEqual(outstring, checkstring)
        outstring = self.reps[0].print_qc_block('SST', ['bud', 'clim', 'nonorm',
                                                        'freez', 'noval', 'nbud',
                                                        'bbud', 'rep', 'spike',
                                                        'hardlimit'], header=True)
        self.assertEqual(outstring, checkheader)


class TestQCFilter(unittest.TestCase):

    def setUp(self):
        vals = {'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0, 'LAT': 0.0, 'LON': 0.0}
        rec = IMMA()
        for key in vals:
            rec.data[key] = vals[key]

        self.rep = ex.MarineReport(rec)
        self.rep.set_qc('POS', 'pos', 0)

        self.rep_fail = ex.MarineReport(rec)
        self.rep_fail.set_qc('POS', 'pos', 1)

        self.deck = ex.Deck()
        self.deck.append(self.rep)
        self.deck.append(self.rep_fail)

    def tearDown(self):
        del self.rep

    def test_creation(self):
        afilter = ex.QC_filter()
        self.assertEqual(afilter.test_report(self.rep), 0)

    def test_split(self):
        afilter = ex.QC_filter()
        afilter.add_qc_filter('POS', 'pos', 0)

        p, f = afilter.split_reports(self.deck)

        self.assertEqual(len(p), 1)
        self.assertEqual(len(f), 1)

    def test_fail(self):
        afilter = ex.QC_filter()
        afilter.add_qc_filter('POS', 'pos', 0)

        self.assertEqual(afilter.test_report(self.rep_fail), 1)

    def test_pass(self):
        afilter = ex.QC_filter()
        afilter.add_qc_filter('POS', 'pos', 0)

        self.assertEqual(afilter.test_report(self.rep), 0)


class TestBayesianBuddy(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
