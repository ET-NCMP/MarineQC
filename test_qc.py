import unittest
import math
import numpy.ma as ma
import numpy as np
import qc
from netCDF4 import Dataset
import json
import ConfigParser


class TestWindConsistency(unittest.TestCase):
    def test_calm(self):
        self.assertEqual(0, qc.wind_consistency(0.0, 361, 4.0))
        self.assertEqual(1, qc.wind_consistency(1.0, 361, 4.0))

    def test_variable(self):
        self.assertEqual(0, qc.wind_consistency(2.0, 362, 4.0))
        self.assertEqual(1, qc.wind_consistency(5.0, 362, 4.0))


class Testseason(unittest.TestCase):
    def test_all(self):
        self.assertEqual(qc.season(1), 'DJF')
        self.assertEqual(qc.season(2), 'DJF')
        self.assertEqual(qc.season(3), 'MAM')
        self.assertEqual(qc.season(4), 'MAM')
        self.assertEqual(qc.season(5), 'MAM')
        self.assertEqual(qc.season(6), 'JJA')
        self.assertEqual(qc.season(7), 'JJA')
        self.assertEqual(qc.season(8), 'JJA')
        self.assertEqual(qc.season(9), 'SON')
        self.assertEqual(qc.season(10), 'SON')
        self.assertEqual(qc.season(11), 'SON')
        self.assertEqual(qc.season(12), 'DJF')

    def test_odd(self):
        self.assertIsNone(qc.season(13))


class Testyesterday(unittest.TestCase):

    def test_odd(self):
        y, m, d = qc.yesterday(2003, 2, 30)
        self.assertIsNone(y, 3000)
        self.assertIsNone(m, 12)
        self.assertIsNone(d, 31)

    def test_easy(self):
        y, m, d = qc.yesterday(2003, 2, 3)
        self.assertEqual(y, 2003)
        self.assertEqual(m, 2)
        self.assertEqual(d, 2)

    def test_jan1(self):
        y, m, d = qc.yesterday(1999, 1, 1)
        self.assertEqual(y, 1998)
        self.assertEqual(m, 12)
        self.assertEqual(d, 31)

    def test_leap(self):
        y, m, d = qc.yesterday(2008, 3, 1)
        self.assertEqual(y, 2008)
        self.assertEqual(m, 2)
        self.assertEqual(d, 29)

    def test_nonleap(self):
        y, m, d = qc.yesterday(2007, 3, 1)
        self.assertEqual(y, 2007)
        self.assertEqual(m, 2)
        self.assertEqual(d, 28)


class TestPentadToMonth(unittest.TestCase):

    def test_all_ps(self):
        for p in range(1, 74):
            m, d = qc.pentad_to_month_day(p)
            self.assertEqual(p, qc.which_pentad(m, d))


class TestDayInYear(unittest.TestCase):

    def test_janfirst(self):
        self.assertEqual(qc.day_in_year(1, 1), 1)

    def test_dec31st(self):
        self.assertEqual(qc.day_in_year(12, 31), 365)

    def test_pesky_leapyear(self):
        self.assertEqual(qc.day_in_year(2, 29), qc.day_in_year(3, 1))

    def test_jan31(self):
        self.assertEqual(qc.day_in_year(1, 31), 31)

    def test_all_days(self):
        month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        count = 1
        for month in range(1, 13):
            for day in range(1, month_lengths[month - 1] + 1):
                self.assertEqual(qc.day_in_year(month, day), count)
                count += 1


class TestQCMethodsGetHiresSST(unittest.TestCase):

    def setUp(self):
        """
        The high resolution SST climatology is specified in the parameter file.
        """

        with open('Parameters.json', 'r') as f:
            parameters = json.load(f)

        sst_climatology_file = None
        for entry in parameters['hires_climatologies']:
            if entry[0] == 'SST' and entry[1] == 'mean':
                sst_climatology_file = entry[2]

        assert sst_climatology_file is not None, 'sst_climatology file not specified in parameter file'

        climatology = Dataset(sst_climatology_file)
        self.sst = climatology.variables['temperature'][:]

    #        self.dummyclim = np.full([365,1,720,1440], 1.13)

    def tearDown(self):
        del self.sst

    #        del self.dummyclim

    # @unittest.skip("demonstrating skipping because this takes for-ev-er")
    def test_sst_is_none_at_S_pole_at_all_longitudes(self):
        for xx in range(1440):
            val = qc.get_hires_sst(-89.9, -179.9 + 0.25 * xx, 1, 1, self.sst)
            self.assertEqual(val, None)

    # @unittest.skip("demonstrating skipping because this takes for-ev-er")
    def test_sst_at_N_pole(self):
        val = qc.get_hires_sst(89.89, -179.9, 1, 1, self.sst)
        self.assertAlmostEqual(val, -1.607731, delta=0.000001)
        val = qc.get_hires_sst(89.89, -179.9 + 0.25, 1, 1, self.sst)
        self.assertAlmostEqual(val, -1.607775, delta=0.000001)
        val = qc.get_hires_sst(89.89, 179.9, 1, 1, self.sst)
        self.assertAlmostEqual(val, -1.6075414419, delta=0.000001)


