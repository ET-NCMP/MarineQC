import unittest
import numpy as np
from SimpleIMMA import IMMA
import Extended_IMMA as ex
import trackqc as tqc
import os
import sys

class TestTrackQC_track_day_test(unittest.TestCase):

    def test_daytime_exeter(self):
        daytime=tqc.track_day_test(2019,6,21,12.0,50.7,-3.5,elevdlim=-2.5)
        self.assertEqual(daytime,True)

    def test_nighttime_exeter(self):
        daytime=tqc.track_day_test(2019,6,21,0.0,50.7,-3.5,elevdlim=-2.5)
        self.assertEqual(daytime,False)

    def test_large_elevdlim_exeter(self):
        daytime=tqc.track_day_test(2019,6,21,12.0,50.7,-3.5,elevdlim=89.0)
        self.assertEqual(daytime,False)

    def test_error_invalid_parameter(self):
        try:
            daytime=tqc.track_day_test(2019,13,21,0.0,50.7,-3.5,elevdlim=-2.5)
        except AssertionError as error:
            error_return_text='month is invalid'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)


class TestTrackQC_trim_mean(unittest.TestCase):

    def test_no_trim(self):
        arr=np.array([10.0,4.0,3.0,2.0,1.0])
        trim=tqc.trim_mean(arr,0)
        self.assertEqual(trim,4.0)
        self.assertEqual(np.all(arr==np.array([10.0,4.0,3.0,2.0,1.0])),True) # this checks the array is not modifed by the function

    def test_with_trim(self):
        arr=np.array([10.0,4.0,3.0,2.0,1.0])
        trim=tqc.trim_mean(arr,5)
        self.assertEqual(trim,3.0)
        self.assertEqual(np.all(arr==np.array([10.0,4.0,3.0,2.0,1.0])),True) # this checks the array is not modifed by the function


class TestTrackQC_trim_std(unittest.TestCase):

    def test_no_trim(self):
        arr=np.array([6.0,1.0,1.0,1.0,1.0])
        trim=tqc.trim_std(arr,0)
        self.assertEqual(trim,2.0)
        self.assertEqual(np.all(arr==np.array([6.0,1.0,1.0,1.0,1.0])),True) # this checks the array is not modifed by the function

    def test_with_trim(self):
        arr=np.array([6.0,1.0,1.0,1.0,1.0])
        trim=tqc.trim_std(arr,5)
        self.assertEqual(trim,0.0)
        self.assertEqual(np.all(arr==np.array([6.0,1.0,1.0,1.0,1.0])),True) # this checks the array is not modifed by the function


