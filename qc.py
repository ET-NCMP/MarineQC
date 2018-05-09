'''
The QC module contains a set of functions for performing the basic QC 
checks on marine reports as well as some generally helpful functions 
for identifying which grid box or pentad an observations falls in
'''

import numpy as np
import math
import sys
from datetime import datetime
import calendar
import spherical_geometry as sph
import csv

class MarineReport:
    
    '''
    Class is an object for storing marine reports, containing information needed for the :term:`QC`. Coded items 
    like ds and vs are automatically converted 
    to appropriate units (degrees and knots respectively) and stored internally as dsi and vsi. The class also has 
    attributes to store QC flags and climatological averages of SST and MAT. Marine reports in a list can be sorted 
    into time order using the list sort function.
    '''
    
    def __init__(self, shipid, lat, lon, sst, mat, year, \
                 month, day, hour, icoads_ds, icoads_vs, uid):

        '''
        Create a marine report.
        
        :param id: The 9-digit ID of the report, often the ship's callsign
        :param lat: The latitude of the report in degrees
        :param lon: the longitude of the report in degrees
        :param sst: the reported sea-surface temperature in degrees C
        :param mat: the reported air temperature in degrees C
        :param year: the year of the report
        :param month: the month of the report
        :param day: the day of the report
        :param hour: the hour of the report coded as a float from 0.0 to 23.99
        :param ds: the ship's heading in IMMA codes 0-9
        :param vs: the ship's speed in IMMA codes 
        :param uid: string the uniquely identifies the report
        :type id: string
        :type lat: float
        :type lon: float
        :type sst: float
        :type mat: float
        :type year: integer 
        :type month: integer
        :type day: integer
        :type hour: float
        :type ds: integer
        :type vs: integer
        :type uid: string
        
        Marine reports can in created using this function. All the elements can be set to None if missing. ds and vs are 
        converted internally to dsi and vsi in degrees and knots respectively using the IMMA look up tables. An internal 
        dtime variable is set up which is used to order observations when sorted.
        '''
        
        ds_convert = [0, 45, 90, 135, 180, 225, 270, 315, 360, None]
        
        self.id = shipid
        self.uid = uid
        
        self.lat = lat
        self.lon = lon
        self.sst = sst
        self.mat = mat
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        
        if calendar.isleap(year):
            month_lengths = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        if (hour != None and 
            day != None and 
            day > 0 and day <= month_lengths[month-1]):
            self.rounded_hour = int(math.floor(hour))
            self.rounded_minute = int(math.floor(60 * (hour-self.rounded_hour)))
            self.dt = datetime(year, month, int(day), \
                               self.rounded_hour, self.rounded_minute)
        else:
            self.rounded_hour = None
            self.rounded_minute = None        
            self.dt = None

        self.ds = icoads_ds
        self.dsi = None
        if icoads_ds != None:
            self.dsi = ds_convert[icoads_ds]

        self.vs = icoads_vs
        self.vsi = None
        if icoads_vs != None:
            if year >= 1968:
                self.vsi = icoads_vs * 5.0 - 2.0
            else:
                self.vsi = icoads_vs * 3.0 - 1.0
            if icoads_vs == 0:
                self.vsi = 0.0

        self.pt = None
        self.si = None
        self.c1 = None
        self.dck = None
        self.sid = None
        
        self.sst_norm = None
        self.sst_anomaly = None

        self.mat_norm = None
        self.mat_anomaly = None

#basic QC
        self.bad_date = 0
        self.blacklist = 0
        self.bad_position = 0
        self.bad_time = 0
        self.bad_track = 0
        self.land = 0
        self.day_check = 0
        self.fewsome_check = 0

        self.no_sst = 0
        self.sst_below_freezing = 0
        self.no_sst_normal = 0
        self.sst_climatology_fail = 0
        self.sst_buddy_fail = 0

        self.no_mat = 0
        self.no_mat_normal = 0
        self.mat_climatology_fail = 0
        self.mat_buddy_fail = 0
        
        self.new_track_check = 0 
        self.new_buddy_check = 0 
        self.bayesian_sst_buddy_check = 0 
        self.bayesian_mat_buddy_check = 0 
        self.bayesian_track_check = 0 
        self.spike_check = 0 
        self.iquam_spike_check = 0 
        self.repeated_value = 0 
 
        return
    
    def getvar(self, var):
        '''
        Get variable name
        
        :param var: variable name
        :type var: string
        :return: variable corresponding to variable name
        :rtype: depends on variable, float or string
        '''
        if var == 'LAT': return self.lat
        if var == 'LON': return self.lon
        if var == 'YR': return self.year 
        if var == 'MO': return self.month
        if var == 'DY': return self.day
        if var == 'HR': return self.hour
        if var == 'SST': return self.sst 
        if var == 'AT': return self.mat 

        #if var == '': return 
        
        return 
    
    def getanom(self, var):
        
        if var == 'SST': return self.sst_anomaly
        if var == 'AT':  return self.mat_anomaly
    
    def set_qc(self, qc_type, specific_flag, set_value):
    
        if qc_type == 'AT':
            if specific_flag == 'buddy_fail':
                self.mat_buddy_fail = set_value

        if qc_type == 'SST':
            if specific_flag == 'buddy_fail':
                self.sst_buddy_fail = set_value
#            elif specific_flag == '':
#                pass
#            elif specific_flag == '':
#                pass
#            elif specific_flag == '':
#                pass

        return

    def get_qc(self, qc_type, specific_flag):
    
        if qc_type == 'AT':
            if specific_flag == 'buddy_fail':
                qcvalue = self.mat_buddy_fail

        if qc_type == 'SST':
            if specific_flag == 'buddy_fail':
                qcvalue = self.sst_buddy_fail
#            elif specific_flag == '':
#                pass
#            elif specific_flag == '':
#                pass
#            elif specific_flag == '':
#                pass

        return qcvalue
    
    @staticmethod
    def report_from_imma(imma):
        '''
        Create a MarineReport from an IMMA report
        
        :param x: IMMA report
        :type x: IMMA report
        :return: MarineReport created from IMMA report
        :rtype: MarineReport
        '''
        rep = MarineReport(imma.data['ID'],
                           imma.data['LAT'], imma.data['LON'], 
                           imma.data['SST'], imma.data['AT'], 
                           imma.data['YR'], imma.data['MO'], 
                           imma.data['DY'], imma.data['HR'], 
                           imma.data['DS'], imma.data['VS'], 
                           str(imma.data['UID']))

        rep.pt = imma.data['PT']
        rep.si = imma.data['SI']
        rep.c1 = imma.data['C1']
        rep.dck = imma.data['DCK']
        rep.sid = imma.data['SID']

        return rep

    @staticmethod
    def report_from_array(x):
        '''
        Create a MarineReport from an array in a very specific order
        
        :param x: array containing variables needed to initialise MarineReport
        :type x: list
        :return: MarineReport created from input array
        :rtype: MarineReport
        '''
        
        id = "{:9.9}".format(x[0])

        rep = MarineReport(str(x[0]),
                           x[1], x[2], 
                           x[3], x[4], 
                           x[5], x[6], 
                           x[7], x[8], 
                           x[9], x[10], 
                           str(x[11]))

        rep.pt = x[12]
        rep.si = x[13]
        rep.c1 = x[14]
        rep.dck = x[15]
        rep.sid = x[16]
        
        rep.setnorm(x[17], x[18])

        return rep


    def print_report(self):
        '''
        A simple routine to print out the marine report in the old fashioned tenday format 
        for comparison to earlier versions of the :term:`MDS` QC system.
        '''
        #callsign,lat,lon,year,month,day,hour,mat,sst,pressure,
        #wind,deckid,sourceid,obtype,qc1,qc2,qc3,qc4,qc5
        #'(a8,12i8,i3,2x,a8,4(x,a8))'
   
        mat = self.mat
        if mat == None:
            mat = -32768
        else:
            mat = round(self.mat * 10)
        
        sst = self.sst
        if sst == None:
            sst = -32768
        else:
            sst = round(self.sst * 10)
        
        day = self.day
        if day == None:
            day = -32768
        
        hur = self.hour
        if hur == None:
            hur = -32768
        else:
            hur = int(self.hour * 100)
        
        sid = self.sid
        duplicate = 0
        pressure = -32768
        obtype = 2
        if self.pt == 6:
            obtype = 1
        elif self.pt == 7:
            obtype = 0
        
        dsvs = 9999
        if self.ds != None and self.vs != None:
            dsvs = (self.ds*100+self.vs)
        
        lon = round(self.lon*100, 0)
        if lon > 18000:
            lon = lon-36000
        
        shipid = self.id
        if shipid == None:
            shipid = '         '
        
        qc_block = "{:d}{:d}{:d}{:d}{:d}{:d}{:d}{:d} "
        qc_end = "{:d}{:d}{:d}{:d}{:d}{:d}{:d}{:d}\n"
        
        repout = "{:8.8}".format(shipid)
        repout = repout + "{:8d}".format(int(round(self.lat*100, 0)))
        repout = repout + "{:8d}".format(int(lon))
        repout = repout + "{:8d}".format(self.year)
        repout = repout + "{:8d}".format(self.month)
        repout = repout + "{:8d}".format(day)
        repout = repout + "{:8d}".format(hur)
        repout = repout + "{:8d}".format(int(mat))
        repout = repout + "{:8d}".format(int(sst))
        repout = repout + "{:8d}".format(pressure)
        repout = repout + "{:8d}".format(dsvs)
        repout = repout + "{:8d}".format(self.dck)
        repout = repout + "{:8d}".format(sid)
        repout = repout + "{:3d}  ".format(obtype)
        repout = repout + qc_block.format(self.day_check, 
                                          self.land, 
                                          self.bad_track, 
                                          self.bad_time, 
                                          self.bad_time, 
                                          self.bad_position, 
                                          self.blacklist, 
                                          duplicate)
        repout = repout + qc_block.format(self.sst_buddy_fail, 
                                          self.sst_climatology_fail, 
                                          self.no_sst_normal, 
                                          self.sst_below_freezing, 
                                          self.no_sst, 
                                          0, 0, 0)
        repout = repout + qc_block.format(self.mat_buddy_fail, 
                                          self.mat_climatology_fail, 
                                          self.no_mat_normal, 
                                          0,
                                          self.no_mat,
                                          0, 0, 0)
        repout = repout + qc_block.format(0, 0, 0, 0, 0, 0, 0, 0)
        repout = repout + qc_end.format(self.fewsome_check, 
                                        self.new_track_check, 
                                        self.new_buddy_check, 
                                        self.bayesian_sst_buddy_check, 
                                        self.bayesian_mat_buddy_check, 
                                        0, 0, 0)
        
        return repout

    def __sub__(self, other):
        '''
        Subtracting one :class:`.MarineReport` from another will yield the distance and the time difference 
        between the two reports.
        
        Usage: distance, timediff = report_a - report_b
        '''
        distance = sph.sphere_distance(self.lat, self.lon,
                                       other.lat, other.lon)

        timediff = time_difference(other.year, other.month, 
                                   other.day, other.hour,
                                   self.year, self.month, 
                                   self.day, self.hour)
        speed = None
        if timediff != 0:
            speed = distance/timediff
        else:
            timediff = 0.0
            speed = distance

        course = sph.course_between_points(other.lat, other.lon, 
                                           self.lat, self.lon)


        return speed, distance, course, timediff

    def __eq__(self, other):
        if self.id == other.id and self.dt == other.dt:
            return True
        else:
            return False
    
    def __gt__(self, other):
        if self.id > other.id:
            return True
        if self.dt != None and other.dt != None and self.dt > other.dt:
            return True
        else:
            return False

    def __ge__(self, other):
        if self.id > other.id:
            return True
        if self.dt >= other.dt:
            return True
        else:
            return False
    
    def __le__(self, other):
        if self.id < other.id:
            return True
        if self.dt <= other.dt:
            return True
        else:
            return False

    def setnorm(self, sst_climav, mat_climav):

        '''
        Assign a climatological average to this report
        
        :param sst_climav: climatological SST in degC
        :param mat_climav: climatological MAT in degC
        :type sst_climav: float
        :type mat_climav: float
        
        A climatological average is assigned and, if non-missing, an anomaly is calculate and stored internally.
        '''
        
        self.sst_norm = sst_climav
        if sst_climav != None and self.sst != None:
            self.sst_anomaly = self.sst - sst_climav
        
        self.mat_norm = mat_climav
        if mat_climav != None and self.mat != None:
            self.mat_anomaly = self.mat - mat_climav

        return

    def printqc(self):

        '''
        Print current QC flags for the MarineReport
        '''

        print 'BASE QC', self.bad_date, self.blacklist, self.bad_position, \
        self.bad_time, self.bad_track, self.land, self.day_check, \
        ' SST QC', self.no_sst, self.no_sst_normal, self.sst_climatology_fail, \
        self.sst_buddy_fail,self.sst_below_freezing, \
        ' MAT QC', self.no_mat, self.no_mat_normal, self.mat_climatology_fail, \
        self.mat_buddy_fail    

        return
    
    def shift_day(self, shift):
        """
        Shift the day of the report forward or back one day.
        
        :param shift: set to 1 or -1 to shift forward or backward a day.
        :type shift: integer
        
        This is a simple function to push a day forward or backward exactly one day, 
        keeping everything else constant. This is necessary because some observations 
        in ICOADS are in the wrong day. This particularly affects Deck 201 and sundry 
        observations close to the dateline.                
        """
        assert shift == -1 or shift == 1
        
        mls = month_lengths(self.year)
        
        self.day += shift
        if self.day <= 0:
            self.month -= 1
            if self.month <= 0:
                self.year -= 1
                self.month = 12
            self.day += mls[self.month-1]
            
        if self.day > mls[self.month-1]:
            self.month += 1
            if self.month > 12:
                self.year += 1
                self.month = 1
            self.day = 1