class TestQCMethodsGetSST(unittest.TestCase):

    def setUp(self):
        """
        The test climatologies used here are specified in the configuration file in the TestFiles section
        """
        config = ConfigParser.ConfigParser()
        config.read('configuration.txt')

        sst_climatology_file = config.get('TestFiles', 'sst_climatology_file')
        climatology = Dataset(sst_climatology_file)
        self.sst = climatology.variables['sst'][:]

        mat_climatology_file = config.get('TestFiles', 'mat_climatology_file')
        climatology = Dataset(mat_climatology_file)
        self.mat = climatology.variables['nmat'][:]

        stdev_climatology_file = config.get('TestFiles', 'stdev_climatology_file')
        climatology = Dataset(stdev_climatology_file)
        self.sdv = climatology.variables['sst'][:]

        self.dummyclim = np.full([73, 180, 360], 1.13)

        self.dummyclim_single_field = np.full([1, 180, 360], 3.13)

    def test_december(self):
        """
        other tests test Jan 1st, this test tests the other end of the calendar
        """
        val = qc.get_sst(89.9, 0.0, 12, 31, self.sdv)
        self.assertEqual(val, None)

    def test_single_field(self):
        """
        Test that single fields ignore the time info
        """
        val = qc.get_sst(89.9, 0.0, 12, 31, self.dummyclim_single_field)
        self.assertEqual(val, 3.13)

    def test_stdev_is_none_at_pole(self):
        val = qc.get_sst(89.9, 0.0, 1, 1, self.sdv)
        self.assertEqual(val, None)

    def test_stdev_known_value(self):
        val = qc.get_sst(-9.5, -179.5, 1, 1, self.sdv)
        self.assertAlmostEqual(val, 2.19, delta=0.0001)
        val = qc.get_sst(-10.5, -179.5, 12, 31, self.sdv)
        self.assertAlmostEqual(val, 0.44, delta=0.0001)

    def test_north_pole_is_freezing_in_january(self):
        val = qc.get_sst(89.9, 0.0, 1, 1, self.sst)
        self.assertAlmostEqual(val, -1.8, delta=0.0001)

        val = qc.get_sst(89.9, 0.0, 1, 1, self.mat)
        self.assertAlmostEqual(val, 0, delta=0.0001)

    def test_known_value(self):
        val = qc.get_sst(0.5, -179.5, 1, 1, self.sst)
        self.assertAlmostEqual(val, 28.2904, delta=0.0001)
        val = qc.get_sst(-0.5, -179.5, 1, 1, self.sst)
        self.assertAlmostEqual(val, 28.4300, delta=0.0001)

        val = qc.get_sst(0.5, -179.5, 1, 1, self.mat)
        self.assertAlmostEqual(val, 27.4615, delta=0.0001)
        val = qc.get_sst(-0.5, -179.5, 1, 1, self.mat)
        self.assertAlmostEqual(val, 27.2693, delta=0.0001)

    def test_south_pole_is_missing(self):
        val = qc.get_sst(-89.9, 0.0, 1, 1, self.sst)
        self.assertEqual(val, None)

    def test_works_with_dummy_arrays(self):
        val = qc.get_sst(0, 0, 1, 1, self.dummyclim)
        self.assertEqual(val, 1.13)


class TestQCMethodsJulDay(unittest.TestCase):

    def test_one_day_difference(self):
        j1 = qc.jul_day(2001, 1, 1)
        j2 = qc.jul_day(2001, 1, 2)
        self.assertEqual(1.0, j2 - j1)

    def test_one_year_difference(self):
        j1 = qc.jul_day(2001, 1, 1)
        j2 = qc.jul_day(2002, 1, 1)
        self.assertEqual(365.0, j2 - j1)

    def test_one_leapyear_difference(self):
        j1 = qc.jul_day(2004, 1, 1)
        j2 = qc.jul_day(2005, 1, 1)
        self.assertEqual(366.0, j2 - j1)