class TestTrackQC_aground_check(unittest.TestCase):

    def setUp(self):

        #stationary drifter
        vals1 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0}]

        #stationary drifter (artificial 'jitter' spikes)
        vals2 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':1.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.0, 'LON':1.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0}]

        #stationary drifter (artificial 'jitter' which won't be fully smoothed and outside tolerance)
        vals3 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':1.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':1.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0}]

        #stationary drifter (artificial 'jitter' which won't be fully smoothed and within tolerance)
        vals4 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.01, 'LON':0.01, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.01, 'LON':0.01, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0}]

        #moving drifter (going west)
        vals5 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':-0.02, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.0, 'LON':-0.04, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.0, 'LON':-0.06, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.0, 'LON':-0.08, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.0, 'LON':-0.10, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':-0.12, 'SST':5.0}]

        #moving drifter (going north)
        vals6 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.02, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.04, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.06, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.08, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.10, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.12, 'LON':0.0, 'SST':5.0}]

        #runs aground (drifter going north then stops)
        vals7 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.02, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.04, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.06, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.08, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.08, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.08, 'LON':0.0, 'SST':5.0}]

        #stationary drifter (high frequency sampling prevents detection)
        vals8 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':1, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':2, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':3, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':4, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':5, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':6, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':7, 'LAT':0.0, 'LON':0.0, 'SST':5.0}]

        #stationary drifter (low frequency sampling prevents detection)
        vals9 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':10, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':13, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':16, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':19, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0}]

        #stationary drifter (mid frequency sampling enables detection)
        vals10 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':0, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':0, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':9, 'HR':0, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':10, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0}]

        #stationary drifter (changed sampling prevents early detection)
        vals11 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':8, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':9, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':10, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':11, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0}]

        #moving drifter (going northwest at equator but going slowly and within tolerance)
        vals12 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.005, 'LON':-0.005, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.01, 'LON':-0.01, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.015, 'LON':-0.015, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.02, 'LON':-0.02, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.025, 'LON':-0.025, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.03, 'LON':-0.03, 'SST':5.0}]

        #moving drifter (going west in high Arctic but going slower than tolerance set at equator)
        vals13 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':85.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':85.0, 'LON':-0.02, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':85.0, 'LON':-0.04, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':85.0, 'LON':-0.06, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':85.0, 'LON':-0.08, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':85.0, 'LON':-0.10, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':85.0, 'LON':-0.12, 'SST':5.0}]

        #stationary then moves
        vals14 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.02, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.04, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.06, 'LON':0.0, 'SST':5.0}]

        #too short for QC
        vals15 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':-0.02, 'SST':5.0}]

        #assertion error - bad input parameter
        vals16 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':-0.02, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.0, 'LON':-0.04, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.0, 'LON':-0.06, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.0, 'LON':-0.08, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.0, 'LON':-0.10, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':-0.12, 'SST':5.0}]

        #assertion error - missing observation
        vals17 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':-0.02, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.0, 'LON':-0.04, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.0, 'LON':-0.06, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.0, 'LON':-0.08, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.0, 'LON':-0.10, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':-0.12, 'SST':5.0}]

        #assertion error - times not sorted
        vals18 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':-0.02, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.0, 'LON':-0.04, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':-0.06, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.0, 'LON':-0.08, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.0, 'LON':-0.10, 'SST':5.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':-0.12, 'SST':5.0}]

        self.reps1 = ex.Voyage()
        self.reps2 = ex.Voyage()
        self.reps3 = ex.Voyage()
        self.reps4 = ex.Voyage()
        self.reps5 = ex.Voyage()
        self.reps6 = ex.Voyage()
        self.reps7 = ex.Voyage()
        self.reps8 = ex.Voyage()
        self.reps9 = ex.Voyage()
        self.reps10 = ex.Voyage()
        self.reps11 = ex.Voyage()
        self.reps12 = ex.Voyage()
        self.reps13 = ex.Voyage()
        self.reps14 = ex.Voyage()
        self.reps15 = ex.Voyage()
        self.reps16 = ex.Voyage()
        self.reps17 = ex.Voyage()
        self.reps18 = ex.Voyage()

        for v in vals1:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps1.add_report(rep)

        for v in vals2:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps2.add_report(rep)

        for v in vals3:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps3.add_report(rep)

        for v in vals4:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps4.add_report(rep)

        for v in vals5:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps5.add_report(rep)

        for v in vals6:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps6.add_report(rep)

        for v in vals7:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps7.add_report(rep)

        for v in vals8:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps8.add_report(rep)

        for v in vals9:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps9.add_report(rep)

        for v in vals10:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps10.add_report(rep)

        for v in vals11:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps11.add_report(rep)

        for v in vals12:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps12.add_report(rep)

        for v in vals13:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps13.add_report(rep)

        for v in vals14:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps14.add_report(rep)

        for v in vals15:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps15.add_report(rep)

        for v in vals16:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps16.add_report(rep)

        for v in vals17:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps17.add_report(rep)
        self.reps17.setvar(1,'LON',None)

        for v in vals18:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps18.add_report(rep)

    def tearDown(self):
        
        del self.reps1
        del self.reps2
        del self.reps3
        del self.reps4
        del self.reps5
        del self.reps6
        del self.reps7
        del self.reps8
        del self.reps9
        del self.reps10
        del self.reps11
        del self.reps12
        del self.reps13
        del self.reps14
        del self.reps15
        del self.reps16
        del self.reps17
        del self.reps18

    # --- original aground check ---

    def test_stationary(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.aground_check(self.reps1.reps,3,1,2)
        for i in range(0, len(self.reps1)):
            self.assertEqual(self.reps1.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_stationary_jitter_spikes(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.aground_check(self.reps2.reps,3,1,2)
        for i in range(0, len(self.reps2)):
            self.assertEqual(self.reps2.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_stationary_big_remaining_jitter(self):
        expected_flags=[0,0,0,0,1,1,1]
        tqc.aground_check(self.reps3.reps,3,1,2)
        for i in range(0, len(self.reps3)):
            self.assertEqual(self.reps3.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_stationary_small_remaining_jitter(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.aground_check(self.reps4.reps,3,1,2)
        for i in range(0, len(self.reps4)):
            self.assertEqual(self.reps4.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_moving_west(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.aground_check(self.reps5.reps,3,1,2)
        for i in range(0, len(self.reps5)):
            self.assertEqual(self.reps5.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_moving_north(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.aground_check(self.reps6.reps,3,1,2)
        for i in range(0, len(self.reps6)):
            self.assertEqual(self.reps6.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_moving_north_then_stop(self):
        expected_flags=[0,0,0,0,1,1,1]
        tqc.aground_check(self.reps7.reps,3,1,2)
        for i in range(0, len(self.reps7)):
            self.assertEqual(self.reps7.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_stationary_high_freq_sampling(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.aground_check(self.reps8.reps,3,1,2)
        for i in range(0, len(self.reps8)):
            self.assertEqual(self.reps8.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_stationary_low_freq_sampling(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.aground_check(self.reps9.reps,3,1,2)
        for i in range(0, len(self.reps9)):
            self.assertEqual(self.reps9.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_stationary_mid_freq_sampling(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.aground_check(self.reps10.reps,3,1,2)
        for i in range(0, len(self.reps10)):
            self.assertEqual(self.reps10.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_stationary_low_to_mid_freq_sampling(self):
        expected_flags=[0,0,1,1,1,1,1]
        tqc.aground_check(self.reps11.reps,3,1,2)
        for i in range(0, len(self.reps11)):
            self.assertEqual(self.reps11.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_moving_slowly_northwest(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.aground_check(self.reps12.reps,3,1,2)
        for i in range(0, len(self.reps12)):
            self.assertEqual(self.reps12.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_moving_slowly_west_in_arctic(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.aground_check(self.reps13.reps,3,1,2)
        for i in range(0, len(self.reps13)):
            self.assertEqual(self.reps13.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_stop_then_moving_north(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.aground_check(self.reps14.reps,3,1,2)
        for i in range(0, len(self.reps14)):
            self.assertEqual(self.reps14.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_too_short_for_qc(self):
        expected_flags=[0,0]
        old_stdout = sys.stdout 
        f = open(os.devnull, 'w')
        sys.stdout = f
        tqc.aground_check(self.reps15.reps,3,1,2)
        sys.stdout = old_stdout
        for i in range(0, len(self.reps15)):
            self.assertEqual(self.reps15.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_error_bad_input_parameter(self):
        expected_flags=[9,9,9,9,9,9,9]
        try:
            tqc.aground_check(self.reps16.reps,0,1,2)
        except AssertionError as error:
            error_return_text='invalid input parameter: smooth_win must be >= 1'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps16)):
            self.assertEqual(self.reps16.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_error_missing_observation(self):
        expected_flags=[9,9,9,9,9,9,9]
        try:
            tqc.aground_check(self.reps17.reps,3,1,2)
        except AssertionError as error:
            error_return_text='problem with report values: Nan(s) found in longitude'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps17)):
            self.assertEqual(self.reps17.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_error_not_time_sorted(self):
        expected_flags=[9,9,9,9,9,9,9]
        try:
            tqc.aground_check(self.reps18.reps,3,1,2)
        except AssertionError as error:
            error_return_text='problem with report values: times are not sorted'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps18)):
            self.assertEqual(self.reps18.get_qc(i,'POS','drf_agr'), expected_flags[i])

    # --- new aground check---

    def test_new_stationary(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.new_aground_check(self.reps1.reps,3,1)
        for i in range(0, len(self.reps1)):
            self.assertEqual(self.reps1.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_stationary_jitter_spikes(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.new_aground_check(self.reps2.reps,3,1)
        for i in range(0, len(self.reps2)):
            self.assertEqual(self.reps2.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_stationary_big_remaining_jitter(self):
        expected_flags=[0,0,0,0,1,1,1]
        tqc.new_aground_check(self.reps3.reps,3,1)
        for i in range(0, len(self.reps3)):
            self.assertEqual(self.reps3.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_stationary_small_remaining_jitter(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.new_aground_check(self.reps4.reps,3,1)
        for i in range(0, len(self.reps4)):
            self.assertEqual(self.reps4.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_moving_west(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.new_aground_check(self.reps5.reps,3,1)
        for i in range(0, len(self.reps5)):
            self.assertEqual(self.reps5.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_moving_north(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.new_aground_check(self.reps6.reps,3,1)
        for i in range(0, len(self.reps6)):
            self.assertEqual(self.reps6.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_moving_north_then_stop(self):
        expected_flags=[0,0,0,0,1,1,1]
        tqc.new_aground_check(self.reps7.reps,3,1)
        for i in range(0, len(self.reps7)):
            self.assertEqual(self.reps7.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_stationary_high_freq_sampling(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.new_aground_check(self.reps8.reps,3,1)
        for i in range(0, len(self.reps8)):
            self.assertEqual(self.reps8.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_stationary_low_freq_sampling(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.new_aground_check(self.reps9.reps,3,1)
        for i in range(0, len(self.reps9)):
            self.assertEqual(self.reps9.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_stationary_mid_freq_sampling(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.new_aground_check(self.reps10.reps,3,1)
        for i in range(0, len(self.reps10)):
            self.assertEqual(self.reps10.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_stationary_low_to_mid_freq_sampling(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.new_aground_check(self.reps11.reps,3,1)
        for i in range(0, len(self.reps11)):
            self.assertEqual(self.reps11.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_moving_slowly_northwest(self):
        expected_flags=[0,0,0,1,1,1,1]
        tqc.new_aground_check(self.reps12.reps,3,1)
        for i in range(0, len(self.reps12)):
            self.assertEqual(self.reps12.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_moving_slowly_west_in_arctic(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.new_aground_check(self.reps13.reps,3,1)
        for i in range(0, len(self.reps13)):
            self.assertEqual(self.reps13.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_stop_then_moving_north(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.new_aground_check(self.reps14.reps,3,1)
        for i in range(0, len(self.reps14)):
            self.assertEqual(self.reps14.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_too_short_for_qc(self):
        expected_flags=[0,0]
        old_stdout = sys.stdout 
        f = open(os.devnull, 'w')
        sys.stdout = f
        tqc.new_aground_check(self.reps15.reps,3,1)
        sys.stdout = old_stdout
        for i in range(0, len(self.reps15)):
            self.assertEqual(self.reps15.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_error_bad_input_parameter(self):
        expected_flags=[9,9,9,9,9,9,9]
        try:
            tqc.new_aground_check(self.reps16.reps,2,1)
        except AssertionError as error:
            error_return_text='invalid input parameter: smooth_win must be an odd number'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps16)):
            self.assertEqual(self.reps16.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_error_missing_observation(self):
        expected_flags=[9,9,9,9,9,9,9]
        try:
            tqc.new_aground_check(self.reps17.reps,3,1)
        except AssertionError as error:
            error_return_text='problem with report values: Nan(s) found in longitude'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps17)):
            self.assertEqual(self.reps17.get_qc(i,'POS','drf_agr'), expected_flags[i])

    def test_new_error_not_time_sorted(self):
        expected_flags=[9,9,9,9,9,9,9]
        try:
            tqc.new_aground_check(self.reps18.reps,3,1)
        except AssertionError as error:
            error_return_text='problem with report values: times are not sorted'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps18)):
            self.assertEqual(self.reps18.get_qc(i,'POS','drf_agr'), expected_flags[i])


class TestTrackQC_speed_check(unittest.TestCase):

    def setUp(self):

        #iquam parameter dictionary
        self.iquam_parameters = {'number_of_neighbours':5, 
                                 'buoy_speed_limit':15.0,
                                 'ship_speed_limit':60.0, 
                                 'delta_d':1.11,
                                 'delta_t':0.01}

        #stationary drifter
        vals1 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7}]

        #fast moving drifter
        vals2 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':3.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':6.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':9.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':12.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':15.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':18.0, 'LON':0.0, 'SST':5.0, 'PT':7}]

        #slow moving drifter
        vals3 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':1.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.0, 'LON':2.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.0, 'LON':3.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.0, 'LON':4.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.0, 'LON':5.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':6.0, 'SST':5.0, 'PT':7}]

        #slow-fast-slow moving drifter
        vals4 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':1.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':2.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':5.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':8.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':9.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':10.0, 'LON':0.0, 'SST':5.0, 'PT':7}]

        #fast moving drifter (high frequency sampling)
        vals5 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':1, 'LAT':3.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':2, 'LAT':6.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':3, 'LAT':9.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':4, 'LAT':12.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':5, 'LAT':15.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':6, 'LAT':18.0, 'LON':0.0, 'SST':5.0, 'PT':7}]

        #fast moving drifter (low frequency sampling)
        vals6 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':13, 'LAT':5.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':14, 'LAT':10.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':15, 'LAT':15.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':16, 'LAT':20.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':17, 'LAT':25.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':18, 'LAT':30.0, 'LON':0.0, 'SST':5.0, 'PT':7}]

        #slow-fast-slow moving drifter (mid frequency sampling)
        vals7 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.5, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':0, 'LAT':1.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':2.5, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':0, 'LAT':4.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':4.5, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':0, 'LAT':5.0, 'LON':0.0, 'SST':5.0, 'PT':7}]

        #fast moving drifter (with irregular sampling)
        vals8 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':3.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':12.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':12.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':23, 'LAT':14.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':23, 'LAT':14.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':23, 'LAT':17.0, 'LON':0.0, 'SST':5.0, 'PT':7}]

        #fast moving Arctic drifter 
        vals9 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':85.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':85.0, 'LON':30.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':85.0, 'LON':60.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':85.0, 'LON':90.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':85.0, 'LON':120.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':85.0, 'LON':150.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':85.0, 'LON':180.0, 'SST':5.0, 'PT':7}]

        #stationary drifter (gross position errors) 
        vals10 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':50.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':50.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7}]

        #too short for QC
        vals11 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7}]

        #assertion error - bad input parameter
        vals12 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7}]

        #assertion error - missing observation
        vals13 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':4, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7}]

        #assertion error - times not sorted
        vals14 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':3, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':2, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':5, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':6, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':7, 'HR':12, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'PT':7}]

        self.reps1 = ex.Voyage()
        self.reps2 = ex.Voyage()
        self.reps3 = ex.Voyage()
        self.reps4 = ex.Voyage()
        self.reps5 = ex.Voyage()
        self.reps6 = ex.Voyage()
        self.reps7 = ex.Voyage()
        self.reps8 = ex.Voyage()
        self.reps9 = ex.Voyage()
        self.reps10 = ex.Voyage()
        self.reps11 = ex.Voyage()
        self.reps12 = ex.Voyage()
        self.reps13 = ex.Voyage()
        self.reps14 = ex.Voyage()

        for v in vals1:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps1.add_report(rep)

        for v in vals2:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps2.add_report(rep)

        for v in vals3:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps3.add_report(rep)

        for v in vals4:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps4.add_report(rep)

        for v in vals5:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps5.add_report(rep)

        for v in vals6:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps6.add_report(rep)

        for v in vals7:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps7.add_report(rep)

        for v in vals8:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps8.add_report(rep)

        for v in vals9:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps9.add_report(rep)

        for v in vals10:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps10.add_report(rep)

        for v in vals11:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps11.add_report(rep)

        for v in vals12:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps12.add_report(rep)

        for v in vals13:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps13.add_report(rep)
        self.reps13.setvar(1,'LON',None)

        for v in vals14:
            rec = IMMA()
            for key in v:
                rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            self.reps14.add_report(rep)

    def tearDown(self):
        
        del self.iquam_parameters
        del self.reps1
        del self.reps2
        del self.reps3
        del self.reps4
        del self.reps5
        del self.reps6
        del self.reps7
        del self.reps8
        del self.reps9
        del self.reps10
        del self.reps11
        del self.reps12
        del self.reps13
        del self.reps14

    # --- original speed check ---

    def test_stationary(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.speed_check(self.reps1.reps,2.5,0.5,1.0)
        for i in range(0, len(self.reps1)):
            self.assertEqual(self.reps1.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_fast_drifter(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.speed_check(self.reps2.reps,2.5,0.5,1.0)
        for i in range(0, len(self.reps2)):
            self.assertEqual(self.reps2.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_slow_drifter(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.speed_check(self.reps3.reps,2.5,0.5,1.0)
        for i in range(0, len(self.reps3)):
            self.assertEqual(self.reps3.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_slow_fast_slow_drifter(self):
        expected_flags=[0,0,1,1,1,0,0]
        tqc.speed_check(self.reps4.reps,2.5,0.5,1.0)
        for i in range(0, len(self.reps4)):
            self.assertEqual(self.reps4.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_high_freqency_sampling(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.speed_check(self.reps5.reps,2.5,0.5,1.0)
        for i in range(0, len(self.reps5)):
            self.assertEqual(self.reps5.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_low_freqency_sampling(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.speed_check(self.reps6.reps,2.5,0.5,1.0)
        for i in range(0, len(self.reps6)):
            self.assertEqual(self.reps6.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_slow_fast_slow_mid_freqency_sampling(self):
        expected_flags=[0,1,1,1,1,1,0]
        tqc.speed_check(self.reps7.reps,2.5,0.5,1.0)
        for i in range(0, len(self.reps7)):
            self.assertEqual(self.reps7.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_irregular_sampling(self):
        expected_flags=[1,1,0,0,0,1,1]
        tqc.speed_check(self.reps8.reps,2.5,0.5,1.0)
        for i in range(0, len(self.reps8)):
            self.assertEqual(self.reps8.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_fast_arctic_drifter(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.speed_check(self.reps9.reps,2.5,0.5,1.0)
        for i in range(0, len(self.reps9)):
            self.assertEqual(self.reps9.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_stationary_gross_error(self):
        expected_flags=[0,1,1,1,1,1,1]
        tqc.speed_check(self.reps10.reps,2.5,0.5,1.0)
        for i in range(0, len(self.reps10)):
            self.assertEqual(self.reps10.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_too_short_for_qc(self):
        expected_flags=[0,0]
        old_stdout = sys.stdout 
        f = open(os.devnull, 'w')
        sys.stdout = f
        tqc.speed_check(self.reps11.reps,2.5,0.5,1.0)
        sys.stdout = old_stdout
        for i in range(0, len(self.reps11)):
            self.assertEqual(self.reps11.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_error_bad_input_parameter(self):
        expected_flags=[9,9,9,9,9,9,9]
        try:
            tqc.speed_check(self.reps12.reps,-2.5,0.5,1.0)
        except AssertionError as error:
            error_return_text='invalid input parameter: speed_limit must be >= 0'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps12)):
            self.assertEqual(self.reps12.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_error_missing_observation(self):
        expected_flags=[9,9,9,9,9,9,9]
        try:
            tqc.speed_check(self.reps13.reps,2.5,0.5,1.0)
        except AssertionError as error:
            error_return_text='problem with report values: Nan(s) found in longitude'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps13)):
            self.assertEqual(self.reps13.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_error_not_time_sorted(self):
        expected_flags=[9,9,9,9,9,9,9]
        try:
            tqc.speed_check(self.reps14.reps,2.5,0.5,1.0)
        except AssertionError as error:
            error_return_text='problem with report values: times are not sorted'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps14)):
            self.assertEqual(self.reps14.get_qc(i,'POS','drf_spd'), expected_flags[i])

    # --- new speed check ---

    def test_new_stationary(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.new_speed_check(self.reps1.reps,self.iquam_parameters,2.5,0.5)
        for i in range(0, len(self.reps1)):
            self.assertEqual(self.reps1.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_new_fast_drifter(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.new_speed_check(self.reps2.reps,self.iquam_parameters,2.5,0.5)
        for i in range(0, len(self.reps2)):
            self.assertEqual(self.reps2.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_new_slow_drifter(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.new_speed_check(self.reps3.reps,self.iquam_parameters,2.5,0.5)
        for i in range(0, len(self.reps3)):
            self.assertEqual(self.reps3.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_new_slow_fast_slow_drifter(self):
        expected_flags=[0,0,1,1,1,0,0]
        tqc.new_speed_check(self.reps4.reps,self.iquam_parameters,2.5,0.5)
        for i in range(0, len(self.reps4)):
            self.assertEqual(self.reps4.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_new_high_freqency_sampling(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.new_speed_check(self.reps5.reps,self.iquam_parameters,2.5,0.5)
        for i in range(0, len(self.reps5)):
            self.assertEqual(self.reps5.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_new_low_freqency_sampling(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.new_speed_check(self.reps6.reps,self.iquam_parameters,2.5,0.5)
        for i in range(0, len(self.reps6)):
            self.assertEqual(self.reps6.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_new_slow_fast_slow_mid_freqency_sampling(self):
        expected_flags=[0,0,1,1,1,0,0]
        tqc.new_speed_check(self.reps7.reps,self.iquam_parameters,2.5,0.5)
        for i in range(0, len(self.reps7)):
            self.assertEqual(self.reps7.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_new_irregular_sampling(self):
        expected_flags=[1,1,1,0,0,1,1]
        tqc.new_speed_check(self.reps8.reps,self.iquam_parameters,2.5,0.5)
        for i in range(0, len(self.reps8)):
            self.assertEqual(self.reps8.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_new_fast_arctic_drifter(self):
        expected_flags=[1,1,1,1,1,1,1]
        tqc.new_speed_check(self.reps9.reps,self.iquam_parameters,2.5,0.5)
        for i in range(0, len(self.reps9)):
            self.assertEqual(self.reps9.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_new_stationary_gross_error(self):
        expected_flags=[0,0,0,0,0,0,0]
        tqc.new_speed_check(self.reps10.reps,self.iquam_parameters,2.5,0.5)
        for i in range(0, len(self.reps10)):
            self.assertEqual(self.reps10.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_new_too_short_for_qc(self):
        expected_flags=[0,0]
        old_stdout = sys.stdout 
        f = open(os.devnull, 'w')
        sys.stdout = f
        tqc.new_speed_check(self.reps11.reps,self.iquam_parameters,2.5,0.5)
        sys.stdout = old_stdout
        for i in range(0, len(self.reps11)):
            self.assertEqual(self.reps11.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_new_error_bad_input_parameter(self):
        expected_flags=[9,9,9,9,9,9,9]
        try:
            tqc.new_speed_check(self.reps12.reps,self.iquam_parameters,-2.5,0.5)
        except AssertionError as error:
            error_return_text='invalid input parameter: speed_limit must be >= 0'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps12)):
            self.assertEqual(self.reps12.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_new_error_missing_observation(self):
        expected_flags=[9,9,9,9,9,9,9]
        try:
            tqc.new_speed_check(self.reps13.reps,self.iquam_parameters,2.5,0.5)
        except AssertionError as error:
            error_return_text='problem with report values: Nan(s) found in longitude'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps13)):
            self.assertEqual(self.reps13.get_qc(i,'POS','drf_spd'), expected_flags[i])

    def test_new_error_not_time_sorted(self):
        expected_flags=[9,9,9,9,9,9,9]
        try:
            tqc.new_speed_check(self.reps14.reps,self.iquam_parameters,2.5,0.5)
        except AssertionError as error:
            error_return_text='problem with report values: times are not sorted'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps14)):
            self.assertEqual(self.reps14.get_qc(i,'POS','drf_spd'), expected_flags[i])

class TestTrackQC_tail_check(unittest.TestCase):

    def setUp(self):

        #all daytime
        vals1 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #all land-masked
        vals2 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0}]

        #all ice
        vals3 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2}]
       
        #one usable value
        vals4 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0}]

        #start tail bias
        vals5 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #start tail negative bias
        vals6 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':4.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':4.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':4.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':4.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #start tail bias obs missing
        vals7 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #end tail bias
        vals8 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #end tail bias obs missing
        vals9 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0}]

        #start tail noisy
        vals10 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':7.5, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #end tail noisy
        vals11 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':7.5, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #two tails
        vals12 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':7.5, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #all biased
        vals13 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #all noisy
        vals14 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':7.5, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':7.5, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':7.5, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #start tail bias with bgvar
        vals15 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #all biased with bgvar
        vals16 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #short start tail
        vals17 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #short end tail
        vals18 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #short two tails
        vals19 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #short all fail
        vals20 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #short start tail with bgvar
        vals21 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #short all fail with bgvar
        vals22 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':7.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #long and short start tail
        vals23 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #long and short end tail
        vals24 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #long and short two tail
        vals25 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #one long and one short tail
        vals26 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #too short for short tail
        vals27 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #long and short all fail
        vals28 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.5, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.5, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #long and short start tail with bgvar
        vals29 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':7.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':7.0, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #long and short all fail with bgvar
        vals30 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':6.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.5, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.5, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0}]

        #good data
        vals31 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.1, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.1, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.1, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.1, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.1, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #long and short start tail big bgvar
        vals32 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.1, 'OSTIA':5.0, 'BGVAR':0.3, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.1, 'OSTIA':5.0, 'BGVAR':0.3, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.1, 'OSTIA':5.0, 'BGVAR':0.3, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.1, 'OSTIA':5.0, 'BGVAR':0.3, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.3, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.3, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.3, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.3, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.3, 'ICE':0.0}]

        #start tail noisy big bgvar
        vals33 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':7.5, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0}]

        #assertion error - bad input parameter
        vals34 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0}]

        #assertion error - missing matched value
        vals35 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0}]

        #assertion error - invalid ice value
        vals36 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':1.1},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0}]

        #assertion error - missing observation value
        vals37 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0}]

        #assertion error - times not sorted
        vals38 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0}]

        #assertion error - invalid background sst
        vals39 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':46.0, 'BGVAR':1.0, 'ICE':0.0}]

        #assertion error - invalid background error variance
        vals40 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':-1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':1.0, 'ICE':0.0}]

        self.reps1 = ex.Voyage()
        self.reps2 = ex.Voyage()
        self.reps3 = ex.Voyage()
        self.reps4 = ex.Voyage()
        self.reps5 = ex.Voyage()
        self.reps6 = ex.Voyage()
        self.reps7 = ex.Voyage()
        self.reps8 = ex.Voyage()
        self.reps9 = ex.Voyage()
        self.reps10 = ex.Voyage()
        self.reps11 = ex.Voyage()
        self.reps12 = ex.Voyage()
        self.reps13 = ex.Voyage()
        self.reps14 = ex.Voyage()
        self.reps15 = ex.Voyage()
        self.reps16 = ex.Voyage()
        self.reps17 = ex.Voyage()
        self.reps18 = ex.Voyage()
        self.reps19 = ex.Voyage()
        self.reps20 = ex.Voyage()
        self.reps21 = ex.Voyage()
        self.reps22 = ex.Voyage()
        self.reps23 = ex.Voyage()
        self.reps24 = ex.Voyage()
        self.reps25 = ex.Voyage()
        self.reps26 = ex.Voyage()
        self.reps27 = ex.Voyage()
        self.reps28 = ex.Voyage()
        self.reps29 = ex.Voyage()
        self.reps30 = ex.Voyage()
        self.reps31 = ex.Voyage()
        self.reps32 = ex.Voyage()
        self.reps33 = ex.Voyage()
        self.reps34 = ex.Voyage()
        self.reps35 = ex.Voyage()
        self.reps36 = ex.Voyage()
        self.reps37 = ex.Voyage()
        self.reps38 = ex.Voyage()
        self.reps39 = ex.Voyage()
        self.reps40 = ex.Voyage()

        for v in vals1:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps1.add_report(rep)

        for v in vals2:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps2.add_report(rep)

        for v in vals3:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps3.add_report(rep)

        for v in vals4:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps4.add_report(rep)

        for v in vals5:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps5.add_report(rep)

        for v in vals6:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps6.add_report(rep)

        for v in vals7:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps7.add_report(rep)

        for v in vals8:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps8.add_report(rep)

        for v in vals9:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps9.add_report(rep)

        for v in vals10:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps10.add_report(rep)

        for v in vals11:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps11.add_report(rep)

        for v in vals12:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps12.add_report(rep)

        for v in vals13:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps13.add_report(rep)

        for v in vals14:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps14.add_report(rep)

        for v in vals15:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps15.add_report(rep)

        for v in vals16:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps16.add_report(rep)

        for v in vals17:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps17.add_report(rep)

        for v in vals18:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps18.add_report(rep)

        for v in vals19:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps19.add_report(rep)

        for v in vals20:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps20.add_report(rep)

        for v in vals21:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps21.add_report(rep)

        for v in vals22:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps22.add_report(rep)

        for v in vals23:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps23.add_report(rep)

        for v in vals24:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps24.add_report(rep)

        for v in vals25:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps25.add_report(rep)

        for v in vals26:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps26.add_report(rep)

        for v in vals27:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps27.add_report(rep)

        for v in vals28:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps28.add_report(rep)

        for v in vals29:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps29.add_report(rep)

        for v in vals30:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps30.add_report(rep)

        for v in vals31:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps31.add_report(rep)

        for v in vals32:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps32.add_report(rep)

        for v in vals33:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps33.add_report(rep)

        for v in vals34:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps34.add_report(rep)

        for v in vals35:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            #rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps35.add_report(rep)

        for v in vals36:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps36.add_report(rep)

        for v in vals37:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps37.add_report(rep)
        self.reps37.setvar(1,'LAT',None)

        for v in vals38:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps38.add_report(rep)

        for v in vals39:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps39.add_report(rep)

        for v in vals40:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps40.add_report(rep)

    def tearDown(self):
        
        del self.reps1
        del self.reps2
        del self.reps3
        del self.reps4
        del self.reps5
        del self.reps6
        del self.reps7
        del self.reps8
        del self.reps9
        del self.reps10
        del self.reps11
        del self.reps12
        del self.reps13
        del self.reps14
        del self.reps15
        del self.reps16
        del self.reps17
        del self.reps18
        del self.reps19
        del self.reps20
        del self.reps21
        del self.reps22
        del self.reps23
        del self.reps24
        del self.reps25
        del self.reps26
        del self.reps27
        del self.reps28
        del self.reps29
        del self.reps30
        del self.reps31
        del self.reps32
        del self.reps33
        del self.reps34
        del self.reps35
        del self.reps36
        del self.reps37
        del self.reps38
        del self.reps39
        del self.reps40

    # --- tail check tests ---

    def test_all_daytime(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps1.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps1)):
            self.assertEqual(self.reps1.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps1.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_all_land_masked(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps2.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps2)):
            self.assertEqual(self.reps2.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps2.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_all_ice(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps3.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps3)):
            self.assertEqual(self.reps3.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps3.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_one_usable_value(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps4.reps,3,3.0,2,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps4)):
            self.assertEqual(self.reps4.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps4.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_start_tail_bias(self):
        expected_flags={'drf_tail1':[1,1,1,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps5.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps5)):
            self.assertEqual(self.reps5.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps5.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_start_tail_negative_bias(self):
        expected_flags={'drf_tail1':[1,1,1,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps6.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps6)):
            self.assertEqual(self.reps6.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps6.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_start_tail_bias_obs_missing(self):
        expected_flags={'drf_tail1':[1,1,1,1,1,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps7.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps7)):
            self.assertEqual(self.reps7.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps7.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_end_tail_bias(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,1,1,1]}
        tqc.sst_tail_check(self.reps8.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps8)):
            self.assertEqual(self.reps8.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps8.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_end_tail_bias_obs_missing(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,1,1,1,1,1]}
        tqc.sst_tail_check(self.reps9.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps9)):
            self.assertEqual(self.reps9.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps9.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_start_tail_noisy(self):
        expected_flags={'drf_tail1':[1,1,1,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps10.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps10)):
            self.assertEqual(self.reps10.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps10.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_end_tail_noisy(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,1,1,1]}
        tqc.sst_tail_check(self.reps11.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps11)):
            self.assertEqual(self.reps11.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps11.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_two_tails(self):
        expected_flags={'drf_tail1':[1,1,1,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,1,1,1]}
        tqc.sst_tail_check(self.reps12.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps12)):
            self.assertEqual(self.reps12.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps12.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_all_biased(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps13.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps13)):
            self.assertEqual(self.reps13.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps13.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_all_noisy(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps14.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps14)):
            self.assertEqual(self.reps14.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps14.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_start_tail_bias_with_bgvar(self):
        expected_flags={'drf_tail1':[1,1,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps15.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps15)):
            self.assertEqual(self.reps15.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps15.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_all_biased_with_bgvar(self):
        expected_flags={'drf_tail1':[1,1,1,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,1,1,1]}
        tqc.sst_tail_check(self.reps16.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps16)):
            self.assertEqual(self.reps16.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps16.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_short_start_tail(self):
        expected_flags={'drf_tail1':[1,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps17.reps,7,3.0,3,2.0,2,0.29,1.0,0.3)
        for i in range(0, len(self.reps17)):
            self.assertEqual(self.reps17.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps17.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_short_end_tail(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,1]}
        tqc.sst_tail_check(self.reps18.reps,7,3.0,3,2.0,2,0.29,1.0,0.3)
        for i in range(0, len(self.reps18)):
            self.assertEqual(self.reps18.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps18.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_short_two_tails(self):
        expected_flags={'drf_tail1':[1,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,1]}
        tqc.sst_tail_check(self.reps19.reps,7,3.0,3,2.0,2,0.29,1.0,0.3)
        for i in range(0, len(self.reps19)):
            self.assertEqual(self.reps19.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps19.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_short_all_fail(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps20.reps,7,9.0,3,2.0,2,0.29,1.0,0.3)
        for i in range(0, len(self.reps20)):
            self.assertEqual(self.reps20.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps20.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_short_start_tail_with_bgvar(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps21.reps,7,3.0,3,2.0,2,0.29,1.0,0.3)
        for i in range(0, len(self.reps21)):
            self.assertEqual(self.reps21.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps21.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_short_all_fail_with_bgvar(self):
        expected_flags={'drf_tail1':[1,1,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,1,1]}
        tqc.sst_tail_check(self.reps22.reps,7,9.0,3,2.0,2,0.29,1.0,0.3)
        for i in range(0, len(self.reps22)):
            self.assertEqual(self.reps22.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps22.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_long_and_short_start_tail(self):
        expected_flags={'drf_tail1':[1,1,1,1,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps23.reps,3,3.0,1,1.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps23)):
            self.assertEqual(self.reps23.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps23.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_long_and_short_end_tail(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,1,1,1,1]}
        tqc.sst_tail_check(self.reps24.reps,3,3.0,1,1.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps24)):
            self.assertEqual(self.reps24.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps24.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_long_and_short_two_tails(self):
        expected_flags={'drf_tail1':[1,1,1,1,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,1,1,1,1]}
        tqc.sst_tail_check(self.reps25.reps,3,3.0,1,1.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps25)):
            self.assertEqual(self.reps25.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps25.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_one_long_and_one_short_tail(self):
        expected_flags={'drf_tail1':[1,1,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,1]}
        tqc.sst_tail_check(self.reps26.reps,3,3.0,1,1.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps26)):
            self.assertEqual(self.reps26.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps26.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_too_short_for_short_tail(self):
        expected_flags={'drf_tail1':[1,1,1,1,1,1,1,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps27.reps,3,3.0,3,0.5,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps27)):
            self.assertEqual(self.reps27.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps27.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_long_and_short_all_fail(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps28.reps,3,3.0,1,0.25,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps28)):
            self.assertEqual(self.reps28.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps28.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_long_and_short_start_tail_with_bgvar(self):
        expected_flags={'drf_tail1':[1,1,1,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps29.reps,3,3.0,1,1.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps29)):
            self.assertEqual(self.reps29.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps29.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_long_and_short_all_fail_with_bgvar(self):
        expected_flags={'drf_tail1':[1,1,1,1,1,1,1,1,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps30.reps,3,3.0,1,0.25,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps30)):
            self.assertEqual(self.reps30.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps30.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_good_data(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps31.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps31)):
            self.assertEqual(self.reps31.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps31.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_long_and_short_start_tail_big_bgvar(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps32.reps,3,3.0,1,1.0,1,0.29,1.0,0.3)
        for i in range(0, len(self.reps32)):
            self.assertEqual(self.reps32.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps32.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_start_tail_noisy_big_bgvar(self):
        expected_flags={'drf_tail1':[0,0,0,0,0,0,0,0,0],
                        'drf_tail2':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_tail_check(self.reps33.reps,3,3.0,1,3.0,1,0.29,1.0,2.0)
        for i in range(0, len(self.reps33)):
            self.assertEqual(self.reps33.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps33.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_error_bad_input_parameter(self):
        expected_flags={'drf_tail1':[9,9,9,9,9,9,9,9,9],
                        'drf_tail2':[9,9,9,9,9,9,9,9,9]}
        try:
            tqc.sst_tail_check(self.reps34.reps,0,3.0,1,3.0,1,0.29,1.0,0.3)
        except AssertionError as error:
            error_return_text='invalid input parameter: long_win_len must be >= 1'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps34)):
            self.assertEqual(self.reps34.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps34.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_error_missing_matched_value(self):
        expected_flags={'drf_tail1':[9,9,9,9,9,9,9,9,9],
                        'drf_tail2':[9,9,9,9,9,9,9,9,9]}
        try:
            tqc.sst_tail_check(self.reps35.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        except AssertionError as error:
            error_return_text='matched report value is missing: unknown extended variable name OSTIA'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps35)):
            self.assertEqual(self.reps35.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps35.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_error_invalid_ice_value(self):
        expected_flags={'drf_tail1':[9,9,9,9,9,9,9,9,9],
                        'drf_tail2':[9,9,9,9,9,9,9,9,9]}
        try:
            tqc.sst_tail_check(self.reps36.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        except AssertionError as error:
            error_return_text='matched ice proportion is invalid'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps36)):
            self.assertEqual(self.reps36.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps36.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_error_missing_ob_value(self):
        expected_flags={'drf_tail1':[9,9,9,9,9,9,9,9,9],
                        'drf_tail2':[9,9,9,9,9,9,9,9,9]}
        try:
            tqc.sst_tail_check(self.reps37.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        except AssertionError as error:
            error_return_text='problem with report value: latitude is missing'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps37)):
            self.assertEqual(self.reps37.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps37.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_error_not_time_sorted(self):
        expected_flags={'drf_tail1':[9,9,9,9,9,9,9,9,9],
                        'drf_tail2':[9,9,9,9,9,9,9,9,9]}
        try:
            tqc.sst_tail_check(self.reps38.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        except AssertionError as error:
            error_return_text='problem with report value: times are not sorted'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps38)):
            self.assertEqual(self.reps38.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps38.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_error_invalid_background(self):
        expected_flags={'drf_tail1':[9,9,9,9,9,9,9,9,9],
                        'drf_tail2':[9,9,9,9,9,9,9,9,9]}
        try:
            tqc.sst_tail_check(self.reps39.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        except AssertionError as error:
            error_return_text='matched background sst is invalid'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps39)):
            self.assertEqual(self.reps39.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps39.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    def test_error_invalid_background_error_variance(self):
        expected_flags={'drf_tail1':[9,9,9,9,9,9,9,9,9],
                        'drf_tail2':[9,9,9,9,9,9,9,9,9]}
        try:
            tqc.sst_tail_check(self.reps40.reps,3,3.0,1,3.0,1,0.29,1.0,0.3)
        except AssertionError as error:
            error_return_text='matched background error variance is invalid'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps40)):
            self.assertEqual(self.reps40.get_qc(i,'SST','drf_tail1'), expected_flags['drf_tail1'][i])
            self.assertEqual(self.reps40.get_qc(i,'SST','drf_tail2'), expected_flags['drf_tail2'][i])

    #tests summary
    '''
    - NO CHECK MADE
    + alldaytime
    + all OSTIA missing
    + all ice
    + record too short for either check
    - LONG-TAIL ONLY
    + start tail bias
    + start tail negative bias
    + start tail bias first few obs missing
    + end tail bias
    + end tail bias last few obs missing
    + start tail noisy
    + end tail noisy
    + two tails
    + all record biased
    + all record noisy
    + background error short circuits start tail
    + background error short circuits all biased
    - SHORT-TAIL ONLY
    + start tail
    + end tail
    + two tails
    + all record fail
    + background error short circuits start tail
    + background error short circuits all fail
    - LONG-TAIL then SHORT-TAIL
    + long and short start tail
    + long and short end tail
    + long and short two tails
    + one long tail and one short tail
    + too short for short tail
    + long and short combined fail whole record
    + background error short circuits start tail
    + background error short circuits all fail
    - NO-TAILS
    + no tails
    - EXTRA
    + long and short start tail big bgvar
    + start tail noisy big bgvar
    + assertion error - bad input parameter
    + assertion error - missing matched value
    + assertion error - missing ob value
    + assertion error - invalid ice value
    + assertion error - data not time-sorted
    + assertion error - invalid background sst
    + assertion error - invalid background error
    '''

class TestTrackQC_biased_noisy_check(unittest.TestCase):

    def setUp(self):

        #all daytime
        vals1 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':12.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #all land-masked
        vals2 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0}]

        #all ice
        vals3 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.2}]

        #all bgvar exceeds limit
        vals4 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.4, 'ICE':0.0}]

        #biased warm
        vals5 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #biased cool
        vals6 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':3.8, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':3.8, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':3.8, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':3.8, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':3.8, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':3.8, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':3.8, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':3.8, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':3.8, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #noisy
        vals7 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':7.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':3.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':7.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':3.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':7.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #biased and noisy
        vals8 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':9.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':7.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':7.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':9.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':7.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':7.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':9.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #biased warm obs missing
        vals9 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':6.2, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0}]

        #short record one bad
        vals10 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':9.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #short record two bad
        vals11 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':9.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':9.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #short record two bad obs missing
        vals12 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':9.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':9.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0}]

        #short record two bad obs missing with bgvar masked
        vals13 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.4, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':9.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':9.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0}]

        #good data
        vals14 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #short record good data
        vals15 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #short record obs missing good data
        vals16 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':0.01, 'ICE':0.0}]

        #noisy big bgvar
        vals17 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':7.0, 'OSTIA':5.0, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':3.0, 'OSTIA':5.0, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':7.0, 'OSTIA':5.0, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':3.0, 'OSTIA':5.0, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':7.0, 'OSTIA':5.0, 'BGVAR':4.0, 'ICE':0.0}]

        #short record two bad obs missing big bgvar
        vals18 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':9.0, 'OSTIA':5.0, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':9.0, 'OSTIA':5.0, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':4.0, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':None, 'BGVAR':4.0, 'ICE':0.0}]

        #good data
        vals19 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #assertion error - bad input parameter
        vals20 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #assertion error - missing matched value
        vals21 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #assertion error - invalid ice value
        vals22 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':1.1},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #assertion error - missing observation value
        vals23 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #assertion error - times not sorted
        vals24 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        #assertion error - invalid background sst
        vals25 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':46.0, 'BGVAR':0.01, 'ICE':0.0}]

        #assertion error - invalid background error variance
        vals26 = [{'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.0, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.1, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.2, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.3, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':-0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.4, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.5, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.6, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.7, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0},
                 {'ID':'AAAAAAAAA', 'YR':2003, 'MO':12, 'DY':1, 'HR':0.8, 'LAT':0.0, 'LON':0.0, 'SST':5.0, 'OSTIA':5.0, 'BGVAR':0.01, 'ICE':0.0}]

        self.reps1 = ex.Voyage()
        self.reps2 = ex.Voyage()
        self.reps3 = ex.Voyage()
        self.reps4 = ex.Voyage()
        self.reps5 = ex.Voyage()
        self.reps6 = ex.Voyage()
        self.reps7 = ex.Voyage()
        self.reps8 = ex.Voyage()
        self.reps9 = ex.Voyage()
        self.reps10 = ex.Voyage()
        self.reps11 = ex.Voyage()
        self.reps12 = ex.Voyage()
        self.reps13 = ex.Voyage()
        self.reps14 = ex.Voyage()
        self.reps15 = ex.Voyage()
        self.reps16 = ex.Voyage()
        self.reps17 = ex.Voyage()
        self.reps18 = ex.Voyage()
        self.reps19 = ex.Voyage()
        self.reps20 = ex.Voyage()
        self.reps21 = ex.Voyage()
        self.reps22= ex.Voyage()
        self.reps23= ex.Voyage()
        self.reps24= ex.Voyage()
        self.reps25= ex.Voyage()
        self.reps26= ex.Voyage()

        for v in vals1:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps1.add_report(rep)

        for v in vals2:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps2.add_report(rep)

        for v in vals3:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps3.add_report(rep)

        for v in vals4:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps4.add_report(rep)

        for v in vals5:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps5.add_report(rep)

        for v in vals6:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps6.add_report(rep)

        for v in vals7:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps7.add_report(rep)

        for v in vals8:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps8.add_report(rep)

        for v in vals9:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps9.add_report(rep)

        for v in vals10:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps10.add_report(rep)

        for v in vals11:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps11.add_report(rep)

        for v in vals12:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps12.add_report(rep)

        for v in vals13:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps13.add_report(rep)

        for v in vals14:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps14.add_report(rep)

        for v in vals15:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps15.add_report(rep)

        for v in vals16:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps16.add_report(rep)
 
        for v in vals17:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps17.add_report(rep)

        for v in vals18:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps18.add_report(rep)

        for v in vals19:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps19.add_report(rep)

        for v in vals20:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps20.add_report(rep)

        for v in vals21:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            #rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps21.add_report(rep)

        for v in vals22:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps22.add_report(rep)

        for v in vals23:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps23.add_report(rep)
        self.reps23.setvar(1,'LAT',None)

        for v in vals24:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps24.add_report(rep)

        for v in vals25:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps25.add_report(rep)

        for v in vals26:
            rec = IMMA()
            for key in v:
                if not key in ['OSTIA','BGVAR','ICE']:
                    rec.data[key] = v[key]
            rep = ex.MarineReportQC(rec)
            rep.setext('OSTIA', v['OSTIA'])
            rep.setext('BGVAR', v['BGVAR'])
            rep.setext('ICE', v['ICE'])
            self.reps26.add_report(rep)

    def tearDown(self):
        
        del self.reps1
        del self.reps2
        del self.reps3
        del self.reps4
        del self.reps5
        del self.reps6
        del self.reps7
        del self.reps8
        del self.reps9
        del self.reps10
        del self.reps11
        del self.reps12
        del self.reps13
        del self.reps14
        del self.reps15
        del self.reps16
        del self.reps17
        del self.reps18
        del self.reps19
        del self.reps20
        del self.reps21
        del self.reps22
        del self.reps23
        del self.reps24
        del self.reps25
        del self.reps26

    def test_all_daytime(self):
        expected_flags={'drf_bias':[0,0,0,0,0,0,0,0,0],
                        'drf_noise':[0,0,0,0,0,0,0,0,0],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps1.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps1)):
            self.assertEqual(self.reps1.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps1.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps1.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_all_land_masked(self):
        expected_flags={'drf_bias':[0,0,0,0,0,0,0,0,0],
                        'drf_noise':[0,0,0,0,0,0,0,0,0],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps2.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps2)):
            self.assertEqual(self.reps2.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps2.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps2.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_all_ice(self):
        expected_flags={'drf_bias':[0,0,0,0,0,0,0,0,0],
                        'drf_noise':[0,0,0,0,0,0,0,0,0],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps3.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps3)):
            self.assertEqual(self.reps3.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps3.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps3.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_all_bgvar_exceeds_limit(self):
        expected_flags={'drf_bias':[0,0,0,0,0,0,0,0,0],
                        'drf_noise':[0,0,0,0,0,0,0,0,0],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps4.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps4)):
            self.assertEqual(self.reps4.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps4.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps4.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_biased_warm(self):
        expected_flags={'drf_bias':[1,1,1,1,1,1,1,1,1],
                        'drf_noise':[0,0,0,0,0,0,0,0,0],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps5.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps5)):
            self.assertEqual(self.reps5.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps5.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps5.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_biased_cool(self):
        expected_flags={'drf_bias':[1,1,1,1,1,1,1,1,1],
                        'drf_noise':[0,0,0,0,0,0,0,0,0],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps6.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps6)):
            self.assertEqual(self.reps6.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps6.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps6.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_noisy(self):
        expected_flags={'drf_bias':[0,0,0,0,0,0,0,0,0],
                        'drf_noise':[1,1,1,1,1,1,1,1,1],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps7.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps7)):
            self.assertEqual(self.reps7.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps7.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps7.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_biased_and_noisy(self):
        expected_flags={'drf_bias':[1,1,1,1,1,1,1,1,1],
                        'drf_noise':[1,1,1,1,1,1,1,1,1],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps8.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps8)):
            self.assertEqual(self.reps8.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps8.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps8.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_biased_warm_obs_missing(self):
        expected_flags={'drf_bias':[1,1,1,1,1,1,1,1,1],
                        'drf_noise':[0,0,0,0,0,0,0,0,0],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps9.reps,5,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps9)):
            self.assertEqual(self.reps9.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps9.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps9.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_short_record_one_bad(self):
        expected_flags={'drf_bias':[0,0,0,0,0],
                        'drf_noise':[0,0,0,0,0],
                        'drf_short':[0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps10.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps10)):
            self.assertEqual(self.reps10.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps10.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps10.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_short_record_two_bad(self):
        expected_flags={'drf_bias':[0,0,0,0,0],
                        'drf_noise':[0,0,0,0,0],
                        'drf_short':[1,1,1,1,1]}
        tqc.sst_biased_noisy_check(self.reps11.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps11)):
            self.assertEqual(self.reps11.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps11.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps11.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_short_record_two_bad_obs_missing(self):
        expected_flags={'drf_bias':[0,0,0,0,0,0,0,0,0],
                        'drf_noise':[0,0,0,0,0,0,0,0,0],
                        'drf_short':[1,1,1,1,1,1,1,1,1]}
        tqc.sst_biased_noisy_check(self.reps12.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps12)):
            self.assertEqual(self.reps12.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps12.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps12.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_short_record_two_bad_obs_missing_with_bgvar(self):
        expected_flags={'drf_bias':[0,0,0,0,0,0,0,0,0],
                        'drf_noise':[0,0,0,0,0,0,0,0,0],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps13.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps13)):
            self.assertEqual(self.reps13.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps13.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps13.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_good_data(self):
        expected_flags={'drf_bias':[0,0,0,0,0,0,0,0,0],
                        'drf_noise':[0,0,0,0,0,0,0,0,0],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps14.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps14)):
            self.assertEqual(self.reps14.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps14.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps14.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_short_record_good_data(self):
        expected_flags={'drf_bias':[0,0,0,0,0],
                        'drf_noise':[0,0,0,0,0],
                        'drf_short':[0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps15.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps15)):
            self.assertEqual(self.reps15.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps15.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps15.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_short_record_obs_missing_good_data(self):
        expected_flags={'drf_bias':[0,0,0,0,0,0,0,0,0],
                        'drf_noise':[0,0,0,0,0,0,0,0,0],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps16.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps16)):
            self.assertEqual(self.reps16.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps16.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps16.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_noisy_big_bgvar(self):
        expected_flags={'drf_bias':[0,0,0,0,0,0,0,0,0],
                        'drf_noise':[0,0,0,0,0,0,0,0,0],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps17.reps,9,1.10,1.0,0.29,3.0,2,4.0)
        for i in range(0, len(self.reps17)):
            self.assertEqual(self.reps17.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps17.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps17.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_short_record_two_bad_obs_missing_big_bgvar(self):
        expected_flags={'drf_bias':[0,0,0,0,0,0,0,0,0],
                        'drf_noise':[0,0,0,0,0,0,0,0,0],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps18.reps,9,1.10,1.0,0.29,3.0,2,4.0)
        for i in range(0, len(self.reps18)):
            self.assertEqual(self.reps18.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps18.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps18.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_good_data(self):
        expected_flags={'drf_bias':[0,0,0,0,0,0,0,0,0],
                        'drf_noise':[0,0,0,0,0,0,0,0,0],
                        'drf_short':[0,0,0,0,0,0,0,0,0]}
        tqc.sst_biased_noisy_check(self.reps19.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        for i in range(0, len(self.reps19)):
            self.assertEqual(self.reps19.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps19.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps19.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_error_bad_input_parameter(self):
        expected_flags={'drf_bias':[9,9,9,9,9,9,9,9,9],
                        'drf_noise':[9,9,9,9,9,9,9,9,9],
                        'drf_short':[9,9,9,9,9,9,9,9,9]}
        try:
            tqc.sst_biased_noisy_check(self.reps20.reps,0,1.10,1.0,0.29,3.0,2,0.3)
        except AssertionError as error:
            error_return_text='invalid input parameter: n_eval must be > 0'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps20)):
            self.assertEqual(self.reps20.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps20.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps20.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_error_missing_matched_value(self):
        expected_flags={'drf_bias':[9,9,9,9,9,9,9,9,9],
                        'drf_noise':[9,9,9,9,9,9,9,9,9],
                        'drf_short':[9,9,9,9,9,9,9,9,9]}
        try:
            tqc.sst_biased_noisy_check(self.reps21.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        except AssertionError as error:
            error_return_text='matched report value is missing: unknown extended variable name OSTIA'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps21)):
            self.assertEqual(self.reps21.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps21.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps21.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_error_invalid_ice_value(self):
        expected_flags={'drf_bias':[9,9,9,9,9,9,9,9,9],
                        'drf_noise':[9,9,9,9,9,9,9,9,9],
                        'drf_short':[9,9,9,9,9,9,9,9,9]}
        try:
            tqc.sst_biased_noisy_check(self.reps22.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        except AssertionError as error:
            error_return_text='matched ice proportion is invalid'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps22)):
            self.assertEqual(self.reps22.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps22.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps22.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_error_missing_ob_value(self):
        expected_flags={'drf_bias':[9,9,9,9,9,9,9,9,9],
                        'drf_noise':[9,9,9,9,9,9,9,9,9],
                        'drf_short':[9,9,9,9,9,9,9,9,9]}
        try:
            tqc.sst_biased_noisy_check(self.reps23.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        except AssertionError as error:
            error_return_text='problem with report value: latitude is missing'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps23)):
            self.assertEqual(self.reps23.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps23.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps23.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_error_not_time_sorted(self):
        expected_flags={'drf_bias':[9,9,9,9,9,9,9,9,9],
                        'drf_noise':[9,9,9,9,9,9,9,9,9],
                        'drf_short':[9,9,9,9,9,9,9,9,9]}
        try:
            tqc.sst_biased_noisy_check(self.reps24.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        except AssertionError as error:
            error_return_text='problem with report value: times are not sorted'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps24)):
            self.assertEqual(self.reps24.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps24.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps24.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_error_invalid_background(self):
        expected_flags={'drf_bias':[9,9,9,9,9,9,9,9,9],
                        'drf_noise':[9,9,9,9,9,9,9,9,9],
                        'drf_short':[9,9,9,9,9,9,9,9,9]}
        try:
            tqc.sst_biased_noisy_check(self.reps25.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        except AssertionError as error:
            error_return_text='matched background sst is invalid'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps25)):
            self.assertEqual(self.reps25.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps25.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps25.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    def test_error_invalid_background_error_variance(self):
        expected_flags={'drf_bias':[9,9,9,9,9,9,9,9,9],
                        'drf_noise':[9,9,9,9,9,9,9,9,9],
                        'drf_short':[9,9,9,9,9,9,9,9,9]}
        try:
            tqc.sst_biased_noisy_check(self.reps26.reps,9,1.10,1.0,0.29,3.0,2,0.3)
        except AssertionError as error:
            error_return_text='matched background error variance is invalid'
            self.assertEqual(str(error)[0:len(error_return_text)],error_return_text)
        for i in range(0, len(self.reps26)):
            self.assertEqual(self.reps26.get_qc(i,'SST','drf_bias'), expected_flags['drf_bias'][i])
            self.assertEqual(self.reps26.get_qc(i,'SST','drf_noise'), expected_flags['drf_noise'][i])
            self.assertEqual(self.reps26.get_qc(i,'SST','drf_short'), expected_flags['drf_short'][i])

    # tests summary
    '''
    + all daytime
    + all land masked
    + all ice
    + all bgvar exceeds limit
    + long record biased warm
    + long record biased cool
    + long record noisy
    + long record biased and noisy
    + long record biased (obs missing)
    + short record one bad (no fail)
    + short record two bad
    + short record two bad (obs missing)
    + short record two bad bgvar short circuit
    + good data
    + short record good data
    + short record good data obs missing
    + long record noisy big bgvar
    + short record two bad (obs missing) big bgvar
    + long record good data
    + assertion error - bad input parameter
    + assertion error - missing matched value
    + assertion error - missing ob value
    + assertion error - invalid ice value
    + assertion error - data not time-sorted
    + assertion error - invalid background sst
    + assertion error - invalid background error
    '''

if __name__ == '__main__':
    unittest.main()