#recompute dt
        if (self.hour != None and 
            self.day != None and 
            self.day > 0 and self.day <= mls[self.month-1]):
            self.rounded_hour = int(math.floor(self.hour))
            self.rounded_minute = int(math.floor(60 * (self.hour-self.rounded_hour)))
            self.dt = datetime(self.year, self.month, int(self.day), \
                               self.rounded_hour, self.rounded_minute)
        else:
            self.rounded_hour = None
            self.rounded_minute = None        
            self.dt = None

class ExtendedMarineReport(MarineReport):

    """
    The ExtendedMarineReport is just like a regular marine report 
    except it has a new attribute, ext. ext is just a dictionary 
    which can be accessed by a number of predefined keys. Its 
    intended for use in track checking and other QC tests where 
    reports are organised into voyages.
    """

    def __init__(self, shipid, lat, lon, sst, mat, year, \
                 month, day, hour, icoads_ds, icoads_vs, uid):
        
        MarineReport.__init__(self, shipid, lat, lon, sst, mat, year, \
                 month, day, hour, icoads_ds, icoads_vs, uid)
        
        self.ext_var = ['speed', 'alt_speed', 
                        'course', 'alt_course', 
                        'distance', 'alt_distance', 
                        'time_diff']
        self.ext = {}
        for v in self.ext_var:
            self.ext[v] = None

    
    @staticmethod
    def report_from_imma(imma):
        '''
        Create a MarineReport from an IMMA report
        
        :param x: IMMA report
        :type x: IMMA report
        :return: MarineReport created from IMMA report
        :rtype: MarineReport
        '''
        rep = ExtendedMarineReport(imma.data['ID'],
                                   imma.data['LAT'], imma.data['LON'], 
                                   imma.data['SST'], imma.data['AT'], 
                                   imma.data['YR'], imma.data['MO'], 
                                   imma.data['DY'], imma.data['HR'], 
                                   imma.data['DS'], imma.data['VS'], 
                                   str(imma.data['UID']))

        rep.pt = imma.data['PT']
        rep.si = imma.data['SI']
        rep.c1 = imma.data['C1']
        rep.dck = imma.data['DCK']
        rep.sid = imma.data['SID']

        return rep

    @staticmethod
    def report_from_array(x):
        '''
        Create a MarineReport from an array in a very specific order
        
        :param x: array containing variables needed to initialise MarineReport
        :type x: list
        :return: MarineReport created from input array
        :rtype: MarineReport
        '''
        rep = ExtendedMarineReport(str(x[0]),
                                   x[1], x[2], 
                                   x[3], x[4], 
                                   x[5], x[6], 
                                   x[7], x[8], 
                                   x[9], x[10], 
                                   str(x[11]))

        rep.pt = x[12]
        rep.si = x[13]
        rep.c1 = x[14]
        rep.dck = x[15]
        rep.sid = x[16]
        
        rep.setnorm(x[17], x[18])

        return rep

class Voyage:
    """
    A Voyage is a class which is effectively a list of ExtendedMarineReports. 
    There are a number of methods which can be used to do things like 
    sort the reports into time order, calculate speeds from the reported 
    positions and so on.
    """
    def __init__(self):
        self.reps = []
        
    def sort(self):
        """
        Sorts the reports into time order
        """
        self.reps.sort()
        #then recalculate times, speeds etc.
        if len(self.reps) > 1:
            for i in range(1, len(self.reps)):
                shpspd, shpdis, shpdir, tdiff = self.reps[i] - self.reps[i-1]
                self.reps[i].ext['speed'] = shpspd
                self.reps[i].ext['course'] = shpdir
                self.reps[i].ext['distance'] = shpdis
                self.reps[i].ext['time_diff'] = tdiff
        

    def get_latitudes(self):
        """
        Return a list containing the latitudes of all the reports
        
        :return: list of latitudes of the reports
        :rtype: float
        """
        lats = []
        for i in range(0, len(self.reps)):
            lats.append(self.reps[i].lat)
        return lats
    
    def get_longitudes(self):
        """
        Return a list containing the longitudes of all the reports
        
        :return: list of longitudes of the reports
        :rtype: float
        """
        lats = []
        for i in range(0, len(self.reps)):
            lats.append(self.reps[i].lon)
        return lats
    
    def get_speed(self):
        """
        Return a list containing the speeds of all the reports as 
        estimated from the positions of consecutive reports
        
        :return: list of speeds in km/hr
        :rtype: float
        """
        spd = []
        for i in range(0, len(self.reps)):
            spd.append(self.reps[i].ext['speed'])
        return spd
    
    def meansp(self):
        """
        Calculate the mean speed of the voyage based on speeds 
        estimated from the positions of consecutive reports.
        
        :return: mean voyage speed
        :rtype: float
        """
        spd = self.get_speed()

        if len(spd) > 1:
            amean = np.mean(spd[1:])
        else:
            amean = None

        return amean

    def add_report(self, rep):
        """
        Add a single ExtendedMarineReport to the voyage
        
        :param rep: ExtendedMarineReport to be added to the Voyage.
        :type rep: ExtendedMarineReport
        
        The report is added to the end of the Voyage and the ExtendedMarineReport 
        variables like speed and course are computed from the positions of the 
        report and the one that precedes it.
        """
        self.reps.append(rep)

        if len(self.reps) > 1:
            i = len(self.reps)
            shpspd, shpdis, shpdir, tdiff = self.reps[i-1] - self.reps[i-2]
            self.reps[i-1].ext['speed'] = shpspd
            self.reps[i-1].ext['course'] = shpdir
            self.reps[i-1].ext['distance'] = shpdis
            self.reps[i-1].ext['time_diff'] = tdiff

    def calc_alternate_speeds(self):
        """
        The speeds and courses can also be calculated using alternating reports
        """
        if len(self.reps) > 2:
            for i in range(1, len(self.reps)-1):
                shpspd, shpdis, shpdir, tdiff = self.reps[i+1] - self.reps[i-1]
                self.reps[i].ext['alt_speed'] = shpspd
                self.reps[i].ext['alt_course'] = shpdir
                self.reps[i].ext['alt_distance'] = shpdis
                self.reps[i].ext['alt_time_diff'] = tdiff

    def last_rep(self):
        """
        Get the last report in the Voyage
        
        :return: last ExtendedMarineReport in the Voyage
        :rtype: ExtendedMarineReport
        """
        nreps = len(self.reps)
        return self.reps[nreps-1]
                
    def predict_next_point(self, timediff):
        """
        The latitude and longitude of the next point are estimated based on 
        an extrapolation of the great circle drawn between the previous two 
        points
        
        :param timediff: predict the latitude and longitude after this timediff has elapsed.
        :type timediff: float
        """
        assert timediff >= 0
        nreps = len(self.reps)
        
        assert nreps > 0, "Need at least one report in the voyage to predict"
       
        if nreps == 1:
            return self.reps[0].lat, self.reps[0].lon

        if abs(self.reps[nreps-1].ext['time_diff']) < 0.00001:
            return self.reps[nreps-1].lat, self.reps[nreps-1].lon
            
        #take last-but-one and last point. Calculate a speed and 
        #great circle course from them.
        course = self.reps[nreps-1].ext['course']
        distance = (self.reps[nreps-1].ext['speed'] * 
                    (self.reps[nreps-1].ext['time_diff']+timediff))

        lat1 = self.reps[nreps-2].lat
        lon1 = self.reps[nreps-2].lon
     
        lat, lon = sph.lat_lon_from_course_and_distance(lat1, lon1, 
                                                        course, distance)

        return lat, lon
        
    def find_repeated_values(self, threshold=0.7, intype='SST'):
        """
        Find cases where more than a given proportion of SSTs have the same value
        
        :param threshold: the maximum fraction of observations that can have a given value
        :param intype: either 'SST' or 'MAT' to find repeated SSTs or MATs
        :type threshold: float
        :type intype: string
        
        This method goes through a voyage and finds any cases where more than a threshold fraction of 
        the observations have the same SST or NMAT value.
        """
        
        assert threshold >= 0.0 and threshold <= 1.0
        assert intype in ['SST','MAT']
        
        if intype == 'SST':
            valcount = {}
            allcount = 0
                    
            for i, rep in enumerate(self.reps):
                if rep.sst != None:
                    allcount += 1
                    if str(rep.sst) in valcount:
                        valcount[str(rep.sst)].append(i)
                    else:
                        valcount[str(rep.sst)]  = [i]
                        
            if allcount > 20:
                for key in valcount:
                    if float(len(valcount[key]))/float(allcount) > threshold:
                        for i in valcount[key]:
                            self.reps[i].repeated_value = 1
        
        if intype == 'MAT':
            valcount = {}
            allcount = 0
                    
            for i, rep in enumerate(self.reps):
                if rep.mat != None:
                    allcount += 1
                    if str(rep.mat) in valcount:
                        valcount[str(rep.mat)].append(i)
                    else:
                        valcount[str(rep.mat)]  = [i]
                        
            if allcount > 20:
                for key in valcount:
                    if float(len(valcount[key]))/float(allcount) > threshold:
                        for i in valcount[key]:
                            self.reps[i].repeated_value = 1
                            

        return 