class TestQCMethodsTimeDifference(unittest.TestCase):

    def test_missing_hour(self):
        timdif1 = qc.time_difference(2000, 1, 7, None, 2000, 1, 7, 5)
        timdif2 = qc.time_difference(2000, 1, 7, 5, 2000, 1, 7, None)
        timdif3 = qc.time_difference(2000, 1, 7, None, 2000, 1, 7, None)

        self.assertEqual(None, timdif1)
        self.assertEqual(None, timdif2)
        self.assertEqual(None, timdif3)

    def test_time_difference_one_hour(self):
        timdif = qc.time_difference(2000, 1, 7, 5, 2000, 1, 7, 6)
        self.assertAlmostEqual(1.0, timdif, delta=0.00001)

    def test_time_difference_same_time(self):
        timdif = qc.time_difference(2000, 1, 7, 5, 2000, 1, 7, 5)
        self.assertEqual(0.0, timdif)

    def test_time_difference_one_day(self):
        timdif = qc.time_difference(2000, 1, 7, 5, 2000, 1, 8, 5)
        self.assertAlmostEqual(24.0, timdif, delta=0.00001)

    def test_time_difference_minus_one_day(self):
        timdif = qc.time_difference(2000, 1, 8, 5, 2000, 1, 7, 5)
        self.assertAlmostEqual(-24.0, timdif, delta=0.00001)

    def test_time_difference_one_year(self):
        timdif = qc.time_difference(2001, 1, 7, 5, 2002, 1, 7, 5)
        self.assertEqual(8760.0, timdif)

    def test_time_difference_two_years(self):
        timdif = qc.time_difference(2001, 1, 7, 5, 2003, 1, 7, 5)
        self.assertEqual(17520.0, timdif)

    def test_time_difference_100_years(self):
        timdif = qc.time_difference(1800, 1, 1, 0, 1900, 1, 1, 0)
        self.assertEqual(876576.0, timdif)


class TestQCMethodsWhichPentad(unittest.TestCase):

    def test_second_and_fifth_pentad(self):
        self.assertEqual(2, qc.which_pentad(1, 6))
        self.assertEqual(5, qc.which_pentad(1, 21))

    def test_second_to_last_pentad(self):
        self.assertEqual(72, qc.which_pentad(12, 26))

    def test_pentad_of_jan_1st(self):
        self.assertEqual(1, qc.which_pentad(1, 1))

    def test_pentad_of_dec_31st(self):
        self.assertEqual(73, qc.which_pentad(12, 31))

    def test_pentad_of_feb_29th(self):
        self.assertEqual(12, qc.which_pentad(2, 29))


class TestQCMethodsValueCheck(unittest.TestCase):

    def test_value_missing(self):
        self.assertEqual(1, qc.value_check(None))

    def test_value_present(self):
        self.assertEqual(0, qc.value_check(5.7))


class TestQCMethodsSSTFreezeCheck(unittest.TestCase):

    def test_exactly_freezing(self):
        self.assertEqual(0, qc.sst_freeze_check(-1.80))
        self.assertEqual(0, qc.sst_freeze_check(-1.80, 0.0))
        self.assertEqual(0, qc.sst_freeze_check(-1.80, 0.0, -1.80))

    def test_above_freezing(self):
        self.assertEqual(0, qc.sst_freeze_check(3.80))
        self.assertEqual(0, qc.sst_freeze_check(3.80, 0.0))
        self.assertEqual(0, qc.sst_freeze_check(3.80, 0.0, -1.80))

    def test_below_freezing(self):
        self.assertEqual(1, qc.sst_freeze_check(-3.80))
        self.assertEqual(1, qc.sst_freeze_check(-3.80, 0.0))
        self.assertEqual(1, qc.sst_freeze_check(-3.80, 0.0, -1.80))

    def test_nonstandard_freezing_point(self):
        self.assertEqual(0, qc.sst_freeze_check(-1.80, 0.0, -1.90))
        self.assertEqual(1, qc.sst_freeze_check(-2.00, 0.0, -1.90))


class TestQCMethodsHardLimit(unittest.TestCase):

    def test_safe(self):
        self.assertEqual(0, qc.hard_limit(0.0, [-1.0, 1.0]))

    def test_borderline(self):
        limits = [-1.2324230, 1.7484]
        self.assertEqual(0, qc.hard_limit(limits[0], limits))
        self.assertEqual(0, qc.hard_limit(limits[1], limits))

    def test_a_failure(self):
        limits = [-1.2324230, 1.7484]
        self.assertEqual(1, qc.hard_limit(limits[0] - 23.2, limits))
        self.assertEqual(1, qc.hard_limit(limits[1] + 9.5, limits))


