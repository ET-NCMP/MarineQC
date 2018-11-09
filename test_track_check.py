import unittest
import qc
import math
import Extended_IMMA as ex
from IMMA1 import IMMA 
import numpy as np
import spherical_geometry as sph
import track_check as tc
from netCDF4 import Dataset

class TestTrackQCMethods_increment_position(unittest.TestCase):
#increment_position(alat1,alat2,avs,ads,timdif)
    def test_ship_heading_north_at_60knots_goes1degree_in_1hour(self):
        '''
        A ship travelling north at 60 knots will go 1 degree in 1 hours
        '''
        km_to_nm = 0.539957
        for lat in range(-90,90):
            alat1 = lat
            alon1 = lat
            avs = 60.0/km_to_nm
            ads = 0.0
            timdif = 2.0
            alat2,alon2 = tc.increment_position(alat1,alon1,avs,ads,timdif)
            self.assertAlmostEqual(alon2,0,delta=0.001)
            self.assertAlmostEqual(alat2,1,delta=0.001)

    def test_ship_heading_east_at_60knots_goes1degree_in_1hour(self):
        '''
        A ship travelling east at 60 knots will go 1 degree in 1 hour
        '''
        km_to_nm = 0.539957
        alat1 = 0.0
        alat2 = 0.0
        avs = 60.0/km_to_nm
        ads = 90.0
        timdif = 2.0
        aud1,avd1 = tc.increment_position(alat1,alat2,avs,ads,timdif)
        self.assertAlmostEqual(avd1,1,delta=0.001)
        self.assertAlmostEqual(aud1,0,delta=0.001)

    def test_ship_heading_east_at_60knots_at_latitude60_goes2degrees_in_1hour(self):
        '''
        A ship travelling east at 60 knots will go 2 degrees in 1 hour at 60N
        '''
        km_to_nm = 0.539957
        alat = 60.0
        alon = 0.0
        avs = 60.0/km_to_nm
        ads = 90.0
        timdif = 2.0
        dlat,dlon = tc.increment_position(alat,alon,avs,ads,timdif)
        distance = sph.sphere_distance(alat,alon,alat+dlat,alon+dlon) * km_to_nm
        self.assertAlmostEqual(distance, 60, delta=0.0001)

    def test_ship_goes_southwest(self):
        km_to_nm = 0.539957
        alat1 = 0.0
        alat2 = 0.0
        avs = 60.0/km_to_nm
        ads = 225.0
        timdif = 2.0
        aud1,avd1 = tc.increment_position(alat1,alat2,avs,ads,timdif)
        self.assertAlmostEqual(avd1,-1./np.sqrt(2),delta=0.001)
        self.assertAlmostEqual(aud1,-1./np.sqrt(2),delta=0.001)

class TestTrackQCMethods_modesp(unittest.TestCase):
    
    def test_noinput(self):
        m = tc.modesp([])
        self.assertEqual(None, m)
        
    def test_one_input(self):
        m = tc.modesp([17.0])
        self.assertEqual(None, m)

    def test_single_speed_input_over8point5(self):
        km_to_nm = 0.539957
        speeds = [20.0/km_to_nm,20.0/km_to_nm,20.0/km_to_nm,20.0/km_to_nm,20.0/km_to_nm,20.0/km_to_nm]
        m = tc.modesp(speeds)
        self.assertEqual(19.5/km_to_nm, m)

    def test_single_speed_input_under8point5(self):
        km_to_nm = 0.539957
        speeds = [2.0/km_to_nm,2.0/km_to_nm,2.0/km_to_nm,2.0/km_to_nm,2.0/km_to_nm,2.0/km_to_nm]
        m = tc.modesp(speeds)
        self.assertEqual(8.5/km_to_nm, m)

    def test_single_speed_input_overmaximum(self):
        km_to_nm = 0.539957
        speeds = [200.0/km_to_nm,200.0/km_to_nm,200.0/km_to_nm,200.0/km_to_nm,200.0/km_to_nm,200.0/km_to_nm]
        m = tc.modesp(speeds)
        self.assertEqual(34.5/km_to_nm,m)

    def test_one_of_each_speed_input_min_under8point5(self):
        km_to_nm = 0.539957
        speeds = []
        for i in range(1,20):
            speeds.append(i/km_to_nm)      
        m = tc.modesp(speeds)
        self.assertEqual(8.5/km_to_nm,m)