def get_arguments(opts):
    """
    This is a simple function to parse the arguments passed to various of the QC routines
    
    :param opts: list of options
    :type opts: list of strings
    :return: name of input file, first year, last year, first month in first year, last month in last year
    :rtype: string, integer, integer, integer, integer
    """
    inputfile = 'configuration.txt'
    month1 = 1
    month2 = 12
    year1 = -999
    year2 = -999

    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-x", "--year1"):
            try:
                year1 = int(arg)
            except:
                sys.exit("Failed: year1 not an integer")
        elif opt in ("-y", "--year2"):
            try:
                year2 = int(arg)
            except:
                sys.exit("Failed: year2 not an integer")
        elif opt in ("-m", "--month1"):
            try:
                month1 = int(arg)
            except:
                sys.exit("Failed: month1 not an integer")
        elif opt in ("-n", "--month2"):
            try:
                month2 = int(arg)
            except:
                sys.exit("Failed: month2 not an integer")

    assert year1 != -999 and year2 != -999, "Year not specified."

    return inputfile, year1, year2, month1, month2
        
def get_config(filename='configuration.txt'):
    '''
    Get the contents of a configuration file
    
    :param filename: name and location of the file
    :type filename: str
    :return: dictionary containing the id of the config variable (key) and its value
    :rtype: dictionary
    '''
    config = {}
    
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            config[row[0]] = row[1]
    
    assert 'data_base_dir'  in config, "No data base directory specified"
    assert 'data_base_name' in config, "No data base name specified"
    assert 'ICOADS_dir'     in config, "No ICOADS directory specified"
    assert 'SST_climatology'       in config, "No SST climatology specified"
    assert 'MAT_climatology'       in config, "No MAT climatology specified"
    assert 'SST_stdev_climatology' in config, "No SST stdev climatology specified"
    
    return config

def pentad_to_month_day(p):
    '''
    Given a pentad number, return the month and day of the first day in the pentad    
    '''
    assert p > 0 and p<74, 'p outside allowed range 1-73 '+str(p)
    m = [1,1,1,1,1,1,1,2,2,2,2,2,
         3,3,3,3,3,3,4,4,4,4,4,4,
         5,5,5,5,5,5,5,6,6,6,6,6,6,
         7,7,7,7,7,7,8,8,8,8,8,8,
         9,9,9,9,9,9,10,10,10,10,10,10,
         11,11,11,11,11,11,12,12,12,12,12,12]
    d = [1, 6,11,16,21,26,31,5,10,15,20,25,2,7,12,17,22,
         27,1,6,11,16,21,26,1,6,11,16,21,26,31,5,10,15,20,
         25,30,5,10,15,20,25,30,4,9,14,19,24,29,3,8,13,18,
         23,28,3,8,13,18,23,28,2,7,12,17,22,27,2,7,12,17,22,27]  
    return m[p-1], d[p-1]

def which_pentad(inmonth, inday):
    '''
    take month and day as inputs and return pentad in range 1-73.
    
    :param inmonth: month containing the day for which we want to calculate the pentad
    :param inday: day for the day for which we want to calculate the pentad
    :type inmonth: integer
    :type inday: integer
    :return: pentad (5-day period) containing input day, from 1 (1 Jan-5 Jan) to 73 (27-31 Dec)
    :rtype: integer

    The calculation is rather simple. It just loops through the year and adds up days till it reaches 
    the day we are interested in. February 29th is treated as though it were March 1st in a regular year.
    '''
    assert inmonth <= 12 and inmonth >= 1
    assert inday <= 31 and inday >= 1

    pentad = (day_in_year(inmonth, inday)-1)/5
    pentad = pentad + 1

    assert pentad >= 1
    assert pentad <= 73
    
    return pentad

def day_in_year(month, day):
    '''
    Find the day number of a particular day from Jan 1st which is 1 
    to Dec 31st which is 365.
    
    :param month: month to be processed
    :param day: day in the month 
    :type month: integer
    :type day: integer
    :return: day number in year 1-365
    :rtype: integer
    '''
    assert month >= 1
    assert month <= 12,str(month)
    month_lengths = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    assert day >= 1
    assert day <= month_lengths[month-1]
    month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if month == 1:
        dindex = day
    elif month == 2 and day == 29:
        dindex = day_in_year(3, 1)
    else:
        dindex = np.sum(month_lengths[0:month-1]) + day

    return dindex

def get_hires_sst(lat, lon, month, day, hires_field):

    assert lat >= -90.0
    assert lat <= 90.0
    assert lon >= -180.00
    assert lon <= 360.00
    assert month >= 1
    assert month <= 12
    month_lengths = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    assert day >= 1
    assert day <= month_lengths[month-1]
    
    dindex = day_in_year(month, day) - 1
    yindex = lat_to_yindex(lat, 0.25)
    xindex = lon_to_xindex(lon, 0.25)
    
    result = hires_field[dindex, 0, yindex, xindex]

    if result == -999:
        result = None

    return result

def get_sst_daily(lat, lon, month, day, sst):
    '''
    Get SST from pentad climatology interpolated to day
    '''
    assert lat >= -90.0
    assert lat <= 90.0
    assert lon >= -185.00
    assert lon <= 365.00
    assert month >= 1
    assert month <= 12
    month_lengths = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]   
    assert day >= 1
    assert day <= month_lengths[month-1]

    dindex = day_in_year(month, day) - 1
    yindex = mds_lat_to_yindex(lat)
    xindex = mds_lon_to_xindex(lon)
    
    result = sst[dindex, yindex, xindex]

    if type(result) is np.float64 or type(result) is np.float32:
        pass
    else:
        if result.mask:
            result = None
        else:
            result = result.data[0]

    return result

def get_sst(lat, lon, month, day, sst):
    
    '''
    when given an array (sst) of appropriate type, extracts the value associated with that pentad, 
    latitude and longitude.
    
    :param lat: latitude of the point
    :param lon: longitude of the point
    :param month: month of the point
    :param day: day of the point
    :param sst: an array holding the 1x1x5-day gridded values
    :type lat: float
    :type lon: float
    :type month: integer
    :type day: integer
    :type sst: numpy array
    :return: value in array at this point
    :rtype: float
    
    The structure of the SST array has to be quite specific it assumes a grid that is 360 x 180 x 73 
    i.e. one year of 1degree lat x 1degree lon data split up into pentads. The west-most box is at 180degrees with index 0
    and the northern most box also has index zero.
    '''
    assert lat >= -90.0
    assert lat <= 90.0
    assert lon >= -185.00
    assert lon <= 365.00
    assert month >= 1
    assert month <= 12
    
    month_lengths = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    assert day >= 1
    assert day <= month_lengths[month-1]

    if len(sst[:,0,0]) == 1:
        result = get_sst_single_field(lat, lon, sst)
    else:
    
        #read sst from grid
        pentad = which_pentad(month, day)
        yindex = lat_to_yindex(lat)
        xindex = lon_to_xindex(lon)
    
        result = sst[pentad-1, yindex, xindex]
    
    #sometimes this will be a numpy array and sometimes it will 
    #be a masked array. Need to identify which and 
    #make sure output is appropriate
        if type(result) is np.float64 or type(result) is np.float32:
            pass
        else:
            if result.mask:
                result = None
            else:
                result = result.data[0]

    return result

def get_hires_clim(rep, clim):
    '''
    Get the climatological value for this particular observation
    
    :param rep: a MarineReport
    :param clim: a masked array containing the climatological averages
    :type rep: MarineReport
    :type clim: numpy array
    '''
    try: 
        rep_clim = get_hires_sst(rep.lat(), 
                                 rep.lon(), 
                                 rep.getvar('MO'),
                                 rep.getvar('DY'), 
                                 clim)
        rep_clim = float(rep_clim)
    except:
        rep_clim = None

    return rep_clim