class TestQCMethodsClimatologyCheck(unittest.TestCase):

    def test_borderline(self):
        self.assertEqual(0, qc.climatology_check(0.0, 8.0))

    def test_negative_borderlines(self):
        self.assertEqual(0, qc.climatology_check(0.0, -8.0))

    def test_should_pass(self):
        self.assertEqual(0, qc.climatology_check(17.0, 23.2))

    def test_should_fail(self):
        self.assertEqual(1, qc.climatology_check(17.0, 17.0 + 8.1))

    def test_should_fail_negative(self):
        self.assertEqual(1, qc.climatology_check(17.0, 17.0 - 8.1))

    def test_should_pass_with_limit(self):
        self.assertEqual(0, qc.climatology_check(17.0, 17.3, 1.0))

    def test_should_fail_with_limit(self):
        self.assertEqual(1, qc.climatology_check(17.0, 17.3, 0.2))

    def test_missing_climatology(self):
        self.assertEqual(1, qc.climatology_check(20.0, None))

    def test_missing_value(self):
        self.assertEqual(1, qc.climatology_check(None, 7.3))

    def test_missing_limit(self):
        self.assertEqual(1, qc.climatology_check(0.0, 3.0, None))


class TestQCMethodsPositionCheck(unittest.TestCase):

    def test_good_position(self):
        self.assertEqual(0, qc.position_check(0.0, 0.0))

    def test_bad_latitudes(self):
        self.assertEqual(1, qc.position_check(91.0, 0.0))
        self.assertEqual(1, qc.position_check(-91.0, 0.0))

    def test_bad_longitudes(self):
        self.assertEqual(1, qc.position_check(0.0, -180.1))
        self.assertEqual(1, qc.position_check(0.0, 360.1))


class TestQCMethodsDayInYear(unittest.TestCase):

    def test_jan1(self):
        self.assertEqual(1, qc.dayinyear(1999, 1, 1))

    def test_dec31(self):
        self.assertEqual(365, qc.dayinyear(1999, 12, 31))

    def test_dec31_leapyear(self):
        self.assertEqual(366, qc.dayinyear(1984, 12, 31))


class TestQCMethodsWinsorisedMean(unittest.TestCase):

    def test_all_zeroes(self):
        inarr = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(0.0, qc.winsorised_mean(inarr))

    def test_all_fours(self):
        inarr = [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0]
        self.assertEqual(4.0, qc.winsorised_mean(inarr))

    def test_three_fours(self):
        inarr = [4.0, 4.0, 4.0]
        self.assertEqual(4.0, qc.winsorised_mean(inarr))

    def test_ascending(self):
        inarr = [3., 4., 5.]
        self.assertEqual(4.0, qc.winsorised_mean(inarr))

    def test_longer_ascending_run(self):
        inarr = [1., 2., 3., 4., 5., 6., 7.]
        self.assertEqual(4.0, qc.winsorised_mean(inarr))

    def test_longer_ascending_run_large_outlier(self):
        inarr = [1., 2., 3., 4., 5., 6., 700.]
        self.assertEqual(4.0, qc.winsorised_mean(inarr))

    def test_longer_ascending_run_two_outliers(self):
        inarr = [1., 2., 3., 4., 5., 6., 7., 8., 9., 10., 11., 12., 13., 14., 99., 1000.]
        self.assertEqual(8.5, qc.winsorised_mean(inarr))


class TestQCMethodsTrimmedMean(unittest.TestCase):

    def test_all_zeroes(self):
        inarr = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        trim = 10
        self.assertEqual(0.0, qc.trimmed_mean(inarr, trim))

    def test_all_zeroes_one_outlier_trimmed(self):
        inarr = [0, 0, 0, 0, 0, 0, 0, 0, 0, 10.0]
        trim = 4
        self.assertEqual(0.0, qc.trimmed_mean(inarr, trim))

    def test_all_zeroes_one_outlier_not_trimmed(self):
        inarr = [0, 0, 0, 0, 0, 0, 0, 0, 0, 10.0]
        trim = 50
        self.assertEqual(1.0, qc.trimmed_mean(inarr, trim))

    def test_trim_zero(self):
        inarr = [1.3, 0.7, 4.0]
        trim = 0
        self.assertEqual(2.0, qc.trimmed_mean(inarr, trim))