class TestTrackQCMethods_distr1(unittest.TestCase):
    
    #rec = IMMA()
     #       v = {'ID':'SHIP1   ', 'YR':2001, 'MO':1, 'DY':1, 'HR':hour, 'LAT': hour*speed1/60., 'LON':0.0, 'DS':8, 'VS':4 }
      #      for key in v: rec.data[key] = v[key]
       #     self.trip1.add_report(ex.MarineReport(rec))
#shipid, lat, lon, sst, mat, year, month, day, hour, icoads_ds, icoads_vs, uid
    def setUp(self):
        self.km_to_nm = 0.539957
        self.trip1 = ex.Voyage()
        self.speed1 = 18./self.km_to_nm
        for hour in range(0,24):
            rec = IMMA()
            v = {'ID':'SHIP1    ', 'YR':2001, 'MO':1, 'DY':1, 'HR':hour, 
                 'LAT':hour*self.speed1*360./(2*np.pi*6371.0088), 'LON':0.0, 'DS':8, 'VS':4}
            for key in v: rec.data[key] = v[key]
            self.trip1.add_report(ex.MarineReport(rec))

        self.trip2 = ex.Voyage()
        self.speed1 = 18./self.km_to_nm
        for hour in range(0,3):
            rec = IMMA()
            v = {'ID':'SHIP1    ', 'YR':2001, 'MO':1, 'DY':1, 'HR':hour, 
                 'LAT':hour*self.speed1*360./(2*np.pi*6371.0088), 'LON':0.0, 'DS':8, 'VS':4}
            for key in v: rec.data[key] = v[key]
            self.trip2.add_report(ex.MarineReport(rec))
        self.trip2.reps[1].setvar('LON', 1.0)

    def test_first_entry_missing(self):
        difference_from_estimated_location = tc.distr1(self.trip1)
        self.assertEqual(difference_from_estimated_location[0],None)

    def test_ship_is_at_computed_location(self):
        difference_from_estimated_location = tc.distr1(self.trip1)
        for i, diff in enumerate(difference_from_estimated_location):
            if i > 0 and i < len(difference_from_estimated_location)-1:
                self.assertAlmostEqual(diff,0,delta=0.00001)

    def test_misplaced_ob_out_by_1degree_times_coslat(self):
        difference_from_estimated_location = tc.distr1(self.trip2)
        self.assertAlmostEqual(difference_from_estimated_location[1],
                               (2*np.pi*6371.0088)*np.cos(self.trip2.reps[1].lat()*np.pi/180.)/360.,delta=0.00001)

class TestTrackQCMethods_distr2(unittest.TestCase):
    
    def setUp(self):
        self.km_to_nm = 0.539957
        self.trip1 = ex.Voyage()
        self.speed1 = 18./self.km_to_nm
        for hour in range(0,24):
            rec = IMMA()
            v = {'ID':'SHIP1    ', 'YR':2001, 'MO':1, 'DY':1, 'HR':hour, 
                 'LAT':hour*self.speed1*360./(2*np.pi*6371.0088), 'LON':0.0, 'DS':8, 'VS':4}
            for key in v: rec.data[key] = v[key]
            self.trip1.add_report(ex.MarineReport(rec))

        self.trip2 = ex.Voyage()
        self.speed1 = 18./self.km_to_nm
        for hour in range(0,3):
            rec = IMMA()
            v = {'ID':'SHIP1    ', 'YR':2001, 'MO':1, 'DY':1, 'HR':hour, 
                 'LAT':hour*self.speed1*360./(2*np.pi*6371.0088), 'LON':0.0, 'DS':8, 'VS':4}
            for key in v: rec.data[key] = v[key]
            self.trip2.add_report(ex.MarineReport(rec))
        self.trip2.reps[1].setvar('LON', 1.0)

    def test_last_entry_missing(self):
        difference_from_estimated_location = tc.distr2(self.trip1)
        self.assertEqual(difference_from_estimated_location[-1],None)

    def test_ship_is_at_computed_location(self):
        difference_from_estimated_location = tc.distr2(self.trip1)
        for i, diff in enumerate(difference_from_estimated_location):
            if i > 0 and i < len(difference_from_estimated_location)-1:
                self.assertAlmostEqual(diff,0,delta=0.00001)

    def test_misplaced_ob_out_by_1degree_times_coslat(self):
        difference_from_estimated_location = tc.distr2(self.trip2)
        self.assertAlmostEqual(difference_from_estimated_location[1],
                               (2*np.pi*6371.0088)*np.cos(self.trip2.reps[1].lat()*np.pi/180.)/360.,delta=0.00001)

