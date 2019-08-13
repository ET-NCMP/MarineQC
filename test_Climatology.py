import unittest
import numpy as np
import Climatology as clim
import os
import subprocess


class Test_init(unittest.TestCase):

    def setUp(self):
        sst_climatology_file = '/home/h04/hadjj/HadSST2_pentad_climatology.nc'
        self.sst = clim.Climatology.from_filename(sst_climatology_file, 'sst')
        mat_climatology_file = '/home/h04/hadjj/HadNMAT2_pentad_climatology.nc'
        self.mat = clim.Climatology.from_filename(mat_climatology_file, 'nmat')
        
        sst_daily_file = '/project/hadobs2/hadsst3/HadSST2_daily_1x1_climatology.nc'
        self.sst_daily = clim.Climatology.from_filename(sst_daily_file, 'sst')

        self.dummy = clim.Climatology(np.full([1, 360, 720], 1.0))
    
    def test_tindex(self):
        
        self.assertEqual(self.dummy.get_tindex(1, 1), 0)
        self.assertEqual(self.dummy.get_tindex(12, 31), 0)

        self.assertEqual(self.sst_daily.get_tindex(1, 1), 0)
        self.assertEqual(self.sst_daily.get_tindex(12, 31), 364)

        self.assertEqual(self.sst.get_tindex(1, 1), 0)
        self.assertEqual(self.sst.get_tindex(12, 31), 72)

    def test_basics_work(self):
        self.assertEqual(self.sst.n, 73)
        self.assertEqual(self.sst.res, 1)
        self.assertEqual(self.sst.get_tindex(12, 31), 72)
        
        self.assertEqual(self.dummy.n, 1)
        self.assertEqual(self.dummy.res, 0.5)
        self.assertEqual(self.dummy.get_tindex(12, 31), 0)
        
    def test_get_val_freezin_at_poles(self):
        
        self.assertAlmostEqual(self.sst.get_value(89.9, 0.0, 12, 31), -1.8, delta=0.0001)
        self.assertAlmostEqual(self.sst.get_value(89.9, 0.0, 1, 1), -1.8, delta=0.0001)
        
    def test_daily(self):
        self.assertEqual(self.sst_daily.n, 365)
        self.assertEqual(self.sst_daily.res, 1)
        self.assertEqual(self.sst_daily.get_tindex(12, 31), 364)
        self.assertNotEqual(self.sst.get_value(89.9, 0.0, 1, 1), None)
        self.assertNotEqual(self.sst.get_value(89.9, 0.0, 12, 31), None)

    def test_known_values(self):
        
        val = self.dummy.get_value(12.0, 72.5, 3, 7)
        self.assertEqual(val, 1.0)

        val = self.sst.get_value(0.5, -179.5, 1, 1)
        self.assertAlmostEqual(val, 28.2904, delta=0.0001)
        val = self.sst.get_value(-0.5, -179.5, 1, 1)
        self.assertAlmostEqual(val, 28.4300, delta=0.0001)

        val = self.mat.get_value(0.5, -179.5, 1, 1)
        self.assertAlmostEqual(val, 27.4615, delta=0.0001)
        val = self.mat.get_value(-0.5, -179.5, 1, 1)
        self.assertAlmostEqual(val, 27.2693, delta=0.0001)


class TestBGVar(unittest.TestCase):

    def setUp(self):

        fname = '/scratch/hadjj/DJF_bckerr_smooth.nc'
        self.bgvar = clim.Climatology.from_filename(fname, 'bg_var')

    def test_southpole_is_odd_value(self):

        testbgvar = self.bgvar.get_value_mds_style(-89.9999, -180.0, 2, 1)
        self.assertAlmostEqual(testbgvar, 0.0383331, delta=0.0001)

    def test_northpole_is_another_odd_value(self):

        testbgvar = self.bgvar.get_value_mds_style(89.9999, -0.5, 2, 1)
        self.assertAlmostEqual(testbgvar, 0.733052, delta=0.0001)

    def test_near_equator(self):

        testbgvar = self.bgvar.get_value_mds_style(0.1, 0.1, 2, 1)
        self.assertAlmostEqual(testbgvar, 0.141453, delta=0.0001)

class TestOstia(unittest.TestCase):

    def setUp(self):

        year = 2009
        month = 1
        day = 1

        sy = str(year)
        sm = "%02d" % (month)
        sd = "%02d" % (day)
        ostia_dir = '/project/ofrd/ostia/'
        odir = ostia_dir + '/data/netcdf/' + sy + '/' + sm + '/'
        ostia_daily_file = sy + sm + sd + '-UKMO-L4HRfnd-GLOB-v01-fv02-OSTIA.nc'

        if (os.path.isfile('/scratch/hadjj/' + ostia_daily_file) and
                os.stat('/scratch/hadjj/' + ostia_daily_file).st_size != 0):
            self.ostia = clim.Climatology.from_filename('/scratch/hadjj/'+ostia_daily_file, 'analysed_sst')
        else:
            subprocess.call('bunzip2 -c '+odir+ostia_daily_file+'.bz2 > /scratch/hadjj/'+ostia_daily_file, shell=True)
            self.ostia = clim.Climatology.from_filename('/scratch/hadjj/'+ostia_daily_file, 'analysed_sst')

    def test_frozen_north_pole(self):

        testsst = self.ostia.get_value_ostia(89.999, -180.0)
        self.assertAlmostEqual(273.15 - 1.8, testsst, delta=0.001)

    def test_southpole_missing(self):

        testsst = self.ostia.get_value_ostia(-89.999, -180.0)
        self.assertIsNone(testsst)

    def test_zerozero(self):

        testsst = self.ostia.get_value_ostia(0.01, 0.01)
        self.assertAlmostEqual(301.120, testsst, delta=0.001)

    def test_various_points(self):

        testsst = self.ostia.get_value_ostia(5.001, -179.99)
        self.assertAlmostEqual(301.630, testsst, delta=0.001)


if __name__ == '__main__':
    unittest.main()