class TestQCMethodsLatToYindex(unittest.TestCase):

    def test_latitude_too_high(self):
        self.assertEqual(0, qc.lat_to_yindex(99.2))

    def test_borderline37(self):
        self.assertEqual(53, qc.lat_to_yindex(37.00))
        self.assertEqual(11, qc.lat_to_yindex(35.00, 5))

    def test_latitude_too_low(self):
        self.assertEqual(179, qc.lat_to_yindex(-199.3))

    def test_borderline(self):
        for i in range(0, 180):
            self.assertEqual(i, qc.lat_to_yindex(90 - i))

    def test_gridcentres(self):
        for i in range(0, 180):
            self.assertEqual(i, qc.lat_to_yindex(90 - i - 0.5))

    def test_some_points(self):
        self.assertEqual(9, qc.lat_to_yindex(87.52, 0.25))
        self.assertEqual(18, qc.lat_to_yindex(-2.5, 5))

    def test_latitude_varying_res(self):
        self.assertEqual(0, qc.lat_to_yindex(89.9, 0.25))
        self.assertEqual(0, qc.lat_to_yindex(89.9, 0.5))
        self.assertEqual(0, qc.lat_to_yindex(89.9, 1.0))
        self.assertEqual(0, qc.lat_to_yindex(89.9, 2.0))
        self.assertEqual(0, qc.lat_to_yindex(89.9, 5.0))

        self.assertEqual(719, qc.lat_to_yindex(-89.9, 0.25))
        self.assertEqual(359, qc.lat_to_yindex(-89.9, 0.5))
        self.assertEqual(179, qc.lat_to_yindex(-89.9, 1.0))
        self.assertEqual(89, qc.lat_to_yindex(-89.9, 2.0))
        self.assertEqual(35, qc.lat_to_yindex(-89.9, 5.0))


class TestQCMethodsLonToXindex(unittest.TestCase):

    def test_borderline(self):
        self.assertEqual(0, qc.lon_to_xindex(-180))
        self.assertEqual(0, qc.lon_to_xindex(180))

    def test_high_negative_long(self):
        self.assertEqual(359, qc.lon_to_xindex(-180.5))
        self.assertEqual(358, qc.lon_to_xindex(-181.5))

    def test_non180_borderline(self):
        self.assertEqual(106, qc.lon_to_xindex(-74.0))

    def test_gridcentres(self):
        self.assertEqual(0, qc.lon_to_xindex(-179.5))
        self.assertEqual(0, qc.lon_to_xindex(180.5))

    def test_highlong(self):
        self.assertEqual(179, qc.lon_to_xindex(359.5))

    def test_highlong_different_res(self):
        self.assertEqual(71, qc.lon_to_xindex(179.5, 5))
        self.assertEqual(1439, qc.lon_to_xindex(179.9, 0.25))

    def test_oneshift_along_at_hires(self):
        self.assertEqual(1, qc.lon_to_xindex(-179.9 + 0.25, 0.25))

    def test_lons_ge_180(self):
        """test to make sure wrapping works"""
        self.assertEqual(180, qc.lon_to_xindex(360.0))
        self.assertEqual(5, qc.lon_to_xindex(185.1))
        for i in range(0, 520):
            self.assertEqual(math.fmod(i, 360), qc.lon_to_xindex(-179.5 + float(i)))


class TestQCMethodsBlacklist(unittest.TestCase):

    def test_fail_zero_lat_zero_lon_fail(self):
        result = qc.blacklist('', 980, 1850, 1, 0, 0)
        self.assertEqual(result, 1)

    def test_fail_SEAS(self):
        result = qc.blacklist('', 874, 1850, 1, 0, 1)
        self.assertEqual(result, 1)

    def test_fail_CMAN(self):
        result = qc.blacklist('', 732, 1850, 1, 0, 1, 13)
        self.assertEqual(result, 1)

    def test_obvious_pass(self):
        result = qc.blacklist('', 732, 1850, 1, 0, 1)
        self.assertEqual(result, 0)

    def test_obvious_fails(self):
        result = qc.blacklist('', 732, 1958, 1, 45, -172)
        self.assertEqual(result, 1)
        result = qc.blacklist('', 732, 1974, 1, -47, -60)
        self.assertEqual(result, 1)

    def test_obvious_fails_shifted_long(self):
        result = qc.blacklist('', 732, 1958, 1, 45, -172 + 360)
        self.assertEqual(result, 1)
        result = qc.blacklist('', 732, 1974, 1, -47, -60 + 360)
        self.assertEqual(result, 1)

    def test_right_area_wrong_callsign_passes(self):
        result = qc.blacklist('', 731, 1958, 1, 45, -172)
        self.assertEqual(result, 0)
        result = qc.blacklist('', 731, 1974, 1, -47, -60)
        self.assertEqual(result, 0)

    def test_right_area_wrong_year_passes(self):
        result = qc.blacklist('', 732, 1957, 1, 45, -172)
        self.assertEqual(result, 0)
        result = qc.blacklist('', 732, 1975, 1, -47, -60)
        self.assertEqual(result, 0)