def bilinear_interp(x1, x2, y1, y2, x, y, Q11, Q12, Q21, Q22):
    '''
    Perform a bilinear interpolation at the point x,y from the rectangular grid 
    defined by x1,y1 and x2,y2 with values at the four corners equal to Q11, Q12, 
    Q21 and Q22.
    '''

    assert x >= x1 and x <= x2
    assert y >= y1 and y <= y2
    assert x2 > x1
    assert y2 > y1
    assert Q11 != None and Q12 != None and Q21 != None and Q22 != None
    
    val =  Q11 * (x2 -  x) * (y2 - y)
    val += Q21 * (x  - x1) * (y2 - y)
    val += Q12 * (x2 -  x) * (y  - y1)
    val += Q22 * (x  - x1) * (y  - y1)
    val /= (x2 - x1) * (y2 - y1)
    
    assert val <=  0.0001+max([Q11, Q12, Q21, Q22]), \
    str(val)+' '+str(Q11)+' '+str(Q12)+' '+str(Q21)+' '+str(Q22)
    assert val >= -0.0001+min([Q11, Q12, Q21, Q22]), \
    str(val)+' '+str(Q11)+' '+str(Q12)+' '+str(Q21)+' '+str(Q22)
    return val

def missing_mean(inarr):
    result = 0.0
    num = 0.0
    for val in inarr:
        if val != None:
            result += val
            num += 1.0
    if num == 0.0:
        return None
    else:
        return result/num

def fill_missing_vals(Q11, Q12, Q21, Q22):
    '''
    For a group of four neighbouring grid boxes which form a square, 
    fill gaps using means of neighbours
    '''
    outQ11 = Q11
    outQ12 = Q12
    outQ21 = Q21
    outQ22 = Q22

    if outQ11 == None:
        outQ11 = missing_mean([Q12, Q21])
    if outQ11 == None:
        outQ11 = Q22

    if outQ22 == None:
        outQ22 = missing_mean([Q12, Q21])
    if outQ22 == None:
        outQ22 = Q11

    if outQ12 == None:
        outQ12 = missing_mean([Q11, Q22])
    if outQ12 == None:
        outQ12 = Q21

    if outQ21 == None:
        outQ21 = missing_mean([Q11, Q22])
    if outQ21 == None:
        outQ21 = Q12

    return outQ11, outQ12, outQ21, outQ22

def get_four_surrounding_points(lat, lon, max90=1):

    assert lat >= -90.0 and lat <= 90.0
    assert lon >= -180.0 and lon <= 180.0

    x2_index = lon_to_xindex(lon+0.5)
    x2       = xindex_to_lon(x2_index)
    if x2 < lon:
        x2 += 360.

    x1_index = lon_to_xindex(lon-0.5)
    x1       = xindex_to_lon(x1_index)
    if x1 > lon:
        x1 -= 360.

    if lat+0.5 <= 90:
        y2_index = lat_to_yindex(lat+0.5)
        y2       = yindex_to_lat(y2_index)
    else:
        y2 = 89.5
        if max90 == 0:
            y2 = 90.5

    if lat-0.5 >= -90:
        y1_index = lat_to_yindex(lat-0.5)
        y1       = yindex_to_lat(y1_index)
    else:
        y1 = -89.5
        if max90 == 0:
            y1 = -90.5

    return x1, x2, y1, y2

def get_clim_interpolated(rep, clim):

    lat = rep.lat()
    lon = rep.lon()
    mo = rep.getvar('MO')
    dy = rep.getvar('DY')

    try:
        pert1 = get_sst(lat+0.001, lon+0.001, mo, dy, clim)
    except:
        pert1 = None
    try:
        pert2 = get_sst(lat+0.001, lon-0.001, mo, dy, clim)
    except:
        pert2 = None
    try:
        pert3 = get_sst(lat-0.001, lon+0.001, mo, dy, clim)
    except:
        pert3 = None
    try:
        pert4 = get_sst(lat-0.001, lon-0.001, mo, dy, clim)
    except:
        pert4 = None
    if (pert1 == None and pert2 == None and 
        pert3 == None and pert4 == None):
        return None
    
    x1, x2, y1, y2 = get_four_surrounding_points(lat, lon, 1)   

    try:
        Q11 = get_sst(y1, x1, mo, dy, clim)
    except:
        Q11 = None
    if Q11 != None:
        Q11 = float(Q11)

    try:
        Q22 = get_sst(y2, x2, mo, dy, clim)
    except:
        Q22 = None
    if Q22 != None:
        Q22 = float(Q22)

    try:
        Q12 = get_sst(y2, x1, mo, dy, clim)
    except:
        Q12 = None
    if Q12 != None:
        Q12 = float(Q12)

    try:
        Q21 = get_sst(y1, x2, mo, dy, clim)
    except:
        Q21 = None
    if Q21 != None:
        Q21 = float(Q21)

    Q11,Q12,Q21,Q22 = fill_missing_vals(Q11,Q12,Q21,Q22)

    x1, x2, y1, y2 = get_four_surrounding_points(lat, lon, 0)   

    return bilinear_interp(x1, x2, y1, y2,
                           lon, lat,
                           Q11, Q12, Q21, Q22)

def get_clim(rep, clim):
    '''
    Get the climatological value for this particular observation
    
    :param rep: a MarineReport
    :param clim: a masked array containing the climatological averages
    :type rep: MarineReport
    :type clim: numpy array
    '''
    try: 
        rep_clim = get_sst(rep.lat(), rep.lon(), 
                           rep.getvar('MO'),
                           rep.getvar('DY'), 
                           clim)
        rep_clim = float(rep_clim)
    except:
        rep_clim = None

    return rep_clim

def get_sst_single_field(lat, lon, sst):

    '''
    when given an array (sst) of appropriate type, extracts the value associated with that pentad, 
    latitude and longitude.
    
    :param lat: latitude of the point
    :param lon: longitude of the point
    :param month: month of the point
    :param day: day of the point
    :param sst: an array holding the 1x1x5-day gridded values
    :type lat: float
    :type lon: float
    :type month: integer
    :type day: integer
    :type sst: numpy array
    :return: value in array at this point
    :rtype: float
    
    The structure of the SST array has to be quite specific it assumes a grid that is 360 x 180 x 73 
    i.e. one year of 1degree lat x 1degree lon data split up into pentads. The west-most box is at 180degrees with index 0
    and the northern most box also has index zero.
    '''
    assert lat >= -90.0
    assert lat <= 90.0
    assert lon >= -180.00
    assert lon <= 360.00
    
    #read sst from grid
    yindex = lat_to_yindex(lat)
    xindex = lon_to_xindex(lon)

    result = sst[0, yindex, xindex]

#sometimes this will be a numpy array and sometimes it will 
#be a masked array. Need to identify which and 
#make sure output is appropriate
    if type(result) is np.float64 or type(result) is np.float32:
        pass
    else:
        if result.mask:
            result = None
        else:
            result = result.data[0]

    return result

def blacklist(inid, indeck, inyear, inmonth, inlat, inlon, inpt=1):
    '''
    Blacklisting of observations from Deck 732 and others as needed
    
    :param inid: ID of the report
    :param indeck: Deck of the report
    :param inyear: year of the report
    :param inlat: latitude of the report
    :param inlon: longitude of the report
    :type inid: string
    :type indeck: integer
    :type inyear: integer
    :type inlat: float
    :type inlon: float
    
    If the report is from Deck 732, compares the observations year and location to a table of pre-identified 
    regions in which Deck 732 observations are known to be dubious - see Rayner et al. 2006 and Kennedy et al. 
    2011b. Observations at 0 degrees latitude 0 degrees longitude are blacklisted as this is a common error. 
    C-MAN stations with platform type 13 are blacklisted. SEAS data from deck 874 are unreliable (SSTs were 
    often in excess of 50degC) and so the deck was removed.
    '''
    
    if inlon > 180.0:
        inlon -= 360

    result = 0
    
    if inlat == 0.0 and inlon == 0.0:
        result = 1 #blacklist all obs at 0,0
    
    if inpt != None and inpt == 13:
        result = 1 #C-MAN data

    if inid == 'SUPERIGORINA':
        result = 1
    
    #these are the definitions of the regions which are blacklisted for Deck 732
    region = {}
    region[1]  = [-175,  40, -170,  55]
    region[2]  = [-165,  40, -160,  60]
    region[3]  = [-145,  40, -140,  50]
    region[4]  = [-140,  30, -135,  40]
    region[5]  = [-140,  50, -130,  55]
    region[6]  = [ -70,  35,  -60,  40]
    region[7]  = [ -50,  45,  -40,  50]
    region[8]  = [   5,  70,   10,  80]
    region[9]  = [   0, -10,   10,   0]
    region[10] = [ -30, -25,  -25, -20]
    region[11] = [ -60, -50,  -55, -45]
    region[12] = [  75, -20,   80, -15]
    region[13] = [  50, -30,   60, -20]
    region[14] = [  30, -40,   40, -30]
    region[15] = [  20,  60,   25,  65]
    region[16] = [   0, -40,   10, -30]
    region[17] = [-135,  30, -130,  40]

    #this dictionary contains the regions that are to be excluded for this year
    year_to_regions = {}
    year_to_regions[1958] = [1, 2, 3, 4, 5, 6, 14, 15]
    year_to_regions[1959] = [1, 2, 3, 4, 5, 6, 14, 15]
    year_to_regions[1960] = [1, 2, 3, 5, 6, 9, 14, 15]
    year_to_regions[1961] = [1, 2, 3, 5, 6, 14, 15, 16]
    year_to_regions[1962] = [1, 2, 3, 5, 12, 13, 14, 15, 16]
    year_to_regions[1963] = [1, 2, 3, 5, 6, 12, 13, 14, 15, 16]
    year_to_regions[1964] = [1, 2, 3, 5, 6, 12, 13, 14, 16]
    year_to_regions[1965] = [1, 2, 6, 10, 12, 13, 14, 15, 16]
    year_to_regions[1966] = [1, 2, 6, 9, 14, 15, 16]
    year_to_regions[1967] = [1, 2, 5, 6, 9, 14, 15]
    year_to_regions[1968] = [1, 2, 3, 5, 6, 9, 14, 15]
    year_to_regions[1969] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15, 16]
    year_to_regions[1970] = [1, 2, 3, 4, 5, 6, 8, 9, 14, 15]
    year_to_regions[1971] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 14, 16]
    year_to_regions[1972] = [4, 7, 8, 9, 10, 11, 13, 16, 17]
    year_to_regions[1973] = [4, 7, 8, 10, 11, 13, 16, 17]
    year_to_regions[1974] = [4, 7, 8, 10, 11, 16, 17]

    if indeck == 732:
        if inyear in year_to_regions:
            regions_to_check = year_to_regions[inyear]
            for regid in regions_to_check:
                thisreg = region[regid]
                if (inlon >= thisreg[0] and 
                    inlon <= thisreg[2] and 
                    inlat >= thisreg[1] and 
                    inlat <= thisreg[3]):
                    result = 1

    if indeck == 874:
        result = 1 #SEAS data gets blacklisted

    if ((inyear == 2005 and inmonth == 11) or 
        (inyear == 2005 and inmonth == 12) or 
        (inyear == 2006 and inmonth == 1)):
        if inid in ["53521    ", "53522    ", "53566    ", "53567    ", 
                    "53568    ", "53571    ", "53578    ", "53580    ", 
                    "53582    ", "53591    ", "53592    ", "53593    ", 
                    "53594    ", "53595    ", "53596    ", "53599    ", 
                    "53600    ", "53601    ", "53602    ", "53603    ", 
                    "53604    ", "53605    ", "53606    ", "53607    ", 
                    "53608    ", "53609    ", "53901    ", "53902    "]:
            result = 1

    return result