class TestTrackQCMethods_midpt(unittest.TestCase):
    #midpoint_discrepancies = midpt(inreps,time_differences)
    def setUp(self):
        self.km_to_nm = 0.539957
        self.trip1 = ex.Voyage()
        self.speed1 = 18./self.km_to_nm
        for hour in range(0,24):
            rec = IMMA()
            v = {'ID':'SHIP1    ', 'YR':2001, 'MO':1, 'DY':1, 'HR':hour, 
                 'LAT':hour*self.speed1*360./(2*np.pi*6371.0088), 'LON':0.0, 'DS':8, 'VS':4}
            for key in v: rec.data[key] = v[key]
            self.trip1.add_report(ex.MarineReport(rec))

        self.trip2 = ex.Voyage()
        self.speed1 = 18./self.km_to_nm
        for hour in range(0,3):
            rec = IMMA()
            v = {'ID':'SHIP1    ', 'YR':2001, 'MO':1, 'DY':1, 'HR':hour, 
                 'LAT':hour*self.speed1*360./(2*np.pi*6371.0088), 'LON':0.0, 'DS':8, 'VS':4}
            for key in v: rec.data[key] = v[key]
            self.trip2.add_report(ex.MarineReport(rec))
        self.trip2.reps[1].setvar('LON', 1.0)

    def test_first_and_last_are_missing(self):
        midpoint_discrepancies = tc.midpt(self.trip1)
        self.assertEqual(midpoint_discrepancies[0],None)
        self.assertEqual(midpoint_discrepancies[-1],None)
    
    def test_midpt_1_deg_error_out_by_60coslat(self):
        midpoint_discrepancies = tc.midpt(self.trip2)
        self.assertAlmostEqual(midpoint_discrepancies[1],
                               (2*np.pi*6371.0088)*math.cos(self.trip2.reps[1].lat()*np.pi/180)/360.,delta=0.00001)

    def test_midpt_at_computed_location(self):
        midpoint_discrepancies = tc.midpt(self.trip1)
        for i,pt in enumerate(midpoint_discrepancies):
            if i > 0 and i < len(midpoint_discrepancies)-1:
                self.assertNotEqual(pt,None,'Failed at '+str(i)+' out of '+str(len(midpoint_discrepancies)))
                self.assertAlmostEqual(pt,0,msg='Failed at '+str(i)+' with mid point = '+str(pt),delta=0.00001)
   
class TestTrackQCMethods_direction_continuity(unittest.TestCase):
#result = direction_continuity(dsi,dsi_previous,ship_directions)
    def test_just_pass_and_just_fail(self):
        for angle in [0,45,90,135,180,225,270,315,360]:
            self.assertEqual(10, tc.direction_continuity(angle,angle,angle+60.1))
            self.assertEqual( 0, tc.direction_continuity(angle,angle,angle+59.9))

class TestTrackQCMethods_speed_continuity(unittest.TestCase):
 
    def test_1(self):
        km_to_nm = 0.539957
        result = tc.speed_continuity(12,12,12/km_to_nm)
        self.assertEqual(0,result)
    
    def test_just_fails(self):
        km_to_nm = 0.539957
        result = tc.speed_continuity(12,12,(12+10.01)/km_to_nm)
        self.assertEqual(10,result)
    
    def test_just_passes(self):
        km_to_nm = 0.539957
        result = tc.speed_continuity(12,12,(12+9.99)/km_to_nm)
        self.assertEqual(0,result)

    def test_input_speed_is_None(self):
        result = tc.speed_continuity(12,12,None)
        self.assertEqual(0,result)



if __name__ == '__main__':
    unittest.main()