class TestQCMethodsSunangle(unittest.TestCase):
    # sunangle(year,day,hour,min,sec,zone,dasvtm,lat,lon)
    def test_looking_through_window(self):
        """test devised by looking through the window at the sun resting on the horizon at 07:45 15 October 2015"""
        day = qc.dayinyear(2015, 10, 15)
        a, e, rta, hra, sid, dec = qc.sunangle(2015, day, 7, 40, 0, 0, 1, 50.7365, -3.5344)
        self.assertAlmostEqual(0, e, delta=5.00)

    def test_sunrise_summer_solstice_2016_exeter(self):
        day = qc.dayinyear(2016, 6, 20)
        a, e, rta, hra, sid, dec = qc.sunangle(2016, day, 5, 1, 0, 0, 1, 50.7365, -3.5344)
        self.assertAlmostEqual(0, e, delta=1.5)

    def test_sunrise_in_Lima_March_3_1996(self):
        day = qc.dayinyear(1996, 3, 3)
        a, e, rta, hra, sid, dec = qc.sunangle(1996, day, 6, 11, 0, 5, 0, -12.0433, -77.0283)
        self.assertAlmostEqual(0, e, delta=1.5)

    def test_sunset_in_Zanzibar_City_Jan_31_1995(self):
        day = qc.dayinyear(1995, 1, 31)
        a, e, rta, hra, sid, dec = qc.sunangle(1995, day, 18, 17, 0, 21.38, 0, -6.1658, 39.1992)
        self.assertAlmostEqual(0, e, delta=1.5)


class TestQCMethodsDayTest(unittest.TestCase):
    # result = day_test(year,month,day,hour,lat,lon)
    def test_looking_through_window_plus_an_hour_sunup(self):
        result = qc.day_test(2015, 10, 15, 7.8000, 50.7365, -3.5344)
        self.assertEqual(1, result)

    def test_looking_through_window_at_elevenish(self):
        result = qc.day_test(2018, 9, 25, 11.5000, 50.7365, -3.5344)
        self.assertEqual(1, result)

    def test_looking_through_window_plus_an_hour_sunstilldown(self):
        result = qc.day_test(2015, 10, 15, 7.5000, 50.7365, -3.5344)
        self.assertEqual(0, result)


class TestQCMethodsYindexToLat(unittest.TestCase):

    def test_0_is_89point5(self):
        self.assertEqual(qc.yindex_to_lat(0, 1), 89.5)

    def test_179_is_minus89point5(self):
        self.assertEqual(qc.yindex_to_lat(179, 1), -89.5)

    def test_35_is_minus87point5_atresof5(self):
        self.assertEqual(qc.yindex_to_lat(35, 5), -87.5)

    def test_0_is_87point5_atresof5(self):
        self.assertEqual(qc.yindex_to_lat(0, 5), 87.5)


class TestQCMethodsXindexToLon(unittest.TestCase):

    def test_0(self):
        self.assertEqual(qc.xindex_to_lon(0, 1), -179.5)

    def test_359(self):
        self.assertEqual(qc.xindex_to_lon(359, 1), 179.5)

    def test_179(self):
        self.assertEqual(qc.xindex_to_lon(179, 1), -0.5)

    def test_180(self):
        self.assertEqual(qc.xindex_to_lon(180, 1), 0.5)


class TestQCMethodMissingMean(unittest.TestCase):

    def test_all_missing(self):
        self.assertEqual(qc.missing_mean([None, None]), None)

    def test_one_non_missing(self):
        self.assertEqual(qc.missing_mean([None, 7.3]), 7.3)
        self.assertEqual(qc.missing_mean([994.2, None]), 994.2)

    def test_all_non_missing(self):
        self.assertEqual(qc.missing_mean([6.0, 1.0]), 3.5)


class TestQCMethodFillMissingValues(unittest.TestCase):

    def test_all_missing_in_square(self):
        q11, q12, q21, q22 = qc.fill_missing_vals(None, None, None, None)
        self.assertEqual(q11, None)
        self.assertEqual(q12, None)
        self.assertEqual(q21, None)
        self.assertEqual(q22, None)

    def test_one_missing_corner(self):
        q11, q12, q21, q22 = qc.fill_missing_vals(1., 2., 3., None)
        self.assertEqual(q11, 1.)
        self.assertEqual(q12, 2.)
        self.assertEqual(q21, 3.)
        self.assertEqual(q22, 2.5)

    def test_two_missing_corners(self):
        q11, q12, q21, q22 = qc.fill_missing_vals(None, 2., 3., None)
        self.assertEqual(q11, 2.5)
        self.assertEqual(q12, 2.)
        self.assertEqual(q21, 3.)
        self.assertEqual(q22, 2.5)

    def test_three_missing_corners(self):
        q11, q12, q21, q22 = qc.fill_missing_vals(None, None, 3., None)
        self.assertEqual(q11, 3.)
        self.assertEqual(q12, 3.)
        self.assertEqual(q21, 3.)
        self.assertEqual(q22, 3.)