def climatology_plus_stdev_check(inval, inclimav, instdev, 
                                 stdev_limits, limit):
    '''
    Climatology check which uses standardised anomalies.
    
    :param inval: value to be compared to climatology
    :param inclimav: the climatological average to which the value will be compared
    :param instdev: the climatological standard deviation which will be used to standardise the anomaly
    :param stdev_limits: upper and lower limits for standard deviation used in check
    :param limit: the maximum allowed normalised anomaly
    :type inval: float
    :type inclimav: float
    :type instdev: float
    :type stdev_limits: two-membered list
    :type limit: float
    :return: return 1 if the difference is outside the specified limit, 0 otherwise (or if any input is None)
    :rtype: integer
    '''
    assert stdev_limits[1] > stdev_limits[0], "limits are awry"
    assert limit > 0, "multiplier must be positive and non-zero"

    result = 0
    if inval == None or inclimav == None or instdev == None:
        result = 1
    else:
        stdev = instdev
        if stdev < stdev_limits[0]: stdev = stdev_limits[0]
        if stdev > stdev_limits[1]: stdev = stdev_limits[1]

        if abs(inval-inclimav)/stdev > limit:
            result = 1

    assert result == 0 or result == 1

    return result

def climatology_check(inval, inclimav, limit=8.0):
    '''
    Simple function to compare a value with a climatological average with some arbitrary limit on the difference
    
    :param inval: value to be compared to climatology
    :param inclimav: the climatological average to which the value will be compared
    :param limit: the maximum allowed difference between the two
    :type inval: float
    :type inclimav: float
    :type limit: float
    :return: return 1 if the difference is outside the specified limit, 0 otherwise
    :rtype: integer
    
    This may be the second simplest function I have ever written (see blacklist)
    '''

    result = 0

    if inval == None or inclimav == None or limit == None:
        result = 1
    else:
        if abs(inval-inclimav) > limit:
            result = 1
    
    assert result == 0 or result == 1
    
    return result

def value_check(inval):
    '''
    Check if a value is equal to None
    
    :param inval: the input value
    :param inval: float
    :return: 1 if the input value is None, 0 otherwise
    :return type: integer
    '''
    result = 0
    if inval == None:
        result = 1
    return result

def no_normal_check(inclimav):
    '''
    Check if a climatological average is equal to None
    
    :param inclimav: the input value
    :type inclimav: float
    :return: 1 if the input value is None, 0 otherwise
    :return type: integer
    '''
    result = 0
    if inclimav == None:
        result = 1
    return result

def supersat_check(invaltd, invalt):
    '''
    Check if a valid dewpoint temperature is 
    greater than a valid air temperature
    
    :param invaltd: the input value for dewpoint temperature
    :param invalt: the input value for air temperature
    :type invaltd: float
    :type invalt: float
    :return: 1 if the input values are invalid/None
    :return: 1 if the dewpoint temperature is greater than the air temperarture 
    :return: 0 otherwise
    :return type: integer
    '''
    result = 0
    if ((invaltd == None) | (invalt == None)):
        result = 1
    elif (invaltd > invalt):
        result = 1
    
    return result

def sst_freeze_check(insst, sst_uncertainty=0.0, freezing_point=-1.80, n_sigma=2.0):
    '''
    Compare an input SST to see if it is above freezing.
    
    :param insst: the input SST
    :param sst_uncertainty: the uncertainty in the SST value, defaults to zero
    :param freezing_point: the freezing point of the water, defaults to -1.8C
    :type insst: float
    :type sst_uncertainty: float
    :type freezing_point: float
    :return: 1 if the input SST is below freezing point by more than twice the uncertainty, 0 otherwise
    :return type: integer
    
    This is a simple freezing point check made slightly more complex. We want to check if a 
    measurement of SST is above freezing, but there are two problems. First, the freezing point 
    can vary from place to place depending on the salinity of the water. Second, there is uncertainty 
    in SST measurements. If we place a hard cut-off at -1.8, then we are likely to bias the average 
    of many measurements too high when they are near the freezing point - observational error will 
    push the measurements randomly higher and lower, and this test will trim out the lower tail, thus 
    biasing the result. The inclusion of an SST uncertainty parameter *might* mitigate that.    
    '''
    
    assert sst_uncertainty != None and freezing_point != None
       
#fail if SST below the freezing point by more than twice the uncertainty
    result = 0
    if (insst != None):
        if insst < (freezing_point - n_sigma * sst_uncertainty):
            result = 1

    assert result == 1 or result == 0
    return result

def position_check(inlat, inlon):
    '''
    Simple check to make sure that the latitude and longitude are within the bounds specified 
    by the ICOADS documentation. Latitude is between -90 and 90. Longitude is between -180 and 360
    
    :param inlat: latitude
    :param inlon: longitude
    :type inlat: float
    :type inlon: float
    :return: 1 if either latitude or longitude is invalid, 0 otherwise
    :return type: integer
    '''
#return 1 if lat or lon is invalid, 0 otherwise
    assert inlat != None and not(math.isnan(inlat))
    assert inlon != None and not(math.isnan(inlon))
    result = 0
    if (inlat < -90 or inlat > 90):
        result = 1
    if (inlon <-180 or inlon > 360):
        result = 1
    assert result == 1 or result == 0
    return result

def time_check(inhour):
    '''
    Check that the time is valid
    
    :param inhour: hour of the time to be checked
    :type inhour: float
    :return: 1 if the hour is invalid, 0 otherwise
    :return type: integer
    '''   

    result = 0
    
    if (inhour != None and (inhour >= 24 or inhour < 0)):
        result = 1

    if (inhour == None):
        result = 1

    return result

def date_check(inyear, inmonth, inday):
    '''
    Check that the date is valid
    
    :param inyear: year of the date to be checked
    :param inmonth: month of the data to be checked
    :param inday: day of the date to be checked
    :param inhour: hour of the date and time to be checked
    :type inyear: integer
    :type inmonth: integer
    :type inday: integer
    :type inhour: float
    :return: 1 if any one of the inputs (or the combined inputs) is invalid, 0 otherwise
    :return type: integer
    '''
#return 1 if date is valid. 0 otherwise
    assert inyear != None
    assert inmonth != None
    
    result = 0

    if (inyear > 2024 or inyear < 1850):
        result = 1

    if (inmonth < 1 or inmonth > 12):
        result = 1

    if calendar.isleap(inyear):
        month_lengths = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    if inday == None:
        result = 1
    else:
        if (inday < 1 or inday > month_lengths[inmonth-1]):
            result = 1

    return result

def p_data_given_good(x, Q, R_hi, R_lo, mu, sigma):
    """
    Calculate the probability of an observed value x given a normal distribution with mean mu 
    standard deviation of sigma, where x is constrained to fall between R_hi and R_lo 
    and is known only to an integer multiple of Q, the quantization level.
    
    :param x: observed value for which probability is required
    :param Q: quantization of x, i.e. x is an integer multiple of Q
    :param R_hi: the upper limit on x imposed by previous QC choices.
    :param R_lo: the lower limit on x imposed by previous QC choices.
    :param mu: the mean of the distribution.
    :param sigma: the standard deviation of the distribution
    :type x: float
    :type Q: float
    :type R_hi: float
    :type R_lo: float
    :type mu: float
    :type sigma: float
    :return: probability of the observed value given the specified distribution.
    :rtype: float
    """
    assert Q > 0.0, "Q <= 0" + str(Q)
    assert sigma > 0.0, "sigma <= 0 " + str(sigma)
    assert R_hi > R_lo, "Limits not ascending R_lo "+str(R_lo)+" > R_hi "+str(R_hi)
    assert x >= R_lo, "x below lower limit "+str(x)+" < R_lo "+str(R_lo)
    assert x <= R_hi, "x above upper limit "+str(x)+" > R_hi "+str(R_hi)
    
    upper_x = min([x + 0.5*Q, R_hi + 0.5*Q])
    lower_x = max([x - 0.5*Q, R_lo - 0.5*Q])

    normalizer = 0.5 * (math.erf((R_hi + 0.5*Q - mu)/(sigma*math.sqrt(2))) -
                        math.erf((R_lo - 0.5*Q - mu)/(sigma*math.sqrt(2))))

    return 0.5 * (math.erf((upper_x-mu)/(sigma*math.sqrt(2))) -
                  math.erf((lower_x-mu)/(sigma*math.sqrt(2)))) / normalizer

def p_data_given_gross(Q, R_hi, R_lo):
    """
    Calculate the probability of the data given a gross error
    assuming gross errors are uniformly distributed between
    R_low and R_high and that the quantization, rounding level is Q
    
    :param Q: quantization of x, i.e. x is an integer multiple of Q
    :param R_hi: the upper limit on x imposed by previous QC choices.
    :param R_lo: the lower limit on x imposed by previous QC choices.
    :type Q: float
    :type R_hi: float
    :type R_lo: float
    :return: probability of the observed value given that its a gross error.
    :rtpye: float
    """
    assert R_hi > R_lo, "Limits not ascending R_lo "+str(R_lo)+" > R_hi "+str(R_hi)
    assert Q > 0.0, "Q <= 0" + str(Q)
    
    R = R_hi-R_lo
    return 1./(1.+(R/Q))