class TestQCMethodsGetFourSurroundingPoints(unittest.TestCase):

    # get_four_surrounding_points(lat, lon, max90=1)

    def test_high_lon(self):
        x1, x2, y1, y2 = qc.get_four_surrounding_points(0.4, 322.2 - 360, 1)
        self.assertEqual(x1, -38.5)
        self.assertEqual(x2, -37.5)
        self.assertEqual(y1, -0.5)
        self.assertEqual(y2, 0.5)

    def test_high_n_lat(self):
        x1, x2, y1, y2 = qc.get_four_surrounding_points(89.9, 0.1, 1)
        self.assertEqual(x1, -0.5)
        self.assertEqual(x2, 0.5)
        self.assertEqual(y1, 89.5)
        self.assertEqual(y2, 89.5)

        x1, x2, y1, y2 = qc.get_four_surrounding_points(89.9, 0.1, 0)
        self.assertEqual(x1, -0.5)
        self.assertEqual(x2, 0.5)
        self.assertEqual(y1, 89.5)
        self.assertEqual(y2, 90.5)

    def test_off_zero(self):
        x1, x2, y1, y2 = qc.get_four_surrounding_points(0.1, 0.1)
        self.assertEqual(x1, -0.5)
        self.assertEqual(x2, 0.5)
        self.assertEqual(y1, -0.5)
        self.assertEqual(y2, 0.5)

    def test_zero_zero(self):
        x1, x2, y1, y2 = qc.get_four_surrounding_points(0.0, 0.0)
        self.assertEqual(x1, -0.5)
        self.assertEqual(x2, 0.5)
        self.assertEqual(y1, -0.5)
        self.assertEqual(y2, 0.5)

    def test_dateline_crossover(self):
        x1, x2, y1, y2 = qc.get_four_surrounding_points(0.0, 179.9)
        self.assertEqual(x1, 179.5)
        self.assertEqual(x2, 180.5)
        self.assertEqual(y1, -0.5)
        self.assertEqual(y2, 0.5)

    def test_negative_dateline_crossover(self):
        x1, x2, y1, y2 = qc.get_four_surrounding_points(0.0, -179.9)
        self.assertEqual(x1, -180.5)
        self.assertEqual(x2, -179.5)
        self.assertEqual(y1, -0.5)
        self.assertEqual(y2, 0.5)


class TestQCMethodsBilinear(unittest.TestCase):
    # bilinear_interp(x1,x2,y1,y2,x,y,Q11,Q12,Q21,Q22)

    def test_zero_when_all_zero(self):
        result = qc.bilinear_interp(0., 1., 0., 1., 0., 0., 0., 0., 0., 0.)
        self.assertEqual(result, 0)

    def test_gradient_across_square(self):
        result = qc.bilinear_interp(0., 1., 0., 1., 0.5, 0.5, 0., 1., 1., 2.)
        self.assertEqual(result, 1)
        result = qc.bilinear_interp(0., 1., 0., 1., 0.0, 0.0, 0., 1., 1., 2.)
        self.assertEqual(result, 0)
        result = qc.bilinear_interp(0., 1., 0., 1., 1.0, 1.0, 0., 1., 1., 2.)
        self.assertEqual(result, 2)
        result = qc.bilinear_interp(0., 1., 0., 1., 0.0, 1.0, 0., 1., 1., 2.)
        self.assertEqual(result, 1)
        result = qc.bilinear_interp(0., 1., 0., 1., 1.0, 0.0, 0., 1., 1., 2.)
        self.assertEqual(result, 1)

    def test_zero_at_point_set_to_zero(self):
        result = qc.bilinear_interp(0., 1., 0., 1., 0., 0., 0., 1., 1., 1.)
        self.assertEqual(result, 0)

    def test_one_at_points_set_to_one(self):
        result = qc.bilinear_interp(0., 1., 0., 1., 0., 1., 0., 1., 1., 1.)
        self.assertEqual(result, 1)

        result = qc.bilinear_interp(0., 1., 0., 1., 1., 1., 0., 1., 1., 1.)
        self.assertEqual(result, 1)

        result = qc.bilinear_interp(0., 1., 0., 1., 1., 0., 0., 1., 1., 1.)
        self.assertEqual(result, 1)

    def test_half_at_point_halfway_between_zero_and_one(self):
        result = qc.bilinear_interp(0., 1., 0., 1., 0.5, 0., 0., 0., 1., 1.)
        self.assertEqual(result, 0.5)
        result = qc.bilinear_interp(0., 1., 0., 1., 0.5, 0.5, 0., 0., 1., 1.)
        self.assertEqual(result, 0.5)


class TestQCMethodsMdsLatAndLon(unittest.TestCase):

    def test_lats_with_res(self):
        self.assertEqual(qc.mds_lat_to_yindex(90.0, 5.0), 0)
        self.assertEqual(qc.mds_lat_to_yindex(88.0, 5.0), 0)
        self.assertEqual(qc.mds_lat_to_yindex(85.0, 5.0), 0)

        self.assertEqual(qc.mds_lat_to_yindex(-85.0, 5.0), 35)
        self.assertEqual(qc.mds_lat_to_yindex(-88.4, 5.0), 35)
        self.assertEqual(qc.mds_lat_to_yindex(-90.0, 5.0), 35)

        self.assertEqual(qc.mds_lat_to_yindex(0.0, 5.0), 18)

    def test_lons_with_res(self):
        self.assertEqual(qc.mds_lon_to_xindex(-180.0, 5.0), 0)
        self.assertEqual(qc.mds_lon_to_xindex(-178.0, 5.0), 0)
        self.assertEqual(qc.mds_lon_to_xindex(-175.0, 5.0), 0)

        self.assertEqual(qc.mds_lon_to_xindex(175.0, 5.0), 71)
        self.assertEqual(qc.mds_lon_to_xindex(178.4, 5.0), 71)
        self.assertEqual(qc.mds_lon_to_xindex(180.0, 5.0), 71)

        self.assertEqual(qc.mds_lon_to_xindex(0.0, 5.0), 35)

    def test_lats(self):
        self.assertEqual(qc.mds_lat_to_yindex(90.0), 0)
        self.assertEqual(qc.mds_lat_to_yindex(89.0), 0)
        self.assertEqual(qc.mds_lat_to_yindex(88.0), 1)
        self.assertEqual(qc.mds_lat_to_yindex(87.0), 2)

        self.assertEqual(qc.mds_lat_to_yindex(88.7), 1)

        self.assertEqual(qc.mds_lat_to_yindex(-90.0), 179)
        self.assertEqual(qc.mds_lat_to_yindex(-89.0), 179)
        self.assertEqual(qc.mds_lat_to_yindex(-88.0), 178)
        self.assertEqual(qc.mds_lat_to_yindex(-87.0), 177)

        self.assertEqual(qc.mds_lat_to_yindex(-88.7), 178)

        self.assertEqual(qc.mds_lat_to_yindex(0.0), 90)
        self.assertEqual(qc.mds_lat_to_yindex(0.5), 89)
        self.assertEqual(qc.mds_lat_to_yindex(1.0), 88)
        self.assertEqual(qc.mds_lat_to_yindex(-0.5), 90)
        self.assertEqual(qc.mds_lat_to_yindex(-1.0), 91)

    def test_lons(self):
        self.assertEqual(qc.mds_lon_to_xindex(-180.0), 0)
        self.assertEqual(qc.mds_lon_to_xindex(-179.0), 0)
        self.assertEqual(qc.mds_lon_to_xindex(-178.0), 1)

        self.assertEqual(qc.mds_lon_to_xindex(180.0), 359)
        self.assertEqual(qc.mds_lon_to_xindex(179.0), 359)
        self.assertEqual(qc.mds_lon_to_xindex(178.0), 358)

        self.assertEqual(qc.mds_lon_to_xindex(-1.0), 178)
        self.assertEqual(qc.mds_lon_to_xindex(0.0), 179)
        self.assertEqual(qc.mds_lon_to_xindex(1.0), 181)


class TestQCMethodsPgross(unittest.TestCase):
    # p_gross(p0, Q, R_hi, R_lo, x, mu, sigma)

    def test_prior_probability_is_one(self):
        p = qc.p_gross(1.0, 0.1, 8.0, -8.0, 0.0, 0.0, 1.0)
        self.assertEqual(p, 1.0)

    def test_prior_probability_is_zero(self):
        p = qc.p_gross(0.0, 0.1, 8.0, -8.0, 0.0, 0.0, 1.0)
        self.assertEqual(p, 0.0)


class TestQCMethodsPDataGivenGross(unittest.TestCase):
    #   p_data_given_gross(Q, R_hi, R_lo)
    def test_simple(self):
        p = qc.p_data_given_gross(1.0, 10.0, 0.0)
        self.assertEqual(p, 1.0 / 11.)


if __name__ == '__main__':
    unittest.main()