def p_gross(p0, Q, R_hi, R_lo, x, mu, sigma):
    """
    Calculate the posterior probability of a gross error given the prior probability p0, 
    the quantization level of the observed value, Q, previous limits on the observed value, 
    R_hi and R_lo, the observed value, x, and the mean (mu) and standard deviation (sigma) of the 
    distribution of good observations assuming they are normally distributed. Gross errors are 
    assumed to be uniformly distributed between R_lo and R_hi.
    
    :param p0: prior probability of gross error
    :param Q: quantization of x, i.e. x is an integer multiple of Q
    :param R_hi: the upper limit on x imposed by previous QC choices.
    :param R_lo: the lower limit on x imposed by previous QC choices.
    :param x: observed value for which probability is required
    :param mu: the mean of the distribution of good obs.
    :param sigma: the standard deviation of the distribution of good obs
    :type Q: float
    :type R_hi: float
    :type R_lo: float
    :return: probability of gross error given an observed value
    :rtpye: float
    """
    assert p0 > 0, "p0 <= 0 "+str(p0)
    assert p0 <= 1, "p0 > 1 "+str(p0) 
    assert Q > 0.0, "Q <= 0 "+str(Q)
    assert R_hi > R_lo, "Limits not ascending R_lo "+str(R_lo)+" > R_hi "+str(R_hi)
    assert x >= R_lo, "x below lower limit "+str(x)+" < R_lo "+str(R_lo)
    assert x <= R_hi, "x above upper limit "+str(x)+" > R_hi "+str(R_hi)
    assert sigma > 0.0, "sigma <= 0 " + str(sigma)
    
    pgross = (p0 * p_data_given_gross(Q, R_hi, R_lo) /
               (  p0   * p_data_given_gross(Q, R_hi, R_lo) +
                (1-p0) * p_data_given_good(x, Q, R_hi, R_lo, mu, sigma)))

    if pgross > 0:
        pass
    else:
        print p0, pgross, x, Q, R_hi, R_lo, mu, sigma

    assert pgross > 0.0, pgross
    assert pgross <= 1.0, pgross

    return pgross
    
def split_generic_callsign(invoyage):
    '''
    Prototype function to identify when a callsign is being used by multiple ships 
    and to split the observations into pseudo IDs that each represents a different ship
    
    :param invoyage: a voyage object containing marine reports
    :type invoyage: Voyage
    :return: list of separate Voyages that the input Voyage has been split into.
    :return type: Voyage
    
    The function works by comparing consecutive observations in the input lists 
    and calculating the implied speed. If it is greater than 40 knots, a new ship 
    is generated. Each subsequent observation is assigned to the closest ship 
    unless the speed exceed 40 knots. If it does, a new ship is generated. 
    '''

    knots_conversion     = 0.539957
    
    if len(invoyage.reps) <= 0:
        return []
    
    result = [1]
    n_ships = 1

    outvoyages = [Voyage()]
    outvoyages[0].add_report(invoyage.reps[0])
    
    ntimes = len(invoyage.reps)

    if ntimes > 1:
        for i in range(1, ntimes):
            #calculate speeds from last position for each ship
            speeds = []
            distances = []
            for j in range(0, n_ships):
                
                last_rep = outvoyages[j].last_rep()
                
                speed, distance, course, timediff = invoyage.reps[i] - last_rep
                
                #calc predicted position and distance of new ob from predicted position
                pred_lat, pred_lon = outvoyages[j].predict_next_point(timediff)
                d = sph.sphere_distance(invoyage.reps[i].lat, 
                                        invoyage.reps[i].lon, 
                                        pred_lat, 
                                        pred_lon)
            
                distances.append(d)
                if timediff != 0:
                    speeds.append(speed)
                else:
                    speeds.append(10000.)
                                                     
            #if all speeds exceed 40 knots then create new ship
            if min(speeds) > 40.0 / knots_conversion:
                n_ships = n_ships + 1
                v = Voyage()
                v.add_report(invoyage.reps[i])
                outvoyages.append(v)
                result.append(n_ships)

            #else ob is assigned to ship whose predicted location is closest to the ob
            else:
                winner = distances.index(min(distances))
                outvoyages[winner].add_report(invoyage.reps[i])
                result.append(winner+1)
    
    return outvoyages

def angle_diff(angle1, angle2):
    '''
    Calculate the angular distance on a circle between two points given in radians
    
    :param angle1: angle of first point
    :param angle2: angle of second point
    :type angle1: float
    :type angle2: float
    :return: angle between the two input points in radians
    :return type: float
    '''
    assert angle1 != None and angle2 != None
#calculate angle between two angles
    diff = abs(angle1 - angle2)
    if diff > np.pi:
        diff = 2.0 * np.pi - diff
    return diff

def sunangle(year, day, hour, minute, sec, zone, dasvtm, lat, lon):
    '''
    Calculate the local azimuth and elevation of the sun at a specified location and time.
    
    :param year: year number
    :param day: day number of year starting with 1 for Jan 1st and running up to 365/6
    :param hour: hour
    :param minute: minute
    :param sec: second
    :param zone: the local international time zone, counted westward from Greenwich
    :param dasvtm: 1 if daylight saving time is in effect, otherwise 0
    :param lat: latitude in degrees, north is positive
    :param lon: longitude in degrees, east is positive
    :type year: integer
    :type day: integer
    :type hour: integer
    :type minute: integer
    :type sec: integer
    :type zone: integer
    :type dasvtm: integer
    :type lat: float
    :type lon: float

    :return:  Azimuth angle of the sun (degrees east of north), Elevation of sun (degrees), 
              Right ascension of sun (degrees), Hour angle of sun (degrees), Hour angle of 
              local siderial time (degrees), Declination of sun (degrees)
    :rtype: float
    
    Copied from Rob Hackett's area 28 Apr 1998 by J.Arnott. 
    Add protection for ASIN near +/- 90 degrees 07 Jan 2002 by J.Arnott. 
    Pythonised 25/09/2015 by J.J. Kennedy
    
    The Python version gets within a fraction of a degree of the original Fortran code from which it was ported 
    for a range of values. The differences are larger if single precision values are used suggesting that this is not the 
    most numerically robust scheme.
    '''
    
    assert day > 0 and day <= 366
    assert hour >= 0 and hour < 24
    assert minute >= 0 and minute < 60
    assert sec >= 0 and sec < 60
    assert lat <= 90 and lat >= -90
    
# Conversion factor between degrees and radians
    degrad = np.pi/180.

#Find number of whole years since end of 1979 (reference point)
    delyear = (year - 1980)#
#Find leap year correction
    leap = math.floor(delyear/4.)
#Find time in whole hours since midnight (allow for "daylight saving").
    time_in_hours = hour + (minute + sec/60.)/60. + zone - dasvtm
#Find time in whole days since start of January 1980
    time = delyear*365 + leap + day - 1.0 + time_in_hours /24.0
#Make leapyear correction
    if delyear == leap * 4.0:
        time = time - 1.0
    if delyear < 0 and delyear != leap*4.0:
        time = time - 1.0
#Find position of sun in celestial sphere, assuming circular orbit (radians).
    theta = (360.0 * time / 365.25) * degrad
#Corrections for elliptical orbit
#Mean anomaly of earth (g)
    mean_anomaly = -0.031271 - 4.5396e-7 * time + theta
#Longitude of sun (el)
    long_of_sun = (4.900968 + 3.6747e-7 * time + 
                   (0.033434 - 2.3e-9*time)*math.sin(mean_anomaly) +  
                   0.000349  * math.sin(2.0*mean_anomaly) + 
                   theta)
#Angle plane of elliptic to plane of celestial equator (eps)
#Slowly decreasing every year
    angle_of_elliptic = 0.409140 - 6.2149e-9 * time
    sin_long_of_sun = math.sin(long_of_sun)
#Intermediate calculation for right ascension
    a1  = sin_long_of_sun * math.cos(angle_of_elliptic)
    a2  = math.cos(long_of_sun)
#Calculate right ascension
    right_ascension = math.atan2(a1, a2)
    if right_ascension < 0.0:
        right_ascension = right_ascension + 2*np.pi
    rta = right_ascension/degrad      #Convert to degrees

#Calculate declination
    declination = math.asin(sin_long_of_sun * math.sin(angle_of_elliptic))

#Calculate siderial time
    siderial_time = 1.759335 + 2*np.pi*(time/365.25 - delyear) + 3.694e-7*time
    if siderial_time >= 2*np.pi:
        siderial_time = siderial_time - 2*np.pi     

#Claculate local siderial time
    local_siderial_time = siderial_time + (time_in_hours*15.0 + lon)*degrad
    if local_siderial_time >= 2*np.pi:
        local_siderial_time = local_siderial_time - 2*np.pi
    sid = local_siderial_time / degrad       # Convert to degrees
    if sid < 0:
        sid = 360.0 + sid             

# Hour Angle
    hour_angle = local_siderial_time - right_ascension

    if hour_angle < 0:
        hour_angle = hour_angle + 2*np.pi    #Correct for negative angles
    hra = hour_angle / degrad             # Convert to degrees
    if hra < 0.0:
        hra = 360.0 + hra   

#Latitude in radians
    phi = lat * degrad
    
#q Sine of elevation
    sin_elevation = (math.sin(phi) * math.sin(declination) +
                     math.cos(phi) * math.cos(declination) * 
                     math.cos(hour_angle))

    if sin_elevation >  1.0:
        sin_elevation =  1.0
    if sin_elevation < -1.0:
        sin_elevation = -1.0 
        
#Geometric elevation
    elevation = math.asin(sin_elevation)
    
#Is sun north or south of zenith
    if (phi - declination) > 0:
        azimuth = 0
    else:
        azimuth = 180
        
# If sun is not very near the zenith, leave a as 0 or 180
    if abs(elevation - 2*np.pi/4.0) > 0.000001:
         
# Protect against rounding error near +/-90 degrees.
        val_to_asin = (math.cos(declination) * 
                       math.sin(hour_angle) / 
                       math.cos(elevation))
        if val_to_asin >  1.0:
            val_to_asin =  1.0
        if val_to_asin < -1.0:
            val_to_asin = -1.0
        azimuth = math.asin(val_to_asin) / degrad  # Azimuth in degrees
#WAS . . .
#a = ASIN (COS (declination) * SIN (h) / COS (e)) / degrad  ! Azimuth is degrees
#Wrap around beyond -180 to 180
        if math.sin(elevation) < math.sin(declination)/math.sin(phi):
            if azimuth < 0:
                azimuth = azimuth + 360.0
            azimuth = 180.0 - azimuth
#Convert to degrees east of north
        azimuth = 180.0 + azimuth

    elevation   = elevation   / degrad   # Convert elevation to degrees
    declination = declination / degrad   # Convert declination to degrees

    assert elevation <= 180 and elevation >= -180
    
    return azimuth, elevation, rta, hra, sid, declination

def dayinyear(year, month, day):

    '''
    Calculate the day in year, running from 1 for Jan 1st to 365 (or 366) for Dec 31st
    
    :param year: Year
    :param month: Month
    :param day: Day
    :type year: integer
    :type month: integer
    :type day: integer
    :return: day in year, between 1 and 366
    :rtype: integer
    '''
    assert month >= 1 and month <= 12
    assert day >= 1
    
    if calendar.isleap(year):
        month_lengths = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    assert day <= month_lengths[month-1], "Day out of range "+str(day)
    
    result = day
    if month > 1:
        result = result + sum(month_lengths[0:month-1])
    
    assert result >= 1 and result <= 366
    return result

def day_test(year, month, day, hour, lat, lon, time_since_sun_above_horizon=1.0):

    '''
    Given year month day hour lat and long calculate if the sun was above the horizon an hour ago.
    
    :param year: Year
    :param month: Month
    :param day: Day
    :param hour: Hour
    :param lat: Latitude in degrees
    :param lon: Longitude in degrees
    :type year: integer
    :type month: integer
    :type day: integer
    :type hour: integer
    :type lat: float
    :type lon: float
    :return: 1 if the sun was above the horizon an hour ago, 0 otherwise.
        
    This is the "day" test used to decide whether a Marine Air Temperature (MAT) measurement is 
    a Night MAT (NMAT) or a Day (MAT). This is important because solar heating of the ship biases 
    the MAT measurements. It uses the function sunangle to calculate the elevation of the sun.
    '''
    assert month >= 1 and month <= 12
    assert day >= 1 and day <= 31
    assert hour >= 0 and hour <= 24
    assert lat <= 90 and lat >= -90    
#hour expressed as decimal fractions of 24 hour day.
#lat and lon in degrees
#return 0 for night
#return 1 for day

    result = 0
    
    if year != None and month != None and day != None and hour != None:
    
        year2 = year
        day2 = dayinyear(year, month, day)
        hour2 = math.floor(hour)
        minute2 = (hour - math.floor(hour))*60.0
        
#go back one hour and test if the sun was above the horizon    
        hour2 = hour2 - time_since_sun_above_horizon
        if hour2 < 0:
            hour2 = hour2 + 24.0
            day2 = day2 - 1
            if day2 <= 0:
                year2 = year2 - 1
                day2 = dayinyear(year2, 12, 31)
    
        lat2 = lat
        lon2 = lon
        if lat == 0:
            lat2 = 0.0001
        if lon == 0:
            lon2 = 0.0001
    
        azimuth, elevation, rta, hra, sid, dec = \
        sunangle(year2, day2, hour2, minute2, 0, 0, 0, lat2, lon2)

        if elevation > 0:
            result = 1

    assert result == 1 or result == 0
    return result

def jul_day(year, month, day):
    '''
    Routine to calculate julian day. This is the weird Astronomical thing which counts from 1 Jan 4713 BC.
    
    :param year: Year
    :param month: Month
    :param day: Day
    :type year: integer
    :type month: integer
    :type day: integer
    :return: julian day
    :rtype: integer
    
    This is one of those routines that looks baffling but works. No one is sure exactly how. It gets 
    written once and then remains untouched for centuries, mysteriously working.
    '''
    assert month >= 1 and month <= 12
    assert day >= 1 and day <= 31
    a = (14 - month)//12
    y = year + 4800 - a
    m = month + 12*a - 3
    return day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045

def time_difference(year1, month1, day1, hour1, year2, month2, day2, hour2):
    '''
    Calculate time difference in hours between any two times
    
    :param year1: Year of first time point
    :param month1: Month of first time point
    :param day1: Day of first time point
    :param hour1: Hour of first time point
    :param year2: Year of second time point
    :param month2: Month of second time point
    :param day2: Day of second time point
    :param hour2: Hour of second time point
    :type year1: integer
    :type month1: integer
    :type day1: integer
    :type hour1: float
    :type year2: integer
    :type month2: integer
    :type day2: integer
    :type hour2: float
    :return: difference in hours between the two times
    :rtype: float
    '''
#return time difference in hours
    if hour1 == None or hour2 == None:
        return None

    assert hour1 >= 0 and hour2 >= 0 and hour1 < 24 and hour2 < 24

    if ( (year1 > year2) or 
         (year1 == year2 and month1 > month2) or 
         (year1 == year2 and month1 == month2 and day1 > day2) or 
         (year1 == year2 and month1 == month2 and
           day1 == day2 and hour1 > hour2) ):
        return -1*time_difference(year2, month2, day2, hour2, 
                                  year1, month1, day1, hour1) 
    
    first_day = jul_day(year1, month1, day1) + hour1/24.
    last_day = jul_day(year2, month2, day2) + hour2/24.

    timdif = 24.*(last_day - first_day)
    
    return timdif

def winsorised_mean(inarr):
    
    '''
    The winsorised mean is a resistant way of calculating an average.
    
    :param inarr: input array to be averaged
    :type inarr: float
    :return: the winsorised mean of the input array with a 25% trimming
    :rtype: float
    
    The winsorised mean is that which you get if you set the first quarter of 
    the sorted input array to the 1st quartile value and the the last quarter 
    to the 3rd quartile and then take the mean. This is quite a heavy trimming of 
    the distribution. It makes it very resistant - about half the obs can be egregiously 
    bad without affecting the mean strongly - but it will be less accurate if 
    there are lots of observations, or the quality of the obs is higher.
    '''
    
    length = len(inarr)
   
    total = 0
    lower = 0
    upper = length-1
    
    inarr.sort()
    
    if length >= 4:
        lower = (length/4)
        upper = upper - lower
        total = total + (inarr[lower] + inarr[upper] )*lower
           
    for j in range(lower, upper+1):
        total += inarr[j]
    
    return total/length

def trimmed_mean(inarr, trim):

    '''
    Calculate a resistant (aka robust) mean of an input array given a trimming criteria.
    
    :param inarr: list of numbers
    :param trim: trimming criteria. A value of 10 trims one tenth of the values off each end of the sorted array before calculating the mean.
    :type inarr: list of floats
    :type trim: integer
    :return: trimmed mean
    :rtype: float
    '''
    
    if trim == 0:
        return np.mean(inarr)
    
    length = len(inarr)
    inarr.sort()
    
    index1 = (length/trim)
       
    trim = np.mean(inarr[index1:length-index1])
      
    return trim

def yindex_to_lat(yindex, res=1):
    assert yindex >= 0
    assert yindex < 180/res
    lat = 90. - yindex*res - res/2.
    return lat

def mds_lat_to_yindex(lat, res=1.0):
    '''
    For a given latitude return the y-index as it was in MDS2/3 in a 1x1 global grid
    
    :param lat: Latitude of the point
    :type lat: float
    :return: grid box index
    :rtype: integer
    
    In the northern hemisphere, borderline latitudes which fall on grid boundaries are pushed north, except 
    90 which goes south. In the southern hemisphere, they are pushed south, except -90 which goes north. 
    At 0 degrees they are pushed south.
    '''

    lat_local = round(lat,1)
    
    if lat_local == -90:
        lat_local += 0.001 
    if lat_local ==  90:
        lat_local -= 0.001
           
    if lat > 0.0:
        return 90/res - 1 - int(lat_local/res)
    else:
        return 90/res - int(lat_local/res)
    
    pass

def lat_to_yindex(lat, res=1):
    '''
    For a given latitude return the y index in a 1x1x5-day global grid
    
    :param lat: Latitude of the point
    :param res: resolution of the grid
    :type lat: float
    :type res: float
    :return: grid box index
    :rtype: integer
    
    The routine assumes that the structure of the SST array is a grid that is 360 x 180 x 73 
    i.e. one year of 1degree lat x 1degree lon data split up into pentads. The west-most box is at 180degrees with index 0
    and the northern most box also has index zero. Inputs on the border between grid cells are pushed south.
    '''
    if res == 1:
        yindex = int(90 - lat)
        if yindex >= 180:
            yindex = 179
        if yindex < 0:
            yindex = 0
        return yindex
    else:
        yindex = int( (90 - lat)/res )
        if yindex >= 180/res:
            yindex = 180/res - 1
        if yindex < 0:
            yindex = 0
        return yindex

def xindex_to_lon(xindex, res=1):
    assert xindex >= 0
    assert xindex < 360/res
    lon = xindex*res - 180. + res/2.
    return lon

def mds_lon_to_xindex(lon, res=1.0):
    '''
    For a given longitude return the x-index as it was in MDS2/3 in a 1x1 global grid
    
    :param lon: Longitude of the point
    :type lon: float
    :return: grid box index
    :rtype: integer
    
    In the western hemisphere, borderline longitudes which fall on grid boundaries are pushed west, except 
    -180 which goes east. In the eastern hemisphere, they are pushed east, except 180 which goes west. 
    At 0 degrees they are pushed west.
    '''
    long_local = round(lon,1)
    
    if long_local == -180:
        long_local += 0.001   
    if long_local == 180:
        long_local -= 0.001   
    if long_local > 0.0:
        return int(long_local/res) + 180/res
    else: 
        return int(long_local/res) + 180/res - 1

def lon_to_xindex(lon, res=1):
    '''
    For a given longitude return the x index in a 1x1x5-day global grid
    
    :param lon: Longitude of the point
    :param res: resolution of the grid
    :type lon: float
    :type res: float
    :return: grid box index
    :rtype: integer
    
    The routine assumes that the structure of the SST array is a grid that is 360 x 180 x 73 
    i.e. one year of 1degree lat x 1degree lon data split up into pentads. The west-most box is at 180degrees W with index 0
    and the northern most box also has index zero. Inputs on the border betwen grid cells are pushed east.
    '''
    
    if res == 1:
        inlon = lon
        if inlon >= 180.0:
            inlon = -180.0 + (inlon - 180.0)
        if inlon < -180.0:
            inlon = inlon + 360.
        xindex = int(inlon + 180.0)
        while xindex >= 360:
            xindex -= 360
        return xindex
    else:
        inlon = lon
        if inlon >= 180.0:
            inlon = -180.0 + (inlon - 180.0)
        if inlon < -180.0:
            inlon = inlon + 360.
        xindex = int( (inlon + 180.0)/res )
        while xindex >= 360/res:
            xindex -= 360/res
        return xindex

def id_is_generic(inid, inyear):
    '''
    Test to see if an ID is one of the generic IDs
    
    :param inid: ID from marine report
    :param inyear: year we are checking for
    :type inid: string
    :type inyear: integer
    :return: True if the ID is generic and False otherwise
    :rtype: logical
    
    Certain callsigns are shared by large numbers of ships. e.g. SHIP, PLAT, 0120, 
    MASK, MASKSTID. This simple routine has a list of known generic call signs. 
    Some call signs are only generic between certain years.
    '''
    generic_ids = [None,
                   '1        ',
                   '58       ',
                   'RIGG     ',
                   '     RIGG',
                   'SHIP     ',
                   'ship     ',
                   '     SHIP',
                   'PLAT     ',
                   '     PLAT',
                   '         ',
                   '0120     ',
                   '0204     ',
                   '0205     ',
                   '0206     ',
                   '0207     ',
                   '0208     ',
                   '0209     ',
                   'MASKST   ',
                   'MASKSTID ',
                   'MASK     ',
                   'XXXX     ']

    if inyear >= 1921 and inyear <= 1941:
        generic_ids.append('2        ')
        generic_ids.append('00002    ')

    if inyear >= 1930 and inyear <= 1937:
        generic_ids.append('3        ')

    if inyear >= 1934 and inyear <= 1954:
        generic_ids.append('7        ')
        generic_ids.append('00007    ')

    result = False
    if inid in generic_ids:
        result = True
    return result

def calc_sst_gradients(inreps):
    
    '''
    calculate SST changes along a route and the distance travelled 
    and the time elapsed between observations.
    '''
    
    nobs = len(inreps)
    
    if nobs > 0:
    
        sst_change = [None]
        temporal_differences = [None]
        spatial_differences = [None]

        for i in range(1, nobs):
                
            sst_difference = inreps[i].sst - inreps[i-1].sst
            distance = sph.sphere_distance(inreps[i-1].lat, 
                                           inreps[i-1].lon, 
                                           inreps[i].lat, 
                                           inreps[i].lon)
            timdif = time_difference(inreps[i-1].year, 
                                     inreps[i-1].month, 
                                     inreps[i-1].day, 
                                     inreps[i-1].hour,
                                     inreps[i].year,   
                                     inreps[i].month,   
                                     inreps[i].day,   
                                     inreps[i].hour)
            
            temporal_differences.append(timdif)
            spatial_differences.append(distance)
            sst_change.append(sst_difference)

    else:
        sst_change = []
        temporal_differences = []
        spatial_differences = []

    return sst_change, spatial_differences, temporal_differences

def iquam_spike_check(inreps):

    '''
    spike check as defined in Xu and Ignatov 2014 section 2b(4): SST SPIKE CHECK.
    '''
    
    max_space_gradient = 0.5 #K/km maximum SST gradient in space gd
    max_time_gradient = 1.0 #K/hr maximum SST gradient in time gt
    delta_t = 2.0 #K deviation associated with ship observations
    #delta_T = 1.0 #K deviation associated with tropical moorings
    #delta_T = 1.0 #K deviation associated with drifters
    #delta_T = 1.6 #K deviation associated with coastal moorings

    qcs = [0]

#generic ids get a free pass on this check 
    if id_is_generic(inreps[0].id, inreps[0].year):
        qcs = []
        for rep in inreps:
            qcs.append(0)
        return qcs

    sst_change, spatial_differences, temporal_differences = \
    calc_sst_gradients(inreps)

    ntime = len(sst_change)
    for i in range(1, ntime):

        threshold = max([delta_t, 
                         max_space_gradient * spatial_differences[i], 
                         max_time_gradient * temporal_differences[i]])

        if sst_change[i] > threshold:
            qcs.append(1)
        else:
            qcs.append(0)

    return qcs

def last_month_was(year, month):
    '''
    Short function to get the previous month given a particular month of interest
    
    :param year: year of interest
    :param month: month of interest
    :type year: integer
    :type month: integer
    '''
    last_year = year
    last_month = month - 1
    if last_month == 0:
        last_month = 12
        last_year = year - 1
        
    return last_year, last_month

def next_month_is(year, month):
    '''
    Short function to get the next month given a particular month of interest
    
    :param year: year of interest
    :param month: month of interest
    :type year: integer
    :type month: integer
    '''
    next_year = year
    next_month = month + 1
    if next_month > 12:
        next_month = 1
        next_year = year + 1
        
    return next_year, next_month

def year_month_gen(year1, month1, year2, month2):
    '''
    A generator to loop one month at a time between 
    year1 month1 and year2 month2
    
    :param year1: first year to loop from
    :param month1: month in first year to start from
    :param year2: Last year to loop over
    :param month2: last month in last year to loop over
    :type year1: integer
    :type month1: integer
    :type year2: integer
    :type month2: integer
    :return: Return an iterator that yields tuples of a year and month
    :rtype: integer
    '''
    
    assert year2 >= year1, "Start year after end year"
    assert month1 > 0 and month1 <= 12, "Month outside 1-12"
    
    year = year1
    month = month1
    
    while not(year == year2 and month == month2):
        yield year, month
        month += 1
        if month > 12:
            month = 1
            year += 1 
    
    yield year, month

def month_lengths(year):
    '''
    Return a list holding the lengths of the months in a given year
    
    :param year: Year for which you want month lengths
    :type year: int
    :return: list of month lengths
    :rtype: int
    '''
    if calendar.isleap(year):
        month_lengths = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    return month_lengths

def imma1_record_to_marine_rep(x, climsst, climnmat):
    '''
    Given a database cursor and an IMMA report it will populate the appropriate table in the data base.
    
    :param cursor: data base cursor for SQLite3 data base
    :param year: year of the table to which the observation is to be added
    :param x: IMMA report to be added to the data base
    :param climsst: SST climatology
    :param climnmat: NMAT climatology
    :type cursor: unknown
    :type year: integer
    :type x: IMMA report
    :type climsst: numpy array
    :type climnmat: numpy array
    
    A feature of the current version is that, in line with MDS3 and earlier, the hour defaults to zero UTC when 
    hour is missing from the report.
    '''
    
    rep = MarineReport.report_from_imma(x)
    
#Deck 201 GMT midnights are assigned to the wrong day, see Carella, Kent, Berry 2015 Appendix A3 
    if rep.dck == 201 and rep.year < 1899 and rep.hour == 0:
        rep.shift_day(-1)

#Deck 701 prior to 1857ish has lots of obs with no hour set
    if rep.dck == 701 and rep.year < 1860 and rep.hour == None:
        rep.hour = 12.

    try:
        sst_climav  = get_sst(rep.lat, rep.lon, 
                              rep.month, rep.day, climsst)
    except:
        sst_climav = None
    if sst_climav != None:
        sst_climav = float(sst_climav)

    try:
        mat_climav = get_sst(rep.lat, rep.lon, 
                             rep.month, rep.day, climnmat)
    except:
        mat_climav = None
    if mat_climav != None:
        mat_climav = float(mat_climav)

    rep.setnorm(sst_climav, mat_climav)

    return rep

def base_qc_report(rep):
    '''
    Take a marine report and do some base qc on it.
    '''
#Basic positional QC
    if rep.getvar('PT') in [6, 7]:
        rep.set_qc('POS', 'isbuoy', 1)
    else:
        rep.set_qc('POS', 'isbuoy', 0)

    if rep.getvar('PT') in [0, 1, 2, 3, 4, 5, 10, 11, 12, 17]:
        rep.set_qc('POS', 'isship', 1)
    else:
        rep.set_qc('POS', 'isship', 0)

#See Kent et al. HadNMAT2 QC section
    rep.set_qc('POS', 'mat_blacklist', 0)
    if rep.getvar('PT') == 5 and rep.getvar('DCK') == 780:
        rep.set_qc('POS', 'mat_blacklist', 1)

#make sure lons are in range -180 to 180
    lon = rep.lon()
    lat = rep.lat()
#North Atlantic, Suez and indian ocean to be excluded from MAT processing
    if (rep.getvar('DCK') == 193 and 
        rep.getvar('YR') >= 1880 and 
        rep.getvar('YR') <= 1893 and 
        ((lon >= -80.0 and lon <= 0.0   and lat >= 40.0  and lat <= 55.0) or
         (lon >= -10.0 and lon <= 30.0  and lat >= 35.0  and lat <= 45.0) or 
         (lon >=  15.0 and lon <= 45.0  and lat >= -10.0 and lat <= 40.0) or 
         (lon >=  15.0 and lon <= 95.0  and lat >= -10.0 and lat <= 15.0) or 
         (lon >=  95.0 and lon <= 105.0 and lat >= -10.0 and lat <= 5.0)
         )):
        rep.set_qc('POS', 'mat_blacklist', 1)

    if rep.getvar('DCK') == 780:
        rep.set_qc('POS', 'is780', 1)
    else:
        rep.set_qc('POS', 'is780', 0)
    
    rep.set_qc('POS', 'pos', position_check(rep.lat(), 
                                            rep.lon()))
    
    rep.set_qc('POS', 'date', date_check(rep.getvar('YR'), 
                                         rep.getvar('MO'), 
                                         rep.getvar('DY'), 
                                         rep.getvar('HR')))

    if (rep.get_qc('POS', 'pos') == 0 and rep.get_qc('POS', 'date') == 0):
        rep.set_qc('POS', 'day', 
                   day_test(rep.getvar('YR'), 
                            rep.getvar('MO'), 
                            rep.getvar('DY'), 
                            rep.getvar('HR'), 
                            rep.lat(), 
                            rep.lon()))
    else:
        rep.set_qc('POS', 'day', 1)

    rep.set_qc('POS', 'blklst', 
                blacklist(rep.getvar('ID'), rep.getvar('DCK'), 
                          rep.getvar('YR'), rep.getvar('MO'), 
                          rep.lat(), rep.lon(), 
                          rep.getvar('PT')))

#SST base QC
    rep.set_qc('SST', 'noval', value_check(rep.getvar('SST')))
    rep.set_qc('SST', 'freez', sst_freeze_check(rep.getvar('SST'), 0.0))
    rep.set_qc('SST', 'clim', climatology_check(rep.getvar('SST'), 
                                                rep.getnorm('SST'), 8.0))
    rep.set_qc('SST', 'nonorm', no_normal_check(rep.getnorm('SST')))

#MAT base QC
    rep.set_qc('AT', 'noval', value_check(rep.getvar('AT')))
    rep.set_qc('AT', 'clim', climatology_check(rep.getvar('AT'), 
                                               rep.getnorm('AT'), 10.0))
    rep.set_qc('AT', 'nonorm', no_normal_check(rep.getnorm('AT')))

    return rep

